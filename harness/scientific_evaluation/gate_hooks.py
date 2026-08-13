"""Workflow guard integration into Problem 04's own gate (doc05 §6:
"deterministic critical failure 不得进入 build approval" / "unresolved
critical blocker 不得进入 approved_for_build" / "Human Gate 前不得发布
build-ready package").

Design choice: this is additive and opt-in, not a retroactive hard
requirement bolted onto every existing Problem 04 project. If no
`EvaluationCase` was ever opened for a design project (i.e. this
project/test never engaged Problem 05), these hooks no-op and Problem 04's
existing `governance_service` behaves exactly as it did before this round -
its own test suite (`tests/engineering_design/test_build_test_and_
governance.py` etc.) keeps passing unmodified. The moment a project DOES
open a scientific `EvaluationCase`, its outcome becomes a real, enforced
precondition for that project's planning-complete and build-approval
steps - see `harness/engineering_design/governance_service.py`'s two call
sites.
"""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from harness.scientific_evaluation.models import EvaluationCase


class ScientificGateNotSatisfiedError(ValueError):
    pass


def _latest_case_for_project(session: Session, design_project_id: str) -> EvaluationCase | None:
    return session.execute(
        select(EvaluationCase).where(EvaluationCase.design_project_id == design_project_id).order_by(EvaluationCase.created_at.desc())
    ).scalars().first()


def check_before_planning_complete(session: Session, *, design_project_id: str) -> None:
    case = _latest_case_for_project(session, design_project_id)
    if case is None:
        return
    if case.status not in ("approved_for_planning", "approved_for_build"):
        raise ScientificGateNotSatisfiedError(
            f"scientific EvaluationCase {case.evaluation_id} is status={case.status!r} - planning cannot be marked "
            "complete before it reaches approved_for_planning/approved_for_build via a HumanEvaluationDecision (doc05 §6/§2.7)"
        )


def check_before_build_approval(session: Session, *, design_project_id: str) -> None:
    case = _latest_case_for_project(session, design_project_id)
    if case is None:
        return
    if case.status != "approved_for_build":
        raise ScientificGateNotSatisfiedError(
            f"scientific EvaluationCase {case.evaluation_id} is status={case.status!r}, not approved_for_build - "
            "Problem 04's build-approval Human Gate cannot be granted until the scientific evaluation's own Human Gate has (doc05 §6)"
        )
