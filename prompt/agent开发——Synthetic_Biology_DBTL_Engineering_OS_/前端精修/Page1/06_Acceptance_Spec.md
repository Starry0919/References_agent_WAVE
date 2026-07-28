```yaml
page_id: page-01
page_name: Project Command Center
spec_type: Acceptance Spec
version: 0.1.0
status: Draft
owners:
  - Product Owner
reviewers:
  - UX Reviewer
  - Frontend Architect
  - Synthetic Biology Reviewer
parent_contract: Page Design Contract v1.2.0
parent_architecture: Frontend Architecture Prompt v1.2
last_updated: 2026-07-23
dependencies:
  - 01_Product_Spec.md
  - 02_UI_Spec.md
  - 03_Interaction_Spec.md
  - 04_Technical_Spec.md
  - 05_Content_Spec.md
open_questions:
  - Every record below is status DEFERRED (untested). Several checklist domains (7, 9, 12, 13, 14,
    15, 16) have no criteria yet because their source specs are still BLOCKED/GAP.
approved_exceptions: []
```

> **Provenance note (2026-07-23)**: this file replaces the prior `Page1/05_Acceptance_Spec.md`,
> which did not contain acceptance criteria in Contract §82's required format — it was a discussion
> draft proposing a global "System Certification Standard" (relocated, verbatim, to
> `Page1/references/Proposal_Global_Certification_Standard.md`). Several individual criterion ideas
> from that draft were genuinely Page-1-relevant and have been migrated below, reformatted into the
> required Acceptance Record structure, with `status: DEFERRED` since none have actually been tested.
> Checklist domains with no available source content are left as empty tables rather than filled
> with invented criteria.

---

## 1. Product / Mission

| criterion_id | requirement | priority | test_method | expected | status | owner | remediation |
| --- | --- | --- | --- | --- | --- | --- | --- |
| P01-PROD-01 | User can immediately understand the current project state | P0 | Task-based usability test | User states project status correctly within stated time budget | DEFERRED | Product Owner | Run learnability test per Contract §9.1 |
| P01-PROD-02 | User can locate the current engineering stage | P0 | Task-based usability test | User correctly identifies current DBTL stage | DEFERRED | Product Owner | — |
| P01-PROD-03 | User can explain the current bottleneck | P1 | Task-based usability test | User paraphrases current bottleneck correctly | DEFERRED | Product Owner | — |
| P01-PROD-04 | User can identify the next engineering action | P0 | Task-based usability test | User names the correct next action | DEFERRED | Product Owner | — |
| P01-PROD-05 | User can navigate without confusion into the correct workspace | P1 | Task-based usability test | User reaches intended destination without backtracking | DEFERRED | UX Reviewer | — |

*(Migrated from `references/Proposal_Global_Certification_Standard.md`, "Product Certification"
question list.)*

## 2. Functional

*(empty — depends on `03_Interaction_Spec.md` and `04_Technical_Spec.md`, both currently GAP/BLOCKED)*

## 3. UI and Design System

| criterion_id | requirement | priority | test_method | expected | status | owner | remediation |
| --- | --- | --- | --- | --- | --- | --- | --- |
| P01-UI-01 | Page 1 color semantics reconcile with Global Contract §23.3 tokens | P0 | Design review | No unresolved private color semantic exists | DEFERRED | UX Reviewer | See `02_UI_Spec.md` Part Z flagged conflict |
| P01-UI-02 | Canonical 1440px reference state exists and matches shell geometry | P0 | Visual regression at 1440px | Matches Global §87 Reference State | DEFERRED | UX Reviewer | Requires Nanobanana Composition Constraints (currently GAP) |

## 4. Scientific Content

| criterion_id | requirement | priority | test_method | expected | status | owner | remediation |
| --- | --- | --- | --- | --- | --- | --- | --- |
| P01-SCI-01 | Every scientific object surfaced on Page 1 exposes source, evidence, confidence, version, history, and ownership | P0 | Content review against rendered objects | All six attributes present or explicitly marked unavailable | DEFERRED | Synthetic Biology Reviewer | Requires `05_Content_Spec.md` §2–4 (currently GAP) |

*(Migrated from `references/Proposal_Global_Certification_Standard.md`, "Scientific Certification.")*

## 5. Evidence and Traceability

| criterion_id | requirement | priority | test_method | expected | status | owner | remediation |
| --- | --- | --- | --- | --- | --- | --- | --- |
| P01-EVD-01 | Any recommendation surfaced on Page 1 exposes evidence → trade-off → alternative → confidence → human review → decision chain | P0 | Content/interaction review | Chain is inspectable within 3 interactions (Contract §9) | DEFERRED | Synthetic Biology Reviewer | Requires `03_Interaction_Spec.md` §8/§13 (currently GAP) |

*(Migrated from `references/Proposal_Global_Certification_Standard.md`, "Decision Certification.")*

## 6. Human Governance

