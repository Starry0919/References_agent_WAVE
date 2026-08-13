"""doc04 §13.2: Diagnosis Handoff Gate behavior."""
from __future__ import annotations

from harness import db
from harness.diagnosis import decision_service as dec_svc
from harness.engineering_design import handoff as handoff_mod
from harness.engineering_design.models import DiagnosisHandoffRecord
from tests.engineering_design.fixtures import build_evidence_limited_probe_diagnosis, build_trp_diagnosis


def test_valid_actionable_diagnosis_passes_handoff():
    with db.session_scope() as s:
        _, _, decision = build_trp_diagnosis(s)
        proj, handoff = handoff_mod.ingest_diagnosis_decision(s, decision=decision, actor_id="agent")
        assert proj.status == "objective_draft"
        assert handoff.approved_for_design is True
        assert handoff.handoff_kind == "diagnosis_decision"
        # inherited fields, not a bare summary string
        assert handoff.supported_hypotheses == decision.supported_hypothesis_ids
        assert handoff.unresolved_alternatives == decision.alternatives_not_excluded_ids
        assert handoff.evidence_references == decision.evidence_references


def test_unapproved_evidence_limited_diagnosis_is_blocked_as_plain_handoff():
    with db.session_scope() as s:
        _, _, decision = build_evidence_limited_probe_diagnosis(s)
        try:
            handoff_mod.ingest_diagnosis_decision(s, decision=decision, actor_id="agent", handoff_kind="diagnosis_decision")
            assert False, "should have been rejected"
        except handoff_mod.HandoffRejectedError:
            pass
        # nothing was persisted
        assert s.query(DiagnosisHandoffRecord).count() == 0


def test_unresolved_diagnosis_requires_explicit_human_approval_for_probe():
    with db.session_scope() as s:
        _, _, decision = build_evidence_limited_probe_diagnosis(s)
        try:
            handoff_mod.ingest_diagnosis_decision(s, decision=decision, actor_id="agent", handoff_kind="diagnostic_probe", human_approved=None)
            assert False, "should require explicit human approval"
        except handoff_mod.HandoffRejectedError:
            pass
        try:
            handoff_mod.ingest_diagnosis_decision(s, decision=decision, actor_id="agent", handoff_kind="diagnostic_probe", human_approved=False)
            assert False, "should require explicit human approval"
        except handoff_mod.HandoffRejectedError:
            pass

        proj, handoff = handoff_mod.ingest_diagnosis_decision(s, decision=decision, actor_id="agent", handoff_kind="diagnostic_probe", human_approved=True)
        assert handoff.handoff_kind == "diagnostic_probe"
        assert handoff.approval_reference is not None


def test_safety_stop_never_hands_off_even_with_human_approval():
    from harness.workflow.gates import engineering_design_handoff_gate

    gate = engineering_design_handoff_gate(
        handoff_kind="diagnostic_probe", stopping_reason="safety_stop", engineering_value_passed=True, human_approved=True,
    )
    assert gate.status.value == "fail"


def test_chassis_and_context_are_inherited_not_reprompted():
    with db.session_scope() as s:
        _, sess, decision = build_trp_diagnosis(s)
        proj, handoff = handoff_mod.ingest_diagnosis_decision(s, decision=decision, actor_id="agent", chassis="E. coli")
        assert proj.chassis == "E. coli"
        assert proj.temporal_and_environmental_context.get("medium") == "M9"
        assert proj.temporal_and_environmental_context.get("carbon_source") == "glucose"


def test_diagnosis_version_update_marks_handoff_stale():
    with db.session_scope() as s:
        _, sess, decision = build_trp_diagnosis(s)
        proj, handoff = handoff_mod.ingest_diagnosis_decision(s, decision=decision, actor_id="agent")
        assert handoff.is_stale is False

        dec_svc.create_diagnosis_decision(
            s, diagnosis_session_id=sess.diagnosis_session_id, diagnosis_version=2, actor_id="pi",
            context_reference={"medium": "M9"}, leading_hypothesis_ids=[], supported_hypothesis_ids=[],
            alternatives_not_excluded_ids=[], contradictions=[], confidence_representation={}, uncertainty="revised",
            evidence_references=[], stopping_reason="actionable_stop", allowed_next_action="handoff_to_design",
            engineering_value_assessment={"biological_importance": "high", "engineering_leverage": "high"},
        )
        refreshed = handoff_mod.refresh_staleness(s, handoff_id=handoff.handoff_id)
        assert refreshed.is_stale is True


def test_project_preferences_do_not_change_diagnosis_confidence_or_availability():
    """doc04 §2.2: project preferences may reorder candidates but must
    never change whether a diagnosis is usable/handed-off, nor its
    confidence representation."""
    with db.session_scope() as s:
        _, _, decision = build_trp_diagnosis(s)
        before = dict(decision.confidence_representation)
        proj, handoff = handoff_mod.ingest_diagnosis_decision(s, decision=decision, actor_id="agent")
        # nothing in the handoff path ever writes back to the DiagnosisDecision row
        assert decision.confidence_representation == before
        assert handoff.approved_for_design is True
