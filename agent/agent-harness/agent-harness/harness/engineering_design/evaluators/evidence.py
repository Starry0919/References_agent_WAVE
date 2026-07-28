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
}


def _tier_for(link: dict[str, Any]) -> str:
    return _SOURCE_TYPE_TO_TIER.get(link.get("source_type", "unknown"), "unknown")


def evaluate(candidate: dict[str, Any]) -> EvaluatorResult:
    mods = candidate.get("genetic_modifications", [])
    all_links = [l for m in mods for l in m.get("evidence_links", [])] or list(candidate.get("evidence_links", []))
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
