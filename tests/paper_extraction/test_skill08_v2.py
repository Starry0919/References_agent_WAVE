import copy
import hashlib
import json
from datetime import datetime, timezone

import pytest

from harness.paper_extraction.handoff import HandoffRejected, assert_unique_handoffs, build_handoff, canonical_hash
from harness.paper_extraction.knowledge_admission import KnowledgeAdmissionBlocked, evaluate_admission, require_admissible_skill08
from harness.paper_extraction.vendor.paper_experimental_design_extraction.workflow.engine import WorkflowEngine
from harness.paper_extraction.vendor.paper_experimental_design_extraction.config import DEFAULT_CONFIG
from harness.paper_extraction.vendor.skills.skill08_evidence_binding.skill import EvidenceBindingEngine
from harness.paper_extraction.vendor.skills.skill08_evidence_binding.verification import semantic_support


def _document(tmp_path, paper_id="paper-a", text="Engineered strain A increased titer to 10 g/L in M9 glucose medium versus WT control."):
    doc = {
        "document_metadata": {"paper_id": paper_id},
        "sections": [{"id": "results", "title": "Results"}],
        "paragraphs": [{"paragraph_id": "p1", "section": "results", "text": text, "page": 1}],
        "figures": [], "tables": [],
    }
    path = tmp_path / f"{paper_id}.json"
    path.write_text(json.dumps(doc), encoding="utf-8")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    return {
        "document_metadata": {"paper_id": paper_id}, "clean_json_path": str(path),
        "clean_json_artifact": {"artifact_id": f"artifact:doc:{paper_id}", "sha256": digest, "uri": str(path)},
    }


def _candidate(value="Engineered strain A increased titer to 10 g/L in M9 glucose medium versus WT control.", attribution="current_article"):
    field = {"value": value, "status": "reported", "applicability_status": "applicable", "confidence": .8,
             "extraction_method": "direct_quote", "evidence_ids": ["candidate:p1"], "notes": None, "inference": None}
    ddr = {"decision_type": "engineering_decision", "design_action": "M3", "design_action_rationale": "Engineered strain A increased titer",
           "trigger_observation": "WT control had lower titer", "reason_nature": "mechanistic_inference",
           "reason_nature_rationale": "Engineered strain A increased titer", "generalizable_rule": "candidate only"}
    return {"contract_version": "skill07_semantic_contract_v1", "fields": {"outcomes": field},
            "field_metadata": {"outcomes": {"evidence_role": "candidate", "source_locations": [{"paragraph_id": "p1", "source_attribution": attribution}]}},
            "experimental_design_object": {"experiments": [{"experiment_id": "e1", "intervention": "Engineered strain A", "outcome": value,
                                                               "evidence": ["p1"], "ddr_annotation": ddr}]}, "extensions": {}, "conflicts": []}


def _result(candidate, *, status="succeeded", eligible=True, passed=True):
    return {"status": status, "output": candidate, "eligible_for_evidence_verification": eligible,
            "self_check": {"passed": passed}, "provenance": {
                "output_hash": canonical_hash(candidate), "schema_version": "wave://paper-extraction/skill07-output/2.1.0",
                "semantic_contract_version": "skill07_semantic_contract_v1", "validation_rules_version": "skill07_validation_rules_v1"}}


def _run(tmp_path, candidate=None, document=None):
    candidate = candidate or _candidate()
    document = document or _document(tmp_path)
    handoff = build_handoff(_result(candidate), document, "artifact:skill07:1", 0)
    return EvidenceBindingEngine(logger=lambda _: None, clock=lambda: datetime(2026, 8, 12, tzinfo=timezone.utc)).execute({"handoff": handoff, "clean_document_artifact": document})


@pytest.mark.parametrize("status,eligible,passed", [
    ("needs_review", True, True), ("succeeded", False, True), ("succeeded", True, False),
])
def test_handoff_gate_blocks_invalid_skill07(tmp_path, status, eligible, passed):
    with pytest.raises(HandoffRejected):
        build_handoff(_result(_candidate(), status=status, eligible=eligible, passed=passed), _document(tmp_path), "artifact:skill07:1")


def test_handoff_blocks_missing_identity_and_hash_mismatch(tmp_path):
    clean = _document(tmp_path)
    clean["document_metadata"]["paper_id"] = None
    with pytest.raises(HandoffRejected): build_handoff(_result(_candidate()), clean, "artifact:skill07:1")


def test_duplicate_identity_fails_closed(tmp_path):
    clean = _document(tmp_path)
    handoff = build_handoff(_result(_candidate()), clean, "artifact:skill07:1")
    with pytest.raises(HandoffRejected): assert_unique_handoffs([handoff, copy.deepcopy(handoff)])
    clean = _document(tmp_path, "paper-b"); clean["clean_json_artifact"]["sha256"] = "0" * 64
    with pytest.raises(HandoffRejected): build_handoff(_result(_candidate()), clean, "artifact:skill07:1")


