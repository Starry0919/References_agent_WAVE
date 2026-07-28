```yaml
page_id: page-01
page_name: Project Command Center
spec_type: Product Spec
version: 2.1.0
status: Approved
owners:
  - Product Owner
reviewers:
  - Synthetic Biology Reviewer
  - UX Reviewer
parent_contract: Page Design Contract v1.2.0
parent_architecture: Frontend Architecture Prompt v1.2
last_updated: 2026-07-23
dependencies:
  - 02_UI_Spec.md
  - 03_Interaction_Spec.md
  - 05_Content_Spec.md
open_questions:
  - See "Part Z — Contract Cross-Reference & Gap Map" appendix at the end of this document
approved_exceptions: []
```

> **Spec Package normalization note (2026-07-23)**: this document's body (Sections 00–16 below) is
> the pre-existing, approved Page 1 product definition (previously versioned "v2.0"). Its text has
> **not been rewritten, reworded, or reorganized** during normalization — only this header and the
> "Contract Cross-Reference & Gap Map" appendix at the end were added, to satisfy Page Design
> Contract v1.2.0 §75 (Spec Header) and to make required-section coverage traceable per §77. No
> product decision, scope, or positioning was changed.

---

# ============================================================
# Synthetic Biology DBTL Engineering OS
# Page Constitution
# Page 01 — Project Command Center
# Version: v2.0
# ============================================================

> This document is NOT a feature specification.
>
> It is the constitutional contract of Page 01.
>
> Every UI, interaction, component, backend integration,
> animation and future iteration MUST comply with this document.
>
> This page defines the identity of the entire product.

---

# 00. Product Identity

## Official Name

Project Command Center

## Product Identity

The Project Command Center is the Mission Control of the entire Synthetic Biology DBTL Engineering OS.

It is NOT a dashboard.

It is NOT a homepage.

It is NOT a report.

It is NOT a chatbot.

It is the persistent operational interface that continuously answers one question:

> **What is happening in my engineering project right now?**

Everything displayed on this page exists solely to answer that question.

---

## Identity Keywords

Mission Control

Scientific Operating System

Persistent Workspace

Decision Center

Engineering Awareness

Human Governance

Scientific Transparency

Traceability

Trust

---

## Responsibilities

The page is responsible for:

• maintaining global project awareness

• summarizing the current engineering state

• exposing scientific evidence

• visualizing engineering progress

• exposing project risks

• surfacing pending approvals

• recommending next actions

• navigating to deeper workspaces

---

## The page is NOT responsible for

Editing experiments

Editing workflows

Engineering design

Knowledge editing

Prompt editing

Simulation execution

Database browsing

Chat conversation

These belong to dedicated workspaces.

---

# 01. Product Mission

## Mission Statement

The Project Command Center provides a persistent, real-time overview of the complete DBTL engineering lifecycle.

Within ten seconds of opening this page, every user should understand:

What project is active.

Where the engineering currently stands.

What has already been completed.

What evidence supports the current direction.

What risks remain.

What requires human approval.

What should happen next.

No other page should be required to understand the overall state of the project.

---

## Product Promise

This page promises:

Complete awareness.

Minimal cognitive load.

Maximum scientific transparency.

Continuous project orientation.

Reliable engineering status.

Persistent context.

---

# 02. Scientific Role

This page represents the orchestration layer of the DBTL Engineering System.

It never performs engineering itself.

Instead it orchestrates scientific awareness.

Scientific Mapping

Research Goal

↓

Knowledge

↓

Engineering Design

↓

Build

↓

Experiment

↓

Validation

↓

Learning

↓

Iteration

↓

Next Action

The page continuously summarizes this lifecycle.

---

# 03. Product Philosophy

Traditional dashboards visualize metrics.

The Project Command Center visualizes scientific understanding.

Traditional dashboards answer:

"What happened?"

The Project Command Center answers:

What are we trying to achieve?

Why are we doing this?

How confident are we?

What evidence supports it?

What risks remain?

What should happen next?

Who needs to make the decision?

The page exists to improve scientific decision making rather than information display.

---

# 04. Mental Model

