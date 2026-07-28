"""Evidence linking (doc03 2.3), Hypothesis Assessor rule-out logic
(doc03 2.4), and the Diagnosis Evaluator (doc03 4.15)."""
from __future__ import annotations

import pytest

from harness import db
from harness.diagnosis import evidence as evidence_svc
from harness.diagnosis.assessor import AssessmentInput, assess_hypothesis, rank_hypotheses
from harness.diagnosis.evaluator import evaluate_diagnosis
from harness.learning import service as learning_svc
from harness.projects import service as proj_svc


def _project_and_hypothesis():
    with db.session_scope() as s:
        p = proj_svc.create_project(s, name="t", host_definition={}, target_product="trp", actor_id="pi")
        fam = learning_svc.create_hypothesis_family(s, project_id=p.project_id, title="h")
        hv = learning_svc.propose_hypothesis(s, project_id=p.project_id, hypothesis_family_id=fam.hypothesis_family_id, statement="x", actor_id="agent")
        return p.project_id, hv.hypothesis_version_id


def test_evidence_link_relation_must_be_one_of_the_four():
    project_id, hv_id = _project_and_hypothesis()
    with db.session_scope() as s:
        item = evidence_svc.record_evidence_item(s, project_id=project_id, source_type="expert_rule", content_summary="x", actor_id="agent")
        with pytest.raises(evidence_svc.InvalidEvidenceRelation):
            evidence_svc.link_evidence(s, hypothesis_version_id=hv_id, evidence_item_id=item.evidence_item_id, relation="proves", actor_id="agent")
        link = evidence_svc.link_evidence(s, hypothesis_version_id=hv_id, evidence_item_id=item.evidence_item_id, relation="is_consistent_with", actor_id="agent")
        assert link.relation == "is_consistent_with"


def test_consistent_with_is_never_the_same_as_supports_in_assessment():
    """doc03 2.3: 'consistent with' must not be treated as 'proves' - the
    assessor's status computation only counts `supporting_links`, so a
    hypothesis with ONLY is_consistent_with links stays untested/weak, not
    strongly_supported."""
    inp = AssessmentInput(hypothesis_id="H1", is_consistent_links=[{"claim": "consistent"}], observations_explained_count=1, observations_total_count=1)
    a = assess_hypothesis(inp, has_predeclared_discriminating_prediction=False, has_sufficient_measurement_sensitivity=False, has_valid_controls=False, condition_matches=False, alternatives_reviewed=False)
    assert a.status == "untested"


def test_single_negative_result_alone_cannot_rule_out():
    """doc03 2.4: a contradicting result WITHOUT predeclared prediction/
    sensitivity/controls/condition-match/alternatives-review must be
    'weakened', never 'provisionally_ruled_out'."""
    inp = AssessmentInput(hypothesis_id="H1", contradicting_links=[{"claim": "one negative result"}], observations_explained_count=0, observations_total_count=1)
    a = assess_hypothesis(inp, has_predeclared_discriminating_prediction=False, has_sufficient_measurement_sensitivity=True, has_valid_controls=True, condition_matches=True, alternatives_reviewed=True)
    assert a.status == "weakened"


def test_rigorous_contradiction_can_provisionally_rule_out():
    inp = AssessmentInput(hypothesis_id="H1", contradicting_links=[{"claim": "rigorous negative"}], observations_explained_count=0, observations_total_count=1)
    a = assess_hypothesis(inp, has_predeclared_discriminating_prediction=True, has_sufficient_measurement_sensitivity=True, has_valid_controls=True, condition_matches=True, alternatives_reviewed=True)
    assert a.status == "provisionally_ruled_out"


def test_no_status_is_ever_definitively_proven():
    """The assessor's status vocabulary structurally excludes
    'definitively_proven'/'true_bottleneck' - there is no code path that
    can produce them."""
    from harness.diagnosis.assessor import _STATUS_ORDER
    assert "definitively_proven" not in _STATUS_ORDER
    assert "true_bottleneck" not in _STATUS_ORDER


def test_ranking_is_a_transparent_tiebreak_not_a_hidden_score():
    a1 = AssessmentInput(hypothesis_id="H1", supporting_links=[{"quality": "high"}], observations_explained_count=8, observations_total_count=10)
    a2 = AssessmentInput(hypothesis_id="H2", supporting_links=[{"quality": "high"}], observations_explained_count=3, observations_total_count=10)
    assessments = [
        assess_hypothesis(a1, has_predeclared_discriminating_prediction=True, has_sufficient_measurement_sensitivity=True, has_valid_controls=True, condition_matches=True, alternatives_reviewed=True),
        assess_hypothesis(a2, has_predeclared_discriminating_prediction=True, has_sufficient_measurement_sensitivity=True, has_valid_controls=True, condition_matches=True, alternatives_reviewed=True),
    ]
    ranked = rank_hypotheses(assessments)
    assert ranked[0].hypothesis_id == "H1"  # higher coverage ranked first within the same status tier


def test_evaluator_flags_missing_alternative_class():
    report = evaluate_diagnosis(
        represented_classes={"biological_mechanism"}, excluded_classes=set(), assessed_statuses={"weakly_supported"},
        mixed_timepoints_without_scope=False, objective_referenced_in_assessment=False, rule_out_without_sufficient_conditions=False,
    )
    assert report.has_blocking_issues
    assert any(f.code == "missing_alternative_class" for f in report.findings)


def test_evaluator_flags_objective_contamination_and_temporal_mixing():
    report = evaluate_diagnosis(
        represented_classes={"biological_mechanism", "process_environment", "measurement_data", "model_mismatch"}, excluded_classes=set(),
        assessed_statuses={"weakly_supported"}, mixed_timepoints_without_scope=True, objective_referenced_in_assessment=True,
        rule_out_without_sufficient_conditions=True,
    )
    codes = {f.code for f in report.findings}
    assert {"temporal_state_mixing", "objective_contamination", "premature_rule_out"}.issubset(codes)


def test_evaluator_clean_diagnosis_has_no_findings():
    report = evaluate_diagnosis(
        represented_classes={"biological_mechanism", "process_environment", "measurement_data", "model_mismatch"}, excluded_classes=set(),
        assessed_statuses={"weakly_supported"}, mixed_timepoints_without_scope=False, objective_referenced_in_assessment=False,
        rule_out_without_sufficient_conditions=False,
    )
    assert not report.has_blocking_issues
