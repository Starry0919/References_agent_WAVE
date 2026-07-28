"""Controller-level unit tests (doc 7.1/7.4): illegal stage jumps rejected,
retry-then-stop, checkpoint-restore consistency, non-idempotent rerun
prevention, and human-approval actually blocking the transition."""
from __future__ import annotations

import pytest

from harness.tools.executor import ToolExecutor
from harness.workflow import checkpoint
from harness.workflow.controller import (
    IllegalTransitionError,
    RunAlreadyTerminalError,
    RunWaitingOnUserError,
    StageOutcome,
    WorkflowController,
)
from harness.workflow.definitions import Stage
from harness.workflow.state import RunStatus, StageRecordStatus
from harness.workflow.synbio_stages import STAGE_IMPLS, build_controller, build_tool_executor


def _empty_tool_executor() -> ToolExecutor:
    return ToolExecutor({})


def test_advancing_a_fresh_run_walks_intake_to_task_normalization() -> None:
    controller = build_controller()
    run = controller.create_run("Improve E. coli K-12 L-tryptophan production from glucose.")
    assert run.current_stage == Stage.INTAKE.value
    run = controller.advance(run)
    assert run.current_stage == Stage.TASK_NORMALIZATION.value
    assert run.stage_records[-1].stage_id == Stage.INTAKE.value
    assert run.stage_records[-1].status == StageRecordStatus.completed


def test_illegal_stage_jump_is_rejected() -> None:
    controller = build_controller()
    run = controller.create_run("Improve E. coli K-12 L-tryptophan production from glucose.")
    # Tamper directly with current_stage the way a buggy/malicious caller
    # might try to "skip ahead" - the controller is the only legitimate
    # writer, so this must be rejected via each stage's entry_condition.
    run.current_stage = Stage.MODEL_AND_RULE_VALIDATION.value
    with pytest.raises(IllegalTransitionError):
        controller.advance(run)


def test_completed_run_cannot_be_advanced_again() -> None:
    controller = build_controller()
    run = controller.create_run("Improve E. coli K-12 L-tryptophan production from glucose.")
    run = controller.run_to_completion_or_pause(run, max_steps=30)
    assert run.status == RunStatus.completed
    with pytest.raises(RunAlreadyTerminalError):
        controller.advance(run)


def test_waiting_user_run_cannot_be_advanced_without_resolving_pending_request() -> None:
    controller = build_controller()
    run = controller.create_run("Improve E. coli K-12 production from glucose.")  # no product
    run = controller.run_to_completion_or_pause(run, max_steps=10)
    assert run.status == RunStatus.waiting_user
    with pytest.raises(RunWaitingOnUserError):
        controller.advance(run)


def test_submit_user_response_resumes_a_waiting_user_run() -> None:
    controller = build_controller()
    run = controller.create_run("Improve E. coli K-12 production from glucose.")
    run = controller.run_to_completion_or_pause(run, max_steps=10)
    assert run.status == RunStatus.waiting_user
    run = controller.submit_user_response(run, response="L-tryptophan")
    run = controller.run_to_completion_or_pause(run, max_steps=30)
    assert run.status == RunStatus.completed
    assert run.task_spec is not None
    assert run.task_spec.product == "L-tryptophan"


def test_schema_invalid_stage_retries_then_fails_after_retry_limit() -> None:
    attempts = {"n": 0}

    def flaky_intake(run, _tools):
        attempts["n"] += 1
        return StageOutcome(output={"attempt": attempts["n"]}, schema_valid=False, schema_errors=["always invalid"], apply=lambda r: None)

    impls = dict(STAGE_IMPLS)
    impls[Stage.INTAKE] = flaky_intake
    controller = WorkflowController(impls, _empty_tool_executor())
    run = controller.create_run("anything")

    # INTAKE's retry_limit is 1 -> the very first failure should exhaust it
    # and trigger INTAKE's "fail" fallback immediately.
    run = controller.advance(run)
    assert run.status == RunStatus.failed
    assert attempts["n"] == 1


