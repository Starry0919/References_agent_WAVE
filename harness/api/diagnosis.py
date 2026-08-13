"""Bottleneck Diagnosis Loop API routes (doc03 §9). Read/write against the
real workflow, not a demo page - every route calls the same service
functions the end-to-end smoke tests and integration tests exercise.
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from harness.api.deps import get_db_session
from harness.diagnosis import decision_service as dec_svc
from harness.diagnosis import evidence as evidence_svc
from harness.diagnosis import model_service as model_svc
from harness.diagnosis import service as diag_svc
from harness.diagnosis.loop import DiagnosisGateRejectedError, DiagnosisLoopController, IllegalDiagnosisTransitionError
from harness.diagnosis.model_adapters.registry import detect_all_capabilities
from harness.diagnosis.models import (
    DiagnosisDecision, DiagnosisSession, DiagnosisTransition, EngineeringProblem, EvidenceItem, EvidenceLink, HypothesisAssessment,
)
from harness.diagnosis.grounding import GroundingError, derive_engineering_problem, evaluate_observation_grounding
from harness.diagnosis.report import render_report
from harness.learning.models import HypothesisVersion
from harness.memory import event_types as et
from harness.projects.models import ProjectEvent

router = APIRouter(prefix="/api/diagnosis", tags=["diagnosis"])
_loop = DiagnosisLoopController()


class CreateSessionBody(BaseModel):
    project_id: str
    actor_id: str
    workflow_run_id: str | None = None
    triggering_failure_case_id: str | None = None
    objective_id: str | None = None
    biological_system: dict[str, Any] = {}
    baseline_observation_ids: list[str] = []
    observation_ids: list[str] = []


@router.post("/sessions")
def create_session(body: CreateSessionBody, session: Session = Depends(get_db_session)) -> dict:
    data = body.model_dump()
    observation_ids = data.pop("observation_ids")
    sess = diag_svc.start_diagnosis_session(session, **data)
    sess.pending_request_context = {**(sess.pending_request_context or {}), "observation_ids": observation_ids}
    session.flush()
    return {"diagnosis_session_id": sess.diagnosis_session_id, "status": sess.status}


@router.get("/sessions/{diagnosis_session_id}")
def get_session(diagnosis_session_id: str, session: Session = Depends(get_db_session)) -> dict:
    sess = diag_svc.get_session(session, diagnosis_session_id)
    if sess is None:
        raise HTTPException(404, "diagnosis session not found")
    return {
        "diagnosis_session_id": sess.diagnosis_session_id, "project_id": sess.project_id, "status": sess.status,
        "data_sufficiency": sess.data_sufficiency, "approval_state": sess.approval_state,
        "active_hypothesis_set_version": sess.active_hypothesis_set_version, "biological_system": sess.biological_system,
        "baseline_observation_ids": sess.baseline_observation_ids, "version": sess.version,
    }


class DeriveEngineeringProblemBody(BaseModel):
    observation_id: str
    comparison_observation_id: str
    abnormality_statement: str | None = None


@router.get("/sessions/{diagnosis_session_id}/grounding")
def get_grounding(diagnosis_session_id: str, session: Session = Depends(get_db_session)) -> dict:
    try:
        return evaluate_observation_grounding(session, diagnosis_session_id).to_dict()
    except GroundingError as e:
        raise HTTPException(404, str(e))


@router.post("/sessions/{diagnosis_session_id}/engineering-problems/derive")
def derive_problem(diagnosis_session_id: str, body: DeriveEngineeringProblemBody, session: Session = Depends(get_db_session)) -> dict:
    try:
        p = derive_engineering_problem(session, diagnosis_session_id=diagnosis_session_id, **body.model_dump())
    except GroundingError as e:
        raise HTTPException(422, str(e))
    return {"engineering_problem_id": p.engineering_problem_id, "status": p.status}


@router.get("/sessions/{diagnosis_session_id}/engineering-problems")
def list_engineering_problems(diagnosis_session_id: str, session: Session = Depends(get_db_session)) -> dict:
    rows = session.execute(select(EngineeringProblem).where(EngineeringProblem.diagnosis_session_id == diagnosis_session_id)).scalars().all()
    return {"engineering_problems": [{c.name: getattr(p, c.name) for c in p.__table__.columns} for p in rows]}


@router.get("/sessions")
def list_sessions_for_project(project_id: str, session: Session = Depends(get_db_session)) -> dict:
    rows = session.execute(
        select(DiagnosisSession).where(DiagnosisSession.project_id == project_id).order_by(DiagnosisSession.created_at.desc())
    ).scalars().all()
    return {
        "sessions": [
            {
                "diagnosis_session_id": s.diagnosis_session_id, "project_id": s.project_id, "status": s.status,
                "data_sufficiency": s.data_sufficiency, "approval_state": s.approval_state,
                "biological_system": s.biological_system, "created_at": s.created_at, "updated_at": s.updated_at,
            }
            for s in rows
        ]
    }


@router.get("/sessions/{diagnosis_session_id}/hypotheses")
def list_hypotheses(diagnosis_session_id: str, session: Session = Depends(get_db_session)) -> dict:
    assessments = session.execute(
        select(HypothesisAssessment).where(HypothesisAssessment.diagnosis_session_id == diagnosis_session_id)
    ).scalars().all()
    hyp_ids = {a.hypothesis_version_id for a in assessments}
    hyps = {
        h.hypothesis_version_id: h
        for h in session.execute(select(HypothesisVersion).where(HypothesisVersion.hypothesis_version_id.in_(hyp_ids))).scalars()
    } if hyp_ids else {}
    return {
        "hypotheses": [
            {
                "hypothesis_version_id": a.hypothesis_version_id, "status": a.status,
                "mechanism_class": hyps.get(a.hypothesis_version_id).mechanism_class if a.hypothesis_version_id in hyps else None,
                "statement": hyps.get(a.hypothesis_version_id).statement if a.hypothesis_version_id in hyps else None,
                "explanatory_coverage": a.explanatory_coverage, "contradictions": a.contradictions,
                # Module 2 §7/§9: already computed by hypothesis_generator.py
                # and persisted on HypothesisVersion, but this route never
                # returned them before - falsifiers/omics_layers stayed
                # invisible even after a successful diagnosis.
                "falsifiers": hyps.get(a.hypothesis_version_id).falsifiers if a.hypothesis_version_id in hyps else [],
                "omics_layers": (hyps.get(a.hypothesis_version_id).scope or {}).get("omics_layers", []) if a.hypothesis_version_id in hyps else [],
            }
            for a in assessments
        ]
    }


def _latest_reviews(session: Session, evidence_link_ids: list[str]) -> dict[str, dict]:
    """Latest human review verdict per evidence link, read back off the
    `ProjectEvent` ledger (see `evidence_svc.review_evidence_link`'s
    docstring for why this isn't a mutable column)."""
    if not evidence_link_ids:
        return {}
    rows = session.execute(
        select(ProjectEvent)
        .where(ProjectEvent.entity_type == "EvidenceLink", ProjectEvent.entity_id.in_(evidence_link_ids), ProjectEvent.event_type == et.DIAGNOSIS_EVIDENCE_LINK_REVIEWED)
        .order_by(ProjectEvent.seq)
    ).scalars().all()
    latest: dict[str, dict] = {}
    for r in rows:
        latest[r.entity_id] = r.payload  # ordered by seq ascending, so the last write per id wins
    return latest


@router.get("/sessions/{diagnosis_session_id}/evidence")
def list_evidence(diagnosis_session_id: str, session: Session = Depends(get_db_session)) -> dict:
    assessments = session.execute(
        select(HypothesisAssessment).where(HypothesisAssessment.diagnosis_session_id == diagnosis_session_id)
    ).scalars().all()
    hyp_ids = {a.hypothesis_version_id for a in assessments}
    links = session.execute(select(EvidenceLink).where(EvidenceLink.hypothesis_version_id.in_(hyp_ids))).scalars().all() if hyp_ids else []
    reviews = _latest_reviews(session, [l.evidence_link_id for l in links])
    return {
        "evidence_links": [
            {
                "evidence_link_id": l.evidence_link_id, "hypothesis_version_id": l.hypothesis_version_id,
                "evidence_item_id": l.evidence_item_id, "relation": l.relation, "claim": l.claim,
                "review_status": reviews[l.evidence_link_id]["verdict"] if l.evidence_link_id in reviews else "unreviewed",
                "review_note": reviews[l.evidence_link_id].get("note", "") if l.evidence_link_id in reviews else "",
            }
            for l in links
        ]
    }


class ReviewEvidenceLinkBody(BaseModel):
    verdict: str
    actor_id: str
    note: str = ""


@router.post("/evidence-links/{evidence_link_id}/review")
def review_evidence_link(evidence_link_id: str, body: ReviewEvidenceLinkBody, session: Session = Depends(get_db_session)) -> dict:
    try:
        evidence_svc.review_evidence_link(session, evidence_link_id=evidence_link_id, **body.model_dump())
    except evidence_svc.InvalidReviewVerdict as e:
        raise HTTPException(422, str(e))
    except ValueError as e:
        raise HTTPException(404, str(e))
    return {"evidence_link_id": evidence_link_id, "verdict": body.verdict}


class LinkEvidenceBody(BaseModel):
    hypothesis_version_id: str
    evidence_item_id: str
    relation: str
    actor_id: str
    claim: str = ""
    condition_match: str = "unknown"


@router.post("/evidence-links")
def link_evidence(body: LinkEvidenceBody, session: Session = Depends(get_db_session)) -> dict:
    try:
        link = evidence_svc.link_evidence(session, **body.model_dump())
    except evidence_svc.InvalidEvidenceRelation as e:
        raise HTTPException(422, str(e))
    return {"evidence_link_id": link.evidence_link_id}


@router.get("/evidence-items")
def list_evidence_items(project_id: str, session: Session = Depends(get_db_session)) -> dict:
    """So the frontend can offer a picker instead of asking the user to
    remember/type an `evidence_item_id` by hand."""
    rows = session.execute(
        select(EvidenceItem).where(EvidenceItem.project_id == project_id).order_by(EvidenceItem.created_at.desc())
    ).scalars().all()
    return {
        "evidence_items": [
            {
                "evidence_item_id": r.evidence_item_id, "source_type": r.source_type,
                "source_reference": r.source_reference, "content_summary": r.content_summary,
                "quality": r.quality, "directness": r.directness, "created_at": r.created_at,
            }
            for r in rows
        ]
    }


class CreateEvidenceItemBody(BaseModel):
    project_id: str
    actor_id: str
    source_type: str
    content_summary: str
    source_reference: str | None = None
    quality: str = "low"
    directness: str = "indirect"


@router.post("/evidence-items")
def create_evidence_item(body: CreateEvidenceItemBody, session: Session = Depends(get_db_session)) -> dict:
    """`evidence_item_id` is always server-generated (`evidence_svc.record_evidence_item`
    -> `new_id("EVID")`) - the request body never carries a caller-supplied id."""
    item = evidence_svc.record_evidence_item(session, **body.model_dump())
    return {"evidence_item_id": item.evidence_item_id}


@router.get("/model-capabilities")
def model_capabilities() -> dict:
    caps = detect_all_capabilities()
    return {name: {"available": c.available, "reason": c.reason} for name, c in caps.items()}


class RunModelBody(BaseModel):
    project_id: str
    diagnosis_session_id: str
    adapter_name: str
    actor_id: str
    inputs: dict[str, Any] = {}
    context: dict[str, Any] = {}
    constraints_objective_parameters: dict[str, Any] = {}
    sensitivity_variant_of: str | None = None


@router.post("/model-runs")
def run_model(body: RunModelBody, session: Session = Depends(get_db_session)) -> dict:
    try:
        record = model_svc.execute_model_run(session, **body.model_dump())
    except KeyError as e:
        raise HTTPException(400, str(e))
    return {
        "model_run_id": record.model_run_id, "capability_status": record.capability_status,
        "runtime_status": record.runtime_status, "outputs": record.outputs, "log_summary": record.log_summary,
    }


@router.get("/sessions/{diagnosis_session_id}/tests")
def list_tests(diagnosis_session_id: str, session: Session = Depends(get_db_session)) -> dict:
    from harness.diagnosis.models import DiagnosticTest, ExperimentalExecutionPlan

    tests = session.execute(select(DiagnosticTest).where(DiagnosticTest.diagnosis_session_id == diagnosis_session_id)).scalars().all()
    result = []
    for t in tests:
        plans = session.execute(select(ExperimentalExecutionPlan).where(ExperimentalExecutionPlan.diagnostic_test_id == t.test_id)).scalars().all()
        result.append({
            "test_id": t.test_id, "assay": t.assay, "status": t.status, "discriminates_hypotheses": t.discriminates_hypotheses,
            "expected_information_gain": t.expected_information_gain,
            "plans": [{"plan_id": p.plan_id, "readiness": p.readiness} for p in plans],
        })
    return {"tests": result}


class HumanApprovalBody(BaseModel):
    decision_id: str
    actor_id: str
    approved: bool
    reason: str = ""


@router.post("/decisions/{decision_id}/approve")
def approve_decision(decision_id: str, body: HumanApprovalBody, session: Session = Depends(get_db_session)) -> dict:
    status = "approved" if body.approved else "rejected"
    try:
        d = dec_svc.set_handoff_status(
            session, decision_id=decision_id, handoff_status=status, actor_id=body.actor_id,
            human_approval={"approver": body.actor_id, "decision": status, "reason": body.reason},
        )
    except ValueError as e:
        raise HTTPException(404, str(e))
    return {"decision_id": d.decision_id, "handoff_status": d.handoff_status}


@router.get("/sessions/{diagnosis_session_id}/decisions")
def list_decisions(diagnosis_session_id: str, session: Session = Depends(get_db_session)) -> dict:
    rows = session.execute(
        select(DiagnosisDecision).where(DiagnosisDecision.diagnosis_session_id == diagnosis_session_id).order_by(DiagnosisDecision.diagnosis_version)
    ).scalars().all()
    return {
        "decisions": [
            {
                "decision_id": d.decision_id, "diagnosis_version": d.diagnosis_version, "stopping_reason": d.stopping_reason,
                "allowed_next_action": d.allowed_next_action, "handoff_status": d.handoff_status,
                "leading_hypothesis_ids": d.leading_hypothesis_ids, "alternatives_not_excluded_ids": d.alternatives_not_excluded_ids,
            }
            for d in rows
        ]
    }


@router.get("/sessions/{diagnosis_session_id}/audit-trail")
def audit_trail(diagnosis_session_id: str, session: Session = Depends(get_db_session)) -> dict:
    rows = session.execute(
        select(DiagnosisTransition).where(DiagnosisTransition.diagnosis_session_id == diagnosis_session_id).order_by(DiagnosisTransition.started_at)
    ).scalars().all()
    return {
        "transitions": [
            {"state": t.state, "selected_next_state": t.selected_next_state, "gate_result": t.gate_result, "started_at": t.started_at}
            for t in rows
        ]
    }


@router.get("/sessions/{diagnosis_session_id}/report")
def get_report(diagnosis_session_id: str, session: Session = Depends(get_db_session)) -> dict:
    try:
        report = render_report(session, diagnosis_session_id=diagnosis_session_id)
    except ValueError as e:
        raise HTTPException(404, str(e))
    return report.to_dict()


@router.get("/sessions/{diagnosis_session_id}/mechanism-graph")
def get_mechanism_graph(diagnosis_session_id: str, session: Session = Depends(get_db_session)) -> dict:
    """Module 2 (Engineering Decision Intelligence Layer prompt §8): the
    Engineering Reasoning Graph, read-only. `build_mechanism_graph`'s output
    is not persisted anywhere (`HypothesisVersion.mechanism_graph_ref` is a
    bare reference string no writer ever populates) - this recomputes the
    same, real, deterministic graph the diagnosis pipeline itself built from
    the project's own `target_product`/`host_definition`, never a fabricated
    or cached-stale view.
    """
    from dataclasses import asdict

    from harness.diagnosis.mechanism_graph import build_mechanism_graph
    from harness.projects.models import Project

    sess = diag_svc.get_session(session, diagnosis_session_id)
    if sess is None:
        raise HTTPException(404, "diagnosis session not found")
    proj = session.get(Project, sess.project_id)
    host = " ".join(str(v) for v in (proj.host_definition or {}).values() if v) if proj else "unknown"
    product = proj.target_product if proj else "unknown"
    graph = build_mechanism_graph(
        phenotype=f"bottleneck diagnosis for {product}", product=product or "unknown", host=host or "unknown",
    )
    return {
        "nodes": [asdict(n) for n in graph.nodes],
        "edges": [asdict(e) for e in graph.edges],
        "unknowns": graph.unknowns,
    }


_SESSION_ACTIONS = (
    "mark_hypotheses_generated", "mark_evidence_assessed", "mark_model_evidence_pending", "mark_hypotheses_ranked",
    "enter_model_conflicted", "enter_test_selection_required", "select_test", "enter_awaiting_test_result",
    "ingest_test_result_and_update_belief", "resolve_human_review", "reopen_diagnosis", "close_diagnosis",
)


class SessionActionBody(BaseModel):
    actor_id: str
    kwargs: dict[str, Any] = {}


@router.post("/sessions/{diagnosis_session_id}/action/{action}")
def session_action(diagnosis_session_id: str, action: str, body: SessionActionBody, session: Session = Depends(get_db_session)) -> dict:
    if action not in _SESSION_ACTIONS:
        raise HTTPException(400, f"unknown or unsupported action {action!r}; must be one of {_SESSION_ACTIONS}")
    sess = diag_svc.get_session(session, diagnosis_session_id)
    if sess is None:
        raise HTTPException(404, "diagnosis session not found")
    fn = getattr(_loop, action)
    try:
        fn(session, sess, actor_id=body.actor_id, **body.kwargs)
    except IllegalDiagnosisTransitionError as e:
        raise HTTPException(409, str(e))
    except DiagnosisGateRejectedError as e:
        raise HTTPException(422, str(e))
    return {"diagnosis_session_id": sess.diagnosis_session_id, "status": sess.status}
