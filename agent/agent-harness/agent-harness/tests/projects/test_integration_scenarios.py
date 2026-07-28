"""The 4 required integration scenarios (doc 18.2-18.5)."""
from __future__ import annotations

import pytest

from harness import db
from harness.constructs import service as construct_svc
from harness.experiments import service as exp_svc
from harness.experiments.ingestion.data_ingestor import SampleBinding
from harness.experiments.ingestion.growth_titer_csv import GrowthTiterCsvIngestor
from harness.experiments.ingestion.service import ingest_csv_asset
from harness.learning import service as learning_svc
from harness.learning.outcome_classifier import classify_outcome, compare_metric
from harness.learning.redesign import RedesignRejected, propose_redesign
from harness.projects import service as proj_svc
from harness.workflow.gates import genotype_verification_gate, policy_update_gate

V0_GENOTYPE = {
    "baseline_strain": "K-12",
    "modifications": [
        {"gene": "trpE", "operation": "mutation", "detail": "S40F"},
        {"gene": "trpC", "operation": "integration", "detail": "AnTrpC replacement"},
        {"gene": "tnaA", "operation": "knockout", "detail": ""},
    ],
}


# ---------------------------------------------------------------------------
# Scenario A: two-round L-tryptophan DBTL
# ---------------------------------------------------------------------------


