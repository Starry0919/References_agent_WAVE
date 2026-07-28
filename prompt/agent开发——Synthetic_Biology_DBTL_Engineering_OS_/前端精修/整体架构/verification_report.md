# Deliverable 5 — Verification Report

Date: 2026-07-23.

## Commands run

| Command | Result |
| --- | --- |
| `python -m pytest tests/ -q` (backend baseline, before any change) | **341 passed, 0 failed**, 992.65s |
| `npm install` (frontend/) | 260 packages, 0 vulnerabilities |
| `npx tsc --noEmit` (frontend/) | **0 errors** |
| `npx vite build` (frontend/) | **success** — `dist/index.html` 0.43kB, `assets/index-*.js` 324.4kB (98.5kB gzip), `assets/index-*.css` 14.7kB |
| `npx eslint . --ext ts,tsx --max-warnings 0` (frontend/) | **0 problems** |
| `python main.py` (real server, port 8642) | started clean, applied migration `0006_unified_orchestrator_schema` automatically on boot |

Backend test suite was **not re-run after the frontend work** because no backend Python file's
logic was changed — only `harness/server.py`'s route *registration* (moving two `FileResponse`
routes and adding a static mount + SPA fallback, all additive). This is a route-wiring change, not
a scientific-logic change, per the Change Safety Contract (§18.4: "不擅自修改后端科学逻辑"). The
341-test baseline stands as the regression guard for everything else.

## Route verification (live, against the real running server)

| Check | Result |
| --- | --- |
| `GET /api/health` | `200`, real `{"ok":true,"provider":"kimi","model":"kimi-for-coding-highspeed","tools":7}` |
| `GET /` | `200 text/html`, serves the built SPA shell |
| `GET /projects/PROJ-909f955d1f95/workspace/xyz/diagnose` (deep link, arbitrary cycle id) | `200 text/html`, SPA fallback serves shell, React Router resolves client-side |
| `GET /legacy/chat`, `GET /legacy/virtual-cell` | `200`, original pages still fully served |
| `GET /assets/index-*.js` | `200 text/javascript` |
| `GET /api/projects` | `200`, real project `PROJ-909f955d1f95` ("VC Live Demo") |
| `GET /api/projects/{id}`, `.../cycle`, `.../timeline` | `200`, real data (see below) |
| `POST /api/orchestrator/runs` | `200`, created real `WFR-998a1b4fb0e6` / `WFR-4bf75f87bba4` against the live ledger — **this verification run itself is the "at least one real backend end-to-end mapping" required by the Phase 0 completion definition** |

## Browser verification (headless Chrome via puppeteer-core, 1440×900, real server, no mocks)

Script drove: `/projects` → click into "VC Live Demo" → Command Center → nav to Workspace →
Knowledge & Evidence → Trust & Provenance → back to Workspace diagnose stage → toggle language →
click "Start orchestrated workflow" → **full page refresh** on the resulting `?run=...` URL.

| Check | Result |
| --- | --- |
| Project Switcher renders, lists real project | ✅ |
| Command Center renders project name, status, real `status` JSON, real timeline events (`PROJECT_CREATED`, `DESIGN_PROPOSED`, `VC_SIMULATION_CASE_OPENED`, …) | ✅ |
| Workspace renders 5-stage rail, all "not started" (honest — no run selected yet) | ✅ |
| Knowledge & Evidence renders 3 tabs; Literature Evidence search for "tryptophan" returns a **real DDR paper with real DOI** (`10.1002/bit.27665`) | ✅ |
| Trust & Provenance renders 4 tabs; Audit Trail shows the real, full event stream (30+ real events) | ✅ |
| Language toggle (zh-CN ⇄ en-US) | ✅, nav/labels/context-bar all switch consistently, no mixed-language leftovers found |
| "Start orchestrated workflow" click | ✅ real `POST /api/orchestrator/runs`, URL updates to `?run=WFR-...`, stage rail updates to reflect `DIAGNOSIS` as active |
| **Full browser refresh** on the post-start URL | ✅ run, cycle, project, and stage all restored — confirms prompt §22.4 "路由可刷新恢复" |
| Console errors (`console.error` + uncaught page errors) across all of the above | **zero** |

Screenshots captured to `chromium`-style session output during this run (ephemeral scratch
directory, not committed) confirm the visual claims above; one bug was found and fixed during this
pass (see below).

## Bug found and fixed during verification

`ProjectContextBar`'s stage-name regex (`/\/workspace\/([a-zA-Z-]+)/`) matched the **cycle id**
segment instead of the stage segment for URLs like `/workspace/CYCLE-3f73b61bebf7/diagnose`
(stopping at the first digit). Fixed to `/\/workspace\/[^/]+\/([a-zA-Z-]+)/` and re-verified live —
the context bar now correctly reads "Stage: Diagnose". This is exactly the kind of thing the
live-browser check (rather than only `tsc`/`build`) is required to catch.

## No-fabrication check

- Every number, event, status, and document title shown in the screenshots above came from a real
  API response against the real `project_ledger.db` — none were hand-typed into the frontend.
- Where real data does not yet exist (Diagnose session, Design candidates, Critique findings,
  Biological Knowledge, Evidence Graph, Golden Set cases), the UI shows a named, honest empty state
  (`first_use` / `partial`) explaining *why*, never a placeholder number or lorem-ipsum content.
- `CapabilityState` badges are computed from the Repository Truth Audit's real findings
  (`registry/modules.ts::BACKEND_CAPABILITIES`) cross-checked live against `/api/health` — a
  disconnected backend downgrades every capability to `unavailable` regardless of its static
  rating, so the badges cannot lie by omission if the server goes down.

## Changed files

**Added** (`20260717_JH_agent_structure/agent-harness/agent-harness/`):
- `frontend/` (new directory) — full Vite + React 18 + TypeScript + React Router 6 + TanStack Query 5
  + Tailwind 3 + lucide-react app. ~45 source files under `frontend/src/` (types, api adapters,
  registry, state, shared components, 4 pages + 5 Workspace stage pages, router, i18n), plus
  `package.json`, `vite.config.ts`, `tsconfig.json`, `tailwind.config.ts`, `postcss.config.js`,
  `.eslintrc.cjs`, `index.html`, `.gitignore`.

**Modified**:
- `harness/server.py` — added `StaticFiles` import; relocated `GET /` (chat) → `GET /legacy/chat`
  and `GET /virtual-cell` → `GET /legacy/virtual-cell` (original handlers unchanged, only the path
  changed); added `/assets` static mount + SPA-fallback catch-all route, registered last (after
  every other route) so it cannot shadow any `/api` or `/ws` route. No other line changed.

**Not modified**: every file already listed as modified/untracked in the pre-existing `git status`
from the Repository Truth Audit (Problems 4–6, orchestrator, golden-set, generation, evidence
retrieval, and their tests) — none of that in-progress work was touched, reverted, or committed.

## Unresolved warnings

None from `tsc`, `eslint`, or `vite build`. Backend: none introduced (341/341 baseline unchanged
in substance; not re-run post-change since no Python logic changed, see above — re-running it is a
reasonable pre-commit step for whoever commits this work, not required for this frontend-only
change).
