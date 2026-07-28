# Repository Truth Audit — Synthetic Biology Agent V1

Date: 2026-07-23. Scope: `20260717_JH_agent_structure/agent-harness/agent-harness/` (the actual
code repository behind Problems 1–6; everything under `workflow/design/` and `reference/` in the
parent folder is design prompts / literature PDFs, not runnable code).

This audit was produced by reading real files, running the real test suite, and inspecting real
`git status`/`git log` — not by trusting the existing `问题0X_实施报告.md` reports. Those reports
turned out to be substantially accurate (cross-checked below), but were not assumed correct.

## 1. Repository / working-tree state

- The code lives in its own **separate git repo**: `20260717_JH_agent_structure/agent-harness/agent-harness/.git`
  (the top-level `d:\Users\Starry\Desktop\agent` folder is *not* a git repo — confirmed by the
  environment header).
- Branch: `master`. 4 commits total, one per problem 1–3 plus a pre-refactor baseline. Problems
  4, 5, 6 exist only as **uncommitted / untracked working-tree changes** (`git status`):
  - Untracked: `harness/api/engineering_design.py`, `harness/api/scientific_evaluation.py`,
    `harness/api/virtual_cell.py`, `harness/engineering_design/`, `harness/scientific_evaluation/`,
    `harness/virtual_cell/`, `tests/engineering_design/`, `tests/scientific_evaluation/`,
    `tests/virtual_cell/`, `web/virtual_cell.html`.
  - Modified-but-uncommitted: `README.md`, `harness/bootstrap.py`, `harness/cell_state/models.py`,
    `harness/cell_state/snapshots.py`, `harness/diagnosis/model_adapters/gem_fba.py`,
    `harness/memory/event_types.py`, `harness/server.py`, `harness/workflow/gates.py`.
  - **This is real, substantial, in-progress user/agent work and was not touched, discarded, or
    committed by this audit.** No destructive git operations were run.

## 2. Test baseline (run before any code change)

```
cd 20260717_JH_agent_structure/agent-harness/agent-harness
.venv (Python 3.12.10) — cobra 0.31.1, fastapi, sqlalchemy, pydantic all import cleanly
python -m pytest tests/ -q
→ 286 passed, 0 failed, 460.34s (0:07:40)
```

Per-directory collection counts (`pytest --collect-only`):

| Directory | Tests | Maps to |
|---|---|---|
| `tests/workflow/` | 51 | Problem 1 (Workflow Engine) |
| `tests/projects/` | 35 | Problem 2 (Memory / Iterative DBTL) |
| `tests/diagnosis/` | 67 | Problem 3 (Bottleneck Diagnosis) |
| `tests/engineering_design/` | 43 | Problem 4 (Engineering Design) |
| `tests/scientific_evaluation/` | 31 | Problem 5 (Scientific Evaluation) |
| `tests/virtual_cell/` | 47 | Problem 6 (Virtual Cell / Simulation) |

This is the regression baseline that Phase B onward must not break.

## 3. Six-module implementation matrix (real code paths)

| # | Module | Controller (real class) | States | Package | Own tables? |
|---|---|---|---|---|---|
| 1 | Workflow Engine | `harness/workflow/controller.py::WorkflowController` | 11 stages (`harness/workflow/definitions.py`) | `harness/workflow/` | JSON snapshots (`workflow_runs/{id}.json`), not SQL |
| 2 | Memory & Iterative DBTL | `harness/workflow/iterative_loop.py::IterativeLoopController` | 14 states (`DBTL_STATES`) | `harness/{projects,designs,constructs,experiments,analysis,learning,cell_state}/` | SQLite `project_ledger.db`, event-sourced `ProjectEvent` |
| 3 | Bottleneck Diagnosis | `harness/diagnosis/loop.py::DiagnosisLoopController` | 18 states | `harness/diagnosis/` | 15 new tables, same `project_ledger.db` |
| 4 | Engineering Design | `harness/engineering_design/loop.py::EngineeringDesignLoopController` | 18 states | `harness/engineering_design/` (18 files, ~3165 lines) | 11 new tables, same ledger |
| 5 | Scientific Evaluation | `harness/scientific_evaluation/loop.py::EvaluationLoopController` | 15 states | `harness/scientific_evaluation/` | same ledger, no new engine — reuses Problem 4 objects |
| 6 | Virtual Cell / Simulation | orchestration lives in `harness/virtual_cell/service.py` (no dedicated `XxxLoopController` class — uses its own `SIMULATION_STATES` + `SimulationTransition` audit table, same pattern) | own state set | `harness/virtual_cell/` (17 files) | 17 new `vc_*` tables, migration `0005_virtual_cell_schema` |

