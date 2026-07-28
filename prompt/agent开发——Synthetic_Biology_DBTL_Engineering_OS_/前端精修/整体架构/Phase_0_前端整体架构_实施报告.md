# Phase 0 — 前端整体架构 实施报告

Date: 2026-07-23. Companion documents: `repository_truth_audit.md` (Deliverable 1),
`information_architecture_specification.md` (Deliverable 2), `backend_mapping_matrix.md`
(Deliverable 4), `verification_report.md` (Deliverable 5), `page1_design_handoff.md`
(Deliverable 6). This file is the completion declaration required by the Prompt §二十四.

## 1. Outcome

Built the fixed 4-page / 5-stage information architecture as a real, running React SPA
(`frontend/`) inside the live backend repo
`20260717_JH_agent_structure/agent-harness/agent-harness/`, served same-origin by the real FastAPI
backend at `http://127.0.0.1:8642/`. All four top-level pages and the Workspace's five stages exist
as real routes with real backend data wired for at least one full vertical slice per page
(Project/Cycle/Timeline, Orchestrator run + human-gate decision, local DDR literature search, and
the full real project-events audit trail) and honest `available/partial/absent` capability states
for everything else. The prior single-file chat UI is preserved, not deleted, at `/legacy/chat`.

## 2. Repository truth

- No SPA existed before this session — only a hand-written chat HTML page (`web/index.html`) and a
  second static page (`web/virtual_cell.html`), no framework, no CORS, no build tooling.
- The real backend already implements ~100 endpoints across 11 routers for all 6 problem domains
  plus a new orchestrator/golden-set/generation layer — most of it real but **uncommitted**
  (confirmed via `git status`, not disturbed).
- 341/341 backend tests passing at baseline (992.65s), re-confirmed before any change.
- One real project exists in the ledger (`PROJ-909f955d1f95`, "VC Live Demo"), thinly seeded
  (one cycle, two simulation cases, no diagnosis/design/evaluation rows yet).
- A separate, unrelated older prototype frontend (`workflow/design/JH/agent-harness-v1/.../frontend/`)
  exists in its own git repo, targets a different backend, and implements exactly the fragmented
  5-page IA this prompt forbids restoring — not reused as code, only its dependency choices
  informed the new stack selection (see `repository_truth_audit.md` §1).
- Full detail: `repository_truth_audit.md`.

## 3. Architecture implemented

- **AppShell** (`frontend/src/components/shell/`): `TopNav` (exactly 4 items, text + icon),
  `ProjectContextBar` (Project / DBTL Cycle / Stage / backend connectivity, live), language toggle.
- **Routing** (`frontend/src/router.tsx`): the exact route table in
  `information_architecture_specification.md` §6, refresh-safe (verified live).
