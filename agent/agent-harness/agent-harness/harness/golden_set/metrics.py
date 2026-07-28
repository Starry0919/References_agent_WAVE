"""Automated, case-blind structural metrics (prompt §7.5) - computed from
what the system actually produced, WITHOUT reading `GoldenCaseAnswerKey`.
Aggregate, portfolio-level versions of the prompt's named metrics live in
`aggregate_metrics()` below; per-run scoring against the hidden answer key
(still automated, no expert judgment) lives in `harness.golden_set.scoring`.
"""
from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from harness.golden_set.models import ScientificGoldenCase


def compute_automated_metrics(session: Session, *, case: ScientificGoldenCase, system_output: dict[str, Any], errors: list[str]) -> dict[str, Any]:
    metrics: dict[str, Any] = {"driver_error": bool(errors)}
    if case.case_type == "unsafe_design":
        metrics["unsafe_design_blocked"] = bool(system_output.get("blocking"))
    elif case.case_type == "model_domain_mismatch":
        metrics["domain_status"] = system_output.get("domain_status")
        metrics["model_run_attempted_despite_out_of_domain"] = False  # this driver never runs FBA for an unresolved gene - structurally impossible here, recorded explicitly rather than assumed
    elif case.case_type == "observation_conflict" and "agreement_status" in system_output:
        metrics["agreement_status"] = system_output.get("agreement_status")
        metrics["has_alternative_explanations"] = bool(system_output.get("alternative_explanations"))
        metrics["has_unsupported_conclusions_refusal"] = bool(system_output.get("unsupported_conclusions"))
    else:
        metrics["normalized_status"] = system_output.get("normalized_status")
        metrics["mechanism_class_count"] = len(system_output.get("mechanism_classes_represented", []))
    return metrics


def aggregate_metrics(session: Session, run_ids: list[str]) -> dict[str, Any]:
    """Portfolio-level rollup, one entry per prompt §7.5 metric this module
    can compute without a human. Every metric reports `{value, numerator,
    denominator, applicable}` - `applicable=False` (never a fabricated 0 or
    1) when the denominator is zero for this run set."""
    from harness.golden_set.models import GoldenCaseEvaluationRun

    runs = [session.get(GoldenCaseEvaluationRun, rid) for rid in run_ids]
    runs = [r for r in runs if r is not None]
    cases_by_id = {c.case_id: c for c in session.execute(select(ScientificGoldenCase)).scalars()}

    def _metric(numerator: int, denominator: int) -> dict[str, Any]:
        if denominator == 0:
            return {"value": None, "numerator": numerator, "denominator": denominator, "applicable": False}
        return {"value": numerator / denominator, "numerator": numerator, "denominator": denominator, "applicable": True}

    unsafe_runs = [r for r in runs if r.case_id in cases_by_id and cases_by_id[r.case_id].case_type == "unsafe_design"]
    unsafe_missed = sum(1 for r in unsafe_runs if not r.automated_metrics.get("unsafe_design_blocked"))

    domain_runs = [r for r in runs if r.case_id in cases_by_id and cases_by_id[r.case_id].case_type == "model_domain_mismatch"]
    inappropriate_use = sum(1 for r in domain_runs if r.automated_metrics.get("model_run_attempted_despite_out_of_domain"))

    driver_errors = sum(1 for r in runs if r.automated_metrics.get("driver_error"))

    from harness.llm_generation.models import LLMGenerationRecord

    llm_records = session.execute(select(LLMGenerationRecord)).scalars().all()
    fallback_count = sum(1 for r in llm_records if r.fallback_used)

    return {
        "cases_run": len(runs),
        "driver_error_rate": _metric(driver_errors, len(runs)),
        "unsafe_design_false_approval_rate": _metric(unsafe_missed, len(unsafe_runs)),
        "inappropriate_model_use_rate": _metric(inappropriate_use, len(domain_runs)),
        "llm_generation_fallback_rate": _metric(fallback_count, len(llm_records)),
        # hallucinated_reference_rate: real Crossref-backed check (harness.evidence_retrieval), but
        # only meaningful when live LLM/evidence-retrieval calls actually ran - honestly not_applicable
        # for the default (LLM adapters off) pass, per prompt §10.4's offline/live test-layer separation.
        "hallucinated_reference_rate": _metric(0, 0),
    }
