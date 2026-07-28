"""HTTP surface tests (doc06 §11) - exercises the real service layer
through FastAPI, not a mocked client.
"""
from __future__ import annotations

from fastapi.testclient import TestClient

from harness import db
from harness.server import create_app
from tests.virtual_cell.fixtures import build_approved_ppc_knockout_design, build_out_of_domain_design

_ENV = {"medium": "M9_minimal", "carbon_source": "glucose"}
_CHASSIS = {"organism": "Escherichia coli", "strain": "K-12 MG1655"}


def _client() -> TestClient:
    return TestClient(create_app())


def test_list_models_reports_real_and_unavailable():
    with _client() as client:
        r = client.get("/api/virtual-cell/models")
        assert r.status_code == 200
        models = {m["adapter_id"] if "adapter_id" in m else m["model_id"]: m for m in r.json()["models"]}
        gem = next(m for m in r.json()["models"] if m["model_id"] == "MREG-gem_fba")
        assert gem["availability_status"] == "available"
        vecoli = next(m for m in r.json()["models"] if m["model_id"] == "MREG-vecoli")
        assert vecoli["availability_status"] == "unavailable"


def test_route_question_endpoint():
    with _client() as client:
        r = client.post("/api/virtual-cell/models/route", json={"question_type": "steady_state_flux"})
        assert r.status_code == 200
        assert r.json()["selected_model_id"] == "MREG-gem_fba"


def test_run_simulation_endpoint_produces_full_pipeline_result():
    with db.session_scope() as s:
        proj, dv = build_approved_ppc_knockout_design(s)
        project_id, design_version_id = proj.project_id, dv.design_version_id

    with _client() as client:
        r = client.post("/api/virtual-cell/simulations", json={
            "project_id": project_id, "design_version_id": design_version_id, "chassis": _CHASSIS, "environment": _ENV, "actor_id": "agent",
        })
        assert r.status_code == 200
        body = r.json()
        assert body["case"]["status"] in ("comparison_ready", "prediction_under_review", "validation_planned", "awaiting_observation")
        assert body["baseline_run"]["status"] == "optimal"
        assert body["candidate_run"]["status"] == "optimal"
        growth = next(e for e in body["comparison"]["endpoints"] if e["name"] == "growth_rate")
        assert growth["delta"] < 0
        assert body["review"]["decision"] in ("decision_ready", "limited_acceptance")
        assert any(v["endpoint"] == "growth_rate" for v in body["validation_items"])

        run_id = body["baseline_run"]["model_run_id"]
        r2 = client.get(f"/api/virtual-cell/simulations/{run_id}")
        assert r2.status_code == 200
        r3 = client.get(f"/api/virtual-cell/simulations/{run_id}/artifacts")
        assert r3.status_code == 200
        assert "inputs_hash" in r3.json()


def test_run_simulation_endpoint_out_of_domain_never_fabricates_a_number():
    with db.session_scope() as s:
        proj, dv = build_out_of_domain_design(s)
        project_id, design_version_id = proj.project_id, dv.design_version_id

    with _client() as client:
        r = client.post("/api/virtual-cell/simulations", json={
            "project_id": project_id, "design_version_id": design_version_id, "chassis": _CHASSIS, "environment": _ENV, "actor_id": "agent",
        })
        assert r.status_code == 200
        body = r.json()
        assert body["case"]["status"] == "out_of_domain"
        assert body["baseline_run"] is None
        assert body["comparison"] is None
