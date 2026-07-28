"""The append-only `ProjectEvent` ledger (doc 9.1): the single source of
truth every other view must be reconstructable from. `append_event` is the
one primitive every mutating service function in this codebase calls;
`replay_project` is the generic reducer that reconstructs project state
purely from these rows, independent of any live table - proving the
ledger is real, not decorative (design-review requirement: a test builds a
project through the normal service path, then asserts replay-only
reconstruction matches the live tables exactly).
"""
from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from harness.ids import new_id, now
from harness.memory import event_types as et
from harness.projects.models import ProjectEvent


def append_event(
    session: Session,
    *,
    project_id: str,
    event_type: str,
    entity_type: str,
    entity_id: str,
    payload: dict[str, Any],
    actor_type: str,
    actor_id: str,
    causation_id: str | None = None,
    correlation_id: str | None = None,
    workflow_run_id: str | None = None,
) -> ProjectEvent:
    """Append one immutable event. Callers pass a FULL snapshot of the
    entity as `payload` (not a diff) - this is what makes `replay_project`
    a uniform reduction instead of needing a bespoke applier per event
    type."""
    event = ProjectEvent(
        event_id=new_id("EVT"),
        project_id=project_id,
        event_type=event_type,
        entity_type=entity_type,
        entity_id=entity_id,
        payload=payload,
        actor_type=actor_type,
        actor_id=actor_id,
        causation_id=causation_id,
        correlation_id=correlation_id,
        workflow_run_id=workflow_run_id,
        timestamp=now(),
    )
    session.add(event)
    session.flush()
    return event


def snapshot(row: Any, fields: tuple[str, ...]) -> dict[str, Any]:
    """Extract a plain-dict snapshot of the named attributes off an ORM
    row - the standard way every service module builds an
    `append_event(..., payload=...)` argument, so payloads stay a genuine
    full snapshot rather than an ad hoc partial dict."""
    return {f: getattr(row, f) for f in fields}


def project_events(session: Session, project_id: str) -> list[ProjectEvent]:
    return list(
        session.execute(
            select(ProjectEvent).where(ProjectEvent.project_id == project_id).order_by(ProjectEvent.seq)
        ).scalars()
    )


def replay_project(session: Session, project_id: str) -> dict[str, Any]:
    """Reconstruct project state purely from `ProjectEvent` rows, ignoring
    every live table's current content.

    Returns:
        {"entities": {entity_type: {entity_id: latest_payload}},
         "pointers": {...project-level "current X" fields...}}

    `entities` is a uniform reduction (last snapshot wins per entity_id) -
    valid for every entity type this codebase emits full-snapshot events
    for. `pointers` handles the smaller set of derived project-level facts
    (current design version, lifecycle stage, status) that aren't
    "the latest snapshot of one entity" but a computed fact about the event
    sequence.
    """
    events = project_events(session, project_id)
    entities: dict[str, dict[str, dict]] = {}
    pointers: dict[str, Any] = {}

    for e in events:
        entities.setdefault(e.entity_type, {})[e.entity_id] = e.payload

        if e.event_type == et.PROJECT_CREATED:
            pointers["project_id"] = e.payload.get("project_id")
            pointers["name"] = e.payload.get("name")
            pointers["status"] = "active"
            pointers["lifecycle_stage"] = "PROJECT_CONTEXT_READY"
            pointers["current_design_branch"] = e.payload.get("current_design_branch", "main")
        elif e.event_type == et.PROJECT_STATUS_CHANGED:
            pointers["status"] = e.payload.get("status")
        elif e.event_type == et.CYCLE_STATE_CHANGED:
            pointers["lifecycle_stage"] = e.payload.get("current_state")
            pointers["active_cycle_state_id"] = e.entity_id
        elif e.event_type == et.DESIGN_APPROVED:
            pointers["current_design_version_id"] = e.entity_id

    return {"entities": entities, "pointers": pointers}
