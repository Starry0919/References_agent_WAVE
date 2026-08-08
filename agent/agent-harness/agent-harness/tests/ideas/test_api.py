"""HTTP surface smoke test for the Idea Capture API."""
from __future__ import annotations

from fastapi.testclient import TestClient

from harness import db
from harness.engineering_design import handoff as handoff_mod
from harness.server import create_app
from tests.engineering_design.fixtures import build_trp_diagnosis


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


def test_rank_for_design_project_id_surfaces_the_text_overlapping_idea_first():
    """`rank_for_design_project_id` should reorder ideas by relevance to the
    design project's originating diagnosis hypotheses (`harness/ideas/
    matching.py`), never silently reorder when nothing actually overlaps."""
    with db.session_scope() as s:
        proj, _sess, decision = build_trp_diagnosis(s)
        design_proj, _handoff = handoff_mod.ingest_diagnosis_decision(
            s, decision=decision, actor_id="agent", chassis="E. coli", chassis_version_or_genotype="K-12 MG1655 wild-type",
        )
        project_id = proj.project_id
        design_project_id = design_proj.design_project_id

    with _client() as client:
        # Deliberately captured in an order where the relevant idea is NOT
        # newest-first, so a passing test can't be explained by the default
        # newest-first ordering alone.
        unrelated = client.post(
            f"/api/projects/{project_id}/ideas",
            json={"actor_id": "alice", "free_text": "try adding a blue LED growth chamber for fun"},
        ).json()
        relevant = client.post(
            f"/api/projects/{project_id}/ideas",
            json={"actor_id": "alice", "free_text": "address the precursor supply limitation from imbalanced central carbon flux"},
        ).json()

        unranked = client.get(f"/api/projects/{project_id}/ideas").json()
        assert unranked["recommended_idea_id"] is None
        assert {i["idea_id"] for i in unranked["ideas"]} == {relevant["idea_id"], unrelated["idea_id"]}

        ranked = client.get(f"/api/projects/{project_id}/ideas", params={"rank_for_design_project_id": design_project_id}).json()
        assert ranked["recommended_idea_id"] == relevant["idea_id"]
        assert ranked["ideas"][0]["idea_id"] == relevant["idea_id"]
