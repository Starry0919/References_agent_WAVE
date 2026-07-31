r"""paper_extraction → DDR v2 转换桥接层.

将 ``harness/paper_extraction/`` (Skill01–13 论文实验设计抽取管道) 的结构化输出
转换为教师指定的 DDR v2 格式 (``knowledge/ddr_database/schema_v2.json``)。

这个模块解决了 gap #2——老师要求 Agent 半自动抽取论文 DDR、人工抽检,
而 paper_extraction Skill 已经能全自动抽取实验设计但输出格式≠DDR 格式。

设计原则 (对齐老师 §4.3 抽取流程):
- Skill07 (实验设计抽取) 的输出作为 DDR 的初稿
- 不覆盖需要人工判断的字段 (evidence_grading, reason_nature, rule)
- 这些字段标记为 ``pending_human_review``,交给人工抽检环节
- 转化后立即入库,校准状态为 ``pending``

evidence_grading/reason_nature/rule 现在有两层信号,都不直接免检:
- 模型自评 (``ddr_annotation``, 见 ``harness/paper_extraction/SKILL.md`` §5.5)——
  Skill07 抽取时已被明确教导硬/软证据定义、五类理由性质及"仅机理推断/文献
  类比才允许写规则"的纪律,不再默认答成"机理推断"
- 本模块自己的关键词启发式 (``_auto_evidence_grade``/``_auto_reason_nature``)

模型自评存在且合法时优先采用,否则回退到关键词启发式;两者分歧时额外记入
``pending`` 提示人工重点复核。``rule`` 字段的"仅机理推断/文献类比可填"约束在
Python 侧无条件重新校验一遍,不管模型自己是否已经遵守——这是防止"抽取阶段
提示词是唯一防线、一旦提示词被忽略规则库就被污染"的第二道防线。
"""
from __future__ import annotations

import json
import re
import uuid
from collections import Counter
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

from harness.config import PROJECT_ROOT

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DDR_DIR = PROJECT_ROOT / "knowledge" / "ddr_database"

# Mapping from paper_extraction module types → DDR design_action codes
MODULE_TO_DESIGN_ACTION: dict[str, str] = {
    "feedback_deregulation": "M3",
    "feedforward_deregulation": "M3",
    "transcriptional_deregulation": "M3",
    "rate_limiting_enzyme": "M4",
    "enzyme_engineering": "M4",
    "heterologous_replacement": "M4",
    "knockout": "M5",
    "competing_pathway_attenuation": "M5",
    "flux_redistribution": "M5",
    "precursor_supply": "M2",
    "cofactor_balancing": "M2",
    "pathway_construction": "M1",
    "de_novo_pathway": "M1",
    "promoter_engineering": "M6",
    "rbs_engineering": "M6",
    "copy_number": "M6",
    "dynamic_control": "M7",
    "toxicity_management": "M8",
    "fermentation": "M9",
    "medium_optimization": "M9",
}

# Implementation method mapping from intervention types
INTERVENTION_TO_IMPLEMENTATION: dict[str, str] = {
    "knockout": "KO",
    "deletion": "KO",
    "crispri": "CRISPRi",
    "crispr_interference": "CRISPRi",
    "overexpression": "过表达",
    "plasmid_expression": "过表达",
    "point_mutation": "点突变",
    "site_directed_mutagenesis": "点突变",
    "heterologous_expression": "异源表达",
    "heterologous_replacement": "异源表达",
    "promoter_replacement": "启动子工程",
    "promoter_engineering": "启动子工程",
    "rbs_engineering": "RBS工程",
    "medium_optimization": "培养基优化",
    "fermentation_control": "发酵调控",
    "cofactor_engineering": "辅因子工程",
    "dynamic_sensor": "动态调控",
}

# Evidence grading heuristics (conservative: defaults to pending_human_review)
# These heuristics flag obvious cases but never auto-decide borderline ones.
EVIDENCE_GRADING_HEURISTICS = {
    "硬": [
        "measured", "crystal_structure", "in_vitro_assay", "in_vivo_assay",
        "stoichiometric", "known_regulation", "validated_result",
        "enzyme_kinetics", "growth_phenotype", "lc_ms", "hplc",
        "nmr", "gene_essentiality", "theoretical_yield",
    ],
    "软": [
        "optknock", "docking", "foldx", "delta_delta_g",
        "alphafold_prediction", "esmfold", "grow_match",
        "machine_learning", "homology_model", "de_novo_prediction",
    ],
}

# reason_nature keyword heuristics. Mirrors the conservatism of the evidence
# heuristics above: only an explicit textual signal earns a *positive*
# classification. "机理推断" is deliberately NOT the fallback (see
# _auto_reason_nature) — 老师 §4.1 warns that forcing a paper without a clean
# decision chain into a mechanistic-sounding rule is exactly how the rule
# library gets polluted by post-hoc rationalization.
SCREENING_KEYWORDS = (
    "library", "screening", "screen", "keio", "random_mutagenesis",
    "directed_evolution", "high_throughput_screen", "ale",
    "adaptive_laboratory_evolution",
)
LITERATURE_ANALOGY_KEYWORDS = (
    "as_described_previously", "as_reported_by", "following_the_protocol_of",
    "similar_to", "analogous_to",
)
AVAILABLE_RESOURCE_KEYWORDS = (
    "available_strain", "commercial_kit", "off_the_shelf", "convenient",
    "readily_available",
)
MECHANISTIC_KEYWORDS = (
    "feedback", "feedforward", "allosteric", "kinetic", "km", "ic50",
    "binding_site", "crystal_structure", "docking", "inhibit", "represses",
    "represser", "repressor", "activates", "regulation", "regulon",
    "mechanism", "rate_limiting", "rate-limiting",
)

