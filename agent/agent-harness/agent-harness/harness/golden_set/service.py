"""Golden Set persistence: seeding candidate cases + the ONLY sanctioned
path to `review_status="expert_reviewed"` (prompt: never set automatically).
"""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from harness.golden_set.cases import CASES
from harness.golden_set.models import REVIEW_STATUSES, GoldenCaseAnswerKey, ScientificGoldenCase
from harness.ids import now


def seed_candidate_cases(session: Session) -> list[ScientificGoldenCase]:
    """Idempotent: inserts any `CASES` entry not already present by
    `case_id`. Every inserted `GoldenCaseAnswerKey` starts
    `review_status="pending_expert_review"` - this function never marks
    anything reviewed."""
    inserted: list[ScientificGoldenCase] = []
    for case_dict, answer_dict in CASES:
        existing = session.get(ScientificGoldenCase, case_dict["case_id"])
        if existing is not None:
            inserted.append(existing)
            continue
        row = ScientificGoldenCase(created_at=now(), **case_dict)
        session.add(row)
        answer_row = GoldenCaseAnswerKey(case_id=case_dict["case_id"], created_at=now(), **answer_dict)
        session.add(answer_row)
        inserted.append(row)
    session.flush()
    return inserted


def list_cases(session: Session) -> list[ScientificGoldenCase]:
    return list(session.execute(select(ScientificGoldenCase)).scalars())


def get_case(session: Session, case_id: str) -> ScientificGoldenCase | None:
    return session.get(ScientificGoldenCase, case_id)


def get_answer_key(session: Session, case_id: str) -> GoldenCaseAnswerKey | None:
    return session.get(GoldenCaseAnswerKey, case_id)


class ExpertReviewError(ValueError):
    pass


def mark_expert_reviewed(
    session: Session, *, case_id: str, reviewer_name: str, reviewer_affiliation: str, review_date: str, notes: str = "",
) -> GoldenCaseAnswerKey:
    """The ONLY function in this codebase allowed to set
    `review_status="expert_reviewed"`. Requires a real, non-empty reviewer
    identity and date - refuses to silently mark a case reviewed."""
    if not reviewer_name.strip():
        raise ExpertReviewError("mark_expert_reviewed requires a real, non-empty reviewer_name - refusing to fabricate expert review")
    if not review_date.strip():
        raise ExpertReviewError("mark_expert_reviewed requires a real review_date - refusing to fabricate expert review")
    answer = session.get(GoldenCaseAnswerKey, case_id)
    if answer is None:
        raise ValueError(f"no such golden case answer key: {case_id}")
    answer.expert_reviewers = [*answer.expert_reviewers, {"name": reviewer_name, "affiliation": reviewer_affiliation, "date": review_date}]
    answer.review_status = "expert_reviewed"
    answer.review_notes = notes
    session.flush()
    return answer


def reject_case(session: Session, *, case_id: str, reviewer_name: str, notes: str) -> GoldenCaseAnswerKey:
    answer = session.get(GoldenCaseAnswerKey, case_id)
    if answer is None:
        raise ValueError(f"no such golden case answer key: {case_id}")
    if not reviewer_name.strip():
        raise ExpertReviewError("reject_case requires a real reviewer_name")
    answer.review_status = "rejected"
    answer.review_notes = notes
    session.flush()
    return answer


def formally_accepted_cases(session: Session) -> list[str]:
    """Case IDs eligible to count toward formal scientific validation
    (prompt: unreviewed candidates must never be counted). Empty until a
    human actually reviews cases via `mark_expert_reviewed`."""
    rows = session.execute(select(GoldenCaseAnswerKey).where(GoldenCaseAnswerKey.review_status == "expert_reviewed")).scalars().all()
    return [r.case_id for r in rows]
