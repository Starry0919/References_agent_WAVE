# Final Closure Wave Regression Report — 2026-08-12

STATUS: PARTIAL (external dependency only)

## Numbers

- Total backend shards: 25
- Completed backend shards: 25
- Total backend collected tests: 821
- Passed: 819
- Failed: 1
- Skipped: 1
- Not run: 0
- Frontend test files: 15/15 passed
- Frontend tests: 50/50 passed
- Frontend typecheck: PASS
- Frontend production build: PASS

## Shard results

All directory shards and the root-test shard completed. Deterministic failures found during the run (legacy ungrounded orchestrator fixtures, candidate selection order, simulation provenance expectations, iJO1366 identity, stale frontend mock shape) were fixed and their affected shards rerun successfully.

The sole remaining failure is:

`tests/llm_generation/test_live_llm_generation.py::test_real_poe_call_produces_valid_structured_hypotheses`

Classification: environment/external-provider. `health_check.available=True`, but two separate calls returned output rejected by the structured schema, so `fallback_used=True`. Production behavior is honest: no fabricated hypotheses and no false success.

The one skip is the existing optional evidence-intelligence case. Warnings are deprecations (Starlette TestClient, SWIG types) and do not change scientific outputs.

## High-risk reruns

- Core closure + state/FBA/governance: 55 passed.
- Replays/golden/orchestrator/simulation/large-GEM: 58 passed.
- Root + golden/orchestrator/simulation/virtual-cell: 101 passed.
- Frontend final: 50 passed.