def test_scenario_a_tryptophan_two_round_dbtl():
    with db.session_scope() as s:
        p = proj_svc.create_project(
            s, name="Trp project", host_definition={"species": "E. coli", "strain": "K-12"}, target_product="L-tryptophan",
            constraints=["growth must not drop more than 20% vs baseline"], actor_id="pi",
        )
        project_id = p.project_id

        # 1. v0 saved.
        v0 = proj_svc.get_project(s, project_id)
        dv0 = __import__("harness.designs.service", fromlist=["service"]).propose_design_version(
            s, project_id=project_id, version_label="strain_v0", parent_version_ids=[], branch_name="main",
            genotype_manifest=V0_GENOTYPE, decisions=[
                {"target": "trpE", "operation": "mutation", "expected_effects": ["increase Trp flux"], "confidence": "medium"},
                {"target": "tnaA", "operation": "knockout", "expected_effects": ["reduce Trp degradation"], "confidence": "medium"},
            ],
            proposed_by="agent",
        )
        from harness.designs.service import approve_design_version
        approve_design_version(s, design_version_id=dv0.design_version_id, approver_id="pi", expected_project_version=v0.version)

        construct = construct_svc.register_construct(s, project_id=project_id, design_version_id=dv0.design_version_id, created_by="wetlab")
        construct_svc.record_genotype_verification(
            s, construct_id=construct.construct_id, project_id=project_id, method="sanger_sequencing",
            result="confirmed", verified_by="wetlab",
        )

        plan = exp_svc.create_experiment_plan(s, project_id=project_id, design_version_ids=[dv0.design_version_id], created_by="pi")
        run = exp_svc.record_experiment_run(
            s, project_id=project_id, experiment_plan_id=plan.experiment_plan_id,
            executed_design_version_ids=[dv0.design_version_id], actor_id="wetlab",
        )
        run_id = run.experiment_run_id
        design_version_id = dv0.design_version_id

    # Import result: Trp +10%, growth -40%, full sample mapping + QC.
    csv_bytes = b"sample_id,metric,value,unit\ns1,titer,11.0,g/L\ns2,growth_rate,0.30,1/h\n"
    manifest = {
        "s1": SampleBinding(sample_id="s1", design_version_id=design_version_id, condition_ref={"medium": "M9", "carbon_source": "glucose"}),
        "s2": SampleBinding(sample_id="s2", design_version_id=design_version_id, condition_ref={"medium": "M9", "carbon_source": "glucose"}),
    }
    with db.session_scope() as s:
        result = ingest_csv_asset(
            s, project_id=project_id, experiment_run_id=run_id, file_uri="mem://trp_v0.csv", raw_bytes=csv_bytes,
            assay_type="titer", ingestor=GrowthTiterCsvIngestor(), sample_manifest=manifest, uploaded_by="wetlab",
        )
    assert not result.duplicate and result.qc_report.passed

    # 2/3. Classify: NOT a bare success - a tradeoff/constraint violation.
    titer_cmp = compare_metric(metric="titer", expected_direction="increase", observed_value=11.0, baseline_value=10.0)
    growth_cmp = compare_metric(metric="growth_rate", expected_direction="maintain", observed_value=0.30, baseline_value=0.50,
                                 constraint_max_percent_drop=20.0)
    assessment = classify_outcome(comparisons=[titer_cmp, growth_cmp], data_qc_passed=True, genotype_verified=True)
    assert assessment.failure_class == "tradeoff"
    assert assessment.is_tradeoff
    assert not assessment.is_unconditional_success

    with db.session_scope() as s:
        # 4. Competing explanations recorded as candidate_causes, not a single cause.
        failure_case = learning_svc.classify_failure(
            s, project_id=project_id, failure_class="tradeoff", design_version_id=design_version_id,
            experiment_run_id=run_id, expected_outcome="increase Trp titer without growth penalty",
            candidate_causes=[
                "metabolic burden from tnaA knockout removing a catabolic escape valve",
                "combinatorial effect between trpE S40F and AnTrpC replacement",
                "AnTrpC expression strength imbalance",
            ],
            causal_confidence="medium", actor_id="agent",
        )
        assert len(failure_case.candidate_causes) >= 2  # NOT collapsed to one cause

        # 5. Hypothesis update - not a bare accept/reject.
        fam = learning_svc.create_hypothesis_family(s, project_id=project_id, title="Trp titer vs growth tradeoff")
        h0 = learning_svc.propose_hypothesis(
            s, project_id=project_id, hypothesis_family_id=fam.hypothesis_family_id,
            statement="tnaA KO + trpE S40F + AnTrpC increases Trp titer without growth cost", actor_id="agent",
            posterior_status="inconclusive",
        )
        h1 = learning_svc.revise_hypothesis(
            s, parent_hypothesis_version_id=h0.hypothesis_version_id,
            statement="tnaA KO relieves catabolic loss but imposes a growth-limiting metabolic burden; "
                       "trpE/AnTrpC contribution to the burden is not yet isolated",
            posterior_status="weakened", confidence="medium", actor_id="agent",
            has_expected_vs_observed=True, has_alternatives_considered=True, has_uncertainty=True,
            alternatives=["burden from AnTrpC alone", "burden from combined edits"],
        )
        assert h1.posterior_status == "weakened"
        assert h1.parent_hypothesis_version_id == h0.hypothesis_version_id

        learning_cycle = learning_svc.start_learning_cycle(
            s, project_id=project_id, input_design_versions=[design_version_id], experiment_run_ids=[run_id], actor_id="agent",
        )

        # 6. v1: explicit retain/remove/add relative to v0, justified by the observation/hypothesis update.
        v1_genotype = {
            "baseline_strain": "K-12",
            "modifications": [
                {"gene": "trpE", "operation": "mutation", "detail": "S40F"},        # retained
                {"gene": "trpC", "operation": "integration", "detail": "AnTrpC replacement"},  # retained
                # tnaA knockout REMOVED - hypothesized burden source
            ],
        }
        dv1, diff = propose_redesign(
            s, project_id=project_id, parent_design_version_id=design_version_id, version_label="strain_v1",
            branch_name="main", new_genotype_manifest=v1_genotype,
            new_decisions=[{"target": "trpE", "operation": "mutation", "expected_effects": ["retain Trp flux gain"], "confidence": "medium"}],
            triggering_justification=f"removing tnaA KO per hypothesis {h1.hypothesis_version_id} (growth-burden weakened result "
                                      f"from observation-backed failure case {failure_case.failure_case_id})",
            created_from_learning_cycle_id=learning_cycle.cycle_id, proposed_by="agent",
        )
        assert diff["removed"] and diff["removed"][0]["gene"] == "tnaA"
        assert {m["gene"] for m in diff["retained"]} == {"trpE", "trpC"}
        assert dv1.parent_version_ids == [design_version_id]  # 8. traceable to v0
        assert dv1.created_from_learning_cycle_id == learning_cycle.cycle_id  # traceable to the learning cycle/observation

        # 7. A second redesign attempt with the IDENTICAL v0 genotype must be rejected, not silently re-proposed.
        with pytest.raises(RedesignRejected):
            propose_redesign(
                s, project_id=project_id, parent_design_version_id=design_version_id, version_label="strain_v1_dup",
                branch_name="main", new_genotype_manifest=V0_GENOTYPE, new_decisions=[],
                triggering_justification="", created_from_learning_cycle_id=learning_cycle.cycle_id, proposed_by="agent",
            )