Every user should naturally build the following mental model.

Project

↓

Current Iteration

↓

Engineering Objective

↓

Scientific Bottleneck

↓

Engineering Strategy

↓

Supporting Evidence

↓

Validation Plan

↓

Remaining Risks

↓

Next Action

↓

Future Iteration

The UI should reinforce this model continuously.

No widget should violate this hierarchy.

---

# 05. User Personas

## Principal Investigator

Primary Goal

Understand project health immediately.

Key Questions

Is the project progressing?

Which risks exist?

What requires approval?

Can I trust the current recommendation?

What experiments remain?

Success

PI understands the project within ten seconds.

---

## Synthetic Biology Researcher

Primary Goal

Understand today's engineering problem.

Questions

Current bottleneck?

Current strategy?

Supporting literature?

Evidence quality?

Recommended engineering?

Success

Research direction is immediately clear.

---

## Wet Lab Scientist

Primary Goal

Understand experimental validation.

Questions

Which protocol?

Which strain?

Which measurement?

Expected phenotype?

Success

Experiments become executable.

---

## Dry Lab Scientist

Primary Goal

Understand computational progress.

Questions

Simulation status?

Prediction confidence?

Available datasets?

Pending analysis?

Success

Computational progress is immediately visible.

---

## Student

Primary Goal

Understand the project.

Questions

Where am I?

What is happening?

What should I learn next?

Success

No onboarding required.

---

# 06. User Journey

Typical flow

Open website

↓

Understand project

↓

Understand engineering state

↓

Review evidence

↓

Review risks

↓

Approve or investigate

↓

Navigate into detailed workspace

↓

Continue engineering

The homepage should never become the engineering workspace itself.

---

# 07. Scientific Workflow Mapping

The page summarizes the entire DBTL workflow.

Research Goal

↓

Knowledge Retrieval

↓

Diagnosis

↓

Engineering Design

↓

Simulation

↓

Validation Planning

↓

Wet Lab

↓

Data Analysis

↓

Learning

↓

Iteration

↓

Project Evolution

The page represents all stages simultaneously.

---

# 08. Information Architecture

Information hierarchy follows awareness rather than functionality.

Level 1

Global Awareness

Current Objective

Current Stage

Project Health

Critical Alerts

Next Action

--------------------

Level 2

Engineering Status

Evidence Summary

Simulation Status

Knowledge Updates

Pending Reviews

Project Timeline

--------------------

Level 3

Scientific Reports

Historical Iterations

Execution Logs

Prompt History

Raw Evidence

Everything deeper than Level 3 belongs to another page.

---

# 09. Decision Architecture

Every module should help answer one or more of the following questions.

What happened?

Why did it happen?

How certain are we?

Can this be trusted?

What evidence supports it?

Should we approve?

Should we reject?

What should happen next?

No widget exists merely to display data.

Every widget exists to improve decisions.

---

# 10. Backend Responsibilities

The frontend NEVER performs scientific reasoning.

Frontend Responsibilities

Visualization

Aggregation

Navigation

Explanation

Interaction

Progressive Disclosure

Backend Responsibilities

Scientific reasoning

Knowledge retrieval

Evidence scoring

Simulation

Workflow orchestration

Engineering planning

Risk evaluation

Validation generation

The frontend must remain deterministic.

---

# 11. Success Definition

This page succeeds only when users achieve:

Awareness

Orientation

Understanding

Trust

Decision readiness

Navigation

without opening additional pages.

---

# 12. Design Principles

Scientific First

Evidence Before Conclusion

Human Before Agent

Progressive Disclosure

Persistent Workspace

Single Source of Truth

Everything Explainable

Everything Traceable

Minimal Cognitive Load

No Decorative Information

Every Pixel Has Purpose

---

# 13. Emotional Goal

Users should feel

"I understand the project."

"I trust the system."

"I know what to do."

"I remain in control."

Users should never feel

Overwhelmed

Lost

Distracted

Confused

Manipulated

The page should communicate calmness, confidence and scientific rigor.

---

# 14. Explicit Non-goals

This page must NEVER become

A chatbot

A workflow editor

