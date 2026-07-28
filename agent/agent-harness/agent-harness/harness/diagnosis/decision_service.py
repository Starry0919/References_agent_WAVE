"""Persistence for `DiagnosticTest` / `ExperimentalExecutionPlan` /
`BeliefUpdateEvent` / `BottleneckValueAssessment` / `DiagnosisDecision` -
the Phase 2 objects that carry a diagnosis from ranked hypotheses through a
discriminating test to a gated handoff decision (doc03 §4.10-4.14, 3.8/
3.11-3.14).
"""
from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from harness.diagnosis.execution_planner import PlanDraft
from harness.diagnosis.models import (
    ALLOWED_NEXT_ACTIONS,
    STOPPING_REASONS,
    BeliefUpdateEvent,
    BottleneckValueAssessment,
    DiagnosisDecision,
    DiagnosisSession,
    DiagnosticTest,
    ExperimentalExecutionPlan,
)
from harness.ids import new_id, now
from harness.memory import event_types as et
from harness.memory.event_store import append_event, snapshot

TEST_FIELDS = (
    "test_id", "diagnosis_session_id", "compared_hypothesis_ids", "predicted_outcomes_per_hypothesis", "assay",
    "positive_control", "negative_control", "decision_rule", "expected_information_gain", "cost", "turnaround",
    "availability", "technical_feasibility", "risk", "prerequisites", "discriminates_hypotheses", "status", "created_at",
)
PLAN_FIELDS = (
    "plan_id", "diagnostic_test_id", "protocol_reference_or_draft", "materials", "controls",
    "biological_replicates", "technical_replicates", "sampling_schedule", "qc_acceptance_criteria",
    "expected_output_schema", "interpretation_rule", "owner", "approval_state", "readiness", "created_at",
)
DECISION_FIELDS = (
    "decision_id", "diagnosis_session_id", "diagnosis_version", "context_reference", "leading_hypothesis_ids",
    "supported_hypothesis_ids", "alternatives_not_excluded_ids", "contradictions", "confidence_representation",
    "uncertainty", "evidence_references", "model_assessment_reference", "selected_diagnostic_test_id",
    "stopping_reason", "engineering_value_assessment", "allowed_next_action", "handoff_status", "human_approval",
    "created_by", "created_at",
)


def create_diagnostic_test(
    session: Session,
    *,
    project_id: str,
    diagnosis_session_id: str,
    compared_hypothesis_ids: list[str],
    predicted_outcomes_per_hypothesis: dict[str, Any],
    actor_id: str,
    assay: str = "",
    positive_control: str = "",
    negative_control: str = "",
    decision_rule: str = "",
    expected_information_gain: str = "unknown",
    cost: str = "unknown",
    turnaround: str = "unknown",
    availability: str = "unknown",
    technical_feasibility: str = "unknown",
    risk: str = "unknown",
    prerequisites: list[str] | None = None,
    discriminates_hypotheses: bool = False,
) -> DiagnosticTest:
    t = DiagnosticTest(
        test_id=new_id("DTEST"), diagnosis_session_id=diagnosis_session_id, compared_hypothesis_ids=compared_hypothesis_ids,
        predicted_outcomes_per_hypothesis=predicted_outcomes_per_hypothesis, assay=assay, positive_control=positive_control,
        negative_control=negative_control, decision_rule=decision_rule, expected_information_gain=expected_information_gain,
        cost=cost, turnaround=turnaround, availability=availability, technical_feasibility=technical_feasibility, risk=risk,
        prerequisites=prerequisites or [], discriminates_hypotheses=discriminates_hypotheses, status="proposed",
        created_by=actor_id, created_at=now(),
    )
    session.add(t)
    session.flush()
    append_event(
        session, project_id=project_id, event_type=et.DIAGNOSIS_TEST_SELECTED, entity_type="DiagnosticTest",
        entity_id=t.test_id, payload=snapshot(t, TEST_FIELDS), actor_type="agent", actor_id=actor_id,
    )
    return t


