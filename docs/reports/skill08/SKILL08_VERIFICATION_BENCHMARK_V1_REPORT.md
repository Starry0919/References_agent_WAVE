# Skill08 Verification Benchmark V1 Report

Date: 2026-08-12

The dataset contains 13 manually specified cases grounded in three repository
`clean_document.json` artifacts. Every case carries paper/document identity,
artifact path, paragraph anchor, claim, candidate evidence, experiment context,
gold status and rationale. Tests verify source existence, anchor existence,
schema validity, and at least 0.65 candidate-to-source token overlap.

| Metric | Result |
|---|---:|
| Cases | 13 |
| Verification precision | 1.000 |
| Verification recall | 1.000 |
| Overall status accuracy | 1.000 |
| Attribution accuracy | 1.000 |
| False-verified critical claims | 0 |
| Unresolved rate | 0.000 |

Coverage includes direct evidence, background/current-study confusion, strain
lineage, deletion/overexpression confusion, negative direction, treatment/control
reversal, numeric conflict, condition mismatch, cross-experiment attribution and
mechanism-vs-observation strength. Machine-readable results are stored at
`benchmarks/skill08_verification_benchmark/reports/benchmark_results.json`.

This small repository-bound benchmark does not establish broad biological NLP
coverage. It verifies only the explicitly audited failure modes.
