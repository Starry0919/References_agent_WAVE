"""Observation ingestion + residual computation (doc06 §9.2/§9.3/§3.11).
`harness.experiments.models.Observation` is reused directly for the scalar
phenotype endpoints this round's adapters actually produce (growth rate,
uptake/secretion fluxes) - doc06 §3.10's OmicsObservation maps onto that
existing table rather than a parallel schema. Residuals are computed by
code, never by an LLM; a context/unit/QC mismatch blocks residual creation
entirely (doc06 §2.9/§9.2), it does not fabricate a "close enough" number.
"""
from __future__ import annotations

from harness.experiments.models import Observation
from harness.ids import new_id, now
from harness.memory import event_types as et
from harness.memory.event_store import append_event
from harness.virtual_cell.guards import SimulationGuardError, assert_context_matches_before_residual
from harness.virtual_cell.models import CounterfactualComparison, PredictionResidual, SimulationResult, SimulationRun, ValidationPlanItem


def _find_predicted_endpoint(result: SimulationResult, endpoint: str) -> dict | None:
    for e in result.endpoints:
        if e["name"] == endpoint:
            return e
    return None


def _check_context(observation: Observation, cell_state_environment: dict, predicted_unit: str) -> tuple[bool, str]:
    if observation.qc_status != "passed":
        return False, f"observation qc_status={observation.qc_status!r} (must be 'passed')"
    if observation.unit != predicted_unit:
        return False, f"unit mismatch: observation unit={observation.unit!r} vs prediction unit={predicted_unit!r}"
    cond = observation.condition_ref or {}
    for key in ("medium", "carbon_source"):
        if key in cond and key in cell_state_environment and cond[key] != cell_state_environment[key]:
            return False, f"condition mismatch on {key!r}: observation={cond[key]!r} vs prediction cell state={cell_state_environment[key]!r}"
    return True, "matched"


def compute_residual(
    session, *, simulation_case_id: str, validation_item_id: str, observation_id: str, actor_id: str,
) -> PredictionResidual:
    item = session.get(ValidationPlanItem, validation_item_id)
    if item is None:
        raise ValueError(f"no such validation plan item: {validation_item_id}")
    observation = session.get(Observation, observation_id)
    if observation is None:
        raise ValueError(f"no such observation: {observation_id}")
    comparison = session.get(CounterfactualComparison, item.comparison_id)
    if comparison is None:
        raise ValueError(f"no such comparison: {item.comparison_id}")
    candidate_run = session.get(SimulationRun, comparison.candidate_run_id)
    if candidate_run is None or candidate_run.normalized_result_id is None:
        raise ValueError("candidate run has no normalized result to compare against")
    result = session.get(SimulationResult, candidate_run.normalized_result_id)
    predicted = _find_predicted_endpoint(result, item.endpoint)
    if predicted is None:
        raise ValueError(f"endpoint {item.endpoint!r} was not modeled by the candidate run - no residual can be computed")

    from harness.virtual_cell.cell_state_service import get_cell_state

    cell_state = get_cell_state(session, candidate_run.baseline_state_id)
    environment = cell_state.environment if cell_state else {}

    context_match, mismatch_status = _check_context(observation, environment, predicted["unit"])
    try:
        assert_context_matches_before_residual(context_match, mismatch_status)
    except SimulationGuardError:
        raise

    predicted_value = predicted["value"]
    observed_value = observation.value
    residual_value = observed_value - predicted_value
    relative_error = residual_value / abs(predicted_value) if predicted_value != 0 else None

    recommended_level = None
    if relative_error is not None:
        if abs(relative_error) >= 0.5:
            recommended_level = "parameter_calibration"
        elif abs(relative_error) >= 0.1:
            recommended_level = "input_state"

    residual = PredictionResidual(
        residual_id=new_id("PRESID"), simulation_case_id=simulation_case_id, validation_item_id=validation_item_id,
        prediction_run_id=candidate_run.model_run_id, observation_id=observation_id, endpoint=item.endpoint,
        predicted_value=predicted_value, observed_value=observed_value, unit=predicted["unit"], residual=residual_value,
        relative_error=relative_error, measurement_uncertainty=observation.uncertainty,
        prediction_uncertainty=result.endpoint_uncertainty.get(item.endpoint), context_match=True, mismatch_status="matched",
        possible_causes=[], recommended_update_level=recommended_level, created_at=now(),
    )
    session.add(residual)
    item.status = "resolved"
    session.flush()
    append_event(
        session, project_id=_project_id_for_case(session, simulation_case_id), event_type=et.VC_RESIDUAL_COMPUTED,
        entity_type="PredictionResidual", entity_id=residual.residual_id,
        payload={"endpoint": residual.endpoint, "residual": residual.residual, "relative_error": residual.relative_error, "recommended_update_level": residual.recommended_update_level},
        actor_type="agent", actor_id=actor_id,
    )
    return residual


def _project_id_for_case(session, simulation_case_id: str) -> str:
    from harness.virtual_cell.models import SimulationCase

    case = session.get(SimulationCase, simulation_case_id)
    return case.project_id if case else "unknown"
