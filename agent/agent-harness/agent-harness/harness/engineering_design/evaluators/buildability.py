"""BuildabilityEvaluator (doc04 §2.6): whether the candidate's targets are
resolved enough to construct at all - independent of whether a full
`BuildTestPackage` (protocol/materials/QC) exists yet, which is
`ValidationEvaluator`'s job.
"""
from __future__ import annotations

from typing import Any

from harness.engineering_design.evaluators.base import EvaluatorResult


def evaluate(candidate: dict[str, Any]) -> EvaluatorResult:
    mods = candidate.get("genetic_modifications", [])
    unresolved = [m for m in mods if m.get("target_identifier") in ("to_be_determined", "", None)]
    findings = [f"{len(mods) - len(unresolved)}/{len(mods)} modification target(s) resolved to a concrete identifier"] if mods else ["no genetic modifications - trivially buildable (reference/control)"]

    if unresolved:
        return EvaluatorResult(
            evaluator="BuildabilityEvaluator", status="insufficient_evidence", findings=findings,
            evidence_or_tool_refs=[], assumptions=[],
            required_revisions=[f"resolve target identifier for {len(unresolved)} modification(s) currently to_be_determined"],
            blocking=False,
        )
    return EvaluatorResult(evaluator="BuildabilityEvaluator", status="pass", findings=findings, evidence_or_tool_refs=[], assumptions=[], required_revisions=[], blocking=False)
