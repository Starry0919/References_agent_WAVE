"""Phase 3 end-to-end: prediction -> real experimental observation ->
code-computed residual -> governed ModelUpdateProposal (+ Human Gate for
Level 3-5) -> ModelBenchmarkRecord -> PredictionCalibrationProfile
(doc06 §9). Reuses `harness.experiments.models.Observation` directly for
the observation (doc06 §3.10's OmicsObservation mapped onto the existing
table, not duplicated).
"""
from __future__ import annotations

import pytest

from harness import db
from harness.experiments.models import Observation
from harness.ids import new_id, now
from harness.virtual_cell import benchmark_service, calibration_service, residual_service, service as vc_service, update_service
from harness.virtual_cell.guards import SimulationGuardError
from harness.virtual_cell.models import ModelUpdateProposal
from tests.virtual_cell.fixtures import build_approved_ppc_knockout_design

_ENV = {"medium": "M9_minimal", "carbon_source": "glucose"}
_CHASSIS = {"organism": "Escherichia coli", "strain": "K-12 MG1655"}


def _make_observation(session, *, project_id: str, value: float, unit: str = "1/h", qc_status: str = "passed", condition_ref: dict | None = None) -> Observation:
    obs = Observation(
        observation_id=new_id("OBS"), project_id=project_id, data_asset_ids=[], subject_design_version_id=None,
        subject_construct_id=None, condition_ref=condition_ref if condition_ref is not None else dict(_ENV),
        timepoint={"value": 6, "unit": "h", "phase": "exponential"}, metric="growth_rate", value=value, unit=unit,
        uncertainty=0.01, replicate_summary={"n": 3, "mean": value, "sd": 0.01, "cv": 0.01}, qc_flags=[], qc_status=qc_status,
        analysis_pipeline_version="v1", source_type="instrument", created_at=now(),
    )
    session.add(obs)
    session.flush()
    return obs


def test_full_feedback_loop_prediction_to_governed_update_proposal():
    with db.session_scope() as s:
        proj, dv = build_approved_ppc_knockout_design(s)
        result = vc_service.run_prediction_pipeline(
            s, project_id=proj.project_id, design_version_id=dv.design_version_id, chassis=_CHASSIS, environment=_ENV, actor_id="agent",
        )
        assert result["review"].decision in ("decision_ready", "limited_acceptance")
        growth_item = next(v for v in result["validation_items"] if v.endpoint == "growth_rate")

        predicted_growth = growth_item.expected_interval["point_estimate"]
        # Real observed growth rate deviates meaningfully from the FBA
        # prediction (e.g. unmodeled regulation/compensation) - a genuine,
        # non-trivial residual, not a copy of the prediction.
        observed_growth = predicted_growth * 0.6
        obs = _make_observation(s, project_id=proj.project_id, value=observed_growth)

        residual = residual_service.compute_residual(
            s, simulation_case_id=result["case"].simulation_case_id, validation_item_id=growth_item.validation_item_id,
            observation_id=obs.observation_id, actor_id="agent",
        )
        assert residual.context_match is True
        assert abs(residual.residual - (observed_growth - predicted_growth)) < 1e-9
        assert residual.recommended_update_level in ("input_state", "parameter_calibration")

        proposal = update_service.propose_update(
            s, project_id=proj.project_id, residual_ids=[residual.residual_id], update_level="parameter_calibration",
            rationale="systematic overprediction of growth rate under ppc knockout", actor_id="agent",
        )
        assert proposal.status == "proposed"
        assert proposal.human_approval_required is True

        # Cannot activate without a Human Gate decision.
        with pytest.raises(SimulationGuardError):
            from harness.virtual_cell.guards import assert_update_may_activate

            assert_update_may_activate(proposal, has_human_approval=False)

        decision = update_service.decide_update(s, proposal=proposal, decision="approved", approver_id="pi", rationale="agreed, recalibrate")
        assert decision.decision == "approved"
        assert proposal.status == "approved"

        benchmark = benchmark_service.evaluate_benchmark(
            s, model_id="MREG-gem_fba", endpoint="growth_rate", split_type="prospective", residual_ids=[residual.residual_id],
            benchmark_dataset_id="ppc-ko-cohort-1", benchmark_dataset_version="v1", evaluation_protocol_id="proto-v1",
            organism="Escherichia coli", strain="K-12", condition=_ENV, perturbation_class="single_gene_deletion",
        )
        assert benchmark.sample_count == 1
        assert benchmark.metrics["mae"] is not None
        assert benchmark.status == "provisional"

        profile = calibration_service.build_calibration_profile(
            s, model_id="MREG-gem_fba", endpoint="growth_rate", residual_ids=[residual.residual_id],
            calibration_dataset_version="v1", minimum_sample_requirement=5,
        )
        assert profile.reliability_status == "insufficient_data"  # only 1 sample, honest downgrade
        calibration_service.approve_profile(s, profile=profile, approver_id="pi")
        assert profile.reliability_status == "insufficient_data"  # approval cannot force-upgrade an under-sampled profile


