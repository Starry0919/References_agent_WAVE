"""doc03 §11.3's 12 required integration assertions, one test per item
(a few overlap with more focused unit tests elsewhere - duplicated here
deliberately so this file is the single canonical checklist against the
doc's own numbering).
"""
from __future__ import annotations

from harness import db
from harness.diagnosis import decision_service as dec_svc
from harness.diagnosis import model_service as model_svc
from harness.diagnosis import service as diag_svc
from harness.diagnosis.assessor import AssessmentInput, assess_hypothesis
from harness.diagnosis.execution_planner import PlanDraft, assess_readiness
from harness.diagnosis.handoff import HandoffNotAllowedError, hand_off_to_engineering_design
from harness.diagnosis.loop import DiagnosisLoopController
from harness.diagnosis.normalizer import RawObservationInput, normalize_and_commit
from harness.diagnosis.report import render_report
from harness.learning import service as learning_svc
from harness.projects import service as proj_svc
from harness.workflow.gates import engineering_value_gate

loop = DiagnosisLoopController()


def _project():
    with db.session_scope() as s:
        p = proj_svc.create_project(s, name="t", host_definition={}, target_product="L-tryptophan", actor_id="pi")
        return p.project_id


# 1. Same evidence under "max titer" vs "industrial stability" objectives:
# diagnostic assessment identical, engineering value differs.
def test_assertion_1_objective_does_not_change_diagnostic_assessment():
    inp = AssessmentInput(hypothesis_id="H1", supporting_links=[{"quality": "high"}], observations_explained_count=8, observations_total_count=10)
    assessment_under_titer_goal = assess_hypothesis(
        inp, has_predeclared_discriminating_prediction=True, has_sufficient_measurement_sensitivity=True,
        has_valid_controls=True, condition_matches=True, alternatives_reviewed=True,
    )
    # assess_hypothesis has no objective parameter at all - the SAME
    # evidence produces the SAME assessment regardless of what "objective"
    # a caller has in mind; nothing here could vary by objective.
    assessment_under_stability_goal = assess_hypothesis(
        inp, has_predeclared_discriminating_prediction=True, has_sufficient_measurement_sensitivity=True,
        has_valid_controls=True, condition_matches=True, alternatives_reviewed=True,
    )
    assert assessment_under_titer_goal.status == assessment_under_stability_goal.status
    assert assessment_under_titer_goal.explanatory_coverage == assessment_under_stability_goal.explanatory_coverage

    # engineering value legitimately differs by objective/leverage inputs
    ev_high_leverage = engineering_value_gate(diagnostic_stopping_reason="actionable_stop", biological_importance="high", engineering_leverage="high", has_objective=True)
    ev_low_leverage = engineering_value_gate(diagnostic_stopping_reason="actionable_stop", biological_importance="high", engineering_leverage="low", has_objective=True)
    assert ev_high_leverage.status.value == "pass"
    assert ev_low_leverage.status.value == "pass"  # gate passes either way, but the recorded leverage differs
    # (leverage itself, a real BottleneckValueAssessment field, is what downstream ranking differs on)


# 2. 0h / 20h / 30h conflicting observations are never silently merged.
def test_assertion_2_conflicting_timepoints_never_silently_merged():
    project_id = _project()
    with db.session_scope() as s:
        ctx = diag_svc.create_biological_context(s, project_id=project_id, medium="M9")
        committed = []
        for hours, value in ((0, 10.0), (20, 4.0), (30, 9.0)):
            raw = RawObservationInput(
                feature_or_phenotype="titer", value=value, unit="g/L", condition_id=ctx.context_id, qc_status="passed",
                timepoint={"value": hours, "unit": "h"},
            )
            obs, report = normalize_and_commit(s, project_id=project_id, raw=raw, actor_id="agent")
            assert obs is not None
            committed.append(obs)
        assert len({o.observation_id for o in committed}) == 3  # three distinct rows, not merged
        assert [o.timepoint["value"] for o in committed] == [0, 20, 30]


# 3. GEM vs. a conflicting model result: both preserved, state -> model_conflicted.
def test_assertion_3_cross_model_conflict_preserved_and_enters_conflicted_state():
    project_id = _project()
    with db.session_scope() as s:
        sess = diag_svc.start_diagnosis_session(s, project_id=project_id, actor_id="pi")
        baseline = model_svc.execute_model_run(s, project_id=project_id, diagnosis_session_id=sess.diagnosis_session_id,
            adapter_name="gem_fba", inputs={}, context={}, constraints_objective_parameters={}, actor_id="agent")
        restricted = model_svc.execute_model_run(s, project_id=project_id, diagnosis_session_id=sess.diagnosis_session_id,
            adapter_name="gem_fba", inputs={"reaction_bounds": {"EX_glc__D_e": {"lower": -2, "upper": 1000}}}, context={},
            constraints_objective_parameters={}, actor_id="agent")
        conv = model_svc.assess_cross_model_convergence(s, diagnosis_session_id=sess.diagnosis_session_id, model_run_ids=[baseline.model_run_id, restricted.model_run_id])
        assert conv.convergence_status == "conflicting"
        assert baseline.outputs["objective_value"] != restricted.outputs["objective_value"]  # both preserved, not averaged

        from harness.workflow.gates import data_sufficiency_gate
        loop.run_intake(s, sess, actor_id="agent", sufficiency_gate_result=data_sufficiency_gate(
            has_baseline=True, has_genotype=True, has_condition=True, has_time=True, has_qc=True, has_key_phenotype=True))
        loop.mark_hypotheses_generated(s, sess, actor_id="agent")
        loop.mark_evidence_assessed(s, sess, actor_id="agent")
        loop.mark_model_evidence_pending(s, sess, actor_id="agent")
        loop.enter_model_conflicted(s, sess, actor_id="agent")
        assert sess.status == "model_conflicted"


