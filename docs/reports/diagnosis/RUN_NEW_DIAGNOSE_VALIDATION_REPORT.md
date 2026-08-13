# Run New Diagnosis — Validation Report

Date: 2026-08-12

## Automated checks

| Check | Result |
|---|---|
| Focused ESLint on new page and test | PASS, 0 warnings |
| TypeScript `tsc --noEmit` | PASS |
| Production `vite build` | PASS |
| Focused Vitest | PASS, 2/2 |
| Full frontend Vitest | PARTIAL, 45/46 |

The sole full-suite failure is the pre-existing `CommandCenterPage.test.tsx` fixture mismatch: its mocked `listIdeas` returns a raw array while the current component reads the API's `{ideas}` envelope. The failing code path is unrelated to this diagnosis-page change. The new page tests pass within the same suite.

The production build retains the repository's existing large-chunk warning (`~1.29 MB` main JS); this is a warning, not a build failure.

## Browser and live API validation

Target validated:

`http://127.0.0.1:5175/projects/PROJ-3f77f638302b/run_new_diagnose`

Live services used:

- frontend: Vite on `127.0.0.1:5175`
- backend: FastAPI on `127.0.0.1:8651`

### Initial state — PASS

The rendered page showed the real project context:

- host: `Escherichia coli · K-12`
- target product: `L-tryptophan`
- evidence items: `12`
- available model adapters: `2 / 4`
- only genotype/chassis preselected in the data-sufficiency gate
- Start Diagnosis disabled until a diagnostic question is supplied

Visual artifact: `run_new_diagnose_initial.png`.

### Partial/data-required state — PASS

A real validation run was created with conservative data declarations:

- workflow run: `WFR-0ab546ca97c3`
- diagnosis session: `DIAG-e6dbb783bb73`
- workflow status: `waiting`
- workflow phase: `DIAGNOSIS`
- diagnosis status: `data_required`
- data sufficiency: `insufficient`
- persisted diagnosis evidence links: `0`

Refreshing the page with `?run=WFR-0ab546ca97c3` restored the durable workflow and displayed the Partial badge. The Engineering Design action remained unavailable because no diagnosis decision existed.

Visual artifact: `run_new_diagnose_partial.png`.

### Completed record and handoff readiness — API PASS / visual automation limited

Existing completed workflow `WFR-08e1ff797098` was read through the same live APIs:

- diagnosis session: `DIAG-ae993574f6a3`
- hypotheses: `4`
- evidence links: `3`
- diagnosis decisions: `1`
- allowed next action: `handoff_to_design`
- persisted handoff status: `handed_off`

This confirms the completed-page data dependencies and handoff eligibility contract. Headless Chrome intermittently stayed on the app loading skeleton for this longer multi-request recovery path, so a completed-state visual screenshot is not claimed as passed. Initial and partial visual states were successfully captured.

## Browser console limitation

The available headless Chrome workflow captured rendered output but did not provide a reliable DevTools console collector. API responses, page rendering, automated tests, typecheck, and build were validated; “zero browser console errors” is therefore not asserted.

## Final status

**PASS with documented validation limitation**: implementation, focused checks, build, live initial state, durable partial state, and completed data contract all pass. The only non-task test failure and the completed-state screenshot limitation are explicitly recorded above.
