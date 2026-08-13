r"""Build a clear, human-readable extraction summary directly from the
workflow's on-disk checkpoint - independent of skill13's frontend adapter
(which is engineering-plan-shaped and only runs when `result_level ==
"engineering_plan"`, see `WorkflowEngine._plan`). This is what backs the
"论文抽取结果" results view: for every paper, the agent's reasoning
("抽取思路") is kept visually separate from the paper's own experimental
design content ("实验设计思路"), and every reported/inferred design field
carries its literal supporting quote back to the source PDF.

Reads straight from `RUNTIME_DIR / task_id / checkpoint.json` (the same
file `harness.paper_extraction.service.get_live_skill_states` already
reads), so this works whether the run is still in progress, finished, or
sitting at WAITING_REVIEW for a genuine missing-input reason - never
requires the run to have reached `result_level="engineering_plan"`.

Human review (skill12) is surfaced here as an independent, non-blocking
audit trail (governance.review_tasks / governance.qc_by_paper) - it never
gates whether a paper's results are shown; see the workflow engine's
completion logic (`WorkflowEngine.run`) for the corresponding decision on
the run-completion side.
"""
from __future__ import annotations

import json
from typing import Any

from harness.i18n import get_locale
from harness.translation.service import translate_text

from harness.paper_extraction.service import RUNTIME_DIR

# Fields that are the agent's own reasoning about the paper/task, not part
# of the paper's experimental design content - kept out of the generic
# design-fields list and routed to their own dedicated sections instead.
# Skill07's contract nests these under `extensions`, but live model output
# has been observed putting them directly under `fields` too (a known
# schema drift in the LLM-extraction path) - checked in both places.
_REASONING_KEYS = {"article_type_gate", "paper_target_strains", "user_target_system", "target_system_adaptation"}

_FIELD_LABELS_ZH: dict[str, str] = {
    "objective": "研究目标",
    "hypothesis": "研究假设",
    "strain": "使用菌株",
    "genotype": "基因型",
    "engineering_method": "工程方法/干预手段",
    "experimental_groups": "实验组",
    "controls": "对照组",
    "culture_conditions": "培养条件",
    "medium": "培养基",
    "dosage": "剂量",
    "time": "时间",
    "replicates": "重复次数",
    "assay": "检测方法",
    "instruments": "仪器",
    "analysis_methods": "分析方法",
    "outcomes": "结果/产出",
}

_STATUS_LABELS_ZH = {"reported": "原文报道", "inferred": "推断", "unknown": "未识别", "not_applicable": "不适用"}


def _load_checkpoint(task_id: str) -> dict[str, Any] | None:
    path = RUNTIME_DIR / task_id / "checkpoint.json"
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _as_evidence_bound(field: Any) -> dict[str, Any]:
    """Normalize a field to {value,status,confidence,evidence_ids} - skill07's
    raw output doesn't always comply (same defensive normalization skill08
    itself applies before processing)."""
    if isinstance(field, dict) and "status" in field:
        return field
    return {"value": field, "status": "unknown" if field is None else "reported", "confidence": None, "evidence_ids": []}


def _resolve_evidence(evidence_ids: list[str], evidence_map: dict[str, Any]) -> list[dict[str, Any]]:
    items = []
    for eid in evidence_ids or []:
        record = evidence_map.get(eid)
        if not record:
            continue
        locator = record.get("locator", {})
        items.append({
            "evidence_id": eid,
            "quote": record.get("quote", ""),
            "page": locator.get("page"),
            "section_path": locator.get("section_path", []),
            "figure_id": locator.get("figure_id"),
            "table_id": locator.get("table_id"),
        })
    return items


