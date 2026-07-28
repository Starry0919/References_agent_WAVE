# Deliverable 1 — Frontend Architecture Audit

Date: 2026-07-23. Scope: `20260717_JH_agent_structure/agent-harness/agent-harness/` — the real,
running backend repo behind Problems 1–6 (confirmed against `workflow/design/evolution/后端精修/repository_truth_audit.md`,
independently re-verified this session, not just trusted). Everything under `workflow/design/` in
the parent folder is design prompts, not runnable product code.

## 1. Current stack (before this work)

- **Backend**: FastAPI (`harness/server.py`), SQLAlchemy + SQLite (`project_ledger.db`), Pydantic,
  cobrapy for FBA. Real, git-tracked (4 commits) plus substantial **uncommitted** working-tree
  changes: `harness/api/{engineering_design,generation,golden_set,orchestrator,scientific_evaluation,virtual_cell}.py`,
  `harness/{engineering_design,evidence_retrieval,golden_set,llm_generation,orchestrator,scientific_evaluation,virtual_cell}/`
  packages, and matching `tests/*`. **This is real, in-progress user/agent work — not touched,
  discarded, or committed by this audit or by the frontend build.**
- **Frontend**: **none**, in the SPA sense. `web/index.html` (1215 lines) is a single hand-written
  HTML/CSS/vanilla-JS file implementing exactly the anti-pattern the design prompt forbids as the
  product's primary surface (§3.1): a left session list + center chat bubbles + bottom input box,
  talking to `/api/sessions/*`. `web/virtual_cell.html` (403 lines) is a second, similarly
  framework-free static page for Problem 06. **No `package.json`, no bundler, no component
  framework, no router, no CORS middleware existed anywhere in this repo before this session.**
- A **separate, older prototype** frontend exists at
  `workflow/design/JH/agent-harness-v1/agent-harness-v1/frontend/` (React 19 + Vite + TS + Tailwind
  4 + react-three-fiber + framer-motion). It lives in its **own separate git repo**
  (`agent-harness v1 — standalone finalized release`), talks to a **different, older backend**
  (`synbio/evaluator.py`, not `harness/scientific_evaluation/`), and its page set
  (`AgentWorkflowPage`, `EngineeringDesignPage`, `EvaluatorPage`, `SimulationPage`, …) is exactly
  the fragmented 5-page IA the current design prompt explicitly forbids restoring (§二). It is
  **not part of the live product** and was not reused as code — only its dependency choices
  (React + Vite + TS + Tailwind + lucide-react) were taken as a reasonable precedent, since no
  live-repo stack existed to "reuse" per §18.

## 2. Backend API surface (real, independently verified by reading route source)

11 FastAPI routers, ~100 endpoints, all mounted in `harness/server.py::create_app()`:

| Router | Prefix | Git state | Test coverage (341-test baseline, this session) |
| --- | --- | --- | --- |
| `projects` | `/api/projects` | committed | covered |
| `designs` | `/api` (`/designs`, `/constructs`) | committed | covered |
| `experiments` | `/api/experiments` | committed | covered |
| `learning` | `/api/learning` | committed | covered |
| `diagnosis` | `/api/diagnosis` | committed | covered (67 tests) |
| `engineering_design` | `/api/engineering-design` | **uncommitted** | covered (43 tests, uncommitted `tests/engineering_design/`) |
| `scientific_evaluation` | `/api/scientific-evaluation` | **uncommitted** | covered (31 tests) |
| `virtual_cell` | `/api/virtual-cell` | **uncommitted** | covered (47 tests) |
| `orchestrator` | `/api/orchestrator` | **uncommitted** | not in the 341-test baseline's per-module split; exercised live this session (see Verification Report) |
| `generation` | `/api/generation` | **uncommitted** | not separately isolated in baseline; exercised live this session |
| `golden_set` | `/api/golden-set` | **uncommitted** | not separately isolated in baseline |

Full field-level shapes for every route are recorded in `backend_mapping_matrix.md`.

## 3. Reusable components / conflicting legacy pages

- **Reusable**: none at the component level (no prior SPA). Reusable at the *data* level: every
  router above, the real `project_ledger.db` (one real project, "VC Live Demo" /
  `PROJ-909f955d1f95`, one active cycle, two virtual-cell simulation cases), and the local
  knowledge base (`knowledge/ddr_database/*.json`, `knowledge/biological_rules/`,
  `knowledge/engineering_actions/`).
