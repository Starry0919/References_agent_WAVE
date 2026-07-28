# Synthetic Biology DBTL Engineering OS

# Page 04 — Trust & Provenance Center

# 02_UI_Spec.md

> **Document type**: Page-specific visual and interface specification
> **Page**: Page 04 — Trust & Provenance Center
> **Product role**: Trust, Governance & Provenance Control Plane
> **Status**: Normative / Implementation-Binding
> **Parent contract**: Page Design Contract v1.2.0
> **Parent architecture**: Synthetic Biology DBTL Engineering OS Frontend Architecture v1.2
> **Parent product spec**: Page 04 `01_Product_Spec.md` v1.0.0
> **Default UI language**: English
> **Specification language**: English, with implementation notes permitted in Chinese
> **Version**: 1.0.0
> **Last updated**: 2026-07-23

---

## Specification Header

```yaml
page_id: page-04
page_name: Trust & Provenance Center
spec_type: UI Spec
version: 1.0.0
status: Approved
product_positioning: Trust, Governance & Provenance Control Plane
owners:
  - Product Owner
  - UX Lead
  - Scientific Product Lead
  - Governance Owner
reviewers:
  - Principal Investigator
  - Synthetic Biology Reviewer
  - Dry-Lab Reviewer
  - Wet-Lab Reviewer
  - Governance Reviewer
  - Frontend Architect
  - Accessibility Reviewer
parent_contract: Page Design Contract v1.2.0
parent_architecture: Frontend Architecture Prompt v1.2
parent_product_spec: Page04/01_Product_Spec.md
dependencies:
  - 00_Page_Research.md
  - 01_Product_Spec.md
  - 03_Operating_Principles.md
  - 04_Interaction_Spec.md
  - 05_Technical_Spec.md
  - 06_Content_Spec.md
  - 07_Acceptance_Spec.md
approved_exceptions: []
open_questions: []
```

---

# Part I — Visual Identity

## 1. UI Mission

The Page 04 interface must help authorized users:

* identify which trust, governance, provenance, memory, approval, or evaluation issue requires attention;
* understand why the issue matters;
* inspect the exact object and version involved;
* reconstruct the causal and computational history;
* evaluate evidence, risk, uncertainty, and policy compliance;
* make a governed decision;
* record corrective action;
* return to the originating scientific workflow without losing context.

The page must visually communicate:

```text
Attention
→ Governed Object
→ Basis
→ History
→ Decision
→ Consequence
```

The visual center is not the system itself.

The visual center is:

> **The consequential object, decision, event, memory, approval, or evaluation currently being governed.**

---

## 2. Desired Visual Character

The page should feel like:

* a scientific review room;
* a version-control inspection workspace;
* an audit and approval console;
* a high-trust research governance environment;
* an incident investigation surface;
* an evaluator workbench.

It should not feel like:

* an admin dashboard;
* a cybersecurity console;
* a raw log viewer;
* a banking compliance system;
* a KPI analytics page;
* a generic ticketing queue;
* a model leaderboard;
* a chatbot.

---

## 3. Visual Design Principles

### 3.1 Object Before Metric

The page must prioritize governed objects, decisions, versions, and review states over aggregate counts.

Metrics may orient the user, but must not dominate the workspace.

### 3.2 Attention Before Exploration

Users should first see:

* what requires action;
* why it requires action;
* what risk or consequence exists;
* who owns the next decision.

### 3.3 Basis Before Decision

Approval, rejection, restriction, or override controls must never visually precede:

* evidence;
* provenance;
* changes;
* risk;
* limitations;
* downstream effect.

### 3.4 History Without Log Noise

History should be presented as structured scientific and governance events, not as an unfiltered infrastructure log stream.

### 3.5 Immutable History, Explicit Current State

Historical events should appear stable and inspectable.

The current actionable object or request should remain visually distinct from historical records.

### 3.6 Trust Is Multidimensional

The UI must never reduce trust to one green, yellow, or red score.

Trust should be represented through separate dimensions such as:

* evidence completeness;
* provenance completeness;
* approval state;
* evaluation result;
* memory validity;
* reproducibility;
* unresolved risk.

### 3.7 Human Authority Is Visible

The interface must show:

* who may decide;
* who requested the decision;
* who previously reviewed it;
* whether the current user has authority;
* what action will occur after a decision.

---

# Part II — Page Anatomy

## 4. Canonical Page Structure

The canonical desktop anatomy is:

```text
┌──────────────────────────────────────────────────────────────────────┐
│ Global Application Shell                                             │
├──────────────────────────────────────────────────────────────────────┤
│ Context Header                                                       │
│ Project / Cycle / Source Object / Version / Governance Status         │
├───────────────┬──────────────────────────────────────┬───────────────┤
│ Governance    │ Primary Governance Workspace         │ Inspector /   │
│ Navigation    │                                      │ Decision Rail │
│               │ Attention Queue or Selected Object   │               │
│               │                                      │               │
├───────────────┴──────────────────────────────────────┴───────────────┤
│ Expandable Provenance / Audit / Evaluation Detail Region             │
└──────────────────────────────────────────────────────────────────────┘
```

The page must preserve the global application shell defined by the parent contract.

---

## 5. Canonical Regions

### 5.1 Context Header

Purpose:

* orient the user;
* preserve cross-page context;
* expose selected object and version;
* show governance status;
* provide return path.

Required content:

* breadcrumb;
* project;
* DBTL cycle;
* source page or stage;
* selected object;
* object version;
* current governance state;
* owner;
* freshness or historical state;
* return-to-source action.

The header must not become an oversized hero section.

---

### 5.2 Governance Navigation

Purpose:

* provide stable movement among major Page 04 work modes.

Recommended primary navigation items:

