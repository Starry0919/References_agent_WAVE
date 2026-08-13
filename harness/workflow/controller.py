"""`WorkflowController`: the single writer of `WorkflowRun.current_stage`
and `WorkflowRun.status`. Nothing else in this codebase may set either
field directly - a stage implementation (`synbio_stages.py`) only ever
*proposes* a `StageOutcome`; this controller decides whether the proposal
passes its gates and what happens next (doc: "LLM 无法直接修改
current_stage").

`advance()` is deliberately split into named steps (design-review fix #3)
so a test can assert on "illegal jump rejected" or "unauthorized tool
call rejected" without going through a full multi-stage integration run.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Callable

from harness.tools.executor import ToolExecutor
from harness.workflow import gates
from harness.workflow.store import JSONCheckpointStore, RunStore
from harness.workflow.contracts import (
    ApprovalDecision,
    ApprovalRecord,
    DiagnosisRecord,
    EngineeringDecision,
    GateResult,
    GateStatus,
    PendingRequest,
    PendingRequestKind,
)
from harness.workflow.definitions import STAGE_DEFINITIONS, Stage, StageDefinition
from harness.workflow.policies import RetryPolicy
from harness.workflow.state import RunStatus, StageRecord, StageRecordStatus, WorkflowRun


def _first_decision_id_in_violations(gate_result: GateResult) -> str | None:
    """Best-effort extraction of which decision a human_review GateResult is
    actually about, so the resulting `PendingRequest.decision_id` can be
    resolved by `submit_approval()` without the caller having to dig
    through violations themselves."""
    for v in gate_result.violations:
        if v.target_id and v.target_id.startswith("DEC-"):
            return v.target_id
    return None


class WorkflowEngineError(Exception):
    """Base for all controller-raised errors."""


class IllegalTransitionError(WorkflowEngineError):
    """Raised when a stage's entry_condition is not met - the only way to
    reach a stage is through `advance()` following `allowed_next_stages`,
    so this only fires if a run's `current_stage` was tampered with
    directly, or a bug tries to skip a required predecessor stage."""


class RunAlreadyTerminalError(WorkflowEngineError):
    """A completed/failed/cancelled run cannot be advanced again - the
    non-idempotent-rerun guard the acceptance bar requires."""


class RunWaitingOnUserError(WorkflowEngineError):
    """A run with an unresolved `pending_request` cannot be advanced until
    `submit_user_response()` or `submit_approval()` clears it."""


@dataclass
class StageOutcome:
    """What a stage implementation returns. Generic - not synbio-specific -
    so a future non-synbio workflow can reuse this same controller."""

    output: dict[str, Any]
    schema_valid: bool
    schema_errors: list[str]
    apply: Callable[[WorkflowRun], None]
    gate_candidates: list[EngineeringDecision] = field(default_factory=list)
    diagnosis: DiagnosisRecord | None = None
    resolve: Callable[[WorkflowRun, GateResult, dict[str, str]], None] | None = None
    pending_request: PendingRequest | None = None


StageImpl = Callable[[WorkflowRun, ToolExecutor], StageOutcome]


class WorkflowController:
    def __init__(
        self,
        stage_impls: dict[Stage, StageImpl],
        tool_executor: ToolExecutor,
        retry_policy: RetryPolicy | None = None,
        store: RunStore | None = None,
    ) -> None:
        self._impls = stage_impls
        self._tools = tool_executor
        self._retry = retry_policy or RetryPolicy()
        self._store: RunStore = store or JSONCheckpointStore()

    # -- run lifecycle -----------------------------------------------------

    def create_run(self, raw_request: str) -> WorkflowRun:
        run = WorkflowRun(status=RunStatus.running, current_stage=Stage.INTAKE.value)
        run.decisions.append({"event": "intake", "raw_request": raw_request, "ts": time.time()})
        self._store.save(run)
        return run

    def resume(self, run_id: str) -> WorkflowRun | None:
        return self._store.load(run_id)

    def run_to_completion_or_pause(self, run: WorkflowRun, *, max_steps: int = 30) -> WorkflowRun:
        """Repeatedly `advance()` until the run reaches a terminal state or
        needs the user (`waiting_user`/`blocked`), bounded by `max_steps` so
        a bug can never spin forever."""
        for _ in range(max_steps):
            if run.status in (RunStatus.completed, RunStatus.failed, RunStatus.cancelled,
                               RunStatus.waiting_user, RunStatus.blocked):
                return run
            run = self.advance(run)
        return run

    # -- human-in-the-loop resume paths -------------------------------------

    def submit_user_response(self, run: WorkflowRun, *, response: str) -> WorkflowRun:
        if run.pending_request is None or run.pending_request.kind != PendingRequestKind.missing_information:
            raise ValueError("run has no pending missing_information request")
        for d in run.decisions:
            if d.get("event") == "intake":
                d["raw_request"] = f"{d.get('raw_request', '')} {response}".strip()
        run.current_stage = Stage.TASK_NORMALIZATION.value
        run.pending_request = None
        run.status = RunStatus.running
        self._store.save(run)
        return run

    def submit_approval(
        self,
        run: WorkflowRun,
        *,
        decision_id: str,
        approver: str,
        decision: str,
        risk_reason: str = "",
        evidence_snapshot: list[str] | None = None,
    ) -> WorkflowRun:
        record = ApprovalRecord(
            requested_action=f"approve engineering decision {decision_id}",
            risk_reason=risk_reason or "forced human approval tier (doc 5.7)",
            evidence_snapshot=evidence_snapshot or [],
            approver=approver,
            decision=ApprovalDecision(decision),
            scope=decision_id,
        )
        run.approvals.append(record)
        if run.status == RunStatus.waiting_user and run.pending_request and run.pending_request.decision_id == decision_id:
            run.pending_request = None
            run.status = RunStatus.running
        self._store.save(run)
        return run

    # -- the single transition entry point ----------------------------------

    def advance(self, run: WorkflowRun) -> WorkflowRun:
        if run.status in (RunStatus.completed, RunStatus.failed, RunStatus.cancelled):
            raise RunAlreadyTerminalError(f"run {run.run_id} is already {run.status.value}")
        if run.status == RunStatus.waiting_user:
            raise RunWaitingOnUserError(f"run {run.run_id} is waiting_user; resolve pending_request first")
        if run.status == RunStatus.blocked:
            raise RunAlreadyTerminalError(f"run {run.run_id} is blocked: {run.termination_reason}")

        if len(run.stage_records) >= self._retry.max_total_stage_executions:
            run.status = RunStatus.blocked
            run.termination_reason = f"exceeded max_total_stage_executions budget ({self._retry.max_total_stage_executions})"
            self._store.save(run)
            return run

        stage = Stage(run.current_stage)
        stage_def = STAGE_DEFINITIONS[stage]

        ok, reason = (stage_def.entry_condition or (lambda _r: (True, "")))(run)
        if not ok:
            raise IllegalTransitionError(f"cannot enter {stage.value}: {reason}")

        attempt = run.attempts_for(stage.value) + 1
        record = StageRecord(
            stage_id=stage.value,
            attempt=attempt,
            allowed_next_stages=[s.value for s in stage_def.allowed_next_stages],
            implementation_status=stage_def.implementation_status,
        )

        try:
            outcome = self._impls[stage](run, self._tools)
        except Exception as exc:  # noqa: BLE001 - a stage bug must not crash the run silently
            record.status = StageRecordStatus.failed
            record.error = f"{type(exc).__name__}: {exc}"
            record.ended_at = time.time()
            run.stage_records.append(record)
            run.status = RunStatus.failed
            run.termination_reason = f"unhandled exception in stage {stage.value}: {record.error}"
            self._store.save(run)
            return run

        record.output = outcome.output
        record.schema_valid = outcome.schema_valid

        if not outcome.schema_valid:
            ctx = gates.GateContext(stage_id=stage.value, schema_valid=False, schema_errors=outcome.schema_errors)
            record.gate_result = gates.run_gate_battery(ctx, stage_def.gates)
            record.status = StageRecordStatus.failed
            record.error = "; ".join(outcome.schema_errors)
            record.ended_at = time.time()
            run.stage_records.append(record)
            self._retry_or_fallback(run, stage, stage_def, attempt, record.gate_result, outcome)
            self._store.save(run)
            return run

        # Phase 1: commit the stage's own state updates.
        outcome.apply(run)

        approvals_by_scope = {a.scope: a.decision.value for a in run.approvals}
        ctx = gates.GateContext(
            stage_id=stage.value,
            schema_valid=True,
            candidates=outcome.gate_candidates,
            host_species=run.biological_state.host.species,
            approvals=approvals_by_scope,
            diagnosis=outcome.diagnosis,
        )
        gate_result = gates.run_gate_battery(ctx, stage_def.gates)
        record.gate_result = gate_result

        # Phase 2: gate-result-dependent finalization (e.g. resolving
        # candidate_designs -> engineering_decisions status).
        if outcome.resolve is not None:
            outcome.resolve(run, gate_result, approvals_by_scope)

        record.ended_at = time.time()

        # A stage-level pending_request (e.g. TASK_NORMALIZATION: missing
        # target) blocks progress regardless of gate status - the stage
        # implementation itself is refusing to guess, which SchemaGate alone
        # cannot detect (its output is still schema-valid).
        if outcome.pending_request is not None:
            record.status = StageRecordStatus.completed
            run.stage_records.append(record)
            run.status = RunStatus.waiting_user
            run.pending_request = outcome.pending_request
            self._store.save(run)
            return run

        if gate_result.status == GateStatus.passed:
            record.status = StageRecordStatus.completed
            next_stage = stage_def.allowed_next_stages[0] if stage_def.allowed_next_stages else None
            record.selected_next_stage = next_stage.value if next_stage else None
            record.selection_reason = "all required gates passed"
            run.stage_records.append(record)
            if next_stage is None:
                run.status = RunStatus.completed
                run.termination_reason = "workflow reached REPORT and completed"
            else:
                run.current_stage = next_stage.value
                run.status = RunStatus.running
            self._store.save(run)
            return run

        record.status = StageRecordStatus.completed if gate_result.status == GateStatus.human_review else StageRecordStatus.failed
        run.stage_records.append(record)

        if gate_result.status == GateStatus.human_review:
            run.status = RunStatus.waiting_user
            run.pending_request = PendingRequest(
                kind=PendingRequestKind.approval,
                stage_id=stage.value,
                question="; ".join(gate_result.required_actions) or f"{stage.value} requires human review",
                decision_id=_first_decision_id_in_violations(gate_result),
            )
            self._store.save(run)
            return run

        self._retry_or_fallback(run, stage, stage_def, attempt, gate_result, outcome)
        self._store.save(run)
        return run

    # -- retry / fallback / termination (doc 5.8) ---------------------------

    def _retry_or_fallback(
        self,
        run: WorkflowRun,
        stage: Stage,
        stage_def: StageDefinition,
        attempt: int,
        gate_result: GateResult,
        outcome: StageOutcome,
    ) -> None:
        history = [r for r in run.stage_records if r.stage_id == stage.value]
        if len(history) >= 2 and history[-1].output == history[-2].output:
            run.status = RunStatus.blocked
            run.termination_reason = (
                f"{stage.value}: two consecutive attempts produced identical output with no new "
                "information; stopping and requesting human judgment instead of looping (doc 5.8)"
            )
            return

        if attempt >= stage_def.retry_limit:
            self._apply_fallback(run, stage, stage_def, gate_result, outcome)
        else:
            run.status = RunStatus.running  # same stage, next advance() retries it

    def _apply_fallback(
        self,
        run: WorkflowRun,
        stage: Stage,
        stage_def: StageDefinition,
        gate_result: GateResult,
        outcome: StageOutcome,
    ) -> None:
        fallback = stage_def.fallback
        violation_summary = "; ".join(v.message for v in gate_result.violations) or "; ".join(gate_result.required_actions)

        if fallback == "fail":
            run.status = RunStatus.failed
            run.termination_reason = f"{stage.value} failed after {stage_def.retry_limit} attempt(s): {violation_summary}"

        elif fallback == "waiting_user":
            run.status = RunStatus.waiting_user
            run.pending_request = outcome.pending_request or PendingRequest(
                kind=PendingRequestKind.missing_information,
                stage_id=stage.value,
                question=violation_summary or f"{stage.value} needs user input",
            )

        elif fallback == "insufficient_evidence":
            evidence_attempts = run.attempts_for(Stage.CONTEXT_AND_EVIDENCE_ACQUISITION.value)
            if evidence_attempts >= self._retry.max_stage_attempts + 1:
                run.status = RunStatus.blocked
                run.termination_reason = (
                    "insufficient evidence to support a conclusion after the evidence-acquisition "
                    f"budget was exhausted: {violation_summary}"
                )
            else:
                run.current_stage = Stage.CONTEXT_AND_EVIDENCE_ACQUISITION.value
                run.status = RunStatus.running

        elif fallback == "revise_candidates":
            run.current_stage = Stage.ENGINEERING_STRATEGY_GENERATION.value
            run.status = RunStatus.running
            run.decisions.append({"event": "revise_candidates", "reason": violation_summary, "ts": time.time()})

        elif fallback == "degrade_to_no_evidence":
            run.biological_state.uncertainty.assumptions.append(
                f"{stage.value} degraded to a no-evidence continuation after repeated failure: {violation_summary}"
            )
            next_stage = stage_def.allowed_next_stages[0] if stage_def.allowed_next_stages else None
            run.current_stage = next_stage.value if next_stage else run.current_stage
            run.status = RunStatus.running

        else:
            run.status = RunStatus.blocked
            run.termination_reason = f"unrecognized fallback policy '{fallback}' for stage {stage.value}"
