"""Competition Pathway Analysis (revision spec section 5).

Runs after pathway analysis and before genetic design: identifies
pathways that compete with the target pathway for shared precursors or
that degrade the accumulated product, so the engineering/evaluator
modules can weigh interventions against those risks instead of designing
against the target pathway in isolation.

V0.1 uses a small mock knowledge base, same caveat as literature.py: not
backed by a verified literature lookup.
"""
from __future__ import annotations

from typing import Any

_COMPETITION_MOCK_DB: dict[str, list[dict[str, Any]]] = {
    "tryptophan": [
        {
            "pathway": "aromatic amino acid biosynthesis (shikimate pathway)",
            "competition": "tyrosine and phenylalanine biosynthesis share the DAHP-synthase-derived precursor pool and the chorismate branch point",
            "gene": "aroG/aroF/aroH, pheA, tyrA",
            "strategy": "use a feedback-resistant DAHP synthase isoenzyme (e.g. aroG_fbr) to secure precursor flux toward the shared branch point before committing flux to trp-specific steps",
            "risk": "over-diverting chorismate toward tryptophan can starve tyrosine/phenylalanine synthesis, which may impair growth unless those pathways are otherwise supplemented",
        },
        {
            "pathway": "tryptophan accumulation",
            "competition": "tryptophanase (tnaA) catabolizes accumulated tryptophan back to indole, pyruvate, and ammonia",
            "gene": "tnaA",
            "strategy": "knock out tnaA to block the degradation route",
            "risk": "tnaA deletion may affect indole-dependent signaling/biofilm behavior; low risk to core viability under standard fermentation conditions",
        },
    ],
}

_GENERIC_COMPETITION: dict[str, Any] = {
    "pathway": "pathway unknown in the V0.1 mock knowledge base",
    "competition": "no competing-pathway data available",
    "gene": "",
    "strategy": "",
    "risk": "unassessed - flag for future literature/flux analysis",
}


def analyze(task: dict[str, Any]) -> list[dict[str, Any]]:
    """Return mock competition-pathway records for the task's target product."""
    product = task.get("product", "").lower()
    records = _COMPETITION_MOCK_DB.get(product)
    if records:
        return [dict(record) for record in records]
    return [dict(_GENERIC_COMPETITION)]
