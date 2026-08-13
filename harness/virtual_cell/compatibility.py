"""Compatibility check (doc06 §2.4/§3.4/§4): must run and pass BEFORE any
`SimulationRun` is created for a given (model, cell state, perturbation)
triple. Never bypassed by a router's benchmark ranking (doc06 §9.5's own
rule) and never skipped because "the adapter will just fail anyway" - the
report itself is the auditable artifact of that check having happened.
"""
from __future__ import annotations

from harness.ids import new_id, now
from harness.virtual_cell.compiler import resolve_gene
from harness.virtual_cell.models import CompatibilityReport, ModelRegistryEntry, PerturbationSpec

_SUPPORTED_OPERATIONS = {"knockout", "deletion", "knockdown", "attenuation", "overexpression"}


def check_compatibility(
    *,
    simulation_case_id: str,
    registry_entry: ModelRegistryEntry,
    cell_state_id: str,
    chassis: dict,
    perturbations: list[PerturbationSpec],
) -> CompatibilityReport:
    ts = now()
    if registry_entry.availability_status != "available":
        return CompatibilityReport(
            compatibility_id=new_id("COMPAT"), simulation_case_id=simulation_case_id, model_id=registry_entry.model_id,
            cell_state_id=cell_state_id, perturbation_ids=[p.perturbation_id for p in perturbations],
            organism_match="unknown", strain_match="unknown", condition_match="unknown", perturbation_support={},
            input_completeness="unknown", output_coverage=[], domain_status="unavailable",
            blocking_reasons=[registry_entry.unavailability_reason or "model reported unavailable"],
            non_blocking_assumptions=[], decision="unavailable", created_at=ts,
        )

    blocking: list[str] = []
    assumptions: list[str] = []
    perturbation_support: dict[str, str] = {}

    organism = chassis.get("organism", "")
    organism_match = "close" if organism and organism.lower().startswith("escherichia coli") else "unknown"
    if organism and not organism.lower().startswith("escherichia coli"):
        blocking.append(f"chassis organism {organism!r} does not match model organism {registry_entry.organism!r}")

    strain = chassis.get("strain", "")
    strain_match = "partial" if strain else "unknown"
    if strain and "k-12" not in strain.lower():
        assumptions.append(f"strain {strain!r} approximated by the model's K-12-derived core-metabolism parameterization")

    if registry_entry.model_type != "gem_fba":
        blocking.append(f"no compiler exists for model_type={registry_entry.model_type!r} this round")

    from harness.virtual_cell.compiler import _load_gem_model  # local import: avoid loading cobra unless gem_fba path taken

    model = _load_gem_model(registry_entry.model_id) if registry_entry.model_type == "gem_fba" else None
    for p in perturbations:
        op = (p.operation or "").strip().lower()
        if op not in _SUPPORTED_OPERATIONS:
            perturbation_support[p.perturbation_id] = "unsupported"
            blocking.append(f"perturbation {p.perturbation_id} operation {op!r} is not supported by {registry_entry.model_id}")
            continue
        if model is None:
            perturbation_support[p.perturbation_id] = "unsupported"
            continue
        gene = resolve_gene(model, p.target)
        if gene is None:
            perturbation_support[p.perturbation_id] = "unsupported"
            blocking.append(f"gene {p.target!r} is out of domain for {registry_entry.model_id} (not in its {len(model.genes)}-gene set)")
        elif op == "knockout" or op == "deletion":
            perturbation_support[p.perturbation_id] = "supported"
        else:
            perturbation_support[p.perturbation_id] = "approximate"
            assumptions.append(f"{op} on {p.target!r} is approximated as a reaction-bound scaling, not a measured expression change")

    output_coverage = list(registry_entry.output_modalities)

    if blocking:
        decision = "out_of_domain" if any("out of domain" in b or "does not match" in b for b in blocking) else "unsupported"
        domain_status = decision
    elif assumptions:
        decision = "compatible_with_assumptions"
        domain_status = "in_domain_with_assumptions"
    else:
        decision = "compatible"
        domain_status = "in_domain"

    return CompatibilityReport(
        compatibility_id=new_id("COMPAT"), simulation_case_id=simulation_case_id, model_id=registry_entry.model_id,
        cell_state_id=cell_state_id, perturbation_ids=[p.perturbation_id for p in perturbations],
        organism_match=organism_match, strain_match=strain_match, condition_match="close",
        perturbation_support=perturbation_support, input_completeness="complete" if perturbations else "no_perturbations_requested",
        output_coverage=output_coverage, domain_status=domain_status, blocking_reasons=blocking,
        non_blocking_assumptions=assumptions, decision=decision, created_at=ts,
    )
