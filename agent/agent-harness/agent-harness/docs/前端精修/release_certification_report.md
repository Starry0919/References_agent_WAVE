# Final Integration, Validation & Release Certification Report

Executed against `Synthetic_Biology_DBTL_Engineering_OS_Final_Browser_Validation_and_Polish_Claude_Code_Prompt(4).md` v2.1
(path: `workflow/design/evolution——Synthetic_Biology_DBTL_Engineering_OS_/前端精修/`).
Date: 2026-07-24 (session; environment date advanced from 2026-07-23 mid-session). Executed against the real
product at `20260717_JH_agent_structure/agent-harness/agent-harness/` (frontend + FastAPI backend + SQLite
`project_ledger.db`), not the design-spec directory (`workflow/design/...`, which is prompts, not product code).

## A. Executive Summary

- Scope: real-browser (Chromium/Playwright + axe-core) audit of all 4 pages across the 6 required viewports,
  console/network capture, one keyboard-flow trace, one overlay-state check, classification of every finding
  against the Contract's 5-type Capability Gap taxonomy, minimal fixes for confirmed `frontend_bug` findings only,
  full regression, and this certification.
- Overall conclusion: **no P0/P1 defects, no scientific/governance violations, no fabricated backend capability**
  found or introduced. 5 real accessibility/design-token defects were found, fixed with a 6-file minimal change,
  and reverified clean (0 serious/critical/moderate axe violations across all 24 page×viewport combinations,
  down from violations present in all 24 at baseline).
- What is **not** certified this pass: verification at the Contract's prescribed large-data-density scale
  (100 projects / 100 candidates+1000 evidence / 1000 knowledge records / 10,000 audit events) and systematic
  failure-injection (timeout, mid-mutation refresh, network drop) were not executed — no seeding/fault-injection
  script was run this session. This is the reason the release decision below is `NEEDS_REVISION` rather than
  `READY`, even though everything that *was* tested is clean.
- Top findings (all fixed, see §E): (1) shared `ink-faint` text-color token failed WCAG AA contrast app-wide,
  (2) `StatusBadge` success/caution colors failed AA contrast, (3) Pages 1/3/4 had zero `<h1>`, (4) the
  project-context breadcrumb bar wasn't in an accessibility landmark, (5) one scrollable list wasn't
  keyboard-focusable. A pre-existing, real i18n coverage gap (infrastructure exists; most page content isn't
  wired to it) was found and — per explicit user decision — logged as `product_scope_gap`, not fixed this pass.
- Release decision: **NEEDS_REVISION** (system-level, for evidence-completeness reasons only — see §I). Every
  individual page qualifies for **READY WITH ACCEPTED LIMITATIONS** on its own merits (see §I).

## B. Environment

- Repository root: `20260717_JH_agent_structure/agent-harness/agent-harness/` (git repo, branch `master`,
  commit `95aac568e3f57841e01165749ffdde96dc5f5dcb`).
- Git state at session start (preserved, not authored by this session): 13 modified + ~25 untracked backend
  paths under `harness/`, `tests/`, plus the entire `frontend/` tree untracked (never committed). Verified
  byte-identical to session start except the 6 files listed in §E.
- Stack: React 18 + Vite 6 + TypeScript 5 + Tailwind 3 + TanStack Query 5 + react-router-dom 6 (frontend);
  FastAPI + SQLAlchemy + SQLite + cobrapy/COBRA FBA (backend, real GEM computation, not mocked).
- Backend started for real: `python main.py --port 8642`, health-checked (`/api/health` → `ok:true`), served
  139 real OpenAPI routes, serving the production `dist/` build same-origin (confirmed via `vite.config.ts`
  comment and live request).
- Browser: Chromium only (Playwright 1.61.1, matching a pre-cached `chromium-1228`/`chromium_headless_shell-1228`
  on this machine). This repo has **no existing** Playwright/cross-browser config to reuse (§3.1 allows adding
  one; none existed before this session), so per Contract §5.1 Firefox/WebKit are not required — only the
  Chromium-only limitation must be disclosed, which it is here.
