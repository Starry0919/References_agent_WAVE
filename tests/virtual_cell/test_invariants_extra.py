"""Remaining doc06 §14.1 scientific invariants not already covered by
`test_compiler.py` / `test_compatibility.py` / `test_pipeline_e2e.py` /
`test_guards_and_failure_paths.py` / `test_reviewer.py` / `test_router.py` /
`test_phase3_feedback_loop.py`.
"""
from __future__ import annotations

import pytest

from harness import db
from harness.db import ImmutableFieldError
from harness.virtual_cell import residual_service, router as router_mod, service as vc_service
from harness.virtual_cell.guards import SimulationGuardError
from harness.virtual_cell.models import CompiledIntervention, SimulationResult
from tests.virtual_cell.fixtures import build_approved_ppc_knockout_design
from tests.virtual_cell.test_phase3_feedback_loop import _make_observation

_ENV = {"medium": "M9_minimal", "carbon_source": "glucose"}
_CHASSIS = {"organism": "Escherichia coli", "strain": "K-12 MG1655"}


def test_unknown_physiology_fields_are_never_auto_filled():
    """doc06 §2.2: a CellStateSnapshot field with no supplied value must be
    'unknown', never interpolated/guessed."""
    with db.session_scope() as s:
        proj, dv = build_approved_ppc_knockout_design(s)
        from harness.virtual_cell.cell_state_service import build_baseline_cell_state

        snap = build_baseline_cell_state(s, project_id=proj.project_id, design_version=dv, chassis=_CHASSIS, environment=_ENV, actor_id="agent")
        # No physiology values were supplied - every physiology field must
        # be recorded unknown/missing, never defaulted to 0 or copied from
        # elsewhere.
        for field in ("growth_rate", "biomass", "substrate_uptake", "product_titer", "product_yield", "productivity", "stress_state"):
            assert snap.field_provenance[f"physiology.{field}"] == "unknown"
            assert f"physiology.{field}" in snap.missing_modalities
        assert snap.physiology == {}
        assert snap.quality_status == "degraded"


def test_unit_mismatched_observation_blocks_residual_computation():
    with db.session_scope() as s:
        proj, dv = build_approved_ppc_knockout_design(s)
        result = vc_service.run_prediction_pipeline(
            s, project_id=proj.project_id, design_version_id=dv.design_version_id, chassis=_CHASSIS, environment=_ENV, actor_id="agent",
        )
        growth_item = next(v for v in result["validation_items"] if v.endpoint == "growth_rate")
        # growth_rate's predicted unit is "1/h"; report the observation in a mismatched unit.
        obs = _make_observation(s, project_id=proj.project_id, value=0.55, unit="mmol/gDW/h")
        with pytest.raises(SimulationGuardError):
            residual_service.compute_residual(
                s, simulation_case_id=result["case"].simulation_case_id, validation_item_id=growth_item.validation_item_id,
                observation_id=obs.observation_id, actor_id="agent",
            )


def test_gem_fba_endpoint_uncertainty_never_reports_a_fake_calibrated_confidence():
    with db.session_scope() as s:
        proj, dv = build_approved_ppc_knockout_design(s)
        result = vc_service.run_prediction_pipeline(
            s, project_id=proj.project_id, design_version_id=dv.design_version_id, chassis=_CHASSIS, environment=_ENV, actor_id="agent",
        )
        candidate_result = result["candidate_result"]
        for endpoint_name, u in candidate_result.endpoint_uncertainty.items():
            assert u["confidence_status"] == "unavailable"
            assert "not_applicable" in u["stochastic_variability"] or "deterministic" in u["stochastic_variability"]


def test_compiled_intervention_is_append_only():
    with db.session_scope() as s:
        proj, dv = build_approved_ppc_knockout_design(s)
        result = vc_service.run_prediction_pipeline(
            s, project_id=proj.project_id, design_version_id=dv.design_version_id, chassis=_CHASSIS, environment=_ENV, actor_id="agent",
        )
        ci = result["compiled"][0]
        ci.new_bounds = {"PPC": {"lower": -5, "upper": 5}}  # tamper attempt
        with pytest.raises(ImmutableFieldError):
            s.flush()
        s.rollback()  # leave the session usable for session_scope()'s own final commit


def test_simulation_result_is_fully_immutable():
    with db.session_scope() as s:
        proj, dv = build_approved_ppc_knockout_design(s)
        result = vc_service.run_prediction_pipeline(
            s, project_id=proj.project_id, design_version_id=dv.design_version_id, chassis=_CHASSIS, environment=_ENV, actor_id="agent",
        )
        sim_result = result["candidate_result"]
        sim_result.endpoints = []  # tamper attempt: try to erase model output
        with pytest.raises(ImmutableFieldError):
            s.flush()
        s.rollback()  # leave the session usable for session_scope()'s own final commit


def test_router_benchmark_ranking_cannot_change_selection_or_bypass_compatibility():
    with db.session_scope() as s:
        decision_plain = router_mod.route(s, question_type="steady_state_flux")
        decision_ranked = router_mod.route(s, question_type="steady_state_flux", benchmark_ranking={"MREG-vecoli": 0.99, "MREG-gem_fba": 0.1})
        # A benchmark ranking favoring an unavailable model must not change
        # which model is actually selected - only order among compatible ones.
        assert decision_plain["selected_model_id"] == decision_ranked["selected_model_id"] == "MREG-gem_fba"
