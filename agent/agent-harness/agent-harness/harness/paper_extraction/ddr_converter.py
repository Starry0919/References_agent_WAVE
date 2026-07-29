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
"""
from __future__ import annotations

import json
import re
import uuid
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

    for i, candidate in enumerate(step_candidates, start=1):
        step = _build_single_step(i, candidate, fields, pending)
        chain.append(step)

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
) -> dict[str, Any]:
    """Build one decision_chain step from a candidate."""
    data = candidate["data"]
    source = candidate["source"]

    # --- design_action ---
    action_type = data.get("action_type") or data.get("modification_type") or data.get("intervention_type", "")
    design_action = _map_design_action(action_type, data)
    if not design_action or design_action == "M3":
        pending.append(f"step_{step_num}.design_action: unable to map '{action_type}' confidently")

    # --- target ---
    target = {
        "gene": data.get("gene") or data.get("target_gene") or data.get("gene_or_pathway", ""),
        "enzyme": data.get("enzyme") or data.get("target_enzyme", ""),
        "pathway": data.get("pathway") or data.get("target_pathway", ""),
        "condition": data.get("condition") or data.get("medium", None),
    }

    # --- trigger ---
    trigger = {
        "observation": data.get("trigger_observation") or data.get("observation", ""),
        "reasoning": data.get("rationale") or data.get("trigger_reasoning", ""),
        "source_location": data.get("source_location", ""),
    }

    # --- evidence ---
    evidence = {
        "description": data.get("evidence_description") or data.get("evidence", ""),
        "source": data.get("evidence_source") or data.get("source", ""),
        "source_location": data.get("evidence_location", ""),
        "values": data.get("evidence_values") or data.get("values", {}),
    }

    # --- evidence_grading: ALWAYS pending human review ---
    evidence_grading = "软"  # default conservative
    grading_rationale = ""
    auto_grade = _auto_evidence_grade(data)
    if auto_grade:
        evidence_grading = auto_grade
        grading_rationale = f"自动启发式判定({auto_grade}): 基于证据关键词匹配——需人工确认"
    else:
        grading_rationale = "自动判定失败——请人工判定"
    pending.append(f"step_{step_num}.evidence_grading: auto={auto_grade or 'none'}, requires human review")

    # --- reason_nature: ALWAYS pending human review ---
    reason_nature = _auto_reason_nature(data, fields)
    pending.append(f"step_{step_num}.reason_nature: auto={reason_nature}, requires human review")

    # --- alternatives ---
    alternatives = data.get("alternatives", [])

    # --- implementation ---
    impl_raw = data.get("implementation") or data.get("modification_type") or data.get("intervention_type", "")
    implementation = _map_implementation(impl_raw)

    # --- implementation_detail ---
    impl_detail = data.get("implementation_detail") or data.get("modification_detail", "")

    # --- result ---
    result = {
        "metric": data.get("result_metric", ""),
        "before": data.get("result_before", ""),
        "after": data.get("result_after", ""),
        "fold_change": data.get("fold_change", None),
        "quantified": bool(data.get("result_quantified", False)),
    }

    # --- rule: ALWAYS pending human review ---
    rule = data.get("generalizable_rule") or data.get("rule", None)
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


def _build_engineering_problem(
    fields: dict[str, Any],
    ed_obj: dict[str, Any],
    decision_chain: list[dict[str, Any]],
) -> dict[str, Any]:
    """Synthesize the engineering problem from available data."""
    ep = fields.get("engineering_problem", {})
    return {
        "problem_statement": ep.get("problem_statement") or fields.get("objective", ""),
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


def _map_implementation(impl_raw: str) -> str:
    """Map intervention type to standardized implementation method."""
    normalized = impl_raw.lower().replace(" ", "_").replace("-", "_")
    # Direct match
    if normalized in INTERVENTION_TO_IMPLEMENTATION:
        return INTERVENTION_TO_IMPLEMENTATION[normalized]
    # Partial match
    for key, value in INTERVENTION_TO_IMPLEMENTATION.items():
        if key in normalized or normalized in key:
            return value
    return "其他"


def _auto_evidence_grade(data: dict[str, Any]) -> str | None:
    """Heuristic evidence grading — returns '硬', '软', or None if unclear.

    These heuristics are deliberately conservative. They only flag clear cases;
    borderline cases return None → human must decide.
    """
    evidence_text = json.dumps(data, ensure_ascii=False).lower()

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

    This is intentionally conservative — most cases will default to '机理推断'
    based on the paper's own stated rationale, but the auto-classification is
    ALWAYS flagged for human review in the pending list.
    """
    text = json.dumps(data, ensure_ascii=False).lower()

    # Screening/library hints
    if any(kw in text for kw in ["library", "screening", "screen", "keio", "random_mutagenesis", "directed_evolution"]):
        return "筛选得来"

    # "As done in [previous paper]" patterns
    if any(kw in text for kw in ["as_described_previously", "as_reported_by", "following_the_protocol_of"]):
        return "文献类比"

    # "Readily available" / "convenient" patterns
    if any(kw in text for kw in ["available_strain", "commercial_kit", "off_the_shelf", "convenient"]):
        return "现成可得"

    # Default: papers almost always present their rationale as mechanism-based
    return "机理推断"


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
