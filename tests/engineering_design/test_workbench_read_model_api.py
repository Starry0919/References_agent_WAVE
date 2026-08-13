from __future__ import annotations

import time

from fastapi import FastAPI
from fastapi.testclient import TestClient
from harness import db
from harness.engineering_design.models import CandidateDesign, EngineeringDesignProject
from harness.projects.models import Project
from harness.api.engineering_design import router


def _client() -> TestClient:
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


def test_project_evaluations_returns_empty_collection_without_404() -> None:
    project = EngineeringDesignProject(
        design_project_id="EDP-WORKBENCH", project_id="PROJ-WORKBENCH", schema_version="1",
        chassis="E. coli", chassis_version_or_genotype="K-12", diagnosis_session_id="DIAG-WORKBENCH",
        diagnosis_decision_id="DDEC-WORKBENCH", diagnosis_version=1, status="portfolio_generated",
        created_by="test", created_at=time.time(), updated_at=time.time(),
    )
    candidate = CandidateDesign(
        design_id="CAND-WORKBENCH", design_project_id=project.design_project_id, lineage_id="CAND-WORKBENCH",
        design_version=1, parent_design_ids=[], strategy_ids=[], genetic_modifications=[],
        regulatory_architecture={}, process_modifications=[], expected_mechanism="reference",
        causal_chain=[], interaction_and_epistasis_assumptions=[], evidence_links=[],
        counterfactual_requests=[], counterfactual_results=[], uncertainty_and_model_conflicts=[], safety_flags=[],
        source_diagnosis_version=1, proposed_by="test", created_at=time.time(),
    )
    with db.session_scope() as session:
        session.add(Project(project_id="PROJ-WORKBENCH", name="Workbench", host_definition={}, target_product="target", created_at=time.time(), updated_at=time.time()))
        session.flush()
        session.add(project)
        session.flush()
        session.add(candidate)
    response = _client().get("/api/engineering-design/projects/EDP-WORKBENCH/evaluations")
    assert response.status_code == 200
    assert response.json() == {"evaluations": {}}


def test_candidate_read_model_exposes_existing_scientific_fields() -> None:
    project = EngineeringDesignProject(
        design_project_id="EDP-FIELDS", project_id="PROJ-FIELDS", schema_version="1", chassis="E. coli",
        chassis_version_or_genotype="K-12", diagnosis_session_id="DIAG-FIELDS", diagnosis_decision_id="DDEC-FIELDS",
        diagnosis_version=2, status="portfolio_generated", created_by="test", created_at=time.time(), updated_at=time.time(),
    )
    candidate = CandidateDesign(
        design_id="CAND-FIELDS", design_project_id=project.design_project_id, lineage_id="CAND-FIELDS",
        design_version=1, parent_design_ids=[], strategy_ids=[], genetic_modifications=[{"target_identifier": "ptsG"}],
        regulatory_architecture={}, process_modifications=[{"operation": "fed_batch"}], expected_mechanism="PEP conservation",
        causal_chain=["PTS reduction", "PEP conservation"], interaction_and_epistasis_assumptions=["requires non-PTS uptake"],
        evidence_links=[{"source_type": "diagnosis_hypothesis", "reference": "HYP-1"}], counterfactual_requests=[],
        counterfactual_results=[], uncertainty_and_model_conflicts=["growth effect not computed"], safety_flags=[],
        source_diagnosis_version=2, proposed_by="test", created_at=time.time(),
    )
    with db.session_scope() as session:
        session.add(Project(project_id="PROJ-FIELDS", name="Fields", host_definition={}, target_product="target", created_at=time.time(), updated_at=time.time()))
        session.flush()
        session.add(project)
        session.flush()
        session.add(candidate)
    payload = _client().get("/api/engineering-design/candidates/CAND-FIELDS").json()
    assert payload["causal_chain"] == ["PTS reduction", "PEP conservation"]
    assert payload["interaction_and_epistasis_assumptions"] == ["requires non-PTS uptake"]
    assert payload["evidence_links"][0]["reference"] == "HYP-1"
    assert payload["process_modifications"] == [{"operation": "fed_batch"}]
    assert payload["source_diagnosis_version"] == 2