1. Attention
2. Approvals
3. Provenance
4. Memory
5. Audit
6. Evaluation

These are work modes, not independent mini-products.

Recommended order:

```text
Attention
→ Approvals
→ Provenance
→ Memory
→ Audit
→ Evaluation
```

The navigation must support:

* active state;
* pending count where meaningful;
* critical-state marker;
* permission-aware visibility;
* compact collapsed state.

Navigation counts must not replace meaningful status.

---

### 5.3 Primary Governance Workspace

Purpose:

* hold the main task;
* show selected governed object;
* present basis and risk;
* support review, investigation, comparison, or evaluation.

The workspace changes according to mode but retains common structure:

```text
Workspace Header
→ Orientation Summary
→ Primary Object or Queue
→ Supporting Basis
→ Current Decision or Investigation
```

---

### 5.4 Inspector / Decision Rail

Purpose:

* preserve selected-object context;
* expose essential metadata;
* show governance actions;
* show next action and downstream effect.

The rail must be selection-driven.

Recommended sections:

1. Object Identity
2. Current State
3. Version
4. Owner and Actors
5. Trust Dimensions
6. Required Action
7. Downstream Effect
8. Related Objects
9. Governance Actions

The action region should remain visible when the user scrolls through the basis.

---

### 5.5 Expandable Detail Region

Purpose:

* expose deep provenance, audit history, evaluation detail, or raw reproducibility data without overloading the primary workspace.

Permitted contents:

* full provenance chain;
* audit timeline;
* prompt/model/tool metadata;
* parameter diff;
* evidence detail;
* evaluation failure examples;
* raw event payload;
* exportable governance record.

This region may be:

* a bottom drawer;
* an expandable split pane;
* a full-height side drawer;
* a dedicated detail route for exceptionally complex content.

It must preserve the selected object.

---

# Part III — Workspace Modes

## 6. Attention Workspace

### Purpose

Provide a prioritized view of trust and governance issues requiring attention.

### Must Show

* pending approval;
* provenance gap;
* stale or conflicting memory;
* evaluation regression;
* unauthorized or failed transition;
* unresolved override;
* reproducibility failure;
* approval expiry;
* object affected;
* consequence;
* owner;
* required action.

### Recommended Layout

```text
Attention Summary Strip
→ Prioritized Attention Queue
→ Selected Issue Detail
→ Decision or Remediation Rail
```

### Attention Queue Row

Each row should include:

* issue type;
* affected object;
* project or cycle;
* severity;
* reason;
* age;
* owner;
* required action;
* governance state.

The queue must not resemble a generic support-ticket list.

The scientific or governance consequence must remain visible.

---

## 7. Approval Workspace

### Purpose

Support review and decision for consequential object transitions.

### Recommended Layout

```text
Approval Queue
→ Selected Approval Package
→ Version / Change Comparison
→ Evidence, Risk, and Validation
→ Decision Rail
```

### Approval Package Visual Order

1. Requested Transition
2. Target Object and Version
3. Scientific Purpose
4. Changed Since Previous Version
5. Evidence and Contradiction
6. Risk and Trade-off
7. Assumptions and Limitations
8. Validation Requirements
9. Downstream Effect
10. Prior Review History
11. Decision Controls

Decision controls must not appear as the dominant first visual element.

### Required Decisions

* Approve
* Reject
* Request Changes
* Override with Reason, when authorized

Approval must display the exact version being approved.

---

## 8. Provenance Workspace

### Purpose

Reconstruct how an object or output was produced.

### Recommended Layout

```text
Selected Object
→ Provenance Path
→ Stage Details
→ Version and Artifact Links
→ Reproducibility Status
```

### Canonical Provenance Visualization

```text
Input
→ Retrieved Knowledge and Memory
→ Prompt or Task
→ Agent and Model
→ Tools and Parameters
→ Intermediate Artifacts
→ Generated Output
→ Evaluation
→ Human Review
→ Approval
→ Execution
→ Observation
```

The visualization should support:

* horizontal or vertical path;
* selectable stages;
* missing-stage indicator;
* status per stage;
* object and version links;
* compact summary;
* table fallback.

The path must not become an uncontrolled graph.

### Provenance Stage Card

Each stage card should show:

* stage type;
* actor;
* version;
* timestamp;
* status;
* primary input;
* primary output;
* provenance completeness;
* inspect action.

---

## 9. Memory Governance Workspace

### Purpose

Inspect, review, correct, supersede, restrict, or retire persistent memory.

### Recommended Layout

```text
Memory Scope and Filters
→ Memory Object List
→ Selected Memory Detail
→ Usage and Impact
→ Governance Actions
```

### Memory List Must Show

* memory type;
* title;
* scope;
* source;
* status;
* freshness;
* version;
* last used;
* risk state;
* review state.

### Memory Detail Must Show

* content summary;
* original source;
* scope;
* validity conditions;
* usage history;
* affected projects or decisions;
* conflicts;
* previous versions;
* proposed correction;
* review history.

### Memory Risk Presentation

The UI must visually distinguish:

* stale;
* conflicting;
* unsupported;
* scope mismatch;
* sensitive;
* superseded;
* restricted;
* under review.

Risk must not rely on color alone.

---

## 10. Audit Workspace

### Purpose

Reconstruct chronological and causal system history.

### Recommended Layout

```text
Audit Scope and Filters
→ Structured Event Timeline or Table
→ Selected Event Inspector
→ Related Object History
```

### Audit Presentation Modes

Supported views:

* Timeline
* Table
* Object History
* Version History
* Causal Chain

Timeline is appropriate for chronological investigation.

Table is appropriate for filtering and exact comparison.

Causal chain is appropriate when several events led to one outcome.

