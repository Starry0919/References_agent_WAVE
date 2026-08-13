# Skill07 Experiment-Native V3 design

`ExperimentInstance` is the canonical unit. It carries paper/document/version identity, scope and parent relations, biological context, interventions, conditions, controls, measurements, outcomes, rationale, interpretation, limitations, evidence links, provenance, extraction state and uncertainty. Unknown values remain unresolved—not negative biological assertions.

IDs are deterministic hashes of document identity and source-local anchors/identity; model prose and output order are excluded. If a legacy artifact lacks document identity or anchors, migration preserves its raw payload, marks identity unresolved and requires review. Papers may contain multiple experiments, controls, time points, doses and related subexperiments without cross-binding.

V2 fields remain available only as `projection_metadata.derived_projection=true`; this projection is deterministic and explicitly lossy.
