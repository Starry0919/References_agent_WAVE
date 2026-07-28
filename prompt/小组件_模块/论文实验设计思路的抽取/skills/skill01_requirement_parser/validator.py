"""Contract, hallucination and executability checks for Skill01."""

from __future__ import annotations

from typing import Any, Dict, List, Mapping, Optional

try:
    from .schema import ALLOWED_FIELD_STATUSES
except ImportError:
    from schema import ALLOWED_FIELD_STATUSES

REQUIRED_INTENT_FIELDS = {
    "organism", "strain", "phenotype", "engineering_objective",
    "keywords", "inclusion_criteria", "exclusion_criteria",
}


def validate_input(request: Mapping[str, Any]) -> Optional[Dict[str, Any]]:
    valid_mapping = isinstance(request, Mapping)
    value = request.get("user_request") if valid_mapping else None
    constraints = request.get("constraints", {}) if valid_mapping else None
    if isinstance(value, str) and value.strip() and isinstance(constraints, Mapping):
        return None
    return {
        "code": "EDX-VAL-001",
        "local_code": "REQ001",
        "category": "validation",
        "message": "user_request must be a non-empty string and constraints must be an object.",
        "retryable": False,
        "severity": "error",
        "context": {"field": "user_request"},
        "suggested_action": "Provide a non-empty natural-language research request.",
    }


def validate_output(output: Mapping[str, Any]) -> List[Dict[str, Any]]:
    intent = output.get("research_intent", {})
    metadata = output.get("field_metadata", {})
    strategy = output.get("retrieval_strategy", {})
    coverage = REQUIRED_INTENT_FIELDS == set(intent) == set(metadata)
    consistent = coverage and all(
        metadata[name].get("value") == intent[name]
        and metadata[name].get("status") in ALLOWED_FIELD_STATUSES
        and metadata[name].get("source") == "user_input"
        for name in REQUIRED_INTENT_FIELDS
    )
    no_hallucinated_missing = coverage and all(
        not (
            item.get("status") in {"unknown", "needs_clarification"}
            and item.get("value") not in (None, [])
        )
        for item in metadata.values()
    )
    clarification_ready = any(
        item.get("status") == "needs_clarification" for item in metadata.values()
    )
    executable = bool(strategy.get("queries")) or bool(
        output.get("field_metadata", {}).get("engineering_objective", {}).get("value")
    ) or clarification_ready
    return [
        {"name": "schema_completeness", "passed": coverage},
        {"name": "metadata_value_consistency", "passed": consistent},
        {"name": "hallucination_prevention", "passed": no_hallucinated_missing},
        {"name": "search_executability", "passed": executable},
    ]
