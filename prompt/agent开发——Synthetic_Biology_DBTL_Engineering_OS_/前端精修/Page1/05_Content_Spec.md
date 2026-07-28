```yaml
page_id: page-01
page_name: Project Command Center
spec_type: Content Spec
version: 0.1.0
status: Draft
owners:
  - Product Owner
reviewers:
  - Synthetic Biology Reviewer
parent_contract: Page Design Contract v1.2.0
parent_architecture: Frontend Architecture Prompt v1.2
last_updated: 2026-07-23
dependencies:
  - 01_Product_Spec.md
  - 02_UI_Spec.md
open_questions:
  - Most §81 required sections have no approved Page 1 content at field level and are marked GAP.
approved_exceptions: []
```

> **Provenance note (2026-07-23)**: this file did not exist before Spec Package normalization. It
> assembles the scientific-content-relevant fragments already present in the approved
> `01_Product_Spec.md` and `02_UI_Spec.md`, and marks the detailed, field-level content requirements
> of Contract §81 as `GAP` where no approved source exists. No scientific object, field, or claim was
> invented to fill these gaps.

---

## 1. Scientific Question Supported

Inherited from `01_Product_Spec.md` §01: "What is happening in my engineering project right now?"
— decomposed by §03 (Product Philosophy) into: What are we trying to achieve? Why are we doing this?
How confident are we? What evidence supports it? What risks remain? What should happen next? Who
needs to decide?

## 2. Scientific Objects

Partial. `01_Product_Spec.md` §04 (Mental Model) names, in order: Project → Current Iteration →
Engineering Objective → Scientific Bottleneck → Engineering Strategy → Supporting Evidence →
Validation Plan → Remaining Risks → Next Action → Future Iteration. This aligns with, but does not
use identical labels to, the Global Contract §13 Scientific Object Hierarchy (Project / DBTL Cycle /
Engineering Decision, etc.) and the parent architecture §12 hierarchy (Project → DBTL Cycle →
Scientific Question → Observation → Hypothesis → Engineering Design → ...). `GAP`: no field-level
object definitions (id/type/title/status/owner/... per Global §14) exist for any of these objects as
they appear on Page 1.

## 3. Object Relationships

`GAP`. No relationship diagram or mapping exists for how Page 1 surfaces relationships between
Project / Cycle / Bottleneck / Strategy / Evidence / Risk / Next Action.

## 4. Required Fields

`GAP`. No per-object required-field list exists.

## 5. Content Hierarchy

Covered. `01_Product_Spec.md` §08 (Information Architecture): Level 1 (Global Awareness: Current
Objective, Current Stage, Project Health, Critical Alerts, Next Action) → Level 2 (Engineering
Status, Evidence Summary, Simulation Status, Knowledge Updates, Pending Reviews, Project Timeline) →
Level 3 (Scientific Reports, Historical Iterations, Execution Logs, Prompt History, Raw Evidence).
"Everything deeper than Level 3 belongs to another page."

## 6. Default Visible Content

Covered by Level 1 above (§5). No separate statement exists distinguishing "default visible" from
"Level 1" — treated as equivalent here.

## 7. Progressive Disclosure Content

Partial. Levels 2–3 above function as the progressive-disclosure content, consistent with Global
Contract §8.3. No statement of *how* disclosure is triggered (expand, drawer, navigation) exists —
that belongs in `03_Interaction_Spec.md`, where it is currently `GAP`.

## 8. Scientific Cards and Fields

Partial. `02_UI_Spec.md` §10 (Card Library) gives a generic card contract (Purpose / Status /
Evidence / Action, one scientific topic per card) but no per-card-type field list (e.g., what
specifically appears on a "Bottleneck" card vs. a "Pending Approval" card).

## 9. Evidence Hierarchy

