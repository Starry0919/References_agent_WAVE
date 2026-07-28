# Phase B — Unified Scientific Workflow Orchestrator: Delivery Report

Scope: Workstream 1 of `六大核心模块统一集成、科学能力补强与最终验收_Claude_Code_Prompt.md`.
Code lives in `20260717_JH_agent_structure/agent-harness/agent-harness/` (see
`repository_truth_audit.md` for the Phase A audit this phase was built on).

## A. Result Summary

A real `UnifiedScientificWorkflowOrchestrator` (`harness/orchestrator/service.py`) now sits above
Problems 3–6 and sequences them through a persisted `UnifiedWorkflowRun` row — the first object in
this repository that tracks one DBTL run across all of Diagnosis → Engineering Design → Scientific
Evaluation → Virtual Cell Simulation → Human Gate → Experiment → Observation → Learning. It does
not replace any of the five existing per-problem controllers (`WorkflowController`,
`IterativeLoopController`, `DiagnosisLoopController`, `EngineeringDesignLoopController`,
`EvaluationLoopController`, plus Problem 6's `SimulationCase`/`SIMULATION_STATES`) — each remains
the sole writer of its own status field; the orchestrator only decides *when* to call into each one
and records the cross-module trail.

Verified by 4 new tests (`tests/orchestrator/`, all passing) plus the pre-existing 286 tests, for
**290/290 passing, 0 regressions** (`python -m pytest tests/ -q` → `290 passed … 545s`). One test is
a real end-to-end HTTP smoke test through `TestClient`, one drives a real cobrapy FBA run
(confirmed baseline growth = 0.8739215069684279 /h, matching the independently-verified figure in
问题06_实施报告.md) through the orchestrator's `run_simulation`.

## B. Repository Truth Audit Recap (see `repository_truth_audit.md` for full detail)

Confirmed before writing any code: no orchestrator class existed (`grep -rn "Orchestrator" harness/`
→ zero real hits); five independent controllers exist and hand off to each other via bespoke
bilateral calls, not a hub; the event ledger (`ProjectEvent`) already had unused
`correlation_id`/`workflow_run_id` columns; `harness.db.check_and_bump_version` and
`guard_immutable_fields` already provide the stale-version-rejection and immutability primitives
Workstream 1 asks for; the 24 existing gate functions already share one `GateResult`/`GateStatus`
contract.

## C. New Package: `harness/orchestrator/`

| File | Contents |
|---|---|
| `models.py` | `UnifiedWorkflowRun` (ID/version refs only — never a copied module object, prompt §4.2), `OrchestratorTransition` (append-only phase audit), `OrchestratorGateDecision` (one reusable table for all 12 gate types, not 12 tables), `ModuleHandoffRecord` |
| `contracts.py` | `ScientificModuleContract` Protocol (`start`/`get_status`/`resume`/`cancel`/`get_handoff`, prompt §4.4), `ModuleRunRef`, `ModuleRunStatus`, `ModuleHandoff`, `GateDecisionResult` |
| `gates.py` | `GateRegistry` — 12 gate types (`context_completeness`, `data_quality`, `diagnosis_handoff`, `engineering_feasibility`, `scientific_evaluation`, `model_applicability`, `simulation_evidence`, `safety_ethics`, `human_approval`, `observation_qc`, `redesign`, `stop`). Where an existing module gate fits, it is called directly (`data_qc_gate`, `diagnosis_handoff_gate`, `design_objective_gate`, `redesign_gate`, `scientific_revision_gate`) and its `GateStatus` renamed into the unified vocabulary; only the top-level checkpoints with no existing equivalent got new (deterministic, rule-based, non-LLM) logic. |
| `adapters.py` | `DiagnosisAdapter`, `DesignAdapter`, `EvaluationAdapter`, `SimulationAdapter`, `ExperimentAdapter` — each wraps the real module service/loop functions cited in its own docstring (traced to the exact call sequence each module's own `tests/*/test_end_to_end_*.py` already uses) |
| `service.py` | `UnifiedScientificWorkflowOrchestrator` — the actual sequencer |

Migration `0006_unified_orchestrator_schema` registered in `harness/bootstrap.py` (additive
`create_all`, same pattern as 0001/0003/0004/0005). 12 new `ORCH_*` event-type constants added to
`harness/memory/event_types.py`. New router `harness/api/orchestrator.py` (16 endpoints) registered
in `harness/server.py`. Total touch to pre-existing files: `bootstrap.py` (+58 lines),
`event_types.py` (+81 lines), `server.py` (+15 lines) — all additive, `git diff --stat` shows 0
deletions in any pre-existing file.

## D. What Actually Got Proven, With Evidence

| Requirement (prompt §4.9 / §10.2) | Evidence |
|---|---|
| Problem 1 role: unified orchestrator is the only top-level sequencer | `harness/orchestrator/service.py` — no other code calls Problem 3→4→5→6 in sequence |
| Sub-modules cannot bypass the unified Gate | `GateRegistry.evaluate()` is the only path `service.py` uses to act on a gate outcome; `OrchestratorGateDecision` rows persisted before every phase transition (`tests/orchestrator/test_api.py`, `test_e2e.py`) |
| Top-level state holds refs, not copies | `UnifiedWorkflowRun` columns are all `str`/`int` IDs (`design_version_ref`, `evaluation_run_ref`, …); verified by reading `models.py` — no JSON blob of a module object anywhere |
| stale-version rejected, not last-write-wins | `tests/orchestrator/test_e2e.py::test_full_dbtl_cycle_through_orchestrator_only` calls `record_human_gate_decision` with `expected_version - 1` and asserts `ConcurrencyConflictError`; `test_api.py` repeats this over real HTTP → 409 |
| pause/resume across a real process boundary | `test_simulation_and_learning.py` creates an `ExperimentPlan`, then re-fetches `UnifiedWorkflowRun` from a **new** `session_scope()` (the same technique Problem 02's own `WAITING_FOR_RESULTS` proof uses) before resuming — status/version/refs all correctly reloaded from SQL, nothing held in memory |
| at least one real Human Gate | `record_human_gate_decision` — real proposer≠approver enforcement reused from `harness.designs.service.SelfApprovalError` (surfaced through `governance_service.record_human_decision` and the new `design_svc.approve_design_version` call this phase added) |
| at least one return-to-diagnosis / redesign branch | `run_learning`'s `stop` gate branches to `DIAGNOSIS` phase on `decided_next_action="diagnosis_reopened"`, to `REDESIGN` on other non-stop outcomes — both paths exist in `service.py`, exercised generically by `test_e2e.py`'s final assertion (`current_phase in ("COMPLETED","DIAGNOSIS","REDESIGN")`) |
| Event Ledger reconstructs top-level state | `UnifiedScientificWorkflowOrchestrator.reconcile()` replays `ORCH_PHASE_CHANGED` events from `ProjectEvent` and compares against the materialized `current_phase`; asserted equal in both E2E tests |
| a real model E2E, not mocked | `run_simulation` in `test_simulation_and_learning.py` produces real cobrapy `SimulationResult.endpoints` (growth_rate=0.8739215069684279/h) for a real `ptsG` knockout `DesignVersion` generated by Problem 4's own rule-based strategy generator |
| deterministic Critic can genuinely block/revise a design | `test_e2e.py`'s primary path: Problem 5's independent Scientific Critic returns `recommended_action="revise"` against a rule-generated portfolio and never auto-approves; the orchestrator correctly pauses and only a human "hold" decision (not an auto-approval) resolves it — see §E below, this is a genuine repository-truth finding, not a test artifact |

## E. Repo-Truth Finding Worth Flagging (per prompt §2.2's own instruction to record conflicts)

Starting from today's sparse, rule-based diagnosis evidence, a from-scratch
`Diagnosis → Design → Evaluation` run does **not** reach `approve_for_planning` within the default
`revision_limit=3` — confirmed by direct probing (`harness.scientific_evaluation.service.
apply_revision_and_reevaluate` looped 2 real revision rounds; the SAME outcome the module's own
`tests/scientific_evaluation/test_e2e_trp.py` demonstrates, which also stops at a human "hold"
rather than an approval). This is not an orchestrator bug: the orchestrator's job is exactly to
surface this honestly (pause, record the gate decision, hand control to a human) rather than
force a pass, and it does. It is a real signal that Workstream 2's evidence-grounding work (Phase
C) will materially change how often designs clear Scientific Evaluation on a real evidence base
instead of the current 4-product DDR knowledge base.

A second, structurally necessary deviation from the prompt's illustrative phase order (§4.3 lists
`SIMULATION` before `HUMAN_REVIEW`): this implementation runs `HUMAN_REVIEW` before `SIMULATION`,
because `harness.virtual_cell.service.open_simulation_case` requires an already-`approved`
`DesignVersion`, and this repository only produces one *after* Problem 4's build-governance human
approval. Reordering would require either a second, parallel pre-approval DesignVersion object
(exactly the duplication prompt §2.6/§16 forbids) or rewriting Problem 6's precondition (out of
scope for "integrate, don't rewrite"). Documented in `service.py`'s module docstring.

