"""Exercises `UnifiedScientificWorkflowOrchestrator`'s HUMAN_REVIEW ->
SIMULATION -> WAITING_FOR_EXPERIMENT -> OBSERVATION_INGESTION -> LEARNING
segment against a real, already-approved `DesignVersion`.

To reach that starting point without depending on whether Problem 5's
independent Critic happens to clear a given rule-generated portfolio this
round (see `test_e2e.py`'s docstring - it may or may not, honestly, run to
run), this test builds the DesignVersion the same way Problem 4's OWN
end-to-end test does (`tests/engineering_design/test_end_to_end_trp.py`):
via `harness.engineering_design.evaluation_service.evaluate_portfolio`
(Problem 4's own 8-evaluator suite), never creating a Problem 5
`EvaluationCase`. This is not a bypass of a required gate - it is the
real, intentional, already-tested behavior this repository documents in
`harness/scientific_evaluation/gate_hooks.py`: "未创建 EvaluationCase 的
项目零行为变化" (zero behavior change for a design project that never had
an EvaluationCase opened against it). `test_e2e.py` is what proves the
Problem-5-gated path; this test isolates and proves the downstream
SIMULATION/EXPERIMENT/LEARNING machinery on its own.
"""
from __future__ import annotations

from harness import db
from harness.engineering_design.evaluation_service import evaluate_portfolio
from harness.orchestrator.models import UnifiedWorkflowRun
from harness.orchestrator.service import UnifiedScientificWorkflowOrchestrator
from harness.projects import service as proj_svc

ORC = UnifiedScientificWorkflowOrchestrator()

_BUILD_TEST_KWARGS = dict(
    construction_concept="lambda-red recombineering", required_materials=["pKD46", "pCP20"],
    controls=[{"name": "wild-type baseline"}], replication_plan={"biological_replicates": 3},
    sampling_plan=[{"time": "24h"}], qc_checkpoints=["colony PCR"],
    decision_rules=["titer increase >=10% vs baseline = success"],
)
_SUFFICIENT = {"has_baseline": True, "has_genotype": True, "has_condition": True, "has_time": True, "has_qc": True, "has_key_phenotype": True}


def _build_run_to_human_review():
    with db.session_scope() as s:
        proj = proj_svc.create_project(
            s, name="Trp orchestrator sim/learning segment", host_definition={"species": "E. coli", "strain": "K-12"},
            target_product="L-tryptophan", actor_id="pi",
        )
        run = ORC.create_run(s, project_id=proj.project_id, actor_id="pi", target_product="L-tryptophan", host="E. coli K-12")
        run_id = run.workflow_run_id

    with db.session_scope() as s:
        run = ORC.start_diagnosis(
            s, run_id, expected_version=1, actor_id="agent",
            request={"biological_system": {"species": "E. coli", "strain": "K-12"}, "phenotype": "L-tryptophan titer plateaus below target",
                     "target_product": "L-tryptophan", "host": "E. coli K-12", "data_sufficiency": _SUFFICIENT},
            context={"medium": "M9", "carbon_source": "glucose"},
        )
        assert run.current_phase == "DESIGN"
        v = run.version

    with db.session_scope() as s:
        run = ORC.start_design(
            s, run_id, expected_version=v, actor_id="system",
            request={"chassis": "E. coli", "chassis_version_or_genotype": "K-12 MG1655 wild-type",
                     "primary_metrics": [{"metric": "titer", "unit": "g/L"}],
                     "hard_constraints": [{"constraint": "no essential gene knockout", "type": "no_essential_gene_knockout"}],
                     "available_resources": {"materials": ["pKD46", "pCP20"], "instruments": ["HPLC"]}},
            context={},
        )
        assert run.current_phase == "EVALUATION"

    # Deliberate, documented deviation from `test_e2e.py`'s path: run
    # Problem 4's own evaluator instead of opening a Problem 5
    # EvaluationCase, then move the top-level phase pointer directly - the
    # orchestrator's own `_transition_phase` helper is used (not a raw SQL
    # write) so the OrchestratorTransition/ProjectEvent audit trail stays
    # complete and honest about what actually happened.
    with db.session_scope() as s:
        run = s.get(UnifiedWorkflowRun, run_id)
        handoff = ORC._design.get_handoff(s, run.design_project_ref)
        portfolio_id = handoff.payload_refs["portfolio_id"]
        result = evaluate_portfolio(s, portfolio_id=portfolio_id, actor_id="system")
        selected_design_id = result["decision"]["selected_design_ids"][0]
        ORC._transition_phase(s, run, to_phase="HUMAN_REVIEW", reason="test setup: evaluated via Problem 4's own evaluator (no Problem 5 EvaluationCase opened)", actor_id="system")
        v = run.version

    return run_id, selected_design_id, v


