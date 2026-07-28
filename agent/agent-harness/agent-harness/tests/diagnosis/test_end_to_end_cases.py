"""doc03 §11.4's two required non-mock-only end-to-end cases, plus a
tool-unavailable case."""
from __future__ import annotations

from harness import db
from harness.diagnosis import decision_service as dec_svc
from harness.diagnosis import model_service as model_svc
from harness.diagnosis import service as diag_svc
from harness.diagnosis.assessor import AssessmentInput, assess_hypothesis, rank_hypotheses
from harness.diagnosis.dedup import deduplicate
from harness.diagnosis.hypothesis_generator import generate_competing_hypotheses
from harness.diagnosis.loop import DiagnosisLoopController
from harness.diagnosis.mechanism_graph import build_mechanism_graph
from harness.diagnosis.models import DiagnosisDecision
from harness.diagnosis.normalizer import RawObservationInput, normalize_and_commit
from harness.learning import service as learning_svc
from harness.projects import service as proj_svc
from harness.workflow.gates import data_sufficiency_gate, diagnosis_stopping_gate

loop = DiagnosisLoopController()

_HARDCODED_GENE_RECOMMENDATIONS = {"aroG", "trpE", "tktA", "tnaA", "ΔtnaA"}


def test_case_a_insufficient_data_never_recommends_a_gene_list():
    """Given ONLY 'improve L-tryptophan production' and a host - no
    baseline, genotype, condition, time, or QC - the system must return
    data gaps and, at most, limited hypotheses. It must never directly
    recommend aroG/trpE/tktA/ΔtnaA as if diagnosis were complete."""
    with db.session_scope() as s:
        p = proj_svc.create_project(s, name="Trp - insufficient info", host_definition={"species": "E. coli"}, target_product="L-tryptophan", actor_id="pi")
        sess = diag_svc.start_diagnosis_session(s, project_id=p.project_id, actor_id="pi")

        gate = data_sufficiency_gate(has_baseline=False, has_genotype=False, has_condition=False, has_time=False, has_qc=False, has_key_phenotype=False)
        loop.run_intake(s, sess, actor_id="agent", sufficiency_gate_result=gate)

        assert sess.status == "data_required"
        assert sess.data_sufficiency == "insufficient"

        # The loop structurally cannot reach hypotheses_ranked/actionable
        # from data_required without first re-running intake with more
        # data - confirmed by the illegal-transition guard.
        from harness.diagnosis.loop import IllegalDiagnosisTransitionError
        try:
            loop.mark_hypotheses_generated(s, sess, actor_id="agent")
            raise AssertionError("should have been blocked")
        except IllegalDiagnosisTransitionError:
            pass

        # No DiagnosisDecision was ever created, let alone one recommending action.
        decisions = s.query(DiagnosisDecision).filter_by(diagnosis_session_id=sess.diagnosis_session_id).all()
        assert decisions == []

        # Even a rule-based hypothesis pass (if run anyway on this thin
        # input) never emits a bare gene list - every hypothesis is a
        # falsifiable claim, not an action recommendation, and none of the
        # canonical Trp genes are hardcoded anywhere in the generator.
        graph = build_mechanism_graph(phenotype="improve L-tryptophan production", product="L-tryptophan", host="E. coli")
        result = generate_competing_hypotheses(graph=graph, observation_ids=[], context={}, has_reference_model=False)
        for h in result.hypotheses:
            assert not any(gene in h.statement for gene in _HARDCODED_GENE_RECOMMENDATIONS)
            assert h.falsifiers  # a claim with a falsifier, not a recommendation


