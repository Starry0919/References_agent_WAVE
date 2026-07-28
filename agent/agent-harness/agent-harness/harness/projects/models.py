"""Project, event ledger, actor identity, and the durable Iterative Design
Loop cycle state - the persistence-layer foundation everything else in the
Problem-02 stack hangs off (doc section 8.1, section 9, section 10).
"""
from __future__ import annotations

from sqlalchemy import JSON, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from harness.db import Base


class Actor(Base):
    """Minimal collaboration-governance identity (doc 6.11): every mutating
    event carries an actor_id resolved through this table. `role` is a
    simplified RBAC tier, not a full ABAC policy engine (explicitly
    out of scope this round)."""

    __tablename__ = "actors"

    actor_id: Mapped[str] = mapped_column(String, primary_key=True)
    display_name: Mapped[str] = mapped_column(String)
    actor_type: Mapped[str] = mapped_column(String)  # human|agent|tool|external_system
    role: Mapped[str] = mapped_column(String, default="proposer")  # viewer|proposer|approver|admin
    created_at: Mapped[float] = mapped_column(Float)


class Project(Base):
    """doc 8.1. `version` is the optimistic-concurrency guard (doc 6.11):
    every mutation that touches project-level pointer fields must supply
    the version it read, or be rejected as a conflict - never silent
    last-write-wins."""

    __tablename__ = "projects"

    project_id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    host_definition: Mapped[dict] = mapped_column(JSON, default=dict)
    target_product: Mapped[str] = mapped_column(String)
    objectives: Mapped[list] = mapped_column(JSON, default=list)
    constraints: Mapped[list] = mapped_column(JSON, default=list)
    current_design_branch: Mapped[str] = mapped_column(String, default="main")
    current_design_version_id: Mapped[str | None] = mapped_column(String, default=None)
    status: Mapped[str] = mapped_column(String, default="active")  # active|paused|completed
    lifecycle_stage: Mapped[str] = mapped_column(String, default="PROJECT_CONTEXT_READY")
    owners: Mapped[list] = mapped_column(JSON, default=list)  # actor_ids
    version: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[float] = mapped_column(Float)
    updated_at: Mapped[float] = mapped_column(Float)


class ProjectEvent(Base):
    """The append-only event ledger (doc 9.1) - the single source of truth
    every materialized view must be reconstructable from
    (`harness/memory/event_store.py::replay_project`). `payload` carries a
    FULL entity snapshot, not a diff, so replay is a uniform "insert/update
    this record" reduction rather than N bespoke per-event-type appliers
    (design-review requirement: replay-correctness must be provable, not
    just asserted). `seq` is a monotonic per-row order independent of
    `timestamp` (clocks can collide or skew; replay order must not)."""

    __tablename__ = "project_events"

    # `seq` (not `event_id`) is the primary key: SQLite (and Postgres via
    # SERIAL/IDENTITY) only guarantees monotonic auto-increment for the
    # actual integer primary key. `event_id` remains the stable business
    # identifier used in payloads/API responses.
    seq: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    event_id: Mapped[str] = mapped_column(String, unique=True, index=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.project_id"), index=True)
    event_type: Mapped[str] = mapped_column(String, index=True)
    entity_type: Mapped[str] = mapped_column(String)
    entity_id: Mapped[str] = mapped_column(String)
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    actor_type: Mapped[str] = mapped_column(String)
    actor_id: Mapped[str] = mapped_column(String)
    causation_id: Mapped[str | None] = mapped_column(String, default=None)
    correlation_id: Mapped[str | None] = mapped_column(String, default=None)
    workflow_run_id: Mapped[str | None] = mapped_column(String, default=None)
    timestamp: Mapped[float] = mapped_column(Float)
    schema_version: Mapped[str] = mapped_column(String, default="1")


class IdempotencyKey(Base):
    """doc 9.3: checksum-derived (or caller-supplied) keys that let upload/
    parse/event-write retries detect "already done" instead of producing
    duplicate Observations or design versions."""

    __tablename__ = "idempotency_keys"

    key: Mapped[str] = mapped_column(String, primary_key=True)
    project_id: Mapped[str] = mapped_column(String, index=True)
    entity_type: Mapped[str] = mapped_column(String)
    entity_id: Mapped[str] = mapped_column(String)
    created_at: Mapped[float] = mapped_column(Float)


class IterativeCycleState(Base):
    """The durable Iterative Design Loop position (doc section 10) - the
    SQL-backed analogue of Problem 01's `WorkflowRun`, but built to survive
    the process ending entirely: `WAITING_FOR_RESULTS` can persist for
    days. One row per active cycle per project (a project can have at most
    one non-terminal cycle at a time in this round)."""

    __tablename__ = "iterative_cycle_states"

    cycle_state_id: Mapped[str] = mapped_column(String, primary_key=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.project_id"), index=True)
    current_state: Mapped[str] = mapped_column(String)
    active_design_version_id: Mapped[str | None] = mapped_column(String, default=None)
    active_experiment_plan_id: Mapped[str | None] = mapped_column(String, default=None)
    active_experiment_run_id: Mapped[str | None] = mapped_column(String, default=None)
    active_learning_cycle_id: Mapped[str | None] = mapped_column(String, default=None)
    pending_gate: Mapped[dict | None] = mapped_column(JSON, default=None)
    status: Mapped[str] = mapped_column(String, default="running")  # running|waiting_user|blocked|completed|paused
    termination_reason: Mapped[str | None] = mapped_column(String, default=None)
    version: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[float] = mapped_column(Float)
    updated_at: Mapped[float] = mapped_column(Float)


class IterativeCycleTransition(Base):
    """Transition history for one `IterativeCycleState` - the relational
    analogue of Problem 01's `StageRecord`, queryable for a Project
    Timeline view without replaying the whole event ledger."""

    __tablename__ = "iterative_cycle_transitions"

    transition_id: Mapped[str] = mapped_column(String, primary_key=True)
    cycle_state_id: Mapped[str] = mapped_column(ForeignKey("iterative_cycle_states.cycle_state_id"), index=True)
    state: Mapped[str] = mapped_column(String)
    attempt: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[str] = mapped_column(String)  # completed|failed|skipped
    output: Mapped[dict] = mapped_column(JSON, default=dict)
    gate_result: Mapped[dict | None] = mapped_column(JSON, default=None)
    selected_next_state: Mapped[str | None] = mapped_column(String, default=None)
    selection_reason: Mapped[str] = mapped_column(String, default="")
    error: Mapped[str | None] = mapped_column(String, default=None)
    started_at: Mapped[float] = mapped_column(Float)
    ended_at: Mapped[float | None] = mapped_column(Float, default=None)
