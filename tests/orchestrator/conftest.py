"""Shared fixtures for the orchestrator test suite - same isolated-DB
pattern as every other Problem's test suite (`tests/diagnosis/conftest.py`,
`tests/virtual_cell/conftest.py`, etc.)."""
from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import pytest

from harness import db
from harness.bootstrap import bootstrap_schema
from harness.experiments.models import DataAsset, ExperimentPlan, ExperimentRun, Observation
from harness.ids import new_id, now


def grounded_request(session, project_id: str, request: dict, *, modalities: list[tuple[str, str]] | None = None) -> dict:
    """Attach real, QC-passed subject/baseline measurements to a request."""
    pairs = modalities or [("phenotypic", "tryptophan_titer")]
    plan_id, run_id = new_id("PLAN"), new_id("RUN")
    session.add(ExperimentPlan(
        experiment_plan_id=plan_id, project_id=project_id, design_version_ids=[], hypotheses_tested=[],
        controls=[{"name": "matched baseline"}], factors=[], response_variables=[m for _, m in pairs],
        acceptance_criteria=[], created_by="orchestrator-test", created_at=now(),
    ))
    session.add(ExperimentRun(experiment_run_id=run_id, experiment_plan_id=plan_id,
                              executed_design_version_ids=[], execution_status="completed",
                              operator_or_source="orchestrator-test"))
    session.flush()
    subject_ids, baseline_ids = [], []
    condition = {"strain": "E. coli K-12", "medium": "M9", "carbon_source": "glucose", "temperature_c": 37}
    for index, (modality, metric) in enumerate(pairs):
        for role, value in (("subject", 8.0), ("baseline", 12.0)):
            oid, aid = new_id("OBS"), new_id("ASSET")
            session.add(DataAsset(
                data_asset_id=aid, project_id=project_id, experiment_run_id=run_id,
                file_uri=f"fixture://{aid}.csv", checksum=aid, assay_type="titer", qc_status="passed",
                source_type="instrument", provenance={"instrument": "HPLC", "fixture": "orchestrator"},
                uploaded_by="orchestrator-test", uploaded_at=now(),
            ))
            session.add(Observation(
                observation_id=oid, project_id=project_id, data_asset_ids=[aid], condition_ref=condition,
                metric=metric, value=value + index, unit="a.u." if metric != "tryptophan_titer" else "g/L",
                qc_status="passed", source_type="instrument", modality=modality,
                analysis_pipeline_version="fixture-v1", created_at=now(),
            ))
            (subject_ids if role == "subject" else baseline_ids).append(oid)
    session.flush()
    return {**request, "observation_ids": subject_ids, "baseline_observation_ids": baseline_ids}


@pytest.fixture(autouse=True)
def isolated_db(tmp_path):
    db_path = tmp_path / "test_project_ledger.db"
    db.reset_engine_for_tests(f"sqlite:///{db_path}")
    bootstrap_schema()
    yield
