"""The Iterative Design Loop (doc section 10): a durable, SQL-backed state
machine spanning one project's whole DBTL history - fundamentally
different in lifetime from Problem 01's `WorkflowRun` (one request/
response cycle) because `WAITING_FOR_RESULTS` must survive the process
ending entirely while a real experiment runs for days.

Follows the same controller discipline as Problem 01
(`harness.workflow.controller.WorkflowController`): `IterativeLoopController`
is the SOLE writer of `IterativeCycleState.current_state`; every transition
is validated against the state it must currently be in, checked against a
gate when one applies, and recorded as an immutable
`IterativeCycleTransition` row plus a `CYCLE_STATE_CHANGED` ProjectEvent.
Unlike Problem 01's pipeline (a pure computation that can run start-to-
finish in one call), most states here correspond to real-world events
(a human approves a design; a wet lab reports results days later), so this
controller exposes one explicit method per named transition rather than an
eagerly-evaluated `advance()` loop - the safety properties (single writer,
gated transitions, durable audit trail) are the same; the shape that fits
an event-driven, multi-day process is different, deliberately.
"""
from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from harness.ids import new_id, now
from harness.memory import event_types as et
from harness.memory.event_store import append_event, snapshot
from harness.projects.models import IterativeCycleState, IterativeCycleTransition
from harness.projects.service import CYCLE_SNAPSHOT_FIELDS
from harness.workflow.contracts import GateResult

DBTL_STATES = (
    "PROJECT_CONTEXT_READY",
    "DESIGN_BASELINE_CAPTURED",
    "DESIGN_PROPOSED",
    "HUMAN_DESIGN_GATE",
    "BUILD_TEST_HANDOFF",
    "WAITING_FOR_RESULTS",
    "DATA_INGESTION",
    "DATA_QC",
    "OBSERVATION_EXTRACTION",
    "RESULT_INTERPRETATION",
    "HYPOTHESIS_UPDATE",
    "FAILURE_OR_SUCCESS_CLASSIFICATION",
    "LEARNING_UPDATE_GATE",
    "REDESIGN_OR_STOP_DECISION",
    "PROJECT_PAUSED",
    "PROJECT_COMPLETED",
)

_TERMINAL_STATUS_BY_STATE = {
    "PROJECT_PAUSED": "paused",
    "PROJECT_COMPLETED": "completed",
}


class IllegalCycleTransitionError(RuntimeError):
    """The cycle is not currently in a state this transition is legal
    from - the equivalent of Problem 01's `IllegalTransitionError`."""


class GateRejectedError(RuntimeError):
    """A gate attached to this transition returned `fail` - the
    transition never happened."""


def _gate_result_to_dict(gate_result: GateResult | None) -> dict[str, Any] | None:
    if gate_result is None:
        return None
    return {
        "gate_name": gate_result.gate_name,
        "status": gate_result.status.value,
        "violations": [v.model_dump() for v in gate_result.violations],
        "required_actions": gate_result.required_actions,
    }


