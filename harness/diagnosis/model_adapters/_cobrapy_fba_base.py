"""Shared cobrapy FBA execution logic for every real GEM adapter in this
registry (`gem_fba.py`'s `e_coli_core`, `gem_fba_iml1515.py`'s `iML1515`) -
one real model-execution stack, not one per model file (prompt §6.7: "不得
重复实现现有 core FBA adapter"). Each concrete adapter only supplies its own
model loader/cache and identity fields; `validate_input`/`run` below are
verbatim-shared.
"""
from __future__ import annotations

from typing import Any, Callable

from harness.diagnosis.model_adapters.base import ModelRunResult

_NAMED_EXCHANGE_IDS = (
    "EX_glc__D_e", "EX_o2_e", "EX_co2_e", "EX_ac_e", "EX_etoh_e",
    "EX_for_e", "EX_lac__D_e", "EX_succ_e", "EX_pyr_e",
)


class CobrapyFbaAdapterMixin:
    """Mixed into a `ModelAdapter` subclass. The subclass must implement
    `_get_model() -> cobra.Model` (its own cached loader) and set the usual
    `name`/`model_name`/`model_version` class attributes."""

    def _get_model(self):  # pragma: no cover - overridden by subclasses
        raise NotImplementedError

    def validate_input(self, inputs: dict[str, Any], context: dict[str, Any]) -> tuple[bool, list[str]]:
        errors: list[str] = []
        try:
            model = self._get_model()
        except Exception as e:  # noqa: BLE001
            return False, [f"model unavailable: {e}"]
        valid_ids = {r.id for r in model.reactions}
        for rxn_id in inputs.get("reaction_bounds", {}):
            if rxn_id not in valid_ids:
                errors.append(f"unknown reaction id {rxn_id!r} for {self.model_version}")
        objective_reaction = inputs.get("objective_reaction")
        if objective_reaction and objective_reaction not in valid_ids:
            errors.append(f"unknown objective reaction {objective_reaction!r}")
        return not errors, errors

    def run(
        self, inputs: dict[str, Any], context: dict[str, Any], constraints_objective_parameters: dict[str, Any]
    ) -> ModelRunResult:
        model = self._get_model().copy()  # never mutate the cached shared model
        domain_flags: list[str] = []

        for rxn_id, bounds in inputs.get("reaction_bounds", {}).items():
            if rxn_id not in {r.id for r in model.reactions}:
                domain_flags.append(f"skipped unknown reaction {rxn_id}")
                continue
            rxn = model.reactions.get_by_id(rxn_id)
            try:
                if "lower" in bounds and "upper" in bounds:
                    rxn.bounds = (bounds["lower"], bounds["upper"])
                elif "lower" in bounds:
                    rxn.lower_bound = bounds["lower"]
                elif "upper" in bounds:
                    rxn.upper_bound = bounds["upper"]
            except ValueError as e:
                return ModelRunResult(
                    runtime_status="error", log_summary=f"invalid bounds for reaction {rxn_id}: {e}",
                    solver="glpk (via optlang)", domain_flags=domain_flags,
                )

        for gene_id in inputs.get("gene_knockouts", []):
            gene = model.genes.get_by_id(gene_id) if gene_id in {g.id for g in model.genes} else None
            if gene is None:
                domain_flags.append(f"skipped unknown gene {gene_id} for {self.model_version}")
                continue
            gene.knock_out()

        objective_reaction = inputs.get("objective_reaction")
        if objective_reaction:
            try:
                model.objective = objective_reaction
            except Exception as e:  # noqa: BLE001
                domain_flags.append(f"failed to set objective {objective_reaction}: {e}")

        try:
            solution = model.optimize()
        except Exception as e:  # noqa: BLE001
            return ModelRunResult(runtime_status="error", log_summary=str(e), solver="glpk (via optlang)", domain_flags=domain_flags)

        status_map = {"optimal": "optimal", "infeasible": "infeasible", "unbounded": "unbounded"}
        runtime_status = status_map.get(solution.status, "error")

        outputs: dict[str, Any] = {}
        if runtime_status == "optimal":
            outputs["objective_value"] = float(solution.objective_value)
            top_fluxes = solution.fluxes.abs().sort_values(ascending=False).head(15)
            outputs["flux_distribution_top15"] = {rid: float(solution.fluxes[rid]) for rid in top_fluxes.index}
            model_reaction_ids = {r.id for r in model.reactions}
            outputs["named_exchange_fluxes"] = {
                rid: float(solution.fluxes[rid]) for rid in _NAMED_EXCHANGE_IDS if rid in model_reaction_ids
            }
            fva_reactions = [rid for rid in inputs.get("fva_reactions", []) if rid in model_reaction_ids]
            if fva_reactions:
                try:
                    from cobra.flux_analysis import flux_variability_analysis
                    fva = flux_variability_analysis(model, reaction_list=fva_reactions, fraction_of_optimum=float(inputs.get("fva_fraction", .9)))
                    outputs["fva"] = {rid: {"minimum": float(fva.loc[rid, "minimum"]), "maximum": float(fva.loc[rid, "maximum"])} for rid in fva_reactions}
                except Exception as exc:  # FBA result remains valid; FVA failure is explicit.
                    domain_flags.append(f"FVA unavailable: {type(exc).__name__}: {exc}")

        return ModelRunResult(
            runtime_status=runtime_status, outputs=outputs, domain_flags=domain_flags, solver="glpk (via optlang)",
            log_summary=f"cobrapy FBA on {self.model_version}, solver status={solution.status}",
            reproducibility_ref=self._reproducibility_ref(),
        )

    def _reproducibility_ref(self) -> dict[str, Any]:
        return {"model_id": self.model_version}
