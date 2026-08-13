"""EvidenceEvaluator (doc04 §11): classifies every evidence link's source
into the doc's evidence-tier vocabulary and flags claims backed only by
`expert_or_llm_judgment` or nothing at all - never silently treats those as
equivalent to `experimental_evidence`/`model_computation`.
"""
from __future__ import annotations

from typing import Any

from harness.engineering_design.evaluators.base import EvaluatorResult
from harness.engineering_design.models import EVIDENCE_TIERS

_SOURCE_TYPE_TO_TIER = {
    "curated_knowledge": "curated_knowledge",
    "diagnosis_hypothesis": "general_biological_knowledge",
    "model_computation": "model_computation",
    "experimental_evidence": "experimental_evidence",
    "expert_or_llm_judgment": "expert_or_llm_judgment",
    # harness/engineering_design/strategy_prior_retrieval.py::to_evidence_link -
    # only hard-graded (evidence_grading == "硬") DDR/rule precedent reaches
    # this tier; softer priors stay in the strategy's `historical_priors`
    # display payload and never appear as an evidence_links entry at all.
    "historical_precedent": "unknown",  # legacy rows: never auto-promote prior to evidence
}


def _tier_for(link: dict[str, Any]) -> str:
    return _SOURCE_TYPE_TO_TIER.get(link.get("source_type", "unknown"), "unknown")


def all_evidence_links(candidate: dict[str, Any]) -> list[dict[str, Any]]:
    """Same aggregation `evaluate()` uses: per-modification `evidence_links`
    when present, else the candidate's own top-level list - one place this
    logic lives, reused by `ConfidenceEvaluator` and `decision.py`'s
    `evidence_strength` Pareto dimension so neither re-derives it."""
    mods = candidate.get("genetic_modifications", [])
    return [l for m in mods for l in m.get("evidence_links", [])] or list(candidate.get("evidence_links", []))


def strongest_tier(candidate: dict[str, Any]) -> str:
    """The best (lowest-index, per `EVIDENCE_TIERS`' best-to-worst order)
    tier among the candidate's evidence links, or `"unknown"` when there are
    none - never a fabricated default."""
    tiers = [_tier_for(l) for l in all_evidence_links(candidate)]
    ranked = [t for t in tiers if t in EVIDENCE_TIERS]
    if not ranked:
        return "unknown"
    return min(ranked, key=EVIDENCE_TIERS.index)


def evaluate(candidate: dict[str, Any]) -> EvaluatorResult:
    all_links = all_evidence_links(candidate)
    tiers = [_tier_for(l) for l in all_links]

    findings = [f"{tiers.count(t)} evidence link(s) at tier {t!r}" for t in EVIDENCE_TIERS if t in tiers]
    required_revisions: list[str] = []

    if not all_links:
        return EvaluatorResult(
            evaluator="EvidenceEvaluator", status="insufficient_evidence",
            findings=["no evidence links recorded for this candidate's modifications"],
            evidence_or_tool_refs=[], assumptions=[],
            required_revisions=["attach at least curated_knowledge or diagnosis-hypothesis evidence before evaluation can proceed"],
            blocking=candidate.get("portfolio_role") != "reference_or_control",
        )

    strong = {"experimental_evidence", "model_computation", "curated_knowledge"}
    if not any(t in strong for t in tiers):
        required_revisions.append("no evidence link rises above general_biological_knowledge/expert_or_llm_judgment - "
                                   "seek curated or model-computed support before treating this as build-ready")
        status = "warning"
    else:
        status = "pass"

    return EvaluatorResult(
        evaluator="EvidenceEvaluator", status=status, findings=findings,
        evidence_or_tool_refs=[str(l.get("reference", "")) for l in all_links], assumptions=[],
        required_revisions=required_revisions, blocking=False,
    )