class IterativeLoopController:
    """Stateless (all state lives in the DB) - every method takes an open
    `Session` and the `IterativeCycleState` row to transition."""

    def get_cycle(self, session: Session, cycle_state_id: str) -> IterativeCycleState | None:
        return session.get(IterativeCycleState, cycle_state_id)

    def _transition(
        self,
        session: Session,
        cycle: IterativeCycleState,
        *,
        from_states: tuple[str, ...],
        to_state: str,
        actor_id: str,
        gate_result: GateResult | None = None,
        pending_gate: dict[str, Any] | None = None,
        pointer_updates: dict[str, Any] | None = None,
    ) -> IterativeCycleState:
        if cycle.current_state not in from_states:
            raise IllegalCycleTransitionError(
                f"cannot move cycle {cycle.cycle_state_id} from {cycle.current_state!r} to {to_state!r}: "
                f"only legal from {from_states}"
            )
        if gate_result is not None and gate_result.status.value == "fail":
            raise GateRejectedError(
                f"transition to {to_state!r} rejected by {gate_result.gate_name}: "
                f"{[v.message for v in gate_result.violations]}"
            )

        started = now()
        from_state = cycle.current_state

        cycle.current_state = to_state
        if pointer_updates:
            for key, value in pointer_updates.items():
                setattr(cycle, key, value)

        if to_state in _TERMINAL_STATUS_BY_STATE:
            cycle.status = _TERMINAL_STATUS_BY_STATE[to_state]
            cycle.pending_gate = None
        elif to_state == "WAITING_FOR_RESULTS":
            cycle.status = "running"  # durable but not blocked on a human answer - see resume_after_wait()
            cycle.pending_gate = None
        elif gate_result is not None and gate_result.status.value == "human_review":
            cycle.status = "waiting_user"
            cycle.pending_gate = pending_gate or {
                "kind": "approval",
                "state": to_state,
                "question": "; ".join(gate_result.required_actions) or f"{to_state} requires human review",
            }
        elif pending_gate is not None:
            cycle.status = "waiting_user"
            cycle.pending_gate = pending_gate
        else:
            cycle.status = "running"
            cycle.pending_gate = None

        cycle.updated_at = now()
        session.flush()

        transition = IterativeCycleTransition(
            transition_id=new_id("TRANS"),
            cycle_state_id=cycle.cycle_state_id,
            state=from_state,
            attempt=1,
            status="completed",
            output={},
            gate_result=_gate_result_to_dict(gate_result),
            selected_next_state=to_state,
            selection_reason=f"transition to {to_state} triggered by actor {actor_id}",
            started_at=started,
            ended_at=now(),
        )
        session.add(transition)
        session.flush()

        append_event(
            session,
            project_id=cycle.project_id,
            event_type=et.CYCLE_STATE_CHANGED,
            entity_type="IterativeCycleState",
            entity_id=cycle.cycle_state_id,
            payload=snapshot(cycle, CYCLE_SNAPSHOT_FIELDS),
            actor_type="agent" if actor_id == "system" else "human",
            actor_id=actor_id,
        )
        return cycle

    # -- named transitions, in DBTL order -----------------------------------

    def capture_baseline(self, session: Session, cycle: IterativeCycleState, *, actor_id: str) -> IterativeCycleState:
        return self._transition(
            session, cycle, from_states=("PROJECT_CONTEXT_READY",), to_state="DESIGN_BASELINE_CAPTURED", actor_id=actor_id
        )

    def propose_design(
        self, session: Session, cycle: IterativeCycleState, *, design_version_id: str, actor_id: str
    ) -> IterativeCycleState:
        return self._transition(
            session, cycle,
            from_states=("DESIGN_BASELINE_CAPTURED", "REDESIGN_OR_STOP_DECISION"),
            to_state="DESIGN_PROPOSED", actor_id=actor_id,
            pointer_updates={"active_design_version_id": design_version_id},
        )

    def enter_human_design_gate(self, session: Session, cycle: IterativeCycleState, *, actor_id: str) -> IterativeCycleState:
        return self._transition(
            session, cycle, from_states=("DESIGN_PROPOSED",), to_state="HUMAN_DESIGN_GATE", actor_id=actor_id,
            pending_gate={"kind": "approval", "state": "HUMAN_DESIGN_GATE", "question": "approve this design for build/test?"},
        )

    def approve_design_and_handoff(self, session: Session, cycle: IterativeCycleState, *, actor_id: str) -> IterativeCycleState:
        """Caller must have already recorded the real approval via
        `harness.designs.service.approve_design_version` (which enforces
        proposer-cannot-self-approve) before calling this - this method
        only advances the CYCLE's state, it is not itself the approval."""
        return self._transition(session, cycle, from_states=("HUMAN_DESIGN_GATE",), to_state="BUILD_TEST_HANDOFF", actor_id=actor_id)

    def enter_waiting_for_results(
        self, session: Session, cycle: IterativeCycleState, *, experiment_plan_id: str, actor_id: str
    ) -> IterativeCycleState:
        return self._transition(
            session, cycle, from_states=("BUILD_TEST_HANDOFF",), to_state="WAITING_FOR_RESULTS", actor_id=actor_id,
            pointer_updates={"active_experiment_plan_id": experiment_plan_id},
        )

    def begin_data_ingestion(
        self, session: Session, cycle: IterativeCycleState, *, experiment_run_id: str, actor_id: str
    ) -> IterativeCycleState:
        """This is the resume point after `WAITING_FOR_RESULTS` - legal to
        call in a fresh process, days after the process that created the
        experiment plan exited, as long as the cycle row is reloaded from
        the database first."""
        return self._transition(
            session, cycle, from_states=("WAITING_FOR_RESULTS",), to_state="DATA_INGESTION", actor_id=actor_id,
            pointer_updates={"active_experiment_run_id": experiment_run_id},
        )

    def run_data_qc(
        self, session: Session, cycle: IterativeCycleState, *, qc_gate_result: GateResult, actor_id: str
    ) -> IterativeCycleState:
        return self._transition(
            session, cycle, from_states=("DATA_INGESTION",), to_state="DATA_QC", actor_id=actor_id, gate_result=qc_gate_result
        )

    def extract_observations(self, session: Session, cycle: IterativeCycleState, *, actor_id: str) -> IterativeCycleState:
        return self._transition(session, cycle, from_states=("DATA_QC",), to_state="OBSERVATION_EXTRACTION", actor_id=actor_id)

    def interpret_results(self, session: Session, cycle: IterativeCycleState, *, actor_id: str) -> IterativeCycleState:
        return self._transition(
            session, cycle, from_states=("OBSERVATION_EXTRACTION",), to_state="RESULT_INTERPRETATION", actor_id=actor_id
        )

    def update_hypothesis(self, session: Session, cycle: IterativeCycleState, *, actor_id: str) -> IterativeCycleState:
        return self._transition(
            session, cycle, from_states=("RESULT_INTERPRETATION",), to_state="HYPOTHESIS_UPDATE", actor_id=actor_id
        )

    def classify_outcome(self, session: Session, cycle: IterativeCycleState, *, actor_id: str) -> IterativeCycleState:
        return self._transition(
            session, cycle, from_states=("HYPOTHESIS_UPDATE",), to_state="FAILURE_OR_SUCCESS_CLASSIFICATION", actor_id=actor_id
        )

    def enter_learning_update_gate(
        self, session: Session, cycle: IterativeCycleState, *, policy_gate_result: GateResult, actor_id: str
    ) -> IterativeCycleState:
        return self._transition(
            session, cycle, from_states=("FAILURE_OR_SUCCESS_CLASSIFICATION",), to_state="LEARNING_UPDATE_GATE",
            actor_id=actor_id, gate_result=policy_gate_result,
        )

    def decide_redesign_or_stop(
        self, session: Session, cycle: IterativeCycleState, *, actor_id: str, active_learning_cycle_id: str | None = None
    ) -> IterativeCycleState:
        return self._transition(
            session, cycle, from_states=("LEARNING_UPDATE_GATE",), to_state="REDESIGN_OR_STOP_DECISION", actor_id=actor_id,
            pointer_updates={"active_learning_cycle_id": active_learning_cycle_id} if active_learning_cycle_id else None,
        )

    def create_new_design_version(
        self,
        session: Session,
        cycle: IterativeCycleState,
        *,
        design_version_id: str,
        actor_id: str,
        redesign_gate_result: GateResult,
    ) -> IterativeCycleState:
        """doc's "NEW_DESIGN_VERSION" outcome of REDESIGN_OR_STOP_DECISION:
        implemented as a direct transition back to DESIGN_PROPOSED (the
        next real state a fresh design version enters) rather than a
        distinct sit-in state, since the doc lists NEW_DESIGN_VERSION
        alongside PROJECT_PAUSED/PROJECT_COMPLETED as what the decision
        resolves *into*, not a state anything waits in."""
        return self._transition(
            session, cycle, from_states=("REDESIGN_OR_STOP_DECISION",), to_state="DESIGN_PROPOSED", actor_id=actor_id,
            gate_result=redesign_gate_result, pointer_updates={"active_design_version_id": design_version_id},
        )

    def pause_project(self, session: Session, cycle: IterativeCycleState, *, actor_id: str, reason: str) -> IterativeCycleState:
        cycle.termination_reason = reason
        return self._transition(session, cycle, from_states=("REDESIGN_OR_STOP_DECISION",), to_state="PROJECT_PAUSED", actor_id=actor_id)

    def complete_project(self, session: Session, cycle: IterativeCycleState, *, actor_id: str) -> IterativeCycleState:
        return self._transition(session, cycle, from_states=("REDESIGN_OR_STOP_DECISION",), to_state="PROJECT_COMPLETED", actor_id=actor_id)

    # -- human-in-the-loop resume --------------------------------------------

    def resolve_pending_gate(self, session: Session, cycle: IterativeCycleState, *, actor_id: str) -> IterativeCycleState:
        """Clears `pending_gate`/`waiting_user` after the caller has
        already recorded the real approval/decision elsewhere (design
        approval, policy approval, etc.) - mirrors Problem 01's
        `submit_approval` clearing `pending_request`."""
        cycle.pending_gate = None
        cycle.status = "running"
        cycle.updated_at = now()
        session.flush()
        append_event(
            session, project_id=cycle.project_id, event_type=et.CYCLE_STATE_CHANGED, entity_type="IterativeCycleState",
            entity_id=cycle.cycle_state_id, payload=snapshot(cycle, CYCLE_SNAPSHOT_FIELDS),
            actor_type="human", actor_id=actor_id,
        )
        return cycle
