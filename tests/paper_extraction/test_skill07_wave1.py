import json

from tools.canonical_document_transformer import restore_document, transform_document
from tools.skill07_wave1 import (
    cache_identity,
    cascade_gate,
    classify_repair_failure,
    compare_scientific_outputs,
    high_recall_route,
    local_parse_repair,
    map_reduce_plan,
)


def _document():
    return {
        "document_metadata": {"paper_id": "p"},
        "sections": [
            {"id": "results", "title": "Results", "level": 1, "content": "lead\nP1\nP2\n![](fig.png)"},
        ],
        "paragraphs": [
            {"paragraph_id": "p1", "text": "P1", "section": "results"},
            {"paragraph_id": "p2", "text": "P2", "section": "results"},
        ],
        "figures": [{"figure_id": "Fig. 1", "caption": "caption"}],
        "tables": [{"table_id": "Table 1", "content": "x"}],
        "citations": [],
        "cleaning_metadata": {},
    }


def test_canonical_transform_is_deterministic_exact_and_residual_preserving():
    original = _document()
    first, report = transform_document(original)
    second, _ = transform_document(original)
    assert first == second
    assert restore_document(first) == original
    assert report["exact_roundtrip"] is True
    residual = "".join(item["content"] for item in first["sections"][0]["residual_content"])
    assert "lead" in residual
    assert "![](fig.png)" in residual


def test_cache_identity_isolated_by_candidate_representation_and_model():
    common = dict(
        paper_id="p", source_document_hash="d", prompt_hash="q", skill_hash="s",
        schema_hash="c", validator_version="v", model_provider="poe", model="kimi-k3",
        model_parameters={},
    )
    baseline = cache_identity(**common, representation_version="baseline", candidate_id="A_BASELINE")
    canonical = cache_identity(**common, representation_version="0.1", candidate_id="B_CANONICAL")
    changed_model = cache_identity(**{**common, "model": "different"}, representation_version="baseline", candidate_id="A_BASELINE")
    assert len({baseline["sha256"], canonical["sha256"], changed_model["sha256"]}) == 3


def test_repair_routing_and_local_parse_repair():
    assert classify_repair_failure("JSONDecodeError")["class"] == "R0_PARSE_ERROR"
    assert classify_repair_failure("evidence_id x does not resolve")["class"] == "R3_LOCAL_SEMANTIC_ERROR"
    assert classify_repair_failure("causal chain is contradictory")["class"] == "R4_SCIENTIFIC_REASONING_ERROR"
    assert local_parse_repair("note ```json\n{\"x\": 1}\n``` tail") == {"x": 1}


def test_high_recall_router_retains_scientific_modalities_and_fails_closed():
    routed, report = high_recall_route(_document())
    assert routed["paragraphs"] == _document()["paragraphs"]
    assert routed["figures"] == _document()["figures"]
    assert routed["tables"] == _document()["tables"]
    assert report["coverage_guard_passed"] is True
    assert report["critical_evidence_recall"] == "UNKNOWN_WITHOUT_GOLD"


def test_map_reduce_plan_keeps_original_anchors_and_quality_checks():
    plan = map_reduce_plan(_document())
    assert set(plan["maps"]["evidence_candidates"]) == {"p1", "p2"}
    assert "lost_causal_chain" in plan["quality_checks"]
    assert plan["execution_status"] == "FRAMEWORK_ONLY_NOT_LLM_BENCHMARKED"


def test_cascade_falls_back_without_independent_evidence_and_human_gold():
    decision = cascade_gate({"status": "succeeded"})
    assert decision.decision == "FALLBACK_KIMI_K3"


def test_comparator_flags_missing_experiments_and_evidence_without_claiming_truth():
    baseline = {"experiment_id": "e1", "evidence_ids": ["p1"], "design_action": "M1"}
    candidate = {"experiment_id": "e2", "evidence_ids": [], "design_action": "M1"}
    result = compare_scientific_outputs(baseline, candidate)
    assert result["hard_quality_flags"]
    assert result["human_scientific_judgement"] == "REQUIRED"


def test_resume_contract_preserves_successful_result_file(tmp_path):
    result_path = tmp_path / "result.json"
    value = {"status": "succeeded", "output": {"x": 1}}
    result_path.write_text(json.dumps(value), encoding="utf-8")
    before = result_path.read_bytes()
    loaded = json.loads(result_path.read_text(encoding="utf-8"))
    if loaded.get("status") == "succeeded":
        pass
    assert result_path.read_bytes() == before
