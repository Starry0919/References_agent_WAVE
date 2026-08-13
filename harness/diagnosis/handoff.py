"""Problem 3 -> Problem 4 handoff (doc03 6.2). Audit finding: Problem 4
(Engineering Design Generation) has no standalone implementation in this
repository yet - only a design doc exists
(`问题04_Engineering_Design_Generation_...md`). The real, currently-existing
"Engineering Design" system is Problem 01's synbio Workflow Engine
(`harness.workflow.synbio_stages.build_controller`), which already
produces gated, evidence-backed `EngineeringDecision`s. This module is the
literal handoff target: a gated `DiagnosisDecision` becomes context for a
new Problem 01 `WorkflowRun`, not a second, parallel design generator -
when a standalone Problem 4 system is built, this is the one call site
that needs to be repointed.
"""
from __future__ import annotations

from harness.diagnosis.models import DiagnosisDecision
from harness.workflow.state import WorkflowRun
from harness.workflow.synbio_stages import build_controller


class HandoffNotAllowedError(RuntimeError):
    """The decision was never gated to an approved, actionable handoff -
    defense in depth beyond the caller's own `DiagnosisHandoffGate` check."""


def build_design_request_from_decision(decision: DiagnosisDecision, *, target_product: str, host: str) -> str:
    """Renders the gated decision into the free-text `raw_request` Problem
    01's INTAKE stage expects - carries leading hypotheses, alternatives
    NOT excluded, and unresolved contradictions forward as context, never
    silently treating an unresolved alternative as ruled out (doc03 6.2)."""
    lines = [
        f"Improve {target_product} production in {host}.",
        f"Diagnosis {decision.diagnosis_session_id} v{decision.diagnosis_version} leading hypothesis set: {decision.leading_hypothesis_ids}.",
    ]
    if decision.alternatives_not_excluded_ids:
        lines.append(f"Alternatives NOT excluded (do not assume ruled out): {decision.alternatives_not_excluded_ids}.")
    if decision.contradictions:
        lines.append(f"Known contradictions/unresolved conflicts: {decision.contradictions}.")
    lines.append(f"Uncertainty: {decision.uncertainty}")
    return " ".join(lines)


def hand_off_to_engineering_design(decision: DiagnosisDecision, *, target_product: str, host: str, session=None) -> WorkflowRun:
    """Triggers a real Problem 01 `WorkflowRun`. Only callable once the
    decision has been gated: `stopping_reason == "actionable_stop"` and
    `handoff_status` already approved."""
    if decision.stopping_reason != "actionable_stop":
        raise HandoffNotAllowedError(f"decision stopping_reason={decision.stopping_reason!r} is not actionable_stop")
    if decision.handoff_status not in ("approved", "handed_off"):
        raise HandoffNotAllowedError(f"decision handoff_status={decision.handoff_status!r} has not been approved")
    if session is not None:
        from harness.diagnosis.grounding import evaluate_observation_grounding
        result = evaluate_observation_grounding(session, decision.diagnosis_session_id)
        if not result.actionable:
            raise HandoffNotAllowedError(f"data_required: {result.blocking_reasons}")

    request = build_design_request_from_decision(decision, target_product=target_product, host=host)
    controller = build_controller()
    run = controller.create_run(request)
    return controller.run_to_completion_or_pause(run, max_steps=30)
