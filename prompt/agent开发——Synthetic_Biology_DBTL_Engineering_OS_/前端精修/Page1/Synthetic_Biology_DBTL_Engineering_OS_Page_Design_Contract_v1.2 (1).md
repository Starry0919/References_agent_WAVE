# Synthetic Biology DBTL Engineering OS

# Page Design Contract v1.2

> **Document type**: Project-wide design contract  
> **Status**: Normative / Single Source of Truth  
> **Applies to**: Product definition, page research, UI design, Nanobanana image generation, frontend implementation, scientific content, interaction, QA, and acceptance  
> **Product positioning**: Persistent, Traceable, Human-Governed DBTL Engineering System  
> **Parent architecture**: `Synthetic_Biology_DBTL_Engineering_OS_前端整体架构设计_Prompt.md` v1.2  
> **Default language**: English product UI; Chinese may be used in specifications and implementation notes  
> **Contract version**: 1.2.0  
> **Version date**: 2026-07-23  

---

## 0. Purpose of This Contract

This document prevents visual, interaction, scientific, and engineering drift across Page 1, Page 2, Page 3, Page 4, and all future modules.

It is not a mood board, a one-page UI brief, or a component inventory. It is the binding contract shared by:

- product owners;
- synthetic biology experts;
- PI, dry-lab, and wet-lab users;
- UX and visual designers;
- Nanobanana or other visual generators;
- Claude Code or other implementation agents;
- frontend maintainers;
- reviewers and acceptance testers.

Every page must inherit this contract. A page specification may add page-specific rules, but may not silently override global rules.

The desired result is one coherent research operating system—not a collection of individually attractive screens.

---

# Part I — Contract Governance

## 1. Sources of Truth and Precedence

When requirements conflict, apply the following precedence:

1. **Scientific truth and safety**
2. **Real backend capability, schema, and provenance**
3. **This Page Design Contract**
4. **Approved page-specific Specs**
5. **Approved reference design or Nanobanana image**
6. **Implementation convenience**

Consequences:

- A generated image may never override scientific meaning, data state, or workflow logic.
- A page-specific Spec may introduce a justified exception only through an explicit Exception Record.
- Claude Code must not invent backend capabilities to reproduce a visual.
- Visual fidelity means fidelity to the approved contract and design—not blind copying of scientifically incorrect pixels.

## 2. Normative Language

- **MUST / 必须**: required for acceptance.
- **MUST NOT / 禁止**: disallowed.
- **SHOULD / 应**: expected unless a documented reason exists.
- **MAY / 可**: optional.
- **DEFERRED / 延后**: intentionally outside the current implementation scope.

Words such as “professional,” “clean,” “advanced,” or “scientific” are not sufficient requirements unless translated into measurable rules.

## 3. Change Control

Any change to this contract must include:

```yaml
change_id:
date:
author:
affected_rules:
reason:
affected_pages:
migration_required:
visual_regression_required:
scientific_review_required:
approval_status:
```

Global tokens, core component behavior, object semantics, evidence levels, approval states, or navigation patterns may not be changed inside a single page implementation.

### 3.1 Contract Version Policy

This contract uses semantic versioning:

| Version | Meaning | Examples | Required action |
| --- | --- | --- | --- |
| **Major** `X.0.0` | Breaking contract change | navigation model, scientific object semantics, approval workflow, component API | migration plan, impact review, all affected pages revalidated |
| **Minor** `x.Y.0` | Backward-compatible capability or enforceable rule | shared component, acceptance gate, optional state | affected Specs updated; targeted regression |
| **Patch** `x.y.Z` | Editorial clarification without behavioral change | typo, example clarification, non-normative wording | changelog entry; no migration unless stated |

Every page Spec MUST declare the exact parent contract version. A page MUST NOT silently consume a newer Major version. Minor-version adoption must be recorded when it changes page acceptance. Patch versions may be adopted automatically only when runtime behavior is unchanged.

### 3.2 Compatibility and Migration

- The root `CHANGELOG.md` MUST state added, changed, deprecated, removed, and migration-required rules.
- Deprecated tokens or components MUST include a replacement and removal version.
- A global change MUST identify affected pages and shared components before implementation.
- Mixed contract versions may exist temporarily only with a documented migration window.
- A page MUST NOT locally imitate a new global rule while the shared system remains on an older version.

## 4. Page Exception Record

If a page must depart from a global rule, its Spec must include:

```yaml
exception_id:
global_rule:
page:
scientific_or_product_reason:
scope:
fallback:
reviewer:
approval_status:
expiry_or_review_date:
```

An undocumented exception is a defect.

## 5. Definition of “No Drift”

A page is considered consistent only when all five layers remain aligned:

1. **Product** — the page answers the correct research question.
2. **Scientific content** — objects, evidence, uncertainty, and provenance use the shared model.
3. **Interaction** — selection, inspection, disclosure, approval, and recovery behave consistently.
4. **Visual system** — tokens, typography, spacing, components, charts, and states are reused.
5. **Engineering** — shared shell, components, types, adapters, and state ownership are reused.

Passing only visual comparison is not sufficient.

## 5.1 System Invariants

The following invariants are absolute. No Page Spec, generated design, local
optimization, DSR, ADR, exception, deadline, or implementation convenience may
override them.

| ID | Invariant | Non-negotiable requirement |
| --- | --- | --- |
| `INV-001` | Scientific Truth | Never alter, simplify, imply, or fabricate scientific meaning to satisfy a layout or demo. |
| `INV-002` | Evidence Traceability | Every consequential scientific claim and recommendation remains traceable to its evidence, assumptions, uncertainty, and provenance. |
| `INV-003` | Human Governance | Agent output is proposed, not approved or executed; consequential transitions require an authorized human decision. |
| `INV-004` | Persistent Context | Project, cycle, stage, object, version, draft, selection, and review context must survive expected navigation and recovery boundaries. |
| `INV-005` | Single Source of Truth | Each mutable state and scientific fact has one declared authoritative owner; UI copies cannot become competing truth. |
| `INV-006` | Repository Compatibility | Implementation must preserve the real repository stack, schemas, routes, shared contracts, and unrelated user work. |
| `INV-007` | No Local Design Language | A page may not create private tokens, semantics, interaction grammar, status vocabulary, or parallel global components. |
| `INV-008` | Explicit Epistemic State | Observed, predicted, inferred, literature-reported, proposed, reviewed, approved, executed, stale, and superseded must never be visually or semantically conflated. |
| `INV-009` | Safe Scientific Handoff | A design proposal cannot appear wet-lab-ready without validation requirements, limitations, risk/trade-off review, and explicit approval state. |

If an invariant cannot be preserved, the implementation is `BLOCKED`. An
Exception Record cannot legalize an invariant violation.

## 5.2 Decision Hierarchy

Use this complete hierarchy whenever two instructions, artifacts, or
implementations disagree:

```text
System Invariants
→ Verified scientific truth and safety
→ Real backend source of truth and repository constraints
→ Approved Global Architecture
→ This Global Page Design Contract
→ Approved global DSR / ADR
→ Approved Page Spec package
→ Approved page-specific DSR / ADR and Exception Record
→ Approved canonical visual reference
→ Implementation details
```

Rules at the same level are resolved by:

1. narrower approved scope over broader non-specific wording;
2. newer compatible version over older version;
3. explicit normative rule over example or recommendation;
4. if ambiguity remains, stop at the Conditional Audit Gate.

Claude Code MUST NOT choose whichever interpretation is easiest to implement.
Conflict resolution must be recorded in the delivery report.

## 5.3 Visual Identity Hierarchy

Every page must express the same nested identity:

```text
Brand
→ Workspace
→ Page
→ Region
→ Panel
→ Component
→ Scientific Object
```

Lower levels may specialize content and density, but may not introduce a
competing visual identity. Scientific-object encodings remain recognizable
across pages even when their container or task context changes.

---

# Part II — Product and Scientific Design Philosophy

## 6. Five Mandatory Product Qualities

Every page and every primary scientific view must provide:

### 6.1 Visibility

The user can immediately identify:

- where they are;
- which project, DBTL cycle, stage, object, and version are active;
- what is happening now;
- what has changed;
- whether data are current, historical, stale, partial, simulated, or unavailable.

### 6.2 Understandability

The user can understand:

- why a status, diagnosis, recommendation, or risk exists;
- which observations and mechanisms support it;
- which alternatives were considered;
- what uncertainty or contradiction remains.

### 6.3 Actionability

The user can identify:

- the next meaningful scientific or governance action;
- who owns that action;
- prerequisites and blockers;
- whether the action is reversible;
- whether approval is required.

### 6.4 Traceability

The user can trace:

- conclusion → evidence;
- evidence → paper, DDR, rule, dataset, simulation, or observation;
- design → prompt, agent, model, parameters, and version;
- decision → reviewer, timestamp, rationale, and audit event.

### 6.5 Trustworthiness

The interface must distinguish:

