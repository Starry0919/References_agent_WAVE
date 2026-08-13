"""Smoke test: the full happy-path pipeline runs end to end without error.
Detailed assertions live in the other test modules in this package."""
from __future__ import annotations

from harness import db
from harness.engineering_design import (
    build_test_planner,
    governance_service,
    handoff as handoff_mod,
    outcome_service,
    portfolio_service,
    project_service,
    strategy_service,
)
from harness.engineering_design.evaluation_service import evaluate_portfolio
from tests.engineering_design.fixtures import build_trp_diagnosis


def test_smoke_full_pipeline():
    with db.session_scope() as s:
        proj, sess, decision = build_trp_diagnosis(s)
        design_proj, handoff = handoff_mod.ingest_diagnosis_decision(
            s, decision=decision, actor_id="agent", chassis="E. coli", chassis_version_or_genotype="K-12 MG1655 wild-type",
        )
        assert design_proj.status == "objective_draft"
        assert handoff.approved_for_design is True

        design_proj = project_service.set_objectives(
            s, design_project_id=design_proj.design_project_id,
            primary_metrics=[{"metric": "titer", "unit": "g/L"}], secondary_metrics=[],
            hard_constraints=[{"constraint": "no essential gene knockout", "type": "no_essential_gene_knockout"}],
            preferences_or_weights=[], available_resources={"materials": ["pKD46", "pCP20"], "instruments": ["HPLC"]},
            expected_version=design_proj.version, actor_id="pi",
        )

        from harness.engineering_design.loop import EngineeringDesignLoopController
        from harness.workflow.gates import design_objective_gate

        gate = design_objective_gate(has_primary_metrics=True, has_hard_constraints_declared=True)
        design_proj = EngineeringDesignLoopController().confirm_objective(s, design_proj, actor_id="pi", objective_gate_result=gate)
        assert design_proj.status == "strategy_generated"

        strategies = strategy_service.generate_and_persist_strategies(
            s, design_project_id=design_proj.design_project_id, handoff_id=handoff.handoff_id, actor_id="system",
        )
        assert strategies

        portfolio, candidates, suppressed = portfolio_service.generate_and_persist_portfolio(
            s, design_project_id=design_proj.design_project_id, actor_id="system",
        )
        assert len(candidates) >= 3
        EngineeringDesignLoopController().generate_portfolio(s, design_proj, actor_id="system")

        result = evaluate_portfolio(s, portfolio_id=portfolio.portfolio_id, actor_id="system")
        assert result["evaluations"]

        design_proj = project_service.get_design_project(s, design_proj.design_project_id)
        assert design_proj.status in ("portfolio_evaluated", "revision_required")
