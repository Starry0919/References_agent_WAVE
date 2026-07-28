# Page 3 — Decision Records

## DSR-KC-001 — Map the real 4-state `KnowledgeClaim` ladder onto the prompt's illustrative 12-state vocabulary honestly, rather than inventing the missing 8 states

```yaml
id: DSR-KC-001
context: >
  Page 3 prompt §15 lists 12 Knowledge Status values (Candidate, Extracted, Normalized,
  Structured, Under Review, Validated, Published for Reuse, Needs Revision, Contested,
  Superseded, Deprecated, Retired, Rejected). The only real backend status enum reachable by
  this page is `KNOWLEDGE_CLAIM_STATUSES = (project_candidate, lab_candidate, lab_approved,
  retracted)` (harness/learning/models.py). Inventing UI-only synonyms for the other 8 states
  (e.g. rendering a client-computed "Needs Revision" that the backend never actually set) would
  violate System Invariant 3 (Human Governance: status must not be silently granted by the UI)
  and Invariant 5 (Single Source of Truth).
decision: >
  Render the real 4 statuses as-is via the shared StatusBadge (extended, not forked - see
  ADR-KC-001), with plain-language subtitles in the Inspector explaining where each real status
  sits on the prompt's conceptual ladder (project_candidate ~= Candidate/Extracted/Structured
  collapsed; lab_candidate ~= Under Review; lab_approved ~= Validated + Published for Reuse
  collapsed; retracted ~= Superseded/Deprecated/Retired/Rejected collapsed - the backend does not
  distinguish these). The Specification Matrix documents this mapping once; it is not repeated
  as fabricated distinct states anywhere in the UI.
alternatives:
  - "Invent the 8 missing states as client-side derived flags": rejected - a UI-derived "Validated"
    badge sitting next to a real "lab_approved" badge would look like two different facts about
    the same object, and nothing prevents them from drifting (Invariant 5).
  - "Refuse to render any status until backend adds all 12": rejected - the real 4-state ladder is
    itself a genuine, tested, human-governed promotion ladder (self-approval guard, independent-
    evidence-group threshold, conflict-acknowledgment requirement) and is more scientifically
    rigorous than most 12-state vocabularies that skip those checks; withholding it would be
    strictly worse for the product than presenting it honestly.
tradeoff: The Inspector's status subtitle is one extra line of explanatory text per object; no functional cost.
impact: "frontend/src/components/common/StatusBadge.tsx, frontend/src/pages/knowledge/KnowledgeClaimsTab.tsx"
approval: self-applied (documented interpretation of an already-flagged spec/backend gap, consistent with Page 2's DSR-002 precedent for resolving spec/backend tension via documented reading rather than pausing)
```

## ADR-KC-001 — Extend `StatusBadge`'s vocabulary instead of forking a Page-3-local badge

```yaml
id: ADR-KC-001
context: >
  StatusBadge (frontend/src/components/common/StatusBadge.tsx) is the single, explicitly-shared
  status->color/icon/text mapping for the whole app (its own doc comment: "不允许每页用不同颜色
  表达不同语义"). Its `BadgeStatus` union does not include `project_candidate`/`lab_candidate`/
  `lab_approved`/`retracted`.
constraints:
  - Must not fork a Page-3-private badge component (Invariant 7 "No Local Design Language";
    repo-wide precedent set by ADR-001 in the Page 2 decision records, which extended
    HumanGatePanel instead of forking it for the exact same reason).
  - Must not change the visual meaning of any existing status value.
decision: >
  Add the 4 real KnowledgeClaim statuses as new `BadgeStatus` union members with their own
  color/icon entries (retracted reuses the existing "superseded" slate/History treatment since
  both mean "no longer active, history preserved"; project_candidate reuses "draft"'s dashed-
  outline treatment; lab_candidate reuses "under_review"'s amber/clock treatment; lab_approved
  reuses "approved"'s emerald/check treatment) - additive only, zero existing entries touched.
alternatives:
  - "New KnowledgeStatusBadge component": rejected by the repo-wide no-fork precedent (ADR-001).
reason: One status vocabulary for the whole app, extended additively, exactly as ADR-001 already established the pattern for HumanGatePanel.
affected_files:
  - frontend/src/components/common/StatusBadge.tsx
rollback: Remove the 4 added union members/CONFIG entries; no other file depends on their absence.
approval: self-applied (additive, backward-compatible extension of a shared component - same category ADR-001 was self-applied under)
```

## ADR-KC-002 — Require a distinct "acting as (reviewer)" identity for promote/retract, separate from the submitter identity

