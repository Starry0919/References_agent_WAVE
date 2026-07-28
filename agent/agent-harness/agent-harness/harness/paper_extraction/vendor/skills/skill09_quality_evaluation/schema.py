from __future__ import annotations
import hashlib, json

SKILL_ID = "skill09_quality_evaluation"
SKILL_VERSION = "0.2.0"
POLICY = "skill09-weighted-v1"
WEIGHTS = {
    "field_completeness": .25, "evidence_quality": .25,
    "experimental_logic": .15, "reproducibility": .15,
    "method_quality": .10, "workflow_quality": .10,
}

def sha256_json(value):
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

def present(field):
    return isinstance(field, dict) and field.get("status") in {"reported", "inferred"} and field.get("value") not in (None, "", [], {})

def get_fields(skill08):
    return skill08.get("literature_experiment", {}).get("fields", {})

def get_extensions(skill08, skill07=None):
    ext = skill08.get("evidence_linked_design", {}).get("extensions")
    if isinstance(ext, dict):
        return ext
    return (skill07 or {}).get("extensions", {})
