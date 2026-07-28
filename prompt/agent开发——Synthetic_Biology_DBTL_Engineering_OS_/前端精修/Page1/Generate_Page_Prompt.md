```yaml
page_id: page-01
page_name: Project Command Center
spec_type: Generate Page Prompt
version: 0.1.0
status: BLOCKED
owners:
  - Product Owner
reviewers:
  - Frontend Architect
parent_contract: Page Design Contract v1.2.0
parent_architecture: Frontend Architecture Prompt v1.2
last_updated: 2026-07-23
dependencies:
  - 00_Page_Research.md
  - 01_Product_Spec.md
  - 02_UI_Spec.md
  - 03_Interaction_Spec.md
  - 04_Technical_Spec.md
  - 05_Content_Spec.md
  - 06_Acceptance_Spec.md
open_questions:
  - This document is NOT ready to hand to an implementation agent. See "BLOCKED" banner below.
approved_exceptions: []
```

> ## ⚠ STATUS: BLOCKED — DO NOT USE TO START IMPLEMENTATION
>
> Per Contract §83, this document may only be generated "after all seven Specs are approved." As of
> 2026-07-23, `00_Page_Research.md`, `03_Interaction_Spec.md`, `04_Technical_Spec.md`, and
> `05_Content_Spec.md` are all `status: Draft` with substantial `GAP`/`BLOCKED` sections, and
> `06_Acceptance_Spec.md` has zero criteria in 7 of 17 domains. Only `01_Product_Spec.md` and
> `02_UI_Spec.md` are `status: Approved`. This file is created now, in skeleton form, purely to
> complete the required §74 directory structure and to make the remaining blockers explicit — not to
> declare Page 1 ready for implementation. Sections below are filled only where an approved source
> exists; everything else is marked `BLOCKED`.

---

## 1. Role

Frontend implementation agent for the Synthetic Biology DBTL Engineering OS, operating under Page
Design Contract v1.2.0 Part XV (Contract Runtime) and the Scope Lock in Part VIII.

## 2. Mission

Implement the Project Command Center (Page 1) — the Mission Control surface described in
`01_Product_Spec.md` — as a persistent, real-time, decision-focused overview of the DBTL engineering
lifecycle. **Not** buildable yet: see BLOCKED banner above.

## 3. Sources of Truth

In precedence order per Contract §1 and §5.2:
1. Page Design Contract v1.2.0 (`Page1/Synthetic_Biology_DBTL_Engineering_OS_Page_Design_Contract_v1.2 (1).md`)
2. Frontend Architecture Prompt v1.2 (`前端整体架构设计.md`)
3. `01_Product_Spec.md` (Approved)
4. `02_UI_Spec.md` (Approved)
5. `03_Interaction_Spec.md` (Draft — GAP-heavy)
6. `04_Technical_Spec.md` (Draft — BLOCKED pending Repository Audit)
7. `05_Content_Spec.md` (Draft — GAP-heavy)
8. `06_Acceptance_Spec.md` (Draft — BLOCKED, 7/17 domains empty)
9. `00_Page_Research.md` (Draft — benchmark analysis GAP)

## 4. Repository Audit — `BLOCKED`

Requires executing Contract §61 (Repository-First Rule) against the real frontend codebase. Not
performed in this normalization pass (explicitly out of scope: "不得触碰前端代码"). See
`04_Technical_Spec.md` §1.

## 5. Page Scope and Non-Goals

Covered — directly from `01_Product_Spec.md` §00 (Responsibilities / "NOT responsible for") and §14
(Explicit Non-goals). Not restated here; see those sections. Summary: Page 1 maintains global project
awareness, summarizes engineering state, exposes evidence/risk/approvals, and recommends next
actions — it must never become an editor, database browser, report page, or chatbot.

## 6. User and Scientific Workflow

Covered — from `01_Product_Spec.md` §05 (User Personas), §06 (User Journey), §07 (Scientific Workflow
Mapping). Not restated here.

