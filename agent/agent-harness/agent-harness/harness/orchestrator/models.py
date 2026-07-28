"""Unified Scientific Workflow Orchestrator tables (top-level Phase B of the
六大核心模块统一集成 prompt). This package does not fork a second Memory or
Event Ledger: every mutating function in `harness/orchestrator/service.py`
still calls `harness.memory.event_store.append_event` into the SAME
`project_events` table Problems 01-06 use, passing `workflow_run_id` and
`correlation_id` - both columns `ProjectEvent` already declared
(`harness/projects/models.py`) but no prior module ever populated.

`UnifiedWorkflowRun` stores only ID/version references into each module's
own persisted objects (`DiagnosisDecision`, `CandidateDesign`,
`EvaluationCase`, `SimulationCase`, `DesignVersion`, `ExperimentPlan`/
`ExperimentRun`) - never a copy of the object itself (prompt §4.2). Problem
3-6's own controllers remain the sole writers of their own `status` fields;
this package only sequences *when* each is invoked and records the
top-level phase/gate/handoff trail.
"""
from __future__ import annotations

from sqlalchemy import JSON, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from harness.db import Base, guard_immutable_fields

ORCHESTRATOR_PHASES = (
    "INTAKE", "CONTEXT_VALIDATION", "DIAGNOSIS", "DESIGN", "EVALUATION", "SIMULATION",
    "HUMAN_REVIEW", "WAITING_FOR_EXPERIMENT", "OBSERVATION_INGESTION", "LEARNING",
    "REDESIGN", "COMPLETED", "BLOCKED", "FAILED",
)

# `status` is the run's own lifecycle (orthogonal to `current_phase`, which
# names WHERE in the DBTL sequence the run currently is).
ORCHESTRATOR_RUN_STATUSES = ("active", "paused", "waiting", "blocked", "completed", "failed", "cancelled")

GATE_TYPES = (
    "context_completeness", "data_quality", "diagnosis_handoff", "engineering_feasibility",
    "scientific_evaluation", "model_applicability", "simulation_evidence", "safety_ethics",
    "human_approval", "observation_qc", "redesign", "stop",
)

GATE_DECISIONS = (
    "pass", "pass_with_conditions", "revise", "wait_for_data", "human_review_required", "blocked", "not_applicable",
)


class UnifiedWorkflowRun(Base):
    """The one top-level object naming which run of each module belongs to
    this DBTL iteration. Prompt §4.3's YAML mapped 1:1 onto columns; fields
    not applicable to this repo's actual module boundaries (e.g. a single
    `objective_id`) are kept nullable rather than invented."""

    __tablename__ = "orchestrator_workflow_runs"

    workflow_run_id: Mapped[str] = mapped_column(String, primary_key=True)
    project_id: Mapped[str] = mapped_column(String, index=True)
    objective_id: Mapped[str | None] = mapped_column(String, default=None)
    dbtl_iteration_id: Mapped[str | None] = mapped_column(String, default=None)
    # The `IterativeCycleState` (Problem 02's business-cycle container) this
    # run was created under, if the project has one - set once at create_run
    # and never moved (see 状态机一致性 decision in service.py's module
    # docstring: WorkflowRun is the sole execution-state authority once a
    # project adopts it; Cycle stays the legacy/standalone engine for
    # projects that never do - this column is for traceability, not sync).
    cycle_state_id: Mapped[str | None] = mapped_column(String, default=None)

    status: Mapped[str] = mapped_column(String, default="active")
    current_phase: Mapped[str] = mapped_column(String, default="INTAKE")
    current_module: Mapped[str | None] = mapped_column(String, default=None)

    diagnosis_run_ref: Mapped[str | None] = mapped_column(String, default=None)
    diagnosis_handoff_ref: Mapped[str | None] = mapped_column(String, default=None)
    design_project_ref: Mapped[str | None] = mapped_column(String, default=None)
    design_version_ref: Mapped[str | None] = mapped_column(String, default=None)
    evaluation_run_ref: Mapped[str | None] = mapped_column(String, default=None)
    simulation_campaign_ref: Mapped[str | None] = mapped_column(String, default=None)
    experiment_plan_ref: Mapped[str | None] = mapped_column(String, default=None)
    experiment_run_ref: Mapped[str | None] = mapped_column(String, default=None)
    observation_set_ref: Mapped[list] = mapped_column(JSON, default=list)
    active_gate_ref: Mapped[str | None] = mapped_column(String, default=None)

    pause_reason: Mapped[str | None] = mapped_column(String, default=None)
    blocked_reason: Mapped[str | None] = mapped_column(String, default=None)
    # prompt calls this `resume_token_or_checkpoint_ref`; this repo has no
    # separate token concept, so it is the single field that both a
    # cross-process resume() call and a reconciliation pass read/compare.
    checkpoint_ref: Mapped[str | None] = mapped_column(String, default=None)

    correlation_id: Mapped[str] = mapped_column(String, index=True)
    created_at: Mapped[float] = mapped_column(Float)
    updated_at: Mapped[float] = mapped_column(Float)
    version: Mapped[int] = mapped_column(Integer, default=1)