- fact from inference;
- observation from prediction;
- literature support from general knowledge;
- verified result from agent proposal;
- confidence from evidence quality;
- absence of evidence from evidence of absence.

## 7. Five Questions Every Primary View Must Answer

Within the visible view or one level of progressive disclosure:

1. **Now** — What is happening?
2. **Why** — Why is it happening or why is this proposed?
3. **Next** — What should happen next?
4. **Basis** — What evidence, mechanism, or model supports it?
5. **State** — Is it proposed, reviewed, approved, executed, observed, stale, or superseded?

If a panel cannot answer at least one of these questions, its necessity must be challenged.

## 8. Global Design Principles

### 8.1 Scientific First

Scientific meaning precedes decoration. Visual hierarchy must reflect scientific importance, not aesthetic symmetry.

### 8.2 Evidence Driven

Every non-trivial conclusion, recommendation, or design must expose evidence and provenance. “AI says” is never a valid terminal explanation.

### 8.3 Progressive Disclosure

Use this default depth:

```text
Overview
→ Summary
→ Scientific Detail
→ Evidence and Provenance
→ Raw Data or Source
```

Not every object requires five separate screens. The levels may live in a master–detail layout, inspector, drawer, expandable region, or deep link.

### 8.4 Human Governed

The agent may propose, compare, simulate, and critique. It must not silently convert a proposal into an approved wet-lab action.

Governed actions must support:

- Review;
- Approve;
- Reject;
- Request changes;
- Modify;
- Override with reason;
- Undo where technically and scientifically safe.

### 8.5 Persistent Workspace

The product is a stateful workspace, not a transient chat. Selection, filters, stage, comparison set, drafts, approvals, and relevant viewport state should survive navigation and restoration as defined by the state contract.

### 8.6 Traceable by Default

Provenance is attached to scientific objects, not hidden in a separate audit page only.

### 8.7 Expert Workflow

The experience should combine:

- Benchling-like scientific object rigor;
- IDE-like persistent workspace and inspector behavior;
- Linear-like interaction discipline;
- GitHub-like versions, review, and audit;
- Nature-figure-level information design;
- instrument-console clarity for status and uncertainty.

It must not resemble a generic admin dashboard or a full-page chatbot.

### 8.8 One Task, One Workspace

Diagnose, Design, Simulate, Critique, and Build/Test Plan belong to one engineering decision chain. Preserve the task context rather than forcing repeated page changes.

### 8.9 Information Flow over Feature Inventory

Organize around:

```text
Question → Understand → Design → Evaluate → Execute → Learn
```

Do not mirror backend module boundaries in the primary user experience.

## 9. Product-Wide Success Criteria

The system succeeds when:

- a PI can identify current status, next decision, and critical risk within 30 seconds;
- a researcher can move from an anomalous observation to a reviewable experiment plan without losing context;
- a user can reach the basis of a consequential conclusion within three deliberate interactions;
- an approved design has visible owner, version, evidence, assumptions, and approval history;
- simulated and observed values can never be mistaken for each other;
- returning users recover their active scientific context;
- new pages reuse the system rather than creating new local design languages.

### 9.1 Learnability Contract

The interface MUST NOT assume that every user already understands DBTL terminology, evidence grading, agent states, or provenance mechanics.

For a first-time qualified research user:

- within **30 seconds**, the current project state, current cycle, next action, and principal risk are identifiable;
- within **5 minutes**, the user can inspect a claim’s basis, distinguish observation from prediction, and locate the next governed action;
- product-specific domain terms provide concise inline help or a glossary link;
- empty states teach the next valid action without inventing scientific results;
- onboarding uses progressive, dismissible assistance and does not block expert workflows;
- dismissed repeated guidance remains disabled unless explicitly restored.

Learnability MUST be tested with representative PI, dry-lab, wet-lab, and junior-researcher tasks. Tooltips alone are not sufficient evidence.

---

# Part III — Global Information Architecture

## 10. Approved Primary Navigation

The product has four primary pages:

1. **Project Command Center**
2. **DBTL Engineering Workspace**
3. **Knowledge & Evidence Layer**
4. **Trust & Provenance Center**

No page Spec may recreate Diagnosis, Design, Simulation, Critique, or Experiment as separate primary applications.

## 11. Page Responsibilities

### 11.1 Project Command Center

Mission control for:

- current project state;
- current DBTL cycle;
- next required action;
- blocking risk;
- pending decision;
- recent meaningful change.

It must not become a metric-card dashboard.

### 11.2 DBTL Engineering Workspace

The primary working environment containing:

1. Diagnose
2. Design
3. Simulate
4. Critique
5. Build/Test Plan

The five stages are one governed engineering decision, not five disconnected tools.

### 11.3 Knowledge & Evidence Layer

A lower-frequency query, curation, and exploration layer for:

- biological knowledge;
- DDRs and rules;
- literature evidence;
- evidence graphs.

In-task evidence remains accessible through the Workspace Evidence Drawer.

### 11.4 Trust & Provenance Center

The dedicated governance and inspection environment for:

- memory;
- version history;
- audit trail;
- human approvals;
- system evaluation;
- golden sets.

Provenance still appears locally throughout the product.

## 12. Persistent Location Model

The application must continuously preserve and, where relevant, display:

```text
Project / DBTL Cycle / Stage / Selected Object / Version
```

The breadcrumb is not decorative. Each segment must represent real navigable context.

URLs should encode shareable, meaningful state:

```text
/projects/:projectId
/projects/:projectId/cycles/:cycleId/workspace/:stage
/projects/:projectId/cycles/:cycleId/workspace/:stage?object=:objectId&version=:versionId
```

Temporary UI state such as hover or panel width does not belong in the URL.

## 13. Scientific Object Hierarchy

### 13.1 Primary Objects

1. **Project**
2. **DBTL Cycle**
3. **Engineering Decision / Engineering Design**

These objects anchor navigation, ownership, state, and versions.

### 13.2 Workflow Objects

- Research Question
- Observation
- Dataset
- Measurement
- Bottleneck
- Hypothesis
- Candidate Design
- Simulation Run
- Critique
- Build/Test Plan
- Experiment
- Result
- Learning

### 13.3 Supporting Scientific Objects

- Strain
- Genotype
- Pathway
- Gene
- Protein
- Metabolite
- Reaction
- Construct
- Assay
- Sample
- Parameter

### 13.4 Cross-Cutting Objects

- Evidence
- Paper
- DDR
- Biological Rule
- Mechanism
- Inference
- Provenance Record
- Version
- Approval
- Audit Event
- Memory
- Evaluation

Cross-cutting objects attach to primary or workflow objects. They must not compete with the current engineering decision as the visual center.

## 14. Object Identity Contract

Every consequential object must support:

```yaml
id:
type:
title:
project_id:
cycle_id:
version_id:
status:
owner:
created_at:
updated_at:
source_type:
source_reference:
confidence:
evidence_ids:
provenance_id:
```

Optional fields must not be displayed as invented values. Use explicit unavailable states.

## 15. Global Status Language

Use one controlled vocabulary:

### 15.1 Lifecycle

- Draft
- Proposed
- In Review
- Changes Requested
- Approved
- Rejected
- Scheduled
- Running
- Completed
- Failed
- Superseded
- Archived

### 15.2 Data Freshness

- Current
- Historical
- Stale
- Partial
- Unavailable

### 15.3 Scientific Nature

- Observed
- Predicted
- Inferred
- Literature Reported
- Curated Rule
- User Entered

Do not use color as the only differentiator.

## 16. Evidence Hierarchy

The system must distinguish:

```text
Primary observation / raw measurement
↓
Processed result
↓
Curated literature evidence or DDR
↓
Biological rule or mechanism
↓
Inference
↓
Recommendation or design claim
```

This is a reasoning chain, not a universal ranking of truth. A page must expose contradictions and gaps rather than collapsing them into a single score.

## 17. Confidence and Evidence Quality

### 17.1 Confidence

Represent confidence as:

- label;
- value or band when available;
- method;
- contributing evidence;
- known uncertainty.

### 17.2 Evidence Quality

Suggested controlled values:

- Strong
- Moderate
- Limited
- Conflicting
- Unverified
- Not available

Never display precision such as `87%` unless the computation is real and explainable.

---

# Part IV — Global Visual Design System

## 18. Visual Identity

The visual identity is:

> **Scientific Engineering Mission Control**

It should feel precise, calm, information-dense, inspectable, and durable.

Default characteristics:

- light neutral canvas;
- structured panels;
- restrained blue primary interaction;
- compact typography;
- subtle borders instead of heavy shadows;
- small radii;
- meaningful scientific color;
- high legibility;
- limited decorative imagery.

## 19. Forbidden Visual Defaults

Do not use:

- generic SaaS dashboard composition;
- a grid of oversized KPI cards;
- blue–purple gradients as brand shorthand;
- glassmorphism;
- neon sci-fi styling;
- excessive pill-shaped containers;
- large empty hero sections inside the application;
- decorative 3D cells without a scientific task;
- excessive shadows;
- rainbow categorical palettes;
- arbitrary page-specific colors;
- chatbot bubbles as the primary workspace;
- animation that delays scientific reading.

