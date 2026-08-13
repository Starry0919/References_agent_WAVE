# P0/P1 repairs

`E2E-BENCH-002` fixed the replay stage-status mapping from nonexistent keys to current `existence_status`, `attribution_status`, and `semantic_support_status`. Before: 0/15 stages reported complete. After: E1/E2/E3 each 15/15. A permanent regression test asserts all manifest papers are attempted and mapped. No scientific prompt, ontology or threshold was changed.