def mark_test_selected(session: Session, *, test_id: str) -> DiagnosticTest:
    t = session.get(DiagnosticTest, test_id)
    if t is None:
        raise ValueError(f"no such diagnostic test: {test_id}")
    t.status = "selected"
    session.flush()
    return t


def create_execution_plan(
    session: Session, *, project_id: str, diagnostic_test_id: str, actor_id: str, plan: PlanDraft, readiness: str
) -> ExperimentalExecutionPlan:
    p = ExperimentalExecutionPlan(
        plan_id=new_id("EXPLAN"), diagnostic_test_id=diagnostic_test_id, protocol_reference_or_draft=plan.protocol_reference_or_draft,
        materials=plan.materials, controls=plan.controls, biological_replicates=plan.biological_replicates,
        technical_replicates=plan.technical_replicates, sampling_schedule=plan.sampling_schedule,
        qc_acceptance_criteria=plan.qc_acceptance_criteria, expected_output_schema=plan.expected_output_schema,
        interpretation_rule=plan.interpretation_rule, owner=plan.owner, readiness=readiness, created_at=now(),
    )
    session.add(p)
    session.flush()
    append_event(
        session, project_id=project_id, event_type=et.DIAGNOSIS_EXECUTION_PLAN_DRAFTED, entity_type="ExperimentalExecutionPlan",
        entity_id=p.plan_id, payload=snapshot(p, PLAN_FIELDS), actor_type="agent", actor_id=actor_id,
    )
    return p


def record_belief_update(
    session: Session,
    *,
    project_id: str,
    diagnosis_session_id: str,
    new_evidence_or_test_result_ref: dict[str, Any],
    update_rule: str,
    posterior_assessment_id: str,
    status_change: dict[str, Any],
    actor_id: str,
    prior_assessment_id: str | None = None,
    unresolved_conflicts: list[str] | None = None,
    rationale: str = "",
) -> BeliefUpdateEvent:
    ev = BeliefUpdateEvent(
        update_id=new_id("BELIEF"), diagnosis_session_id=diagnosis_session_id, prior_assessment_id=prior_assessment_id,
        new_evidence_or_test_result_ref=new_evidence_or_test_result_ref, update_rule=update_rule,
        posterior_assessment_id=posterior_assessment_id, status_change=status_change,
        unresolved_conflicts=unresolved_conflicts or [], actor_id=actor_id, rationale=rationale, created_at=now(),
    )
    session.add(ev)
    session.flush()
    append_event(
        session, project_id=project_id, event_type=et.DIAGNOSIS_BELIEF_UPDATED, entity_type="BeliefUpdateEvent",
        entity_id=ev.update_id,
        payload={"update_id": ev.update_id, "diagnosis_session_id": diagnosis_session_id, "status_change": status_change,
                 "unresolved_conflicts": ev.unresolved_conflicts, "posterior_assessment_id": posterior_assessment_id},
        actor_type="agent", actor_id=actor_id,
    )
    return ev


def record_bottleneck_value_assessment(
    session: Session,
    *,
    hypothesis_version_id: str,
    actor_id: str,
    objective_id: str | None = None,
    biological_importance: str = "unknown",
    engineering_leverage: str = "unknown",
    expected_gain_range: dict[str, Any] | None = None,
    intervention_complexity: str = "unknown",
    growth_stability_tradeoff: str = "unknown",
    reversibility: str = "unknown",
    robustness: str = "unknown",
    priority: str = "unranked",
    prerequisites: list[str] | None = None,
    rationale: str = "",
) -> BottleneckValueAssessment:
    """doc03 2.9: this is NOT diagnostic evidence - never written into
    `HypothesisAssessment`/`HypothesisVersion`, only referenced from
    `DiagnosisDecision.engineering_value_assessment` as a separate field."""
    v = BottleneckValueAssessment(
        value_assessment_id=new_id("BVALUE"), hypothesis_version_id=hypothesis_version_id, objective_id=objective_id,
        biological_importance=biological_importance, engineering_leverage=engineering_leverage,
        expected_gain_range=expected_gain_range, intervention_complexity=intervention_complexity,
        growth_stability_tradeoff=growth_stability_tradeoff, reversibility=reversibility, robustness=robustness,
        priority=priority, prerequisites=prerequisites or [], rationale=rationale, created_at=now(),
    )
    session.add(v)
    session.flush()
    return v


