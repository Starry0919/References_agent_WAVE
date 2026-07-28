"""Step01 - establish the knowledge-distillation task contract.

Records the user's request verbatim, assigns a stable source_id to every
input source, and never defaults an unset target organism/strain to
E. coli K-12 (SKILL.md 3.5 / Step01 requirement 8).
"""
from __future__ import annotations

VERSION = "0.1.0"

DEFAULT_LEVELS_WHEN_UNSET = [
    "level1_source_parsing", "level2_basic_knowledge",
    "level3_engineering_distillation", "level4_cross_source_fusion",
]


def execute(request, **kwargs):
    user_request = (request.get("user_request") or "").strip()
    input_sources = request.get("input_sources") or []

    errors = []
    if not user_request:
        errors.append({"code": "SCHEMA_VALIDATION_ERROR", "message": "user_request is empty.", "retryable": True})
    if not input_sources:
        errors.append({"code": "NO_INPUT_ARTIFACT", "message": "No input_sources provided.", "retryable": True})
    if errors:
        return {"output": None, "status": "terminal_failure", "errors": errors, "provenance": {"step_version": VERSION, "source_ids": []}}

    contract_sources = []
    for i, src in enumerate(input_sources, start=1):
        contract_sources.append({**src, "source_id": f"src_{i}"})

    requested_levels = request.get("requested_output_level") or list(DEFAULT_LEVELS_WHEN_UNSET)
    notes = []
    if not request.get("target_organism"):
        notes.append("target_organism not specified by the user; this does not block Level1-4, only target-system adaptation and automatic engineering suggestions.")
    if not request.get("target_engineering_goal"):
        notes.append("no engineering goal given; Step06-08 will still run if requested_output_level asks for engineering distillation, using domain-general trigger conditions.")

    engineering_requested = any(l in requested_levels for l in ("level3_engineering_distillation", "level4_cross_source_fusion", "level5_knowledge_hub_adapter")) or bool(request.get("target_engineering_goal"))
    requires_human_review = bool(
        "level5_knowledge_hub_adapter" in requested_levels
        or request.get("requires_cross_source_fusion")
        or (request.get("quality_requirement") or "").lower() in {"high", "publication_grade", "严格", "高"}
    )

    task_contract = {
        "user_request": user_request,
        "input_sources": contract_sources,
        "target_domain": request.get("target_domain", []),
        "target_organism": request.get("target_organism", []),
        "target_strain": request.get("target_strain", []),
        "target_engineering_goal": request.get("target_engineering_goal", []),
        "requested_output_level": requested_levels,
        "source_languages": request.get("source_languages", []),
        "output_languages": request.get("output_languages") or ["zh", "en"],
        "quality_requirement": request.get("quality_requirement", ""),
        "requires_cross_source_fusion": bool(request.get("requires_cross_source_fusion", False)),
        "requires_paper_case_linking": bool(request.get("requires_paper_case_linking", False)),
        "requires_frontend_adapter": bool(request.get("requires_frontend_adapter", False)),
        "engineering_knowledge_requested": engineering_requested,
        "requires_human_review": requires_human_review,
        "notes": notes,
    }

    return {
        "output": task_contract,
        "status": "succeeded",
        "errors": [],
        "provenance": {"step_version": VERSION, "source_ids": [s["source_id"] for s in contract_sources]},
    }