### Audit Event Display

Each event should expose:

* actor;
* action;
* target;
* target version;
* timestamp;
* previous state;
* new state;
* reason;
* result;
* related project or cycle;
* related evidence or approval;
* failure or retry state.

Low-level infrastructure noise should not dominate the default view.

---

## 11. Evaluation Workspace

### Purpose

Assess agents, models, prompts, tools, retrieval strategies, workflows, and outcomes.

### Recommended Layout

```text
Evaluation Target and Version
→ Baseline Comparison
→ Dimension Results
→ Scientific Slice Analysis
→ Failure Examples
→ Governance Decision
```

### Evaluation Overview

Must show:

* target;
* target version;
* evaluation suite;
* baseline;
* run time;
* review state;
* overall outcome;
* material regression;
* limitation.

### Dimension Presentation

Recommended dimensions:

* correctness;
* evidence support;
* provenance completeness;
* contradiction handling;
* uncertainty;
* context match;
* biological plausibility;
* actionability;
* governance compliance;
* reproducibility;
* latency or cost where relevant.

Avoid using a single radar chart as the only evaluation representation.

Preferred forms:

* aligned score rows;
* comparison table;
* dot plot;
* compact bars;
* pass/fail/blocked matrix.

### Failure Example Presentation

Each failure example should show:

* input or task;
* expected behavior;
* actual output;
* failure category;
* affected scientific object;
* source or evidence;
* severity;
* reproducibility;
* remediation state.

---

# Part IV — Visual Hierarchy

## 12. Primary Reading Order

The default reading order must be:

```text
Where am I?
→ What requires attention?
→ Which object and version are involved?
→ Why does it matter?
→ What supports or contradicts it?
→ What happened previously?
→ What decision is required?
→ What happens next?
```

---

## 13. Dominant Focus

Every viewport must contain one primary focus.

Examples:

* one selected approval request;
* one provenance chain;
* one memory object;
* one audit event;
* one evaluation target.

The page must not show several equal-priority dashboard panels.

---

## 14. Visual Weight

Highest visual weight:

* active governed object;
* requested transition;
* material risk;
* required human decision;
* critical regression;
* provenance gap.

Medium visual weight:

* evidence summary;
* change comparison;
* trust dimensions;
* review history;
* affected objects.

Lower visual weight:

* IDs;
* timestamps;
* secondary metadata;
* low-risk historical events;
* configuration detail.

---

## 15. Visual Rhythm Map

Each canonical Page 04 layout should follow:

```text
Context Header — orient
Governance Navigation — support
Attention or Object Summary — focus
Evidence / History / Evaluation Region — dense
Decision Rail — focus
Deep Provenance or Raw Detail — dense
Footer / Completion State — rest
```

Required rhythm labels:

| Region                               | Rhythm  |
| ------------------------------------ | ------- |
| Context Header                       | orient  |
| Navigation                           | support |
| Active Object Summary                | focus   |
| Queue / Timeline / Evaluation Detail | dense   |
| Decision Rail                        | focus   |
| Provenance Detail                    | dense   |
| Completion / Empty Closure           | rest    |

---

# Part V — Layout System

## 16. Desktop Baseline

Canonical acceptance viewport:

```text
1440 × 1024
Theme: Light
Density: Expert
Navigation: Expanded
Inspector: Open
Data State: Normal
```

Recommended baseline dimensions:

* global navigation: inherited from AppShell;
* local governance navigation: 184–220 px;
* primary workspace: flexible, minimum 720 px;
* inspector or decision rail: 320–380 px;
* major gap: 16 px;
* panel padding: 16–24 px.

Exact values must adapt to the real repository tokens.

---

## 17. Wide Desktop — 1920 px and Above

* full governance navigation visible;
* primary workspace and inspector coexist;
* provenance chain may render horizontally;
* comparison views may show three or more aligned columns;
* evaluation slices and failure detail may coexist;
* no unnecessary oversized gutters.

---

## 18. Standard Desktop — 1600 to 1919 px

* full navigation retained;
* inspector remains docked;
* provenance chain may scroll inside its region;
* dense tables use column prioritization;
* secondary metadata may collapse into expandable groups.

---

## 19. Baseline Desktop — 1440 to 1599 px

* approved canonical composition;
* navigation, primary workspace, and inspector visible;
* bottom detail region collapsible;
* long comparison content scrolls within its container;
* decision rail remains visible.

---

## 20. Compact Desktop — 1280 to 1439 px

* governance navigation may collapse to icon-and-label compact mode;
* inspector may reduce width;
* evidence and history sections may stack;
* provenance path may become vertical;
* secondary action labels may move into overflow;
* primary decision and risk remain visible.

---

## 21. Review / Tablet — 1024 to 1279 px

* navigation becomes compact rail or drawer;
* inspector becomes overlay drawer;
* queue and detail use master–detail transition;
* complex editing may be limited;
* approval review remains available;
* approval action must remain reachable without losing basis;
* evaluation and audit tables may use responsive column control.

---

## 22. Below 1024 px

The page prioritizes:

* review;
* inspection;
* approval status;
* essential decision action;
* audit reconstruction.

Complex multi-object comparison, graph exploration, or large-table editing may be explicitly limited.

The page must state when desktop is required for a complex governance action.

---

# Part VI — Shared Component Reuse

## 23. Required Global Components

The page must reuse:

