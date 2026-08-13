"""Intervention Compiler (doc06 §5): turns one `PerturbationSpec` (a
biological-intent-level genotype modification, e.g. `{gene: "ppc",
operation: "knockout"}`) into a `CompiledIntervention` - a real,
GPR-resolved reaction-bound change on the `gem_fba` adapter's actual
cobrapy model, never a hand-guessed lookup table.

This replaces `harness.engineering_design.counterfactual_service`'s
`_GENE_TO_REACTION_BOUND_HINT` (a 3-gene hardcoded dict) with genuine
gene->GPR->reaction resolution via cobrapy itself. That distinction
matters biologically, not just architecturally: this round's audit found
the hint table's own claim (`ptsG` knockout -> `GLCpts` fully blocked) is
WRONG under the model's actual GPR - `GLCpts`'s rule is an OR of three
PTS-subunit complexes, so knocking out `ptsG` alone leaves two redundant
complexes catalyzing the reaction and cobrapy's own
`knock_out_model_genes` correctly reports zero affected reactions. A
manual hint table would have silently asserted a growth effect that the
model does not actually predict; resolving through cobra's real GPR logic
cannot make that mistake.

Only single-gene deletion/knockdown/overexpression against `gem_fba`'s
bundled `e_coli_core` model is compiled this round (doc06 §1.3's minimum
vertical slice: "一个可映射的单基因干预"). Anything else (gene not in the
137-gene core model, unsupported operation, multi-gene epistasis) is
rejected with a structured reason - never silently ignored or guessed.
"""
from __future__ import annotations

from typing import Any

from harness.ids import new_id, now
from harness.virtual_cell.models import CompiledIntervention, PerturbationSpec

_SUPPORTED_OPERATIONS = {"knockout", "deletion", "knockdown", "attenuation", "overexpression"}

# doc06 §5: recording the approximation explicitly rather than presenting a
# flux-bound scale factor as a measured expression change.
_KNOCKDOWN_FACTOR_DEFAULT = 0.5
_OVEREXPRESSION_FACTOR_DEFAULT = 2.0


_COMPILABLE_MODEL_IDS = ("MREG-gem_fba", "MREG-gem_fba_iml1515")


def _load_gem_model(model_id: str = "MREG-gem_fba"):
    """Fresh, mutation-safe copy of the same bundled/loaded model the
    corresponding `harness.diagnosis.model_adapters` adapter uses - never
    the shared cached instance. `model_id` dispatch added in Phase D
    (`六大核心模块统一集成` prompt §6.7's larger-GEM adapter) - an earlier
    version of this function always loaded `e_coli_core` regardless of
    which model was actually selected, which silently made every
    compatibility/compile check run against the wrong (smaller) model's
    gene set whenever a caller selected `gem_fba_iml1515`; caught and
    fixed alongside `harness/virtual_cell/runner.py`'s matching bug."""
    if model_id == "MREG-gem_fba_iml1515":
        from harness.diagnosis.model_adapters.gem_fba_iml1515 import _load_model as _load_iml1515

        return _load_iml1515().copy()
    from harness.diagnosis.model_adapters.gem_fba import _load_model

    return _load_model().copy()


def resolve_gene(model, gene_symbol: str):
    """Case-insensitive match against the model's real gene *names* (e.g.
    'ppc' -> gene id 'b3956') - never a fuzzy/embedding match. Returns
    `None` if the gene genuinely is not part of this model's domain."""
    target = gene_symbol.strip().lower()
    for gene in model.genes:
        if gene.id.lower() == target or gene.name.lower() == target:
            return gene
    return None


def _knockout_affected_reactions(model, gene) -> list[str]:
    """Reactions whose GPR becomes non-functional once `gene` alone is
    knocked out - accounts for isozyme/complex redundancy exactly as
    cobrapy's own `cobra.manipulation.knock_out_model_genes` does (this is
    that same real logic, inlined so we can report affected reactions
    without yet committing bound changes to a run)."""
    reactions = list(gene.reactions)
    gene.knock_out()
    return [r.id for r in reactions if not r.functional]


