"""Evaluation Loop Controller (doc05 §6): the sole writer of
`EvaluationCase.status`, mirroring `harness.engineering_design.loop.
EngineeringDesignLoopController` / `harness.diagnosis.loop.
DiagnosisLoopController`'s controller discipline - every transition is
validated against its legal from-states and recorded as an immutable
`EvaluationTransition` row plus a `ProjectEvent` in the SAME ledger.

Only the two consequential junctions are actually gate-enforced (raise on
fail): `revision_required` vs proceeding to `awaiting_human_decision`
(`scientific_revision_gate`), and `awaiting_human_decision` -> `approved_
for_planning`/`approved_for_build` (`scientific_human_gate_precondition`,
enforced in `harness/scientific_evaluation/human_gate.py` before this
controller is even called). The seven intermediate pipeline stages
(`deterministic_validation` -> ... -> `meta_review`) are sequential
progress markers - doc05 §6's guard list names specific hard stops, not
"every micro-transition needs its own veto"; gathering the full evidence/
model/critique picture before any stage can block is a deliberate,
documented design choice (see the final report's Architecture section).
"""
from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from harness.ids import new_id, now
from harness.memory import event_types as et
from harness.memory.event_store import append_event, snapshot
from harness.scientific_evaluation.models import EvaluationCase, EvaluationTransition
from harness.workflow.contracts import GateResult

CASE_SNAPSHOT_FIELDS = (
    "evaluation_id", "schema_version", "project_id", "design_project_id", "workflow_run_id", "diagnosis_reference",
    "portfolio_reference", "design_version_references", "frozen_context", "evaluation_mode", "status",
    "revision_round", "created_by", "created_at", "updated_at", "version",
)


class IllegalEvaluationTransitionError(RuntimeError):
    pass


class EvaluationGateRejectedError(RuntimeError):
    pass


def _gate_result_to_dict(gate_result: GateResult | None) -> dict[str, Any] | None:
    if gate_result is None:
        return None
    return {
        "gate_name": gate_result.gate_name, "status": gate_result.status.value,
        "violations": [v.model_dump() for v in gate_result.violations],
        "required_actions": gate_result.required_actions, "next_stage": gate_result.next_stage,
    }


class EvaluationLoopController:
    def _transition(
        self, session: Session, case: EvaluationCase, *, from_states: tuple[str, ...], to_state: str, actor_id: str,
        gate_result: GateResult | None = None, enforce: bool = True,
    ) -> EvaluationCase:
        if case.status not in from_states:
            raise IllegalEvaluationTransitionError(
                f"cannot move evaluation case {case.evaluation_id} from {case.status!r} to {to_state!r}: only legal from {from_states}"
            )
        if enforce and gate_result is not None and gate_result.status.value == "fail":
            raise EvaluationGateRejectedError(
                f"transition to {to_state!r} rejected by {gate_result.gate_name}: {[v.message for v in gate_result.violations]}"
            )

        started = now()
        from_state = case.status
        case.status = to_state
        case.updated_at = now()
        session.flush()

        transition = EvaluationTransition(
            transition_id=new_id("ETRANS"), evaluation_id=case.evaluation_id, state=from_state, status="completed",
            gate_result=_gate_result_to_dict(gate_result), selected_next_state=to_state,
            selection_reason=f"transition to {to_state} triggered by actor {actor_id}", actor_id=actor_id,
            started_at=started, ended_at=now(),
        )
        session.add(transition)
        session.flush()

        append_event(
            session, project_id=case.project_id, event_type=et.EVAL_STATE_CHANGED, entity_type="EvaluationCase",
            entity_id=case.evaluation_id, payload=snapshot(case, CASE_SNAPSHOT_FIELDS),
            actor_type="agent" if actor_id == "system" else "human", actor_id=actor_id,
        )
        return case

    def start_deterministic_validation(self, session: Session, case: EvaluationCase, *, actor_id: str) -> EvaluationCase:
        return self._transition(session, case, from_states=("evaluation_pending",), to_state="deterministic_validation", actor_id=actor_id)

    def start_evidence_review(self, session: Session, case: EvaluationCase, *, actor_id: str) -> EvaluationCase:
        return self._transition(session, case, from_states=("deterministic_validation",), to_state="evidence_review", actor_id=actor_id)

    def start_model_review(self, session: Session, case: EvaluationCase, *, actor_id: str) -> EvaluationCase:
        return self._transition(session, case, from_states=("evidence_review",), to_state="model_review", actor_id=actor_id)

    def start_scientific_review(self, session: Session, case: EvaluationCase, *, actor_id: str) -> EvaluationCase:
        return self._transition(session, case, from_states=("model_review",), to_state="scientific_review", actor_id=actor_id)

    def start_candidate_comparison(self, session: Session, case: EvaluationCase, *, actor_id: str) -> EvaluationCase:
        return self._transition(session, case, from_states=("scientific_review",), to_state="candidate_comparison", actor_id=actor_id)

    def start_meta_review(self, session: Session, case: EvaluationCase, *, actor_id: str) -> EvaluationCase:
        return self._transition(session, case, from_states=("candidate_comparison",), to_state="meta_review", actor_id=actor_id)

    def complete_meta_review(
        self, session: Session, case: EvaluationCase, *, actor_id: str, revision_gate_result: GateResult,
    ) -> EvaluationCase:
        to_state = "revision_required" if revision_gate_result.status.value in ("revise", "fail") else "awaiting_human_decision"
        return self._transition(
            session, case, from_states=("meta_review",), to_state=to_state, actor_id=actor_id,
            gate_result=revision_gate_result, enforce=False,
        )
        # note: `enforce=False` - reaching the revision_limit yields
        # `human_review` status (see `scientific_revision_gate`), which must
        # still be allowed to land on `awaiting_human_decision` (doc05 §4.9:
        # "达到最大轮数不能自动批准,应进入 hold 或 human_review_required"),
        # never silently blocked from reaching a human at all.

    def restart_after_revision(self, session: Session, case: EvaluationCase, *, actor_id: str) -> EvaluationCase:
        """A new `CandidateDesign` version exists (`revision.apply_revision`)
        - doc05 §6: "revision 后必须以新版本重新评审", so the case restarts
        the pipeline from `evaluation_pending` rather than resuming
        mid-stream on stale claim/evidence/review rows."""
        return self._transition(session, case, from_states=("revision_required",), to_state="evaluation_pending", actor_id=actor_id)

    def record_human_gate_outcome(self, session: Session, case: EvaluationCase, *, actor_id: str, target_state: str) -> EvaluationCase:
        """A human may act from `awaiting_human_decision` (the normal path,
        once the pipeline has a recommendation) OR from `revision_required`
        (doc05 §2.7: a human can always override/intervene - hold, stop,
        reject, or force a return to diagnosis - rather than being forced to
        wait for another automated revision round)."""
        return self._transition(
            session, case, from_states=("awaiting_human_decision", "revision_required"), to_state=target_state, actor_id=actor_id,
        )
