"""Load and validate the machine-readable Skill07 semantic rules.

The YAML file is the normative source of controlled vocabularies and
cross-field invariants.  This module deliberately contains no duplicate
reason-nature or evidence-role lists: it only validates the shape needed by
the runtime and offers vocabulary-neutral lookup helpers.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any, Mapping

import yaml


_REQUIRED_REASON_NATURES = {
    "mechanistic_inference",
    "literature_analogy",
    "resource_available",
    "screening_derived",
    "evolution_derived",
    "rationale_not_reported",
    "post_hoc_rationalization_uncertain",
}


@lru_cache(maxsize=8)
def _parse_rules(payload: bytes) -> dict[str, Any]:
    value = yaml.safe_load(payload.decode("utf-8"))
    if not isinstance(value, dict):
        raise ValueError("Skill07 validation rules must be a YAML mapping")
    validate_rules_document(value)
    return value


def load_validation_rules(path: str | Path) -> dict[str, Any]:
    """Load a rules file by content so edits invalidate the parser cache."""
    return _parse_rules(Path(path).read_bytes())


def validate_rules_document(rules: Mapping[str, Any]) -> None:
    """Fail closed when the semantic rules omit a required runtime concept."""
    for key in (
        "version",
        "semantic_contract_version",
        "critical_checks",
        "epistemic_validation",
        "applicability_validation",
        "evidence_validation",
        "ddr_validation",
        "generalizable_rule_validation",
    ):
        if key not in rules:
            raise ValueError(f"Skill07 validation rules missing {key}")

    epistemic = rules["epistemic_validation"]
    if set(epistemic.get("statuses", [])) != {"reported", "inferred", "unknown"}:
        raise ValueError("epistemic statuses must be reported, inferred and unknown")

    applicability = rules["applicability_validation"]
    if set(applicability.get("statuses", [])) != {"applicable", "not_applicable", "uncertain"}:
        raise ValueError("applicability statuses are incomplete")

    evidence = rules["evidence_validation"]
    if evidence.get("skill07_role") != "candidate" or "verified" not in evidence.get("forbidden_skill07_roles", []):
        raise ValueError("Skill07 evidence rules must permit candidate and forbid verified")

    reason = rules["ddr_validation"].get("reason_nature", {})
    canonical = set(reason.get("canonical_values", []))
    if canonical != _REQUIRED_REASON_NATURES:
        missing = sorted(_REQUIRED_REASON_NATURES - canonical)
        extra = sorted(canonical - _REQUIRED_REASON_NATURES)
        raise ValueError(f"reason_nature vocabulary mismatch; missing={missing}, extra={extra}")

    allowed_rule_reasons = set(rules["generalizable_rule_validation"].get("allowed_reason_nature", []))
    if not allowed_rule_reasons or not allowed_rule_reasons <= canonical:
        raise ValueError("generalizable-rule reasons must be canonical reason_nature values")


def canonical_reason_nature(value: Any, rules: Mapping[str, Any]) -> str | None:
    """Return the canonical reason-nature value while accepting legacy labels."""
    if not isinstance(value, str) or not value:
        return None
    reason = rules["ddr_validation"]["reason_nature"]
    aliases = reason.get("legacy_aliases", {})
    return aliases.get(value, value)

