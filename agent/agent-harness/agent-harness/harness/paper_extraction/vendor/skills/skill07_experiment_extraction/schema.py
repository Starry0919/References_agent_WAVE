import hashlib
import json
from typing import Any

SKILL_ID = "skill07_experiment_extraction"
SKILL_VERSION = "0.2.0"
CORE_FIELDS = [
    "objective", "hypothesis", "strain", "genotype", "engineering_method",
    "experimental_groups", "controls", "culture_conditions", "medium",
    "dosage", "time", "replicates", "assay", "instruments",
    "analysis_methods", "outcomes"
]


def sha256_json(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(raw.encode("utf-8")).hexdigest()


def unknown_field():
    return {
        "value": None, "status": "unknown", "confidence": 1.0,
        "extraction_method": "not_applicable", "evidence_ids": [],
        "notes": "Not reported in the supplied clean document."
    }


def reported_field(value, candidates, confidence=0.9, notes=None):
    evidence_ids = list(dict.fromkeys(f"candidate:{v['paragraph_id']}" for v in candidates))
    return {
        "value": value, "status": "reported", "confidence": round(confidence, 3),
        "extraction_method": "rule",
        "evidence_ids": evidence_ids,
        "notes": notes
    }
