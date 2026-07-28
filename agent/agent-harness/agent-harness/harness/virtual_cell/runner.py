"""Simulation execution (doc06 §3.6/§3.7/§6): runs the real `gem_fba`
adapter (never an LLM) for one scenario, persists the run - including
failure/infeasible/error outcomes, never discarded - and normalizes the raw
result into a `SimulationResult` with explicit `source_type` and honest
`unsupported_scales`/`not_modeled` endpoints.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any

from sqlalchemy.orm import Session

from harness.diagnosis.model_adapters.registry import get_adapter
from harness.ids import new_id, now
from harness.virtual_cell.models import SimulationResult, SimulationRun

# doc06 §3.7: each endpoint this adapter can genuinely produce, with its
# unit and the model-output field it comes from. Anything not in this list
# for a given run is `not_modeled`, never silently absent.
_ENDPOINT_SPEC = {
    "growth_rate": {"unit": "1/h", "source_key": "objective_value"},
    "substrate_uptake_glucose": {"unit": "mmol/gDW/h", "source_key": "named_exchange_fluxes.EX_glc__D_e", "sign_convention": "negative=uptake"},
    "oxygen_uptake": {"unit": "mmol/gDW/h", "source_key": "named_exchange_fluxes.EX_o2_e", "sign_convention": "negative=uptake"},
    "acetate_secretion": {"unit": "mmol/gDW/h", "source_key": "named_exchange_fluxes.EX_ac_e"},
    "co2_secretion": {"unit": "mmol/gDW/h", "source_key": "named_exchange_fluxes.EX_co2_e"},
    "ethanol_secretion": {"unit": "mmol/gDW/h", "source_key": "named_exchange_fluxes.EX_etoh_e"},
}
_NOT_MODELED_ENDPOINTS = (
    "biomass", "product_titer", "product_yield", "productivity", "stress_state",
    "transcriptome", "proteome", "metabolome", "resource_burden",
)


def compute_inputs_hash(model_id: str, reaction_bounds: dict, objective_reaction: str, config: dict) -> str:
    payload = json.dumps({"model_id": model_id, "reaction_bounds": reaction_bounds, "objective_reaction": objective_reaction, "config": config}, sort_keys=True)
    return hashlib.sha256(payload.encode()).hexdigest()[:24]


def find_existing_run(session: Session, simulation_case_id: str, inputs_hash: str) -> SimulationRun | None:
    """Idempotency (doc06 §11.2): a repeat request with the same model +
    inputs + config for the same case reuses the completed run rather than
    re-executing it."""
    from sqlalchemy import select

    return session.execute(
        select(SimulationRun).where(SimulationRun.simulation_case_id == simulation_case_id, SimulationRun.inputs_hash == inputs_hash)
    ).scalars().first()


def _get_nested(d: dict, dotted_key: str) -> Any:
    cur: Any = d
    for part in dotted_key.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def run_gem_fba_scenario(
    session: Session,
    *,
    simulation_case_id: str,
    scenario_label: str,
    baseline_state_id: str,
    perturbation_ids: list[str],
    compiled_intervention_ids: list[str],
    reaction_bounds: dict[str, dict[str, float]],
    objective_reaction: str | None = None,
    simulation_config: dict[str, Any] | None = None,
    model_id: str = "MREG-gem_fba",
    adapter_name: str = "gem_fba",
) -> tuple[SimulationRun, SimulationResult | None]:
    """`model_id`/`adapter_name` select which registered
    `harness.diagnosis.model_adapters` adapter actually runs (prompt §6.7 -
    a real dispatch, not a hardcoded single-model call: an earlier version
    of this function always called `get_adapter("gem_fba")` regardless of
    which model a `SimulationCase` had selected, which would have silently
    run e_coli_core even when a caller asked for `gem_fba_iml1515` - caught
    and fixed during Phase D). `objective_reaction=None` uses whatever
    objective the model's own file/definition already declares (both
    `e_coli_core` and `iML1515` ship a correct default objective; forcing
    one specific reaction id was itself an `e_coli_core`-only assumption
    baked into the old default)."""
    config = simulation_config or {"solver": "glpk (via optlang)", "random_seed": None, "replicate_index": 0}
    inputs_hash = compute_inputs_hash(adapter_name, reaction_bounds, objective_reaction or "", config)

    existing = find_existing_run(session, simulation_case_id, inputs_hash)
    if existing is not None:
        result = session.get(SimulationResult, existing.normalized_result_id) if existing.normalized_result_id else None
        return existing, result

    adapter = get_adapter(adapter_name)
    capability = adapter.detect_capability()
    started = now()

    if not capability.available:
        run = SimulationRun(
            model_run_id=new_id("SIMRUN"), simulation_case_id=simulation_case_id, scenario_label=scenario_label,
            model_id=model_id, model_version=adapter.model_version, adapter_version="", baseline_state_id=baseline_state_id,
            perturbation_ids=perturbation_ids, compiled_intervention_ids=compiled_intervention_ids,
            simulation_config=config, inputs_hash=inputs_hash, status="not_computed",
            started_at=started, finished_at=now(), log_summary=capability.reason, failure_reason=capability.reason, created_at=started,
        )
        session.add(run)
        session.flush()
        return run, None

    inputs: dict[str, Any] = {"reaction_bounds": reaction_bounds}
    if objective_reaction:
        inputs["objective_reaction"] = objective_reaction
    valid, errors = adapter.validate_input(inputs, {})
    if not valid:
        run = SimulationRun(
            model_run_id=new_id("SIMRUN"), simulation_case_id=simulation_case_id, scenario_label=scenario_label,
            model_id=model_id, model_version=adapter.model_version, adapter_version="", baseline_state_id=baseline_state_id,
            perturbation_ids=perturbation_ids, compiled_intervention_ids=compiled_intervention_ids,
            simulation_config=config, inputs_hash=inputs_hash, status="not_computed",
            started_at=started, finished_at=now(), log_summary="; ".join(errors), failure_reason="invalid_input", created_at=started,
        )
        session.add(run)
        session.flush()
        return run, None

    result_raw = adapter.run(inputs, {}, {})
    finished = now()
    run = SimulationRun(
        model_run_id=new_id("SIMRUN"), simulation_case_id=simulation_case_id, scenario_label=scenario_label,
        model_id=model_id, model_version=adapter.model_version,
        artifact_hash=result_raw.reproducibility_ref.get("cobra_version"), adapter_version=result_raw.reproducibility_ref.get("cobra_version", ""),
        baseline_state_id=baseline_state_id, perturbation_ids=perturbation_ids, compiled_intervention_ids=compiled_intervention_ids,
        simulation_config=config, inputs_hash=inputs_hash, status=result_raw.runtime_status,
        started_at=started, finished_at=finished, runtime_s=finished - started, log_summary=result_raw.log_summary,
        raw_output_ref=result_raw.outputs, failure_reason=None if result_raw.runtime_status == "optimal" else result_raw.runtime_status,
        created_at=started,
    )
    session.add(run)
    session.flush()

    if result_raw.runtime_status != "optimal":
        return run, None  # doc06 §2.10: failed run persisted, no fabricated result

    endpoints = []
    unsupported = []
    for name, spec in _ENDPOINT_SPEC.items():
        value = _get_nested(result_raw.outputs, spec["source_key"])
        if value is None:
            unsupported.append(name)
            continue
        endpoints.append({"name": name, "value": value, "unit": spec["unit"], "statistic": "point_estimate", "source_type": "model_output"})
    unsupported.extend(_NOT_MODELED_ENDPOINTS)

    result = SimulationResult(
        simulation_result_id=new_id("SIMRES"), model_run_id=run.model_run_id, initial_state_id=baseline_state_id,
        terminal_state={"objective_value": result_raw.outputs.get("objective_value")},
        trajectory_ref=None,  # steady-state FBA has no time trajectory
        endpoints=endpoints,
        endpoint_uncertainty={
            e["name"]: {
                "endpoint": e["name"], "estimate": e["value"], "unit": e["unit"], "interval": None, "interval_method": "none",
                "stochastic_variability": "not_applicable (deterministic steady-state LP solve)",
                "parameter_uncertainty": "unavailable (no sensitivity analysis performed for this run)",
                "initial_state_uncertainty": "unavailable",
                "model_structure_uncertainty": "unavailable (single fixed core-metabolism stoichiometry)",
                "intervention_mapping_uncertainty": "see CompiledIntervention.mapping_uncertainty",
                "domain_shift": "unknown", "calibration_status": "unavailable", "benchmark_id": None,
                "confidence_status": "unavailable",
            }
            for e in endpoints
        },
        supported_scales=["steady_state_flux"], unsupported_scales=unsupported,
        assumptions=["optimal-growth flux balance analysis assumption (maximization of biomass objective)"],
        warnings=list(result_raw.domain_flags), created_at=finished,
    )
    session.add(result)
    session.flush()
    run.normalized_result_id = result.simulation_result_id
    session.flush()
    return run, result
