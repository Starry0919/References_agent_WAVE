"""LIVE integration tests (prompt §10.4's "optional live integration
tests" layer) - real network calls to `api.crossref.org`, confirmed
reachable from this environment during Phase C's audit. These are the
concrete mechanism behind invariant #10 ("DOI 不得补造"): a hallucinated
DOI is rejected via a REAL lookup, not a pattern check.

If network access is unavailable when this suite runs elsewhere, these
tests fail with a clear connection error rather than silently passing -
per prompt §10.4, a skipped/failed live test must never be reported as a
pass.
"""
from __future__ import annotations

from harness import db
from harness.evidence_retrieval.crossref_adapter import CrossrefEvidenceAdapter
from harness.evidence_retrieval.local_ddr_adapter import LocalDDRAdapter
from harness.evidence_retrieval.service import verify_doi
from harness.projects import service as proj_svc


def test_crossref_health_check_reports_real_availability():
    health = CrossrefEvidenceAdapter().health_check()
    assert health.available is True
    assert health.source_name == "crossref"
    assert health.latency is not None


def test_real_doi_from_the_local_knowledge_base_resolves():
    """DDR-001's cited reference (10.1002/bit.27665) is a real paper -
    Crossref must resolve it."""
    assert CrossrefEvidenceAdapter().resolve_doi("10.1002/bit.27665") is True


def test_hallucinated_doi_is_rejected():
    assert CrossrefEvidenceAdapter().resolve_doi("10.9999/this-doi-does-not-exist-fabricated-12345") is False


def test_hallucinated_doi_rejection_recorded_as_project_event():
    with db.session_scope() as s:
        proj = proj_svc.create_project(s, name="DOI test", host_definition={"species": "E. coli"}, target_product="x", actor_id="pi")
        resolved = verify_doi(s, project_id=proj.project_id, doi="10.9999/fabricated-doi-abcdef", actor_id="agent")
        assert resolved is False
        from sqlalchemy import select

        from harness.memory import event_types as et
        from harness.projects.models import ProjectEvent

        events = s.execute(select(ProjectEvent).where(ProjectEvent.project_id == proj.project_id, ProjectEvent.event_type == et.GEN_HALLUCINATED_REFERENCE_REJECTED)).scalars().all()
        assert len(events) == 1


def test_crossref_search_returns_real_documents():
    result = CrossrefEvidenceAdapter().search("tryptophan biosynthesis Escherichia coli", pagination={"rows": 3})
    assert result.source_name == "crossref"
    assert len(result.documents) > 0
    assert all(d.source_type == "literature" for d in result.documents)


def test_local_ddr_adapter_health_and_search():
    adapter = LocalDDRAdapter()
    health = adapter.health_check()
    assert health.available is True
    result = adapter.search("L-tryptophan")
    assert any(d.source_id == "DDR-001" for d in result.documents)
    ddr1 = adapter.fetch("DDR-001")
    assert ddr1 is not None
    assert ddr1.doi_or_accession == "10.1002/bit.27665"
    claims = adapter.extract_claims(ddr1, schema_version="1")
    assert len(claims) > 0
    assert all(c.extraction_method == "manual_or_rule" for c in claims)


def test_local_ddr_adapter_reports_unavailable_for_missing_directory(tmp_path):
    adapter = LocalDDRAdapter(ddr_dir=tmp_path / "does_not_exist")
    health = adapter.health_check()
    assert health.available is False
    assert "not found" in health.reason
