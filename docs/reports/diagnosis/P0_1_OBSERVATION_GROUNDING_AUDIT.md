# P0-1 Observation Grounding Pre-implementation Audit

Date: 2026-08-12

## Scope

This audit covers the existing Observation/Experiment/Diagnosis/Evidence/API/frontend path before implementing P0-1. It does not authorize P0-2 evaluator or P0-3 validation-plan work.

## Current flow

```text
Request text + client data-sufficiency booleans
  -> DiagnosisSession
  -> HypothesisVersion / HypothesisAssessment
  -> EvidenceItem / EvidenceLink
  -> DiagnosisDecision
  -> approval / design handoff
```

The repository can persist real observations, but the diagnosis gate does not yet make those persisted records authoritative.

## Target flow

```text
DataAsset
  -> QC-passed Observation (measured fact)
  -> EngineeringProblem (reproducible descriptive comparison)
  -> Hypothesis (causal interpretation)
  -> Evidence
  -> DiagnosisDecision
```

## Reusable assets

### Observation and experiment data

- `harness/experiments/models.py::Observation` is already the canonical measurement model. It includes project, subject design/construct or biological-context reference, condition, timepoint, metric, numeric value, unit, QC, uncertainty, replicates, modality, assay and data-asset references.
- `DataAsset` provides raw-file provenance, checksum, parser identity, assay, QC and source type.
- `harness/diagnosis/normalizer.py` already normalizes raw observation input and commits derived observations; it should remain the ingestion path.
- Observation values are immutable except QC disposition, which is scientifically correct.

### Diagnosis and evidence

- `DiagnosisSession` already stores `project_id`, `biological_system` and `baseline_observation_ids`.
- Hypotheses, evidence relations, model runs, decisions and state transitions are already separate, auditable records.
- `DiagnosisDecision` is insert-only apart from governed approval/handoff fields.
- The shared project event ledger can record grounding and engineering-problem creation without introducing a second history store.

### API and frontend

- `harness/api/diagnosis.py` exposes sessions, hypotheses, evidence, decisions, approval and state actions.
- `frontend/src/api/diagnosis.ts` centralizes diagnosis DTO mapping.
- `DiagnosisSessionDetailPage.tsx` already renders operational diagnosis facts and is the smallest appropriate location for observation/problem/grounding display.
- Existing common status/provenance components can be reused.

## Gaps

1. There is no first-class `EngineeringProblem`; the system cannot persist a descriptive observed-vs-baseline delta separately from a causal hypothesis.
2. Existing data sufficiency can be driven by frontend/request booleans rather than repository observations.
3. There is no single repository-backed check for project ownership, subject/context, metric/value/unit, provenance, QC and comparison availability.
4. Actionable decisions can be created without proving observation grounding.
5. Decision approval and design handoff do not independently re-check persisted grounding.
6. The frontend does not show measured observation -> engineering problem -> hypothesis as distinct layers.
7. A causal phrase entered as observation text is not a persisted measurement, but the UI can make such text appear observation-like.

## Scientific boundary

- Observation: measured value only. “Tryptophan titer is 8 g/L” is allowed.
- Engineering problem: descriptive comparison only. “Titer is 33% below matched baseline” is allowed.
- Hypothesis: causal interpretation. “Precursor supply may limit flux” belongs here.
- Literature rules and expert priors are evidence/knowledge, never project observations.
- The MVP will reject causal language in `EngineeringProblem.abnormality_statement`; it will not attempt unreliable automatic linguistic splitting.

## Implementation decision

- Reuse `Observation`; do not create another observation table.
- Add one minimal `EngineeringProblem` table and deterministic derivation service.
- Add `ObservationGroundingGate`, whose result is computed exclusively from persisted `Observation`, `DataAsset`, `BiologicalContext`, session and project-objective records.
- Require the gate for actionable decision creation, decision approval, handoff-ready transition and final handoff.
- Preserve hypothesis generation without grounding, but it remains non-actionable.
- Add read/derive API endpoints and minimal detail-page rendering.
- Preserve legacy records as readable. New approval/handoff attempts fail closed until grounded; no synthetic backfill is permitted.

## Audit verdict

The repository has strong reusable measurement and provenance foundations, but the operational diagnosis chain is currently **PARTIAL** because persisted observations do not govern actionability. P0-1 can be implemented additively without changing P0-2 or P0-3.
