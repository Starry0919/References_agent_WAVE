import json
import re
from pathlib import Path

import jsonschema

from benchmarks.skill08_verification_benchmark.evaluation.evaluate import evaluate


ROOT = Path(__file__).resolve().parents[2]
BENCHMARK = ROOT / "benchmarks" / "skill08_verification_benchmark"


def _cases():
    return json.loads((BENCHMARK / "cases" / "real_paper_cases.json").read_text(encoding="utf-8"))["cases"]


def _tokens(text):
    return set(re.findall(r"[a-z0-9]+", text.casefold())) - {"the", "a", "an", "of", "to", "and", "was", "were", "is"}


def test_gold_cases_validate_against_versioned_schema():
    schema = json.loads((BENCHMARK / "gold_annotations" / "gold.schema.json").read_text(encoding="utf-8"))
    for case in _cases():
        jsonschema.validate(case, schema)


def test_every_benchmark_anchor_exists_in_real_clean_document():
    for case in _cases():
        source = ROOT / case["source_path"]
        assert source.is_file(), case["case_id"]
        document = json.loads(source.read_text(encoding="utf-8"))
        paragraph = next((p for p in document["paragraphs"] if p["paragraph_id"] == case["source_anchor"]), None)
        assert paragraph is not None, case["case_id"]
        evidence_tokens = _tokens(case["candidate_evidence"])
        overlap = len(evidence_tokens & _tokens(paragraph["text"])) / max(1, len(evidence_tokens))
        assert overlap >= 0.65, (case["case_id"], overlap)


def test_benchmark_release_gates():
    _, metrics = evaluate(_cases())
    assert metrics["false_verified_critical_claims"] == 0
    assert metrics["verification_precision"] >= 0.90
    assert metrics["verification_recall"] >= 0.80
    assert metrics["attribution_accuracy"] >= 0.90
    assert metrics["overall_accuracy"] >= 0.85
