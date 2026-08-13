# Skill07 Architecture Audit

审计日期：2026-08-12  
范围：`harness/paper_extraction` 的 System Prompt、Skill07 规则、runtime schema、`opus_extractor.py`、cache/provenance，以及 Skill07→Skill08 handoff。

## 1. Current Data Flow

```text
Skill06 clean_document_artifact
  -> opus_extractor._source_document
  -> InputDocumentGate
  -> content-addressed cache lookup
  -> _build_prompt
       system prompt
       full SKILL.md
       runtime JSON Schema
       full clean document
  -> Poe Code CLI / configured model
  -> safe structural normalization
  -> JSON Schema validation
  -> field semantic checks
  -> candidate evidence-anchor resolution
  -> article-type, experiment-graph, DDR and coverage checks
  -> optional full-context repair
  -> cache + provenance
  -> Skill08 independent evidence binding
```

Runtime entrypoints:

- `harness/paper_extraction/service.py` injects `make_executor(EXTRACTION_MODEL)` for Skill07.
- `harness/paper_extraction/opus_extractor.py` owns prompt construction, schema loading, deterministic validation, cache identity and provenance.
- `vendor/paper_experimental_design_extraction/workflow/engine.py` passes each Skill07 output and the same clean document to Skill08.
- Skill08 independently resolves and quote-checks evidence; Skill07 is only a candidate-anchor producer.

## 2. Current Ontology

The scientific ontology currently exists, but is distributed across prose and code:

- Biological objects: SKILL §3 describes organism/strain/host/construct identities, normalization and lineage.
- Experiments: SKILL §4 makes experiment instances canonical and the 16 document-level fields a compatibility projection.
- Claims: System Prompt and SKILL distinguish observations, author interpretation, cited-study claims and model inference, but there is no single normative vocabulary.
- Evidence: SKILL clearly says Skill07 anchors are candidates and Skill08 verifies them; the runtime field name remains generic `evidence_ids`.
- Epistemic state: schema supports `reported|inferred|unknown`; semantic non-applicability is encoded through `unknown` plus notes / `extraction_method=not_applicable`.
- DDR: decision gates and annotations are described in SKILL/System Prompt, while allowed rule reasons and enforcement are partly hard-coded in Python.
- Rule candidates: prose says `generalizable_rule` is a bounded single-paper candidate, not an approved rule.

## 3. Contract Drift

### 3.1 Epistemic/applicability conflation

`status` carries knowledge state, while `not_applicable` appears in `extraction_method`. This permits an unknown field and a semantically inapplicable field to look identical downstream. There is no machine field for `applicable|not_applicable|uncertain`.

### 3.2 Evidence-role ambiguity

The schema field `evidence_ids` does not state whether an ID is a Skill07 candidate or Skill08-verified evidence. Python resolves anchors but cannot prevent a model-generated object from describing them as verified elsewhere in a permissive nested object.

### 3.3 DDR vocabulary drift

`opus_extractor._ddr_checks` hard-codes a small rule-reason set. `ddr_converter.py` has another hard-coded legacy Chinese vocabulary. SKILL describes additional distinctions such as rationale not reported. There is no versioned normative source.

### 3.4 Rule-candidate validation gap

The current validator checks an allowed reason and tested/validated scope. It does not require all of:

- `decision_type == engineering_decision`;
- tested scope;
- excluded scope;
- a declared single-paper candidate role.

### 3.5 Schema carrying semantic work

The JSON Schema correctly enforces shape, types and required fields, but semantic invariants are split between schema, prompt prose and Python. The output does not identify which semantic contract produced it.

### 3.6 Misleading self-check score

`_self_check` emits `score: 1.0|0.0`. This is a validator pass fraction presented in a shape that can be mistaken for scientific quality/confidence.

### 3.7 Incomplete provenance/cache identity

Provenance records skill/system/schema/validator versions, but not a semantic-contract version or validation-rules version. Cache identity likewise cannot invalidate on ontology/rule changes alone.

### 3.8 Prompt injection cost

Every Skill07 call injects the complete SKILL, schema and document. The Skill contains core, DDR, parameter and evidence rules that are scientifically cross-dependent. Splitting them without a routing-quality benchmark could omit rules needed by an unexpected paper section or experiment type.

## 4. Planned Upgrade

1. Add `contracts/skill07_semantic_contract.md` as the normative scientific world model, separate from API schema.
2. Add versioned `contracts/skill07_validation_rules.yaml` as the single machine-readable source for epistemic/applicability, evidence role, reason-nature and rule-candidate invariants.
3. Add a small contract loader with fail-closed validation and hashes.
4. Extend runtime schema additively with:
   - top-level `contract_version`;
   - per-field `applicability_status`;
   - `field_metadata.evidence_role`, constrained to `candidate` in Skill07.
5. Preserve old successful data through deterministic additive normalization. Ambiguous legacy `unknown` values default to applicability `uncertain`; only explicit notes may migrate to `not_applicable`.
6. Refactor validator checks to read rule values from YAML; add excluded-scope and verified-evidence prohibitions.
7. Replace self-check score with required/passed/failed counts and explicit critical failures.
8. Add semantic-contract/rules versions and hashes to provenance and cache identity.
9. Do not split prompt injection in this change. Record it as benchmark-gated because conditional rule loading can reduce scientific coverage.
10. Add focused tests, then run the existing 116 paper-extraction tests plus the expanded suite.

## 5. Compatibility Policy

- Existing field meanings and the `evidence_ids` field name remain intact.
- New fields are additive and deterministically populated for legacy model/cache output.
- Skill07 remains unable to assert Skill08 verification.
- No existing extraction is automatically promoted to an approved rule.
- Cache invalidation is intentional when semantic contract or rules change.

