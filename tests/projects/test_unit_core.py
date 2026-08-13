"""Doc 18.1's required unit tests: immutability, genotype diff, upload
idempotency, Data Identity Gate, QC-gated policy updates, hypothesis
versioning, event-replay reconstruction, and Problem-01<->02 adapters.
"""
from __future__ import annotations

import time

import pytest

from harness import db
from harness.constructs import service as construct_svc
from harness.db import ImmutableFieldError
from harness.designs import service as design_svc
from harness.designs.decision_diff import diff_decisions
from harness.designs.genotype_diff import diff_genotype
from harness.designs.models import DesignVersion
from harness.experiments import service as exp_svc
from harness.experiments.ingestion.data_ingestor import SampleBinding
from harness.experiments.ingestion.growth_titer_csv import GrowthTiterCsvIngestor
from harness.experiments.ingestion.service import DataIdentityError, ingest_csv_asset
from harness.learning import service as learning_svc
from harness.learning.service import HypothesisUpdateRejected
from harness.memory.event_store import project_events, replay_project
from harness.memory.views import build_project_status_view, build_project_status_view_from_ledger
from harness.projects import service as proj_svc

TRP_CSV = b"sample_id,metric,value,unit\ns1,titer,12.5,g/L\n"


def _bootstrap_project():
    with db.session_scope() as s:
        p = proj_svc.create_project(s, name="t", host_definition={"species": "E. coli"}, target_product="trp", actor_id="pi")
        return p.project_id


# ---------------------------------------------------------------------------
# Immutability
# ---------------------------------------------------------------------------


def test_design_version_genotype_cannot_be_overwritten():
    project_id = _bootstrap_project()
    with db.session_scope() as s:
        dv = design_svc.propose_design_version(
            s, project_id=project_id, version_label="v0", parent_version_ids=[], branch_name="main",
            genotype_manifest={"baseline_strain": "K-12", "modifications": []}, decisions=[], proposed_by="agent",
        )
        design_version_id = dv.design_version_id

    with pytest.raises(ImmutableFieldError):
        with db.session_scope() as s:
            dv = s.get(DesignVersion, design_version_id)
            dv.genotype_manifest = {"baseline_strain": "K-12", "modifications": [{"gene": "x", "operation": "knockout", "detail": ""}]}

    # status IS allowed to progress
    with db.session_scope() as s:
        dv = s.get(DesignVersion, design_version_id)
        dv.status = "approved"


def test_hypothesis_version_is_fully_immutable():
    project_id = _bootstrap_project()
    with db.session_scope() as s:
        fam = learning_svc.create_hypothesis_family(s, project_id=project_id, title="trp titer")
        hv = learning_svc.propose_hypothesis(s, project_id=project_id, hypothesis_family_id=fam.hypothesis_family_id,
                                              statement="X improves titer", actor_id="agent")
        hv_id = hv.hypothesis_version_id

    with pytest.raises(ImmutableFieldError):
        with db.session_scope() as s:
            from harness.learning.models import HypothesisVersion
            row = s.get(HypothesisVersion, hv_id)
            row.statement = "changed my mind"


def test_observation_value_is_immutable_but_qc_status_can_change():
    project_id = _bootstrap_project()
    manifest = {"s1": SampleBinding(sample_id="s1", condition_ref={"medium": "M9"})}
    with db.session_scope() as s:
        plan = exp_svc.create_experiment_plan(s, project_id=project_id, design_version_ids=[], created_by="pi")
        run = exp_svc.record_experiment_run(s, project_id=project_id, experiment_plan_id=plan.experiment_plan_id,
                                             executed_design_version_ids=[], actor_id="wetlab")
        result = ingest_csv_asset(s, project_id=project_id, experiment_run_id=run.experiment_run_id, file_uri="mem://a.csv",
                                   raw_bytes=TRP_CSV, assay_type="titer", ingestor=GrowthTiterCsvIngestor(),
                                   sample_manifest=manifest, uploaded_by="wetlab")
        obs_id = result.committed_observation_ids[0]

    with pytest.raises(ImmutableFieldError):
        with db.session_scope() as s:
            from harness.experiments.models import Observation
            obs = s.get(Observation, obs_id)
            obs.value = 999.0

    with db.session_scope() as s:  # qc_status IS mutable
        from harness.experiments.models import Observation
        obs = s.get(Observation, obs_id)
        obs.qc_status = "excluded"


# ---------------------------------------------------------------------------
# Genotype / decision diff
# ---------------------------------------------------------------------------