- **Conflicting legacy pages**: `web/index.html` (chat-first UI) and `web/virtual_cell.html`
  (Problem 06 standalone page) both directly contradict the new IA (§3.1, §19 items 2/4). They are
  **real, working functionality**, so per the Change Safety Contract (§18.4, "不为了完成而移除现有
  功能") they were **not deleted** — they are relocated to `/legacy/chat` and `/legacy/virtual-cell`
  (see §5 below) and remain fully reachable.

## 4. Known backend duplication surfaced by this audit (relevant to the frontend's state model)

Two independent state machines exist for "where is this project in its DBTL loop":

1. **`IterativeCycleState`** (`harness/workflow/iterative_loop.py`, Problem 2, committed) — 14
   `DBTL_STATES`, one row per project, exposed at `GET /api/projects/{id}/cycle`.
2. **`UnifiedWorkflowRun`** (`harness/orchestrator/models.py`, uncommitted) — 14
   `ORCHESTRATOR_PHASES` (`INTAKE…LEARNING…COMPLETED`), meant to be the top-level sequencer across
   Problems 3–6, exposed at `/api/orchestrator/runs/*`.

These are **not the same state machine** and are not kept in sync automatically. The frontend
treats `IterativeCycleState` as the Command Center's cycle-ledger summary and
`UnifiedWorkflowRun` as the Workspace stage rail's driver — documented explicitly rather than
silently merged (see `information_architecture_specification.md` §State model).

Additionally, the backend's real phase order is
`DIAGNOSIS → DESIGN → EVALUATION → SIMULATION → HUMAN_REVIEW → WAITING_FOR_EXPERIMENT → …`
(confirmed in `harness/orchestrator/service.py`, a deliberate backend design choice) while the
design prompt's fixed frontend stage order is `Diagnose → Design → Simulate → Critique →
Build/Test Plan`. The two are reconciled by a documented, honest per-phase mapping
(`frontend/src/api/orchestrator.ts::PHASE_TO_STAGE`), not by silently reordering or hiding either
side's reality.

## 5. Risks

1. **No `GET /api/orchestrator/runs?project_id=`** (list-by-project) endpoint exists — the
   frontend cannot discover a project's existing run(s) on its own; it can only look up a run by
   ID once one is known (deep link / just-created). Flagged in the mapping matrix as `partial`,
   with an honest empty-state + "start a run" CTA rather than a fabricated run.
2. **Uncommitted backend work**: Problems 4–6 + orchestrator + golden-set + generation are real
   and passing their own tests but not yet on `master`. If that work is reverted or rebased before
   commit, the corresponding frontend adapters will start failing loudly (typed adapters + real
   fetches, not silently — no mock fallback is wired in).
3. **Thin real seed data**: only one real project exists in `project_ledger.db`, with no
   `diag_sessions`, `design_projects`, or `eval_cases` rows yet. Diagnose/Design/Critique stage
   panels are therefore honestly empty (`first_use` state) until a real orchestrator run is walked
   through those phases — this was not papered over with mock content.
4. **vEcoli / larger E. coli GEM**: per the backend audit, only the toy `e_coli_core` model is
   real; `vecoli`/`kinetic` adapters honestly report `unavailable`. The frontend's model registry
   view (`SimulateStage`) surfaces this as-is.

## 6. Recommended migration path (executed this session)

1. Add a real SPA (`frontend/`) inside the live backend repo — no existing SPA to migrate away
   from, so this is net-new, not a rewrite (§18: "不因个人偏好重写前端" does not apply — there was
   nothing to preserve at the framework level).
2. Serve it same-origin from FastAPI (`frontend/dist` mounted + SPA-fallback route), avoiding any
   CORS change to the backend, since none currently exists.
3. Relocate (not delete) `web/index.html` → `/legacy/chat`, `web/virtual_cell.html` →
   `/legacy/virtual-cell`.
4. Build typed adapters that call the real routers directly; capability state (`available` /
   `partial` / `absent` / `unclear` / `blocked`) is tracked centrally in
   `frontend/src/registry/modules.ts` and cross-checked live against `/api/health`.

## 7. Files touched / added (this session)

See `verification_report.md` §Changed files for the exhaustive list.
