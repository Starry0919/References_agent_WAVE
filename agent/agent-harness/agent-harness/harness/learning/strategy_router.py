"""Strategy routing (doc 12.2): which class of method should propose the
next design, given the shape of the current decision space. Rule-based
routing only this round - no real Bayesian optimization/Gaussian-process
implementation exists. Where BO would apply, `route_strategy` says so
honestly (`implemented=False`) and falls back to mechanistic rules, rather
than faking an optimizer call - the doc explicitly tolerates this as a
Phase-5 deferral as long as cross-project propagation stays off by default
(see `harness/learning/policy_registry.py`).
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class StrategyClass(str, Enum):
    bayesian_optimization = "bayesian_optimization"
    mechanistic_rules = "mechanistic_rules"
    model_based_simulation = "model_based_simulation"
    human_review_required = "human_review_required"


@dataclass
class StrategyDecision:
    strategy: StrategyClass
    reason: str
    implemented: bool


def route_strategy(
    *,
    is_low_dimensional_continuous_space: bool,
    has_quantifiable_objective: bool,
    has_conflicting_evidence: bool,
    is_out_of_model_domain: bool,
    is_high_risk: bool,
    has_mechanistic_model: bool,
) -> StrategyDecision:
    if has_conflicting_evidence or is_out_of_model_domain or is_high_risk:
        return StrategyDecision(
            strategy=StrategyClass.human_review_required,
            reason="conflicting evidence, out-of-domain model use, or high risk - route to a discriminating "
            "experiment or human review, not automated candidate selection",
            implemented=True,
        )
    if has_mechanistic_model:
        return StrategyDecision(
            strategy=StrategyClass.model_based_simulation,
            reason="a mechanistic model is available for this scope", implemented=False,
        )
    if is_low_dimensional_continuous_space and has_quantifiable_objective:
        return StrategyDecision(
            strategy=StrategyClass.bayesian_optimization,
            reason="low-dimensional, well-defined variable space with a quantifiable objective would suit BO/"
            "active-learning, but no real implementation is wired up this round - falls back to mechanistic_rules",
            implemented=False,
        )
    return StrategyDecision(
        strategy=StrategyClass.mechanistic_rules,
        reason="combinatorial genetic design with sparse data - mechanistic rules + constrained candidate "
        "generation + conservative ranking",
        implemented=True,
    )
