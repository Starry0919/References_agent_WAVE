# Skill08 Evidence Contract

Version: `skill08_evidence_contract_v2`

Skill08 independently verifies immutable Skill07 candidates. It may append
evidence records, verification verdicts, reasons, conflicts and provenance. It
must not change candidate values, epistemic/applicability states, inference,
experiment bindings, DDR annotations, or rule candidates.

`verified` means existence, attribution and conservative semantic support all
pass. Other verdicts are `unsupported`, `unresolved`, and `conflicted`.
Uncertainty is `unresolved`; lexical similarity alone is never verification.

