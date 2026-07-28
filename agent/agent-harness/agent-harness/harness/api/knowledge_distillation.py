"""Biological Knowledge Distillation module API routes.

Wraps the vendored 13-step pipeline (harness/knowledge_distillation/) -
task contract, source validation, document parsing, extraction-scope
selection, concept/mechanism extraction (Opus-routed, see opus_extractor.py),
engineering-principle distillation, decision-rule generation, design-
pattern/validation-strategy/failure-pattern extraction, evidence-binding
audit, cross-source fusion, paper-case linking, quality governance and
knowledge-graph/frontend adaptation. Runs are async (thread-pool backed);
submit, then poll the combined status+result endpoint - same shape as
`harness/api/paper_extraction.py` on purpose, so a frontend page can reuse
the same polling pattern.

Independent of the project ledger DB (harness/db.py): the module keeps its
own file-based checkpoint/artifact store under
harness/knowledge_distillation/vendor/biological_knowledge_distillation/storage/,
matching the paper-extraction precedent.
"""
from __future__ import annotations

import base64
from typing import Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from harness.knowledge_distillation import service

router = APIRouter(prefix="/api/knowledge-distillation", tags=["knowledge-distillation"])


class SourceBody(BaseModel):
    text: str | None = None
    file_path: str | None = None
    title: str = ""
    authors: list[str] = Field(default_factory=list)
    publisher: str = ""
    publication_year: int | None = None
    isbn: list[str] = Field(default_factory=list)
    doi: str = ""
    edition: str = ""
    chapter: str = ""
    page_range: str = ""
    source_type: str = ""


class RunRequestBody(BaseModel):
    project_id: str | None = None
    user_request: str
    sources: list[SourceBody] = Field(default_factory=list)
    target_domain: list[str] = Field(default_factory=list)
    target_organism: list[str] = Field(default_factory=list)
    target_strain: list[str] = Field(default_factory=list)
    target_engineering_goal: list[str] = Field(default_factory=list)
    requested_output_level: list[str] = Field(default_factory=list)
    source_languages: list[str] = Field(default_factory=list)
    output_languages: list[str] = Field(default_factory=list)
    quality_requirement: str = ""
    requires_cross_source_fusion: bool | None = None
    requires_frontend_adapter: bool = True
    paper_case_artifacts: list[dict[str, Any]] = Field(default_factory=list)
    automatic: bool = True
    human_review: bool = True


class UploadBody(BaseModel):
    filename: str
    content_base64: str


@router.post("/uploads")
def upload_source(body: UploadBody) -> dict:
    # base64-in-JSON, not multipart (harness/api/paper_extraction.py precedent).
    try:
        data = base64.b64decode(body.content_base64)
    except Exception as exc:
        raise HTTPException(400, f"content_base64 is not valid base64: {exc}") from exc
    if not data:
        raise HTTPException(422, "uploaded file is empty")
    try:
        path = service.save_upload(body.filename, data)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    return {"path": path, "filename": body.filename}


@router.post("/tasks", status_code=202)
def submit_task(body: RunRequestBody) -> dict:
    try:
        return service.submit_run(body.model_dump())
    except (ValueError, KeyError) as exc:  # invalid request shape against the module's own input schema
        raise HTTPException(400, str(exc)) from exc


@router.get("/tasks")
def list_tasks(project_id: str | None = Query(default=None)) -> dict:
    return {"tasks": service.list_tasks(project_id=project_id)}


@router.get("/tasks/{task_id}")
def get_task(task_id: str) -> dict[str, Any]:
    """Combined status+result poll target, mirroring
    `harness/api/paper_extraction.py::get_task`: `result` stays null while
    running, and `step_states` is surfaced at the top level (read from the
    on-disk checkpoint) so a client can show live per-step progress instead
    of an undifferentiated spinner."""
    try:
        status = service.get_status(task_id)
    except KeyError:
        raise HTTPException(404, "task not found")
    result = service.get_result(task_id)
    step_states = result["step_states"] if result else service.get_live_step_states(task_id)
    return {**status, "result": result, "step_states": step_states}
