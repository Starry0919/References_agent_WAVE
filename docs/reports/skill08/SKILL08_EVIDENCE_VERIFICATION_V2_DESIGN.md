# Skill08 Evidence Verification V2 Design

## Flow

```text
Skill07 result envelope + CleanDocumentArtifact + workflow artifact identity
  -> Handoff validator (fail closed)
  -> immutable candidate snapshot
  -> E1 anchor integrity
  -> E2 source/experiment attribution
  -> conservative E3 structured support
  -> field and DDR verification verdicts
  -> output validator
  -> Knowledge Admission Gate
  -> persistent DDR candidate / pending rule candidate
```

## Decisions

- Join key is the clean-document artifact id plus paper id and SHA-256. There
  is no positional fallback.
- `verified` requires E1, E2 and E3 all to pass. Lexical retrieval is only a
  provisional locator and never a semantic verdict.
- Verification failure never changes candidate epistemic/applicability state.
- DDR verification asks whether the paper supports the reported decision, not
  whether the decision is scientifically correct.
- Admission is claim-level. Critical DDR components must be verified; unrelated
  unresolved fields do not erase verified claims.
- Rule text remains a single-paper `rule_candidate` after admission.

