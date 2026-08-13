"""Module 2 (Engineering Decision Intelligence Layer) §11: `ConfidenceEvaluator`
- an explicit, explained aggregate confidence dimension, never a bare score.
"""
from __future__ import annotations

from harness.engineering_design.evaluators import confidence


def test_no_evidence_no_model_no_mechanism_is_insufficient_evidence():
    candidate = {"genetic_modifications": [], "evidence_links": [], "portfolio_role": "low_risk"}
    result = confidence.evaluate(candidate, mechanism_status="fail", counterfactual_runs=[])
    assert result.status == "insufficient_evidence"
    assert result.blocking is True
    assert len(result.findings) == 3  # evidence / model / mechanism, each explained


def test_reference_control_insufficient_evidence_is_never_blocking():
    candidate = {"genetic_modifications": [], "evidence_links": [], "portfolio_role": "reference_or_control"}
    result = confidence.evaluate(candidate, mechanism_status="fail", counterfactual_runs=[])
    assert result.status == "insufficient_evidence"
    assert result.blocking is False


def test_strong_evidence_and_clean_mechanism_is_pass():
    candidate = {
        "genetic_modifications": [{"evidence_links": [{"source_type": "experimental_evidence", "reference": "EXP-1"}]}],
        "evidence_links": [], "portfolio_role": "low_risk",
    }
    result = confidence.evaluate(candidate, mechanism_status="pass", counterfactual_runs=[])
    assert result.status == "pass"
    assert not result.required_revisions


def test_only_one_strong_component_is_warning_not_pass():
    candidate = {
        "genetic_modifications": [{"evidence_links": [{"source_type": "expert_or_llm_judgment", "reference": "X"}]}],
        "evidence_links": [], "portfolio_role": "low_risk",
    }
    result = confidence.evaluate(candidate, mechanism_status="warning", counterfactual_runs=[])
    assert result.status == "warning"
    assert result.required_revisions


def test_never_returns_a_bare_numeric_score():
    """The contract is EvaluatorResult (status + explained findings) - there
    is no numeric confidence field anywhere in the return shape."""
    candidate = {"genetic_modifications": [], "evidence_links": [], "portfolio_role": "low_risk"}
    result = confidence.evaluate(candidate, mechanism_status="pass", counterfactual_runs=[])
    assert not hasattr(result, "score")
    assert not hasattr(result, "confidence")
    assert isinstance(result.status, str)
