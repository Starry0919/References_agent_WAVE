"""Portfolio-level evaluation orchestration (doc04 §4.4/§4.5): runs the
evaluator suite over every candidate in a portfolio, computes Pareto
dominance across them, and drives the `EngineeringDesignLoopController`
`evaluation_in_progress -> revision_required | portfolio_evaluated`
transition through `evaluator_revision_gate`.
"""
from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from harness.engineering_design import decision as decision_mod
from harness.engineering_design.evaluators import runner
from harness.engineering_design.loop import EngineeringDesignLoopController
from harness.engineering_design.models import CandidateDesign, DesignEvaluation, DesignPortfolio, EngineeringDesignProject
from harness.engineering_design.decision_state import transition_candidate
from harness.engineering_design.failure_recall import failure_penalty
from harness.ids import now
from harness.memory import event_types as et
from harness.memory.event_store import append_event
from harness.workflow.gates import evaluator_revision_gate

_loop = EngineeringDesignLoopController()


def evaluate_portfolio(session: Session, *, portfolio_id: str, actor_id: str) -> dict[str, Any]:
    portfolio = session.get(DesignPortfolio, portfolio_id)
    if portfolio is None:
        raise ValueError(f"no such portfolio: {portfolio_id}")
    proj = session.get(EngineeringDesignProject, portfolio.design_project_id)

    candidates = session.execute(select(CandidateDesign).where(CandidateDesign.portfolio_id == portfolio_id)).scalars().all()

    _loop.start_evaluation(session, proj, actor_id=actor_id)

    evaluations: dict[str, DesignEvaluation] = {}
    for c in candidates:
        if c.decision_state == "candidate_generated":
            transition_candidate(session, design_id=c.design_id, target="evaluation_pending", actor_id=actor_id)
        recall = failure_penalty(
            session, project_id=proj.project_id,
            intervention_tokens=[str(m.get("target_identifier")) for m in c.genetic_modifications if m.get("target_identifier")],
            context={"host": proj.chassis, **(proj.temporal_and_environmental_context or {})},
        )
        evaluations[c.design_id] = runner.run_evaluator_suite(
            session, design_id=c.design_id, actor_id=actor_id,
            objective_extensions=[{"metric":"failure_memory_penalty","direction_estimate":"computed",
                "magnitude":recall["penalty"],"unit":"context-matched penalty (lower is better)",
                "basis":recall,"evidence_tier":"engineering_memory"}],
        )
        transition_candidate(session, design_id=c.design_id, target="evaluated", actor_id=actor_id)

    eval_by_design = {
        did: {
            "hard_constraint_results": ev.hard_constraint_results, "objective_vector": ev.objective_vector,
            "blocking_findings": runner.blocking_findings_for(ev),
            "portfolio_role": next(c.portfolio_role for c in candidates if c.design_id == did),
            "failure_recall": failure_penalty(
                session, project_id=proj.project_id,
                intervention_tokens=[str(m.get("target_identifier")) for m in next(c for c in candidates if c.design_id == did).genetic_modifications if m.get("target_identifier")],
                context={"host": proj.chassis, **(proj.temporal_and_environmental_context or {})},
            ),
        }
        for did, ev in evaluations.items()
    }
    decision_result = decision_mod.recommend_portfolio(evaluations_by_design=eval_by_design, preferences_or_weights=proj.preferences_or_weights)

    for did, status in decision_result["pareto_status"].items():
        evaluations[did].pareto_status = status
    for did in decision_result.get("rejected", {}):
        if did in evaluations and evaluations[did].pareto_status is None:
            evaluations[did].pareto_status = "not_computed"
    rejected_ids = set(decision_result.get("rejected", {}))
    for candidate in candidates:
        if candidate.design_id in rejected_ids:
            transition_candidate(session, design_id=candidate.design_id, target="rejected", actor_id=actor_id,
                                 reasons=[decision_result["rejected"][candidate.design_id]])
        else:
            transition_candidate(session, design_id=candidate.design_id, target="ranked", actor_id=actor_id)
            transition_candidate(session, design_id=candidate.design_id, target="human_selection_pending", actor_id=actor_id)
    session.flush()

    portfolio.decision = decision_result
    portfolio.status = "evaluated"
    session.flush()
    append_event(
        session, project_id=proj.project_id, event_type=et.DESIGN_PORTFOLIO_DECIDED, entity_type="DesignPortfolio",
        entity_id=portfolio.portfolio_id, payload={"portfolio_id": portfolio.portfolio_id, "decision": decision_result}, actor_type="agent", actor_id=actor_id,
    )

    all_blocking = [f for ev in evaluations.values() for f in runner.blocking_findings_for(ev)]
    revision_gate = evaluator_revision_gate(blocking_findings=all_blocking, revision_count=proj.revision_count)
    _loop.complete_evaluation(session, proj, actor_id=actor_id, revision_gate_result=revision_gate)

    return {"portfolio": portfolio, "evaluations": evaluations, "decision": decision_result, "revision_gate": revision_gate}
