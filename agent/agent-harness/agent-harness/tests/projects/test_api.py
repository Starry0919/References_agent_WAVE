"""API-level regression tests via `fastapi.testclient.TestClient` - these
exercise real HTTP routing, which caught a genuine route-ordering bug
during manual smoke testing (`/api/designs/diff` was being matched by the
parameterized `/api/designs/{design_version_id}` route registered before
it, resolving `design_version_id="diff"` instead of hitting the diff
handler).
"""
from __future__ import annotations

from fastapi.testclient import TestClient

from harness.server import create_app


def _client() -> TestClient:
    return TestClient(create_app())


def test_design_diff_route_is_not_shadowed_by_parameterized_route():
    with _client() as client:
        p = client.post("/api/projects", json={"name": "t", "target_product": "trp", "actor_id": "pi"}).json()
        dv0 = client.post(
            "/api/designs",
            json={
                "project_id": p["project_id"], "version_label": "v0", "parent_version_ids": [], "branch_name": "main",
                "genotype_manifest": {"baseline_strain": "K-12", "modifications": [{"gene": "trpE", "operation": "mutation", "detail": "S40F"}]},
                "decisions": [], "proposed_by": "agent",
            },
        ).json()
        dv1 = client.post(
            "/api/designs",
            json={
                "project_id": p["project_id"], "version_label": "v1", "parent_version_ids": [dv0["design_version_id"]], "branch_name": "main",
                "genotype_manifest": {"baseline_strain": "K-12", "modifications": [
                    {"gene": "trpE", "operation": "mutation", "detail": "S40F"},
                    {"gene": "tnaA", "operation": "knockout", "detail": ""},
                ]},
                "decisions": [], "proposed_by": "agent",
            },
        ).json()

        resp = client.get(f"/api/designs/diff?a={dv0['design_version_id']}&b={dv1['design_version_id']}")
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert "genotype_diff" in body and "decision_diff" in body
        assert body["genotype_diff"]["added"][0]["gene"] == "tnaA"


def test_full_api_walkthrough_project_to_design_approval():
    with _client() as client:
        p = client.post("/api/projects", json={"name": "t", "target_product": "trp", "actor_id": "pi"}).json()
        dv = client.post(
            "/api/designs",
            json={
                "project_id": p["project_id"], "version_label": "v0", "parent_version_ids": [], "branch_name": "main",
                "genotype_manifest": {"baseline_strain": "K-12", "modifications": []}, "decisions": [], "proposed_by": "agent",
            },
        ).json()
        approve = client.post(
            f"/api/designs/{dv['design_version_id']}/approve", json={"approver_id": "pi", "expected_project_version": 1}
        )
        assert approve.status_code == 200
        assert approve.json()["status"] == "approved"

        status = client.get(f"/api/projects/{p['project_id']}/status").json()
        assert status["active_design_version"] == dv["design_version_id"]

        status_from_ledger = client.get(f"/api/projects/{p['project_id']}/status/from-ledger").json()
        assert status_from_ledger["active_design_version"] == dv["design_version_id"]

        # self-approval must be rejected via the API too
        dv2 = client.post(
            "/api/designs",
            json={
                "project_id": p["project_id"], "version_label": "v1", "parent_version_ids": [dv["design_version_id"]],
                "branch_name": "main", "genotype_manifest": {"baseline_strain": "K-12", "modifications": []},
                "decisions": [], "proposed_by": "agent_self",
            },
        ).json()
        self_approve = client.post(
            f"/api/designs/{dv2['design_version_id']}/approve", json={"approver_id": "agent_self", "expected_project_version": 2}
        )
        assert self_approve.status_code == 409


def test_cycle_action_illegal_jump_returns_409():
    with _client() as client:
        p = client.post("/api/projects", json={"name": "t", "target_product": "trp", "actor_id": "pi"}).json()
        resp = client.post(
            f"/api/projects/{p['project_id']}/cycle/begin_data_ingestion",
            json={"actor_id": "pi", "kwargs": {"experiment_run_id": "RUN-x"}},
        )
        assert resp.status_code == 409


def test_rename_project():
    with _client() as client:
        p = client.post("/api/projects", json={"name": "old name", "target_product": "trp", "actor_id": "pi"}).json()
        resp = client.patch(f"/api/projects/{p['project_id']}", json={"name": "new name", "actor_id": "pi"})
        assert resp.status_code == 200, resp.text
        assert resp.json()["name"] == "new name"

        got = client.get(f"/api/projects/{p['project_id']}").json()
        assert got["name"] == "new name"

        listed = client.get("/api/projects").json()["projects"]
        assert any(row["project_id"] == p["project_id"] and row["name"] == "new name" for row in listed)


def test_rename_project_404_for_unknown_project():
    with _client() as client:
        resp = client.patch("/api/projects/PROJ-does-not-exist", json={"name": "x", "actor_id": "pi"})
        assert resp.status_code == 404


def test_list_orchestrator_runs_for_project_returns_newest_first():
    with _client() as client:
        p = client.post("/api/projects", json={"name": "t", "target_product": "trp", "actor_id": "pi"}).json()

        run1 = client.post(
            "/api/orchestrator/runs",
            json={"project_id": p["project_id"], "actor_id": "pi", "target_product": "trp", "host": "E. coli K-12"},
        ).json()
        run2 = client.post(
            "/api/orchestrator/runs",
            json={"project_id": p["project_id"], "actor_id": "pi", "target_product": "trp", "host": "E. coli K-12"},
        ).json()

        listed = client.get(f"/api/orchestrator/runs?project_id={p['project_id']}").json()["runs"]
        assert [r["workflow_run_id"] for r in listed] == [run2["workflow_run_id"], run1["workflow_run_id"]]

        other = client.post("/api/projects", json={"name": "other", "target_product": "trp", "actor_id": "pi"}).json()
        assert client.get(f"/api/orchestrator/runs?project_id={other['project_id']}").json()["runs"] == []


def test_delete_project_cascades_and_removes_from_list():
    with _client() as client:
        p = client.post("/api/projects", json={"name": "t", "target_product": "trp", "actor_id": "pi"}).json()
        run = client.post(
            "/api/orchestrator/runs",
            json={"project_id": p["project_id"], "actor_id": "pi", "target_product": "trp", "host": "E. coli K-12"},
        ).json()

        resp = client.delete(f"/api/projects/{p['project_id']}")
        assert resp.status_code == 200, resp.text
        assert resp.json() == {"deleted": True, "project_id": p["project_id"]}

        assert client.get(f"/api/projects/{p['project_id']}").status_code == 404
        assert client.get(f"/api/projects/{p['project_id']}/timeline").json()["events"] == []
        assert client.get(f"/api/orchestrator/runs/{run['workflow_run_id']}").status_code == 404
        listed = client.get("/api/projects").json()["projects"]
        assert all(row["project_id"] != p["project_id"] for row in listed)


def test_delete_project_404_for_unknown_project():
    with _client() as client:
        resp = client.delete("/api/projects/PROJ-does-not-exist")
        assert resp.status_code == 404
