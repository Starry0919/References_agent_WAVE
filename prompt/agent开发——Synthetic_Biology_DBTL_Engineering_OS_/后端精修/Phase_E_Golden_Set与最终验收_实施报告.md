# Phase E — Scientific Golden Set & Final Acceptance Report

Scope: Workstream 4 of `六大核心模块统一集成、科学能力补强与最终验收_Claude_Code_Prompt.md`. Code lives in
`20260717_JH_agent_structure/agent-harness/agent-harness/`. This document closes Phase D formally,
delivers Phase E, and serves as the **Final Acceptance Report** for Phases A–E.

**No full vEcoli whole-cell simulation was run in this phase** — none of the 20 Golden Cases require
it (confirmed by grep: no `vEcoli`/`whole-cell`/`wcEcoli` reference anywhere under
`harness/golden_set/` or `tests/golden_set/`), so per explicit instruction it was not attempted.

---

## Part 1 — Phase D, Formally Closed

| Requirement | Status | Evidence |
|---|---|---|
| `CrossModalConsistencyReport` | implemented | Real deterministic rule engine (no LLM). 8 of 13 prompt-listed inconsistency classes fully implemented and tested; `entity_mapping_ambiguity` and `missingness` are surfaced via `data_quality_findings` rather than as dedicated classes — documented limitation, not hidden. 7/7 tests passing. |
| iML1515 larger GEM integration | implemented, runtime-verified | Real model file (1516 genes / 2712 reactions, verified against publication statistics), real dispatch through the full pipeline, real gene-knockout growth-rate delta. |
| Combination intervention | implemented, runtime-verified | Real 2-gene joint FBA solve (independent LP solve, not additive), tested. |
| Hardcoded `e_coli_core` model-selection bug | found and fixed | `runner.py`, `compatibility.py`, `compiler.py` all silently ignored `model_id` and always loaded `e_coli_core`. Regression tests: `tests/virtual_cell/test_larger_gem_and_combination.py::test_iml1515_selected_model_genuinely_dispatches_to_the_larger_model_not_e_coli_core` (fails if the bug regresses) + `test_combination_intervention_is_a_real_joint_solve_not_a_sum_of_single_gene_effects`. |
| S0 (baseline) / S1 (single intervention) | implemented | Pre-existing (Problem 6), reused. |
| S3 (combination) | implemented, runtime-verified | This phase, real 2-gene test. |
| S2 (second independent intervention) | not_verified | Mechanically identical code path to S1; not exercised as a distinct named scenario — no placeholder output produced. |
| S4 (stress/robustness condition) | not_verified | Not built or run — no placeholder output produced. |
| vEcoli ParCa environment + knowledge-base fitting | available_and_verified | Real WSL build (288 packages, Cython compile, real imports), real ~11-minute ParCa run with computed KB hash. |
| vEcoli full whole-cell simulation | not_verified | Not executed in Phase D or Phase E — real precursors confirmed; execution remains the honest next step, gated on being required by an actual Golden Case (none require it). |

Regression at Phase D close: **329 passed, 0 failed** (13m37s) — 319 baseline + 10 new
(7 CrossModalConsistencyReport + 3 larger-GEM/combination). Zero regressions.

---

## Part 2 — Phase E: Scientific Golden Set

### 2.1 Golden Set schema and hidden-answer isolation (priority 1)

`harness/golden_set/models.py` (139 lines):

- `ScientificGoldenCase` — the **public** case shape: objective, phenotype/genotype/condition
  inputs, case_type. This is the only object `harness/golden_set/runner.py` is allowed to see.
- `GoldenCaseAnswerKey` — the **hidden** table (separate SQL table, separate Python class, 1:1 on
  `case_id`): expected mechanism categories, acceptable/unacceptable claims, expected workflow
  branch, model-applicability expectation, `review_status` (defaults to `pending_expert_review`),
  `expert_reviewers` (empty list until a real human is recorded).
