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
import copy
import uuid
from collections import Counter
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

from harness.config import PROJECT_ROOT
from harness.paper_extraction.contracts import (
    canonical_reason_nature as _contract_reason_nature,
    load_validation_rules,
)
from harness.paper_extraction.knowledge_sync import sync_after_save

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

# decision_type keyword heuristics (0804 优化 §3 Phase 3 / §7 Q1-Q3 filter).
# A candidate step is "engineering_decision" (enters decision_chain) only if
# none of these signals fire — same conservative direction as the grading
# heuristics above: a positive match on a *narrower* category always wins
# over the default. Checked in this order: background (Q2) > post_hoc (needs
# BOTH a post-hoc-context signal and a no-new-action signal) > validation
# (Q1/Q3) > engineering_decision.
BACKGROUND_KEYWORDS = (
    "constructed previously", "constructed in previous studies",
    "constructed in prior", "as previously described", "as described previously",
    "in our previous study", "in our previous work", "in a previous study",
    "in previous studies", "previously constructed", "background construct",
    "not applicable (constructed",
)
NO_NEW_ACTION_KEYWORDS = (
    "none (characterization)", "none (computational", "none (observational",
    "none beyond", "no new modification", "none (in silico)",
)
VALIDATION_KEYWORDS = (
    "verify that", "verify the", "validate that", "validate the",
    "confirm that", "confirm the", "evaluate the performance of",
    "phenotype validation", "assess the performance",
)
POST_HOC_SIGNAL_KEYWORDS = (
    "docking", "structure-based", "structural analysis", "structural effect",
    "homology model", "genome sequenc", "genomic analysis", "whole genome", "wgs",
)

# ---------------------------------------------------------------------------
# Engineering paper-type classification (0804 优化_2 §3/§4, SKILL.md §3.1) —
# paper-level, not per-step. design_action is the primary signal (every
# retained decision_chain step already has one); keyword overrides catch the
# two categories no M-code maps to directly (protein_engineering vs. plain
# M4 enzyme work, chassis_engineering) and disambiguate M4 between "swapped
# in a rate-limiting enzyme" (metabolic) and "engineered the enzyme itself"
# (protein). Order matters: keyword overrides checked before the M-code
# default so an M4 step described with mutagenesis language routes to
# protein_engineering instead of the metabolic_engineering default.
BIOSENSOR_TYPE_KEYWORDS = ("biosensor", "genetic circuit", "regulatory switch", "dynamic control", "dose-response")
PROTEIN_ENG_TYPE_KEYWORDS = (
    "enzyme variant", "directed evolution", "structure-guided", "site-directed mutagenesis",
    "point mutation", "protein engineering", "rational design of the enzyme",
)
CHASSIS_TYPE_KEYWORDS = ("chassis engineering", "host redesign", "tolerance engineering", "genome reduction", "minimal genome")
EVOLUTIONARY_TYPE_KEYWORDS = SCREENING_KEYWORDS  # library/screening/ALE/directed_evolution — already defined above

_DESIGN_ACTION_TO_ENGINEERING_PAPER_TYPE: dict[str, str] = {
    "M0": "metabolic_engineering", "M1": "metabolic_engineering", "M2": "metabolic_engineering",
    "M3": "metabolic_engineering", "M4": "metabolic_engineering", "M5": "metabolic_engineering",
    "M6": "metabolic_engineering", "M8": "metabolic_engineering", "M9": "metabolic_engineering",
    "M7": "biosensor_platform", "M11": "evolutionary_engineering",
}

_VALID_ENGINEERING_PAPER_TYPES = frozenset({
    "metabolic_engineering", "biosensor_platform", "evolutionary_engineering",
    "protein_engineering", "chassis_engineering", "multi_strategy",
})
_VALID_CALIBRATION_STATUSES = frozenset({"auto_accepted", "needs_review", "rejected"})

# Rule Scope Validator (0804 优化_2 §12): a rule containing one of these
# over-broad scope phrases claims more than a single paper's decision_chain
# can support and must be flagged for human review, never silently trusted
# or silently rewritten (rewriting a claim it didn't verify is itself a
# fabrication risk - flagging is the safe action here).
BROAD_RULE_SCOPE_KEYWORDS = (
    "all amino acid", "all amino acids", "any product", "all products",
    "all metabolic", "universally", "所有氨基酸", "任何产物", "所有产物", "普遍适用",
)

# ---------------------------------------------------------------------------
# Engineering Strategy Ontology (0804 优化_3 §13/§14) — controlled vocabulary
# a decision_chain step maps into, collapsing synonymous phrasing across
# papers (e.g. "dynamic regulation"/"dynamic control"/"feedback regulation"/
# "metabolite-responsive control" all → dynamic_control) onto §14's fixed
# category names. A step can map to more than one category; unmatched steps
# get an empty list rather than a forced guess.
STRATEGY_ONTOLOGY_KEYWORDS: dict[str, tuple[str, ...]] = {
    "flux_redirection": ("flux redistribution", "redirect carbon flux", "flux redirection", "carbon flux"),
    "precursor_supply_enhancement": ("precursor supply", "precursor availability", "increase precursor", "cofactor balancing", "nadph supply", "nadh supply"),
    "competitive_pathway_removal": ("competing pathway", "competing byproduct", "byproduct pathway", "eliminate competing", "knockout of ldha", "knockout of adhe"),
    "dynamic_control": (
        "dynamic regulation", "dynamic control", "feedback regulation", "feedback control",
        "metabolite-responsive control", "metabolite-responsive", "biosensor", "autonomous regulation", "dynamic pathway",
    ),
    "enzyme_activity_improvement": ("rate-limiting enzyme", "rate limiting enzyme", "enzyme engineering", "enzyme activity", "kinetic improvement", "resist feedback inhibition"),
    "transport_engineering": ("glucose uptake", "transporter", "galp", "pts", "membrane transport", "substrate uptake"),
    "stress_tolerance_engineering": ("tolerance engineering", "stress tolerance", "toxicity management", "solvent tolerance", "acid tolerance"),
    "evolutionary_optimization": ("adaptive laboratory evolution", "directed evolution", "screening", "ale ", "genome evolution"),
}
_VALID_STRATEGY_CATEGORIES = frozenset(STRATEGY_ONTOLOGY_KEYWORDS.keys())