def compile_intervention(
    perturbation: PerturbationSpec, *, model_id: str, knockdown_factor: float | None = None, overexpression_factor: float | None = None,
) -> CompiledIntervention:
    """Real cobrapy-backed compilation for the `gem_fba`/`gem_fba_iml1515`
    adapters. Any other `model_id` (vecoli, kinetic_resource) has no
    compiler this round and must be rejected upstream by the compatibility
    check before this is ever called."""
    ts = now()
    operation = (perturbation.operation or "").strip().lower()
    log: list[str] = []

    if model_id not in _COMPILABLE_MODEL_IDS:
        return _rejected(
            perturbation, model_id, ts,
            reason=f"no compiler implemented for model_id={model_id!r} this round (only {_COMPILABLE_MODEL_IDS} have a real compiler)",
        )

    if operation not in _SUPPORTED_OPERATIONS:
        return _rejected(
            perturbation, model_id, ts,
            reason=f"operation {operation!r} has no gem_fba compilation rule (supported: {sorted(_SUPPORTED_OPERATIONS)})",
        )

    model = _load_gem_model(model_id)
    gene = resolve_gene(model, perturbation.target)
    if gene is None:
        return _rejected(
            perturbation, model_id, ts,
            reason=(
                f"gene {perturbation.target!r} is not part of {model_id}'s {len(model.genes)}-gene set "
                "(out of this model's domain)"
            ),
        )

    original_bounds = {r.id: {"lower": r.lower_bound, "upper": r.upper_bound} for r in gene.reactions}

    if operation in ("knockout", "deletion"):
        affected = _knockout_affected_reactions(model, gene)
        if not affected:
            log.append(
                f"gene {gene.id} ({perturbation.target}) participates in reaction(s) "
                f"{[r.id for r in gene.reactions]} but GPR isozyme/complex redundancy means single-gene knockout "
                "leaves every reaction functional under this model - a real, GPR-computed null result, not a compiler failure"
            )
            return CompiledIntervention(
                compiled_intervention_id=new_id("CINT"), perturbation_id=perturbation.perturbation_id, model_id=model_id,
                target_kind="gene", resolved_gene_id=gene.id, affected_reactions=[], modification_type="reaction_bound_scaling",
                original_bounds=original_bounds, new_bounds={}, mapping_rule="GPR-resolved gene knockout (cobra.manipulation semantics)",
                mapping_status="direct", mapping_assumptions=[
                    "single-gene deletion mapped directly via the model's own gene-protein-reaction (GPR) rule, no manual hint table",
                ],
                mapping_uncertainty="none beyond the model's own GPR logic; isozyme redundancy genuinely predicts no flux-bound change",
                unsupported_inference=[], compilation_log=log, status="compiled", created_at=ts,
            )
        new_bounds = {rid: {"lower": 0.0, "upper": 0.0} for rid in affected}
        log.append(f"gene {gene.id} ({perturbation.target}) knockout blocks reaction(s) {affected} per model GPR")
        return CompiledIntervention(
            compiled_intervention_id=new_id("CINT"), perturbation_id=perturbation.perturbation_id, model_id=model_id,
            target_kind="gene", resolved_gene_id=gene.id, affected_reactions=affected, modification_type="reaction_bound_scaling",
            original_bounds={rid: original_bounds[rid] for rid in affected}, new_bounds=new_bounds,
            mapping_rule="GPR-resolved gene knockout (cobra.manipulation semantics: reaction bounds -> (0,0) where GPR becomes non-functional)",
            mapping_status="direct",
            mapping_assumptions=["genetic deletion == complete loss of the affected reaction's flux capacity (standard FBA gene-deletion convention)"],
            mapping_uncertainty="none beyond standard FBA gene-deletion convention; does not model partial/leaky knockouts",
            unsupported_inference=["real-world knockout efficiency", "off-target/polar effects", "compensatory regulation"],
            compilation_log=log, status="compiled", created_at=ts,
        )

    # knockdown/attenuation/overexpression: scale bounds on reactions that a
    # full knockout WOULD affect (same GPR resolution), never the gene's
    # entire reaction set naively - an isozyme-redundant gene has no real
    # single-gene expression lever under this model either.
    affected = _knockout_affected_reactions(model, gene)
    if not affected:
        return _rejected(
            perturbation, model_id, ts,
            reason=(
                f"gene {gene.id} ({perturbation.target}) has isozyme/complex redundancy under this model's GPR - "
                "no single reaction's bounds are uniquely attributable to this gene, so a knockdown/overexpression "
                "bound-scaling approximation is not meaningful here"
            ),
        )
    factor = knockdown_factor if knockdown_factor is not None else _KNOCKDOWN_FACTOR_DEFAULT
    if operation == "overexpression":
        factor = overexpression_factor if overexpression_factor is not None else _OVEREXPRESSION_FACTOR_DEFAULT

    new_bounds = {}
    for rid in affected:
        ob = original_bounds[rid]
        if operation == "overexpression":
            new_bounds[rid] = {"lower": ob["lower"], "upper": ob["upper"] * factor if ob["upper"] > 0 else ob["upper"]}
        else:
            new_bounds[rid] = {"lower": ob["lower"] * factor, "upper": ob["upper"] * factor}

    log.append(f"{operation} on {gene.id} ({perturbation.target}) approximated as bound scaling x{factor} on reaction(s) {affected}")
    return CompiledIntervention(
        compiled_intervention_id=new_id("CINT"), perturbation_id=perturbation.perturbation_id, model_id=model_id,
        target_kind="gene", resolved_gene_id=gene.id, affected_reactions=affected, modification_type="reaction_bound_scaling",
        original_bounds={rid: original_bounds[rid] for rid in affected}, new_bounds=new_bounds,
        mapping_rule=f"reaction bound scaling by factor={factor} on GPR-resolved reaction(s), approximating {operation}",
        mapping_status="approximate",
        mapping_assumptions=[
            f"{operation} is approximated as a x{factor} scaling of steady-state flux bound capacity, "
            "not a measured transcript/protein-level expression change",
        ],
        mapping_uncertainty=(
            "the scaling factor is an engineering convention, not fit to this gene/strain; actual expression change "
            "under the real genetic implementation (e.g. CRISPRi, promoter/RBS edit) is not measured or modeled"
        ),
        unsupported_inference=["CRISPRi/promoter/RBS efficiency", "off-target effects", "expression burden"],
        compilation_log=log, status="compiled", created_at=ts,
    )


