"""Step15 - build the "生物学知识 / Biological Knowledge" page structure and
knowledge graph. Internal step numbers never surface here - card fields
follow SKILL.md 13.3 exactly (name, one-line definition, type, applicable
system, DBTL stage, confidence, evidence count, source count, conflict
flag, human-reviewed flag), and the expanded view keeps 是什么/为什么/
适用条件/不适用条件/怎么做/先测什么/如何验证/失败模式/替代方案/来源/证据
as separate fields rather than one paragraph.
"""
from __future__ import annotations

VERSION = "0.1.0"

_CATEGORY_KEYS = {
    "concepts_and_mechanisms": ("concept", "mechanism"),
    "engineering_principles": ("engineering_principle",),
    "design_patterns": ("design_pattern",),
    "decision_rules": ("decision_rule",),
    "validation_strategies": ("validation_strategy",),
    "failure_patterns": ("failure_pattern",),
}


def _confidence_value(c):
    return c.get("value", 0.0) if isinstance(c, dict) else c


def _card(obj, conflicted_ids):
    name = obj.get("name_en") or obj.get("name_zh") or obj.get("decision_topic") or obj.get("id")
    definition = (obj.get("definition_en") or obj.get("definition_zh") or obj.get("principle_statement_en")
                  or obj.get("principle_statement_zh") or obj.get("target_claim") or "")
    return {
        "id": obj.get("id"),
        "name": name,
        "one_line_definition": definition[:200],
        "knowledge_type": obj.get("type"),
        "applicable_system": obj.get("organism_scope", []) or ["unknown"],
        "dbtl_stage": obj.get("dbtl_stage", []),
        "confidence": _confidence_value(obj.get("confidence", 0.0)),
        "evidence_count": len(obj.get("evidence", [])),
        "source_count": len({e.get("source_id") for e in obj.get("evidence", []) if e.get("source_id")}),
        "has_conflict": obj.get("id") in conflicted_ids,
        "human_reviewed": obj.get("review_status") == "approved",
        "detail": {
            "是什么_what": definition,
            "为什么_why": " ".join(obj.get("biological_basis", [])),
            "适用条件_when_applicable": obj.get("required_preconditions", []) or obj.get("applicable_conditions", []),
            "不适用条件_when_not_applicable": obj.get("contraindications", []) or obj.get("non_applicable_conditions", []),
            "推荐怎么做_recommended_actions": obj.get("recommended_actions", []) or obj.get("canonical_structure", []),
            "需要先测什么_required_measurements": obj.get("validation_requirements", []) or obj.get("minimum_validation", []),
            "如何验证_how_to_validate": obj.get("validation_requirements", []) or obj.get("recommended_validation", []),
            "可能怎么失败_failure_modes": obj.get("failure_conditions", []) or obj.get("observed_symptoms", []),
            "替代方案_alternatives": obj.get("alternatives", []) or obj.get("mitigation_options", []),
            "教材来源_sources": sorted({e.get("source_id") for e in obj.get("evidence", []) if e.get("source_id")}),
            "证据原文_evidence_excerpts": [e.get("original_text", "") for e in obj.get("evidence", [])],
        },
    }


def execute(request, **kwargs):
    audit = request.get("evidence_audit", {})
    fusion = request.get("fusion", {})
    paper_links = request.get("paper_links", [])
    quality_report = request.get("quality_report", {})
    governance = request.get("governance", {})

    all_objects = audit.get("all_objects", [])
    conflicted_ids = set()
    for c in fusion.get("canonical_knowledge_objects", []):
        if c.get("conflicts"):
            conflicted_ids.update(c.get("merged_from", []))

    frontend_view = {}
    for category, types in _CATEGORY_KEYS.items():
        frontend_view[category] = [_card(o, conflicted_ids) for o in all_objects if o.get("type") in types]
    frontend_view["experimental_cases"] = paper_links
    frontend_view["sources_and_evidence"] = {
        "total_evidence_bindings": sum(len(o.get("evidence", [])) for o in all_objects),
        "coverage": audit.get("evidence_coverage", {}),
    }
    frontend_view["conflicts_and_human_review"] = {
        "conflicts": fusion.get("source_conflicts", []),
        "review_items": quality_report.get("review_items", []),
    }

    nodes, edges = [], []
    for o in all_objects:
        nodes.append({"id": o.get("id"), "node_type": o.get("type"), "label": o.get("name_en") or o.get("name_zh") or o.get("id")})
        for src_id in {e.get("source_id") for e in o.get("evidence", []) if e.get("source_id")}:
            nodes.append({"id": src_id, "node_type": "Source", "label": src_id})
            edges.append({"from": o.get("id"), "to": src_id, "relation": "derived_from"})
        for organism in o.get("organism_scope", []):
            nodes.append({"id": f"organism:{organism}", "node_type": "Organism", "label": organism})
            edges.append({"from": o.get("id"), "to": f"organism:{organism}", "relation": "applies_to"})
    for c in fusion.get("source_conflicts", []):
        for claim in c.get("claims", []):
            if claim.get("knowledge_id"):
                edges.append({"from": claim["knowledge_id"], "to": c["conflict_id"], "relation": "contradicted_by"})
    for link in paper_links:
        nodes.append({"id": link["paper_case_id"], "node_type": "ExperimentalCase", "label": link["paper_case_id"]})
        edges.append({"from": link["knowledge_object_id"], "to": link["paper_case_id"], "relation": link["link_type"] + "_by" if link["link_type"] not in {"supports", "instantiates"} else link["link_type"]})
    # de-duplicate nodes by id
    seen = {}
    for n in nodes:
        seen[n["id"]] = n
    knowledge_graph = {"nodes": list(seen.values()), "edges": edges}

    summary_view = {
        "message": "Distillation complete; see governance before using engineering_principles for automatic design.",
        "objects_total": len(all_objects),
        "engineering_principles": len(frontend_view["engineering_principles"]),
        "overall_status": quality_report.get("overall_status", "unknown"),
        "governance": governance,
        "top_risk_flags": quality_report.get("risk_flags", [])[:5],
    }

    return {
        "output": {"frontend_view": frontend_view, "knowledge_graph": knowledge_graph, "summary_view": summary_view},
        "status": "succeeded", "errors": [],
        "provenance": {"step_version": VERSION, "source_ids": sorted({n["id"] for n in knowledge_graph["nodes"] if n["node_type"] == "Source"})},
    }