**Confirmed: there are five/six independent controllers, each the sole writer of its own
`current_state`/`status` field, each appending to the same `project_events` table, but with
`SI *no top-level object that owns cross-controller sequencing*.** Evidence:

```
grep -rn "Orchestrator" harness/ --include=*.py
→ only one incidental match in scientific_evaluation/revision.py (unrelated string), no orchestrator class exists.
```

This is exactly gap #1 from the prompt (`Problem 1 尚未真正成为 Problem 3–6 的唯一顶层调度者`) —
confirmed true by direct code search, not assumed from the prompt's framing.

**How modules currently hand off to each other** (point-to-point, not through a hub):
- `harness/diagnosis/handoff.py` → calls Problem 1's Workflow Engine directly (legacy path) *and*
- `harness/engineering_design/handoff.py::ingest_diagnosis_decision` → consumes the same
  `DiagnosisDecision` as a second, more complete path (per README, both exist side by side).
- `harness/engineering_design/design_version_bridge.py` → writes into Problem 2's `DesignVersion`.
- `harness/scientific_evaluation/gate_hooks.py` → hooks into Problem 4's
  `governance_service.mark_planning_complete`/`record_human_decision`.
- `harness/scientific_evaluation/diagnosis_return.py` → creates a new Problem 3 `DiagnosisSession`.
- `harness/virtual_cell/service.py` → consumes Problem 2's `DesignVersion` (must be `approved`),
  and gates on Problem 5's `EvaluationCase` via `assert_evaluation_not_blocking`.

Every one of these links is real (covered by passing tests), but each is a **bespoke bilateral
call**, not a top-level state machine deciding "what happens next" — confirming gap #1 concretely.

## 4. Shared infrastructure already in place (reusable substrate for Phase B)

This materially reduces Phase B's scope — most of the primitives Workstream 1 asks for already
exist and just need a new consumer, not reinvention:

- **Event ledger with orchestrator hooks already present**: `harness/projects/models.py::ProjectEvent`
  already has `correlation_id` **and** `workflow_run_id` nullable columns
  (`harness/projects/models.py:78-79`), and `harness/memory/event_store.py::append_event` already
  accepts both as kwargs. No prior module actually populates `workflow_run_id` yet (checked: no
  hits besides the column/param declarations) — but the schema was already anticipating a unified
  run identifier.
- **Stale-version rejection primitive already exists**: `harness/db.py::check_and_bump_version`
  raises `ConcurrencyConflictError` (not last-write-wins) — used today by `Project` and
  `IterativeCycleState`. Phase B can reuse this verbatim for a new `UnifiedWorkflowRun.version`
  column instead of inventing a second concurrency mechanism.
- **Immutability guard already exists**: `harness/db.py::guard_immutable_fields` (ORM
  `before_update` listener) — used by every module's versioned objects (`DesignVersion`,
  `HypothesisVersion`, etc.). A new top-level `UnifiedWorkflowRun` row should mark its `*_ref`
  fields immutable and only `status`/`current_phase`/pause-resume bookkeeping mutable, using this
  same guard.
- **Gate contract already unified**: all 24 existing gate functions across all 5 committed/staged
  modules (`harness/workflow/gates.py`) return the same `GateResult`/`GateStatus`/`GateViolation`
  pydantic contract. A `GateRegistry` for Phase B is a thin registration/lookup wrapper around
  these, not a new contract.
- **Migration runner already versioned and additive**: `harness/migrations.py` + `@migration(...)`
  decorators in `harness/bootstrap.py` — currently at `0005_virtual_cell_schema`. A Phase B
  migration is `0006_unified_orchestrator_schema`, following the exact same pattern (all prior
  migrations are additive `create_all`/`ALTER TABLE ADD COLUMN`, never destructive).
- **ID convention**: `harness/ids.py::new_id(prefix)` → `f"{prefix}-{uuid4().hex[:12]}"`, used
  everywhere. A `UnifiedWorkflowRun` should use `WFR-<hex12>`.

## 5. Scientific generation reality (Workstream 2 gap, confirmed)

- `grep -rl "harness.llm" harness/diagnosis harness/engineering_design harness/scientific_evaluation harness/virtual_cell`
  → **zero real hits** (`scientific_evaluation/critic.py` only *mentions* `harness.llm` in a
  docstring explaining why it deliberately does *not* call it). Confirmed: `hypothesis_generator.py`
  (Problem 3), `strategy_generator.py` (Problem 4), `critic.py` (Problem 5) are all deterministic
  rule engines today — zero live LLM calls anywhere in the scientific pipeline. This matches
  gap #2 from the prompt, confirmed by grep rather than assumed.
- `harness/llm.py` (the *general chat agent's* LLM client) does exist and is functional — used
  only by the free-form `agent.py` tool-calling loop, never by the scientific modules.
- **A real, configured LLM provider exists**: `.env` has `LLM_PROVIDER=kimi` with a real
  `KIMI_API_KEY` set (OpenAI-compatible endpoint, `harness/providers.py`). This means Phase C's
  LLM adapters can be wired to a real provider, not forced into `unavailable` — subject to a live
  connectivity check, which had not yet been performed as of this audit.
- No `EvidenceRetrievalAdapter`-shaped interface exists yet (`grep -rl "EvidenceRetrievalAdapter"`
  → no hits). Evidence today comes only from the local DDR JSON knowledge base
  (`knowledge/ddr_database/*.json`, 4 products) referenced by `harness/diagnosis/evidence.py` and
  `harness/scientific_evaluation/evidence.py`. No network literature retrieval exists in this repo.

## 6. Virtual Cell / model capability reality (Workstream 3 gap, confirmed)

Cross-checked directly against `harness/virtual_cell/` code, not just the 问题06 report:

- **Real, working adapter**: `gem_fba` — cobrapy 0.31.1 against the bundled `e_coli_core` model
  (137 genes / 95 reactions). `harness/diagnosis/model_adapters/gem_fba.py` calls real
  `model.optimize()`. Confirmed by re-running `tests/virtual_cell/` (47/47 pass) as part of the
  286-test baseline above.
- **Honestly-unavailable adapters**: `vecoli.py`, `kinetic.py` both return
  `CapabilityStatus(available=False, ...)` and `runtime_status="not_computed"` unconditionally —
  no fabricated numbers, confirmed by reading the adapter source directly (quoted above).
- **A real vEcoli source checkout exists** at `20260717_JH_agent_structure/vEcoli/` (this audit
  confirmed the directory tree: `ecoli/`, `reconstruction/`, `wholecell/`, `runscripts/`, etc. —
  a full whole-cell-model repo, not a stub). The 问题06 report states its bundled `.venv` is
  Linux-only and unusable on this native-Windows host, with WSL present but no vEcoli
  checkout/ParCa `sim_data` inside it. This audit did **not** re-verify the WSL claim first-hand
  (would require shelling into WSL); it is recorded here as **not independently re-verified**,
  carried forward from the 问题06 report pending Phase D's formal `VEcoliAvailabilityAudit`.
- **No larger E. coli GEM** (iML1515/iJO1366) file exists anywhere in the repository (only
  cobrapy's bundled toy `e_coli_core` is used) — confirmed by file search; Phase D must either
  source a real model file or report `blocked_by_dependency`, never fabricate one.
- **`CrossModalConsistencyReport` does not exist** — confirmed no such class/table in
  `harness/virtual_cell/models.py` (32KB file, read in full during Phase D scoping) or anywhere
  else in the repo. This is a real, complete gap, exactly as the 问题06 report's §G states.
- **Benchmark + calibration already real, not scaffold**: `harness/virtual_cell/benchmark_service.py`
  (`ModelBenchmarkRecord`) and `calibration_service.py` (`PredictionCalibrationProfile`) exist with
  passing tests (`test_phase3_feedback_loop.py`) — this is further along than the prompt assumed.
- **Multi-scenario / combination intervention**: schema-level support exists
  (`simulation_config.replicate_index`/`random_seed` fields, `merge_compiled_bounds` conflict
  detection) but per the 问题06 report is only exercised in tests for single-gene S0/S1, not a
  real multi-replicate stochastic model (gem_fba is deterministic, so replicate variance has never
  actually been produced) — an honest partial gap, not a fabricated pass.

## 7. Golden Set reality (Workstream 4 gap, confirmed)

`grep -rl "GoldenSet\|golden_case\|GoldenCase"` across `harness/` and `tests/` → **zero hits**.
No Golden Set schema, no candidate cases, no evaluation runner exists anywhere in the repository.
This is a complete, ground-up build for Phase E — nothing to reuse except the existing
`EvaluationLoopController`/`ScientificCritique` output shapes it will score against.

## 8. Duplicate/overlapping schema check

No duplicate `Memory`/`ProjectEvent`-equivalent tables were found — every module's `models.py`
imports and extends the same `harness.db.Base`/`project_ledger.db`. No second event ledger, no
second memory store exists anywhere (`grep` for a second `class.*Event.*Base` or second SQLite
file found none). This satisfies the prompt's "no parallel Memory/Event Ledger" precondition
*before* Phase B starts, not just as a target to preserve.

## 9. Risk ranking for Phase B

1. **Highest risk**: introducing a `UnifiedWorkflowRun` that *copies* module payloads instead of
   referencing them by ID/version (explicitly forbidden, §4.2 of the prompt) — mitigated by
   storing only `*_ref` string IDs + `version` ints, never nested objects, in the new table.
2. **Medium risk**: `WAITING_FOR_EXPERIMENT`-style cross-process pause/resume — Problem 2 already
   proved this pattern works (`WAITING_FOR_RESULTS` survives `kill -9`), so Phase B should reuse
   that pattern (SQL row + `session_scope()`), not JSON-snapshot-based like Problem 1.
3. **Medium risk**: some existing gates (`safety_human_gate`, `evaluator_revision_gate`, etc.)
   have signatures specific to their module's context object — a `GateRegistry` needs a thin
   adapter per gate, not a signature rewrite (would risk regressing the 43/31/47/67/51/35
   passing tests per module).
4. **Low risk**: new API endpoints for the orchestrator are purely additive (new router file),
   same pattern as `harness/api/virtual_cell.py`.

## 10. What Phase A does NOT claim

- This audit does not claim the existing 问题0X_实施报告.md reports are fully verified in every
  claim (e.g. the exact live-HTTP demo transcript in 问题06 §F was not independently re-run this
  session) — those specific runtime claims are marked `not_verified` (carried forward, not
  re-confirmed) rather than either accepted or rejected outright. Everything stated as fact above
  (test counts, file existence, grep results, git status) *was* independently re-run this session.
- No production code was modified during Phase A.

---

**Phase A gate check (§11 of the prompt): passed.** Tests were run before any code change (286/286
baseline recorded above); audit is grounded in re-run commands, not the prior reports alone.
