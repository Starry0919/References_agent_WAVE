```yaml
page_id: page-01
page_name: Project Command Center
spec_type: Interaction Spec
version: 0.1.0
status: Draft
owners:
  - Product Owner
reviewers:
  - UX Reviewer
  - Frontend Architect
parent_contract: Page Design Contract v1.2.0
parent_architecture: Frontend Architecture Prompt v1.2
last_updated: 2026-07-23
dependencies:
  - 01_Product_Spec.md
  - 02_UI_Spec.md
open_questions:
  - Most §79 required sections (see coverage table) have no approved Page 1 content and are marked
    GAP below. They require dedicated interaction design work, not fabrication in this pass.
approved_exceptions: []
```

> **Provenance note (2026-07-23)**: this file replaces `Page1/03_Operating_Principles.md`, which did
> not contain Page 1 interaction content — it was a discussion draft proposing a global, cross-page
> "Operating Constitution" document (relocated, verbatim, to
> `Page1/references/Proposal_Global_Operating_Constitution.md`). This file instead assembles the
> genuinely Page-1-specific interaction fragments that already existed inside the approved
> `01_Product_Spec.md` and `02_UI_Spec.md`, and honestly marks everything else as `GAP`. No new
> interaction behavior has been designed or invented here.

---

## 1. Interaction Model

Partial. `01_Product_Spec.md` §06 (User Journey) establishes the outer loop: Open → Understand
project → Understand engineering state → Review evidence → Review risks → Approve or investigate →
Navigate into detailed workspace → Continue engineering. `01_Product_Spec.md` §09 (Decision
Architecture) establishes that every interactive element must help answer one of: What happened? Why?
How certain? Can this be trusted? What evidence? Approve/reject? What's next? These are approved
product-level constraints on interaction, not a full Selection-Driven / Master-Detail interaction
model per Global Contract §37. `GAP` for the formal model statement.

## 2. Navigation

Partial. `01_Product_Spec.md` §06 states the page must hand off into a "detailed workspace" and must
never become the workspace itself. Which specific routes/deep links this hands off to, and how
breadcrumb/back-navigation behaves, is `GAP`.

## 3. Selection Model

`GAP`. No selection behavior is defined for Page 1's cards/modules.

## 4. Click

`GAP`.

## 5. Hover

`GAP`. (`02_UI_Spec.md` §13 gives a hover *timing* value — 100–150ms — but not hover *content/behavior*.)

## 6. Expand / Collapse

`GAP`. `02_UI_Spec.md` §13 gives a generic "Panel Transition" timing (200–250ms) but no expand/collapse
trigger or scope is defined for Page 1.

## 7. Inspector

`GAP`. `02_UI_Spec.md` §02 and §15 name an "Inspector Panel" / "Floating Panel" as layout regions, and
§09 states "Drawer provides detail," but no inspector content composition, trigger, or update-on-
selection behavior is defined.

## 8. Evidence Drawer

`GAP`. Not defined for Page 1 specifically. Global Contract §36 (Evidence Drawer Contract) applies by
default until a page-specific composition is authored.

## 9. Search

`GAP`.

## 10. Filter and Sort

`GAP`.

## 11. Comparison

Partial. `01_Product_Spec.md` §00 lists "Compare active design candidates" as a user action reachable
from this page, but Page 1 itself does not perform comparison — it hands off to
`DBTL Engineering Workspace`. No comparison UI is defined on Page 1, consistent with §00's "The page
is NOT responsible for... Engineering design."

## 12. Timeline

Partial. `02_UI_Spec.md` §09 names "Timeline shows evolution" as a component responsibility, and §11
lists Timeline as a preferred visualization. No event schema (actor/action/object/timestamp/result per
Global §43) is defined for Page 1's timeline instance.

## 13. Provenance Inspection

`GAP`. Not defined for Page 1 (Trust & Provenance Center owns full provenance browsing per parent
architecture §10; Page 1 needs a local provenance entry point, per Global §8.6 Traceable by Default,
which is not yet specified here).

## 14. AI Interaction

`GAP`. `01_Product_Spec.md` §10 (Backend Responsibilities) states the frontend "NEVER performs
scientific reasoning" and lists backend-owned responsibilities (scientific reasoning, knowledge
retrieval, evidence scoring, simulation, workflow orchestration, engineering planning, risk
evaluation, validation generation), which constrains AI interaction design but does not define it
(no inspect-basis, regenerate, accept/reject affordances specified for this page).

## 15. Draft and Commit

`GAP`. Not applicable to most of Page 1 per §00 ("NOT responsible for... Editing experiments...
Editing workflows"), but the page does surface approvals (§16 below), so a minimal draft/commit
question may still apply there — not yet specified.

## 16. Review and Approval

Partial. `01_Product_Spec.md` §00 lists "surfacing pending approvals" as a page responsibility, and
§06 lists "Approve or investigate" as a journey step. No approval interaction detail (what is shown
before approval, reviewer role requirement, reject/override reason capture per Global §46) is defined
for Page 1 — approval is expected to be *initiated* here and *completed* in the Workspace or Trust &
Provenance Center, but this handoff is not explicitly specified.

## 17. Keyboard Shortcuts

`GAP`.

## 18. Undo / Redo

`GAP`. Likely low-relevance for Page 1 (a largely read/summary surface) but not explicitly scoped out.

## 19. Error Recovery

Partial. `02_UI_Spec.md` §18 (Error States) specifies that errors must explain what happened, why,
suggested recovery, and expandable technical detail, and must never show raw stack traces. This is a
visual/content contract, not a full Global §51 Error Recovery flow (what remains safe / whether data
were saved / whether retry is safe) — those are `GAP`.

## 20. Notifications

`GAP`. Not defined; Global §48 (Toast / Inline Alert / Banner / Attention Queue) applies by default.

## 21. Context Menu

`GAP`.

## 22. Focus Management

`GAP`. `02_UI_Spec.md` §20 (Accessibility) requires "visible focus states" generally but does not
define per-region focus order.

## 23. Context Preservation

`GAP` for Page 1 specifically. Global §8.5 (Persistent Workspace) and the parent architecture §6.6
(Persistent Location Model) apply by default; no Page-1-specific statement of what must survive
navigation exists yet.

## 24. Deep Linking

`GAP`. Parent architecture §6.3 defines the general deep-link pattern
(`/projects/:projectId`); Page 1 has not specified which of its own regions are independently
deep-linkable.

## 25. Permission Behavior

`GAP`.

## 26. Analytics / Event Instrumentation

`GAP`.

---

## Coverage Summary

| Status | Count (of 26) |
| --- | --- |
| Covered | 0 |
| Partial | 8 |
| `GAP` | 18 |

**Recommended next step (decision, not executed here):** this document cannot reach `status:
Approved` or pass Gate 1/2 in its current state. The page owner should commission a dedicated
Interaction Spec authoring pass covering at minimum Selection Model, Inspector, Evidence Drawer,
Review and Approval, Context Preservation, and Deep Linking before Page 1 proceeds past Gate 1.
