"""Problem 06 (Predictive Simulation Loop & Virtual Cell Integration) API
routes (doc06 §11). Every route calls the same service functions the unit/
integration tests exercise; no business logic lives here.
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from harness.api.deps import get_db_session
from harness.virtual_cell import registry as registry_mod
from harness.virtual_cell import router as router_mod
from harness.virtual_cell import service as vc_service
from harness.virtual_cell.cell_state_service import cell_state_to_dict, get_cell_state
from harness.virtual_cell.guards import SimulationGuardError
from harness.virtual_cell.models import (
    CompatibilityReport,
    CompiledIntervention,
    CounterfactualComparison,
    ModelUpdateProposal,
    PerturbationSpec,
    PredictionResidual,
    PredictionReview,
    SimulationRun,
    ValidationPlanItem,
)

router = APIRouter(prefix="/api/virtual-cell", tags=["virtual-cell"])


def _case_dict(c) -> dict[str, Any]:
    return {
        "simulation_case_id": c.simulation_case_id, "project_id": c.project_id, "design_version_id": c.design_version_id,
        "evaluation_reference": c.evaluation_reference, "status": c.status, "stop_reason": c.stop_reason,
        "baseline_cell_state_id": c.baseline_cell_state_id, "model_id": c.model_id, "router_rationale": c.router_rationale,
        "created_at": c.created_at, "updated_at": c.updated_at,
    }


def _run_dict(r: SimulationRun) -> dict[str, Any]:
    return {
        "model_run_id": r.model_run_id, "scenario_label": r.scenario_label, "model_id": r.model_id, "model_version": r.model_version,
        "artifact_hash": r.artifact_hash, "status": r.status, "simulation_config": r.simulation_config, "log_summary": r.log_summary,
        "failure_reason": r.failure_reason, "normalized_result_id": r.normalized_result_id, "runtime_s": r.runtime_s,
    }


def _comparison_dict(c: CounterfactualComparison) -> dict[str, Any]:
    return {
        "comparison_id": c.comparison_id, "baseline_run_id": c.baseline_run_id, "candidate_run_id": c.candidate_run_id,
        "comparability_status": c.comparability_status, "comparability_violations": c.comparability_violations,
        "endpoints": c.endpoints, "missing_endpoints": c.missing_endpoints, "robustness": c.robustness,
    }


def _compatibility_dict(r: CompatibilityReport) -> dict[str, Any]:
    return {
        "compatibility_id": r.compatibility_id, "model_id": r.model_id, "decision": r.decision,
        "organism_match": r.organism_match, "strain_match": r.strain_match, "perturbation_support": r.perturbation_support,
        "output_coverage": r.output_coverage, "blocking_reasons": r.blocking_reasons, "non_blocking_assumptions": r.non_blocking_assumptions,
    }


def _compiled_dict(c: CompiledIntervention) -> dict[str, Any]:
    return {
        "compiled_intervention_id": c.compiled_intervention_id, "perturbation_id": c.perturbation_id,
        "resolved_gene_id": c.resolved_gene_id, "affected_reactions": c.affected_reactions, "new_bounds": c.new_bounds,
        "mapping_status": c.mapping_status, "mapping_assumptions": c.mapping_assumptions, "mapping_uncertainty": c.mapping_uncertainty,
        "unsupported_inference": c.unsupported_inference, "status": c.status, "rejection_reason": c.rejection_reason,
    }


def _review_dict(r: PredictionReview) -> dict[str, Any]:
    return {
        "review_id": r.review_id, "comparison_id": r.comparison_id, "findings": r.findings,
        "model_derived_endpoints": r.model_derived_endpoints, "not_modeled_endpoints": r.not_modeled_endpoints,
        "mapping_status_summary": r.mapping_status_summary, "decision": r.decision,
    }


def _validation_item_dict(v: ValidationPlanItem) -> dict[str, Any]:
    return {
        "validation_item_id": v.validation_item_id, "endpoint": v.endpoint, "assay": v.assay, "unit": v.unit,
        "expected_direction": v.expected_direction, "expected_interval": v.expected_interval,
        "falsification_condition": v.falsification_condition, "alternative_explanations": v.alternative_explanations, "status": v.status,
    }


# -- Model registry ----------------------------------------------------------


@router.get("/models")
def list_models(session: Session = Depends(get_db_session)) -> dict:
    entries = registry_mod.list_registry_entries(session)
    return {"models": [
        {
            "model_id": e.model_id, "model_name": e.model_name, "model_type": e.model_type, "model_version": e.model_version,
            "organism": e.organism, "strains": e.strains, "supported_perturbations": e.supported_perturbations,
            "known_failure_modes": e.known_failure_modes, "availability_status": e.availability_status,
            "unavailability_reason": e.unavailability_reason,
        }
        for e in entries
    ]}


class RouteQuestionBody(BaseModel):
    question_type: str


@router.post("/models/route")
def route_question(body: RouteQuestionBody, session: Session = Depends(get_db_session)) -> dict:
    try:
        return router_mod.route(session, question_type=body.question_type)
    except ValueError as e:
        raise HTTPException(422, str(e))


# -- Cell state ---------------------------------------------------------------


@router.get("/cell-states/{cell_state_id}")
def get_cell_state_route(cell_state_id: str, session: Session = Depends(get_db_session)) -> dict:
    snap = get_cell_state(session, cell_state_id)
    if snap is None:
        raise HTTPException(404, "no such cell state")
    return cell_state_to_dict(snap)


# -- Simulation case lifecycle ------------------------------------------------


class OpenCaseBody(BaseModel):
    project_id: str
    design_version_id: str
    requested_by: str
    evaluation_reference: str | None = None


@router.post("/simulation-cases")
def open_case(body: OpenCaseBody, session: Session = Depends(get_db_session)) -> dict:
    try:
        case = vc_service.open_simulation_case(
            session, project_id=body.project_id, design_version_id=body.design_version_id,
            requested_by=body.requested_by, evaluation_reference=body.evaluation_reference,
        )
    except SimulationGuardError as e:
        raise HTTPException(422, str(e))
    return _case_dict(case)


@router.get("/simulation-cases/{simulation_case_id}")
def get_case_route(simulation_case_id: str, session: Session = Depends(get_db_session)) -> dict:
    case = vc_service.get_case(session, simulation_case_id)
    if case is None:
        raise HTTPException(404, "no such simulation case")
    return _case_dict(case)


@router.get("/simulation-cases/{simulation_case_id}/transitions")
def get_case_transitions(simulation_case_id: str, session: Session = Depends(get_db_session)) -> dict:
    transitions = vc_service.list_transitions(session, simulation_case_id)
    return {"transitions": [{"from_state": t.from_state, "to_state": t.to_state, "reason": t.reason, "created_at": t.created_at} for t in transitions]}


class RunPredictionBody(BaseModel):
    project_id: str
    design_version_id: str
    chassis: dict[str, Any]
    environment: dict[str, Any]
    model_id: str = "MREG-gem_fba"
    actor_id: str
    evaluation_reference: str | None = None
    human_override: dict[str, Any] | None = None


@router.post("/simulations")
def run_prediction(body: RunPredictionBody, session: Session = Depends(get_db_session)) -> dict:
    """doc06 §11.1's `POST /simulations`: runs the full doc06 §1.3 vertical
    slice (baseline + intervention + comparison + review + validation
    plan) for one formal DesignVersion in a single call."""
    try:
        result = vc_service.run_prediction_pipeline(
            session, project_id=body.project_id, design_version_id=body.design_version_id, chassis=body.chassis,
            environment=body.environment, model_id=body.model_id, actor_id=body.actor_id,
            evaluation_reference=body.evaluation_reference, human_override=body.human_override,
        )
    except SimulationGuardError as e:
        raise HTTPException(422, str(e))
    return {
        "case": _case_dict(result["case"]),
        "compatibility": _compatibility_dict(result["compatibility"]) if result.get("compatibility") else None,
        "compiled": [_compiled_dict(c) for c in result.get("compiled", [])],
        "baseline_run": _run_dict(result["baseline_run"]) if result.get("baseline_run") else None,
        "candidate_run": _run_dict(result["candidate_run"]) if result.get("candidate_run") else None,
        "comparison": _comparison_dict(result["comparison"]) if result.get("comparison") else None,
        "review": _review_dict(result["review"]) if result.get("review") else None,
        "validation_items": [_validation_item_dict(v) for v in result.get("validation_items", [])],
    }


@router.get("/simulations/{run_id}")
def get_run(run_id: str, session: Session = Depends(get_db_session)) -> dict:
    run = session.get(SimulationRun, run_id)
    if run is None:
        raise HTTPException(404, "no such simulation run")
    return _run_dict(run)


@router.get("/simulations/{run_id}/artifacts")
def get_run_artifacts(run_id: str, session: Session = Depends(get_db_session)) -> dict:
    run = session.get(SimulationRun, run_id)
    if run is None:
        raise HTTPException(404, "no such simulation run")
    return {
        "model_run_id": run.model_run_id, "simulation_config": run.simulation_config, "inputs_hash": run.inputs_hash,
        "raw_output_ref": run.raw_output_ref, "log_summary": run.log_summary, "started_at": run.started_at, "finished_at": run.finished_at,
    }


# -- Comparisons / reviews / validation ---------------------------------------


@router.get("/comparisons/{comparison_id}")
def get_comparison(comparison_id: str, session: Session = Depends(get_db_session)) -> dict:
    c = session.get(CounterfactualComparison, comparison_id)
    if c is None:
        raise HTTPException(404, "no such comparison")
    return _comparison_dict(c)


@router.get("/simulation-cases/{simulation_case_id}/validation-plan")
def get_validation_plan(simulation_case_id: str, session: Session = Depends(get_db_session)) -> dict:
    items = list(session.execute(select(ValidationPlanItem).where(ValidationPlanItem.simulation_case_id == simulation_case_id)).scalars())
    return {"items": [_validation_item_dict(v) for v in items]}


# -- Observations / residuals / update proposals (Phase 3) --------------------


class RecordObservationLinkBody(BaseModel):
    simulation_case_id: str
    validation_item_id: str
    observation_id: str
    actor_id: str


@router.post("/residuals")
def compute_residual_route(body: RecordObservationLinkBody, session: Session = Depends(get_db_session)) -> dict:
    from harness.virtual_cell import residual_service

    try:
        residual = residual_service.compute_residual(
            session, simulation_case_id=body.simulation_case_id, validation_item_id=body.validation_item_id,
            observation_id=body.observation_id, actor_id=body.actor_id,
        )
    except (ValueError, SimulationGuardError) as e:
        raise HTTPException(422, str(e))
    return {
        "residual_id": residual.residual_id, "endpoint": residual.endpoint, "predicted_value": residual.predicted_value,
        "observed_value": residual.observed_value, "residual": residual.residual, "relative_error": residual.relative_error,
        "context_match": residual.context_match, "mismatch_status": residual.mismatch_status,
    }


class CreateUpdateProposalBody(BaseModel):
    project_id: str
    residual_ids: list[str]
    update_level: str
    rationale: str
    required_data: list[str] = []
    validation_plan: str = ""
    rollback_plan: str = ""
    actor_id: str


@router.post("/model-update-proposals")
def create_update_proposal(body: CreateUpdateProposalBody, session: Session = Depends(get_db_session)) -> dict:
    from harness.virtual_cell import update_service

    try:
        proposal = update_service.propose_update(
            session, project_id=body.project_id, residual_ids=body.residual_ids, update_level=body.update_level,
            rationale=body.rationale, required_data=body.required_data, validation_plan=body.validation_plan,
            rollback_plan=body.rollback_plan, actor_id=body.actor_id,
        )
    except ValueError as e:
        raise HTTPException(422, str(e))
    return {"proposal_id": proposal.proposal_id, "update_level": proposal.update_level, "status": proposal.status, "human_approval_required": proposal.human_approval_required}


class DecideUpdateProposalBody(BaseModel):
    decision: str
    approver_id: str
    approver_role: str = ""
    rationale: str = ""
    conditions: list[str] = []


@router.post("/model-update-proposals/{proposal_id}/decision")
def decide_update_proposal(proposal_id: str, body: DecideUpdateProposalBody, session: Session = Depends(get_db_session)) -> dict:
    from harness.virtual_cell import update_service

    proposal = session.get(ModelUpdateProposal, proposal_id)
    if proposal is None:
        raise HTTPException(404, "no such update proposal")
    try:
        decision = update_service.decide_update(
            session, proposal=proposal, decision=body.decision, approver_id=body.approver_id,
            approver_role=body.approver_role, rationale=body.rationale, conditions=body.conditions,
        )
    except (ValueError, SimulationGuardError) as e:
        raise HTTPException(422, str(e))
    return {"decision_id": decision.decision_id, "decision": decision.decision, "proposal_status": proposal.status}


# -- Benchmarks / calibration (Phase 3) ---------------------------------------


@router.get("/models/{model_id}/benchmarks")
def get_benchmarks(model_id: str, session: Session = Depends(get_db_session)) -> dict:
    from harness.virtual_cell.models import ModelBenchmarkRecord

    rows = list(session.execute(select(ModelBenchmarkRecord).where(ModelBenchmarkRecord.model_id == model_id)).scalars())
    return {"benchmarks": [
        {
            "benchmark_record_id": r.benchmark_record_id, "endpoint": r.endpoint, "split_type": r.split_type,
            "sample_count": r.sample_count, "metrics": r.metrics, "status": r.status, "perturbation_class": r.perturbation_class,
        }
        for r in rows
    ]}


class BenchmarkEvaluateBody(BaseModel):
    model_id: str
    endpoint: str
    split_type: str
    residual_ids: list[str]
    benchmark_dataset_id: str
    benchmark_dataset_version: str
    evaluation_protocol_id: str
    organism: str = "Escherichia coli"
    strain: str = "K-12"
    condition: dict[str, Any] = {}
    perturbation_class: str = "gene_deletion"


@router.post("/benchmarks/evaluate")
def evaluate_benchmark(body: BenchmarkEvaluateBody, session: Session = Depends(get_db_session)) -> dict:
    from harness.virtual_cell import benchmark_service

    try:
        record = benchmark_service.evaluate_benchmark(
            session, model_id=body.model_id, endpoint=body.endpoint, split_type=body.split_type, residual_ids=body.residual_ids,
            benchmark_dataset_id=body.benchmark_dataset_id, benchmark_dataset_version=body.benchmark_dataset_version,
            evaluation_protocol_id=body.evaluation_protocol_id, organism=body.organism, strain=body.strain,
            condition=body.condition, perturbation_class=body.perturbation_class,
        )
    except ValueError as e:
        raise HTTPException(422, str(e))
    return {"benchmark_record_id": record.benchmark_record_id, "metrics": record.metrics, "sample_count": record.sample_count, "status": record.status}


@router.get("/models/{model_id}/calibration-profiles")
def get_calibration_profiles(model_id: str, session: Session = Depends(get_db_session)) -> dict:
    from harness.virtual_cell.models import PredictionCalibrationProfile

    rows = list(session.execute(select(PredictionCalibrationProfile).where(PredictionCalibrationProfile.model_id == model_id)).scalars())
    return {"profiles": [
        {
            "calibration_profile_id": p.calibration_profile_id, "endpoint": p.endpoint, "sample_count": p.sample_count,
            "minimum_sample_requirement": p.minimum_sample_requirement, "metrics": p.metrics,
            "reliability_status": p.reliability_status, "status": p.status,
        }
        for p in rows
    ]}


class BuildCalibrationProfileBody(BaseModel):
    model_id: str
    endpoint: str
    residual_ids: list[str]
    calibration_dataset_version: str
    minimum_sample_requirement: int = 5


@router.post("/calibration-profiles/build")
def build_calibration_profile(body: BuildCalibrationProfileBody, session: Session = Depends(get_db_session)) -> dict:
    from harness.virtual_cell import calibration_service

    try:
        profile = calibration_service.build_calibration_profile(
            session, model_id=body.model_id, endpoint=body.endpoint, residual_ids=body.residual_ids,
            calibration_dataset_version=body.calibration_dataset_version, minimum_sample_requirement=body.minimum_sample_requirement,
        )
    except ValueError as e:
        raise HTTPException(422, str(e))
    return {
        "calibration_profile_id": profile.calibration_profile_id, "sample_count": profile.sample_count,
        "reliability_status": profile.reliability_status, "metrics": profile.metrics,
    }


class ReviewCalibrationProfileBody(BaseModel):
    approver_id: str


@router.post("/calibration-profiles/{profile_id}/review")
def review_calibration_profile(profile_id: str, body: ReviewCalibrationProfileBody, session: Session = Depends(get_db_session)) -> dict:
    from harness.virtual_cell import calibration_service
    from harness.virtual_cell.models import PredictionCalibrationProfile

    profile = session.get(PredictionCalibrationProfile, profile_id)
    if profile is None:
        raise HTTPException(404, "no such calibration profile")
    calibration_service.approve_profile(session, profile=profile, approver_id=body.approver_id)
    return {"calibration_profile_id": profile.calibration_profile_id, "approved_by": profile.approved_by}
