"""Unit tests for the 260718 设计文档 §7 metric computations. Design-project/
strategy/candidate/evaluation rows are constructed directly via the ORM
(rather than driven through the full diagnosis->handoff->strategy->portfolio
pipeline) so each metric's numerator/denominator arithmetic can be asserted
exactly, independent of the rule-based generator's keyword-matching output.
"""
from __future__ import annotations

import pytest

from harness import db
from harness.engineering_design.models import CandidateDesign, DesignEvaluation, EngineeringDesignProject, EngineeringStrategy
from harness.evaluation_metrics import aggregator
from harness.ids import new_id, now
from harness.projects import service as proj_svc


def _make_design_project(session, *, reference_ddr_ids=None, primary_metrics=None) -> EngineeringDesignProject:
    proj = proj_svc.create_project(
        session, name="Trp engineering", host_definition={"species": "E. coli", "strain": "K-12"},
        target_product="L-tryptophan", actor_id="pi",
    )
    dp = EngineeringDesignProject(
        design_project_id=new_id("DESIGNPROJ"), project_id=proj.project_id, diagnosis_session_id=new_id("DIAGSESS"),
        diagnosis_decision_id=new_id("DECISION"), diagnosis_version=1, primary_metrics=primary_metrics or [{"metric": "titer"}],
        status="portfolio_generated", created_by="pi", created_at=now(), updated_at=now(),
        reference_ddr_ids=reference_ddr_ids or [],
    )
    session.add(dp)
    session.flush()
    return dp


def _make_strategy(session, dp, *, strategy_class: str, evidence_links: list, excluded_strategy_reasons: list | None = None) -> EngineeringStrategy:
    s = EngineeringStrategy(
        strategy_id=new_id("STRAT"), design_project_id=dp.design_project_id, diagnosis_reference="HANDOFF-x",
        engineering_objective="improve titer", mechanism_target="test mechanism", strategy_class=strategy_class,
        evidence_links=evidence_links, excluded_strategy_reasons=excluded_strategy_reasons or [],
        created_by="pi", created_at=now(),
    )
    session.add(s)
    session.flush()
    return s


def _make_candidate(session, dp, *, genetic_modifications: list, portfolio_id: str | None = None, status: str = "proposed") -> CandidateDesign:
    c = CandidateDesign(
        design_id=new_id("CAND"), design_project_id=dp.design_project_id, lineage_id=new_id("LINEAGE"),
        genetic_modifications=genetic_modifications, portfolio_id=portfolio_id, status=status,
        source_diagnosis_version=1, proposed_by="pi", created_at=now(),
    )
    session.add(c)
    session.flush()
    return c


def _make_evaluation(session, candidate, *, recommendation: str, required_revisions: list | None = None, evaluator_findings: list | None = None) -> DesignEvaluation:
    e = DesignEvaluation(
        evaluation_id=new_id("EVAL"), design_id=candidate.design_id, design_version=candidate.design_version,
        recommendation=recommendation, required_revisions=required_revisions or [], evaluator_findings=evaluator_findings or [],
        created_at=now(),
    )
    session.add(e)
    session.flush()
    return e


# ---------------------------------------------------------------------------
# 接地率
# ---------------------------------------------------------------------------


def test_grounding_rate_counts_strategies_and_modifications():
    with db.session_scope() as s:
        dp = _make_design_project(s)
        _make_strategy(s, dp, strategy_class="feedback_relief", evidence_links=[{"source_type": "curated_knowledge"}])
        _make_strategy(s, dp, strategy_class="precursor_supply", evidence_links=[{"source_type": "diagnosis_hypothesis"}])
        _make_candidate(s, dp, genetic_modifications=[
            {"target_type": "gene", "target_identifier": "trpE", "evidence_links": [{"source_type": "experimental_evidence"}]},
            {"target_type": "gene", "target_identifier": "trpC", "evidence_links": []},
        ])

        result = aggregator.compute_grounding_rate(s, dp.design_project_id)
        assert result["applicable"] is True
        assert result["numerator"] == 2
        assert result["denominator"] == 4
        assert result["value"] == pytest.approx(0.5)


def test_grounding_rate_not_applicable_with_nothing_generated():
    with db.session_scope() as s:
        dp = _make_design_project(s)
        result = aggregator.compute_grounding_rate(s, dp.design_project_id)
        assert result["applicable"] is False
        assert result["value"] is None


# ---------------------------------------------------------------------------
# 覆盖完备
# ---------------------------------------------------------------------------


def test_coverage_completeness_counts_covered_and_excluded_classes():
    with db.session_scope() as s:
        dp = _make_design_project(s)
        excluded = [{"strategy_class": "dynamic_regulation", "reason": "not applicable to this diagnosis"}]
        _make_strategy(s, dp, strategy_class="feedback_relief", evidence_links=[], excluded_strategy_reasons=excluded)
        _make_strategy(s, dp, strategy_class="precursor_supply", evidence_links=[], excluded_strategy_reasons=excluded)

        result = aggregator.compute_coverage_completeness(s, dp.design_project_id)
        assert result["applicable"] is True
        assert result["numerator"] == 3  # feedback_relief + precursor_supply (covered) + dynamic_regulation (excluded)
        assert result["denominator"] == 9
        by_class = {r["strategy_class"]: r for r in result["coverage_by_class"]}
        assert by_class["feedback_relief"]["status"] == "covered"
        assert by_class["dynamic_regulation"]["status"] == "excluded"
        assert by_class["dynamic_regulation"]["reason"] == "not applicable to this diagnosis"
        assert by_class["cofactor_energy_balancing"]["status"] == "missing"


