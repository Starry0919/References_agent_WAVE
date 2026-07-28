# Backend Mapping Matrix — Page 2, all five stages

Referenced by `frontend/src/api/orchestrator.ts` (comment pointed here before this file existed).
Now covers all five Workspace stages.

## Diagnose

| UI need | Real endpoint | Real schema (table) | Availability | Adapter | Unresolved issue | Demo data used? |
| --- | --- | --- | --- | --- | --- | --- |
| Session summary | `GET /api/diagnosis/sessions/{id}` | `diag_sessions` | available | `getDiagnosisSession` | `objective_id` column exists on the model but is not selected by the handler | No |
| Hypothesis list w/ coverage & contradictions | `GET /api/diagnosis/sessions/{id}/hypotheses` | `diag_hypothesis_assessments` join `hypothesis_versions` | available | `getHypotheses` (extended this session to map `explanatory_coverage`/`contradictions`, previously dropped) | `evidence_quality`, `robustness`, `testability`, `condition_match`, `remaining_uncertainty`, `ranking_rank`, `pareto_state`, `rationale_references` exist on `diag_hypothesis_assessments` but are not in this response | No |
| Evidence for a hypothesis | `GET /api/diagnosis/sessions/{id}/evidence` | `diag_evidence_links` | available | `getEvidenceLinks` + `evidenceLinkToSummary` (new) | Returns `evidence_link_id`/`hypothesis_version_id`/`evidence_item_id`/`relation`/`claim` only; no route resolves `evidence_item_id` to the full `diag_evidence_items` row (title/quality/source/DOI), so the Evidence Drawer shows `kind: unknown` honestly rather than a fabricated title | No |
| Diagnostic alternatives / next verification action | `GET /api/diagnosis/sessions/{id}/tests` | `diag_diagnostic_tests` + `diag_execution_plans` | available | `getDiagnosticTests` (new) | none found | No |
| Diagnosis decision (gated handoff) | `GET /api/diagnosis/sessions/{id}/decisions` | `diag_decisions` | available | `getDiagnosisDecisions` (new) | none found | No |
| Human approval of a decision | `POST /api/diagnosis/decisions/{decision_id}/approve` | `diag_decisions.handoff_status` | available | `approveDiagnosisDecision` (new) | Boolean approve/reject only, no revision-requested outcome (see ADR-001) | No |
| Audit trail | `GET /api/diagnosis/sessions/{id}/audit-trail` | `diag_transitions` | available | `getDiagnosisAuditTrail` (new) | none found | No |
| Model capability roster | `GET /api/diagnosis/model-capabilities` | n/a (live adapter probe) | available | `getModelCapabilities` (pre-existing, unused by any current stage UI — noted, not wired this session, low priority since `CapabilityState` already surfaces the static roster) | none found | No |

## Design

| UI need | Real endpoint | Availability | Adapter | Unresolved issue |
| --- | --- | --- | --- | --- |
| Project/objective context | `GET /api/engineering-design/projects/{id}` | available | `getDesignProject` (extended) | none found |
| Alternative strategies incl. rejected | `GET /api/engineering-design/projects/{id}/strategies` | available | `getStrategies` (new) | none found |
| Candidate list | `GET /api/engineering-design/projects/{id}/candidates` | available | `getCandidates` (extended) | none found |
| Per-candidate evaluation (comparison) | `GET /api/engineering-design/candidates/{id}/evaluation` | available, 404 if not yet evaluated | `getCandidateEvaluation` (new) | none found |
| Human approval | `POST /api/engineering-design/candidates/{id}/human-decision` | available | `recordCandidateHumanDecision` (new) | `decision` field only confirmed to accept `approved`/`rejected` (code comment) |
| Build/test package content | none | absent | n/a | `CandidateDesign.build_test_package_id` is a real reference; no `GET` route resolves it to `construction_concept`/`controls`/`replication_plan`/etc. Rendered as reference-only |
| Audit trail | `GET /api/engineering-design/projects/{id}/audit-trail` | available | `getDesignAuditTrail` (new) | none found |

## Simulate

