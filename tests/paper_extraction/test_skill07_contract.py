import copy

import harness.paper_extraction.opus_extractor as module
from harness.paper_extraction import ddr_converter
from harness.paper_extraction.contracts import load_validation_rules


def _base_output():
    fields = {
        name: {
            "value": None,
            "status": "unknown",
            "applicability_status": "uncertain",
            "confidence": 0.0,
            "extraction_method": "not_applicable",
            "evidence_ids": [],
            "notes": "Not reported in the available document.",
            "inference": None,
        }
        for name in module._core_fields()
    }
    return {
        "contract_version": "skill07_semantic_contract_v1",
        "fields": fields,
        "experimental_design_object": {"experiments": []},
        "field_metadata": {
            name: {"source_locations": [], "evidence_role": "candidate"}
            for name in fields
        },
        "extensions": {
            "article_type_gate": {
                "article_type": "primary_research",
                "contains_original_experiment": True,
                "classification_evidence": ["p1"],
            },
            "document_coverage": {"available_sections": []},
            "paper_target_strains": [],
            "user_target_system": None,
        },
        "conflicts": [],
    }


def _document():
    return {"paragraphs": [{"paragraph_id": "p1", "text": "Primary research."}]}


def _decision_annotation(**overrides):
    value = {
        "decision_type": "engineering_decision",
        "decision_type_rationale": "The current study selected an intervention.",
        "decision_gates": {
            "q1_intervention": True,
            "q2_current_study": True,
            "q3_decisionhood": True,
        },
        "design_action": "M1",
        "trigger_observation": "p1",
        "reason_nature": "mechanistic_inference",
        "generalizable_rule": None,
    }
    value.update(overrides)
    return value


def test_not_applicable_is_separate_from_unknown_knowledge_state():
    output = _base_output()
    output["fields"]["hypothesis"]["applicability_status"] = "not_applicable"
    output["fields"]["hypothesis"]["notes"] = "Not applicable to this article type."

    checks = module.validate_skill07_output(output, _document())

    assert module._checks_pass(checks)
    assert output["fields"]["hypothesis"]["status"] == "unknown"
    assert output["fields"]["hypothesis"]["applicability_status"] == "not_applicable"
    assert output["fields"]["objective"]["applicability_status"] == "uncertain"


def test_reason_nature_machine_vocabulary_is_complete_and_accepts_legacy_aliases():
    rules = load_validation_rules(module.VALIDATION_RULES_PATH)
    reason = rules["ddr_validation"]["reason_nature"]
    assert set(reason["canonical_values"]) == {
        "mechanistic_inference",
        "literature_analogy",
        "resource_available",
        "screening_derived",
        "evolution_derived",
        "rationale_not_reported",
        "post_hoc_rationalization_uncertain",
    }
    assert reason["legacy_aliases"]["机理推断"] == "mechanistic_inference"
    assert reason["legacy_aliases"]["事后合理化存疑"] == "post_hoc_rationalization_uncertain"
    assert ddr_converter._VALID_REASON_NATURES == frozenset(
        [*reason["canonical_values"], *reason["legacy_aliases"]]
    )
    assert ddr_converter._canonical_reason("机理推断") == "mechanistic_inference"

    for index, value in enumerate(reason["canonical_values"]):
        output = _base_output()
        output["experimental_design_object"]["experiments"] = [{
            "experiment_id": f"e{index}",
            "ddr_annotation": _decision_annotation(reason_nature=value),
        }]
        assert module._checks_pass(module.validate_skill07_output(output, _document()))


def test_rule_candidate_without_tested_and_excluded_scope_fails():
    output = _base_output()
    output["experimental_design_object"]["experiments"] = [{
        "experiment_id": "e1",
        "ddr_annotation": _decision_annotation(
            generalizable_rule="Under these conditions, intervention X can improve Y."
        ),
    }]

    checks = module.validate_skill07_output(output, _document())
    ddr = next(check for check in checks if check["name"] == "ddr_integrity")

    assert ddr["passed"] is False
    assert any("tested scope" in detail for detail in ddr["details"])
    assert any("excluded scope" in detail for detail in ddr["details"])


def test_skill07_candidate_evidence_cannot_be_marked_verified():
    output = _base_output()
    output["experimental_design_object"]["evidence_claim"] = {
        "evidence_role": "verified",
        "verified_evidence_ids": ["p1"],
    }

    checks = module.validate_skill07_output(output, _document())
    evidence = next(check for check in checks if check["name"] == "evidence_role_integrity")

    assert evidence["passed"] is False
    assert any("Skill07 cannot emit verified" in detail for detail in evidence["details"])
    assert any("belongs to Skill08" in detail for detail in evidence["details"])


def test_provenance_carries_semantic_contract_and_validation_rules_versions():
    provenance = module._version_provenance()

    assert provenance["semantic_contract_version"] == "skill07_semantic_contract_v1"
    assert provenance["validation_rules_version"] == "skill07_validation_rules_v1"
    assert len(provenance["semantic_contract_sha256"]) == 64
    assert len(provenance["validation_rules_sha256"]) == 64


def test_self_check_reports_counts_and_critical_failures_without_score():
    self_check = module._self_check([
        module._check("top_level_and_field_schema", True),
        module._check("ddr_integrity", False, details=["bad rule"]),
        module._check("advisory", False, required=False),
    ])

    assert self_check["required_checks"] == 2
    assert self_check["passed"] == 1
    assert self_check["failed"] == 1
    assert self_check["critical_failures"] == [{"name": "ddr_integrity", "details": ["bad rule"]}]
    assert "score" not in self_check


def test_legacy_output_is_migrated_additively_without_claiming_not_applicable():
    legacy = _base_output()
    legacy.pop("contract_version")
    for field in legacy["fields"].values():
        field.pop("applicability_status")
    for meta in legacy["field_metadata"].values():
        meta.pop("evidence_role")
    legacy["fields"]["hypothesis"]["notes"] = "not_applicable for this review"

    normalized, actions = module._safe_normalize_skill07_output(copy.deepcopy(legacy))

    assert normalized["contract_version"] == "skill07_semantic_contract_v1"
    assert normalized["fields"]["objective"]["applicability_status"] == "uncertain"
    assert normalized["fields"]["hypothesis"]["applicability_status"] == "not_applicable"
    assert all(meta["evidence_role"] == "candidate" for meta in normalized["field_metadata"].values())
    assert actions