## 20. Layout Grid

### 20.1 Application Frame

- Desktop-first.
- Global shell fills the viewport.
- Persistent navigation and workspace regions align to the same grid.
- Use a 12-column content grid where free-form page composition is needed.
- Use CSS Grid for application structure and Flexbox for local alignment.

### 20.2 Canonical Workspace Regions

```text
Global Navigation
Context Header
Stage / Local Navigation
Primary Workspace
Inspector or Evidence Drawer
Status / Activity Region when required
```

Not every page must show every region, but it must reuse the same structural logic.

### 20.3 Breakpoints

| Viewport | Contract |
| --- | --- |
| ≥ 1920 px | Full workspace; primary content and inspector may coexist comfortably |
| 1600–1919 px | Full desktop composition; reduced gutters |
| 1440–1599 px | Baseline design and screenshot acceptance width |
| 1280–1439 px | Compact desktop; secondary rails may collapse |
| 1024–1279 px | Review/tablet mode; drawers overlay when necessary |
| < 1024 px | Read/review priority; complex engineering editing may be limited explicitly |

Horizontal scrolling is allowed only inside inherently wide scientific content such as matrices or large tables, never for the full application shell.

## 21. Spacing System

Use an 8 px base grid with 4 px half-steps for dense controls.

```text
space-0  = 0
space-0.5 = 4
space-1  = 8
space-1.5 = 12
space-2  = 16
space-3  = 24
space-4  = 32
space-5  = 40
space-6  = 48
space-8  = 64
```

Rules:

- compact control gaps: 4–8 px;
- card internal padding: 12–16 px;
- panel internal padding: 16–24 px;
- major section separation: 24–32 px;
- avoid arbitrary values unless required by an existing repository system.

## 22. Size and Shape Tokens

```text
radius-xs = 3 px
radius-sm = 5 px
radius-md = 8 px
radius-lg = 12 px

border-default = 1 px
control-height-sm = 28 px
control-height-md = 36 px
control-height-lg = 44 px
```

Use `radius-lg` sparingly. Scientific panels and tables should generally use `radius-sm` or `radius-md`.

## 23. Color Tokens

Exact values may be adapted once to the existing repository, but semantic roles must remain stable.

### 23.1 Neutral Foundation

```css
--bg-canvas: #F6F7F9;
--bg-surface: #FFFFFF;
--bg-subtle: #F1F3F5;
--bg-selected: #EAF2FF;
--border-subtle: #E2E6EA;
--border-strong: #C8D0D8;
--text-primary: #17212B;
--text-secondary: #52606D;
--text-tertiary: #7B8794;
--text-disabled: #A8B0B8;
```

### 23.2 Interaction

```css
--action-primary: #2563EB;
--action-primary-hover: #1D4ED8;
--focus-ring: #60A5FA;
--link: #1D4ED8;
```

### 23.3 Semantic State

```css
--success: #237A57;
--warning: #A86516;
--danger: #B83A3A;
--info: #276FAE;
--unknown: #697586;
```

### 23.4 Scientific Data Color

- Scientific visualization colors are separate from UI state colors.
- Observed and predicted series must have consistent product-wide encodings.
- Gene, protein, metabolite, reaction, and pathway colors require a shared legend if used.
- A page must not assign semantic meaning to color without recording it in its Spec.
- Use color-blind-safe palettes and redundant encoding through label, line style, marker, shape, or pattern.

## 24. Typography

Use a modern sans-serif family already available in the project. Recommended stack:

```css
font-family: Inter, "IBM Plex Sans", "Segoe UI", system-ui, sans-serif;
font-family-mono: "IBM Plex Mono", "SFMono-Regular", Consolas, monospace;
```

### 24.1 Type Scale

| Token | Size / Line height | Weight | Use |
| --- | --- | --- | --- |
| Display | 28 / 36 | 600 | Rare page or project title |
| H1 | 24 / 32 | 600 | Page title |
| H2 | 20 / 28 | 600 | Major section |
| H3 | 16 / 24 | 600 | Panel title |
| Body | 14 / 21 | 400 | Default scientific reading |
| Body Strong | 14 / 21 | 600 | Emphasis and object names |
| Small | 12 / 18 | 400 | Metadata and secondary labels |
| Micro | 11 / 16 | 500 | Dense status, axes, compact controls |
| Mono | 12 / 18 | 400 | IDs, versions, parameters, code-like values |

Rules:

- Do not use font size alone to create hierarchy.
- Avoid body text below 12 px.
- Numeric tables use tabular numerals.
- Long reports prioritize readable line length; dense workspaces prioritize scanability.

## 25. Border, Elevation, and Focus

- Borders define persistent structure.
- Shadows indicate temporary elevation such as menus, popovers, and drag surfaces.
- Default panels should not float visually.
- Focus state must remain visible on every interactive control.
- Selected, hovered, focused, active, and disabled states must not be conflated.

## 26. Icon System

- Use one icon family, preferably Lucide.
- Default sizes: 14, 16, 18, 20 px.
- Icons supplement labels; they do not replace unfamiliar scientific actions.
- Destructive, approval, evidence, simulation, and version actions must use stable icons.
- No decorative emoji in the production UI.

## 27. Density Modes

The default is **Expert Density**.

Permitted modes:

- **Guided**: more explanations, fewer simultaneous controls.
- **Expert**: compact rows, persistent metadata, higher information density.

Modes may change density and assistance, but not scientific content, object states, or evidence availability.

### 27.1 Global Visual Rhythm

Scientific density MUST be deliberately modulated. A page MUST NOT render every region with equal visual weight, padding, contrast, and detail.

```text
Dense evidence or status
→ Relaxed orientation space
→ Dense working region
→ Focused decision or selected object
→ Dense supporting detail
→ Rest or closure
```

Rules:

- every viewport SHOULD contain one dominant focus region, not several equal “hero” cards;
- dense tables, graphs, or timelines MUST be separated by lower-density orientation or decision regions;
- whitespace communicates grouping and phase change, not decorative emptiness;
- Inspector and Evidence Drawer may be dense while the primary decision region preserves stronger hierarchy;
- consecutive sections with identical background, card weight, spacing, and emphasis MUST be regrouped or differentiated;
- rhythm comes from hierarchy, spacing, and disclosure—not gradients, oversized illustration, or arbitrary alternating backgrounds;
- responsive layouts preserve the order of attention when panel geometry changes.

Every UI Spec MUST include a `Visual Rhythm Map` labeling major regions as `orient`, `dense`, `focus`, `support`, or `rest`.

## 28. Motion

Motion exists to explain state change.

```text
micro feedback: 100–150 ms
panel transition: 160–220 ms
complex spatial change: up to 300 ms
easing: standard ease-out for entrance, ease-in for exit
```

Rules:

- support reduced motion;
- no looping decorative movement in workspaces;
- skeletons should not create distracting shimmer;
- stage transition must preserve perceived object continuity;
- charts must not animate from misleading baselines;
- motion must never postpone access to critical status or evidence.

---

# Part V — Global Component Library

## 29. Component Hierarchy

```text
L0 — App Shell
L1 — Page / Workspace Frame
L2 — Scientific Panel
L3 — Scientific Object View
L4 — Inspector / Drawer / Comparison
L5 — Evidence and Provenance Detail
```

Lower levels may not recreate higher-level navigation or context.

## 30. Required Shared Components

### 30.1 Shell

- `AppShell`
- `PrimaryNavigation`
- `ProjectSwitcher`
- `ContextHeader`
- `Breadcrumb`
- `GlobalSearch`
- `CommandPalette`
- `ConnectionStatus`
- `UserAndRoleMenu`

### 30.2 Workspace

- `WorkspaceFrame`
- `StageRail`
- `WorkspaceToolbar`
- `PrimaryCanvas`
- `InspectorPanel`
- `EvidenceDrawer`
- `ResizableSplitPane`
- `SelectionSummary`

### 30.3 Scientific Objects

- `ScientificObjectHeader`
- `ScientificObjectCard`
- `ObjectStatusBadge`
- `ObjectMetadata`
- `ConfidenceIndicator`
- `EvidenceSummary`
- `ProvenanceStamp`
- `VersionBadge`
- `SourceTypeBadge`
- `StaleDataBanner`

### 30.4 Decisions and Governance

- `DecisionCard`
- `ApprovalBar`
- `ReviewThread`
- `ChangeRequest`
- `OverrideWithReason`
- `AuditTimeline`
- `DiffViewer`
- `ActorStamp`

### 30.5 Data and Visualization

- `DataTable`
- `ComparisonTable`
- `MetricStrip`
- `ScientificChart`
- `NetworkView`
- `PathwayView`
- `Timeline`
- `Heatmap`
- `RawDataViewer`
- `VisualizationLegend`