* `AppShell`
* `PrimaryNavigation`
* `ContextHeader`
* `Breadcrumb`
* `ProjectSwitcher`
* `ConnectionStatus`
* `WorkspaceFrame`
* `InspectorPanel`
* `EvidenceDrawer`
* `ResizableSplitPane`
* `ScientificObjectHeader`
* `ObjectStatusBadge`
* `VersionBadge`
* `ProvenanceStamp`
* `ConfidenceIndicator`
* `DataTable`
* `ComparisonTable`
* `Timeline`
* `DiffViewer`
* `AuditTimeline`
* `ApprovalBar`
* `ReviewThread`
* `OverrideWithReason`
* `ActorStamp`
* `InlineAlert`
* `StaleDataBanner`
* `EmptyState`
* `ErrorState`
* `UnavailableState`
* `PartialDataState`

Page-local copies are prohibited.

---

## 24. Page-Specific Components

Permitted Page 04 components include:

* `GovernanceNavigation`
* `AttentionQueue`
* `AttentionIssueRow`
* `TrustDimensionSummary`
* `ApprovalPackage`
* `ApprovalDecisionRail`
* `ProvenancePath`
* `ProvenanceStageCard`
* `ProvenanceCompleteness`
* `MemoryGovernanceList`
* `MemoryUsageMap`
* `MemoryRiskSummary`
* `AuditCausalChain`
* `EvaluationTargetHeader`
* `EvaluationDimensionMatrix`
* `EvaluationFailureExample`
* `RegressionSummary`
* `GovernanceActionCard`
* `AffectedObjectsPanel`
* `ReproducibilityStatus`

Each component must map to a real product need.

---

## 25. Shared Component Reuse Matrix

| Need               | Shared Component         | Page-Specific Extension             |
| ------------------ | ------------------------ | ----------------------------------- |
| Page context       | `ContextHeader`          | Governance status and source return |
| Object identity    | `ScientificObjectHeader` | Trust and review metadata           |
| Approval           | `ApprovalBar`            | `ApprovalDecisionRail`              |
| History            | `AuditTimeline`          | Scientific event grouping           |
| Version comparison | `DiffViewer`             | Approval-aware field grouping       |
| Object selection   | `InspectorPanel`         | Governance actions                  |
| Evidence           | `EvidenceDrawer`         | Approval package evidence mode      |
| Table              | `DataTable`              | Audit and memory columns            |
| Comparison         | `ComparisonTable`        | Evaluation baseline comparison      |
| Status             | `ObjectStatusBadge`      | Governance vocabulary               |
| Provenance         | `ProvenanceStamp`        | Full `ProvenancePath`               |
| Actor              | `ActorStamp`             | Role and authority state            |

---

# Part VII — Component Records

## 26. Attention Issue Card

```yaml
component: AttentionIssueCard
purpose: Represent one actionable trust or governance issue
scientific_object: Governance Issue
priority: P0
default_state: Unselected
interactive_states:
  - hover
  - selected
  - focused
  - loading
  - resolved
  - blocked
content_fields:
  - issue_type
  - affected_object
  - object_version
  - project_or_cycle
  - reason
  - severity
  - required_action
  - owner
  - age
  - governance_status
primary_action: Inspect
secondary_actions:
  - Assign
  - Open source object
  - Mark reviewed when permitted
shared_or_page_specific: Page-specific
responsive_behavior: Compress metadata before hiding consequence
accessibility: Full issue summary available to screen reader
```

---

## 27. Approval Package

```yaml
component: ApprovalPackage
purpose: Present all information required for a governed decision
scientific_object: Approval Request
priority: P0
default_state: In Review
interactive_states:
  - loading
  - partial
  - changes_requested
  - approved
  - rejected
  - expired
content_fields:
  - requested_transition
  - target_object
  - target_version
  - scientific_purpose
  - change_summary
  - evidence
  - conflicting_evidence
  - risk
  - tradeoffs
  - assumptions
  - limitations
  - validation_requirements
  - downstream_effect
  - review_history
primary_action: Review decision
secondary_actions:
  - Compare version
  - Inspect provenance
  - Open source object
shared_or_page_specific: Page-specific
responsive_behavior: Stack sections; preserve requested transition and version
accessibility: Structured headings and review summary
```

---

## 28. Provenance Stage Card

```yaml
component: ProvenanceStageCard
purpose: Represent one stage in an object provenance chain
scientific_object: Provenance Stage
priority: P0
default_state: Complete
interactive_states:
  - selected
  - missing
  - partial
  - failed
  - stale
  - permission_restricted
content_fields:
  - stage_type
  - actor
  - model_or_tool
  - version
  - timestamp
  - input_summary
  - output_summary
  - status
  - completeness
primary_action: Inspect stage
secondary_actions:
  - Open artifact
  - Compare version
  - View audit event
shared_or_page_specific: Page-specific
responsive_behavior: Horizontal card becomes vertical step
accessibility: Ordered list semantics for chain
```

---

## 29. Memory Object Row

```yaml
component: MemoryObjectRow
purpose: Represent one governed memory object
scientific_object: Memory Object
priority: P0
default_state: Active
interactive_states:
  - selected
  - stale
  - conflicting
  - restricted
  - superseded
  - under_review
content_fields:
  - memory_type
  - title
  - scope
  - source
  - version
  - freshness
  - last_used
  - review_status
  - risk_state
primary_action: Inspect memory
secondary_actions:
  - View usage
  - Compare version
  - Request review
shared_or_page_specific: Page-specific
responsive_behavior: Hide low-priority metadata through column control
accessibility: Row state must be textually announced
```

---

## 30. Evaluation Failure Example

```yaml
component: EvaluationFailureExample
purpose: Expose one concrete system evaluation failure
scientific_object: Evaluation Failure
priority: P1
default_state: Unresolved
interactive_states:
  - selected
  - reproduced
  - remediated
  - accepted_limitation
content_fields:
  - task
  - expected_behavior
  - actual_behavior
  - failure_category
  - scientific_context
  - severity
  - provenance
  - reproducibility
  - remediation_status
primary_action: Inspect failure
secondary_actions:
  - Reproduce
  - Create remediation
  - Open target version
shared_or_page_specific: Page-specific
responsive_behavior: Summary first; expected/actual stack
accessibility: Expected and actual content must have explicit labels
```

