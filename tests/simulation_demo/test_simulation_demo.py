"""Tests for the Simulation/Demo Workspace (查缺补漏04): the browser-visible
SIM-DBTL-TRYPTOPHAN-001 demo backed by a completely separate database from
the real project ledger.
"""
from __future__ import annotations

from fastapi.testclient import TestClient

from harness import db
from harness.server import create_app
from harness.simulation_demo import db as sim_db
from harness.simulation_demo.seed import DEMO_PROJECT_NAME


def _client() -> TestClient:
    return TestClient(create_app())


def test_seed_creates_demo_project_visible_only_under_simulation_prefix():
    with _client() as client:
        resp = client.post("/api/simulation/admin/seed")
        assert resp.status_code == 200, resp.text
        result = resp.json()
        assert result["already_seeded"] is False
        project_id = result["project_id"]
        assert result["final_phase"] in ("COMPLETED", "DIAGNOSIS", "REDESIGN")

        sim_projects = client.get("/api/simulation/api/projects").json()["projects"]
        assert any(p["project_id"] == project_id and p["name"] == DEMO_PROJECT_NAME for p in sim_projects)

        real_projects = client.get("/api/projects").json()["projects"]
        assert all(p["project_id"] != project_id for p in real_projects), "the demo project must never appear in the real project list"
        assert real_projects == [], "no real project should exist in this isolated test database at all"


def test_seed_is_idempotent_never_duplicates():
    with _client() as client:
        first = client.post("/api/simulation/admin/seed").json()
        second = client.post("/api/simulation/admin/seed").json()
        assert second["already_seeded"] is True
        assert second["project_id"] == first["project_id"]

        sim_projects = client.get("/api/simulation/api/projects").json()["projects"]
        matching = [p for p in sim_projects if p["name"] == DEMO_PROJECT_NAME]
        assert len(matching) == 1, "seeding twice must not create a second demo project"


def test_reset_rebuilds_a_fresh_demo_project():
    with _client() as client:
        first = client.post("/api/simulation/admin/seed").json()
        first_project_id = first["project_id"]

        reset = client.post("/api/simulation/admin/reset").json()
        assert reset["reset"] is True
        assert reset["project_id"] != first_project_id, "reset must rebuild a fresh project, not reuse the old one"

        assert client.get(f"/api/simulation/api/projects/{first_project_id}").status_code == 404
        assert client.get(f"/api/simulation/api/projects/{reset['project_id']}").status_code == 200


def test_synthetic_observations_isolated_from_real_evidence_provenance():
    with _client() as client:
        client.post("/api/simulation/admin/seed")

    from sqlalchemy import select

    from harness.experiments.models import Observation

    with db.session_scope() as s:
        real_obs = s.execute(select(Observation)).scalars().all()
        assert real_obs == [], "seeding the demo must never write an Observation row into the real ledger"

    with sim_db.simulation_session_scope() as s:
        sim_obs = s.execute(select(Observation)).scalars().all()
        assert len(sim_obs) >= 3
        synthetic_ones = [o for o in sim_obs if o.reference_or_baseline and o.reference_or_baseline.get("data_provenance") == "synthetic_simulation_data"]
        assert len(synthetic_ones) >= 2, "the injected subject/baseline pair must be tagged synthetic_simulation_data in the simulation database"


def test_workspace_read_endpoints_work_under_simulation_prefix():
    """The real Workspace UI's stage pages (Diagnose/Design/Simulate/
    Critique/BuildTestPlan) call these exact read endpoints - proving they
    resolve correctly under `/api/simulation/*` is what makes the demo
    actually clickable in a browser, not just seedable."""
    with _client() as client:
        seed = client.post("/api/simulation/admin/seed").json()
        project_id = seed["project_id"]
        run_id = seed["workflow_run_id"]
        diagnosis_session_id = seed["diagnosis_session_id"]

        assert client.get(f"/api/simulation/api/orchestrator/runs/{run_id}").status_code == 200
        assert client.get(f"/api/simulation/api/orchestrator/runs?project_id={project_id}").status_code == 200
        assert client.get(f"/api/simulation/api/diagnosis/sessions/{diagnosis_session_id}").status_code == 200
        assert client.get(f"/api/simulation/api/diagnosis/sessions/{diagnosis_session_id}/hypotheses").status_code == 200
        assert client.get(f"/api/simulation/api/projects/{project_id}/status").status_code == 200
