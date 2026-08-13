"""Candidate Portfolio Generator (doc04 §4.3): deterministic, rule-based
instantiation of `EngineeringStrategy` objects into structurally distinct
`CandidateDesign` drafts. Gene identifiers are only ever taken from (a) the
curated `action_database.json` entries a strategy is grounded in, or (b) a
literal, case-insensitive gene-symbol mention inside the grounding
hypothesis/DDR text, checked against the shared `essential_genes_reference.
json` registry (`harness.workflow.gene_registry`) - never invented. Anything
that cannot be resolved this way is left `"to_be_determined"` (doc04 §3.4).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from harness.i18n import strategy_class_label, t

_OPERATION_KEYWORDS: tuple[tuple[str, str], ...] = (
    ("knockout", "knockout"), ("attenuat", "attenuation"), ("knockdown", "knockdown"),
    ("heterologous", "gene_insertion"), ("insertion", "gene_insertion"), ("promoter", "promoter_edit"),
    ("rbs", "rbs_edit"), ("dynamic", "dynamic_control"), ("allele", "allele_replacement"),
    ("overexpress", "overexpression"),
)


def _normalize_operation(modification_type: str) -> str:
    text = modification_type.lower()
    for kw, op in _OPERATION_KEYWORDS:
        if kw in text:
            return op
    return "overexpression"


def _first_gene_token(target_gene: str) -> str:
    return re.split(r"[\s/(]", target_gene.strip())[0] if target_gene else ""


def find_gene_mentions(text: str, known_genes: set[str]) -> list[str]:
    """Case-insensitive substring match of curated gene symbols against
    free text (a hypothesis statement or DDR bottleneck description) -
    never a guess, only genes the shared registry already knows about."""
    lowered = text.lower()
    return sorted({g for g in known_genes if g.lower() in lowered})


@dataclass
class GeneticModificationDraft:
    target_type: str
    target_identifier: str
    operation: str
    desired_effect: str
    allele_or_variant: str = "unknown"
    expression_control: str = "unknown"
    genomic_or_vector_context: str = "unknown"
    order_or_dependency: str = "unknown"
    reversibility: str = "unknown"
    evidence_links: list[dict[str, str]] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "target_type": self.target_type, "target_identifier": self.target_identifier, "operation": self.operation,
            "desired_effect": self.desired_effect, "allele_or_variant": self.allele_or_variant,
            "expression_control": self.expression_control, "genomic_or_vector_context": self.genomic_or_vector_context,
            "order_or_dependency": self.order_or_dependency, "reversibility": self.reversibility,
            "evidence_links": self.evidence_links, "assumptions": self.assumptions,
        }


@dataclass
class GeneratedCandidate:
    portfolio_role: str
    strategy_ids: list[str]
    genetic_modifications: list[dict[str, Any]]
    regulatory_architecture: dict[str, Any]
    process_modifications: list[dict[str, Any]]
    expected_mechanism: str
    causal_chain: list[str]
    interaction_and_epistasis_assumptions: list[str]
    evidence_links: list[dict[str, str]]
    rationale: str


@dataclass
class AbsentRole:
    role: str
    reason: str


@dataclass
class PortfolioGenerationResult:
    candidates: list[GeneratedCandidate] = field(default_factory=list)
    absent_roles: list[AbsentRole] = field(default_factory=list)


def _modifications_for_strategy(strategy: dict[str, Any], action_database: list[dict[str, Any]], known_genes: set[str]) -> list[GeneticModificationDraft]:
    action_ids = {l["reference"] for l in strategy.get("evidence_links", []) if l.get("source_type") == "curated_knowledge"}
    matching_actions = [a for a in action_database if a.get("action_id") in action_ids]

    mods: list[GeneticModificationDraft] = []
    for a in matching_actions:
        gene = _first_gene_token(str(a.get("target_gene", "")))
        target_type = "gene" if gene in known_genes else "pathway"
        target_identifier = gene if gene in known_genes else (a.get("target_gene") or "to_be_determined")
        mods.append(GeneticModificationDraft(
            target_type=target_type, target_identifier=target_identifier,
            operation=_normalize_operation(str(a.get("modification", a.get("action_type", "")))),
            desired_effect=str(a.get("expected_effect", "")),
            evidence_links=[{"source_type": "curated_knowledge", "reference": a.get("action_id", "")}],
            assumptions=[f"curated action_database entry {a.get('action_id')}"] + ([f"replacement: {a['replacement']}"] if a.get("replacement") else []),
        ))

    if not mods:
        # No curated action entry - fall back to a literal gene-symbol
        # mention in the grounding text, never a fabricated identifier.
        mentioned = find_gene_mentions(strategy.get("mechanism_target", ""), known_genes)
        if mentioned:
            for gene in mentioned[:2]:
                mods.append(GeneticModificationDraft(
                    target_type="gene", target_identifier=gene,
                    operation="attenuation" if strategy["strategy_class"] == "feedback_relief" else "knockout",
                    desired_effect=f"address {strategy['strategy_class']} per grounding hypothesis",
                    evidence_links=list(strategy.get("evidence_links", [])),
                    assumptions=[f"gene symbol {gene!r} found in grounding text; specific allele/variant not yet determined"],
                ))
        else:
            mods.append(GeneticModificationDraft(
                target_type="regulatory_element", target_identifier="to_be_determined",
                operation="process_only" if strategy["strategy_class"] == "process_condition_engineering" else "attenuation",
                desired_effect=f"address {strategy['strategy_class']} per grounding hypothesis",
                evidence_links=list(strategy.get("evidence_links", [])),
                assumptions=["no curated action or literal gene mention available - target left to_be_determined, not fabricated"],
            ))
    return mods


def generate_portfolio(
    *,
    strategies: list[dict[str, Any]],
    known_genes: set[str],
    action_database: list[dict[str, Any]],
) -> PortfolioGenerationResult:
    result = PortfolioGenerationResult()
    by_class = {s["strategy_class"]: s for s in strategies}  # one representative per class is enough for role construction
    probe = by_class.get("diagnostic_measurement_probe")
    non_probe_classes = [c for c in by_class if c != "diagnostic_measurement_probe"]

    # -- reference_or_control: always representable -----------------------
    result.candidates.append(GeneratedCandidate(
        portfolio_role="reference_or_control", strategy_ids=[], genetic_modifications=[], regulatory_architecture={},
        process_modifications=[], expected_mechanism=t("portfolio.reference.expected_mechanism"),
        causal_chain=[t("portfolio.reference.causal_chain")], interaction_and_epistasis_assumptions=[],
        evidence_links=[], rationale=t("portfolio.reference.rationale"),
    ))

    # -- low_risk: single best-evidenced strategy, single modification ----
    if non_probe_classes:
        low_risk_class = max(non_probe_classes, key=lambda c: len(by_class[c].get("evidence_links", [])))
        strategy = by_class[low_risk_class]
        mods = _modifications_for_strategy(strategy, action_database, known_genes)[:1]
        result.candidates.append(GeneratedCandidate(
            portfolio_role="low_risk", strategy_ids=[strategy["strategy_id"]],
            genetic_modifications=[m.to_dict() for m in mods], regulatory_architecture={},
            process_modifications=[], expected_mechanism=strategy["mechanism_target"],
            causal_chain=strategy.get("expected_causal_chain", []), interaction_and_epistasis_assumptions=[],
            evidence_links=strategy.get("evidence_links", []),
            rationale=t("portfolio.low_risk.rationale", strategy_class=strategy_class_label(low_risk_class)),
        ))
    else:
        result.absent_roles.append(AbsentRole("low_risk", "no non-probe strategy was generated for this diagnosis"))

    # -- high_upside: combine two mechanistically distinct strategies -----
    if len(non_probe_classes) >= 2:
        chosen_classes = non_probe_classes[:2]
        combined_mods: list[GeneticModificationDraft] = []
        combined_chain: list[str] = []
        combined_evidence: list[dict[str, str]] = []
        for c in chosen_classes:
            combined_mods.extend(_modifications_for_strategy(by_class[c], action_database, known_genes))
            combined_chain.extend(by_class[c].get("expected_causal_chain", []))
            combined_evidence.extend(by_class[c].get("evidence_links", []))
        result.candidates.append(GeneratedCandidate(
            portfolio_role="high_upside", strategy_ids=[by_class[c]["strategy_id"] for c in chosen_classes],
            genetic_modifications=[m.to_dict() for m in combined_mods], regulatory_architecture={},
            process_modifications=[], expected_mechanism=" + ".join(strategy_class_label(c) for c in chosen_classes),
            causal_chain=combined_chain,
            interaction_and_epistasis_assumptions=[
                t(
                    "portfolio.high_upside.assumption",
                    class_a=strategy_class_label(chosen_classes[0]), class_b=strategy_class_label(chosen_classes[1]),
                )
            ],
            evidence_links=combined_evidence,
            rationale=t(
                "portfolio.high_upside.rationale",
                class_a=strategy_class_label(chosen_classes[0]), class_b=strategy_class_label(chosen_classes[1]),
            ),
        ))
    elif non_probe_classes:
        result.absent_roles.append(AbsentRole("high_upside", "only one non-probe strategy class was generated - no second, mechanistically distinct strategy to combine with"))
    else:
        result.absent_roles.append(AbsentRole("high_upside", "no non-probe strategy was generated for this diagnosis"))

    # -- information_gain: from the diagnostic_measurement_probe strategy -
    if probe is not None:
        mentioned = find_gene_mentions(probe.get("mechanism_target", ""), known_genes)
        target = mentioned[0] if mentioned else "to_be_determined"
        mods = [GeneticModificationDraft(
            target_type="gene" if mentioned else "regulatory_element", target_identifier=target,
            operation="knockdown", desired_effect=t("portfolio.information_gain.desired_effect"),
            evidence_links=probe.get("evidence_links", []),
            assumptions=[t("portfolio.information_gain.assumption")],
        )]
        discriminates = [
            t("portfolio.information_gain.discriminates", ref=l.get("reference"))
            for l in probe.get("evidence_links", [])
        ]
        result.candidates.append(GeneratedCandidate(
            portfolio_role="information_gain", strategy_ids=[probe["strategy_id"]],
            genetic_modifications=[m.to_dict() for m in mods], regulatory_architecture={}, process_modifications=[],
            expected_mechanism=probe["mechanism_target"], causal_chain=probe.get("expected_causal_chain", []),
            interaction_and_epistasis_assumptions=discriminates, evidence_links=probe.get("evidence_links", []),
            rationale=t("portfolio.information_gain.rationale"),
        ))
    else:
        result.absent_roles.append(AbsentRole("information_gain", "no unresolved alternatives were carried by the diagnosis handoff, so no diagnostic_measurement_probe strategy was generated"))

    # -- process_first: only if a process-condition strategy exists -------
    if "process_condition_engineering" in by_class:
        strategy = by_class["process_condition_engineering"]
        result.candidates.append(GeneratedCandidate(
            portfolio_role="process_first", strategy_ids=[strategy["strategy_id"]], genetic_modifications=[],
            regulatory_architecture={}, process_modifications=[{"parameter": strategy["mechanism_target"], "change": strategy["rationale"]}],
            expected_mechanism=strategy["mechanism_target"], causal_chain=strategy.get("expected_causal_chain", []),
            interaction_and_epistasis_assumptions=[], evidence_links=strategy.get("evidence_links", []),
            rationale=t("portfolio.process_first.rationale"),
        ))
    else:
        result.absent_roles.append(AbsentRole("process_first", "no process_condition_engineering strategy was grounded by this diagnosis"))

    # -- fallback: de-scoped version of high_upside, excluding whatever
    # modification(s) low_risk already covers - never a bare duplicate of
    # low_risk (doc04 §3.6: candidates must differ in mechanism/architecture,
    # not just be the same intervention under a different role label).
    high_upside = next((c for c in result.candidates if c.portfolio_role == "high_upside"), None)
    low_risk = next((c for c in result.candidates if c.portfolio_role == "low_risk"), None)
    if high_upside is not None and len(high_upside.genetic_modifications) > 1:
        low_risk_keys = {(m["target_identifier"], m["operation"]) for m in (low_risk.genetic_modifications if low_risk else [])}
        remaining = [m for m in high_upside.genetic_modifications if (m["target_identifier"], m["operation"]) not in low_risk_keys]
        if remaining:
            result.candidates.append(GeneratedCandidate(
                portfolio_role="fallback", strategy_ids=high_upside.strategy_ids, genetic_modifications=remaining[:1],
                regulatory_architecture={}, process_modifications=[], expected_mechanism=high_upside.expected_mechanism,
                causal_chain=high_upside.causal_chain[:1], interaction_and_epistasis_assumptions=[],
                evidence_links=high_upside.evidence_links,
                rationale=t("portfolio.fallback.rationale"),
            ))
        else:
            result.absent_roles.append(AbsentRole("fallback", "every high_upside modification duplicates low_risk once de-scoped to one modification - no distinct fallback available"))
    else:
        result.absent_roles.append(AbsentRole("fallback", "high_upside candidate has only one modification already - no further de-scope available"))

    return result