---

# Part VIII — State Presentation

## 31. Governance Status Vocabulary

The UI should support:

* Pending Review
* In Review
* Changes Requested
* Approved
* Rejected
* Overridden
* Revoked
* Expired
* Restricted
* Quarantined
* Superseded
* Resolved

These must remain separate from scientific lifecycle states.

---

## 32. Provenance Completeness States

* Complete
* Partial
* Missing Input
* Missing Version
* Missing Actor
* Missing Evaluation
* Missing Approval
* Restricted
* Unavailable
* Legacy Record

A provenance record must not display “Complete” if a required field is unknown.

---

## 33. Evaluation States

* Not Evaluated
* Scheduled
* Running
* Passed
* Passed with Limitations
* Regression Detected
* Failed
* Blocked
* Superseded
* Invalid Run

---

## 34. Memory States

* Candidate
* Active
* Under Review
* Stale
* Conflicting
* Restricted
* Superseded
* Retired
* Rejected

---

## 35. Trust Dimension Presentation

Trust dimensions should be presented as separate labeled rows or compact blocks.

Example:

```text
Evidence Support        Moderate
Provenance Completeness Partial
Human Review            Approved
Reproducibility         Not verified
Memory Validity         Current
Evaluation              Regression detected
```

Do not average these into one number.

---

# Part IX — Empty, Loading, Partial, Stale, and Error States

## 36. Empty Attention Queue

Message meaning:

* no current actionable governance issue exists under the selected scope.

Must show:

* current scope;
* last refresh;
* recent resolved items;
* how to inspect all records;
* no implication that the entire system is risk-free.

Avoid:

> Everything is trusted.

Preferred meaning:

> No open governance actions were found for the current scope.

---

## 37. Empty Approval Queue

Distinguish:

* no approval request created;
* no request assigned to current user;
* filters removed all results;
* user lacks reviewer permission;
* backend unavailable.

---

## 38. Empty Provenance State

Distinguish:

* object has no provenance record;
* record is legacy;
* record is permission-restricted;
* record has not finished generating;
* provenance service unavailable;
* selected object is not consequential and does not require full provenance.

---

## 39. Empty Memory State

Distinguish:

* no memory exists in selected scope;
* no memory matches filters;
* memory unavailable due to permissions;
* persistence is disabled;
* memory backend unavailable.

---

## 40. Empty Evaluation State

Distinguish:

* no evaluation suite exists;
* target version has not been evaluated;
* no matching evaluation run;
* evaluation is not applicable;
* user lacks access;
* evaluation service unavailable.

---

## 41. Loading State

Loading should be region-specific.

Examples:

* shell loads first;
* queue skeleton loads independently;
* selected object identity loads before deep provenance;
* decision rail remains disabled until required basis is available;
* evaluation summary loads before failure examples.

The full page must not freeze for one secondary request.

---

## 42. Partial State

Examples:

* provenance chain missing tool parameters;
* approval package missing one evidence source;
* evaluation run lacks one slice;
* memory usage map incomplete;
* audit history contains legacy events.

The UI must show:

* what is available;
* what is missing;
* whether decision is blocked;
* whether retry is possible;
* who owns the missing information.

---

## 43. Stale State

Stale information must show:

* stale label;
* timestamp;
* reason;
* newer version if known;
* reuse or approval consequence;
* refresh or migration action.

---

## 44. Offline State

When offline:

* cached content must show timestamp;
* mutation controls must be disabled unless safe offline drafts are supported;
* unsaved review notes must be preserved;
* approval must not appear committed;
* stale and offline state must not be conflated.

---

## 45. Error State

Every error must answer:

* what failed;
* which object or region is affected;
* whether user work was saved;
* what remains trustworthy;
* whether retry is safe;
* where technical detail can be inspected.

Examples:

* approval mutation failed;
* audit events unavailable;
* provenance stage cannot load;
* evaluation results inconsistent;
* memory update conflict;
* permissions changed.

---

# Part X — Tables

## 46. Attention Queue Columns

Recommended columns:

* Issue
* Affected Object
* Project / Cycle
* Reason
* Severity
* Owner
* Age
* Required Action
* Status

Optional:

* Version
* Last Event
* Due Date
* Reviewer

---

## 47. Approval Queue Columns

* Requested Transition
* Target Object
* Version
* Project
* Requested By
* Required Reviewer
* Risk
* Age
* Status

---

## 48. Memory Table Columns

* Memory
* Type
* Scope
* Source
* Version
* Freshness
* Last Used
* Risk
* Review State
* Owner

---

## 49. Audit Table Columns

* Time
* Actor
* Action
* Object
* Version
* Previous State
* New State
* Reason
* Result
* Project / Cycle

---

## 50. Evaluation Run Columns

* Target
* Version
* Suite
* Baseline
* Result
* Regression
* Run By
* Run Time
* Review State

---

## 51. Table Rules

All Page 04 tables should support, when applicable:

* sticky header;
* exact timestamps;
* sorting;
* visible filters;
* stable columns;
* column selection;
* row selection;
* object deep links;
* provenance access;
* pagination or virtualization;
* export consistent with filtered scope.

Scientific and governance values must not be silently truncated.

---

# Part XI — Comparison and Diff

## 52. Approval Version Comparison

Must support:

* previous version;
* current proposed version;
* field-level changes;
* scientific impact;
* changed evidence;
* changed risk;
* changed validation;
* changed execution implication.

Changed text alone is insufficient.

---

## 53. Memory Version Comparison