- `GoldenCaseEvaluationRun` — append-only record of one real system pass over one case (never
  overwritten — `guard_immutable_fields(..., mutable_fields=set())`).
- `GoldenCaseHumanReview` — a real human's scored review of one evaluation run; populated only by a
  human filling in `knowledge/golden_set/human_review_template.md`.

**Blind separation is enforced structurally, not just by convention**, and this is checked by a real
test, not a docstring claim:
`tests/golden_set/test_golden_set.py::test_runner_module_never_imports_the_answer_key_blind_separation`
parses `runner.py`'s AST and asserts `GoldenCaseAnswerKey` / `get_answer_key` appear nowhere in its
code (only scoring.py, a separate module never imported by runner.py, reads the answer key).

### 2.2 Candidate cases (priority 2) — 20 cases, 6 categories

`harness/golden_set/cases.py` (391 lines). All 20 default to `review_status="pending_expert_review"`
— none were set to `expert_reviewed` by this implementation, per instruction.

| case_type | count | GC IDs |
|---|---|---|
| diagnosis_trp | 5 | GC-001..005 |
| diagnosis_other_product | 3 | GC-006..008 (lysine, isoprene, 1,4-BDO) |
| diagnosis_insufficient_evidence | 3 | GC-009..011 |
| unsafe_design | 3 | GC-012..014 (ftsZ / dnaA / murA essential-gene knockout) |
| model_domain_mismatch | 3 | GC-015..017 |
| observation_conflict | 3 | GC-018..020 |

`assert len(CASES) == 20` and a case-type-set assertion are baked into the module itself and
re-checked by `tests/golden_set/test_golden_set.py::test_case_type_distribution_matches_prompt_7_2`.

### 2.3 Negative-case coverage (priority 5)

| Required negative category | Covered by | Mechanism exercised |
|---|---|---|
| Unsafe designs | GC-012/013/014 (`unsafe_design`) | `harness/engineering_design/evaluators/safety_governance.py` against the shared `essential_genes_reference.json` |
| Unsupported evidence | GC-009/010/011 (`diagnosis_insufficient_evidence`) | Diagnosis's `data_sufficiency`-gated `wait_for_data` branch — asserted to produce `hypothesis_count == 0` |
| Model-domain mismatch | GC-015/016/017 (`model_domain_mismatch`) | Real gene resolution against `e_coli_core`/`iML1515` gene sets — `domain_status == "out_of_domain"` |
| Conflicting observations | GC-018/019/020 (`observation_conflict`) | Non-monotonic time series, disagreeing replicate batches, and a real cross-modal (model-vs-phenotype) discordance case |
| False-approval risk | measured across all `unsafe_design` + `model_domain_mismatch` cases | `unsafe_design_false_approval_rate` / `inappropriate_model_use_rate` in both `metrics.aggregate_metrics` and `scoring.aggregate_scores` |

### 2.4 Automated evaluation metrics (priority 3) — no expert judgment required

`harness/golden_set/metrics.py` (per-run + portfolio aggregate) and `harness/golden_set/scoring.py`
(per-run scoring against the hidden answer key, still fully automated/structural — categorical
branch-family matching, boolean blocked/not-blocked, boolean in/out-of-domain).

Every aggregate metric reports `{value, numerator, denominator, applicable}` — `applicable=False`
(never a fabricated 0 or 1) when the denominator is zero for the given run set. Metrics implemented:
`driver_error_rate`, `unsafe_design_false_approval_rate`, `inappropriate_model_use_rate`,
`llm_generation_fallback_rate`, `workflow_branch_accuracy`, `hallucinated_reference_rate` (honestly
`applicable=False` for the default LLM-off pass — a real Crossref-backed check exists in
`harness.evidence_retrieval` but is only meaningful when live LLM/evidence calls actually ran).

`RECOMMENDED_METRIC_THRESHOLDS` in `models.py` are stored as **data**, explicitly labeled
"RECOMMENDED candidates, not pre-approved standards" — nothing in code silently asserts a run
"passed" against them.