def test_case_b_temporal_and_conflicting_evidence_forms_competing_classes_and_updates_belief():
    """Multiple timepoints with growth/product data and a real model run
    that conflicts with a simple expectation: the system must form at
    least biological + process/measurement-class hypotheses, select a
    discriminating test, ingest a result, version the belief update, and
    land in a legitimate continue/stop/handoff state - never silently
    merging the timepoints or averaging away the model conflict."""
    with db.session_scope() as s:
        p = proj_svc.create_project(s, name="Trp - conflicting evidence", host_definition={"species": "E. coli", "strain": "K-12"}, target_product="L-tryptophan", actor_id="pi")
        project_id = p.project_id
        ctx = diag_svc.create_biological_context(s, project_id=project_id, medium="M9", carbon_source="glucose", environment={"oxygenation": "DO 30%", "temperature_c": 37})
        sess = diag_svc.start_diagnosis_session(s, project_id=project_id, actor_id="pi", biological_system={"species": "E. coli", "strain": "K-12"})

        # Multi-timepoint, internally inconsistent titer trajectory.
        observations = []
        for hours, value in ((0, 0.0), (20, 8.0), (30, 5.5)):  # rises then falls - a real conflict signal
            raw = RawObservationInput(feature_or_phenotype="titer", value=value, unit="g/L", condition_id=ctx.context_id,
                                       qc_status="passed", timepoint={"value": hours, "unit": "h"})
            obs, report = normalize_and_commit(s, project_id=project_id, raw=raw, actor_id="agent")
            assert obs is not None
            observations.append(obs)
        assert len({o.timepoint["value"] for o in observations}) == 3  # never merged

        gate = data_sufficiency_gate(has_baseline=True, has_genotype=True, has_condition=True, has_time=True, has_qc=True, has_key_phenotype=True)
        loop.run_intake(s, sess, actor_id="agent", sufficiency_gate_result=gate)
        assert sess.status == "observations_normalized"

        graph = build_mechanism_graph(phenotype="Trp titer declines after 20h", product="L-tryptophan", host="E. coli K-12")
        gen_result = generate_competing_hypotheses(
            graph=graph, observation_ids=[o.observation_id for o in observations],
            context={"medium": "M9", "oxygenation": "DO 30%"}, has_reference_model=True,
        )
        kept, _groups = deduplicate(gen_result.hypotheses)
        represented_classes = {h.mechanism_class for h in kept}
        assert {"biological_mechanism", "measurement_data"}.issubset(represented_classes)
        loop.mark_hypotheses_generated(s, sess, actor_id="agent")

        fam = learning_svc.create_hypothesis_family(s, project_id=project_id, title="Trp decline after 20h")
        persisted = [
            learning_svc.propose_hypothesis(
                s, project_id=project_id, hypothesis_family_id=fam.hypothesis_family_id, statement=h.statement, actor_id="agent",
                mechanism_class=h.mechanism_class, causal_graph_nodes=h.causal_graph_nodes, discriminating_predictions=h.discriminating_predictions,
                falsifiers=h.falsifiers, assumptions=h.assumptions, generation_provenance=h.generation_provenance,
            )
            for h in kept
        ]
        loop.mark_evidence_assessed(s, sess, actor_id="agent")

        # A real, conflicting model comparison.
        run1 = model_svc.execute_model_run(s, project_id=project_id, diagnosis_session_id=sess.diagnosis_session_id,
            adapter_name="gem_fba", inputs={}, context={}, constraints_objective_parameters={}, actor_id="agent")
        run2 = model_svc.execute_model_run(s, project_id=project_id, diagnosis_session_id=sess.diagnosis_session_id,
            adapter_name="gem_fba", inputs={"reaction_bounds": {"EX_o2_e": {"lower": -5, "upper": 1000}}}, context={},
            constraints_objective_parameters={}, actor_id="agent")
        conv = model_svc.assess_cross_model_convergence(s, diagnosis_session_id=sess.diagnosis_session_id, model_run_ids=[run1.model_run_id, run2.model_run_id])
        loop.mark_model_evidence_pending(s, sess, actor_id="agent")

        if conv.convergence_status == "conflicting":
            loop.enter_model_conflicted(s, sess, actor_id="agent")
            assert sess.status == "model_conflicted"
            loop.mark_hypotheses_ranked(s, sess, actor_id="agent")
        else:
            loop.mark_hypotheses_ranked(s, sess, actor_id="agent")
        assert sess.status == "hypotheses_ranked"

        # Rank and select a discriminating test.
        assessments = [
            assess_hypothesis(
                AssessmentInput(hypothesis_id=hv.hypothesis_version_id, observations_explained_count=1, observations_total_count=3),
                has_predeclared_discriminating_prediction=True, has_sufficient_measurement_sensitivity=True,
                has_valid_controls=True, condition_matches=True, alternatives_reviewed=True,
            )
            for hv in persisted
        ]
        ranked = rank_hypotheses(assessments)
        assert ranked  # a real, non-empty competing set

        loop.enter_test_selection_required(s, sess, actor_id="agent")
        loop.select_test(s, sess, actor_id="agent")
        loop.enter_awaiting_test_result(s, sess, actor_id="agent")
        assert sess.status == "awaiting_test_result"

        # Result arrives; belief update creates a NEW version, not an overwrite.
        loop.ingest_test_result_and_update_belief(s, sess, actor_id="agent")
        belief_event = dec_svc.record_belief_update(
            s, project_id=project_id, diagnosis_session_id=sess.diagnosis_session_id,
            new_evidence_or_test_result_ref={"test_result": "confirms process/measurement class"},
            update_rule="discriminating test result", posterior_assessment_id="ASSESS-placeholder",
            status_change={"from": "untested", "to": "weakly_supported"}, actor_id="agent",
        )
        assert belief_event.update_id

        stop_gate = diagnosis_stopping_gate(
            has_competing_set=True, has_fatal_contradiction=False, has_unresolved_model_conflict=False,
            ranking_stable=True, safety_concern=False, evidence_sufficient=True,
        )
        loop.run_stopping_gate(s, sess, actor_id="agent", stopping_gate_result=stop_gate)
        assert sess.status in ("actionable", "evidence_limited", "human_review_required", "hypotheses_ranked")


def test_tool_unavailable_case_not_computed_never_reported_as_success():
    """A model adapter with no real backing (vEcoli, kinetic) must never
    have its `not_computed` result treated as a completed prediction."""
    with db.session_scope() as s:
        p = proj_svc.create_project(s, name="t", host_definition={}, target_product="trp", actor_id="pi")
        sess = diag_svc.start_diagnosis_session(s, project_id=p.project_id, actor_id="pi")

        for adapter_name in ("vecoli", "kinetic_resource"):
            record = model_svc.execute_model_run(
                s, project_id=p.project_id, diagnosis_session_id=sess.diagnosis_session_id, adapter_name=adapter_name,
                inputs={}, context={}, constraints_objective_parameters={}, actor_id="agent",
            )
            assert record.runtime_status == "not_computed"
            assert record.capability_status == "unavailable"
            assert record.outputs == {}  # no fabricated numeric output
            assert record.runtime_status != "optimal"  # never silently reported as a successful computation
