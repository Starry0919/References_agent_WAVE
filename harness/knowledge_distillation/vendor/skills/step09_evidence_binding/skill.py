"""Step09 - audit evidence for every knowledge object produced so far.

This step does not invent new evidence bindings; Step05/06 already attach
a block_id + literal cited text to every object at creation time. Step09's
job is to *check* those bindings against the actual parsed blocks and
enforce the hard gate from SKILL.md Step12/Step09:

    若无可定位证据: 不能标记为 source_reported
    若证据缺失: confidence 不得高于既定上限, knowledge_status 保持 candidate

Existence (does the block exist and contain the cited text) and
attribution (does the block's source_id match the object's own source_id)
are both checked; a hit on either failure caps confidence and flags the
object rather than silently keeping it at full confidence.
"""
from __future__ import annotations

VERSION = "0.1.0"

_ROLE_BY_TYPE = {
    "concept": "definition", "mechanism": "mechanism",
    "engineering_principle": "recommendation", "decision_rule": "recommendation",
    "design_pattern": "recommendation", "validation_strategy": "example", "failure_pattern": "limitation",
}
_UNSUPPORTED_CONFIDENCE_CAP = 0.3


def _source_id_of(any_id):
    return any_id.split(":", 1)[0]


def _block_index(source_structures):
    index = {}
    for ss in source_structures:
        for b in ss.get("blocks", []):
            index[(ss["source_id"], b["block_id"])] = b
    return index


def _direct_source_statements(obj):
    return [(s.get("block_id"), s.get("text", "")) for s in obj.get("source_statements", [])]


def _linked_source_statements(obj):
    pairs = []
    for e in obj.get("evidence", []):
        for s in e.get("source_statements", []):
            pairs.append((s.get("block_id"), s.get("text", "")))
    return pairs


def _audit_one(obj, kind, own_source_id, evidence_pairs, block_index, object_ref, errors):
    formal_evidence = []
    all_direct = True
    n = 0
    for block_id, cited_text in evidence_pairs:
        block = block_index.get((own_source_id, block_id))
        n += 1
        if block is None:
            all_direct = False
            errors.append({"code": "EVIDENCE_NOT_FOUND", "message": f"{object_ref}: cited block {block_id} not found under source {own_source_id}.", "retryable": False, "source_id": own_source_id, "affected_objects": [object_ref]})
            continue
        if block.get("source_anchor", {}).get("source_id") not in (None, own_source_id):
            all_direct = False
            errors.append({"code": "SOURCE_ATTRIBUTION_ERROR", "message": f"{object_ref}: block {block_id} is attributed to a different source.", "retryable": False, "source_id": own_source_id, "affected_objects": [object_ref]})
            continue
        support_level = "direct" if cited_text and cited_text.strip() in block.get("text", "") else "partial"
        if support_level != "direct":
            all_direct = False
        formal_evidence.append({
            "evidence_id": f"ev:{own_source_id}:{block_id}:{n}",
            "source_id": own_source_id,
            "source_type": "unknown",
            "source_language": block.get("language", "unknown"),
            "original_text": block.get("text", ""),
            "translated_text": "",
            "chapter": block.get("chapter_id", ""),
            "section": "/".join(block.get("section_path", [])),
            "page": str(block.get("page_start")) if block.get("page_start") is not None else "",
            "figure": block.get("figure_or_table_label", "") if block.get("block_type") == "figure" else "",
            "table": block.get("figure_or_table_label", "") if block.get("block_type") == "table" else "",
            "equation": "",
            "source_anchor": block.get("source_anchor", {}),
            "supports_field": object_ref,
            "evidence_role": _ROLE_BY_TYPE.get(kind, "example"),
            "subject_attribution": own_source_id,
            "support_level": support_level,
            "confidence": 0.85 if support_level == "direct" else 0.5,
        })
    evidence_supported = bool(formal_evidence) and all_direct
    return formal_evidence, evidence_supported


def _finalize(obj, kind, formal_evidence, evidence_supported):
    obj = dict(obj)
    obj["_kind"] = kind
    obj["evidence"] = formal_evidence
    obj["evidence_supported"] = evidence_supported
    current_confidence = obj.get("confidence", 0.4)
    if isinstance(current_confidence, dict):
        current_confidence = current_confidence.get("value", 0.4)
    if not evidence_supported:
        current_confidence = min(current_confidence, _UNSUPPORTED_CONFIDENCE_CAP)
        obj["knowledge_status"] = "candidate"
        if obj.get("status") == "reported":
            obj["status"] = "unknown"
    else:
        obj["knowledge_status"] = "validated" if obj.get("derivation_type") in {None, "explicit_in_source", "normalized_from_source"} else "candidate"
    obj["confidence"] = round(current_confidence, 3)
    return obj


def execute(request, **kwargs):
    source_structures = request.get("source_structures", [])
    block_index = _block_index(source_structures)
    errors = []

    audited = {"concepts": [], "mechanisms": [], "engineering_principles": [], "constraints_and_tradeoffs": [],
               "decision_rules": [], "design_patterns": [], "validation_strategies": [], "failure_patterns": []}
    all_objects = []

    for kind, key in (("concept", "concepts"), ("mechanism", "mechanisms")):
        for obj in request.get(key, []):
            source_id = _source_id_of(obj["knowledge_id"])
            evidence_pairs = _direct_source_statements(obj)
            formal_evidence, supported = _audit_one(obj, kind, source_id, evidence_pairs, block_index, obj["knowledge_id"], errors)
            final = _finalize(obj, kind, formal_evidence, supported)
            audited[key].append(final)
            all_objects.append({**final, "id": final["knowledge_id"], "type": kind})

    for kind, key, id_field in (
        ("engineering_principle", "engineering_principles", "principle_id"),
        ("decision_rule", "decision_rules", "decision_rule_id"),
        ("design_pattern", "design_patterns", "pattern_id"),
        ("validation_strategy", "validation_strategies", "validation_strategy_id"),
        ("failure_pattern", "failure_patterns", "failure_pattern_id"),
    ):
        for obj in request.get(key, []):
            ref = obj[id_field]
            source_id = _source_id_of(ref)
            evidence_pairs = _linked_source_statements(obj)
            formal_evidence, supported = _audit_one(obj, kind, source_id, evidence_pairs, block_index, ref, errors)
            final = _finalize(obj, kind, formal_evidence, supported)
            audited[key].append(final)
            all_objects.append({**final, "id": ref, "type": kind})

    audited["constraints_and_tradeoffs"] = request.get("constraints_and_tradeoffs", [])

    total = len(all_objects)
    supported_count = sum(1 for o in all_objects if o.get("evidence_supported"))
    coverage = {
        "total_objects": total,
        "objects_with_direct_evidence": supported_count,
        "coverage_ratio": round(supported_count / total, 3) if total else 1.0,
        "unresolved_object_ids": [o["id"] for o in all_objects if not o.get("evidence_supported")],
    }

    status = "succeeded_with_warnings" if errors else "succeeded"
    return {
        "output": {**audited, "all_objects": all_objects, "evidence_coverage": coverage},
        "status": status, "errors": errors,
        "provenance": {"step_version": VERSION, "source_ids": sorted({o["id"].split(":", 1)[0] for o in all_objects}) if all_objects else []},
    }