def _rejected(perturbation: PerturbationSpec, model_id: str, ts: float, *, reason: str) -> CompiledIntervention:
    return CompiledIntervention(
        compiled_intervention_id=new_id("CINT"), perturbation_id=perturbation.perturbation_id, model_id=model_id,
        target_kind="gene", resolved_gene_id=None, affected_reactions=[], modification_type="none",
        original_bounds={}, new_bounds={}, mapping_rule="", mapping_status="unsupported", mapping_assumptions=[],
        mapping_uncertainty="", unsupported_inference=[], compilation_log=[reason], status="rejected",
        rejection_reason=reason, created_at=ts,
    )


def merge_compiled_bounds(compiled: list[CompiledIntervention]) -> dict[str, Any]:
    """Merges every *compiled* (non-rejected) intervention's `new_bounds`
    into one `reaction_bounds` dict for a single `gem_fba` run - a
    combination scenario. Conflicting bounds on the same reaction from two
    different compiled interventions are flagged, not silently
    last-write-wins (doc06 §5.6: "检查冲突、重复、方向矛盾")."""
    merged: dict[str, dict[str, float]] = {}
    conflicts: list[str] = []
    for ci in compiled:
        if ci.status != "compiled":
            continue
        for rid, bounds in ci.new_bounds.items():
            if rid in merged and merged[rid] != bounds:
                conflicts.append(f"conflicting bounds on {rid}: {merged[rid]} vs {bounds} (from {ci.compiled_intervention_id})")
                continue
            merged[rid] = bounds
    if conflicts:
        raise ValueError("; ".join(conflicts))
    return merged
