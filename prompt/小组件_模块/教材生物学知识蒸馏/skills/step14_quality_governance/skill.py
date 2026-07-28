"""Step14 - quality report + hard governance gates (SKILL.md Step14).

This module never generates exact wet-lab SOPs (exact_SOP_generation and
automatic_DBTL_design stay blocked by default); it only widens
engineering_principle_retrieval/decision_support to "allowed" once the
specific per-object conditions below are met, and always keeps a
mechanism-level conflict from silently promoting an engineering
suggestion (SKILL.md 十一.1, 十二 hard gates).
"""
from __future__ import annotations

VERSION = "0.1.0"


def execute(request, **kwargs):
    contract = request.get("task_contract", {})
    sources = request.get("validated_sources", [])
    structures = request.get("source_structures", [])
    scope = request.get("extraction_scope", [])
    audit = request.get("evidence_audit", {})
    fusion = request.get("fusion", {})
    paper_links = request.get("paper_links", [])

    risk_flags, review_items = [], []

    unverified_sources = [s["source_id"] for s in sources if not s.get("identity_verified")]
    unresolved_editions = [s["source_id"] for s in sources if s.get("unresolved_edition")]
    if unverified_sources:
        risk_flags.append(f"SOURCE_IDENTITY_ERROR: unverified source identity for {unverified_sources}")
        review_items.extend({"item": "unverified_source", "source_id": sid} for sid in unverified_sources)
    if unresolved_editions:
        risk_flags.append(f"UNRESOLVED_EDITION: {unresolved_editions}")
        review_items.extend({"item": "unresolved_edition", "source_id": sid} for sid in unresolved_editions)

    coverage = audit.get("evidence_coverage", {})
    coverage_ratio = coverage.get("coverage_ratio", 1.0)
    if coverage.get("unresolved_object_ids"):
        risk_flags.append(f"EVIDENCE_NOT_FOUND: {len(coverage['unresolved_object_ids'])} objects lack direct evidence support")
        review_items.extend({"item": "unsupported_object", "object_id": oid} for oid in coverage["unresolved_object_ids"])

    principles = audit.get("engineering_principles", [])
    model_inferred = [p["principle_id"] for p in principles if p.get("derivation_type") == "model_inference"]
    missing_precondition = [p["principle_id"] for p in principles if not p.get("required_preconditions")]
    missing_organism = [p["principle_id"] for p in principles if not p.get("organism_scope")]
    simplifications = [p["principle_id"] for p in principles if p.get("pedagogical_simplification")]
    if model_inferred:
        risk_flags.append(f"OVERGENERALIZATION_RISK: {len(model_inferred)} engineering principles are model_inference, not source-stated recommendations")
        review_items.extend({"item": "model_inferred_principle", "object_id": pid} for pid in model_inferred)
    if missing_organism:
        review_items.extend({"item": "organism_scope_unknown_do_not_default_k12", "object_id": pid} for pid in missing_organism)

    conflicts = fusion.get("source_conflicts", [])
    mechanism_conflicts = [c for c in conflicts if c.get("conflict_type") in {"definition", "organism_difference"} and c.get("topic")]
    if conflicts:
        risk_flags.append(f"FUSION_CONFLICT: {len(conflicts)} unresolved source conflicts")
        review_items.extend({"item": "source_conflict", "conflict_id": c["conflict_id"]} for c in conflicts)

    decision_rules_present = bool(audit.get("decision_rules"))
    paper_links_present = bool(paper_links)
    if paper_links_present:
        review_items.extend({"item": "paper_case_link_needs_confirmation", "link_id": link["link_id"]} for link in paper_links)

    quality_report = {
        "source_quality": {
            "total_sources": len(sources),
            "identity_verified": len(sources) - len(unverified_sources),
            "unresolved_editions": len(unresolved_editions),
        },
        "parsing_quality": {
            "sources_with_structure": sum(1 for s in structures if any(b["block_type"] in {"chapter", "section"} for b in s.get("blocks", []))),
            "total_blocks": sum(len(s.get("blocks", [])) for s in structures),
        },
        "evidence_quality": coverage,
        "knowledge_completeness": {
            "sections_extract_full": sum(1 for s in scope if s.get("recommended_action") == "extract_full"),
            "sections_extract_partial": sum(1 for s in scope if s.get("recommended_action") == "extract_partial"),
            "sections_metadata_only": sum(1 for s in scope if s.get("recommended_action") == "metadata_only"),
        },
        "engineering_utility": {
            "principles_total": len(principles),
            "principles_model_inference": len(model_inferred),
            "principles_missing_precondition": len(missing_precondition),
            "principles_pedagogical_simplification_only": len(simplifications),
        },
        "cross_source_consistency": {
            "canonical_objects": len(fusion.get("canonical_knowledge_objects", [])),
            "conflicts": len(conflicts),
        },
        "translation_quality": {"status": "not_applicable_in_phase1", "note": "bilingual normalization is a future-phase capability; see README Phase roadmap."},
        "risk_flags": risk_flags,
        "review_items": review_items,
        "overall_status": "PASS",
    }

    if unverified_sources and not sources:
        quality_report["overall_status"] = "BLOCKED"
    elif coverage.get("total_objects", 0) > 0 and coverage_ratio == 0:
        quality_report["overall_status"] = "BLOCKED"
    elif conflicts or unverified_sources or coverage.get("unresolved_object_ids"):
        quality_report["overall_status"] = "REVIEW_REQUIRED"
    elif risk_flags:
        quality_report["overall_status"] = "PASS_WITH_WARNINGS"

    governance = {
        "concept_explanation": "allowed",
        "mechanism_reasoning": "review" if mechanism_conflicts else "allowed",
        "engineering_principle_retrieval": "blocked" if quality_report["overall_status"] == "BLOCKED" else ("review" if (missing_precondition or model_inferred) else "allowed"),
        "decision_support": "review" if decision_rules_present else "allowed",
        "automatic_DBTL_design": "blocked" if (mechanism_conflicts or model_inferred or simplifications or quality_report["overall_status"] != "PASS") else "review",
        "exact_SOP_generation": "blocked",
    }

    status = "needs_review" if quality_report["overall_status"] in {"REVIEW_REQUIRED", "BLOCKED"} else "succeeded_with_warnings" if risk_flags else "succeeded"
    return {
        "output": {"quality_report": quality_report, "governance": governance},
        "status": status, "errors": [],
        "provenance": {"step_version": VERSION, "source_ids": [s["source_id"] for s in sources]},
    }
