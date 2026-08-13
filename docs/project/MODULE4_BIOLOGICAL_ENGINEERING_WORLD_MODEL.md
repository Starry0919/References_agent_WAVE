# Module 4: Biological Engineering World Model

## Architecture review

WAVE already contained authoritative building blocks: `BiologicalStateSnapshot` for condition-scoped observed/predicted states, Virtual Cell's structured perturbation vocabulary, DDR-derived mechanism graphs, Module 3 evidence objects and provenance, the biological rule library, and project-event DBTL audit trails. It did not contain a stable biological-entity registry or a persisted, general `State A + perturbation -> State B` engineering transition.

Module 4 therefore adds only `BiologicalEntity` and `StateTransitionRecord`. It reuses existing states, perturbation vocabulary, rules, Evidence IDs, DDRs, and human governance. It does not predict a future state, run a model, approve a strategy, or replace DDR.

Compatibility risks are controlled as follows:

- Missing context is rejected instead of assumed.
- V1.1 rejects hosts outside E. coli K-12 and objectives outside tryptophan improvement while maintaining growth.
- Nonexperimental transitions cannot be marked validated.
- Every transition requires an Evidence Object ID or Simulation Run ID.
- Missing evidence resolution remains visible as unresolved provenance; no biological claim is generated.
- Existing `CellStateTrajectory` remains untouched because it serves prediction/observation residual tracking.

## Data flow

```text
Evidence Object / Experiment / Simulation
  -> represented initial cell state
  -> represented perturbation
  -> represented final cell state and observed changes
  -> StateTransitionRecord + mandatory context + uncertainty
  -> entity/state-transition/provenance views
  -> Module 2 reasoning
  -> DDR decision (unchanged owner)
```

## Schemas

### BiologicalEntity

Fields: `entity_id`, controlled `entity_type`, `name`, optional canonical ID and namespace, aliases, E. coli organism scope, description, source, source reference, creator, and timestamp. Supported types are gene, RNA, protein, protein complex, metabolite, reaction, pathway, regulator, phenotype, and environment. Entities are created lazily from real references rather than bulk-generated.

Example: `gene / trpE / b1264 / EcoCyc / Escherichia coli K-12`.

### Cell state

The existing `BiologicalStateSnapshot` remains authoritative. It represents host/strain, environment, genotype, time/growth phase, perturbations, physiology, functional state, multi-omics references, uncertainty, per-field provenance, and missing modalities. A transition may link a real snapshot ID or carry an explicit summary when literature has no stored snapshot.

### Perturbation

The normalized shape contains type, target, target namespace, implementation, description, environmental changes, source shape/reference, and explicit assumptions. It reuses the Virtual Cell perturbation vocabulary but does not invoke simulation.

### StateTransitionRecord

Required fields are transition ID, initial state, perturbation, final state, observed changes, mechanism, phenotype, context, origin, provenance reference, uncertainty, status, and outcome. Mandatory context fields are host, strain, medium, carbon source, oxygen condition, growth phase, and engineering objective. Outcomes include success, failure, unexpected, and not applicable.

Origins are categorical and unequal: experimental, multi-omics derived, simulation, literature inferred, expert curated, and hypothesis. Only experimental or multi-omics-derived records may be validated; all others remain inferred or hypothesis.

## API and visualization

- `POST/GET /api/world-model/entities`
- `POST/GET /api/world-model/transitions`
- `GET /api/world-model/transitions/{id}` including Module 3 provenance
- `GET /api/world-model/transition-graph`
- `GET /api/world-model/entity-graph`

The project route `/projects/{project_id}/world-model` presents state changes, perturbations, mechanism, outcome, origin/status, and links to evidence provenance. It renders stored transitions only.

## Validation and limitations

Tests cover entity idempotency, scope/context enforcement, provenance enforcement, nonexperimental status, querying, and graph construction. Python compilation and frontend production build validate API/router and UI integration.

Known limitations: there is no automatic DDR-to-transition importer because inferring initial/final states from incomplete prose could fabricate claims; callers must explicitly submit reviewed transitions. JSON context filtering is intentionally project-scale and not indexed. Stable experiment-level provenance depends on future upstream experiment identifiers. Predictive state transitions remain exclusively in future Virtual Cell work.