def _field_reasoning(bound: dict[str, Any]) -> dict[str, Any]:
    """skill07's per-field `extraction_method`/`notes` (always present per
    schema.py's `unknown_field`/`reported_field`) plus the optional
    `inference: {method, rationale}` object the opus_extractor prompt
    contracts for status="inferred" - together the closest thing this
    pipeline has to a per-field "how did the agent get here" trace, since
    the underlying LLM call returns only a final JSON object, never a
    logged chain-of-thought to replay."""
    inference = bound.get("inference") if isinstance(bound.get("inference"), dict) else {}
    return {
        "extraction_method": bound.get("extraction_method"),
        "notes": bound.get("notes"),
        "inference_method": inference.get("method"),
        "inference_rationale": inference.get("rationale"),
    }


def _build_design_fields(bound_fields: dict[str, Any] | None, raw_fields: dict[str, Any], evidence_map: dict[str, Any]) -> list[dict[str, Any]]:
    """Prefer skill08's evidence-verified fields (a field downgraded to
    "unknown" there means no supporting quote could be found - more
    trustworthy than skill07's raw, unverified claim). Fields skill08 never
    processed (e.g. the run stopped before skill08, or skill08 dropped a
    key it didn't recognize) fall back to skill07's raw value."""
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    primary = bound_fields if bound_fields else {}
    for key, value in primary.items():
        if key in _REASONING_KEYS:
            continue
        seen.add(key)
        bound = _as_evidence_bound(value)
        out.append({
            "key": key,
            "label": _FIELD_LABELS_ZH.get(key, key.replace("_", " ").strip().title() or key),
            "value": bound.get("value"),
            "status": bound.get("status", "unknown"),
            "status_label": _STATUS_LABELS_ZH.get(bound.get("status", "unknown"), bound.get("status", "unknown")),
            "confidence": bound.get("confidence"),
            "evidence": _resolve_evidence(bound.get("evidence_ids", []), evidence_map),
            "reasoning": _field_reasoning(bound),
            "verified": True,
        })
    for key, value in (raw_fields or {}).items():
        if key in _REASONING_KEYS or key in seen:
            continue
        bound = _as_evidence_bound(value)
        out.append({
            "key": key,
            "label": _FIELD_LABELS_ZH.get(key, key.replace("_", " ").strip().title() or key),
            "value": bound.get("value"),
            "status": bound.get("status", "unknown"),
            "status_label": _STATUS_LABELS_ZH.get(bound.get("status", "unknown"), bound.get("status", "unknown")),
            "confidence": bound.get("confidence"),
            "evidence": _resolve_evidence(bound.get("evidence_ids", []), evidence_map),
            "reasoning": _field_reasoning(bound),
            "verified": False,
        })
    return out


def _paper_identity(papers: list[dict[str, Any]], index: int, fallback_paper_id: str | None) -> dict[str, Any]:
    if index < len(papers):
        identity = papers[index].get("paper_identity") or {}
    else:
        identity = {}
    title = identity.get("title")
    if title and get_locale() in ("zh-CN", "en-US"):
        title = translate_text(title, get_locale())
    return {
        "paper_id": identity.get("paper_id") or fallback_paper_id or f"paper_{index + 1}",
        "title": title,
        "authors": identity.get("authors", []),
        "journal": identity.get("journal"),
        "year": identity.get("year"),
        "doi": identity.get("doi"),
    }


def _extract_reasoning(raw_fields: dict[str, Any], extensions: dict[str, Any], key: str) -> Any:
    """Reasoning keys have been observed both under `fields` (live model
    drift) and under `extensions` (the documented contract) - check both,
    preferring `fields` since that's what was actually seen in production
    checkpoints."""
    if key in raw_fields:
        return raw_fields[key]
    return extensions.get(key)


def _experimental_design_paper_id(value: Any) -> Any:
    """Return a paper id from either supported skill07 output shape.

    The extraction model normally emits one experimental-design object, but
    may emit a list when it identifies multiple experiments in one paper.
    Summary rendering must remain available for both shapes.
    """
    if isinstance(value, dict):
        return value.get("paper_id")
    if isinstance(value, list):
        for item in value:
            if isinstance(item, dict) and item.get("paper_id"):
                return item["paper_id"]
    return None


