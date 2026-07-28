"""Problem 03 -> Problem 04 handoff adapter (doc04 §5): the ONE real
integration point that reads Problem 03's actual `DiagnosisDecision` object
and turns it into a structured `DiagnosisHandoffRecord` plus a new
`EngineeringDesignProject` - never a free-text summary re-fed to an LLM
(the degenerate path `harness/diagnosis/handoff.py` itself documents as
the only "Engineering Design" that existed before this package: converting
a gated decision into free-text `raw_request` for Problem 01's intake
stage). That old path is left in place (still used by whatever currently
calls it) but is no longer the way a `DiagnosisDecision` reaches a real
Engineering Design workflow - `ingest_diagnosis_decision` below is.
"""
from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from harness.diagnosis.models import DiagnosisDecision, DiagnosisSession
from harness.engineering_design import project_service
from harness.engineering_design.loop import EngineeringDesignLoopController
from harness.engineering_design.models import DiagnosisHandoffRecord, EngineeringDesignProject
from harness.ids import new_id, now
from harness.memory import event_types as et
from harness.memory.event_store import append_event, snapshot
from harness.workflow.gates import engineering_design_handoff_gate

HANDOFF_SNAPSHOT_FIELDS = (
    "handoff_id", "design_project_id", "diagnosis_session_id", "diagnosis_decision_id", "diagnosis_version",
    "handoff_kind", "decision_status", "supported_hypotheses", "unresolved_alternatives", "counterevidence",
    "confidence", "uncertainty", "evidence_references", "engineering_value_assessment",
    "temporal_and_environmental_context", "approved_for_design", "approval_reference", "adapter_provenance",
    "is_stale", "created_at",
)

_loop = EngineeringDesignLoopController()


class HandoffRejectedError(RuntimeError):
    """The EngineeringDesignHandoffGate rejected this decision/probe -
    nothing was persisted (mirrors `harness.learning.service.
    HypothesisUpdateRejected`'s "gate first, persist only on pass" discipline)."""


def _engineering_value_present(decision: DiagnosisDecision) -> bool:
    return bool(decision.engineering_value_assessment)


