# Deliverable 4 — Backend Mapping Matrix

Status legend: `available` (real, reachable, wired) · `partial` (real endpoint exists but a needed
capability, usually list/discovery, is missing) · `absent` (no endpoint exists) · `unclear` ·
`blocked`. "Demo data" column is `no` throughout — this build wires real endpoints only; where data
is genuinely absent the UI shows an honest empty state, never a fabricated number.

| UI domain | Required object | Real endpoint / schema | Status | Adapter | Demo data |
| --- | --- | --- | --- | --- | --- |
| Project Switcher / Command Center identity | `Project` | `GET/POST /api/projects`, `GET /api/projects/{id}` | available | `api/projects.ts` | no |
| Command Center cycle summary | `IterativeCycleState` | `GET /api/projects/{id}/cycle` | available | `api/projects.ts` | no |
| Command Center status view | project status view | `GET /api/projects/{id}/status` | available | `api/projects.ts::getProjectStatus` (raw passthrough — see Page 1 handoff) | no |
| Command Center recent events / Trust audit trail | `ProjectEvent` | `GET /api/projects/{id}/timeline` | available | `api/projects.ts::getTimeline` | no |
| Workspace stage rail driver | `UnifiedWorkflowRun` | `POST /api/orchestrator/runs`, `GET /api/orchestrator/runs/{id}` | **partial** — real, but no list-by-project endpoint; run must be known by ID (URL `?run=`) or freshly created | `api/orchestrator.ts` | no |
| Workspace stage rail status history | `OrchestratorTransition`, `OrchestratorGateDecision` | `GET /api/orchestrator/runs/{id}/audit-trail` | partial (same run-discovery gap) | `api/orchestrator.ts::getAuditTrail` | no |
| Build/Test Plan human gate | governance decision | `POST /api/orchestrator/runs/{id}/human-gate-decision` | available (real mutation, wired) | `pages/workspace/BuildTestPlanStage.tsx` | no |
| Diagnose stage | `DiagnosisSession`, `HypothesisVersion` | `GET /api/diagnosis/sessions/{id}`, `.../hypotheses` | available (committed, 67 tests) — but **no real session exists for the only real project yet** | `api/diagnosis.ts` | no (honest `first_use` empty state) |
| Diagnose model capabilities | model adapter registry | `GET /api/diagnosis/model-capabilities` | available | `api/diagnosis.ts::getModelCapabilities` | no (not yet wired into a page, see Known Gaps) |
| Design stage | `EngineeringDesignProject`, `CandidateDesign` | `GET /api/engineering-design/projects/{id}`, `.../candidates` | partial — real, uncommitted, not yet exercised against the one real project | `api/engineeringDesign.ts` | no |
| Simulate stage — model registry | `Model` | `GET /api/virtual-cell/models` | available — real, honestly reports `gem_fba` available, `vecoli`/`kinetic` unavailable | `api/virtualCell.ts::listModels` | no |
| Simulate stage — case | `SimulationCase` | `GET /api/virtual-cell/simulation-cases/{id}` | partial — real, uncommitted; 2 real cases exist in the DB but not yet linked to an orchestrator run | `api/virtualCell.ts` | no |
| Critique stage | `EvaluationCase`, `CriticFinding` | `GET /api/scientific-evaluation/evaluations/{id}`, `.../reviews` | partial — real, uncommitted, not yet exercised against the one real project | `api/scientificEvaluation.ts` | no |
| Knowledge — Literature Evidence | local DDR search | `GET /api/generation/evidence/search?source=local_ddr` | **available — real, verified live** (returns a real DDR paper w/ real DOI for "tryptophan") | `api/evidence.ts::searchEvidence` | no |
| Knowledge — Literature Evidence (network) | crossref | `GET /api/generation/health` reports `crossref.available` | unclear (depends on runtime network + API key; not independently verified this session) | `api/evidence.ts::getGenerationHealth` | no |
| Knowledge — Biological Knowledge | DDR / rules / engineering-action library | none — only raw JSON files under `knowledge/` | **absent** | none | no (explicit `partial` empty state naming the gap) |
| Knowledge — Evidence Graph | Observation→…→Outcome graph query | none | **absent** | none | no |
| Trust — Memory | project/cycle memory, lessons learned | `harness/memory/` exists server-side but has no dedicated read API | **absent** | none | no |
| Trust — Version History / Audit Trail | `ProjectEvent` | `GET /api/projects/{id}/timeline` | available — **verified live**, real event stream (30+ real events for the seed project) | `api/projects.ts::getTimeline` | no |
| Trust — Human Approval (consolidated) | cross-object pending approvals | no unified query; per-object approval endpoints exist (`designs.approve`, `scientific-evaluation.human-decision`, `orchestrator.human-gate-decision`) | **partial** | none (approvals actioned inline in Workspace instead) | no |
| Trust — System Evaluation | `GoldenCase` | `GET /api/golden-set/cases`, `.../review-status` | partial — real, uncommitted; **0 cases seeded in this DB session** (`POST /seed` not run) | `api/goldenSet.ts` | no (honest `first_use` state) |
| Backend connectivity | health | `GET /api/health` | available — polled every 30s, drives every `CapabilityState` badge | `state/BackendHealth.tsx` | no |

## Unresolved issues (carried into Page 1/2 handoff)

1. No `GET /api/orchestrator/runs?project_id=` — every Workspace page-load for a project with an
   existing run requires the run id to already be in the URL. First-time users must click "Start
   orchestrated workflow," which is real but creates a *new* run rather than resuming a prior one.
2. `build_project_status_view()` (`GET /api/projects/{id}/status`) has no committed frontend view
   model yet — the Command Center currently renders it as raw formatted JSON pending Page 1
   detailed design deciding which fields become first-class UI.
3. No cross-object "pending approvals" query — Trust & Provenance's Human Approval tab cannot list
   what's outstanding across Diagnose/Design/Critique/Build-Test-Plan today.
4. No Biological Knowledge browse/search API and no Evidence Graph query API — both domains are
   named, honest `absent` placeholders, not stubbed with fake content.
