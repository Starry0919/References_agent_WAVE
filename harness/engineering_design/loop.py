"""The Engineering Design Decision Loop (doc04 §4.1): same controller
discipline as `harness.diagnosis.loop.DiagnosisLoopController` -
`EngineeringDesignLoopController` is the sole writer of
`EngineeringDesignProject.status`, every transition is validated against
its legal from-states, gated where doc04 requires, and recorded as an
immutable `DesignWorkflowTransition` row plus a `ProjectEvent` in the SAME
ledger Problems 01-03 use.
"""
from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from harness.engineering_design.models import EngineeringDesignProject, DesignWorkflowTransition
from harness.ids import new_id, now
from harness.memory import event_types as et
from harness.memory.event_store import append_event, snapshot
from harness.workflow.contracts import GateResult

PROJECT_SNAPSHOT_FIELDS = (
    "design_project_id", "project_id", "schema_version", "chassis", "chassis_version_or_genotype",
    "baseline_state_id", "diagnosis_session_id", "diagnosis_decision_id", "diagnosis_version",
    "temporal_and_environmental_context", "primary_metrics", "secondary_metrics", "hard_constraints",
    "preferences_or_weights", "available_resources", "autonomy_level", "required_human_gates",
    "status", "revision_count", "created_by", "created_at", "updated_at", "version",
)


class IllegalDesignTransitionError(RuntimeError):
    pass


class DesignGateRejectedError(RuntimeError):
    pass


def _gate_result_to_dict(gate_result: GateResult | None) -> dict[str, Any] | None:
    if gate_result is None:
        return None
    return {
        "gate_name": gate_result.gate_name, "status": gate_result.status.value,
        "violations": [v.model_dump() for v in gate_result.violations],
        "required_actions": gate_result.required_actions, "next_stage": gate_result.next_stage,
    }


