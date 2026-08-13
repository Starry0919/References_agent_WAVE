# Paper Extraction E2E Benchmark V1 Design

## Governance and split

- Safety: immutable existing 13-case Skill08 benchmark.
- Development: 10 real papers selected by stable artifact-path ordering.
- Holdout: 5 disjoint real papers, evaluated only by the final evaluator run.
- Annotation tier: Silver (`AI_ASSISTED`, not human reviewed, adjudication
  pending). No Gold file is created.

Each paper record carries document identity/hash, available modalities, parser
limitations, all 16 Skill07 projection fields, candidate values, evidence
anchors, source attribution, E1/E2/E3 results, criticality, DDR/admission
adjudication limitations, provenance and runtime.

## Metrics and limits

E1 measures anchor resolvability. E2 uses the production biological object and
intervention resolver. E3 uses production conservative semantic support.
`supported_claim_precision_silver` is agreement with these deterministic checks,
not human scientific precision. Experiment recall and DDR precision/recall are
reported as null because no independent ExperimentInstance/decision Gold exists.

The benchmark runner is deterministic, performs no LLM or network calls, and
validates real source paths. Its output is reproducible but cannot substitute for
human adjudication.