### 30.6 Feedback and State

- `Skeleton`
- `EmptyState`
- `ErrorState`
- `UnavailableState`
- `PartialDataState`
- `InlineAlert`
- `Toast`
- `ProgressIndicator`
- `RetryAction`

## 31. Component Variant Rule

Before creating a new component, answer:

1. Can an existing component support the need through content?
2. Can a documented variant support it?
3. Is the difference scientific behavior or merely visual preference?
4. Will the component be reused?

Page-local copies of shared components are prohibited.

## 32. Card Contract

Cards are used for bounded scientific objects or decisions—not as universal layout containers.

Every scientific card must define:

- object type;
- object title;
- primary state;
- essential scientific summary;
- provenance or source access;
- primary action;
- selected, loading, empty, error, stale, and disabled behavior where applicable.

Avoid nested cards deeper than two levels.

## 33. Badge Contract

Badges may encode:

- lifecycle status;
- data freshness;
- scientific nature;
- evidence quality;
- object type;
- version.

One badge may communicate one dimension only. Do not create a cluster of redundant pills.

## 34. Table Contract

Scientific tables must support, when applicable:

- sticky header;
- stable column semantics;
- sorting;
- filtering;
- selection;
- column visibility;
- units;
- missing-value representation;
- provenance access;
- pagination or virtualization;
- export consistent with the visible filtered set.

Never silently truncate scientific values.

## 35. Inspector Contract

The Inspector is selection-driven and context-preserving.

It should show:

1. object identity and status;
2. scientific summary;
3. key fields and parameters;
4. evidence and provenance entry points;
5. relevant actions;
6. version and activity.

Changing selection updates the Inspector without destroying the main workspace.

## 36. Evidence Drawer Contract

The Evidence Drawer is contextual, not a miniature knowledge center.

Default sections:

- Evidence summary;
- Supporting and conflicting sources;
- Mechanism;
- Confidence and uncertainty;
- Provenance;
- Open in Knowledge & Evidence Layer.

It must preserve the selected scientific object and stage.

---

# Part VI — Global Interaction Contract

## 37. Core Interaction Philosophy

Use:

- Single Workspace;
- Master–Detail;
- Selection-Driven UI;
- Persistent Inspector;
- Progressive Disclosure;
- Resizable Panels;
- Context Preservation;
- Explicit Commit;
- Reversible Editing where safe;
- Deep Linking.

## 38. Navigation

- Primary navigation changes product area.
- Stage navigation changes the current step of one engineering decision.
- Breadcrumb changes scientific context.
- Tabs switch equivalent local views only.
- Links to evidence or provenance preserve return context.
- Browser back/forward must behave predictably.

Do not use tabs merely to hide unrelated functions.

## 39. Click and Selection

- Single click selects.
- Double click must not be required for a critical action.
- Primary action must be visually distinct.
- Row selection and row navigation must not conflict.
- Selected object state persists while opening an inspector or drawer.

## 40. Hover

Hover may reveal:

- concise definitions;
- exact values;
- secondary actions;
- graph relationships;
- provenance preview.

Hover must not be the only way to access required content or actions.

## 41. Expand and Collapse

- Use expansion for hierarchical or optional detail.
- Preserve expansion state within the active context.
- “Expand all” is appropriate only for bounded content.
- Avoid accordion layouts that allow the user to see only one scientific comparison item at a time.

## 42. Search and Filter

All search/filter systems must define:

- scope;
- fields searched;
- active filter visibility;
- result count;
- zero-result behavior;
- clear/reset action;
- persistence rules;
- URL behavior when shareable.

Filters must never silently remove data without visible indication.

## 43. Timeline

Timeline is reserved for real temporal, version, cycle, or audit order. Do not use it as decorative navigation.

Each event must define actor, action, object, timestamp, and result.

## 44. Modal Policy

Modal dialogs are allowed only for:

- consequential confirmation;
- short focused creation;
- authentication or authorization interruption;
- irreversible or high-risk action;
- compact, self-contained input that should block background interaction.

Do not use modals for browsing scientific detail, evidence, provenance, comparisons, or long forms. Use an Inspector, Drawer, split pane, or dedicated view.

## 45. AI Interaction

AI output must be rendered as structured scientific objects, not only prose.

The UI must distinguish:

- user input;
- retrieved evidence;
- deterministic computation;
- model-generated inference;
- proposed action;
- approved decision.

Required AI affordances where applicable:

- inspect basis;
- inspect prompt/model/version;
- compare alternatives;
- regenerate with changed constraints;
- edit proposal;
- accept into draft;
- reject;
- report unsupported claim.

Streaming text may be shown as progress, but partial output is not a committed scientific object.

## 46. Approval Interaction

Approval must be object- and version-specific.

Before approval, show:

- what will be approved;
- version;
- evidence summary;
- unresolved risks;
- downstream effect;
- required reviewer role.

Rejection and override require a reason. Approval history is immutable audit data.

## 47. Undo and Recovery

- Local reversible edits should support undo.
- Server mutations should use explicit save/commit and provide result state.
- Failed operations must preserve user input.
- Conflict recovery must compare local and server versions.
- Never imply rollback if it is not technically available.

## 48. Notifications

- Toast: low-context confirmation.
- Inline alert: state tied to a panel or object.
- Banner: page-wide freshness, outage, or governance state.
- Attention Queue: cross-object actionable items.

Do not use a toast as the sole record of an important decision or failure.

## 49. Context Menu

Context menus may expose advanced secondary actions. All essential actions must also exist in visible, keyboard-accessible UI.

## 50. Keyboard

Minimum desktop support:

- logical tab order;
- `Esc` closes temporary layers;
- arrow navigation in supported lists/trees;
- `/` or product-approved shortcut focuses search;
- command palette shortcut;
- save/commit shortcut only when behavior is unambiguous;
- visible shortcut hints.

## 51. Error Recovery

Every error state must answer:

- what failed;
- what remains safe;
- whether data were saved;
- what the user can do;
- whether retry is safe;
- where to inspect technical detail.

Do not display raw stack traces as the primary message.

---

# Part VII — Scientific Content and Visualization Contract

## 52. Content before Layout

No page may begin high-fidelity design before defining:

- scientific objects;
- decisions;
- inputs and outputs;
- evidence chain;
- uncertainty;
- actions;
- empty and partial states.

## 53. Scientific Claim Contract

Every consequential claim must identify:

```yaml
claim:
claim_type:
subject_object:
supporting_evidence:
conflicting_evidence:
mechanism:
confidence:
assumptions:
limitations:
generated_by:
generated_at:
version:
```

## 54. Units and Numerical Integrity

- Display units at the value, column, axis, or field level.
- Preserve raw precision in detail views.
- Use appropriate significant figures in summaries.
- State normalization, transformation, aggregation, and imputation.
- Distinguish `0`, `not detected`, `missing`, `not measured`, and `not applicable`.
- Timezone and timestamp conventions must be explicit.

## 55. Visualization Selection

Use:

| Question | Preferred form |
| --- | --- |
| Exact values across objects | Table |
| Trend over time/cycle | Line or timeline |
| Candidate comparison | Comparison table, dot plot, or aligned small multiples |
| Composition | Stacked bar only when parts form a meaningful whole |
| Distribution | Box/violin/histogram with sample context |
| Relationships | Network/graph only when topology is the question |
| Pathway mechanism | Pathway diagram |
| High-dimensional matrix | Heatmap |
| Sequential governed process | Stage rail or state diagram |
| Version change | Diff |

Do not use a graph where a short table is clearer.

## 56. Scientific Chart Requirements

Every chart must define:

- question;
- data source;
- observed/predicted/inferred distinction;
- axes and units;
- sample size;
- missing-data behavior;
- uncertainty representation;
- selection and linking behavior;
- legend;
- accessible alternative;
- export behavior.

Defaults:

- avoid 3D charts;
- avoid dual axes unless scientifically justified;
- do not truncate axes in misleading ways;
- show uncertainty where known;
- allow inspection of exact values;
- use consistent encodings across pages.

## 57. Network and Knowledge Graph Limits

- Load progressively.
- Define node and edge semantics.
- Provide legend and search.
- Limit initial visible nodes.
- Preserve selected-node context.
- Support table fallback.
- Do not use “hairball” graphs as evidence of sophistication.

## 58. Three.js Contract

Three.js may be used only when spatial or structural interaction materially improves a scientific task.

Every Three.js use must state:

- scientific purpose;
- data source;
- selectable objects;
- mapping from geometry/color to biology;
- fallback;
- performance budget;
- accessibility alternative.

A decorative E. coli model is not sufficient justification.

## 59. Report Contract

If a page generates a report, define:

- audience;
- decision supported;
- section order;
- included object versions;
- evidence and citations;
- assumptions and limitations;
- approval state;
- export format;
- reproducibility metadata.

The report must not become a prose dump of the visible UI.

## 60. Empty Scientific State

