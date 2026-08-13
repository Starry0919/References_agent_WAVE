"""Service-layer guards (doc06 §10, §14.1) - enforced in code, not only
documented in a prompt. Every guard here is exercised by a dedicated
failure-path test in `tests/virtual_cell/`.
"""
from __future__ import annotations

from harness.designs.models import DesignVersion
from harness.virtual_cell.models import CompatibilityReport, CounterfactualComparison, ModelUpdateProposal, PredictionReview, SimulationRun


class SimulationGuardError(RuntimeError):
    """Raised when a workflow-invariant guard rejects an action."""


_EVALUATION_BLOCKING_STATUSES = {"rejected", "returned_to_diagnosis", "stopped", "held"}


def assert_evaluation_not_blocking(evaluation_case, *, human_override: dict | None = None) -> None:
    """doc06 §10: 'Problem 5 有 blocking rejection 时不得直接模拟，除非
    Human Override 被审计记录'. `evaluation_case` is a `harness.
    scientific_evaluation.models.EvaluationCase | None`; `human_override`
    must be an explicit, actor-attributed override record (never a bare
    True) to proceed anyway."""
    if evaluation_case is None:
        return
    if evaluation_case.status in _EVALUATION_BLOCKING_STATUSES and not human_override:
        raise SimulationGuardError(
            f"EvaluationCase {evaluation_case.evaluation_id} is {evaluation_case.status!r} (blocking); "
            "Problem 06 may not simulate this DesignVersion without an audited Human Override"
        )
    if human_override is not None and not human_override.get("approver_id"):
        raise SimulationGuardError("human_override must carry an approver_id to be a valid audited override")


def assert_design_version_formal(design_version: DesignVersion | None) -> None:
    """doc06 §10: 'Problem 4 正式 DesignVersion 不存在，不得编译' - only an
    `approved` `DesignVersion` may be compiled into perturbations."""
    if design_version is None:
        raise SimulationGuardError("no such DesignVersion")
    if design_version.status != "approved":
        raise SimulationGuardError(
            f"DesignVersion {design_version.design_version_id} is not a formal (approved) design "
            f"(status={design_version.status!r}); Problem 06 may not compile a proposed/rejected design"
        )


def assert_compatible_before_run(report: CompatibilityReport) -> None:
    if report.decision not in ("compatible", "compatible_with_assumptions"):
        raise SimulationGuardError(
            f"compatibility decision {report.decision!r} does not permit a run "
            f"(blocking_reasons={report.blocking_reasons})"
        )


def assert_baseline_succeeded_before_delta(baseline_run: SimulationRun) -> None:
    if baseline_run.status != "optimal":
        raise SimulationGuardError(
            f"baseline run {baseline_run.model_run_id} did not succeed (status={baseline_run.status}); "
            "no counterfactual delta may be produced without a successful baseline"
        )


def assert_comparison_valid_before_review(comparison: CounterfactualComparison) -> None:
    if comparison.comparability_status != "comparable":
        raise SimulationGuardError(
            f"comparison {comparison.comparison_id} is {comparison.comparability_status!r} "
            f"(violations={comparison.comparability_violations}); cannot proceed to prediction review"
        )


def assert_review_passed_before_decision(review: PredictionReview) -> None:
    blocking = [f for f in review.findings if f.get("severity") == "blocking"]
    if blocking:
        raise SimulationGuardError(
            f"prediction review {review.review_id} has {len(blocking)} unresolved blocking finding(s); "
            "cannot be used as a decision basis until resolved"
        )
    if review.decision != "decision_ready":
        raise SimulationGuardError(f"prediction review decision is {review.decision!r}, not decision_ready")


def assert_context_matches_before_residual(context_match: bool, mismatch_status: str) -> None:
    if not context_match:
        raise SimulationGuardError(f"observation context mismatch ({mismatch_status}); residual may not be computed")


def assert_update_may_activate(proposal: ModelUpdateProposal, *, has_human_approval: bool) -> None:
    """doc06 §9.4/§2.9: Level 3-5 updates require a Human Gate decision
    before `status` may become `approved`/`applied` - enforced here, not
    only by a frontend button (doc06 §15.16)."""
    if proposal.update_level in ("parameter_calibration", "model_structure", "model_retraining") and not has_human_approval:
        raise SimulationGuardError(
            f"update proposal {proposal.proposal_id} is level={proposal.update_level!r}; "
            "requires an explicit ModelUpdateDecision before it may be approved/applied"
        )
