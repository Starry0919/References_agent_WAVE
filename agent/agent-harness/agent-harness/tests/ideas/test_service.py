"""Idea Capture service tests: the user's own text is persisted and kept
distinct from knowledge-base content, every mutation lands in the same
ProjectEvent ledger, and no simulation/prediction is ever fabricated -
`link_idea_to_design` only records a hand-off, it returns no result."""
from __future__ import annotations

import pytest

from harness import db
from harness.ideas import service
from harness.ideas.models import ProjectIdea
from harness.memory import event_types as et
from harness.memory.event_store import project_events
from harness.projects import service as proj_svc


def _make_project(session, *, name: str = "Idea capture test project") -> str:
    proj = proj_svc.create_project(
        session, name=name, host_definition={"species": "E. coli", "strain": "K-12"},
        target_product="L-tryptophan", actor_id="alice",
    )
    return proj.project_id


def test_capture_idea_persists_and_defaults_to_captured():
    with db.session_scope() as s:
        project_id = _make_project(s)
        idea = service.capture_idea(
            s, project_id=project_id, actor_id="alice", free_text="  knock out pfkA to redirect flux toward trp  ",
            target_gene="pfkA", modification_type="knockout", rationale="reduce competing flux",
        )
        assert idea.status == "captured"
        assert idea.free_text == "knock out pfkA to redirect flux toward trp"  # stripped, not fabricated/altered otherwise
        assert idea.linked_design_project_id is None

        events = project_events(s, project_id)
        assert any(e.event_type == et.PROJECT_IDEA_CAPTURED and e.entity_id == idea.idea_id for e in events)


def test_capture_idea_rejects_empty_text():
    with db.session_scope() as s:
        project_id = _make_project(s)
        with pytest.raises(ValueError):
            service.capture_idea(s, project_id=project_id, actor_id="alice", free_text="   ")


def test_list_ideas_scoped_to_project_newest_first():
    with db.session_scope() as s:
        project_id = _make_project(s, name="Project A")
        other_project_id = _make_project(s, name="Project B")
        service.capture_idea(s, project_id=project_id, actor_id="alice", free_text="idea one")
        service.capture_idea(s, project_id=project_id, actor_id="alice", free_text="idea two")
        service.capture_idea(s, project_id=other_project_id, actor_id="bob", free_text="unrelated project idea")

        rows = service.list_ideas(s, project_id)
        assert [r.free_text for r in rows] == ["idea two", "idea one"]


def test_link_idea_to_design_records_handoff_without_fabricating_a_result():
    with db.session_scope() as s:
        project_id = _make_project(s)
        idea = service.capture_idea(s, project_id=project_id, actor_id="alice", free_text="try overexpressing tktA")
        linked = service.link_idea_to_design(s, idea_id=idea.idea_id, design_project_id="EDP-1", actor_id="alice")

        assert linked.status == "linked_to_design"
        assert linked.linked_design_project_id == "EDP-1"
        events = project_events(s, project_id)
        assert any(e.event_type == et.PROJECT_IDEA_LINKED_TO_DESIGN and e.entity_id == idea.idea_id for e in events)


def test_link_idea_to_design_unknown_idea_raises():
    with db.session_scope() as s:
        with pytest.raises(ValueError):
            service.link_idea_to_design(s, idea_id="IDEA-does-not-exist", design_project_id="EDP-1", actor_id="alice")


def test_dismiss_idea():
    with db.session_scope() as s:
        project_id = _make_project(s)
        idea = service.capture_idea(s, project_id=project_id, actor_id="alice", free_text="a discarded idea")
        dismissed = service.dismiss_idea(s, idea_id=idea.idea_id, actor_id="alice")
        assert dismissed.status == "dismissed"


def test_original_idea_text_is_immutable_after_capture():
    """Only status/linked_design_project_id may change post-capture - the
    user's own words are never silently rewritten (guard_immutable_fields,
    same discipline as `KnowledgeClaim`)."""
    from harness.db import ImmutableFieldError

    with db.session_scope() as s:
        project_id = _make_project(s)
        idea = service.capture_idea(s, project_id=project_id, actor_id="alice", free_text="original wording")
        idea_id = idea.idea_id

    with pytest.raises(ImmutableFieldError):
        with db.session_scope() as s:
            row = s.get(ProjectIdea, idea_id)
            row.free_text = "rewritten wording"