## 7. Scientific Objects and Content — Partial / `BLOCKED`

`05_Content_Spec.md` §2 gives an object list at name level only; field-level definitions are `GAP`.
Cannot be used as an implementation contract yet.

## 8. Layout and Visual Contract — Partial

`02_UI_Spec.md` is Approved but has 6 `GAP` and 8 `Partial` items in its own Part Z coverage map
(notably: no annotated wireframe, no Nanobanana Composition Constraints, no full 5-breakpoint
responsive table, and one unresolved color-token conflict against Global §23.3). Usable as a strong
directional reference; not usable as a complete implementation contract yet.

## 9. Interaction Contract — `BLOCKED`

`03_Interaction_Spec.md` has 18 of 26 required sections at `GAP`. Cannot be used as an implementation
contract yet.

## 10. Backend/API Mapping — `BLOCKED`

`04_Technical_Spec.md` §10–11 are `BLOCKED` pending Repository Audit.

## 11. State Ownership — `BLOCKED`

`04_Technical_Spec.md` §8 is `BLOCKED` pending Repository Audit.

## 12. Component and File Plan — `BLOCKED`

`04_Technical_Spec.md` §4–5, §30 are `BLOCKED`.

## 13. Implementation Priority — `BLOCKED`

Cannot be sequenced (P0–P3 per Contract §77 Required Priority Format) until `01_Product_Spec.md`
Part Z's `GAP` item "Required Priority Format (P0–P3)" is resolved by the page owner.

## 14. Change Safety

Covered by default — Contract Part VIII Scope Lock and Protected Repository Surface apply in full
regardless of Page 1's readiness state; no Page-1-specific extension to this has been identified
because Repository Audit has not run.

## 15. Verification — `BLOCKED`

Cannot be defined until `04_Technical_Spec.md` §27 Testing Strategy is unblocked.

## 16. Acceptance Criteria — `BLOCKED`

`06_Acceptance_Spec.md` is itself `BLOCKED` (7 of 17 domains empty; the rest `DEFERRED`/untested).

## 17. Required Deliverables — `BLOCKED`

Cannot be finalized until the above are resolved.

## 18. Completion Report Format

The eventual implementation MUST use Contract §105 (Page Contract Completion) and §113 (Contract
Runtime Result) formats. No completion report may be produced until this document's BLOCKED status is
lifted.

---

## Unblocking Path (decision, not executed here)

In order, before this document can be regenerated as `status: Approved` and handed to an
implementation agent:

1. Page owner resolves `01_Product_Spec.md` Part Z `GAP` items (Secondary User Stories, Entry Points,
   Risks and Failure Modes, Product Success Metrics with measurable thresholds, P0–P3 priorities).
2. UX Reviewer resolves `02_UI_Spec.md` Part Z `GAP` items and the flagged color-token conflict
   against Global Contract §23.3 (via reconciliation or a Page Exception Record).
3. A dedicated Interaction Spec authoring pass closes the 18 `GAP` sections in
   `03_Interaction_Spec.md`, at minimum Selection Model, Inspector, Evidence Drawer, Review and
   Approval, Context Preservation, and Deep Linking.
4. A dedicated Content Spec authoring pass, with a Synthetic Biology Reviewer, closes the `GAP`
   sections in `05_Content_Spec.md`, at minimum Scientific Objects (field level), Evidence Hierarchy,
   Claim–Evidence Mapping, and Confidence and Uncertainty.
5. A Page-1-scoped Repository Audit is executed against the real frontend codebase, unblocking all of
   `04_Technical_Spec.md`.
6. `06_Acceptance_Spec.md`'s 7 empty domains (Functional, Backend Truthfulness, Interaction,
   State/Persistence, Responsive, Performance, Code/Architecture, Security/Permissions, Visual
   Regression) are populated from the now-unblocked specs above.
7. Gates 0–3 (Contract §90–93) are re-checked; only then may this Generate_Page_Prompt.md be
   regenerated with `status: Approved`.