# ---------------------------------------------------------------------------
# Rule Provenance System (0804 优化_3 §9-§12).
# ---------------------------------------------------------------------------
_VALID_RULE_SOURCES = frozenset({"single_paper", "multi_paper_supported", "textbook_mechanism", "expert_curated"})
_VALID_RULE_CONFIDENCES = frozenset({"high", "medium", "low"})
_VALID_EDGE_RELATIONS = frozenset({"triggered_by", "solves", "alternative_to", "validated_by", "depends_on"})

# Cross-paper rule similarity: plain token-overlap (Jaccard-style), not an
# embedding search - conservative on purpose, mirrors _find_existing_ddr's
# "no fuzzy matching, a false positive is worse than a false negative" stance.
_RULE_STOPWORDS = frozenset({
    "the", "a", "an", "of", "in", "to", "for", "and", "or", "with", "by", "on", "when", "apply",
    "because", "this", "that", "is", "are", "may", "can", "improve", "increase", "reduce",
})
_RULE_SIMILARITY_THRESHOLD = 0.5


def _rule_tokens(rule_text: str) -> set[str]:
    words = re.findall(r"[a-zA-Z一-鿿]+", rule_text.lower())
    return {w for w in words if w not in _RULE_STOPWORDS and len(w) > 2}


# Failure-driven reasoning (0804 优化_3 §8): text signals that the previous
# step's outcome was a setback rather than progress - used to add a `solves`
# edge (this step solves that setback) on top of the deterministic
# `triggered_by` edge, and to populate failure_points.
FAILURE_SIGNAL_KEYWORDS = (
    "suppressed", "severely", "impaired", "growth defect", "defect", "declined",
    "did not increase", "no improvement", "growth-product tradeoff", "inhibited growth",
    "toxic", "toxicity", "reduced growth", "lower productivity",
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
_SKILL07_VALIDATION_RULES = load_validation_rules(
    Path(__file__).with_name("contracts") / "skill07_validation_rules.yaml"
)
_REASON_NATURE_RULES = _SKILL07_VALIDATION_RULES["ddr_validation"]["reason_nature"]
_VALID_REASON_NATURES = frozenset(
    [*_REASON_NATURE_RULES["canonical_values"], *_REASON_NATURE_RULES["legacy_aliases"]]
)
_RULE_ELIGIBLE_REASON_NATURES = frozenset(
    _SKILL07_VALIDATION_RULES["generalizable_rule_validation"]["allowed_reason_nature"]
)
_VALID_DECISION_TYPES = frozenset({"engineering_decision", "validation", "background", "post_hoc_interpretation"})


def _canonical_reason(value: Any) -> str | None:
    """Map accepted legacy labels to the contract's canonical vocabulary."""
    return _contract_reason_nature(value, _SKILL07_VALIDATION_RULES)


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
    from harness.paper_extraction.knowledge_admission import require_admissible_skill08

    warnings: list[str] = []
    pending: list[str] = []
    skill08_output = extraction_output.get("skill08_output")
    skill08_provenance = extraction_output.get("skill08_provenance")
    admission = None
    if auto_save:
        admission = require_admissible_skill08(skill08_output, skill08_provenance)
        admitted = copy.deepcopy(skill08_output.get("candidate_payload") or {})
        allowed_fields = set(admission.get("admitted_field_claims") or [])
        admitted["fields"] = {k: v for k, v in (admitted.get("fields") or {}).items() if k in allowed_fields}
        allowed_ddrs = set(admission.get("admitted_ddr_candidates") or [])
        design = admitted.get("experimental_design_object") or {}
        if isinstance(design, dict) and isinstance(design.get("experiments"), list):
            design["experiments"] = [exp for i, exp in enumerate(design["experiments"]) if f"experiment:{i}:ddr" in allowed_ddrs]
        elif isinstance(design, list):
            admitted["experimental_design_object"] = [exp for i, exp in enumerate(design) if f"experiment:{i}:ddr" in allowed_ddrs]
        extraction_output = {**extraction_output, "output": admitted}

    # -- Step 1: Extract core output -------------------------------------------------
    output = _get_nested(extraction_output, "output", default={})
    fields = output.get("fields", {}) if isinstance(output, dict) else {}
    ed_obj = output.get("experimental_design_object", {}) if isinstance(output, dict) else {}
    # Skill07 may represent multiple experiments directly as a list instead
    # of wrapping them in {"experiments": [...]}. Normalize both valid
    # model-output shapes before the DDR builders consume the object.
    if isinstance(ed_obj, list):
        ed_obj = {"experiments": [item for item in ed_obj if isinstance(item, dict)]}
    elif not isinstance(ed_obj, dict):
        ed_obj = {}
    extensions = output.get("extensions", {}) if isinstance(output, dict) else {}
    gate = extensions.get("article_type_gate", {})

    if not fields and not ed_obj:
        warnings.append("extraction_output has neither 'fields' nor 'experimental_design_object'; DDR may be sparse")

    # -- Step 2: Build metadata ------------------------------------------------------
    metadata = _build_metadata(extraction_output, fields, gate, warnings)

    # -- Step 3: Build decision_chain -------------------------------------------------
    decision_chain, excluded_records = _build_decision_chain(extraction_output, fields, ed_obj, warnings, pending)

    # -- Step 4: Build paper-level context (v1 compat) --------------------------------
    problem = _build_engineering_problem(fields, ed_obj, decision_chain)
    diagnosis = _build_biological_diagnosis(fields, ed_obj, decision_chain)
    hypothesis = _build_engineering_hypothesis(fields, ed_obj, decision_chain)

    # -- Step 4.5: Reasoning layer (0804 优化_2, additive on top of V2) ---------------
    engineering_paper_type, engineering_paper_type_rationale = _classify_engineering_paper_type(decision_chain, extensions)
    decision_map = _build_engineering_decision_map(decision_chain, problem, diagnosis, hypothesis)
    reasoning_overview = _build_paper_reasoning_overview(engineering_paper_type, decision_map)
    calibration_report = _build_human_calibration_report(decision_chain)

    # -- Step 4.6: Knowledge representation layer (0804 优化_3, additive on top of V2.1) --
    decision_graph = _build_engineering_decision_graph(decision_chain, excluded_records)
    failure_points = _build_failure_points(decision_chain)
    logic_chain = _build_engineering_logic_chain(decision_map, failure_points)

    # -- Step 5: Build extraction_meta ------------------------------------------------
    extraction_meta = _build_extraction_meta(
        pending, extraction_task_id, paper_index, paper_extraction_detail,
        engineering_paper_type=engineering_paper_type,
        engineering_paper_type_rationale=engineering_paper_type_rationale,
    )

    # -- Step 6: Assemble DDR ---------------------------------------------------------
    # Re-extracting a paper already in the knowledge base (same DOI, or same
    # title when no DOI) reuses that paper's ddr_id instead of allocating a
    # new one, so _save_ddr overwrites it - "only the latest extraction is
    # kept" rather than accumulating duplicates every time a paper is
    # (re-)submitted (see the DDR-006/007 and DDR-009/012/015 duplicates
    # this replaced).
    existing = _find_existing_ddr(metadata.get("reference", {}))
    if existing is not None:
        ddr_id = existing.get("ddr_id") or _allocate_ddr_id()
        prev_task_id = existing.get("extraction_meta", {}).get("paper_extraction_task_id")
        if prev_task_id and prev_task_id != extraction_task_id:
            extraction_meta["previous_extraction_task_id"] = prev_task_id
    else:
        ddr_id = _allocate_ddr_id()

    # rule_source's cross-paper scan and the graph nodes' source_ddr_id both
    # need ddr_id, which only exists from this point on - see the placeholder
    # comments in _build_single_step / _build_engineering_decision_graph.
    _apply_rule_provenance(decision_chain, ddr_id)
    for node in decision_graph["nodes"]:
        node["source_ddr_id"] = ddr_id
    rule_provenance = _build_rule_provenance(decision_chain)

    ddr = {
        "ddr_id": ddr_id,
        "schema_version": "2.0",
        "metadata": metadata,
        "decision_chain": decision_chain,
        "excluded_records": excluded_records,
        "engineering_problem": problem,
        "biological_diagnosis": diagnosis,
        "engineering_hypothesis": hypothesis,
        "extraction_meta": extraction_meta,
        "engineering_decision_map": decision_map,
        "paper_reasoning_overview": reasoning_overview,
        "human_calibration_report": calibration_report,
        "engineering_decision_graph": decision_graph,
        "engineering_logic_chain": logic_chain,
        "rule_provenance": rule_provenance,
        "knowledge_admission": ({
            **admission,
            "source_skill08_artifact_id": skill08_provenance.get("skill08_artifact_id"),
            "source_skill07_artifact_id": skill08_provenance.get("source_skill07_artifact_id"),
            "document_artifact_id": skill08_provenance.get("document_artifact_id"),
            "document_hash": skill08_provenance.get("document_hash"),
        } if admission else {"status": "NOT_EVALUATED", "persistent": False}),
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


_EXCLUSION_REASON_BY_TYPE = {
    "validation": "Q1/Q3 未通过：只验证/表征已选定的设计，未包含新的改造动作或未引出新的策略选择",
    "background": "Q2 未通过：本文引用/沿用此前研究已构建的底盘或元件，非本文完成的设计决策",
    "post_hoc_interpretation": "Q1 未通过：Discussion/结构分析/docking/基因组测序等事后解释，未驱动本文的工程决策",
}


def _build_decision_chain(
    extraction_output: dict[str, Any],
    fields: dict[str, Any],
    ed_obj: dict[str, Any],
    warnings: list[str],
    pending: list[str],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Build the decision_chain (and excluded_records) from extraction output.

    Uses experimental_design_object's intervention/experiment list as the primary
    source for decision steps. Falls back to extracting from fields.

    Every candidate is first built into a full step record (see
    _build_single_step), then partitioned by its `decision_type` (0804 优化
    §3 Phase 3 Q1/Q2/Q3 filter): only `engineering_decision` steps stay in
    `decision_chain` and get renumbered 1..N contiguously so the saved chain
    reads as a clean decision sequence with no gaps; validation/background/
    post_hoc_interpretation steps move to `excluded_records` instead, keeping
    their original step index inside `step_snapshot` for traceability but
    never occupying a decision_chain slot or contributing a rule.
    """
    chain: list[dict[str, Any]] = []
    excluded: list[dict[str, Any]] = []

    # Primary source: experimental_design_object with explicit interventions
    experiments = ed_obj.get("experiments", [])
    interventions = ed_obj.get("interventions", [])
    design_steps = ed_obj.get("design_steps", [])

    # Combine all potential step sources
    step_candidates = _collect_step_candidates(fields, ed_obj, experiments, interventions, design_steps)

    if not step_candidates:
        warnings.append("no step candidates found in extraction output; decision_chain will be empty")
        return chain, excluded

    # Design doc §4.1: a decision step's trigger is "what observation caused
    # this action" — usually the *previous* step's result, not the paper's
    # abstract. Tracked across the loop so step i>1 can point at step i-1's
    # outcome instead of leaving trigger.observation blank whenever the
    # source record has no explicit per-step observation field of its own
    # (true for Skill07's flat experiment records — see _build_single_step).
    # Threaded across *all* candidates (not just retained ones) so a filtered
    # background/validation step's outcome can still serve as the next real
    # engineering step's trigger — excluding a step from decision_chain
    # doesn't erase it from the paper's actual causal sequence.
    prev_outcome = ""
    raw_steps: list[dict[str, Any]] = []
    for i, candidate in enumerate(step_candidates, start=1):
        step = _build_single_step(i, candidate, fields, pending, prev_outcome=prev_outcome)
        raw_steps.append(step)
        prev_outcome = step["result"].get("after") or prev_outcome

    next_step_num = 1
    for step in raw_steps:
        if step["decision_type"] == "engineering_decision":
            step["step"] = next_step_num
            next_step_num += 1
            chain.append(step)
        else:
            excluded.append({
                "decision_type": step["decision_type"],
                "exclusion_reason": _EXCLUSION_REASON_BY_TYPE.get(step["decision_type"], ""),
                "step_snapshot": step,
            })

    return chain, excluded


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

    # (c) Experiments (from Skill07 extraction).  Two shapes are emitted in
    # practice: the legacy singular ``intervention`` string and a richer
    # ``interventions`` list whose items carry their own DDR annotations.
    # Treat every item in the latter as a decision candidate while inheriting
    # the experiment-level host/conditions/readouts/outcome context.
    for exp in experiments:
        if exp.get("intervention") and exp.get("purpose"):
            candidates.append({"source": "experiments", "data": exp})
            continue

        nested_interventions = exp.get("interventions") or []
        if not isinstance(nested_interventions, list):
            continue
        for intervention in nested_interventions:
            if not isinstance(intervention, dict):
                continue
            description = intervention.get("description") or intervention.get("intervention")
            if not description:
                continue
            data = {
                **exp,
                **intervention,
                "intervention": description,
                "readout": exp.get("readout") or exp.get("readouts", ""),
                "control": exp.get("control") or exp.get("controls", ""),
            }
            candidates.append({"source": "experiments", "data": data})

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
    canonical_reason = _canonical_reason(reason_nature)
    if canonical_reason not in _RULE_ELIGIBLE_REASON_NATURES:
        rule = None  # 不写出可能编造的规则
    elif rule:
        pending.append(f"step_{step_num}.rule: requires human calibration (dual-review process)")

    # --- decision_type: Q1/Q2/Q3 filter (0804 优化 §3 Phase 3 / §7) ---
    # Model self-assessment first (SKILL.md §5.5's own Q1/Q2/Q3 discipline),
    # falling back to the keyword heuristic exactly like every other field
    # above. This decides whether the step is a real engineering_decision
    # (stays in decision_chain) or gets filed under excluded_records as
    # validation/background/post_hoc_interpretation — see _build_decision_chain.
    model_decision_type = annotation.get("decision_type")
    if model_decision_type not in _VALID_DECISION_TYPES:
        model_decision_type = None
    step_haystack = " ".join(
        str(x).lower() for x in (
            intervention_text, purpose_text, trigger["observation"], trigger["reasoning"],
            target.get("condition") or "", impl_detail,
        )
    )
    evidence_desc = evidence.get("description")
    evidence_haystack = " ".join(str(x) for x in evidence_desc) if isinstance(evidence_desc, list) else str(evidence_desc or "")
    evidence_haystack = evidence_haystack.replace("_", " ").lower()

    # --- reason_nature_tags: additive multi-label (0804 优化_2 §9) ---
    # Only ever a *supplement* to `reason_nature` (never a replacement), and
    # only ever populated when the primary value already qualifies for rule
    # generation (机理推断/文献类比) — this is deliberate: rule-gating logic
    # elsewhere reads `reason_nature` (the single value), never this array,
    # so a screening-derived/post-hoc step can never gain rule eligibility by
    # having a stray "机理推断" keyword coincidentally land in its tags.
    model_reason_nature_tags = annotation.get("reason_nature_tags")
    if canonical_reason in _RULE_ELIGIBLE_REASON_NATURES and isinstance(model_reason_nature_tags, list):
        reason_nature_tags = [t for t in model_reason_nature_tags if t in _VALID_REASON_NATURES and t != reason_nature]
    elif canonical_reason in _RULE_ELIGIBLE_REASON_NATURES:
        # LITERATURE_ANALOGY_KEYWORDS/MECHANISTIC_KEYWORDS are underscore-cased
        # (e.g. "as_described_previously") to match `_normalized_haystack`'s
        # convention elsewhere in this module - re-normalize step_haystack the
        # same way here rather than matching against the raw space-separated
        # text, or these keyword lists silently never match anything.
        step_haystack_underscored = re.sub(r"[\s\-]+", "_", step_haystack)
        reason_nature_tags = []
        if canonical_reason == "mechanistic_inference" and any(kw in step_haystack_underscored for kw in LITERATURE_ANALOGY_KEYWORDS):
            reason_nature_tags.append("文献类比")
        if canonical_reason == "literature_analogy" and any(kw in step_haystack_underscored for kw in MECHANISTIC_KEYWORDS):
            reason_nature_tags.append("机理推断")
    else:
        reason_nature_tags = []

    auto_decision_type, auto_decision_type_reason = _auto_decision_type(step_haystack, evidence_haystack)
    if model_decision_type:
        decision_type = model_decision_type
        if auto_decision_type != model_decision_type:
            pending.append(
                f"step_{step_num}.decision_type: model self-assessment ({model_decision_type}) disagrees "
                f"with keyword heuristic ({auto_decision_type}) — flag for careful human review"
            )
    else:
        decision_type = auto_decision_type
        if decision_type != "engineering_decision":
            pending.append(f"step_{step_num}.decision_type: heuristic classified as {decision_type} ({auto_decision_type_reason}) — requires human confirmation")

    if decision_type != "engineering_decision":
        rule = None  # 只有 engineering_decision 才允许携带可迁移规则

    # --- strategy_categories: controlled vocabulary (0804 优化_3 §13/§14) ---
    model_strategy_categories = annotation.get("strategy_categories")
    if isinstance(model_strategy_categories, list):
        strategy_categories = sorted({c for c in model_strategy_categories if c in _VALID_STRATEGY_CATEGORIES})
    else:
        strategy_categories = []
    if not strategy_categories:
        strategy_categories = sorted({
            category for category, keywords in STRATEGY_ONTOLOGY_KEYWORDS.items()
            if any(kw in step_haystack for kw in keywords)
        })

    # --- rule provenance placeholders (0804 优化_3 §9-§12) ---
    # rule_source needs to exclude *this paper's own* already-saved DDR file
    # when scanning the knowledge base for similar rules (otherwise
    # re-extracting the same paper would "discover" its own prior save as a
    # second supporting paper) - but the ddr_id isn't allocated yet at this
    # point in the pipeline (see convert_extraction_to_ddr's Step 6). Left as
    # placeholders here and filled in by _apply_rule_provenance once the
    # ddr_id is known, exactly like source_ddr_id on the decision graph nodes.
    rule_source = None
    rule_confidence = None
    supporting_ddr: list[str] = []

    # --- calibration_status: per-step uncertainty flag (0804 优化_2 §7/§8/§12) ---
    # Distinct from extraction_meta.calibration_status (paper-level, dual-
    # annotator agreement) - this is single-annotator, single-step "should a
    # human look at this before trusting it downstream".
    calibration_reasons: list[str] = []
    if decision_type == "engineering_decision" and any(
        f"step_{step_num}.design_action: unable to map" in p for p in pending
    ) and not (target["gene"] or target["enzyme"] or target["pathway"]):
        calibration_status, calibration_reason = "rejected", (
            "engineering_decision 步骤既未能确定 design_action 也未提取到 target（基因/酶/通路），抽取失败，不应作为可信 DDR 使用"
        )
    else:
        if reason_nature_tags:
            calibration_reasons.append("reason_nature 存在多个标签（Case 1），需人工确认是否两者都成立")
        if decision_type == "engineering_decision" and any(kw in step_haystack or kw in evidence_haystack for kw in POST_HOC_SIGNAL_KEYWORDS):
            calibration_reasons.append("命中结构分析/docking/基因组测序等事后解释信号但仍判定为 engineering_decision（Case 2），需人工复核该分类本身")
        if rule and any(kw in rule.lower() for kw in BROAD_RULE_SCOPE_KEYWORDS):
            calibration_reasons.append("rule 命中过宽泛的适用范围用词（Case 3），可能超出本文证据范围，需人工确认")
        if calibration_reasons:
            calibration_status, calibration_reason = "needs_review", "; ".join(calibration_reasons)
        else:
            calibration_status, calibration_reason = "auto_accepted", ""

    return {
        "step": step_num,
        "decision_type": decision_type,
        "design_action": design_action,
        "target": target,
        "trigger": trigger,
        "evidence": evidence,
        "evidence_grading": evidence_grading,
        "evidence_grading_rationale": grading_rationale,
        "reason_nature": reason_nature,
        "reason_nature_tags": reason_nature_tags,
        "alternatives": alternatives,
        "implementation": implementation,
        "implementation_detail": impl_detail,
        "result": result,
        "rule": rule,
        "rule_source": rule_source,
        "rule_confidence": rule_confidence,
        "supporting_ddr": supporting_ddr,
        "strategy_categories": strategy_categories,
        "calibration_status": calibration_status,
        "calibration_reason": calibration_reason,
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


# ---------------------------------------------------------------------------
# Reasoning layer (0804 优化_2, additive on top of V2's decision_type filter)
# ---------------------------------------------------------------------------


def _step_engineering_paper_type(step: dict[str, Any]) -> str | None:
    """Best-effort engineering-strategy category for one decision_chain step.

    Keyword overrides are checked before the design_action default so a
    step whose implementation_detail reads as protein engineering or
    chassis engineering doesn't get swallowed by the generic M-code
    default. Returns None (never a guess) when nothing matches."""
    target = step.get("target") or {}
    text = " ".join(str(x).lower() for x in (
        step.get("implementation_detail") or "", target.get("gene") or "",
        target.get("enzyme") or "", target.get("pathway") or "",
    ))
    if any(kw in text for kw in CHASSIS_TYPE_KEYWORDS):
        return "chassis_engineering"
    if any(kw in text for kw in BIOSENSOR_TYPE_KEYWORDS):
        return "biosensor_platform"
    if any(kw in text for kw in PROTEIN_ENG_TYPE_KEYWORDS):
        return "protein_engineering"
    if any(kw in text for kw in EVOLUTIONARY_TYPE_KEYWORDS):
        return "evolutionary_engineering"
    return _DESIGN_ACTION_TO_ENGINEERING_PAPER_TYPE.get(step.get("design_action", ""))


def _classify_engineering_paper_type(
    decision_chain: list[dict[str, Any]],
    extensions: dict[str, Any],
) -> tuple[list[str], str]:
    """Paper-level engineering-strategy classification (SKILL.md §3.1).

    Model self-assessment first (paper-level `extensions.engineering_paper_type`,
    validated against the same enum the DDR schema declares), falling back to
    a heuristic aggregated across the already-filtered decision_chain's
    design_action/implementation_detail — same model-first/heuristic-fallback
    pattern used everywhere else in this module. `multi_strategy` is a
    holistic judgment call about which strategies are *central* to the paper,
    not just present, so the heuristic never emits it on its own; it only
    passes it through when the model explicitly says so.
    """
    raw_model_types = extensions.get("engineering_paper_type")
    if isinstance(raw_model_types, list):
        model_types = sorted({t for t in raw_model_types if t in _VALID_ENGINEERING_PAPER_TYPES})
        if model_types:
            rationale = extensions.get("engineering_paper_type_rationale") or "模型自评(SKILL.md §3.1 engineering_paper_type)"
            return model_types, rationale

    if not decision_chain:
        return [], ""
    categories = {cat for step in decision_chain if (cat := _step_engineering_paper_type(step))}
    if not categories:
        return [], ""
    return sorted(categories), "基于 decision_chain 的 design_action/implementation_detail 关键词启发式判定——需人工确认"


def _build_engineering_decision_map(
    decision_chain: list[dict[str, Any]],
    problem: dict[str, Any],
    diagnosis: dict[str, Any],
    hypothesis: dict[str, Any],
) -> dict[str, Any]:
    """Human-readable reasoning chain connecting DDRs (0804 优化_2 §5/§6) —
    not the DDR itself. `decision_sequence` is a simplified projection of
    `decision_chain`, which V2's Q1/Q2/Q3 filter has already restricted to
    engineering_decision steps only, so no additional filtering is needed
    here (§6's "only include decision_type = engineering_decision" is
    already an invariant of decision_chain, not something this function has
    to re-check)."""
    initial_bottleneck = ""
    key_hypothesis = hypothesis.get("hypothesis", "")
    if decision_chain:
        # §6: the bottleneck must precede engineering, not be a post-hoc
        # result description - the first retained step's own trigger is by
        # construction the observation that existed before that first action.
        # trigger.observation is often empty for a true first step (there is
        # no prior step's outcome to draw from - see _build_decision_chain's
        # prev_outcome threading), so trigger.reasoning (the stated rationale
        # for that first action, still a pre-engineering constraint
        # statement) is tried next, before falling back to some other step's
        # diagnosis observation that isn't actually about the initial state.
        first_trigger = decision_chain[0]["trigger"]
        initial_bottleneck = first_trigger.get("observation", "") or first_trigger.get("reasoning", "")
        if not key_hypothesis:
            key_hypothesis = first_trigger.get("reasoning", "")
    if not initial_bottleneck:
        observations = diagnosis.get("observations") or []
        initial_bottleneck = observations[0] if observations else ""

    decision_sequence = [
        {
            "step": step.get("step"),
            "design_action": step.get("design_action", ""),
            "action_summary": step.get("implementation_detail") or step.get("implementation", ""),
        }
        for step in decision_chain
    ]

    return {
        "goal": problem.get("problem_statement", ""),
        "initial_bottleneck": initial_bottleneck,
        "key_hypothesis": key_hypothesis,
        "decision_sequence": decision_sequence,
    }


def _build_paper_reasoning_overview(
    engineering_paper_type: list[str],
    decision_map: dict[str, Any],
) -> dict[str, Any]:
    """Convenience projection for Part 1 ("Paper Reasoning Overview") -
    aggregates fields already computed elsewhere, introduces no new source
    of truth."""
    return {
        "paper_type": engineering_paper_type,
        "goal": decision_map.get("goal", ""),
        "initial_bottleneck": decision_map.get("initial_bottleneck", ""),
        "key_hypothesis": decision_map.get("key_hypothesis", ""),
    }


def _build_human_calibration_report(decision_chain: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate per-step calibration_status across decision_chain (Part 5).
    Scoped to decision_chain (real engineering decisions) rather than also
    including excluded_records - those are already visible as their own
    separately-labeled bucket and don't compete for the same review queue."""
    counts = Counter(step.get("calibration_status", "auto_accepted") for step in decision_chain)
    needs_review_steps = [
        {
            "step": step.get("step"),
            "calibration_status": step.get("calibration_status"),
            "calibration_reason": step.get("calibration_reason", ""),
        }
        for step in decision_chain
        if step.get("calibration_status") != "auto_accepted"
    ]
    return {
        "auto_accepted": counts.get("auto_accepted", 0),
        "needs_review": counts.get("needs_review", 0),
        "rejected": counts.get("rejected", 0),
        "needs_review_steps": needs_review_steps,
    }


# ---------------------------------------------------------------------------
# Knowledge representation layer (0804 优化_3): decision graph, failure-driven
# reasoning, rule provenance aggregate.
# ---------------------------------------------------------------------------


def _node_target_text(step: dict[str, Any]) -> str:
    target = step.get("target") or {}
    return target.get("gene") or target.get("enzyme") or target.get("pathway") or ""


def _build_engineering_decision_graph(
    decision_chain: list[dict[str, Any]],
    excluded_records: list[dict[str, Any]],
) -> dict[str, Any]:
    """Within-paper decision dependency graph (0804 优化_3 §2-§6).

    Only infers edges the data itself already supports - see
    schema_v2.json's engineering_decision_graph._relation_generation_notes
    for exactly which signal justifies each relation. `depends_on` is
    deliberately never auto-generated (documented there as a known
    limitation) rather than guessed from weak text overlap.
    """
    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    node_id_by_step: dict[int, str] = {}

    for step in decision_chain:
        node_id = f"D{step['step']}"
        node_id_by_step[step["step"]] = node_id
        trigger = step.get("trigger") or {}
        nodes.append({
            "id": node_id,
            "type": "engineering_decision",
            "target": _node_target_text(step),
            "decision_summary": step.get("implementation_detail") or step.get("implementation", ""),
            "trigger": trigger.get("observation") or trigger.get("reasoning", ""),
            "evidence_level": step.get("evidence_grading", ""),
            "reason_nature": step.get("reason_nature", ""),
            "source_ddr_id": "",  # patched by convert_extraction_to_ddr once ddr_id is allocated
        })

    # triggered_by / solves: deterministic - a later step's trigger.observation
    # equal to the previous step's result.after is the same linkage
    # _build_decision_chain's prev_outcome threading already establishes, not
    # a new guess. `solves` piggybacks on that edge only when the earlier
    # outcome reads as a setback (FAILURE_SIGNAL_KEYWORDS).
    for i in range(1, len(decision_chain)):
        prev_step, cur_step = decision_chain[i - 1], decision_chain[i]
        prev_id, cur_id = node_id_by_step[prev_step["step"]], node_id_by_step[cur_step["step"]]
        prev_outcome = (prev_step.get("result") or {}).get("after") or ""
        cur_observation = (cur_step.get("trigger") or {}).get("observation") or ""
        if cur_observation and prev_outcome and cur_observation == prev_outcome:
            edges.append({"from": prev_id, "to": cur_id, "relation": "triggered_by", "evidence": cur_observation})
            if any(kw in prev_outcome.lower() for kw in FAILURE_SIGNAL_KEYWORDS):
                edges.append({
                    "from": cur_id, "to": prev_id, "relation": "solves",
                    "evidence": f"{cur_step.get('implementation_detail', '')} addresses: {prev_outcome}",
                })

    # alternative_to: an alternative naming the same gene symbol as another
    # real step's target in this paper's own decision_chain. Gene-symbol
    # equality only (no fuzzy text matching) - a missed edge is preferable
    # to a fabricated relationship between two unrelated steps.
    seen_alt_edges: set[tuple[str, str]] = set()
    for step in decision_chain:
        step_id = node_id_by_step[step["step"]]
        for alt in step.get("alternatives") or []:
            approach = alt.get("approach", "") if isinstance(alt, dict) else str(alt)
            gene = _extract_gene_symbol(approach)
            if not gene:
                continue
            for other in decision_chain:
                if other["step"] == step["step"]:
                    continue
                if (other.get("target") or {}).get("gene") == gene:
                    other_id = node_id_by_step[other["step"]]
                    key = (step_id, other_id) if step_id < other_id else (other_id, step_id)
                    if key in seen_alt_edges:
                        continue
                    seen_alt_edges.add(key)
                    edges.append({"from": step_id, "to": other_id, "relation": "alternative_to", "evidence": approach})

    # validated_by: a validation-type excluded_record whose target matches a
    # decision node's target becomes its own node, linked back to that
    # decision - excluded_records already carries exactly this information
    # (V2's Q1/Q2/Q3 filter), this just surfaces it as a graph edge instead
    # of leaving it only reachable by scanning excluded_records separately.
    validation_counter = 0
    for record in excluded_records:
        if record.get("decision_type") != "validation":
            continue
        snapshot = record.get("step_snapshot", {})
        val_target = _node_target_text(snapshot)
        matching_decision = next(
            (step for step in decision_chain if val_target and _node_target_text(step) == val_target),
            None,
        )
        if matching_decision is None:
            continue
        validation_counter += 1
        val_id = f"V{validation_counter}"
        snap_trigger = snapshot.get("trigger") or {}
        nodes.append({
            "id": val_id,
            "type": "validation_evidence",
            "target": val_target,
            "decision_summary": snap_trigger.get("reasoning") or snapshot.get("implementation_detail", ""),
            "trigger": snap_trigger.get("observation", ""),
            "evidence_level": snapshot.get("evidence_grading", ""),
            "reason_nature": "",
            "source_ddr_id": "",
        })
        edges.append({
            "from": node_id_by_step[matching_decision["step"]],
            "to": val_id,
            "relation": "validated_by",
            "evidence": (snapshot.get("result") or {}).get("after", ""),
        })

    return {"nodes": nodes, "edges": edges}


def _build_failure_points(decision_chain: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Explicit failure→pivot pattern (0804 优化_3 §8). Reuses the same
    adjacent-step signal as the decision graph's `solves` edges, kept as a
    standalone list so engineering_logic_chain doesn't need to parse the
    graph just to answer "where did the reasoning pivot because something
    didn't work"."""
    points: list[dict[str, Any]] = []
    for i in range(1, len(decision_chain)):
        prev_step, cur_step = decision_chain[i - 1], decision_chain[i]
        prev_outcome = (prev_step.get("result") or {}).get("after") or ""
        cur_observation = (cur_step.get("trigger") or {}).get("observation") or ""
        if cur_observation and prev_outcome and cur_observation == prev_outcome and any(
            kw in prev_outcome.lower() for kw in FAILURE_SIGNAL_KEYWORDS
        ):
            points.append({
                "failure_point": prev_outcome,
                "caused_by": prev_step.get("implementation_detail") or prev_step.get("implementation", ""),
                "resolved_by": cur_step.get("implementation_detail") or cur_step.get("implementation", ""),
            })
    return points


def _build_engineering_logic_chain(
    decision_map: dict[str, Any],
    failure_points: list[dict[str, Any]],
) -> dict[str, Any]:
    """§7's upgraded view. Reuses engineering_decision_map's already-computed
    goal/initial_bottleneck/key_hypothesis (that function's own docstring
    explains the fallback order) rather than recomputing them a second,
    possibly-divergent way."""
    return {
        "goal": decision_map.get("goal", ""),
        "initial_bottleneck": decision_map.get("initial_bottleneck", ""),
        "hypothesis": decision_map.get("key_hypothesis", ""),
        "failure_points": failure_points,
        "decision_graph": "见顶层 engineering_decision_graph（不在此重复存储图数据）",
    }


def _build_rule_provenance(decision_chain: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Part 6 aggregate - only steps with a non-null rule."""
    return [
        {
            "step": step.get("step"),
            "rule": step["rule"],
            "rule_source": step.get("rule_source"),
            "rule_confidence": step.get("rule_confidence"),
            "supporting_ddr": step.get("supporting_ddr", []),
        }
        for step in decision_chain
        if step.get("rule")
    ]


def _build_extraction_meta(
    pending: list[str],
    extraction_task_id: str | None,
    paper_index: int | None = None,
    paper_extraction_detail: dict[str, Any] | None = None,
    *,
    engineering_paper_type: list[str] | None = None,
    engineering_paper_type_rationale: str = "",
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
        "engineering_paper_type": engineering_paper_type or [],
        "engineering_paper_type_rationale": engineering_paper_type_rationale,
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


def _auto_decision_type(
    haystack: str,
    evidence_haystack: str,
) -> tuple[str, str]:
    """Heuristic Q1/Q2/Q3 classification (0804 优化 §3 Phase 3) — returns
    ``(decision_type, rationale)``.

    ``haystack`` should already combine the step's intervention/purpose/
    trigger/implementation-detail text (lowercased); ``evidence_haystack``
    the step's evidence description/source text (paragraph anchors etc.,
    underscores normalized to spaces) — genome/docking signals typically
    only show up there, not in the intervention text itself. Order matters:
    background (Q2) is checked first because a background chassis mentioned
    alongside real new engineering in the same record should still be
    flagged for human review rather than silently kept; post_hoc requires a
    *combination* of a post-hoc-context signal and a no-new-action signal
    (never `reason_nature` alone — SCREENING_KEYWORDS's bare "ale" substring
    already false-positives on ordinary words like "genome-scale", so
    reason_nature=="筛选得来" is not a reliable second signal here) so a
    genuinely new but docking-supported engineering step isn't misfiled.
    """
    if any(kw in haystack for kw in BACKGROUND_KEYWORDS):
        return "background", "命中背景底盘关键词（本文引用/沿用此前研究已构建的构建体，未通过 Q2）"

    no_new_action = any(kw in haystack for kw in NO_NEW_ACTION_KEYWORDS)
    post_hoc_signal = any(kw in haystack or kw in evidence_haystack for kw in POST_HOC_SIGNAL_KEYWORDS)
    if post_hoc_signal and no_new_action:
        return "post_hoc_interpretation", "命中结构分析/docking/基因组测序等事后解释信号，且无新改造动作，未驱动本文的工程决策（未通过 Q1）"

    if no_new_action or any(kw in haystack for kw in VALIDATION_KEYWORDS):
        return "validation", "记录只验证/表征已选定的设计，未包含新的改造动作或未引出新的策略选择（未通过 Q1 或 Q3）"

    return "engineering_decision", ""


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


def _normalize_title(title: str) -> str:
    return re.sub(r"[^\w]+", " ", title.lower()).strip()


def _find_existing_ddr(ref: dict[str, Any]) -> dict[str, Any] | None:
    """Find an already-saved DDR for the same paper, so re-extracting it
    overwrites the existing record instead of creating a duplicate.

    Matches by DOI first (case/whitespace-insensitive exact match, when both
    records have a non-empty DOI), falling back to normalized title (also
    exact match). Deliberately no fuzzy matching - a false-positive merge
    would silently discard a different paper's record."""
    if not DDR_DIR.is_dir():
        return None
    doi = (ref.get("doi") or "").strip().lower()
    title = _normalize_title(ref.get("title") or "")
    if not doi and not title:
        return None
    for f in DDR_DIR.glob("DDR-*.json"):
        try:
            rec = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        rec_ref = rec.get("metadata", {}).get("reference", {})
        rec_doi = (rec_ref.get("doi") or "").strip().lower()
        if doi and rec_doi and doi == rec_doi:
            return rec
        rec_title = _normalize_title(rec_ref.get("title") or "")
        if not doi and title and title == rec_title:
            return rec
    return None


def _classify_rule_source(rule_text: str, own_ddr_id: str | None) -> tuple[str, list[str]]:
    """Scan the knowledge base for other DDRs carrying a similar rule
    (0804 优化_3 §9/§10). Conservative token-overlap match, same philosophy
    as `_find_existing_ddr` - a false-positive "this rule is already
    supported elsewhere" is worse than the default `single_paper`, so the
    threshold is deliberately not tuned to be clever. `textbook_mechanism`
    and `expert_curated` are never auto-assigned - those require a human
    judgment this scan can't make."""
    if not rule_text or not DDR_DIR.is_dir():
        return "single_paper", []
    own_tokens = _rule_tokens(rule_text)
    if not own_tokens:
        return "single_paper", []
    supporting: list[str] = []
    for f in DDR_DIR.glob("DDR-*.json"):
        if f.stem.startswith(f"{own_ddr_id}_") or f.stem == own_ddr_id:
            continue
        try:
            rec = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        rec_id = rec.get("ddr_id")
        for step in rec.get("decision_chain", []):
            other_rule = step.get("rule")
            if not other_rule:
                continue
            other_tokens = _rule_tokens(other_rule)
            if not other_tokens:
                continue
            overlap = len(own_tokens & other_tokens) / len(own_tokens | other_tokens)
            if overlap >= _RULE_SIMILARITY_THRESHOLD and rec_id and rec_id not in supporting:
                supporting.append(rec_id)
                break
    if supporting:
        return "multi_paper_supported", supporting
    return "single_paper", []


def _classify_rule_confidence(
    reason_nature: str,
    evidence_grading: str,
    rule_source: str,
    rule_scope_too_broad: bool,
) -> str:
    """0804 优化_3 §11: high = mechanistic reasoning + multiple evidence
    sources; medium = one strong paper; low = analogy or incomplete
    evidence. An over-broad rule (§12) is capped at low unconditionally,
    even if every other signal would otherwise support a higher grade -
    scope violation is itself evidence the claim outran what was verified."""
    if rule_scope_too_broad:
        return "low"
    canonical_reason = _canonical_reason(reason_nature)
    if canonical_reason == "literature_analogy":
        return "low"
    if canonical_reason == "mechanistic_inference" and evidence_grading == "硬":
        if rule_source in ("multi_paper_supported", "textbook_mechanism", "expert_curated"):
            return "high"
        return "medium"
    return "low"


def _apply_rule_provenance(decision_chain: list[dict[str, Any]], ddr_id: str) -> None:
    """Fills in rule_source/rule_confidence/supporting_ddr for every step
    with a non-null rule, now that ddr_id is known (see the placeholder
    comment in _build_single_step for why this can't happen earlier).
    Mutates decision_chain's step dicts in place."""
    for step in decision_chain:
        rule = step.get("rule")
        if not rule:
            continue
        rule_source, supporting = _classify_rule_source(rule, ddr_id)
        rule_scope_too_broad = any(kw in rule.lower() for kw in BROAD_RULE_SCOPE_KEYWORDS)
        step["rule_source"] = rule_source
        step["supporting_ddr"] = supporting
        step["rule_confidence"] = _classify_rule_confidence(
            step.get("reason_nature", ""), step.get("evidence_grading", ""), rule_source, rule_scope_too_broad,
        )


def _save_ddr(ddr: dict[str, Any]) -> Path:
    """Persist a converted DDR to the knowledge base directory, overwriting
    any existing file(s) for the same ddr_id (the filename embeds a title
    slug, which can drift slightly between extractions of the same paper -
    stale same-id files are removed so overwriting never leaves a
    half-duplicate behind)."""
    DDR_DIR.mkdir(parents=True, exist_ok=True)
    ddr_id = ddr["ddr_id"]
    stale = list(DDR_DIR.glob(f"{ddr_id}_*.json"))
    for f in stale:
        f.unlink(missing_ok=True)
    # Create a safe filename from title
    title = ddr.get("metadata", {}).get("title", "")
    safe_title = re.sub(r"[^\w\s-]", "", title.lower())[:50].strip().replace(" ", "_") or "untitled"
    path = DDR_DIR / f"{ddr_id}_{safe_title}.json"
    path.write_text(json.dumps(ddr, ensure_ascii=False, indent=2), encoding="utf-8")
    sync_after_save([path])
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
    verifications = full_result.get("evidence_verifications", [])
    verification_provenance = full_result.get("evidence_verification_provenance", [])
    provenance_by_artifact = {p.get("skill08_artifact_id"): p for p in verification_provenance if isinstance(p, dict)}
    entries: list[tuple[int, dict[str, Any]]] = []
    for verified in verifications:
        if not isinstance(verified, dict):
            continue
        admission = verified.get("knowledge_admission") or {}
        artifact_id = admission.get("source_skill08_artifact_id")
        provenance = provenance_by_artifact.get(artifact_id)
        candidate = verified.get("candidate_payload")
        if not provenance or not isinstance(candidate, dict):
            continue
        index = provenance.get("source_item_index")
        if not isinstance(index, int):
            continue
        entries.append((index, {"output": candidate, "skill08_output": verified, "skill08_provenance": provenance}))

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


def _idea_display_text(value: Any) -> str:
    """Convert legacy extraction field envelopes into safe card text.

    Older DDR records can retain Skill07's ``{value, status, ...}`` field
    shape in narrative slots.  The knowledge-ideas API is a presentation
    view, so it must never leak those dictionaries to React as children.
    """
    while isinstance(value, dict) and "value" in value:
        value = value.get("value")
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, (int, float, bool)):
        return str(value)
    if isinstance(value, list):
        return "; ".join(filter(None, (_idea_display_text(item) for item in value)))
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


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
    summary = _idea_display_text(
        hypothesis.get("hypothesis")
        or diagnosis.get("mechanistic_explanation")
        or next(iter(diagnosis.get("observations") or []), "")
    )
    ddr_id = rec.get("ddr_id", "")
    return {
        "idea_id": ddr_id,
        "title": _idea_display_text(problem.get("problem_statement") or meta.get("title") or ddr_id),
        "summary": summary,
        "category": _category_for_decision_chain(decision_chain),
        "source": {
            "paper_id": ddr_id,
            "title": _idea_display_text(ref.get("title") or meta.get("title", "")),
            "journal": _idea_display_text(ref.get("journal", "")),
            "year": _idea_display_text(ref.get("year", "")),
            "doi": _idea_display_text(ref.get("doi", "")),
        },
        "evidence_ids": [f"{ddr_id}:{step.get('step')}" for step in decision_chain],
    }