def create_diagnosis_decision(
    session: Session,
    *,
    diagnosis_session_id: str,
    diagnosis_version: int,
    actor_id: str,
    context_reference: dict[str, Any],
    leading_hypothesis_ids: list[str],
    supported_hypothesis_ids: list[str],
    alternatives_not_excluded_ids: list[str],
    contradictions: list[str],
    confidence_representation: dict[str, Any],
    uncertainty: str,
    evidence_references: list[str],
    stopping_reason: str,
    allowed_next_action: str,
    model_assessment_reference: str | None = None,
    selected_diagnostic_test_id: str | None = None,
    engineering_value_assessment: dict[str, Any] | None = None,
    handoff_status: str = "not_applicable",
    human_approval: dict[str, Any] | None = None,
) -> DiagnosisDecision:
    if stopping_reason not in STOPPING_REASONS:
        raise ValueError(f"stopping_reason must be one of {STOPPING_REASONS}, got {stopping_reason!r}")
    if allowed_next_action not in ALLOWED_NEXT_ACTIONS:
        raise ValueError(f"allowed_next_action must be one of {ALLOWED_NEXT_ACTIONS}, got {allowed_next_action!r}")

    sess = session.get(DiagnosisSession, diagnosis_session_id)
    if sess is None:
        raise ValueError(f"no such diagnosis session: {diagnosis_session_id}")

    d = DiagnosisDecision(
        decision_id=new_id("DDEC"), diagnosis_session_id=diagnosis_session_id, diagnosis_version=diagnosis_version,
        context_reference=context_reference, leading_hypothesis_ids=leading_hypothesis_ids,
        supported_hypothesis_ids=supported_hypothesis_ids, alternatives_not_excluded_ids=alternatives_not_excluded_ids,
        contradictions=contradictions, confidence_representation=confidence_representation, uncertainty=uncertainty,
        evidence_references=evidence_references, model_assessment_reference=model_assessment_reference,
        selected_diagnostic_test_id=selected_diagnostic_test_id, stopping_reason=stopping_reason,
        engineering_value_assessment=engineering_value_assessment, allowed_next_action=allowed_next_action,
        handoff_status=handoff_status, human_approval=human_approval, created_by=actor_id, created_at=now(),
    )
    session.add(d)
    session.flush()
    append_event(
        session, project_id=sess.project_id, event_type=et.DIAGNOSIS_STOPPING_DECIDED, entity_type="DiagnosisDecision",
        entity_id=d.decision_id, payload=snapshot(d, DECISION_FIELDS),
        actor_type="agent" if actor_id == "system" else "human", actor_id=actor_id,
    )
    return d


def set_handoff_status(
    session: Session, *, decision_id: str, handoff_status: str, actor_id: str, human_approval: dict[str, Any] | None = None
) -> DiagnosisDecision:
    d = session.get(DiagnosisDecision, decision_id)
    if d is None:
        raise ValueError(f"no such diagnosis decision: {decision_id}")
    sess = session.get(DiagnosisSession, d.diagnosis_session_id)
    d.handoff_status = handoff_status
    if human_approval is not None:
        d.human_approval = human_approval
    session.flush()
    event_type = et.DIAGNOSIS_HANDED_OFF if handoff_status == "handed_off" else et.DIAGNOSIS_HUMAN_DECISION_RECORDED
    append_event(
        session, project_id=sess.project_id, event_type=event_type, entity_type="DiagnosisDecision",
        entity_id=d.decision_id, payload=snapshot(d, DECISION_FIELDS), actor_type="human", actor_id=actor_id,
    )
    return d
