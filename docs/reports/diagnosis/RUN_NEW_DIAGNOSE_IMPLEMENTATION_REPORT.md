# Run New Diagnosis — Implementation Report

Date: 2026-08-12

## Outcome

Implemented a dedicated scientific diagnosis run page at:

`/projects/:projectId/run_new_diagnose`

The Diagnosis Workspace entry now navigates to this page instead of immediately launching a run with a hard-coded fully-sufficient data declaration.

## Delivered behavior

- Scientific objective selection and required diagnostic-question input.
- Read-only project host/strain and target-product context.
- Optional carbon source, known mutations, constraints, and observation context.
- Explicit six-part data-sufficiency attestation wired to the backend gate.
- Requested diagnostic scope with honest `OUTPUT FOUND`, `NOT EVALUATED`, and `OUT OF SCOPE` reporting.
- Live project evidence inventory and runtime model-capability counts.
- Initial, running, partial, failed/retry, and completed UI states.
- Durable workflow-run recovery via `?run=<workflowRunId>`.
- Persisted hypothesis cards with evidence provenance, quality/directness tooltips, contradictions, and falsification paths.
- Decision summary that explains “actionable” does not prove a unique true cause.
- A governed Engineering Design handoff that calls `createHandoff` only when a persisted decision exists, then navigates using the returned design-project id.

## Truth-preserving design decisions

- Individual M0–M5 stages are not animated as completed while the synchronous diagnosis request is pending.
- Requested scope is not equated with backend execution.
- Host/chassis is the only data category inferred from a recorded host definition. All measurement-related categories require explicit user attestation.
- Evidence and model capability are displayed separately; available adapters are not described as executed models.
- No new scientific output schema, evidence ontology, model result, or chain-of-thought surface was introduced.

## Changed files

- `frontend/src/router.tsx`
- `frontend/src/pages/diagnosis/DiagnosisWorkbenchPage.tsx`
- `frontend/src/pages/diagnosis/RunNewDiagnosisPage.tsx`
- `frontend/src/pages/diagnosis/RunNewDiagnosisPage.test.tsx`
- `RUN_NEW_DIAGNOSE_AUDIT.md`
- `RUN_NEW_DIAGNOSE_IMPLEMENTATION_REPORT.md`
- `RUN_NEW_DIAGNOSE_VALIDATION_REPORT.md`

## Generated QA artifacts

- `run_new_diagnose_initial.png`
- `run_new_diagnose_partial.png`

