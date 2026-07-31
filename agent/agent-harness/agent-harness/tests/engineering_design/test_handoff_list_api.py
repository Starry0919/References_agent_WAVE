"""`GET /api/engineering-design/projects/{design_project_id}/handoff` -
lets a client that lost the `handoff_id` returned by the original
`POST /handoff` call (e.g. after a page refresh) look it back up before
calling `POST /projects/{id}/strategies`, which requires it."""
from __future__ import annotations

from fastapi.testclient import TestClient

from harness import db
from harness.server import create_app
from tests.engineering_design.fixtures import handoff_through_portfolio


def _client() -> TestClient:
    return TestClient(create_app())


def test_list_handoffs_returns_the_record_created_at_handoff_time():
    with db.session_scope() as s:
        proj, _portfolio, _candidates = handoff_through_portfolio(s)
        design_project_id = proj.design_project_id
        diagnosis_session_id = proj.diagnosis_session_id

    with _client() as client:
        r = client.get(f"/api/engineering-design/projects/{design_project_id}/handoff")
        assert r.status_code == 200
        handoffs = r.json()["handoffs"]
        assert len(handoffs) == 1
        assert handoffs[0]["design_project_id"] == design_project_id
        assert handoffs[0]["diagnosis_session_id"] == diagnosis_session_id
        assert handoffs[0]["handoff_id"]


def test_list_handoffs_for_unknown_project_is_empty_not_404():
    with _client() as client:
        r = client.get("/api/engineering-design/projects/does-not-exist/handoff")
        assert r.status_code == 200
        assert r.json()["handoffs"] == []
