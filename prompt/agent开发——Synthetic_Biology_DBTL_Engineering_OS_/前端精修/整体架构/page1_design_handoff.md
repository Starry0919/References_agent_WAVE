# Deliverable 6 — Page 1 (Project Command Center) Detailed-Design Handoff

## What's already real and available to design against

- `GET /api/projects/{id}` — identity, target product, host definition, objectives, constraints,
  lifecycle stage, current design version id, owners.
- `GET /api/projects/{id}/cycle` — cycle ledger state (`current_state` from the 14-value
  `DBTL_STATES`), `pending_gate`, active design/experiment refs, termination reason.
- `GET /api/projects/{id}/timeline` — full real event stream, typed `event_type` values (seen live:
  `PROJECT_CREATED`, `CYCLE_STATE_CHANGED`, `DESIGN_PROPOSED`, `DESIGN_APPROVED`,
  `VC_SIMULATION_CASE_OPENED`, `OBSERVATION_DERIVED`, `VC_CELL_STATE_RECORDED`, …).
- `GET /api/projects/{id}/status` — real, but its shape is currently rendered as raw JSON (see
  below — this is the single biggest open design question for Page 1).
- `POST /api/orchestrator/runs`, `GET /api/orchestrator/runs/{id}` — real pending-work/next-step
  driver once a run exists for the project.

## Missing API (do not design around fabricating these client-side)

1. **List orchestrator runs by project** (`GET /api/orchestrator/runs?project_id=`) — needed so
   Command Center can show "current DBTL cycle / current workflow state" from the *real* current
   run instead of requiring the user to have a `?run=` link already. This is the single highest
   priority backend addition for Page 1.
2. **A formalized "pending decisions" query** — today Command Center can only point at Trust &
   Provenance in general; there is no endpoint that answers "what, specifically, is waiting on a
   human right now for this project" across Diagnose/Design/Critique/Build-Test-Plan.
3. **A formalized "bottleneck summary"** object — `diag_bottleneck_value_assessments` exists as a
   real table server-side, but has no read endpoint yet.

## Decisions needed from the user / product owner before Page 1 visual design

1. **`build_project_status_view()` shape**: should its fields (seen live: `active_design_version`,
   `active_construct`, `active_learning_cycle`, `latest_accepted_results`, `waiting_for`,
   `qc_state`, …) become individually designed Command Center widgets, or should the backend add a
   purpose-built `/command-center-summary` endpoint that already returns Now/Next/Risk-shaped
   data? Recommendation: the latter — it keeps the "no full diagnosis/design/simulation on this
   page" boundary (prompt §7.4) enforced server-side, not by frontend discipline alone.
2. **Where does "leading engineering direction"** (prompt §7.3) come from once real Design
   candidates exist? No `is_leading` / `recommended` flag currently exists on `CandidateDesign` —
   needs either a backend field or an explicit non-fabricated frontend rule (e.g., "the
   `reference_or_control` portfolio role," if that's scientifically appropriate — a product
   decision, not a frontend one).
3. **Multi-cycle history**: `GET /api/projects/{id}/cycle` returns only the *active* cycle. Page 1's
   "previous-cycle learning" panel needs either a cycle-history endpoint or confirmation that
   `IterativeCycleState` rows are retained (not overwritten) across cycles.

## Content domains that should NOT be duplicated on Page 1

- Full hypothesis/evidence detail → stays in Workspace/Diagnose + Evidence Drawer.
- Full candidate comparison → stays in Workspace/Design.
- Full audit trail → stays in Trust & Provenance (Page 1 shows only the 8 most recent events).
- Full literature/DDR browse → stays in Knowledge & Evidence.

## Recommended priority for Page 1 detailed design

1. Formalize the Command Center summary endpoint (unblocks the raw-JSON status panel).
2. Wire the orchestrator list-by-project endpoint so Command Center's "current DBTL cycle" reflects
   the real active `UnifiedWorkflowRun`, not just the older `IterativeCycleState`.
3. Design the Pending Decisions panel against whatever the consolidated-approvals endpoint (also
   needed by Trust & Provenance, see `backend_mapping_matrix.md`) ends up returning — build it once,
   reuse in both places.
4. Only after 1–3: visual/interaction polish (card layout, typography scale, risk-panel severity
   ordering) — this is explicitly P3-adjacent work that must not precede the above per the Priority
   Matrix (prompt §二十).

## Open questions

- Is "VC Live Demo" (`PROJ-909f955d1f95`) intended to become the running example (à la the
  prompt's suggested L-tryptophan case), or should a fresh project be seeded for Page 1 design
  review so its DBTL history is representative rather than ad hoc test data?
- Should Golden Set cases be seeded (`POST /api/golden-set/seed`) before Page 1 design starts, so
  the Trust & Provenance "System Evaluation" tab has real content to design against instead of an
  empty state?
