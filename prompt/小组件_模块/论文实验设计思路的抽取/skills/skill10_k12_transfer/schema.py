from __future__ import annotations
import hashlib, json
SKILL_ID = "skill10_k12_transfer"
SKILL_VERSION = "0.3.0"
POLICY = "k12-design-space-v1"

def sha256_json(value):
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(raw.encode()).hexdigest()

def unknown(notes):
    return {"value": None, "status": "unknown", "confidence": 1.0,
            "extraction_method": "not_applicable", "evidence_ids": [], "notes": notes}

def inferred(value, evidence_ids, rationale, confidence):
    if not evidence_ids:
        return unknown("Analysis could not be evidence-bound.")
    return {"value": value, "status": "inferred", "confidence": round(confidence, 3),
            "extraction_method": "rule", "evidence_ids": sorted(set(evidence_ids)),
            "notes": "AI compatibility analysis; not a literature fact.",
            "inference": {"method": "deterministic_compatibility_rule", "rationale": rationale}}

def fields_of(design):
    return design.get("fields") or design.get("experimental_design_object", {}).get("fields") or {}

def extensions_of(design):
    return design.get("extensions", {})

def value(fields, name):
    item = fields.get(name, {})
    return item.get("value") if item.get("status") in {"reported", "inferred"} else None