# Valid values for a model-supplied `ddr_annotation` (SKILL.md §5.5) - the
# extraction model is now taught the same DDR discipline as this module's own
# keyword heuristics (a second line of defense: if the Python heuristics
# below have a bug, the model's own honest self-assessment, produced under an
# explicit anti-fabrication instruction, is still available as a check).
# Never trust an out-of-vocabulary value from the model - fall back to the
# keyword heuristic instead of passing through an unvalidated string.
_VALID_DESIGN_ACTIONS = frozenset(MODULE_TO_DESIGN_ACTION.values()) | {"M0", "M11"}
_VALID_EVIDENCE_GRADES = frozenset({"硬", "软"})
_VALID_REASON_NATURES = frozenset({"机理推断", "文献类比", "现成可得", "筛选得来", "事后合理化存疑"})


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


@dataclass
class DDRConversionResult:
    """Result of converting one paper's extraction output to DDR format."""

    ddr: dict[str, Any]
    warnings: list[str] = field(default_factory=list)
    pending_human_review_fields: list[str] = field(default_factory=list)
    extraction_task_id: str | None = None


# ---------------------------------------------------------------------------
# Main conversion entry point
# ---------------------------------------------------------------------------


def convert_extraction_to_ddr(
    extraction_output: dict[str, Any],
    *,
    extraction_task_id: str | None = None,
    paper_index: int | None = None,
    paper_extraction_detail: dict[str, Any] | None = None,
    auto_save: bool = False,
) -> DDRConversionResult:
    """Convert a paper_extraction Skill07+ output to DDR v2 format.

    Parameters
    ----------
    extraction_output:
        The full output from the paper_extraction pipeline (after Skill07–09).
        Must include at minimum: ``output.fields``, ``output.experimental_design_object``,
        and ``extensions.article_type_gate`` (or equivalent).
    extraction_task_id:
        The task_id from the paper_extraction run, for provenance tracking.
    paper_index:
        This paper's position within the task's paper list, for idempotent
        re-conversion (see ``ensure_task_saved_as_evidence``) and for linking
        this DDR back to a specific paper within a multi-paper task.
    paper_extraction_detail:
        The paper's entry from ``result_summary.build_extraction_summary()``
        (agent reasoning + evidence-bound design fields + quality), embedded
        verbatim into ``extraction_meta`` so the literature-evidence detail
        page has a durable source that survives the run's own checkpoint
        being deleted.
    auto_save:
        If True, write the DDR JSON to ``knowledge/ddr_database/`` automatically.
        Default False — caller should review before saving.

    Returns
    -------
    DDRConversionResult
        The converted DDR dict, plus warnings and fields needing human review.
    """
    warnings: list[str] = []
    pending: list[str] = []

    # -- Step 1: Extract core output -------------------------------------------------
    output = _get_nested(extraction_output, "output", default={})
    fields = output.get("fields", {}) if isinstance(output, dict) else {}
    ed_obj = output.get("experimental_design_object", {}) if isinstance(output, dict) else {}
    extensions = output.get("extensions", {}) if isinstance(output, dict) else {}
    gate = extensions.get("article_type_gate", {})

    if not fields and not ed_obj:
        warnings.append("extraction_output has neither 'fields' nor 'experimental_design_object'; DDR may be sparse")

    # -- Step 2: Build metadata ------------------------------------------------------
    metadata = _build_metadata(extraction_output, fields, gate, warnings)

    # -- Step 3: Build decision_chain -------------------------------------------------
    decision_chain = _build_decision_chain(extraction_output, fields, ed_obj, warnings, pending)

    # -- Step 4: Build paper-level context (v1 compat) --------------------------------
    problem = _build_engineering_problem(fields, ed_obj, decision_chain)
    diagnosis = _build_biological_diagnosis(fields, ed_obj, decision_chain)
    hypothesis = _build_engineering_hypothesis(fields, ed_obj, decision_chain)

    # -- Step 5: Build extraction_meta ------------------------------------------------
    extraction_meta = _build_extraction_meta(pending, extraction_task_id, paper_index, paper_extraction_detail)

    # -- Step 6: Assemble DDR ---------------------------------------------------------
    ddr_id = _allocate_ddr_id()
    ddr = {
        "ddr_id": ddr_id,
        "schema_version": "2.0",
        "metadata": metadata,
        "decision_chain": decision_chain,
        "engineering_problem": problem,
        "biological_diagnosis": diagnosis,
        "engineering_hypothesis": hypothesis,
        "extraction_meta": extraction_meta,
    }

    result = DDRConversionResult(
        ddr=ddr,
        warnings=warnings,
        pending_human_review_fields=pending,
        extraction_task_id=extraction_task_id,
    )

    if auto_save:
        _save_ddr(ddr)

    return result


# ---------------------------------------------------------------------------
# Step builders
# ---------------------------------------------------------------------------


