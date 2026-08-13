# Cache stress report

Deterministic cache tests pass: exact hits, document/schema/prompt invalidation, Skill/contract hash participation, invalid/corrupt cache rejection, current-validator recheck, atomic writes and failed-output non-caching. `test_unified_extraction.py` passed 14/14. A remaining P1 capability gap is that the extraction cache has atomic writes but no per-key singleflight lock, so concurrent cold requests for the same paper may duplicate provider calls; writes remain content-addressed/atomic and should not corrupt data.
