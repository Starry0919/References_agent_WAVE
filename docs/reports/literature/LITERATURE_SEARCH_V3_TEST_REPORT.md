# Literature Search v3 Test Report

## Observed regression results

- `tests/literature_discovery`: 27 passed, 0 failed, 1 existing catch-all API duplicate-operation-ID warning, 2.50 seconds.
- `tests/literature_verification` and `tests/evidence_retrieval`: 26 passed, 0 failed, 1 existing Starlette TestClient deprecation warning.
- `tests/paper_extraction`: 228 passed, 0 failed, 1 existing Starlette TestClient deprecation warning, 25.27 seconds according to the complete captured pytest log.
- Total required domains: 281 passed, 0 failed.

The direct `paper_extraction -q` tool wait timed out at 60 seconds during process teardown. A verbose rerun reached 100%, printed `228 passed`, and again remained alive after summary; the process was then stopped. This timeout is recorded and is not reported as a clean whole-command exit.

v3 coverage includes natural-language intents, request modes and budgets, query-family diversity/deduplication, K-12 lineage states, target and adjacent products, engineering/model/enzyme distinctions, DOI/cross-ID resolution and conflicts, bounded citation expansion, hard-negative suppression, classic preservation, fulltext promotion, result explanation/provenance, cache/idempotency, and Gold-independent readiness.
