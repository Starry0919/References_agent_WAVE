"""IterativeLoopController: illegal jumps rejected, WAITING_FOR_RESULTS
survives a simulated process restart, gate-rejected transitions never
happen, and the transition history is queryable.
"""
from __future__ import annotations

import pytest

from harness import db
from harness.projects import service as proj_svc
from harness.workflow.contracts import GateResult, GateStatus, GateViolation
from harness.workflow.iterative_loop import GateRejectedError, IllegalCycleTransitionError, IterativeLoopController

loop = IterativeLoopController()


def _project_and_cycle():
    with db.session_scope() as s:
        p = proj_svc.create_project(s, name="t", host_definition={}, target_product="trp", actor_id="pi")
        cycle = proj_svc.get_active_cycle(s, p.project_id)
        return p.project_id, cycle.cycle_state_id


def test_illegal_jump_is_rejected():
    project_id, cycle_id = _project_and_cycle()
    with db.session_scope() as s:
        cycle = loop.get_cycle(s, cycle_id)
        with pytest.raises(IllegalCycleTransitionError):
            loop.begin_data_ingestion(s, cycle, experiment_run_id="RUN-x", actor_id="pi")


def test_gate_rejected_transition_never_happens():
    project_id, cycle_id = _project_and_cycle()
    fail_result = GateResult(gate_name="DataQCGate", status=GateStatus.fail, violations=[
        GateViolation(gate="DataQCGate", code="negative_value", message="bad data")
    ])
    with db.session_scope() as s:
        cycle = loop.get_cycle(s, cycle_id)
        loop.capture_baseline(s, cycle, actor_id="pi")
        loop.propose_design(s, cycle, design_version_id="DV-x", actor_id="agent")
        loop.enter_human_design_gate(s, cycle, actor_id="agent")
        loop.approve_design_and_handoff(s, cycle, actor_id="pi")
        loop.enter_waiting_for_results(s, cycle, experiment_plan_id="PLAN-x", actor_id="wetlab")
        loop.begin_data_ingestion(s, cycle, experiment_run_id="RUN-x", actor_id="wetlab")
        with pytest.raises(GateRejectedError):
            loop.run_data_qc(s, cycle, qc_gate_result=fail_result, actor_id="agent")
        # state must still be DATA_INGESTION - the rejected transition never committed
        assert cycle.current_state == "DATA_INGESTION"


def test_waiting_for_results_survives_simulated_process_restart():
    project_id, cycle_id = _project_and_cycle()
    with db.session_scope() as s:
        cycle = loop.get_cycle(s, cycle_id)
        loop.capture_baseline(s, cycle, actor_id="pi")
        loop.propose_design(s, cycle, design_version_id="DV-x", actor_id="agent")
        loop.enter_human_design_gate(s, cycle, actor_id="agent")
        loop.approve_design_and_handoff(s, cycle, actor_id="pi")
        loop.enter_waiting_for_results(s, cycle, experiment_plan_id="PLAN-x", actor_id="wetlab")
        assert cycle.current_state == "WAITING_FOR_RESULTS"

    # Simulate the process ending entirely: reload purely from the DB, no
    # in-memory object survives across this boundary in this test.
    with db.session_scope() as s:
        reloaded = loop.get_cycle(s, cycle_id)
        assert reloaded.current_state == "WAITING_FOR_RESULTS"
        loop.begin_data_ingestion(s, reloaded, experiment_run_id="RUN-y", actor_id="wetlab")
        assert reloaded.current_state == "DATA_INGESTION"


def test_human_design_gate_sets_pending_gate_and_blocks_until_resolved():
    project_id, cycle_id = _project_and_cycle()
    with db.session_scope() as s:
        cycle = loop.get_cycle(s, cycle_id)
        loop.capture_baseline(s, cycle, actor_id="pi")
        loop.propose_design(s, cycle, design_version_id="DV-x", actor_id="agent")
        loop.enter_human_design_gate(s, cycle, actor_id="agent")
        assert cycle.status == "waiting_user"
        assert cycle.pending_gate is not None
        with pytest.raises(IllegalCycleTransitionError):
            loop.enter_waiting_for_results(s, cycle, experiment_plan_id="PLAN-x", actor_id="wetlab")
        loop.approve_design_and_handoff(s, cycle, actor_id="pi")
        assert cycle.current_state == "BUILD_TEST_HANDOFF"


def test_transition_history_is_recorded():
    project_id, cycle_id = _project_and_cycle()
    with db.session_scope() as s:
        cycle = loop.get_cycle(s, cycle_id)
        loop.capture_baseline(s, cycle, actor_id="pi")

    with db.session_scope() as s:
        from sqlalchemy import select
        from harness.projects.models import IterativeCycleTransition
        rows = s.execute(select(IterativeCycleTransition).where(IterativeCycleTransition.cycle_state_id == cycle_id)).scalars().all()
        assert len(rows) == 1
        assert rows[0].state == "PROJECT_CONTEXT_READY"
        assert rows[0].selected_next_state == "DESIGN_BASELINE_CAPTURED"
