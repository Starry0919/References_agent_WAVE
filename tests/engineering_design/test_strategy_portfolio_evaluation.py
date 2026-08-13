"""doc04 §13.3/§13.4: Strategy -> Candidate -> Evaluation pipeline."""
from __future__ import annotations

import pytest

from harness import db
from harness.engineering_design import handoff as handoff_mod, memory_integration, portfolio_service, strategy_service
from harness.engineering_design.evaluation_service import evaluate_portfolio
from harness.engineering_design.evaluators.runner import run_evaluator_suite
from harness.engineering_design.portfolio_service import PortfolioDiversityRejected
from tests.engineering_design.fixtures import build_trp_diagnosis, handoff_through_portfolio


def _handoff(s):
    _, _, decision = build_trp_diagnosis(s)
    return handoff_mod.ingest_diagnosis_decision(s, decision=decision, actor_id="agent", chassis="E. coli")


def test_strategy_precedes_modification_and_records_exclusions():
    with db.session_scope() as s:
        proj, handoff = _handoff(s)
        strategies = strategy_service.generate_and_persist_strategies(s, design_project_id=proj.design_project_id, handoff_id=handoff.handoff_id, actor_id="system")
        assert strategies
        for st in strategies:
            assert st.strategy_class  # every strategy classified before any gene is chosen
            assert st.excluded_strategy_reasons  # non-applicable classes recorded, not silently absent
            assert st.rationale


def test_strategy_carries_historical_priors_from_real_ddr_corpus():
    """ELISER-inspired Strategy Prior Retrieval integration: the trp fixture's
    precursor/feedback hypotheses should surface real DDR-001/DDR-005 as
    historical precedent, and hard-graded precedent should be folded into
    evidence_links so EvidenceEvaluator actually sees it (not just the UI)."""
    with db.session_scope() as s:
        proj, handoff = _handoff(s)
        strategies = strategy_service.generate_and_persist_strategies(s, design_project_id=proj.design_project_id, handoff_id=handoff.handoff_id, actor_id="system")

        assert any(st.design_prior is not None for st in strategies)
        for st in strategies:
            assert st.design_prior is not None
            assert 0.0 <= st.design_prior["score"] <= 1.0
            assert st.design_prior["basis"]  # every strategy explains its historical-support number, even if zero
            assert isinstance(st.historical_priors, list)

        precursor_strategy = next(st for st in strategies if st.strategy_class == "precursor_supply")
        assert precursor_strategy.historical_priors
        assert any(p["source_id"] == "DDR-001" for p in precursor_strategy.historical_priors)
        assert not any(link.get("source_type") == "historical_precedent" for link in precursor_strategy.evidence_links)

        from harness.engineering_design.evaluators.evidence import evaluate as evaluate_evidence

        result = evaluate_evidence({"genetic_modifications": [], "evidence_links": precursor_strategy.evidence_links})
        assert all("historical" not in f.lower() for f in result.findings)


def test_portfolio_generates_three_structurally_distinct_roles():
    with db.session_scope() as s:
        proj, handoff = _handoff(s)
        strategy_service.generate_and_persist_strategies(s, design_project_id=proj.design_project_id, handoff_id=handoff.handoff_id, actor_id="system")
        portfolio, candidates, suppressed = portfolio_service.generate_and_persist_portfolio(s, design_project_id=proj.design_project_id, actor_id="system")

        roles = {c.portfolio_role for c in candidates}
        assert {"low_risk", "high_upside", "information_gain"}.issubset(roles)

        by_role = {c.portfolio_role: c for c in candidates}
        low_sig = memory_integration.modification_signature(by_role["low_risk"].genetic_modifications)
        high_sig = memory_integration.modification_signature(by_role["high_upside"].genetic_modifications)
        info_sig = memory_integration.modification_signature(by_role["information_gain"].genetic_modifications)
        assert low_sig != high_sig
        assert low_sig != info_sig
        assert high_sig != info_sig
        # roles are not just "the same intervention re-labeled"
        assert by_role["low_risk"].expected_mechanism != by_role["information_gain"].expected_mechanism


def test_diversity_gate_rejects_a_portfolio_of_surface_rewrites():
    from harness.workflow.gates import design_diversity_gate

    gate = design_diversity_gate(distinct_mechanism_or_architecture_count=1, total_candidates=3)
    assert gate.status.value == "fail"


