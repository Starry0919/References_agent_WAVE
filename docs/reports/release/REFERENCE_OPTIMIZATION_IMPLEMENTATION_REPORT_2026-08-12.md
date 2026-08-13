# WAVE Reference Optimization Implementation Report — 2026-08-12

## STATUS

**PARTIAL**. The highest-risk scientific error path is now blocked before generic experiment extraction, real candidate/product/condition-specific GEM evaluation is persisted, and observation grounding remains mandatory. Several P1 capabilities and legacy-entry-point integrations are deliberately not claimed as complete.

## Quick implementation audit

| Capability | Existing implementation | Decision | Relevant files |
|---|---|---|---|
| Literature Classification V2 / route enums | Multi-axis classifier and routing existed | Reuse + enforce | `harness/literature_discovery/classification.py`, `routing.py` |
| Atomic claims / evidence ledger | Existing extraction and evidence models | Reuse | `harness/paper_extraction`, `harness/diagnosis/models.py` |
| Observation Grounding | Strong project/QC/provenance/baseline gate existed | Reuse + add finding bridge | `harness/diagnosis/grounding.py`, `findings.py` |
| HypothesisVersion / FailureCase / LearningCycle | Versioned learning records existed | Reuse + failure recall | `harness/learning/models.py`, `harness/engineering_design/failure_recall.py` |
| Evaluators / Pareto / counterfactual | Existing candidate evaluation stack | Reuse + explicit decision state | `harness/engineering_design/evaluators`, `decision_state.py` |
| Build/Test / Human Approval | Existing planner and governance services | Reuse | `build_test_planner.py`, `governance_service.py` |
| cobrapy/FBA | Real model adapter existed | Extend with FVA and candidate comparison | `_cobrapy_fba_base.py`, `model_evaluation.py` |
| Frontend adapter | Existing Skill13 adapter | Add route-safe output | `harness/paper_extraction/frontend_adapter.py` |

## Implemented changes

- Added versioned `LiteratureExecutionPlan`; allow/forbid lists are executable guards, not labels.
- Moved classification and route gating before cache lookup, LLM call, generic `ExperimentInstance`, and downstream evidence binding.
- Non-primary routes emit route-specific method/benchmark/resource objects with zero model calls and no experiment instances.
- Added typed quantitative semantic roles and projection guards for benchmark count/runtime/replicate/cultivation/centrifugation contamination.
- Added immutable, observation-grounded `DiagnosisFinding` and candidate `diagnosis_finding_ids` linkage field.
- Added mandatory transition graph and illegal-transition checks for candidate decisions.
- Added immutable `ModelEvaluation`, real baseline/candidate growth and target-product runs, real FVA, condition bounds, assumptions, limitations, and provenance.
- Corrected scientific model identity: the bundled `knowledge/models/iML1515.xml` is internally iJO1366; runtime reports `iJO1366`, retaining the legacy asset name only as provenance.
- Added typed `EvidenceNeed` with gap-driven source routing, accepted/rejected audit, budget and stop reasons.
- Added section-aware lexical/dense RRF retrieval with section authority.
- Added Bronze historical-prior record and compatibility scoring isolated from evidence strength and recommendation rank.
- Added negative-result recall penalty; construction/execution/measurement/schema-tool failures are excluded from biological negative evidence.
- Added Benchmark V2 and release-manifest contracts, artifact hash, data dictionary, enum contract fields, and migration note.
- Updated stale tests so primary-extraction transport/cache tests use explicitly primary experimental documents and engineering fixtures use persisted QC-passed observations with provenance.

## New schemas

- `literature-execution-plan/1.0`
- `quantitative-observation/1.0`
- `diagnosis-finding/1.0`
- `model-evaluation/1.0`
- `evidence-need/1.0`
- `scientific-benchmark-case/2.0`
- `scientific-benchmark-result/2.0`
- `artifact-release-manifest/1.0`
- `frontend-scientific-route/1.0`

## P0 status

| Item | Result | Notes |
|---|---|---|
| P0-1 LiteratureExecutionPlan + runtime gate | PASS | Enforced before LLM/extractor; real SynBioGPT2 and ELISER replays produce no wet-lab objects. |
| P0-2 Quantitative Semantic Role | PARTIAL | Typed classifier and cross-projection guards tested; not yet threaded through every legacy extractor projection. |
| P0-3 Observation Grounding + DiagnosisFinding | PARTIAL | Grounding is mandatory and finding creation is strict; not every legacy candidate generator yet requires a persisted finding id. |
| P0-4 Candidate state machine | PARTIAL | Illegal jumps are blocked by the new service; some older workflow services still maintain their legacy status fields in parallel. |
| P0-5 Candidate/product/condition GEM/FBA | PASS | Real iJO1366/cobrapy baseline-vs-tnaA-knockout, growth/product/FVA persistence. |
| P0-6 EvidenceNeed loop | PARTIAL | Gap-driven retrieval and audit are real; automatic claim/hypothesis version creation after acceptance remains unintegrated. |

