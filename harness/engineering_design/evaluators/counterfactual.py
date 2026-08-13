"""CounterfactualEvaluator (doc04 §2.4, §9): reports whatever
`CounterfactualRun` records exist for this candidate honestly - `not_
computed` when none were requested/available, never a fabricated
prediction, and never silently averages disagreeing runs.
"""
from __future__ import annotations

from typing import Any

from harness.engineering_design.evaluators.base import EvaluatorResult


def evaluate(candidate: dict[str, Any], *, counterfactual_runs: list[dict[str, Any]]) -> EvaluatorResult:
    if not counterfactual_runs:
        return EvaluatorResult(
            evaluator="CounterfactualEvaluator", status="not_computed",
            findings=["no counterfactual model run has been requested/executed for this candidate"],
            evidence_or_tool_refs=[], assumptions=[],
            required_revisions=["request a counterfactual run via a real model adapter, or record why none applies"],
            blocking=False,
        )

    computed = [r for r in counterfactual_runs if r.get("runtime_status") == "optimal"]
    unavailable = [r for r in counterfactual_runs if r.get("capability_status") == "unavailable"]
    findings = [
        f"{len(computed)}/{len(counterfactual_runs)} run(s) produced a usable result; "
        f"{len(unavailable)} adapter(s) reported unavailable"
    ]
    refs = [str(r.get("run_id", "")) for r in counterfactual_runs]

    if len(computed) >= 2:
        values = [r["outputs"]["objective_value"] for r in computed if "objective_value" in r.get("outputs", {})]
        if len(values) >= 2:
            spread = (max(values) - min(values)) / (abs(max(values)) or 1.0)
            if spread >= 0.25:
                return EvaluatorResult(
                    evaluator="CounterfactualEvaluator", status="warning",
                    findings=findings + [f"model runs disagree (relative spread {spread:.0%}) - conflict preserved, not averaged"],
                    evidence_or_tool_refs=refs, assumptions=[], required_revisions=["resolve via additional evidence or human review"],
                    blocking=False,
                )
    if not computed:
        return EvaluatorResult(
            evaluator="CounterfactualEvaluator", status="insufficient_evidence", findings=findings,
            evidence_or_tool_refs=refs, assumptions=[], required_revisions=["no model run produced a usable result"], blocking=False,
        )
    return EvaluatorResult(evaluator="CounterfactualEvaluator", status="pass", findings=findings, evidence_or_tool_refs=refs, assumptions=[], required_revisions=[], blocking=False)