Must show:

* previous content;
* new content;
* source change;
* scope change;
* confidence or validity change;
* usage impact;
* supersession reason.

---

## 54. Evaluation Comparison

Must support:

* target version A and B;
* same evaluation suite;
* baseline;
* dimension-by-dimension result;
* newly introduced failures;
* resolved failures;
* critical regressions;
* changed limitations.

---

## 55. Comparison Visual Rules

* align equivalent dimensions;
* show missing values;
* avoid misleading composite score;
* use textual explanation for material differences;
* support source inspection;
* preserve exact version labels.

---

# Part XII — Visualization

## 56. Permitted Visualizations

Recommended:

* structured timelines;
* provenance paths;
* decision state diagrams;
* evaluation comparison bars;
* dot plots;
* failure matrices;
* version diffs;
* affected-object lists;
* compact relationship graphs;
* causal chains.

---

## 57. Prohibited Defaults

Avoid:

* decorative network hairballs;
* animated blockchain-style provenance;
* 3D audit graphs;
* circular trust gauges;
* radial score charts;
* oversized donut charts;
* red-yellow-green-only status encoding;
* world maps unrelated to governance;
* model leaderboards without task context.

---

## 58. Provenance Graph Limits

A graph may be used only when topology is the actual question.

Requirements:

* limited initial nodes;
* explicit edge semantics;
* direction;
* selected path emphasis;
* table or list fallback;
* no unsupported edge;
* provenance version displayed;
* performance budget;
* accessible alternative.

---

## 59. Timeline Requirements

Every event must define:

* actor;
* action;
* target;
* version;
* timestamp;
* result.

Optional:

* reason;
* policy;
* related evidence;
* prior state;
* next state.

The timeline must visually distinguish:

* human action;
* agent action;
* automated system action;
* external event.

---

## 60. Evaluation Chart Requirements

Each chart must state:

* evaluation question;
* target and version;
* baseline;
* metric or dimension;
* sample size;
* uncertainty where relevant;
* missing data;
* failure threshold;
* data source;
* review status.

---

# Part XIII — Inspector and Decision Rail

## 61. Inspector Composition

Recommended order:

1. Object Type and Title
2. Version
3. Current State
4. Governance Status
5. Owner
6. Source Context
7. Trust Dimensions
8. Related Events
9. Related Objects
10. Open Provenance
11. Open Source Object

---

## 62. Decision Rail Composition

Recommended order:

1. Required Decision
2. User Authority
3. Target Object and Version
4. Blocking Issues
5. Consequence
6. Review Note
7. Primary Action
8. Secondary Action
9. Prior Decision
10. Audit Notice

The rail must state:

> This decision applies to version X.

---

## 63. Decision Control Rules

* primary approval action must be explicit;
* destructive or restrictive action requires confirmation;
* rejection requires reason;
* override requires expanded rationale;
* controls remain disabled if required basis is unavailable;
* permission state is visible;
* loading state must not allow duplicate decisions;
* committed decision must show result and audit reference.

---

# Part XIV — Search, Filters, and Scope

## 64. Global Page Search

Search may cover:

* object title;
* object ID;
* version;
* actor;
* project;
* cycle;
* approval request;
* memory;
* audit event;
* evaluation run;
* model;
* tool;
* prompt reference.

Search relevance must not imply trust or priority.

---

## 65. Scope Controls

Recommended scope filters:

* Project
* DBTL Cycle
* Object Type
* Governance State
* Actor
* Role
* Version
* Time Range
* Severity
* Memory Scope
* Evaluation Target
* Regression State

---

## 66. Filter Visibility

Active filters must remain visible.

Users must be able to:

* clear one filter;
* clear all filters;
* see result count;
* save an approved view if supported;
* deep-link shareable scope;
* distinguish no result from no data.

---

# Part XV — Motion and Feedback

## 67. Motion Principles

Motion should explain:

* selection;
* panel opening;
* provenance path expansion;
* decision completion;
* version comparison;
* timeline focus.

Motion must not dramatize governance.

---

## 68. Timing

Recommended:

* hover feedback: 100–120 ms;
* selection transition: 120–160 ms;
* inspector open: 160–220 ms;
* detail drawer: 180–240 ms;
* provenance path expansion: maximum 300 ms.

Reduced motion must be supported.

---

## 69. Decision Feedback

After approval, rejection, or request changes:

* state updates visibly;
* actor and timestamp appear;
* downstream effect is stated;
* audit event is linked;
* the page does not rely on a toast alone.

---

# Part XVI — Accessibility

## 70. Accessibility Requirements

The page must support:

* logical heading hierarchy;
* keyboard navigation;
* visible focus;
* accessible tables;
* screen-reader labels;
* text alternatives for graphs;
* no color-only meaning;
* sufficient contrast;
* reduced motion;
* clear error announcements;
* accessible diff reading;
* accessible timeline ordering;
* clear authority and disabled-state explanations.

---

## 71. Keyboard Navigation

Minimum support:

* move through navigation;
* move through queue rows;
* select object;
* open and close inspector;
* open evidence or provenance detail;
* move through provenance stages;
* open decision controls;
* close temporary layer with `Esc`;
* focus search;
* activate safe primary action.

Approval should not use a single-key shortcut.

---

## 72. Screen Reader Semantics

Use:

* list semantics for queues;
* table semantics for audit and comparison;
* ordered list semantics for provenance chain;
* status announcement for loading and decision completion;
* explicit before-and-after labels in diffs;
* actor type and role in event descriptions.

---

# Part XVII — Nanobanana Composition Contract

## 73. Nanobanana Role

Nanobanana may generate:

* page-specific composition;
* visual hierarchy;
* governed-object layout;
* provenance path presentation;
* approval package composition;
* evaluation failure analysis layout;
* memory and audit content-region design.

