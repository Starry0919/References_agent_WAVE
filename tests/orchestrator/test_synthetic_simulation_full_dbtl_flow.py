"""全真 DBTL Agent 模拟验收: a synthetic, sandboxed full-lifecycle simulation
that mirrors exactly what a real user does through the actual UI - never a
shortcut through internal service functions the frontend doesn't call.

This test drives `harness.simulation_demo.seed.run_synthetic_simulation_flow`
- the SAME function the live `POST /api/simulation/admin/seed` endpoint
calls to build the browser-visible SIM-DBTL-TRYPTOPHAN-001 demo (查缺补漏04
requirement 7: one real, tested flow, reused - not re-derived per caller).
Here it runs against the MAIN app under this test's isolated per-test
SQLite file (`tests/orchestrator/conftest.py`'s `isolated_db` fixture via
`harness.db.reset_engine_for_tests`); the live endpoint runs the identical
function against the separate, persistent `simulation_demo_ledger.db`
sub-app engine (`harness/simulation_demo/db.py`). Same code path, two
different physically-isolated databases - never the real project ledger
either way.

This test's job is specifically to prove: once a diagnosis session's data
sufficiency gate is satisfied (data_sufficiency == "sufficient"), the
orchestrator ACTUALLY continues past DIAGNOSIS through the rest of the DBTL
chain - not just that the gate transitions, and not just at the service
layer (already covered by test_full_lifecycle.py) but through the real HTTP
API surface the frontend calls (harness/api/orchestrator.py,
harness/api/diagnosis.py), catching any API-layer-only bugs a
service-layer-only test would miss (this test itself uncovered exactly such
a bug: HypothesisAssessment rows were computed but never persisted, so
GET /api/diagnosis/sessions/{id}/hypotheses always returned an empty list
even after a successful diagnosis - fixed in
harness/orchestrator/adapters.py's `_run_hypothesis_pipeline`).
"""
from __future__ import annotations

from fastapi.testclient import TestClient

from harness import db
from harness.simulation_demo.seed import DEMO_PROJECT_NAME, run_synthetic_simulation_flow


def _client() -> TestClient:
    from harness.server import create_app

    return TestClient(create_app())


def test_synthetic_simulation_full_dbtl_flow():
    with _client() as client:
        result = run_synthetic_simulation_flow(client, db.session_scope)

        assert result["final_phase"] in ("COMPLETED", "DIAGNOSIS", "REDESIGN"), (
            f"expected the flow to reach Learning's outcome classification, got {result['final_phase']!r}. Log:\n" + "\n".join(result["log"])
        )
        project_id = result["project_id"]
        run_id = result["workflow_run_id"]
        diagnosis_session_id = result["diagnosis_session_id"]

        # -- the API a real Diagnose page reads must actually reflect the
        #    real hypotheses that were generated, not silently show none. --
        resp = client.get(f"/api/diagnosis/sessions/{diagnosis_session_id}/hypotheses")
        hyps = resp.json()["hypotheses"]
        assert len(hyps) >= 2, "diagnosis reached DESIGN, so a real competing hypothesis set must be visible via the API the frontend actually calls"

        resp = client.get(f"/api/diagnosis/sessions/{diagnosis_session_id}/decisions")
        assert len(resp.json()) >= 1

        # -- reconciliation: ledger must agree with materialized state --
        resp = client.get(f"/api/orchestrator/runs/{run_id}/reconcile")
        assert resp.json()["ledger_matches_materialized_state"] is True

        # -- project is clearly named/tagged as synthetic --
        resp = client.get(f"/api/projects/{project_id}")
        assert resp.json()["name"] == DEMO_PROJECT_NAME

    # -- isolation proof: this test's DiagnosisSession/Observations never
    #    touch a real project's evidence chain, because they were never
    #    created against any project the real system knows about outside
    #    this test's own isolated database (tests/orchestrator/conftest.py's
    #    `isolated_db` fixture repoints the engine before this test runs and
    #    disposes it after - see harness/db.py's `reset_engine_for_tests`). --
    with db.session_scope() as s:
        from sqlalchemy import select

        from harness.experiments.models import Observation
        from harness.projects.models import Project

        other_projects = s.execute(select(Project).where(Project.project_id != project_id)).scalars().all()
        assert other_projects == [], "this test's isolated DB must contain only the synthetic simulation project"

        synthetic_obs = s.execute(
            select(Observation).where(Observation.project_id == project_id, Observation.metric != "titer")
        ).scalars().all()
        assert len(synthetic_obs) == 2, "the subject/baseline QC pair (titer's later experiment-run observation is separate) must both be present"
        assert all(o.reference_or_baseline and o.reference_or_baseline.get("data_provenance") == "synthetic_simulation_data" for o in synthetic_obs)
