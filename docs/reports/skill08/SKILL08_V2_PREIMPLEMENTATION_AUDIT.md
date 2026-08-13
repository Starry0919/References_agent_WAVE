# Skill08 V2 Preimplementation Audit

Date: 2026-08-12

## Baseline

- Paper-extraction regression: `123 passed, 1 warning`.
- Skill07 emits a result envelope containing status, output, self-check,
  provenance, and `eligible_for_evidence_verification`.
- Workflow context retained only filtered outputs and later paired them with
  clean documents using positional `zip`.
- Skill08 repaired malformed Skill07 fields and overwrote values/statuses when
  evidence was not found.
- Its support check was substring matching; there was no experiment/source
  attribution verdict.
- DDR persistence consumed `experimental_designs` (Skill07 output) directly.

## P0 paths confirmed

1. Filtering out a failed paper's `None` output shifted later outputs and could
   pair paper B with paper A's document.
2. Skill07 `eligible=false` was not present in the Skill08 request.
3. `ensure_task_saved_as_evidence` persisted Skill07 candidates without a
   Skill08 admission decision.
4. Rule distillation accepted any stored DDR with an eligible-looking rule.

## Required implementation boundary

- Stable handoff identity and hashes must be built before Skill08.
- Invalid/legacy handoffs fail closed; they are not repaired.
- Skill07 candidates remain byte-for-byte immutable within Skill08 output.
- Verification is a separate verdict with existence, attribution and semantic
  dimensions.
- Persistent DDR/rule paths require a deterministic admission record.