def test_genotype_diff_identifies_add_remove_modify_retain():
    baseline = {"baseline_strain": "K-12", "modifications": [
        {"gene": "trpE", "operation": "mutation", "detail": "S40F"},
        {"gene": "tnaA", "operation": "knockout", "detail": ""},
        {"gene": "aroG", "operation": "overexpression", "detail": "weak promoter"},
    ]}
    candidate = {"baseline_strain": "K-12", "modifications": [
        {"gene": "trpE", "operation": "mutation", "detail": "S40F"},  # retained
        {"gene": "aroG", "operation": "overexpression", "detail": "strong promoter"},  # modified
        {"gene": "ptsG", "operation": "knockout", "detail": ""},  # added
    ]}
    diff = diff_genotype(baseline, candidate)
    assert [m["gene"] for m in diff["added"]] == ["ptsG"]
    assert [m["gene"] for m in diff["removed"]] == ["tnaA"]
    assert [m["gene"] for m in diff["modified"]] == ["aroG"]
    assert [m["gene"] for m in diff["retained"]] == ["trpE"]


def test_decision_diff_reports_changed_fields():
    baseline = [{"target": "trpE", "operation": "mutation", "confidence": "low", "risks": [], "expected_effects": [],
                 "mechanism_hypothesis_ids": [], "approval_state": "proposed"}]
    candidate = [{"target": "trpE", "operation": "mutation", "confidence": "high", "risks": ["burden"], "expected_effects": [],
                  "mechanism_hypothesis_ids": [], "approval_state": "accepted"}]
    diff = diff_decisions(baseline, candidate)
    assert diff["added"] == [] and diff["removed"] == []
    assert len(diff["changed"]) == 1
    assert set(diff["changed"][0]["fields_changed"]) == {"confidence", "risks", "approval_state"}


# ---------------------------------------------------------------------------
# Idempotent ingestion + Data Identity Gate
# ---------------------------------------------------------------------------


def test_identical_upload_is_idempotent_no_duplicate_observation():
    project_id = _bootstrap_project()
    manifest = {"s1": SampleBinding(sample_id="s1", condition_ref={"medium": "M9"})}
    with db.session_scope() as s:
        plan = exp_svc.create_experiment_plan(s, project_id=project_id, design_version_ids=[], created_by="pi")
        run = exp_svc.record_experiment_run(s, project_id=project_id, experiment_plan_id=plan.experiment_plan_id,
                                             executed_design_version_ids=[], actor_id="wetlab")
        run_id = run.experiment_run_id

    with db.session_scope() as s:
        r1 = ingest_csv_asset(s, project_id=project_id, experiment_run_id=run_id, file_uri="mem://a.csv", raw_bytes=TRP_CSV,
                               assay_type="titer", ingestor=GrowthTiterCsvIngestor(), sample_manifest=manifest, uploaded_by="wetlab")
    with db.session_scope() as s:
        r2 = ingest_csv_asset(s, project_id=project_id, experiment_run_id=run_id, file_uri="mem://a.csv", raw_bytes=TRP_CSV,
                               assay_type="titer", ingestor=GrowthTiterCsvIngestor(), sample_manifest=manifest, uploaded_by="wetlab")

    assert not r1.duplicate
    assert r2.duplicate
    with db.session_scope() as s:
        from sqlalchemy import select
        from harness.experiments.models import Observation
        count = len(s.execute(select(Observation).where(Observation.project_id == project_id)).scalars().all())
    assert count == len(r1.committed_observation_ids)  # no extra rows from the second upload


def test_data_identity_gate_rejects_unmapped_sample():
    project_id = _bootstrap_project()
    with db.session_scope() as s:
        plan = exp_svc.create_experiment_plan(s, project_id=project_id, design_version_ids=[], created_by="pi")
        run = exp_svc.record_experiment_run(s, project_id=project_id, experiment_plan_id=plan.experiment_plan_id,
                                             executed_design_version_ids=[], actor_id="wetlab")
        run_id = run.experiment_run_id

    with pytest.raises(DataIdentityError):
        with db.session_scope() as s:
            ingest_csv_asset(s, project_id=project_id, experiment_run_id=run_id, file_uri="mem://b.csv", raw_bytes=TRP_CSV,
                              assay_type="titer", ingestor=GrowthTiterCsvIngestor(), sample_manifest={}, uploaded_by="wetlab")


# ---------------------------------------------------------------------------
# Hypothesis update gate
# ---------------------------------------------------------------------------


def test_hypothesis_update_creates_new_version_and_preserves_old():
    project_id = _bootstrap_project()
    with db.session_scope() as s:
        fam = learning_svc.create_hypothesis_family(s, project_id=project_id, title="trp")
        hv0 = learning_svc.propose_hypothesis(s, project_id=project_id, hypothesis_family_id=fam.hypothesis_family_id,
                                               statement="v0 hypothesis", actor_id="agent")
        hv1 = learning_svc.revise_hypothesis(
            s, parent_hypothesis_version_id=hv0.hypothesis_version_id, statement="v1 hypothesis",
            posterior_status="weakened", confidence="medium", actor_id="agent",
            has_expected_vs_observed=True, has_alternatives_considered=True, has_uncertainty=True,
        )
        assert hv1.parent_hypothesis_version_id == hv0.hypothesis_version_id
        # old version still readable, unchanged
        from harness.learning.models import HypothesisVersion
        reloaded_v0 = s.get(HypothesisVersion, hv0.hypothesis_version_id)
        assert reloaded_v0.statement == "v0 hypothesis"


