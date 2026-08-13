import pytest
from sqlalchemy import select

from harness.db import get_session_factory
from harness.engineering_design.decision_state import InvalidCandidateTransition, transition_candidate
from harness.engineering_design.model_evaluation import evaluate_candidate_fba
from harness.engineering_design.models import CandidateDesign, EngineeringDesignProject
from harness.projects.service import create_project
from harness.ids import new_id, now

def make_candidate(db):
    project=create_project(db,name="grounded test project",host_definition={"species":"E. coli","strain":"K-12 MG1655"},target_product="L-tryptophan",actor_id="test")
    dp=EngineeringDesignProject(design_project_id=new_id("DPROJ"),project_id=project.project_id,chassis="E. coli",chassis_version_or_genotype="K-12 MG1655",
        diagnosis_session_id="DIAG-TEST",diagnosis_decision_id="DDEC-TEST",diagnosis_version=1,created_by="test",created_at=now(),updated_at=now())
    db.add(dp); db.flush()
    candidate=CandidateDesign(design_id=new_id("CDES"),design_project_id=dp.design_project_id,lineage_id=new_id("LIN"),strategy_ids=["STRAT-TEST"],
        diagnosis_finding_ids=["DFIND-TEST"],genetic_modifications=[{"operation":"knockout","target_identifier":"b3708","display_name":"tnaA"}],
        expected_mechanism="reduce tryptophan degradation",source_diagnosis_version=1,proposed_by="test",created_at=now())
    db.add(candidate);db.flush();return project,dp,candidate

def test_generated_candidate_cannot_skip_to_selected_or_build_ready():
    with get_session_factory()() as db:
        _,_,candidate=make_candidate(db)
        with pytest.raises(InvalidCandidateTransition): transition_candidate(db,design_id=candidate.design_id,target="selected",actor_id="system")
        with pytest.raises(InvalidCandidateTransition): transition_candidate(db,design_id=candidate.design_id,target="build_ready",actor_id="system")

def test_real_candidate_specific_iml1515_baseline_vs_candidate():
    with get_session_factory()() as db:
        project,_,candidate=make_candidate(db)
        kos=[m["target_identifier"] for m in candidate.genetic_modifications if m.get("operation")=="knockout"]
        result=evaluate_candidate_fba(db,project_id=project.project_id,candidate_id=candidate.design_id,target_product="L-tryptophan",
            product_reaction="EX_trp__L_e",biomass_reaction="BIOMASS_Ec_iJO1366_core_53p95M",
            medium_bounds={"EX_glc__D_e":{"lower":-10,"upper":1000},"EX_o2_e":{"lower":-20,"upper":1000}},
            oxygen_condition="aerobic",gene_knockouts=kos,actor_id="test")
        assert result.model_version == "iJO1366"
        assert result.baseline_growth is not None and result.baseline_product_flux is not None
        assert result.fva_summary
        assert result.assumptions and result.limitations