# ---------------------------------------------------------------------------
# Scenario B: technical failure must not pollute biological memory
# ---------------------------------------------------------------------------


def test_scenario_b_technical_failure_does_not_pollute_biology():
    with db.session_scope() as s:
        p = proj_svc.create_project(s, name="t", host_definition={}, target_product="trp", actor_id="pi")
        project_id = p.project_id
        from harness.designs.service import propose_design_version

        dv = propose_design_version(
            s, project_id=project_id, version_label="v0", parent_version_ids=[], branch_name="main",
            genotype_manifest=V0_GENOTYPE, decisions=[], proposed_by="agent",
        )
        construct = construct_svc.register_construct(s, project_id=project_id, design_version_id=dv.design_version_id, created_by="wetlab")

        # Genotype verification FAILS (e.g. PCR failure / sample mismatch).
        construct_svc.record_genotype_verification(
            s, construct_id=construct.construct_id, project_id=project_id, method="colony_pcr",
            result="failed", detail="PCR band absent - construction likely incomplete", verified_by="wetlab",
        )
        from harness.constructs.models import Construct
        reloaded_construct = s.get(Construct, construct.construct_id)
        assert reloaded_construct.status != "verified"

        # The Genotype Verification Gate must block biological attribution.
        gate_result = genotype_verification_gate(reloaded_construct.status)
        assert gate_result.status.value == "insufficient_evidence"

        # Classified as a construction/technical failure, not a biological one.
        failure_case = learning_svc.classify_failure(
            s, project_id=project_id, failure_class="construction", design_version_id=dv.design_version_id,
            expected_outcome="confirmed genotype", candidate_causes=["PCR failure or sample mismatch"],
            causal_confidence="low", actor_id="agent",
        )
        assert failure_case.failure_class == "construction"

        # A cross-project/global policy update attempted off the back of
        # this technical failure must be rejected outright, regardless of
        # evidence count or approval - never silently allowed through.
        policy_result = policy_update_gate(
            scope="cross_project", failure_class="construction", has_human_approval=True, evidence_count=10,
        )
        assert policy_result.status.value == "fail"
        assert any(v.code == "technical_failure_cannot_drive_policy" for v in policy_result.violations)


# ---------------------------------------------------------------------------
# Scenario C: same design, opposite results under different media - never
# collapsed into one unconditional verdict.
# ---------------------------------------------------------------------------


