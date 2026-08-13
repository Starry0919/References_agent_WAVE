# Paper Extraction E2E Benchmark V1 Report

## Measured result

| Metric | Development | Holdout | Combined |
|---|---:|---:|---:|
| Papers | 10 | 5 | 15 |
| Field claims | 160 | 80 | 240 |
| E1 anchor rate | 1.000 | 0.788 | 0.929 |
| E2 pass rate | 0.656 | 0.550 | 0.621 |
| E3 pass rate | 0.106 | 0.038 | 0.083 |
| Strict verified yield | 0.082 | 0.039 | 0.068 |
| Unresolved rate | 0.338 | 0.413 | 0.363 |
| Provenance traceability | 1.000 | 1.000 | 1.000 |

The development-to-holdout strict-yield gap is 0.042. This does not establish
overfitting because no tuning used holdout, but it shows worse holdout coverage.
The largest observed bottleneck is E3 semantic support after broad document-level
Skill07 values are flattened into single claims. This suggests that historical
Skill07 projection values are often too composite for claim-level verification.

Experiment precision/recall and DDR decision precision/recall are **not
estimable** from the available Silver assets. The historical caches predate the
current handoff contract, so knowledge admission was not replayed and its invalid
admission rate is also not estimable. Safety regressions separately preserve zero
known false-verified critical claims.

Machine-readable results:
`benchmarks/paper_extraction_e2e_v1/reports/e2e_results.json`.

Validation: the scoped paper-extraction suite passed 175 tests with one existing
Starlette deprecation warning. The whole-repository suite exceeded 120 seconds
without producing progress/failure output and is therefore INCONCLUSIVE.
