# Final Closure Wave Acceptance Matrix — 2026-08-12

| Requirement | Production implementation path | Test/replay | Result | Evidence/artifact path | Remaining gap |
|---|---|---|---|---|---|
| Quantitative role isolation | `quantitative_roles.py` → guarded legacy projection | 3 mixed-context cases | PASS | `tests/reference_optimization/test_routing_and_quantitative.py` | none |
| DiagnosisFinding required | orchestrator diagnosis → finding → portfolio service | grounded orchestration and design tests | PASS | `tests/orchestrator`, `tests/engineering_design` | legacy rows remain explicitly unverified |
| Candidate state machine | `decision_state.py` plus governance/build planner | illegal jump, human-select, validation readiness | PASS | `tests/engineering_design` | none |
| EvidenceNeed closure | `dynamic_loop.resolve_and_update_hypothesis` | append-only integration replay | PASS | `tests/reference_optimization/test_evidence_need_and_prior.py` | none |
| Failure recall ranking | evaluation service → decision ranking | matched FailureCase lowers X rank | PASS | `tests/reference_optimization/test_evidence_need_and_prior.py` | none |
| Historical Prior boundary | strategy prior separated from evidence | prior/evidence assertions | PASS | `tests/reference_optimization`, `tests/engineering_design` | full ELISER ETL intentionally out of scope |
| Candidate-specific FBA | persisted ModelEvaluation / real cobrapy solve | baseline vs candidate | PASS | `tests/reference_optimization/test_candidate_state_and_fba.py` | bundled asset is iJO1366 despite legacy filename |
| Scientific state UI | canonical backend read model → candidate drawer | typecheck, 50 frontend tests, build | PASS | `frontend/src/pages/design/CandidateDetailDrawer.tsx` | no large UI redesign (out of scope) |
| Full backend regression | 25 independent shards | 821 collected | PARTIAL | `FINAL_CLOSURE_WAVE_REGRESSION_REPORT_2026-08-12.md` | 1 external LLM live failure |
| Five replay families | route, extraction, engineering, failure | 5/5 | PASS | `FINAL_CLOSURE_WAVE_REPLAY_REPORT_2026-08-12.md` | human selection intentionally remains human |
