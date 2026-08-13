"""Module 4: Biological Engineering World Model.

Represents biological entities, cell states, engineering perturbations, and
evidence-supported state transitions (State A + Perturbation -> State B) -
NOT a Virtual Cell simulator and NOT predictive modeling of state
transitions (both explicitly out of scope; `harness.virtual_cell` already
owns the real simulation/prediction pipeline this module deliberately does
not duplicate).

Phase 1 architecture review found:

  - `harness.cell_state.models.BiologicalStateSnapshot` already IS most of
    the "Cell State Layer" (host/strain/environment/timepoint/physiology/
    multi-omics refs/per-field provenance) - reused as-is, not duplicated.
  - `harness.virtual_cell.models.PerturbationSpec` already IS the
    "Perturbation Layer"'s structured shape - reused as the canonical
    perturbation vocabulary; `perturbation_adapter.py` only adds read-side
    normalization from the three OTHER ad hoc perturbation shapes that
    already exist elsewhere (DDR `decision_chain[i]`, `genotype_manifest`,
    `CandidateDesign.genetic_modifications`).
  - No first-class, persisted biological-ENTITY registry existed anywhere -
    genes/reactions/pathways were only ever bare strings. `models.py`'s
    `BiologicalEntity` fills exactly that gap, populated lazily as entities
    are actually referenced (never a bulk genome import).
  - No "State A + Perturbation -> State B" object with mechanism/phenotype/
    provenance/uncertainty existed - `harness.cell_state.models.
    CellStateTrajectory` was clearly meant to be this but is orphaned dead
    code (zero callers) and shaped for a different purpose (predicted-vs-
    observed residual tracking). `models.py`'s `StateTransitionRecord` is a
    new, additive table rather than repurposing that orphaned one.
  - `harness.diagnosis.mechanism_graph.build_mechanism_graph()` already
    builds a DDR-sourced entity-level graph (gene/enzyme/pathway/process) -
    `entity_graph.py` reuses it rather than building a second graph
    builder, only adding canonical entity-id resolution on top.
  - Module 3 (`harness.evidence_intelligence`) integration is by reference
    only (`StateTransitionRecord.evidence_id`, Module 3's own id scheme) -
    this package never re-derives "is this evidence trustworthy," it only
    points at Module 3's existing `get_evidence_object`/provenance-graph
    endpoint (zero edits to Module 3's code).

Components:
  1. `models.py`               - `BiologicalEntity`, `StateTransitionRecord`.
  2. `entities.py`              - entity registry service (get-or-create, list).
  3. `perturbation_adapter.py`  - normalizes the 3 other perturbation shapes into PerturbationSpec's vocabulary.
  4. `transitions.py`           - StateTransitionRecord service (record/list/get).
  5. `entity_graph.py`          - Component: Entity Graph (static biological relationships).
  6. `state_transition_graph.py`- Component: State Transition Graph (dynamic engineering relationships).
  7. `rule_linkage.py`          - Component: Engineering Rule Layer (read-side link to knowledge/biological_rules).
  8. `provenance.py`            - Component: Provenance Interface (pointer into Module 3, not a re-implementation).
"""