| UI need | Real endpoint | Availability | Adapter | Unresolved issue |
| --- | --- | --- | --- | --- |
| Model/tool registry | `GET /api/virtual-cell/models` | available | `listModels` (extended) | none found |
| Simulation case status | `GET /api/virtual-cell/simulation-cases/{id}` | available | `getSimulationCase` (extended) | none found |
| Case transitions (provenance) | `GET /api/virtual-cell/simulation-cases/{id}/transitions` | available | `getCaseTransitions` (new) | none found |
| Validation plan (falsification/baseline) | `GET /api/virtual-cell/simulation-cases/{id}/validation-plan` | available | `getValidationPlan` (new) | none found |
| Run-level inputs/outputs/uncertainty | `GET /api/virtual-cell/simulations/{run_id}` exists but | **absent from this UI's reach** | n/a | No route lists `SimulationRun`s for a case; a run id is only ever returned from `POST /simulations` (a mutation this read-only pass does not trigger). Rendered as an explicit "Unavailable via current API" panel, not guessed |

## Critique

| UI need | Real endpoint | Availability | Adapter | Unresolved issue |
| --- | --- | --- | --- | --- |
| Case summary | `GET /api/scientific-evaluation/evaluations/{id}` | available | `getEvaluationCase` (extended) | none found |
| Deterministic (rule-based) checks | `GET .../deterministic-results` | available | `getDeterministicResults` (new) | none found |
| Evidence gaps/contradictions per claim | `GET .../evidence-assessments` | available | `getEvidenceAssessments` (new) | none found |
| Reviews + findings | `GET .../reviews` | available | `getReviewsAndFindings` (extended from `getFindings`) | none found |
| Cross-candidate Pareto comparison | `GET .../candidate-comparison` | available | `getCandidateComparison` (new) | none found |
| Meta-review (resolution/governance) | `GET .../meta-review` | available, 404 if none yet | `getMetaReview` (new) | none found |
| Revision history | `GET .../version-history` | available | `getVersionHistory` (new) | none found |
| Human gate decision | `POST .../human-decision` | available | `submitEvaluationHumanDecision` (new) | Accepted `decision` vocabulary beyond `approved`/`rejected` (e.g. is there a revision-request value?) was not confirmed by reading `harness/scientific_evaluation/human_gate.py` this session — kept conservative, only approve/reject offered |
| Audit trail | `GET .../audit-trail` | available | `getEvaluationAuditTrail` (new) | none found |

## Build / Test Plan

| UI need | Real endpoint | Availability | Adapter | Unresolved issue |
| --- | --- | --- | --- | --- |
| Intervention/genotype summary | composed from `GET /api/engineering-design/.../candidates` (approved candidate) | available (composition, not a dedicated endpoint) | reuses `getCandidates` | The run object only stores `design_version_ref`, which no endpoint resolves back to a `CandidateDesign` - this session instead finds the approved candidate from the design project's candidate list, which is real but an approximation, not a guaranteed 1:1 link. Documented as such |
| Experiment plan (dependencies) | `GET /api/experiments/plans/{id}` | available | `getExperimentPlan` (new adapter file `experiments.ts`) | `controls`/`factors`/`response_variables`/`acceptance_criteria`/`hypotheses_tested`/`protocol_ref_id` are accepted by `POST /plans` but not returned by this `GET` |
| Execution status | `GET /api/experiments/runs/{id}` | available | `getExperimentRun` (new) | none found |
| Readouts/measurements | `GET /api/experiments/runs/{id}/observations` | available | `getObservations` (new) | none found |
| Human approval | `POST /api/orchestrator/runs/{id}/human-gate-decision` | available | pre-existing, unchanged | none found (already real prior to this session) |
| Build/test package content | see Design section above | absent | n/a | same reference-only gap |

## Session-level honesty notes
- No fixture/mock data was introduced anywhere in this session's changes across either pass.
  Every rendered field traces to a real HTTP call against a real, already-implemented FastAPI
  route.
- Fields the backend does not return are rendered as an explicit "Unavailable via current API"
  string in the UI rather than omitted silently or guessed - see each stage file for the exact
  wording and the endpoint named as the reason.
- Neither pass started the FastAPI backend against the shared `project_ledger.db` (it has
  concurrent, uncommitted, same-day edits from work not attributable to this session - starting
  a server that writes to that file risked colliding with it, and a second concurrent session was
  independently confirmed to be active in `frontend/` during the second pass). Verification was
  therefore static (typecheck/lint/build/test/dev-server-transform), not a live end-to-end data
  render. See the completion report's `verification` section for exactly what was and wasn't run.
