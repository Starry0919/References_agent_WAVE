"""`WorkflowRun` / `StageRecord` (doc 5.2): the top-level structured run
state. `WorkflowController` (controller.py) is the only code allowed to
mutate `current_stage` or append to `stage_records`; everything else reads
this object or proposes into it via a `StageOutput`.
"""
from __future__ import annotations

import time
from enum import Enum
from typing import Any

from pydantic import Field

from harness.workflow.contracts import (
    ApprovalRecord,
    BiologicalState,
    DiagnosisRecord,
    EngineeringDecision,
    EvidenceRecord,
    GateResult,
    PendingRequest,
    StrictModel,
    TaskSpec,
    ToolRecord,
    ValidationPlanItem,
    new_id,
)

WORKFLOW_VERSION = "synbio_v1.workflow_engine.1"


class RunStatus(str, Enum):
    queued = "queued"
    running = "running"
    waiting_user = "waiting_user"
    blocked = "blocked"
    failed = "failed"
    completed = "completed"
    cancelled = "cancelled"


class StageRecordStatus(str, Enum):
    running = "running"
    completed = "completed"
    failed = "failed"
    skipped = "skipped"


class ImplementationStatus(str, Enum):
    """Honesty label required by doc 5.3: a scaffold stage must never be
    reported as if it had expert-level diagnostic depth."""

    scaffold = "scaffold"
    partial = "partial"
    validated = "validated"


class StageRecord(StrictModel):
    stage_id: str
    attempt: int = 1
    status: StageRecordStatus = StageRecordStatus.running
    started_at: float = Field(default_factory=time.time)
    ended_at: float | None = None
    input_snapshot: dict[str, Any] = Field(default_factory=dict)
    output: dict[str, Any] = Field(default_factory=dict)
    schema_valid: bool | None = None
    gate_result: GateResult | None = None
    allowed_next_stages: list[str] = Field(default_factory=list)
    selected_next_stage: str | None = None
    selection_reason: str = ""
    model_id: str = "deterministic:v1"
    prompt_version: str = "n/a"
    tool_call_ids: list[str] = Field(default_factory=list)
    error: str | None = None
    implementation_status: ImplementationStatus = ImplementationStatus.validated


class WorkflowRun(StrictModel):
    run_id: str = Field(default_factory=lambda: new_id("RUN"))
    workflow_version: str = WORKFLOW_VERSION
    project_id: str = "synbio_v1"
    status: RunStatus = RunStatus.queued
    current_stage: str = "INTAKE"

    task_spec: TaskSpec | None = None
    biological_state: BiologicalState = Field(default_factory=BiologicalState)

    stage_records: list[StageRecord] = Field(default_factory=list)

    # Append-only proposals from ENGINEERING_STRATEGY_GENERATION - never
    # mutated in place once appended (design-review fix #1). A revised
    # decision is always a *new* EngineeringDecision with parent_decision_ids
    # pointing back, never an edit to an existing candidate_designs entry.
    candidate_designs: list[EngineeringDecision] = Field(default_factory=list)

    # Same EngineeringDecision objects, carried forward and status-updated by
    # MODEL_AND_RULE_VALIDATION's gates (proposed -> accepted/rejected/
    # revised/human_review). This list, not candidate_designs, is where
    # status ever changes.
    engineering_decisions: list[EngineeringDecision] = Field(default_factory=list)

    diagnoses: list[DiagnosisRecord] = Field(default_factory=list)
    evidence_records: list[EvidenceRecord] = Field(default_factory=list)
    tool_records: list[ToolRecord] = Field(default_factory=list)
    validation_records: list[ValidationPlanItem] = Field(default_factory=list)
    approvals: list[ApprovalRecord] = Field(default_factory=list)

    # doc 5.2 also lists a generic `decisions: []` array (workflow-level
    # audit trail of controller choices, distinct from EngineeringDecision)
    decisions: list[dict[str, Any]] = Field(default_factory=list)

    checkpoints: list[str] = Field(default_factory=list)  # checkpoint file paths, newest last
    final_report: str | None = None

    pending_request: PendingRequest | None = None
    created_at: float = Field(default_factory=time.time)
    updated_at: float = Field(default_factory=time.time)
    termination_reason: str | None = None

    def latest_record_for(self, stage_id: str) -> StageRecord | None:
        for record in reversed(self.stage_records):
            if record.stage_id == stage_id:
                return record
        return None

    def attempts_for(self, stage_id: str) -> int:
        return sum(1 for r in self.stage_records if r.stage_id == stage_id)
