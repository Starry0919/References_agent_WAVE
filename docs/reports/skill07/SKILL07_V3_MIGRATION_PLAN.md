# Skill07 V3 Migration Plan

Date: 2026-08-12

## Current flow and drift

The model receives the full clean document, Skill07 rules, semantic contract and
schema. The semantic contract already calls ExperimentInstance canonical, but
the runtime schema requires only 16 fields plus a permissive
`experimental_design_object`. Normalization does not create a versioned native
representation; Skill08 loops over fields first; DDR reads the legacy object.
Thus consumers, not prose, determine truth and currently favor projections.

## Additive migration

1. Add `representation_version`, `experiment_instances`, `atomic_claims`, and
   `projection_metadata` to the Skill07 transport schema.
2. Define strict standalone schemas and a representation contract for native
   objects, claims and evidence bundles.
3. For legacy model/cache output, add only structural compatibility defaults:
   retain the old design object as one review-required experiment and derive
   review-required claim candidates from non-empty fields. This migration never
   promotes them to verified facts.
4. Validate claim IDs, experiment foreign keys, evidence slots, single
   subject/predicate/object scalarity and candidate evidence role.
5. Make Skill08 verify native atomic claims first while retaining field
   verification as a deprecated compatibility projection.
6. Keep candidate immutability, handoff identity, DDR and admission fail-closed.

## Risks and scope

Legacy projection-derived claims are not scientifically equivalent to model-
native atomic claims and are explicitly marked `migration_generated` plus
`review_required`. The migration does not guess biological lineage or split
scientific semantics by punctuation. Prompt/Skill rules may request native
output, but deterministic code will reject malformed native claims rather than
repair their science.
