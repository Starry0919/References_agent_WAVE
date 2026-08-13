from harness.literature_discovery.classification import LiteratureClassification, classify
from harness.literature_discovery.models import PaperCandidate, ScientificLiteratureRequest
from harness.literature_discovery.readiness import literature_readiness
from harness.literature_discovery.routing import route
from harness.literature_discovery.service import LiteratureDiscoveryService
from harness.literature_discovery.taxonomy import TAXONOMY


def paper(title, abstract="", **kw):
    return PaperCandidate(candidate_id=title, canonical_title=title, abstract=abstract, **kw)


def values(result, axis): return {x.value for x in getattr(result, axis).labels}


def test_taxonomy_contract_and_required_vocabularies():
    assert TAXONOMY["contract_version"] == "literature-taxonomy/2.0"
    assert {"ORIGINAL_RESEARCH", "SYSTEMATIC_REVIEW", "DATABASE_PAPER"} <= set(TAXONOMY["publication_form"])
    assert {"WET_LAB_EXPERIMENTAL", "COMPUTATIONAL", "HYBRID_COMPUTATIONAL_EXPERIMENTAL"} <= set(TAXONOMY["research_design"])
    assert {"GENE_KNOCKOUT", "TRANSPORTER_ENGINEERING", "ADAPTIVE_LABORATORY_EVOLUTION"} <= set(TAXONOMY["engineering_modes"])


def test_review_subtypes_and_generic_fallback():
    cases = {
        "A narrative review of tryptophan": "NARRATIVE_REVIEW",
        "Systematic review of strain engineering": "SYSTEMATIC_REVIEW",
        "A scoping review of biosynthesis": "SCOPING_REVIEW",
        "Meta-analysis of fermentation": "META_ANALYSIS",
        "Tryptophan technology review": "TECHNOLOGY_REVIEW",
    }
    for title, expected in cases.items(): assert expected in values(classify(paper(title)), "publication_form")
    assert "REVIEW" in values(classify(paper("Tryptophan pathways", "This review summarizes prior research.")), "publication_form")
    assert "REVIEW_SYNTHESIS_ROUTE" == route(classify(paper("A systematic review of engineering")))["value"]


def test_false_review_and_primary_form_are_separate_from_strength():
    result = classify(paper("Review of promoter activity after fermentation", "We reviewed measurements and constructed strains; we measured titer."))
    assert "REVIEW" not in values(result, "publication_form")
    assert result.classification_conflict is False
    assert "ORIGINAL_RESEARCH" in values(result, "publication_form")


def test_wet_computational_hybrid_and_model_route():
    hybrid = classify(paper("Model-guided engineering", "We constructed strains and measured fermentation; computational simulation guided design."))
    assert {"WET_LAB_EXPERIMENTAL", "COMPUTATIONAL", "HYBRID_COMPUTATIONAL_EXPERIMENTAL"} <= values(hybrid, "research_design")
    model = classify(paper("Genome-scale model of tryptophan", "We developed a computational model simulation in silico."))
    assert route(model)["value"] == "MODEL_ROUTE"


def test_engineering_and_evidence_are_multilabel():
    result = classify(paper("Metabolic engineering by promoter and transporter engineering", "We overexpressed genes, performed knockout and fed-batch fermentation with titer, yield and productivity."))
    assert {"GENE_KNOCKOUT", "GENE_OVEREXPRESSION", "PROMOTER_ENGINEERING", "TRANSPORTER_ENGINEERING"} <= values(result, "engineering_modes")
    assert {"FERMENTATION", "TITER", "YIELD", "PRODUCTIVITY"} <= values(result, "evidence_modalities")


def test_method_resource_software_benchmark_routes():
    cases = {
        "A new method for enzyme activity": "METHOD_ROUTE",
        "TryptoBase database resource": "RESOURCE_ROUTE",
        "TryptoTool software package": "SOFTWARE_ROUTE",
        "A benchmark of metabolic models": "BENCHMARK_ROUTE",
    }
    for title, expected in cases.items(): assert route(classify(paper(title)))["value"] == expected


def test_fulltext_refinement_preserves_metadata_provenance_and_conflict():
    candidate = paper("A review of tryptophan", publication_type="review", is_review=True)
    metadata = classify(candidate)
    candidate.metadata_classification = metadata.model_dump()
    refined = LiteratureDiscoveryService.refine_with_fulltext(candidate, {"text": "Methods. We constructed strains and measured fermentation titer."})
    assert refined.fulltext_classification["provenance"][0]["stage"] == "metadata"
    assert refined.final_classification["classification_conflict"] is True
    assert refined.route["value"] == "MANUAL_REVIEW_ROUTE"


def test_gold_pending_does_not_block_search_classification_or_acquisition():
    readiness = literature_readiness(False)
    assert readiness["literature_discovery"] == "PRODUCTION_READY"
    assert readiness["literature_classification"] == "PRODUCTION_READY_WITH_CONFIDENCE"
    assert readiness["literature_acquisition"] == "PRODUCTION_READY_WITH_PROVENANCE"
    assert readiness["formal_validation"] == "GOLD_PENDING"
    assert readiness["downstream_auto_knowledge_admission"] == "CONSERVATIVE"
    assert readiness["ddr_writes_enabled"] is False


def test_old_candidate_and_request_are_backward_compatible():
    candidate = PaperCandidate(candidate_id="old", canonical_title="Old record")
    request = ScientificLiteratureRequest.k12_tryptophan()
    assert classify(candidate).contract_version == "literature-classification/2.0"
    assert request.desired_publication_forms == []
