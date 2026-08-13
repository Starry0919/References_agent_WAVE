"""Component 2 - engineering-aware retrieval tests, against the real DDR
corpus plus a freshly-recorded diagnosis EvidenceItem."""
from __future__ import annotations

from harness import db
from harness.diagnosis.evidence import record_evidence_item
from harness.evidence_intelligence.models import EngineeringContextQuery
from harness.evidence_intelligence.retrieval import search_evidence
from harness.projects.service import create_project


def test_empty_query_is_a_full_browse_of_the_ddr_corpus():
    results = search_evidence(EngineeringContextQuery(), limit=100)
    ids = {o.origin_ref["ddr_id"] for o in results if o.origin_kind == "ddr_decision_step"}
    assert "DDR-001" in ids  # the whole corpus is reachable, not filtered down by default


def test_host_and_product_query_matches_ddr001_and_ranks_it_first():
    results = search_evidence(EngineeringContextQuery(host="Escherichia coli", product="L-tryptophan"), limit=50)
    assert results, "expected at least one match for E. coli / L-tryptophan"
    assert all(o.host and "coli" in o.host.lower() for o in results if o.host)
    top_ddr_ids = {o.origin_ref["ddr_id"] for o in results[:5] if o.origin_kind == "ddr_decision_step"}
    assert "DDR-001" in top_ddr_ids


def test_product_mismatch_excludes_ddr001_steps():
    results = search_evidence(EngineeringContextQuery(host="Escherichia coli", product="1,4-butanediol"), limit=50)
    ddr001_hits = [o for o in results if o.origin_ref.get("ddr_id") == "DDR-001"]
    assert not ddr001_hits


def test_search_includes_project_scoped_diagnosis_evidence_when_session_given():
    with db.session_scope() as session:
        project = create_project(session, name="t", host_definition={"species": "Escherichia coli"}, target_product="L-tryptophan", actor_id="tester")
        record_evidence_item(
            session, project_id=project.project_id, source_type="literature", content_summary="a project-local finding",
            actor_id="tester", quality="high", directness="direct", organism="Escherichia coli", intervention="knock out ptsG",
        )
        session.flush()

        results = search_evidence(
            EngineeringContextQuery(host="Escherichia coli", intervention_type="ptsG"),
            session=session, project_id=project.project_id, limit=50,
        )
        assert any(o.origin_kind == "diagnosis_evidence_item" for o in results)


def test_search_without_session_never_touches_diagnosis_evidence():
    results = search_evidence(EngineeringContextQuery(free_text="tryptophan"), session=None, limit=50)
    assert all(o.origin_kind != "diagnosis_evidence_item" for o in results)
