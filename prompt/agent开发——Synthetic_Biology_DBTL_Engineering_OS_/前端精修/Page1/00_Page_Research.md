```yaml
page_id: page-01
page_name: Project Command Center
spec_type: Page Research
version: 0.1.0
status: Draft
owners:
  - Product Owner
reviewers:
  - UX Reviewer
parent_contract: Page Design Contract v1.2.0
parent_architecture: Frontend Architecture Prompt v1.2
last_updated: 2026-07-23
dependencies: []
open_questions:
  - Full Benchmark Records (§76 Benchmark Rule) for each reference product have not been authored
    and are out of scope for this normalization pass. See "Research Gaps" below.
approved_exceptions: []
```

> **Provenance note (2026-07-23)**: this file did not exist before Spec Package normalization. No
> dedicated, evidence-backed benchmark study (per Contract §76 Benchmark Rule — `reference /
> observed_pattern / user_problem_solved / why_it_works / limitations / transfer_to_this_product /
> do_not_copy`) currently exists for Page 1. Rather than fabricate specific claims about how named
> products behave, this document (a) records the reference product list already inherited from the
> approved parent architecture (`前端整体架构设计.md` §13.1), (b) extracts the practices Page 1's own
> approved `01_Product_Spec.md` and `02_UI_Spec.md` already committed to adopting or avoiding, and
> (c) leaves the comparative benchmark analysis itself as an explicit open gap for the page owner /
> UX researcher to complete before Gate 1 sign-off.

---

## 1. Research Question

What layout, information-density, and trust-communication patterns allow a Principal Investigator to
assess overall project state, current bottleneck, and pending decisions within a short, bounded
reading time, without the page collapsing into either (a) a generic KPI dashboard or (b) a chat
interface? — This question is inherited directly from `01_Product_Spec.md` §01 (Mission Statement,
"within ten seconds") and §03 (Product Philosophy).

## 2. Target Workflow and User Context

Inherited from `01_Product_Spec.md` §05 (User Personas) and §06 (User Journey): PI, Synthetic Biology
Researcher, Wet Lab Scientist, Dry Lab Scientist, and Student, each opening the page to answer "where
does the project stand and what needs my attention," then navigating into a deeper workspace. See
`01_Product_Spec.md` for the full persona detail; not duplicated here.

## 3. Product Benchmarks

`GAP` — No per-product Benchmark Record exists. Reference list inherited (not independently
re-verified in this pass) from `前端整体架构设计.md` §13.1: Benchling, Galaxy, IDE (persistent
workspace / inspector pattern), GitHub (versions / review / history), NASA mission control (status /
risk / decision framing), genome browsers (high-density scientific information with context). Each
requires an individual Benchmark Record before this section can be marked `Covered`.

## 4. Layout Benchmarks

`GAP` — see §3. `01_Product_Spec.md` §08 (Information Architecture, Level 1–3) and `02_UI_Spec.md`
§02 (Layout System) already encode layout *decisions*; what is missing is the benchmark evidence that
those decisions were derived from a comparative study rather than asserted directly.

## 5. Interaction Benchmarks

`GAP`. No page-specific interaction benchmark analysis exists. See `03_Interaction_Spec.md` for the
current state of interaction content (mostly also `GAP`, migrated from Product/UI Spec fragments).

## 6. Information Density Benchmarks

`GAP`. `02_UI_Spec.md` §03 (Spatial System) asserts density principles ("the page should breathe")
without citing comparative benchmarks.

## 7. Scientific Visualization Benchmarks

`GAP`. `02_UI_Spec.md` §12 (Scientific Visualization Rules) names required visualization types
(network, metabolic pathway, gene interaction, evidence graph, timeline, validation flow) but does
not cite specific tools or studies these were derived from.

## 8. Evidence and Provenance Benchmarks

`GAP`. Not present in any existing Page 1 file.

## 9. Animation and Feedback Benchmarks

`GAP`. `02_UI_Spec.md` §13 (Motion System) specifies timing values (100–150ms hover, 200–250ms panel,
250ms drawer) but does not cite the benchmark source for these values.

## 10. Accessibility Benchmarks

`GAP`. `02_UI_Spec.md` §20 states a WCAG AA target without benchmark comparison.

## 11. Good Practices to Adopt

Extracted from Page 1's own already-approved commitments (not external benchmark analysis, but
legitimate existing content):

- Clarity over decoration; every visual element must improve understanding (`02_UI_Spec.md` §01).
- Progressive disclosure — only the most important information appears initially (`02_UI_Spec.md` §01, §03).
- Persistent, spatially stable workspace — components must not jump unexpectedly (`02_UI_Spec.md` §01).
- Every widget must help answer a decision question, not merely display data (`01_Product_Spec.md` §09).
- Scientific First / Evidence Before Conclusion / Human Before Agent design principles (`01_Product_Spec.md` §12).

## 12. Bad Practices to Avoid

Directly inherited from `02_UI_Spec.md` §21 (UI Anti-patterns) and `01_Product_Spec.md` §14
(Explicit Non-goals) — not duplicated here in full; see those sections. Summary: no long scrolling
dashboards, no marketing hero sections, no glassmorphism/neon/animated backgrounds, no card overload,
no chat-style layout, and the page must never become a workflow/experiment/knowledge editor or a
chatbot.

## 13. Transferability Analysis

`GAP`. Requires §3–§10 to be completed first; a transferability judgment without the underlying
benchmark evidence would be unsupported.

## 14. Derived Page Design Principles

Already covered by `01_Product_Spec.md` §12 (Design Principles) and `02_UI_Spec.md` §01 (Visual
Philosophy) — cross-referenced here rather than restated, since the principles predate and do not
depend on the missing benchmark sections above.

## 15. Research Gaps and Unresolved Questions

- No individual Benchmark Records exist for any reference product (§3–§10 above).
- No transferability analysis exists (§13).
- It is an open product decision whether Page 1 requires a dedicated UX benchmarking pass before
  Gate 1, or whether the existing derived principles (§14, already approved) are considered
  sufficient justification to proceed without one. This normalization pass does not decide that
  question — it is recorded as an open question for the page owner.
