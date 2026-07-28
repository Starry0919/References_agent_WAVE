"""Engineering-decision diff (doc 6.4's DesignDiff, layer 2: engineering
decision) - mechanism/risk/confidence changes between two DesignVersions'
decision sets, keyed like `genotype_diff` by (target, operation).
"""
from __future__ import annotations

from typing import Any

_TRACKED_FIELDS = ("mechanism_hypothesis_ids", "expected_effects", "risks", "confidence", "approval_state")


def _decision_key(d: dict[str, Any]) -> tuple[str, str]:
    return (d.get("target", "unknown"), d.get("operation", "unknown"))


def diff_decisions(baseline: list[dict[str, Any]], candidate: list[dict[str, Any]]) -> dict[str, Any]:
    """Returns `{added, removed, changed, unchanged}`. `changed` entries
    name exactly which tracked fields differ, not just that something did."""
    baseline_by_key = {_decision_key(d): d for d in baseline}
    candidate_by_key = {_decision_key(d): d for d in candidate}

    added = [d for k, d in candidate_by_key.items() if k not in baseline_by_key]
    removed = [d for k, d in baseline_by_key.items() if k not in candidate_by_key]
    changed: list[dict[str, Any]] = []
    unchanged: list[dict[str, Any]] = []
    for key in set(baseline_by_key) & set(candidate_by_key):
        before, after = baseline_by_key[key], candidate_by_key[key]
        fields_changed = [f for f in _TRACKED_FIELDS if before.get(f) != after.get(f)]
        if fields_changed:
            changed.append({"target": key[0], "operation": key[1], "fields_changed": fields_changed, "before": before, "after": after})
        else:
            unchanged.append(after)

    return {"added": added, "removed": removed, "changed": changed, "unchanged": unchanged}