An empty state must distinguish:

- not created;
- not imported;
- not measured;
- no result;
- filtered out;
- inaccessible;
- backend unavailable;
- scientifically not applicable.

It should explain the next scientifically valid action, not merely say “No data.”

---

# Part VIII — Technical Design Contract

## Implementation Scope Lock

The implementation agent is authorized to implement only the page, shared primitives, adapters, tests, and documentation explicitly required by the approved Spec package.

Unless an approved requirement or blocking compatibility issue demands it, the implementation agent MUST NOT:

- improve, replace, or broadly refactor unrelated architecture;
- rename, remove, or reinterpret existing APIs;
- modify backend scientific logic, model behavior, evidence grading, or governance rules;
- replace the approved Design System or create a competing token set;
- create new primary navigation, workflows, object types, or approval states;
- redesign completed pages by local judgment;
- overwrite or discard unrelated user changes;
- introduce a new framework, state library, visualization library, or component system;
- promote deferred P2/P3 work into current scope;
- continue aesthetic polishing after all defined gates pass.

Permitted incidental changes MUST be minimal, directly necessary, and listed in the delivery report. If an out-of-scope change is required, implementation pauses at the Conditional Audit Gate and records the blocker instead of silently expanding scope.

### Protected Repository Surface

The implementation prompt MUST resolve the real paths for the following
protected surfaces before editing:

```yaml
protected_surfaces:
  - AppShell and global layout geometry
  - Global design tokens and themes
  - Primary navigation and routing semantics
  - Global domain object model and terminology
  - Global types and API contracts
  - Shared component public APIs
  - Authentication, authorization, approval, and audit logic
  - Backend scientific reasoning and workflow logic
  - Existing migrations and persistence schemas
  - Unrelated modified or untracked user files
```

Protection means **read and reuse by default**, not “never touch.” A protected
surface may be edited only when all of the following are true:

1. the approved scope explicitly requires the change;
2. repository evidence proves it is necessary;
3. affected consumers and regression tests are identified;
4. the appropriate DSR/ADR and approval exist;
5. the smallest compatible change is used.

Otherwise the agent must adapt the page locally through approved extension
points or return `BLOCKED`.

### Forbidden Autonomous Behaviors

The agent MUST NOT autonomously:

- reinterpret the product architecture or page responsibility;
- change a scientific workflow, approval transition, evidence grade, or status meaning;
- create speculative backend endpoints, data, measurements, citations, or capabilities;
- convert a proposed design into an approved or executable experiment;
- delete, overwrite, rename, or migrate protected or unrelated assets;
- replace an existing dependency merely because another is preferred;
- suppress errors, failed tests, contradictory evidence, or missing data;
- relax acceptance criteria or rewrite snapshots to manufacture a pass;
- continue beyond the Stop Condition.

### Conditional Audit Gate

Pause before mutation and return a decision request when any of these is true:

- an invariant would be violated;
- source documents conflict after applying the Decision Hierarchy;
- the requested implementation requires backend scientific logic or API changes not explicitly authorized;
- a protected surface requires a breaking or cross-page modification;
- real data/schema differs materially from the approved Page Spec;
- required access, dependency, scientific input, or approval is unavailable;
- proceeding risks data loss, governance bypass, or overwriting unrelated work.

Minor implementation gaps that can be resolved through an existing approved
extension point do not require a pause.

## 61. Repository-First Rule

Before implementation, inspect:

- framework and versions;
- router;
- styling and tokens;
- existing shared components;
- state libraries;
- API clients and schemas;
- authentication and roles;
- tests;
- build commands;
- existing uncommitted changes.

Reuse before replacing. Do not modify backend scientific logic unless explicitly authorized.

## 62. React Architecture

Recommended separation:

```text
app/
  shell/
  routing/
  providers/
modules/
  command-center/
  dbtl-workspace/
  knowledge-evidence/
  trust-provenance/
components/
  ui/
  scientific/
  visualization/
  governance/
domain/
  objects/
  schemas/
  terminology/
services/
  api/
  adapters/
  queries/
state/
  workspace/
  preferences/
styles/
  tokens/
  themes/
tests/
```

Adapt this to the real repository rather than creating a parallel architecture.

## 63. Module Registration

New pages or modules should register:

- route;
- navigation metadata;
- permissions;
- context requirements;
- data dependencies;
- page component;
- error boundary;
- feature flag where relevant.

A new page must not require rewriting `AppShell`.

## 64. State Ownership Matrix

| State | Owner |
| --- | --- |
| Project, cycle, stage, selected shareable object | URL/router |
| Backend objects and server truth | Query/cache layer |
| Cross-page workspace context | Global workspace store |
| Unsaved form/draft state | Local or dedicated draft store |
| Panel width, collapsed region, density preference | UI preference state |
| Hover, local expansion, temporary menu | Component state |
| Approval, audit, versions | Backend source of truth |

Do not mirror the same mutable state in multiple owners.

## 65. API Contract

Each page Spec must map:

```yaml
ui_object:
backend_endpoint_or_event:
request_schema:
response_schema:
source_of_truth:
adapter:
loading_state:
empty_state:
partial_state:
error_state:
refresh_or_revalidation:
permission:
mock_policy:
```

Mock data must be labeled and isolated. It must not silently appear as real scientific output.

## 66. Data Flow

Preferred flow:

```text
Backend schema
→ typed API client
→ adapter / normalizer
→ domain object
→ query/cache
→ page model
→ shared scientific component
```

Components should not parse inconsistent backend payloads directly.

## 67. Loading and Lazy Loading

- Load shell and essential current-state content first.
- Lazy-load heavy graphs, raw-data viewers, Three.js, and infrequent governance views.
- Do not block the whole page for one secondary request.
- Preserve layout during loading.
- Use virtualization for large tables and lists.

## 68. Performance Baseline

Target for a representative 1440 px desktop on a normal development machine:

- visible interaction response: within 100 ms where local;
- panel open feedback: within 200 ms;
- meaningful page skeleton: within 1 s after route activation when cached/local;
- no unbounded DOM rendering;
- large list/table virtualization;
- graph initial node budget documented;
- route-level code splitting for heavy modules;
- no avoidable re-render of full workspace on selection.

If real network/backend behavior prevents a target, show progressive state instead of freezing.

## 69. Memoization

Use memoization based on measured or structurally obvious cost:

- derived scientific comparisons;
- large filtered tables;
- graph layouts;
- expensive visualization transforms.

Do not scatter `memo`, `useMemo`, or `useCallback` without a reason.

## 70. Error Boundaries

At minimum:

- application boundary;
- route/module boundary;
- heavy visualization boundary.

A failed visualization must not destroy the engineering decision context.

## 71. Accessibility

Required:

- semantic structure;
- keyboard navigation;
- visible focus;
- labels for controls;
- sufficient contrast;
- no color-only meaning;
- reduced motion;
- accessible tables;
- text alternative or data table for charts;
- screen-reader announcement for meaningful async state;
- target size appropriate to density and use.

Accessibility is part of scientific reliability, not a cosmetic afterthought.

## 72. Internationalization

- UI language must be internally consistent.
- Scientific symbols, gene names, units, and identifiers are not translated.
- Do not mix Chinese and English randomly.
- Layout must tolerate reasonable text expansion.
- Date, time, decimal, and unit formatting use explicit locale rules.

## 73. Testing

Each implemented page should include:

- unit tests for domain transforms;
- component tests for states and actions;
- integration tests for critical workflow;
- accessibility checks;
- visual regression at agreed widths;
- contract tests for API adapters;
- acceptance fixtures representing normal, empty, partial, stale, conflict, and error states.

### 73.1 Regression Rule

Every page delivery MUST demonstrate:

```text
No Page Drift
No Component Drift
No Interaction Drift
No Scientific Drift
No Backend Contract Drift
```

Required evidence:

- affected existing routes retain their responsibilities;
- shared components use approved variants and tokens;
- navigation, selection, disclosure, approval, recovery, and keyboard behavior remain consistent;
- scientific status, units, evidence, uncertainty, and provenance semantics remain intact unless explicitly approved;
- API contracts, adapters, loading states, and error states remain compatible;
- approved visual baselines are compared at required breakpoints;
- failures are recorded rather than hidden by snapshot replacement.

Updating a snapshot or expected result solely to make a regression test pass is prohibited without an approved decision record.

### 73.2 Regression Matrix

Every page delivery must report each regression domain separately:

| Domain | Minimum evidence |
| --- | --- |
| UI | canonical viewport comparison; tokens, shell, hierarchy, and state variants |
| Interaction | critical task flow, keyboard path, recovery, selection, disclosure, and undo |
| Scientific | object semantics, units, epistemic state, evidence, uncertainty, and limitations |
| Backend | adapter/contract tests, source-of-truth ownership, partial/error behavior |
| Performance | render bounds, virtualization/lazy loading, interaction responsiveness |
| Accessibility | automated checks plus keyboard/focus and non-color meaning |
| Governance | version-specific review, approval, override reason, audit, and provenance |