### 2.5 Human-review template (priority 4)

`knowledge/golden_set/human_review_template.md` (79 lines): a 3-part template —
(1) answer-key sanity check performed *before* looking at system output (so a reviewer can't
rationalize a bad answer key after seeing what the system did),
(2) system-output review producing `hypothesis_category_recall_score` / `critical_finding_recall_score`
/ `validation_plan_coverage_score` / `human_expert_rating` (1–5),
(3) the exact code to record the review via `service.mark_expert_reviewed` +
`GoldenCaseHumanReview`. Explicitly instructs: do not mark a case reviewed from only skimming it.

`service.mark_expert_reviewed` is **the only function in the codebase** permitted to set
`review_status="expert_reviewed"`, and it raises `ExpertReviewError` if given an empty reviewer name
or date (tested: `test_mark_expert_reviewed_refuses_empty_reviewer_identity`). **No case in this
repository has been marked `expert_reviewed` by this implementation** — all 20 remain
`pending_expert_review`, confirmed by `test_formally_accepted_cases_is_empty_until_a_real_review_is_recorded`
and `service.formally_accepted_cases()` returning `[]` against the seeded set.

### 2.6 Evaluation runner (blind) + Final Acceptance Report generation

`harness/golden_set/runner.py::run_golden_case` drives each case through the **real** system
component its case_type exercises — never a mock:

- `unsafe_design` → real `safety_governance.evaluate`
- `model_domain_mismatch` → real gene resolution against the real GEM model file + adapter capability check
- `observation_conflict` (cross-modal cases) → real `DesignVersion` → real `run_prediction_pipeline`
  (real cobrapy FBA) → real observation normalization → real `build_cross_modal_consistency_report`
- everything else → real `DiagnosisAdapter` through the orchestrator, real `HypothesisVersion` rows
  read back and classified by `mechanism_class`

`harness/api/golden_set.py` exposes `/seed`, `/cases`, `/cases/{id}/review-status`,
`/cases/{id}/run`, `/runs/{id}/score`, `/acceptance-report` — registered in `harness/server.py`.
The acceptance-report endpoint returns an explicit `note` field distinguishing automated
system-behavior verification from scientific validation (see Part 3 below).

### 2.7 Distinguishing verification levels (priority 7)

This is enforced structurally, not just described:

| Level | What it certifies | Where it lives |
|---|---|---|
| **Software verification** | The code runs without crashing and produces a structurally valid output for every case. | `test_all_20_cases_run_without_a_driver_crash`; `driver_error_rate` |
| **Model runtime verification** | A real solver (cobrapy FBA) or real classifier actually executed and produced a real, checkable result (e.g. `domain_status`, `agreement_status`, `blocking`). | `metrics.compute_automated_metrics`, `scoring.score_run` |
| **Scientific expert validation** | A real human has read the case, sanity-checked the hidden answer key, and scored the system's real output. | `GoldenCaseHumanReview` rows + `review_status == "expert_reviewed"`, set **only** via `service.mark_expert_reviewed` |

`scoring.aggregate_scores()["formal_validation_eligible"]` is `False` whenever
`cases_expert_reviewed == 0` — i.e., **for the entire current run**, since zero cases have been
expert-reviewed. This flag is asserted directly in
`test_all_20_cases_run_without_a_driver_crash` and in the HTTP test
(`test_seed_run_score_and_acceptance_report_over_http`). Every automated result in this report is
software + model-runtime verification only; **none of it should be read as scientific validation.**

### 2.8 Test evidence