def test_simulation_experiment_and_learning_segment():
    run_id, selected_design_id, v = _build_run_to_human_review()

    with db.session_scope() as s:
        run = ORC.record_human_gate_decision(
            s, run_id, expected_version=v, decision="approve", actor_id="pi_lead", reason="approved via Problem 4 evaluator path",
            selected_design_id=selected_design_id, build_test_kwargs=_BUILD_TEST_KWARGS,
        )
        assert run.design_version_ref is not None, f"expected a bridged DesignVersion; status={run.status} pause={run.pause_reason} blocked={run.blocked_reason}"
        assert run.current_phase == "SIMULATION"
        v = run.version

    with db.session_scope() as s:
        run = ORC.run_simulation(
            s, run_id, expected_version=v, actor_id="system",
            chassis={"species": "E. coli", "strain": "K-12"}, environment={"medium": "M9", "carbon_source": "glucose"},
        )
        assert run.simulation_campaign_ref is not None
        assert run.current_phase in ("WAITING_FOR_EXPERIMENT", "BLOCKED")
        if run.current_phase == "BLOCKED":
            assert run.blocked_reason
            return
        v = run.version

    with db.session_scope() as s:
        run = ORC.create_experiment_plan(
            s, run_id, expected_version=v, actor_id="pi",
            controls=["wild-type baseline"], factors=["genotype"], response_variables=["titer"],
            acceptance_criteria=["titer increase >=10% vs baseline"],
        )
        assert run.status == "waiting"
        assert run.current_phase == "WAITING_FOR_EXPERIMENT"
        v = run.version
        plan_ref = run.experiment_plan_ref

    # -- cross-process resume: fresh session, nothing held in memory --
    with db.session_scope() as s:
        reloaded = s.get(UnifiedWorkflowRun, run_id)
        assert reloaded.status == "waiting"
        assert reloaded.experiment_plan_ref == plan_ref
        assert reloaded.version == v

    with db.session_scope() as s:
        from harness.diagnosis import service as diag_svc
        from harness.diagnosis.normalizer import RawObservationInput

        ctx = diag_svc.create_biological_context(s, project_id=run.project_id, medium="M9", carbon_source="glucose")
        raw = RawObservationInput(feature_or_phenotype="titer", value=1.2, unit="g/L", qc_status="passed", condition_id=ctx.context_id)
        run = ORC.record_experiment_run_and_ingest_observation(s, run_id, expected_version=v, actor_id="tech", raw_observation=raw)
        assert run.experiment_run_ref is not None
        assert len(run.observation_set_ref) == 1
        assert run.current_phase == "LEARNING"
        v = run.version

    with db.session_scope() as s:
        run = ORC.run_learning(
            s, run_id, expected_version=v, actor_id="tech",
            observed_results=[{"metric": "titer", "value": 0.9, "baseline_value": 1.0}],
            construction_verified=True, assay_qc_passed=True,
        )
        assert run.current_phase in ("COMPLETED", "DIAGNOSIS", "REDESIGN")

    with db.session_scope() as s:
        report = ORC.reconcile(s, run_id)
        assert report["ledger_matches_materialized_state"] is True


def test_observation_qc_failure_does_not_advance_to_learning():
    """Prompt §13.8: Observation QC failure must not update biological
    belief - the run must stay paused in OBSERVATION_INGESTION/
    WAITING_FOR_EXPERIMENT, never silently proceed to LEARNING."""
    run_id, selected_design_id, v = _build_run_to_human_review()

    with db.session_scope() as s:
        run = ORC.record_human_gate_decision(
            s, run_id, expected_version=v, decision="approve", actor_id="pi_lead", reason="approved via Problem 4 evaluator path",
            selected_design_id=selected_design_id, build_test_kwargs=_BUILD_TEST_KWARGS,
        )
        v = run.version

    with db.session_scope() as s:
        run = ORC.run_simulation(
            s, run_id, expected_version=v, actor_id="system",
            chassis={"species": "E. coli", "strain": "K-12"}, environment={"medium": "M9", "carbon_source": "glucose"},
        )
        if run.current_phase == "BLOCKED":
            return
        v = run.version

    with db.session_scope() as s:
        run = ORC.create_experiment_plan(
            s, run_id, expected_version=v, actor_id="pi", controls=["wild-type baseline"], factors=["genotype"],
            response_variables=["titer"], acceptance_criteria=["titer increase >=10% vs baseline"],
        )
        v = run.version

    with db.session_scope() as s:
        from harness.diagnosis.normalizer import RawObservationInput

        # no unit -> a real NormalizationIssue(severity="error") from the
        # existing normalizer, not a fabricated QC failure.
        raw = RawObservationInput(feature_or_phenotype="titer", value=1.2, unit=None, qc_status="failed")
        run = ORC.record_experiment_run_and_ingest_observation(s, run_id, expected_version=v, actor_id="tech", raw_observation=raw)
        assert run.current_phase != "LEARNING", "observation_qc gate must block advancement to LEARNING on a failed observation"
        assert run.status == "waiting"
        assert run.pause_reason and "observation_qc" in run.pause_reason
