"""Module 2 — Pathway Analysis: structured placeholder pathway knowledge.

V0.1 uses a small hardcoded knowledge base as a stand-in for a future
pathway database (e.g. KEGG/MetaCyc). No external database calls happen here.
"""
from __future__ import annotations

from typing import Any

_PATHWAY_MOCK_DB: dict[str, dict[str, Any]] = {
    "tryptophan": {
        "pathway": "shikimate pathway -> chorismate -> anthranilate -> tryptophan (trp operon)",
        "substrate": "glucose",
        "intermediates": [
            "phosphoenolpyruvate", "erythrose-4-phosphate", "DAHP",
            "shikimate", "chorismate", "anthranilate",
            "N-(5-phosphoribosyl)-anthranilate", "indole-3-glycerol phosphate",
        ],
        "enzymes": [
            "DAHP synthase (AroG/AroF/AroH)",
            "anthranilate synthase (TrpE/TrpD)",
            "anthranilate phosphoribosyltransferase (TrpD)",
            "PRA isomerase / IGP synthase (TrpC)",
            "tryptophan synthase (TrpB/TrpA)",
        ],
        "genes": ["aroG", "aroF", "aroH", "trpE", "trpD", "trpC", "trpB", "trpA", "trpR", "tnaA"],
    },
}

_GENERIC_PATHWAY: dict[str, Any] = {
    "pathway": "pathway unknown in the V0.1 mock knowledge base",
    "substrate": "",
    "intermediates": [],
    "enzymes": [],
    "genes": [],
}


def analyze(task: dict[str, Any]) -> dict[str, Any]:
    """Return structured pathway knowledge for the task's target product."""
    product = task.get("product", "").lower()
    entry = _PATHWAY_MOCK_DB.get(product)
    if entry is None:
        return dict(_GENERIC_PATHWAY, substrate=task.get("substrate", ""))
    result = dict(entry)
    result["substrate"] = task.get("substrate") or entry["substrate"]
    return result