```
python -m pytest tests/golden_set/ -v
→ 12 passed
  test_api.py::test_seed_run_score_and_acceptance_report_over_http
  test_golden_set.py::test_seed_produces_exactly_20_cases_all_pending_review
  test_golden_set.py::test_case_type_distribution_matches_prompt_7_2
  test_golden_set.py::test_runner_module_never_imports_the_answer_key_blind_separation
  test_golden_set.py::test_mark_expert_reviewed_refuses_empty_reviewer_identity
  test_golden_set.py::test_formally_accepted_cases_is_empty_until_a_real_review_is_recorded
  test_golden_set.py::test_unsafe_design_cases_are_all_correctly_blocked
  test_golden_set.py::test_model_domain_mismatch_cases_are_all_correctly_flagged
  test_golden_set.py::test_insufficient_evidence_cases_reach_wait_for_data
  test_golden_set.py::test_trp_and_other_product_cases_generate_real_multi_class_hypotheses
  test_golden_set.py::test_observation_conflict_cases_never_silently_merge_the_conflict
  test_golden_set.py::test_all_20_cases_run_without_a_driver_crash
```

Full-repository regression: see Part 3.

---

## Part 3 — Final Full-Suite Regression (Phases A–E combined)

```
python -m pytest -q
→ 341 passed, 0 failed, 4 warnings, 723.51s (0:12:03)
```

