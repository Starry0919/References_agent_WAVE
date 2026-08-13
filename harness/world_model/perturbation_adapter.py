"""Component: Perturbation Layer. `harness.virtual_cell.models.
PerturbationSpec` is reused as the one canonical, structured perturbation
shape (real, tested, already has the right vocabulary) - this module only
normalizes the THREE other ad hoc perturbation shapes already scattered
across the repo (DDR `decision_chain[i]`, `genotype_manifest.modifications`,
`CandidateDesign.genetic_modifications`) into the same read-only view, the
same pattern `harness.evidence_intelligence.adapters` used for evidence in
Module 3. Nothing here writes a `PerturbationSpec` row - that table belongs
to a `vc_simulation_case`; a DDR-sourced perturbation, for instance, has no
simulation case to attach to.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from harness.world_model.models import PERTURBATION_TYPES

# Ordered, first-match-wins keyword -> PERTURBATION_TYPES classification.
# Deliberately conservative: an implementation string that matches nothing
# here becomes "unknown", never guessed into a specific category (Module 4
# prompt §10's "do not fabricate" extends to perturbation classification,
# not just transitions).
_TYPE_KEYWORDS: tuple[tuple[str, str], ...] = (
    ("敲除", "deletion"), ("ko", "deletion"), ("knockout", "deletion"), ("delet", "deletion"),
    ("敲低", "knockdown"), ("knockdown", "knockdown"), ("干扰", "knockdown"), ("crispri", "knockdown"),
    ("过表达", "overexpression"), ("overexpress", "overexpression"),
    ("启动子", "promoter_edit"), ("promoter", "promoter_edit"),
    ("rbs", "rbs_edit"), ("核糖体结合位点", "rbs_edit"),
    ("点突变", "point_mutation"), ("point mutation", "point_mutation"),
    ("敲入", "gene_insertion"), ("插入", "gene_insertion"), ("insertion", "gene_insertion"),
    ("培养基", "medium_change"), ("medium", "medium_change"), ("碳源", "medium_change"), ("carbon source", "medium_change"),
    ("厌氧", "oxygen_change"), ("好氧", "oxygen_change"), ("oxygen", "oxygen_change"),
    ("温度", "temperature_change"), ("temperature", "temperature_change"),
)


def _classify(*texts: str | None) -> str:
    haystack = " ".join(t for t in texts if t).lower()
    for keyword, ptype in _TYPE_KEYWORDS:
        if keyword in haystack:
            return ptype
    return "unknown"


@dataclass
class NormalizedPerturbation:
    """A read-only projection of any of the 4 perturbation shapes into one
    common view. `type` is always a member of `PERTURBATION_TYPES`."""

    type: str
    target: str
    target_namespace: str = "gene_symbol"
    implementation: str = ""
    description: str = ""
    environmental_changes: list[dict[str, Any]] = field(default_factory=list)
    source_shape: str = ""  # perturbation_spec | ddr_decision_step | genotype_manifest | candidate_design_modification
    source_ref: dict[str, Any] = field(default_factory=dict)
    assumptions: list[str] = field(default_factory=list)


def from_perturbation_spec(spec) -> NormalizedPerturbation:
    """`spec` is a `harness.virtual_cell.models.PerturbationSpec` row - the
    canonical case, a pure passthrough."""
    return NormalizedPerturbation(
        type=spec.type if spec.type in PERTURBATION_TYPES else "unknown",
        target=spec.target, target_namespace=spec.target_namespace, implementation=spec.implementation,
        description=spec.biological_intent, environmental_changes=list(spec.environmental_changes or []),
        source_shape="perturbation_spec", source_ref={"perturbation_id": spec.perturbation_id, "design_version_id": spec.design_version_id},
        assumptions=list(spec.assumptions or []),
    )


def from_ddr_decision_step(ddr_id: str, step: dict[str, Any]) -> NormalizedPerturbation:
    """`step` is one `decision_chain[i]` dict from `knowledge/ddr_database/
    *.json`. Target prefers `target.gene` (a real gene symbol) over
    `target.enzyme` (often a protein/complex name, not directly a
    perturbation target namespace) - falls back to enzyme only when no gene
    is recorded, and flags the namespace accordingly rather than silently
    treating an enzyme name as a gene symbol."""
    target_block = step.get("target") or {}
    gene, enzyme = target_block.get("gene"), target_block.get("enzyme")
    target = gene or enzyme or ""
    namespace = "gene_symbol" if gene else "enzyme_name"
    implementation = str(step.get("implementation") or "")
    implementation_detail = str(step.get("implementation_detail") or "")
    return NormalizedPerturbation(
        type=_classify(implementation, implementation_detail),
        target=str(target), target_namespace=namespace, implementation=implementation,
        description=implementation_detail, source_shape="ddr_decision_step",
        source_ref={"ddr_id": ddr_id, "step": step.get("step")},
        assumptions=["target inferred from DDR free text - not a validated gene/protein identifier resolution"] if target else [],
    )


def from_genotype_manifest_entry(entry: dict[str, Any]) -> NormalizedPerturbation:
    """`entry` is one `DesignVersion.genotype_manifest.modifications[i]`
    dict, shape `{gene, operation, detail}` (see `harness.designs.adapters.
    genotype_manifest_from_p1_decisions`) - the same shape `harness.
    virtual_cell.service.extract_perturbations` already converts into a
    real `PerturbationSpec`; this function produces the read-only view
    version of that same conversion for callers with no simulation case."""
    gene = str(entry.get("gene") or "")
    operation = str(entry.get("operation") or "")
    detail = str(entry.get("detail") or "")
    return NormalizedPerturbation(
        type=_classify(operation, detail), target=gene, target_namespace="gene_symbol", implementation=operation,
        description=detail, source_shape="genotype_manifest", source_ref={"gene": gene, "operation": operation},
    )


def from_candidate_design_modification(entry: dict[str, Any]) -> NormalizedPerturbation:
    """`entry` is one `CandidateDesign.genetic_modifications[i]` dict -
    documented only as a comment (`# list[GeneticModification-shaped
    dict]`, `harness/engineering_design/models.py:269`), no class actually
    enforces its shape anywhere in the repo. Reads defensively via `.get()`
    over the field names that convention implies, and is explicit in
    `assumptions` about that lack of a real schema rather than presenting
    the result as equally reliable to the other three adapters."""
    target = str(entry.get("gene") or entry.get("target") or "")
    operation = str(entry.get("operation") or entry.get("modification") or entry.get("type") or "")
    detail = str(entry.get("detail") or entry.get("description") or "")
    return NormalizedPerturbation(
        type=_classify(operation, detail), target=target, target_namespace="gene_symbol", implementation=operation,
        description=detail, source_shape="candidate_design_modification", source_ref={"raw": entry},
        assumptions=["CandidateDesign.genetic_modifications has no enforced schema in this codebase - fields read best-effort via .get()"],
    )


def normalized_perturbation_to_dict(p: NormalizedPerturbation) -> dict[str, Any]:
    return {
        "type": p.type, "target": p.target, "target_namespace": p.target_namespace, "implementation": p.implementation,
        "description": p.description, "environmental_changes": p.environmental_changes, "source_shape": p.source_shape,
        "source_ref": p.source_ref, "assumptions": p.assumptions,
    }
