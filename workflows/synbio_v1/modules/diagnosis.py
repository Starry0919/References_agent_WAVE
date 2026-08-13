"""Module 2 - Biological Diagnosis (spec section 12).

Surfaces the matched DDR's biological_diagnosis and engineering_hypothesis
verbatim rather than independently re-deriving the biology - dev rule 3
("keep biological evidence separated from model reasoning"). This module
does not analyze pathways itself; the analysis already lives in the DDR
record produced by expert reasoning, and this module just structures it
for the report (pathway bottleneck / precursor limitation / competing
pathway / regulation / carbon allocation, per spec section 12's Module 2
analysis list, are whatever the matched DDR's `bottlenecks` cover).
"""
from __future__ import annotations

from typing import Any

_NO_MATCH_DIAGNOSIS: dict[str, Any] = {
    "matched_ddr": None,
    "observations": [],
    "bottlenecks": [],
    "mechanistic_explanation": "",
    "hypothesis": "",
    "expected_effect": "",
}


def diagnose(retrieval: dict[str, Any]) -> dict[str, Any]:
    """Extract the biological diagnosis from the retrieved DDR, if any."""
    ddr = retrieval.get("ddr")
    if ddr is None:
        return dict(_NO_MATCH_DIAGNOSIS)

    diagnosis = ddr["biological_diagnosis"]
    hypothesis = ddr["engineering_hypothesis"]
    return {
        "matched_ddr": ddr["ddr_id"],
        "observations": list(diagnosis.get("observations", [])),
        "bottlenecks": list(diagnosis.get("bottlenecks", [])),
        "mechanistic_explanation": diagnosis.get("mechanistic_explanation", ""),
        "hypothesis": hypothesis.get("hypothesis", ""),
        "expected_effect": hypothesis.get("expected_effect", ""),
    }