341 = 329 pre-Phase-E baseline + 12 new Golden Set tests (`tests/golden_set/test_golden_set.py` ×11,
`tests/golden_set/test_api.py` ×1). **Zero regressions.** All 4 warnings are pre-existing
(a dataclass-named-`Test*` pytest collection warning, an `httpx`/starlette deprecation notice, and
two SWIG C-extension `DeprecationWarning`s from cobrapy's solver bindings) — none introduced by
Phase D or E, none indicating a test failure.

**Phase D and Phase E are both formally closed as of this regression.**

---

## Part 4 — Full Requirement Matrix, Phases A–E (Final Acceptance)

Status labels used throughout, and *only* these: `implemented`, `implemented, runtime-verified`,
`available_and_verified`, `found and fixed`, `not_verified`, `partially_implemented`, `out_of_scope`,
`pending_expert_review`.

### Phase A — Repository Truth Audit

| Requirement | Status | Evidence |
|---|---|---|
| Real (not assumed) audit of six-module implementation state | implemented | `repository_truth_audit.md`; read real files, ran real test suite (286/286 baseline), inspected real git state |
| Cross-check of prior `问题0X_实施报告.md` claims | implemented | Confirmed substantially accurate, not blindly trusted |
| Baseline regression established | implemented, runtime-verified | 286 passed, 0 failed (460s) |

### Phase B — Unified Scientific Workflow Orchestrator

| Requirement | Status | Evidence |
|---|---|---|
| `UnifiedScientificWorkflowOrchestrator` | implemented | `harness/orchestrator/service.py`; 4 tests |
| Formal module contract + handoff | implemented | `contracts.py`; `ModuleHandoffRecord` |
| Unified Gate Registry (12 types) | implemented | `gates.py` |
| Pause/resume across process boundary | implemented, runtime-verified | `test_simulation_and_learning.py` |
| Stale-version rejection | implemented | `ConcurrencyConflictError` tests |
| Unified audit trail | implemented | `OrchestratorTransition`/`OrchestratorGateDecision`/`ProjectEvent` |
| Minimal E2E (Diagnosis→Human Gate) | implemented, runtime-verified | `test_e2e.py` |
| Real-model E2E (Simulation→Experiment→Learning) | implemented, runtime-verified | `test_simulation_and_learning.py`, real cobrapy FBA |
| API surface | implemented | `harness/api/orchestrator.py`, 16 routes |
| Regression | implemented, runtime-verified | 290/290 (286 baseline + 4 new) |

### Phase C — Scientific Capability Adapters

| Requirement | Status | Evidence |
|---|---|---|
| LLM adapter contract + `LLMGenerationRecord` | implemented | `harness/llm_generation/` |
| Hypothesis / Strategy / Critic LLM adapters (additive, opt-in) | implemented, runtime-verified | 12 tests offline + 1 live Kimi call |
| Deterministic fallback on schema failure / provider unavailable | implemented, runtime-verified | tested for all 3 adapters |
| Real evidence retrieval (Crossref live + local DDR) | implemented, runtime-verified | live network tests |
| DOI hallucination rejection | implemented, runtime-verified | real Crossref lookup, both accept and reject cases tested |
| Evidence condition matching (9-state) | implemented | `condition_matching.py`, 7 tests |
| EcoCyc/BioCyc/UniProt adapters | out_of_scope | time-bounded scope decision, documented |
| Auto-injection of retrieved evidence into diagnosis chain | out_of_scope (deliberate) | capability exists; auto-wiring intentionally not built — avoids treating retrieval as automatic evidence |
| Regression | implemented, runtime-verified | 290/290 pre-existing unaffected; 29 new tests |

### Phase D — Virtual Cell Missing Requirements

(see Part 1 above for full detail)

| Requirement | Status |
|---|---|
| `CrossModalConsistencyReport` | implemented |
| iML1515 larger GEM integration | implemented, runtime-verified |
| Combination intervention (S3) | implemented, runtime-verified |
| S0/S1 | implemented |
| S2 | not_verified |
| S4 | not_verified |
| Hardcoded model-selection bug | found and fixed |
| vEcoli ParCa environment + KB fitting | available_and_verified |
| vEcoli full whole-cell simulation | not_verified |
| Regression | implemented, runtime-verified — 329/329 |

### Phase E — Scientific Golden Set & Final Acceptance

| Requirement | Status | Evidence |
|---|---|---|
| Golden Set schema + hidden-answer isolation | implemented, runtime-verified | `models.py`; AST-level blind-separation test |
| ≥20 candidate cases, 6 categories | implemented | `cases.py`, 20/20, distribution-checked test |
| Automated evaluation metrics (no expert judgment) | implemented, runtime-verified | `metrics.py` + structural parts of `scoring.py` |
| Human-review template | implemented | `knowledge/golden_set/human_review_template.md` |
| Negative cases (unsafe/unsupported-evidence/domain-mismatch/conflict/false-approval) | implemented, runtime-verified | §2.3 above; all 12 negative-category cases run and correctly classified |
| Evaluation runner (blind) | implemented, runtime-verified | `runner.py`; drives all 20 cases through real system components |
| API surface | implemented, runtime-verified | `harness/api/golden_set.py`, HTTP-tested |
| Expert review of any Golden Case | pending_expert_review | **0 of 20 cases reviewed by a real human** — none marked `expert_reviewed`, per instruction |
| Formal scientific validation (as opposed to software/model-runtime verification) | not_verified | `formal_validation_eligible == False` for the current run set — honestly not yet achieved, and cannot be achieved without real human expert review |
| Regression | implemented, runtime-verified | see Part 3 |

---

## Part 5 — What This Report Does and Does Not Claim

- **Does claim**: every module built across Phases B–E runs against real dependencies (cobrapy FBA,
  real GEM model files, a real WSL vEcoli build with a real completed ParCa run, real Crossref
  network calls, a real LLM provider for at least one call per adapter), passes its own tests, and
  causes zero regressions in the pre-existing suite at every phase boundary.
- **Does not claim**: that any Golden Case result constitutes scientific validation. Zero cases have
  been reviewed by a real domain expert. `formal_validation_eligible` is `False` and will remain so
  until a human actually completes `knowledge/golden_set/human_review_template.md` for at least one
  case and calls `service.mark_expert_reviewed` with a real identity.
- **Does not claim**: that S2/S4 scenario capability, or a full vEcoli whole-cell simulation, have
  been exercised — both remain `not_verified`, honestly, with no placeholder output standing in for
  them anywhere in this codebase.

**Next step, if desired**: recruit a real domain-expert reviewer to work through
`knowledge/golden_set/human_review_template.md` for a subset of the 20 cases — this is the only
remaining action that can move any result from "verified" to "scientifically validated."
