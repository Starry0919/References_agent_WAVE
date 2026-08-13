"""Mandatory candidate decision state machine; no generated-to-build shortcuts."""
from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from harness.engineering_design.models import BuildTestPackage, CandidateDesign, DesignEvaluation, HumanApprovalRecord


class InvalidCandidateTransition(RuntimeError): pass


_ALLOWED = {
    "candidate_generated": {"evaluation_pending"}, "evaluation_pending": {"evaluated"},
    "evaluated": {"rejected", "ranked"}, "ranked": {"human_selection_pending"},
    "human_selection_pending": {"selected", "rejected"}, "selected": {"validation_plan_pending"},
    "validation_plan_pending": {"validation_ready"}, "validation_ready": {"build_ready"},
    "rejected": set(), "build_ready": set(),
}


def transition_candidate(db: Session, *, design_id: str, target: str, actor_id: str,
                         reasons: list[str] | None = None) -> CandidateDesign:
    candidate = db.get(CandidateDesign, design_id)
    if candidate is None: raise ValueError(f"no such candidate: {design_id}")
    current = candidate.decision_state or "candidate_generated"
    if target not in _ALLOWED.get(current, set()):
        raise InvalidCandidateTransition(f"illegal transition {current} -> {target}")
    evaluations = db.execute(select(DesignEvaluation).where(DesignEvaluation.design_id == design_id)).scalars().all()
    if target in {"evaluated", "ranked", "human_selection_pending"} and not evaluations:
        raise InvalidCandidateTransition("candidate has no persisted evaluation")
    if target == "selected":
        approvals = db.execute(select(HumanApprovalRecord).where(
            HumanApprovalRecord.design_id == design_id, HumanApprovalRecord.decision == "approved"
        )).scalars().all()
        if not approvals: raise InvalidCandidateTransition("human selection record is required")
    if target in {"validation_ready", "build_ready"}:
        package = db.get(BuildTestPackage, candidate.build_test_package_id) if candidate.build_test_package_id else None
        if package is None or package.readiness != "build_ready":
            raise InvalidCandidateTransition("complete ValidationPlan/BuildTestPackage is required")
    candidate.decision_state = target
    status_projection = {
        "candidate_generated": "proposed", "evaluation_pending": "proposed", "evaluated": "proposed",
        "ranked": "proposed", "human_selection_pending": "proposed", "selected": "selected",
        "validation_plan_pending": "selected", "validation_ready": "selected", "build_ready": "approved_for_build",
        "rejected": "rejected",
    }
    readiness_projection = {
        "candidate_generated": "conceptual", "evaluation_pending": "conceptual", "evaluated": "evaluated",
        "rejected": "evaluated", "ranked": "evaluated", "human_selection_pending": "evaluated",
        "selected": "evaluated", "validation_plan_pending": "planning_ready",
        "validation_ready": "planning_ready", "build_ready": "build_ready",
    }
    candidate.status = status_projection[target]
    candidate.readiness = readiness_projection[target]
    if target == "rejected" and reasons:
        candidate.rejection_reasons = [*candidate.rejection_reasons, *reasons]
    db.flush(); return candidate


def set_execution_status(db: Session, *, design_id: str, status: str) -> CandidateDesign:
    """Post-decision compatibility lifecycle, guarded by build readiness."""
    candidate = db.get(CandidateDesign, design_id)
    if candidate is None: raise ValueError(f"no such candidate: {design_id}")
    if candidate.decision_state != "build_ready":
        raise InvalidCandidateTransition("execution lifecycle requires build_ready decision state")
    allowed = {"approved_for_build":{"built"},"built":{"tested"}}
    if status not in allowed.get(candidate.status,set()):
        raise InvalidCandidateTransition(f"illegal execution status {candidate.status} -> {status}")
    candidate.status=status; db.flush(); return candidate
