```yaml
page_id: page-01
page_name: Project Command Center
spec_type: UI Spec
version: 2.1.0
status: Approved
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
  - 03_Interaction_Spec.md
  - 04_Technical_Spec.md
open_questions:
  - See "Part Z — Contract Cross-Reference & Gap Map" appendix at the end of this document
approved_exceptions: []
```

> **Spec Package normalization note (2026-07-23)**: this document's body (Sections 00–22 below) is
> the pre-existing, approved Page 1 UI definition (previously versioned "v2.0"). Its text has **not
> been rewritten, reworded, or reorganized** during normalization — only this header and the
> "Contract Cross-Reference & Gap Map" appendix at the end were added, to satisfy Page Design
> Contract v1.2.0 §75 (Spec Header) and to make required-section coverage traceable per §78. No
> visual direction was changed. One pre-existing conflict against the Global Color Tokens (§23) is
> flagged, not resolved, in the appendix — see the note there before treating §07 Color System below
> as implementation-ready.

---

# ============================================================
# Synthetic Biology DBTL Engineering OS
# UI Specification
# Page 01 — Project Command Center
# Version: v2.0
# ============================================================

> This document defines the visual language of the Project Command Center.
>
> It is NOT a mockup.
>
> It defines how the interface should feel, communicate,
> prioritize information and build scientific trust.

---

# 00. Visual Identity

The Project Command Center should immediately communicate:

Professional

Scientific

Reliable

Calm

Transparent

Human-Governed

Never:

Fancy

Gaming

Futuristic for its own sake

AI toy

Marketing website

Users should feel they are entering a scientific operating system rather than a website.

---

# 01. Visual Philosophy

The interface follows five principles.

## Clarity over Decoration

Every visual element exists to improve understanding.

No decorative graphics.

No meaningless illustrations.

No visual noise.

---

## Information before Interaction

Users should understand the project before interacting with it.

Layout must guide understanding naturally.

---

## Progressive Disclosure

Only the most important information appears initially.

Scientific depth is revealed gradually.

Never overwhelm users.

---

## Persistent Workspace

The interface should always feel stable.

Components should not jump unexpectedly.

Layout should remain spatially predictable.

---

## Scientific Credibility

Every design choice should reinforce scientific trust.

Avoid exaggerated animations.

Avoid emotional colors.

Avoid attention-seeking effects.

---

# 02. Layout System

The page follows a persistent application shell.

Header

↓

Global Navigation

↓

Workspace

↓

Inspector Panel

↓

Footer Status

Each region has a permanent responsibility.

The layout must never become a scrolling landing page.

---

# 03. Spatial System

Whitespace is functional.

Spacing communicates hierarchy.

Use large spacing between major scientific concepts.

Use medium spacing between modules.

Use small spacing inside components.

Never compress unrelated information.

The page should breathe.

---

# 04. Grid System

Desktop First

1920px optimized

12-column responsive grid

Maximum readable width:

1600px

Consistent vertical rhythm

All modules align to grid.

Never allow floating components.

---

# 05. Visual Hierarchy

Hierarchy follows scientific importance.

Level 1

Project Objective

Current Stage

Project Health

Critical Alerts

---

Level 2

Engineering Status

Evidence

Simulation

Knowledge

---

Level 3

Historical Activity

Reports

Logs

Metadata

No lower-priority information should visually dominate higher-priority content.

---

# 06. Design Tokens

Border Radius

Consistent

Medium rounded corners

Elevation

Minimal

Only enough to separate layers.

Borders

Soft

Subtle

Readable

Shadow

Very light.

Never floating card style.

---

# 07. Color System

Color communicates meaning.

Never decoration.

Blue

System information

Scientific state

Green

Validated

Completed

Safe

Yellow

Needs review

Awaiting approval

Orange

Warning

Risk

Red

Critical issue

Failure

Purple

Knowledge

Memory

Evidence

Gray

Inactive

Historical

Metadata

Never use color as the only indicator.

---

# 08. Typography System

Typography communicates hierarchy.

Page Title

Largest

Workspace Title

Second

Section Title

Third

Body

Readable

Metadata

Small

Code

Monospace

Numbers

Tabular alignment

Avoid excessive font weights.

---

# 09. Component Language

Every component has one responsibility.

Cards summarize.

Panels explain.

Tables compare.

Timeline shows evolution.

Drawer provides detail.

Dialog requests confirmation.

Never mix responsibilities.

---

# 10. Card Library

Cards are the fundamental information unit.

Each card contains

Purpose

Status

Evidence

Action

No card should exceed one scientific topic.

Cards should always answer one question.

---

# 11. Data Visualization Rules

Charts exist only when they reveal patterns.

Never use charts for decoration.

Prefer

Timeline

Progress

Distribution

Comparison

Trend

Avoid

3D pie charts

Decorative gauges

Animated numbers

Scientific meaning comes first.

---

# 12. Scientific Visualization Rules

Biological information should use domain-specific visualization.

Network

Metabolic pathway

Gene interaction

Evidence graph

Timeline

Validation flow

Do not replace scientific diagrams with generic business charts.

---

# 13. Motion System

Animation should communicate state.

Never entertainment.

Hover

100–150ms

Panel Transition

200–250ms

Drawer

250ms

Page Transition

Minimal

Respect reduced-motion settings.

---

# 14. Iconography

Icons reinforce recognition.

DNA

Gene

Flask

Experiment

Book

Knowledge

Shield

Validation

Clock

Timeline

Warning

Risk

Icons never replace text.

---

# 15. Depth & Elevation

Depth communicates ownership.

Workspace

Base layer

Floating Panel

+1

Modal

Highest

Never stack unnecessary floating layers.

---

# 16. Empty States

No scientific data available.

Explain:

