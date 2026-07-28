"""Experimental Validation Module (V1.1 Phase 4).

The V1 validation plan was too general ("measure metabolites"). This
buckets every validation step into the four levels the spec requires, and
- for the level nothing upstream ever populated (genotype confirmation) -
generates one standard molecular-biology QC step per action. That's
routine practice (PCR/sequencing to confirm an intended edit), not a
biological claim, so it carries no fabrication risk the way inventing a
paper result would.

Level 4 (trade-off) is derived directly from each action's own `risk`
field rather than invented separately, keeping it grounded in what the
action already states.
"""
from __future__ import annotations

from typing import Any

_MECHANISM_KEYWORDS = (
    "metabolite", "enzyme activity", "flux", "intracellular", "pool",
    "13c", "transcript", "qrt-pcr", "reporter-fusion", "cofactor",
)
_PHENOTYPE_KEYWORDS = ("titer", "yield", "productivity", "growth", "biomass")
_GENOTYPE_KEYWORDS = ("pcr", "sequenc", "genotyp", "genome verif", "southern blot")


def _classify(text: str) -> str:
    lowered = text.lower()
    if any(k in lowered for k in _GENOTYPE_KEYWORDS) and "qrt-pcr" not in lowered:
        return "genotype"
    if any(k in lowered for k in _PHENOTYPE_KEYWORDS):
        return "phenotype"
    if any(k in lowered for k in _MECHANISM_KEYWORDS):
        return "mechanism"
    return "mechanism"  # default bucket for otherwise-unclassified DDR validation text


def build_validation_plan(engineering_actions: list[dict[str, Any]]) -> dict[str, list[str]]:
    """Aggregate a 4-level {genotype, mechanism, phenotype, tradeoff} validation plan."""
    plan: dict[str, list[str]] = {"genotype": [], "mechanism": [], "phenotype": [], "tradeoff": []}

    for action in engineering_actions:
        target = action.get("target", "unknown target")
        modification = action.get("modification_type", "modification")

        plan["genotype"].append(
            f"{target}: confirm the {modification} by PCR and/or sequencing of the target locus"
        )

        existing = action.get("validation", [])
        classified_any_mechanism = False
        classified_any_phenotype = False
        for item in existing:
            level = _classify(item)
            plan[level].append(f"{target}: {item}")
            classified_any_mechanism = classified_any_mechanism or level == "mechanism"
            classified_any_phenotype = classified_any_phenotype or level == "phenotype"

        if not classified_any_mechanism:
            plan["mechanism"].append(
                f"{target}: measure the expected mechanistic effect (e.g. relevant enzyme activity, "
                f"transcript level, or metabolite pool) relative to the unmodified strain"
            )
        if not classified_any_phenotype:
            plan["phenotype"].append(
                f"{target}: compare strain titer, yield, and growth to the unmodified control strain"
            )

        risk = action.get("risk")
        if risk:
            plan["tradeoff"].append(f"{target}: monitor for the stated risk - {risk}")

    return plan