def test_stage_retries_before_exhausting_limit_then_advances_on_recovery() -> None:
    calls = {"n": 0}

    def sometimes_invalid(run, _tools):
        calls["n"] += 1
        if calls["n"] == 1:
            return StageOutcome(output={"n": 1}, schema_valid=False, schema_errors=["retry me"], apply=lambda r: None)
        return StageOutcome(output={"n": calls["n"]}, schema_valid=True, schema_errors=[], apply=lambda r: None)

    impls = dict(STAGE_IMPLS)
    impls[Stage.TASK_NORMALIZATION] = sometimes_invalid  # retry_limit=2
    controller = WorkflowController(impls, _empty_tool_executor())
    run = controller.create_run("anything")
    run = controller.advance(run)  # INTAKE -> TASK_NORMALIZATION
    assert run.current_stage == Stage.TASK_NORMALIZATION.value

    run = controller.advance(run)  # attempt 1: invalid, retry (under limit)
    assert run.status == RunStatus.running
    assert run.current_stage == Stage.TASK_NORMALIZATION.value

    run = controller.advance(run)  # attempt 2: valid, passes gates, advances
    assert run.current_stage == Stage.CONTEXT_AND_EVIDENCE_ACQUISITION.value


def test_two_identical_consecutive_attempts_stop_instead_of_looping_forever() -> None:
    def always_same_invalid(run, _tools):
        return StageOutcome(output={"n": 1}, schema_valid=False, schema_errors=["never changes"], apply=lambda r: None)

    impls = dict(STAGE_IMPLS)
    impls[Stage.TASK_NORMALIZATION] = always_same_invalid
    controller = WorkflowController(impls, _empty_tool_executor())
    run = controller.create_run("anything")
    run = controller.advance(run)  # INTAKE -> TASK_NORMALIZATION

    run = controller.advance(run)  # attempt 1 (retry_limit=2, so this retries)
    assert run.status == RunStatus.running
    run = controller.advance(run)  # attempt 2: identical output to attempt 1 -> stop
    assert run.status == RunStatus.blocked
    assert "identical output" in (run.termination_reason or "")


def test_checkpoint_restore_is_consistent_after_each_transition() -> None:
    controller = build_controller()
    run = controller.create_run("Improve E. coli K-12 L-tryptophan production from glucose.")
    for _ in range(4):
        run = controller.advance(run)
        reloaded = checkpoint.load(run.run_id)
        assert reloaded is not None
        assert reloaded.current_stage == run.current_stage
        assert reloaded.status == run.status
        assert len(reloaded.stage_records) == len(run.stage_records)


def test_essential_gene_knockout_requires_approval_before_implementation_plan() -> None:
    """End-to-end: a run whose only candidate is an essential-gene knockout
    must reach waiting_user at MODEL_AND_RULE_VALIDATION and never silently
    proceed into EXPERIMENT_AND_IMPLEMENTATION_PLAN without an approval."""
    from harness.workflow.contracts import EngineeringDecision, EvidenceRecord, OperationType, TargetEntity, TargetEntityType

    def strategy_generation_with_essential_ko(run, _tools):
        evid = EvidenceRecord(action_source="ddr_reasoning", evidence_status="reference_available", confidence="medium")
        decision = EngineeringDecision(
            target_entity=TargetEntity(type=TargetEntityType.gene, canonical_id="ftsZ", display_name="ftsZ"),
            operation=OperationType.knockout,
            mechanism="test", expected_effect="test",
            evidence_record_ids=[evid.evidence_record_id],
        )

        def apply(r):
            r.evidence_records.append(evid)
            r.candidate_designs.append(decision)

        return StageOutcome(output={"candidate_count": 1}, schema_valid=True, schema_errors=[], apply=apply, gate_candidates=[decision])

    impls = dict(STAGE_IMPLS)
    impls[Stage.ENGINEERING_STRATEGY_GENERATION] = strategy_generation_with_essential_ko
    controller = WorkflowController(impls, build_tool_executor())
    run = controller.create_run("Improve E. coli K-12 L-tryptophan production from glucose.")
    run = controller.run_to_completion_or_pause(run, max_steps=30)

    assert run.status == RunStatus.waiting_user
    assert run.current_stage == Stage.MODEL_AND_RULE_VALIDATION.value
    assert run.pending_request is not None
    assert run.pending_request.kind.value == "approval"

    decision_id = run.pending_request.decision_id
    run = controller.submit_approval(run, decision_id=decision_id, approver="test_reviewer", decision="approved")
    run = controller.run_to_completion_or_pause(run, max_steps=30)

    assert run.status == RunStatus.completed
    resolved = [d for d in run.engineering_decisions if d.decision_id == decision_id]
    assert resolved and resolved[0].status.value == "accepted"