Nanobanana must not invent:

* approval logic;
* trust score;
* audit events;
* scientific evidence;
* model metrics;
* object versions;
* actors;
* system capabilities;
* new navigation;
* new global component styles.

---

## 74. Fixed Program-Controlled Regions

The following are fixed:

* AppShell;
* logo;
* global navigation;
* project context;
* breadcrumb;
* typography;
* spacing tokens;
* colors;
* global buttons;
* global badges;
* table primitives;
* Inspector shell;
* Evidence Drawer;
* approval state semantics;
* object and version identity.

---

## 75. Generated Regions

Nanobanana may design within constraints:

* Attention Queue layout;
* selected governance issue;
* Approval Package content arrangement;
* Provenance Path content composition;
* Memory Usage presentation;
* Audit investigation composition;
* Evaluation comparison and failure detail;
* Decision Rail internal hierarchy.

---

## 76. Canonical Nanobanana State

```yaml
viewport: 1440x1024
theme: light
density: expert
global_navigation: expanded
page_navigation: expanded
project_context: populated
workspace_mode: Approval
queue_state: populated
selected_object: Candidate Engineering Design
selected_version: v3
approval_state: In Review
inspector: open
provenance_detail: collapsed
evidence_state: supporting_and_conflicting
decision_controls: visible
```

---

## 77. Required Visible Content in Canonical State

The canonical image must show:

* project and cycle;
* selected design and version;
* requested transition;
* approval status;
* reason approval is required;
* evidence summary;
* conflicting evidence;
* risk;
* trade-off;
* validation requirements;
* prior reviewer or review state;
* decision controls;
* provenance access;
* return-to-source action.

---

## 78. Nanobanana Prompt Constraints

The generation prompt must explicitly state:

```text
This is not an admin dashboard.

This is not a cybersecurity console.

This is not a raw log viewer.

This is not a model leaderboard.

Design a persistent scientific governance workspace centered on one consequential object and one human decision.

Use the existing global application shell, restrained scientific colors, compact typography, structured panels, subtle borders, and expert information density.

The user must understand the exact object, version, requested transition, scientific basis, unresolved risk, provenance access, review authority, and downstream effect before acting.
```

---

## 79. Visual Do

* use one strong governed-object focus;
* show exact version prominently;
* preserve project and cycle context;
* distinguish human, agent, and system actors;
* show evidence and contradiction;
* show changed fields;
* show authority and downstream consequence;
* use dense but ordered information;
* use restrained semantic state indicators;
* keep audit history readable.

---

## 80. Visual Don’t

* do not create metric-card dashboard;
* do not use large green trust score;
* do not place approval button before basis;
* do not hide version;
* do not show generic activity feed;
* do not use chatbot bubbles;
* do not create neon control room;
* do not use decorative blockchain imagery;
* do not create graph hairball;
* do not reduce evaluation to one ranking;
* do not show raw JSON as primary content;
* do not make every panel equally prominent.

---

# Part XVIII — Annotated Wireframes

## 81. Approval Workspace Wireframe

```text
┌───────────────────────────────────────────────────────────────────────────┐
│ Project Alpha / Cycle 04 / Design / Candidate Design CD-017 / v3          │
│ Trust & Provenance Center                  In Review · Requested by Agent   │
├──────────────┬────────────────────────────────────────┬───────────────────┤
│ Attention    │ Approval Request                       │ Decision           │
│ Approvals  4 │                                        │                   │
│ Provenance   │ Promote Candidate Design v3            │ Required action   │
│ Memory       │ Proposed → Approved                    │ Review v3          │
│ Audit        │                                        │                   │
│ Evaluation   │ Why approval is required               │ Your authority    │
│              │ Wet-lab experiment planning handoff    │ PI Reviewer       │
│              │                                        │                   │
│              │ Changed since v2                       │ Blocking issues   │
│              │ • Added ptsG intervention              │ 1 unresolved risk │
│              │ • Updated validation assay             │                   │
│              │ • New conflicting evidence             │ Downstream effect │
│              │                                        │ Enables Build/Test│
│              │ Evidence                               │                   │
│              │ Supporting 4 · Conflicting 1           │ Review note       │
│              │                                        │ [______________]  │
│              │ Mechanism                              │                   │
│              │ PEP redistribution...                  │ [Approve]         │
│              │                                        │ [Request changes] │
│              │ Risks and trade-offs                   │ [Reject]          │
│              │ Growth burden · context mismatch       │                   │
│              │                                        │ Applies to v3     │
│              │ Validation requirements                │                   │
│              │ Genotype / Mechanism / Phenotype       │                   │
├──────────────┴────────────────────────────────────────┴───────────────────┤
│ Provenance Summary · Audit History · Prior Reviews · Open Full Detail     │
└───────────────────────────────────────────────────────────────────────────┘
```

---

## 82. Provenance Workspace Wireframe

```text
┌───────────────────────────────────────────────────────────────────────────┐
│ Project Alpha / Cycle 04 / Simulation Result SR-021 / v2                  │
├──────────────┬────────────────────────────────────────┬───────────────────┤
│ Attention    │ Provenance Path                        │ Object Inspector   │
│ Approvals    │                                        │                   │
│ Provenance   │ Input                                  │ Simulation Result │
│ Memory       │   ↓                                    │ v2                │
│ Audit        │ Knowledge + Memory                     │ Predicted         │
│ Evaluation   │   ↓                                    │                   │
│              │ Prompt / Task                          │ Completeness      │
│              │   ↓                                    │ Partial           │
│              │ Agent + Model                          │                   │
│              │   ↓                                    │ Missing           │
│              │ Tool + Parameters                      │ Tool parameter set│
│              │   ↓                                    │                   │
│              │ Output                                 │ Reproducibility   │
│              │   ↓                                    │ Not verified      │
│              │ Evaluation                             │                   │
│              │   ↓                                    │ [Open audit]      │
│              │ Human Review                           │ [Open source]     │
│              │                                        │ [Report gap]      │
├──────────────┴────────────────────────────────────────┴───────────────────┤
│ Selected Stage Detail: Tool / Parameter / Artifact / Timestamp / Version  │
└───────────────────────────────────────────────────────────────────────────┘
```

