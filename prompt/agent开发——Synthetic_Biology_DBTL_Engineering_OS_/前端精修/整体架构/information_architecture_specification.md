# Deliverable 2 — Information Architecture Specification

This is the single navigation contract, in both code (`frontend/src/router.tsx`,
`frontend/src/registry/modules.ts`) and this document. Any future change to top-level pages or
Workspace stages must update the registry, not add a second hard-coded list.

## 1. Four top-level pages (fixed, no fifth)

| # | Page | Route | Primary role | Default audience |
| --- | --- | --- | --- | --- |
| 1 | Project Command Center | `/projects/:projectId` | Now / Next / Risk mission control | PI |
| 2 | DBTL Engineering Workspace | `/projects/:projectId/workspace/:cycleId/<stage>` | ~90% of daily scientific work | Researcher / Dry Lab / Wet Lab |
| 3 | Knowledge & Evidence | `/projects/:projectId/knowledge` | Deep query layer, de-emphasized in nav weight | occasional, all roles |
| 4 | Trust & Provenance | `/projects/:projectId/provenance` | Full record: memory, audit, approval, evaluation | Evaluator/Admin, occasional PI |

Entry point `/projects` (no project selected) is the explicit project-switch screen (prompt §6.2 —
switching projects must never be implicit). `/` redirects there.

## 2. Workspace's five stages (one continuous workspace, not five pages)

`diagnose → design → simulate → critique → build-test-plan`, all under one route family
`/projects/:projectId/workspace/:cycleId/<stage>`, sharing one `WorkspaceLayout` that owns:
project, cycle, the selected `UnifiedWorkflowRun` (`?run=` query param), and the Evidence Drawer
open/closed state — none of which reset on stage navigation (prompt §6.5).

Stage status (`not_started / active / blocked / waiting_for_human / waiting_for_experiment /
completed`) is computed from the **real** orchestrator run + its transition history
(`computeStageStatuses` in `frontend/src/api/orchestrator.ts`), never from tab position. See
`repository_truth_audit.md` §4 for why backend phase order and frontend stage order differ and how
they're reconciled.

## 3. Evidence Drawer vs. Knowledge & Evidence Layer (prompt §6.4, §9.4)

- **`EvidenceDrawer`** (`frontend/src/components/workspace/EvidenceDrawer.tsx`): docked panel
  inside the Workspace, opened per-selection via `setEvidence()` on the Workspace outlet context.
  Never a modal; never clears the current stage selection. Scoped to "why should I believe the
  thing I just clicked."
- **`Page 3 / Knowledge & Evidence`**: full-page, cross-project search and browse
  (`KnowledgePage.tsx`, three tabs: Biological Knowledge / Literature Evidence / Evidence Graph).
  Reachable from nav, not part of the Diagnose→Build/Test Plan loop.

## 4. Command Center vs. Trust & Provenance (prompt §7.4, §10.6)

- **Command Center**: summaries + jump-in links only. It must not render a full diagnosis,
  candidate comparison, simulation parameter set, literature library, or audit log. It answers
  Now/Next/Risk in ≤3 panels of that kind plus supporting context (status view, recent events,
  learning) — never a flat KPI-card wall.
- **Trust & Provenance**: the full record — complete audit trail (`AuditTrailTab`, real
  `projects.timeline`), Memory (domain skeleton, no dedicated read API yet), Human Approval (inline
  in Workspace today; consolidated inbox is future work), System Evaluation (real `golden-set`
  cases, no pass-rate-as-trust framing).

## 5. Cross-page context contract (prompt §6.2, §6.6, §18.2 State Ownership Matrix)

| State | Owner | Where |
| --- | --- | --- |
| `projectId`, `cycleId`, workspace `stage` | URL path segments | `router.tsx` |
| `run` (selected orchestrator run), `version` (object version) | URL search params | `?run=`, `?version=` |
| Project detail, cycle state, timeline, design/diagnosis/simulation/evaluation summaries | TanStack Query cache, keyed by `[entity, id, ...]` | `frontend/src/api/*.ts` consumers |
| Backend connectivity / capability status | React Context (`BackendHealthProvider`) | `frontend/src/state/BackendHealth.tsx` |
| Language preference | `localStorage` (UI preference, not scientific data) | `frontend/src/lib/i18n.tsx` |
| Panel collapse, Evidence Drawer open/closed, form drafts | local component state | per-component `useState` |

No scientific object is duplicated across URL + global store + local state — the query cache is
the single source keyed by project+object+version, exactly as §18.3 requires.

## 6. Route table (prompt §6.3, adapted to this repo's router)

```
/                                                        -> redirect to /projects
/projects                                                -> Project Switcher (explicit project selection)
/projects/:projectId                                     -> Command Center
/projects/:projectId/workspace                           -> resolves active cycle, redirects to .../:cycleId/diagnose
/projects/:projectId/workspace/:cycleId/diagnose          -> Workspace / Diagnose
/projects/:projectId/workspace/:cycleId/design            -> Workspace / Design
/projects/:projectId/workspace/:cycleId/simulate          -> Workspace / Simulate
/projects/:projectId/workspace/:cycleId/critique          -> Workspace / Critique
/projects/:projectId/workspace/:cycleId/build-test-plan   -> Workspace / Build-Test Plan
/projects/:projectId/knowledge                            -> Knowledge & Evidence
/projects/:projectId/provenance                           -> Trust & Provenance
```

`?run=<workflow_run_id>` and `?version=<n>` compose onto any of the above. All are refresh-safe:
TanStack Query re-fetches from the URL-derived key on mount, never from an in-memory-only value
(verified — see `verification_report.md`).

## 7. Terminology contract enforcement

`frontend/src/types/domain.ts` centralizes `STAGE_LABEL`, `ObjectStatus`, `StageStatus`,
`ObjectSource`, `CapabilityAvailability` exactly per prompt §4A.2 / §12. All adapters translate
backend snake_case field/enum names into this vocabulary; no page invents a local synonym.