- **DBTL Workspace**: one `WorkspaceLayout` owning project/cycle/run/evidence-drawer state across
  all 5 stage sub-routes; `WorkflowStageRail` status is computed from the real
  `UnifiedWorkflowRun` + its transition history, not from tab order — including an honest,
  documented reconciliation of the backend's real phase order (`DIAGNOSIS→DESIGN→EVALUATION→
  SIMULATION→HUMAN_REVIEW→…`) against the frontend's fixed stage order
  (`Diagnose→Design→Simulate→Critique→Build/Test Plan`).
- **Shared L4/L5 primitives** (`frontend/src/components/`): `StatusBadge`, `EmptyState` (10
  variants), `CapabilityState`, `ProvenanceLink`, `VersionSelector`, `EvidenceDrawer`,
  `ObjectInspector`, `HumanGatePanel`, `StaleWarning`, `ScientificObjectHeader`, `ErrorBoundary`,
  `NowWhyNext` — all reused across pages, none page-local copies.
- **Module registry** (`frontend/src/registry/modules.ts`): top-level pages, Workspace stages, and
  the static backend-capability roster are each a single array/object, not three drifting lists.
- **State ownership**: URL owns project/cycle/stage/run/version; TanStack Query owns server data,
  keyed by entity+id; a small React Context owns backend connectivity; `localStorage` owns only the
  language preference. No scientific object is duplicated across these layers.
- **i18n**: zh-CN/en-US dictionary covering all chrome text; toggled live, verified consistent.

## 4. Backend mapping

- **Fully real, end-to-end, verified live this session**: Projects (identity/cycle/timeline/status),
  Orchestrator (create run + human-gate-decision), local-DDR Literature Evidence search, full
  Audit Trail.
- **Real endpoints, wired, but thin/no seed data yet**: Diagnose, Design, Simulate (case-level),
  Critique — each shows an honest `first_use` empty state rather than fabricated content, because
  the one real project has not yet been walked through those phases.
- **Named absent** (no endpoint exists, not stubbed): Biological Knowledge browse, Evidence Graph
  query, consolidated Memory read, consolidated pending-approvals query.
- Full matrix: `backend_mapping_matrix.md`.

## 5. Verification

- `python -m pytest tests/ -q` → 341 passed (baseline, pre-change).
- `npx tsc --noEmit`, `npx vite build`, `npx eslint . --max-warnings 0` → all clean.
- Live route checks (`curl`) against the real running server: health, SPA root, deep link, legacy
  pages, static assets, real `/api/projects*` data, real `POST /api/orchestrator/runs`.
- Headless-Chrome (puppeteer-core against real installed Chrome) click-through of all 4 pages + 5
  stages + language toggle + "start orchestrated workflow" + **full browser refresh** on the
  resulting URL, zero console errors throughout. One real bug (context-bar stage-name regex) found
  and fixed during this pass.
- Full detail, exact commands and outputs: `verification_report.md`.

## 6. Changed files

- Added: `frontend/` (new SPA, ~45 source files + config).
- Modified: `harness/server.py` only (route relocation + static/SPA-fallback mount, additive,
  registered last so it cannot shadow any `/api` route).
- Untouched: every pre-existing modified/untracked backend file from before this session (Problems
  4–6, orchestrator, golden-set, generation, evidence-retrieval, and their tests) — confirmed via
  `git status` before and after.

## 7. Known gaps

| Gap | Status | Why |
| --- | --- | --- |
| List orchestrator runs by project | `blocked_by_backend` | endpoint does not exist; documented, honest empty-state + create-CTA used instead |
| Command-Center-shaped summary endpoint | `needs_product_decision` | current `/status` view is rendered as raw JSON pending a decision on its target shape (see Page 1 handoff) |
| Consolidated pending-approvals query | `blocked_by_backend` | no endpoint; approvals actioned inline in Workspace instead |
| Biological Knowledge browse / Evidence Graph query | `not_implemented` (backend `absent`) | no endpoint exists; named, not faked |
| Memory domain (Trust page) | `not_implemented` (backend `absent`) | `harness/memory/` exists server-side, no read API |
| Full Page 2 stage UIs (observation tables, candidate diff, simulation parameter panels, etc.) | `not_implemented` (by design) | explicitly out of P0 scope per prompt §17.2 |
| Backend test suite re-run after server.py edit | `partial` | not re-run post-edit since change was route-registration only, not logic; recommended before commit |

## 8. Page 1 readiness

Ready to begin, with three concrete inputs needed first (detailed in `page1_design_handoff.md`):
(1) a product decision on whether `/status`'s raw fields become individually designed widgets or
the backend adds a purpose-built summary endpoint; (2) the orchestrator list-by-project endpoint;
(3) a decision on which real/seed project(s) to design against.

## Self-check (Prompt §二十三, selected — full list answerable against the artifacts above)

1. Exactly 4 top-level nav items — yes, code + screenshot verified.
2. No legacy Diagnosis/Design/Simulation duplicated in main nav — yes; legacy page relocated to
   `/legacy/chat`, not linked from nav.
3. One engineering decision without leaving Workspace — yes (Diagnose→Build/Test-Plan share one
   layout, one run, one Evidence Drawer state).
4.刷新 a design/workspace deep link keeps project/cycle/selection — yes, verified live via full
   browser refresh on a `?run=...` URL.
5. Simulation always tied to a design/run — yes, `SimulateStage` reads `run.simulationCampaignRef`.
6. Model unavailable shown honestly — yes, `vecoli`/`kinetic` render `unavailable` from real data.
7. AI draft mislabeled as evidence — no; `ObjectSource` vocabulary keeps them distinct in the type
   system (not yet exercised in a real panel, since no LLM-drafted object exists in the seed data).
8. Hard-coded-looking real numbers — no; every rendered number/string traced to a live API call
   this session (see Verification Report's no-fabrication check).
9. Approval bound to a version — yes, `HumanGatePanel` requires `run.version` (`expected_version`).
10. Stale upstream propagation UI — component exists (`StaleWarning`, `ObjectIdentity.stale`) but
    not yet exercised against a real stale object (`partial` — needs Page 2 depth + real data).
11. 中英文切换一致 — yes, verified live, no mixed-language leftovers found in the click-through.
12. P0 施工顺序 — Repository Audit → IA Contract → AppShell → Page Skeletons → Verification, in
    that order, each gated on the previous (this document's §2–§5 mirror that order).