def _build_metadata(
    extraction_output: dict[str, Any],
    fields: dict[str, Any],
    gate: dict[str, Any],
    warnings: list[str],
) -> dict[str, Any]:
    """Extract paper metadata from extraction output."""
    # Try multiple paths to find paper identity
    paper_id = fields.get("paper_identity", {})
    if not paper_id:
        paper_id = extraction_output.get("paper_identity", {})
    if not paper_id:
        # Try validated_papers from task-level output
        vps = extraction_output.get("validated_papers", [])
        paper_id = vps[0] if vps else {}

    # `.get(key, default)` only falls back when the key is *missing* - the
    # identity dict here always has every key present, explicitly `None`
    # when skill04 couldn't resolve it (observed for real uploaded PDFs
    # with no extractable title/DOI), so `or default` is required or a
    # None title would reach `_save_ddr`'s `.lower()` and crash.
    ref = {
        "title": paper_id.get("title") or "",
        "authors": _format_authors(paper_id.get("authors") or []),
        "journal": paper_id.get("journal") or "",
        "year": str(paper_id.get("year")) if paper_id.get("year") else "",
        "doi": paper_id.get("doi") or "",
    }
    if not ref["title"]:
        # Still usable/identifiable rather than an unusable blank literature-
        # evidence entry - mirrors the frontend's own untitled-paper fallback
        # (PaperResultTabs.tsx::paperIdentityTitle).
        ref["title"] = f"Untitled paper ({paper_id.get('paper_id') or 'unknown'})"
        warnings.append("no paper title resolved from extraction output; using a placeholder title")

    strains = fields.get("paper_target_strains", [])
    target_strain = strains[0] if strains else {}

    return {
        "title": ref["title"],
        "category": _infer_categories(fields),
        "organism": target_strain.get("paper_organism") or paper_id.get("organism", ""),
        "host": target_strain.get("paper_strain_normalized") or target_strain.get("paper_strain_raw", ""),
        "target_product": fields.get("target_product", ""),
        "product_class": fields.get("product_class", ""),
        "engineering_level": fields.get("engineering_level", ""),
        "reference": ref,
        "paper_type": gate.get("article_type", "primary_research"),
    }


def _build_decision_chain(
    extraction_output: dict[str, Any],
    fields: dict[str, Any],
    ed_obj: dict[str, Any],
    warnings: list[str],
    pending: list[str],
) -> list[dict[str, Any]]:
    """Build the decision_chain from extraction output.

    Uses experimental_design_object's intervention/experiment list as the primary
    source for decision steps. Falls back to extracting from fields.
    """
    chain: list[dict[str, Any]] = []

    # Primary source: experimental_design_object with explicit interventions
    experiments = ed_obj.get("experiments", [])
    interventions = ed_obj.get("interventions", [])
    design_steps = ed_obj.get("design_steps", [])

    # Combine all potential step sources
    step_candidates = _collect_step_candidates(fields, ed_obj, experiments, interventions, design_steps)

    if not step_candidates:
        warnings.append("no step candidates found in extraction output; decision_chain will be empty")
        return chain

    # Design doc §4.1: a decision step's trigger is "what observation caused
    # this action" — usually the *previous* step's result, not the paper's
    # abstract. Tracked across the loop so step i>1 can point at step i-1's
    # outcome instead of leaving trigger.observation blank whenever the
    # source record has no explicit per-step observation field of its own
    # (true for Skill07's flat experiment records — see _build_single_step).
    prev_outcome = ""
    for i, candidate in enumerate(step_candidates, start=1):
        step = _build_single_step(i, candidate, fields, pending, prev_outcome=prev_outcome)
        chain.append(step)
        prev_outcome = step["result"].get("after") or prev_outcome

    return chain


