"""Context Builder: never leaks another project's or an inapplicable
condition's data in; budget shortfall trims background_knowledge only.
"""
from __future__ import annotations

from harness import db
from harness.experiments import service as exp_svc
from harness.experiments.ingestion.data_ingestor import SampleBinding
from harness.experiments.ingestion.growth_titer_csv import GrowthTiterCsvIngestor
from harness.experiments.ingestion.service import ingest_csv_asset
from harness.learning import service as learning_svc
from harness.memory.context_builder import DEFAULT_BUDGETS, build_context_bundle
from harness.projects import service as proj_svc

CSV_M9 = b"sample_id,metric,value,unit\ns1,titer,12.5,g/L\n"
CSV_RICH = b"sample_id,metric,value,unit\ns2,titer,3.0,g/L\n"


def test_context_bundle_never_leaks_another_project():
    with db.session_scope() as s:
        p1 = proj_svc.create_project(s, name="trp", host_definition={}, target_product="trp", actor_id="pi")
        p2 = proj_svc.create_project(s, name="lys", host_definition={}, target_product="lys", actor_id="pi")
        id1, id2 = p1.project_id, p2.project_id

        plan1 = exp_svc.create_experiment_plan(s, project_id=id1, design_version_ids=[], created_by="pi")
        run1 = exp_svc.record_experiment_run(s, project_id=id1, experiment_plan_id=plan1.experiment_plan_id,
                                              executed_design_version_ids=[], actor_id="wetlab")
        ingest_csv_asset(s, project_id=id1, experiment_run_id=run1.experiment_run_id, file_uri="mem://a.csv",
                          raw_bytes=CSV_M9, assay_type="titer", ingestor=GrowthTiterCsvIngestor(),
                          sample_manifest={"s1": SampleBinding(sample_id="s1", condition_ref={"medium": "M9"})}, uploaded_by="wetlab")

    with db.session_scope() as s:
        bundle1 = build_context_bundle(s, project_id=id1)
        bundle2 = build_context_bundle(s, project_id=id2)

    assert bundle1.project_summary["project_id"] == id1
    assert len(bundle1.accepted_observations) == 1
    assert bundle2.project_summary["project_id"] == id2
    assert bundle2.accepted_observations == []  # project 1's observation never appears here


def test_context_bundle_filters_by_condition():
    with db.session_scope() as s:
        p = proj_svc.create_project(s, name="trp", host_definition={}, target_product="trp", actor_id="pi")
        project_id = p.project_id
        plan = exp_svc.create_experiment_plan(s, project_id=project_id, design_version_ids=[], created_by="pi")
        run = exp_svc.record_experiment_run(s, project_id=project_id, experiment_plan_id=plan.experiment_plan_id,
                                             executed_design_version_ids=[], actor_id="wetlab")
        run_id = run.experiment_run_id

    with db.session_scope() as s:
        ingest_csv_asset(s, project_id=project_id, experiment_run_id=run_id, file_uri="mem://m9.csv", raw_bytes=CSV_M9,
                          assay_type="titer", ingestor=GrowthTiterCsvIngestor(),
                          sample_manifest={"s1": SampleBinding(sample_id="s1", condition_ref={"medium": "M9"})}, uploaded_by="wetlab")
    with db.session_scope() as s:
        ingest_csv_asset(s, project_id=project_id, experiment_run_id=run_id, file_uri="mem://rich.csv", raw_bytes=CSV_RICH,
                          assay_type="titer", ingestor=GrowthTiterCsvIngestor(),
                          sample_manifest={"s2": SampleBinding(sample_id="s2", condition_ref={"medium": "rich"})}, uploaded_by="wetlab")

    with db.session_scope() as s:
        bundle = build_context_bundle(s, project_id=project_id, condition_filter={"medium": "M9"})
        assert len(bundle.accepted_observations) == 1
        assert bundle.accepted_observations[0]["condition_ref"]["medium"] == "M9"


def test_budget_shortfall_trims_background_not_critical_facts():
    with db.session_scope() as s:
        p = proj_svc.create_project(s, name="trp", host_definition={}, target_product="trp", actor_id="pi")
        project_id = p.project_id
        fam = learning_svc.create_hypothesis_family(s, project_id=project_id, title="many hypotheses")
        for i in range(20):
            learning_svc.propose_hypothesis(
                s, project_id=project_id, hypothesis_family_id=fam.hypothesis_family_id,
                statement=f"hypothesis number {i} " + "x" * 200, actor_id="agent",
            )
            # each is its own family so all 20 remain "active" (latest per family)
            fam = learning_svc.create_hypothesis_family(s, project_id=project_id, title=f"h{i}")

    tiny_budgets = {**DEFAULT_BUDGETS, "background_knowledge": 50}
    with db.session_scope() as s:
        bundle = build_context_bundle(s, project_id=project_id, budgets=tiny_budgets)

    assert any("background_knowledge trimmed" in o for o in bundle.omissions_and_token_budget["omissions"])
    # critical facts (project_summary) must never be empty/trimmed
    assert bundle.project_summary["project_id"] == project_id
