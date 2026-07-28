"""Unified Scientific Workflow Orchestrator API routes (prompt §8.1). Every
route calls `harness.orchestrator.service.UnifiedScientificWorkflowOrchestrator`
- no business logic lives here, matching every other Problem's API router
convention in this repo (`harness/api/virtual_cell.py` etc).

Error mapping follows the same convention as the rest of this repo's API
(see README's API table): illegal phase transitions -> 409, stale-version
conflicts -> 409, gate/precondition rejections -> 422.
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from harness.api.deps import get_db_session
from harness.db import ConcurrencyConflictError
from harness.designs.service import SelfApprovalError
from harness.diagnosis.loop import DiagnosisGateRejectedError, IllegalDiagnosisTransitionError
from harness.engineering_design.handoff import HandoffRejectedError
from harness.engineering_design.loop import DesignGateRejectedError, IllegalDesignTransitionError
from harness.engineering_design.portfolio_service import PortfolioDiversityRejected
from harness.engineering_design.project_service import ObjectiveRejected
from harness.orchestrator import service as orch_service
from harness.orchestrator.models import ModuleHandoffRecord, OrchestratorGateDecision, OrchestratorTransition, UnifiedWorkflowRun
from harness.scientific_evaluation.human_gate import HumanGatePreconditionError
from harness.scientific_evaluation.loop import EvaluationGateRejectedError, IllegalEvaluationTransitionError
from harness.workflow.iterative_loop import GateRejectedError, IllegalCycleTransitionError

router = APIRouter(prefix="/api/orchestrator", tags=["orchestrator"])
ORC = orch_service.UnifiedScientificWorkflowOrchestrator()


def _run_dict(r: UnifiedWorkflowRun) -> dict[str, Any]:
    return {
        "workflow_run_id": r.workflow_run_id, "project_id": r.project_id, "objective_id": r.objective_id,
        "dbtl_iteration_id": r.dbtl_iteration_id, "status": r.status, "current_phase": r.current_phase,
        "current_module": r.current_module, "diagnosis_run_ref": r.diagnosis_run_ref,
        "diagnosis_handoff_ref": r.diagnosis_handoff_ref, "design_project_ref": r.design_project_ref,
        "design_version_ref": r.design_version_ref, "evaluation_run_ref": r.evaluation_run_ref,
        "simulation_campaign_ref": r.simulation_campaign_ref, "experiment_plan_ref": r.experiment_plan_ref,
        "experiment_run_ref": r.experiment_run_ref, "observation_set_ref": r.observation_set_ref,
        "active_gate_ref": r.active_gate_ref, "pause_reason": r.pause_reason, "blocked_reason": r.blocked_reason,
        "checkpoint_ref": r.checkpoint_ref, "correlation_id": r.correlation_id, "created_at": r.created_at,
        "updated_at": r.updated_at, "version": r.version,
    }


def _handle(fn, *args, **kwargs):
    """Every orchestrator route drives a whole underlying module's loop
    controller/service layer (`DiagnosisAdapter`, `DesignAdapter`, etc,
    harness/orchestrator/adapters.py) - any domain-specific rejection that
    module's OWN API routes already handle (harness/api/{diagnosis,
    engineering_design,scientific_evaluation,projects}.py) can just as
    easily bubble up through this parallel orchestrator entry point, which
    never caught them. Found via a real, reproducible 500: `POST .../design`
    with no primary_metrics raised `ObjectiveRejected` here uncaught.
    """
    try:
        return fn(*args, **kwargs)
    except ConcurrencyConflictError as e:
        raise HTTPException(409, str(e))
    except (
        orch_service.OrchestratorPhaseError,
        orch_service.CycleConflictError,
        IllegalDiagnosisTransitionError,
        IllegalDesignTransitionError,
        IllegalEvaluationTransitionError,
        IllegalCycleTransitionError,
        SelfApprovalError,
    ) as e:
        raise HTTPException(409, str(e))
    except (
        ValueError,
        orch_service.OrchestratorBlockedError,
        DiagnosisGateRejectedError,
        DesignGateRejectedError,
        EvaluationGateRejectedError,
        GateRejectedError,
        ObjectiveRejected,
        PortfolioDiversityRejected,
        HumanGatePreconditionError,
        HandoffRejectedError,
    ) as e:
        raise HTTPException(422, str(e))


class CreateRunBody(BaseModel):
    project_id: str
    actor_id: str
    target_product: str
    host: str
    dbtl_iteration_id: str | None = None


@router.post("/runs")
def create_run(body: CreateRunBody, session: Session = Depends(get_db_session)) -> dict:
    run = _handle(ORC.create_run, session, project_id=body.project_id, actor_id=body.actor_id, target_product=body.target_product, host=body.host, dbtl_iteration_id=body.dbtl_iteration_id)
    return _run_dict(run)


@router.get("/runs")
def list_runs(project_id: str, session: Session = Depends(get_db_session)) -> dict:
    """Lists every `UnifiedWorkflowRun` for a project, most-recently-updated
    first - closes the "frontend cannot discover a project's run on its
    own" gap this module's own docstring flagged (`frontend/src/api/
    orchestrator.ts`): WorkspaceEntry/WorkspaceLayout use this to resume the
    latest real run instead of always minting a new empty one."""
    from sqlalchemy import select

    rows = session.execute(
        select(UnifiedWorkflowRun).where(UnifiedWorkflowRun.project_id == project_id).order_by(UnifiedWorkflowRun.updated_at.desc())
    ).scalars().all()
    return {"runs": [_run_dict(r) for r in rows]}


@router.get("/runs/{workflow_run_id}")
def get_run(workflow_run_id: str, session: Session = Depends(get_db_session)) -> dict:
    try:
        run = ORC.get_status(session, workflow_run_id)
    except ValueError as e:
        raise HTTPException(404, str(e))
    return _run_dict(run)


@router.get("/runs/{workflow_run_id}/reconcile")
def reconcile_run(workflow_run_id: str, session: Session = Depends(get_db_session)) -> dict:
    try:
        return ORC.reconcile(session, workflow_run_id)
    except ValueError as e:
        raise HTTPException(404, str(e))


@router.get("/runs/{workflow_run_id}/audit-trail")
def audit_trail(workflow_run_id: str, session: Session = Depends(get_db_session)) -> dict:
    from sqlalchemy import select

    transitions = session.execute(select(OrchestratorTransition).where(OrchestratorTransition.workflow_run_id == workflow_run_id).order_by(OrchestratorTransition.created_at)).scalars().all()
    gates = session.execute(select(OrchestratorGateDecision).where(OrchestratorGateDecision.workflow_run_id == workflow_run_id).order_by(OrchestratorGateDecision.timestamp)).scalars().all()
    return {
        "transitions": [
            {"transition_id": t.transition_id, "from_phase": t.from_phase, "to_phase": t.to_phase, "reason": t.reason, "actor_id": t.actor_id, "created_at": t.created_at}
            for t in transitions
        ],
        "gate_decisions": [
            {"gate_decision_id": g.gate_decision_id, "gate_type": g.gate_type, "decision": g.decision, "blocking_findings": g.blocking_findings,
             "non_blocking_findings": g.non_blocking_findings, "required_actions": g.required_actions, "actor": g.actor, "timestamp": g.timestamp}
            for g in gates
        ],
    }


@router.get("/runs/{workflow_run_id}/handoffs")
def handoffs(workflow_run_id: str, session: Session = Depends(get_db_session)) -> dict:
    from sqlalchemy import select

    rows = session.execute(select(ModuleHandoffRecord).where(ModuleHandoffRecord.workflow_run_id == workflow_run_id).order_by(ModuleHandoffRecord.created_at)).scalars().all()
    return {
        "handoffs": [
            {"handoff_id": h.handoff_id, "source_module": h.source_module, "target_module": h.target_module, "payload_refs": h.payload_refs,
             "unresolved_items": h.unresolved_items, "warnings": h.warnings, "confidence_status": h.confidence_status, "created_at": h.created_at}
            for h in rows
        ]
    }


class StartDiagnosisBody(BaseModel):
    expected_version: int
    actor_id: str
    request: dict[str, Any]
    context: dict[str, Any] = {}


@router.post("/runs/{workflow_run_id}/diagnosis")
def start_diagnosis(workflow_run_id: str, body: StartDiagnosisBody, session: Session = Depends(get_db_session)) -> dict:
    run = _handle(ORC.start_diagnosis, session, workflow_run_id, expected_version=body.expected_version, request=body.request, context=body.context, actor_id=body.actor_id)
    return _run_dict(run)


class ResumeDiagnosisBody(BaseModel):
    expected_version: int
    actor_id: str
    data_sufficiency: dict[str, bool]


@router.post("/runs/{workflow_run_id}/diagnosis/resume")
def resume_diagnosis(workflow_run_id: str, body: ResumeDiagnosisBody, session: Session = Depends(get_db_session)) -> dict:
    run = _handle(ORC.resume_diagnosis_with_data, session, workflow_run_id, expected_version=body.expected_version, data_sufficiency=body.data_sufficiency, actor_id=body.actor_id)
    return _run_dict(run)


class StartDesignBody(BaseModel):
    expected_version: int
    actor_id: str
    request: dict[str, Any]
    context: dict[str, Any] = {}


@router.post("/runs/{workflow_run_id}/design")
def start_design(workflow_run_id: str, body: StartDesignBody, session: Session = Depends(get_db_session)) -> dict:
    run = _handle(ORC.start_design, session, workflow_run_id, expected_version=body.expected_version, request=body.request, context=body.context, actor_id=body.actor_id)
    return _run_dict(run)


class EvaluateDesignPortfolioBody(BaseModel):
    expected_version: int
    actor_id: str


@router.post("/runs/{workflow_run_id}/design/evaluate-portfolio")
def evaluate_design_portfolio(workflow_run_id: str, body: EvaluateDesignPortfolioBody, session: Session = Depends(get_db_session)) -> dict:
    """Problem 4's own portfolio evaluation - a precondition for the
    build-governance sequence inside `/human-gate-decision` that
    `DesignAdapter.start()`'s auto-chain never triggered on its own.
    """
    run = _handle(ORC.evaluate_design_portfolio, session, workflow_run_id, expected_version=body.expected_version, actor_id=body.actor_id)
    return _run_dict(run)


class RunEvaluationBody(BaseModel):
    expected_version: int
    actor_id: str
    revision_limit: int = 3
    enable_llm_critic: bool = False


@router.post("/runs/{workflow_run_id}/evaluation")
def run_evaluation(workflow_run_id: str, body: RunEvaluationBody, session: Session = Depends(get_db_session)) -> dict:
    run = _handle(ORC.run_evaluation, session, workflow_run_id, expected_version=body.expected_version, actor_id=body.actor_id, revision_limit=body.revision_limit, enable_llm_critic=body.enable_llm_critic)
    return _run_dict(run)


class EvaluationHumanDecisionBody(BaseModel):
    expected_version: int
    decision: str  # one of harness.scientific_evaluation.models.HUMAN_DECISIONS
    actor_id: str
    approver_role: str = ""
    selected_candidates: list[str] = []
    rationale: str = ""
    revision_limit: int = 3


@router.post("/runs/{workflow_run_id}/evaluation/human-decision")
def record_evaluation_human_decision(workflow_run_id: str, body: EvaluationHumanDecisionBody, session: Session = Depends(get_db_session)) -> dict:
    """Records the scientific_evaluation module's own human decision AND
    re-gates the case so `current_phase` actually advances - unlike
    `POST /api/scientific-evaluation/evaluations/{id}/human-decision`,
    which only updates the EvaluationCase row and leaves the orchestrator's
    run stuck at phase=EVALUATION regardless of the decision.
    """
    run = _handle(
        ORC.record_evaluation_human_decision, session, workflow_run_id, expected_version=body.expected_version,
        decision=body.decision, actor_id=body.actor_id, approver_role=body.approver_role,
        selected_candidates=body.selected_candidates or None, rationale=body.rationale, revision_limit=body.revision_limit,
    )
    return _run_dict(run)


class SubmitRevisionBody(BaseModel):
    expected_version: int
    actor_id: str
    design_id: str
    modification_reason: str
    revision_limit: int = 3
    genetic_modifications: list[dict[str, Any]] | None = None


@router.post("/runs/{workflow_run_id}/evaluation/revise")
def submit_evaluation_revision(workflow_run_id: str, body: SubmitRevisionBody, session: Session = Depends(get_db_session)) -> dict:
    kwargs = {}
    if body.genetic_modifications is not None:
        kwargs["genetic_modifications"] = body.genetic_modifications
    run = _handle(
        ORC.submit_evaluation_revision, session, workflow_run_id, expected_version=body.expected_version, design_id=body.design_id,
        modification_reason=body.modification_reason, actor_id=body.actor_id, revision_limit=body.revision_limit, **kwargs,
    )
    return _run_dict(run)


class HumanGateDecisionBody(BaseModel):
    expected_version: int
    decision: str
    actor_id: str
    reason: str = ""
    selected_design_id: str | None = None
    build_test_kwargs: dict[str, Any] | None = None


@router.post("/runs/{workflow_run_id}/human-gate-decision")
def record_human_gate_decision(workflow_run_id: str, body: HumanGateDecisionBody, session: Session = Depends(get_db_session)) -> dict:
    run = _handle(
        ORC.record_human_gate_decision, session, workflow_run_id, expected_version=body.expected_version, decision=body.decision,
        actor_id=body.actor_id, reason=body.reason, selected_design_id=body.selected_design_id, build_test_kwargs=body.build_test_kwargs,
    )
    return _run_dict(run)


class RunSimulationBody(BaseModel):
    expected_version: int
    actor_id: str
    chassis: dict[str, Any] = {}
    environment: dict[str, Any] = {}
    model_id: str = "MREG-gem_fba"


@router.post("/runs/{workflow_run_id}/simulation")
def run_simulation(workflow_run_id: str, body: RunSimulationBody, session: Session = Depends(get_db_session)) -> dict:
    run = _handle(
        ORC.run_simulation, session, workflow_run_id, expected_version=body.expected_version, chassis=body.chassis,
        environment=body.environment, actor_id=body.actor_id, model_id=body.model_id,
    )
    return _run_dict(run)


class CreateExperimentPlanBody(BaseModel):
    expected_version: int
    actor_id: str
    hypotheses_tested: list[str] = []
    controls: list[str] = []
    factors: list[str] = []
    response_variables: list[str] = []
    acceptance_criteria: list[str] = []
    protocol_ref_id: str | None = None


@router.post("/runs/{workflow_run_id}/experiment-plan")
def create_experiment_plan(workflow_run_id: str, body: CreateExperimentPlanBody, session: Session = Depends(get_db_session)) -> dict:
    kwargs = body.model_dump(exclude={"expected_version", "actor_id"})
    run = _handle(ORC.create_experiment_plan, session, workflow_run_id, expected_version=body.expected_version, actor_id=body.actor_id, **kwargs)
    return _run_dict(run)


class RawObservationBody(BaseModel):
    feature_or_phenotype: str
    value: float | None = None
    unit: str | None = None
    condition_id: str | None = None
    qc_status: str | None = None
    replicates: int | None = None
    detection_limit: float | None = None
    assay_id: str | None = None
    timepoint: dict[str, Any] | None = None
    reference_or_baseline: dict[str, Any] | None = None


class RecordExperimentRunBody(BaseModel):
    expected_version: int
    actor_id: str
    raw_observation: RawObservationBody
    execution_status: str = "completed"
    deviations: list[str] = []
    operator_or_source: str = ""


@router.post("/runs/{workflow_run_id}/experiment-run")
def record_experiment_run(workflow_run_id: str, body: RecordExperimentRunBody, session: Session = Depends(get_db_session)) -> dict:
    from harness.diagnosis.normalizer import RawObservationInput

    raw = RawObservationInput(**body.raw_observation.model_dump())
    run_kwargs = {"execution_status": body.execution_status, "deviations": body.deviations, "operator_or_source": body.operator_or_source}
    run = _handle(
        ORC.record_experiment_run_and_ingest_observation, session, workflow_run_id, expected_version=body.expected_version,
        actor_id=body.actor_id, raw_observation=raw, run_kwargs=run_kwargs,
    )
    return _run_dict(run)


class RunLearningBody(BaseModel):
    expected_version: int
    actor_id: str
    observed_results: list[dict[str, Any]]
    construction_verified: bool
    assay_qc_passed: bool


@router.post("/runs/{workflow_run_id}/learning")
def run_learning(workflow_run_id: str, body: RunLearningBody, session: Session = Depends(get_db_session)) -> dict:
    run = _handle(
        ORC.run_learning, session, workflow_run_id, expected_version=body.expected_version, actor_id=body.actor_id,
        observed_results=body.observed_results, construction_verified=body.construction_verified, assay_qc_passed=body.assay_qc_passed,
    )
    return _run_dict(run)
