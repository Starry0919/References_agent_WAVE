"""Real candidate-specific baseline-vs-candidate GEM evaluation."""
from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from harness.diagnosis.model_adapters.registry import get_adapter
from harness.engineering_design.models import CandidateDesign, EngineeringDesignProject, ModelEvaluation
from harness.ids import new_id, now


def evaluate_candidate_fba(db: Session, *, project_id: str, candidate_id: str, target_product: str,
                           product_reaction: str, biomass_reaction: str,
                           medium_bounds: dict[str, dict[str, float]], oxygen_condition: str,
                           gene_knockouts: list[str] | None, actor_id: str,
                           adapter_name: str = "gem_fba_iml1515") -> ModelEvaluation:
    candidate = db.get(CandidateDesign, candidate_id)
    if candidate is None: raise ValueError(f"no such candidate: {candidate_id}")
    design_project = db.get(EngineeringDesignProject, candidate.design_project_id)
    if design_project is None or design_project.project_id != project_id:
        raise ValueError("candidate does not belong to project")
    declared_knockouts = [str(x.get("target_identifier")) for x in candidate.genetic_modifications if x.get("operation") == "knockout" and x.get("target_identifier")]
    gene_knockouts = declared_knockouts if gene_knockouts is None else gene_knockouts
    if not set(gene_knockouts).issubset(set(declared_knockouts)):
        raise ValueError("model intervention must be declared by the candidate")
    adapter = get_adapter(adapter_name); capability = adapter.detect_capability()
    assumptions = ["steady state", "stoichiometric feasibility only", "gene-reaction rules supplied by model"]
    limitations = ["does not validate regulation, toxicity, folding, transporter kinetics, or in-vivo efficacy"]
    if not capability.available:
        row = ModelEvaluation(model_evaluation_id=new_id("CMEVAL"), project_id=project_id, candidate_id=candidate_id,
            model_id=adapter_name, model_version=adapter.model_version, model_scope="out_of_model_scope", medium=medium_bounds,
            substrate_bounds=medium_bounds, oxygen_condition=oxygen_condition, objective=product_reaction, target_product=target_product,
            intervention_constraints={"gene_knockouts": gene_knockouts}, runtime_status="not_computed", assumptions=assumptions,
            limitations=[*limitations, capability.reason], provenance={"actor_id": actor_id}, created_at=now())
        db.add(row); db.flush(); return row

    def run(objective: str, knockouts: list[str], fva: bool = False):
        inputs={"reaction_bounds": medium_bounds, "gene_knockouts": knockouts, "objective_reaction": objective}
        if fva: inputs["fva_reactions"]=[biomass_reaction, product_reaction]
        valid, errors=adapter.validate_input(inputs,{})
        if not valid: raise ValueError("; ".join(errors))
        return adapter.run(inputs, {}, {"target_product": target_product, "condition": oxygen_condition})

    bg=run(biomass_reaction, []); cg=run(biomass_reaction, gene_knockouts)
    bp=run(product_reaction, []); cp=run(product_reaction, gene_knockouts, True)
    statuses={bg.runtime_status,cg.runtime_status,bp.runtime_status,cp.runtime_status}
    def val(result): return result.outputs.get("objective_value") if result.runtime_status == "optimal" else None
    baseline_product=val(bp); candidate_product=val(cp)
    row = ModelEvaluation(model_evaluation_id=new_id("CMEVAL"), project_id=project_id, candidate_id=candidate_id,
        model_id=adapter_name, model_version=adapter.model_version, model_scope="stoichiometric_gem",
        medium=medium_bounds, substrate_bounds=medium_bounds, oxygen_condition=oxygen_condition,
        objective=product_reaction, target_product=target_product, intervention_constraints={"gene_knockouts": gene_knockouts},
        baseline_growth=val(bg), candidate_growth=val(cg), baseline_product_flux=baseline_product,
        candidate_product_flux=candidate_product, fva_summary=cp.outputs.get("fva", {}),
        key_flux_changes={"product_delta": None if baseline_product is None or candidate_product is None else candidate_product-baseline_product},
        runtime_status="optimal" if statuses=={"optimal"} else "partial_or_failed", infeasible="infeasible" in statuses,
        assumptions=assumptions, limitations=limitations, provenance={"actor_id":actor_id,"adapter_reproducibility":cp.reproducibility_ref}, created_at=now())
    db.add(row); db.flush(); return row
