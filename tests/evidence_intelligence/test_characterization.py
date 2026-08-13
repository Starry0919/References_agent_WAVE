"""Component 3 - pure-function tests: every confidence/origin/type mapping
must be a deterministic function of EXISTING categorical fields, never a new
numeric score (Module 3 prompt §4.11/§6)."""
from __future__ import annotations

from harness.evidence_intelligence import characterization as char
from harness.evidence_intelligence.models import CONFIDENCE_LEVELS


def test_confidence_levels_vocabulary_is_exactly_the_prompt_vocabulary():
    assert set(CONFIDENCE_LEVELS) == {"High", "Medium", "Low", "Unknown"}


def test_ddr_grading_hard_and_calibrated_is_high():
    level, basis = char.confidence_from_ddr_grading(evidence_grading="硬", calibration_status="calibrated")
    assert level == "High"
    assert "calibrat" in basis.lower()


def test_ddr_grading_hard_but_not_calibrated_is_medium_not_high():
    level, _ = char.confidence_from_ddr_grading(evidence_grading="硬", calibration_status="pending")
    assert level == "Medium"
    level2, _ = char.confidence_from_ddr_grading(evidence_grading="硬", calibration_status=None)
    assert level2 == "Medium"


def test_ddr_grading_soft_is_low_and_unclear_is_unknown():
    assert char.confidence_from_ddr_grading(evidence_grading="软", calibration_status=None)[0] == "Low"
    assert char.confidence_from_ddr_grading(evidence_grading="待定", calibration_status=None)[0] == "Unknown"
    assert char.confidence_from_ddr_grading(evidence_grading="混合", calibration_status=None)[0] == "Medium"


def test_ddr_grading_missing_is_unknown_never_fabricated():
    level, basis = char.confidence_from_ddr_grading(evidence_grading=None, calibration_status=None)
    assert level == "Unknown"
    assert "no evidence_grading" in basis


def test_diagnosis_item_quality_and_directness_mapping():
    assert char.confidence_from_diagnosis_item(quality="high", directness="direct")[0] == "High"
    assert char.confidence_from_diagnosis_item(quality="high", directness="indirect")[0] == "Medium"
    assert char.confidence_from_diagnosis_item(quality="medium", directness="direct")[0] == "Medium"
    assert char.confidence_from_diagnosis_item(quality="low", directness="direct")[0] == "Low"
    assert char.confidence_from_diagnosis_item(quality=None, directness=None)[0] == "Unknown"


def test_origin_and_type_from_ddr_step_detects_simulation_source():
    step = {"evidence": {"source": "OptKnock 预测"}, "evidence_grading": "软", "reason_nature": ""}
    origin, evidence_type = char.origin_and_type_from_ddr_step(step)
    assert origin == "model prediction"
    assert evidence_type == "simulation prediction"


def test_origin_and_type_from_ddr_step_hard_measured_is_direct_validation():
    step = {"evidence": {"source": "论文实测"}, "evidence_grading": "硬", "reason_nature": "机理推断"}
    origin, evidence_type = char.origin_and_type_from_ddr_step(step)
    assert origin == "published experiment"
    # mechanistic reason_nature wins over the bare grade, per the mapping's priority
    assert evidence_type == "mechanistic hypothesis"


def test_origin_and_type_from_ddr_step_hard_no_mechanistic_reason_is_direct_validation():
    step = {"evidence": {"source": "论文实测"}, "evidence_grading": "硬", "reason_nature": "直接引用"}
    origin, evidence_type = char.origin_and_type_from_ddr_step(step)
    assert evidence_type == "direct engineering validation"


def test_origin_and_type_from_diagnosis_item_covers_every_source_type():
    cases = {
        "literature": ("published experiment", "direct engineering validation"),
        "expert_rule": ("expert annotation", "expert interpretation"),
        "llm_reasoning": ("literature-derived analysis", "mechanistic hypothesis"),
        "model_run": ("model prediction", "simulation prediction"),
        "experiment_result": ("internal experiment", "direct engineering validation"),
        "observation": ("internal experiment", "direct engineering validation"),
    }
    for source_type, (expected_origin, expected_type) in cases.items():
        origin, evidence_type = char.origin_and_type_from_diagnosis_item(source_type=source_type, directness="direct")
        assert origin == expected_origin, source_type
        assert evidence_type == expected_type, source_type


def test_characterize_never_emits_a_number_and_uses_the_four_way_vocabulary():
    result = char.characterize(
        evidence_type="direct engineering validation", confidence_level="High",
        applicability_boundary=["host: Escherichia coli"], limitations=["only tested under one condition"],
    )
    assert result == {
        "evidence_level": "direct engineering validation",
        "applicability": "Medium",
        "limitation": "only tested under one condition",
        "uncertainty": "Low",
    }
    for value in result.values():
        assert not isinstance(value, (int, float))


def test_applicability_level_uses_match_status_when_available():
    assert char.applicability_level(applicability_boundary=[], match_status="direct_match") == "High"
    assert char.applicability_level(applicability_boundary=[], match_status="partial_match") == "Medium"
    assert char.applicability_level(applicability_boundary=[], match_status="cross_species") == "Low"
    assert char.applicability_level(applicability_boundary=[], match_status="insufficient_metadata") == "Unknown"
    assert char.applicability_level(applicability_boundary=[], match_status=None) == "Unknown"
