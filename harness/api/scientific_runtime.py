from __future__ import annotations
from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session
from harness.api.deps import get_db_session
from harness.scientific_runtime.models import ScientificCapability, ScientificTask
from harness.scientific_runtime.service import complete_node, create_task, record_failure, record_human_action, register_capability, task_view

router = APIRouter(prefix="/api/scientific-runtime", tags=["scientific-runtime"])

class CreateTaskBody(BaseModel):
    project_id: str; objective: str = Field(min_length=1); constraints: dict[str, Any] = {}; actor_id: str = "human"
class CompleteNodeBody(BaseModel):
    output_refs: dict[str, Any] = {}; provenance: dict[str, Any] = {}; actor_id: str = "system"
class FailureBody(BaseModel):
    classification: str; message: str; retryable: bool = False; actor_id: str = "system"
class HumanActionBody(BaseModel):
    decision: str; actor_id: str; reason: str = ""
class CapabilityBody(BaseModel):
    name: str; module_name: str; capability: str; input_schema: dict[str, Any] = {}; output_schema: dict[str, Any] = {}; limitations: str = ""; provenance: str = ""; uncertainty: str = "unknown"; invocation_kind: str = "module"; invocation_ref: str

def _task_dict(task: ScientificTask) -> dict[str, Any]: return {c.name: getattr(task, c.name) for c in task.__table__.columns}

@router.post("/tasks")
def create(body: CreateTaskBody, session: Session = Depends(get_db_session)):
    try: return _task_dict(create_task(session, **body.model_dump()))
    except ValueError as exc: raise HTTPException(422, str(exc)) from exc

@router.get("/tasks")
def tasks(project_id: str, session: Session = Depends(get_db_session)):
    rows = session.execute(select(ScientificTask).where(ScientificTask.project_id == project_id).order_by(ScientificTask.updated_at.desc())).scalars().all()
    return {"tasks": [_task_dict(row) for row in rows]}

@router.get("/tasks/{task_id}")
def get(task_id: str, session: Session = Depends(get_db_session)):
    result = task_view(session, task_id)
    if result is None: raise HTTPException(404, "task not found")
    return result

@router.post("/tasks/{task_id}/nodes/{node_id}/complete")
def complete(task_id: str, node_id: str, body: CompleteNodeBody, session: Session = Depends(get_db_session)):
    try: return _task_dict(complete_node(session, task_id=task_id, node_id=node_id, **body.model_dump()))
    except ValueError as exc: raise HTTPException(422, str(exc)) from exc

@router.post("/tasks/{task_id}/nodes/{node_id}/failure")
def fail(task_id: str, node_id: str, body: FailureBody, session: Session = Depends(get_db_session)):
    try: return _task_dict(record_failure(session, task_id=task_id, node_id=node_id, **body.model_dump()))
    except ValueError as exc: raise HTTPException(422, str(exc)) from exc

@router.post("/tasks/{task_id}/human-action")
def human_action(task_id: str, body: HumanActionBody, session: Session = Depends(get_db_session)):
    try: return _task_dict(record_human_action(session, task_id=task_id, **body.model_dump()))
    except ValueError as exc: raise HTTPException(422, str(exc)) from exc

@router.post("/capabilities")
def capability(body: CapabilityBody, session: Session = Depends(get_db_session)):
    try:
        row = register_capability(session, **body.model_dump()); return {c.name: getattr(row, c.name) for c in row.__table__.columns}
    except ValueError as exc: raise HTTPException(409, str(exc)) from exc

@router.get("/capabilities")
def capabilities(module_name: str | None = None, session: Session = Depends(get_db_session)):
    stmt = select(ScientificCapability)
    if module_name: stmt = stmt.where(ScientificCapability.module_name == module_name)
    rows = session.execute(stmt).scalars().all(); return {"capabilities": [{c.name: getattr(row, c.name) for c in row.__table__.columns} for row in rows]}
