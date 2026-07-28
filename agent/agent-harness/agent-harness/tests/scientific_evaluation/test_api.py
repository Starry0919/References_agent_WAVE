"""API-level smoke tests (doc05 §10.1) - the same service calls, exercised
through the real FastAPI app + `get_db_session` dependency (repointed at
the isolated test DB), not a re-implementation.
"""
from __future__ import annotations

from fastapi.testclient import TestClient

from harness import db
from harness.api import deps
from harness.db import session_scope
from harness.engineering_design.evaluation_service import evaluate_portfolio
from harness.server import create_app

from tests.engineering_design.fixtures import handoff_through_portfolio


def _client() -> TestClient:
    app = create_app()
    return TestClient(app)


def test_start_evaluation_and_read_back_via_api(isolated_db):
    with session_scope() as session:
        proj, portfolio, candidates = handoff_through_portfolio(session)
        evaluate_portfolio(session, portfolio_id=portfolio.portfolio_id, actor_id="system")
        portfolio_id = portfolio.portfolio_id

    client = _client()
    resp = client.post("/api/scientific-evaluation/evaluations", json={"portfolio_id": portfolio_id, "actor_id": "pi"})
    assert resp.status_code == 200, resp.text
    body = resp.json()
    evaluation_id = body["case"]["evaluation_id"]
    assert body["case"]["status"] in ("revision_required", "awaiting_human_decision")
    assert body["meta_decision"]["recommended_action"]

    resp2 = client.get(f"/api/scientific-evaluation/evaluations/{evaluation_id}")
    assert resp2.status_code == 200
    assert resp2.json()["evaluation_id"] == evaluation_id

    resp3 = client.get(f"/api/scientific-evaluation/evaluations/{evaluation_id}/evidence-assessments")
    assert resp3.status_code == 200
    assert "assessments" in resp3.json()

    resp4 = client.get(f"/api/scientific-evaluation/evaluations/{evaluation_id}/reviews")
    assert resp4.status_code == 200
    assert resp4.json()["reviews"]

    resp5 = client.get(f"/api/scientific-evaluation/evaluations/{evaluation_id}/audit-trail")
    assert resp5.status_code == 200
    assert resp5.json()["transitions"]


def test_human_decision_requires_distinct_approver_via_api(isolated_db):
    with session_scope() as session:
        proj, portfolio, candidates = handoff_through_portfolio(session)
        evaluate_portfolio(session, portfolio_id=portfolio.portfolio_id, actor_id="system")
        portfolio_id = portfolio.portfolio_id
        proposer = candidates[0].proposed_by

    client = _client()
    started = client.post("/api/scientific-evaluation/evaluations", json={"portfolio_id": portfolio_id, "actor_id": "pi"}).json()
    evaluation_id = started["case"]["evaluation_id"]

    bad = client.post(
        f"/api/scientific-evaluation/evaluations/{evaluation_id}/human-decision",
        json={"decision": "hold", "approver_id": proposer, "selected_candidates": [started["candidates"][0]]},
    )
    assert bad.status_code == 409

    ok = client.post(
        f"/api/scientific-evaluation/evaluations/{evaluation_id}/human-decision",
        json={"decision": "hold", "approver_id": "someone_else"},
    )
    assert ok.status_code == 200
    assert ok.json()["case_status"] == "held"
