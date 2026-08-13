"""Cross-session diagnosis memory recall (doc03 6.3): a new
`DiagnosisSession` on the same project can read prior sessions' decisions,
non-discriminating tests, unresolved alternatives, and unresolved
contradictions - never starting cold or reading only a final Markdown
report/`success` flag. All of this comes from the SAME `ProjectEvent`
ledger and diagnosis tables Problems 01/02 already use.
"""
from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from harness.diagnosis.models import DiagnosisDecision, DiagnosisSession, DiagnosticTest


def recall_prior_diagnoses(session: Session, *, project_id: str, exclude_session_id: str | None = None) -> dict[str, Any]:
    sessions = session.execute(
        select(DiagnosisSession).where(DiagnosisSession.project_id == project_id).order_by(DiagnosisSession.created_at.desc())
    ).scalars().all()
    if exclude_session_id:
        sessions = [s for s in sessions if s.diagnosis_session_id != exclude_session_id]
    session_ids = [s.diagnosis_session_id for s in sessions]

    decisions: list[DiagnosisDecision] = []
    non_discriminating_tests: list[DiagnosticTest] = []
    for sid in session_ids:
        decisions.extend(session.execute(select(DiagnosisDecision).where(DiagnosisDecision.diagnosis_session_id == sid)).scalars().all())
        non_discriminating_tests.extend(
            session.execute(
                select(DiagnosticTest).where(DiagnosticTest.diagnosis_session_id == sid, DiagnosticTest.discriminates_hypotheses.is_(False))
            ).scalars().all()
        )

    unresolved_alternatives = sorted({hid for d in decisions for hid in d.alternatives_not_excluded_ids})
    unresolved_conflicts = sorted({c for d in decisions for c in d.contradictions})

    return {
        "prior_session_ids": session_ids,
        "prior_decisions": [
            {"decision_id": d.decision_id, "stopping_reason": d.stopping_reason, "leading_hypothesis_ids": d.leading_hypothesis_ids}
            for d in decisions
        ],
        "non_discriminating_test_ids": [t.test_id for t in non_discriminating_tests],
        "unresolved_alternatives_not_excluded": unresolved_alternatives,
        "unresolved_conflicts": unresolved_conflicts,
    }
