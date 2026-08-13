# Experiment-Native V3 pre-analysis

## Repository truth and frozen baseline

The runtime path is canonical/clean document → `opus_extractor.py` → Skill07 output → Skill07/08 handoff → conservative E1/E2/E3 verification → DDR converter → knowledge admission. V2 fields are document-level projections and historical `field_metadata`/locators occur as strings, dictionaries and arrays. The principal loss occurs when several experiment-specific interventions, contexts and outcomes are flattened into one field before E3.

V1 recorded 15 real papers, 240 field claims, E1 0.929, E2 0.621, E3 0.083, Silver strict yield 0.068, traceability 1.0, contamination 0, safety 13/13, and 175 scoped tests passed. Whole-repository testing timed out at 120 seconds and remains inconclusive, never PASS.

## Compatibility risks and implementation map

V3 is additive: canonical `experiment_instances` and `atomic_claims`, with legacy fields retained as a declared lossy projection. Stable identity uses document identity plus source-local identity; unresolved legacy identity is marked for review. Skill08 consumes claim-first envelopes without lowering E1/E2/E3. Gold schemas/workbench, replay, evaluator and release gates remain separate from model-generated Silver.

Changed areas are `experiment_native.py`, runtime schemas, Skill07/08 adapters, admission, Gold API/UI, `benchmarks/paper_extraction_e2e_v2`, tests and these reports. Tests cover stable identity, lineage, legacy normalization, fail-closed evidence, Gold separation and anti-gaming.

Non-goals: manufacturing Gold, changing scientific thresholds, semantic ontology completion, holdout tuning, deleting V2, or repairing unrelated repository failures.