def build_extraction_summary(task_id: str) -> dict[str, Any] | None:
    """Build the full extraction summary for one task. Returns None if no
    checkpoint exists yet for this task_id (e.g. the task hasn't started).

    Safe to call at any point in the run's lifecycle - reflects whatever
    has been checkpointed so far, paper by paper.
    """
    state = _load_checkpoint(task_id)
    if state is None:
        return None

    c = state.get("context", {})
    papers = c.get("paper_artifacts", []) or []
    skill01 = c.get("skill01", {}) or {}
    skill07_list = c.get("skill07", []) or []
    skill08_list = c.get("skill08", []) or []
    skill09_list = c.get("skill09", []) or []
    skill12 = c.get("skill12", {}) or {}

    paper_count = max(len(papers), len(skill07_list))
    paper_summaries: list[dict[str, Any]] = []

    for i in range(paper_count):
        s07 = skill07_list[i] if i < len(skill07_list) else {}
        s08 = skill08_list[i] if i < len(skill08_list) else {}
        s09 = skill09_list[i] if i < len(skill09_list) else {}

        raw_fields = s07.get("fields", {}) or {}
        extensions = s07.get("extensions", {}) or {}
        bound_fields = (s08.get("literature_experiment", {}) or {}).get("fields")
        evidence_map = s08.get("evidence_map", {}) or {}

        fallback_paper_id = _experimental_design_paper_id(s07.get("experimental_design_object"))
        identity = _paper_identity(papers, i, fallback_paper_id)

        article_type = _extract_reasoning(raw_fields, extensions, "article_type_gate")
        target_strains = _extract_reasoning(raw_fields, extensions, "paper_target_strains") or []
        target_system_adaptation = _extract_reasoning(raw_fields, extensions, "target_system_adaptation")

        design_fields = _build_design_fields(bound_fields, raw_fields, evidence_map)
        has_design_content = any(f["status"] != "unknown" for f in design_fields)

        quality = s09.get("quality_evaluation", {}) or {}
        report = s09.get("evaluation_report", {}) or {}
        coverage = s08.get("coverage", {}) or {}

        per_paper_qc = (skill12.get("qc_reports_by_artifact") or {}).get(f"skill07_experiment_extraction:{i}") \
            or (skill12.get("qc_reports_by_artifact") or {}).get(f"{task_id}:skill07:{i}")

        paper_summaries.append({
            "paper_id": identity["paper_id"],
            "identity": identity,
            "article_type": article_type,
            "target_strains": target_strains,
            "target_system_adaptation": target_system_adaptation,
            "design_fields": design_fields,
            "has_design_content": has_design_content,
            "quality": {
                "completeness": quality.get("completeness"),
                "reproducibility": quality.get("reproducibility"),
                "evidence_level": quality.get("evidence_level"),
                "extraction_confidence": quality.get("extraction_confidence"),
                "missing_information": quality.get("missing_information", []),
                "overall_score": report.get("overall_score"),
                "confidence_label": report.get("confidence"),
                "recommendation": report.get("recommendation"),
                "dimensions": report.get("dimensions", {}),
                "risks": report.get("risks", []),
            },
            "coverage": coverage,
            "governance": {
                "qc_status": (per_paper_qc or {}).get("final_status"),
                "note": "独立质控参考信息，不影响本次抽取结果的展示。" if per_paper_qc else None,
            },
        })

    return {
        "task_id": task_id,
        "status": state.get("status"),
        "task_understanding": skill01.get("research_intent", {}),
        "papers": paper_summaries,
        "governance": {
            "review_tasks": skill12.get("review_tasks", []),
            "note": "以下为独立质控/人工复核参考信息，供审阅者核查抽取质量使用，不影响本次抽取已呈现的结果。",
        },
        "skill_states": state.get("skill_states", {}),
    }