def test_coverage_completeness_zero_when_no_strategies_yet():
    with db.session_scope() as s:
        dp = _make_design_project(s)
        result = aggregator.compute_coverage_completeness(s, dp.design_project_id)
        assert result["applicable"] is True
        assert result["numerator"] == 0
        assert result["denominator"] == 9
        assert all(r["status"] == "missing" for r in result["coverage_by_class"])


# ---------------------------------------------------------------------------
# 筛选能力
# ---------------------------------------------------------------------------


def test_screening_ability_agreement_between_independent_risk_and_evaluator():
    with db.session_scope() as s:
        dp = _make_design_project(s)
        safe = _make_candidate(s, dp, portfolio_id="PORT-1", genetic_modifications=[
            {"target_type": "gene", "target_identifier": "trpE", "operation": "knockout", "evidence_links": [{"source_type": "experimental_evidence"}]},
        ])
        weak_caught = _make_candidate(s, dp, portfolio_id="PORT-1", genetic_modifications=[
            {"target_type": "gene", "target_identifier": "trpC", "operation": "knockout", "evidence_links": []},
        ])
        _make_evaluation(s, weak_caught, recommendation="revise", required_revisions=["attach evidence"])

        dup_a = _make_candidate(s, dp, portfolio_id="PORT-1", genetic_modifications=[
            {"target_type": "gene", "target_identifier": "aroG", "operation": "overexpression", "evidence_links": [{"source_type": "curated_knowledge"}]},
        ])
        dup_b = _make_candidate(s, dp, portfolio_id="PORT-1", genetic_modifications=[
            {"target_type": "gene", "target_identifier": "aroG", "operation": "overexpression", "evidence_links": [{"source_type": "curated_knowledge"}]},
        ])
        _make_evaluation(s, dup_a, recommendation="select")
        _make_evaluation(s, dup_b, recommendation="select")
        _make_evaluation(s, safe, recommendation="select")

        result = aggregator.compute_screening_ability(s, dp.design_project_id)
        assert result["applicable"] is True
        assert result["denominator"] == 3  # weak_caught + dup_a + dup_b are risk-flagged; safe is not
        assert result["numerator"] == 1  # only weak_caught was actually caught by the evaluator suite
        assert result["value"] == pytest.approx(1 / 3)


def test_screening_ability_not_applicable_with_no_candidates():
    with db.session_scope() as s:
        dp = _make_design_project(s)
        result = aggregator.compute_screening_ability(s, dp.design_project_id)
        assert result["applicable"] is False


# ---------------------------------------------------------------------------
# 合理新颖 / 复现率 (sanity check)
# ---------------------------------------------------------------------------


def test_novelty_and_reproduction_require_reference_ddr():
    with db.session_scope() as s:
        dp = _make_design_project(s)
        _make_candidate(s, dp, genetic_modifications=[
            {"target_type": "gene", "target_identifier": "trpE", "evidence_links": [{"source_type": "experimental_evidence"}]},
        ])
        novelty = aggregator.compute_reasoned_novelty(s, dp.design_project_id)
        reproduction = aggregator.compute_reproduction_rate(s, dp.design_project_id)
        assert novelty["applicable"] is False
        assert reproduction["applicable"] is False


def test_novelty_and_reproduction_against_ddr_001():
    with db.session_scope() as s:
        dp = _make_design_project(s, reference_ddr_ids=["DDR-001"])
        # "ptsG, pykF (候选)" is a real target string in DDR-001's decision_chain -
        # reusing it verbatim forces a deterministic reference-set intersection.
        _make_candidate(s, dp, genetic_modifications=[
            {"target_type": "gene", "target_identifier": "trpE", "evidence_links": [{"source_type": "experimental_evidence"}]},
            {"target_type": "gene", "target_identifier": "ptsG, pykF (候选)", "evidence_links": []},
        ])

        novelty = aggregator.compute_reasoned_novelty(s, dp.design_project_id)
        assert novelty["applicable"] is True
        assert novelty["denominator"] == 2  # trpE + "ptsG, pykF (候选)"
        assert novelty["numerator"] == 1  # only trpE is both absent from the reference and grounded
        assert novelty["novel_grounded_genes"] == ["trpe"]

        reproduction = aggregator.compute_reproduction_rate(s, dp.design_project_id)
        assert reproduction["applicable"] is True
        assert reproduction["numerator"] == 1  # "ptsg, pykf (候选)" matches a reference target
        assert reproduction["denominator"] == 2  # DDR-001 has two distinct gene-target strings


# ---------------------------------------------------------------------------
# Bundle / error handling
# ---------------------------------------------------------------------------


def test_compute_all_metrics_shape():
    with db.session_scope() as s:
        dp = _make_design_project(s)
        result = aggregator.compute_all_metrics(s, dp.design_project_id)
        assert set(result["process"]) == {"grounding_rate", "coverage_completeness"}
        assert set(result["capability"]) == {"screening_ability", "reasoned_novelty"}
        assert set(result["sanity_check"]) == {"reproduction_rate"}


def test_unknown_design_project_raises():
    with db.session_scope() as s:
        with pytest.raises(ValueError):
            aggregator.compute_grounding_rate(s, "no-such-project")
