from harness.db import get_session_factory
from harness.evidence_retrieval.dynamic_loop import create_evidence_need, resolve_evidence_need, resolve_and_update_hypothesis
from harness.engineering_design.historical_prior import HistoricalPriorRecord, compatibility_score
from harness.evidence_retrieval.hybrid import RetrievalUnit, hybrid_retrieve
from harness.engineering_design.failure_recall import failure_penalty
from harness.learning.models import FailureCase
from harness.projects.models import Project
from harness.learning.models import HypothesisFamily
from harness.learning.service import propose_hypothesis
from harness.engineering_design.decision import recommend_portfolio

def test_evidence_need_retrieval_update_and_stop():
    with get_session_factory()() as db:
        need=create_evidence_need(db,project_id="P1",decision_node_id="D1",claim_or_hypothesis_id="H1",
            gap_type="critical_claim_coverage",missing_relation="direct result evidence",required_source_type="primary_literature",required_context={"host":"E. coli"})
        resolved=resolve_evidence_need(db,need_id=need.need_id,query="E. coli direct experiment",
            retriever=lambda q,c:[{"evidence_id":"E1","host":"E. coli"}],
            accept=lambda r:(r["host"]=="E. coli","context matched"))
        assert resolved.status == "resolved" and resolved.evidence_refs == ["E1"]
        assert resolved.audit_log[-1]["stop_reason"] == "all_critical_gaps_resolved"

def test_historical_prior_is_never_evidence_or_recommendation():
    row=HistoricalPriorRecord(publication_id="PMID:1",host="Escherichia coli",product="L-tryptophan",gene="aroG",modification_direction="Positive")
    score=compatibility_score(row,host="Escherichia coli",product="L-tryptophan",condition_known=False)
    assert score["historical_prior"] > 0
    assert score["evidence_strength"] == 0 and score["not_evidence"] and score["not_recommendation"]

def test_section_aware_hybrid_retrieval_preserves_claim_authority():
    units=[RetrievalUnit("r","aroG overexpression increased tryptophan titer","results","p",{}),
           RetrievalUnit("d","aroG may be useful in future designs","discussion","p",{})]
    rows=hybrid_retrieve("aroG tryptophan titer",units,dense_score=lambda q,t: .9 if "aroG" in t else 0)
    assert rows[0]["unit"].unit_id=="r" and rows[0]["claim_authority"]=="experimental_fact"

def test_biological_negative_result_is_recalled_but_qc_failure_is_excluded():
    with get_session_factory()() as db:
        db.add(Project(project_id="P1",name="trp",host_definition={},target_product="L-tryptophan",
                       objectives=[],constraints=[],owners=[],created_at=1,updated_at=1))
        db.flush()
        db.add_all([
            FailureCase(failure_case_id="BIO",project_id="P1",failure_class="biological_null",
                        expected_outcome="aroG overexpression raises titer",candidate_causes=["aroG burden"],
                        data_qc_status="passed",applicability_scope={"host":"E. coli"},created_at=1),
            FailureCase(failure_case_id="QC",project_id="P1",failure_class="measurement",
                        expected_outcome="aroG overexpression raises titer",candidate_causes=["instrument error"],
                        data_qc_status="passed",applicability_scope={"host":"E. coli"},created_at=1),
        ])
        db.flush()
        result=failure_penalty(db,project_id="P1",intervention_tokens=["aroG"],context={"host":"E. coli"})
        assert result["penalty"] > 0
        assert [x["failure_case_id"] for x in result["retrieved_failure_cases"]] == ["BIO"]

def test_failure_memory_penalty_changes_production_rank():
    vector=[{"metric":"build_complexity","direction_estimate":"low"}]
    base={"hard_constraint_results":[],"objective_vector":vector,"blocking_findings":[],"portfolio_role":"low_risk"}
    before=recommend_portfolio(evaluations_by_design={
        "X":{**base,"failure_recall":{"penalty":0.0}},"Y":{**base,"failure_recall":{"penalty":0.0}}},preferences_or_weights=[])
    after=recommend_portfolio(evaluations_by_design={
        "X":{**base,"failure_recall":{"penalty":0.8,"retrieved_failure_cases":[{"failure_case_id":"BIO"}]}},
        "Y":{**base,"failure_recall":{"penalty":0.0}}},preferences_or_weights=[])
    assert before["selected_design_ids"].index("X") == 0
    assert after["selected_design_ids"].index("X") == 1

def test_evidence_need_appends_hypothesis_version_and_graph_snapshot():
    with get_session_factory()() as db:
        db.add(Project(project_id="PE",name="evidence",host_definition={},target_product="trp",
                       objectives=[],constraints=[],owners=[],created_at=1,updated_at=1)); db.flush()
        db.add(HypothesisFamily(hypothesis_family_id="HF",project_id="PE",title="limitation",created_at=1)); db.flush()
        parent=propose_hypothesis(db,project_id="PE",hypothesis_family_id="HF",statement="precursor supply limits titer",
            actor_id="system",posterior_status="weakly_supported",confidence="low",alternatives=["measurement artifact"])
        need=create_evidence_need(db,project_id="PE",decision_node_id="D",claim_or_hypothesis_id=parent.hypothesis_version_id,
            gap_type="critical_claim_coverage",missing_relation="direct result",required_source_type="primary_literature",
            required_context={"host":"E. coli"})
        resolved,new=resolve_and_update_hypothesis(db,need_id=need.need_id,query="precursor perturbation result",actor_id="system",
            retriever=lambda q,c:[{"evidence_id":"EV-primary","relation":"supports","host":"E. coli"}],
            accept=lambda r:(r["host"]=="E. coli","context matched"))
        assert new is not None and new.parent_hypothesis_version_id == parent.hypothesis_version_id
        assert new.posterior_status == "strongly_supported" and new.supporting_evidence_ids == ["EV-primary"]
        assert resolved.audit_log[-1]["before_graph"]["hypothesis_version_id"] == parent.hypothesis_version_id
        assert resolved.audit_log[-1]["after_graph"]["hypothesis_version_id"] == new.hypothesis_version_id
