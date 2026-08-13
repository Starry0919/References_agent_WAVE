"""Model and Tool Evaluator (doc05 §4.4/§2.4/§3.4): normalizes whatever
real `CounterfactualRun` rows exist for a candidate (Problem 04's own
wrapper around `harness.diagnosis.model_adapters` - real cobrapy/
e_coli_core FBA, honestly-`unavailable` vEcoli/kinetic) into
`ModelEvaluationRecord`, adding the `domain_match` judgment doc05 requires
that `CounterfactualRun` itself does not carry. Never runs a model itself -
`harness/scientific_evaluation/service.py` never calls a model adapter
directly, only reads what Problem 04 already computed (or honestly did
not).
"""
from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from harness.diagnosis.model_adapters.registry import detect_all_capabilities
from harness.engineering_design.models import CandidateDesign, CounterfactualRun
from harness.ids import new_id, now
from harness.scientific_evaluation.models import EvaluationCase, ModelEvaluationRecord

# doc05 §3.4's run_status vocabulary. CounterfactualRun's own
# capability_status/runtime_status/status fields (doc04 §9) are mapped
# honestly, never re-labeled to look more complete than they are.
_CAPABILITY_TO_RUN_STATUS = {"unavailable": "unavailable", "out_of_domain": "out_of_domain"}


def _run_status_for(run: CounterfactualRun) -> str:
    if run.capability_status in _CAPABILITY_TO_RUN_STATUS:
        return _CAPABILITY_TO_RUN_STATUS[run.capability_status]
    if run.runtime_status == "optimal":
        return "computed"
    if run.runtime_status in ("infeasible", "unbounded", "error", "timeout"):
        return "failed"
    return "not_computed"


def _domain_match_for(run: CounterfactualRun) -> str:
    if run.capability_status == "out_of_domain" or run.domain_flags:
        return "poor"
    if run.capability_status == "unavailable":
        return "unknown"
    if run.runtime_status == "optimal":
        return "close"  # a real solve inside the adapter's declared domain, but this evaluator never re-derives biological applicability itself
    return "unknown"


def assess_model_records(
    session: Session, *, case: EvaluationCase, candidate: CandidateDesign,
) -> list[ModelEvaluationRecord]:
    runs = list(session.execute(select(CounterfactualRun).where(CounterfactualRun.design_id == candidate.design_id)).scalars())
    ts = now()
    rows: list[ModelEvaluationRecord] = []

    if not runs:
        row = ModelEvaluationRecord(
            record_id=new_id("MEVAL"), evaluation_id=case.evaluation_id, design_reference=candidate.design_id,
            adapter_name="none", model_or_tool_name="", version="", prediction_target="unspecified",
            input_references=[], parameters={}, assumptions=[], training_or_validity_domain="unknown",
            query_domain="unknown", domain_match="unknown", run_status="not_computed", result_reference=None,
            result_summary={}, uncertainty_available=False, uncertainty=None,
            warnings=["no model/tool run was requested or executed for this candidate - reporting honestly as not_computed"],
            provenance={"method": "model_evaluator_v1", "capabilities_at_assessment_time": {k: v.available for k, v in detect_all_capabilities().items()}},
            created_at=ts,
        )
        session.add(row)
        return [row]

    for run in runs:
        row = ModelEvaluationRecord(
            record_id=new_id("MEVAL"), evaluation_id=case.evaluation_id, design_reference=candidate.design_id,
            adapter_name=run.adapter_name, model_or_tool_name=run.model_name, version=run.model_version,
            prediction_target=str(run.request.get("intervention_or_query", {})), input_references=[run.run_id],
            parameters=run.request.get("intervention_or_query", {}).get("inputs", {}) if isinstance(run.request.get("intervention_or_query"), dict) else {},
            assumptions=run.assumptions, training_or_validity_domain="e_coli_core (cobrapy textbook GEM)" if run.adapter_name == "gem_fba" else "unknown",
            query_domain=str(case.frozen_context.get("chassis", "unknown")), domain_match=_domain_match_for(run),
            run_status=_run_status_for(run), result_reference=run.run_id, result_summary=run.outputs,
            uncertainty_available=run.uncertainty is not None, uncertainty=run.uncertainty,
            warnings=list(run.domain_flags), provenance={"method": "model_evaluator_v1", "source": "CounterfactualRun", "capability_status": run.capability_status},
            created_at=ts,
        )
        session.add(row)
        rows.append(row)

    session.flush()
    return rows


def honest_not_computed_count(records: list[ModelEvaluationRecord]) -> int:
    return sum(1 for r in records if r.run_status in ("not_computed", "unavailable"))