def _collect_step_candidates(
    fields: dict[str, Any],
    ed_obj: dict[str, Any],
    experiments: list[dict[str, Any]],
    interventions: list[dict[str, Any]],
    design_steps: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Collect all potential decision-step candidates from various parts of the extraction output."""
    candidates: list[dict[str, Any]] = []

    # (a) Explicit design_steps (best case)
    for ds in design_steps:
        candidates.append({"source": "design_steps", "data": ds})

    # (b) Interventions with purpose
    for iv in interventions:
        if iv.get("purpose") or iv.get("rationale"):
            candidates.append({"source": "interventions", "data": iv})

    # (c) Experiments (from Skill07 extraction)
    for exp in experiments:
        if exp.get("intervention") and exp.get("purpose"):
            candidates.append({"source": "experiments", "data": exp})

    # (d) engineering_actions from old v1 DDR format (backward compat)
    eng_actions = fields.get("engineering_actions", [])
    for act in eng_actions:
        candidates.append({"source": "engineering_actions", "data": act})

    # (e) Fallback: extract from experimental_design_object narrative
    if not candidates:
        narrative = ed_obj.get("experimental_narrative", "")
        if narrative:
            candidates.append({"source": "narrative", "data": {"narrative": narrative}})

    return candidates


def _build_single_step(
    step_num: int,
    candidate: dict[str, Any],
    fields: dict[str, Any],
    pending: list[str],
    *,
    prev_outcome: str = "",
) -> dict[str, Any]:
    """Build one decision_chain step from a candidate.

    Two source shapes are handled. "design_steps"/"interventions" candidates
    (hand-assembled or from a future richer Skill07 extension) already carry
    decision-chain-shaped keys (action_type/gene/trigger_observation/
    rationale/...). "experiments" candidates are Skill07's *actual* current
    output shape — flat experimental-design records with keys
    (experiment_id/purpose/host/intervention/conditions/control/replicates/
    readout/outcome) that were never decision-chain keys to begin with; every
    field below that reads `data.get("action_type")` etc. returned "" for
    that shape (confirmed against a real converted record, DDR-006 in
    knowledge/ddr_database/ — every step landed on the "M3" default and
    implementation "KO" from a separate substring-match bug in
    _map_implementation, with every other field blank). The `intervention`/
    `purpose`/`readout`/`outcome` fallbacks below close that gap.
    """
    data = candidate["data"]
    source = candidate["source"]

    intervention_text = str(data.get("intervention") or "")
    purpose_text = str(data.get("purpose") or "")

    # The extraction model may have already self-assessed this step per
    # SKILL.md §5.5 ("ddr_annotation"). Validate before trusting it - an
    # out-of-vocabulary or missing value falls through to the existing
    # keyword heuristics below exactly as if no annotation were present.
    annotation = data.get("ddr_annotation") if isinstance(data.get("ddr_annotation"), dict) else {}
    model_design_action = annotation.get("design_action")
    if model_design_action not in _VALID_DESIGN_ACTIONS:
        model_design_action = None
    model_evidence_grade = annotation.get("evidence_grading")
    if model_evidence_grade not in _VALID_EVIDENCE_GRADES:
        model_evidence_grade = None
    model_reason_nature = annotation.get("reason_nature")
    if model_reason_nature not in _VALID_REASON_NATURES:
        model_reason_nature = None

    # --- design_action ---
    if model_design_action:
        design_action = model_design_action
    else:
        action_type = data.get("action_type") or data.get("modification_type") or data.get("intervention_type", "")
        design_action = _map_design_action(action_type, data)
        if design_action == "M3" and not action_type:
            # No explicit action_type key on this candidate shape (true for all
            # "experiments" candidates) — try inferring from the free-text
            # intervention/purpose description before falling back to the M3
            # default, so a knockout/competing-pathway experiment doesn't get
            # silently mislabeled as feedback deregulation.
            inferred = _infer_design_action_from_text(f"{intervention_text} {purpose_text}")
            if inferred:
                design_action = inferred
            else:
                pending.append(f"step_{step_num}.design_action: unable to map '{action_type or intervention_text[:60]}' confidently, defaulted to M3")

    # --- target ---
    gene_match = _extract_gene_symbol(intervention_text)
    target = {
        "gene": data.get("gene") or data.get("target_gene") or data.get("gene_or_pathway", "") or gene_match,
        "enzyme": data.get("enzyme") or data.get("target_enzyme", ""),
        "pathway": data.get("pathway") or data.get("target_pathway", ""),
        "condition": data.get("condition") or data.get("medium") or data.get("conditions", None),
    }
    if not target["gene"] and not target["enzyme"] and not target["pathway"]:
        pending.append(f"step_{step_num}.target: no gene/enzyme/pathway extracted from '{intervention_text[:60]}'; needs human fill-in")

    # --- trigger ---
    # Design doc §4.1: trigger.observation = "what did the researcher observe
    # that led to this step" — for a flat experiment record there is no such
    # field; the previous step's measured outcome is the best available
    # proxy for a sequential decision chain (falls back to "" for step 1,
    # same as before, rather than fabricating an observation).
    trigger = {
        "observation": annotation.get("trigger_observation") or data.get("trigger_observation") or data.get("observation", "") or prev_outcome,
        "reasoning": data.get("rationale") or data.get("trigger_reasoning", "") or purpose_text,
        "source_location": data.get("source_location") or data.get("host", ""),
    }

    # --- evidence ---
    evidence = {
        "description": data.get("evidence_description") or data.get("evidence", "") or data.get("readout", ""),
        "source": data.get("evidence_source") or data.get("source", "") or ("论文实测" if data.get("readout") or data.get("outcome") else ""),
        "source_location": data.get("evidence_location") or data.get("control", ""),
        "values": data.get("evidence_values") or data.get("values", {}),
    }

    # --- evidence_grading: ALWAYS pending human review, regardless of source ---
    # Two independent signals feed this, in priority order: the extraction
    # model's own self-assessment (SKILL.md §5.5 `ddr_annotation`, produced
    # under an explicit hard/soft definition and anti-fabrication
    # instruction) first, then this module's own keyword heuristic as a
    # fallback for candidates the model didn't annotate. Neither signal is
    # ever auto-trusted into the DDR without human review - see `pending`.
    auto_grade = _auto_evidence_grade(data)
    if model_evidence_grade:
        evidence_grading = model_evidence_grade
        grading_rationale = f"模型自评({model_evidence_grade}): 见 ddr_annotation.evidence_grading_rationale——需人工确认"
        if annotation.get("evidence_grading_rationale"):
            grading_rationale += f" | {annotation['evidence_grading_rationale']}"
        if auto_grade and auto_grade != model_evidence_grade:
            pending.append(
                f"step_{step_num}.evidence_grading: model self-assessment ({model_evidence_grade}) "
                f"disagrees with keyword heuristic ({auto_grade}) — flag for careful human review"
            )
    elif auto_grade:
        evidence_grading = auto_grade
        grading_rationale = f"自动启发式判定({auto_grade}): 基于证据关键词匹配——需人工确认"
    else:
        evidence_grading = "软"  # default conservative
        grading_rationale = "自动判定失败——请人工判定"
    pending.append(
        f"step_{step_num}.evidence_grading: model={model_evidence_grade or 'none'}, "
        f"heuristic={auto_grade or 'none'}, requires human review"
    )

    # --- reason_nature: ALWAYS pending human review, regardless of source ---
    auto_reason_nature = _auto_reason_nature(data, fields)
    reason_nature = model_reason_nature or auto_reason_nature
    if model_reason_nature and model_reason_nature != auto_reason_nature:
        pending.append(
            f"step_{step_num}.reason_nature: model self-assessment ({model_reason_nature}) disagrees "
            f"with keyword heuristic ({auto_reason_nature}) — flag for careful human review"
        )
    pending.append(
        f"step_{step_num}.reason_nature: model={model_reason_nature or 'none'}, "
        f"heuristic={auto_reason_nature}, requires human review"
    )

    # --- alternatives ---
    # Contract is a list of {approach, rejected_reason} objects (SKILL.md
    # §5.5), but some models (observed: kimi-k3) return a list of plain
    # strings instead - normalize here so every consumer of decision_chain
    # sees the contracted shape regardless of which model produced it.
    raw_alternatives = annotation.get("alternatives_considered") or data.get("alternatives", [])
    alternatives = [
        a if isinstance(a, dict) else {"approach": str(a), "rejected_reason": ""}
        for a in raw_alternatives
    ]

    # --- implementation ---
    impl_raw = data.get("implementation") or data.get("modification_type") or data.get("intervention_type", "") or intervention_text
    implementation = _map_implementation(impl_raw)

    # --- implementation_detail ---
    # Free-text `intervention` has no structured home elsewhere in the DDR
    # schema (target.gene/enzyme only fit a single symbol) — keeping the full
    # sentence here means a step never regresses to fully empty just because
    # the source shape had no dedicated gene/enzyme/pathway keys.
    impl_detail = data.get("implementation_detail") or data.get("modification_detail", "") or intervention_text

    # --- result ---
    result = {
        "metric": data.get("result_metric", "") or data.get("readout", ""),
        "before": data.get("result_before", ""),
        "after": data.get("result_after", "") or str(data.get("outcome") or ""),
        "fold_change": data.get("fold_change", None),
        "quantified": bool(data.get("result_quantified", False)) or bool(re.search(r"\d", str(data.get("outcome") or ""))),
    }

    # --- rule: ALWAYS pending human review ---
    # `annotation["generalizable_rule"]` is the model's own SKILL.md §5.5
    # output, produced under the same "null unless 机理推断/文献类比"
    # instruction as the gate immediately below - but that instruction is a
    # prompt, not a guarantee, so the Python gate re-checks it independently
    # against `reason_nature` regardless of source. This is the second line
    # of defense the model-level instruction was added for: even a model
    # that ignores its own instructions, or a reason_nature the model
    # disagreed with above, still can't get a fabricated rule past this line.
    rule = annotation.get("generalizable_rule") or data.get("generalizable_rule") or data.get("rule", None)
    if reason_nature not in ("机理推断", "文献类比"):
        rule = None  # 不写出可能编造的规则
    elif rule:
        pending.append(f"step_{step_num}.rule: requires human calibration (dual-review process)")

    return {
        "step": step_num,
        "design_action": design_action,
        "target": target,
        "trigger": trigger,
        "evidence": evidence,
        "evidence_grading": evidence_grading,
        "evidence_grading_rationale": grading_rationale,
        "reason_nature": reason_nature,
        "alternatives": alternatives,
        "implementation": implementation,
        "implementation_detail": impl_detail,
        "result": result,
        "rule": rule,
    }


def _field_text(fields: dict[str, Any], key: str) -> str:
    """Skill07's `fields[key]` is a {value, status, confidence, ...} object
    per the extraction contract (see opus_extractor.py's output_contract),
    not a plain string - unwrap `.value` here so callers that need the text
    (not the whole field-metadata object) never propagate a dict downstream
    into places (e.g. translation, template strings) that expect `str`."""
    value = fields.get(key)
    if isinstance(value, dict):
        value = value.get("value")
    return value if isinstance(value, str) else ""


def _build_engineering_problem(
    fields: dict[str, Any],
    ed_obj: dict[str, Any],
    decision_chain: list[dict[str, Any]],
) -> dict[str, Any]:
    """Synthesize the engineering problem from available data."""
    ep = fields.get("engineering_problem", {})
    return {
        "problem_statement": ep.get("problem_statement") or _field_text(fields, "objective"),
        "problem_type": ep.get("problem_type") or _infer_problem_types(decision_chain),
        "trigger_conditions": ep.get("trigger_conditions") or _infer_trigger_conditions(decision_chain),
    }


def _build_biological_diagnosis(
    fields: dict[str, Any],
    ed_obj: dict[str, Any],
    decision_chain: list[dict[str, Any]],
) -> dict[str, Any]:
    """Synthesize biological diagnosis from available data."""
    diag = fields.get("biological_diagnosis", {})
    obs = diag.get("observations", [])
    if not obs:
        obs = [step["trigger"]["observation"] for step in decision_chain if step["trigger"]["observation"]]

    bottlenecks_list = diag.get("bottlenecks", [])
    if not bottlenecks_list:
        bottlenecks_list = [f"{step['target'].get('gene','')}: {step['trigger']['observation'][:80]}" for step in decision_chain]

    return {
        "observations": obs,
        "bottlenecks": bottlenecks_list,
        "mechanistic_explanation": diag.get("mechanistic_explanation", ""),
    }


def _build_engineering_hypothesis(
    fields: dict[str, Any],
    ed_obj: dict[str, Any],
    decision_chain: list[dict[str, Any]],
) -> dict[str, Any]:
    """Synthesize hypothesis from available data."""
    hyp = fields.get("engineering_hypothesis", {})
    return {
        "hypothesis": hyp.get("hypothesis", ""),
        "expected_effect": hyp.get("expected_effect", ""),
    }


def _build_extraction_meta(
    pending: list[str],
    extraction_task_id: str | None,
    paper_index: int | None = None,
    paper_extraction_detail: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "extraction_method": "semi_automated",
        "extracted_by": ["agent_harness_v2"],
        "extraction_date": date.today().isoformat(),
        "calibration_status": "pending",
        "calibrated_by": [],
        "calibration_notes": f"由 paper_extraction Skill 自动抽取后经 ddr_converter 转换。{len(pending)} 个字段待人工审核。",
        "human_review_status": "pending",
        "review_notes": "",
        "paper_extraction_task_id": extraction_task_id,
        "paper_index": paper_index,
        "paper_extraction_detail": paper_extraction_detail,
    }


# ---------------------------------------------------------------------------
# Mapping helpers
# ---------------------------------------------------------------------------


def _map_design_action(action_type: str, data: dict[str, Any]) -> str:
    """Map an intervention/action type to a module code (M0–M11)."""
    normalized = action_type.lower().replace(" ", "_").replace("-", "_")
    return MODULE_TO_DESIGN_ACTION.get(normalized, "M3")  # default to M3 (解除调控) since most common


# Keyword → module code, for inferring design_action from free-text
# intervention/purpose descriptions when no explicit action_type field
# exists (Skill07's "experiments" shape never has one — see
# _build_single_step). Checked in order; first match wins, so more specific
# module keywords are listed before generic ones.
_TEXT_TO_DESIGN_ACTION: tuple[tuple[str, str], ...] = (
    ("knockout", "M5"), ("delet", "M5"), ("Δ", "M5"), ("competing", "M5"), ("byproduct", "M5"), ("by-product", "M5"),
    ("feedback", "M3"), ("feedforward", "M3"), ("derepress", "M3"), ("deregulat", "M3"), ("point mutation", "M3"),
    ("rate-limiting", "M4"), ("rate limiting", "M4"), ("heterologous", "M4"), ("enzyme engineering", "M4"),
    ("promoter", "M6"), ("rbs", "M6"), ("copy number", "M6"), ("plasmid expression", "M6"),
    ("sensor", "M7"), ("dynamic control", "M7"), ("oscillat", "M7"),
    ("precursor", "M2"), ("cofactor", "M2"), ("nadh", "M2"), ("nadph", "M2"),
    ("de novo pathway", "M1"), ("pathway construction", "M1"), ("retropath", "M1"),
    ("fermentation", "M9"), ("medium", "M9"), ("induction", "M9"), ("fed-batch", "M9"), ("bioreactor", "M9"),
)


def _infer_design_action_from_text(text: str) -> str | None:
    """Best-effort module inference from a free-text description. Returns
    None (never a guess) when nothing matches, so the caller's own pending
    human-review flag still fires."""
    lowered = text.lower()
    for keyword, module in _TEXT_TO_DESIGN_ACTION:
        if keyword.lower() in lowered:
            return module
    return None


# E. coli gene symbols: 3-4 lowercase letters optionally followed by an
# uppercase letter/digits denoting the operon member (trpE, tktAB, aceE,
# gapA, lysC). Deliberately narrow — a missed gene falls through to the
# pending-review flag rather than a wrong match from a broader pattern.
_GENE_SYMBOL_RE = re.compile(r"\bΔ?([a-z]{3,4}[A-Z]{1,3}\d?)\b")


def _extract_gene_symbol(text: str) -> str:
    """Pull the first E. coli-style gene symbol out of free text, or ''."""
    match = _GENE_SYMBOL_RE.search(text)
    return match.group(1) if match else ""


def _map_implementation(impl_raw: str) -> str:
    """Map intervention type/description to a standardized implementation method."""
    normalized = impl_raw.lower().replace(" ", "_").replace("-", "_")
    if not normalized:
        return "其他"
    # Direct match (short canonical tokens, e.g. "knockout")
    if normalized in INTERVENTION_TO_IMPLEMENTATION:
        return INTERVENTION_TO_IMPLEMENTATION[normalized]
    # Substring match against a longer free-text description (e.g. a full
    # `intervention` sentence). Only `key in normalized` makes sense here —
    # `normalized in key` would match any short/empty string against every
    # key, which is how every step used to fall through to the dict's first
    # entry ("knockout" → "KO") whenever impl_raw was "".
    for key, value in INTERVENTION_TO_IMPLEMENTATION.items():
        if key in normalized:
            return value
    return "其他"


def _normalized_haystack(data: dict[str, Any]) -> str:
    """Lowercased JSON dump with whitespace/hyphens collapsed to underscores,
    so snake_case heuristic keywords (``in_vitro_assay``, ``known_regulation``)
    also match the natural free-text phrasing ("in vitro assay", "known
    regulation") that Skill07's actual ``experiments`` records use — before
    this, every hard-evidence keyword containing an underscore could only
    ever match already-underscore-cased input, which real extracted text
    never is, silently disabling most of the hard/soft keyword list."""
    text = json.dumps(data, ensure_ascii=False).lower()
    return re.sub(r"[\s\-]+", "_", text)


def _auto_evidence_grade(data: dict[str, Any]) -> str | None:
    """Heuristic evidence grading — returns '硬', '软', or None if unclear.

    These heuristics are deliberately conservative. They only flag clear cases;
    borderline cases return None → human must decide.
    """
    evidence_text = _normalized_haystack(data)

    hard_hits = sum(1 for kw in EVIDENCE_GRADING_HEURISTICS["硬"] if kw in evidence_text)
    soft_hits = sum(1 for kw in EVIDENCE_GRADING_HEURISTICS["软"] if kw in evidence_text)

    if hard_hits >= 3 and soft_hits == 0:
        return "硬"
    if soft_hits >= 2 and hard_hits == 0:
        return "软"
    if hard_hits > soft_hits * 2:
        return "硬"
    if soft_hits > hard_hits * 2:
        return "软"
    return None  # borderline → human review


def _auto_reason_nature(data: dict[str, Any], fields: dict[str, Any]) -> str:
    """Heuristic reason_nature classification.

    Conservative in the same direction as _auto_evidence_grade: only an
    explicit textual signal earns a positive classification. The default is
    NOT "机理推断" — 老师 §4.1 explicitly warns against forcing a paper
    without a clean, mechanism-stated decision chain into a mechanism-
    sounding rule ("硬把这类论文凑成一条听起来合理的规则,会用事后编造的
    理由污染规则库"). A record with no mechanistic language detected
    defaults to "事后合理化存疑" (post-hoc/uncertain), which — via
    _build_single_step's `if reason_nature not in (机理推断, 文献类比):
    rule = None` — also suppresses rule generation until a human confirms
    otherwise. The auto-classification is ALWAYS flagged for human review in
    the pending list regardless of which branch is taken.
    """
    text = _normalized_haystack(data)

    if any(kw in text for kw in SCREENING_KEYWORDS):
        return "筛选得来"
    if any(kw in text for kw in LITERATURE_ANALOGY_KEYWORDS):
        return "文献类比"
    if any(kw in text for kw in AVAILABLE_RESOURCE_KEYWORDS):
        return "现成可得"
    if any(kw in text for kw in MECHANISTIC_KEYWORDS):
        return "机理推断"

    return "事后合理化存疑"


def _infer_categories(fields: dict[str, Any]) -> list[str]:
    """Infer category tags from fields."""
    cats = fields.get("category", [])
    if not cats:
        product = fields.get("target_product", "")
        product_class = fields.get("product_class", "")
        if product:
            cats.append(f"{product} production")
        if product_class:
            cats.append(product_class)
    return cats or ["unknown"]


def _infer_problem_types(chain: list[dict[str, Any]]) -> list[str]:
    """Infer problem types from the decision chain's design_actions."""
    types = set()
    for step in chain:
        da = step.get("design_action", "")
        if da == "M3":
            types.add("feedback inhibition")
        elif da == "M5":
            types.add("competing pathway")
        elif da == "M2":
            types.add("precursor limitation")
        elif da == "M1":
            types.add("pathway construction")
        elif da == "M4":
            types.add("enzyme activity bottleneck")
    return sorted(types)


def _infer_trigger_conditions(chain: list[dict[str, Any]]) -> list[str]:
    """Infer trigger conditions from decision chain observations."""
    return [step["trigger"]["observation"][:120] for step in chain if step["trigger"]["observation"]]


def _format_authors(authors: list[str] | str) -> str:
    """Normalize author list to a single string."""
    if isinstance(authors, str):
        return authors
    if len(authors) <= 5:
        return ", ".join(authors)
    return f"{authors[0]} et al."


# ---------------------------------------------------------------------------
# ID allocation and persistence
# ---------------------------------------------------------------------------


def _allocate_ddr_id() -> str:
    """Allocate the next DDR-XXX id by scanning the existing knowledge base."""
    existing = set()
    if DDR_DIR.is_dir():
        for f in DDR_DIR.glob("DDR-*.json"):
            match = re.match(r"DDR-(\d+)", f.stem)
            if match:
                existing.add(int(match.group(1)))
    next_id = max(existing) + 1 if existing else 6  # 1–5 already exist
    return f"DDR-{next_id:03d}"


def _save_ddr(ddr: dict[str, Any]) -> Path:
    """Persist a converted DDR to the knowledge base directory."""
    DDR_DIR.mkdir(parents=True, exist_ok=True)
    ddr_id = ddr["ddr_id"]
    # Create a safe filename from title
    title = ddr.get("metadata", {}).get("title", "")
    safe_title = re.sub(r"[^\w\s-]", "", title.lower())[:50].strip().replace(" ", "_") or "untitled"
    path = DDR_DIR / f"{ddr_id}_{safe_title}.json"
    path.write_text(json.dumps(ddr, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def _get_nested(d: dict[str, Any], key: str, default: Any = None) -> Any:
    """Safely get a nested key from a dict that might not be a dict."""
    if not isinstance(d, dict):
        return default
    return d.get(key, default)


# ---------------------------------------------------------------------------
# Batch conversion entry point (used by the tool)
# ---------------------------------------------------------------------------


def batch_convert_from_task(
    task_id: str,
    *,
    auto_save: bool = False,
) -> list[DDRConversionResult]:
    """Convert all papers from a paper_extraction task into DDR format.

    This is the main entry point called by the synbio tool or directly from
    the paper_extraction API.

    Parameters
    ----------
    task_id:
        The paper_extraction task ID (from ``harness.paper_extraction.service``).
    auto_save:
        If True, save each DDR to disk immediately.

    Returns
    -------
    list[DDRConversionResult]
        One result per paper in the task.
    """
    from harness.paper_extraction.service import get_result, get_status

    status = get_status(task_id)
    if status.get("status") != "completed":
        raise ValueError(f"task {task_id} is not completed (status={status.get('status')})")

    full_result = get_result(task_id)
    if full_result is None:
        raise ValueError(f"task {task_id} has no result")

    results: list[DDRConversionResult] = []

    # Case 1: single-paper result
    output = full_result.get("output", {})
    if isinstance(output, dict) and (output.get("fields") or output.get("experimental_design_object")):
        result = convert_extraction_to_ddr(
            {"output": output},
            extraction_task_id=task_id,
            auto_save=auto_save,
        )
        results.append(result)

    # Case 2: multi-paper result (paper_artifacts array)
    paper_artifacts = full_result.get("paper_artifacts", [])
    for artifact in paper_artifacts:
        art_output = artifact.get("output") or artifact.get("extraction_result") or artifact
        if isinstance(art_output, dict):
            result = convert_extraction_to_ddr(
                {"output": art_output, "paper_identity": artifact.get("paper_identity", {})},
                extraction_task_id=task_id,
                auto_save=auto_save,
            )
            results.append(result)

    return results


# ---------------------------------------------------------------------------
# Literature-evidence auto-save (used by the paper_extraction API route)
# ---------------------------------------------------------------------------


def _existing_saved_indices(task_id: str) -> dict[int, str]:
    """``{paper_index: ddr_id}`` for DDRs already saved from this task.

    Scans the knowledge base once per call rather than maintaining a
    separate index file - ``knowledge/ddr_database/`` is small and this is
    only called on task-completion polls, not on every request.
    """
    out: dict[int, str] = {}
    if not DDR_DIR.is_dir():
        return out
    for f in DDR_DIR.glob("DDR-*.json"):
        try:
            rec = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        meta = rec.get("extraction_meta", {})
        if meta.get("paper_extraction_task_id") == task_id and meta.get("paper_index") is not None:
            out[meta["paper_index"]] = rec.get("ddr_id")
    return out


def ensure_task_saved_as_evidence(task_id: str) -> list[dict[str, Any]]:
    """Idempotently save every paper of a completed task as a literature-
    evidence DDR record, and return each paper's resulting evidence id.

    Safe to call repeatedly (e.g. on every completed-task poll from the
    paper_extraction API route): papers already saved for this ``task_id``
    (tracked via ``extraction_meta.paper_index``) are returned as-is rather
    than converted/saved again.

    Returns
    -------
    list[dict[str, Any]]
        One entry per paper: ``{"paper_index": int, "evidence_source_id": str}``.
    """
    from harness.paper_extraction.result_summary import build_extraction_summary
    from harness.paper_extraction.service import get_result, get_status

    status = get_status(task_id)
    if status.get("status") != "completed":
        return []

    full_result = get_result(task_id)
    if full_result is None:
        return []

    # `full_result` is `WorkflowEngine._report()`'s shape (see workflow/
    # engine.py's `_report` method), not a raw per-paper "output"/
    # "paper_artifacts" envelope - `experimental_designs` is literally
    # `context.skill07` (one entry per paper, each already the skill07
    # `output` dict: fields/experimental_design_object/extensions/
    # field_metadata/conflicts), the same list `result_summary.
    # build_extraction_summary` reads as `skill07_list`, so indices line
    # up 1:1 with `summary_papers` below.
    experimental_designs = full_result.get("experimental_designs", [])
    entries: list[tuple[int, dict[str, Any]]] = [
        (i, {"output": ed})
        for i, ed in enumerate(experimental_designs)
        if isinstance(ed, dict) and (ed.get("fields") or ed.get("experimental_design_object"))
    ]

    summary = build_extraction_summary(task_id) or {}
    summary_papers: list[dict[str, Any]] = summary.get("papers", [])
    already = _existing_saved_indices(task_id)

    results: list[dict[str, Any]] = []
    for i, extraction_output in entries:
        if i in already:
            results.append({"paper_index": i, "evidence_source_id": already[i]})
            continue
        detail = summary_papers[i] if i < len(summary_papers) else None
        identity = (detail or {}).get("identity")
        if identity:
            extraction_output = {**extraction_output, "paper_identity": identity}
        conv = convert_extraction_to_ddr(
            extraction_output,
            extraction_task_id=task_id,
            paper_index=i,
            paper_extraction_detail=detail,
            auto_save=True,
        )
        results.append({"paper_index": i, "evidence_source_id": conv.ddr["ddr_id"]})
    return results


# ---------------------------------------------------------------------------
# Idea Workbench view (used by the paper_extraction API's /knowledge-ideas route)
# ---------------------------------------------------------------------------

# design_action module code -> ExtractedIdea category (frontend/src/api/
# paperExtraction.ts's `ExtractedIdea["category"]`), reusing the same M1-M9
# vocabulary MODULE_TO_DESIGN_ACTION above already maps intervention types
# into, so this needs no separate keyword classifier of its own.
_DESIGN_ACTION_CATEGORY: dict[str, str] = {
    "M1": "metabolism", "M2": "metabolism", "M9": "metabolism",
    "M3": "regulation", "M7": "regulation",
    "M4": "protein",
    "M5": "genome",
    "M6": "expression",
}


def _category_for_decision_chain(decision_chain: list[dict[str, Any]]) -> str:
    """Best-effort idea category for one DDR, majority-voted across its own
    decision_chain steps' design_action codes - falls back to "other" for a
    DDR with no decision_chain steps at all."""
    if not decision_chain:
        return "other"
    votes = Counter(_DESIGN_ACTION_CATEGORY.get(step.get("design_action", ""), "other") for step in decision_chain)
    return votes.most_common(1)[0][0]


def ddr_to_idea_view(rec: dict[str, Any]) -> dict[str, Any]:
    """Reshapes one DDR record already sitting in the knowledge base into the
    same "extracted idea" card shape the Idea Workbench renders for a live
    paper_extraction run's experimental_designs (`toExtractedIdeas` in
    frontend/src/api/paperExtraction.ts) - so a DDR from *any* past run
    (any project, any upload) can populate the workbench without requiring a
    fresh retrieval run scoped to this one project. Read-only view over
    fields the DDR already has; never fabricates a summary/title the record
    doesn't already contain (same discipline as `rule_as_knowledge_claim_view`
    in `rule_distillation.py`)."""
    meta = rec.get("metadata", {})
    ref = meta.get("reference", {})
    problem = rec.get("engineering_problem", {})
    diagnosis = rec.get("biological_diagnosis", {})
    hypothesis = rec.get("engineering_hypothesis", {})
    decision_chain = rec.get("decision_chain", [])
    summary = (
        hypothesis.get("hypothesis")
        or diagnosis.get("mechanistic_explanation")
        or next(iter(diagnosis.get("observations") or []), "")
    )
    ddr_id = rec.get("ddr_id", "")
    return {
        "idea_id": ddr_id,
        "title": problem.get("problem_statement") or meta.get("title") or ddr_id,
        "summary": summary,
        "category": _category_for_decision_chain(decision_chain),
        "source": {
            "paper_id": ddr_id,
            "title": ref.get("title") or meta.get("title", ""),
            "journal": ref.get("journal", ""),
            "year": str(ref.get("year", "")),
            "doi": ref.get("doi", ""),
        },
        "evidence_ids": [f"{ddr_id}:{step.get('step')}" for step in decision_chain],
    }
