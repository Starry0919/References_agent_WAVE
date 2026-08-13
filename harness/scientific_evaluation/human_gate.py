"""Human Evaluation Gate (doc05 §2.7/§3.11): the ONE place an
`EvaluationCase` may move into `approved_for_planning`/`approved_for_build`
- and every other terminal/human-arbitrated state
(`revise`/`request_more_evidence`/`request_model_run`/`return_to_diagnosis`/
`reject`/`hold`/`stop`). An Agent may only ever *recommend* one of these
(`MetaReviewDecision.recommended_action`); writing a `HumanEvaluationDecision`
row always requires an explicit, identified human actor distinct from the
proposer of any candidate it selects (doc05 §2.7, reusing `harness.designs.
service.SelfApprovalError` - the same "proposer cannot self-approve" rule
Problem 04's own `governance_service.record_human_decision` already
enforces at build-approval time; this is the earlier, science-level gate).
"""
from __future__ import annotations

from sqlalchemy.orm import Session

from harness.designs.service import SelfApprovalError
from harness.engineering_design.models import CandidateDesign
from harness.ids import new_id, now
from harness.memory import event_types as et
from harness.memory.event_store import append_event
from harness.scientific_evaluation import deterministic
from harness.scientific_evaluation.loop import EvaluationLoopController
from harness.scientific_evaluation.models import HUMAN_DECISIONS, EvaluationCase, HumanEvaluationDecision

_loop = EvaluationLoopController()

_DECISION_TO_CASE_STATUS = {
    "approve_for_planning": "approved_for_planning",
    "approve_for_build": "approved_for_build",
    "revise": "revision_required",
    "request_more_evidence": "revision_required",
    "request_model_run": "revision_required",
    "return_to_diagnosis": "returned_to_diagnosis",
    "reject": "rejected",
    "hold": "held",
    "stop": "stopped",
}


class InvalidHumanDecisionError(ValueError):
    pass


class HumanGatePreconditionError(RuntimeError):
    """A deterministic pre-human-gate check (Human Gate legality /
    critical-finding bypass) failed - doc05 §6: "Human Gate 前不得发布
    build-ready package"."""


def record_human_evaluation_decision(
    session: Session, *, case: EvaluationCase, decision: str, approver_id: str, approver_role: str = "",
    selected_candidates: list[str] | None = None, conditions: list[str] | None = None, rationale: str = "",
    acknowledged_risks: list[str] | None = None,
) -> HumanEvaluationDecision:
    if decision not in HUMAN_DECISIONS:
        raise InvalidHumanDecisionError(f"decision={decision!r} is not one of {HUMAN_DECISIONS}")

    selected = selected_candidates or []
    for design_id in selected:
        candidate = session.get(CandidateDesign, design_id)
        if candidate is None:
            raise ValueError(f"no such candidate design: {design_id}")
        if candidate.proposed_by == approver_id:
            raise SelfApprovalError(f"actor {approver_id!r} proposed candidate {design_id} and cannot also approve it")

    if decision in ("approve_for_planning", "approve_for_build"):
        for design_id in selected:
            candidate = session.get(CandidateDesign, design_id)
            checks = deterministic.run_pre_human_gate_checks(session, case=case, candidate=candidate)
            if deterministic.blocks_progression(checks):
                raise HumanGatePreconditionError(
                    f"candidate {design_id} fails a pre-human-gate deterministic check: "
                    f"{[c.message for c in checks if c.status == 'fail']}"
                )
        if not acknowledged_risks and decision == "approve_for_build":
            # Not a hard block (doc05 never requires zero risk, only that risk is
            # acknowledged where it exists) - downstream findings are re-checked by
            # DET-008 above; this only documents the decision honestly.
            pass

    row = HumanEvaluationDecision(
        human_decision_id=new_id("HEVAL"), evaluation_id=case.evaluation_id, decision=decision,
        selected_candidates=selected, conditions=conditions or [], reviewer_or_approver=approver_id,
        role=approver_role, rationale=rationale, acknowledged_risks=acknowledged_risks or [], timestamp=now(),
    )
    session.add(row)
    session.flush()

    _loop.record_human_gate_outcome(session, case, actor_id=approver_id, target_state=_DECISION_TO_CASE_STATUS[decision])

    append_event(
        session, project_id=case.project_id, event_type=et.EVAL_HUMAN_DECISION_RECORDED, entity_type="HumanEvaluationDecision",
        entity_id=row.human_decision_id, payload={
            "human_decision_id": row.human_decision_id, "evaluation_id": case.evaluation_id, "decision": decision,
            "selected_candidates": selected, "conditions": conditions or [], "reviewer_or_approver": approver_id,
            "role": approver_role, "rationale": rationale, "acknowledged_risks": acknowledged_risks or [], "timestamp": row.timestamp,
        }, actor_type="human", actor_id=approver_id,
    )
    return row