class EngineeringDesignLoopController:
    def get_project(self, session: Session, design_project_id: str) -> EngineeringDesignProject | None:
        return session.get(EngineeringDesignProject, design_project_id)

    def _transition(
        self,
        session: Session,
        proj: EngineeringDesignProject,
        *,
        from_states: tuple[str, ...],
        to_state: str,
        actor_id: str,
        gate_result: GateResult | None = None,
        pointer_updates: dict[str, Any] | None = None,
    ) -> EngineeringDesignProject:
        if proj.status not in from_states:
            raise IllegalDesignTransitionError(
                f"cannot move design project {proj.design_project_id} from {proj.status!r} to {to_state!r}: "
                f"only legal from {from_states}"
            )
        if gate_result is not None and gate_result.status.value == "fail":
            raise DesignGateRejectedError(
                f"transition to {to_state!r} rejected by {gate_result.gate_name}: "
                f"{[v.message for v in gate_result.violations]}"
            )

        started = now()
        from_state = proj.status
        proj.status = to_state
        if pointer_updates:
            for key, value in pointer_updates.items():
                setattr(proj, key, value)
        proj.updated_at = now()
        session.flush()

        transition = DesignWorkflowTransition(
            transition_id=new_id("DWTRANS"), design_project_id=proj.design_project_id, state=from_state,
            status="completed", gate_result=_gate_result_to_dict(gate_result), selected_next_state=to_state,
            selection_reason=f"transition to {to_state} triggered by actor {actor_id}", actor_id=actor_id,
            started_at=started, ended_at=now(),
        )
        session.add(transition)
        session.flush()

        append_event(
            session, project_id=proj.project_id, event_type=et.DESIGN_WORKFLOW_STATE_CHANGED,
            entity_type="EngineeringDesignProject", entity_id=proj.design_project_id,
            payload=snapshot(proj, PROJECT_SNAPSHOT_FIELDS),
            actor_type="agent" if actor_id == "system" else "human", actor_id=actor_id,
        )
        return proj

    # -- handoff / objective ---------------------------------------------

    def ingest_handoff(
        self, session: Session, proj: EngineeringDesignProject, *, actor_id: str, handoff_gate_result: GateResult
    ) -> EngineeringDesignProject:
        return self._transition(
            session, proj, from_states=("diagnostic_blocked",), to_state="objective_draft",
            actor_id=actor_id, gate_result=handoff_gate_result,
        )

    def confirm_objective(
        self, session: Session, proj: EngineeringDesignProject, *, actor_id: str, objective_gate_result: GateResult
    ) -> EngineeringDesignProject:
        return self._transition(
            session, proj, from_states=("objective_draft",), to_state="strategy_generated",
            actor_id=actor_id, gate_result=objective_gate_result,
        )

    # -- strategy / portfolio ---------------------------------------------

    def generate_portfolio(self, session: Session, proj: EngineeringDesignProject, *, actor_id: str) -> EngineeringDesignProject:
        return self._transition(
            session, proj, from_states=("strategy_generated", "revision_required"), to_state="portfolio_generated", actor_id=actor_id,
        )

    def start_evaluation(self, session: Session, proj: EngineeringDesignProject, *, actor_id: str) -> EngineeringDesignProject:
        return self._transition(session, proj, from_states=("portfolio_generated",), to_state="evaluation_in_progress", actor_id=actor_id)

    def complete_evaluation(
        self, session: Session, proj: EngineeringDesignProject, *, actor_id: str, revision_gate_result: GateResult
    ) -> EngineeringDesignProject:
        needs_revision = revision_gate_result.status.value in ("revise", "human_review")
        to_state = "revision_required" if needs_revision else "portfolio_evaluated"
        pointer_updates = {"revision_count": proj.revision_count + 1} if needs_revision else None
        return self._transition(
            session, proj, from_states=("evaluation_in_progress",), to_state=to_state, actor_id=actor_id,
            gate_result=revision_gate_result, pointer_updates=pointer_updates,
        )

    # -- planning / approval -----------------------------------------------

    def complete_planning(self, session: Session, proj: EngineeringDesignProject, *, actor_id: str) -> EngineeringDesignProject:
        return self._transition(session, proj, from_states=("planning_ready",), to_state="approved_for_build", actor_id=actor_id)

    def request_human_approval(self, session: Session, proj: EngineeringDesignProject, *, actor_id: str) -> EngineeringDesignProject:
        return self._transition(session, proj, from_states=("portfolio_evaluated",), to_state="awaiting_human_approval", actor_id=actor_id)

    def record_human_decision(
        self, session: Session, proj: EngineeringDesignProject, *, actor_id: str, approved: bool
    ) -> EngineeringDesignProject:
        # Approval here means human candidate selection. Build approval is
        # only reached after the selected candidate's ValidationPlan passes.
        to_state = "planning_ready" if approved else "rejected"
        return self._transition(session, proj, from_states=("awaiting_human_approval",), to_state=to_state, actor_id=actor_id)

    # -- build / test --------------------------------------------------------

    def start_build(self, session: Session, proj: EngineeringDesignProject, *, actor_id: str) -> EngineeringDesignProject:
        return self._transition(session, proj, from_states=("approved_for_build",), to_state="build_in_progress", actor_id=actor_id)

    def mark_test_pending(self, session: Session, proj: EngineeringDesignProject, *, actor_id: str) -> EngineeringDesignProject:
        return self._transition(session, proj, from_states=("build_in_progress",), to_state="test_pending", actor_id=actor_id)

    def ingest_test_outcome(self, session: Session, proj: EngineeringDesignProject, *, actor_id: str) -> EngineeringDesignProject:
        return self._transition(session, proj, from_states=("test_pending",), to_state="tested", actor_id=actor_id)

    def complete_learning_update(self, session: Session, proj: EngineeringDesignProject, *, actor_id: str) -> EngineeringDesignProject:
        return self._transition(session, proj, from_states=("tested",), to_state="learning_update", actor_id=actor_id)

    # -- next iteration / reopen / stop --------------------------------------

    def start_next_iteration(self, session: Session, proj: EngineeringDesignProject, *, actor_id: str) -> EngineeringDesignProject:
        return self._transition(
            session, proj, from_states=("learning_update", "rejected"), to_state="next_iteration", actor_id=actor_id,
        )

    def reopen_diagnosis(self, session: Session, proj: EngineeringDesignProject, *, actor_id: str) -> EngineeringDesignProject:
        return self._transition(
            session, proj, from_states=("learning_update", "rejected"), to_state="diagnosis_reopened", actor_id=actor_id,
        )

    def complete(self, session: Session, proj: EngineeringDesignProject, *, actor_id: str) -> EngineeringDesignProject:
        return self._transition(
            session, proj, from_states=("learning_update", "next_iteration"), to_state="completed", actor_id=actor_id,
        )

    def restart_from_next_iteration(self, session: Session, proj: EngineeringDesignProject, *, actor_id: str) -> EngineeringDesignProject:
        """`next_iteration` re-enters strategy generation carrying forward
        history (failures, residuals, rejected candidates) - never a fresh,
        amnesiac restart."""
        return self._transition(session, proj, from_states=("next_iteration",), to_state="strategy_generated", actor_id=actor_id)
