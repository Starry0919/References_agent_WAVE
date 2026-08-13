# Diagnosis / Engineering Design Workbench Implementation Report

Date: 2026-08-12

## Outcome

The two project base routes now act as a connected scientific engineering workspace instead of collection/creation screens:

- Diagnosis opens with real project context, ranked engineering problems, conservative diagnostic coverage, competing hypotheses, evidence for/against, epistemic labels, model capability versus run separation, unresolved state and an explicit handoff to design.
- Engineering Design opens with the immutable diagnosis-to-intervention trace, real strategy/candidate space, a decomposed comparison matrix, M11 gate states, rejected/why-not explanations, selected-stack governance, dependencies/conflicts and experimental validation readiness.

The existing operational detail routes remain available for state-changing actions, audit history and deep records.

## Backend changes

- Extended the existing candidate serializer with fields already persisted on `CandidateDesign`: causal chain, evidence, process modifications, regulatory architecture, interaction/epistasis assumptions, counterfactuals, uncertainty/conflicts, trade-offs, buildability, fallback, safety and diagnosis version.
- Added a read-only project-level evaluation listing endpoint. An unevaluated portfolio now returns `{evaluations: {}}` with HTTP 200 instead of requiring expected candidate-level 404 probes.
- Added focused API tests for both behaviors. No database migration or new scientific ontology was introduced.

## Scientific truth preserved

- Substrate is displayed as not specified.
- All three target-project evidence links are shown as soft rule-transfer evidence (low quality, indirect), not hard facts.
- No theoretical yield, flux, growth effect or predicted benefit number is displayed because the project has no model run.
- Absence of contradictory evidence is worded as none recorded, not proof that counterevidence does not exist.
- Candidate proposals are not displayed as selected, recommended, approved or validated because no evaluator result or human selection exists.
- Process design, evaluator gates and build/test package are explicitly pending/not evaluated.

## Files changed by this task

- `frontend/src/pages/diagnosis/DiagnosisWorkbenchPage.tsx`
- `frontend/src/pages/design/DesignWorkbenchPage.tsx`
- `frontend/src/api/engineeringDesign.ts`
- `harness/api/engineering_design.py`
- `tests/engineering_design/test_workbench_read_model_api.py`
- Required audit, architecture, plan, implementation and validation reports
- Browser screenshots under `artifacts/`

## Working-tree note

The repository began with a large pre-existing layout mismatch: many historical paths appeared deleted and the current application tree appeared untracked. Existing `.gitignore` and `README.md` changes predated this task. No attempt was made to reset, delete or normalize those unrelated changes.
