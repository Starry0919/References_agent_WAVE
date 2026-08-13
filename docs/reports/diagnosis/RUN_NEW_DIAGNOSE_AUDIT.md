# Run New Diagnosis — Repository Truth Audit

Date: 2026-08-12

## Scope and result

The requested browser target, `/projects/:project_id/run_new_diagnose`, did not exist before this change. The router exposed only the diagnosis overview and diagnosis-session detail routes. The existing “Run new diagnosis” button bypassed configuration and called a helper with a hard-coded *fully sufficient* data declaration.

This implementation therefore adds a dedicated route and page while preserving the existing scientific services. It does not introduce a second diagnosis engine.

## Reusable real contracts

- `frontend/src/api/orchestrator.ts`
  - `createRun` creates a durable project-scoped workflow run.
  - `startDiagnosis` calls the real diagnosis adapter and returns its durable checkpoint.
- `harness/orchestrator/adapters.py::DiagnosisAdapter`
  - Runs the existing data sufficiency gate.
  - When sufficient, builds the mechanism graph, generates competing hypotheses, assesses evidence, ranks hypotheses, runs the stopping gate, and creates a diagnosis decision when actionable.
  - When insufficient, persists the same diagnosis session in `data_required`; it does not fabricate a result.
- `frontend/src/api/diagnosis.ts`
  - Reads sessions, hypotheses, evidence links/items, diagnostic tests, decisions, and model capability detection from real endpoints.
- `frontend/src/api/engineeringDesign.ts::createHandoff`
  - Creates the governed diagnosis-to-design handoff from a real `DiagnosisDecision`.

## Scientific and UI truth constraints

1. The orchestrator diagnosis endpoint is synchronous. It does not stream M0–M5 events. The UI may show that the request is running, but must not pretend that individual scientific modules completed while the request is still in flight.
2. Module coverage is derived from persisted hypothesis/evidence/test/decision outputs. A requested scope without a matching output is labelled **NOT EVALUATED**, not “normal” and not “completed”.
3. The six data-availability flags are user attestations. Defaults are conservative: only genotype/chassis is preselected when the project actually records a host definition. No hidden “all sufficient” default is used.
4. Evidence counts, source types, quality, and directness come from persisted `EvidenceItem`/`EvidenceLink` rows. Model availability comes from runtime capability detection. No paper count, model result, database fact, or experimental confirmation is invented.
5. `context` fields (objective type, carbon source, known mutations, observations, and requested scopes) are recorded as run context. They do not imply backend support for a scientific module.
6. The UI presents structured status, outputs, uncertainty, falsifiers, and evidence provenance. It does not expose or simulate hidden chain-of-thought.

## State model

- **initial**: configuration is editable; no run selected.
- **running**: workflow creation/start request is in flight; configuration remains visible and locked.
- **partial**: the durable diagnosis session is `data_required`, `evidence_limited`, or otherwise lacks an actionable decision.
- **failed**: API failure is shown with retry while preserving configuration.
- **completed**: an actionable persisted decision exists and findings/evidence are renderable.

## Handoff semantics

“Proceed to Engineering Design” is enabled only when a persisted diagnosis decision exists. It calls the real Engineering Design handoff endpoint and navigates with the returned design-project id. The selected leading hypotheses and evidence context are transferred by the immutable diagnosis-decision contract; the frontend does not construct an ungoverned substitute payload.

## Files intended for change

- `frontend/src/router.tsx`
- `frontend/src/pages/diagnosis/RunNewDiagnosisPage.tsx` (new)
- `frontend/src/pages/diagnosis/DiagnosisWorkbenchPage.tsx`
- focused frontend tests
- implementation and validation reports
