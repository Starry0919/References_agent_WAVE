"""ConfidenceEvaluator (Module 2 - Engineering Decision Intelligence Layer
prompt §11): the "Confidence" dimension the spec names explicitly and
separately from Evidence/Mechanism - audit finding: the existing 8
evaluators (`EVALUATOR_NAMES`) had no evaluator whose job is specifically
"how confident should a reviewer be overall, and why."

Deliberately an AGGREGATOR, not a new measurement: it reads the evidence
tier already computed by `evaluators.evidence.strongest_tier`, whether a
real (`runtime_status == "optimal"`) counterfactual run exists, and the
already-computed `MechanismEvaluator` status - combining them via an
explicit, reviewable rule table into one of three qualitative confidence
levels, each with a stated reason. Never a bare number: this package's own
`decision.py` docstring forbids exactly that ("never collapsed into a
single unweighted or arbitrarily-weighted composite score"), and the same
discipline applies here - `EvaluatorResult.findings` always names which
specific component (evidence/model/mechanism) is strong or weak.
"""
from __future__ import annotations

from typing import Any

from harness.engineering_design.evaluators import evidence as evidence_mod
from harness.engineering_design.evaluators.base import EvaluatorResult

_STRONG_EVIDENCE_TIERS = {"experimental_evidence", "model_computation", "curated_knowledge"}


def evaluate(candidate: dict[str, Any], *, mechanism_status: str, counterfactual_runs: list[dict[str, Any]] | None = None) -> EvaluatorResult:
    counterfactual_runs = counterfactual_runs or []
    tier = evidence_mod.strongest_tier(candidate)
    has_model_result = any(r.get("runtime_status") == "optimal" for r in counterfactual_runs)
    mechanism_clean = mechanism_status == "pass"

    findings: list[str] = [
        f"evidence: strongest linked tier is {tier!r}" + (" (strong)" if tier in _STRONG_EVIDENCE_TIERS else " (not strong)"),
        f"model computation: {'a real optimal counterfactual run exists' if has_model_result else 'no computed model result available'}",
        f"mechanism: {'traces cleanly to a known, declared strategy' if mechanism_clean else 'MechanismEvaluator did not report a clean pass'}",
    ]

    if tier == "unknown" and not has_model_result and not mechanism_clean:
        return EvaluatorResult(
            evaluator="ConfidenceEvaluator", status="insufficient_evidence", findings=findings,
            evidence_or_tool_refs=[], assumptions=[],
            required_revisions=["no evidence, no model computation, and no clean mechanism linkage - overall confidence cannot be assessed"],
            blocking=candidate.get("portfolio_role") != "reference_or_control",
        )

    strong_components = sum([tier in _STRONG_EVIDENCE_TIERS, has_model_result, mechanism_clean])
    if strong_components >= 2:
        status = "pass"
        required_revisions: list[str] = []
    else:
        status = "warning"
        required_revisions = ["strengthen at least one of evidence/model computation/mechanism linkage before treating this as high confidence"]

    return EvaluatorResult(
        evaluator="ConfidenceEvaluator", status=status, findings=findings,
        evidence_or_tool_refs=[str(l.get("reference", "")) for l in evidence_mod.all_evidence_links(candidate)],
        assumptions=["confidence is an aggregate of already-computed evidence/model/mechanism signals, not an independent measurement"],
        required_revisions=required_revisions, blocking=False,
    )
