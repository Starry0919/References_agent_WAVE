"""Model Update Proposal governance (doc06 §3.12/§9.4). Level 1 (project
belief) may be auto-applied; Levels 3-5 (parameter calibration / model
structure / retraining) require a `ModelUpdateDecision` (Human Gate) before
`status` can leave `proposed` - enforced here AND independently by
`harness.virtual_cell.guards.assert_update_may_activate`, so a caller that
skips this service function and tries to flip `status` directly still
cannot activate an ungated Level 3-5 proposal (`guard_immutable_fields`
only allows `status` to change at all, but nothing stops a bug from
setting it without a decision row - the guard call here is what a
persistence-layer test actually exercises).
"""
from __future__ import annotations

from harness.ids import new_id, now
from harness.memory import event_types as et
from harness.memory.event_store import append_event
from harness.virtual_cell.guards import SimulationGuardError, assert_update_may_activate
from harness.virtual_cell.models import UPDATE_LEVELS, UPDATE_LEVELS_REQUIRING_HUMAN_GATE, ModelUpdateDecision, ModelUpdateProposal


def propose_update(
    session, *, project_id: str, residual_ids: list[str], update_level: str, rationale: str, actor_id: str,
    required_data: list[str] | None = None, validation_plan: str = "", rollback_plan: str = "", model_id: str | None = None,
) -> ModelUpdateProposal:
    if update_level not in UPDATE_LEVELS:
        raise ValueError(f"unknown update_level {update_level!r}; must be one of {UPDATE_LEVELS}")
    if not residual_ids:
        raise ValueError("a ModelUpdateProposal must cite at least one triggering residual")

    proposal = ModelUpdateProposal(
        proposal_id=new_id("MUP"), project_id=project_id, triggering_residual_ids=residual_ids, update_level=update_level,
        rationale=rationale, required_data=required_data or [], identifiability_status="unknown",
        validation_plan=validation_plan, rollback_plan=rollback_plan,
        human_approval_required=update_level in UPDATE_LEVELS_REQUIRING_HUMAN_GATE, status="proposed", model_id=model_id,
        created_at=now(),
    )
    session.add(proposal)
    session.flush()
    append_event(
        session, project_id=project_id, event_type=et.VC_UPDATE_PROPOSED, entity_type="ModelUpdateProposal",
        entity_id=proposal.proposal_id, payload={"update_level": update_level, "rationale": rationale, "residual_ids": residual_ids},
        actor_type="agent", actor_id=actor_id,
    )
    return proposal


def auto_apply_level1(session, *, proposal: ModelUpdateProposal, actor_id: str) -> ModelUpdateProposal:
    """doc06 §9.4 Level 1: project belief / residual-history updates may be
    appended automatically - never Levels 2-5."""
    if proposal.update_level != "project_belief":
        raise SimulationGuardError(f"only update_level='project_belief' may be auto-applied; got {proposal.update_level!r}")
    proposal.status = "applied"
    session.flush()
    append_event(
        session, project_id=proposal.project_id, event_type=et.VC_UPDATE_DECIDED, entity_type="ModelUpdateProposal",
        entity_id=proposal.proposal_id, payload={"status": "applied", "auto_applied": True}, actor_type="agent", actor_id=actor_id,
    )
    return proposal


def decide_update(
    session, *, proposal: ModelUpdateProposal, decision: str, approver_id: str, approver_role: str = "", rationale: str = "", conditions: list[str] | None = None,
) -> ModelUpdateDecision:
    if decision not in ("approved", "rejected"):
        raise ValueError(f"decision must be 'approved' or 'rejected', got {decision!r}")

    row = ModelUpdateDecision(
        decision_id=new_id("MUDEC"), proposal_id=proposal.proposal_id, decision=decision, approver_id=approver_id,
        approver_role=approver_role, rationale=rationale, conditions=conditions or [], created_at=now(),
    )
    session.add(row)
    session.flush()

    if decision == "approved":
        assert_update_may_activate(proposal, has_human_approval=True)
        proposal.status = "approved"
    else:
        proposal.status = "rejected"
    session.flush()

    append_event(
        session, project_id=proposal.project_id, event_type=et.VC_UPDATE_DECIDED, entity_type="ModelUpdateProposal",
        entity_id=proposal.proposal_id, payload={"status": proposal.status, "decision_id": row.decision_id, "approver_id": approver_id},
        actor_type="human", actor_id=approver_id,
    )
    return row
