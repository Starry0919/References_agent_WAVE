"""Structural genotype diff (doc 6.4's DesignDiff, layer 1: genotype).
Compares two `DesignVersion.genotype_manifest` dicts by modification
identity (gene + operation), never by diffing rendered report text.
Each modification dict is `{"gene": str, "operation": str, "detail": str}`.
"""
from __future__ import annotations

from typing import Any


def _mod_key(mod: dict[str, Any]) -> tuple[str, str]:
    return (mod.get("gene", mod.get("target", "unknown")), mod.get("operation", "unknown"))


def diff_genotype(baseline: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    """Returns `{baseline_strain_changed, added, removed, modified, retained}`.
    `modified` pairs entries sharing a (gene, operation) key whose `detail`
    text differs; `retained` are identical modifications kept as-is."""
    baseline_mods = {_mod_key(m): m for m in baseline.get("modifications", [])}
    candidate_mods = {_mod_key(m): m for m in candidate.get("modifications", [])}

    added = [m for k, m in candidate_mods.items() if k not in baseline_mods]
    removed = [m for k, m in baseline_mods.items() if k not in candidate_mods]
    modified: list[dict[str, Any]] = []
    retained: list[dict[str, Any]] = []
    for key in set(baseline_mods) & set(candidate_mods):
        before, after = baseline_mods[key], candidate_mods[key]
        if before.get("detail") != after.get("detail"):
            modified.append({"gene": key[0], "operation": key[1], "before": before, "after": after})
        else:
            retained.append(after)

    return {
        "baseline_strain_changed": baseline.get("baseline_strain") != candidate.get("baseline_strain"),
        "added": added,
        "removed": removed,
        "modified": modified,
        "retained": retained,
    }
