"""DiversityEvaluator (doc04 §4.3/§13.3): catches a candidate that is only
a surface rewrite of a sibling in the same portfolio - identical genetic-
modification signature, different prose.
"""
from __future__ import annotations

from typing import Any

from harness.engineering_design.evaluators.base import EvaluatorResult
from harness.engineering_design.memory_integration import modification_signature


def evaluate(candidate: dict[str, Any], *, sibling_candidates: list[dict[str, Any]]) -> EvaluatorResult:
    own_sig = modification_signature(candidate.get("genetic_modifications", []))
    duplicates = [
        s["design_id"] for s in sibling_candidates
        if s["design_id"] != candidate.get("design_id")
        and modification_signature(s.get("genetic_modifications", [])) == own_sig
        and own_sig  # an empty signature (reference/control) is legitimately shared
    ]
    if duplicates:
        return EvaluatorResult(
            evaluator="DiversityEvaluator", status="fail",
            findings=[f"identical genetic-modification set as sibling candidate(s): {duplicates}"],
            evidence_or_tool_refs=duplicates, assumptions=[],
            required_revisions=["differentiate this candidate's mechanism/architecture or remove the duplicate"],
            blocking=True,
        )
    return EvaluatorResult(
        evaluator="DiversityEvaluator", status="pass",
        findings=["no sibling candidate in this portfolio shares this candidate's genetic-modification signature"],
        evidence_or_tool_refs=[], assumptions=[], required_revisions=[], blocking=False,
    )