def test_skill08_candidate_is_immutable_when_unsupported(tmp_path):
    candidate = _candidate("Engineered strain A increased titer to 99 g/L")
    before = copy.deepcopy(candidate)
    result = _run(tmp_path, candidate)
    assert result["output"]["candidate_payload"] == before
    assert result["output"]["candidate_payload"]["fields"]["outcomes"]["status"] == "reported"
    assert result["output"]["field_verifications"]["outcomes"]["verification"]["overall_status"] == "conflicted"
    assert result["output"]["ddr_verifications"][0]["candidate_ddr"] == before["experimental_design_object"]["experiments"][0]["ddr_annotation"]
    assert result["output"]["ddr_verifications"][0]["rule_candidate_role"] == "single_paper_rule_candidate"


def test_level1_nonexistent_anchor_is_not_verified(tmp_path):
    candidate = _candidate(); candidate["field_metadata"]["outcomes"]["source_locations"][0]["paragraph_id"] = "missing"
    verdict = _run(tmp_path, candidate)["output"]["field_verifications"]["outcomes"]["verification"]
    assert verdict["existence_status"] == "failed"
    assert verdict["overall_status"] != "verified"


def test_level2_background_attribution_is_not_current_experiment(tmp_path):
    verdict = _run(tmp_path, _candidate(attribution="background_citation"))["output"]["field_verifications"]["outcomes"]["verification"]
    assert verdict["attribution_status"] == "failed"
    assert verdict["overall_status"] == "unsupported"


@pytest.mark.parametrize("claim,evidence,expected", [
    ("Strain A increased titer", "Strain A did not increase titer", "conflicted"),
    ("Strain A increased titer", "Strain A decreased titer", "conflicted"),
    ("Titer was 10 g/L", "Titer was 9 g/L", "conflicted"),
    ("Dose was 10 mg/L", "Dose was 10 g/L", "conflicted"),
    ("Growth increased in M9 glucose", "Growth increased in LB glycerol", "unresolved"),
    ("Mutation caused higher titer", "Mutation was correlated with higher titer", "conflicted"),
])
def test_conservative_level3_adversarial(claim, evidence, expected):
    assert semantic_support(claim, evidence)[0] == expected


def test_verified_requires_all_three_dimensions(tmp_path):
    result = _run(tmp_path)
    verdict = result["output"]["field_verifications"]["outcomes"]["verification"]
    assert verdict["overall_status"] == "verified"
    assert verdict["existence_status"] == verdict["attribution_status"] == verdict["semantic_support_status"] == "passed"
    assert verdict["verified_evidence_ids"]


def test_ddr_missing_rationale_is_not_created_or_admitted(tmp_path):
    candidate = _candidate(); candidate["experimental_design_object"]["experiments"][0]["ddr_annotation"]["reason_nature_rationale"] = ""
    before = copy.deepcopy(candidate)
    output = _run(tmp_path, candidate)["output"]
    assert output["candidate_payload"] == before
    assert output["ddr_verifications"][0]["components"]["rationale"]["overall_status"] == "unresolved"
    assert output["knowledge_admission"]["admitted_ddr_candidates"] == []


def test_knowledge_gate_blocks_bare_skill07_and_missing_provenance():
    with pytest.raises(KnowledgeAdmissionBlocked): require_admissible_skill08({"fields": {}}, {})
    output = {"contract_version": "skill08_evidence_contract_v2", "knowledge_admission": {"status": "KNOWLEDGE_ADMISSION_PARTIAL"}}
    with pytest.raises(KnowledgeAdmissionBlocked): require_admissible_skill08(output, {})


def test_claim_level_admission_keeps_verified_field_despite_unrelated_unresolved():
    output = {"field_verifications": {
        "outcome": {"verification": {"overall_status": "verified"}},
        "replicates": {"verification": {"overall_status": "unresolved"}}}, "ddr_verifications": []}
    admission = evaluate_admission(output, {"skill08_artifact_id": "s8"})
    assert admission["status"] == "KNOWLEDGE_ADMISSION_PARTIAL"
    assert admission["admitted_field_claims"] == ["outcome"]


def test_workflow_keeps_failed_and_successful_papers_bound_to_own_document(tmp_path):
    engine = WorkflowEngine(DEFAULT_CONFIG)
    a, b = _document(tmp_path, "paper-a", "same keyword"), _document(tmp_path, "paper-b", "same keyword")
    results = [_result(_candidate(), status="needs_review", eligible=False), _result(_candidate())]
    artifacts = [None, {"artifact_id": "artifact:skill07:b"}]
    context = {}
    engine._update_context("skill07_experiment_extraction", results, context,
                           [{"clean_document_artifact": a}, {"clean_document_artifact": b}], artifacts)
    requests = engine._inputs("skill08_evidence_binding", {"literature_source": {}}, context, {})
    assert len(requests) == 2
    assert requests[0].get("handoff_error")
    assert requests[1]["handoff"]["paper_identity"]["paper_id"] == "paper-b"
    assert requests[1]["clean_document_artifact"]["document_metadata"]["paper_id"] == "paper-b"


def test_provenance_traces_skill08_to_skill07_document_and_paper(tmp_path):
    result = _run(tmp_path)
    p = result["provenance"]
    assert p["paper_id"] == "paper-a"
    assert p["document_artifact_id"] == "artifact:doc:paper-a"
    assert p["source_skill07_artifact_id"] == "artifact:skill07:1"
    assert result["output"]["knowledge_admission"]["source_skill08_artifact_id"] == p["skill08_artifact_id"]
