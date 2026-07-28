"""Unit tests for the 5 new Problem-03 gates in harness/workflow/gates.py."""
from __future__ import annotations

from harness.workflow import gates


def test_data_sufficiency_gate_all_present_passes():
    r = gates.data_sufficiency_gate(has_baseline=True, has_genotype=True, has_condition=True, has_time=True, has_qc=True, has_key_phenotype=True)
    assert r.status.value == "pass"
    assert r.next_stage == "sufficient"


def test_data_sufficiency_gate_mostly_missing_fails():
    r = gates.data_sufficiency_gate(has_baseline=False, has_genotype=False, has_condition=False, has_time=False, has_qc=True, has_key_phenotype=True)
    assert r.status.value == "fail"
    assert r.next_stage == "insufficient"


def test_data_sufficiency_gate_partial_revises():
    r = gates.data_sufficiency_gate(has_baseline=True, has_genotype=True, has_condition=True, has_time=False, has_qc=False, has_key_phenotype=True)
    assert r.status.value == "revise"
    assert r.next_stage == "partial"


def test_competing_set_gate_requires_two_and_two_classes():
    assert gates.competing_set_gate(1, {"biological_mechanism"}).status.value == "fail"
    assert gates.competing_set_gate(3, {"biological_mechanism"}).status.value == "revise"
    assert gates.competing_set_gate(3, {"biological_mechanism", "measurement_data"}).status.value == "pass"


def test_stopping_gate_safety_concern_always_wins():
    r = gates.diagnosis_stopping_gate(
        has_competing_set=True, has_fatal_contradiction=False, has_unresolved_model_conflict=False,
        ranking_stable=True, safety_concern=True, evidence_sufficient=True,
    )
    assert r.next_stage == "safety_stop"
    assert r.status.value == "human_review"


def test_stopping_gate_unresolved_conflict_escalates():
    r = gates.diagnosis_stopping_gate(
        has_competing_set=True, has_fatal_contradiction=False, has_unresolved_model_conflict=True,
        ranking_stable=True, safety_concern=False, evidence_sufficient=True,
    )
    assert r.next_stage == "human_escalation"


def test_stopping_gate_no_competing_set_continues():
    r = gates.diagnosis_stopping_gate(
        has_competing_set=False, has_fatal_contradiction=False, has_unresolved_model_conflict=False,
        ranking_stable=True, safety_concern=False, evidence_sufficient=True,
    )
    assert r.next_stage == "continue_diagnosis"


def test_stopping_gate_stable_and_sufficient_is_actionable():
    r = gates.diagnosis_stopping_gate(
        has_competing_set=True, has_fatal_contradiction=False, has_unresolved_model_conflict=False,
        ranking_stable=True, safety_concern=False, evidence_sufficient=True,
    )
    assert r.next_stage == "actionable_stop"
    assert r.status.value == "pass"


def test_stopping_gate_unstable_ranking_is_evidence_limited():
    r = gates.diagnosis_stopping_gate(
        has_competing_set=True, has_fatal_contradiction=False, has_unresolved_model_conflict=False,
        ranking_stable=False, safety_concern=False, evidence_sufficient=True,
    )
    assert r.next_stage == "evidence_limited_stop"


def test_engineering_value_gate_requires_diagnosis_stopped_first():
    r = gates.engineering_value_gate(
        diagnostic_stopping_reason="continue_diagnosis", biological_importance="high", engineering_leverage="high", has_objective=True,
    )
    assert r.status.value == "fail"


def test_engineering_value_gate_requires_objective():
    r = gates.engineering_value_gate(
        diagnostic_stopping_reason="actionable_stop", biological_importance="high", engineering_leverage="high", has_objective=False,
    )
    assert r.status.value == "revise"


def test_engineering_value_gate_passes_when_complete():
    r = gates.engineering_value_gate(
        diagnostic_stopping_reason="actionable_stop", biological_importance="high", engineering_leverage="high", has_objective=True,
    )
    assert r.status.value == "pass"


def test_diagnosis_handoff_gate_requires_actionable_and_approval():
    ok = gates.diagnosis_handoff_gate(stopping_reason="actionable_stop", engineering_value_passed=True, human_approval_required=True, human_approved=True)
    assert ok.status.value == "pass"

    not_actionable = gates.diagnosis_handoff_gate(stopping_reason="evidence_limited_stop", engineering_value_passed=True, human_approval_required=False, human_approved=None)
    assert not_actionable.status.value == "fail"

    no_approval = gates.diagnosis_handoff_gate(stopping_reason="actionable_stop", engineering_value_passed=True, human_approval_required=True, human_approved=False)
    assert no_approval.status.value == "fail"
