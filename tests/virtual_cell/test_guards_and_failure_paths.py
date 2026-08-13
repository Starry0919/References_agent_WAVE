"""Failure-path / invariant tests (doc06 §14.1) - each one exercises a
guard that must reject or honestly degrade, never fabricate.
"""
from __future__ import annotations

import pytest

from harness import db
from harness.virtual_cell import runner as runner_mod
from harness.virtual_cell import service as vc_service
from harness.virtual_cell.compatibility import check_compatibility
from harness.virtual_cell.comparison import compare_runs
from harness.virtual_cell.guards import SimulationGuardError, assert_baseline_succeeded_before_delta, assert_compatible_before_run
from tests.virtual_cell.fixtures import build_approved_ppc_knockout_design, build_out_of_domain_design, build_unapproved_design

_ENV = {"medium": "M9_minimal", "carbon_source": "glucose"}
_CHASSIS = {"organism": "Escherichia coli", "strain": "K-12 MG1655"}


def test_unapproved_design_version_cannot_be_compiled():
    with db.session_scope() as s:
        proj, dv = build_unapproved_design(s)
        with pytest.raises(vc_service.SimulationGuardError):
            vc_service.open_simulation_case(s, project_id=proj.project_id, design_version_id=dv.design_version_id, requested_by="agent")


def test_out_of_domain_design_never_reaches_a_run():
    with db.session_scope() as s:
        proj, dv = build_out_of_domain_design(s)
        result = vc_service.run_prediction_pipeline(
            s, project_id=proj.project_id, design_version_id=dv.design_version_id, chassis=_CHASSIS, environment=_ENV, actor_id="agent",
        )
        assert result["case"].status == "out_of_domain"
        assert result["baseline_run"] is None
        assert result["candidate_run"] is None


def test_infeasible_baseline_blocks_any_delta():
    """Contradictory reaction bounds make the LP infeasible/erroring - the
    guard must refuse to produce a counterfactual delta from it."""
    with db.session_scope() as s:
        proj, dv = build_approved_ppc_knockout_design(s)
        case = vc_service.open_simulation_case(s, project_id=proj.project_id, design_version_id=dv.design_version_id, requested_by="agent")
        run, result = runner_mod.run_gem_fba_scenario(
            s, simulation_case_id=case.simulation_case_id, scenario_label="S0_baseline", baseline_state_id="SNAP-x",
            perturbation_ids=[], compiled_intervention_ids=[], reaction_bounds={"EX_glc__D_e": {"lower": 5, "upper": -5}},
        )
        assert run.status == "error"
        assert result is None
        with pytest.raises(SimulationGuardError):
            assert_baseline_succeeded_before_delta(run)


def test_unavailable_model_never_produces_a_run_record_with_fabricated_output():
    with db.session_scope() as s:
        proj, dv = build_approved_ppc_knockout_design(s)
        case = vc_service.open_simulation_case(s, project_id=proj.project_id, design_version_id=dv.design_version_id, requested_by="agent")
        perturbations = vc_service.extract_perturbations(s, case=case, design_version=dv, actor_id="agent")
        report = vc_service.run_compatibility_check(
            s, case=case, model_id="MREG-vecoli", cell_state_id="SNAP-x", chassis=_CHASSIS, perturbations=perturbations, actor_id="agent",
        )
        assert report.decision == "unavailable"
        with pytest.raises(SimulationGuardError):
            assert_compatible_before_run(report)


def test_unit_mismatch_endpoint_is_flagged_not_silently_compared():
    with db.session_scope() as s:
        proj, dv = build_approved_ppc_knockout_design(s)
        case = vc_service.open_simulation_case(s, project_id=proj.project_id, design_version_id=dv.design_version_id, requested_by="agent")
        from harness.virtual_cell.cell_state_service import build_baseline_cell_state

        baseline_state = build_baseline_cell_state(s, project_id=proj.project_id, design_version=dv, chassis=_CHASSIS, environment=_ENV, actor_id="agent")
        baseline_run, baseline_result = runner_mod.run_gem_fba_scenario(
            s, simulation_case_id=case.simulation_case_id, scenario_label="S0_baseline", baseline_state_id=baseline_state.snapshot_id,
            perturbation_ids=[], compiled_intervention_ids=[], reaction_bounds={},
        )
        # A distinct, independent stand-in for a hypothetical second
        # model's result with a mismatched unit for the same named
        # endpoint - never averaged/diffed blindly against the baseline.
        import copy as _copy
        import types

        candidate_result = types.SimpleNamespace(endpoints=_copy.deepcopy(baseline_result.endpoints))
        candidate_result.endpoints[0]["unit"] = "mmol/L"  # was "1/h"
        comparison = compare_runs(
            simulation_case_id=case.simulation_case_id, baseline_run=baseline_run, baseline_result=baseline_result,
            candidate_run=baseline_run, candidate_result=candidate_result,
        )
        growth = next(e for e in comparison.endpoints if e["name"] == "growth_rate")
        assert growth["delta"] is None
        assert "unit mismatch" in growth["rejected_reason"]


def test_no_perturbations_yields_needs_input_not_a_silent_noop():
    with db.session_scope() as s:
        from harness.designs.service import approve_design_version, propose_design_version
        from harness.projects import service as proj_svc

        proj = proj_svc.create_project(s, name="empty", host_definition={"species": "Escherichia coli"}, target_product="none", actor_id="pi")
        dv = propose_design_version(
            s, project_id=proj.project_id, version_label="v1", parent_version_ids=[], branch_name="main",
            genotype_manifest={"baseline_strain": "K-12", "modifications": []}, decisions=[], proposed_by="pi",
        )
        dv = approve_design_version(s, design_version_id=dv.design_version_id, approver_id="approver", expected_project_version=proj.version)
        result = vc_service.run_prediction_pipeline(
            s, project_id=proj.project_id, design_version_id=dv.design_version_id, chassis=_CHASSIS, environment=_ENV, actor_id="agent",
        )
        assert result["case"].status == "needs_input"


def test_failed_run_is_persisted_never_discarded():
    with db.session_scope() as s:
        proj, dv = build_approved_ppc_knockout_design(s)
        case = vc_service.open_simulation_case(s, project_id=proj.project_id, design_version_id=dv.design_version_id, requested_by="agent")
        run, _ = runner_mod.run_gem_fba_scenario(
            s, simulation_case_id=case.simulation_case_id, scenario_label="S0_baseline", baseline_state_id="SNAP-x",
            perturbation_ids=[], compiled_intervention_ids=[], reaction_bounds={"EX_glc__D_e": {"lower": 5, "upper": -5}},
        )
        run_id = run.model_run_id

    with db.session_scope() as s2:
        from harness.virtual_cell.models import SimulationRun

        persisted = s2.get(SimulationRun, run_id)
        assert persisted is not None
        assert persisted.status == "error"
        assert persisted.failure_reason is not None
