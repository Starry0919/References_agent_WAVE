"""Common evaluator result shape (doc04 §4.4): every one of the 8
evaluators returns exactly this, never a bare boolean or free prose -
`blocking=True` is what `evaluator_revision_gate` in `harness.workflow.
gates` looks at to force a revision cycle.
"""
from __future__ import annotations

from dataclasses import dataclass, field

STATUSES = ("pass", "warning", "fail", "insufficient_evidence", "not_computed")


@dataclass
class EvaluatorResult:
    evaluator: str
    status: str  # one of STATUSES
    findings: list[str] = field(default_factory=list)
    evidence_or_tool_refs: list[str] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)
    required_revisions: list[str] = field(default_factory=list)
    blocking: bool = False

    def to_dict(self) -> dict:
        return {
            "evaluator": self.evaluator, "status": self.status, "findings": self.findings,
            "evidence_or_tool_refs": self.evidence_or_tool_refs, "assumptions": self.assumptions,
            "required_revisions": self.required_revisions, "blocking": self.blocking,
        }
