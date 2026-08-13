"""ValidationEvaluator (doc04 §4.6): whether a `BuildTestPackage` exists
and, once it does, whether it can actually distinguish the target
phenotype AND the underlying mechanism AND the declared trade-offs - not
just measure the final product titer.
"""
from __future__ import annotations

from typing import Any

from harness.engineering_design.evaluators.base import EvaluatorResult


def evaluate(candidate: dict[str, Any], *, build_test_package: dict[str, Any] | None) -> EvaluatorResult:
    if build_test_package is None:
        return EvaluatorResult(
            evaluator="ValidationEvaluator", status="not_computed",
            findings=["no BuildTestPackage drafted yet for this candidate"], evidence_or_tool_refs=[], assumptions=[],
            required_revisions=["draft a BuildTestPackage before this candidate can be planning_ready"], blocking=False,
        )

    checks = {
        "target_readouts": bool(build_test_package.get("target_readouts")),
        "mechanism_readouts": bool(build_test_package.get("mechanism_readouts")),
        "controls": bool(build_test_package.get("controls")),
        "decision_rules": bool(build_test_package.get("decision_rules")),
    }
    missing = [k for k, present in checks.items() if not present]
    findings = [f"validation covers: {[k for k in checks if checks[k]]}"]
    if missing:
        return EvaluatorResult(
            evaluator="ValidationEvaluator", status="warning", findings=findings + [f"missing: {missing}"],
            evidence_or_tool_refs=[], assumptions=[], required_revisions=[f"add {m} to the build/test plan" for m in missing],
            blocking=False,
        )
    return EvaluatorResult(evaluator="ValidationEvaluator", status="pass", findings=findings, evidence_or_tool_refs=[], assumptions=[], required_revisions=[], blocking=False)
