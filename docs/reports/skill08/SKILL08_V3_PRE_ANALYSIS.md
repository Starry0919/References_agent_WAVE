# Skill08 V3 Pre-analysis

Date: 2026-08-12

## Current state

V2 preserves candidate immutability, separates verification from epistemic
state, enforces identity-bound handoff, requires E1+E2+E3 for verification, and
gates DDR/rule persistence. Its synthetic safety benchmark has zero critical
false-verification.

## Measured V2 gaps

- E2 only understands explicit source attribution and experiment anchor sets.
- Strain aliases, parent/derived/complemented relations and intervention
  synonyms are not represented as objects.
- References such as `this mutant` are lexical tokens rather than bounded
  references to an explicitly named antecedent.
- Knockout/deletion synonyms can reduce recall, while knockout/overexpression
  conflicts are not a dedicated attribution failure.
- The existing benchmark is synthetic and does not cite repository paper
  artifacts.

## V3 boundary

Add a lightweight deterministic biological-object graph and an evidence
benchmark sampled from existing clean-document artifacts. Resolve a reference
only when a unique, local, explicit antecedent exists. Ambiguous or implicit
lineage remains unresolved. No candidate mutation, LLM completion or external
knowledge is permitted.
