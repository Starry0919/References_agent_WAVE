"""Meta-review and Decision Synthesis (doc05 §4.8/§3.9): combines every
`ScientificReview` and the `CandidateEvaluationVector` comparison into ONE
`MetaReviewDecision` - never a majority vote (doc05 §3.9's own instruction:
"不得用多数投票掩盖 critical finding"). Any unresolved, open, blocking
`critical` `CriticFinding` anywhere blocks `approve_for_build`/`approve_for_
planning` regardless of how many other reviewers were satisfied.
"""
from __future__ import annotations

from collections import Counter
from typing import Any

from sqlalchemy.orm import Session

from harness.engineering_design.models import CandidateDesign, DiagnosisHandoffRecord
from harness.ids import new_id, now
from harness.memory import event_types as et
from harness.memory.event_store import append_event
from harness.scientific_evaluation.models import (
    CONFIDENCE_CLASSES,
    CandidateEvaluationVector,
    CriticFinding,
    EvaluationCase,
    MetaReviewDecision,
    RevisionTask,
    ScientificReview,
)


def _worst_confidence(classes: list[str]) -> str:
    if not classes:
        return "not_calibrated"
    return min(classes, key=lambda c: CONFIDENCE_CLASSES.index(c) if c in CONFIDENCE_CLASSES else 0)


def synthesize_meta_review(
    session: Session, *, case: EvaluationCase, candidates: list[CandidateDesign],
    reviews_by_design: dict[str, list[ScientificReview]], findings_by_design: dict[str, list[CriticFinding]],
    vectors_by_design: dict[str, CandidateEvaluationVector], revision_tasks: list[RevisionTask],
) -> MetaReviewDecision:
    all_reviews = [r for lst in reviews_by_design.values() for r in lst]
    blocking_findings = [
        f.finding_id for lst in findings_by_design.values() for f in lst if f.blocking and f.status == "open"
    ]

    agreements: list[str] = []
    disagreements: list[str] = []
    unresolved_conflicts: list[str] = []
    for design_id, findings in findings_by_design.items():
        by_category = Counter(f.category for f in findings)
        reviewer_types_by_category: dict[str, set[str]] = {}
        for f in findings:
            reviewer_type = next((r.reviewer_type for r in reviews_by_design.get(design_id, []) if r.review_id == f.review_id), "unknown")
            reviewer_types_by_category.setdefault(f.category, set()).add(reviewer_type)
        for cat, reviewers in reviewer_types_by_category.items():
            if len(reviewers) > 1:
                agreements.append(f"{design_id}: {len(reviewers)} independent reviewer roles ({sorted(reviewers)}) all raised {cat!r}")

        recs = {r.recommendation for r in reviews_by_design.get(design_id, [])}
        if len(recs) > 1:
            disagreements.append(f"{design_id}: reviewers disagree on recommendation: {sorted(recs)}")
            positive = {"approve_for_planning", "approve_for_build"}
            if recs & positive and recs - positive:
                unresolved_conflicts.append(f"{design_id}: at least one reviewer recommends proceeding ({sorted(recs & positive)}) while another recommends {sorted(recs - positive)} - requires human adjudication")

    recommended_candidates: list[str] = []
    excluded_for_review: dict[str, str] = {}
    for c in candidates:
        vector = vectors_by_design.get(c.design_id)
        reviews = reviews_by_design.get(c.design_id, [])
        findings = findings_by_design.get(c.design_id, [])
        open_blocking = [f for f in findings if f.blocking and f.status == "open"]
        if open_blocking:
            excluded_for_review[c.design_id] = f"{len(open_blocking)} open blocking finding(s)"
            continue
        if vector is not None and vector.excluded_reasons:
            excluded_for_review[c.design_id] = "; ".join(vector.excluded_reasons)
            continue
        if reviews and all(r.recommendation in ("approve_for_planning", "approve_for_build") for r in reviews):
            recommended_candidates.append(c.design_id)

    return_target = None
    competing_explanation_designs = [
        did for did, findings in findings_by_design.items() if any(f.category == "competing_explanation" for f in findings)
    ]

    if any(f.severity == "critical" for lst in findings_by_design.values() for f in lst if f.blocking and f.status == "open"):
        recommended_action = "revise" if not all(c.design_id in excluded_for_review and "hard_constraint_status=violated" in excluded_for_review[c.design_id] for c in candidates) else "reject"
        rationale = "one or more candidates carry an unresolved, blocking, critical finding - cannot proceed regardless of other reviewers' recommendations"
    elif recommended_candidates:
        recommended_action = "approve_for_planning"
        rationale = f"{len(recommended_candidates)} candidate(s) cleared all blocking findings and hard constraints; Human Gate still required before any build/planning progression"
    elif competing_explanation_designs and len(recommended_candidates) == 0:
        recommended_action = "return_to_diagnosis"
        rationale = f"no candidate is clean for planning, and {len(competing_explanation_designs)} candidate(s) surfaced an unresolved competing diagnostic explanation"
        handoff = session.get(DiagnosisHandoffRecord, case.diagnosis_reference) if case.diagnosis_reference else None
        return_target = handoff.diagnosis_session_id if handoff is not None else case.diagnosis_reference
    elif any(rt.task_type == "add_or_replace_evidence" for rt in revision_tasks) and not any(rt.task_type in ("fix_design", "reduce_complexity") for rt in revision_tasks):
        recommended_action = "request_more_evidence"
        rationale = "outstanding revision tasks are evidence-gathering only - no design defect requires a new candidate version yet"
    elif any(rt.task_type == "run_model" for rt in revision_tasks):
        recommended_action = "request_model_run"
        rationale = "outstanding revision tasks require a model/tool computation not yet available"
    else:
        recommended_action = "revise"
        rationale = "no candidate is clear of open findings; revision is required before re-evaluation"

    decision_confidence = _worst_confidence([r.confidence_class for r in all_reviews]) if all_reviews else "not_calibrated"

    decision = MetaReviewDecision(
        decision_id=new_id("MREV"), evaluation_id=case.evaluation_id, review_references=[r.review_id for r in all_reviews],
        candidate_comparison_reference=case.evaluation_id, agreements=agreements, disagreements=disagreements,
        unresolved_conflicts=unresolved_conflicts, blocking_findings=blocking_findings, recommended_action=recommended_action,
        recommended_candidates=recommended_candidates, required_revision_tasks=[t.task_id for t in revision_tasks],
        required_evidence_tasks=[t.task_id for t in revision_tasks if t.task_type in ("add_or_replace_evidence", "run_model")],
        return_target=return_target, decision_rationale=rationale, decision_confidence=decision_confidence,
        human_gate_required=True, created_at=now(),
    )
    session.add(decision)
    session.flush()
    append_event(
        session, project_id=case.project_id, event_type=et.EVAL_META_REVIEW_DECIDED, entity_type="MetaReviewDecision",
        entity_id=decision.decision_id, payload={
            "decision_id": decision.decision_id, "recommended_action": recommended_action,
            "recommended_candidates": recommended_candidates, "blocking_findings": blocking_findings,
            "disagreements": disagreements, "unresolved_conflicts": unresolved_conflicts,
        }, actor_type="agent", actor_id="system",
    )
    return decision
