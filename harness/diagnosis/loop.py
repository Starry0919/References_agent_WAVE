"""The Bottleneck Diagnosis Loop (doc03 §5): an 18-state workflow, same
controller discipline as Problem 01's `WorkflowController` and Problem 02's
`IterativeLoopController` - `DiagnosisLoopController` is the sole writer of
`DiagnosisSession.status`, every transition is validated against its legal
from-states, gated where doc03 §5 requires, and recorded as an immutable
`DiagnosisTransition` row plus a `ProjectEvent` in the SAME ledger Problems
01/02 use (doc03 6.3 - no second, disconnected history store).

`awaiting_test_result` is this loop's durable wait state, directly
analogous to Problem 02's `WAITING_FOR_RESULTS` - a real experiment/test
can take days, and the session must resume from the database alone, not
in-memory state.
"""
from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from harness.diagnosis.models import DiagnosisSession, DiagnosisTransition
from harness.ids import new_id, now
from harness.memory import event_types as et
from harness.memory.event_store import append_event, snapshot
from harness.workflow.contracts import GateResult

SESSION_SNAPSHOT_FIELDS = (
    "diagnosis_session_id", "project_id", "workflow_run_id", "triggering_failure_case_id",
    "triggering_learning_cycle_id", "objective_id", "biological_system", "baseline_observation_ids",
    "active_hypothesis_set_version", "status", "data_sufficiency", "approval_state", "version",
    "created_at", "updated_at",
)


class IllegalDiagnosisTransitionError(RuntimeError):
    pass


class DiagnosisGateRejectedError(RuntimeError):
    pass


def _gate_result_to_dict(gate_result: GateResult | None) -> dict[str, Any] | None:
    if gate_result is None:
        return None
    return {
        "gate_name": gate_result.gate_name, "status": gate_result.status.value,
        "violations": [v.model_dump() for v in gate_result.violations],
        "required_actions": gate_result.required_actions, "next_stage": gate_result.next_stage,
    }


