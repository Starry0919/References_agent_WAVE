# Skill07 Experiment-Native Representation Contract v1

`experiment_instances` is canonical scientific output. `fields` is a derived
document projection and MUST declare `projection_metadata.derived_projection =
true`. `experimental_design_object` is retained only for legacy consumers.

Every atomic claim binds exactly one `experiment_id`, one scalar subject, one
predicate and one scalar object. Optional numeric value/unit refine that single
relation. Sentence splitting is not an atomicity rule. A claim has at least one
candidate evidence slot, even when unresolved; Skill07 never marks evidence
verified.

Legacy compatibility conversion is structural only. Generated native records
MUST carry `migration_generated=true` and `review_required=true`. They cannot be
admitted as verified knowledge without Skill08 verification and normal admission
gates.
