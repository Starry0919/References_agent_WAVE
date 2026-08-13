# P0 Gap Implementation Plan

> Companion to `P0_GAP_RESOLUTION_ARCHITECTURE_DESIGN.md`.
> This is an execution plan, not an implementation-completion report.

## 1. Delivery objective

Deliver one enforceable, audited path from project observations to diagnosis, evaluated human-selected designs, a project-specific validation plan, experiment observations, and learning. P0-1 must land before P0-2, and P0-2 before P0-3, because selection and validation must never rest on an ungrounded diagnosis or unevaluated portfolio.

## 2. Work sequence and dependencies

| Order | Work package | Depends on | Exit condition |
|---:|---|---|---|
| 0 | Contract fixtures and policy/version conventions | None | Failing tests encode the three gaps and legacy behavior. |
| 1 | P0-1 Observation grounding | 0 | Ungrounded diagnosis cannot become actionable/handoff-ready. |
| 2 | P0-2 Evaluator and human selection | 1 | Portfolio lands in evaluation-required and cannot plan/build before governed selection. |
| 3 | P0-3 Validation plan and experiment bridge | 2 | Selected candidate yields a readiness-gated, project-specific experiment plan. |
| 4 | Unified E2E acceptance and enforcement rollout | 1-3 | Tryptophan fixture completes full trace with negative-path proofs. |

No package is complete merely because an endpoint responds or a UI component renders.

## 3. WP0 — contracts, fixtures and safeguards

### Tasks

1. Freeze representative legacy fixtures: an observation-free diagnosis, a generated-but-unevaluated portfolio, and an existing build-test package.
2. Add policy identifiers: `observation-grounding-v1`, `design-evaluation-v1`, `validation-readiness-v1`.
3. Define shared structured gate result and API error projection without collapsing domain-specific details.
4. Add feature flags for observe-only/enforced gating and a compatibility-state mapper.
5. Establish an E. coli K-12 tryptophan fixture with explicit data assets, strain/context, matched baseline, target-capable model, reaction mappings and candidate interventions.

### Primary files

- `harness/config.py`
- `harness/workflow/contracts.py`
- `harness/orchestrator/contracts.py`
- `harness/orchestrator/gates.py`
- test factories/fixtures under `tests/`

### Tests first

- A gate result always contains policy version, evaluated record IDs and blocking reasons.
- Legacy state mapping never reports `portfolio_generated` as completed.
- Feature-flag observe mode logs a would-block event without advancing incorrectly in acceptance tests.

## 4. WP1 — P0-1 Observation grounding

### 4.1 Domain and persistence

1. Keep `harness/experiments/models.py::Observation` canonical; add only a subject-resolution field if existing design/construct/biological-context links cannot identify a strain.
2. Add `EngineeringProblem` to the diagnosis domain with immutable observation/comparator IDs, normalized values/deltas, descriptive abnormality and derivation provenance.
3. Add idempotent schema migration in `harness/migrations.py`, indexes and foreign-key checks.
4. Implement deterministic unit-aware comparator service. Reject incompatible conditions/units unless an explicit validated normalization exists.
5. Implement `ObservationReliabilityAssessment` as a derived view from QC, replicates, uncertainty and detection limits; do not persist a free confidence number as truth.

### 4.2 Gates and workflow

1. Implement repository-backed `ObservationGroundingGate` in the diagnosis/workflow boundary.
2. Replace boolean sufficiency authority in diagnosis service/loop with gate output; retain request booleans only as UI hints.
3. Update actionability and handoff guards to require grounded engineering problems.
4. Add claim-type quantitative requirements. Metabolic yield/flux/essentiality claims must link an applicable model run or declare non-computability.
5. Preserve exploratory hypothesis generation but mark it non-actionable and prevent approval/handoff.

### 4.3 API and frontend

1. Add observation normalization, grounding-report and engineering-problem endpoints in `harness/api/diagnosis.py`, reusing `harness/diagnosis/normalizer.py`.
2. Extend `frontend/src/api/diagnosis.ts` types and calls.
3. Update `frontend/src/pages/diagnosis/RunNewDiagnosisPage.tsx` for structured observation/subject/condition/provenance input or file import.
4. Update `DiagnosisSessionDetailPage.tsx` with observed-vs-comparator deltas, provenance, QC and explicit blockers.
5. Label measured facts, derived abnormalities, causal hypotheses, literature priors and model predictions distinctly.

