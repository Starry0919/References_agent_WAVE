"""`BiologicalEntity` (Component: Biological Entity Layer) and
`StateTransitionRecord` (Component: State Transition Graph, the core object
per the Module 4 prompt: "State A + Perturbation -> State B").

Both tables are brand new and additive - no existing schema is touched.
`StateTransitionRecord` deliberately does NOT reuse `harness.cell_state.
models.CellStateTrajectory` (declared for a similar purpose but orphaned -
zero callers anywhere in the repo - and shaped for predicted-vs-observed
residual tracking, not general "what changed and why"): see package
docstring for the reasoning.
"""
from __future__ import annotations

from sqlalchemy import JSON, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from harness.db import Base, guard_immutable_fields

# Module 4 prompt §6: entities that "should support engineering relationships".
ENTITY_TYPES = (
    "gene", "rna", "protein", "protein_complex", "metabolite", "reaction",
    "pathway", "regulator", "phenotype", "environment",
)

# How a BiologicalEntity row came to exist - never "discovered"/mined, only
# ever created because something else in the repo already named it.
ENTITY_SOURCES = ("ddr_reference", "gem_reference", "perturbation_target", "manual")

# Mirrors `harness.virtual_cell.models.PerturbationSpec.type`'s documented
# vocabulary verbatim (virtual_cell never exported it as an importable
# constant) plus "unknown" - allowed ONLY in `perturbation_adapter.py`'s
# normalized output for a source text this module's keyword mapping
# couldn't classify, never silently guessed into a real category.
PERTURBATION_TYPES = (
    "deletion", "knockdown", "overexpression", "promoter_edit", "rbs_edit",
    "point_mutation", "gene_insertion", "medium_change", "oxygen_change",
    "temperature_change", "combination", "unknown",
)

# Module 4 prompt §10: allowed transition origins, ranked (index = priority,
# lower = more trusted). "hypothesis" is listed only in the prompt's
# priority ordering, not its "Allowed origins" list - folded in here as the
# lowest-ranked, least-trusted origin so the two lists reconcile into one
# ordered vocabulary rather than silently dropping it.
TRANSITION_ORIGINS = ("experimental", "multi_omics_derived", "simulation", "literature_inferred", "expert_curated", "hypothesis")
TRANSITION_ORIGIN_RANK = {origin: i for i, origin in enumerate(TRANSITION_ORIGINS)}

# Module 4 prompt §10: "If a transition is not experimentally validated:
# mark it as inferred or hypothesis... do not promote it into validated
# world knowledge." Stored explicitly (not only derived from `origin`) for
# auditability, mirroring Module 3's persisted-but-derived `confidence_level`.
TRANSITION_STATUSES = ("validated", "inferred", "hypothesis")

# Module 4 prompt §14: successful / failed / unexpected transitions, never a
# fabricated separate "failure database" - just another value on this field.
TRANSITION_OUTCOMES = ("success", "failure", "unexpected", "not_applicable")


class BiologicalEntity(Base):
    """Component: Biological Entity Layer. Rows are created lazily by
    `harness.world_model.entities.get_or_create_entity` the first time
    something else in the repo (a DDR decision_chain step, a
    PerturbationSpec target, a compiled GEM gene/reaction id) actually
    names this entity - never a bulk genome/pathway-database import."""

    __tablename__ = "world_model_entities"

    entity_id: Mapped[str] = mapped_column(String, primary_key=True)
    entity_type: Mapped[str] = mapped_column(String)  # one of ENTITY_TYPES
    name: Mapped[str] = mapped_column(String, index=True)
    canonical_id: Mapped[str | None] = mapped_column(String, default=None, index=True)  # e.g. cobrapy gene id "b3956", BiGG reaction id "PTAr"
    namespace: Mapped[str | None] = mapped_column(String, default=None)  # e.g. "iML1515", "bigg", "ddr_text" when no real namespace exists
    aliases: Mapped[list] = mapped_column(JSON, default=list)
    organism_scope: Mapped[str | None] = mapped_column(String, default=None)  # descriptive only, e.g. "Escherichia coli K-12" - never enforced/generalized
    description: Mapped[str] = mapped_column(String, default="")
    source: Mapped[str] = mapped_column(String)  # one of ENTITY_SOURCES
    source_ref: Mapped[str | None] = mapped_column(String, default=None)  # e.g. the DDR id or PerturbationSpec id that first named this entity
    created_by: Mapped[str] = mapped_column(String)
    created_at: Mapped[float] = mapped_column(Float)


guard_immutable_fields(BiologicalEntity, mutable_fields={"aliases", "description"})


class StateTransitionRecord(Base):
    """Component: State Transition Graph. The fundamental unit the Module 4
    prompt names explicitly: State A + Perturbation -> State B, with
    mechanism/phenotype/context/provenance/uncertainty. `initial_state`/
    `final_state` are `{snapshot_id: str|None, summary: str,
    entities_involved: [entity_id,...]}` - `snapshot_id` links to a real
    `harness.cell_state.models.BiologicalStateSnapshot` row when one exists,
    but is never fabricated when the transition's only source is a DDR
    paper (no formal snapshot was ever recorded for it).

    `context` intentionally duplicates fields a linked snapshot might also
    carry (host/strain/medium/...) rather than requiring a join, because
    Module 4 prompt Principle 3 makes context mandatory on every transition
    even when no snapshot exists at all (e.g. a literature-inferred
    transition)."""

    __tablename__ = "world_model_state_transitions"

    transition_id: Mapped[str] = mapped_column(String, primary_key=True)
    project_id: Mapped[str | None] = mapped_column(ForeignKey("projects.project_id"), default=None, index=True)  # None = cross-project curated knowledge (e.g. straight from a DDR)
    initial_state: Mapped[dict] = mapped_column(JSON, default=dict)
    perturbation: Mapped[dict] = mapped_column(JSON, default=dict)  # PerturbationSpec-shaped, see perturbation_adapter.py
    final_state: Mapped[dict] = mapped_column(JSON, default=dict)
    observed_changes: Mapped[list] = mapped_column(JSON, default=list)  # [{measurement, before, after, direction, unit}]
    mechanism: Mapped[str] = mapped_column(String, default="")
    phenotype: Mapped[str | None] = mapped_column(String, default=None)
    context: Mapped[dict] = mapped_column(JSON, default=dict)  # {host, strain, medium, carbon_source, oxygen_condition, growth_phase, engineering_objective}
    origin: Mapped[str] = mapped_column(String)  # one of TRANSITION_ORIGINS
    status: Mapped[str] = mapped_column(String, default="inferred")  # one of TRANSITION_STATUSES
    evidence_id: Mapped[str | None] = mapped_column(String, default=None)  # harness.evidence_intelligence id scheme, e.g. "ddr:DDR-001:1"
    simulation_run_id: Mapped[str | None] = mapped_column(String, default=None)  # harness.virtual_cell.models.SimulationRun.run_id, when origin="simulation"
    outcome: Mapped[str] = mapped_column(String, default="success")  # one of TRANSITION_OUTCOMES
    uncertainty: Mapped[dict | None] = mapped_column(JSON, default=None)
    superseded_by_transition_id: Mapped[str | None] = mapped_column(String, default=None)
    created_by: Mapped[str] = mapped_column(String)
    created_at: Mapped[float] = mapped_column(Float)


guard_immutable_fields(StateTransitionRecord, mutable_fields={"superseded_by_transition_id"})
