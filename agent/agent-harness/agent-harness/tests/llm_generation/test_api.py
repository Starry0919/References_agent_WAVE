"""HTTP surface smoke test for the Scientific Capability Adapters API
(prompt §8.1) - real FastAPI TestClient, real Crossref network calls for
the health/search/verify-doi routes."""
from __future__ import annotations

from fastapi.testclient import TestClient

from harness import db
from harness.projects import service as proj_svc
from harness.server import create_app


def _client() -> TestClient:
    return TestClient(create_app())


def test_health_reports_real_provider_and_source_status():
    with _client() as client:
        r = client.get("/api/generation/health")
        assert r.status_code == 200
        body = r.json()
        assert body["llm"]["available"] is True
        assert body["llm"]["provider"] == "poe"
        assert body["crossref"]["available"] is True
        assert body["local_ddr"]["available"] is True


def test_verify_doi_and_list_records_over_http():
    with _client() as client:
        with db.session_scope() as s:
            proj = proj_svc.create_project(s, name="api test", host_definition={"species": "E. coli"}, target_product="x", actor_id="pi")
            project_id = proj.project_id

        r = client.post("/api/generation/evidence/verify-doi", json={"project_id": project_id, "doi": "10.9999/fabricated-xyz", "actor_id": "agent"})
        assert r.status_code == 200
        assert r.json()["resolved"] is False

        r2 = client.get("/api/generation/evidence/search", params={"query": "L-tryptophan", "source": "local_ddr"})
        assert r2.status_code == 200
        assert any(d["source_id"] == "DDR-001" for d in r2.json()["documents"])

        r3 = client.get("/api/generation/records")
        assert r3.status_code == 200

        r4 = client.get("/api/generation/records/GEN-does-not-exist")
        assert r4.status_code == 404
