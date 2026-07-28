"""TradeoffEvaluator (doc04 §2.5): qualitative, ordinal trade-off signal
per modification count/type - never a single fabricated composite score.
Growth/burden risk is an explicit *ordinal* estimate, tagged with its own
basis, not a unit-bearing prediction (that is `CounterfactualEvaluator`'s
job once a real model run exists).
"""
from __future__ import annotations

from typing import Any

from harness.engineering_design.evaluators.base import EvaluatorResult

_KNOCKOUT_LIKE = {"knockout", "knockdown", "attenuation"}


_BURDEN_SCALE = ("none", "low", "moderate", "elevated")


def build_tradeoff_profile(candidate: dict[str, Any]) -> dict[str, Any]:
    mods = candidate.get("genetic_modifications", [])
    n = len(mods)
    build_complexity = "low" if n <= 1 else ("medium" if n == 2 else "high")
    knockout_like = sum(1 for m in mods if m.get("operation") in _KNOCKOUT_LIKE)
    overexpression_like = sum(1 for m in mods if m.get("operation") in ("overexpression", "gene_insertion"))
    detail = "no modifications - baseline" if n == 0 else "qualitative: derived from modification count/type, not a computed prediction"

    if n == 0:
        growth_burden_risk = "none"
    elif (knockout_like >= 1 and overexpression_like >= 1) or overexpression_like >= 2:
        growth_burden_risk = "elevated"
        detail = "combines a knockout/attenuation with overexpression, or stacks multiple overexpressions" if knockout_like >= 1 else "multiple overexpression modifications add metabolic burden"
    elif n > 0:
        growth_burden_risk = "moderate"
    else:
        growth_burden_risk = "none"

    return {
        "build_complexity": build_complexity, "modification_count": n, "growth_burden_risk": growth_burden_risk,
        "growth_burden_detail": detail, "basis": "qualitative: no real model computation - ordinal estimate only",
        "evidence_tier": "expert_or_llm_judgment" if n else "curated_knowledge",
    }


def evaluate(candidate: dict[str, Any]) -> EvaluatorResult:
    profile = build_tradeoff_profile(candidate)
    findings = [
        f"build_complexity={profile['build_complexity']}", f"growth_burden_risk={profile['growth_burden_risk']}",
    ]
    return EvaluatorResult(
        evaluator="TradeoffEvaluator", status="pass", findings=findings, evidence_or_tool_refs=[],
        assumptions=[profile["basis"]], required_revisions=[], blocking=False,
    )