A single global `PASS` is invalid if a domain was not tested or is `UNKNOWN`.

### 73.3 Computational Traceability

Agent- or model-generated computational outputs must expose:

```text
Input / Prompt
→ Agent and Model Version
→ Tool and Data Version
→ Parameters
→ Output Artifact
→ Evaluator / Review
→ Approval State
```

Sensitive prompt or parameter content may be permission-gated, but its
existence, version, and audit reference must remain visible.

---

# Part IX — Page Specification Package

## 74. Required Directory

Every page must contain:

```text
PageX/
├── 00_Page_Research.md
├── 01_Product_Spec.md
├── 02_UI_Spec.md
├── 03_Interaction_Spec.md
├── 04_Technical_Spec.md
├── 05_Content_Spec.md
├── 06_Acceptance_Spec.md
└── Generate_Page_Prompt.md
```

Optional:

```text
├── assets/
├── references/
├── decisions/
├── fixtures/
└── visual-regression/
```

## 75. Page Spec Header

Every Spec begins with:

```yaml
page_id:
page_name:
spec_type:
version:
status: Draft | In Review | Approved | Superseded
owners:
reviewers:
parent_contract: Page Design Contract v1.2
parent_architecture: Frontend Architecture Prompt v1.2
last_updated:
dependencies:
open_questions:
approved_exceptions:
```

## 76. 00_Page_Research.md

### Purpose

Study relevant best practices before designing. Distill principles rather than copying layouts.

### Required Sections

1. **Research Question**
2. **Target Workflow and User Context**
3. **Product Benchmarks**
4. **Layout Benchmarks**
5. **Interaction Benchmarks**
6. **Information Density Benchmarks**
7. **Scientific Visualization Benchmarks**
8. **Evidence and Provenance Benchmarks**
9. **Animation and Feedback Benchmarks**
10. **Accessibility Benchmarks**
11. **Good Practices to Adopt**
12. **Bad Practices to Avoid**
13. **Transferability Analysis**
14. **Derived Page Design Principles**
15. **Research Gaps and Unresolved Questions**

### Benchmark Rule

For each reference:

```yaml
reference:
observed_pattern:
user_problem_solved:
why_it_works:
limitations:
transfer_to_this_product:
do_not_copy:
```

### Output

A concise set of evidence-backed design principles for this page—not a screenshot collection.

## 77. 01_Product_Spec.md

### Purpose

Define why the page exists and what research outcome it enables.

### Required Sections

1. Mission
2. Scientific Purpose
3. DBTL Mapping
4. Target Users
5. Jobs to Be Done
6. User Goals by Role
7. Primary User Story
8. Secondary User Stories
9. Entry Points
10. Exit and Handoff
11. Page Responsibilities
12. Explicit Non-Goals
13. Scientific Workflow Mapping
14. Backend Capability Mapping
15. Information Priority
16. Main Decisions and Actions
17. Risks and Failure Modes
18. Product Success Metrics
19. Dependencies
20. Open Questions

### Required Priority Format

```text
P0 — page cannot fulfill its mission without it
P1 — necessary for a complete primary workflow
P2 — important secondary capability
P3 — enhancement, never allowed to delay P0–P2
```

### Output

The approved product definition of the page.

## 78. 02_UI_Spec.md

### Purpose

Define the page’s visible composition while inheriting all global tokens and components.

### Required Sections

1. Page Anatomy
2. Layout Grid
3. Canonical Regions
4. Visual Hierarchy
5. Reading Order
6. Information Density
7. Page-Specific Component Inventory
8. Shared Component Reuse Matrix
9. Card and Panel Definitions
10. Table Definitions
11. Chart and Visualization Definitions
12. Inspector / Drawer Composition
13. State Presentation
14. Empty State
15. Loading State
16. Partial / Stale / Offline State
17. Error State
18. Responsive Rules at 1920, 1600, 1440, 1280, 1024
19. Accessibility Layout Requirements
20. Motion and Transition
21. Nanobanana Composition Constraints
22. Visual Do / Don’t
23. Annotated Wireframe

### Component Record

```yaml
component:
purpose:
scientific_object:
priority:
default_state:
interactive_states:
content_fields:
primary_action:
secondary_actions:
shared_or_page_specific:
responsive_behavior:
accessibility:
```

### Output

A visual specification detailed enough for image generation and implementation without inventing local styles.

## 79. 03_Interaction_Spec.md

### Purpose

Define how the user navigates, selects, investigates, edits, compares, approves, and recovers.

### Required Sections

1. Interaction Model
2. Navigation
3. Selection Model
4. Click
5. Hover
6. Expand / Collapse
7. Inspector
8. Evidence Drawer
9. Search
10. Filter and Sort
11. Comparison
12. Timeline
13. Provenance Inspection
14. AI Interaction
15. Draft and Commit
16. Review and Approval
17. Keyboard Shortcuts
18. Undo / Redo
19. Error Recovery
20. Notifications
21. Context Menu
22. Focus Management
23. Context Preservation
24. Deep Linking
25. Permission Behavior
26. Analytics / Event Instrumentation

### Interaction Flow Record

```yaml
flow:
actor:
precondition:
entry:
steps:
system_feedback:
data_mutation:
approval_required:
success_state:
failure_state:
recovery:
audit_event:
```

### Output

The page interaction contract, including normal, edge, error, and recovery paths.

## 80. 04_Technical_Spec.md

### Purpose

Translate the approved product, UI, and interaction design into a repository-compatible implementation plan.

### Required Sections

1. Repository Findings
2. Existing Assets to Reuse
3. React Architecture
4. Component Tree
5. Folder / Module Placement
6. Route Registration
7. Domain Types
8. State Ownership
9. Context and Providers
10. API Contract
11. Backend Mapping Matrix
12. Adapter and Normalization
13. Data Flow
14. Caching and Revalidation
15. Optimistic Update Rules
16. Lazy Loading
17. Virtualization
18. Memoization
19. Error Boundaries
20. Animation Library
21. Three.js Usage or Explicit Non-Use
22. Performance Budget
23. Accessibility Implementation
24. Internationalization
25. Permissions
26. Telemetry
27. Testing Strategy
28. Feature Flags
29. Migration and Compatibility
30. File Change Plan
31. Explicitly Protected Files / Logic

### Backend Mapping Table

| UI need | Object | Endpoint/event | Schema | Adapter | Source of truth | Missing behavior |
| --- | --- | --- | --- | --- | --- | --- |

### Output

An implementation contract that Claude Code can execute without redesigning the product.

## 81. 05_Content_Spec.md

### Purpose

Define exactly what scientific information is shown and why.

### Required Sections

1. Scientific Question Supported
2. Scientific Objects
3. Object Relationships
4. Required Fields
5. Content Hierarchy
6. Default Visible Content
7. Progressive Disclosure Content
8. Scientific Cards and Fields
9. Evidence Hierarchy
10. Claim–Evidence Mapping
11. Confidence and Uncertainty
12. Provenance Requirements
13. Scientific Terminology
14. Units and Numerical Formatting
15. Visualization Selection
16. Tables and Columns
17. Reports and Exports
18. Empty Scientific State
19. Partial and Contradictory Evidence
20. Sample Content / Fixtures
21. Scientific Review Questions

### Scientific Card Record

```yaml
card:
object_type:
scientific_purpose:
default_fields:
summary_claim:
status:
confidence:
evidence:
provenance:
actions:
detail_fields:
raw_data_link:
empty_behavior:
```

### Output

The page information architecture and scientifically reviewable content model.

## 82. 06_Acceptance_Spec.md

### Purpose

Turn all previous Specs into testable acceptance gates.

### Required Checklists

1. Product / Mission
2. Functional
3. UI and Design System
4. Scientific Content
5. Evidence and Traceability
6. Human Governance
7. Backend Truthfulness
8. Interaction
9. State and Persistence
10. Loading / Empty / Partial / Error
11. Accessibility
12. Responsive
13. Performance
14. Code and Architecture
15. Security and Permissions
16. Visual Regression
17. Final User Experience

### Acceptance Record

```yaml
criterion_id:
requirement:
priority:
test_method:
expected:
actual:
evidence:
status: PASS | FAIL | BLOCKED | DEFERRED
owner:
remediation:
```

### Final Experience Gates

- Can a PI understand Now / Next / Risk quickly?
- Can a scientist understand Why / Basis / Uncertainty?
- Can a user inspect provenance within three deliberate interactions?
- Can a wet-lab user identify an approved, versioned next action?
- Does the page behave as part of one OS?
- Is it free of generic dashboard and chatbot patterns?
- Does it meet the rigor of a scientific instrument workspace?

### Output

PASS, FAIL, BLOCKED, or DEFERRED for every criterion. No vague “mostly complete.”

## 83. Generate_Page_Prompt.md

### Purpose

Generate the final, bounded implementation Prompt after all seven Specs are approved.

