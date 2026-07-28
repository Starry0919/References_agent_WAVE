"""Idea capture service: persist a user's own free-text idea, list a
project's ideas, and (honestly) link one to a real design project - never
fabricates a simulation/prediction result. Turning an idea into an actual
prediction still has to go through the real pipeline (strategy -> portfolio
-> candidate -> bridge -> `POST /api/virtual-cell/simulations`); this
module only records the user's intent and the hand-off, same "no
unsupported synthesis" discipline as `harness/diagnosis/evidence.py`.
"""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from harness.ideas.models import ProjectIdea
from harness.ids import new_id, now
from harness.memory import event_types as et
from harness.memory.event_store import append_event, snapshot

IDEA_SNAPSHOT_FIELDS = (
    "idea_id", "project_id", "actor_id", "free_text", "target_gene", "modification_type",
    "rationale", "status", "linked_design_project_id", "created_at",
)


def capture_idea(
    session: Session,
    *,
    project_id: str,
    actor_id: str,
    free_text: str,
    target_gene: str | None = None,
    modification_type: str | None = None,
    rationale: str | None = None,
) -> ProjectIdea:
    from harness.projects.models import Project

    if session.get(Project, project_id) is None:
        raise ValueError(f"no such project: {project_id}")
    if not free_text or not free_text.strip():
        raise ValueError("free_text must not be empty")
    idea = ProjectIdea(
        idea_id=new_id("IDEA"), project_id=project_id, actor_id=actor_id, free_text=free_text.strip(),
        target_gene=target_gene, modification_type=modification_type, rationale=rationale,
        status="captured", created_at=now(),
    )
    session.add(idea)
    session.flush()
    append_event(
        session, project_id=project_id, event_type=et.PROJECT_IDEA_CAPTURED, entity_type="ProjectIdea",
        entity_id=idea.idea_id, payload=snapshot(idea, IDEA_SNAPSHOT_FIELDS), actor_type="human", actor_id=actor_id,
    )
    return idea


def list_ideas(session: Session, project_id: str) -> list[ProjectIdea]:
    return list(
        session.execute(
            select(ProjectIdea).where(ProjectIdea.project_id == project_id).order_by(ProjectIdea.created_at.desc())
        ).scalars()
    )


def get_idea(session: Session, idea_id: str) -> ProjectIdea | None:
    return session.get(ProjectIdea, idea_id)


def link_idea_to_design(session: Session, *, idea_id: str, design_project_id: str, actor_id: str) -> ProjectIdea:
    """Records that a user's idea is being carried into a real
    EngineeringDesignProject - it does not create a candidate or run any
    simulation itself (no manual-candidate-creation endpoint exists; real
    candidates only come from strategy/portfolio generation). This is
    honest hand-off bookkeeping, not a prediction."""
    idea = session.get(ProjectIdea, idea_id)
    if idea is None:
        raise ValueError(f"no such idea: {idea_id}")
    idea.status = "linked_to_design"
    idea.linked_design_project_id = design_project_id
    session.flush()
    append_event(
        session, project_id=idea.project_id, event_type=et.PROJECT_IDEA_LINKED_TO_DESIGN, entity_type="ProjectIdea",
        entity_id=idea.idea_id, payload=snapshot(idea, IDEA_SNAPSHOT_FIELDS), actor_type="human", actor_id=actor_id,
    )
    return idea


def dismiss_idea(session: Session, *, idea_id: str, actor_id: str) -> ProjectIdea:
    idea = session.get(ProjectIdea, idea_id)
    if idea is None:
        raise ValueError(f"no such idea: {idea_id}")
    idea.status = "dismissed"
    session.flush()
    append_event(
        session, project_id=idea.project_id, event_type=et.PROJECT_IDEA_DISMISSED, entity_type="ProjectIdea",
        entity_id=idea.idea_id, payload=snapshot(idea, IDEA_SNAPSHOT_FIELDS), actor_type="human", actor_id=actor_id,
    )
    return idea
