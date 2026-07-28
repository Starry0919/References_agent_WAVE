# Page 3 — Specification Matrix

Repo: `agent-harness/agent-harness` (frontend `dbtl-engineering-os-frontend`, backend FastAPI `harness/`).
Source contracts: `workflow/design/evolution/前端精修/Page3/Page3_Scientific_Knowledge_Production_System_Claude_Code_Implementation_Prompt.md`,
`workflow/design/evolution/前端整体架构设计.md` (Page 3 = "Knowledge & Evidence Layer").

## Legend
`done` (implemented + verified against a real endpoint) · `reused` (pre-existing Phase-0 skeleton,
verified correct, extended) · `gap_backend` (blocked: no real endpoint/field exists; documented,
not worked around) · `derived_real` (no dedicated endpoint, but the UI value is computed
client-side from ≥1 real HTTP responses — not a fixture, not fabricated) · `n/a`.

## 0. Repository Truth Audit summary

- Frontend: React 18 + Vite 6 + TS 5.7 + Tailwind + `@tanstack/react-query` + `react-router-dom`,
  same stack as Page 1/2/4. Route `/projects/:projectId/knowledge` → `KnowledgePage.tsx` already
  exists as a Phase-0 skeleton (three tabs: Biological Knowledge / Literature Evidence / Evidence
  Graph), registered in `registry/modules.ts`. This pass extends that skeleton in place; it does
  not create a new route or a parallel page.
- Backend: **no dedicated "Knowledge Object" API exists.** The closest real domain object to the
  prompt's `KnowledgeObject` is `harness.learning.models.KnowledgeClaim` (table
  `knowledge_claims`), exposed by `harness/api/learning.py` — submit / promote / retract / get-by-id,
  no list-all route. Discoverability for "list the claims in this project" is real but indirect:
  `GET /api/projects/{id}/timeline` returns the full project event ledger, and
  `KNOWLEDGE_CLAIM_SUBMITTED/PROMOTED/DEMOTED/RETRACTED` events carry `entity_type="KnowledgeClaim"`,
  `entity_id=claim_id` — so the frontend derives the claim id set from real events, then resolves
  each id via the real `GET /knowledge-claims/{id}` route. This is `derived_real`, not a fixture.
