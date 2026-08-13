"""DiagnosisDecision persistence, the Problem-3 -> Problem-1(as-current-
Problem-4) handoff, and cross-session memory recall (doc03 3.14, 6.2, 6.3).
"""
from __future__ import annotations

import pytest

from harness import db
from harness.diagnosis import decision_service as dec_svc
from harness.diagnosis import service as diag_svc
from harness.diagnosis.handoff import HandoffNotAllowedError, hand_off_to_engineering_design
from harness.diagnosis.memory_recall import recall_prior_diagnoses
from harness.projects import service as proj_svc


def _project_and_session():
    with db.session_scope() as s:
        p = proj_svc.create_project(s, name="t", host_definition={}, target_product="L-tryptophan", actor_id="pi")
        sess = diag_svc.start_diagnosis_session(s, project_id=p.project_id, actor_id="pi")
        return p.project_id, sess.diagnosis_session_id


def test_decision_rejects_invalid_stopping_reason_and_action():
    project_id, sess_id = _project_and_session()
    with db.session_scope() as s:
        with pytest.raises(ValueError):
            dec_svc.create_diagnosis_decision(
                s, diagnosis_session_id=sess_id, diagnosis_version=1, actor_id="pi", context_reference={},
                leading_hypothesis_ids=[], supported_hypothesis_ids=[], alternatives_not_excluded_ids=[], contradictions=[],
                confidence_representation={}, uncertainty="", evidence_references=[], stopping_reason="definitely_solved",
                allowed_next_action="handoff_to_design",
            )


def test_handoff_rejected_without_approval():
    project_id, sess_id = _project_and_session()
    with db.session_scope() as s:
        with pytest.raises(ValueError, match="data_required"):
            dec_svc.create_diagnosis_decision(
                s, diagnosis_session_id=sess_id, diagnosis_version=1, actor_id="pi", context_reference={},
                leading_hypothesis_ids=["H1"], supported_hypothesis_ids=["H1"], alternatives_not_excluded_ids=["H2"],
                contradictions=[], confidence_representation={"qualitative": "moderate"}, uncertainty="not isolated",
                evidence_references=[], stopping_reason="actionable_stop", allowed_next_action="handoff_to_design",
            )


def test_handoff_rejected_when_not_actionable_even_if_approved():
    project_id, sess_id = _project_and_session()
    with db.session_scope() as s:
        decision = dec_svc.create_diagnosis_decision(
            s, diagnosis_session_id=sess_id, diagnosis_version=1, actor_id="pi", context_reference={},
            leading_hypothesis_ids=[], supported_hypothesis_ids=[], alternatives_not_excluded_ids=[], contradictions=[],
            confidence_representation={}, uncertainty="", evidence_references=[], stopping_reason="evidence_limited_stop",
            allowed_next_action="collect_data", handoff_status="approved",
        )
        with pytest.raises(HandoffNotAllowedError):
            hand_off_to_engineering_design(decision, target_product="L-tryptophan", host="E. coli K-12")


def test_ungrounded_actionable_decision_cannot_be_created():
    project_id, sess_id = _project_and_session()
    with db.session_scope() as s:
        with pytest.raises(ValueError, match="data_required"):
            dec_svc.create_diagnosis_decision(
                s, diagnosis_session_id=sess_id, diagnosis_version=1, actor_id="pi", context_reference={},
                leading_hypothesis_ids=["H1"], supported_hypothesis_ids=["H1"], alternatives_not_excluded_ids=["H2"],
                contradictions=[], confidence_representation={"qualitative": "moderate"}, uncertainty="not isolated",
                evidence_references=[], stopping_reason="actionable_stop", allowed_next_action="handoff_to_design",
            )


def test_memory_recall_reads_prior_session_alternatives_and_conflicts():
    project_id, sess_id = _project_and_session()
    with db.session_scope() as s:
        dec_svc.create_diagnosis_decision(
            s, diagnosis_session_id=sess_id, diagnosis_version=1, actor_id="pi", context_reference={},
            leading_hypothesis_ids=["H1"], supported_hypothesis_ids=["H1"], alternatives_not_excluded_ids=["H2", "H3"],
            contradictions=["conflict between GEM and kinetic model"], confidence_representation={}, uncertainty="",
            evidence_references=[], stopping_reason="evidence_limited_stop", allowed_next_action="collect_data",
        )

    # a NEW diagnosis session on the same project
    with db.session_scope() as s:
        new_sess = diag_svc.start_diagnosis_session(s, project_id=project_id, actor_id="pi")
        recall = recall_prior_diagnoses(s, project_id=project_id, exclude_session_id=new_sess.diagnosis_session_id)
        assert sess_id in recall["prior_session_ids"]
        assert "H2" in recall["unresolved_alternatives_not_excluded"]
        assert "H3" in recall["unresolved_alternatives_not_excluded"]
        assert "conflict between GEM and kinetic model" in recall["unresolved_conflicts"]
