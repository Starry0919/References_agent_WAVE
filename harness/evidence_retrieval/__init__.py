"""Evidence retrieval + condition-matching + grading infrastructure (prompt
Workstream 2, §5.6-5.8). See `contracts.py` for the adapter interface,
`crossref_adapter.py`/`local_ddr_adapter.py` for the two real adapters
available in this environment, `condition_matching.py` for the
deterministic transferability classifier, and `evidence_grading.py` for
the teacher-spec 硬/软 evidence grading system (工作 A §4.2).
"""
from harness.evidence_retrieval.evidence_grading import (
    EvidenceGrade,
    GradingResult,
    classify_evidence,
    grade_decision_step,
    grade_ddr,
    format_grading_report,
)

__all__ = [
    "EvidenceGrade",
    "GradingResult",
    "classify_evidence",
    "grade_decision_step",
    "grade_ddr",
    "format_grading_report",
]
