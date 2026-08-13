from __future__ import annotations

from sqlalchemy import JSON, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from harness.db import Base, guard_immutable_fields

TASK_STATUSES = ("created", "planning", "executing", "waiting_module", "human_review", "completed", "failed")
NODE_STATUSES = ("pending", "ready", "running", "waiting", "completed", "failed", "skipped")


class ScientificTask(Base):
    __tablename__ = "runtime_scientific_tasks"
    task_id: Mapped[str] = mapped_column(String, primary_key=True)
    project_id: Mapped[str] = mapped_column(String, index=True)
    workflow_run_id: Mapped[str | None] = mapped_column(String, default=None)
    objective: Mapped[str] = mapped_column(String)
    constraints: Mapped[dict] = mapped_column(JSON, default=dict)
    current_stage: Mapped[str] = mapped_column(String, default="intake")
    task_status: Mapped[str] = mapped_column(String, default="created")
    completed_steps: Mapped[list] = mapped_column(JSON, default=list)
    pending_steps: Mapped[list] = mapped_column(JSON, default=list)
    module_outputs: Mapped[dict] = mapped_column(JSON, default=dict)
    human_actions: Mapped[list] = mapped_column(JSON, default=list)
    execution_history: Mapped[list] = mapped_column(JSON, default=list)
    failure: Mapped[dict | None] = mapped_column(JSON, default=None)
    created_at: Mapped[float] = mapped_column(Float)
    updated_at: Mapped[float] = mapped_column(Float)


guard_immutable_fields(ScientificTask, mutable_fields={"workflow_run_id", "current_stage", "task_status", "completed_steps", "pending_steps", "module_outputs", "human_actions", "execution_history", "failure", "updated_at"})


class RuntimeTaskNode(Base):
    __tablename__ = "runtime_task_nodes"
    node_id: Mapped[str] = mapped_column(String, primary_key=True)
    task_id: Mapped[str] = mapped_column(ForeignKey("runtime_scientific_tasks.task_id"), index=True)
    capability_name: Mapped[str] = mapped_column(String)
    module_name: Mapped[str] = mapped_column(String)
    dependencies: Mapped[list] = mapped_column(JSON, default=list)
    status: Mapped[str] = mapped_column(String, default="pending")
    input_refs: Mapped[dict] = mapped_column(JSON, default=dict)
    output_refs: Mapped[dict] = mapped_column(JSON, default=dict)
    requires_human_approval: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[float] = mapped_column(Float)


guard_immutable_fields(RuntimeTaskNode, mutable_fields={"status", "input_refs", "output_refs"})


class ScientificCapability(Base):
    __tablename__ = "runtime_capabilities"
    name: Mapped[str] = mapped_column(String, primary_key=True)
    module_name: Mapped[str] = mapped_column(String, index=True)
    capability: Mapped[str] = mapped_column(String)
    input_schema: Mapped[dict] = mapped_column(JSON, default=dict)
    output_schema: Mapped[dict] = mapped_column(JSON, default=dict)
    limitations: Mapped[str] = mapped_column(String, default="")
    provenance: Mapped[str] = mapped_column(String, default="")
    uncertainty: Mapped[str] = mapped_column(String, default="unknown")
    invocation_kind: Mapped[str] = mapped_column(String, default="module")
    invocation_ref: Mapped[str] = mapped_column(String)
    created_at: Mapped[float] = mapped_column(Float)


guard_immutable_fields(ScientificCapability, mutable_fields=set())


class RuntimeExecutionRecord(Base):
    __tablename__ = "runtime_execution_records"
    execution_id: Mapped[str] = mapped_column(String, primary_key=True)
    task_id: Mapped[str] = mapped_column(ForeignKey("runtime_scientific_tasks.task_id"), index=True)
    node_id: Mapped[str] = mapped_column(String, index=True)
    capability_name: Mapped[str] = mapped_column(String)
    module_or_tool: Mapped[str] = mapped_column(String)
    input_payload: Mapped[dict] = mapped_column(JSON, default=dict)
    output_payload: Mapped[dict] = mapped_column(JSON, default=dict)
    error: Mapped[dict | None] = mapped_column(JSON, default=None)
    provenance: Mapped[dict] = mapped_column(JSON, default=dict)
    started_at: Mapped[float] = mapped_column(Float)
    ended_at: Mapped[float] = mapped_column(Float)


guard_immutable_fields(RuntimeExecutionRecord, mutable_fields=set())
