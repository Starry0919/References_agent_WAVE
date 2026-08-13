# Final Closure Wave Replay Report — 2026-08-12

## Replay 1 — SynBioGPT2

Result: PASS. Routed to `BENCHMARK_ROUTE`; wet-lab `ExperimentInstance` and K-12 proposal are forbidden; benchmark counts/runtime retain computational semantic roles.

Artifact: `tests/reference_optimization/test_contracts_and_replay.py`, `tests/reference_optimization/test_routing_and_quantitative.py`.

## Replay 2 — ELISER

Result: PASS. Routed to `RESOURCE_ROUTE`; zero fake strain experiments; output is Historical Prior only and is explicitly not evidence or recommendation.

Artifact: `tests/reference_optimization/test_contracts_and_replay.py`, `tests/reference_optimization/test_routing_and_quantitative.py`.

## Replay 3 — Primary experimental paper

Result: PASS. A genuine cultivation/titer/biological-replicate document remains on `PRIMARY_EXPERIMENTAL_ROUTE`; `ExperimentInstance` output is permitted and quantities retain role-specific meaning.

Artifact: `tests/reference_optimization/test_routing_and_quantitative.py`, full extractor coverage in `tests/paper_extraction` (234 passed).

## Replay 4 — Grounded engineering project

Result: PASS. Real QC-passed DataAsset/Observation baseline comparison produces EngineeringProblem, HypothesisVersion and DiagnosisFinding; candidate portfolio evaluates to `human_selection_pending`. Without an independent human it stops there. Separate governance tests exercise an explicit non-self human approval fixture.

Artifact: `tests/orchestrator`, `tests/engineering_design/test_end_to_end_trp.py`, `tests/engineering_design/fixtures.py`.

## Replay 5 — Failure learning

Result: PASS. A QC-passed biological negative becomes shared `FailureCase`; measurement failure is excluded; context-matched recall adds a penalty and moves tied Candidate X from rank 1 to rank 2 in the production ranking function.

Artifact: `tests/reference_optimization/test_evidence_need_and_prior.py`, `tests/engineering_design/test_memory_and_outcome.py`.

No replay fabricated Observation, model capability, wet-lab result, human approval, or Human Gold.
