# Skill08 Biological Coreference Design

## Object model

```text
BiologicalEntity
  id / canonical_name / aliases / kind
  derived_from
  modifications[] = {gene, operation}
  source_units[]
```

Supported controlled operations are deletion, overexpression, point mutation,
promoter replacement, complementation and plasmid introduction. Synonyms are
normalized only for comparison; source wording is preserved.

## Resolution policy

1. Extract explicit strain and genetic-operation mentions from the current
   document.
2. Record named strains and explicitly described mutant/complementation
   relations; parent assignment requires one non-generic strain candidate.
3. Resolve `this mutant` and `the engineered/recombinant/deletion/complemented
   strain` only to a unique compatible entity in the same evidence unit or the
   immediately preceding unit in the same section.
4. Multiple compatible antecedents or absent explicit lineage returns
   `unresolved`.
5. E2 reports paper, experiment, biological object and intervention dimensions
   separately. E3 may use resolved canonical aliases but cannot override an E2
   conflict.
