# Diagnosis / Engineering Design Workbench Validation Report

Date: 2026-08-12  
Final status: **PARTIAL**

## Automated validation

- Frontend TypeScript: PASS (`npm run typecheck`).
- Frontend production build: PASS (`npm run build`, 2316 modules transformed).
- Focused backend regression: PASS, 83 tests (`diagnosis`, `engineering_design`, `evaluation_metrics`).
- New workbench read-model tests: PASS, 2 tests included in the 83.
- Frontend tests: 42/43 PASS. One reproducible failure is in the untouched Command Center test: its `listIdeas` mock returns an array while the current component consumes `{ideas: [...]}`, so the expected idea text is absent. This failure is outside the modified workbenches but cannot be proven from a clean pre-task run; it is recorded rather than claimed harmless.

New failures introduced by this task: no failure has been identified in modified code. The full frontend suite is nevertheless not green due to the Command Center case above.

## Real project / network validation

Application launched successfully on real local services. Target routes returned HTTP 200:

- `/projects/PROJ-3f77f638302b/diagnosis`
- `/projects/PROJ-3f77f638302b/design`

All workbench data endpoints returned HTTP 200, including project context, sessions, hypotheses, evidence, evidence items, decisions, tests, model capabilities, design summaries, handoff, strategies, candidates and the new evaluations collection. Target-project evaluations returned the expected successful empty result. No required workbench request returned 404/500 in the final endpoint audit.

## Browser / visual validation

Headless Chrome rendered both real target URLs without a white screen or visible layout break. Screenshots:

- `artifacts/diagnosis_workbench_final.png`
- `artifacts/design_workbench_final.png`

Visual inspection confirms the first screens expose target, host, missing substrate, evidence strength/coverage, supported versus unresolved diagnoses, candidate/evaluator state and validation readiness. Candidate expansion, hypothesis expansion, cross-workbench navigation and operational deep links are implemented as native controls/links. A fully instrumented Playwright console-event capture was unavailable; visual rendering plus explicit endpoint audit was used. This limitation prevents a strict PASS under the prompt's browser-console criterion.

## Missing capabilities, impact, next action

| Missing capability | Reason | Impact | Recommended next action |
|---|---|---|---|
| Project substrate | Not in current project contract | Cannot condition scientific claims on carbon source | Add substrate to project context through a separately reviewed schema change |
| Project model computation | No GEM/kinetic run for target diagnosis | No flux/yield/growth quantitative grounding | Configure model inputs and persist a target-scoped run |
| Evaluator results | Portfolio is generated but unevaluated | No candidate can be selected/rejected by M11 | Run existing evaluator suite and resolve blocking findings |
| Selected stack | No evaluator/human selection | Engineering combination remains proposed | Record selection only after gates and human approval |
| Build/test package | No candidate advanced to planning | Validation plan remains a framework, not an executable protocol | Draft package through existing candidate workflow |
| Process design (M9) | No process modifications generated | Fermentation optimization is not covered | Add a grounded process strategy after conditions are specified |
| Unified epistemic/quantitative envelope | Existing producers use heterogeneous fields | Presentation mapping remains conservative/partial | Standardize in a future backward-compatible contract |
| Full browser console automation | No installed Playwright/Selenium harness | Console absence not programmatically certified | Add Playwright E2E to repository CI |

## FINAL SELF-CHECK

### A. Repository truth

- [x] Read the current implementation rather than implementing prompt assumptions.
- [x] Distinguished schema existence, platform capability and target-project result.
- [x] Inspected real `PROJ-3f77f638302b` database records.

### B. Diagnosis

- [x] Answers why the goal may not be reached.
- [x] Separates observation/mechanism/evidence in the competition view.
- [x] Shows conservative coverage with explicit not-evaluated axes.
- [x] Shows competing hypotheses.
- [x] Shows evidence against separately.
- [x] Shows quantitative grounding state without fake values.
- [x] Shows unresolved state.

### C. Design

- [x] Driven by a versioned diagnosis handoff.
- [x] Shows alternatives.
- [x] Shows dependencies/conflicts where persisted and marks gaps.
- [x] Shows rejected/excluded reasons.
- [x] Shows selected-stack section with honest empty state.
- [x] Shows validation-plan readiness.

### D. Evaluator

- [x] Displays hard gates as separate dimensions.
- [x] Avoids an opaque composite score.
- [x] Essentiality is an explicit gate.
- [x] Pathway integrity is an explicit gate.
- [x] Evidence calibration is an explicit gate.
- [x] Provenance is an explicit gate.

### E. Epistemics

- [x] Measured/computed/predicted states are distinguished.
- [x] Hard/soft evidence is distinguished.
- [x] Fact/inference/hypothesis states are distinguished conservatively.
- [x] No fake scientific number was added.
- [x] No citation was fabricated.

### F. Engineering

- [x] Reused existing capabilities.
- [x] Did not duplicate ontology.
- [x] Preserved existing routes and response compatibility.
- [x] Did not reset or clean the user's worktree.
- [x] Modified-code typecheck/build and focused backend tests pass.

### G. Browser

- [x] Diagnosis URL actually opened and rendered.
- [x] Design URL actually opened and rendered.
- [x] Required API/network endpoints checked.
- [ ] Browser console was not captured by an instrumented E2E harness.
- [x] Provenance is visible through evidence identifiers/expanded rows and deep links.
- [x] Selected/rejected states and reasons are visible, including honest empty states.

## Final determination

**PARTIAL** — the core workbenches are usable and scientifically honest for the real project, but the target project lacks model/evaluator/build-test results, the full frontend test suite has one unrelated reproducible failure, and browser console capture was not instrumented. Reporting PASS would overstate verification and scientific completeness.