- `harness/api/generation.py` (Scientific Capability Adapters) is real and covered by
  `tests/llm_generation/test_api.py`: evidence search (local DDR / Crossref), DOI verification
  (real Crossref network call, confirmed by a live test asserting a fabricated DOI resolves
  `false`), evidence match reports (`EvidenceMatchReport` — organism/strain/genotype/medium/
  condition/timepoint/intervention/measurement match + `overall_match_status` +
  `transfer_risks`/`downgrade_reasons` — this **is** the real backing for "Applicability Context" /
  "context mismatch"), and `LLMGenerationRecord` list/detail (the real backing for "Computational
  Traceability", §20).
- `harness/api/experiments.py` (`getExperimentRun`, real, already adapted in
  `frontend/src/api/experiments.ts` for Page 2) resolves a `KnowledgeClaim.supporting_experiments` /
  `contradicting_experiments` id into a real `execution_status`/`deviations` record — reused here,
  not duplicated.
- No backend endpoint exists for: a cross-project/global Knowledge Object list; Mechanism,
  EngineeringPattern, BiologicalEntity, Relationship-graph, EvidenceGap, Contradiction, or
  ReuseRecord as first-class objects; a relationship/graph query API; a curation-queue API beyond
  the promotion ladder; or a Page-02-writes-a-ReuseRecord endpoint. These gaps are the same ones
  already flagged honestly in the Phase-0 `KnowledgePage.tsx` comments and
  `docs/前端精修/backend_mapping_matrix.md`; this pass does not re-litigate them, it fills in the
  real slice that **does** exist (`KnowledgeClaim` + evidence retrieval/matching + generation
  provenance) to full contract depth instead.
- `harness/memory/knowledge_claims.py` enforces real governance rules this UI must respect, not
  merely display: (a) `reviewer_id == created_by` → `PromotionRejected` (no self-approval); (b)
  promoting to `lab_candidate`/`lab_approved` requires ≥3 non-empty `independence_groups`
  (`MIN_INDEPENDENT_GROUPS_FOR_PROMOTION`); (c) if `contradicting_experiments` is non-empty, a
  non-blank `reason` is required for that same promotion. All three are covered by
  `tests/projects/test_knowledge_claims.py`.
- No authentication system exists anywhere in this repo (confirmed across Page 1/2/4: every
  mutation hardcodes an `actorId` string, e.g. `"frontend-user"`). Knowledge Claim promotion's
  self-approval guard therefore requires the UI to let the acting user type a **different** actor
  id than the one used at submission — see ADR-KC-002.

## 1. Product Constitution (Part II, §6-12)

| Requirement | UI region | Backend dependency | Status |
| --- | --- | --- | --- |
| §6-7 Identity = Knowledge *Production*, not storage; primary operating question always visible | `KnowledgePage.tsx` header + `KnowledgeClaimsTab` empty/loaded states | n/a | done |
| §8 Fixed production lifecycle Acquire→...→Knowledge Evolution rendered as one object's lifecycle, not disjoint tools | `KnowledgeClaimsTab`: submit (Acquire/Extract/Structure collapsed into one real `POST`, since the backend has one creation step, not five) → promote (Evaluate/Validate/Publish) → retract (Supersede/Retire) → `promotion_record` (Knowledge Evolution) | `harness/api/learning.py` | done, with an honest vocabulary mapping — see DSR-KC-001 |
| §12 Explicit failure modes (paper-search-engine home, decorative graph, summary-as-evidence, DOI-only citation, hidden contradictions, no strain/condition shown, ambiguous no-results, silent-validate, overwrite-on-update, Page 2 mutating Page 3) | whole page | n/a | done — see §5/§8 rows below for the concrete mechanism defeating each one |

## 2. Core Object Model / Knowledge Status / Evidence Model (Part III, §13-21)

| Requirement | UI region | Backend dependency | Status |
| --- | --- | --- | --- |
| §13-14 `KnowledgeObject`-equivalent minimum contract (id/version/status/applicability/evidence ids/quality/confidence/limitations/reuse scope/timestamps) | `KnowledgeClaimInspector` | `KnowledgeClaim` row (`claim_id`, `status`, `scope`, `evidence_grade`, `promotion_record`, timestamps) | done for every field the table actually has; `permittedReuseScope`/`supersedesVersion` fields from the prompt's illustrative TS type have **no** backend column — rendered as `gap_backend`, not invented |
| §15 Controlled Knowledge Status vocabulary, scientific/review/publish/reuse states distinguished | `StatusBadge` extended with the 4 real statuses (`project_candidate`/`lab_candidate`/`lab_approved`/`retracted`) | `KNOWLEDGE_CLAIM_STATUSES` | done — see DSR-KC-001 for why the real 4-state ladder is shown as-is instead of the prompt's illustrative 12-state vocabulary |
| §16 Evidence is a first-class object, not a citation string; quality vs. confidence separated | `EvidenceDrawer` (shared, reused) fed by `claimToEvidenceSummaries()`; `evidence_grade` (quality) rendered distinctly from the claim's promotion status (confidence/governance state) | `KnowledgeClaim.evidence_grade` + resolved `ExperimentRunSummary` per `independence_groups` id | done for the fields that exist; strain/genotype/measurement-level Evidence sub-fields the prompt lists (§16) are not separately modeled on `KnowledgeClaim` — only present at `scope` (claim-level) granularity, not per-evidence-item; documented, not fabricated per-item |
| §16 Evidence Quality vs Confidence separation | `KnowledgeClaimInspector` shows `evidence_grade` and `status` in two visually distinct fields, never merged into one badge | as above | done |
| §17 Applicability Context, "Unknown" not "Universal" | `ApplicabilityPanel.tsx` (new shared component) | `KnowledgeClaim.scope` dict (`species, strain_background, genotype_context, medium, carbon_source, cultivation_mode, assay` per the model's own docstring) | done — every one of those 7 keys is rendered; any key absent from the dict (or `null`) renders literally "Unknown", never omitted or defaulted to a guess |
| §17 Cross-strain/condition applicability signal | `EvidenceMatchReport` list (`overall_match_status`, `transfer_risks`, `downgrade_reasons`, per-dimension match) rendered in the Literature Evidence tab | `GET /api/generation/evidence/match-reports` | done |
| §18 Typed, directional, evidenced relationships (supports/contradicts/...) | `independence_groups` (real, returned by `GET .../knowledge-claims/{id}`) resolved per experiment id to a real `ExperimentRunSummary` — this is the `supports` relation. `contradicts` (`contradicting_experiments`) is **not** returned by the same GET route (discovered this session, see backend_mapping_matrix.md) — rendered `unavailable via current API` for any claim not freshly submitted this browser session, never silently omitted or faked as "no contradictions" | `harness/api/experiments.py` | done for `supports`; `contradicts` is `gap_backend` on read (real only transiently, at submission time); the other 13 of the prompt's 15 relation types (`limits`, `contextualizes`, `derived_from`, `explains`, `regulates`, `catalyzes`, `competes_with`, `depends_on`, `applies_to`, `not_transferable_to`, `supersedes`, `reused_in`, `validated_by`) have no backend representation on any object this page can reach — `gap_backend`, listed once in Known Limitations rather than faked per-relation |
| §19 Production lifecycle stage-by-stage (Acquire/Extract/Normalize/Structure/Link/Evaluate/Validate/Publish/Observe/Update/Supersede-Retire) | see §8 row above | `harness/api/learning.py`, `harness/api/generation.py` | done — Acquire/Extract/Structure map to `submit_claim` (one real step, no separate normalize/structure endpoints exist — a single creation call is the entire "candidate" surface); Evaluate/Validate/Publish map to `promote_claim`; Observe Outcome maps to the resolved `supporting_experiments`; Update/Supersede/Retire map to `retract_claim` (the only "remove from active use" verb the backend has — there is no separate `supersede` producing a new linked version; `supersedes_claim_id` is a real column but no endpoint sets it, so "supersede" is `gap_backend`, only "retract" is real) |
| §20 Computational Traceability chain (Prompt→Model→Tool→Params→Inputs→Output→Review→Accepted/Rejected) | `ComputationalTraceabilityTab.tsx` (new) | `GET /api/generation/records`, `GET /api/generation/records/{id}` (`LLMGenerationRecord`: task_type/provider/model_id/prompt_template_id+version/output_schema_version/validation_status/retry_count/fallback_used/shared_model_risk/token_usage/latency) | done — every field in the prompt's chain has a real column except "Review→Accepted/Rejected", which does not exist as a reviewable state on `LLMGenerationRecord` (only `validation_status`, a schema-validation result, exists) — rendered as `gap_backend` explicitly, not conflated with human review |
| §21 Runtime Reuse Contract (Page 2 records `knowledge_id/version/reuse_tier/...`, cannot rewrite Page 3 state) | "Reuse in Engineering Decision" action | none | `gap_backend`, by design not built — see DSR-KC-003 |

## 3. Page IA / UI Contract (Part IV, §22-36)

| Requirement | UI region | Status |
| --- | --- | --- |
| §22 Workspace skeleton (context bar / command header / scope+query / 3-pane body / comparison tray / evidence drawer) | Reuses global `ProjectContextBar` (L0, unmodified) + page-level tab header (existing pattern from Page 4) + `KnowledgeClaimsTab`'s list/inspector split + `EvidenceDrawer` (shared) | done within the existing tabbed-page pattern already established for Page 3/4; a literal 3-column always-visible layout was not introduced net-new because the existing Page 3/4 tab shell is the established, tested IA for this exact route and duplicating a second page shell would violate "No Local Design Language" (Invariant 7) |
| §23 Persistent Context Bar fields | `ProjectContextBar` (global, unmodified) shows project/cycle/stage; "knowledge scope" is additionally stated inline in `KnowledgeClaimsTab` as "Project" (the only real scope — see below) | done; Global/Decision scope not offered, honestly, since no cross-project or per-decision query endpoint exists (`gap_backend`) |
| §25 Left Navigation (Knowledge Types/Organisms/Mechanisms/Patterns/Gaps/Contradictions/Under Review/Published/Superseded/Saved Views), "counts must be real" | Status-filter chips inside `KnowledgeClaimsTab`, computed from the real, already-fetched claim set for the current project (`derived_real` counts, not hardcoded) | done for the 3 dimensions the data actually supports (status ladder, has-contradicting-evidence, insufficient-independent-evidence); Organisms/Strains/Mechanisms/Engineering-Patterns/Saved-Views have no backend index to filter by — `gap_backend`, not simulated with placeholder facets |
| §26-27 Knowledge Surface + Knowledge Card min-fields | `KnowledgeClaimsTab` list — type, statement, status, evidence_grade, supporting/contradicting counts, independent-group count vs. threshold, current version count (`promotion_record.length`), reuse eligibility (`lab_approved` only) | done; DOI/author/journal are correctly *not* the card's primary layer (§27) |
| §28 Relationship View (graph) | kept as the Phase-0 honest `unavailable` panel, wording extended | `gap_backend` — no graph query endpoint; building a client-side graph from only 2 relation types (supports/contradicts) over 1 object type would misrepresent the richer relationship model §18 describes, so it is declared unavailable rather than built as a misleadingly thin "graph" |
| §29 Contextual Inspector (14-item order) | `KnowledgeClaimInspector` | done for the ~9 of 14 items backed by real data (Identity, Scientific Nature[claim statement], Applicability, Supporting Evidence, Conflicting Evidence, Evidence Quality, Limitations[none recorded→explicit], Version History[promotion_record], Review/Curation Actions); Mechanism, Evidence Gaps-as-object, Engineering Reuse, Provenance-beyond-actor, Downstream Usage are `gap_backend`, each rendered as an explicit line, not omitted |
| §30 Evidence Drawer contract | shared `EvidenceDrawer`, reused unmodified (no fork) | done for the resolved-experiment-run items; "open source" link is `gap_backend` for experiment-run evidence (no public URL concept) but real for literature documents (DOI/URL from search results) |
| §31 Comparison (2-4 objects, diff-first) | `KnowledgeComparisonTray` (new) | done — real, client-side comparison of N already-fetched `KnowledgeClaim`s across scope/status/evidence_grade/experiment counts/version count; not a new endpoint, just a second render of already-real data |
| §32 Knowledge Production Queue, distinct from browse view | The status-filter chips (§25 row) double as the queue (`project_candidate` = newly acquired/needs evaluation; `lab_candidate` = under lab review; `lab_approved` = published; `retracted` = retired) — visually distinct filter, not a separate hidden system | done within real data; a dedicated normalization-conflict/validation-pending queue beyond these 4 real statuses is `gap_backend` |
| §33-36 Visual hierarchy/semantics/rhythm/responsive | Tailwind tokens + shared `StatusBadge`/`EmptyState` reused, no new color language | reused |

## 4. Interaction Contract (Part V, §37-46)

| Requirement | Status |
| --- | --- |
| §38 Retrieve: no-results must distinguish no-knowledge / over-filtered / no-permission / index-down / network-fail | done — `EmptyState` variants (`first_use`/`no_result`/`disconnected`/`failed`) used distinctly; "no-permission" is `n/a` (no auth/permission system in this repo, confirmed by audit — not fabricated) |
| §40 Compare: explicit count, incompatible-object warning, diff-first | done for count + client-side diff table; "incompatible objects" warning is `n/a`-adjacent — comparing across projects is not offered (single-project scope), so the cross-scope incompatibility case the prompt anticipates cannot occur here |
| §41 Reuse in Engineering Decision (8-step consequential-action flow) | `gap_backend`, entire flow — no reuse-record endpoint; see DSR-KC-003 |
| §42 Submit Source/Outcome ≠ publish; failed/negative results not dropped | done — `submit_claim` always starts at `project_candidate` regardless of `evidence_grade` passed in (server-enforced, verified by reading `submit_claim`); the submit form does not offer a "publish immediately" option because the backend has none |
| §43 Review/Publish: version-bound, reasoned, confirmed, rollback-safe, conflict-not-silently-overwritten | done — every promote/retract call sends the real `claim_id` + shows the exact current `status`/`promotion_record` length being acted on; 422 (`PromotionRejected`) and 404 responses are surfaced verbatim, not swallowed; no optimistic update is applied before the server confirms (react-query `invalidateQueries` on success only) |
| §44 AI participation boundaries (candidate not auto-Published, no hidden contradictions, no confidence-as-evidence) | done — `submit_claim` never sets a validated/published status; `evidence_grade` and `status` are always rendered as two separate fields; `contradicting_experiments` is always shown alongside `supporting_experiments`, never filtered out |
| §45 Loading/Empty/Error/Partial, 7 empty sub-variants | done via shared `EmptyState` variants; "尚未在决策中复用" (not yet reused in a decision) sub-variant is rendered as the Reuse gap notice itself |
| §46 Accessibility | done to the same bar as Page 2 (native buttons/labels/focus-visible, no keyboard-only pass run — see Verification) |

## 5. Technical Contract / Scope Lock (Part VI-VII)

| Requirement | Status |
| --- | --- |
| §47 Repository Audit before coding | done — this document + backend_mapping_matrix.md, produced before any `src/` edit in this pass |
| §48 Protected Surface frozen (AppShell/tokens/nav/shared object model/auth/Page1-2 workflows) | done — no edits to `AppShell.tsx`, `TopNav.tsx`, `router.tsx` route tree shape, tailwind config, or any Page 1/2 file in this pass |
| §49 Architecture rules (feature boundary, DTO/view-model split, adapters, no fixture-in-prod-path) | done — new code lives in `pages/knowledge/`, `components/knowledge/`, `api/knowledge.ts`; every adapter function does a real `fetch`; zero mock data introduced |
| §52 State ownership | done — claim list/detail/records are server-state via react-query; selected claim id and comparison selection are `useUrlSelection`-style URL state (new: `selected`/`compare` query params on the knowledge route); actor/reviewer-id text input is local component state (ephemeral, not scientific data) |
| §53 API Integration, fabrication ban, explicit-gap requirement | done — see Backend Mapping Matrix (`page3_backend_mapping_matrix.md`) |
| §54 Concurrency/mutation safety | done — no idempotency-key mechanism exists in this backend for any router (confirmed absent app-wide, not just here) so none is added; double-submit is prevented client-side via `isPending` disabling |
| §55 Performance (5000 objects / 50000 evidence) | **not validated at that scale** — this project's real database has a handful of seeded projects/claims; a synthetic 5000/50000 load test was not run (would require fabricating data volume this session has no authorization to seed into the shared, concurrently-edited `project_ledger.db`) — flagged as `NOT AVAILABLE`, not claimed `PASS` |
| §56 Security/content safety | done — no `dangerouslySetInnerHTML`; external literature `url`/DOI links use `target=_blank rel="noreferrer"` |
| §57 Testing strategy | see Verification section of the completion report |
| §58-60 Scope Lock / Forbidden Autonomous Behaviors / Conditional Audit Gate | done — no backend file touched, no shared/global component forked, no dependency added; see decision records for the one shared-component *extension* (StatusBadge) made instead of a fork |
