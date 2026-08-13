# Skill08 biological-attribution contract v1

Skill08 verification MUST keep biological attribution separate from lexical
support.  Each assessed claim exposes `paper_match`, `experiment_match`,
`biological_object_match`, `intervention_match`, `control_relationship_match`,
`confidence`, and `status`.

Statuses are `passed`, `failed`, or `unresolved`. A failed biological dimension
MUST prevent `verified`. An unresolved dimension MUST not be promoted by lexical
similarity. Coreference is limited to the current or immediately preceding unit
inside the same section and requires one compatible antecedent. Ambiguity stays
`unresolved`; it is never guessed.

The output MUST retain the biological object graph and evidence chain so that a
reviewer can reconstruct the object, intervention, control, experiment, and
source used for the decision. Existing source locator and provenance fields are
not weakened by this additive contract.
