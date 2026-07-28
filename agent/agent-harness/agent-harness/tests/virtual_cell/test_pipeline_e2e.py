"""End-to-end vertical slice (doc06 §1.3/§14.2): one formal DesignVersion
-> baseline cell state -> single-gene perturbation -> real gem_fba adapter
-> baseline + intervention runs -> normalized results -> counterfactual
comparison. Every number asserted here is cross-checked against an
independent, direct cobrapy computation - never hardcoded to "whatever the
pipeline happens to produce".
"""
from __future__ import annotations

from harness import db
from harness.virtual_cell import service as vc_service
from tests.virtual_cell.fixtures import build_approved_ppc_knockout_design

_ENV = {"medium": "M9_minimal", "carbon_source": "glucose", "oxygenation": "aerobic", "temperature_c": 37}
_CHASSIS = {"organism": "Escherichia coli", "strain": "K-12 MG1655"}


def _independent_ppc_knockout_growth() -> tuple[float, float]:
    """Recomputes baseline and ppc-knockout growth directly via cobrapy,
    independent of any Problem 06 code, as ground truth to compare against."""
    import cobra
    from cobra.io import load_model

    model = load_model("textbook")
    baseline = model.optimize().objective_value
    m2 = model.copy()
    m2.reactions.get_by_id("PPC").bounds = (0, 0)
    knockout = m2.optimize().objective_value
    return baseline, knockout


def test_full_prediction_pipeline_produces_a_real_comparable_counterfactual():
    expected_baseline, expected_knockout = _independent_ppc_knockout_growth()

    with db.session_scope() as s:
        proj, dv = build_approved_ppc_knockout_design(s)
        result = vc_service.run_prediction_pipeline(
            s, project_id=proj.project_id, design_version_id=dv.design_version_id, chassis=_CHASSIS, environment=_ENV, actor_id="agent",
        )

        case = result["case"]
        assert case.status in ("comparison_ready", "prediction_under_review", "validation_planned", "awaiting_observation")
        assert result["compatibility"].decision in ("compatible", "compatible_with_assumptions")
        assert result["compiled"][0].status == "compiled"
        assert result["compiled"][0].affected_reactions == ["PPC"]

        baseline_run = result["baseline_run"]
        candidate_run = result["candidate_run"]
        assert baseline_run.status == "optimal"
        assert candidate_run.status == "optimal"
        assert baseline_run.scenario_label == "S0_baseline"
        assert candidate_run.scenario_label == "S1_intervention"

        assert any(e["name"] == "growth_rate" for e in result["baseline_result"].endpoints)
        growth_endpoint = next(e for e in result["baseline_result"].endpoints if e["name"] == "growth_rate")
        assert abs(growth_endpoint["value"] - expected_baseline) < 1e-9
        assert growth_endpoint["source_type"] == "model_output"

        candidate_growth = next(e for e in result["candidate_result"].endpoints if e["name"] == "growth_rate")
        assert abs(candidate_growth["value"] - expected_knockout) < 1e-9

        comparison = result["comparison"]
        assert comparison.comparability_status == "comparable"
        growth_cf = next(e for e in comparison.endpoints if e["name"] == "growth_rate")
        assert abs(growth_cf["baseline_value"] - expected_baseline) < 1e-9
        assert abs(growth_cf["candidate_value"] - expected_knockout) < 1e-9
        assert growth_cf["delta"] < 0  # ppc knockout reduces growth in this model
        assert growth_cf["relative_change"] is not None

        # doc06 §6.3: endpoints the model genuinely does not cover must be
        # visibly not_modeled, never silently absent.
        not_modeled_names = {e["name"] for e in comparison.endpoints if e["not_modeled"]}
        assert "product_titer" in not_modeled_names
        assert "biomass" in not_modeled_names

        # doc06 §8: independent prediction review + doc06 §9.1: validation plan
        review = result["review"]
        assert review is not None
        assert not any(f["severity"] == "blocking" for f in review.findings)
        assert review.decision in ("decision_ready", "limited_acceptance")
        assert "growth_rate" in review.model_derived_endpoints
        assert result["validation_items"]
        growth_item = next(v for v in result["validation_items"] if v.endpoint == "growth_rate")
        assert growth_item.expected_direction == "decrease"
        assert growth_item.falsification_condition


def test_idempotent_rerun_reuses_existing_run_not_a_second_execution():
    with db.session_scope() as s:
        proj, dv = build_approved_ppc_knockout_design(s)
        case = vc_service.open_simulation_case(s, project_id=proj.project_id, design_version_id=dv.design_version_id, requested_by="agent")
        from harness.virtual_cell.cell_state_service import build_baseline_cell_state
        from harness.virtual_cell import runner as runner_mod

        baseline_state = build_baseline_cell_state(s, project_id=proj.project_id, design_version=dv, chassis=_CHASSIS, environment=_ENV, actor_id="agent")
        run_a, _ = runner_mod.run_gem_fba_scenario(
            s, simulation_case_id=case.simulation_case_id, scenario_label="S0_baseline", baseline_state_id=baseline_state.snapshot_id,
            perturbation_ids=[], compiled_intervention_ids=[], reaction_bounds={},
        )
        run_b, _ = runner_mod.run_gem_fba_scenario(
            s, simulation_case_id=case.simulation_case_id, scenario_label="S0_baseline", baseline_state_id=baseline_state.snapshot_id,
            perturbation_ids=[], compiled_intervention_ids=[], reaction_bounds={},
        )
        assert run_a.model_run_id == run_b.model_run_id
