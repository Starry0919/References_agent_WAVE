from __future__ import annotations

from pathlib import Path

import httpx

from harness.literature_discovery.acquisition import AcquisitionManager, handoff_manifest, validate_pdf
from harness.literature_discovery.adapters import OpenAlexAdapter
from harness.literature_discovery.adapters import CrossrefAdapter
from harness.literature_discovery.identity import deduplicate
from harness.literature_discovery.models import (
    AcquisitionState, PaperCandidate, RelevanceTier, ScientificLiteratureRequest, SearchQueryRecord, SourceRecord,
)
from harness.literature_discovery.query import generate_queries
from harness.literature_discovery.relevance import assess
from harness.literature_discovery.service import LiteratureDiscoveryService


REQUEST = ScientificLiteratureRequest.k12_tryptophan()


def paper(title: str, abstract: str, *, doi: str | None = None, review: bool = False, oa_urls=None) -> PaperCandidate:
    return PaperCandidate(candidate_id=doi or title, canonical_title=title, abstract=abstract, doi=doi, is_review=review, oa_urls=oa_urls or [])


def test_request_normalization_and_bounded_query_families():
    queries = generate_queries(REQUEST, ["openalex", "crossref"])
    assert REQUEST.organism.lineage == "K-12"
    assert "MG1655" in REQUEST.organism.strain_aliases
    assert len(queries) == REQUEST.max_queries
    assert len({q.query_id for q in queries}) == len(queries)
    assert {q.query_family for q in queries} == {"exact_objective", "metabolic_engineering", "strain_lineage", "pathway_intervention", "fermentation_bioprocess", "recall_expansion"}
    assert all(q.rationale and q.target_source for q in queries)


def test_adapter_normalization_preserves_provenance():
    payload = {"results": [{
        "id": "https://openalex.org/W1", "doi": "https://doi.org/10.1/X", "title": "Engineered tryptophan production",
        "publication_year": 2024, "type": "article", "authorships": [{"author": {"display_name": "A Author"}}],
        "primary_location": {"source": {"display_name": "Journal"}}, "best_oa_location": {"pdf_url": "https://example.org/a.pdf"},
        "locations": [], "abstract_inverted_index": {"Escherichia": [0], "coli": [1]}, "open_access": {"is_oa": True},
    }]}
    transport = httpx.MockTransport(lambda request: httpx.Response(200, json=payload))
    adapter = OpenAlexAdapter(client=httpx.Client(transport=transport))
    query = SearchQueryRecord(query_id="q1", query_text="x", query_family="exact", rationale="test", target_source="openalex")
    result = adapter.search(query, 5)
    assert result[0].doi == "10.1/x"
    assert result[0].abstract == "Escherichia coli"
    assert result[0].source_records[0].query_id == "q1"


def test_crossref_uses_supported_select_fields():
    captured = {}
    def handler(request):
        captured["url"] = str(request.url)
        return httpx.Response(200, json={"message": {"items": []}})
    adapter = CrossrefAdapter(client=httpx.Client(transport=httpx.MockTransport(handler)))
    query = SearchQueryRecord(query_id="q1", query_text="x", query_family="exact", rationale="test", target_source="crossref")
    adapter.search(query, 5)
    assert "subtype" not in captured["url"]
    assert "select=" in captured["url"]


def test_dedup_doi_and_conservative_title():
    a = paper("Engineering L-tryptophan production in Escherichia coli", "", doi="10.1/a")
    a.source_records = [SourceRecord(source="a", query_id="q")]
    b = paper("Engineering L tryptophan production in Escherichia coli", "abstract", doi="10.1/a")
    b.source_records = [SourceRecord(source="b", query_id="q")]
    c = paper("Engineering L-tryptophan production in Bacillus", "", doi="10.1/c")
    result = deduplicate([a, b, c])
    assert len(result) == 2
    assert len(result[0].source_records) == 2
    assert result[0].abstract == "abstract"


def test_positive_relevance_tiers_and_reason_codes():
    positive = paper(
        "Metabolic engineering of Escherichia coli K-12 MG1655 for L-tryptophan production",
        "A feedback resistant enzyme was overexpressed and precursor flux improved in fed-batch fermentation to 42 g/L.",
    )
    result = assess(positive, REQUEST)
    assert result.decision == RelevanceTier.TIER_1
    assert {"HOST_EXACT", "PRODUCT_EXACT", "ENGINEERING_INTERVENTION", "PRODUCTION_METRIC"} <= set(result.reason_codes)


