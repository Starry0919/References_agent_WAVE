# V2 migration and compatibility

Migration is additive and preserves `fields`, `experimental_design_object`, raw legacy payload, source version and normalization version. Lossy/unresolved identity is explicit and review-required. String/dict/list evidence locators continue through the existing normalizer; unsupported shapes fail closed rather than crash. `E2E-BENCH-001` is retained as a named benchmark regression. V3-to-V2 projection is deterministic but does not claim semantic equivalence.
