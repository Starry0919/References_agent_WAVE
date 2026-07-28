"""API-level regression tests via `fastapi.testclient.TestClient` for the
Bottleneck Diagnosis Loop routes."""
from __future__ import annotations

from fastapi.testclient import TestClient

from harness.server import create_app


def _client() -> TestClient:
    return TestClient(create_app())


def test_model_capabilities_endpoint_reports_real_and_unavailable_adapters():
    with _client() as client:
        r = client.get("/api/diagnosis/model-capabilities")
        assert r.status_code == 200
        body = r.json()
        assert body["gem_fba"]["available"] is True
        assert body["vecoli"]["available"] is False


def test_create_session_and_illegal_action_returns_409():
    with _client() as client:
        p = client.post("/api/projects", json={"name": "t", "target_product": "trp", "actor_id": "pi"}).json()
        sess = client.post("/api/diagnosis/sessions", json={"project_id": p["project_id"], "actor_id": "pi"}).json()
        assert sess["status"] == "intake"

        resp = client.post(
            f"/api/diagnosis/sessions/{sess['diagnosis_session_id']}/action/mark_hypotheses_ranked",
            json={"actor_id": "agent", "kwargs": {}},
        )
        assert resp.status_code == 409  # intake -> hypotheses_ranked is illegal


def test_report_endpoint_returns_structured_sections():
    with _client() as client:
        p = client.post("/api/projects", json={"name": "t", "target_product": "trp", "actor_id": "pi"}).json()
        sess = client.post("/api/diagnosis/sessions", json={"project_id": p["project_id"], "actor_id": "pi"}).json()
        r = client.get(f"/api/diagnosis/sessions/{sess['diagnosis_session_id']}/report")
        assert r.status_code == 200
        titles = [s["title"] for s in r.json()["sections"]]
        assert "Executive Summary" in titles
        assert "Alternatives Not Excluded" in titles


def test_run_model_endpoint_executes_real_fba():
    with _client() as client:
        p = client.post("/api/projects", json={"name": "t", "target_product": "trp", "actor_id": "pi"}).json()
        sess = client.post("/api/diagnosis/sessions", json={"project_id": p["project_id"], "actor_id": "pi"}).json()
        r = client.post("/api/diagnosis/model-runs", json={
            "project_id": p["project_id"], "diagnosis_session_id": sess["diagnosis_session_id"],
            "adapter_name": "gem_fba", "actor_id": "agent",
        })
        assert r.status_code == 200
        body = r.json()
        assert body["runtime_status"] == "optimal"
        assert body["outputs"]["objective_value"] > 0