def test_context_mismatched_observation_never_produces_a_residual():
    with db.session_scope() as s:
        proj, dv = build_approved_ppc_knockout_design(s)
        result = vc_service.run_prediction_pipeline(
            s, project_id=proj.project_id, design_version_id=dv.design_version_id, chassis=_CHASSIS, environment=_ENV, actor_id="agent",
        )
        growth_item = next(v for v in result["validation_items"] if v.endpoint == "growth_rate")
        # Different medium than the prediction's cell state - context mismatch.
        obs = _make_observation(s, project_id=proj.project_id, value=0.5, condition_ref={"medium": "LB_rich", "carbon_source": "complex"})
        with pytest.raises(SimulationGuardError):
            residual_service.compute_residual(
                s, simulation_case_id=result["case"].simulation_case_id, validation_item_id=growth_item.validation_item_id,
                observation_id=obs.observation_id, actor_id="agent",
            )


def test_unqc_passed_observation_never_produces_a_residual():
    with db.session_scope() as s:
        proj, dv = build_approved_ppc_knockout_design(s)
        result = vc_service.run_prediction_pipeline(
            s, project_id=proj.project_id, design_version_id=dv.design_version_id, chassis=_CHASSIS, environment=_ENV, actor_id="agent",
        )
        growth_item = next(v for v in result["validation_items"] if v.endpoint == "growth_rate")
        obs = _make_observation(s, project_id=proj.project_id, value=0.5, qc_status="failed")
        with pytest.raises(SimulationGuardError):
            residual_service.compute_residual(
                s, simulation_case_id=result["case"].simulation_case_id, validation_item_id=growth_item.validation_item_id,
                observation_id=obs.observation_id, actor_id="agent",
            )


def test_benchmark_refuses_cross_endpoint_aggregation():
    with db.session_scope() as s:
        proj, dv = build_approved_ppc_knockout_design(s)
        result = vc_service.run_prediction_pipeline(
            s, project_id=proj.project_id, design_version_id=dv.design_version_id, chassis=_CHASSIS, environment=_ENV, actor_id="agent",
        )
        growth_item = next(v for v in result["validation_items"] if v.endpoint == "growth_rate")
        obs = _make_observation(s, project_id=proj.project_id, value=0.5)
        residual = residual_service.compute_residual(
            s, simulation_case_id=result["case"].simulation_case_id, validation_item_id=growth_item.validation_item_id,
            observation_id=obs.observation_id, actor_id="agent",
        )
        with pytest.raises(ValueError):
            benchmark_service.evaluate_benchmark(
                s, model_id="MREG-gem_fba", endpoint="substrate_uptake_glucose", split_type="prospective",
                residual_ids=[residual.residual_id], benchmark_dataset_id="x", benchmark_dataset_version="v1",
                evaluation_protocol_id="p1", organism="Escherichia coli", strain="K-12", condition=_ENV, perturbation_class="single_gene_deletion",
            )


def test_level1_update_may_be_auto_applied_without_human_gate():
    with db.session_scope() as s:
        proj, dv = build_approved_ppc_knockout_design(s)
        result = vc_service.run_prediction_pipeline(
            s, project_id=proj.project_id, design_version_id=dv.design_version_id, chassis=_CHASSIS, environment=_ENV, actor_id="agent",
        )
        growth_item = next(v for v in result["validation_items"] if v.endpoint == "growth_rate")
        obs = _make_observation(s, project_id=proj.project_id, value=0.86)  # small deviation
        residual = residual_service.compute_residual(
            s, simulation_case_id=result["case"].simulation_case_id, validation_item_id=growth_item.validation_item_id,
            observation_id=obs.observation_id, actor_id="agent",
        )
        proposal = update_service.propose_update(
            s, project_id=proj.project_id, residual_ids=[residual.residual_id], update_level="project_belief",
            rationale="minor deviation, record as project experience", actor_id="agent",
        )
        assert proposal.human_approval_required is False
        applied = update_service.auto_apply_level1(s, proposal=proposal, actor_id="agent")
        assert applied.status == "applied"


def test_level3_update_cannot_be_auto_applied():
    with db.session_scope() as s:
        proj, dv = build_approved_ppc_knockout_design(s)
        proposal = ModelUpdateProposal(
            proposal_id=new_id("MUP"), project_id=proj.project_id, triggering_residual_ids=["PRESID-fake"],
            update_level="parameter_calibration", rationale="test", required_data=[], identifiability_status="unknown",
            validation_plan="", rollback_plan="", human_approval_required=True, status="proposed", created_at=now(),
        )
        s.add(proposal)
        s.flush()
        with pytest.raises(SimulationGuardError):
            update_service.auto_apply_level1(s, proposal=proposal, actor_id="agent")
