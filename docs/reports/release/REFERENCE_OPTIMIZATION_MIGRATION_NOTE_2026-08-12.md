# Reference Optimization Migration Note — 2026-08-12

## Migration

Migration id: `0017_reference_optimization_schema` in `harness/bootstrap.py`.

The change is additive:

- adds `diagnosis_finding_ids` JSON to `design_candidates`, default `[]`;
- adds `decision_state` to `design_candidates`, default `candidate_generated`;
- creates `diag_findings`;
- creates `evidence_needs`;
- creates `design_model_evaluations`.

## Legacy semantics

Database defaults exist for physical backward compatibility, but an old candidate with no finding IDs or a default `candidate_generated` state is **not** scientifically verified, evaluated, recommended, selected, or build-ready. Consumers must treat such rows as legacy/unverified until they pass the new services.

The adapter module remains named `gem_fba_iml1515` and the asset remains `knowledge/models/iML1515.xml` for path compatibility. The SBML model's internal identity is iJO1366, so new `ModelEvaluation.model_version` and reproducibility output truthfully report `iJO1366`; `iML1515.xml` is retained only as `legacy_asset_name`.

## Rollout

1. Back up the database.
2. Start the application or run `bootstrap_schema()`; migration is idempotent.
3. Verify the new tables and candidate columns.
4. Do not bulk-mark legacy candidates evaluated/selected/build-ready.
5. Backfill finding links only from real persisted EngineeringProblems, HypothesisVersions, and QC-passed project observations.
6. Re-evaluate candidate model records when product reaction, medium, oxygen, or intervention constraints change.

## Compatibility

No stable field was removed or renamed. New JSON/API contracts are versioned. Frontends that do not yet display the fields may ignore additive keys, but must not translate `candidate_generated` into “recommended”.
