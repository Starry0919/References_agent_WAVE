from __future__ import annotations

import pytest

from harness import db
from harness.diagnosis import service as diag_svc
from harness.diagnosis import decision_service as dec_svc
from harness.diagnosis.grounding import GroundingError, derive_engineering_problem, evaluate_observation_grounding
from harness.experiments.models import DataAsset, ExperimentPlan, ExperimentRun, Observation
from harness.ids import now
from harness.projects import service as proj_svc


def _setup(*, provenance: bool = True):
    with db.session_scope() as s:
        p = proj_svc.create_project(s, name="grounding", host_definition={"strain": "E. coli K-12"}, target_product="L-tryptophan", actor_id="pi")
        s.add(ExperimentPlan(experiment_plan_id="PLAN-grounding", project_id=p.project_id, design_version_ids=[], hypotheses_tested=[], controls=[], factors=[], response_variables=["tryptophan_titer"], acceptance_criteria=[], created_by="pi", created_at=now()))
        s.add(ExperimentRun(experiment_run_id="RUN-grounding", experiment_plan_id="PLAN-grounding", executed_design_version_ids=[], execution_status="completed", operator_or_source="test"))
        sess = diag_svc.start_diagnosis_session(s, project_id=p.project_id, actor_id="pi", biological_system={"strain": "E. coli K-12"}, baseline_observation_ids=["OBS-base"])
        sess.pending_request_context = {"observation_ids": ["OBS-subject"]}
        for aid in ("ASSET-subject", "ASSET-base"):
            s.add(DataAsset(data_asset_id=aid, project_id=p.project_id, experiment_run_id="RUN-grounding", file_uri=f"file:///{aid}.csv", checksum=aid, assay_type="titer", qc_status="passed", provenance={"instrument": "hplc"} if provenance else {}, uploaded_by="pi", uploaded_at=now()))
        for oid, value, aid in (("OBS-subject", 8.0, "ASSET-subject"), ("OBS-base", 12.0, "ASSET-base")):
            s.add(Observation(observation_id=oid, project_id=p.project_id, data_asset_ids=[aid], condition_ref={"medium": "M9", "carbon_source": "glucose"}, metric="tryptophan_titer", value=value, unit="g/L", qc_status="passed", analysis_pipeline_version="hplc-v1", created_at=now()))
        return p.project_id, sess.diagnosis_session_id


def test_no_observation_returns_data_required():
    with db.session_scope() as s:
        p = proj_svc.create_project(s, name="empty", host_definition={}, target_product="trp", actor_id="pi")
        sess = diag_svc.start_diagnosis_session(s, project_id=p.project_id, actor_id="pi")
        result = evaluate_observation_grounding(s, sess.diagnosis_session_id)
        assert result.status == "data_required"
        assert not result.actionable


def test_valid_measurement_and_baseline_derives_problem_and_passes():
    _, sid = _setup()
    with db.session_scope() as s:
        problem = derive_engineering_problem(s, diagnosis_session_id=sid, observation_id="OBS-subject", comparison_observation_id="OBS-base")
        assert problem.delta == -4.0
        assert "below baseline" in problem.abnormality_statement
        result = evaluate_observation_grounding(s, sid)
        assert result.actionable
        decision = dec_svc.create_diagnosis_decision(
            s, diagnosis_session_id=sid, diagnosis_version=1, actor_id="pi", context_reference={},
            leading_hypothesis_ids=["H1"], supported_hypothesis_ids=["H1"], alternatives_not_excluded_ids=[],
            contradictions=[], confidence_representation={"qualitative": "medium"}, uncertainty="",
            evidence_references=["EV-1"], stopping_reason="actionable_stop", allowed_next_action="handoff_to_design",
        )
        dec_svc.set_handoff_status(s, decision_id=decision.decision_id, handoff_status="approved", actor_id="reviewer")
        assert decision.handoff_status == "approved"


def test_causal_contamination_is_rejected():
    _, sid = _setup()
    with db.session_scope() as s, pytest.raises(GroundingError, match="causal interpretation"):
        derive_engineering_problem(s, diagnosis_session_id=sid, observation_id="OBS-subject", comparison_observation_id="OBS-base", abnormality_statement="Production is low because precursor limitation")


def test_missing_provenance_blocks_grounding():
    _, sid = _setup(provenance=False)
    with db.session_scope() as s:
        derive_engineering_problem(s, diagnosis_session_id=sid, observation_id="OBS-subject", comparison_observation_id="OBS-base")
        result = evaluate_observation_grounding(s, sid)
        assert not result.actionable
        assert any("provenance" in reason for reason in result.blocking_reasons)
