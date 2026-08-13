from __future__ import annotations

from typing import Any
from sqlalchemy import select
from sqlalchemy.orm import Session

from harness.ids import new_id, now
from harness.scientific_runtime.models import RuntimeExecutionRecord, RuntimeTaskNode, ScientificCapability, ScientificTask, TASK_STATUSES

DEFAULT_PLAN = (
    ("diagnosis", "engineering_decision", []),
    ("evidence_retrieval", "evidence_intelligence", ["diagnosis"]),
    ("world_model_query", "world_model", ["diagnosis"]),
    ("design_generation", "engineering_decision", ["diagnosis", "evidence_retrieval", "world_model_query"]),
    ("simulation", "virtual_cell", ["design_generation"]),
    ("evaluation", "scientific_evaluation", ["design_generation", "simulation"]),
    ("human_approval", "human_governance", ["evaluation"]),
    ("dbtl_execution", "orchestrator", ["human_approval"]),
)


def create_task(session: Session, *, project_id: str, objective: str, constraints: dict[str, Any], actor_id: str) -> ScientificTask:
    if not objective.strip():
        raise ValueError("objective is required")
    stamp = now()
    task = ScientificTask(task_id=new_id("TASK"), project_id=project_id, objective=objective, constraints=constraints, current_stage="planning", task_status="planning", completed_steps=[], pending_steps=[x[0] for x in DEFAULT_PLAN], module_outputs={}, human_actions=[], execution_history=[{"event": "created", "actor_id": actor_id, "timestamp": stamp}], created_at=stamp, updated_at=stamp)
    session.add(task); session.flush()
    ids: dict[str, str] = {}
    for key, module, _deps in DEFAULT_PLAN:
        ids[key] = new_id("NODE")
    for key, module, deps in DEFAULT_PLAN:
        session.add(RuntimeTaskNode(node_id=ids[key], task_id=task.task_id, capability_name=key, module_name=module, dependencies=[ids[d] for d in deps], status="ready" if not deps else "pending", requires_human_approval=key == "human_approval", created_at=stamp))
    task.task_status = "executing"; task.current_stage = "diagnosis"; session.flush()
    return task


def task_view(session: Session, task_id: str) -> dict[str, Any] | None:
    task = session.get(ScientificTask, task_id)
    if not task: return None
    nodes = session.execute(select(RuntimeTaskNode).where(RuntimeTaskNode.task_id == task_id)).scalars().all()
    executions = session.execute(select(RuntimeExecutionRecord).where(RuntimeExecutionRecord.task_id == task_id).order_by(RuntimeExecutionRecord.started_at)).scalars().all()
    return {"task": {c.name: getattr(task, c.name) for c in task.__table__.columns}, "graph": [{c.name: getattr(n, c.name) for c in n.__table__.columns} for n in nodes], "executions": [{c.name: getattr(e, c.name) for c in e.__table__.columns} for e in executions]}


def register_capability(session: Session, **data: Any) -> ScientificCapability:
    if session.get(ScientificCapability, data["name"]): raise ValueError("capability already registered")
    row = ScientificCapability(**data, created_at=now()); session.add(row); session.flush(); return row


def complete_node(session: Session, *, task_id: str, node_id: str, output_refs: dict[str, Any], provenance: dict[str, Any], actor_id: str) -> ScientificTask:
    task, node = session.get(ScientificTask, task_id), session.get(RuntimeTaskNode, node_id)
    if not task or not node or node.task_id != task_id: raise ValueError("task or node not found")
    if node.requires_human_approval: raise ValueError("human approval node must use record_human_action")
    if node.status not in ("ready", "running", "waiting"): raise ValueError(f"node is not executable: {node.status}")
    stamp = now(); node.status = "completed"; node.output_refs = output_refs
    rec = RuntimeExecutionRecord(execution_id=new_id("EXEC"), task_id=task_id, node_id=node_id, capability_name=node.capability_name, module_or_tool=node.module_name, input_payload=node.input_refs, output_payload=output_refs, provenance=provenance, started_at=stamp, ended_at=stamp)
    session.add(rec)
    task.completed_steps = [*task.completed_steps, node.capability_name]; task.pending_steps = [x for x in task.pending_steps if x != node.capability_name]; task.module_outputs = {**task.module_outputs, node.module_name: output_refs}; task.execution_history = [*task.execution_history, {"execution_id": rec.execution_id, "node_id": node_id, "actor_id": actor_id, "timestamp": stamp}]
    nodes = session.execute(select(RuntimeTaskNode).where(RuntimeTaskNode.task_id == task_id)).scalars().all()
    completed = {n.node_id for n in nodes if n.status == "completed"}
    for candidate in nodes:
        if candidate.status == "pending" and all(d in completed for d in candidate.dependencies): candidate.status = "ready"
    ready = next((n for n in nodes if n.status == "ready"), None)
    task.current_stage = ready.capability_name if ready else node.capability_name; task.task_status = "human_review" if ready and ready.requires_human_approval else ("completed" if not task.pending_steps else "executing"); task.updated_at = stamp
    session.flush(); return task


def record_failure(session: Session, *, task_id: str, node_id: str, classification: str, message: str, retryable: bool, actor_id: str) -> ScientificTask:
    task, node = session.get(ScientificTask, task_id), session.get(RuntimeTaskNode, node_id)
    if not task or not node: raise ValueError("task or node not found")
    stamp = now(); node.status = "ready" if retryable else "failed"; task.failure = {"node_id": node_id, "classification": classification, "message": message, "retryable": retryable, "timestamp": stamp}; task.task_status = "executing" if retryable else "human_review"; task.human_actions = task.human_actions if retryable else [*task.human_actions, {"type": "failure_escalation", "node_id": node_id, "status": "pending"}]; task.updated_at = stamp; session.flush(); return task


def record_human_action(session: Session, *, task_id: str, decision: str, actor_id: str, reason: str = "") -> ScientificTask:
    if decision not in ("approve", "reject", "request_modification", "override"): raise ValueError("invalid human decision")
    task = session.get(ScientificTask, task_id)
    if not task: raise ValueError("task not found")
    stamp = now(); task.human_actions = [*task.human_actions, {"decision": decision, "actor_id": actor_id, "reason": reason, "timestamp": stamp}]
    if decision == "reject": task.task_status = "failed"; task.failure = {"classification": "human_rejection", "message": reason, "retryable": False}
    elif decision == "request_modification": task.task_status = "planning"; task.current_stage = "replanning"
    else:
        nodes = session.execute(select(RuntimeTaskNode).where(RuntimeTaskNode.task_id == task_id, RuntimeTaskNode.requires_human_approval.is_(True))).scalars().all()
        for node in nodes:
            if node.status in ("ready", "waiting"): node.status = "completed"
        all_nodes = session.execute(select(RuntimeTaskNode).where(RuntimeTaskNode.task_id == task_id)).scalars().all()
        completed_ids = {node.node_id for node in all_nodes if node.status == "completed"}
        for node in all_nodes:
            if node.status == "pending" and all(dep in completed_ids for dep in node.dependencies):
                node.status = "ready"
        task.completed_steps = [*task.completed_steps, "human_approval"]; task.pending_steps = [x for x in task.pending_steps if x != "human_approval"]; task.task_status = "executing"; task.current_stage = "dbtl_execution"
    task.updated_at = stamp; session.flush(); return task
