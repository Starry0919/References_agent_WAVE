# Skill08 V3 Self-audit

Date: 2026-08-12  
Final status: **PASS for the scoped Skill08 V3 release gates**

| Gate | Status | Evidence |
|---|---|---|
| Real-paper benchmark and gold schema | PASS | 13 anchored cases; integrity/schema tests pass |
| Critical false-verification count | PASS | 0 |
| E2 attribution improvement | PASS | object, intervention and control dimensions |
| Conservative biological coreference | PASS | unique local antecedent only |
| E3 precision | PASS | subordinate to E2; precision 1.0 |
| Paper-extraction regression | PASS | 164 passed |
| Provenance/admission invariants | PASS | V2 invariant tests remain in regression |
| Whole repository suite | INCONCLUSIVE | no output after >3 minutes; terminated |

## Overclaim and residual-risk check

This benchmark is small and repository-bound. Co-occurrence does not create a
parent relation when multiple named parent candidates exist; cross-section or
long-distance references are not guessed; lexical similarity cannot override a
biological attribution failure; candidate evidence is not rewritten.

Coverage remains regex-driven and English-centric. Multi-hop lineage, organisms
outside the controlled strain set, complete coordinated gene-list modeling,
implicit table headers and distant references remain future benchmark areas.
