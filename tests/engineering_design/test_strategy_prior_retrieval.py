"""ELISER-inspired Strategy Prior Retrieval (harness/engineering_design/
strategy_prior_retrieval.py): pure-function unit tests, no DB needed - same
spirit as the existing `strategy_generator.py` (no dedicated test file of
its own; covered indirectly via `test_strategy_portfolio_evaluation.py`),
except this module's corpus-matching logic is worth testing directly since
it reads real `knowledge/` JSON.
"""
from __future__ import annotations

from harness.engineering_design import strategy_service
from harness.engineering_design.strategy_prior_retrieval import (
    PriorSourceRef,
    compute_design_prior,
    find_prior_sources,
    is_strong_source,
    to_evidence_link,
)


def test_ddr_category_crosswalk_is_conservative_and_covers_all_strategy_classes_with_a_ddr_analogue():
    from harness.engineering_design.models import STRATEGY_CLASSES
    from harness.engineering_design.strategy_prior_retrieval import _STRATEGY_CLASS_TO_DDR_CATEGORIES

    # Every mapped strategy_class must be a real value from STRATEGY_CLASSES -
    # a typo here would silently mean a DDR strategy_categories match never
    # fires for that class.
    for strategy_class in _STRATEGY_CLASS_TO_DDR_CATEGORIES:
        assert strategy_class in STRATEGY_CLASSES
    # Deliberately not every class has a DDR-side analogue (process/resource/
    # diagnostic-probe classes are outside the DDR strategy_categories
    # vocabulary's scope) - the crosswalk must not force one.
    assert "process_condition_engineering" not in _STRATEGY_CLASS_TO_DDR_CATEGORIES
    assert "diagnostic_measurement_probe" not in _STRATEGY_CLASS_TO_DDR_CATEGORIES


def test_find_prior_sources_matches_real_precursor_supply_ddr():
    ddr_records = strategy_service.load_ddr_records()
    rules = strategy_service.load_biological_rules()
    assert ddr_records and rules  # the corpus itself must be non-empty for this test to mean anything

    sources = find_prior_sources(
        "precursor_supply",
        "Precursor (PEP/E4P) supply limitation from imbalanced central carbon flux constrains L-tryptophan titer",
        ddr_records, rules,
    )
    assert sources, "expected at least one real historical source for precursor_supply"
    assert any(s.source_id == "DDR-001" for s in sources), "DDR-001 (Xiong 2021, L-tryptophan precursor engineering) should match"
    for s in sources:
        assert s.source_id and s.basis_quote  # never a source without a traceable id/quote


def test_find_prior_sources_matches_real_feedback_relief_ddr():
    ddr_records = strategy_service.load_ddr_records()
    rules = strategy_service.load_biological_rules()

    sources = find_prior_sources(
        "feedback_relief",
        "Feedback inhibition of anthranilate synthase (TrpE) and attenuation of the trp operon independently caps flux",
        ddr_records, rules,
    )
    assert any(s.source_id == "DDR-005" for s in sources), "DDR-005 (Chen & Zeng, tryptophan feedback relief) should match"


def test_find_prior_sources_is_honest_about_no_corpus_support():
    sources = find_prior_sources("dynamic_regulation", "totally unrelated free text about spreadsheets", [], [])
    assert sources == []


def test_compute_design_prior_never_fabricates_on_empty_corpus():
    prior = compute_design_prior([])
    assert prior.score == 0.0
    assert prior.historical_frequency == 0
    assert prior.basis  # absence is explained, never silently omitted
    assert prior.supporting_sources == []


def test_compute_design_prior_rewards_frequency_and_evidence_quality():
    weak = [PriorSourceRef(
        source_type="ddr_decision", source_id="DDR-X", evidence_grading="软",
        mechanistic_weight=0.25, matched_via="keyword", basis_quote="weak precedent",
    )]
    strong = [
        PriorSourceRef(
            source_type="ddr_decision", source_id=f"DDR-{i}", evidence_grading="硬",
            mechanistic_weight=1.0, matched_via="strategy_category", basis_quote="strong precedent",
        )
        for i in range(3)
    ]
    weak_prior = compute_design_prior(weak)
    strong_prior = compute_design_prior(strong)
    assert strong_prior.score > weak_prior.score
    assert strong_prior.historical_frequency == 3


def test_compute_design_prior_applicability_uses_host_context_when_supplied():
    matching_host = [PriorSourceRef(
        source_type="ddr_decision", source_id="DDR-A", evidence_grading="硬", mechanistic_weight=1.0,
        matched_via="keyword", basis_quote="q", host="E. coli", product="L-tryptophan",
    )]
    mismatched_host = [PriorSourceRef(
        source_type="ddr_decision", source_id="DDR-B", evidence_grading="硬", mechanistic_weight=1.0,
        matched_via="keyword", basis_quote="q", host="S. cerevisiae", product="ethanol",
    )]
    p_match = compute_design_prior(matching_host, host="E. coli", product="L-tryptophan")
    p_mismatch = compute_design_prior(mismatched_host, host="E. coli", product="L-tryptophan")
    assert p_match.score > p_mismatch.score


def test_is_strong_source_only_true_for_hard_grading():
    hard = PriorSourceRef(source_type="ddr_decision", source_id="D", evidence_grading="硬", mechanistic_weight=1.0, matched_via="keyword", basis_quote="q")
    soft = PriorSourceRef(source_type="ddr_decision", source_id="D", evidence_grading="软", mechanistic_weight=1.0, matched_via="keyword", basis_quote="q")
    assert is_strong_source(hard) is True
    assert is_strong_source(soft) is False


def test_to_evidence_link_shape():
    ref = PriorSourceRef(source_type="distilled_rule", source_id="RULE-004", evidence_grading="硬", mechanistic_weight=1.0, matched_via="keyword", basis_quote="precursor diagnosis rule")
    link = to_evidence_link(ref)
    assert link == {"source_type": "historical_precedent", "reference": "RULE-004", "detail": "precursor diagnosis rule"}


def test_migration_0015_is_idempotent_and_adds_the_new_columns():
    from harness.bootstrap import bootstrap_schema
    from sqlalchemy import text

    from harness import db

    applied_again = bootstrap_schema()
    assert "0015_engineering_strategy_historical_priors" not in applied_again  # already applied by the autouse fixture

    with db.session_scope() as s:
        columns = {row[1] for row in s.execute(text("PRAGMA table_info(design_strategies)")).fetchall()}
    assert {"historical_priors", "design_prior"}.issubset(columns)
