"""HTTP surface smoke test for the Golden Set API (prompt §8.1)."""
from __future__ import annotations

from fastapi.testclient import TestClient

from harness.server import create_app


def _client() -> TestClient:
    return TestClient(create_app())


def test_seed_run_score_and_acceptance_report_over_http():
    with _client() as client:
        r = client.post("/api/golden-set/seed")
        assert r.status_code == 200
        assert len(r.json()["cases"]) == 20

        r2 = client.get("/api/golden-set/cases/GC-012/review-status")
        assert r2.status_code == 200
        assert r2.json()["review_status"] == "pending_expert_review"

        r3 = client.post("/api/golden-set/cases/GC-012/run", json={})
        assert r3.status_code == 200
        assert r3.json()["automated_metrics"]["unsafe_design_blocked"] is True
        run_id = r3.json()["evaluation_run_id"]

        r4 = client.get(f"/api/golden-set/runs/{run_id}/score")
        assert r4.status_code == 200
        assert r4.json()["answer_key_review_status"] == "pending_expert_review"

        r5 = client.post("/api/golden-set/acceptance-report", json={"evaluation_run_ids": [run_id]})
        assert r5.status_code == 200
        assert r5.json()["formal_validation_eligible"] is False

        r6 = client.get("/api/golden-set/cases/GC-does-not-exist/review-status")
        assert r6.status_code == 404
