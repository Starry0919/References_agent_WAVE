"""HTTP surface smoke test (prompt §8.1) - exercises the real orchestrator
service layer through FastAPI, not a mocked client, matching every other
Problem's `test_api.py` convention in this repo.
"""
from __future__ import annotations

from fastapi.testclient import TestClient

from harness.projects import service as proj_svc
from harness.server import create_app


def _client() -> TestClient:
    return TestClient(create_app())


def test_create_and_read_run_via_http():
    with _client() as client:
        from harness import db

        with db.session_scope() as s:
            proj = proj_svc.create_project(s, name="HTTP smoke", host_definition={"species": "E. coli"}, target_product="L-tryptophan", actor_id="pi")
            project_id = proj.project_id

        r = client.post("/api/orchestrator/runs", json={"project_id": project_id, "actor_id": "pi", "target_product": "L-tryptophan", "host": "E. coli K-12"})
        assert r.status_code == 200, r.text
        body = r.json()
        assert body["current_phase"] == "DIAGNOSIS"
        run_id = body["workflow_run_id"]

        r2 = client.get(f"/api/orchestrator/runs/{run_id}")
        assert r2.status_code == 200
        assert r2.json()["workflow_run_id"] == run_id

        r3 = client.get(f"/api/orchestrator/runs/{run_id}/audit-trail")
        assert r3.status_code == 200
        assert any(t["to_phase"] == "DIAGNOSIS" for t in r3.json()["transitions"])

        r4 = client.get(f"/api/orchestrator/runs/{run_id}/reconcile")
        assert r4.status_code == 200
        assert r4.json()["ledger_matches_materialized_state"] is True

        # stale version over HTTP -> 409, not 500 or a silent overwrite
        r5 = client.post(
            f"/api/orchestrator/runs/{run_id}/diagnosis",
            json={"expected_version": 999, "actor_id": "agent", "request": {}, "context": {}},
        )
        assert r5.status_code == 409

        r6 = client.get("/api/orchestrator/runs/RUN-does-not-exist")
        assert r6.status_code == 404
