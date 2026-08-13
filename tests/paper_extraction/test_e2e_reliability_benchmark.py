import json
from pathlib import Path

import jsonschema

from benchmarks.paper_extraction_e2e_v1.evaluation.evaluate import BASE, ROOT, run


def test_e2e_benchmark_governance_sources_and_splits():
    annotation, result = run()
    schema = json.loads((BASE / "annotations/e2e_annotation.schema.json").read_text(encoding="utf-8"))
    jsonschema.validate(annotation, schema)
    assert annotation["annotation_tier"] == "silver"
    assert annotation["review_status"] == "NOT_HUMAN_REVIEWED"
    dev = {p["paper_id"] for p in annotation["papers"] if p["split"] == "development"}
    holdout = {p["paper_id"] for p in annotation["papers"] if p["split"] == "holdout"}
    assert len(dev) == 10 and len(holdout) == 5 and dev.isdisjoint(holdout)
    assert sum(len(p["skill07_claims"]) for p in annotation["papers"]) >= 100
    assert result["release_gate"]["status"] == "PARTIAL"


def test_every_paper_and_claim_anchor_is_traceable():
    annotation, _ = run()
    for paper in annotation["papers"]:
        document = json.loads((ROOT / paper["clean_document_path"]).read_text(encoding="utf-8"))
        ids = {p["paragraph_id"] for p in document["paragraphs"]}
        assert paper["document_hash"]
        for claim in paper["skill07_claims"]:
            resolved = [anchor["paragraph_id"] in ids for anchor in claim["gold_evidence_anchors"]]
            if claim["gold_E1"]:
                assert resolved and all(resolved)
            elif resolved:
                assert not all(resolved)


def test_safety_corpus_is_not_modified_or_folded_into_development():
    manifest = json.loads((BASE / "safety/manifest.json").read_text(encoding="utf-8"))
    source = ROOT / "benchmarks/skill08_verification_benchmark/cases/real_paper_cases.json"
    assert manifest["immutable"] is True and manifest["cases"] == 13
    assert len(json.loads(source.read_text(encoding="utf-8"))["cases"]) == 13