- Viewports: all 6 required — 1920×1080, 1600×900, 1440×900, 1280×800, 768×1024, 390×844.
- Data: real seeded project `PROJ-909f955d1f95` ("VC Live Demo"), real DBTL cycle `CYCLE-3f73b61bebf7`, and one
  real orchestrator run `WFR-150018f04aee`. All three pre-date this session (created by the prior Page 4 session's
  own real runtime smoke test, per its `completion_report.md`) — this session did not create new demo data, only
  read/observed existing local dev-DB state. Disclosed as local dev state, not production data.
- Known limitations carried into this report: no Playwright/axe infra existed in-repo before this session (none
  was added to the repo either — the audit tooling lives out-of-repo in a scratch directory, see §G); no
  large-scale data fixtures were seeded; no fault-injection harness was built or run.

## C. Page Results

### Page 1 — Project Command Center (`/projects/:projectId`)

- States tested: default (populated), via real `PROJ-909f955d1f95` data.
- Visual: clean at all 6 viewports post-fix, no unexpected horizontal overflow, no clipped/overlapping regions.
- Responsive: mobile (390) and tablet (768) both usable — situation tiles reflow to single/narrow-multi column,
  nav/context bar readable, no forced desktop 3-column layout.
- Accessibility: 0 serious/critical/moderate axe violations post-fix (was: `color-contrast` serious, 28→9 nodes
  across viewports; `page-has-heading-one` moderate; `region` moderate). Keyboard flow traced end-to-end (see §G) —
  Tab order matches visual order, focus always visible (2px solid outline), no trap, reaches both
  "Continue in Workspace" and "Open Trust & Provenance..." links, satisfying the required
  "locate risk → view evidence → go to workspace" flow.
- Console/network: 0 errors/warnings, 0 failed requests, all 6 viewports.
- Data honesty confirmed live in-browser: "Current bottleneck" and "Scientific evidence / knowledge status" tiles
  correctly render `Not available via current API` / `Not aggregated at project level` with a named reason — real
  backend gaps, not hidden.
- Page-level status: **READY WITH ACCEPTED LIMITATIONS** (limitation = validation coverage: not tested at
  100-project density or under injected failures this pass; no backend-capability limitation blocks this page).

### Page 2 — DBTL Engineering Workspace (`/projects/:id/workspace/:cycleId/diagnose`, tested with a real run)

- States tested: default with a real orchestrator run loaded (`WFR-150018f04aee`), Evidence Drawer open (overlay
  state).
- Visual/responsive: clean at all 6 viewports.
- Accessibility: 0 violations post-fix (pre-fix: `color-contrast` serious 19→15 nodes, `region` moderate). Page 2
  already had a correct `<h1>` per stage before this session (only page that did) — unaffected by the h1 fix.