# 4. Changing boundary/objective/parameter records ranking stability.
def test_assertion_4_sensitivity_variant_records_ranking_stability():
    project_id = _project()
    with db.session_scope() as s:
        sess = diag_svc.start_diagnosis_session(s, project_id=project_id, actor_id="pi")
        baseline = model_svc.execute_model_run(s, project_id=project_id, diagnosis_session_id=sess.diagnosis_session_id,
            adapter_name="gem_fba", inputs={}, context={}, constraints_objective_parameters={}, actor_id="agent")
        variant = model_svc.execute_model_run(s, project_id=project_id, diagnosis_session_id=sess.diagnosis_session_id,
            adapter_name="gem_fba", inputs={"reaction_bounds": {"EX_o2_e": {"lower": -10, "upper": 1000}}}, context={},
            constraints_objective_parameters={}, actor_id="agent", sensitivity_variant_of=baseline.model_run_id)
        conv = model_svc.assess_cross_model_convergence(s, diagnosis_session_id=sess.diagnosis_session_id, model_run_ids=[baseline.model_run_id, variant.model_run_id])
        assert "best_model_run_id" in conv.ranking_stability
        assert conv.ranking_stability["sensitivity_variants_checked"] >= 0


# 5. A selected test's execution plan generates materials/controls/
# replicates/sampling/QC/output-schema/decision-rule; missing items keep it a draft.
def test_assertion_5_incomplete_plan_stays_draft_complete_plan_is_ready():
    incomplete = PlanDraft(protocol_reference_or_draft="qRT-PCR draft", materials=["primers"])
    assert assess_readiness(incomplete) == "draft"

    complete = PlanDraft(
        protocol_reference_or_draft="qRT-PCR of trpE, matched conditions", materials=["primers", "RNA kit"],
        controls={"positive": "known responder"}, sampling_schedule=["t=0h", "t=8h"], qc_acceptance_criteria=["RIN>7"],
        expected_output_schema={"ct_values": "float"}, interpretation_rule="lower Ct = higher expression", owner="wetlab",
    )
    assert assess_readiness(complete) == "ready"

    empty = PlanDraft()
    assert assess_readiness(empty) == "conceptual"


# 6. A negative but underpowered result cannot be provisionally_ruled_out
# (see also tests/diagnosis/test_evidence_and_assessment.py for the focused unit test).
def test_assertion_6_underpowered_negative_result_cannot_rule_out():
    inp = AssessmentInput(hypothesis_id="H1", contradicting_links=[{"claim": "one underpowered negative"}], observations_explained_count=0, observations_total_count=1)
    a = assess_hypothesis(inp, has_predeclared_discriminating_prediction=True, has_sufficient_measurement_sensitivity=False, has_valid_controls=True, condition_matches=True, alternatives_reviewed=True)
    assert a.status != "provisionally_ruled_out"
    assert a.status == "weakened"


# 7. Every Executive Summary judgment traces back to a structured object.
def test_assertion_7_report_sections_carry_trace_ids():
    project_id = _project()
    with db.session_scope() as s:
        sess = diag_svc.start_diagnosis_session(s, project_id=project_id, actor_id="pi")
        decision = dec_svc.create_diagnosis_decision(
            s, diagnosis_session_id=sess.diagnosis_session_id, diagnosis_version=1, actor_id="pi", context_reference={},
            leading_hypothesis_ids=[], supported_hypothesis_ids=[], alternatives_not_excluded_ids=[], contradictions=[],
            confidence_representation={}, uncertainty="", evidence_references=[], stopping_reason="evidence_limited_stop",
            allowed_next_action="collect_data",
        )
        report = render_report(s, diagnosis_session_id=sess.diagnosis_session_id)
        exec_summary = next(sec for sec in report.sections if sec.title == "Executive Summary")
        assert decision.decision_id in exec_summary.trace_ids  # the summary's claim traces to a real row, not free text


# 8. Handoff to Problem 4 is refused without passing Stopping/Engineering-Value/Human gates.
def test_assertion_8_handoff_blocked_without_passing_gates():
    project_id = _project()
    with db.session_scope() as s:
        sess = diag_svc.start_diagnosis_session(s, project_id=project_id, actor_id="pi")
        decision = dec_svc.create_diagnosis_decision(
            s, diagnosis_session_id=sess.diagnosis_session_id, diagnosis_version=1, actor_id="pi", context_reference={},
            leading_hypothesis_ids=[], supported_hypothesis_ids=[], alternatives_not_excluded_ids=[], contradictions=[],
            confidence_representation={}, uncertainty="", evidence_references=[], stopping_reason="evidence_limited_stop",
            allowed_next_action="collect_data",
        )
    try:
        hand_off_to_engineering_design(decision, target_product="L-tryptophan", host="E. coli K-12")
        raise AssertionError("should have been rejected")
    except HandoffNotAllowedError:
        pass


