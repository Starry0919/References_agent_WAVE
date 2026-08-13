"""Module 5 - Evidence Evaluation: attach evidence/confidence/validation to every suggestion.

Confidence is derived from `evidence_type`, honestly reflecting that
V0.1's DDR store is entirely mock/unverified data: "mock evidence" always
maps to "low" confidence and always needs validation, even when the
underlying biology is textbook-standard - see literature.py's disclaimer.
"""
from __future__ import annotations

from typing import Any

_CONFIDENCE_BY_EVIDENCE_TYPE = {
    "hard evidence": "high",
    "soft evidence": "medium",
    "mock evidence": "low",
}


def evaluate(
    engineering_designs: list[dict[str, Any]],
    literature_records: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Pair each engineering suggestion with its supporting DDR, or flag it unsupported."""
    by_target = {record.get("target", "").lower(): record for record in literature_records}
    evaluations: list[dict[str, Any]] = []
    for item in engineering_designs:
        record = by_target.get(item["gene"].lower())
        if record and record.get("evidence"):
            evidence_type = record.get("evidence_type", "mock evidence")
            evaluations.append({
                "recommendation": f"{item['modification']} {item['gene']}",
                "evidence": record["evidence"],
                "confidence": _CONFIDENCE_BY_EVIDENCE_TYPE.get(evidence_type, "low"),
                "needs_validation": evidence_type != "hard evidence",
            })
        else:
            evaluations.append({
                "recommendation": f"{item['modification']} {item['gene']}",
                "evidence": "none (V0.1 mock knowledge base has no record for this target)",
                "confidence": "low",
                "needs_validation": True,
            })
    return evaluations