guard_immutable_fields(
    UnifiedWorkflowRun,
    mutable_fields={
        "status", "current_phase", "current_module",
        "diagnosis_run_ref", "diagnosis_handoff_ref", "design_project_ref", "design_version_ref",
        "evaluation_run_ref", "simulation_campaign_ref", "experiment_plan_ref", "experiment_run_ref",
        "observation_set_ref", "active_gate_ref", "pause_reason", "blocked_reason", "checkpoint_ref",
        "objective_id", "dbtl_iteration_id", "updated_at", "version",
    },
)


class OrchestratorTransition(Base):
    """Append-only phase-transition audit trail - the orchestrator-level
    analogue of `DiagnosisTransition`/`SimulationTransition`."""

    __tablename__ = "orchestrator_transitions"

    transition_id: Mapped[str] = mapped_column(String, primary_key=True)
    workflow_run_id: Mapped[str] = mapped_column(String, index=True)
    from_phase: Mapped[str] = mapped_column(String)
    to_phase: Mapped[str] = mapped_column(String)
    reason: Mapped[str] = mapped_column(String, default="")
    actor_id: Mapped[str] = mapped_column(String)
    created_at: Mapped[float] = mapped_column(Float)


guard_immutable_fields(OrchestratorTransition, mutable_fields=set())


class OrchestratorGateDecision(Base):
    """One reusable table for every top-level `GateDecision` (prompt §4.5) -
    not twelve separate near-identical tables. `gate_type` is constrained to
    `GATE_TYPES` by `harness.orchestrator.gates.GateRegistry`, not by a DB
    CHECK constraint (consistent with this repo's existing pattern of
    enforcing enums in the service layer, e.g. `STOPPING_REASONS` in
    `harness/diagnosis/models.py`)."""

    __tablename__ = "orchestrator_gate_decisions"

    gate_decision_id: Mapped[str] = mapped_column(String, primary_key=True)
    workflow_run_id: Mapped[str] = mapped_column(String, index=True)
    gate_type: Mapped[str] = mapped_column(String, index=True)
    decision: Mapped[str] = mapped_column(String)
    evaluated_refs: Mapped[dict] = mapped_column(JSON, default=dict)
    blocking_findings: Mapped[list] = mapped_column(JSON, default=list)
    non_blocking_findings: Mapped[list] = mapped_column(JSON, default=list)
    required_actions: Mapped[list] = mapped_column(JSON, default=list)
    evidence_refs: Mapped[list] = mapped_column(JSON, default=list)
    rule_versions: Mapped[dict] = mapped_column(JSON, default=dict)
    reviewer_refs: Mapped[list] = mapped_column(JSON, default=list)
    actor: Mapped[str] = mapped_column(String)
    timestamp: Mapped[float] = mapped_column(Float)


guard_immutable_fields(OrchestratorGateDecision, mutable_fields=set())


class ModuleHandoffRecord(Base):
    """One reusable table for every cross-module `ModuleHandoff` (prompt
    §4.4). `payload_refs` holds ID/version strings only, never a nested
    object snapshot."""

    __tablename__ = "orchestrator_module_handoffs"

    handoff_id: Mapped[str] = mapped_column(String, primary_key=True)
    workflow_run_id: Mapped[str] = mapped_column(String, index=True)
    source_module: Mapped[str] = mapped_column(String)
    source_run_id: Mapped[str] = mapped_column(String)
    source_version: Mapped[int] = mapped_column(Integer, default=1)
    target_module: Mapped[str] = mapped_column(String)
    payload_refs: Mapped[dict] = mapped_column(JSON, default=dict)
    preconditions: Mapped[list] = mapped_column(JSON, default=list)
    unresolved_items: Mapped[list] = mapped_column(JSON, default=list)
    warnings: Mapped[list] = mapped_column(JSON, default=list)
    confidence_status: Mapped[str] = mapped_column(String, default="unknown")
    gate_decision_ref: Mapped[str | None] = mapped_column(String, default=None)
    created_at: Mapped[float] = mapped_column(Float)


guard_immutable_fields(ModuleHandoffRecord, mutable_fields=set())
