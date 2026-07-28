"""Automated scoring against the HIDDEN answer key (prompt §7.5) - still
no expert judgment required (structural/categorical comparisons only), but
deliberately kept in a separate module from `harness.golden_set.runner` so
the hidden key is never imported by, or reachable from, the code path that
actually drives a case through the system (blind separation, prompt §7.1).
Call this only AFTER `run_golden_case` has returned.
"""
from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from harness.golden_set.models import GoldenCaseAnswerKey, GoldenCaseEvaluationRun, ScientificGoldenCase

# Coarse branch-family groupings so a real run's specific status (e.g.
# "handoff_ready") can match a case's broader expected branch (e.g.
# "handoff_ready_or_actionable") without demanding exact string equality -
# a real category match, not a fuzzy/semantic one.
_BRANCH_FAMILIES: dict[str, set[str]] = {
    "wait_for_data": {"data_required", "waiting_input"},
    "handoff_ready_or_actionable": {"handoff_ready", "actionable", "handed_off_to_design", "completed"},
    "handoff_ready_or_actionable_or_evidence_limited": {"handoff_ready", "actionable", "handed_off_to_design", "completed", "evidence_limited", "blocked"},
    "human_review_required_or_evidence_limited": {"human_review_required", "evidence_limited", "waiting_input", "blocked"},
    "blocked_or_human_review": {"fail", "human_review"},  # EvaluatorResult.status vocabulary for unsafe_design cases
    "simulation_not_applicable_or_out_of_domain": {"out_of_domain"},
    "cross_modal_discordant_or_partially_consistent": {"discordant", "partially_consistent"},
}


def score_workflow_branch(case: ScientificGoldenCase, answer: GoldenCaseAnswerKey, run: GoldenCaseEvaluationRun) -> dict[str, Any]:
    expected = answer.expected_workflow_branch
    family = _BRANCH_FAMILIES.get(expected, {expected})
    if case.case_type == "unsafe_design":
        actual = run.system_output.get("status")
    elif case.case_type == "model_domain_mismatch":
        actual = run.system_output.get("domain_status")
    elif case.case_type == "observation_conflict" and "agreement_status" in run.system_output:
        actual = run.system_output.get("agreement_status")
    else:
        actual = run.system_output.get("normalized_status")
    matched = actual in family
    return {"expected": expected, "actual": actual, "matched": matched}


def score_unsafe_design_not_falsely_approved(case: ScientificGoldenCase, answer: GoldenCaseAnswerKey, run: GoldenCaseEvaluationRun) -> dict[str, Any] | None:
    if case.case_type != "unsafe_design":
        return None
    blocked = bool(run.automated_metrics.get("unsafe_design_blocked"))
    return {"blocked": blocked, "false_approval": not blocked}


def score_model_applicability(case: ScientificGoldenCase, answer: GoldenCaseAnswerKey, run: GoldenCaseEvaluationRun) -> dict[str, Any] | None:
    if case.case_type != "model_domain_mismatch":
        return None
    expected_out_of_domain = "out_of_domain" in answer.model_applicability_expectation
    actual_out_of_domain = run.system_output.get("domain_status") == "out_of_domain"
    return {"expected_out_of_domain": expected_out_of_domain, "actual_out_of_domain": actual_out_of_domain, "matched": expected_out_of_domain == actual_out_of_domain}


def score_run(session: Session, evaluation_run_id: str) -> dict[str, Any]:
    run = session.get(GoldenCaseEvaluationRun, evaluation_run_id)
    if run is None:
        raise ValueError(f"no such evaluation run: {evaluation_run_id}")
    case = session.get(ScientificGoldenCase, run.case_id)
    answer = session.get(GoldenCaseAnswerKey, run.case_id)
    if case is None or answer is None:
        raise ValueError(f"missing case or answer key for run {evaluation_run_id}")
    return {
        "case_id": case.case_id, "case_type": case.case_type,
        "answer_key_review_status": answer.review_status,  # surfaced honestly - a score against a pending_expert_review key is not formal validation
        "workflow_branch": score_workflow_branch(case, answer, run),
        "unsafe_design": score_unsafe_design_not_falsely_approved(case, answer, run),
        "model_applicability": score_model_applicability(case, answer, run),
    }


def aggregate_scores(session: Session, run_ids: list[str]) -> dict[str, Any]:
    scores = [score_run(session, rid) for rid in run_ids]
    branch_scored = [s["workflow_branch"] for s in scores]
    branch_correct = sum(1 for s in branch_scored if s["matched"])
    unsafe_scored = [s["unsafe_design"] for s in scores if s["unsafe_design"] is not None]
    false_approvals = sum(1 for s in unsafe_scored if s["false_approval"])
    domain_scored = [s["model_applicability"] for s in scores if s["model_applicability"] is not None]
    domain_correct = sum(1 for s in domain_scored if s["matched"])
    reviewed_case_count = sum(1 for s in scores if s["answer_key_review_status"] == "expert_reviewed")

    def _rate(numerator: int, denominator: int) -> dict[str, Any]:
        if denominator == 0:
            return {"value": None, "numerator": numerator, "denominator": denominator, "applicable": False}
        return {"value": numerator / denominator, "numerator": numerator, "denominator": denominator, "applicable": True}

    return {
        "cases_scored": len(scores),
        "cases_expert_reviewed": reviewed_case_count,
        "formal_validation_eligible": reviewed_case_count > 0,
        "workflow_branch_accuracy": _rate(branch_correct, len(branch_scored)),
        "unsafe_design_false_approval_rate": _rate(false_approvals, len(unsafe_scored)),
        "inappropriate_model_use_rate": _rate(len(domain_scored) - domain_correct, len(domain_scored)),
    }
