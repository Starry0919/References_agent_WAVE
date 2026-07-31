"""HTTP surface tests for the evaluation-metrics API, matching
`tests/golden_set/test_api.py`'s TestClient convention."""
from __future__ import annotations

from fastapi.testclient import TestClient

from harness import db
from harness.server import create_app
from tests.engineering_design.fixtures import handoff_through_portfolio


def _client() -> TestClient:
    return TestClient(create_app())


def test_summary_and_reference_ddr_and_consistency_routes_over_http():
    with db.session_scope() as s:
        proj, _portfolio, _candidates = handoff_through_portfolio(s)
        design_project_id = proj.design_project_id
        outer_project_id = proj.project_id

    with _client() as client:
        r1 = client.get(f"/api/evaluation-metrics/by-project/{outer_project_id}")
        assert r1.status_code == 200
        design_projects = r1.json()["design_projects"]
        assert any(dp["design_project_id"] == design_project_id for dp in design_projects)

        r2 = client.get(f"/api/evaluation-metrics/projects/{design_project_id}/summary")
        assert r2.status_code == 200
        body = r2.json()
        assert set(body["process"]) == {"grounding_rate", "coverage_completeness"}
        assert body["capability"]["reasoned_novelty"]["applicable"] is False  # no reference DDR linked yet

        r3 = client.post(f"/api/evaluation-metrics/projects/{design_project_id}/reference-ddr", json={"ddr_ids": ["DDR-001"]})
        assert r3.status_code == 200
        assert r3.json()["reference_ddr_ids"] == ["DDR-001"]

        r4 = client.get(f"/api/evaluation-metrics/projects/{design_project_id}/summary")
        assert r4.status_code == 200
        assert r4.json()["capability"]["reasoned_novelty"]["applicable"] is True

        r5 = client.get(f"/api/evaluation-metrics/projects/{design_project_id}/consistency-runs")
        assert r5.status_code == 200
        assert r5.json()["runs"] == []

        r6 = client.get(f"/api/evaluation-metrics/projects/does-not-exist/summary")
        assert r6.status_code == 404


def test_get_missing_consistency_run_is_404():
    with db.session_scope() as s:
        proj, _portfolio, _candidates = handoff_through_portfolio(s)
        design_project_id = proj.design_project_id

    with _client() as client:
        r = client.get(f"/api/evaluation-metrics/projects/{design_project_id}/consistency-runs/no-such-run")
        assert r.status_code == 404
