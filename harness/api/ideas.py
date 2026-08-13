"""Idea Capture API routes ("sudden inspiration" entry point). Every route
calls the same `harness/ideas/service.py` functions a unit test would; no
business logic lives here.
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from harness.api.deps import get_db_session
from harness.ideas import matching as ideas_matching
from harness.ideas import service as ideas_service
from harness.ideas.models import ProjectIdea

router = APIRouter(tags=["ideas"])


def _idea_dict(i: ProjectIdea) -> dict[str, Any]:
    return {
        "idea_id": i.idea_id, "project_id": i.project_id, "actor_id": i.actor_id, "free_text": i.free_text,
        "target_gene": i.target_gene, "modification_type": i.modification_type, "rationale": i.rationale,
        "status": i.status, "linked_design_project_id": i.linked_design_project_id, "created_at": i.created_at,
    }


class CaptureIdeaBody(BaseModel):
    actor_id: str
    free_text: str
    target_gene: str | None = None
    modification_type: str | None = None
    rationale: str | None = None


@router.post("/api/projects/{project_id}/ideas")
def capture_idea(project_id: str, body: CaptureIdeaBody, session: Session = Depends(get_db_session)) -> dict:
    try:
        idea = ideas_service.capture_idea(session, project_id=project_id, **body.model_dump())
    except ValueError as e:
        raise HTTPException(422, str(e))
    return _idea_dict(idea)


def _target_texts_for_design_project(session: Session, design_project_id: str) -> list[str]:
    """Originating diagnosis hypothesis statements for a design project -
    used only to rank idea relevance (`ideas.matching`), never to
    auto-select/auto-link anything."""
    from harness.diagnosis.models import DiagnosisDecision
    from harness.engineering_design.models import EngineeringDesignProject
    from harness.learning.models import HypothesisVersion

    proj = session.get(EngineeringDesignProject, design_project_id)
    if proj is None or not proj.diagnosis_decision_id:
        return []
    decision = session.get(DiagnosisDecision, proj.diagnosis_decision_id)
    if decision is None or not decision.leading_hypothesis_ids:
        return []
    hyps = session.execute(
        select(HypothesisVersion).where(HypothesisVersion.hypothesis_version_id.in_(decision.leading_hypothesis_ids))
    ).scalars().all()
    return [h.statement for h in hyps if h.statement]


@router.get("/api/projects/{project_id}/ideas")
def list_ideas(project_id: str, rank_for_design_project_id: str | None = None, session: Session = Depends(get_db_session)) -> dict:
    ideas = ideas_service.list_ideas(session, project_id)
    recommended_idea_id = None
    if rank_for_design_project_id:
        target_texts = _target_texts_for_design_project(session, rank_for_design_project_id)
        if target_texts:
            ideas = ideas_matching.rank_ideas_by_relevance(ideas, target_texts)
            if ideas and ideas_matching.relevance_score(ideas[0], target_texts) > 0:
                recommended_idea_id = ideas[0].idea_id
    return {"ideas": [_idea_dict(i) for i in ideas], "recommended_idea_id": recommended_idea_id}


class LinkIdeaBody(BaseModel):
    design_project_id: str
    actor_id: str


@router.post("/api/ideas/{idea_id}/link-to-design")
def link_idea_to_design(idea_id: str, body: LinkIdeaBody, session: Session = Depends(get_db_session)) -> dict:
    try:
        idea = ideas_service.link_idea_to_design(session, idea_id=idea_id, design_project_id=body.design_project_id, actor_id=body.actor_id)
    except ValueError as e:
        raise HTTPException(404, str(e))
    return _idea_dict(idea)


class DismissIdeaBody(BaseModel):
    actor_id: str


@router.post("/api/ideas/{idea_id}/dismiss")
def dismiss_idea(idea_id: str, body: DismissIdeaBody, session: Session = Depends(get_db_session)) -> dict:
    try:
        idea = ideas_service.dismiss_idea(session, idea_id=idea_id, actor_id=body.actor_id)
    except ValueError as e:
        raise HTTPException(404, str(e))
    return _idea_dict(idea)
