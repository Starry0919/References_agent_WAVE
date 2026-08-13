"""Problem 04 (Engineering Design Generation and Decision Loop) API routes.
Every route calls the same service functions the unit/integration/e2e
tests exercise; no business logic lives here."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from harness.api.deps import get_db_session
from harness.designs.service import SelfApprovalError
from harness.diagnosis.models import DiagnosisDecision
from harness.diagnosis.models import DiagnosisFinding, EngineeringProblem
from harness.evidence_retrieval.models import EvidenceNeed
from harness.experiments.models import DataAsset, Observation
from harness.learning.models import HypothesisVersion
from harness.engineering_design import (
    build_test_planner,
    counterfactual_service,
    design_version_bridge,
    evidence_resolution,
    governance_service,
    handoff as handoff_mod,
    memory_integration,
    outcome_service,
    portfolio_service,
    project_service,
    strategy_service,
)
from harness.engineering_design.evaluation_service import evaluate_portfolio
from harness.engineering_design.evaluators.runner import latest_evaluation
from harness.engineering_design.loop import DesignGateRejectedError, EngineeringDesignLoopController, IllegalDesignTransitionError
from harness.engineering_design.models import (
    CandidateDesign,
    DesignEvaluation,
    DesignWorkflowTransition,
    DiagnosisHandoffRecord,
    EngineeringDesignProject,
    EngineeringStrategy,
)
from harness.engineering_design.portfolio_service import PortfolioDiversityRejected
from harness.engineering_design.decision_state import InvalidCandidateTransition
from harness.engineering_design.models import BuildTestPackage, ModelEvaluation

router = APIRouter(prefix="/api/engineering-design", tags=["engineering-design"])


def _project_dict(p: EngineeringDesignProject) -> dict[str, Any]:
    return {
        "design_project_id": p.design_project_id, "project_id": p.project_id, "chassis": p.chassis,
        "chassis_version_or_genotype": p.chassis_version_or_genotype, "diagnosis_session_id": p.diagnosis_session_id,
        "diagnosis_decision_id": p.diagnosis_decision_id, "diagnosis_version": p.diagnosis_version,
        "primary_metrics": p.primary_metrics, "secondary_metrics": p.secondary_metrics,
        "hard_constraints": p.hard_constraints, "preferences_or_weights": p.preferences_or_weights,
        "autonomy_level": p.autonomy_level, "status": p.status, "revision_count": p.revision_count,
        "version": p.version, "reference_ddr_ids": p.reference_ddr_ids,
    }


def _handoff_dict(h: DiagnosisHandoffRecord) -> dict[str, Any]:
    return {
        "handoff_id": h.handoff_id, "design_project_id": h.design_project_id,
        "diagnosis_session_id": h.diagnosis_session_id, "diagnosis_decision_id": h.diagnosis_decision_id,
        "diagnosis_version": h.diagnosis_version, "handoff_kind": h.handoff_kind,
        "decision_status": h.decision_status, "supported_hypotheses": h.supported_hypotheses,
        "unresolved_alternatives": h.unresolved_alternatives, "approved_for_design": h.approved_for_design,
        "is_stale": h.is_stale, "adapter_provenance": h.adapter_provenance, "created_at": h.created_at,
    }


def _strategy_dict(s: EngineeringStrategy) -> dict[str, Any]:
    return {
        "strategy_id": s.strategy_id, "strategy_class": s.strategy_class, "engineering_objective": s.engineering_objective,
        "mechanism_target": s.mechanism_target, "rationale": s.rationale, "status": s.status,
        "excluded_strategy_reasons": s.excluded_strategy_reasons, "evidence_links": s.evidence_links,
        "historical_priors": s.historical_priors, "design_prior": s.design_prior,
    }


def _candidate_dict(c: CandidateDesign) -> dict[str, Any]:
    return {
        "design_id": c.design_id, "lineage_id": c.lineage_id, "design_version": c.design_version,
        "portfolio_id": c.portfolio_id, "portfolio_role": c.portfolio_role, "strategy_ids": c.strategy_ids,
        "genetic_modifications": c.genetic_modifications, "expected_mechanism": c.expected_mechanism,
        "readiness": c.readiness, "status": c.status, "decision_state": c.decision_state,
        "diagnosis_finding_ids": c.diagnosis_finding_ids, "rejection_reasons": c.rejection_reasons,
        "legacy_verification_state": None if c.diagnosis_finding_ids else "LEGACY_UNVERIFIED",
        "build_test_package_id": c.build_test_package_id,
        # These fields were already persisted on CandidateDesign but were
        # previously hidden from every frontend consumer.  Exposing them is
        # read-only and lets the scientific workbench render the actual
        # causal/evidence/dependency/validation record rather than inventing a
        # second summary schema.
        "regulatory_architecture": c.regulatory_architecture,
        "process_modifications": c.process_modifications,
        "causal_chain": c.causal_chain,
        "interaction_and_epistasis_assumptions": c.interaction_and_epistasis_assumptions,
        "evidence_links": c.evidence_links,
        "counterfactual_requests": c.counterfactual_requests,
        "counterfactual_results": c.counterfactual_results,
        "uncertainty_and_model_conflicts": c.uncertainty_and_model_conflicts,
        "tradeoff_profile": c.tradeoff_profile,
        "buildability_assessment": c.buildability_assessment,
        "debug_and_fallback_plan": c.debug_and_fallback_plan,
        "safety_flags": c.safety_flags,
        "source_diagnosis_version": c.source_diagnosis_version,
    }


# -- Handoff / objective ----------------------------------------------------


class HandoffBody(BaseModel):
    diagnosis_decision_id: str
    actor_id: str
    handoff_kind: str = "diagnosis_decision"
    human_approved: bool | None = None
    chassis: str | None = None
    chassis_version_or_genotype: str = "unknown"


@router.post("/handoff")
def create_from_diagnosis(body: HandoffBody, session: Session = Depends(get_db_session)) -> dict:
    decision = session.get(DiagnosisDecision, body.diagnosis_decision_id)
    if decision is None:
        raise HTTPException(404, "diagnosis decision not found")
    try:
        proj, handoff = handoff_mod.ingest_diagnosis_decision(
            session, decision=decision, actor_id=body.actor_id, handoff_kind=body.handoff_kind,
            human_approved=body.human_approved, chassis=body.chassis, chassis_version_or_genotype=body.chassis_version_or_genotype,
        )
    except handoff_mod.HandoffRejectedError as e:
        raise HTTPException(422, str(e))
    except IllegalDesignTransitionError as e:
        raise HTTPException(409, str(e))
    return {"project": _project_dict(proj), "handoff": _handoff_dict(handoff)}


@router.get("/projects/{design_project_id}")
def get_project(design_project_id: str, session: Session = Depends(get_db_session)) -> dict:
    proj = project_service.get_design_project(session, design_project_id)
    if proj is None:
        raise HTTPException(404, "design project not found")
    return _project_dict(proj)


@router.get("/projects/{design_project_id}/handoff")
def list_handoffs(design_project_id: str, session: Session = Depends(get_db_session)) -> dict:
    rows = session.execute(
        select(DiagnosisHandoffRecord).where(DiagnosisHandoffRecord.design_project_id == design_project_id).order_by(DiagnosisHandoffRecord.created_at.desc())
    ).scalars().all()
    return {"handoffs": [_handoff_dict(h) for h in rows]}


class ObjectivesBody(BaseModel):
    primary_metrics: list[dict[str, Any]]
    secondary_metrics: list[dict[str, Any]] = []
    hard_constraints: list[dict[str, Any]]
    preferences_or_weights: list[dict[str, Any]] = []
    available_resources: dict[str, Any] = {}
    expected_version: int
    actor_id: str


@router.post("/projects/{design_project_id}/objectives")
def set_objectives(design_project_id: str, body: ObjectivesBody, session: Session = Depends(get_db_session)) -> dict:
    try:
        proj = project_service.set_objectives(session, design_project_id=design_project_id, **body.model_dump())
    except project_service.ObjectiveRejected as e:
        raise HTTPException(422, str(e))
    except ValueError as e:
        raise HTTPException(404, str(e))
    return _project_dict(proj)


class ConfirmObjectiveBody(BaseModel):
    actor_id: str


@router.post("/projects/{design_project_id}/confirm-objective")
def confirm_objective(design_project_id: str, body: ConfirmObjectiveBody, session: Session = Depends(get_db_session)) -> dict:
    from harness.workflow.gates import design_objective_gate

    proj = project_service.get_design_project(session, design_project_id)
    if proj is None:
        raise HTTPException(404, "design project not found")
    gate = design_objective_gate(has_primary_metrics=bool(proj.primary_metrics), has_hard_constraints_declared=proj.hard_constraints is not None)
    try:
        proj = EngineeringDesignLoopController().confirm_objective(session, proj, actor_id=body.actor_id, objective_gate_result=gate)
    except DesignGateRejectedError as e:
        raise HTTPException(422, str(e))
    except IllegalDesignTransitionError as e:
        raise HTTPException(409, str(e))
    return _project_dict(proj)


# -- Strategy / portfolio -----------------------------------------------


class GenerateStrategiesBody(BaseModel):
    handoff_id: str
    actor_id: str


@router.post("/projects/{design_project_id}/strategies")
def generate_strategies(design_project_id: str, body: GenerateStrategiesBody, session: Session = Depends(get_db_session)) -> dict:
    try:
        rows = strategy_service.generate_and_persist_strategies(session, design_project_id=design_project_id, handoff_id=body.handoff_id, actor_id=body.actor_id)
    except ValueError as e:
        raise HTTPException(404, str(e))
    return {"strategies": [_strategy_dict(s) for s in rows]}


@router.get("/projects/{design_project_id}/strategies")
def list_strategies(design_project_id: str, session: Session = Depends(get_db_session)) -> dict:
    return {"strategies": [_strategy_dict(s) for s in strategy_service.list_strategies(session, design_project_id)]}


@router.get("/evidence-links/resolve")
def resolve_evidence_link(source_type: str, reference: str, detail: str = "") -> dict:
    """Resolves one `EngineeringStrategy.evidence_links[i]` entry to what it
    actually points at (a paper, a diagnosis hypothesis, or a general
    knowledge-base pattern with no specific citation) - see
    `evidence_resolution.py` module docstring for why most `curated_
    knowledge` links resolve to the last of those."""
    return evidence_resolution.resolve_evidence_link(source_type, reference, detail)


class GeneratePortfolioBody(BaseModel):
    actor_id: str


@router.post("/projects/{design_project_id}/portfolio")
def generate_portfolio(design_project_id: str, body: GeneratePortfolioBody, session: Session = Depends(get_db_session)) -> dict:
    try:
        portfolio, rows, suppressed = portfolio_service.generate_and_persist_portfolio(session, design_project_id=design_project_id, actor_id=body.actor_id)
    except PortfolioDiversityRejected as e:
        raise HTTPException(422, str(e))
    except portfolio_service.DiagnosisRequiredError as e:
        raise HTTPException(422, str(e))
    except ValueError as e:
        raise HTTPException(404, str(e))
    proj = project_service.get_design_project(session, design_project_id)
    try:
        EngineeringDesignLoopController().generate_portfolio(session, proj, actor_id=body.actor_id)
    except IllegalDesignTransitionError as e:
        raise HTTPException(409, str(e))
    return {
        "portfolio_id": portfolio.portfolio_id, "candidates": [_candidate_dict(r) for r in rows],
        "absent_roles": portfolio.absent_roles, "suppressed_repeats": suppressed,
    }


@router.get("/projects/{design_project_id}/candidates")
def list_candidates(design_project_id: str, session: Session = Depends(get_db_session)) -> dict:
    return {"candidates": [_candidate_dict(c) for c in portfolio_service.list_candidates(session, design_project_id)]}


@router.get("/projects/{design_project_id}/evaluations")
def list_project_evaluations(design_project_id: str, session: Session = Depends(get_db_session)) -> dict:
    """Returns the latest persisted evaluation per candidate as a normal
    empty collection when evaluation has not run.  Workbench summaries must
    not probe a candidate-only 404 endpoint merely to discover that state."""
    candidates = session.execute(
        select(CandidateDesign).where(CandidateDesign.design_project_id == design_project_id)
    ).scalars().all()
    candidate_ids = [c.design_id for c in candidates]
    rows = session.execute(
        select(DesignEvaluation)
        .where(DesignEvaluation.design_id.in_(candidate_ids))
        .order_by(DesignEvaluation.created_at.desc())
    ).scalars().all() if candidate_ids else []
    latest: dict[str, DesignEvaluation] = {}
    for row in rows:
        latest.setdefault(row.design_id, row)
    return {"evaluations": {
        design_id: {
            "evaluation_id": ev.evaluation_id, "design_version": ev.design_version,
            "objective_vector": ev.objective_vector, "hard_constraint_results": ev.hard_constraint_results,
            "evaluator_findings": ev.evaluator_findings, "pareto_status": ev.pareto_status,
            "recommendation": ev.recommendation, "required_revisions": ev.required_revisions,
        }
        for design_id, ev in latest.items()
    }}


@router.get("/candidates/{design_id}")
def get_candidate(design_id: str, session: Session = Depends(get_db_session)) -> dict:
    c = portfolio_service.get_candidate(session, design_id)
    if c is None:
        raise HTTPException(404, "candidate design not found")
    return _candidate_dict(c)


_STATE_LABELS = {
    "candidate_generated": "generated", "evaluation_pending": "evaluation pending",
    "evaluated": "evaluated", "ranked": "ranked", "human_selection_pending": "awaiting human selection",
    "selected": "human-selected", "validation_plan_pending": "validation plan pending",
    "validation_ready": "validation ready", "build_ready": "build ready", "rejected": "rejected",
}


@router.get("/candidates/{design_id}/scientific-state")
def get_candidate_scientific_state(design_id: str, session: Session = Depends(get_db_session)) -> dict:
    """One read model over the canonical persisted scientific objects.

    This deliberately returns links and status projections, not a second set
    of frontend-owned scientific semantics.
    """
    candidate = session.get(CandidateDesign, design_id)
    if candidate is None:
        raise HTTPException(404, "candidate design not found")
    project = session.get(EngineeringDesignProject, candidate.design_project_id)
    findings = [session.get(DiagnosisFinding, fid) for fid in candidate.diagnosis_finding_ids]
    findings = [f for f in findings if f is not None]
    observation_ids = sorted({oid for f in findings for oid in f.observation_refs})
    observations = [session.get(Observation, oid) for oid in observation_ids]
    observations = [o for o in observations if o is not None]
    asset_ids = sorted({aid for o in observations for aid in o.data_asset_ids})
    assets = {a.data_asset_id: a for a in (session.get(DataAsset, aid) for aid in asset_ids) if a is not None}
    hypotheses = {f.constraint_hypothesis_id: session.get(HypothesisVersion, f.constraint_hypothesis_id) for f in findings}
    needs = session.execute(select(EvidenceNeed).where(EvidenceNeed.project_id == project.project_id)).scalars().all() if project else []
    evaluations = session.execute(select(ModelEvaluation).where(ModelEvaluation.candidate_id == design_id).order_by(ModelEvaluation.created_at.desc())).scalars().all()
    package = session.get(BuildTestPackage, candidate.build_test_package_id) if candidate.build_test_package_id else None
    strategies = [session.get(EngineeringStrategy, sid) for sid in candidate.strategy_ids]
    next_actions = {
        "candidate_generated": "run portfolio evaluation", "evaluation_pending": "complete persisted evaluation",
        "evaluated": "rank candidate", "ranked": "request human selection", "human_selection_pending": "record human decision",
        "selected": "open validation planning", "validation_plan_pending": "complete validation plan",
        "validation_ready": "verify build readiness", "build_ready": "start governed build", "rejected": "create a justified revision",
    }
    return {
        "candidate_decision_state": candidate.decision_state,
        "candidate_state_label": _STATE_LABELS.get(candidate.decision_state, candidate.decision_state),
        "required_next_action": next_actions.get(candidate.decision_state, "review state"),
        "legacy_verification_state": None if findings else "LEGACY_UNVERIFIED",
        "diagnosis_findings": [{
            "finding_id": f.finding_id, "engineering_problem_id": f.engineering_problem_id,
            "observation_refs": f.observation_refs, "mechanism_type": f.mechanism_type,
            "hypothesis_version_id": f.constraint_hypothesis_id,
            "hypothesis_status": hypotheses[f.constraint_hypothesis_id].posterior_status if hypotheses.get(f.constraint_hypothesis_id) else "unknown",
            "validation_needs": f.validation_needs, "provenance": f.provenance,
        } for f in findings],
        "observations": [{
            "observation_id": o.observation_id, "metric": o.metric, "value": o.value, "unit": o.unit,
            "qc_status": o.qc_status, "qc_flags": o.qc_flags, "source_type": o.source_type,
            "data_assets": [{"data_asset_id": aid, "checksum": assets[aid].checksum, "qc_status": assets[aid].qc_status,
                             "parser": assets[aid].parser_name, "provenance": assets[aid].provenance}
                            for aid in o.data_asset_ids if aid in assets],
        } for o in observations],
        "evidence_needs": [{"need_id": n.need_id, "claim_or_hypothesis_id": n.claim_or_hypothesis_id,
                            "criticality": n.criticality, "status": n.status, "stop_rule": n.stop_rule}
                           for n in needs if n.claim_or_hypothesis_id in hypotheses],
        "historical_priors": [{"strategy_id": s.strategy_id, "label": "PRIOR", "not_evidence": True,
                               "requires_fulltext_experiment_verification": True, "priors": s.historical_priors}
                              for s in strategies if s is not None and s.historical_priors],
        "model_evaluations": [{"model_evaluation_id": e.model_evaluation_id, "model_id": e.model_id,
                               "model_version": e.model_version, "runtime_status": e.runtime_status,
                               "infeasible": e.infeasible, "assumptions": e.assumptions, "limitations": e.limitations}
                              for e in evaluations],
        "validation_plan": None if package is None else {"package_id": package.package_id, "readiness": package.readiness,
                                                         "missing_information_or_resources": package.missing_information_or_resources},
    }


class ReviseCandidateBody(BaseModel):
    actor_id: str
    modification_reason: str
    genetic_modifications: list[dict[str, Any]] | None = None
    regulatory_architecture: dict[str, Any] | None = None
    process_modifications: list[dict[str, Any]] | None = None
    expected_mechanism: str | None = None
    causal_chain: list[str] | None = None
    interaction_and_epistasis_assumptions: list[str] | None = None


@router.post("/candidates/{design_id}/revise")
def revise_candidate(design_id: str, body: ReviseCandidateBody, session: Session = Depends(get_db_session)) -> dict:
    try:
        row = portfolio_service.revise_candidate(session, design_id=design_id, **body.model_dump())
    except portfolio_service.RevisionRejected as e:
        raise HTTPException(422, str(e))
    except ValueError as e:
        raise HTTPException(404, str(e))
    return _candidate_dict(row)


# -- Evaluation ---------------------------------------------------------


class EvaluatePortfolioBody(BaseModel):
    actor_id: str


@router.post("/portfolios/{portfolio_id}/evaluate")
def evaluate(portfolio_id: str, body: EvaluatePortfolioBody, session: Session = Depends(get_db_session)) -> dict:
    try:
        result = evaluate_portfolio(session, portfolio_id=portfolio_id, actor_id=body.actor_id)
    except ValueError as e:
        raise HTTPException(404, str(e))
    except IllegalDesignTransitionError as e:
        raise HTTPException(409, str(e))
    return {
        "decision": result["decision"],
        "evaluations": {
            did: {"recommendation": ev.recommendation, "pareto_status": ev.pareto_status, "required_revisions": ev.required_revisions,
                  "evaluator_findings": ev.evaluator_findings, "objective_vector": ev.objective_vector, "hard_constraint_results": ev.hard_constraint_results}
            for did, ev in result["evaluations"].items()
        },
        "revision_gate": {"status": result["revision_gate"].status.value, "violations": [v.message for v in result["revision_gate"].violations]},
    }


@router.get("/candidates/{design_id}/evaluation")
def get_latest_evaluation(design_id: str, session: Session = Depends(get_db_session)) -> dict:
    ev = latest_evaluation(session, design_id)
    if ev is None:
        raise HTTPException(404, "no evaluation on record for this candidate")
    return {
        "evaluation_id": ev.evaluation_id, "design_version": ev.design_version, "objective_vector": ev.objective_vector,
        "hard_constraint_results": ev.hard_constraint_results, "evaluator_findings": ev.evaluator_findings,
        "pareto_status": ev.pareto_status, "recommendation": ev.recommendation, "required_revisions": ev.required_revisions,
    }


# -- Counterfactual -------------------------------------------------------


class CounterfactualBody(BaseModel):
    adapter_name: str
    actor_id: str
    inputs: dict[str, Any] | None = None
    context: dict[str, Any] = {}
    constraints_objective_parameters: dict[str, Any] = {}


@router.post("/candidates/{design_id}/counterfactual")
def request_counterfactual(design_id: str, body: CounterfactualBody, session: Session = Depends(get_db_session)) -> dict:
    try:
        run = counterfactual_service.request_counterfactual(
            session, design_id=design_id, adapter_name=body.adapter_name, actor_id=body.actor_id, inputs=body.inputs,
            context=body.context, constraints_objective_parameters=body.constraints_objective_parameters,
        )
    except (ValueError, KeyError) as e:
        raise HTTPException(400, str(e))
    return {"run_id": run.run_id, "capability_status": run.capability_status, "runtime_status": run.runtime_status, "status": run.status, "outputs": run.outputs}


# -- Build/test -----------------------------------------------------------


class DraftBuildTestBody(BaseModel):
    actor_id: str
    construction_concept: str = ""
    build_steps_or_milestones: list[dict[str, Any]] = []
    required_materials: list[str] = []
    required_capabilities_or_instruments: list[str] = []
    controls: list[dict[str, Any]] = []
    replication_plan: dict[str, Any] = {}
    sampling_plan: list[dict[str, Any]] = []
    qc_checkpoints: list[str] = []
    decision_rules: list[str] = []
    debug_plan: list[str] = []
    fallback_plan: list[str] = []
    estimated_time_cost_and_risk: dict[str, Any] = {}


@router.post("/candidates/{design_id}/build-test-package")
def draft_build_test_package(design_id: str, body: DraftBuildTestBody, session: Session = Depends(get_db_session)) -> dict:
    try:
        pkg = build_test_planner.draft_build_test_package(session, design_id=design_id, **body.model_dump())
    except ValueError as e:
        raise HTTPException(404, str(e))
    except InvalidCandidateTransition as e:
        raise HTTPException(409, str(e))
    return {"package_id": pkg.package_id, "readiness": pkg.readiness, "missing_information_or_resources": pkg.missing_information_or_resources}


class MarkPlanningCompleteBody(BaseModel):
    actor_id: str


@router.post("/projects/{design_project_id}/planning-complete")
def mark_planning_complete(design_project_id: str, body: MarkPlanningCompleteBody, session: Session = Depends(get_db_session)) -> dict:
    try:
        proj = governance_service.mark_planning_complete(session, design_project_id=design_project_id, actor_id=body.actor_id)
    except ValueError as e:
        raise HTTPException(422, str(e))
    except IllegalDesignTransitionError as e:
        raise HTTPException(409, str(e))
    except InvalidCandidateTransition as e:
        raise HTTPException(409, str(e))
    return _project_dict(proj)


# -- Human approval / build progression ------------------------------------


class RequestApprovalBody(BaseModel):
    actor_id: str


@router.post("/projects/{design_project_id}/request-approval")
def request_approval(design_project_id: str, body: RequestApprovalBody, session: Session = Depends(get_db_session)) -> dict:
    try:
        proj = governance_service.request_human_approval(session, design_project_id=design_project_id, actor_id=body.actor_id)
    except ValueError as e:
        raise HTTPException(404, str(e))
    except IllegalDesignTransitionError as e:
        raise HTTPException(409, str(e))
    except InvalidCandidateTransition as e:
        raise HTTPException(409, str(e))
    return _project_dict(proj)


class HumanDecisionBody(BaseModel):
    approver_id: str
    decision: str  # approved|rejected
    approver_role: str = ""
    conditions: list[str] = []
    reason: str = ""


@router.post("/candidates/{design_id}/human-decision")
def record_human_decision(design_id: str, body: HumanDecisionBody, session: Session = Depends(get_db_session)) -> dict:
    try:
        approval, candidate, proj = governance_service.record_human_decision(session, design_id=design_id, **body.model_dump())
    except SelfApprovalError as e:
        raise HTTPException(409, str(e))
    except ValueError as e:
        raise HTTPException(404, str(e))
    except IllegalDesignTransitionError as e:
        raise HTTPException(409, str(e))
    except InvalidCandidateTransition as e:
        raise HTTPException(409, str(e))
    return {"approval_id": approval.approval_id, "candidate_status": candidate.status, "project_status": proj.status}


class BridgeBody(BaseModel):
    actor_id: str
    version_label: str | None = None


@router.post("/candidates/{design_id}/bridge-to-design-version")
def bridge_to_design_version(design_id: str, body: BridgeBody, session: Session = Depends(get_db_session)) -> dict:
    try:
        dv = design_version_bridge.bridge_to_design_version(session, design_id=design_id, actor_id=body.actor_id, version_label=body.version_label)
    except (ValueError, design_version_bridge.CandidateNotApprovedError) as e:
        raise HTTPException(422, str(e))
    return {"design_version_id": dv.design_version_id}


class StartBuildBody(BaseModel):
    actor_id: str


@router.post("/projects/{design_project_id}/candidates/{design_id}/start-build")
def start_build(design_project_id: str, design_id: str, body: StartBuildBody, session: Session = Depends(get_db_session)) -> dict:
    try:
        candidate = governance_service.start_build(session, design_project_id=design_project_id, design_id=design_id, actor_id=body.actor_id)
    except ValueError as e:
        raise HTTPException(404, str(e))
    except IllegalDesignTransitionError as e:
        raise HTTPException(409, str(e))
    return _candidate_dict(candidate)


@router.post("/projects/{design_project_id}/test-pending")
def mark_test_pending(design_project_id: str, body: StartBuildBody, session: Session = Depends(get_db_session)) -> dict:
    try:
        proj = governance_service.mark_test_pending(session, design_project_id=design_project_id, actor_id=body.actor_id)
    except ValueError as e:
        raise HTTPException(404, str(e))
    except IllegalDesignTransitionError as e:
        raise HTTPException(409, str(e))
    return _project_dict(proj)


# -- Outcome ingestion / next iteration ------------------------------------


class OutcomeBody(BaseModel):
    actor_id: str
    observed_results: list[dict[str, Any]]
    construction_verified: bool
    assay_qc_passed: bool
    experiment_run_id: str | None = None
    constraint_violations: list[str] = []
    outcome_update: str = ""


@router.post("/candidates/{design_id}/outcome")
def ingest_outcome(design_id: str, body: OutcomeBody, session: Session = Depends(get_db_session)) -> dict:
    try:
        outcome = outcome_service.ingest_outcome(session, design_id=design_id, **body.model_dump())
    except ValueError as e:
        raise HTTPException(404, str(e))
    except IllegalDesignTransitionError as e:
        raise HTTPException(409, str(e))
    return {
        "outcome_id": outcome.outcome_id, "failure_classification": outcome.failure_classification,
        "decided_next_action": outcome.decided_next_action, "next_iteration_reason": outcome.next_iteration_reason,
        "residuals": outcome.residuals, "failure_case_id": outcome.failure_case_id,
    }


class NextIterationBody(BaseModel):
    actor_id: str


@router.post("/projects/{design_project_id}/next-iteration")
def start_next_iteration(design_project_id: str, body: NextIterationBody, session: Session = Depends(get_db_session)) -> dict:
    try:
        proj = governance_service.start_next_iteration_round(session, design_project_id=design_project_id, actor_id=body.actor_id)
    except ValueError as e:
        raise HTTPException(404, str(e))
    except IllegalDesignTransitionError as e:
        raise HTTPException(409, str(e))
    return _project_dict(proj)


# -- History / audit --------------------------------------------------------


@router.get("/projects/{design_project_id}/history")
def get_history(design_project_id: str, session: Session = Depends(get_db_session)) -> dict:
    return {"lineage": memory_integration.design_lineage_history(session, design_project_id=design_project_id)}


@router.get("/projects/{design_project_id}/audit-trail")
def get_audit_trail(design_project_id: str, session: Session = Depends(get_db_session)) -> dict:
    rows = session.execute(
        select(DesignWorkflowTransition).where(DesignWorkflowTransition.design_project_id == design_project_id).order_by(DesignWorkflowTransition.started_at)
    ).scalars().all()
    return {"transitions": [{"state": t.state, "selected_next_state": t.selected_next_state, "gate_result": t.gate_result, "started_at": t.started_at} for t in rows]}