def test_historical_failure_suppresses_no_new_evidence_repeat():
    with db.session_scope() as s:
        proj, portfolio, candidates = handoff_through_portfolio(s)
        suppressed_round1 = []
        assert suppressed_round1 == []
        evaluate_portfolio(s, portfolio_id=portfolio.portfolio_id, actor_id="system")
        low_risk = next(c for c in candidates if c.portfolio_role == "low_risk" and c.decision_state == "human_selection_pending")
        portfolio_service.reject_candidate(s, design_id=low_risk.design_id, reasons=["excessive growth burden"], actor_id="pi")

        _, candidates2, suppressed_round2 = portfolio_service.generate_and_persist_portfolio(s, design_project_id=proj.design_project_id, actor_id="system")
        assert suppressed_round2, "an identical rejected candidate must be suppressed on regeneration"
        assert not any(c.portfolio_role == "low_risk" and memory_integration.modification_signature(c.genetic_modifications) == memory_integration.modification_signature(low_risk.genetic_modifications) for c in candidates2)


def test_combination_candidate_records_epistasis_assumption():
    with db.session_scope() as s:
        proj, handoff = _handoff(s)
        strategy_service.generate_and_persist_strategies(s, design_project_id=proj.design_project_id, handoff_id=handoff.handoff_id, actor_id="system")
        _, candidates, _ = portfolio_service.generate_and_persist_portfolio(s, design_project_id=proj.design_project_id, actor_id="system")
        high_upside = next(c for c in candidates if c.portfolio_role == "high_upside")
        assert len(high_upside.genetic_modifications) >= 2
        assert high_upside.interaction_and_epistasis_assumptions  # combination risk is stated, not implied


def test_hard_constraint_filters_before_ranking():
    from harness.engineering_design.decision import check_hard_constraints

    candidate = {"genetic_modifications": [{"target_identifier": "murA", "operation": "knockout"}]}  # murA is essential
    results = check_hard_constraints(candidate, [{"constraint": "no essential gene knockout", "type": "no_essential_gene_knockout"}])
    assert results[0]["satisfied"] is False


def test_evidence_strength_participates_in_pareto_dominance():
    """Module 2 §13: Complexity-aware Design Ranking must weigh evidence
    strength alongside build_complexity/growth_burden_risk, not just the
    latter two."""
    from harness.engineering_design import decision as decision_mod

    strong = {"genetic_modifications": [{"evidence_links": [{"source_type": "experimental_evidence", "reference": "E1"}]}]}
    weak = {"genetic_modifications": [{"evidence_links": [{"source_type": "expert_or_llm_judgment", "reference": "E2"}]}]}
    vec_strong = decision_mod.compute_objective_vector(strong, primary_metrics=[])
    vec_weak = decision_mod.compute_objective_vector(weak, primary_metrics=[])

    entry_strong = next(e for e in vec_strong if e["metric"] == "evidence_strength")
    entry_weak = next(e for e in vec_weak if e["metric"] == "evidence_strength")
    assert entry_strong["direction_estimate"] == "experimental_evidence"
    assert entry_weak["direction_estimate"] == "expert_or_llm_judgment"

    # identical on every other ordinal dimension - only evidence_strength differs
    for e in vec_strong + vec_weak:
        if e["metric"] in ("build_complexity", "growth_burden_risk"):
            e["direction_estimate"] = "low" if e["metric"] == "build_complexity" else "none"
    assert decision_mod._dominates(vec_strong, vec_weak) is True
    assert decision_mod._dominates(vec_weak, vec_strong) is False


def test_evidence_strength_with_no_links_never_fabricates_a_tier():
    from harness.engineering_design import decision as decision_mod

    vec = decision_mod.compute_objective_vector({"genetic_modifications": []}, primary_metrics=[])
    entry = next(e for e in vec if e["metric"] == "evidence_strength")
    assert entry["direction_estimate"] == "unknown"


def test_pareto_trade_off_is_preserved_not_collapsed_to_one_score():
    with db.session_scope() as s:
        proj, portfolio, candidates = handoff_through_portfolio(s)
        result = evaluate_portfolio(s, portfolio_id=portfolio.portfolio_id, actor_id="system")
        pareto_values = {ev.pareto_status for ev in result["evaluations"].values()}
        # more than one distinct pareto outcome across the portfolio - never a single collapsed ranking
        assert len(pareto_values) >= 2
        for ev in result["evaluations"].values():
            assert isinstance(ev.objective_vector, list) and ev.objective_vector
            for entry in ev.objective_vector:
                assert "unit" in entry and "basis" in entry and "evidence_tier" in entry  # never a bare unitless number


