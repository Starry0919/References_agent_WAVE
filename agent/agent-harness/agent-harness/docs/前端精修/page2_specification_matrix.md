# Page 2 — Specification Matrix

Repo: `agent-harness/agent-harness` (frontend `dbtl-engineering-os-frontend`, backend FastAPI `harness/`).
Source contracts: `workflow/design/evolution/前端精修/Page2/Page2_DBTL_Engineering_Workspace_Claude_Code_Implementation_Prompt.md`,
`workflow/design/evolution/前端整体架构设计.md`.

**Revision 2** (this pass): all five stages (Diagnose/Design/Simulate/Critique/Build-Test-Plan)
implemented to real-backend depth, plus the Workspace Command Header and URL-persisted
cross-stage selection. Revision 1 covered only Diagnose + foundation; see git history / prior
completion report for that narrower baseline.

## Legend
`done` (implemented + verified) · `reused` (pre-existing, verified correct, not modified) ·
`gap_backend` (blocked: field/endpoint doesn't exist yet, documented not worked around) ·
`deferred` (real, in-scope, genuinely out of budget) · `n/a` (out of the fixed 5-stage IA).

| Requirement (Page2 prompt §) | UI region / object | Backend dependency | Status |
| --- | --- | --- | --- |
| §24 Workspace skeleton | `AppShell`, `ProjectContextBar`, `WorkspaceLayout`, `WorkflowStageRail` | projects/orchestrator routers | reused |
| §25 Persistent Context Bar | `ProjectContextBar.tsx` | as above | reused — decision/version/save-state fields still not shown (no unified `EngineeringDecision` object backend-side); see DSR-002 |
| §26 Workspace Command Header | `WorkspaceCommandHeader.tsx` (NEW), wired into `WorkspaceLayout` | composes `getDiagnosisSession/getHypotheses/getDiagnosisDecisions` + `getCandidates` + `getReviewsAndFindings`, all real, no new endpoints | done — every field is either a real linked object or an explicit "not yet available" string; see DSR-002 for the composition approach |
| §27 Stage Rail | `WorkflowStageRail.tsx` + `computeStageStatuses` | orchestrator audit-trail | reused, now covered by 6 unit tests (`api/orchestrator.test.ts`) |
| §29 Diagnose (objective/context/bottlenecks/causal reasoning/evidence/confidence/uncertainty/alternatives) | `DiagnoseStage.tsx` | `harness/api/diagnosis.py` (7 endpoints consumed) | done — `objective_id` and deeper `HypothesisAssessment` confidence fields remain `gap_backend`, rendered as explicit unavailable notices |
| §29 Design (proposals/interventions/mechanisms/alternatives/trade-offs/feasibility/evidence/selection) | `DesignStage.tsx` | `harness/api/engineering_design.py` (project, strategies, candidates, evaluation, audit-trail, human-decision) | done — build/test package content is `gap_backend` (reference id only, no resolving GET route) |
| §29 Simulate (tool/model/run/status/outputs/uncertainty/limitations/baseline/provenance) | `SimulateStage.tsx` | `harness/api/virtual_cell.py` (models, case, transitions, validation-plan) | done for everything discoverable; run-level inputs/outputs/uncertainty are `gap_backend` — no route lists `SimulationRun`s for a case (see backend_mapping_matrix.md) |
| §29 Critique (reviews/evidence-gaps/contradictions/risks/requested-changes/resolution/governance) | `CritiqueStage.tsx` | `harness/api/scientific_evaluation.py` (deterministic checks, evidence assessments, reviews+findings, candidate-comparison, meta-review, version-history, human-decision, audit-trail — 8 endpoints) | done — the richest stage; meta-review is the real "resolution/governance state" object |
| §29 Build/Test (intervention summary/controls/readouts/success-failure/safety/dependencies/approval/handoff) | `BuildTestPlanStage.tsx` | `harness/api/experiments.py` (NEW adapter) + engineering_design candidates + orchestrator human-gate | done for intervention summary (via approved candidate), plan linkage, execution status, and readouts (real `Observation` rows); controls/factors/success-failure criteria are `gap_backend` — stored at plan creation but not returned by `GET /plans/{id}` |
| §21/§40 Approval/consequential action, all 4 remaining stages | `HumanGatePanel` (shared, extended once with `allowRevision`) | `POST .../human-decision` or `.../approve` per domain, real | done — every gate is bound to a real object id/version; Diagnose/Design/Critique conservatively offer only approve/reject where the exact accepted decision vocabulary wasn't confirmed in code (documented per-file), Build/Test Plan's existing free-string wiring to the orchestrator gate is unchanged |
| §30 Contextual Inspector | `ObjectInspector` (shared) | derived from each stage's already-fetched data | done in all 4 new stages, reusing the one shared component (no forks) |
| §31 Evidence Drawer | `EvidenceDrawer` (shared) | Diagnose evidence-links, Design strategy evidence-links, Critique evidence-assessments | done in 3 of 5 stages (Simulate/Build-Test have no evidence-linkable object in the current backend surface) |
| §32 Decision Comparison | Design stage inline table + Critique's Pareto vector table | `GET candidates/{id}/evaluation` (per-candidate) and `GET evaluations/{id}/candidate-comparison` (cross-candidate) | done when ≥2 comparable candidates exist; explicit `unavailable` state (not hidden) when fewer than 2, naming the exact endpoint needed |
| §22 Cross-stage persistence: project/cycle/stage | route path segments | n/a | reused (pre-existing) |
| §22 Cross-stage persistence: selected object / Inspector state | `useUrlSelection` hook (NEW), adopted by all 4 selection-bearing stages | n/a (URL only) | done — refresh-safe; see DSR-002 |
| §22 Cross-stage persistence: evidence context / drawer-open | not persisted to URL | n/a | intentionally deferred — treated as local/ephemeral UI state per architecture doc §18.2 ("局部交互状态 ... 不升级为全局状态"); see DSR-002 |
| §20 Computational traceability / audit trail | `<details>` sections in all 4 new stages | per-domain audit-trail endpoints (all real) | done |
| §29 Learn canvas | n/a | n/a | out of the fixed 5-stage IA (folded into build_test_plan per 前端整体架构设计.md §八) — not a gap |
| §44 Keyboard/accessibility | real `<button>`s with `aria-pressed`, `aria-label` on drawer close, native `<details>/<summary>` throughout | n/a | partial — implemented per established pattern; no interactive keyboard-only or screen-reader pass was run (no browser automation tool in this environment) |
| §54 Performance budget | n/a | n/a | done (measured): build output 399.9 kB JS / 114.0 kB gzip (+62 kB gzip over the Diagnose-only baseline, spread across 4 new stages + Command Header + 2 new adapters); Design's comparison table caps at 6 candidates (`COMPARISON_CAP`), evaluations fetched via `useQueries` not sequential awaits |
| §56 Testing strategy | Vitest (concurrent session added the framework; this session fixed a `vite`/`vitest` peer-version type conflict and a missing `@testing-library/react` cleanup registration in the shared `test/setup.ts`) | n/a | done — 24 new tests (adapters: mapping + request-shape via `vi.spyOn`; `computeStageStatuses` state-transition coverage; `HumanGatePanel` approval/version-binding + `allowRevision` regression; `EmptyState` unavailable-state coverage). Full suite: 39/39 passing (includes the concurrent session's own Page 1 tests) |

## Concurrent-session note
This repository had a second, concurrent Claude Code session actively editing `frontend/`
throughout this pass (Page 1 Command Center work: `types/domain.ts` `ProjectStatusView`,
`api/projects.ts` `getProjectStatusView`, `CommandCenterPage.tsx`, `StatusBadge.tsx`,
`ProjectContextBar.tsx`, the Vitest setup itself). This session touched none of those files
except the shared `test/setup.ts` (one-line cleanup-registration fix, benefits both sessions)
and `package.json`/`vite.config.ts` (fixed a real `vitest`/`vite` type conflict blocking
`npm run typecheck` for both sessions). See the completion report for the full incident note,
including an operational mistake (`taskkill /F /IM node.exe` twice killed all Node processes
system-wide, not just this session's dev server).
