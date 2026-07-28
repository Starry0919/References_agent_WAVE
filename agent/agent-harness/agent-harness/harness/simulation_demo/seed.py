"""The one real, tested synthetic-simulation DBTL flow (查缺补漏04
requirement 7: reuse, don't re-derive). This module is the single source
of truth for "how the SIM-DBTL-TRYPTOPHAN-001 demo is built" - both
`tests/orchestrator/test_synthetic_simulation_full_dbtl_flow.py` and the
live `POST /api/simulation/admin/seed` endpoint call the SAME
`run_synthetic_simulation_flow` function. The test drives it against the
main app under its isolated per-test SQLite file (see
`tests/orchestrator/conftest.py`); the live endpoint drives it against the
simulation sub-app under the separate, persistent `simulation_demo_ledger.db`
(see `harness/simulation_demo/db.py` / `app.py`). Same code path, two
different physically-isolated databases - never the real project ledger.
"""
from __future__ import annotations

from typing import Any, Callable, Protocol

SIMULATION_NAMESPACE = "test_full_dbtl_run"
SYNTHETIC_TAG = {"data_provenance": "synthetic_simulation_data", "simulation_namespace": SIMULATION_NAMESPACE}
DEMO_PROJECT_NAME = "SIM-DBTL-TRYPTOPHAN-001: E.coli K-12 L-tryptophan optimization [SYNTHETIC SIMULATION DATA]"


class _Response(Protocol):
    status_code: int

    def json(self) -> Any: ...


class _Client(Protocol):
    def get(self, path: str) -> _Response: ...
    def post(self, path: str, json: dict[str, Any]) -> _Response: ...


def _ok(resp: _Response, step: str) -> Any:
    if resp.status_code != 200:
        raise RuntimeError(f"synthetic simulation flow failed at {step!r}: HTTP {resp.status_code} {resp.json()}")
    return resp.json()


def find_existing_demo_project(client: _Client) -> dict[str, Any] | None:
    """Idempotency check: never mint a second demo project on repeat seed
    calls (a user re-clicking "Run Demo" or a page re-mounting must not
    silently multiply simulation projects)."""
    rows = _ok(client.get("/api/projects"), "list projects")["projects"]
    for row in rows:
        if row["name"] == DEMO_PROJECT_NAME:
            return row
    return None


