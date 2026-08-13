# Skill08 V2 Self-Audit

Date: 2026-08-12  
Result: **PARTIAL; no unresolved P0 found**

| Audit question | Result | Evidence/action |
|---|---|---|
| Positional cross-paper join remains? | No in Skill07→08 and admitted downstream path | Replaced with per-item records and stable paper/document/hash handoff. Skill10/11 derive candidates from Skill08. |
| Skill07→DDR/Knowledge bypass remains? | No automatic persistence bypass found | DDR auto-save requires valid Skill08 output/provenance/admission; rule loader filters non-admitted DDRs. |
| Skill08 modifies candidate? | No | Candidate hash is checked before/after; output validator repeats immutability check. |
| Lexical match called semantic verified? | No | Lexical overlap is only one conservative E3 signal; ambiguous overlap is unresolved. |
| Can verified occur with E2/E3 unresolved? | No | Validator enforces E1=E2=E3=`passed` plus verified evidence ids. |
| Can rule candidate be promoted? | No | Output fixes role to `single_paper_rule_candidate`; validator rejects other roles. |
| Provenance break? | No in new V2 artifacts | Knowledge→Skill08→Skill07→document/paper fields are required by gate. Legacy artifacts fail closed. |
| Legacy compatibility reopens fail-open? | No | Legacy artifacts remain readable outside admission, but cannot auto-persist/distill without V2 provenance. |
| Validator repairs bad science? | No | Validator only rejects; it does not normalize candidate values or add evidence. |
| Untested critical path? | Partial | Synthetic adversarial and persistence tests exist; broad real-paper E2/E3 benchmark remains future work. |

## Automatic fixes made during self-audit

- Corrected the handoff schema `$ref` relative path.
- Changed multi-anchor aggregation so an explicit conflict cannot be hidden by
  another passing anchor.
- Removed residual Skill10/11 dependence on filtered Skill07 arrays.
- Restricted persistent DDR conversion to admitted claims and DDR candidates.
- Added duplicate identity and end-to-end provenance tests.

## Why this is not PASS

The required safety invariants and P0 closures are implemented, and the scoped
regression/benchmark gates pass. However, explicit Level 2 attribution does not
yet resolve all implicit biological-object/coreference cases, the benchmark is
synthetic rather than a stratified real-paper corpus, and the full repository
test run timed out. Under the supplied acceptance standard these are material,
so the correct status is `PARTIAL`.
