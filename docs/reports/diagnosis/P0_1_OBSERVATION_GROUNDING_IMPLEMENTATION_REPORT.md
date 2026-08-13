# P0-1 Observation Grounding MVP Implementation Report

Date: 2026-08-12

## Outcome

P0-1 MVP is implemented. An actionable diagnosis now requires persisted, project-owned, QC-passed observations with resolvable subject/context, measurement/value/unit, data provenance, a persisted baseline comparison, and a reproducible descriptive `EngineeringProblem`.

No P0-2 evaluator or P0-3 ValidationPlan behavior was implemented.

## Changed files

### Backend

- `harness/diagnosis/models.py` — added immutable `EngineeringProblem` domain model.
- `harness/diagnosis/grounding.py` — added deterministic comparison service and repository-backed `ObservationGroundingGate`.
- `harness/diagnosis/decision_service.py` — blocks actionable decision creation and approval when grounding fails.
- `harness/diagnosis/loop.py` — blocks handoff-ready/final-handoff transitions when grounding fails.
- `harness/diagnosis/handoff.py` — optional final repository-backed defense-in-depth check.
- `harness/api/diagnosis.py` — added observation IDs on session creation, grounding report, engineering-problem derive/list endpoints.
- `harness/bootstrap.py` — added idempotent `0016_observation_grounding_schema` migration.

### Frontend

- `frontend/src/api/diagnosis.ts` — added grounding/problem DTOs and API adapters.
- `frontend/src/pages/diagnosis/DiagnosisSessionDetailPage.tsx` — minimal grounding status, blockers and measured/problem/hypothesis separation.

### Tests and reports

- `tests/diagnosis/test_observation_grounding.py`
- `tests/diagnosis/test_decision_and_handoff.py`
- `tests/diagnosis/test_required_assertions.py`
- `frontend/src/api/diagnosisGrounding.test.ts`
- `P0_1_OBSERVATION_GROUNDING_AUDIT.md`
- this report.

## Data-flow change

Before:

```text
request text / client sufficiency flags -> hypothesis -> evidence -> actionable decision
```

After:

```text
DataAsset -> QC-passed Observation
          -> matched baseline comparison
          -> EngineeringProblem (descriptive delta)
          -> hypothesis (causal interpretation)
          -> evidence -> actionable decision
```

The gate queries the repository. Frontend booleans, LLM prose, rules and literature cannot satisfy it.

## New capabilities

- Reproducible observed-vs-baseline delta with exact Observation lineage.
- Causal-language rejection for abnormality statements; causal claims must remain hypotheses.
- Structured `grounded` / `data_required` result with blocking reasons and policy version.
- Defense-in-depth blocking at actionable decision creation, approval, handoff-ready and handoff.
- Legacy ungrounded diagnoses remain readable but cannot be newly approved/handed off.
- Minimal UI showing measured fact, descriptive engineering problem and causal hypothesis as different layers.

## Verification

- Backend diagnosis suite: **84 passed**, 3 third-party deprecation warnings.
- New P0-1 backend cases: no observation, valid measurement/baseline, causal contamination, missing provenance, grounded approval.
- Frontend diagnosis adapter/grounding tests: **6 passed**.
- Frontend production build: **passed** (`tsc --noEmit` and Vite build).
- Full frontend suite: **45 passed, 1 failed**. The remaining failure is the pre-existing/unrelated `CommandCenterPage.test.tsx` expectation for asynchronous idea text `Overexpress feedback-resistant trpE`; the P0-1 targeted suites and production build pass.
- Build warning: existing bundle chunk exceeds 500 kB; unrelated to P0-1.

## Current limitations

- MVP comparison requires identical metric, unit and condition dictionaries; no unit-conversion or condition-equivalence ontology is introduced.
- MVP supports persisted matched-baseline comparison. A project-objective numeric target is not yet accepted as a substitute.
- Causal contamination detection is a conservative English phrase deny-list, not a general scientific NLP classifier.
- The session creation API can link existing Observation IDs; it does not fabricate or directly ingest experimental measurements.
- The UI displays grounding and problems but does not add a large observation-ingestion workflow.
- Final standalone handoff defense requires callers to pass a database session; service/loop/approval paths already enforce repository grounding.

## Alignment with the teacher design

The implemented ordering is now:

```text
Observe -> describe the engineering problem -> understand through hypotheses/evidence -> design
```

This is materially closer to the teacher's Observe/Understand/Design/Evaluate/Build/Test/Learn loop and prevents knowledge transfer or expert rules from masquerading as project facts.

## Final acceptance

- Scientific: Observation -> Engineering Problem -> Hypothesis separation is implemented and tested; knowledge is not promoted to fact.
- Engineering: ungrounded actionable decisions, approval and governed handoff are blocked; schema is additive and old records remain readable.
- Teacher objective: the platform now starts diagnosis from persisted observations, but later Evaluate/Build/Test/Learn gaps remain outside this phase.

Overall status: **PARTIAL**. P0-1 MVP is implemented, while the complete teacher loop still requires separately authorized P0-2 and P0-3 work.
