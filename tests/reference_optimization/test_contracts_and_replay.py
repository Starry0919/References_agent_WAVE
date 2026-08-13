from __future__ import annotations

from harness.evaluation.scientific_benchmark_v2 import BenchmarkAxis, ScientificBenchmarkCase
from harness.paper_extraction.execution_plan import build_execution_plan
from harness.paper_extraction.frontend_adapter import execute as frontend_execute
from harness.paper_extraction.opus_extractor import make_executor
from harness.paper_extraction.release_contract import build_release_manifest


def _document(title: str, abstract: str, sections: list[tuple[str,str]]):
    return {
        "document_metadata":{"paper_id":title[:24],"title":title},
        "sections":[{"title":name,"content":text} for name,text in sections],
        "paragraphs":[{"paragraph_id":f"p{i}","section":name,"text":text} for i,(name,text) in enumerate(sections)],
    }


def test_reference_papers_are_permanent_route_regressions_without_title_specific_logic():
    synbio=_document(
        "SynBioGPT2: A dynamic reasoning framework enables high-fidelity design of microbial cell factories",
        "A retrieval-augmented multi-agent framework was evaluated on a benchmark.",
        [("Methods","A benchmark dataset consisting of 120 tasks was constructed."),
         ("Results","The model runtime was 2 min and accuracy was measured against comparative baselines.")],
    )
    eliser=_document(
        "A database of over 15,000 strain design publications reveals a conserved set of metabolic engineering targets",
        "We created a database by extracting host, product, gene, and modification direction from publications.",
        [("Methods","Full texts were processed with named entity recognition and database records retained provenance."),
         ("Results","Gene co-occurrence and historical target frequency were reported across microbial hosts.")],
    )
    assert build_execution_plan(synbio).execution_route == "BENCHMARK_ROUTE"
    assert build_execution_plan(eliser).execution_route == "RESOURCE_ROUTE"


def test_runtime_gate_and_frontend_contract_block_non_experimental_document(tmp_path):
    doc=_document("Database of microbial strain designs","A resource database and dataset.",
                  [("Methods","Database records contain host product gene relations and provenance.")])
    path=tmp_path/"clean.json"
    path.write_text(__import__("json").dumps(doc),encoding="utf-8")
    result=make_executor("must-not-run")({"clean_document_artifact":{"clean_json_path":str(path)}})
    assert result["metrics"]["model_calls"] == 0
    assert result["output"]["experiment_instances"] == []
    plan=result["output"]["extensions"]["literature_execution_plan"]
    front=frontend_execute({"literature_execution_plans":[plan]})
    assert front["status"] == "succeeded"
    assert front["self_check"]["checks"][0]["name"] == "source_labels_valid"
    assert front["output"]["candidate_state"] == "not_applicable"


def test_versioned_benchmark_and_release_manifest_contracts():
    case=ScientificBenchmarkCase(case_id="holdout-2026",axis=BenchmarkAxis.TEMPORAL_HOLDOUT,
        input_artifact_refs=["doi:10/example"],expected_invariants=["no critical false support"],
        development_cutoff_year=2024,publication_year=2026)
    manifest=build_release_manifest(release_id="r1",artifact_type="literature_execution_plan",
        artifact=case.model_dump(mode="json"),contract_version=case.schema_version,
        data_dictionary={"axis":"scientific destruction-test axis"},
        enum_contracts={"axis":[x.value for x in BenchmarkAxis]},migration_note="additive schema")
    assert len(manifest.artifact_sha256) == 64
    assert manifest.schema_version == "artifact-release-manifest/1.0"
