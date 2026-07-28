"""DesignVersion, genotype/decision diff, and Construct API routes."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from harness.api.deps import get_db_session
from harness.constructs import service as construct_svc
from harness.constructs.service import InvalidVerificationResult
from harness.designs import service as design_svc
from harness.designs.decision_diff import diff_decisions
from harness.designs.genotype_diff import diff_genotype
from harness.designs.service import MalformedDecisionError, SelfApprovalError

router = APIRouter(prefix="/api", tags=["designs"])


def _decision_dict(d) -> dict[str, Any]:
    return {
        "decision_id": d.decision_id, "target": d.target, "target_type": d.target_type, "operation": d.operation,
        "mechanism_hypothesis_ids": d.mechanism_hypothesis_ids, "expected_effects": d.expected_effects,
        "risks": d.risks, "evidence_ids": d.evidence_ids, "confidence": d.confidence, "approval_state": d.approval_state,
        "source_run_id": d.source_run_id,
    }


def _design_dict(session: Session, dv) -> dict[str, Any]:
    return {
        "design_version_id": dv.design_version_id, "project_id": dv.project_id, "version_label": dv.version_label,
        "parent_version_ids": dv.parent_version_ids, "branch_name": dv.branch_name, "genotype_manifest": dv.genotype_manifest,
        "status": dv.status, "proposed_by": dv.proposed_by, "created_at": dv.created_at,
        "decisions": [_decision_dict(d) for d in design_svc.list_decisions(session, dv.design_version_id)],
    }


class ProposeDesignBody(BaseModel):
    project_id: str
    version_label: str
    parent_version_ids: list[str] = []
    branch_name: str = "main"
    genotype_manifest: dict[str, Any]
    decisions: list[dict[str, Any]] = []
    proposed_by: str


@router.post("/designs")
def propose_design(body: ProposeDesignBody, session: Session = Depends(get_db_session)) -> dict:
    try:
        dv = design_svc.propose_design_version(session, **body.model_dump())
    except MalformedDecisionError as e:
        raise HTTPException(422, str(e))
    except ValueError as e:
        raise HTTPException(404, str(e))
    return _design_dict(session, dv)


# NOTE: fixed-path routes ("/designs/diff") MUST be registered before the
# parameterized "/designs/{design_version_id}" route below - Starlette
# matches routes in registration order, so a mismatched order here would
# make a request for "/designs/diff" resolve design_version_id="diff"
# instead (a real bug this smoke test caught - see 问题02_实施报告.md).
@router.get("/designs/diff")
def get_design_diff(a: str, b: str, session: Session = Depends(get_db_session)) -> dict:
    dv_a = design_svc.get_design_version(session, a)
    dv_b = design_svc.get_design_version(session, b)
    if dv_a is None or dv_b is None:
        raise HTTPException(404, "one or both design versions not found")
    decisions_a = [_decision_dict(d) for d in design_svc.list_decisions(session, a)]
    decisions_b = [_decision_dict(d) for d in design_svc.list_decisions(session, b)]
    return {
        "genotype_diff": diff_genotype(dv_a.genotype_manifest, dv_b.genotype_manifest),
        "decision_diff": diff_decisions(decisions_a, decisions_b),
    }


@router.get("/designs/{design_version_id}")
def get_design(design_version_id: str, session: Session = Depends(get_db_session)) -> dict:
    dv = design_svc.get_design_version(session, design_version_id)
    if dv is None:
        raise HTTPException(404, "design version not found")
    return _design_dict(session, dv)


class ApproveDesignBody(BaseModel):
    approver_id: str
    expected_project_version: int


@router.post("/designs/{design_version_id}/approve")
def approve_design(design_version_id: str, body: ApproveDesignBody, session: Session = Depends(get_db_session)) -> dict:
    try:
        dv = design_svc.approve_design_version(
            session, design_version_id=design_version_id, approver_id=body.approver_id,
            expected_project_version=body.expected_project_version,
        )
    except SelfApprovalError as e:
        raise HTTPException(409, str(e))
    except ValueError as e:
        raise HTTPException(404, str(e))
    return _design_dict(session, dv)


class RegisterConstructBody(BaseModel):
    project_id: str
    design_version_id: str
    created_by: str


@router.post("/constructs")
def register_construct(body: RegisterConstructBody, session: Session = Depends(get_db_session)) -> dict:
    try:
        c = construct_svc.register_construct(session, **body.model_dump())
    except ValueError as e:
        raise HTTPException(404, str(e))
    return {"construct_id": c.construct_id, "status": c.status}


@router.get("/constructs/{construct_id}")
def get_construct(construct_id: str, session: Session = Depends(get_db_session)) -> dict:
    from harness.constructs.models import Construct

    c = session.get(Construct, construct_id)
    if c is None:
        raise HTTPException(404, "construct not found")
    return {
        "construct_id": c.construct_id, "design_version_id": c.design_version_id, "status": c.status,
        "physical_stock_ref_id": c.physical_stock_ref_id,
    }


class VerifyGenotypeBody(BaseModel):
    project_id: str
    method: str
    result: str
    detail: str = ""
    verified_by: str


@router.post("/constructs/{construct_id}/verify")
def verify_genotype(construct_id: str, body: VerifyGenotypeBody, session: Session = Depends(get_db_session)) -> dict:
    try:
        v = construct_svc.record_genotype_verification(session, construct_id=construct_id, **body.model_dump())
    except InvalidVerificationResult as e:
        raise HTTPException(422, str(e))
    except ValueError as e:
        raise HTTPException(404, str(e))
    return {"verification_id": v.verification_id, "result": v.result}