### Primary backend files

- `harness/experiments/models.py`
- `harness/diagnosis/models.py`
- `harness/diagnosis/normalizer.py`
- `harness/diagnosis/service.py`
- `harness/diagnosis/loop.py`
- `harness/workflow/gates.py`
- `harness/api/diagnosis.py`
- `harness/orchestrator/adapters.py`
- `harness/orchestrator/service.py`
- `harness/migrations.py`

### Required tests

- Model validation for numeric values, units, QC and subject/context resolution.
- Idempotent ingestion and immutable observation behavior.
- Matched baseline delta correctness, unit conversion, detection limits and mismatched-condition rejection.
- No observation -> `data_required`; assertion-only -> non-actionable; failed QC -> blocked.
- Grounded observation pair -> reproducible `EngineeringProblem`.
- A causal phrase cannot be saved as a descriptive abnormality.
- Metabolic bottleneck claim without applicable model run is visibly insufficient.
- Approval and handoff endpoints return structured `409` while blocked.
- Frontend tests show blockers and never label an expert rule as measured evidence.

### Definition of done

- The gate reads persisted records, not client booleans.
- Every actionable diagnosis traces to at least one accepted observation and one reproducible engineering problem.
- Existing ungrounded sessions are readable and labeled `legacy_ungrounded`, not silently backfilled.

## 5. WP2 — P0-2 Evaluator and human selection

### 5.1 State machine correction

1. Add native `evaluation_required` and `selection_required` states in `harness/engineering_design/loop.py` and persistence enums/contracts.
2. Make portfolio generation persist the portfolio atomically and transition the design project to `evaluation_required`.
3. Change orchestrator `DesignAdapter` completion logic: portfolio generation is progress, not completion.
4. Map legacy `portfolio_generated` projects to resumable `evaluation_required` with an audit event.
5. Require evaluation snapshot completion before selection, and confirmed selection before planning/build.

### 5.2 Evaluator completeness

1. Reuse the evaluator runner and `DesignEvaluation`; add explicit hard-failure codes and structured soft-score entries where absent.
2. Implement claim-support coverage and provenance-resolution gates.
3. Include contradicting evidence and unresolved alternative hypotheses in mechanism/evidence evaluation.
4. Implement essentiality and severe growth-coupling checks through the gene registry and applicable GEM run. Persist model/constraint/version references.
5. Tighten buildability to resolve targets, operations, constructs, required resources and governance constraints.
6. Keep unknown values unknown. Do not introduce a magic weighted total.
7. Run Pareto ranking on eligible candidates. Produce preference rank only from an explicit, versioned preference policy.

### 5.3 Selection persistence and API

1. Add append-only `DesignSelectionDecision` plus candidate decision rows and migration/indexes.
2. Validate exact portfolio/evaluation versions with optimistic concurrency.
3. Permit selection only from eligible candidates or governed exceptions.
4. Require reason codes/text for rejected or deferred candidates.
5. Materialize candidate `selection_status` only as a view/cache derived from the decision record.
6. Extend engineering-design endpoints for evaluation summaries and selection decisions.

### 5.4 Frontend

1. Add Evaluation and Selection as mandatory stages in `DesignProjectDetailPage.tsx` and workflow status helpers.
2. Build a comparison table with hard failures, claim/evidence provenance, soft dimensions, uncertainty and Pareto front.
3. Require explicit human selection and rejection/defer reasons.
4. Disable planning/build actions with exact gate blockers and stale-version warnings.

### Primary backend files

- `harness/engineering_design/models.py`
- `harness/engineering_design/loop.py`
- `harness/engineering_design/evaluation_service.py`
- `harness/engineering_design/evidence_resolution.py`
- `harness/engineering_design/decision.py`
- `harness/engineering_design/evaluators/*.py`
- `harness/engineering_design/portfolio_service.py`
- `harness/engineering_design/governance_service.py`
- `harness/api/engineering_design.py`
- `harness/orchestrator/adapters.py`
- `harness/orchestrator/service.py`
- `harness/migrations.py`

