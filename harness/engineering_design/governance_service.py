"""Planning completion, Human Approval Gate, and build-status progression
(doc04 §2.7, §4.1): the ONE place a `CandidateDesign` may move past
`awaiting_human_approval` - proposer and approver are structurally
distinct (reuses `harness.designs.service.SelfApprovalError`, the same
"proposer cannot self-approve" rule doc 6.11 already established for
Problem 02's own `DesignVersion.approve`).
"""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from harness.designs.service import SelfApprovalError
from harness.engineering_design.loop import EngineeringDesignLoopController
from harness.engineering_design.models import CandidateDesign, EngineeringDesignProject, HumanApprovalRecord
from harness.ids import new_id, now
from harness.memory import event_types as et
from harness.memory.event_store import append_event, snapshot
from harness.scientific_evaluation import gate_hooks
from harness.engineering_design.decision_state import InvalidCandidateTransition, transition_candidate

_loop = EngineeringDesignLoopController()

APPROVAL_SNAPSHOT_FIELDS = (
    "approval_id", "design_id", "design_version", "scope", "approver_id", "approver_role", "decision",
    "conditions", "reason", "created_at",
)


def mark_planning_complete(session: Session, *, design_project_id: str, actor_id: str) -> EngineeringDesignProject:
    """doc04 §4.1: `portfolio_evaluated -> planning_ready` requires at
    least one candidate to have reached `planning_ready`/`build_ready` -
    never advances the whole project on an empty portfolio."""
    proj = session.get(EngineeringDesignProject, design_project_id)
    if proj is None:
        raise ValueError(f"no such design project: {design_project_id}")
    ready = session.execute(
        select(CandidateDesign).where(
            CandidateDesign.design_project_id == design_project_id,
            CandidateDesign.decision_state == "build_ready",
        )
    ).scalars().first()
    if ready is None:
        raise ValueError("no human-selected candidate has a complete ValidationPlan/build_ready state")
    gate_hooks.check_before_planning_complete(session, design_project_id=design_project_id)
    return _loop.complete_planning(session, proj, actor_id=actor_id)


def request_human_approval(session: Session, *, design_project_id: str, actor_id: str) -> EngineeringDesignProject:
    proj = session.get(EngineeringDesignProject, design_project_id)
    if proj is None:
        raise ValueError(f"no such design project: {design_project_id}")
    candidates = session.execute(select(CandidateDesign).where(CandidateDesign.design_project_id == design_project_id)).scalars().all()
    if not any(c.decision_state == "human_selection_pending" for c in candidates):
        raise ValueError("no ranked candidate is awaiting human selection")
    return _loop.request_human_approval(session, proj, actor_id=actor_id)


def record_human_decision(
    session: Session,
    *,
    design_id: str,
    approver_id: str,
    decision: str,  # approved|rejected
    approver_role: str = "",
    conditions: list[str] | None = None,
    reason: str = "",
) -> tuple[HumanApprovalRecord, CandidateDesign, EngineeringDesignProject]:
    candidate = session.get(CandidateDesign, design_id)
    if candidate is None:
        raise ValueError(f"no such candidate design: {design_id}")
    if approver_id == candidate.proposed_by:
        raise SelfApprovalError(f"actor {approver_id!r} proposed candidate {design_id} and cannot also approve it")
    proj = session.get(EngineeringDesignProject, candidate.design_project_id)
    if candidate.decision_state != "human_selection_pending":
        raise InvalidCandidateTransition("human decision requires human_selection_pending")

    approval = HumanApprovalRecord(
        approval_id=new_id("HAPR"), design_id=design_id, design_version=candidate.design_version,
        scope="approved_for_build", approver_id=approver_id, approver_role=approver_role, decision=decision,
        conditions=conditions or [], reason=reason, created_at=now(),
    )
    session.add(approval)
    session.flush()
    append_event(
        session, project_id=proj.project_id, event_type=et.DESIGN_HUMAN_DECISION_RECORDED, entity_type="HumanApprovalRecord",
        entity_id=approval.approval_id, payload=snapshot(approval, APPROVAL_SNAPSHOT_FIELDS), actor_type="human", actor_id=approver_id,
    )

    approved = decision == "approved"
    if approved:
        transition_candidate(session, design_id=design_id, target="selected", actor_id=approver_id)
        transition_candidate(session, design_id=design_id, target="validation_plan_pending", actor_id=approver_id)
    else:
        transition_candidate(session, design_id=design_id, target="rejected", actor_id=approver_id,
                             reasons=[reason] if reason else [])

    _loop.record_human_decision(session, proj, actor_id=approver_id, approved=approved)
    return approval, candidate, proj


def start_build(session: Session, *, design_project_id: str, design_id: str, actor_id: str) -> CandidateDesign:
    proj = session.get(EngineeringDesignProject, design_project_id)
    candidate = session.get(CandidateDesign, design_id)
    if proj is None or candidate is None:
        raise ValueError("no such design project or candidate")
    if candidate.decision_state != "build_ready":
        raise InvalidCandidateTransition("candidate must be build_ready before build starts")
    _loop.start_build(session, proj, actor_id=actor_id)
    from harness.engineering_design.decision_state import set_execution_status
    set_execution_status(session, design_id=design_id, status="built")
    session.flush()
    append_event(
        session, project_id=proj.project_id, event_type=et.DESIGN_BUILD_STATUS_CHANGED, entity_type="CandidateDesign",
        entity_id=candidate.design_id, payload={"design_id": candidate.design_id, "status": candidate.status}, actor_type="human", actor_id=actor_id,
    )
    return candidate


def mark_test_pending(session: Session, *, design_project_id: str, actor_id: str) -> EngineeringDesignProject:
    proj = session.get(EngineeringDesignProject, design_project_id)
    if proj is None:
        raise ValueError(f"no such design project: {design_project_id}")
    return _loop.mark_test_pending(session, proj, actor_id=actor_id)


def start_next_iteration_round(session: Session, *, design_project_id: str, actor_id: str) -> EngineeringDesignProject:
    """doc04 §4.7: re-enters `strategy_generated` from `next_iteration` -
    the next `strategy_service.generate_and_persist_strategies` /
    `portfolio_service.generate_and_persist_portfolio` call for this
    project will read `memory_integration`'s history and so will not repeat
    a no-new-evidence rejected/failed candidate."""
    proj = session.get(EngineeringDesignProject, design_project_id)
    if proj is None:
        raise ValueError(f"no such design project: {design_project_id}")
    return _loop.restart_from_next_iteration(session, proj, actor_id=actor_id)