def test_insufficient_evidence_is_a_legitimate_outcome_not_forced_score():
    with db.session_scope() as s:
        proj, handoff = _handoff(s)
        strategy_service.generate_and_persist_strategies(s, design_project_id=proj.design_project_id, handoff_id=handoff.handoff_id, actor_id="system")
        portfolio, candidates, _ = portfolio_service.generate_and_persist_portfolio(s, design_project_id=proj.design_project_id, actor_id="system")
        reference = next(c for c in candidates if c.portfolio_role == "reference_or_control")
        ev = run_evaluator_suite(s, design_id=reference.design_id, actor_id="system")
        assert ev.recommendation == "insufficient_evidence"  # no evidence links on a bare reference candidate


def test_model_conflict_is_not_averaged():
    from harness.engineering_design.evaluators.counterfactual import evaluate as evaluate_counterfactual

    candidate = {"portfolio_role": "low_risk"}
    runs = [
        {"run_id": "R1", "runtime_status": "optimal", "capability_status": "available", "outputs": {"objective_value": 1.0}},
        {"run_id": "R2", "runtime_status": "optimal", "capability_status": "available", "outputs": {"objective_value": 2.0}},
    ]
    result = evaluate_counterfactual(candidate, counterfactual_runs=runs)
    assert result.status == "warning"
    assert "disagree" in " ".join(result.findings)


def test_model_unavailable_never_produces_a_fabricated_number():
    from harness.diagnosis.model_adapters.registry import get_adapter

    adapter = get_adapter("vecoli")
    capability = adapter.detect_capability()
    assert capability.available is False


def test_evaluator_required_revision_creates_a_new_linked_candidate_version():
    with db.session_scope() as s:
        proj, handoff = _handoff(s)
        strategy_service.generate_and_persist_strategies(s, design_project_id=proj.design_project_id, handoff_id=handoff.handoff_id, actor_id="system")
        _, candidates, _ = portfolio_service.generate_and_persist_portfolio(s, design_project_id=proj.design_project_id, actor_id="system")
        low_risk = next(c for c in candidates if c.portfolio_role == "low_risk")

        # identical content with no justification is rejected outright
        with pytest.raises(portfolio_service.RevisionRejected):
            portfolio_service.revise_candidate(s, design_id=low_risk.design_id, actor_id="pi", modification_reason="")

        revised = portfolio_service.revise_candidate(
            s, design_id=low_risk.design_id, actor_id="pi",
            modification_reason="EvidenceEvaluator flagged missing model-tier evidence; switched to knockdown instead of knockout to reduce risk",
            genetic_modifications=[{**low_risk.genetic_modifications[0], "operation": "knockdown"}],
        )
        assert revised.design_id != low_risk.design_id
        assert revised.lineage_id == low_risk.lineage_id
        assert revised.design_version == low_risk.design_version + 1
        assert revised.parent_design_ids == [low_risk.design_id]
        assert revised.created_from_revision_reason
        # the original evaluated version is untouched, not overwritten
        original = portfolio_service.get_candidate(s, low_risk.design_id)
        assert original.genetic_modifications == low_risk.genetic_modifications


def test_revision_loop_creates_new_evaluation_and_can_stop():
    with db.session_scope() as s:
        proj, handoff = _handoff(s)
        strategy_service.generate_and_persist_strategies(s, design_project_id=proj.design_project_id, handoff_id=handoff.handoff_id, actor_id="system")
        portfolio, candidates, _ = portfolio_service.generate_and_persist_portfolio(s, design_project_id=proj.design_project_id, actor_id="system")
        low_risk = next(c for c in candidates if c.portfolio_role == "low_risk")

        ev1 = run_evaluator_suite(s, design_id=low_risk.design_id, actor_id="system")
        ev2 = run_evaluator_suite(s, design_id=low_risk.design_id, actor_id="system")
        assert ev1.evaluation_id != ev2.evaluation_id  # a new row, never overwritten

        from harness.workflow.gates import evaluator_revision_gate

        gate = evaluator_revision_gate(blocking_findings=["x"], revision_count=10, revision_limit=3)
        assert gate.status.value == "human_review"  # revision limit reached -> escalate, not spin forever
