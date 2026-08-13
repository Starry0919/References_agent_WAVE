"""Evaluator Module (revision spec section 6): a gate before the final report.

Checks every engineering design for:
1. Evidence completeness - does the recommendation have supporting evidence?
2. Biological consistency - does the modification conflict with cell survival?
3. Engineering feasibility - is the modification a technique V0.1 recognizes?
4. Confidence level - low-confidence designs are accepted but flagged.

`ESSENTIAL_GENES_MOCK` is loaded from the shared
`knowledge/biological_rules/essential_genes_reference.json` (also consulted
by `harness/workflow/gates.py`'s IdentityGate/BiologicalRuleGate, so both
paths agree on one illustrative list instead of duplicating a hardcoded
set). It remains illustrative only - see that file's `_disclaimer` - NOT a
curated E. coli essentiality dataset. Do not treat its absence/presence as
a real safety signal outside this V0.1 skeleton.
"""
from __future__ import annotations

from typing import Any

from harness.workflow import gene_registry
from workflows.synbio_v01.modules.engineering import MODIFICATION_VOCABULARY

ESSENTIAL_GENES_MOCK: frozenset[str] = frozenset(gene_registry.essential_genes())


def _split_genes(gene_field: str) -> list[str]:
    return [g.strip() for g in gene_field.replace("/", ",").split(",") if g.strip()]


def evaluate(
    engineering_designs: list[dict[str, Any]],
    evidence_records: list[dict[str, Any]],
    competition_records: list[dict[str, Any]],
) -> dict[str, Any]:
    """Accept, reject, or warn on each engineering design."""
    evidence_by_recommendation = {e["recommendation"]: e for e in evidence_records}

    accepted: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    warnings: list[str] = []

    for design in engineering_designs:
        recommendation = f"{design['modification']} {design['gene']}"
        evid = evidence_by_recommendation.get(recommendation)
        genes = _split_genes(design["gene"])
        issues: list[str] = []

        # 1. Evidence completeness
        if evid is None or not evid.get("evidence") or evid["evidence"].startswith("none"):
            issues.append(f"{design['gene']}: no supporting evidence found - evidence completeness check failed")

        # 2. Biological consistency: don't knock out a (mock) essential gene
        essential_hit = [g for g in genes if g in ESSENTIAL_GENES_MOCK]
        if design["modification"] == "knockout" and essential_hit:
            issues.append(
                f"{', '.join(essential_hit)} flagged essential in the V0.1 mock essential-gene list - "
                "knockout risks lethality"
            )

        # 3. Engineering feasibility: is this a technique V0.1 recognizes?
        if design["modification"] not in MODIFICATION_VOCABULARY.values():
            issues.append(f"{design['gene']}: '{design['modification']}' is not a recognized V0.1 modification technique")

        if issues:
            rejected.append({**design, "rejection_reasons": issues})
            warnings.extend(issues)
            continue

        # 4. Confidence level: accepted, but flag low-confidence designs
        if evid and evid.get("confidence") == "low":
            warnings.append(
                f"{design['gene']}: low-confidence recommendation ({evid['evidence']}) - "
                "flagged for validation before wet-lab use"
            )

        # Cross-check against competition-pathway risks for the same gene(s)
        for comp in competition_records:
            comp_genes = _split_genes(comp.get("gene", ""))
            if any(g in comp_genes for g in genes) and comp.get("risk"):
                warnings.append(f"{design['gene']}: competition-pathway risk - {comp['risk']}")

        accepted.append(design)

    return {"accepted_designs": accepted, "rejected_designs": rejected, "warnings": warnings}
