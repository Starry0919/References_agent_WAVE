"""查缺补漏03 Phase 1/2/4: state-machine convergence tests.

Single-source-of-truth decision (see harness/orchestrator/service.py's
`CycleConflictError` docstring for the full rationale): `IterativeCycleState`
(Problem 02's business-cycle loop) and `UnifiedWorkflowRun` (the unified
orchestrator) are NOT merged into one table/state machine - each project
picks exactly ONE authoritative engine, decided by whichever is used first,
enforced by mutual exclusion rather than a best-effort field sync. These
tests prove that guard actually holds in both directions, and that the
reverse-lookup gap (workflow_run_id declared but never written) is closed
for the two module tables the orchestrator itself creates.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from harness import db
from harness.diagnosis import service as diag_svc
from harness.orchestrator.service import CycleConflictError, UnifiedScientificWorkflowOrchestrator
from harness.projects import service as proj_svc
from harness.scientific_evaluation.models import EvaluationCase
from harness.workflow.iterative_loop import IterativeLoopController

ORC = UnifiedScientificWorkflowOrchestrator()
_loop = IterativeLoopController()

_SUFFICIENT = {"has_baseline": True, "has_genotype": True, "has_condition": True, "has_time": True, "has_qc": True, "has_key_phenotype": True}


def _client() -> TestClient:
    from harness.server import create_app

    return TestClient(create_app())


# ---------------------------------------------------------------------------
# State consistency: mutual exclusion between Cycle and WorkflowRun
# ---------------------------------------------------------------------------


def test_create_run_rejects_project_already_driven_by_cycle():
    with db.session_scope() as s:
        proj = proj_svc.create_project(
            s, name="cycle-first project", host_definition={"species": "E. coli"}, target_product="trp", actor_id="pi",
        )
        cycle = proj_svc.get_active_cycle(s, proj.project_id)
        assert cycle.current_state == "PROJECT_CONTEXT_READY"
        _loop.capture_baseline(s, cycle, actor_id="pi")
        project_id = proj.project_id

    with db.session_scope() as s:
        with pytest.raises(CycleConflictError):
            ORC.create_run(s, project_id=project_id, actor_id="pi", target_product="trp", host="E. coli")


def test_create_run_allowed_for_fresh_project_cycle_untouched():
    """A brand-new project's auto-created Cycle sits at PROJECT_CONTEXT_READY
    - create_run must NOT be blocked by its own mere existence, only by the
    Cycle having actually been driven forward."""
    with db.session_scope() as s:
        proj = proj_svc.create_project(
            s, name="orchestrator-first project", host_definition={"species": "E. coli"}, target_product="trp", actor_id="pi",
        )
        project_id = proj.project_id

    with db.session_scope() as s:
        run = ORC.create_run(s, project_id=project_id, actor_id="pi", target_product="trp", host="E. coli")
        assert run.current_phase == "DIAGNOSIS"
        cycle = proj_svc.get_active_cycle(s, project_id)
        assert run.cycle_state_id == cycle.cycle_state_id, "run must record which Cycle it was created under, for traceability"


def test_cycle_action_rejects_project_already_driven_by_orchestrator():
    with _client() as client:
        p = client.post("/api/projects", json={"name": "orch-driven", "target_product": "trp", "actor_id": "pi"}).json()
        run = client.post(
            "/api/orchestrator/runs",
            json={"project_id": p["project_id"], "actor_id": "pi", "target_product": "trp", "host": "E. coli K-12"},
        ).json()
        assert run["current_phase"] == "DIAGNOSIS"

        resp = client.post(f"/api/projects/{p['project_id']}/cycle/capture_baseline", json={"actor_id": "pi"})
        assert resp.status_code == 409, resp.text
        assert "orchestrator run" in resp.json()["detail"]

        # the Cycle itself must be untouched by the rejected attempt
        cycle = client.get(f"/api/projects/{p['project_id']}/cycle").json()
        assert cycle["current_state"] == "PROJECT_CONTEXT_READY"


def test_cycle_action_still_allowed_for_project_with_no_orchestrator_run():
    with _client() as client:
        p = client.post("/api/projects", json={"name": "legacy-only", "target_product": "trp", "actor_id": "pi"}).json()
        resp = client.post(f"/api/projects/{p['project_id']}/cycle/capture_baseline", json={"actor_id": "pi"})
        assert resp.status_code == 200, resp.text
        assert resp.json()["current_state"] == "DESIGN_BASELINE_CAPTURED"


# ---------------------------------------------------------------------------
# Reverse lookup: workflow_run_id populated on module sub-objects
# ---------------------------------------------------------------------------


def test_diagnosis_session_reverse_lookup_to_workflow_run():
    with db.session_scope() as s:
        proj = proj_svc.create_project(
            s, name="reverse-lookup diagnosis", host_definition={"species": "E. coli", "strain": "K-12"},
            target_product="L-tryptophan", actor_id="pi",
        )
        run = ORC.create_run(s, project_id=proj.project_id, actor_id="pi", target_product="L-tryptophan", host="E. coli K-12")
        run_id = run.workflow_run_id

    with db.session_scope() as s:
        run = ORC.start_diagnosis(
            s, run_id, expected_version=1, actor_id="agent",
            request={"biological_system": {"species": "E. coli", "strain": "K-12"}, "phenotype": "titer plateaus below target",
                     "target_product": "L-tryptophan", "host": "E. coli K-12", "data_sufficiency": _SUFFICIENT},
            context={"medium": "M9", "carbon_source": "glucose"},
        )
        diagnosis_session_id = run.diagnosis_run_ref
        assert diagnosis_session_id is not None

    with db.session_scope() as s:
        sess = diag_svc.get_session(s, diagnosis_session_id)
        assert sess.workflow_run_id == run_id, "DiagnosisSession must record which orchestrator run created it"

        # reverse: given only a DiagnosisSession, find its owning run
        from sqlalchemy import select

        from harness.diagnosis.models import DiagnosisSession
        from harness.orchestrator.models import UnifiedWorkflowRun

        found_session = s.execute(select(DiagnosisSession).where(DiagnosisSession.workflow_run_id == run_id)).scalars().first()
        assert found_session is not None and found_session.diagnosis_session_id == diagnosis_session_id

        owning_run = s.execute(select(UnifiedWorkflowRun).where(UnifiedWorkflowRun.diagnosis_run_ref == diagnosis_session_id)).scalars().first()
        assert owning_run is not None and owning_run.workflow_run_id == run_id


def test_evaluation_case_reverse_lookup_to_workflow_run():
    """Reuses the same real Problem 4->5 handoff path `test_e2e.py` exercises
    (portfolio -> EvaluationCase), just asserting the workflow_run_id
    back-reference is populated - not re-testing the evaluation pipeline
    itself."""
    with db.session_scope() as s:
        proj = proj_svc.create_project(
            s, name="reverse-lookup evaluation", host_definition={"species": "E. coli", "strain": "K-12"},
            target_product="L-tryptophan", actor_id="pi",
        )
        run = ORC.create_run(s, project_id=proj.project_id, actor_id="pi", target_product="L-tryptophan", host="E. coli K-12")
        run_id = run.workflow_run_id

    with db.session_scope() as s:
        run = ORC.start_diagnosis(
            s, run_id, expected_version=1, actor_id="agent",
            request={"biological_system": {"species": "E. coli", "strain": "K-12"}, "phenotype": "titer plateaus below target",
                     "target_product": "L-tryptophan", "host": "E. coli K-12", "data_sufficiency": _SUFFICIENT},
            context={"medium": "M9", "carbon_source": "glucose"},
        )
        assert run.current_phase == "DESIGN"
        v = run.version

    with db.session_scope() as s:
        run = ORC.start_design(
            s, run_id, expected_version=v, actor_id="system",
            request={"chassis": "E. coli", "chassis_version_or_genotype": "K-12 MG1655 wild-type",
                     "primary_metrics": [{"metric": "titer", "unit": "g/L"}],
                     "hard_constraints": [{"constraint": "no essential gene knockout", "type": "no_essential_gene_knockout"}],
                     "available_resources": {"materials": ["pKD46", "pCP20"], "instruments": ["HPLC"]}},
            context={},
        )
        assert run.current_phase == "EVALUATION"
        v = run.version

    with db.session_scope() as s:
        run = ORC.run_evaluation(s, run_id, expected_version=v, actor_id="system")
        evaluation_id = run.evaluation_run_ref
        assert evaluation_id is not None

    with db.session_scope() as s:
        case = s.get(EvaluationCase, evaluation_id)
        assert case.workflow_run_id == run_id, "EvaluationCase must record which orchestrator run created it"

        from sqlalchemy import select

        from harness.orchestrator.models import UnifiedWorkflowRun

        found_case = s.execute(select(EvaluationCase).where(EvaluationCase.workflow_run_id == run_id)).scalars().first()
        assert found_case is not None and found_case.evaluation_id == evaluation_id

        owning_run = s.execute(select(UnifiedWorkflowRun).where(UnifiedWorkflowRun.evaluation_run_ref == evaluation_id)).scalars().first()
        assert owning_run is not None and owning_run.workflow_run_id == run_id