def test_scenario_c_cross_condition_results_stay_separate():
    from harness.cell_state.snapshots import record_snapshot

    with db.session_scope() as s:
        p = proj_svc.create_project(s, name="t", host_definition={}, target_product="trp", actor_id="pi")
        project_id = p.project_id
        from harness.designs.service import propose_design_version

        dv = propose_design_version(
            s, project_id=project_id, version_label="v0", parent_version_ids=[], branch_name="main",
            genotype_manifest=V0_GENOTYPE, decisions=[], proposed_by="agent",
        )
        design_version_id = dv.design_version_id

        snap_minimal = record_snapshot(
            s, project_id=project_id, design_version_id=design_version_id, host={"species": "E. coli", "strain": "K-12"},
            environment={"medium": "M9_minimal", "carbon_source": "glucose"}, actor_id="agent",
        )
        snap_rich = record_snapshot(
            s, project_id=project_id, design_version_id=design_version_id, host={"species": "E. coli", "strain": "K-12"},
            environment={"medium": "LB_rich", "carbon_source": "complex"}, actor_id="agent",
        )
        # Both snapshots coexist for the SAME design - neither overwrote the other.
        assert snap_minimal.snapshot_id != snap_rich.snapshot_id
        assert snap_minimal.environment["medium"] != snap_rich.environment["medium"]

        failure_minimal = learning_svc.classify_failure(
            s, project_id=project_id, failure_class="tradeoff", design_version_id=design_version_id,
            candidate_causes=["growth-burden under minimal medium"], applicability_scope={"medium": "M9_minimal"}, actor_id="agent",
        )
        failure_rich = learning_svc.classify_failure(
            s, project_id=project_id, failure_class="inconclusive", design_version_id=design_version_id,
            candidate_causes=["no burden observed under rich medium"], applicability_scope={"medium": "LB_rich"}, actor_id="agent",
        )
        assert failure_minimal.applicability_scope != failure_rich.applicability_scope
        assert failure_minimal.failure_class != failure_rich.failure_class  # opposite outcomes, not merged

    with db.session_scope() as s:
        from harness.cell_state.snapshots import list_snapshots_for_design
        snapshots = list_snapshots_for_design(s, design_version_id)
        assert len(snapshots) == 2
        media = {snap.environment["medium"] for snap in snapshots}
        assert media == {"M9_minimal", "LB_rich"}


# ---------------------------------------------------------------------------
# Scenario D: waiting for results survives a real process boundary
# ---------------------------------------------------------------------------


def test_scenario_d_wait_and_resume_across_process_restart(tmp_path):
    from harness.workflow.iterative_loop import IterativeLoopController

    loop = IterativeLoopController()
    db_path = tmp_path / "scenario_d.db"
    db.reset_engine_for_tests(f"sqlite:///{db_path}")
    from harness.bootstrap import bootstrap_schema

    bootstrap_schema()

    with db.session_scope() as s:
        p = proj_svc.create_project(s, name="t", host_definition={}, target_product="trp", actor_id="pi")
        project_id = p.project_id
        cycle = proj_svc.get_active_cycle(s, project_id)
        loop.capture_baseline(s, cycle, actor_id="pi")
        loop.propose_design(s, cycle, design_version_id="DV-x", actor_id="agent")
        loop.enter_human_design_gate(s, cycle, actor_id="agent")
        loop.approve_design_and_handoff(s, cycle, actor_id="pi")
        loop.enter_waiting_for_results(s, cycle, experiment_plan_id="PLAN-x", actor_id="wetlab")
        cycle_id = cycle.cycle_state_id
        assert cycle.current_state == "WAITING_FOR_RESULTS"

    # --- simulate the process ending entirely: repoint the engine at the
    # SAME sqlite file, as a brand-new process would on restart. No Python
    # object from above survives this boundary. ---
    db.reset_engine_for_tests(f"sqlite:///{db_path}")

    with db.session_scope() as s:
        cycle = loop.get_cycle(s, cycle_id)
        assert cycle is not None
        assert cycle.current_state == "WAITING_FOR_RESULTS"  # resumed, not reset to project creation
        loop.begin_data_ingestion(s, cycle, experiment_run_id="RUN-y", actor_id="wetlab")
        assert cycle.current_state == "DATA_INGESTION"  # continues from data ingestion, never re-designs from scratch
