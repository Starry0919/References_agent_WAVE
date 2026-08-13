import copy
import json

import pytest

from benchmarks.paper_extraction_e2e_v2.annotations.workbench import finalize
from benchmarks.paper_extraction_e2e_v2.evaluation.replay import run
from harness.paper_extraction.experiment_native import migrate_additively, stable_id, validate_native
from benchmarks.paper_extraction_e2e_v2.evaluation.benchmark_v2 import evaluate
from benchmarks.paper_extraction_e2e_v2.evaluation.replay_15 import run as run_15
from harness.paper_extraction.gold_agreement import agreement_report
from harness.paper_extraction.knowledge_admission import evaluate_admission


def _legacy():
    return {"fields": {"outcomes": {"value": "titer increased", "status": "reported", "evidence_ids": ["p1"]}},
            "field_metadata": {"outcomes": {"source_locations": [{"paragraph_id": "p1", "section": "results", "quote": "titer increased", "source_attribution": "current_article"}]}},
            "experimental_design_object": {"experiments": [{"experiment_id": "e1", "evidence": ["p1"]}]}}


def test_additive_migration_preserves_legacy_and_marks_review_required():
    value = _legacy(); before = copy.deepcopy(value); actions = migrate_additively(value)
    assert value["fields"] == before["fields"] and value["experimental_design_object"] == before["experimental_design_object"]
    assert value["projection_metadata"]["derived_projection"] is True
    assert value["experiment_instances"][0]["review_required"] is True
    assert value["atomic_claims"][0]["migration_generated"] is True
    assert not validate_native(value) and actions


def test_native_validator_rejects_cross_experiment_and_non_atomic_shape():
    value = _legacy(); migrate_additively(value)
    value["atomic_claims"][0]["experiment_id"] = "missing"
    value["atomic_claims"][0]["subject"] = ["strain-a", "strain-b"]
    failures = validate_native(value)
    assert any("does not resolve" in item for item in failures)
    assert any("must be scalar" in item or "not of type 'string'" in item for item in failures)


def test_atomic_claim_admission_is_independent_of_legacy_fields():
    admission = evaluate_admission({"claim_verifications": {"c1": {"verification": {"overall_status": "verified"}}}, "field_verifications": {}, "ddr_verifications": []}, {"skill08_artifact_id": "s8"})
    assert admission["status"] == "KNOWLEDGE_ADMISSION_PARTIAL"
    assert admission["admitted_atomic_claims"] == ["c1"]


def test_gold_finalizer_refuses_unreviewed_silver(tmp_path):
    review = tmp_path / "review.json"; review.write_text(json.dumps({"annotation_tier": "silver", "review_status": "PENDING", "adjudication_status": "PENDING"}), encoding="utf-8")
    with pytest.raises(ValueError): finalize(review, tmp_path / "gold.json", "reviewer")


def test_current_contract_real_document_replay():
    report = run()
    assert report["handoff"] == "passed" and report["candidate_immutable"] is True
    assert report["atomic_claim_status"] == "verified"
    assert report["admission_status"] == "KNOWLEDGE_ADMISSION_PARTIAL"


def test_stable_ids_do_not_depend_on_mapping_or_locator_order():
    assert stable_id("experiment", "doc:abc", {"anchors": ["p1", "p2"], "local": "methods-a"}) == stable_id(
        "experiment", "doc:abc", {"local": "methods-a", "anchors": ["p1", "p2"]})
    a, b = _legacy(), _legacy()
    migrate_additively(a, "doc:abc", "paper:1"); migrate_additively(b, "doc:abc", "paper:1")
    assert a["atomic_claims"][0]["claim_id"] == b["atomic_claims"][0]["claim_id"]


def test_migration_preserves_raw_payload_and_exposes_loss():
    value = _legacy(); original = copy.deepcopy(value["experimental_design_object"]["experiments"][0])
    migrate_additively(value)
    exp = value["experiment_instances"][0]
    assert exp["legacy_payload"] == original
    assert exp["review_required"] and not exp["provenance"]["identity_resolved"]


def test_benchmark_refuses_silver_as_gold_and_detects_reject_all():
    result = evaluate([{"experiment_instances": [], "atomic_claims": [], "admission_predictions": []}],
                      [{"annotation_tier": "SILVER_AI_ASSISTED", "experiment_id": "e1"}])
    assert result["gold_records"] == 0
    assert result["scientific_metrics"]["experiment_extraction"]["status"] == "NOT_ESTIMABLE"
    assert result["anti_gaming"]["reject_all_detected"] is True


def test_iaa_refuses_unassigned_or_model_generated_reviewers():
    empty={"annotator_id":"UNASSIGNED","annotation_tier":"UNANNOTATED","experiments":[],"claims":[]}
    assert agreement_report(empty, empty)["status"] == "NOT_ESTIMABLE"


def test_replay_15_attempts_every_manifest_paper_and_maps_stage_status():
    result=run_15()
    assert result["attempted"] == 15 and result["completed"] == 15
    assert result["stage_counts"]["e1_completed"] == result["stage_counts"]["e2_completed"] == result["stage_counts"]["e3_completed"] == 15
    assert result["cross_paper_contamination"] == 0