Why

How to obtain it

Next action

Never show blank cards.

---

# 17. Loading States

Skeleton UI only.

Never spinning forever.

Maintain layout stability.

Avoid content shifting.

---

# 18. Error States

Errors should explain:

What happened

Why

Suggested recovery

Technical details (expandable)

Never display raw stack traces.

---

# 19. Responsive Rules

Priority

Desktop

Laptop

Tablet

Mobile

The system is optimized for professional desktop use.

Mobile focuses on awareness rather than full operation.

---

# 20. Accessibility

WCAG AA minimum.

Keyboard navigation.

Screen reader labels.

Visible focus states.

Color-independent status indication.

---

# 21. UI Anti-patterns

The following are forbidden.

Long scrolling dashboards

Marketing hero sections

Glassmorphism

Neon effects

Animated backgrounds

Large decorative illustrations

Card overload

Nested scrollbars

Inconsistent spacing

Hidden navigation

Chat-style layouts

Scientific credibility always outweighs visual novelty.

---

# 22. Visual Constitution

Every visual decision should answer:

Does this improve scientific understanding?

Does this reduce cognitive load?

Does this increase trust?

Does this reinforce the identity of a Scientific Operating System?

If not, it should not exist.

The Project Command Center should look timeless, calm, rigorous and authoritative.

It should resemble the control room of a modern scientific laboratory rather than a consumer application.

---

# Part Z — Contract Cross-Reference & Gap Map

> Added during Spec Package normalization (2026-07-23). Maps this document's existing sections
> (00–22 above) to Page Design Contract v1.2.0 §78 Required Sections. Nothing in Sections 00–22 was
> altered to produce this map. Items marked `GAP` are genuinely absent from the approved content and
> are **not** invented here.

| §78 Required Section | Coverage | Source in this document |
| --- | --- | --- |
| Page Anatomy | Partial | §02 Layout System (named regions; no annotated diagram) |
| Layout Grid | Covered | §04 Grid System |
| Canonical Regions | Covered | §02 Layout System (Header / Global Navigation / Workspace / Inspector Panel / Footer Status) |
| Visual Hierarchy | Covered | §05 Visual Hierarchy |
| Reading Order | `GAP` | Not explicit |
| Information Density | Partial | §03 Spatial System (spacing rationale only; no explicit Guided/Expert density-mode declaration per Global §27) |
| Page-Specific Component Inventory | Partial | §09 Component Language, §10 Card Library (component roles named; no per-component `component/purpose/priority/default_state/interactive_states/...` record per Global §78 Component Record) |
| Shared Component Reuse Matrix | `GAP` | Not present |
| Card and Panel Definitions | Partial | §10 Card Library (generic contract: Purpose/Status/Evidence/Action; no per-card-type field list) |
| Table Definitions | `GAP` | Tables named only as a responsibility ("Tables compare", §09); no column/sort/filter/export definition |
| Chart and Visualization Definitions | Partial | §11 Data Visualization Rules, §12 Scientific Visualization Rules (principles only; no per-chart question/data-source/axes/uncertainty definition per Global §56) |
| Inspector / Drawer Composition | `GAP` | §02 and §15 name "Inspector Panel" / "Floating Panel" as layout regions; no content composition defined |
| State Presentation | Partial | §07 Color System assigns state meaning; not cross-checked against Global §15 Status Language or paired with non-color redundant encoding |
| Empty State | Covered | §16 Empty States |
| Loading State | Covered | §17 Loading States |
| Partial / Stale / Offline State | `GAP` | Only generic Loading/Error covered; stale, partial-data, and offline/unavailable states (required by Global §14.4 / INV-008) are not addressed |
| Error State | Covered | §18 Error States |
| Responsive Rules at 1920 / 1600 / 1440 / 1280 / 1024 | Partial | §19 Responsive Rules gives a priority order (Desktop > Laptop > Tablet > Mobile) and one max-width (1600px), not the five explicit breakpoint behaviors required by Global §20.3 |
| Accessibility Layout Requirements | Partial | §20 Accessibility lists WCAG AA / keyboard / focus / color-independence generically; not tied to specific layout regions |
| Motion and Transition | Covered | §13 Motion System |
| Nanobanana Composition Constraints | `GAP` | Not present — required before any Nanobanana generation request per Global §86 |
| Visual Do / Don't | Partial | §21 UI Anti-patterns covers "Don't"; no itemized "Do" list (Do is implied throughout the document but not enumerated) |
| Annotated Wireframe | `GAP` | No wireframe or diagram asset exists in this package |

## Flagged conflict — not resolved by this normalization pass

**§07 Color System (this document) vs. Global Contract §23.3 Semantic State tokens.** This
document's §07 defines page-local color semantics (Blue = system information/scientific state,
Green = validated/completed/safe, Yellow = needs review/awaiting approval, Orange = warning/risk,
Red = critical/failure, Purple = knowledge/memory/evidence, Gray = inactive/historical/metadata).
The Global Contract §23.3 defines a fixed semantic token set (`--success`, `--warning`, `--danger`,
`--info`, `--unknown`) and INV-007 prohibits a page from creating private color semantics. This
predates Contract v1.2.0 registration and has **not been altered or reconciled here**, per the
instruction not to redesign approved visual direction. It is recorded as an open conflict requiring
either (a) an approved mapping from this page-local palette onto the Global tokens, or (b) a
documented Page Exception Record (§4) if a deliberate deviation is intended (e.g. Purple for
Knowledge/Evidence has no Global equivalent and would need one). This must be resolved before Gate 2
(Design) can pass.

**Recommended next step (decision, not executed here):** the page owner should reconcile §07 against
Global §23, then decide on the `GAP` items above the same way as in `01_Product_Spec.md` Part Z.