class DiagnosisLoopController:
    def get_session(self, session: Session, diagnosis_session_id: str) -> DiagnosisSession | None:
        return session.get(DiagnosisSession, diagnosis_session_id)

    def _transition(
        self,
        session: Session,
        sess: DiagnosisSession,
        *,
        from_states: tuple[str, ...],
        to_state: str,
        actor_id: str,
        gate_result: GateResult | None = None,
        pointer_updates: dict[str, Any] | None = None,
    ) -> DiagnosisSession:
        if sess.status not in from_states:
            raise IllegalDiagnosisTransitionError(
                f"cannot move diagnosis {sess.diagnosis_session_id} from {sess.status!r} to {to_state!r}: "
                f"only legal from {from_states}"
            )
        if gate_result is not None and gate_result.status.value == "fail":
            raise DiagnosisGateRejectedError(
                f"transition to {to_state!r} rejected by {gate_result.gate_name}: "
                f"{[v.message for v in gate_result.violations]}"
            )

        started = now()
        from_state = sess.status
        sess.status = to_state
        if pointer_updates:
            for key, value in pointer_updates.items():
                setattr(sess, key, value)
        sess.updated_at = now()
        session.flush()

        transition = DiagnosisTransition(
            transition_id=new_id("DTRANS"), diagnosis_session_id=sess.diagnosis_session_id, state=from_state,
            status="completed", output={}, gate_result=_gate_result_to_dict(gate_result), selected_next_state=to_state,
            selection_reason=f"transition to {to_state} triggered by actor {actor_id}", started_at=started, ended_at=now(),
        )
        session.add(transition)
        session.flush()

        append_event(
            session, project_id=sess.project_id, event_type=et.DIAGNOSIS_STATE_CHANGED, entity_type="DiagnosisSession",
            entity_id=sess.diagnosis_session_id, payload=snapshot(sess, SESSION_SNAPSHOT_FIELDS),
            actor_type="agent" if actor_id == "system" else "human", actor_id=actor_id,
        )
        return sess

    # -- intake ---------------------------------------------------------

    def run_intake(
        self, session: Session, sess: DiagnosisSession, *, actor_id: str, sufficiency_gate_result: GateResult
    ) -> DiagnosisSession:
        sufficiency = sufficiency_gate_result.next_stage or "insufficient"
        to_state = "data_required" if sufficiency == "insufficient" else "observations_normalized"
        return self._transition(
            session, sess, from_states=("intake", "data_required"), to_state=to_state, actor_id=actor_id,
            pointer_updates={"data_sufficiency": sufficiency},
        )

    # -- hypothesis generation / evidence / ranking ----------------------

    def mark_hypotheses_generated(self, session: Session, sess: DiagnosisSession, *, actor_id: str) -> DiagnosisSession:
        return self._transition(session, sess, from_states=("observations_normalized",), to_state="hypotheses_generated", actor_id=actor_id)

    def mark_evidence_assessed(self, session: Session, sess: DiagnosisSession, *, actor_id: str) -> DiagnosisSession:
        return self._transition(session, sess, from_states=("hypotheses_generated",), to_state="evidence_assessed", actor_id=actor_id)

    def mark_model_evidence_pending(self, session: Session, sess: DiagnosisSession, *, actor_id: str) -> DiagnosisSession:
        return self._transition(session, sess, from_states=("evidence_assessed",), to_state="model_evidence_pending", actor_id=actor_id)

    def mark_hypotheses_ranked(self, session: Session, sess: DiagnosisSession, *, actor_id: str) -> DiagnosisSession:
        return self._transition(
            session, sess, from_states=("evidence_assessed", "model_evidence_pending", "model_conflicted"),
            to_state="hypotheses_ranked", actor_id=actor_id,
        )

    def enter_model_conflicted(self, session: Session, sess: DiagnosisSession, *, actor_id: str) -> DiagnosisSession:
        return self._transition(
            session, sess, from_states=("model_evidence_pending", "hypotheses_ranked"), to_state="model_conflicted", actor_id=actor_id,
        )

    # -- test selection / execution / waiting ----------------------------

    def enter_test_selection_required(self, session: Session, sess: DiagnosisSession, *, actor_id: str) -> DiagnosisSession:
        return self._transition(session, sess, from_states=("hypotheses_ranked",), to_state="test_selection_required", actor_id=actor_id)

    def select_test(self, session: Session, sess: DiagnosisSession, *, actor_id: str) -> DiagnosisSession:
        return self._transition(session, sess, from_states=("test_selection_required",), to_state="test_planned", actor_id=actor_id)

    def enter_awaiting_test_result(self, session: Session, sess: DiagnosisSession, *, actor_id: str) -> DiagnosisSession:
        """The durable wait state - a real experiment can take days; this
        session row must be reloadable from a fresh process (verified in
        `tests/diagnosis/test_loop.py`, mirroring Problem 02's
        `WAITING_FOR_RESULTS` kill/resume proof)."""
        return self._transition(session, sess, from_states=("test_planned",), to_state="awaiting_test_result", actor_id=actor_id)

    def ingest_test_result_and_update_belief(self, session: Session, sess: DiagnosisSession, *, actor_id: str) -> DiagnosisSession:
        return self._transition(session, sess, from_states=("awaiting_test_result",), to_state="belief_updated", actor_id=actor_id)

    # -- stopping / human review ------------------------------------------

    def run_stopping_gate(
        self, session: Session, sess: DiagnosisSession, *, actor_id: str, stopping_gate_result: GateResult
    ) -> DiagnosisSession:
        reason = stopping_gate_result.next_stage or "continue_diagnosis"
        target = {
            "actionable_stop": "actionable", "evidence_limited_stop": "evidence_limited",
            "safety_stop": "human_review_required", "human_escalation": "human_review_required",
            "continue_diagnosis": "hypotheses_ranked",
        }[reason]
        return self._transition(
            session, sess, from_states=("belief_updated", "hypotheses_ranked"), to_state=target, actor_id=actor_id,
            gate_result=stopping_gate_result if stopping_gate_result.status.value != "fail" else None,
        )

    def resolve_human_review(
        self, session: Session, sess: DiagnosisSession, *, actor_id: str, resolution: str
    ) -> DiagnosisSession:
        if resolution not in ("hypotheses_ranked", "evidence_limited", "closed"):
            raise ValueError(f"resolution must be one of hypotheses_ranked/evidence_limited/closed, got {resolution!r}")
        return self._transition(session, sess, from_states=("human_review_required",), to_state=resolution, actor_id=actor_id)

    # -- handoff -----------------------------------------------------------

    def enter_handoff_ready(
        self, session: Session, sess: DiagnosisSession, *, actor_id: str, engineering_value_gate_result: GateResult
    ) -> DiagnosisSession:
        from harness.diagnosis.grounding import evaluate_observation_grounding
        grounding = evaluate_observation_grounding(session, sess.diagnosis_session_id)
        if not grounding.actionable:
            sess.status = "data_required"
            sess.data_sufficiency = "insufficient"
            session.flush()
            raise DiagnosisGateRejectedError(f"data_required: {grounding.blocking_reasons}")
        return self._transition(
            session, sess, from_states=("actionable",), to_state="handoff_ready", actor_id=actor_id,
            gate_result=engineering_value_gate_result,
        )

    def hand_off_to_design(
        self, session: Session, sess: DiagnosisSession, *, actor_id: str, handoff_gate_result: GateResult
    ) -> DiagnosisSession:
        from harness.diagnosis.grounding import evaluate_observation_grounding
        grounding = evaluate_observation_grounding(session, sess.diagnosis_session_id)
        if not grounding.actionable:
            raise DiagnosisGateRejectedError(f"data_required: {grounding.blocking_reasons}")
        return self._transition(
            session, sess, from_states=("handoff_ready",), to_state="handed_off_to_design", actor_id=actor_id,
            gate_result=handoff_gate_result,
        )

    # -- reopen / close ------------------------------------------------------

    def reopen_diagnosis(self, session: Session, sess: DiagnosisSession, *, actor_id: str, reason: str) -> DiagnosisSession:
        sess.active_hypothesis_set_version += 1
        return self._transition(
            session, sess, from_states=("evidence_limited", "closed", "handed_off_to_design"),
            to_state="hypotheses_ranked", actor_id=actor_id,
        )

    def close_diagnosis(self, session: Session, sess: DiagnosisSession, *, actor_id: str, reason: str) -> DiagnosisSession:
        return self._transition(
            session, sess, from_states=("evidence_limited", "actionable", "handed_off_to_design", "human_review_required"),
            to_state="closed", actor_id=actor_id,
        )
