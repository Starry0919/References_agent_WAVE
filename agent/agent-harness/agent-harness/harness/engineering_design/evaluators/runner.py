"""Evaluator suite runner (doc04 §4.4): composes all 8 independent
evaluators, computes the objective vector and hard-constraint results, and
persists one immutable `DesignEvaluation` row - a re-evaluation of the same
(design_id, design_version) always creates a NEW row, never overwrites the
last one, so `evaluator_revision_gate` and any later audit can see the full
history.
"""
from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from harness.engineering_design import decision as decision_mod
from harness.engineering_design.evaluators import buildability, counterfactual, diversity, evidence, mechanism, safety_governance, tradeoff, validation
from harness.engineering_design.models import (
    BuildTestPackage,
    CandidateDesign,
    CounterfactualRun,
    DesignEvaluation,
    EngineeringDesignProject,
    EngineeringStrategy,
    HumanApprovalRecord,
)
from harness.ids import new_id, now
from harness.memory import event_types as et
from harness.memory.event_store import append_event, snapshot

EVALUATION_SNAPSHOT_FIELDS = (
    "evaluation_id", "design_id", "design_version", "objective_vector", "hard_constraint_results",
    "mechanism_consistency", "evidence_assessment", "model_results", "model_agreement_and_conflicts",
    "sensitivity_and_robustness", "tradeoff_profile", "buildability", "validation_feasibility",
    "expected_information_gain", "safety_and_governance", "evaluator_findings", "required_revisions",
    "pareto_status", "recommendation", "provenance", "created_at",
)


def _candidate_to_dict(c: CandidateDesign) -> dict[str, Any]:
    return {
        "design_id": c.design_id, "portfolio_role": c.portfolio_role, "strategy_ids": c.strategy_ids,
        "genetic_modifications": c.genetic_modifications, "evidence_links": c.evidence_links,
        "safety_flags": c.safety_flags, "status": c.status,
    }


def run_evaluator_suite(session: Session, *, design_id: str, actor_id: str) -> DesignEvaluation:
    candidate = session.get(CandidateDesign, design_id)
    if candidate is None:
        raise ValueError(f"no such candidate design: {design_id}")
    proj = session.get(EngineeringDesignProject, candidate.design_project_id)

    known_strategy_ids = {
        s.strategy_id for s in session.execute(
            select(EngineeringStrategy).where(EngineeringStrategy.design_project_id == candidate.design_project_id)
        ).scalars()
    }
    siblings = [
        _candidate_to_dict(c) for c in session.execute(
            select(CandidateDesign).where(CandidateDesign.portfolio_id == candidate.portfolio_id)
        ).scalars()
    ] if candidate.portfolio_id else []

    build_test_package = None
    if candidate.build_test_package_id:
        pkg = session.get(BuildTestPackage, candidate.build_test_package_id)
        if pkg is not None:
            build_test_package = {
                "target_readouts": pkg.target_readouts, "mechanism_readouts": pkg.mechanism_readouts,
                "controls": pkg.controls, "decision_rules": pkg.decision_rules, "readiness": pkg.readiness,
            }

    counterfactual_runs = [
        {
            "run_id": r.run_id, "adapter_name": r.adapter_name, "runtime_status": r.runtime_status,
            "capability_status": r.capability_status, "outputs": r.outputs,
        }
        for r in session.execute(select(CounterfactualRun).where(CounterfactualRun.design_id == design_id)).scalars()
    ]

    human_approval_on_record = bool(
        session.execute(select(HumanApprovalRecord).where(HumanApprovalRecord.design_id == design_id)).scalars().first()
    )

    cd = _candidate_to_dict(candidate)
    results = [
        mechanism.evaluate(cd, known_strategy_ids=known_strategy_ids),
        evidence.evaluate(cd),
        counterfactual.evaluate(cd, counterfactual_runs=counterfactual_runs),
        tradeoff.evaluate(cd),
        buildability.evaluate(cd),
        validation.evaluate(cd, build_test_package=build_test_package),
        safety_governance.evaluate(cd, human_approval_on_record=human_approval_on_record),
        diversity.evaluate(cd, sibling_candidates=siblings),
    ]

    objective_vector = decision_mod.compute_objective_vector(
        cd, primary_metrics=proj.primary_metrics, counterfactual_results=counterfactual_runs,
    )
    hard_constraint_results = decision_mod.check_hard_constraints(cd, proj.hard_constraints)
    tradeoff_profile = tradeoff.build_tradeoff_profile(cd)

    blocking = [f"{r.evaluator}: {f}" for r in results if r.blocking for f in r.findings]
    required_revisions = [rev for r in results for rev in r.required_revisions]
    hard_violated = any(r["satisfied"] is False for r in hard_constraint_results)

    if hard_violated:
        recommendation = "reject"
    elif blocking:
        recommendation = "revise"
    elif any(r.status == "insufficient_evidence" for r in results):
        recommendation = "insufficient_evidence"
    else:
        recommendation = "select"

    evaluation = DesignEvaluation(
        evaluation_id=new_id("EVAL"), design_id=design_id, design_version=candidate.design_version,
        objective_vector=objective_vector, hard_constraint_results=hard_constraint_results,
        mechanism_consistency=next(r for r in results if r.evaluator == "MechanismEvaluator").to_dict(),
        evidence_assessment=next(r for r in results if r.evaluator == "EvidenceEvaluator").to_dict(),
        model_results=counterfactual_runs, model_agreement_and_conflicts=None, sensitivity_and_robustness=None,
        tradeoff_profile=tradeoff_profile, buildability=next(r for r in results if r.evaluator == "BuildabilityEvaluator").to_dict(),
        validation_feasibility=next(r for r in results if r.evaluator == "ValidationEvaluator").to_dict(),
        expected_information_gain="high" if candidate.portfolio_role == "information_gain" else "not_applicable",
        safety_and_governance=next(r for r in results if r.evaluator == "SafetyGovernanceEvaluator").to_dict(),
        evaluator_findings=[r.to_dict() for r in results], required_revisions=required_revisions,
        pareto_status="not_computed", recommendation=recommendation,
        provenance={"method": "rule_based_evaluator_suite_v1", "evaluators_run": [r.evaluator for r in results]},
        created_at=now(),
    )
    session.add(evaluation)
    if candidate.readiness == "conceptual":
        candidate.readiness = "evaluated"
    session.flush()
    append_event(
        session, project_id=proj.project_id, event_type=et.DESIGN_EVALUATION_COMPLETED, entity_type="DesignEvaluation",
        entity_id=evaluation.evaluation_id, payload=snapshot(evaluation, EVALUATION_SNAPSHOT_FIELDS), actor_type="agent", actor_id=actor_id,
    )
    return evaluation


def blocking_findings_for(evaluation: DesignEvaluation) -> list[str]:
    return [f"{f['evaluator']}: {finding}" for f in evaluation.evaluator_findings if f.get("blocking") for finding in f.get("findings", [])]


def latest_evaluation(session: Session, design_id: str) -> DesignEvaluation | None:
    return session.execute(
        select(DesignEvaluation).where(DesignEvaluation.design_id == design_id).order_by(DesignEvaluation.created_at.desc())
    ).scalars().first()
