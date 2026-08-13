# Paper Extraction E2E Error Propagation Report

The final run attributes non-passing checks in first-failure order:

- `EVIDENCE_ANCHOR`: legacy locator missing or not resolvable in its document.
- `SKILL08_E2`: anchor exists but biological object/intervention attribution is
  failed or unresolved.
- `SKILL08_E3`: E1/E2 survive but conservative semantic entailment does not.
- `UNKNOWN/REVIEW`: candidate has no assessable value.

Counts are emitted in `e2e_results.json`. No error is attributed to DDR or
admission because the required current-contract artifacts were absent; assigning
those failures downstream would obscure the actual measurement boundary.

The dominant measurable loss is E3. The likely upstream cause is document-level
field flattening: one complex JSON/list value is compared with multiple source
paragraphs as one claim. Human ExperimentInstance truth is required to separate
Skill07 extraction loss from verification conservatism.