| criterion_id | requirement | priority | test_method | expected | status | owner | remediation |
| --- | --- | --- | --- | --- | --- | --- | --- |
| P01-GOV-01 | Any AI recommendation surfaced on Page 1 passes through Evidence → Human → Approval → Execution before being treated as decided | P0 | Interaction review | No AI output is visually or semantically presented as already approved | DEFERRED | Product Owner | Requires `03_Interaction_Spec.md` §16 Review and Approval (currently Partial) |
| P01-GOV-02 | Trust signals (evidence, transparency, explainability, traceability, governance) are present wherever confidence is shown | P1 | Content review | No bare confidence value without supporting trust signals | DEFERRED | Synthetic Biology Reviewer | Requires `05_Content_Spec.md` §11 (currently GAP) |

*(Migrated from `references/Proposal_Global_Certification_Standard.md`, "Trust Certification" and
"Human Governance Certification.")*

## 7. Backend Truthfulness

*(empty — depends on `04_Technical_Spec.md`, currently BLOCKED pending Repository Audit)*

## 8. Interaction

*(empty — depends on `03_Interaction_Spec.md`, currently mostly GAP)*

## 9. State and Persistence

*(empty — depends on `03_Interaction_Spec.md` §23–24 Context Preservation / Deep Linking, currently GAP)*

## 10. Loading / Empty / Partial / Error

| criterion_id | requirement | priority | test_method | expected | status | owner | remediation |
| --- | --- | --- | --- | --- | --- | --- | --- |
| P01-STATE-01 | Empty states explain why, how to obtain data, and next action; never a blank card | P0 | Visual/content review | Matches `02_UI_Spec.md` §16 | DEFERRED | UX Reviewer | — |
| P01-STATE-02 | Loading uses skeleton UI, never an indefinite spinner, with stable layout | P1 | Visual review | Matches `02_UI_Spec.md` §17 | DEFERRED | UX Reviewer | — |
| P01-STATE-03 | Errors explain what happened, why, recovery, and expandable technical detail; no raw stack traces | P0 | Content review | Matches `02_UI_Spec.md` §18 | DEFERRED | UX Reviewer | — |
| P01-STATE-04 | Stale / partial / offline states are distinguishable from normal/current state | P0 | Visual/content review | Distinct treatment exists | DEFERRED | UX Reviewer | Currently GAP in `02_UI_Spec.md` Part Z — must be authored first |

## 11. Accessibility

| criterion_id | requirement | priority | test_method | expected | status | owner | remediation |
| --- | --- | --- | --- | --- | --- | --- | --- |
| P01-A11Y-01 | WCAG AA minimum, keyboard navigation, screen-reader labels, visible focus, color-independent status | P0 | Automated + manual audit | Matches `02_UI_Spec.md` §20 | DEFERRED | UX Reviewer | — |

## 12. Responsive

*(empty — `02_UI_Spec.md` Responsive Rules are only Partial; the five required breakpoints — 1920/1600/1440/1280/1024 — are not individually specified yet)*

## 13. Performance

*(empty — depends on `04_Technical_Spec.md` §22 Performance Budget, currently BLOCKED)*

## 14. Code and Architecture

*(empty — depends on `04_Technical_Spec.md`, currently BLOCKED)*

## 15. Security and Permissions

*(empty — depends on `04_Technical_Spec.md` §25 Permissions, currently BLOCKED)*

## 16. Visual Regression

*(empty — depends on a canonical 1440×1024 reference render, not yet produced; see Contract §87)*

## 17. Final User Experience

| criterion_id | requirement | priority | test_method | expected | status | owner | remediation |
| --- | --- | --- | --- | --- | --- | --- | --- |
| P01-UX-01 | Does this feel like a scientific engineering operating system, not a generic dashboard or chatbot? | P0 | Design/product review | Reviewer answers Yes with justification | DEFERRED | Product Owner | Contract §101 Final Experience Questions |
| P01-UX-02 | Can a PI understand the current decision quickly? | P0 | Task-based usability test | Matches Contract §9 Product-Wide Success Criteria | DEFERRED | Product Owner | — |

---

## Coverage Summary

| Checklist domain | Records | Status |
| --- | --- | --- |
| 1 Product/Mission | 5 | DEFERRED |
| 2 Functional | 0 | not yet authorable |
| 3 UI/Design System | 2 | DEFERRED |
| 4 Scientific Content | 1 | DEFERRED |
| 5 Evidence/Traceability | 1 | DEFERRED |
| 6 Human Governance | 2 | DEFERRED |
| 7 Backend Truthfulness | 0 | not yet authorable |
| 8 Interaction | 0 | not yet authorable |
| 9 State/Persistence | 0 | not yet authorable |
| 10 Loading/Empty/Partial/Error | 4 | DEFERRED |
| 11 Accessibility | 1 | DEFERRED |
| 12 Responsive | 0 | not yet authorable |
| 13 Performance | 0 | not yet authorable |
| 14 Code/Architecture | 0 | not yet authorable |
| 15 Security/Permissions | 0 | not yet authorable |
| 16 Visual Regression | 0 | not yet authorable |
| 17 Final UX | 2 | DEFERRED |

Per Contract §82 Output rule, a single global `PASS` is invalid while any domain is untested or
`UNKNOWN` — this document does not claim one. Overall Acceptance status: **BLOCKED** (7 of 17 domains
have no criteria at all; the remaining 10 domains are fully `DEFERRED`, i.e. authored but untested).