def ingest_diagnosis_decision(
    session: Session,
    *,
    decision: DiagnosisDecision,
    actor_id: str,
    handoff_kind: str = "diagnosis_decision",
    human_approved: bool | None = None,
    chassis: str | None = None,
    chassis_version_or_genotype: str = "unknown",
    baseline_state_id: str | None = None,
    autonomy_level: str = "recommend_only",
) -> tuple[EngineeringDesignProject, DiagnosisHandoffRecord]:
    """Reads a real, persisted `DiagnosisDecision`, validates it against
    `EngineeringDesignHandoffGate`, and - only on pass - creates a new
    `EngineeringDesignProject` + `DiagnosisHandoffRecord` and advances the
    loop `diagnostic_blocked -> objective_draft`. Every field the adapter
    could not resolve from the decision is recorded in
    `adapter_provenance.missing_fields`, never silently filled in."""
    sess = session.get(DiagnosisSession, decision.diagnosis_session_id)
    if sess is None:
        raise ValueError(f"no such diagnosis session: {decision.diagnosis_session_id}")

    engineering_value_passed = _engineering_value_present(decision)
    gate = engineering_design_handoff_gate(
        handoff_kind=handoff_kind, stopping_reason=decision.stopping_reason,
        engineering_value_passed=engineering_value_passed, human_approved=human_approved,
    )
    if gate.status.value == "fail":
        raise HandoffRejectedError(
            f"diagnosis decision {decision.decision_id!r} rejected by EngineeringDesignHandoffGate: "
            f"{[v.message for v in gate.violations]}"
        )
    if gate.status.value == "human_review":
        raise HandoffRejectedError(
            f"diagnosis decision {decision.decision_id!r} requires human approval before handoff "
            f"(EngineeringDesignHandoffGate): {[v.message for v in gate.violations]}"
        )

    missing_fields: list[str] = []
    resolved_chassis = chassis or sess.biological_system.get("species") or sess.biological_system.get("host")
    if not resolved_chassis:
        resolved_chassis = "unknown"
        missing_fields.append("chassis")

    resolved_context = dict(decision.context_reference or {})
    if not resolved_context:
        missing_fields.append("temporal_and_environmental_context")
    if not engineering_value_passed:
        missing_fields.append("engineering_value_assessment")
    if not decision.evidence_references:
        missing_fields.append("evidence_references")

    proj = project_service.create_design_project(
        session, project_id=sess.project_id, chassis=resolved_chassis,
        chassis_version_or_genotype=chassis_version_or_genotype, diagnosis_session_id=decision.diagnosis_session_id,
        diagnosis_decision_id=decision.decision_id, diagnosis_version=decision.diagnosis_version, actor_id=actor_id,
        baseline_state_id=baseline_state_id, temporal_and_environmental_context=resolved_context,
        autonomy_level=autonomy_level,
    )

    approval_reference: dict[str, Any] | None = decision.human_approval
    if handoff_kind == "diagnostic_probe":
        approval_reference = {"approver": actor_id, "decision": "approved", "purpose": "diagnostic_probe", **(decision.human_approval or {})}

    handoff = DiagnosisHandoffRecord(
        handoff_id=new_id("HANDOFF"), design_project_id=proj.design_project_id,
        diagnosis_session_id=decision.diagnosis_session_id, diagnosis_decision_id=decision.decision_id,
        diagnosis_version=decision.diagnosis_version, handoff_kind=handoff_kind, decision_status=decision.stopping_reason,
        supported_hypotheses=list(decision.supported_hypothesis_ids), unresolved_alternatives=list(decision.alternatives_not_excluded_ids),
        counterevidence=list(decision.contradictions), confidence=dict(decision.confidence_representation or {}),
        uncertainty=[decision.uncertainty] if decision.uncertainty else [], evidence_references=list(decision.evidence_references),
        engineering_value_assessment=decision.engineering_value_assessment, temporal_and_environmental_context=resolved_context,
        approved_for_design=True, approval_reference=approval_reference,
        adapter_provenance={"adapter_version": "p3_to_p4_v1", "missing_fields": missing_fields, "source_decision_id": decision.decision_id},
        is_stale=False, created_at=now(),
    )
    session.add(handoff)
    session.flush()
    append_event(
        session, project_id=sess.project_id, event_type=et.DESIGN_HANDOFF_INGESTED, entity_type="DiagnosisHandoffRecord",
        entity_id=handoff.handoff_id, payload=snapshot(handoff, HANDOFF_SNAPSHOT_FIELDS), actor_type="agent", actor_id=actor_id,
    )

    _loop.ingest_handoff(session, proj, actor_id=actor_id, handoff_gate_result=gate)
    return proj, handoff


def refresh_staleness(session: Session, *, handoff_id: str) -> DiagnosisHandoffRecord:
    """doc04 §5: "当 Diagnosis 后续更新时,使基于旧版本的设计可被识别为
    stale,而不是静默继续." Call before generating a new strategy/portfolio
    round; if a newer `DiagnosisDecision` exists for the same session, marks
    this handoff (and therefore every design downstream of it) stale."""
    handoff = session.get(DiagnosisHandoffRecord, handoff_id)
    if handoff is None:
        raise ValueError(f"no such handoff record: {handoff_id}")

    from sqlalchemy import select

    latest = session.execute(
        select(DiagnosisDecision)
        .where(DiagnosisDecision.diagnosis_session_id == handoff.diagnosis_session_id)
        .order_by(DiagnosisDecision.diagnosis_version.desc())
    ).scalars().first()
    if latest is not None and latest.diagnosis_version > handoff.diagnosis_version and not handoff.is_stale:
        handoff.is_stale = True
        session.flush()
        proj = session.get(EngineeringDesignProject, handoff.design_project_id)
        append_event(
            session, project_id=proj.project_id if proj else "unknown", event_type=et.DESIGN_HANDOFF_STALE,
            entity_type="DiagnosisHandoffRecord", entity_id=handoff.handoff_id,
            payload=snapshot(handoff, HANDOFF_SNAPSHOT_FIELDS), actor_type="agent", actor_id="system",
        )
    return handoff
