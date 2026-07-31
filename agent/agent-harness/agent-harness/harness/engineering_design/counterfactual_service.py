"""Standardized counterfactual request/result (doc04 §9): reuses
`harness.diagnosis.model_adapters` (the real cobrapy/e_coli_core FBA
adapter, plus the vEcoli/kinetic adapters that honestly report
`unavailable`) - the same registry Problem 03 Phase 3 built, not a second
model-execution stack. A missing/incapable adapter always yields
`not_computed`, never a fabricated number.

`default_gem_inputs_for_candidate` is a best-effort, narrow mapping from a
handful of curated central-carbon-metabolism genes to their `e_coli_core`
reaction ids, so a precursor-supply-style knockout/overexpression candidate
can get a REAL FBA growth-rate counterfactual when it happens to fall in
this small model's domain. Anything outside that mapping is left for the
caller to supply explicitly; the adapter's own `validate_input` honestly
reports `out_of_domain` rather than a crash or a guess if the mapping is
wrong or incomplete.
"""
from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from harness.diagnosis.model_adapters.gem_fba import BIOMASS_OBJECTIVE_ECOLI_CORE, GENE_TO_REACTION_BOUND_HINT
from harness.diagnosis.model_adapters.registry import get_adapter
from harness.engineering_design.models import CandidateDesign, EngineeringDesignProject
from harness.ids import new_id, now
from harness.memory import event_types as et
from harness.memory.event_store import append_event

RUN_SNAPSHOT_FIELDS = (
    "run_id", "design_id", "request", "adapter_name", "model_name", "model_version", "capability_status",
    "runtime_status", "outputs", "uncertainty", "domain_flags", "assumptions", "status",
    "qualitative_expectation_text", "reproducibility_ref", "log_summary", "created_at",
)

# Kept as module-level aliases (not inlined at each call site below) so this
# file's own diff stays minimal if the shared mapping ever needs a
# service-local override; the values themselves now live in
# `harness.diagnosis.model_adapters.gem_fba` as the single source of truth.
_GENE_TO_REACTION_BOUND_HINT = GENE_TO_REACTION_BOUND_HINT
_BIOMASS_OBJECTIVE = BIOMASS_OBJECTIVE_ECOLI_CORE


def default_gem_inputs_for_candidate(candidate: CandidateDesign) -> dict[str, Any] | None:
    """Returns `gem_fba` adapter inputs if at least one modification maps
    into `_GENE_TO_REACTION_BOUND_HINT`; `None` if nothing on this
    candidate is in this narrow model's known domain (caller should then
    either supply its own inputs or accept `not_computed`)."""
    bounds: dict[str, Any] = {}
    for m in candidate.genetic_modifications:
        hint = _GENE_TO_REACTION_BOUND_HINT.get(m.get("target_identifier", ""))
        if hint is None:
            continue
        bound = hint.get(m.get("operation", ""))
        if bound is not None:
            bounds[hint["reaction"]] = bound
    if not bounds:
        return None
    return {"reaction_bounds": bounds, "objective_reaction": _BIOMASS_OBJECTIVE}


def request_counterfactual(
    session: Session,
    *,
    design_id: str,
    adapter_name: str,
    actor_id: str,
    inputs: dict[str, Any] | None = None,
    context: dict[str, Any] | None = None,
    constraints_objective_parameters: dict[str, Any] | None = None,
    intervention_or_query: dict[str, Any] | None = None,
):
    candidate = session.get(CandidateDesign, design_id)
    if candidate is None:
        raise ValueError(f"no such candidate design: {design_id}")
    proj = session.get(EngineeringDesignProject, candidate.design_project_id)

    resolved_inputs = inputs if inputs is not None else (default_gem_inputs_for_candidate(candidate) if adapter_name == "gem_fba" else None) or {}
    request_payload = {"intervention_or_query": intervention_or_query or {"design_id": design_id, "inputs": resolved_inputs}}

    adapter = get_adapter(adapter_name)
    capability = adapter.detect_capability()

    from harness.engineering_design.models import CounterfactualRun  # local import: avoids a models<->service cycle at module load

    if not capability.available:
        run = CounterfactualRun(
            run_id=new_id("CFRUN"), design_id=design_id, request=request_payload, adapter_name=adapter_name,
            model_name=adapter.model_name, model_version=adapter.model_version, capability_status="unavailable",
            runtime_status="not_computed", outputs={}, status="not_computed", log_summary=capability.reason, created_at=now(),
        )
    else:
        valid, errors = adapter.validate_input(resolved_inputs, context or {})
        if not valid:
            run = CounterfactualRun(
                run_id=new_id("CFRUN"), design_id=design_id, request=request_payload, adapter_name=adapter_name,
                model_name=adapter.model_name, model_version=adapter.model_version, capability_status="out_of_domain",
                runtime_status="not_computed", outputs={}, domain_flags=errors, status="not_computed", created_at=now(),
            )
        else:
            result = adapter.run(resolved_inputs, context or {}, constraints_objective_parameters or {})
            run = CounterfactualRun(
                run_id=new_id("CFRUN"), design_id=design_id, request=request_payload, adapter_name=adapter_name,
                model_name=adapter.model_name, model_version=adapter.model_version, capability_status="available",
                runtime_status=result.runtime_status, outputs=result.outputs, uncertainty=result.uncertainty,
                domain_flags=result.domain_flags, status="computed" if result.runtime_status == "optimal" else "not_computed",
                reproducibility_ref=result.reproducibility_ref, log_summary=result.log_summary, created_at=now(),
            )

    session.add(run)
    candidate.counterfactual_requests = candidate.counterfactual_requests + [request_payload]
    candidate.counterfactual_results = candidate.counterfactual_results + [{
        "run_id": run.run_id, "adapter_name": run.adapter_name, "runtime_status": run.runtime_status,
        "capability_status": run.capability_status, "outputs": run.outputs,
    }]
    session.flush()
    append_event(
        session, project_id=proj.project_id, event_type=et.DESIGN_COUNTERFACTUAL_RUN_RECORDED, entity_type="CounterfactualRun",
        entity_id=run.run_id, payload={f: getattr(run, f) for f in RUN_SNAPSHOT_FIELDS}, actor_type="agent", actor_id=actor_id,
    )
    return run