### Mandatory Inputs

Read in this order:

1. Page Design Contract
2. Frontend Architecture Prompt
3. `00_Page_Research.md`
4. `01_Product_Spec.md`
5. `05_Content_Spec.md`
6. `02_UI_Spec.md`
7. `03_Interaction_Spec.md`
8. `04_Technical_Spec.md`
9. `06_Acceptance_Spec.md`
10. Actual repository and backend schemas

Scientific content is read before visual composition so that UI does not determine scientific meaning.

### Required Generated Prompt Structure

1. Role
2. Mission
3. Sources of Truth
4. Repository Audit
5. Page Scope and Non-Goals
6. User and Scientific Workflow
7. Scientific Objects and Content
8. Layout and Visual Contract
9. Interaction Contract
10. Backend/API Mapping
11. State Ownership
12. Component and File Plan
13. Implementation Priority
14. Change Safety
15. Verification
16. Acceptance Criteria
17. Required Deliverables
18. Completion Report Format

### Generation Rule

The generated Prompt must:

- resolve duplicate requirements;
- preserve normative priority;
- expose unresolved contradictions;
- separate P0–P3;
- prohibit unsupported invention;
- identify files that may and may not change;
- include acceptance tests;
- remain specific to one page.

It must not paste all Specs verbatim into an unprioritized mega-prompt.

---

# Part X — Nanobanana Design Contract

## 84. Role of Nanobanana

Nanobanana is an advanced visual generator, not the product architect or scientific authority.

It may generate:

- page composition;
- visual hierarchy;
- scientific content-region mockups;
- controlled visual alternatives;
- polished screen designs.

It must not invent:

- navigation architecture;
- scientific objects;
- data;
- backend capabilities;
- evidence;
- approval state;
- new colors, fonts, or component families;
- interactions that contradict the Specs.

## 85. Fixed vs Generated Layers

### Fixed by Program / Design System

- AppShell;
- logo and branding;
- global navigation;
- project/cycle context;
- typography;
- token values;
- spacing grid;
- shared buttons, fields, badges, tables;
- standard inspector and drawer behavior;
- status meanings;
- page dimensions and safe areas.

### Generated within Constraints

- page-specific content arrangement;
- scientific illustration or content-region composition;
- visual prioritization among approved objects;
- page-specific pathway, graph, or comparison presentation;
- optional controlled variants.

## 86. Nanobanana Input Package

Every generation request must provide:

- target viewport;
- annotated page anatomy;
- approved content;
- exact visible text or realistic fixture;
- token summary;
- component references;
- fixed shell image or template;
- allowed visualization types;
- selected state to depict;
- prohibited patterns;
- expected output count and naming.

## 87. Reference State

Each page must have one canonical reference state for cross-page comparison:

```text
Viewport: 1440 × 1024
Density: Expert
Theme: Light
Navigation: Expanded or globally fixed state
Project context: Populated
Data state: Normal
Inspector: Defined open/closed state
Evidence Drawer: Defined open/closed state
```

Additional states may be generated after the canonical state is approved.

## 88. Visual Generation Acceptance

A generated image passes only if:

- shell geometry matches the global reference;
- typography and spacing match tokens;
- scientific content hierarchy matches the Content Spec;
- primary action is unambiguous;
- status and uncertainty are visible;
- no unsupported object or metric is introduced;
- layout remains implementable in React/CSS;
- it does not rely on impossible image-only effects;
- it belongs visibly to the same product as prior approved pages.

---

# Part XI — Page Creation Workflow

## 89. Mandatory Sequence

```text
1. Repository Audit
→ 2. Read Contract and Approved Specs
→ 3. Component and Capability Inventory
→ 4. Reuse and Gap Decision
→ 5. Implement in Locked Scope
→ 6. Test
→ 7. Acceptance
→ 8. Regression
→ 9. Delivery Declaration
→ 10. Stop
```

Before implementation, the page-definition sequence is:

```text
Architecture confirmed
→ Page Research
→ Product Spec
→ Content Spec
→ UI Spec
→ Interaction Spec
→ Technical Spec
→ Acceptance Spec
→ Cross-Spec Consistency Review
→ Generate Page Prompt
→ Nanobanana canonical design when required
→ Design review
```

No stage may be silently skipped or reordered. No high-fidelity generation may begin before Product and Content Specs are stable.

### 89.2 Unified Task Flow

Every primary user workflow should map explicitly to:

```text
Start
→ Understand
→ Decide
→ Commit
→ Review
→ Complete
```

- **Start** establishes project, cycle, stage, object, version, permissions, and current state.
- **Understand** exposes observations, evidence, mechanism, uncertainty, and conflict.
- **Decide** compares alternatives, trade-offs, limitations, and validation needs.
- **Commit** creates a versioned draft or decision request; it does not silently execute.
- **Review** supports approve, reject, request change, or override with reason.
- **Complete** records the resulting state, provenance, ownership, and next action.

Pages may omit a stage only when it is genuinely outside their responsibility
and the handoff destination is explicit.

### 89.3 Scientific Review Checklist

Every proposed diagnosis, design, simulation interpretation, or experiment
handoff must be reviewable against:

1. **Mechanism** — What causal or biological mechanism is asserted?
2. **Evidence** — What observations, literature, rules, datasets, or simulations support it?
3. **Trade-off** — What competing objectives, burdens, or side effects exist?
4. **Limitation** — What is unknown, assumed, contradicted, stale, or out of domain?
5. **Validation** — What genotype, mechanism, phenotype, safety, and measurement checks are required?

The UI must not compress these into an unexplained confidence score.

### 89.1 Execution Rules

- Repository Audit identifies stack, routes, schemas, shared components, tests, dirty files, and protected modules.
- Contract and Spec reading resolves contradictions before code changes.
- Component Inventory classifies each required element as `reuse`, `extend`, or `new`.
- Creating a global primitive requires a documented gap.
- P0 completes before P1; P2/P3 cannot block release unless the Acceptance Spec says otherwise.
- Tests verify behavior; Acceptance separately verifies the scientific and product contract.
- Regression occurs after acceptance fixes and before delivery.
- Delivery Declaration lists files changed, decisions, exceptions, deferred items, risks, and gate results.
- Stop is mandatory when the Stop Condition is satisfied.

## 90. Gate 0 — Readiness

Before Page Research:

- page belongs to approved architecture;
- mission and owner are known;
- page boundary is not duplicating another page;
- relevant backend capability is identifiable.

## 91. Gate 1 — Product and Science

Before UI design:

- primary research question is defined;
- scientific objects and relationships are defined;
- Now / Why / Next / Basis / State are mapped;
- evidence and uncertainty are mapped;
- P0 content is approved.

## 92. Gate 2 — Design

Before visual generation:

- layout anatomy is approved;
- shared components are selected;
- page-specific components are justified;
- all required states are specified;
- responsive rules are defined;
- fixed and generated regions are separated.

## 93. Gate 3 — Engineering

Before implementation:

- real repository was inspected;
- API and state ownership are mapped;
- file-change scope is defined;
- acceptance tests exist;
- unresolved blockers are explicit.

## 94. Gate 4 — Release

Before page approval:

- functional, scientific, governance, accessibility, responsive, and performance checks pass;
- canonical 1440 px visual regression passes;
- no global token/component fork was introduced;
- evidence and provenance are inspectable;
- all failed or deferred criteria are recorded.

---

# Part XII — Global Acceptance Checklist

## 95. Product Consistency

- [ ] The page has one clear mission.
- [ ] It belongs to one of the four approved primary areas.
- [ ] It does not mirror backend modules as user navigation.
- [ ] It answers Now / Why / Next / Basis / State.
- [ ] It preserves Project / Cycle / Stage / Object / Version context.

## 96. Scientific Integrity

- [ ] Scientific objects use the global hierarchy.
- [ ] Observed, predicted, inferred, and literature-reported states are distinct.
- [ ] Units and missing values are explicit.
- [ ] Claims expose evidence, assumptions, and limitations.
- [ ] Conflicting evidence is not hidden.
- [ ] Empty states are scientifically precise.

## 97. Governance and Traceability

- [ ] Consequential actions have explicit review states.
- [ ] Approval is object- and version-specific.
- [ ] Reject/override captures a reason.
- [ ] Provenance is available locally.
- [ ] Audit history identifies actor, action, object, time, and result.

## 98. Interaction Consistency

- [ ] Master–Detail and selection behavior follow the contract.
- [ ] Scientific detail does not rely on repeated modals.
- [ ] Inspector and Evidence Drawer preserve context.
- [ ] Search/filter scope is visible.
- [ ] Errors preserve user work and provide recovery.
- [ ] Browser navigation and deep links work.

## 99. Visual Consistency

- [ ] Shared tokens are used.
- [ ] Page uses the canonical shell.
- [ ] Typography and spacing match the system.
- [ ] Colors retain global semantic meaning.
- [ ] No unapproved component variants exist.
- [ ] The design avoids generic SaaS/dashboard styling.
- [ ] Charts use consistent scientific encodings.