## P1 status

| Item | Result | Notes |
|---|---|---|
| P1-1 Section-aware hybrid retrieval | PASS (MVP) | Lexical + optional dense + RRF; Methods/Results authority retained. |
| P1-2 ELISER Bronze prior | PARTIAL | Schema/scoring/isolation/tests complete; full 15k ETL and Silver/Gold promotion intentionally absent. |
| P1-3 Failure learning | PARTIAL | Future recall changes penalty/rank input and technical failures are excluded; full automatic hypothesis-version update is not wired. |
| P1-4 Benchmark V2 | PARTIAL | Versioned destruction-test schema and representative tests exist; temporal Human Gold is not fabricated. |
| P1-5 Artifact/schema contracts | PARTIAL | Manifest/hash/data dictionary/backend adapter contracts exist; full frontend UI coverage was not undertaken. |

## Replay results

### SynBioGPT2 (real parsed paper)

- Source: local `clean_document.json` produced from `1-s2.0-S2693125726000233-main (1).pdf`.
- Classification: `ORIGINAL_RESEARCH`; route: `BENCHMARK_ROUTE`, confidence `HIGH`.
- Runtime: `model_calls=0`, `experiment_instances=0`, evidence verification disabled.
- `n=120` and `2 min` regression tests map to benchmark sample count and computation runtime, not biological replicates/cultivation.

### ELISER (real parsed paper)

- Source: local `clean_document.json` produced from `agent-参考 (1).pdf`.
- Classification: `DATABASE_PAPER`; route: `RESOURCE_ROUTE`, confidence `HIGH`.
- Runtime: `model_calls=0`, `experiment_instances=0`, evidence verification disabled.
- Historical frequency/co-occurrence remain Bronze priors; output explicitly separates them from evidence and recommendation.

### Primary experimental

- Repository regression document with explicit engineered E. coli culture/titer methods routes to `PRIMARY_EXPERIMENTAL_ROUTE` and permits `ExperimentInstance`.
- Existing extractor cache/transport tests continue through the primary route.
- A new live LLM extraction was not required for this implementation and is not claimed as a Human Gold replay.

### Candidate-specific model replay

- Host/model: E. coli, bundled SBML whose internal model identity is `iJO1366`.
- Product reaction: `EX_trp__L_e`; biomass: `BIOMASS_Ec_iJO1366_core_53p95M`.
- Candidate: declared `b3708`/tnaA knockout.
- Medium includes glucose and oxygen bounds; baseline and candidate growth/product objectives plus candidate FVA were solved by cobrapy and persisted.

## Tests and regression

- Focused reference-optimization suite: **18 passed**.
- Combined routing, grounding, paper-extraction contract, and affected engineering chains: **70 passed**, 2 cobra/SWIG deprecation warnings.
- Restored affected engineering groups: handoff **7 passed**; build/governance, E2E Trp, and memory/outcome **18 passed**.
- Full `python -m pytest -q` was attempted. It reached about 88% in 483 s before the execution window terminated and had already shown failures in broader legacy groups. A complete green full-suite result is therefore **not claimed**.
- Confirmed pre-existing failure class: engineering fixtures previously attempted actionable diagnosis without observations/baseline/EngineeringProblem; they failed the pre-existing Observation Grounding gate. The shared fixture is now scientifically grounded.
- Directly introduced extraction-test mismatch: five cache/transport tests used `paper`/`x` as their entire document and were correctly routed to UNKNOWN/human review by the new gate. Their fixtures were changed to explicit primary wet-lab text; all affected tests pass.

## Known limitations and remaining blockers

1. Apply quantitative role objects during all legacy field projections, not only the new typed path.
2. Require a persisted `DiagnosisFinding` in every production candidate-generation entry point and backfill legacy rows as `LEGACY_UNVERIFIED`.
3. Consolidate old candidate status/readiness mutations behind `transition_candidate`.
4. Extend EvidenceNeed acceptance to append a new `HypothesisVersion`/claim state and record before/after graph snapshots.
5. Wire failure recall directly into the production portfolio rank computation.
6. Build the minimal frontend panels for finding/prior/evidence-need/model status; current route adapter exposes the data contract only.
7. Run the remaining full backend suite in module shards and resolve unrelated legacy failures/timeouts before a release-level PASS.

## Changed areas

`harness/paper_extraction`, `harness/literature_discovery`, `harness/diagnosis`, `harness/evidence_retrieval`, `harness/engineering_design`, `harness/evaluation`, `harness/bootstrap.py`, `tests/reference_optimization`, `tests/paper_extraction/test_unified_extraction.py`, and `tests/engineering_design/fixtures.py`.
