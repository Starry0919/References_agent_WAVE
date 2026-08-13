"""Learning engine (hypothesis/failure/redesign) + KnowledgeClaim API
routes."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from harness.api.deps import get_db_session
from harness.learning import service as learning_svc
from harness.learning.redesign import RedesignRejected, propose_redesign
from harness.memory import knowledge_claims as kc

router = APIRouter(prefix="/api/learning", tags=["learning"])


class HypothesisFamilyBody(BaseModel):
    project_id: str
    title: str


@router.post("/hypothesis-families")
def create_hypothesis_family(body: HypothesisFamilyBody, session: Session = Depends(get_db_session)) -> dict:
    fam = learning_svc.create_hypothesis_family(session, **body.model_dump())
    return {"hypothesis_family_id": fam.hypothesis_family_id}


class ProposeHypothesisBody(BaseModel):
    project_id: str
    hypothesis_family_id: str
    statement: str
    actor_id: str
    predicted_observations: list[Any] = []
    supporting_evidence_ids: list[str] = []
    contradicting_evidence_ids: list[str] = []
    alternatives: list[str] = []
    posterior_status: str = "inconclusive"
    confidence: str = "low"
    applicability_scope: dict[str, Any] = {}


@router.post("/hypotheses")
def propose_hypothesis(body: ProposeHypothesisBody, session: Session = Depends(get_db_session)) -> dict:
    hv = learning_svc.propose_hypothesis(session, **body.model_dump())
    return {"hypothesis_version_id": hv.hypothesis_version_id, "posterior_status": hv.posterior_status}


class ReviseHypothesisBody(BaseModel):
    parent_hypothesis_version_id: str
    statement: str
    posterior_status: str
    confidence: str
    actor_id: str
    has_expected_vs_observed: bool
    has_alternatives_considered: bool
    has_uncertainty: bool
    supporting_evidence_ids: list[str] = []
    contradicting_evidence_ids: list[str] = []
    alternatives: list[str] = []


@router.post("/hypotheses/revise")
def revise_hypothesis(body: ReviseHypothesisBody, session: Session = Depends(get_db_session)) -> dict:
    try:
        hv = learning_svc.revise_hypothesis(session, **body.model_dump())
    except learning_svc.HypothesisUpdateRejected as e:
        raise HTTPException(422, str(e))
    except ValueError as e:
        raise HTTPException(404, str(e))
    return {"hypothesis_version_id": hv.hypothesis_version_id, "posterior_status": hv.posterior_status, "parent_hypothesis_version_id": hv.parent_hypothesis_version_id}


class ClassifyFailureBody(BaseModel):
    project_id: str
    failure_class: str
    actor_id: str
    design_version_id: str | None = None
    experiment_run_id: str | None = None
    expected_outcome: str = ""
    observed_outcome_ids: list[str] = []
    data_qc_status: str = "passed"
    candidate_causes: list[str] = []
    causal_confidence: str = "low"
    applicability_scope: dict[str, Any] = {}


@router.post("/failures")
def classify_failure(body: ClassifyFailureBody, session: Session = Depends(get_db_session)) -> dict:
    try:
        fc = learning_svc.classify_failure(session, **body.model_dump())
    except ValueError as e:
        raise HTTPException(400, str(e))
    return {"failure_case_id": fc.failure_case_id, "failure_class": fc.failure_class}


class RedesignBody(BaseModel):
    project_id: str
    parent_design_version_id: str
    version_label: str
    branch_name: str = "main"
    new_genotype_manifest: dict[str, Any]
    new_decisions: list[dict[str, Any]] = []
    triggering_justification: str
    created_from_learning_cycle_id: str
    proposed_by: str


@router.post("/redesign")
def redesign(body: RedesignBody, session: Session = Depends(get_db_session)) -> dict:
    try:
        dv, diff = propose_redesign(session, **body.model_dump())
    except RedesignRejected as e:
        raise HTTPException(422, str(e))
    return {"design_version_id": dv.design_version_id, "genotype_diff": diff}


class SubmitClaimBody(BaseModel):
    project_id: str
    statement: str
    scope: dict[str, Any]
    supporting_experiments: list[str]
    independence_groups: list[list[str]]
    created_by: str
    contradicting_experiments: list[str] = []
    evidence_grade: str = "low"


@router.post("/knowledge-claims")
def submit_claim(body: SubmitClaimBody, session: Session = Depends(get_db_session)) -> dict:
    claim = kc.submit_claim(session, **body.model_dump())
    return {"claim_id": claim.claim_id, "status": claim.status}


class PromoteClaimBody(BaseModel):
    target_status: str
    reviewer_id: str
    reason: str = ""


@router.post("/knowledge-claims/{claim_id}/promote")
def promote_claim(claim_id: str, body: PromoteClaimBody, session: Session = Depends(get_db_session)) -> dict:
    try:
        claim = kc.promote_claim(session, claim_id=claim_id, **body.model_dump())
    except kc.PromotionRejected as e:
        raise HTTPException(422, str(e))
    except ValueError as e:
        raise HTTPException(404, str(e))
    return {"claim_id": claim.claim_id, "status": claim.status, "promotion_record": claim.promotion_record}


class RetractClaimBody(BaseModel):
    reviewer_id: str
    reason: str


@router.post("/knowledge-claims/{claim_id}/retract")
def retract_claim(claim_id: str, body: RetractClaimBody, session: Session = Depends(get_db_session)) -> dict:
    try:
        claim = kc.retract_claim(session, claim_id=claim_id, **body.model_dump())
    except ValueError as e:
        raise HTTPException(404, str(e))
    return {"claim_id": claim.claim_id, "status": claim.status}


@router.get("/knowledge-claims/{claim_id}")
def get_claim(claim_id: str, session: Session = Depends(get_db_session)) -> dict:
    claim = kc.get_claim(session, claim_id)
    if claim is None:
        raise HTTPException(404, "knowledge claim not found")
    return {
        "claim_id": claim.claim_id, "statement": claim.statement, "scope": claim.scope, "status": claim.status,
        "independence_groups": claim.independence_groups, "evidence_grade": claim.evidence_grade,
        "promotion_record": claim.promotion_record,
    }
