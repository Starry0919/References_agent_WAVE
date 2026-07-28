"""Return-to-Diagnosis path (doc05 §7): when a `ScientificReview` surfaces
a `competing_explanation` finding (or a critic otherwise concludes the
design exposes a diagnosis-level problem), this creates a structured
`DiagnosisReturnRequest` AND a real new `harness.diagnosis.models.
DiagnosisSession` via `harness.diagnosis.service.start_diagnosis_session` -
never a free-text note asking a human to go re-open Problem 03 by hand
(doc05 §7's "返回诊断不能覆盖旧 DiagnosisDecision,必须创建新诊断轮次或
版本").
"""
from __future__ import annotations

from sqlalchemy.orm import Session

from harness.diagnosis import service as diagnosis_service
from harness.engineering_design.models import CandidateDesign, DiagnosisHandoffRecord
from harness.ids import new_id, now
from harness.memory import event_types as et
from harness.memory.event_store import append_event
from harness.scientific_evaluation.models import DiagnosisReturnRequest, EvaluationCase


def create_diagnosis_return_request(
    session: Session, *, case: EvaluationCase, candidate: CandidateDesign, actor_id: str,
    triggering_findings: list[str], affected_hypotheses: list[str] | None = None,
    new_counterevidence: list[str] | None = None, alternative_explanations: list[str] | None = None,
    requested_discriminating_information: list[str] | None = None,
) -> DiagnosisReturnRequest:
    handoff = session.get(DiagnosisHandoffRecord, case.diagnosis_reference) if case.diagnosis_reference else None
    source_session_id = handoff.diagnosis_session_id if handoff is not None else None

    request = DiagnosisReturnRequest(
        request_id=new_id("DRETURN"), source_evaluation_id=case.evaluation_id, source_design_id=candidate.design_id,
        source_design_version=candidate.design_version, triggering_findings=triggering_findings,
        affected_hypotheses=affected_hypotheses or (handoff.supported_hypotheses if handoff else []),
        new_counterevidence=new_counterevidence or [], alternative_explanations=alternative_explanations or [],
        requested_discriminating_information=requested_discriminating_information or [], context=dict(case.frozen_context),
        new_diagnosis_session_id=None, status="pending", created_by=actor_id, created_at=now(),
    )
    session.add(request)
    session.flush()

    if source_session_id is not None:
        original = diagnosis_service.get_session(session, source_session_id)
        if original is not None:
            new_session = diagnosis_service.start_diagnosis_session(
                session, project_id=case.project_id, actor_id=actor_id, biological_system=original.biological_system,
                objective_id=original.objective_id,
            )
            request.new_diagnosis_session_id = new_session.diagnosis_session_id
            request.status = "session_created"
            session.flush()

    append_event(
        session, project_id=case.project_id, event_type=et.EVAL_RETURNED_TO_DIAGNOSIS, entity_type="DiagnosisReturnRequest",
        entity_id=request.request_id, payload={
            "request_id": request.request_id, "source_evaluation_id": case.evaluation_id, "source_design_id": candidate.design_id,
            "triggering_findings": triggering_findings, "alternative_explanations": alternative_explanations or [],
            "new_diagnosis_session_id": request.new_diagnosis_session_id, "status": request.status,
        }, actor_type="human" if actor_id != "system" else "agent", actor_id=actor_id,
    )
    return request