`GAP` at Page-1-specific level. Global Contract §16 defines the system-wide Evidence Hierarchy
(primary observation → processed result → curated evidence/DDR → rule/mechanism → inference →
recommendation); Page 1 has not stated which levels of this hierarchy it surfaces vs. defers to the
Evidence Drawer / Knowledge & Evidence Layer.

## 10. Claim–Evidence Mapping

`GAP`. No Scientific Claim Contract (Global §53 YAML) instances exist for Page 1 content.

## 11. Confidence and Uncertainty

`GAP` at field level. `01_Product_Spec.md` §09 asks "How certain are we?" as a decision question but
does not specify confidence representation (label/band/method per Global §17.1) for Page 1.

## 12. Provenance Requirements

`GAP` at field level. `01_Product_Spec.md` §00 lists "exposing scientific evidence" as a
responsibility; no provenance display requirement is specified.

## 13. Scientific Terminology

Not duplicated here — governed by the parent architecture §4A.2 Terminology Contract (Diagnose /
Design / Simulate / Critique / Build-Test Plan / Evidence / Knowledge / Memory / Provenance /
Approval / Observation / Prediction). Page 1 has not identified which of these terms it surfaces
directly, but per the Terminology Contract it must not invent synonyms if it does.

## 14. Units and Numerical Formatting

`GAP`. No Page 1 content specifies numeric values requiring units (Global §54 applies by default:
tabular numerals, explicit units, distinguish 0/not-detected/missing/not-measured/not-applicable —
none of this has been instantiated for Page 1's specific fields, since no specific numeric field is
yet defined per §4 above).

## 15. Visualization Selection

Partial. `02_UI_Spec.md` §11 (Data Visualization Rules) and §12 (Scientific Visualization Rules) name
preferred forms (Timeline, Progress, Distribution, Comparison, Trend for general data; Network,
Metabolic Pathway, Gene Interaction, Evidence Graph, Timeline, Validation Flow for scientific data)
and forbid decorative 3D/gauges/animated numbers. Not yet mapped to specific Page 1 content items
(§2 above) per the Global §55 Visualization Selection table.

## 16. Tables and Columns

`GAP`. No table content is defined for Page 1 (consistent with §00 of `01_Product_Spec.md`: Page 1
is not responsible for "database browsing").

## 17. Reports and Exports

`GAP`. `01_Product_Spec.md` §14 explicitly excludes "A report page" as a Page 1 responsibility; no
report/export behavior is expected on this page, but this has not been formally recorded as a
Non-Goal cross-reference in this Content Spec until now.

## 18. Empty Scientific State

Partial. `02_UI_Spec.md` §16 (Empty States) requires explaining why data is absent, how to obtain it,
and the next action, and forbids blank cards. Global §60's specific empty-state taxonomy (not
created / not imported / not measured / no result / filtered out / inaccessible / backend
unavailable / not applicable) has not been mapped per Page-1 object type.

## 19. Partial and Contradictory Evidence

`GAP`. Not addressed anywhere in existing Page 1 content.

## 20. Sample Content / Fixtures

`GAP`. No fixture data exists for Page 1 in this Spec package. Parent architecture §15.4 requires any
sample data to use the E. coli K-12 L-tryptophan case, be labeled DEMO/MOCK, and never be presented as
a real project — this constraint applies by default once fixtures are authored, but none exist yet.

## 21. Scientific Review Questions

Covered indirectly. `01_Product_Spec.md` §09 (Decision Architecture) provides a set of standing
questions every module must answer (What happened? Why? How certain? Trustworthy? Evidence? Approve/
reject? Next?) which substantially overlaps with the Global Contract §89.3 Scientific Review
Checklist (Mechanism / Evidence / Trade-off / Limitation / Validation), but has not been explicitly
cross-mapped to that five-item checklist.

---

**Recommended next step (decision, not executed here):** the `GAP` items above (particularly §2–4,
§9–12, and §16–20) require a dedicated Content Spec authoring pass, ideally done jointly with a
Synthetic Biology Reviewer, before Gate 1 can pass.
