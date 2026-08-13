"""Strategy Prior Retrieval (ELISER-inspired historical design memory,
prompt §8/§9): pure, deterministic matching from a `strategy_class` (the
9-value `harness.engineering_design.models.STRATEGY_CLASSES` vocabulary)
against the two historical-experience corpora that already exist in this
repository but were never connected to candidate generation:

- `knowledge/ddr_database/*.json` — real Design Decision Records, each with
  a `decision_chain` of engineering-decision steps (evidence_grading,
  reason_nature, optional `strategy_categories`).
- `knowledge/biological_rules/rules.json` — cross-paper distilled rules
  (already gated at extraction time to only cover `reason_nature` in
  {机理推断 mechanistic inference, 文献类比 literature analogy} - see
  `harness/paper_extraction/rule_distillation.py`'s own docstring).

Deliberately NOT RAG and NOT an LLM ranking - same "transparent, inspectable
heuristic" precedent as `harness.engineering_design.strategy_generator`
(`_match_strategy_classes`) and `harness.ideas.matching` (bigram overlap,
"never a hidden ML ranking"). `compute_design_prior` is an ADVISORY score
only (prompt §9: "NOT a final recommendation, NOT an automatic decision
maker, NOT frequency-only ranking") - nothing in this module writes to any
persisted row or gates any workflow transition; callers decide what to do
with the result.

The DDR corpus's `strategy_categories` controlled vocabulary
(flux_redirection, precursor_supply_enhancement, competitive_pathway_removal,
dynamic_control, enzyme_activity_improvement, transport_engineering,
stress_tolerance_engineering, evolutionary_optimization - schema_v2.json
§decision_chain.strategy_categories) is a DIFFERENT vocabulary from
`STRATEGY_CLASSES` - it was authored independently (老师 §14) and the two
do not line up by string similarity. `_DDR_CATEGORY_TO_STRATEGY_CLASS` is
the explicit, human-reviewable crosswalk; only about half of the 26 DDRs
currently populate `strategy_categories` at all (pre-v2.4 extractions
predate the field), so a keyword fallback against the same
`_STRATEGY_KEYWORDS` table `strategy_generator.py` already uses for its own
hypothesis-matching is required for full corpus coverage, not an
optional nicety.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

from harness.engineering_design.strategy_generator import _STRATEGY_KEYWORDS
from harness.i18n import t

# Many-to-many, deliberately conservative: a WAVE strategy_class is only
# mapped to a DDR strategy_category when the mechanism they describe is
# genuinely the same thing under a different name. Left unmapped (rather
# than force-mapped) when no DDR category matches - those strategy_classes
# still get corpus coverage via the keyword fallback below, and an honest
# lack of `strategy_categories`-based matches is not a bug (老师 §14 leaves
# process/resource/dynamic-measurement classes outside the DDR vocabulary's
# scope; they are genetic/pathway strategy categories, not process- or
# information-value strategies).
_DDR_CATEGORY_TO_STRATEGY_CLASS: dict[str, tuple[str, ...]] = {
    "flux_redirection": ("competing_flux_control",),
    "precursor_supply_enhancement": ("precursor_supply",),
    "competitive_pathway_removal": ("competing_flux_control",),
    "dynamic_control": ("dynamic_regulation",),
    "enzyme_activity_improvement": ("feedback_relief",),
    "transport_engineering": ("transport_tolerance_engineering",),
    "stress_tolerance_engineering": ("transport_tolerance_engineering",),
    "evolutionary_optimization": (),
}
# Inverted view used for lookup: strategy_class -> set of DDR categories.
_STRATEGY_CLASS_TO_DDR_CATEGORIES: dict[str, set[str]] = {}
for _ddr_cat, _classes in _DDR_CATEGORY_TO_STRATEGY_CLASS.items():
    for _cls in _classes:
        _STRATEGY_CLASS_TO_DDR_CATEGORIES.setdefault(_cls, set()).add(_ddr_cat)

# doc03/doc04 evidence_grading vocabulary is Chinese in the DDR corpus
# ("硬"=hard, "软"=soft) - kept verbatim rather than translated, since it is
# a literal field value read back out of the source JSON, not narrative text.
_HARD_GRADES = {"硬"}
_MECHANISTIC_REASON_NATURES = {"机理推断"}
_ANALOGY_REASON_NATURES = {"文献类比"}

SourceType = Literal["ddr_decision", "distilled_rule"]


@dataclass
class PriorSourceRef:
    source_type: SourceType
    source_id: str  # ddr_id, or rule_id
    evidence_grading: str  # "硬"|"软"|"unknown"
    mechanistic_weight: float  # 1.0 mechanistic, 0.5 analogy/multi-paper, 0.25 weak precedent
    matched_via: str  # "strategy_category" | "keyword"
    basis_quote: str
    host: str | None = None
    product: str | None = None


@dataclass
class DesignPrior:
    score: float  # 0.0-1.0, advisory only
    historical_frequency: int
    basis: list[str] = field(default_factory=list)
    supporting_sources: list[str] = field(default_factory=list)


def _quality_weight(evidence_grading: str) -> float:
    if evidence_grading in _HARD_GRADES:
        return 1.0
    if evidence_grading:
        return 0.5
    return 0.0


def _text_matches(strategy_class: str, haystack: str) -> bool:
    """Deliberately does NOT fall back to arbitrary long words from the
    caller's free-text mechanism description (unlike `local_ddr_adapter.
    search`'s free-text browse, which is fine being permissive for a
    human-driven search box). An earlier version of this module tried that
    and, on the real corpus, pulled in ~15/26 DDRs for `precursor_supply`
    purely because common words like "carbon" or "titer" appear almost
    everywhere in this domain - a false-precision trap, not a real
    historical-precedent signal. Only the curated `_STRATEGY_KEYWORDS` table
    (already trusted by `strategy_generator.py` for the identical
    classification task) and the DDR's own `strategy_categories` field are
    used as match criteria - both are reviewable, bounded vocabularies, not
    open-ended text overlap."""
    haystack = haystack.lower()
    keywords = _STRATEGY_KEYWORDS.get(strategy_class, ())
    return any(kw in haystack for kw in keywords)


def _ddr_step_sources(strategy_class: str, ddr_records: list[dict[str, Any]]) -> list[PriorSourceRef]:
    allowed_categories = _STRATEGY_CLASS_TO_DDR_CATEGORIES.get(strategy_class, set())
    refs: list[PriorSourceRef] = []
    for rec in ddr_records:
        ddr_id = rec.get("ddr_id", "")
        if not ddr_id:
            continue
        meta = rec.get("metadata", {})
        host = meta.get("host") or meta.get("organism")
        product = meta.get("target_product")
        for step in rec.get("decision_chain", []):
            step_categories = set(step.get("strategy_categories") or [])
            trig = step.get("trigger", {})
            tgt = step.get("target", {})
            haystack = " ".join([
                str(step.get("rule") or ""),
                str(trig.get("observation", "")), str(trig.get("reasoning", "")),
                str(step.get("evidence", {}).get("description", "")),
                str(tgt.get("gene") or ""), str(tgt.get("enzyme") or ""), str(tgt.get("pathway") or ""),
            ])
            matched_via: str | None = None
            if step_categories & allowed_categories:
                matched_via = "strategy_category"
            elif _text_matches(strategy_class, haystack):
                matched_via = "keyword"
            if matched_via is None:
                continue

            reason_nature = step.get("reason_nature", "")
            if reason_nature in _MECHANISTIC_REASON_NATURES:
                mechanistic_weight = 1.0
            elif reason_nature in _ANALOGY_REASON_NATURES:
                mechanistic_weight = 0.5
            else:
                mechanistic_weight = 0.25  # genuine precedent, but not marked generalizable at extraction time

            basis_source = step.get("rule") or step.get("trigger", {}).get("observation", "") or haystack
            refs.append(PriorSourceRef(
                source_type="ddr_decision", source_id=ddr_id,
                evidence_grading=step.get("evidence_grading", "unknown"),
                mechanistic_weight=mechanistic_weight, matched_via=matched_via,
                basis_quote=str(basis_source)[:200], host=host, product=product,
            ))
            break  # one reference per DDR - frequency counts distinct papers, not steps
    return refs


def _rule_sources(strategy_class: str, rules: list[dict[str, Any]]) -> list[PriorSourceRef]:
    refs: list[PriorSourceRef] = []
    for rule in rules:
        rule_id = rule.get("rule_id", "")
        if not rule_id:
            continue
        haystack = " ".join([str(rule.get("statement", "")), " ".join(rule.get("trigger_conditions", []))])
        if not _text_matches(strategy_class, haystack):
            continue
        source_ddrs = rule.get("source_ddrs", [])
        # A distilled rule already represents cross-paper agreement when it
        # cites more than one source DDR - treat that as the multi-paper
        # mechanistic-consistency signal (doc04 §11's "multi_paper_supported"
        # tier), never re-derived from scratch.
        mechanistic_weight = 1.0 if len(source_ddrs) > 1 else 0.5
        refs.append(PriorSourceRef(
            source_type="distilled_rule", source_id=rule_id,
            evidence_grading=rule.get("evidence_grading", "unknown"),
            mechanistic_weight=mechanistic_weight, matched_via="keyword",
            basis_quote=str(rule.get("statement", ""))[:200],
        ))
    return refs


def find_prior_sources(
    strategy_class: str, mechanism_text: str, ddr_records: list[dict[str, Any]], rules: list[dict[str, Any]],
) -> list[PriorSourceRef]:
    """All distinct historical sources (DDR decisions + distilled rules)
    that support `strategy_class`. `mechanism_text` (a diagnosis hypothesis
    statement or similar free text) is accepted for call-site symmetry with
    `strategy_generator.py` and as a documented extension point for a future,
    more targeted match (e.g. gene-name overlap) - matching itself currently
    uses only the bounded `_STRATEGY_KEYWORDS`/`strategy_categories`
    vocabularies (see `_text_matches`'s docstring for why an open-ended
    text-overlap fallback was tried and rejected). Never fabricates a match -
    an empty return is the honest, expected result for a strategy_class with
    no corpus support."""
    del mechanism_text
    return _ddr_step_sources(strategy_class, ddr_records) + _rule_sources(strategy_class, rules)


def compute_design_prior(sources: list[PriorSourceRef], *, host: str | None = None, product: str | None = None) -> DesignPrior:
    """Evidence-weighted historical-experience score (prompt §9): combines
    historical frequency, evidence quality, and mechanistic consistency;
    folds in applicability (host/product match) only when the caller
    supplies context to compare against - otherwise applicability is
    treated as neutral, never silently penalized or rewarded. This is an
    advisory signal, never a ranking that selects a candidate by itself;
    `basis` always explains the number in plain language, and a
    zero-source corpus is reported honestly (score 0.0, explicit "no
    historical precedent found" basis) rather than omitted.
    """
    if not sources:
        return DesignPrior(score=0.0, historical_frequency=0, basis=[t("priors.summary.none")], supporting_sources=[])

    distinct_ids = sorted({s.source_id for s in sources})
    frequency_component = min(1.0, len(distinct_ids) / 3.0)
    evidence_component = sum(_quality_weight(s.evidence_grading) for s in sources) / len(sources)
    mechanistic_component = sum(s.mechanistic_weight for s in sources) / len(sources)

    if host is None and product is None:
        applicability_component = 0.6  # neutral: no query context supplied
    else:
        def _match_tier(s: PriorSourceRef) -> float:
            host_match = bool(host) and bool(s.host) and host.lower() in s.host.lower()
            product_match = bool(product) and bool(s.product) and product.lower() in s.product.lower()
            if host_match and product_match:
                return 1.0
            if host_match or product_match:
                return 0.5
            return 0.25
        applicability_component = sum(_match_tier(s) for s in sources) / len(sources)

    score = (
        0.30 * frequency_component + 0.30 * evidence_component
        + 0.25 * mechanistic_component + 0.15 * applicability_component
    )

    basis = [t(
        "priors.summary.found", n=len(distinct_ids),
        quality="high" if evidence_component >= 0.75 else ("mixed" if evidence_component >= 0.4 else "low"),
    )]
    basis.extend(t("priors.basis.source_line", source_id=s.source_id, quote=s.basis_quote, via=s.matched_via) for s in sources)

    return DesignPrior(score=round(score, 3), historical_frequency=len(distinct_ids), basis=basis, supporting_sources=distinct_ids)


def is_strong_source(ref: PriorSourceRef) -> bool:
    """Hard-graded (evidence_grading == "硬") sources are the only ones worth
    surfacing to the Evaluator pipeline as an `evidence_links` entry - a
    soft/unknown-graded prior stays in `historical_priors` for display but
    is not claimed as evidence strong enough to move an EvidenceEvaluator
    tier (doc04 §11's own "LLM critic/soft prediction ≠ evidence" discipline,
    applied here to historical precedent)."""
    return ref.evidence_grading in _HARD_GRADES


def to_evidence_link(ref: PriorSourceRef) -> dict[str, str]:
    """Shape consumed by `harness.engineering_design.evaluators.evidence`
    (`_SOURCE_TYPE_TO_TIER["historical_precedent"]`) - the channel that
    actually feeds the Evaluator pipeline, distinct from the richer
    `historical_priors`/`design_prior` payload kept for display/audit."""
    return {"source_type": "historical_precedent", "reference": ref.source_id, "detail": ref.basis_quote}
