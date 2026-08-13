"""Problem 05 (Evaluator & Scientific Critic) API routes (doc05 §10.1).
Every route calls the same service functions the unit/integration/e2e
tests exercise; no business logic lives here.
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from harness.api.deps import get_db_session
from harness.designs.service import SelfApprovalError
from harness.scientific_evaluation import diagnosis_return, human_gate, intake, revision, service as sci_service
from harness.scientific_evaluation.loop import EvaluationGateRejectedError, IllegalEvaluationTransitionError
from harness.scientific_evaluation.models import (
    CandidateEvaluationVector,
    CriticFinding,
    DeterministicCheckResult,
    EvaluationCase,
    EvaluationTransition,
    EvidenceAssessment,
    HumanEvaluationDecision,
    MetaReviewDecision,
    ModelEvaluationRecord,
    RevisionCycle,
    RevisionTask,
    ScientificClaim,
    ScientificReview,
)

router = APIRouter(prefix="/api/scientific-evaluation", tags=["scientific-evaluation"])


def _case_dict(c: EvaluationCase) -> dict[str, Any]:
    return {
        "evaluation_id": c.evaluation_id, "project_id": c.project_id, "design_project_id": c.design_project_id,
        "portfolio_reference": c.portfolio_reference, "diagnosis_reference": c.diagnosis_reference,
        "design_version_references": c.design_version_references, "frozen_context": c.frozen_context,
        "evaluation_mode": c.evaluation_mode, "status": c.status, "revision_round": c.revision_round,
        "created_at": c.created_at, "updated_at": c.updated_at,
    }


def _det_dict(d: DeterministicCheckResult) -> dict[str, Any]:
    return {
        "check_id": d.check_id, "rule_id": d.rule_id, "rule_version": d.rule_version, "design_reference": d.design_reference,
        "category": d.category, "status": d.status, "severity": d.severity, "message": d.message,
        "affected_fields": d.affected_fields, "remediation": d.remediation,
    }


def _evidence_dict(a: EvidenceAssessment) -> dict[str, Any]:
    return {
        "assessment_id": a.assessment_id, "claim_id": a.claim_id, "evidence_id": a.evidence_id, "evidence_type": a.evidence_type,
        "source_quality": a.source_quality, "host_match": a.host_match, "genotype_match": a.genotype_match,
        "condition_match": a.condition_match, "process_match": a.process_match, "time_match": a.time_match,
        "intervention_match": a.intervention_match, "measurement_match": a.measurement_match, "mechanism_match": a.mechanism_match,
        "directness": a.directness, "opposing_evidence": a.opposing_evidence, "applicability_limits": a.applicability_limits,
        "over_extrapolation_flags": a.over_extrapolation_flags, "overall_strength": a.overall_strength,
        "reasoning_summary": a.reasoning_summary, "assessor_type": a.assessor_type,
    }


def _model_dict(m: ModelEvaluationRecord) -> dict[str, Any]:
    return {
        "record_id": m.record_id, "design_reference": m.design_reference, "adapter_name": m.adapter_name,
        "model_or_tool_name": m.model_or_tool_name, "prediction_target": m.prediction_target, "domain_match": m.domain_match,
        "run_status": m.run_status, "result_summary": m.result_summary, "uncertainty_available": m.uncertainty_available,
        "uncertainty": m.uncertainty, "warnings": m.warnings,
    }


def _finding_dict(f: CriticFinding) -> dict[str, Any]:
    return {
        "finding_id": f.finding_id, "review_id": f.review_id, "design_reference": f.design_reference, "category": f.category,
        "severity": f.severity, "finding": f.finding, "why_it_matters": f.why_it_matters,
        "falsification_condition": f.falsification_condition, "required_action": f.required_action,
        "blocking": f.blocking, "resolvable": f.resolvable, "status": f.status,
        "alternative_explanations": f.alternative_explanations,
    }


def _review_dict(r: ScientificReview) -> dict[str, Any]:
    return {
        "review_id": r.review_id, "design_reference": r.design_reference, "reviewer_type": r.reviewer_type,
        "reviewer_id": r.reviewer_id, "shared_model_risk": r.shared_model_risk, "independence_flags": r.independence_flags,
        "rubric_version": r.rubric_version, "recommendation": r.recommendation, "confidence_class": r.confidence_class,
        "confidence_basis": r.confidence_basis, "major_concerns": r.major_concerns, "minor_concerns": r.minor_concerns,
        "unsupported_claims": r.unsupported_claims, "required_revisions": r.required_revisions, "findings": r.findings,
        "limitations": r.limitations,
    }


def _vector_dict(v: CandidateEvaluationVector) -> dict[str, Any]:
    return {
        "candidate_id": v.candidate_id, "design_version": v.design_version, "hard_constraint_status": v.hard_constraint_status,
        "production_potential": v.production_potential, "growth_impact": v.growth_impact, "stability": v.stability,
        "buildability": v.buildability, "genetic_complexity": v.genetic_complexity, "experimental_cost": v.experimental_cost,
        "time_to_result": v.time_to_result, "evidence_strength": v.evidence_strength, "risk": v.risk,
        "information_gain": v.information_gain, "uncertainty": v.uncertainty, "pareto_status": v.pareto_status,
        "dominates": v.dominates, "dominated_by": v.dominated_by, "excluded_reasons": v.excluded_reasons,
    }


def _meta_dict(d: MetaReviewDecision) -> dict[str, Any]:
    return {
        "decision_id": d.decision_id, "review_references": d.review_references, "agreements": d.agreements,
        "disagreements": d.disagreements, "unresolved_conflicts": d.unresolved_conflicts,
        "blocking_findings": d.blocking_findings, "recommended_action": d.recommended_action,
        "recommended_candidates": d.recommended_candidates, "required_revision_tasks": d.required_revision_tasks,
        "required_evidence_tasks": d.required_evidence_tasks, "return_target": d.return_target,
        "decision_rationale": d.decision_rationale, "decision_confidence": d.decision_confidence,
        "human_gate_required": d.human_gate_required,
    }


def _pipeline_response(case: EvaluationCase, result: dict[str, Any]) -> dict[str, Any]:
    return {
        "case": _case_dict(case),
        "candidates": [c.design_id for c in result["candidates"]],
        "findings_by_design": {did: [_finding_dict(f) for f in fs] for did, fs in result["findings_by_design"].items()},
        "vectors": [_vector_dict(v) for v in result["vectors"]],
        "revision_tasks": [t.task_id for t in result["revision_tasks"]],
        "meta_decision": _meta_dict(result["meta_decision"]),
        "revision_gate": {"status": result["revision_gate"].status.value, "violations": [v.message for v in result["revision_gate"].violations]},
    }


# -- Intake / run -----------------------------------------------------------


class StartEvaluationBody(BaseModel):
    portfolio_id: str
    actor_id: str
    diagnosis_reference: str | None = None
    revision_limit: int = 3


@router.post("/evaluations")
def start_evaluation(body: StartEvaluationBody, session: Session = Depends(get_db_session)) -> dict:
    try:
        result = sci_service.run_scientific_evaluation(
            session, portfolio_id=body.portfolio_id, actor_id=body.actor_id,
            diagnosis_reference=body.diagnosis_reference, revision_limit=body.revision_limit,
        )
    except intake.EvaluationIntakeError as e:
        raise HTTPException(422, str(e))
    return _pipeline_response(result["case"], result)


@router.get("/evaluations/{evaluation_id}")
def get_evaluation(evaluation_id: str, session: Session = Depends(get_db_session)) -> dict:
    case = intake.get_case(session, evaluation_id)
    if case is None:
        raise HTTPException(404, "no such evaluation case")
    return _case_dict(case)


class ContinueEvaluationBody(BaseModel):
    actor_id: str
    revision_limit: int = 3


@router.post("/evaluations/{evaluation_id}/run-stage")
def run_stage(evaluation_id: str, body: ContinueEvaluationBody, session: Session = Depends(get_db_session)) -> dict:
    """"run/retry allowed evaluator stage" (doc05 §10.1) - re-runs the full
    deterministic->meta-review pipeline for a case currently `evaluation_
    pending` (idempotent retry point after a transient failure)."""
    try:
        result = sci_service.continue_scientific_evaluation(
            session, evaluation_id=evaluation_id, actor_id=body.actor_id, revision_limit=body.revision_limit,
        )
    except ValueError as e:
        raise HTTPException(404, str(e))
    except IllegalEvaluationTransitionError as e:
        raise HTTPException(409, str(e))
    return _pipeline_response(result["case"], result)


# -- Read endpoints -----------------------------------------------------


@router.get("/evaluations/{evaluation_id}/deterministic-results")
def list_deterministic_results(evaluation_id: str, session: Session = Depends(get_db_session)) -> dict:
    rows = session.execute(select(DeterministicCheckResult).where(DeterministicCheckResult.evaluation_id == evaluation_id)).scalars().all()
    return {"results": [_det_dict(r) for r in rows]}


@router.get("/evaluations/{evaluation_id}/evidence-assessments")
def list_evidence_assessments(evaluation_id: str, session: Session = Depends(get_db_session)) -> dict:
    rows = session.execute(select(EvidenceAssessment).where(EvidenceAssessment.evaluation_id == evaluation_id)).scalars().all()
    return {"assessments": [_evidence_dict(a) for a in rows]}


@router.get("/evaluations/{evaluation_id}/model-records")
def list_model_records(evaluation_id: str, session: Session = Depends(get_db_session)) -> dict:
    rows = session.execute(select(ModelEvaluationRecord).where(ModelEvaluationRecord.evaluation_id == evaluation_id)).scalars().all()
    return {"records": [_model_dict(m) for m in rows]}


@router.get("/evaluations/{evaluation_id}/reviews")
def get_reviewer_reports(evaluation_id: str, session: Session = Depends(get_db_session)) -> dict:
    reviews = session.execute(select(ScientificReview).where(ScientificReview.evaluation_id == evaluation_id)).scalars().all()
    findings = session.execute(
        select(CriticFinding).where(CriticFinding.review_id.in_([r.review_id for r in reviews]))
    ).scalars().all() if reviews else []
    return {"reviews": [_review_dict(r) for r in reviews], "findings": [_finding_dict(f) for f in findings]}


@router.get("/evaluations/{evaluation_id}/candidate-comparison")
def get_candidate_comparison(evaluation_id: str, session: Session = Depends(get_db_session)) -> dict:
    rows = session.execute(select(CandidateEvaluationVector).where(CandidateEvaluationVector.evaluation_id == evaluation_id)).scalars().all()
    return {"vectors": [_vector_dict(v) for v in rows]}


@router.get("/evaluations/{evaluation_id}/meta-review")
def get_meta_review(evaluation_id: str, session: Session = Depends(get_db_session)) -> dict:
    latest = session.execute(
        select(MetaReviewDecision).where(MetaReviewDecision.evaluation_id == evaluation_id).order_by(MetaReviewDecision.created_at.desc())
    ).scalars().first()
    if latest is None:
        raise HTTPException(404, "no meta-review decision on record yet")
    return _meta_dict(latest)


# -- Revision -------------------------------------------------------------


class SubmitRevisionBody(BaseModel):
    design_id: str
    actor_id: str
    modification_reason: str
    task_ids: list[str] = []
    genetic_modifications: list[dict[str, Any]] | None = None
    regulatory_architecture: dict[str, Any] | None = None
    process_modifications: list[dict[str, Any]] | None = None
    expected_mechanism: str | None = None
    causal_chain: list[str] | None = None
    interaction_and_epistasis_assumptions: list[str] | None = None
    revision_limit: int = 3


@router.post("/evaluations/{evaluation_id}/revisions")
def submit_revision(evaluation_id: str, body: SubmitRevisionBody, session: Session = Depends(get_db_session)) -> dict:
    payload = body.model_dump()
    payload.pop("design_id")
    try:
        result = sci_service.apply_revision_and_reevaluate(session, evaluation_id=evaluation_id, design_id=body.design_id, **payload)
    except (ValueError, IllegalEvaluationTransitionError) as e:
        raise HTTPException(422, str(e))
    if result.get("stopped"):
        return {"stopped": True, "stop_reason": result["stop_reason"]}
    response = _pipeline_response(result["case"], result)
    response["revision_cycle"] = result["revision_cycle"].cycle_id
    response["new_candidate_id"] = result["new_candidate"].design_id
    return response


@router.get("/evaluations/{evaluation_id}/version-history")
def get_version_history(evaluation_id: str, session: Session = Depends(get_db_session)) -> dict:
    cycles = session.execute(select(RevisionCycle).where(RevisionCycle.evaluation_id == evaluation_id).order_by(RevisionCycle.created_at)).scalars().all()
    tasks = session.execute(select(RevisionTask).where(RevisionTask.evaluation_id == evaluation_id)).scalars().all()
    return {
        "cycles": [
            {"cycle_id": c.cycle_id, "from_design_id": c.from_design_id, "from_design_version": c.from_design_version,
             "to_design_id": c.to_design_id, "to_design_version": c.to_design_version, "changed_fields": c.changed_fields,
             "resolved_findings": c.resolved_findings}
            for c in cycles
        ],
        "tasks": [
            {"task_id": t.task_id, "target_design_id": t.target_design_id, "task_type": t.task_type, "priority": t.priority,
             "required_change": t.required_change, "status": t.status, "resolution_reference": t.resolution_reference}
            for t in tasks
        ],
    }


# -- Human gate -----------------------------------------------------------


class HumanDecisionBody(BaseModel):
    decision: str
    approver_id: str
    approver_role: str = ""
    selected_candidates: list[str] = []
    conditions: list[str] = []
    rationale: str = ""
    acknowledged_risks: list[str] = []


@router.post("/evaluations/{evaluation_id}/human-decision")
def submit_human_decision(evaluation_id: str, body: HumanDecisionBody, session: Session = Depends(get_db_session)) -> dict:
    case = intake.get_case(session, evaluation_id)
    if case is None:
        raise HTTPException(404, "no such evaluation case")
    try:
        row = human_gate.record_human_evaluation_decision(
            session, case=case, decision=body.decision, approver_id=body.approver_id, approver_role=body.approver_role,
            selected_candidates=body.selected_candidates, conditions=body.conditions, rationale=body.rationale,
            acknowledged_risks=body.acknowledged_risks,
        )
    except SelfApprovalError as e:
        raise HTTPException(409, str(e))
    except human_gate.HumanGatePreconditionError as e:
        raise HTTPException(422, str(e))
    except (human_gate.InvalidHumanDecisionError, IllegalEvaluationTransitionError) as e:
        raise HTTPException(422, str(e))
    return {"human_decision_id": row.human_decision_id, "decision": row.decision, "case_status": case.status}


class ReturnToDiagnosisBody(BaseModel):
    design_id: str
    actor_id: str


@router.post("/evaluations/{evaluation_id}/return-to-diagnosis")
def return_to_diagnosis(evaluation_id: str, body: ReturnToDiagnosisBody, session: Session = Depends(get_db_session)) -> dict:
    try:
        request = sci_service.initiate_diagnosis_return(session, evaluation_id=evaluation_id, design_id=body.design_id, actor_id=body.actor_id)
    except ValueError as e:
        raise HTTPException(404, str(e))
    return {
        "request_id": request.request_id, "status": request.status, "new_diagnosis_session_id": request.new_diagnosis_session_id,
        "triggering_findings": request.triggering_findings, "alternative_explanations": request.alternative_explanations,
    }


# -- Audit ------------------------------------------------------------------


@router.get("/evaluations/{evaluation_id}/audit-trail")
def get_audit_trail(evaluation_id: str, session: Session = Depends(get_db_session)) -> dict:
    rows = session.execute(
        select(EvaluationTransition).where(EvaluationTransition.evaluation_id == evaluation_id).order_by(EvaluationTransition.started_at)
    ).scalars().all()
    decisions = session.execute(
        select(HumanEvaluationDecision).where(HumanEvaluationDecision.evaluation_id == evaluation_id).order_by(HumanEvaluationDecision.timestamp)
    ).scalars().all()
    return {
        "transitions": [{"state": t.state, "selected_next_state": t.selected_next_state, "gate_result": t.gate_result, "started_at": t.started_at} for t in rows],
        "human_decisions": [{"decision": d.decision, "reviewer_or_approver": d.reviewer_or_approver, "rationale": d.rationale, "timestamp": d.timestamp} for d in decisions],
    }
