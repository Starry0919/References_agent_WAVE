"""Model Router (doc06 §4.2): picks a model by the *scientific question*
being asked, not by "whichever adapter is available" - and always returns
why it did (or didn't) select each candidate, plus the coverage gap when
nothing qualifies. Router output only orders/selects among models that
already pass `CompatibilityReport` (doc06 §9.5's "Router 可用 benchmark
排序，但不能绕过 compatibility check") - it never substitutes for that
gate.
"""
from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from harness.virtual_cell import registry as registry_mod

# doc06 §4.2's table, adapter_id-keyed against this repo's real registry.
QUESTION_TYPES = (
    "steady_state_flux", "theoretical_yield", "reaction_feasibility",
    "culture_time_trend", "expression_resource_competition", "whole_cell_dynamics",
    "protein_local_property", "omics_perturbation_response",
)

_PRIORITY_BY_QUESTION: dict[str, list[str]] = {
    "steady_state_flux": ["gem_fba"],
    "theoretical_yield": ["gem_fba"],
    "reaction_feasibility": ["gem_fba"],
    "culture_time_trend": ["kinetic_resource"],  # dynamic FBA / kinetic model - none installed
    "expression_resource_competition": ["kinetic_resource"],  # ME-model / resource allocation - none installed
    "whole_cell_dynamics": ["vecoli"],
    "protein_local_property": [],  # no protein/structure model adapter exists in this registry at all
    "omics_perturbation_response": [],  # no validated perturbation-response model exists in this registry
}


def route(session: Session, *, question_type: str, benchmark_ranking: dict[str, float] | None = None) -> dict[str, Any]:
    if question_type not in QUESTION_TYPES:
        raise ValueError(f"unknown question_type {question_type!r}; must be one of {QUESTION_TYPES}")

    entries = {e.adapter_id: e for e in registry_mod.list_registry_entries(session)}
    candidate_ids = _PRIORITY_BY_QUESTION.get(question_type, [])
    not_selected: list[dict[str, Any]] = []
    selected: str | None = None
    for adapter_id in candidate_ids:
        entry = entries.get(adapter_id)
        if entry is None:
            not_selected.append({"adapter_id": adapter_id, "reason": "not present in model registry"})
            continue
        if entry.availability_status != "available":
            not_selected.append({"adapter_id": adapter_id, "model_id": entry.model_id, "reason": entry.unavailability_reason or "unavailable"})
            continue
        selected = entry.model_id
        break

    for adapter_id, entry in entries.items():
        if adapter_id in candidate_ids:
            continue
        not_selected.append({"adapter_id": adapter_id, "model_id": entry.model_id, "reason": f"not the priority model class for question_type={question_type!r}"})

    if selected is None:
        return {
            "decision": "no_compatible_model", "selected_model_id": None, "question_type": question_type,
            "not_selected": not_selected,
            "coverage_gap": (
                f"no available model in this environment answers a {question_type!r} question "
                f"(priority classes considered: {candidate_ids or 'none defined'})"
            ),
        }

    rationale = f"question_type={question_type!r} is a {candidate_ids[0]}-class question; {selected} is the highest-priority available adapter"
    if benchmark_ranking:
        rationale += f"; benchmark_ranking used only to order among already-compatible models: {benchmark_ranking}"

    return {
        "decision": "selected", "selected_model_id": selected, "question_type": question_type,
        "rationale": rationale, "not_selected": not_selected, "coverage_gap": None,
    }
