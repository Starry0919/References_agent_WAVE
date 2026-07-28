"""`ModelRunRecord` persistence + cross-model convergence/conflict analysis
(doc03 4.9/3.9): every model invocation - real or unavailable - is
recorded with its capability status, inputs, solver/runtime status, and
reproducibility reference. Conflicting model results are preserved, never
averaged, voted, or silently resolved by the LLM (doc03 2.6).
"""
from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from harness.diagnosis.model_adapters.registry import get_adapter
from harness.diagnosis.models import ModelEvidenceAssessment, ModelRunRecord
from harness.ids import new_id, now
from harness.memory import event_types as et
from harness.memory.event_store import append_event, snapshot

MODEL_RUN_FIELDS = (
    "model_run_id", "diagnosis_session_id", "adapter_name", "model_name", "model_version", "capability_status",
    "inputs", "context", "constraints_objective_parameters", "solver", "runtime_status", "outputs", "uncertainty",
    "domain_flags", "sensitivity_variant_of", "reproducibility_ref", "log_summary", "started_at", "completed_at",
)


def execute_model_run(
    session: Session,
    *,
    project_id: str,
    diagnosis_session_id: str,
    adapter_name: str,
    inputs: dict[str, Any],
    context: dict[str, Any],
    constraints_objective_parameters: dict[str, Any],
    actor_id: str,
    sensitivity_variant_of: str | None = None,
) -> ModelRunRecord:
    adapter = get_adapter(adapter_name)
    capability = adapter.detect_capability()
    started = now()

    if not capability.available:
        record = ModelRunRecord(
            model_run_id=new_id("MRUN"), diagnosis_session_id=diagnosis_session_id, adapter_name=adapter_name,
            model_name=adapter.model_name, model_version=adapter.model_version, capability_status="unavailable",
            inputs=inputs, context=context, constraints_objective_parameters=constraints_objective_parameters,
            runtime_status="not_computed", log_summary=capability.reason, sensitivity_variant_of=sensitivity_variant_of,
            started_at=started, completed_at=now(),
        )
    else:
        valid, errors = adapter.validate_input(inputs, context)
        if not valid:
            record = ModelRunRecord(
                model_run_id=new_id("MRUN"), diagnosis_session_id=diagnosis_session_id, adapter_name=adapter_name,
                model_name=adapter.model_name, model_version=adapter.model_version, capability_status="out_of_domain",
                inputs=inputs, context=context, constraints_objective_parameters=constraints_objective_parameters,
                runtime_status="not_computed", domain_flags=errors, sensitivity_variant_of=sensitivity_variant_of,
                started_at=started, completed_at=now(),
            )
        else:
            result = adapter.run(inputs, context, constraints_objective_parameters)
            record = ModelRunRecord(
                model_run_id=new_id("MRUN"), diagnosis_session_id=diagnosis_session_id, adapter_name=adapter_name,
                model_name=adapter.model_name, model_version=adapter.model_version, capability_status="available",
                inputs=inputs, context=context, constraints_objective_parameters=constraints_objective_parameters,
                solver=result.solver, runtime_status=result.runtime_status, outputs=result.outputs,
                uncertainty=result.uncertainty, domain_flags=result.domain_flags, sensitivity_variant_of=sensitivity_variant_of,
                reproducibility_ref=result.reproducibility_ref, log_summary=result.log_summary,
                started_at=started, completed_at=now(),
            )

    session.add(record)
    session.flush()
    append_event(
        session, project_id=project_id, event_type=et.DIAGNOSIS_MODEL_RUN_RECORDED, entity_type="ModelRunRecord",
        entity_id=record.model_run_id, payload=snapshot(record, MODEL_RUN_FIELDS), actor_type="agent", actor_id=actor_id,
    )
    return record


def assess_cross_model_convergence(
    session: Session, *, diagnosis_session_id: str, model_run_ids: list[str]
) -> ModelEvidenceAssessment:
    runs = [session.get(ModelRunRecord, rid) for rid in model_run_ids]
    runs = [r for r in runs if r is not None]
    computed = [r for r in runs if r.runtime_status == "optimal"]

    ranking_stability: dict[str, Any] = {}
    if len(computed) < 2:
        convergence = "insufficient"
        explanation = f"only {len(computed)} of {len(runs)} requested model run(s) produced a usable ('optimal') result"
    else:
        objective_values = [r.outputs["objective_value"] for r in computed if "objective_value" in r.outputs]
        if len(objective_values) < 2:
            convergence = "insufficient"
            explanation = "not enough comparable objective values across runs"
        else:
            spread = max(objective_values) - min(objective_values)
            denom = abs(max(objective_values)) or 1.0
            rel_spread = spread / denom
            if rel_spread < 0.05:
                convergence = "convergent"
            elif rel_spread < 0.25:
                convergence = "partially_convergent"
            else:
                convergence = "conflicting"
            explanation = f"objective-value relative spread = {rel_spread:.2%} across {len(objective_values)} run(s)"

            best = max((r for r in computed if "objective_value" in r.outputs), key=lambda r: r.outputs["objective_value"])
            # A sensitivity variant of the best run staying the argmax
            # under a perturbed boundary/objective/parameter is the
            # concrete "ranking stability" signal doc03 4.9 asks to
            # record - not a synthetic metric with no basis in the runs.
            variants_of_best = [r for r in computed if r.sensitivity_variant_of == best.model_run_id]
            stable_under_variants = all(
                r.outputs.get("objective_value") is not None and r.outputs["objective_value"] <= best.outputs["objective_value"]
                for r in variants_of_best
            )
            ranking_stability = {
                "best_model_run_id": best.model_run_id, "relative_spread": rel_spread,
                "sensitivity_variants_checked": len(variants_of_best), "stable_under_checked_variants": stable_under_variants,
            }

    assessment = ModelEvidenceAssessment(
        assessment_id=new_id("MEVAL"), diagnosis_session_id=diagnosis_session_id, model_run_ids=model_run_ids,
        convergence_status=convergence, ranking_stability=ranking_stability, conflict_explanation=explanation,
        calibration_note="qualitative threshold-based comparison, not a calibrated statistical test", limitations="",
        created_at=now(),
    )
    session.add(assessment)
    session.flush()
    return assessment