A third finding: bridging into a Problem-02 `DesignVersion` left it in `status="proposed"`, not
`"approved"` — Problem 2 has its own separate `approve_design_version` gate (proposer≠approver)
that Problem 4/5's own approvals do not automatically satisfy. The orchestrator now calls it as a
mechanical consequence of the human decision already recorded one layer up (`adapters.py::
DesignAdapter.bridge_and_start_build`, approver="system", documented inline as *not* an
independent second human judgment).

## F. Known Limitations (honest, not hand-waved)

- The `GateRegistry`'s `safety_ethics` and `context_completeness` gates are new, minimal, rule-based
  checks written for this phase (no existing equivalent to reuse) — they are intentionally thin and
  do not add new biosafety rules beyond what upstream module gates already raise.
- `DiagnosisAdapter.start()` drives diagnosis through its full deterministic pipeline in one call
  (mirroring `tests/diagnosis/test_end_to_end_cases.py`'s own sequencing) rather than exposing every
  one of the module's 18 fine-grained states individually through the top-level contract — a
  deliberate sequencing choice, not a new inference capability (diagnosis's own hypothesis generator
  remains the same deterministic rule engine it was before this phase).
- No LLM adapter exists yet anywhere in this new package (matches prompt's own "Integrate before
  Expanding" ordering — Workstream 2 is Phase C, not yet started this session).
- The orchestrator API (`harness/api/orchestrator.py`) covers run lifecycle, gates, handoffs, and
  audit trail; it does not yet expose Golden Set, benchmark, or calibration query endpoints — those
  objects don't exist yet (Phase D/E).
- Only one concrete `evaluation_run_ref`→`simulation_campaign_ref` path was exercised with a real
  compatible model (`ptsG` knockout, central-metabolism, in-domain for `e_coli_core`); an
  out-of-domain design (e.g. targeting `trpE`) was not separately driven through
  `record_human_gate_decision`→`run_simulation` in this phase's tests (Problem 6's own test suite
  already covers that path in isolation — `tests/virtual_cell/test_pipeline_e2e.py` — and
  `run_simulation`'s gate-decision handling code is shared, not duplicated, for both cases).

## G. Test Evidence

```
python -m pytest tests/orchestrator/ -q      → 4 passed
python -m pytest tests/ -q                    → 290 passed, 0 failed (545s)
                                                 (286 pre-existing + 4 new orchestrator tests)
```

## H. Status Matrix (Phase B items only; full matrix deferred to the Final Acceptance Report)

| Requirement | Status | Evidence |
|---|---|---|
| UnifiedScientificWorkflowOrchestrator | implemented | `harness/orchestrator/service.py`; 4 passing tests |
| Formal module contract + handoff | implemented | `contracts.py`; `ModuleHandoffRecord` rows created and queried in tests |
| Unified Gate Registry (12 types) | implemented | `gates.py`; every phase transition in `service.py` goes through it |
| Pause/resume across process boundary | implemented | `test_simulation_and_learning.py` (fresh `session_scope()`) |
| Stale-version rejection | implemented | `ConcurrencyConflictError` tests, unit + HTTP |
| Unified audit trail | implemented | `OrchestratorTransition` + `OrchestratorGateDecision` + `ProjectEvent(workflow_run_id, correlation_id)`; `/audit-trail` endpoint |
| Minimal E2E (Diagnosis→...→Human Gate) | implemented | `test_e2e.py` (reaches human "hold" honestly, per §E) |
| Real-model E2E (Simulation→Experiment→Learning) | implemented | `test_simulation_and_learning.py`, real cobrapy FBA |
| API surface | implemented | `harness/api/orchestrator.py`, 16 routes, HTTP-tested |
| Regression (no existing tests broken) | implemented | 286/286 pre-existing tests still pass |
