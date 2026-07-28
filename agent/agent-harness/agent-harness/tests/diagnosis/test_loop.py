"""DiagnosisLoopController: illegal jumps rejected, `awaiting_test_result`
survives a simulated process restart, gate-rejected transitions never
commit, and Stopping Gate outcomes route to the correct state (doc03 §5).
"""
from __future__ import annotations

import pytest

from harness import db
from harness.diagnosis import service as diag_svc
from harness.diagnosis.loop import DiagnosisGateRejectedError, DiagnosisLoopController, IllegalDiagnosisTransitionError
from harness.projects import service as proj_svc
from harness.workflow.gates import data_sufficiency_gate, diagnosis_stopping_gate

loop = DiagnosisLoopController()


def _project_and_session():
    with db.session_scope() as s:
        p = proj_svc.create_project(s, name="t", host_definition={}, target_product="trp", actor_id="pi")
        sess = diag_svc.start_diagnosis_session(s, project_id=p.project_id, actor_id="pi")
        return p.project_id, sess.diagnosis_session_id


def test_illegal_jump_is_rejected():
    project_id, sess_id = _project_and_session()
    with db.session_scope() as s:
        sess = loop.get_session(s, sess_id)
        with pytest.raises(IllegalDiagnosisTransitionError):
            loop.mark_hypotheses_ranked(s, sess, actor_id="agent")


def test_insufficient_data_routes_to_data_required_not_a_false_diagnosis():
    project_id, sess_id = _project_and_session()
    gate = data_sufficiency_gate(has_baseline=False, has_genotype=False, has_condition=False, has_time=False, has_qc=False, has_key_phenotype=False)
    with db.session_scope() as s:
        sess = loop.get_session(s, sess_id)
        loop.run_intake(s, sess, actor_id="agent", sufficiency_gate_result=gate)
        assert sess.status == "data_required"
        assert sess.data_sufficiency == "insufficient"
        with pytest.raises(IllegalDiagnosisTransitionError):
            loop.mark_hypotheses_generated(s, sess, actor_id="agent")


def test_awaiting_test_result_survives_simulated_process_restart():
    project_id, sess_id = _project_and_session()
    gate = data_sufficiency_gate(has_baseline=True, has_genotype=True, has_condition=True, has_time=True, has_qc=True, has_key_phenotype=True)
    with db.session_scope() as s:
        sess = loop.get_session(s, sess_id)
        loop.run_intake(s, sess, actor_id="agent", sufficiency_gate_result=gate)
        loop.mark_hypotheses_generated(s, sess, actor_id="agent")
        loop.mark_evidence_assessed(s, sess, actor_id="agent")
        loop.mark_hypotheses_ranked(s, sess, actor_id="agent")
        loop.enter_test_selection_required(s, sess, actor_id="agent")
        loop.select_test(s, sess, actor_id="agent")
        loop.enter_awaiting_test_result(s, sess, actor_id="agent")
        assert sess.status == "awaiting_test_result"

    # simulate the process ending entirely: reload purely from the DB
    with db.session_scope() as s:
        reloaded = loop.get_session(s, sess_id)
        assert reloaded.status == "awaiting_test_result"
        loop.ingest_test_result_and_update_belief(s, reloaded, actor_id="agent")
        assert reloaded.status == "belief_updated"


def test_gate_rejected_stopping_transition_never_commits():
    """A safety_stop/human_escalation routes to human_review_required, not
    a silent auto-continue or auto-handoff."""
    project_id, sess_id = _project_and_session()
    gate = data_sufficiency_gate(has_baseline=True, has_genotype=True, has_condition=True, has_time=True, has_qc=True, has_key_phenotype=True)
    with db.session_scope() as s:
        sess = loop.get_session(s, sess_id)
        loop.run_intake(s, sess, actor_id="agent", sufficiency_gate_result=gate)
        loop.mark_hypotheses_generated(s, sess, actor_id="agent")
        loop.mark_evidence_assessed(s, sess, actor_id="agent")
        loop.mark_hypotheses_ranked(s, sess, actor_id="agent")
        loop.enter_test_selection_required(s, sess, actor_id="agent")
        loop.select_test(s, sess, actor_id="agent")
        loop.enter_awaiting_test_result(s, sess, actor_id="agent")
        loop.ingest_test_result_and_update_belief(s, sess, actor_id="agent")

        conflict_gate = diagnosis_stopping_gate(
            has_competing_set=True, has_fatal_contradiction=True, has_unresolved_model_conflict=False,
            ranking_stable=True, safety_concern=False, evidence_sufficient=True,
        )
        loop.run_stopping_gate(s, sess, actor_id="agent", stopping_gate_result=conflict_gate)
        assert sess.status == "human_review_required"

        resolved = loop.resolve_human_review(s, sess, actor_id="pi", resolution="hypotheses_ranked")
        assert resolved.status == "hypotheses_ranked"


def test_reopen_diagnosis_bumps_hypothesis_set_version():
    project_id, sess_id = _project_and_session()
    gate = data_sufficiency_gate(has_baseline=True, has_genotype=True, has_condition=True, has_time=True, has_qc=True, has_key_phenotype=True)
    with db.session_scope() as s:
        sess = loop.get_session(s, sess_id)
        loop.run_intake(s, sess, actor_id="agent", sufficiency_gate_result=gate)
        loop.mark_hypotheses_generated(s, sess, actor_id="agent")
        loop.mark_evidence_assessed(s, sess, actor_id="agent")
        loop.mark_hypotheses_ranked(s, sess, actor_id="agent")
        loop.enter_test_selection_required(s, sess, actor_id="agent")
        loop.select_test(s, sess, actor_id="agent")
        loop.enter_awaiting_test_result(s, sess, actor_id="agent")
        loop.ingest_test_result_and_update_belief(s, sess, actor_id="agent")

        evidence_limited_gate = diagnosis_stopping_gate(
            has_competing_set=True, has_fatal_contradiction=False, has_unresolved_model_conflict=False,
            ranking_stable=False, safety_concern=False, evidence_sufficient=True,
        )
        loop.run_stopping_gate(s, sess, actor_id="agent", stopping_gate_result=evidence_limited_gate)
        assert sess.status == "evidence_limited"

        version_before = sess.active_hypothesis_set_version
        loop.reopen_diagnosis(s, sess, actor_id="pi", reason="new observations available")
        assert sess.status == "hypotheses_ranked"
        assert sess.active_hypothesis_set_version == version_before + 1


def test_gate_rejection_error_type():
    """A gate result with status='fail' raises DiagnosisGateRejectedError,
    distinct from an illegal state transition."""
    from harness.workflow.contracts import GateResult, GateStatus, GateViolation

    project_id, sess_id = _project_and_session()
    fail_result = GateResult(gate_name="Test", status=GateStatus.fail, violations=[GateViolation(gate="Test", code="x", message="x")])
    with db.session_scope() as s:
        sess = loop.get_session(s, sess_id)
        loop.run_intake(s, sess, actor_id="agent", sufficiency_gate_result=data_sufficiency_gate(
            has_baseline=True, has_genotype=True, has_condition=True, has_time=True, has_qc=True, has_key_phenotype=True))
        loop.mark_hypotheses_generated(s, sess, actor_id="agent")
        with pytest.raises(DiagnosisGateRejectedError):
            loop._transition(s, sess, from_states=("hypotheses_generated",), to_state="evidence_assessed", actor_id="agent", gate_result=fail_result)
        assert sess.status == "hypotheses_generated"  # rejected transition never committed