---

## 83. Evaluation Workspace Wireframe

```text
┌───────────────────────────────────────────────────────────────────────────┐
│ Design Agent / Version 2.4 / Evaluation Suite: E. coli Engineering v3     │
├──────────────┬────────────────────────────────────────┬───────────────────┤
│ Attention    │ Evaluation Comparison                  │ Governance Result │
│ Approvals    │                                        │                   │
│ Provenance   │ Baseline v2.3 vs Current v2.4          │ Regression found  │
│ Memory       │                                        │                   │
│ Audit        │ Correctness              Improved      │ Critical failures │
│ Evaluation   │ Evidence support          Stable        │ 2                 │
│              │ Contradiction handling    Regressed     │                   │
│              │ Context match             Regressed     │ Recommended action│
│              │ Provenance                Improved      │ Restrict release  │
│              │ Governance compliance     Passed        │                   │
│              │                                        │ [Create remediation]│
│              │ Scientific slices                       │ [Restrict version]│
│              │ E. coli K-12             Failed         │ [Accept limitation]│
│              │ Cross-strain transfer     Failed        │                   │
│              │                                        │                   │
│              │ Failure examples                        │                   │
│              │ Unsupported strain transfer ×2          │                   │
│              │ Contradictory evidence omitted ×1       │                   │
├──────────────┴────────────────────────────────────────┴───────────────────┤
│ Selected Failure · Expected / Actual / Evidence / Provenance / Reproduce  │
└───────────────────────────────────────────────────────────────────────────┘
```

---

# Part XIX — Visual Acceptance Conditions

## 84. Page-Level Acceptance

The UI passes only if:

* it clearly behaves as a governance workspace;
* one governed object or issue is visually dominant;
* project, cycle, object, and version are visible;
* proposal, approval, execution, and observation are distinct;
* evidence, contradiction, risk, and limitation are inspectable;
* human authority is visible;
* approval is version-specific;
* provenance is reachable without losing context;
* historical events are distinguishable from current action;
* no single unexplained trust score dominates;
* Memory, Audit, Approval, and Evaluation appear connected;
* the page does not resemble a generic admin dashboard.

---

## 85. Approval UI Acceptance

* requested transition is visible;
* target version is visible;
* changed fields are visible;
* evidence and contradiction are visible;
* risk and downstream effect are visible;
* decision authority is visible;
* rejection and override require reason;
* approval action does not visually precede basis;
* completion creates visible audit confirmation.

---

## 86. Provenance UI Acceptance

* provenance stages are ordered;
* actor and version are inspectable;
* missing stages are explicit;
* human and agent actions are distinct;
* raw detail has accessible fallback;
* the selected object remains visible;
* full history does not overwhelm primary interpretation.

---

## 87. Memory UI Acceptance

* source and scope are visible;
* memory version is visible;
* usage is inspectable;
* stale and conflicting memory are distinct;
* correction does not imply historical rewrite;
* affected active decisions can be found;
* restricted memory does not leak protected content.

---

## 88. Audit UI Acceptance

* event actor, action, object, version, time, and result are visible;
* filters are visible;
* event chronology is understandable;
* causal reconstruction is possible;
* event correction creates an additional event;
* raw technical logs do not dominate.

---

## 89. Evaluation UI Acceptance

* target and version are visible;
* baseline is visible;
* dimensions remain separate;
* critical regression is not hidden by average score;
* failure examples are inspectable;
* evaluation limitations are visible;
* governance action can be derived;
* evaluation does not appear to approve scientific truth automatically.

---

# Part XX — Final UI Constitution

```text
The interface shall center consequential governed objects rather than aggregate metrics.

The interface shall always expose the exact object and version under review.

The interface shall distinguish proposal, review, approval, execution, observation, and evaluation.

The interface shall present scientific basis, contradiction, risk, limitation, and downstream consequence before governed action.

The interface shall expose provenance as an ordered and inspectable chain.

The interface shall preserve historical records while clearly identifying current state.

The interface shall show human authority, ownership, and accountability.

The interface shall not reduce trust to a single unexplained score.

The interface shall not hide memory influence.

The interface shall not present evaluation as a leaderboard detached from scientific tasks.

The interface shall not present audit as raw infrastructure logging.

The interface shall preserve cross-page project, cycle, object, version, and return context.

The interface shall operate as a persistent Trust, Governance & Provenance Control Plane—not as an admin dashboard, generic analytics page, compliance theatre, or chatbot.
```

---

# Part XXI — Final UI Summary

The canonical Page 04 visual journey is:

```text
Attention
→ Selected Governed Object
→ Exact Version and State
→ Scientific Basis
→ Provenance and History
→ Risk, Limitation, and Change
→ Human Decision
→ Recorded Consequence
→ Evaluation and Corrective Action
```

The page succeeds when an authorized user can answer:

```text
What needs attention?
Why does it matter?
Which exact object and version are involved?
What evidence, memory, model, tool, and human action produced it?
What changed?
What remains uncertain or risky?
Who may decide?
What happens after the decision?
Can the complete history be reconstructed later?
```

without losing scientific meaning, object identity, historical integrity, permission boundaries, or human accountability.
