# Skill07 Scientific Semantic Contract

Contract version: `skill07_semantic_contract_v1`

This contract defines the scientific meaning of Skill07 output. It is not an
API or JSON schema. The runtime schema controls transport shape and types;
`skill07_validation_rules.yaml` controls deterministic cross-field rules.

## 1. Biological Object Ontology

A `BiologicalObject` is an identity-bearing entity used by or produced in an
experiment. Supported object kinds are:

- `organism`: a taxonomic organism identity;
- `strain`: a named or otherwise identifiable biological strain;
- `host`: the object receiving an intervention or construct;
- `parent_strain`: the lineage parent from which another strain was derived;
- `engineered_strain`: a strain created by a reported intervention;
- `plasmid`: an extrachromosomal DNA object;
- `construct`: an engineered genetic or molecular construct;
- `sample`: a physical experimental sample;
- `library`: a set of related constructs, strains, variants or samples.

Every identified object should preserve, where available:

- `raw_identity`: the source wording;
- `normalized_identity`: a normalization that never overwrites the raw value;
- `normalization_basis`: the source or deterministic rule supporting normalization;
- `identity_confidence`: confidence in text-to-identity extraction, not biological truth;
- `lineage_relationship`: parent/derived/member/contains relationships scoped to the paper.

Species-only evidence must not be promoted to a strain. Independent and
combinatorial constructs must not be merged without an explicit lineage or
membership relation in the source.

## 2. Experiment Ontology

`ExperimentInstance` is canonical truth. Document-level fields are only a
compatibility projection and must not merge incompatible experiments.

```text
ExperimentInstance
  ├── Object
  ├── Intervention
  ├── Condition
  ├── Control
  ├── Replicate
  ├── Readout
  ├── Analysis
  └── Outcome
```

- `Object` identifies the host, strain, construct, sample or library.
- `Intervention` is an action applied to an object.
- `Condition` is a scoped environment or process parameter.
- `Control` is a comparator belonging to the same experiment instance.
- `Replicate` records biological/technical/independent repetition without inferring one from plotted points.
- `Readout` is the measured variable and its assay/instrument context.
- `Analysis` is the reported computational or statistical treatment.
- `Outcome` is the observation produced by the experiment, not an inferred motivation.

Planned, implemented and verified values are distinct value roles. A later
outcome must never be used to fabricate an earlier trigger.

## 3. Claim Ontology

Claim types are orthogonal to source ownership:

- `direct_observation`: directly measured or explicitly observed in the source;
- `author_interpretation`: the authors' interpretation of observations;
- `paper_claim`: an assertion made by the paper without direct observation at the cited location;
- `model_inference`: a bounded inference produced by Skill07 from current-document evidence;
- `causally_validated`: a causal claim supported by an intervention and an appropriate comparison in the paper.

Temporal order, correlation, enrichment, prediction or expression change alone
does not establish `causally_validated`.

## 4. Evidence Ontology

Skill07 produces only a `candidate_evidence_anchor`: a source locator and quote
proposed as support for a field, claim or decision candidate. Skill08 rereads
the document and may produce `verified_evidence` after existence, attribution
and semantic-support checks.

Skill07 must never label its evidence as verified, approved or independently
validated. The legacy field name `evidence_ids` is retained for compatibility;
its Skill07 role is explicitly `candidate` in field metadata.

## 5. Epistemic and Applicability Ontologies

Knowledge state and applicability are separate dimensions.

`epistemic_status`:

- `reported`: the value is stated by the available document and has candidate evidence;
- `inferred`: the value is boundedly inferred from current-document evidence, with method and rationale;
- `unknown`: the applicable or possibly applicable value cannot be established.

`applicability_status`:

- `applicable`: the field applies to the experiment/document instance;
- `not_applicable`: the field does not semantically apply;
- `uncertain`: available evidence cannot establish applicability.

`not_applicable` is not a knowledge state. For compatibility, a not-applicable
field keeps epistemic status `unknown`, null value and no supporting evidence,
while `applicability_status` carries the actual meaning.

## 6. Rule Candidate Ontology

`generalizable_rule` is never an approved rule. In Skill07 it is a
`single_paper_rule_candidate` and may be non-empty only for a current-study
engineering decision supported by an allowed reason nature.

Every non-empty candidate must have:

- `scope`: the bounded applicability statement represented by the candidate text;
- `evidence_basis`: candidate evidence and reason nature supporting it;
- `tested_conditions` / `tested_scope`: conditions actually tested in the paper;
- `excluded_conditions` / `excluded_scope`: explicit limits and conditions not established.

Cross-paper support, promotion to a reusable rule and approval belong to later
governance stages and human review.

## 7. Contract Boundaries

- Runtime JSON Schema: fields, required keys, JSON types and API compatibility.
- Semantic Contract: scientific entities, meanings and boundaries.
- Validation Rules: deterministic cross-field invariants and controlled vocabularies.
- Skill08: independent evidence verification.
- Skill09+: quality scoring, transfer, planning, governance and promotion.