def test_hypothesis_update_gate_rejects_incomplete_revision():
    project_id = _bootstrap_project()
    with db.session_scope() as s:
        fam = learning_svc.create_hypothesis_family(s, project_id=project_id, title="trp")
        hv0 = learning_svc.propose_hypothesis(s, project_id=project_id, hypothesis_family_id=fam.hypothesis_family_id,
                                               statement="v0", actor_id="agent")
        with pytest.raises(HypothesisUpdateRejected):
            learning_svc.revise_hypothesis(
                s, parent_hypothesis_version_id=hv0.hypothesis_version_id, statement="v1", posterior_status="rejected",
                confidence="low", actor_id="agent",
                has_expected_vs_observed=False, has_alternatives_considered=False, has_uncertainty=False,
            )


# ---------------------------------------------------------------------------
# Event replay
# ---------------------------------------------------------------------------


def test_compensating_style_status_change_is_visible_in_replay():
    project_id = _bootstrap_project()
    with db.session_scope() as s:
        proj_svc.set_project_status(s, project_id=project_id, status="paused", expected_version=1, actor_id="pi")
    with db.session_scope() as s:
        replay = replay_project(s, project_id)
        assert replay["pointers"]["status"] == "paused"
        events = project_events(s, project_id)
        assert any(e.event_type == "PROJECT_STATUS_CHANGED" for e in events)


def test_project_status_view_replay_matches_live_view():
    project_id = _bootstrap_project()
    with db.session_scope() as s:
        dv = design_svc.propose_design_version(s, project_id=project_id, version_label="v0", parent_version_ids=[],
                                                 branch_name="main", genotype_manifest={"baseline_strain": "K-12", "modifications": []},
                                                 decisions=[], proposed_by="agent")
        design_svc.approve_design_version(s, design_version_id=dv.design_version_id, approver_id="pi", expected_project_version=1)

    with db.session_scope() as s:
        live = build_project_status_view(s, project_id)
        replay = build_project_status_view_from_ledger(s, project_id)
        for key in replay:
            assert live[key] == replay[key], f"mismatch on {key}"


def test_project_status_view_reflects_orchestrator_run_not_stale_cycle_state():
    """Regression test: the frontend Workspace drives a project exclusively
    through the Unified Scientific Workflow Orchestrator, never through
    `IterativeCycleState`'s own `/cycle/{action}` endpoints - so for any
    project actually used through the real UI, `cycle.current_state` sits
    frozen at PROJECT_CONTEXT_READY forever. Before this fix,
    build_project_status_view reported that frozen cycle state as
    "lifecycle_stage" regardless of how far the real orchestrator run had
    progressed - a genuine frontend/backend state-inconsistency bug."""
    from harness.orchestrator.service import UnifiedScientificWorkflowOrchestrator

    orc = UnifiedScientificWorkflowOrchestrator()
    project_id = _bootstrap_project()

    with db.session_scope() as s:
        before = build_project_status_view(s, project_id)
        assert before["lifecycle_stage"] == "PROJECT_CONTEXT_READY"

    with db.session_scope() as s:
        run = orc.create_run(s, project_id=project_id, actor_id="pi", target_product="trp", host="E. coli")
        assert run.current_phase == "DIAGNOSIS"

    with db.session_scope() as s:
        after = build_project_status_view(s, project_id)
        assert after["lifecycle_stage"] == "DIAGNOSIS", (
            "status view must reflect the real orchestrator run phase, not the inert Cycle state"
        )
        assert after["next_actions"] == ["run or continue bottleneck diagnosis"]


# ---------------------------------------------------------------------------
# Problem-01 <-> Problem-02 adapter round trip
# ---------------------------------------------------------------------------


def test_adapter_converts_p1_workflow_run_into_persisted_design_version():
    from harness.designs.adapters import workflow_run_to_design_version_args
    from harness.workflow.synbio_stages import build_controller as build_synbio_controller

    synbio = build_synbio_controller()
    p1_run = synbio.create_run("Improve E. coli K-12 L-tryptophan production from glucose.")
    p1_run = synbio.run_to_completion_or_pause(p1_run, max_steps=30)
    assert p1_run.status.value == "completed"

    project_id = _bootstrap_project()
    with db.session_scope() as s:
        args = workflow_run_to_design_version_args(
            p1_run, version_label="strain_v0", parent_version_ids=[], branch_name="main",
            baseline_strain="K-12", proposed_by="agent",
        )
        dv = design_svc.propose_design_version(s, project_id=project_id, **args)
        decisions = design_svc.list_decisions(s, dv.design_version_id)
        # every persisted decision traces back to the Problem-01 run
        assert all(d.source_run_id == p1_run.run_id for d in decisions)
        assert len(decisions) == sum(1 for d in p1_run.engineering_decisions if d.status.value == "accepted")
