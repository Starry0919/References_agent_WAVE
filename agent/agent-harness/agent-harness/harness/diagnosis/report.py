"""Report Renderer (doc03 4.16): a VIEW over structured objects, never the
source of truth. Every section carries `trace_ids` pointing back to the
specific hypothesis/evidence/model-run/decision rows behind it, so a
reader can verify each claim against the underlying record instead of
trusting the prose.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from harness.diagnosis.models import (
    DiagnosisDecision,
    DiagnosisSession,
    DiagnosticTest,
    EvidenceLink,
    HypothesisAssessment,
    ModelEvidenceAssessment,
)
from harness.learning.models import HypothesisVersion


@dataclass
class ReportSection:
    title: str
    content: dict[str, Any]
    trace_ids: list[str] = field(default_factory=list)


@dataclass
class DiagnosisReport:
    sections: list[ReportSection] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {"sections": [{"title": s.title, "content": s.content, "trace_ids": s.trace_ids} for s in self.sections]}


def render_report(session: Session, *, diagnosis_session_id: str) -> DiagnosisReport:
    sess = session.get(DiagnosisSession, diagnosis_session_id)
    if sess is None:
        raise ValueError(f"no such diagnosis session: {diagnosis_session_id}")

    report = DiagnosisReport()

    latest_decision = session.execute(
        select(DiagnosisDecision).where(DiagnosisDecision.diagnosis_session_id == diagnosis_session_id)
        .order_by(DiagnosisDecision.diagnosis_version.desc())
    ).scalars().first()

    report.sections.append(ReportSection(
        title="Executive Summary",
        content={
            "status": sess.status, "data_sufficiency": sess.data_sufficiency,
            "stopping_reason": latest_decision.stopping_reason if latest_decision else None,
            "allowed_next_action": latest_decision.allowed_next_action if latest_decision else None,
            "note": "This is not a claim of a unique true bottleneck - see Leading Set / Alternatives Not Excluded below.",
        },
        trace_ids=[latest_decision.decision_id] if latest_decision else [],
    ))

    report.sections.append(ReportSection(
        title="Context & QC",
        content={"biological_system": sess.biological_system, "baseline_observation_ids": sess.baseline_observation_ids},
        trace_ids=list(sess.baseline_observation_ids),
    ))

    assessments = session.execute(
        select(HypothesisAssessment).where(HypothesisAssessment.diagnosis_session_id == diagnosis_session_id)
    ).scalars().all()
    hyp_ids = {a.hypothesis_version_id for a in assessments}
    hyps: dict[str, HypothesisVersion] = {}
    if hyp_ids:
        hyps = {
            h.hypothesis_version_id: h
            for h in session.execute(select(HypothesisVersion).where(HypothesisVersion.hypothesis_version_id.in_(hyp_ids))).scalars()
        }

    leading = [a for a in assessments if a.status in ("strongly_supported", "weakly_supported")]
    not_excluded = [a for a in assessments if a.status != "provisionally_ruled_out"]

    report.sections.append(ReportSection(
        title="Leading Hypothesis Set",
        content={"hypotheses": [
            {
                "hypothesis_version_id": a.hypothesis_version_id,
                "statement": hyps[a.hypothesis_version_id].statement if a.hypothesis_version_id in hyps else None,
                "mechanism_class": hyps[a.hypothesis_version_id].mechanism_class if a.hypothesis_version_id in hyps else None,
                "status": a.status,
            }
            for a in leading
        ]},
        trace_ids=[a.assessment_id for a in leading],
    ))

    report.sections.append(ReportSection(
        title="Alternatives Not Excluded",
        content={"hypotheses": [{"hypothesis_version_id": a.hypothesis_version_id, "status": a.status} for a in not_excluded]},
        trace_ids=[a.assessment_id for a in not_excluded],
    ))

    links = (
        session.execute(select(EvidenceLink).where(EvidenceLink.hypothesis_version_id.in_(hyp_ids))).scalars().all()
        if hyp_ids else []
    )
    report.sections.append(ReportSection(
        title="Support & Contradiction",
        content={
            "supports": [l.evidence_link_id for l in links if l.relation == "supports"],
            "contradicts": [l.evidence_link_id for l in links if l.relation == "contradicts"],
            "is_consistent_with": [l.evidence_link_id for l in links if l.relation == "is_consistent_with"],
            "does_not_discriminate": [l.evidence_link_id for l in links if l.relation == "does_not_discriminate"],
        },
        trace_ids=[l.evidence_link_id for l in links],
    ))

    report.sections.append(ReportSection(
        title="What We Know / Do Not Know",
        content={
            "known": [f"{a.hypothesis_version_id}: {a.status}" for a in assessments if a.status in ("strongly_supported", "provisionally_ruled_out")],
            "unknown": [f"{a.hypothesis_version_id}: {a.status}" for a in assessments if a.status in ("untested", "non_discriminating")],
        },
        trace_ids=[a.assessment_id for a in assessments],
    ))

    tests = session.execute(
        select(DiagnosticTest).where(DiagnosticTest.diagnosis_session_id == diagnosis_session_id, DiagnosticTest.status.in_(("selected", "proposed")))
    ).scalars().all()
    report.sections.append(ReportSection(
        title="Next Diagnostic Test",
        content={"tests": [{"test_id": t.test_id, "assay": t.assay, "discriminates_hypotheses": t.discriminates_hypotheses, "status": t.status} for t in tests]},
        trace_ids=[t.test_id for t in tests],
    ))

    model_assessments = session.execute(
        select(ModelEvidenceAssessment).where(ModelEvidenceAssessment.diagnosis_session_id == diagnosis_session_id)
    ).scalars().all()
    report.sections.append(ReportSection(
        title="Model Conflicts / Sensitivity",
        content={"assessments": [
            {"assessment_id": m.assessment_id, "convergence_status": m.convergence_status, "conflict_explanation": m.conflict_explanation}
            for m in model_assessments
        ]},
        trace_ids=[m.assessment_id for m in model_assessments],
    ))

    report.sections.append(ReportSection(
        title="Current Status & Design Handoff",
        content={
            "diagnosis_status": sess.status,
            "handoff_status": latest_decision.handoff_status if latest_decision else "not_applicable",
            "human_approval": latest_decision.human_approval if latest_decision else None,
        },
        trace_ids=[latest_decision.decision_id] if latest_decision else [],
    ))

    return report
