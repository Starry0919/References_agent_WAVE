# Backend Mapping Matrix — Page 3 (Knowledge & Evidence Layer / Scientific Knowledge Production)

Companion to `docs/前端精修/backend_mapping_matrix.md` (Page 2). Same format.

## Knowledge Claims (the real `KnowledgeObject` substrate)

| UI need | Real endpoint | Real schema (table) | Availability | Adapter | Unresolved issue | Demo data used? |
| --- | --- | --- | --- | --- | --- | --- |
| Discover which claims exist for a project | `GET /api/projects/{id}/timeline` (filtered client-side for `entity_type=="KnowledgeClaim"`) | `project_events` | available, indirect | `discoverProjectClaimIds` (new, `api/knowledge.ts`) | No dedicated `GET /api/learning/knowledge-claims?project_id=` list route exists; this derivation is real (reads the actual event ledger) but requires the timeline to already contain a submit event — a claim inserted directly at the DB layer with no event would be invisible to this UI (not possible via the real `submit_claim` service function, which always appends an event) | No |
| Claim detail | `GET /api/learning/knowledge-claims/{claim_id}` | `knowledge_claims` | available | `getClaim` (new) | none found | No |
| Submit a new claim (Acquire/Extract/Structure) | `POST /api/learning/knowledge-claims` | `knowledge_claims` | available | `submitClaim` (new) | Always starts at `project_candidate` server-side regardless of submitted `evidence_grade` — UI must not imply the submitter chose the starting status | No |
| Promote (Evaluate/Validate/Publish) | `POST /api/learning/knowledge-claims/{id}/promote` | `knowledge_claims.status`, `.promotion_record` | available | `promoteClaim` (new) | Rejects with 422 if `reviewer_id == created_by`, or if promoting to `lab_candidate`/`lab_approved` with <3 independent evidence groups, or with unaddressed `contradicting_experiments` and a blank reason — all three are real, tested (`tests/projects/test_knowledge_claims.py`) server rules the UI surfaces verbatim rather than re-implementing its own copy | No |
| Retract (Supersede/Retire) | `POST /api/learning/knowledge-claims/{id}/retract` | as above | available | `retractClaim` (new) | Retraction has no self-retraction guard server-side (unlike promotion) — the UI does not add a client-only restriction the backend doesn't enforce | No |
| Version history | `promotion_record` field returned by the detail route above (no separate endpoint) | as above | available | part of `getClaim`'s response | none found | No |
| Resolve claim evidence to real experiment data | `GET /api/experiments/runs/{id}`, applied to every id in `independence_groups` (flattened) | `experiment_runs` | available | reused `getExperimentRun` (`api/experiments.ts`, pre-existing from Page 2, unmodified) + `experimentIdsFromIndependenceGroups` (new) | **Read-path gap discovered this session**: `GET /knowledge-claims/{id}` (`harness/api/learning.py::get_claim`) returns only `claim_id/statement/scope/status/independence_groups/evidence_grade/promotion_record` — it does **not** serialize `project_id`, `supporting_experiments`, `contradicting_experiments`, `reviewers`, `created_by`, `created_at`, `updated_at`, or `supersedes_claim_id`, even though all exist on the `KnowledgeClaim` table. `independence_groups` (returned) happens to also enumerate the same experiment_run_ids as `supporting_experiments` (not returned) by construction of `submit_claim`, so the Evidence Drawer uses `independence_groups` as its real id source instead. `contradicting_experiments`/`reviewers` have **no** real read path at all post-submission; the UI marks them `unavailable via current API` for any claim not freshly submitted in the same browser session (where the submitted values can be echoed as user input, clearly labeled as unconfirmed-by-a-read-endpoint) | No |

## Literature Evidence / Applicability