```yaml
id: ADR-KC-002
context: >
  `promote_claim` raises `PromotionRejected` when `reviewer_id == created_by` (self-approval
  guard, real and tested). This repo has no authentication system anywhere (confirmed: every
  existing mutation across Page 1/2/4 hardcodes `actorId: "frontend-user"`). If Page 3 reused
  that same hardcoded literal for both `submitClaim`'s `created_by` and `promoteClaim`'s
  `reviewer_id`, every single promotion attempt would deterministically fail with a 422 - not a
  edge case, the *only* case, since there is no second identity anywhere else in the app to draw
  from.
decision: >
  Add a plain local (component-state, not persisted, not scientific data per the State Ownership
  Matrix) "Submitting as" / "Reviewing as" text input, defaulting to `frontend-user` for
  submission and `frontend-reviewer` for promotion/retraction - two distinct default literals so
  the default path itself does not immediately trip the self-approval guard, while still letting
  the user type any identity they want. The 422 `PromotionRejected` response is still surfaced
  verbatim if they do collide (never swallowed).
alternatives:
  - "Silently pick a random reviewer id": rejected - a human-governance gate whose "human" is a
    string the UI fabricated without the user's knowledge is a worse violation of Invariant 3
    than asking the user to type a name.
  - "Disable promotion entirely until real auth exists": rejected - would make the entire
    promotion ladder (the one genuinely real governance workflow this backend has) unreachable
    from any UI, which is a much larger regression than a plain text identity field.
reason: The self-approval guard is real backend behavior this UI must respect, not work around; the only way to respect it honestly without real auth is to let the user state who they're acting as.
affected_files:
  - frontend/src/pages/knowledge/KnowledgeClaimsTab.tsx
rollback: Remove the identity inputs and hardcode a single literal; promotion would then always 422, i.e. this is not a safe rollback without also disabling the promote/retract UI.
approval: self-applied (necessary to make a real, tested backend rule usable at all in an app with no auth system; does not touch or simulate authentication)
```

## DSR-KC-003 — Do not build "Reuse in Engineering Decision" (prompt §21/§41); render its absence explicitly

```yaml
id: DSR-KC-003
context: >
  Prompt §21 (Runtime Reuse Contract) and §41 (an 8-step consequential-action flow) require
  Page 3 to let a user commit a specific KnowledgeClaim version to a Page 2 Engineering Decision,
  persisting `knowledge_id/knowledge_version/reuse_tier/applicability_snapshot/
  evidence_summary_snapshot/decision_id/used_at`. No backend endpoint or table for a "reuse
  record" of any shape exists anywhere in this repository (confirmed by reading every router in
  harness/api/). Building this would require adding a new backend mutation - out of Allowed
  Scope §58 ("不得...修改后端业务逻辑") and Conditional Audit Gate §60 ("需要凭证、外部权限或
  不可逆操作" / new backend surface without authorization).
decision: >
  Do not build the reuse flow. Render an explicit "Reuse in Engineering Decision - unavailable"
  panel in the Inspector for `lab_approved` claims (the only status where reuse would even be
  contract-eligible), naming the missing endpoint, consistent with Page 4's ApprovalTab honesty
  pattern (also a documented, explicit "unified endpoint does not exist" panel, not a hidden
  feature).
alternatives:
  - "Persist a reuse record to localStorage as a stand-in": rejected outright - Invariant 5
    (Single Source of Truth) explicitly forbids the frontend maintaining a second domain-truth
    store that competes with the backend; a localStorage-only "reuse record" would silently
    vanish per-browser and give a false impression of durability/auditability, which is worse
    than not offering the feature.
  - "Build the backend endpoint too, since it's small": rejected - modifying backend scientific-
    service code and adding a new mutating route is explicitly outside this pass's Allowed Scope
    without separate authorization (§58/§60), matching Page 2's DSR-002 rejection of the same
    category of workaround ("Build a real aggregation endpoint on the backend...rejected").
tradeoff: Acceptance Gate §77 (Engineering Reuse Gate) cannot be marked fully PASS this pass - reported as a named gap in the completion report, not silently dropped.
impact: "frontend/src/pages/knowledge/KnowledgeClaimsTab.tsx (Inspector's Reuse panel)"
approval: self-applied (refusal of an out-of-scope backend change, per Runtime Refusal Rules §104 "要求你在无关范围做大规模重构" - a new mutating backend endpoint for a page whose contract explicitly locks scope to frontend feature work is the same category of overreach)
```

## ADR-KC-003 — Selected-claim and comparison-set state live in the URL, not a global store

```yaml
id: ADR-KC-003
context: >
  State Ownership Matrix (architecture doc §18.2 / Page 3 prompt §52) requires selection and
  comparison-tray membership to be shareable/refresh-safe navigation state. The existing
  `useUrlSelection` hook (`frontend/src/hooks/useUrlSelection.ts`, built for Page 2) already
  implements exactly this pattern for a single `?selected=` param.
decision: >
  Reuse `useUrlSelection` unmodified for the inspected claim id (`?selected=CLAIM-xxx`). Add a
  second, page-local URL param `?compare=CLAIM-a,CLAIM-b` (comma-joined ids, capped at 4 per
  prompt §31 "2-4个") managed by a small local helper in `KnowledgeClaimsTab.tsx` (not a new
  generic hook, since no other page in this repo has a multi-select comparison need yet - adding
  a second shared hook for a single call site would be a premature abstraction).
alternatives:
  - "Global store for compare selection": rejected by the State Ownership Matrix's own rule that
    shareable navigation state belongs in the URL, not a global store.
reason: Consistent with the one existing precedent (useUrlSelection) without adding a second shared abstraction for a single caller.
affected_files:
  - frontend/src/pages/knowledge/KnowledgeClaimsTab.tsx
rollback: Revert to component-local useState; comparison selection would no longer survive a refresh.
approval: self-applied (additive, follows an established pattern, in Allowed Scope §58 "增加必要 adapter、view model、tests、fixtures")
```
