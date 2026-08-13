"""doc06 §10: Problem 5 blocking rejection must stop Problem 06 from
simulating a DesignVersion, unless an audited Human Override is provided.
"""
from __future__ import annotations

import pytest

from harness import db
from harness.ids import new_id, now
from harness.scientific_evaluation.models import EvaluationCase
from harness.virtual_cell import service as vc_service
from harness.virtual_cell.guards import SimulationGuardError
from tests.virtual_cell.fixtures import build_approved_ppc_knockout_design


def _make_eval_case(session, *, project_id: str, status: str) -> EvaluationCase:
    case = EvaluationCase(
        evaluation_id=new_id("EVAL"), project_id=project_id, design_project_id="DPROJ-x", workflow_run_id=None,
        diagnosis_reference=None, portfolio_reference="PORT-x", design_version_references=[], frozen_context={},
        evaluation_mode="single_candidate", status=status, revision_round=0, created_by="pi", created_at=now(), updated_at=now(),
    )
    session.add(case)
    session.flush()
    return case


def test_rejected_evaluation_blocks_simulation():
    with db.session_scope() as s:
        proj, dv = build_approved_ppc_knockout_design(s)
        eval_case = _make_eval_case(s, project_id=proj.project_id, status="rejected")
        with pytest.raises(SimulationGuardError):
            vc_service.open_simulation_case(
                s, project_id=proj.project_id, design_version_id=dv.design_version_id, requested_by="agent",
                evaluation_reference=eval_case.evaluation_id,
            )


def test_audited_human_override_permits_simulation_despite_rejection():
    with db.session_scope() as s:
        proj, dv = build_approved_ppc_knockout_design(s)
        eval_case = _make_eval_case(s, project_id=proj.project_id, status="rejected")
        case = vc_service.open_simulation_case(
            s, project_id=proj.project_id, design_version_id=dv.design_version_id, requested_by="agent",
            evaluation_reference=eval_case.evaluation_id, human_override={"approver_id": "pi", "reason": "safety exception, PI approved"},
        )
        assert case.status == "simulation_requested"


def test_override_without_approver_id_is_rejected():
    with db.session_scope() as s:
        proj, dv = build_approved_ppc_knockout_design(s)
        eval_case = _make_eval_case(s, project_id=proj.project_id, status="rejected")
        with pytest.raises(SimulationGuardError):
            vc_service.open_simulation_case(
                s, project_id=proj.project_id, design_version_id=dv.design_version_id, requested_by="agent",
                evaluation_reference=eval_case.evaluation_id, human_override={"reason": "no approver named"},
            )


def test_approved_evaluation_does_not_block():
    with db.session_scope() as s:
        proj, dv = build_approved_ppc_knockout_design(s)
        eval_case = _make_eval_case(s, project_id=proj.project_id, status="approved_for_build")
        case = vc_service.open_simulation_case(
            s, project_id=proj.project_id, design_version_id=dv.design_version_id, requested_by="agent",
            evaluation_reference=eval_case.evaluation_id,
        )
        assert case.status == "simulation_requested"