| UI need | Real endpoint | Availability | Adapter | Unresolved issue |
| --- | --- | --- | --- | --- |
| Search sources (local DDR / Crossref) | `GET /api/generation/evidence/search` | available | `searchEvidence` (pre-existing, reused unmodified) | Crossref path is a live network call (see `tests/llm_generation/test_api.py`); if the sandbox has no outbound network, `source=crossref` fails and must render `EmptyState variant="failed"`, not a silent empty list |
| Verify a DOI before trusting it as a citation | `POST /api/generation/evidence/verify-doi` | available | `verifyDoi` (new) | Requires a `project_id` — the UI passes the current route's project | No |
| Applicability / context-match reports (organism/strain/genotype/medium/condition/timepoint/intervention/measurement match, `overall_match_status`, `transfer_risks`, `downgrade_reasons`) | `GET /api/generation/evidence/match-reports` (optionally `?evidence_id=`) | available | `listEvidenceMatchReports` (new) | This table is populated by `harness.evidence_retrieval.service.match_evidence_item`, which nothing in the currently-wired diagnosis/learning flow calls yet in this session's environment — so the list may legitimately be empty in a fresh DB; rendered as `EmptyState variant="first_use"`, not `no_result` |

## Computational Traceability

| UI need | Real endpoint | Availability | Adapter | Unresolved issue |
| --- | --- | --- | --- | --- |
| Capability health (llm/crossref/local_ddr) | `GET /api/generation/health` | available | `getGenerationHealth` (pre-existing, reused) | none found |
| List LLM generation records | `GET /api/generation/records` (optional `?task_type=`) | available | `listGenerationRecords` (new) | none found |
| Generation record detail (incl. artifact refs) | `GET /api/generation/records/{id}` | available | `getGenerationRecord` (new) | `raw_output_artifact_ref`/`parsed_output_ref` are opaque references, not fetchable content — rendered as identifiers, not dereferenced |
| Rejected fabricated references (hallucination guard) | `GET /api/projects/{id}/timeline` filtered for `event_type=="GEN_HALLUCINATED_REFERENCE_REJECTED"` | available, indirect (same derivation pattern as Knowledge Claims) | inline in `ComputationalTraceabilityTab` | Only visible for projects where `verify_doi` was actually called and failed; most projects will show zero, which is the honest "no fabricated references caught yet", not a broken feature |

## Explicitly absent (not built, not faked)

| Prompt concept | Why absent |
| --- | --- |
| Cross-project / Global knowledge list | No endpoint; timeline-derivation only works per-project |
| `Mechanism`, `EngineeringPattern`, `BiologicalEntity`, `Relationship` (as objects), `Contradiction` (as object), `EvidenceGap` (as object), `ReuseRecord`, `CurationTask` | None of these exist as backend tables/routes reachable from any real endpoint |
| Relationship/Evidence graph query | No graph endpoint; `KnowledgeClaim` only carries 2 of the prompt's 15 relation types (supports/contradicts, via experiment ids) |
| Page 2 → Page 3 reuse record | No endpoint; would require a new mutating backend route, which is outside this session's Allowed Scope (§58 forbids backend changes without authorization) |
| DDR/biological-rules/engineering-actions browse API | Real local JSON exists (`knowledge/ddr_database/`, `knowledge/biological_rules/`, `knowledge/engineering_actions/`) but is only consumed server-side by diagnosis/design/evaluation pipelines, not exposed as a queryable route — unchanged from the Phase-0 audit's finding |

## Session note

No fixture/mock data was introduced anywhere in this pass. Every rendered field traces to a real
HTTP call against an already-implemented (real, currently uncommitted alongside the rest of this
session's backend work — `git status` shows `harness/api/*`, `harness/evidence_retrieval/`,
`harness/learning` changes as untracked/modified, consistent with the Page 2 mapping matrix's own
note) FastAPI route. Per the Page 2 precedent, the FastAPI backend was **not** started against the
shared `project_ledger.db` for a live end-to-end render in this pass — the file has same-day
concurrent edits from work not attributable to this session, and starting a server that writes to
it risks colliding with a concurrent session (exactly the incident the Page 2 decision records
already documented once). Verification is therefore static (typecheck/lint/build/test), matching
the precedent set for Page 2's own second pass.
