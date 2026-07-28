"""Engineering Strategy Generator (doc04 §4.2): deterministic, rule-based
generation grounded in (a) the diagnosis's own `supported_hypotheses`
statements and (b) the curated `knowledge/engineering_actions/
action_database.json` - never a bare LLM free-generation whose own
self-review would stand in for evidence (doc04 §11: "LLM critic 不能被
记录为实验或模型证据").

Follows the same deterministic-generator precedent as
`harness.diagnosis.hypothesis_generator` (`generation_provenance` records
`"rule_based_v1"`): reproducible and unit-testable, with an explicit,
structured `excluded` entry for every strategy class this diagnosis does
NOT support, rather than a silent absence. The keyword table below is
generic (keyed by mechanism vocabulary, not by product name) - it happens
to activate for the L-tryptophan DDR/action-database entries this
knowledge base currently ships, but nothing here is conditioned on
`target_product == "L-tryptophan"` (doc04 §1.2's "禁止...硬编码只对
L-tryptophan 有效的最终答案").
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from harness.engineering_design.models import STRATEGY_CLASSES
from harness.i18n import strategy_class_label, t

# Generic mechanism-vocabulary -> strategy_class routing. Extending this
# table (not the generator's control flow) is how a new mechanism class
# gets covered - the routing itself never inspects product/host identity.
_STRATEGY_KEYWORDS: dict[str, tuple[str, ...]] = {
    "precursor_supply": ("precursor", "pep", "e4p", "central carbon", "carbon flux", "supply limitation"),
    "feedback_relief": ("feedback", "attenuat", "inhibit", "regulat", "repress"),
    "competing_flux_control": ("competing", "degradation", "branch", "byproduct", "side reaction", "consum"),
    "cofactor_energy_balancing": ("cofactor", "nadh", "nadph", "atp", "redox", "energy"),
    "resource_burden_management": ("burden", "growth defect", "metabolic load", "overexpression cost"),
    "dynamic_regulation": ("dynamic", "inducible", "switch", "temporal control"),
    "transport_tolerance_engineering": ("transport", "export", "toxic", "tolerance", "efflux"),
    "process_condition_engineering": ("oxygenation", "temperature", "medium", "process condition", "cultivation"),
}

_ACTION_TYPE_TO_STRATEGY_CLASS: dict[str, str] = {
    "transport engineering": "precursor_supply",
    "knockout": "competing_flux_control",
    "heterologous pathway introduction": "precursor_supply",
    "promoter engineering": "cofactor_energy_balancing",
    "overexpression": "precursor_supply",
}


@dataclass
class EvidenceLinkRef:
    source_type: str  # curated_knowledge|diagnosis_hypothesis
    reference: str
    detail: str = ""


@dataclass
class GeneratedStrategy:
    engineering_objective: str
    mechanism_target: str
    strategy_class: str
    rationale: str
    expected_causal_chain: list[str]
    evidence_links: list[dict[str, str]]
    applicability_conditions: list[str]
    known_tradeoffs: list[str]
    failure_modes: list[str]
    uncertainty: list[str]
    grounding_hypothesis_ids: list[str] = field(default_factory=list)


@dataclass
class ExcludedStrategyClass:
    strategy_class: str
    reason: str


@dataclass
class StrategyGenerationResult:
    strategies: list[GeneratedStrategy] = field(default_factory=list)
    excluded: list[ExcludedStrategyClass] = field(default_factory=list)


def _match_strategy_classes(text: str) -> list[str]:
    text = text.lower()
    return [cls for cls, kws in _STRATEGY_KEYWORDS.items() if any(kw in text for kw in kws)]


def _objective_summary(primary_metrics: list[dict[str, Any]]) -> str:
    if not primary_metrics:
        return t("strategy.objective.default")
    names = [str(m.get("metric", m.get("name", "unknown"))) for m in primary_metrics]
    return t("strategy.objective.named", names=", ".join(names))


def generate_strategies(
    *,
    supported_hypotheses: list[dict[str, Any]],  # [{hypothesis_version_id, statement, mechanism_class}]
    unresolved_alternatives: list[str],
    uncertainty: list[str],
    primary_metrics: list[dict[str, Any]],
    action_database: list[dict[str, Any]] | None = None,
) -> StrategyGenerationResult:
    result = StrategyGenerationResult()
    objective = _objective_summary(primary_metrics)
    action_database = action_database or []
    covered_classes: set[str] = set()

    for hyp in supported_hypotheses:
        statement = str(hyp.get("statement", ""))
        matched = _match_strategy_classes(statement)
        if not matched:
            continue
        for strategy_class in matched:
            covered_classes.add(strategy_class)
            matching_actions = [
                a for a in action_database
                if _ACTION_TYPE_TO_STRATEGY_CLASS.get(str(a.get("action_type", "")).lower()) == strategy_class
            ]
            evidence_links = [{"source_type": "diagnosis_hypothesis", "reference": str(hyp.get("hypothesis_version_id", "")), "detail": statement}]
            evidence_links += [
                {"source_type": "curated_knowledge", "reference": str(a.get("action_id", "")), "detail": str(a.get("evidence", ""))}
                for a in matching_actions
            ]
            known_tradeoffs = [str(a.get("risk", "")) for a in matching_actions if a.get("risk")]
            causal_chain = [statement] + [str(a.get("mechanism", "")) for a in matching_actions if a.get("mechanism")]
            action_suffix = (
                t("strategy.rationale.grounded.action_suffix", n=len(matching_actions)) if matching_actions else ""
            )
            result.strategies.append(GeneratedStrategy(
                engineering_objective=objective, mechanism_target=statement, strategy_class=strategy_class,
                rationale=t(
                    "strategy.rationale.grounded", hyp_id=hyp.get("hypothesis_version_id"),
                    strategy_class=strategy_class_label(strategy_class), action_suffix=action_suffix,
                ),
                expected_causal_chain=causal_chain, evidence_links=evidence_links,
                applicability_conditions=[c for a in matching_actions for c in a.get("applicable_conditions", [])] or [t("strategy.applicability.default")],
                known_tradeoffs=known_tradeoffs or [t("strategy.tradeoff.default")],
                failure_modes=[t("strategy.failure_mode.grounded", hyp_id=hyp.get("hypothesis_version_id"))],
                uncertainty=list(uncertainty), grounding_hypothesis_ids=[str(hyp.get("hypothesis_version_id", ""))],
            ))

    # doc04 §2.1/§3.3: a diagnostic/measurement probe strategy is always
    # representable when the diagnosis has unresolved alternatives - never
    # silently dropped in favor of only production-maximizing strategies.
    if unresolved_alternatives:
        covered_classes.add("diagnostic_measurement_probe")
        result.strategies.append(GeneratedStrategy(
            engineering_objective=t("strategy.probe.objective"),
            mechanism_target=t("strategy.probe.mechanism_target", alternatives=unresolved_alternatives),
            strategy_class="diagnostic_measurement_probe",
            rationale=t("strategy.probe.rationale"),
            expected_causal_chain=[t("strategy.probe.causal_chain")],
            evidence_links=[{"source_type": "diagnosis_hypothesis", "reference": h, "detail": t("strategy.probe.evidence_detail")} for h in unresolved_alternatives],
            applicability_conditions=[t("strategy.probe.applicability")],
            known_tradeoffs=[t("strategy.probe.tradeoff")],
            failure_modes=[t("strategy.probe.failure_mode")],
            uncertainty=list(uncertainty),
        ))

    for strategy_class in STRATEGY_CLASSES:
        if strategy_class not in covered_classes:
            result.excluded.append(ExcludedStrategyClass(
                strategy_class=strategy_class,
                reason=t("strategy.excluded.reason"),
            ))

    return result
