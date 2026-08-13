# Diagnosis / Engineering Design Workbench Architecture

## Decision chain

`Project context -> Diagnosis session -> ranked hypotheses -> evidence for/against -> gated diagnosis decision -> versioned handoff -> strategies -> candidate portfolio -> evaluator gates -> selected/rejected state -> build/test validation`

Every visible scientific claim remains anchored to an existing identifier. Presentation adapters may classify an existing source as `RULE_TRANSFER`, `MODEL_COMPUTED`, `LITERATURE_REPORTED`, or `UNRESOLVED`; this classification does not create a new persisted ontology.

## Data contracts

### Diagnosis view

- Project API: real host, product, objective/constraints, lifecycle.
- Diagnosis APIs: newest session plus selector, hypotheses/assessments, evidence links/items, decisions, tests, model capabilities/runs where present, mechanism graph, and audit trail.
- Coverage rows are a view model. A row is checked only when a persisted finding, evidence type, test, or model run supports that conclusion. Otherwise it is `NOT_EVALUATED` with a machine-readable reason.
- Quantitative values render only when a real model/evidence payload supplies value, unit, source and value type.

### Design view

- Existing project lookup selects the newest real engineering-design project for the parent project.
- Handoff provides diagnosis IDs/version, supported hypotheses, unresolved alternatives, approval and stale state.
- Strategy exclusions provide `Why not` explanations before candidate evaluation.
- Candidate serialization exposes existing causal chain, evidence links, modifications, process changes, dependencies/epistasis assumptions, conflicts/uncertainty, trade-offs, buildability, safety, debug/fallback and source diagnosis version.
- Evaluation remains a separate persisted object. No UI score is synthesized when absent.

## Status semantics

- Loading, error, empty, partial, running and complete are separate states.
- `Not evaluated` means the relevant persisted computation/result does not exist.
- `No evidence against recorded` is not equivalent to `no counterevidence exists`.
- `Proposed` is not equivalent to selected, approved, predicted-successful, or validated.
- Model capability availability is distinct from a model run for the current project.

## Evaluator contract

Persisted evaluator output remains authoritative. The UI presents hard-constraint results and evaluator findings without collapsing them into one score. Until a target-project evaluation exists, gates (evidence, essentiality, pathway integrity, internal conflict, evidence calibration, provenance, scope, feasibility) display `Pending evaluation`.

## Backward compatibility

- Existing routes and detail workflows remain available.
- Existing response fields are unchanged; candidate responses only gain fields already present in the ORM model.
- Existing camelCase adapters remain the only snake_case translation boundary.
- No migration or project-state mutation is required to open the new workbenches.

## Known architectural gaps

- Substrate is not part of the current project context contract.
- Unified epistemic status and quantitative-value envelopes are not persisted across all producers.
- Coverage axes and dependency edges are not first-class backend objects.
- The target project has no evaluator run, build/test package, model computation, selected stack, or process-design proposal.
- Final-report consumption of selected diagnosis/design objects is not verified end to end.