def test_required_false_positive_fixture_matrix():
    fixtures = [
        paper("Tryptophan metabolism in E. coli infection", "Clinical patient infection study of pathogenic isolates."),
        paper("Pathogenic Escherichia coli in patients", "Clinical virulence study mentioning tryptophan."),
        paper("Tryptophan assay for E. coli detection", "Analytical detection method for food contamination."),
        paper("Tryptophan physiology in E. coli K-12", "Basic physiology without strain engineering."),
        paper("Engineering Corynebacterium for tryptophan production", "Metabolic engineering increased production to 10 g/L."),
        paper("A review of E. coli K-12 tryptophan production engineering", "Review of pathway engineering and titers.", review=True),
        paper("Aromatic metabolism in bacteria", "K-12 is cited in background references; tryptophan is discussed."),
        paper("Engineering E. coli K-12 for succinate", "Tryptophan was measured, but production engineering targeted succinate."),
    ]
    results = [assess(item, REQUEST) for item in fixtures]
    assert all(r.decision != RelevanceTier.TIER_1 for r in results)
    assert results[0].decision == RelevanceTier.EXCLUDE
    assert "REVIEW_ARTICLE" in results[5].reason_codes


def test_pathway_support_is_not_direct_without_production_metric():
    candidate = paper("Feedback-resistant tryptophan synthase engineering in E. coli W3110", "Pathway flux and transporter overexpression improved biosynthesis.")
    result = assess(candidate, REQUEST)
    assert result.decision == RelevanceTier.TIER_2


def test_related_products_and_abstract_only_terms_are_not_tier_two():
    hydroxy = paper("Production of 5-hydroxytryptophan in Escherichia coli", "Metabolic engineering improved yield to 5 g/L.")
    biofilm = paper("Temporal gene expression in Escherichia coli K-12 biofilms", "Tryptophan production and pathway mutants appear in the study metadata.")
    indole = paper("Indole production by E. coli tryptophanase", "Exogenous tryptophan controls production.")
    assert assess(hydroxy, REQUEST).decision != RelevanceTier.TIER_2
    assert "OTHER_PRODUCT_TARGET" in assess(hydroxy, REQUEST).reason_codes
    assert assess(biofilm, REQUEST).decision != RelevanceTier.TIER_2
    assert assess(indole, REQUEST).decision != RelevanceTier.TIER_2


def test_pdf_validation_and_idempotent_acquisition(tmp_path: Path):
    valid = b"%PDF-1.4\n" + b"x" * 1200 + b"\n%%EOF"
    assert validate_pdf(valid)
    assert not validate_pdf(b"<html>not a pdf</html>")
    transport = httpx.MockTransport(lambda request: httpx.Response(200, headers={"content-type": "application/pdf"}, content=valid))
    manager = AcquisitionManager(tmp_path, client=httpx.Client(transport=transport))
    candidate = paper("Paper", "", doi="10.1/a", oa_urls=["https://example.org/a.pdf"])
    first = manager.acquire(candidate)
    second = manager.acquire(candidate)
    assert first.state == AcquisitionState.ACQUIRED
    assert second.state == AcquisitionState.ALREADY_PRESENT
    assert first.sha256 == second.sha256


def test_html_masquerading_as_pdf_is_rejected(tmp_path: Path):
    body = b"%PDF-<html>" + b"x" * 1200 + b"%%EOF"
    transport = httpx.MockTransport(lambda request: httpx.Response(200, headers={"content-type": "text/html"}, content=body))
    manager = AcquisitionManager(tmp_path, client=httpx.Client(transport=transport))
    result = manager.acquire(paper("Paper", "", oa_urls=["https://example.org/a.pdf"]))
    assert result.state in {AcquisitionState.NOT_PDF, AcquisitionState.HTTP_ERROR}


def test_graceful_source_failure_and_handoff(tmp_path: Path):
    class FailedAdapter(OpenAlexAdapter):
        name = "failed"
        def search(self, *args, **kwargs):
            raise RuntimeError("offline")
    service = LiteratureDiscoveryService(adapters=[FailedAdapter(client=httpx.Client(transport=httpx.MockTransport(lambda r: httpx.Response(500))))])
    result = service.discover(REQUEST)
    assert result.candidates == []
    assert result.source_runs[0].errors
    candidate = paper("Ready", "", doi="10.1/x")
    candidate.acquisition.state = AcquisitionState.ACQUIRED
    candidate.acquisition.local_path = str(tmp_path / "paper.pdf")
    manifest = handoff_manifest([candidate], project_id="p1")
    assert manifest["papers"][0]["processing_state"] == "ready_for_existing_ingest"
    assert manifest["existing_pipeline_payloads"][0]["source_type"] == "upload"
    assert manifest["existing_pipeline_payloads"][0]["files"] == [str(tmp_path / "paper.pdf")]
    from harness.paper_extraction.service import build_request
    built = build_request(manifest["existing_pipeline_payloads"][0])
    assert built["literature_source"]["files"] == [str(tmp_path / "paper.pdf")]
