# Experiment-Native Ontology Design

`ExperimentInstance` is canonical and owns biological objects, interventions,
conditions, controls, measurements, outcomes and evidence links. Biological
roles include organism, strain, parent/derived/engineered strain and plasmid
host. Interventions cover deletion/knockout, overexpression, mutation, promoter
replacement, plasmid introduction and ALE. Conditions and measurements retain
source wording while allowing controlled types.

The native schema is strict about identity, collection shape, evidence links and
review state. `fields` is explicitly tagged as a derived projection.
