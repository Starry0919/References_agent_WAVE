# Literature Classification and Routing v2 Test Report

## Observed results

- `tests/literature_discovery`: 20 passed, 0 failed.
- `tests/literature_verification` plus `tests/evidence_retrieval`: 26 passed, 0 failed, 1 existing Starlette TestClient deprecation warning.
- `tests/paper_extraction`: 228 passed, 0 failed, 1 existing Starlette TestClient deprecation warning; completed in 24.87 seconds according to the captured pytest log.
- Total across the required test directories: 274 passed, 0 failed.

One combined four-directory invocation exceeded the 120-second tool wait while other independent pytest/server processes were active in the same workspace. Split-directory reruns completed successfully. The paper-extraction tool wait also expired during process teardown after pytest had already printed its complete `228 passed` summary; this timeout is recorded rather than hidden.

## v2-specific coverage

- controlled vocabularies and contract versions;
- multi-label axes and unknown fallback;
- narrative, systematic, scoping, meta-analysis, technology, and generic review handling;
- false-review protection;
- wet-lab, computational, and hybrid design;
- knockout, overexpression, promoter, transporter, fermentation, and evidence metrics;
- experimental, review, model, method, resource, software, benchmark, background, and manual-review routing;
- metadata-to-fulltext provenance and conflict routing;
- Gold-pending functional readiness;
- old-candidate and old-request compatibility;
- unchanged Skill07/08 regression behavior.