An experiment editor

A notebook

A database browser

A paper viewer

A report page

A settings page

Adding these functions violates the page identity.

---

# 15. Future Evolution Boundary

Future iterations may add

New metrics

New scientific widgets

New visualization

New notifications

New evidence summaries

Future iterations must NEVER add

Workflow editing

Experiment editing

Knowledge editing

Prompt editing

Chat interfaces

Scientific computation

Those belong to dedicated workspaces.

---

# 16. Page Constitution

The identity of this page is immutable.

Regardless of future versions, redesigns or feature additions, the Project Command Center must always remain:

The Mission Control of the Synthetic Biology DBTL Engineering OS.

It exists to maximize scientific awareness, engineering transparency, decision quality and human governance.

Every future modification must strengthen this identity rather than weaken it.

If a new feature does not improve project awareness, scientific understanding or engineering decision making, it does not belong on this page.

---

# Part Z — Contract Cross-Reference & Gap Map

> Added during Spec Package normalization (2026-07-23). Maps this document's existing sections
> (00–16 above) to Page Design Contract v1.2.0 §77 Required Sections. Nothing in Sections 00–16 was
> altered to produce this map. Items marked `GAP` are genuinely absent from the approved content and
> are **not** invented here — they require a follow-up product decision by the page owner.

| §77 Required Section | Coverage | Source in this document |
| --- | --- | --- |
| Mission | Covered | §01 Product Mission |
| Scientific Purpose | Covered | §02 Scientific Role |
| DBTL Mapping | Covered | §02 Scientific Mapping; §07 Scientific Workflow Mapping |
| Target Users | Covered | §05 User Personas |
| Jobs to Be Done | Partial | §05 User Personas ("Primary Goal" per persona is JTBD-equivalent but not phrased as formal JTBD statements) |
| User Goals by Role | Covered | §05 User Personas ("Questions" / "Success" per persona) |
| Primary User Story | Partial | §06 User Journey (a flow, not phrased as "As a ⟨role⟩, I want ⟨goal⟩ so that ⟨outcome⟩") |
| Secondary User Stories | `GAP` | Not present |
| Entry Points | `GAP` | Not explicitly enumerated (implied: direct navigation, deep link, notification — not confirmed) |
| Exit and Handoff | Partial | §06 User Journey ends at "Navigate into detailed workspace"; specific handoff targets/state per destination not enumerated |
| Page Responsibilities | Covered | §00 Responsibilities / "The page is NOT responsible for" |
| Explicit Non-Goals | Covered | §14 Explicit Non-goals |
| Scientific Workflow Mapping | Covered | §07 Scientific Workflow Mapping |
| Backend Capability Mapping | Partial | §10 Backend Responsibilities (qualitative categories only; no endpoint/schema-level mapping — full mapping belongs in `04_Technical_Spec.md` §80 Backend Mapping Table, currently blocked pending repository audit) |
| Information Priority | Covered | §08 Information Architecture (Level 1–3) |
| Main Decisions and Actions | Covered | §09 Decision Architecture |
| Risks and Failure Modes | `GAP` | §00 references "exposing project risks" as a responsibility, but no risk taxonomy or failure-mode enumeration exists |
| Product Success Metrics | Partial | §11 Success Definition is qualitative ("Awareness, Orientation, Understanding, Trust..."); no measurable thresholds (contract §9.1 asks for e.g. "within 30 seconds") are defined |
| Dependencies | `GAP` | Not listed in original body (now partially captured in the YAML header above) |
| Open Questions | `GAP` | Not listed in original body |
| Required Priority Format (P0–P3) | `GAP` | No P0–P3 prioritization of requirements exists anywhere in this document |

**Unresolved cross-document conflict (not resolved by this normalization pass):** none identified
between this document and the Global Contract at the product-definition level. Conflicts identified
at the UI/visual level are recorded in `02_UI_Spec.md` Part Z instead.

**Recommended next step (decision, not executed here):** the page owner should decide whether to (a)
author the `GAP` items above as a targeted addendum to this file, or (b) accept them as intentionally
deferred and record them as `open_questions` for Gate 1 sign-off.