def run_synthetic_simulation_flow(client: _Client, session_scope: Callable[[], Any]) -> dict[str, Any]:
    """Drives the full, real (never mocked) DBTL lifecycle through the HTTP
    API surface a real user's browser hits:

    Project -> Start Workflow -> Diagnosis (insufficient) -> synthetic
    observation injection -> Resume Diagnosis (sufficient) -> Hypothesis
    Generation -> Design -> Critique/Evaluation -> Human Review ->
    Simulation -> Build/Test Plan (experiment plan + run + observation) ->
    Learning.

    `session_scope` is a zero-arg context-manager factory (either
    `harness.db.session_scope` for the isolated-per-test database, or
    `harness.simulation_demo.db.simulation_session_scope` for the live
    persistent demo database) used only for the handful of steps that
    intentionally bypass the HTTP layer because no HTTP endpoint exists for
    them (biological-context creation, injecting baseline observations, and
    driving Problem 4's own evaluator the same deterministic way
    `tests/orchestrator/test_simulation_and_learning.py` does - see that
    module's docstring for why the independent Critic's own reject/revise
    loop is a separate, honest non-determinism this flow does not fight).

    Returns a dict of the key ids/final state the caller can report or
    link to - never raises to signal "the flow legitimately stopped early"
    (a real BLOCKED/gate-rejected outcome is a valid, honestly-reported
    result, not a failure of this function).
    """
    log: list[str] = []

    def step(msg: str) -> None:
        log.append(msg)

    # -- Project --
    project = _ok(
        client.post(
            "/api/projects",
            json={
                "name": DEMO_PROJECT_NAME,
                "host_definition": {"species": "E. coli", "strain": "K-12", "simulation_namespace": SIMULATION_NAMESPACE},
                "target_product": "L-tryptophan", "actor_id": "sim-operator",
            },
        ),
        "create project",
    )
    project_id = project["project_id"]
    step(f"Created project {project_id} ({DEMO_PROJECT_NAME})")

    # -- Start Workflow --
    run = _ok(
        client.post(
            "/api/orchestrator/runs",
            json={"project_id": project_id, "actor_id": "sim-operator", "target_product": "L-tryptophan", "host": "E. coli K-12"},
        ),
        "create workflow run",
    )
    run_id = run["workflow_run_id"]
    step(f"Started WorkflowRun {run_id}, phase={run['current_phase']}")

    # -- startDiagnosis, honestly with no claimed sufficiency --
    run = _ok(
        client.post(
            f"/api/orchestrator/runs/{run_id}/diagnosis",
            json={
                "expected_version": run["version"], "actor_id": "sim-operator",
                "request": {
                    "phenotype": "Terminal pathway enzymes are induced but titer plateaus after induction.",
                    "target_product": "L-tryptophan", "host": "E. coli K-12",
                    "biological_system": {"species": "E. coli", "strain": "K-12"}, "data_sufficiency": {},
                },
                "context": {"medium": "M9", "carbon_source": "glucose", "simulation_namespace": SIMULATION_NAMESPACE},
            },
        ),
        "start diagnosis",
    )
    diagnosis_session_id = run["diagnosis_run_ref"]
    step(f"DiagnosisSession {diagnosis_session_id}: status=data_required, data_sufficiency=insufficient (by design, honest first state)")

    # -- inject synthetic baseline observations (glucose consumption,
    #    growth curve, titer, precursor proxy) - real DB writes, tagged
    #    synthetic, on whichever engine `session_scope` is bound to. --
    from harness.diagnosis import service as diag_svc
    from harness.diagnosis.normalizer import RawObservationInput, normalize_and_commit

    with session_scope() as s:
        ctx = diag_svc.create_biological_context(s, project_id=project_id, medium="M9", carbon_source="glucose")
        context_id = ctx.context_id
        synthetic_inputs = [
            RawObservationInput(feature_or_phenotype="glucose_consumption_rate", value=0.85, unit="g/L/h", condition_id=context_id, qc_status="passed", reference_or_baseline=SYNTHETIC_TAG, provenance=SYNTHETIC_TAG),
            RawObservationInput(feature_or_phenotype="growth_curve_od600", value=2.4, unit="OD600", condition_id=context_id, qc_status="passed", reference_or_baseline=SYNTHETIC_TAG, provenance=SYNTHETIC_TAG),
            RawObservationInput(feature_or_phenotype="tryptophan_titer", value=1.0, unit="g/L", condition_id=context_id, qc_status="passed", reference_or_baseline=SYNTHETIC_TAG, provenance=SYNTHETIC_TAG),
            RawObservationInput(feature_or_phenotype="precursor_proxy_chorismate", value=0.12, unit="mM", condition_id=context_id, qc_status="passed", reference_or_baseline=SYNTHETIC_TAG, provenance=SYNTHETIC_TAG),
        ]
        observation_ids = []
        for raw in synthetic_inputs:
            obs, report = normalize_and_commit(s, project_id=project_id, raw=raw, actor_id="sim-operator")
            if obs is None:
                raise RuntimeError(f"synthetic observation {raw.feature_or_phenotype!r} rejected: {report.issues}")
            observation_ids.append(obs.observation_id)
    step(f"Injected {len(observation_ids)} synthetic Observations, all tagged data_provenance=synthetic_simulation_data")

    # -- resume with sufficient data (mirrors checking all 6 boxes +
    #    clicking "Continue Diagnosis" in DiagnoseStage.tsx) --
    run = _ok(
        client.post(
            f"/api/orchestrator/runs/{run_id}/diagnosis/resume",
            json={
                "expected_version": run["version"], "actor_id": "sim-operator",
                "data_sufficiency": {"has_baseline": True, "has_genotype": True, "has_condition": True, "has_time": True, "has_qc": True, "has_key_phenotype": True},
            },
        ),
        "resume diagnosis",
    )
    if run["diagnosis_run_ref"] != diagnosis_session_id:
        raise RuntimeError("resume replaced the diagnosis session instead of continuing it - regression in resume_diagnosis_with_data")
    step(f"Resumed diagnosis (data_sufficiency=sufficient) - same session continued, phase={run['current_phase']}")

    if run["current_phase"] != "DESIGN":
        step(f"Diagnosis stopped honestly before DESIGN: status={run['status']!r} pause={run.get('pause_reason')!r}")
        return {"project_id": project_id, "workflow_run_id": run_id, "diagnosis_session_id": diagnosis_session_id, "final_phase": run["current_phase"], "log": log}
    v = run["version"]

    # -- Design --
    run = _ok(
        client.post(
            f"/api/orchestrator/runs/{run_id}/design",
            json={
                "expected_version": v, "actor_id": "sim-operator",
                "request": {
                    "chassis": "E. coli", "chassis_version_or_genotype": "K-12 MG1655 wild-type",
                    "primary_metrics": [{"metric": "titer", "unit": "g/L"}],
                    "hard_constraints": [{"constraint": "no essential gene knockout", "type": "no_essential_gene_knockout"}],
                    "available_resources": {"materials": ["pKD46", "pCP20"], "instruments": ["HPLC"]},
                },
                "context": {},
            },
        ),
        "start design",
    )
    step(f"Design generated, design_project_ref={run['design_project_ref']}, phase={run['current_phase']}")

    # -- Critique/Evaluation via Problem 4's own evaluator (see module
    #    docstring for why - the same technique test_simulation_and_learning.py
    #    and test_full_lifecycle.py use to reach an approved candidate
    #    deterministically). --
    from harness.engineering_design.evaluation_service import evaluate_portfolio
    from harness.orchestrator.models import UnifiedWorkflowRun
    from harness.orchestrator.service import UnifiedScientificWorkflowOrchestrator

    ORC = UnifiedScientificWorkflowOrchestrator()
    with session_scope() as s:
        orch_run = s.get(UnifiedWorkflowRun, run_id)
        handoff = ORC._design.get_handoff(s, orch_run.design_project_ref)
        portfolio_id = handoff.payload_refs["portfolio_id"]
        result = evaluate_portfolio(s, portfolio_id=portfolio_id, actor_id="sim-operator")
        selected_design_id = result["decision"]["selected_design_ids"][0]
        ORC._transition_phase(s, orch_run, to_phase="HUMAN_REVIEW", reason="synthetic simulation: evaluated via Problem 4 evaluator", actor_id="sim-operator")
        v = orch_run.version
    step(f"Critique complete, selected_design_id={selected_design_id}, phase=HUMAN_REVIEW")

    # -- Human Review --
    run = _ok(
        client.post(
            f"/api/orchestrator/runs/{run_id}/human-gate-decision",
            json={
                "expected_version": v, "decision": "approve", "actor_id": "sim-pi", "reason": "synthetic simulation: approved for build",
                "selected_design_id": selected_design_id,
                "build_test_kwargs": {
                    "construction_concept": "lambda-red recombineering", "required_materials": ["pKD46", "pCP20"],
                    "controls": [{"name": "wild-type baseline"}], "replication_plan": {"biological_replicates": 3},
                    "sampling_plan": [{"time": "24h"}], "qc_checkpoints": ["colony PCR"],
                    "decision_rules": ["titer increase >=10% vs baseline = success"],
                },
            },
        ),
        "human gate decision",
    )
    step(f"Human Review approved, design_version_ref={run['design_version_ref']}, phase={run['current_phase']}")

    if run["current_phase"] != "SIMULATION":
        return {"project_id": project_id, "workflow_run_id": run_id, "diagnosis_session_id": diagnosis_session_id, "final_phase": run["current_phase"], "log": log}
    v = run["version"]

    # -- Simulation --
    run = _ok(
        client.post(
            f"/api/orchestrator/runs/{run_id}/simulation",
            json={"expected_version": v, "actor_id": "sim-operator", "chassis": {"species": "E. coli", "strain": "K-12"}, "environment": {"medium": "M9", "carbon_source": "glucose"}},
        ),
        "run simulation",
    )
    step(f"Simulation ran, simulation_campaign_ref={run['simulation_campaign_ref']}, phase={run['current_phase']}")
    if run["current_phase"] == "BLOCKED":
        step(f"Simulation honestly BLOCKED: {run['blocked_reason']}")
        return {"project_id": project_id, "workflow_run_id": run_id, "diagnosis_session_id": diagnosis_session_id, "final_phase": run["current_phase"], "log": log}
    v = run["version"]

    # -- Build/Test Plan --
    run = _ok(
        client.post(
            f"/api/orchestrator/runs/{run_id}/experiment-plan",
            json={"expected_version": v, "actor_id": "sim-pi", "controls": ["wild-type baseline"], "factors": ["genotype"], "response_variables": ["titer"], "acceptance_criteria": ["titer increase >=10% vs baseline"]},
        ),
        "create experiment plan",
    )
    step(f"Experiment plan created, experiment_plan_ref={run['experiment_plan_ref']}")
    v = run["version"]

    run = _ok(
        client.post(
            f"/api/orchestrator/runs/{run_id}/experiment-run",
            json={
                "expected_version": v, "actor_id": "sim-tech",
                "raw_observation": {"feature_or_phenotype": "titer", "value": 1.2, "unit": "g/L", "qc_status": "passed", "condition_id": context_id},
                "execution_status": "completed",
            },
        ),
        "record experiment run",
    )
    step(f"Experiment run recorded + observation ingested, phase={run['current_phase']}")
    v = run["version"]

    # -- Learning --
    run = _ok(
        client.post(
            f"/api/orchestrator/runs/{run_id}/learning",
            json={
                "expected_version": v, "actor_id": "sim-tech",
                "observed_results": [{"metric": "titer", "value": 0.9, "baseline_value": 1.0}],
                "construction_verified": True, "assay_qc_passed": True,
            },
        ),
        "run learning",
    )
    step(f"Learning complete, final phase={run['current_phase']} (an honest outcome, not a fabricated success)")

    return {
        "project_id": project_id, "workflow_run_id": run_id, "diagnosis_session_id": diagnosis_session_id,
        "final_phase": run["current_phase"], "log": log,
    }


def seed_demo_if_needed(client: _Client, session_scope: Callable[[], Any]) -> dict[str, Any]:
    """Idempotent entry point for the live `POST /api/simulation/admin/seed`
    endpoint: reuses an already-seeded demo project rather than minting a
    duplicate on every click."""
    existing = find_existing_demo_project(client)
    if existing is not None:
        return {"already_seeded": True, "project_id": existing["project_id"]}
    result = run_synthetic_simulation_flow(client, session_scope)
    return {"already_seeded": False, **result}
