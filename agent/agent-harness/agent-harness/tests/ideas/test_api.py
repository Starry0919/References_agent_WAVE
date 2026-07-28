"""HTTP surface smoke test for the Idea Capture API."""
from __future__ import annotations

from fastapi.testclient import TestClient

from harness.server import create_app


def _client() -> TestClient:
    return TestClient(create_app())


def test_capture_list_link_and_dismiss_over_http():
    with _client() as client:
        project = client.post(
            "/api/projects",
            json={"name": "Idea capture API test project", "target_product": "L-tryptophan", "actor_id": "alice"},
        ).json()
        project_id = project["project_id"]

        r = client.post(
            f"/api/projects/{project_id}/ideas",
            json={"actor_id": "alice", "free_text": "try a pfkA knockout", "target_gene": "pfkA", "modification_type": "knockout"},
        )
        assert r.status_code == 200
        idea = r.json()
        assert idea["status"] == "captured"
        idea_id = idea["idea_id"]

        r2 = client.get(f"/api/projects/{project_id}/ideas")
        assert r2.status_code == 200
        assert len(r2.json()["ideas"]) == 1

        r3 = client.post(f"/api/ideas/{idea_id}/link-to-design", json={"design_project_id": "EDP-1", "actor_id": "alice"})
        assert r3.status_code == 200
        assert r3.json()["status"] == "linked_to_design"
        assert r3.json()["linked_design_project_id"] == "EDP-1"

        r4 = client.post("/api/ideas/IDEA-does-not-exist/dismiss", json={"actor_id": "alice"})
        assert r4.status_code == 404

        r5 = client.post(f"/api/projects/{project_id}/ideas", json={"actor_id": "alice", "free_text": "   "})
        assert r5.status_code == 422