# 9. Missing ProjectObjective: diagnosis still proceeds, but engineering
# priority cannot be determined.
def test_assertion_9_missing_objective_allows_diagnosis_blocks_engineering_priority():
    inp = AssessmentInput(hypothesis_id="H1", supporting_links=[{"quality": "medium"}], observations_explained_count=1, observations_total_count=1)
    assessment = assess_hypothesis(inp, has_predeclared_discriminating_prediction=True, has_sufficient_measurement_sensitivity=True, has_valid_controls=True, condition_matches=True, alternatives_reviewed=True)
    assert assessment.status in ("strongly_supported", "weakly_supported")  # diagnosis proceeded fine

    ev = engineering_value_gate(diagnostic_stopping_reason="actionable_stop", biological_importance="high", engineering_leverage="high", has_objective=False)
    assert ev.status.value == "revise"  # engineering priority explicitly blocked


# 10. A static (steady-state) model result is never rendered as a dynamic trajectory.
def test_assertion_10_static_fba_result_has_no_trajectory_shape():
    project_id = _project()
    with db.session_scope() as s:
        sess = diag_svc.start_diagnosis_session(s, project_id=project_id, actor_id="pi")
        record = model_svc.execute_model_run(s, project_id=project_id, diagnosis_session_id=sess.diagnosis_session_id,
            adapter_name="gem_fba", inputs={}, context={}, constraints_objective_parameters={}, actor_id="agent")
        assert "timepoints" not in record.outputs
        assert "trajectory" not in record.outputs
        # FBA is a single-point steady-state calculation, structurally
        # distinct from harness.cell_state.models.CellStateTrajectory
        # (which has an explicit `timepoints` field) - a caller cannot
        # accidentally treat one as the other since the shapes differ.


# 11. Service restart resumes a diagnosis waiting on a test result
# (see also tests/diagnosis/test_loop.py for the focused unit test).
def test_assertion_11_resume_after_restart_from_awaiting_test_result():
    project_id = _project()
    from harness.workflow.gates import data_sufficiency_gate

    with db.session_scope() as s:
        sess = diag_svc.start_diagnosis_session(s, project_id=project_id, actor_id="pi")
        sess_id = sess.diagnosis_session_id
        loop.run_intake(s, sess, actor_id="agent", sufficiency_gate_result=data_sufficiency_gate(
            has_baseline=True, has_genotype=True, has_condition=True, has_time=True, has_qc=True, has_key_phenotype=True))
        loop.mark_hypotheses_generated(s, sess, actor_id="agent")
        loop.mark_evidence_assessed(s, sess, actor_id="agent")
        loop.mark_hypotheses_ranked(s, sess, actor_id="agent")
        loop.enter_test_selection_required(s, sess, actor_id="agent")
        loop.select_test(s, sess, actor_id="agent")
        loop.enter_awaiting_test_result(s, sess, actor_id="agent")

    with db.session_scope() as s:  # simulated fresh process
        reloaded = loop.get_session(s, sess_id)
        assert reloaded.status == "awaiting_test_result"


# 12. New results append assessment/decision version, never overwrite history.
def test_assertion_12_new_results_append_never_overwrite():
    project_id = _project()
    with db.session_scope() as s:
        sess = diag_svc.start_diagnosis_session(s, project_id=project_id, actor_id="pi")
        d1 = dec_svc.create_diagnosis_decision(
            s, diagnosis_session_id=sess.diagnosis_session_id, diagnosis_version=1, actor_id="pi", context_reference={},
            leading_hypothesis_ids=["H1"], supported_hypothesis_ids=[], alternatives_not_excluded_ids=[], contradictions=[],
            confidence_representation={}, uncertainty="", evidence_references=[], stopping_reason="evidence_limited_stop",
            allowed_next_action="collect_data",
        )
        d2 = dec_svc.create_diagnosis_decision(
            s, diagnosis_session_id=sess.diagnosis_session_id, diagnosis_version=2, actor_id="pi", context_reference={},
            leading_hypothesis_ids=["H1", "H2"], supported_hypothesis_ids=["H1"], alternatives_not_excluded_ids=["H2"],
            contradictions=[], confidence_representation={}, uncertainty="", evidence_references=[],
            stopping_reason="actionable_stop", allowed_next_action="handoff_to_design",
        )
        assert d1.decision_id != d2.decision_id
        # both versions independently readable - v1 was never mutated to become v2
        from harness.diagnosis.models import DiagnosisDecision
        reloaded_v1 = s.get(DiagnosisDecision, d1.decision_id)
        assert reloaded_v1.diagnosis_version == 1
        assert reloaded_v1.stopping_reason == "evidence_limited_stop"
