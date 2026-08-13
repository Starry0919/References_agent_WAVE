from __future__ import annotations

from harness import db
from harness.diagnosis.models import DiagnosisSession, EngineeringProblem
from harness.experiments.models import DataAsset, ExperimentPlan, ExperimentRun, Observation
from harness.ids import new_id, now
from harness.orchestrator.service import UnifiedScientificWorkflowOrchestrator
from harness.projects import service as proj_svc


def test_automatic_diagnosis_persists_links_and_derives_engineering_problem():
    orchestrator = UnifiedScientificWorkflowOrchestrator()
    with db.session_scope() as session:
        project = proj_svc.create_project(
            session, name="grounded automation", host_definition={"species": "E. coli", "strain": "K-12"},
            target_product="L-tryptophan", actor_id="pi",
        )
        plan_id, experiment_run_id = new_id("PLAN"), new_id("ERUN")
        session.add(ExperimentPlan(
            experiment_plan_id=plan_id, project_id=project.project_id, design_version_ids=[], hypotheses_tested=[],
            controls=[], factors=[], response_variables=["titer"], acceptance_criteria=[], created_by="pi", created_at=now(),
        ))
        session.flush()
        session.add(ExperimentRun(
            experiment_run_id=experiment_run_id, experiment_plan_id=plan_id, executed_design_version_ids=[],
            execution_status="completed", operator_or_source="test",
        ))
        session.flush()
        observation_ids = []
        for role, value in (("baseline", 12.0), ("subject", 8.0)):
            asset_id, observation_id = new_id("ASSET"), new_id("OBS")
            session.add(DataAsset(
                data_asset_id=asset_id, project_id=project.project_id, experiment_run_id=experiment_run_id,
                file_uri=f"file:///{role}.csv", checksum=asset_id, assay_type="titer", qc_status="passed",
                provenance={"instrument": "HPLC"}, uploaded_by="pi", uploaded_at=now(),
            ))
            session.add(Observation(
                observation_id=observation_id, project_id=project.project_id, data_asset_ids=[asset_id],
                condition_ref={"medium": "M9", "carbon_source": "glucose"}, metric="titer", value=value,
                unit="g/L", qc_status="passed", analysis_pipeline_version="hplc-v1", created_at=now(),
            ))
            observation_ids.append(observation_id)
        run = orchestrator.create_run(
            session, project_id=project.project_id, actor_id="pi", target_product="L-tryptophan", host="E. coli K-12",
        )
        result = orchestrator.start_diagnosis(
            session, run.workflow_run_id, expected_version=run.version, actor_id="agent",
            request={
                "biological_system": {"species": "E. coli", "strain": "K-12"},
                "phenotype": "measured titer remains below baseline", "target_product": "L-tryptophan",
                "host": "E. coli K-12", "observation_ids": [observation_ids[1]],
                "baseline_observation_ids": [observation_ids[0]],
                "data_sufficiency": {
                    "has_baseline": True, "has_genotype": True, "has_condition": True,
                    "has_time": True, "has_qc": True, "has_key_phenotype": True,
                },
            },
            context={"medium": "M9", "carbon_source": "glucose"},
        )

        diagnosis = session.get(DiagnosisSession, result.diagnosis_run_ref)
        problem = session.query(EngineeringProblem).filter_by(diagnosis_session_id=diagnosis.diagnosis_session_id).one()
        assert result.current_phase == "DESIGN"
        assert diagnosis.baseline_observation_ids == [observation_ids[0]]
        assert problem.observation_ids == [observation_ids[1]]
        assert problem.comparison_observation_ids == [observation_ids[0]]
        assert problem.delta == -4.0
