# Skill08 Evidence Verification V2 Implementation Report

Date: 2026-08-12  
Final status: **PARTIAL**

## Delivered

### Contracts and schemas

- `contracts/skill07_skill08_handoff_contract.md`
- `contracts/skill07_skill08_handoff_validation_rules.yaml`
- `schemas/skill07_skill08_handoff.schema.json`
- `contracts/skill08_evidence_contract.md`
- `contracts/skill08_validation_rules.yaml`
- `schemas/skill08_verification_output.schema.json`

Versions:

- handoff contract/rules: `skill07_skill08_handoff_v2` / `skill07_skill08_handoff_rules_v2`
- Skill08 contract/rules/executor: `skill08_evidence_contract_v2` / `skill08_validation_rules_v2` / `skill08_verifier_v2`
- knowledge admission rules: `knowledge_admission_rules_v2`

### Production implementation

- Added `harness/paper_extraction/handoff.py`: builds and validates a formal,
  hash-bound handoff; rejects invalid status, eligibility, self-check, schema
  provenance, identity, content hash and duplicate identity.
- Replaced filtered positional Skill07→Skill08 pairing with per-item result,
  clean-document and workflow-artifact records. No positional fallback exists.
- Rebuilt Skill08 as an immutable verification engine. Candidate payload and
  DDR annotation are copied unchanged; verification is stored separately.
- Added deterministic E1 anchor integrity, E2 current-source/experiment-anchor
  attribution, and conservative E3 negation/direction/numeric/unit/condition/
  comparison/causal-strength checks.
- `verified` requires E1+E2+E3 to pass. Lexical overlap alone becomes
  `unresolved`, not verified.
- Added DDR component verification for action, trigger, rationale,
  implementation and outcome. Skill08 neither creates a DDR nor promotes a
  rule candidate.
- Added `knowledge_admission.py` with claim-level allowed/partial/blocked
  decisions and complete-provenance validation.
- DDR persistence now requires Skill08 V2 admission and persists only admitted
  fields/DDR candidates. Rule distillation ignores DDRs without admitted
  Skill08 provenance.
- Skill10/11 now consume candidates paired through Skill08 records, eliminating
  the residual downstream positional association with filtered Skill07 output.

## P0 closures

1. Paper A failure / paper B success can no longer shift B onto A's document.
2. `eligible=false`, `needs_review`, failed self-check and incomplete identity
   are rejected before verification.
3. Skill08 no longer rewrites `reported` to `unknown`, values, applicability,
   inference, experiments, DDR annotations or rule candidates.
4. `ensure_task_saved_as_evidence` no longer consumes naked Skill07 output.
5. Rule distillation requires an admitted Skill08-derived DDR.

## Verification depth

- Level 1: implemented for paragraph/figure/table/supplement resolution,
  uniqueness, current paper/document identity and artifact hash.
- Level 2: implemented for explicit source attribution and DDR experiment
  anchor membership. Background/included-study evidence fails closed.
- Conservative Level 3: implemented for explicit subjects/tokens, negation,
  direction, numeric values, units, conditions/comparators and causal strength.
  Ambiguous paraphrase/coreference returns unresolved.

## Provenance

Skill08 records paper/document identity and hash, source Skill07 artifact/hash
and contract versions, handoff versions, Skill08 artifact/contract/rules/
executor versions, verification timestamp, candidate refs and candidate/
verified evidence ids. Persisted DDRs retain Skill08/Skill07/document admission
links.

## Tests and benchmark

Before implementation:

- paper-extraction: `123 passed, 1 warning`.

After implementation:

- focused Skill08/DDR/rule tests: `46 passed` during the focused run;
- complete paper-extraction suite: `144 passed, 1 warning`;
- new tests: 21 net additional tests;
- Python `compileall`: passed;
- JSON Schema/YAML validation: passed;
- `git diff --check` for scoped files: passed;
- full repository `pytest -q`: timed out after 184 seconds; no PASS claimed.

Synthetic benchmark (6 adversarial semantic cases):

- verification precision: `1.0`;
- false-positive count: `0`;
- false-verified critical claims: `0`;
- unresolved rate: `0.1667`;
- cross-paper mismatch accepted: `0`.

## Known limitations and remaining risk

- The benchmark is intentionally synthetic and small; it is a safety fixture,
  not evidence of broad real-paper recall.
- Level 2 handles explicit metadata and experiment anchors. Complex biological
  coreference, implicit parent/engineered-strain relations, and prose-only
  control/treatment attribution conservatively remain unresolved.
- E3 is deterministic structured checking, not general NLI; complex paraphrases
  may be unresolved. This favors precision over recall by design.
- Existing historical DDR files without V2 admission remain readable but are
  excluded from new automatic rule distillation until migrated/reviewed.
- Full-repository regression did not complete within the time limit.

These limitations prevent a truthful `PASS` under the supplied standard, so the
final state is **PARTIAL**. No unresolved P0 contamination path was found in the
audited Skill07→Skill08→DDR/rule persistence chain.