- Overlay: Evidence Drawer opened, axe-scanned clean, 0 console errors. It does not close on Escape — confirmed
  intentional by its own code comment (a docked, non-modal panel that must never force-clear workspace selection,
  per the page's own design contract), not a defect. No true `role="dialog"` modal exists anywhere in the app, so
  there was no focus-trap pattern to test.
- Console/network: 0 errors/warnings, 0 failed requests.
- Page-level status: **READY WITH ACCEPTED LIMITATIONS** (backend limitations pre-documented and reconfirmed live:
  no `SimulationRun` list endpoint, no build/test-package content resolver — both rendered as explicit
  "Unavailable via current API", not fabricated).

### Page 3 — Scientific Knowledge Production System (`/projects/:id/knowledge`)

- States tested: default (Knowledge Claims tab, real data).
- Visual/responsive: clean at all 6 viewports.
- Accessibility: 0 violations post-fix (pre-fix: `color-contrast` serious up to 11 nodes, `page-has-heading-one`,
  `region`, and `scrollable-region-focusable` on mobile — the claims list was a scrollable panel with no keyboard
  focus target). All four fixed and reverified.
- Console/network: 0 errors/warnings, 0 failed requests.
- Knowledge Layer Integrity: reconfirmed against the live OpenAPI surface (139 routes) that no Knowledge Graph /
  relationship endpoint, no Biological Knowledge browse API, and no Knowledge→Engineering reuse endpoint exist —
  matches the prior session's `page3_backend_mapping_matrix.md` exactly; no such capability is faked in the UI.
- Page-level status: **READY WITH ACCEPTED LIMITATIONS**.

### Page 4 — Trust & Provenance Center (`/projects/:id/provenance`, tested with the real run loaded)

- States tested: default (Attention tab), with a real orchestrator run loaded.
- Visual/responsive: clean at all 6 viewports.
- Accessibility: 0 violations post-fix (pre-fix: `color-contrast` serious up to 8 nodes, `page-has-heading-one`,
  `region`). Tabs use `role="tablist"`/`role="tab"`/`aria-selected` correctly; note (not a violation, recorded for
  completeness) they don't implement full arrow-key roving-tabindex per WAI-ARIA APG — all tabs remain reachable
  via sequential Tab, so this is not a keyboard-trap or WCAG failure, just a P3 polish item, not fixed this pass.
- Console/network: 0 errors/warnings, 0 failed requests.
- Governance boundary reconfirmed live: no RBAC/reviewer-authority, no Memory read API, no consolidated
  approvals/override/revoke, no export endpoint anywhere in the live OpenAPI surface — matches the prior
  session's own `completion_report.md`; all rendered as explicit unavailable states, not fabricated.
- Page-level status: **READY WITH ACCEPTED LIMITATIONS**.

## D. Cross-cutting Finding: i18n Coverage (product_scope_gap, not fixed this pass)

Live evidence (default load, no interaction): the top nav renders in Chinese (`项目总控`, `工程工作台`, ...) while
essentially all page-body content renders in English — visible simultaneously on first load because the stored
default locale is `zh-CN`. Root cause identified in code (`frontend/src/lib/i18n.tsx`): a real, working i18n
system already exists — `I18nProvider`/`useI18n`, a ~35-key dictionary, `localStorage`-persisted, refresh-safe —
but by its own documented design only routes "chrome/nav/state words" through `t()`. A full grep of `frontend/src`
found **zero** CJK characters anywhere outside this dictionary, confirming no page body, card, button, or dialog
text is wired to it. This is a real, correctly-scoped-by-design-doc capability, just far short of full-app
coverage. Per Contract §11.4 ("若产品语言策略未定义，记录为 product_scope_gap") and the user's explicit decision
this session, this is logged as `product_scope_gap` and **not implemented** in this pass — no `LanguageProvider`
rewrite, no new architecture, no code changes for this finding. Flagged for a future scoped effort to extend
`t()` coverage using the *existing* infrastructure (not a new one).

## E. Fixes Applied (Phase 2, all `frontend_bug`, all reverified)

All 5 findings root-caused to one of two shared files (design tokens, shared shell component) or one line each in
3 page files — 6 files total, well inside the ≤9-file "Preferred" budget (Contract §4.5).

| # | Finding | Evidence | File | Change |
|---|---|---|---|---|
| F1 | `ink.faint` (#8b93a1) text failed 4.5:1 AA contrast (measured 2.86–3.09:1); used by `.label-caps` (every section header, all 4 pages) + 29 other files | axe `color-contrast`, all 4 pages, both baseline viewports | `frontend/tailwind.config.ts` | Darkened token to `#616b78` (iterated 3×, verified by real render each time against both `surface-sunken` and `accent-soft` backgrounds — see commit comment in file) |
| F2 | `StatusBadge` success/caution text failed AA (4.12/3.67:1); `stale` shares the same pattern (verified by calculation, not directly observed on tested routes) | axe `color-contrast` on real rendered badges, Pages 1–2 | `frontend/tailwind.config.ts` | `state.success` `#1c8a5a`→`#047857`; `state.caution`/`state.stale` `#b5750a`/`#a2740f`→`#92400e` |
| F3 | Pages 1, 3, 4 had zero `<h1>` (Page 2 already had one per stage) | axe `page-has-heading-one` + static grep, confirmed | `CommandCenterPage.tsx`, `KnowledgePage.tsx`, `TrustPage.tsx` | Added one `<h1 className="sr-only">` per page (no visual change); also promoted `SituationTile`'s `<h3>`→`<h2>` in `CommandCenterPage.tsx` to fix the resulting heading-order skip (h1→h3), same finding, same file |
| F4 | Breadcrumb/context bar not in a landmark | axe `region`, all 4 pages | `components/shell/ProjectContextBar.tsx` | Root `<div>` → `<nav aria-label="Breadcrumb">` |
| F5 | Knowledge-claims scrollable list not keyboard-focusable | axe `scrollable-region-focusable`, Page 3 mobile | `pages/knowledge/KnowledgeClaimsTab.tsx` | Added `tabIndex={0} role="region" aria-label="Knowledge claims list"` |
| — | "Switch project" link contrast (4.2:1) | axe `color-contrast`, all pages (ProjectContextBar renders everywhere) | `components/shell/ProjectContextBar.tsx` | Swapped `text-accent` → `text-accent-strong` (reuses an existing token already used identically for sibling links elsewhere in the app, not a new color) |

No backend file, route, type, or test was touched. No design-system file beyond the two above was touched. No
page's information architecture, center object, or content changed — only color values and semantic HTML tags.

## F. Cross-page Design System Harmonization

- Both fixed tokens (`ink.faint`, `state.success`/`caution`/`stale`) are shared Tailwind config values consumed
  identically by all 4 pages via `.label-caps` and `StatusBadge` — the single-source-of-truth fix cascaded
  correctly everywhere in one edit, with zero page-specific overrides introduced (Contract §11.1 compliance:
  reused/adjusted existing tokens, invented none).
- `StatusBadge` remains the single status→color/icon/text mapping for the whole app — untouched in structure,
  only its two token inputs were darkened.
- No new design tokens, colors, spacing, radii, or components were introduced anywhere.

## G. Test Evidence

- `npm run lint` / `npm run typecheck` / `npm run test` (71/71) / `npm run build`: all **PASS**, both before and
  after the fix (baseline established first per Contract §4.3).
- Backend: `pytest tests/ -q` (deselecting 2 network-dependent "live" LLM-adapter tests, which call a real
  external API and are unsuited to a deterministic audit run) → **333/333 PASS**. Backend was not modified this
  session; rerun only to establish/confirm baseline.
- Browser audit tooling: Playwright 1.61.1 + `@axe-core/playwright`, installed **outside the repo** (session
  scratch directory) specifically so Phase 0's "no repo modification before Phase 1 classification" rule held
  while still producing real, live evidence. Script and results:
  `C:\Users\Starry\AppData\Local\Temp\claude\...\scratchpad\pwaudit\audit.js` and `out/results.json` /
  `out/*.png` (24 full-page screenshots baseline + 24 post-fix, one per page×viewport). These are session-scratch,
  matching the precedent already set by the Page 4 session's own completion report (`docs/前端精修/...`), and
  are not repo artifacts.
- Axe results: baseline had violations (serious `color-contrast` on 8/8 page×viewport-class combos tested at that
  point, moderate `page-has-heading-one` on 6/8, moderate `region` on 8/8, serious `scrollable-region-focusable`
  on 1/8) → **0 violations of any severity across all 24 real page×viewport combinations** after the fix.
- Console/network: 0 errors/warnings and 0 failed/4xx/5xx requests across all 24 combinations, plus the Evidence
  Drawer overlay state.
- Keyboard flow: traced on Page 1 (15 Tab presses, full sequence logged) — logical order, always-visible focus,
  no trap.
- Lighthouse: **not run** — not installed/available this session; not substituted with an equivalent measurement.
  Disclosed as `NOT AVAILABLE`, not silently skipped.
- Cross-browser: Chromium only, per Contract §5.1 (no pre-existing cross-browser config in this repo means
  Firefox/WebKit are not required — disclosed, not fabricated as tested).
- **Not run this session** (see §I for release-decision impact): large-scale data-density fixtures (100
  projects/100 candidates+1000 evidence/1000 knowledge records/10,000 audit events); systematic failure injection
  (API timeout, backend-unavailable, refresh-during-mutation, partial response).

## H. Regression Matrix

| Domain | Result | Evidence |
|---|---|---|
| UI | PASS | 24/24 page×viewport combos clean post-fix, no unexpected horizontal overflow |
| Interaction | PASS | Keyboard flow (Page 1), Evidence Drawer overlay (Page 2), both clean |
| Scientific | PASS | No status/confidence/evidence semantics touched; StatusBadge mapping logic unchanged, only 2 color values |
| Backend | PASS | Zero backend files touched; `git status` identical to session start for all `harness/`/`tests/`/`main.py` paths; 333/333 backend tests pass |
| Performance | PASS (no regression) | Bundle size unchanged (462.26 kB vs 461.96 kB baseline, gzip 128.65 vs 128.57 kB — noise-level) |
| Accessibility | PASS | 0 serious/critical/moderate axe violations post-fix, all pages/viewports (was: violations on all 24 at baseline) |
| Governance | PASS | No approval/audit/provenance/evaluation component touched |
| Failure Recovery | **NOT RUN** | No fault-injection executed this session (see §I) |

## I. Release Decision

```text
NEEDS_REVISION
```

**Basis**: Gates 1 (Runtime), 2 (Visual), 3 (Accessibility), 4 (Scientific), 5 (Governance), 6 (Responsive), 8
(Design System), and 9 (Regression) all **PASS** with real, reproducible evidence, zero P0/P1 findings, and zero
System Invariant violations — no fabricated capability, no governance bypass, no scientific-truth suppression, no
protected-architecture change. Gate 7 (Data Density at the Contract's prescribed scale) and Gate 11 (Failure
Recovery via systematic fault injection) could not be evidenced as PASS this session — not because anything
failed, but because no large-scale seed data and no fault-injection harness were built/run. Per Contract Gate 10
("不得使用 NOT RUN、PARTIAL 后仍判定完全 READY") this alone is sufficient to keep the system-level decision at
`NEEDS_REVISION` rather than `READY`, and per §18 that must not be silently upgraded to close out the session.

### Gate Matrix

| Gate | Result | Evidence | Blocking issue |
|---|---|---|---|
| Runtime | PASS | Real backend+frontend running, 139 live routes, 0 uncaught errors across 24 combos | — |
| Visual | PASS | 24/24 combos clean, 0 unexpected overflow, screenshots in `out/` | — |
| Accessibility | PASS | axe: 0 violations any severity, 24/24 combos, post-fix; keyboard flow traced clean | — |
| Scientific | PASS | No status/confidence/evidence conflation found or introduced | — |
| Governance | PASS | No proposal/approval/execution conflation; no self-approval; no non-versioned mutation added | — |
| Responsive | PASS | 390/768 usable, no forced desktop-only layout, all 6 viewports clean | — |
| Performance | PASS | 0 console errors, bundle size flat; Lighthouse not run (disclosed) | Lighthouse unavailable (non-blocking; browser-measured signals clean) |
| Regression | PASS | lint/typecheck/build/unit tests (71/71 FE, 333/333 BE) all green before and after | — |
| Data density | **BLOCKED (not run)** | Only real, small (~1) project/run/claim data exercised; no 100/1000/10k-scale fixtures seeded | No large-scale seeding executed this session |
| Failure Recovery | **BLOCKED (not run)** | No timeout/offline/partial/conflict fault injection executed | No fault-injection harness built this session |

### Three-dimensional Certification

- **Implementation Readiness**: Yes for all 4 pages at real, small-to-moderate data scale — every route loads
  against the real backend, every core object renders from real API data or an honest unavailable state, no
  P0/P1 defects remain after the fixes in §E.
- **Demo Readiness**: Yes for a single-project, single-run walkthrough (the exact data this session exercised) —
  Page 1's situation tiles, Page 2's stage rail + Evidence Drawer, Page 3's claims list, and Page 4's Attention/
  Approvals tabs all rendered correctly with real data and zero console errors. Not independently re-verified
  this session as a timed 5-minute end-to-end PI walkthrough with a fresh reviewer (that specific scripted
  exercise, §J.1 of the Contract, was not run as a separate pass) — the underlying page-by-page evidence
  supports it, but the scripted trace itself is `NOT RUN` this session.
- **Production Limitations**: Backend-side — no Knowledge Graph/relationship endpoint, no Biological Knowledge
  browse API, no Knowledge→Engineering reuse endpoint, no RBAC/reviewer-authority, no Memory read API, no
  consolidated approvals/override/revoke, no export endpoint, no `SimulationRun` list endpoint, no Golden Set
  target-version/suite/baseline fields — all pre-existing, all honestly degraded in the UI, none fabricated,
  none newly discovered this session (reconfirmed against the live OpenAPI surface, matching prior sessions'
  own mapping matrices exactly). Validation-side — large-scale density and fault-injection scenarios untested.

### Accepted Limitation Register (backend capability gaps — reconfirmed live, not fixed, not blocking page-level release)

```yaml
- capability: Knowledge Graph relationship model / endpoint
  affected_page: Page 3
  missing_backend_object_or_endpoint: no graph query route
  current_honest_degradation: "Unavailable" state with named reason
  blocks_release: false
- capability: Biological Knowledge browse API
  affected_page: Page 3
  missing_backend_object_or_endpoint: local JSON exists server-side only, no route
  current_honest_degradation: "Future capability" state
  blocks_release: false
- capability: Knowledge → Engineering Decision reuse endpoint
  affected_page: Page 2/3
  missing_backend_object_or_endpoint: no mutating reuse route
  current_honest_degradation: "Reuse unavailable — backend capability missing"
  blocks_release: false
- capability: SimulationRun list endpoint
  affected_page: Page 2
  missing_backend_object_or_endpoint: no GET list route (only returned from POST)
  current_honest_degradation: explicit "Unavailable via current API" panel
  blocks_release: false
- capability: reviewer authority / RBAC
  affected_page: Page 4
  missing_backend_object_or_endpoint: no auth/z anywhere in the product
  current_honest_degradation: disclosed on-page, not hidden behind a UI-only disable
  blocks_release: false
- capability: Memory read API / consolidated approvals / override / revoke / export
  affected_page: Page 4
  missing_backend_object_or_endpoint: no such routes exist
  current_honest_degradation: explicit capability-unavailable states
  blocks_release: false
- capability: Golden Set target-version/suite-version/baseline fields
  affected_page: Page 4
  missing_backend_object_or_endpoint: real list API omits these fields
  current_honest_degradation: gap named explicitly where rendered
  blocks_release: false
- capability: i18n full-page coverage
  affected_page: all 4
  missing_backend_object_or_endpoint: "n/a — frontend-only; infra exists (I18nProvider), coverage of page-body text does not"
  current_honest_degradation: "n/a (product_scope_gap, not a runtime degradation) — logged for future roadmap per explicit user decision this session"
  blocks_release: false
```

None of the above block release: each is a proven backend/scope boundary, honestly degraded, with the core task
still completable and no misleading affordances.

## J. What Would Close the Gap to READY

1. Seed representative large-scale fixtures (100 projects; 100 candidates + 1000 evidence items; 1000 knowledge
   records with conflicts/versions; 10,000 audit events) and re-run the same axe+visual+keyboard sweep against
   them (Gate 7).
2. Build or reuse a deterministic fault-injection path (route interception or test fixture) for the 10 scenarios
   in Contract §7A.1 and record pass/blocked per scenario (Gate 11).
3. Optionally: run the scripted 5-minute PI demo trace and 30-second first-time-comprehension test as their own
   timed passes (§J/§J.1 of the Contract) rather than relying on the per-page evidence gathered here.

No code change is required for any of the above — they are additional verification passes, not fixes.

---
*Report generated by an automated Release Certification session. Screenshots and raw axe/console/network JSON
referenced in §G are session-scratch artifacts (not committed to this repository), consistent with the precedent
set by this repository's own prior `docs/前端精修/` session reports.*