## 100. Engineering Consistency

- [ ] Real backend schemas were inspected.
- [ ] No unsupported capability is presented as real.
- [ ] State has one owner.
- [ ] New modules register without rewriting AppShell.
- [ ] Heavy content is lazy-loaded or virtualized.
- [ ] Error boundaries preserve the workspace.
- [ ] Existing unrelated user changes remain untouched.

## 101. Final Experience Questions

The reviewer must answer:

1. Does this feel like a scientific engineering operating system?
2. Can a PI understand the current decision quickly?
3. Can a researcher inspect the scientific basis without losing task context?
4. Can a wet-lab user distinguish proposal from approved experiment?
5. Can a dry-lab user distinguish prediction from observation?
6. Can a maintainer add the next page without creating a new design language?
7. Would this page still make sense if all decorative graphics were removed?

Any “No” requires a recorded remediation or an approved exception.

---

# Part XIII — Recommended Project Structure

## 102. Root Design System

```text
Design_System/
├── Page_Design_Contract.md
├── Global_Product_Principles.md
├── Global_UI_System.md
├── Global_Component_Library.md
├── Global_Color_Tokens.md
├── Global_Typography_Tokens.md
├── Global_Interaction_Rules.md
├── Global_Scientific_Object_Model.md
├── Global_Visualization_Rules.md
├── Global_API_Contract.md
├── Global_State_Ownership.md
├── Global_Coding_Convention.md
├── Global_Accessibility_Requirements.md
└── CHANGELOG.md
```

This contract governs those files. They may expand details but may not contradict it.

## 103. Page Directories

```text
Page_Specs/
├── Page01_Project_Command_Center/
├── Page02_DBTL_Engineering_Workspace/
├── Page03_Knowledge_and_Evidence_Layer/
└── Page04_Trust_and_Provenance_Center/
```

Page 2 may contain stage subdirectories, but all five stages inherit one Workspace Product Spec and one shared interaction model.

## 104. Decision Records

Use two distinct record types:

```text
Design_System/decisions/
├── DSR-001-canonical-shell.md
├── DSR-002-observed-vs-predicted-encoding.md
├── DSR-003-evidence-drawer-behavior.md
├── ADR-001-state-ownership.md
└── ADR-002-graph-rendering-boundary.md
```

- **DSR — Design Decision Record**: layout, navigation, workflow presentation, interaction, visual encoding, or cross-page usability.
- **ADR — Architecture Decision Record**: framework boundary, state ownership, API adapter, rendering strategy, dependency, performance, or deployment.

Every material record MUST use:

```yaml
id:
type: DSR | ADR
title:
status: proposed | accepted | superseded | deprecated
date:
owners:
context:
decision:
alternatives:
  - option:
    reason_not_selected:
reason:
tradeoffs:
positive_consequences:
negative_consequences:
impact:
  pages:
  components:
  scientific_objects:
  APIs:
  tests:
reversal_or_migration:
supersedes:
approval:
```

A record is required when a decision affects more than one page; changes a global component, token, interaction, or state rule; introduces a dependency or architectural pattern; changes scientific encoding, provenance, or approval behavior; or rejects a plausible alternative with meaningful long-term consequences.

Routine implementation details do not require a record. A DSR/ADR documents a decision; it does not authorize violation of scientific truth, the Scope Lock, or the global contract.

---

# Part XIV — Completion Declaration

## 105. Required Declaration for Every Page

```markdown
## Page Contract Completion

- Page:
- Spec version:
- Parent contract version:
- Architecture version:
- Product gate: PASS / FAIL / BLOCKED
- Scientific gate: PASS / FAIL / BLOCKED
- Design gate: PASS / FAIL / BLOCKED
- Engineering gate: PASS / FAIL / BLOCKED
- Acceptance gate: PASS / FAIL / BLOCKED
- Approved exceptions:
- Deferred P3 items:
- Known risks:
- Reviewer:
- Approval date:
```

## 106. Stop Condition

The implementation agent MUST stop when all of the following are true:

```text
Approved scope implemented
AND required tests PASS
AND Acceptance Spec PASS
AND Regression Rule PASS
AND no blocking TODO, placeholder, mocked scientific result, or unresolved error remains
AND required decision, exception, and delivery records are complete
AND deferred work is explicitly listed
AND no Conditional Audit Gate remains open
```

The agent then MUST:

1. produce the Page Contract Completion declaration;
2. report changed files, verification, approved exceptions, deferred items, and known non-blocking risks;
3. stop editing.

After this condition is met, the agent MUST NOT continue visual polishing, refactor adjacent modules, add “helpful” features, expand P2/P3 scope, or revisit accepted decisions without a new request or failed gate.

If a gate cannot pass, return `BLOCKED` or `FAIL` with concrete evidence and the smallest required next decision. Do not conceal the failure, relax the criterion, or continue indefinitely.

## 107. Final Rule

If a design decision cannot be traced to:

- a global contract rule;
- an approved page-specific requirement;
- a scientific need;
- a user workflow need;
- or a documented exception,

then it must not enter the final page.

This contract is the common language connecting scientific reasoning, product design, generated visuals, frontend code, and acceptance. All future pages must remain members of one coherent Synthetic Biology DBTL Engineering OS.

---

# Part XV — Contract Runtime

## 108. Runtime Purpose

This section defines how the contract is executed. Reading the document without
following this runtime is non-compliant.

## 109. Runtime State Machine

```text
LOAD
→ RESOLVE
→ INSPECT
→ PLAN
→ IMPLEMENT
→ VERIFY
→ ACCEPT
→ REGRESS
→ DELIVER
→ STOP
```

| State | Required operation | Exit evidence |
| --- | --- | --- |
| `LOAD` | Read the parent architecture, exact contract version, all approved Page Specs, relevant DSR/ADR, and canonical design | source manifest |
| `RESOLVE` | Detect contradictions, apply Decision Hierarchy, classify invariant or approval blockers | conflict matrix |
| `INSPECT` | Audit repository, protected surfaces, real schemas, existing components, dependencies, tests, and dirty work | repository audit |
| `PLAN` | Define locked scope, file-change list, reuse/extend/new inventory, tests, rollback, and deferred work | implementation plan |
| `IMPLEMENT` | Make the smallest approved changes in dependency order | scoped code and records |
| `VERIFY` | Run build, types, lint, tests, accessibility, responsive, performance, and scientific-state checks | verification evidence |
| `ACCEPT` | Evaluate every Page Acceptance criterion and scientific review item | acceptance matrix |
| `REGRESS` | Execute the seven-domain Regression Matrix against affected existing behavior | regression matrix |
| `DELIVER` | Produce completion declaration, change summary, decisions, exceptions, risks, and deferred items | delivery report |
| `STOP` | Cease edits once Section 106 is satisfied | final state |

No state may be silently skipped. A failed exit condition returns to the
smallest relevant earlier state; it does not authorize unrelated redesign.

## 110. Source Manifest

Before implementation, record:

```yaml
architecture_document:
contract_document:
contract_version:
page_specs:
decision_records:
exception_records:
canonical_visual:
repository_commit_or_state:
backend_schema_version:
unresolved_sources:
```

Missing optional material may be recorded as `not_applicable`. Missing required
material is `BLOCKED`.

## 111. Conflict Matrix

Each detected conflict must be resolved as:

```yaml
conflict_id:
sources:
conflicting_requirements:
hierarchy_level:
invariant_affected:
resolution:
authority:
implementation_effect:
record_required:
status: resolved | blocked
```

Silently merging contradictory requirements is prohibited.

## 112. Runtime Refusal Rules

The agent must refuse or pause the affected action—not the entire safe task—
when asked to:

- violate a System Invariant;
- fabricate scientific truth, evidence, provenance, measurements, or backend behavior;
- bypass human approval, authorization, safety, or audit controls;
- conceal failed acceptance, regression, uncertainty, or contradictory evidence;
- destructively alter protected or unrelated work without explicit authority;
- proceed when a material conflict lacks an authorized resolution.

The response must identify the exact blocked action, evidence, applicable rule,
and smallest user or owner decision needed.

## 113. Runtime Completion Report

The delivery report must contain:

```markdown
## Contract Runtime Result

- Runtime states completed:
- Source manifest:
- Locked scope:
- Files changed:
- Reused / extended / new components:
- DSR / ADR:
- Exceptions:
- Verification:
- Scientific review:
- Acceptance matrix:
- Regression matrix:
- Deferred items:
- Known risks:
- Conditional Audit Gates:
- Stop Condition: PASS / FAIL / BLOCKED
```

## 114. Runtime Finality

`PASS` means the requested scope is complete under the declared versions; it
does not mean the whole product is finished. After `STOP`, any additional
feature, refactor, polish, architecture change, or page expansion requires a
new authorized request and a new runtime cycle.

The Contract Runtime is the only valid path from approved specification to
delivered page.