### Required tests

- Portfolio generation ends in `evaluation_required` in domain, API and orchestrator projections.
- Incomplete/failed evaluator run cannot reach selection.
- Each material claim has support or a hard failure.
- Missing provenance, unresolved contradiction, essentiality and build infeasibility trigger deterministic failure codes.
- Soft scores preserve basis, direction, uncertainty and unknown status.
- Pareto fronts are stable for fixed inputs; baseline/control is not selectable.
- Stale evaluation snapshot selection returns conflict.
- Ineligible candidate selection is rejected absent a governed exception.
- Planning/build endpoints reject projects with no confirmed selection.
- UI cannot imply that evaluator recommendation equals human selection.

### Definition of done

- Every portfolio is evaluated or visibly awaiting evaluation.
- Every selectable candidate has a completed evaluator snapshot.
- Every selected/rejected/deferred result has a human/audit record and exact reviewed versions.
- No design project is reported completed at portfolio generation.

## 6. WP3 — P0-3 Validation plan and experiment bridge

### 6.1 Domain and service

1. Add versioned `ValidationPlan` aggregate linked to confirmed selection, candidate version, engineering problems, hypotheses, `BuildTestPackage` and `ExperimentPlan`.
2. Extend `build_test_planner.py` to draft from the selected candidate and diagnosis trace, never a generic template detached from project context.
3. Implement `ValidationReadinessGate` with machine-readable blockers.
4. Materialize the existing `ExperimentPlan` only after readiness; keep approval in the existing experiment/governance workflow.
5. Freeze the validation-plan version used by each experiment run.
6. Implement deterministic comparison of accepted result observations against criteria and decision rules.
7. Route outcomes to learning, redesign or reopened diagnosis through the unified orchestrator.

### 6.2 API and frontend

1. Add draft/version/readiness/materialization endpoints to `harness/api/engineering_design.py` and link results in `harness/api/experiments.py`.
2. Extend `frontend/src/api/engineeringDesign.ts`, `experiments.ts` and `orchestrator.ts`.
3. Add a validation workspace to the design detail page with concrete conditions, controls, replication, sampling, readouts, QC and criteria.
4. Provide a criterion evaluator preview and exact missing-field blockers.
5. Show experiment results as observed vs predicted/required values and the resulting next decision.

### Primary backend files

- `harness/engineering_design/models.py`
- `harness/engineering_design/build_test_planner.py`
- `harness/engineering_design/outcome_service.py`
- `harness/experiments/models.py`
- `harness/experiments/service.py`
- `harness/experiments/ingestion/service.py`
- `harness/api/engineering_design.py`
- `harness/api/experiments.py`
- `harness/orchestrator/models.py`
- `harness/orchestrator/adapters.py`
- `harness/orchestrator/service.py`
- `harness/api/learning.py`
- `harness/migrations.py`

### Required tests

- No selection -> validation draft rejected.
- Stale candidate/evaluation version -> rejected.
- Placeholder/generic conditions or criteria -> `insufficient`.
- Missing controls, replicates, QC, mechanism readout or decision rule -> deterministic blockers.
- A complete project-specific plan becomes ready and materializes exactly one idempotent `ExperimentPlan`.
- Approved plan amendment creates a new version and preserves the executed version.
- Ingested experimental data yields accepted/rejected observations with provenance.
- Criteria handle units, uncertainty, failed QC, missing timepoints and protocol deviations.
- Success advances; ambiguous result requests more data; falsification reopens diagnosis; intervention failure triggers redesign as declared.

### Definition of done

- A selected candidate has a concrete, traceable and machine-checkable validation plan.
- Experiment planning cannot bypass selection or readiness.
- Results close the loop through canonical observations and an audited next decision.

## 7. WP4 — end-to-end scientific acceptance

Use one controlled tryptophan project and run both positive and negative paths.

### Positive path

1. Ingest target-strain and matched-baseline observations with explicit assay/QC/provenance.
2. Derive a descriptive titer/yield engineering problem.
3. Generate competing causal hypotheses across applicable M1-M5 modules.
4. Resolve hard/soft evidence and run target-capable yield/flux/essentiality analyses with declared assumptions.
5. Approve a grounded diagnosis and hand it to design.
6. Generate multiple intervention candidates and an explicit baseline/control.
7. Run evaluator; demonstrate hard gates, soft scorecards and Pareto comparison.
8. Record human selection/rejection reasons.
9. Produce a project-specific validation plan with mechanism and phenotype readouts, controls, replicates, QC, thresholds and decision rules.
10. Materialize/approve an experiment, ingest results, compare outcomes and update learning state.

### Negative proofs

- Observation-free diagnosis is blocked.
- A free-text “low precursor” input is not accepted as observation.
- `e_coli_core` biomass-only FBA cannot ground a tryptophan-specific metabolic claim.
- Missing provenance and essential-gene intervention hard-fail evaluation.
- Portfolio generation alone is never completed.
- Evaluator recommendation does not auto-select.
- Generic validation templates never become ready.

### Acceptance artifacts

- API/integration test report and frontend test report.
- Full audit export of object IDs, versions, transitions and actors.
- Evidence/claim/model lineage report.
- Rendered screenshots of diagnosis grounding, evaluation/selection and validation/result views.
- Updated `DIAGNOSIS_DESIGN_FINAL_ACCEPTANCE_REPORT.md` with evidence-backed status, retaining `PARTIAL` for any unmet item.

## 8. Migration and rollout procedure

1. Ship additive schema and compatibility readers first.
2. Run migration twice in CI to prove idempotency; test a copy of real dev data.
3. Enable `observe_only` and collect would-block classifications for legacy sessions/projects.
4. Correct genuine false positives in policy or data resolution; never synthesize observations/evaluations.
5. Enforce on new diagnosis/design projects.
6. Mark active legacy records with explicit classifications and require remediation on next mutation.
7. Enforce on all active records after audit sign-off.

Rollback disables enforcement/routing and returns new projects to safe waiting states. It must not drop tables, delete decisions, or rewrite audit history.

## 9. Risks and mitigations

| Risk | Consequence | Mitigation |
|---|---|---|
| Observation fields are present but subject/context cannot resolve | False grounding | Central subject resolver; fail closed with actionable missing fields. |
| “Hard evidence” overstates a model prediction | Scientific overclaim | Claim-specific evidence taxonomy; persist assumptions and separate computed constraints from measured biology. |
| Evaluator becomes a hidden weighted ranker | Unreviewable decisions | Structured scorecard, unknown preservation, Pareto default, explicit preference policy only. |
| State changes break legacy projects | Lost resumability | Compatibility mapper, additive states, observe-only audit and fixture tests. |
| Validation plan duplicates ExperimentPlan/BuildTestPackage | Divergent truths | ValidationPlan is a traceability aggregate; existing records own build/execution details. |
| LLM fills missing experimental details convincingly | Unsafe/generic execution | Field provenance, placeholder detection, readiness fail-closed, human approval. |
| Concurrent portfolio revision invalidates selection | Wrong candidate version built | Immutable versions and optimistic concurrency/ETag checks. |

## 10. Review gates and ownership

Each work package requires four sign-offs before enforcement:

- Scientific: evidence semantics, model applicability, causal-vs-descriptive separation.
- Engineering: migrations, concurrency, idempotency, state recovery and audit integrity.
- Experimental: controls, replication, QC, criteria and executability.
- Product/teacher alignment: the visible flow implements goal-observation-hypothesis-evidence-modification-validation-result and M11 rejection/iteration.

If any sign-off lacks runtime evidence, report the package as `PARTIAL`; do not infer completion from code presence.

## 11. Final implementation readiness assessment

- Architecture dependencies: **READY**.
- Existing-contract reuse plan: **READY**.
- File-level implementation map: **READY**.
- Migration and compatibility strategy: **READY**.
- Test and E2E acceptance plan: **READY**.
- Runtime P0 gaps: **NOT YET RESOLVED**.

Recommended execution start: WP0 followed by WP1. Do not begin validation-plan UI work before the selection contract and gates are stable.
