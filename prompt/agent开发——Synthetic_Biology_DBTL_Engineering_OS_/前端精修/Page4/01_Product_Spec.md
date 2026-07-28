# Synthetic Biology DBTL Engineering OS

# Page 04 — Trust & Provenance Center

# 01_Product_Spec.md

> **Document type**: Page-specific product specification
> **Page**: Page 04 — Trust & Provenance Center
> **Product role**: Trust, Governance & Provenance Control Plane
> **Status**: Normative / Implementation-Binding
> **Parent contract**: Page Design Contract v1.2.0
> **Parent architecture**: Synthetic Biology DBTL Engineering OS Frontend Architecture v1.2
> **Default UI language**: English
> **Specification language**: English, with implementation notes permitted in Chinese
> **Version**: 1.0.0
> **Last updated**: 2026-07-23

---

## Specification Header

```yaml
page_id: page-04
page_name: Trust & Provenance Center
spec_type: Product Spec
version: 1.0.0
status: Approved
product_positioning: Trust, Governance & Provenance Control Plane
owners:
  - Product Owner
  - Scientific Product Lead
  - Governance Owner
reviewers:
  - Principal Investigator
  - Synthetic Biology Reviewer
  - Dry-Lab Reviewer
  - Wet-Lab Reviewer
  - Data Governance Reviewer
  - Frontend Architect
  - UX Reviewer
parent_contract: Page Design Contract v1.2.0
parent_architecture: Frontend Architecture Prompt v1.2
dependencies:
  - 00_Page_Research.md
  - 02_UI_Spec.md
  - 03_Operating_Principles.md
  - 04_Interaction_Spec.md
  - 05_Technical_Spec.md
  - 06_Content_Spec.md
  - 07_Acceptance_Spec.md
approved_exceptions: []
open_questions: []
```

---

# Part I — Product Identity

## 1. Mission

Page 04 exists to make every consequential scientific output, engineering decision, model action, memory update, approval event, and system evaluation:

* traceable;
* inspectable;
* attributable;
* versioned;
* reviewable;
* governable;
* reproducible where possible;
* reversible where technically and scientifically safe.

Its mission is:

> **Ensure that the Synthetic Biology DBTL Engineering OS remains scientifically trustworthy, human governed, historically reconstructable, and continuously evaluable.**

Page 04 must allow authorized users to answer:

```text
What happened?
→ Who or what caused it?
→ Which object and version were involved?
→ What evidence, memory, model, prompt, tool, and parameter supported it?
→ Who reviewed or approved it?
→ What changed afterward?
→ Was the outcome correct, useful, safe, and reproducible?
```

---

## 2. Product Positioning

Page 04 is the system-wide:

> **Trust, Governance & Provenance Control Plane**

It governs four closely connected capability areas:

```text
Memory
→ What the system retained and reused

Audit Trail
→ What happened, when, by whom, and to which version

Human Approval
→ Which consequential transitions were authorized or rejected

Evaluation
→ Whether agents, models, knowledge, recommendations, and workflows performed acceptably
```

These capabilities are not independent dashboards.

They form one governance loop:

```text
System remembers
→ System acts
→ Action is recorded
→ Human reviews
→ Outcome is evaluated
→ Evaluation changes trust, policy, or future system behavior
→ Updated governance is recorded
```

---

## 3. Core Product Definition

Page 04 is a persistent governance workspace in which users can:

1. inspect the memory used by the system;
2. inspect the full provenance of a scientific or engineering object;
3. reconstruct how an output was produced;
4. review consequential proposed transitions;
5. approve, reject, request changes, or override with reason;
6. inspect immutable audit history;
7. compare versions and decisions;
8. evaluate agents, models, retrieval, evidence use, recommendations, and workflow outcomes;
9. identify trust failures, governance gaps, stale memory, unsupported claims, and regressions;
10. determine what corrective action must happen next.

---

## 4. Primary Product Question

Every major surface on Page 04 must help answer:

> **Can this system output, decision, memory, or action be trusted—and what evidence proves that?**

Supporting questions include:

* What information did the system use?
* Was that information current and applicable?
* Which agent, model, prompt, tool, dataset, or rule produced the output?
* What transformations occurred?
* Which human reviewed the result?
* What was approved, rejected, overridden, or executed?
* Has the result been independently evaluated?
* Did the system behave consistently with policy?
* Can the decision be reconstructed later?
* What happens when trust is insufficient?

---

## 5. Trust Model

Page 04 must not reduce trust to one numeric score.

Trust is a multidimensional judgement composed of:

```text
Scientific validity
+
Evidence traceability
+
Provenance completeness
+
Version integrity
+
Human governance
+
Computational reproducibility
+
Policy compliance
+
Evaluation performance
+
Outcome history
+
Known uncertainty
```

A high evaluation score must not hide:

* incomplete provenance;
* weak evidence;
* unauthorized execution;
* stale memory;
* contradictory results;
* unreproducible computation;
* unreviewed model changes.

---

# Part II — Product Boundaries

## 6. Page Responsibilities

Page 04 owns the product experience for:

### 6.1 Memory Governance

* inspecting persistent system memory;
* understanding memory origin and scope;
* distinguishing facts, summaries, preferences, prior decisions, learned patterns, and temporary context;
* viewing when and where memory was used;
* identifying stale, conflicting, invalid, or sensitive memory;
* reviewing proposed memory changes;
* correcting, superseding, restricting, or retiring memory;
* preserving memory version history.

### 6.2 Audit Trail

* recording consequential system and human events;
* reconstructing object history;
* tracing actor, action, target, version, time, rationale, and result;
* linking events to projects, cycles, decisions, evidence, models, and approvals;
* identifying failed, retried, overridden, or reversed operations;
* providing immutable historical inspection.

### 6.3 Human Approval

* presenting reviewable decision packages;
* exposing evidence, risk, uncertainty, trade-offs, validation requirements, and downstream effects;
* supporting approve, reject, request changes, and override with reason;
* enforcing role- and version-specific authority;
* preventing proposals from appearing executed or approved prematurely;
* preserving approval history.

### 6.4 Evaluation

* evaluating agents, models, prompts, tools, retrieval, evidence use, generated claims, recommendations, workflows, and outcomes;
* running or inspecting golden-set evaluations;
* comparing versions;
* tracking regression;
* identifying systematic failure patterns;
* linking evaluation results to deployment, model, prompt, tool, and dataset versions;
* creating governance actions from evaluation findings.

---

## 7. Explicit Non-Goals

Page 04 must not become:

* a generic admin dashboard;
* a server-log viewer;
* an observability replacement for infrastructure engineers;
* a permission-settings page only;
* a metric-card wall;
* a model leaderboard without scientific context;
* a raw database browser;
* a generic analytics page;
* a compliance theatre page containing badges without evidence;
* an autonomous policy-enforcement agent;
* a second Knowledge & Evidence Layer;
* a duplicate DBTL Engineering Workspace;
* a place where users directly modify scientific truth without review;
* a full repository or source-code management interface.

---

## 8. Responsibilities Owned by Other Pages

### Page 01 — Project Command Center

Owns:

* current project and cycle status;
* high-level risk;
* next action;
* pending decision summary;
* recent meaningful change.

Page 04 may provide the audit and governance basis behind those summaries.

### Page 02 — DBTL Engineering Runtime

Owns:

* diagnosis;
* design;
* simulation;
* critique;
* experiment planning;
* engineering decision construction.

Page 04 governs and audits consequential transitions generated in Page 02.

### Page 03 — Knowledge & Evidence Layer

Owns:

* scientific knowledge production;
* evidence structuring;
* mechanism and rule curation;
* knowledge versioning;
* reusable knowledge.

Page 04 records and evaluates how Page 03 knowledge was created, reviewed, changed, and used.

---

# Part III — DBTL and System Mapping

## 9. Role Across the DBTL Lifecycle

Page 04 is cross-cutting and applies to every DBTL stage.

### 9.1 Design

It records and governs:

* inputs used;
* evidence retrieved;
* hypotheses created;
* candidate designs generated;
* agent and model versions;
* user edits;
* review decisions;
* approved design version.

### 9.2 Build

It records and governs:

* approved construct or intervention;
* responsible owner;
* build authorization;
* protocol or implementation version;
* deviations;
* changes requested;
* execution status.

### 9.3 Test

It records and governs:

* assay plan;
* dataset identity;
* analysis pipeline;
* processing version;
* model parameters;
* observed results;
* exceptions and failures;
* validation review.

### 9.4 Learn

It records and governs:

* interpretation;
* prediction–observation comparison;
* knowledge update proposal;
* memory update;
* accepted or rejected learning;
* changed rule version;
* affected downstream decisions.

---

## 10. Cross-Page Governance Loop

The canonical cross-page loop is:

```text
Page 03 provides governed knowledge
→ Page 02 creates an engineering proposal
→ Page 04 exposes provenance and approval package
→ Authorized human reviews
→ Approved work proceeds
→ Observed result returns
→ Page 04 evaluates process and outcome
→ Page 03 receives candidate knowledge update
→ Page 04 records review, version, and memory change
→ Page 01 reflects the new project state
```

---

# Part IV — Target Users

## 11. Principal Investigator

### Goals

* understand which decisions require attention;
* assess whether evidence and evaluation justify approval;
* review unresolved risks and trade-offs;
* identify governance violations;
* inspect who approved what;
* compare system performance across cycles;
* override exceptional cases with accountable rationale.

### Product Needs

* concise decision package;
* high-impact trust failures;
* visible unresolved uncertainty;
* clear downstream consequence;
* minimal need to inspect raw logs unless necessary.

---

## 12. Dry-Lab Researcher

### Goals

* reproduce computational output;
* inspect model, tool, data, parameter, prompt, and code versions;
* compare output versions;
* identify which memory or evidence affected an analysis;
* report model or retrieval failure;
* inspect evaluation results.

### Product Needs

* computational provenance;
* parameter diff;
* dataset lineage;
* model and tool traceability;
* reproducibility status;
* evaluation drill-down.

---

## 13. Wet-Lab Researcher

### Goals

* determine whether an experiment is actually approved;
* identify the exact approved version;
* understand required validation and safety checks;
* inspect deviations from approved plans;
* record execution and observations;
* identify who authorized a change.

### Product Needs

* unambiguous proposed versus approved state;
* clear owner;
* version lock;
* practical downstream effect;
* readable change history;
* no requirement to interpret raw AI traces.

---

## 14. Knowledge Curator

### Goals

* inspect memory and knowledge update history;
* identify unsupported memory entries;
* see where knowledge has been reused;
* review corrections and supersession;
* evaluate extraction or synthesis quality;
* track provenance completeness.

### Product Needs

* object lineage;
* memory usage map;
* version comparison;
* affected-object analysis;
* review queue;
* immutable curation history.

---

## 15. Governance Reviewer

### Goals

* review consequential state transitions;
* verify role and policy compliance;
* inspect evidence packages;
* identify audit gaps;
* investigate overrides;
* confirm that required human approvals occurred.

### Product Needs

* actionable review queue;
* policy context;
* evidence sufficiency;
* approval authority visibility;
* exception and override reporting.

---

## 16. System Maintainer and Evaluator

### Goals

* compare models, agents, prompts, tools, and workflow versions;
* inspect regressions;
* identify recurring failure patterns;
* assess golden-set performance;
* understand deployment impact;
* link evaluation failures to concrete outputs.

### Product Needs

* version-aware evaluation;
* cohort and slice analysis;
* reproducible test fixtures;
* regression history;
* failure examples;
* actionability beyond aggregate metrics.

---

# Part V — Jobs to Be Done

## 17. Primary Jobs

### JTBD-01 — Reconstruct a Decision

> When I inspect a consequential engineering decision, I need to reconstruct the exact evidence, memory, model, prompt, tool, parameters, edits, review, and approval that produced it, so that I can determine whether it remains scientifically and procedurally trustworthy.

### JTBD-02 — Review a Proposed Transition

> When the system proposes moving an object into a consequential state, I need a complete review package and explicit authority controls so that I can approve, reject, or request changes without confusing proposal with execution.

### JTBD-03 — Inspect and Govern Memory

> When the system reuses prior information, I need to understand what was remembered, where it came from, why it was retrieved, and whether it remains valid, so that stale or incorrect memory does not silently affect future decisions.

### JTBD-04 — Evaluate System Performance

> When a model, agent, prompt, tool, or workflow version changes, I need to evaluate it against representative scientific tasks and prior baselines so that regressions are detected before high-consequence use.

### JTBD-05 — Investigate a Trust Failure

> When an output appears unsupported, inconsistent, unsafe, or incorrect, I need to trace the failure across evidence, memory, computation, review, and execution so that the cause and corrective action are explicit.

---

## 18. Secondary Jobs

* compare two approval versions;
* identify all objects affected by a memory correction;
* inspect all decisions made with a specific model version;
* identify missing provenance fields;
* review unresolved overrides;
* find recurring hallucination or retrieval failures;
* inspect why an evaluation score changed;
* export an audit package;
* verify that a completed experiment used the approved plan;
* inspect historical state without changing current truth;
* restore or supersede memory through governance;
* determine whether an object is stale or superseded.

---

# Part VI — Primary User Stories

## 19. Story A — Decision Provenance Inspection

```text
User opens a candidate design
→ Opens Trust & Provenance
→ Sees object identity and approved version
→ Inspects evidence, memory, model, tool, and parameter lineage
→ Reviews human edits and approval history
→ Identifies unresolved limitation
→ Returns to the original design with context preserved
```

Success means the user can reconstruct the decision without searching across unrelated logs.

---

## 20. Story B — Human Approval

```text
A proposed experiment enters review
→ Authorized reviewer opens the approval package
→ Reviews scientific basis
→ Reviews trade-offs, risk, limitations, and validation requirements
→ Compares current version with prior version
→ Approves, rejects, or requests changes
→ Decision, reason, actor, time, and version become immutable audit events
→ Downstream state updates according to policy
```

Success means no user can mistake the proposal for an approved or executed experiment.

---

## 21. Story C — Memory Correction

```text
Researcher notices stale strain information
→ Opens the memory object
→ Inspects source and prior usage
→ Sees which projects and decisions consumed it
→ Proposes a correction or retirement
→ Reviewer evaluates the change
→ New memory version is created
→ Historical decisions retain the version originally used
→ Affected active objects receive a warning
```

Success means correction does not rewrite history.

---

## 22. Story D — Agent Evaluation

```text
Maintainer selects agent version
→ Chooses evaluation suite and comparison baseline
→ Reviews aggregate result
→ Drills into scientific task slices
→ Inspects failed examples
→ Traces failure to retrieval, evidence, reasoning, tool use, or output formatting
→ Creates remediation action
→ Re-runs evaluation after change
→ Regression and improvement history are preserved
```

Success means evaluation produces actionable governance, not only a score.

---

## 23. Story E — Audit Investigation

```text
Unexpected wet-lab deviation is reported
→ Reviewer opens the experiment history
→ Compares approved plan with executed version
→ Identifies actor, time, reason, and changed fields
→ Determines whether override was authorized
→ Links observed effect to deviation
→ Records investigation outcome
→ Creates corrective or policy action
```

Success means the event can be reconstructed without relying on memory or informal communication.

---

# Part VII — Product Surfaces

## 24. Trust Overview

Purpose:

* orient the user;
* summarize consequential trust state;
* identify pending approvals, critical provenance gaps, memory risks, and evaluation regressions;
* provide entry into actionable work.

It must not become a generic KPI dashboard.

Primary questions:

* What requires attention?
* Why does it matter?
* Who owns the next action?
* What system or scientific object is affected?

---

## 25. Memory Governance Surface

Purpose:

* inspect persistent memory objects;
* understand scope, source, version, freshness, and usage;
* review proposed memory changes;
* identify stale or conflicting memory.

Required concepts:

* memory object;
* memory type;
* source;
* scope;
* owner;
* version;
* use history;
* validity;
* sensitivity;
* review state;
* supersession.

---

## 26. Audit Trail Surface

Purpose:

* reconstruct chronological and causal history;
* filter by project, cycle, object, actor, action, model, tool, or state;
* inspect event details and related objects;
* compare planned, approved, executed, and observed states.

Required concepts:

* immutable audit event;
* actor;
* action;
* target;
* previous state;
* new state;
* version;
* rationale;
* timestamp;
* linked evidence;
* result.

---

## 27. Human Approval Surface

Purpose:

* manage consequential review and approval work;
* provide complete decision packages;
* prevent unsafe or unauthorized state transitions.

Required concepts:

* approval request;
* target object and version;
* required role;
* evidence package;
* risk;
* trade-off;
* validation requirement;
* decision;
* reason;
* expiration or validity;
* downstream effect.

---

## 28. Evaluation Surface

Purpose:

* evaluate system components and workflows;
* compare versions;
* inspect failure patterns;
* support release, rollback, restriction, or remediation decisions.

Evaluation targets may include:

* agent;
* model;
* prompt;
* retrieval strategy;
* tool;
* evaluator;
* knowledge extraction;
* recommendation;
* workflow;
* full DBTL cycle.

---

## 29. Provenance Inspector

Purpose:

* provide a cross-page, object-specific lineage view.

Canonical lineage:

```text
Source Data / User Input / Memory
→ Retrieval
→ Prompt or Task
→ Agent and Model
→ Tool and Parameters
→ Intermediate Artifacts
→ Generated Output
→ Evaluator
→ Human Review
→ Approval
→ Execution
→ Observation
```

Not every object will have every stage. Missing stages must be explicit.

---

# Part VIII — Core Product Objects

## 30. Memory Object

```yaml
memory_id:
memory_type:
title:
content_summary:
scope:
source_type:
source_reference:
created_by:
created_at:
updated_at:
version:
status:
freshness:
confidence:
sensitivity:
usage_count:
usage_records:
supersedes:
superseded_by:
review_status:
```

Possible memory types:

* project fact;
* scientific fact;
* user preference;
* workflow decision;
* prior result;
* learned pattern;
* temporary working context;
* policy;
* model-generated summary.

These types must not be visually or semantically conflated.

---

## 31. Audit Event

```yaml
event_id:
event_type:
actor_type:
actor_id:
actor_role:
action:
target_type:
target_id:
target_version:
previous_state:
new_state:
reason:
timestamp:
project_id:
cycle_id:
related_objects:
provenance_id:
result:
```

Audit history is append-only from the product perspective.

---

## 32. Approval Request

```yaml
approval_id:
target_object:
target_version:
requested_transition:
requested_by:
required_reviewer_role:
evidence_package:
risks:
tradeoffs:
limitations:
validation_requirements:
downstream_effect:
status:
reviewer:
decision:
decision_reason:
requested_at:
decided_at:
expires_at:
```

---

## 33. Evaluation Run

```yaml
evaluation_id:
evaluation_target:
target_version:
evaluation_suite:
dataset_or_golden_set:
evaluator_version:
metrics:
slices:
failure_examples:
baseline:
result:
regression_status:
limitations:
run_by:
run_at:
provenance:
review_status:
```

---

## 34. Provenance Record

```yaml
provenance_id:
subject_object:
subject_version:
source_inputs:
memory_inputs:
retrieved_objects:
agent:
model:
prompt_or_task:
tools:
parameters:
intermediate_artifacts:
output:
evaluation:
human_edits:
approval:
execution:
timestamps:
```

---

## 35. Governance Action

Possible actions:

* approve;
* reject;
* request changes;
* override with reason;
* revoke;
* supersede;
* restrict;
* retire;
* quarantine;
* re-evaluate;
* request evidence;
* request reproducibility check;
* report unsupported claim;
* create remediation task.

Each action must define authority and downstream effect.

---

# Part IX — Human Governance Model

## 36. Proposal Is Not Approval

The following states must remain distinct:

```text
Generated
→ Draft
→ Proposed
→ In Review
→ Changes Requested
→ Approved
→ Scheduled
→ Executed
→ Observed
→ Evaluated
→ Superseded
```

No model or UI shortcut may silently skip required governance states.

---

## 37. Approval Requirements

Approval must be:

* object-specific;
* version-specific;
* transition-specific;
* role-aware;
* time-stamped;
* attributable;
* based on an inspectable review package;
* preserved as immutable history.

An approval for version 3 does not automatically approve version 4.

---

## 38. Approval Package

Before an authorized human decides, the system must expose:

1. target object;
2. current version;
3. requested state transition;
4. scientific purpose;
5. evidence;
6. conflicting evidence;
7. mechanism;
8. assumptions;
9. limitations;
10. risk;
11. trade-offs;
12. validation requirements;
13. downstream consequences;
14. prior review history;
15. changed fields since prior version.

---

## 39. Rejection and Change Request

Rejection and request for changes must require a reason.

The reason should be classifiable when useful:

* insufficient evidence;
* scientific inconsistency;
* unresolved risk;
* missing validation;
* context mismatch;
* implementation problem;
* governance violation;
* unclear ownership;
* incorrect version;
* incomplete provenance;
* other.

Free-text rationale remains available.

---

## 40. Override

Override is exceptional, visible, and reviewable.

Override requires:

* authorized role;
* explicit reason;
* accepted risk;
* affected object and version;
* original policy or decision;
* downstream effect;
* audit event;
* later review when policy requires.

An override does not erase the original decision.

---

## 41. Approval Expiry and Revocation

Approval may become invalid when:

* the target object changes;
* material evidence changes;
* required reviewer authority expires;
* relevant knowledge is superseded;
* safety or validation requirements change;
* the approval validity window ends.

The system must not silently continue treating invalid approval as current.

---

# Part X — Memory Product Model

## 42. Memory Purpose

Memory exists to preserve useful context across:

* sessions;
* projects;
* DBTL cycles;
* agent executions;
* reviews;
* decisions;
* experiments;
* learning loops.

Memory must improve continuity without creating hidden scientific truth.

---

## 43. Memory Scope

Memory scope may be:

* current task;
* current session;
* user;
* project;
* DBTL cycle;
* organism or strain;
* laboratory;
* global governed knowledge.

Scope must remain visible.

A project-specific observation must not silently become global truth.

---

## 44. Memory Lifecycle

```text
Candidate Memory
→ Structured Memory
→ Review if consequential
→ Active
→ Used
→ Re-evaluated
→ Updated
→ Superseded, Restricted, or Retired
```

---

## 45. Memory Use Transparency

When memory materially affects an output, the user must be able to inspect:

* which memory was used;
* memory version;
* why it was retrieved;
* source;
* scope;
* freshness;
* applicability;
* how it affected the output.

---

## 46. Memory Risk States

* stale;
* conflicting;
* unsupported;
* overgeneralized;
* sensitive;
* scope mismatch;
* source unavailable;
* superseded;
* under review;
* restricted.

Risk states should create appropriate warnings or reuse restrictions.

---

## 47. Memory Correction

Correction must create a new version.

Historical outputs continue to reference the original memory version.

Active decisions affected by corrected memory should be identifiable.

---

# Part XI — Audit Product Model

## 48. Audit Purpose

Audit exists to make consequential system history reconstructable.

It is not only for security incidents.

Scientific audit includes:

* what evidence was available;
* what version was used;
* what interpretation was generated;
* what human changed;
* what decision was made;
* what was executed;
* what was observed.

---

## 49. Audit Event Categories

* creation;
* modification;
* deletion request;
* supersession;
* retrieval;
* generation;
* evaluation;
* review;
* approval;
* rejection;
* override;
* execution;
* failure;
* retry;
* import;
* export;
* permission change;
* memory update;
* provenance update;
* policy action.

Not every low-level UI interaction must become an audit event.

---

## 50. Audit Reconstruction

The system should support reconstruction by:

* object;
* version;
* project;
* cycle;
* actor;
* model;
* agent;
* tool;
* approval;
* experiment;
* time range;
* event category.

---

## 51. Audit Integrity

Audit history must not be editable through ordinary page actions.

Corrections to audit metadata must themselves create audit events.

Technical immutability guarantees depend on backend architecture and must be verified in the Technical Spec.

---

# Part XII — Evaluation Product Model

## 52. Evaluation Mission

Evaluation determines whether the system performs acceptably for scientific engineering work.

Evaluation must answer more than:

> Did the model produce a plausible answer?

It should assess:

* scientific correctness;
* evidence fidelity;
* provenance completeness;
* context sensitivity;
* uncertainty calibration;
* hallucination;
* instruction following;
* tool use;
* retrieval quality;
* recommendation quality;
* governance compliance;
* reproducibility;
* practical engineering usefulness.

---

## 53. Evaluation Levels

### 53.1 Component Evaluation

* retriever;
* extractor;
* classifier;
* simulator;
* tool;
* evidence ranker;
* evaluator.

### 53.2 Agent Evaluation

* diagnosis agent;
* design agent;
* simulation agent;
* critic;
* experiment planner;
* knowledge agent.

### 53.3 Workflow Evaluation

* full diagnosis-to-design chain;
* full design-to-experiment chain;
* DBTL learning loop;
* approval workflow;
* memory update workflow.

### 53.4 Outcome Evaluation

* prediction versus observation;
* expected versus measured phenotype;
* recommendation utility;
* validation success;
* transferability across conditions.

---

## 54. Evaluation Dimensions

Recommended controlled dimensions:

* correctness;
* completeness;
* evidence support;
* contradiction handling;
* provenance completeness;
* uncertainty expression;
* context match;
* biological plausibility;
* recommendation actionability;
* validation quality;
* safety and governance compliance;
* reproducibility;
* latency;
* cost where relevant.

A single aggregate score must not replace dimension-level inspection.

---

## 55. Golden Sets

Golden sets must be:

* versioned;
* scoped;
* traceable;
* scientifically reviewed;
* representative of intended use;
* protected from accidental training contamination where applicable;
* associated with expected answers or review rubrics;
* explicit about ambiguity and acceptable alternatives.

---

## 56. Regression

A new version must be compared with an approved baseline where appropriate.

Regression may be:

* global;
* scientific-domain-specific;
* strain-specific;
* task-specific;
* safety-specific;
* governance-specific;
* performance-specific.

An average improvement does not justify a critical scientific or governance regression.

---

## 57. Failure Analysis

Evaluation failures should be classifiable as:

* retrieval failure;
* evidence omission;
* unsupported claim;
* hallucinated citation;
* context mismatch;
* entity resolution error;
* reasoning failure;
* tool failure;
* simulation misuse;
* uncertainty failure;
* approval bypass;
* provenance gap;
* output schema failure;
* latency or performance failure.

---

## 58. Evaluation Outcome Actions

Possible actions:

* approve version;
* approve with limitation;
* request changes;
* restrict use;
* rollback;
* quarantine;
* require human review;
* update prompt;
* update tool;
* update retrieval;
* update golden set;
* create a new evaluation;
* investigate failure;
* block release.

---

# Part XIII — Information Priority

## 59. P0 — Mission-Critical

Page 04 cannot fulfill its mission without:

* object- and version-specific provenance;
* immutable audit history;
* clear actor and timestamp;
* proposal versus approval distinction;
* role-aware approval;
* approval reason;
* memory source and usage trace;
* evaluation target and version;
* failure and regression visibility;
* context-preserving cross-page entry;
* explicit missing, partial, stale, and unavailable states;
* no fabricated provenance or evaluation data.

---

## 60. P1 — Complete Primary Workflow

* approval queue;
* decision package;
* memory inspection and correction;
* audit filtering and reconstruction;
* version comparison;
* evaluation run inspection;
* failure-example drill-down;
* governance action creation;
* provenance export;
* affected-object analysis;
* override workflow;
* revocation or supersession.

---

## 61. P2 — Important Secondary Capability

* policy simulation;
* advanced audit graph;
* cross-project trust analytics;
* automated provenance gap detection;
* automated evaluation scheduling;
* trust trend analysis;
* advanced cohort comparison;
* evaluation cost tracking;
* reusable governance templates.

---

## 62. P3 — Enhancement

* decorative provenance animation;
* advanced graph layout customization;
* nonessential trust scoring;
* personalized dashboard composition;
* secondary visual analytics;
* speculative predictive governance.

P3 must never delay P0 or P1.

---

# Part XIV — Entry Points

## 63. Primary Navigation

Users may enter Page 04 through the main product navigation.

Default landing behavior should be role- and attention-aware without hiding the complete information architecture.

---

## 64. Contextual Entry

Page 04 may be opened from:

* Page 01 pending decision;
* Page 01 recent change;
* Page 02 candidate design;
* Page 02 simulation result;
* Page 02 experiment plan;
* Page 03 knowledge object;
* Page 03 evidence or rule;
* approval notification;
* evaluation regression;
* memory warning;
* audit alert;
* provenance badge;
* deep link.

---

## 65. Entry Context

The following context should be preserved where relevant:

```text
Project
/ DBTL Cycle
/ Stage
/ Source Object
/ Source Version
/ Governance Question
/ Selected Event or Approval
```

---

# Part XV — Exit and Handoff

## 66. Return to Source Object

Users must be able to return to the originating:

* project;
* cycle;
* candidate design;
* simulation;
* experiment;
* knowledge object;
* evidence;
* report.

The return path must preserve selection and review context where possible.

---

## 67. Governance Handoffs

Page 04 may hand off:

* approved object to Page 02;
* change request to object owner;
* knowledge correction to Page 03;
* project warning to Page 01;
* evaluation remediation to maintainer workflow;
* memory correction to governance review;
* provenance issue to investigation queue.

---

## 68. Handoff Integrity

Every handoff must preserve:

* object ID;
* object version;
* source context;
* governance status;
* owner;
* requested action;
* audit linkage.

---

# Part XVI — Main Decisions and Actions

## 69. Primary Decisions

Users may need to decide:

* Is this output sufficiently trustworthy?
* Is provenance complete?
* Is the memory valid and applicable?
* Should this object be approved?
* Should changes be requested?
* Should an override be allowed?
* Should an approval be revoked?
* Should a system version be released or blocked?
* Is an evaluation failure material?
* Should an object, memory, model, or tool be restricted?
* Is a historical decision still valid under new evidence?

---

## 70. Primary Actions

* inspect provenance;
* inspect memory;
* inspect audit event;
* compare versions;
* approve;
* reject;
* request changes;
* override with reason;
* revoke;
* supersede;
* restrict;
* retire;
* re-evaluate;
* run approved evaluation;
* report unsupported claim;
* create investigation;
* export governance package;
* return to source object.

---

# Part XVII — Failure Modes and Risks

## 71. Product Failure — Generic Admin Dashboard

Symptoms:

* oversized KPI cards;
* counts without scientific consequence;
* audit events separated from objects;
* no review workflow;
* no provenance reconstruction.

Mitigation:

* organize around trust questions and actionable governance objects.

---

## 72. Product Failure — Raw Log Viewer

Symptoms:

* infrastructure-style event stream;
* low-level technical noise;
* no scientific object context;
* no human-readable causal reconstruction.

Mitigation:

* present audit events through scientific objects, decisions, versions, and outcomes.

---

## 73. Scientific Failure — False Trust

Symptoms:

* one “trust score”;
* green badge hiding weak evidence;
* evaluation pass hiding missing provenance;
* approval state not tied to version.

Mitigation:

* multidimensional trust model and visible limitations.

---

## 74. Governance Failure — Approval Theatre

Symptoms:

* approval button without review package;
* no required role;
* no reason;
* approval not tied to version;
* automatic approval by agent.

Mitigation:

* enforce object-, version-, transition-, and role-specific approval.

---

## 75. Memory Failure — Hidden Influence

Symptoms:

* system reuses memory without showing it;
* stale memory silently affects recommendations;
* memory has no scope or source;
* corrected memory rewrites history.

Mitigation:

* memory usage trace and version-preserving correction.

---

## 76. Evaluation Failure — Metric Worship

Symptoms:

* aggregate score without examples;
* no scientific slices;
* no baseline;
* no version trace;
* evaluation not linked to governance action.

Mitigation:

* dimension-level results, failure examples, and actionable outcomes.

---

## 77. Audit Failure — Incomplete Reconstruction

Symptoms:

* missing actor;
* missing object version;
* missing prior state;
* missing reason;
* missing model or tool version;
* unable to determine what was executed.

Mitigation:

* minimum audit event contract and completeness checks.

---

## 78. Permission Failure

Symptoms:

* users can approve without authority;
* restricted memory exposed;
* reviewers can edit immutable history;
* actor identity unclear.

Mitigation:

* backend-enforced roles and explicit permission behavior.

---

## 79. Cross-Page Failure

Symptoms:

* Page 04 loses the originating object;
* approval updates wrong version;
* audit opens disconnected from project;
* knowledge correction does not notify affected decisions.

Mitigation:

* persistent context and stable object/version identity.

---

# Part XVIII — Product Success Metrics

## 80. Trust and Traceability Metrics

* percentage of consequential objects with complete provenance;
* percentage of approvals tied to exact versions;
* percentage of outputs exposing evidence and model/tool lineage;
* median time to reconstruct a decision;
* percentage of material memory uses that are inspectable;
* number of unresolved provenance gaps.

---

## 81. Governance Metrics

* review completion time;
* percentage of approvals with complete rationale;
* number of unauthorized transition attempts blocked;
* number of overrides;
* override review completion;
* number of stale approvals detected;
* number of approval/version mismatches prevented.

Metrics must not incentivize superficial fast approval.

---

## 82. Evaluation Metrics

* evaluation coverage by agent and workflow;
* regression detection rate;
* unsupported-claim rate;
* hallucinated-citation rate;
* provenance completeness rate;
* context-mismatch rate;
* successful remediation rate;
* repeat failure rate;
* prediction-to-observation evaluation coverage.

---

## 83. Memory Metrics

* percentage of governed memory with identifiable source;
* stale-memory detection rate;
* conflicting-memory resolution rate;
* memory correction propagation;
* number of active decisions using superseded memory;
* memory reuse with visible trace.

---

## 84. User Experience Metrics

* time for PI to understand a pending approval;
* time to locate the basis of a decision;
* time to identify the owner of a governance action;
* successful return to originating object;
* review-package comprehension;
* audit investigation completion without external assistance.

---

# Part XIX — Product Acceptance Questions

## 85. PI Acceptance

* Can the PI identify the highest-risk pending decision quickly?
* Can the PI understand why approval is required?
* Can the PI inspect the evidence and unresolved risks?
* Can the PI see downstream effects before deciding?
* Can the PI distinguish proposal, approval, execution, and observation?

---

## 86. Dry-Lab Acceptance

* Can the researcher identify model, tool, data, prompt, and parameter versions?
* Can the output be computationally reconstructed where supported?
* Can versions be compared?
* Are evaluation failures linked to concrete examples?
* Is missing reproducibility information explicit?

---

## 87. Wet-Lab Acceptance

* Can the researcher identify the exact approved experiment version?
* Can they distinguish approved work from a proposed plan?
* Are deviations and overrides visible?
* Is the responsible owner visible?
* Are validation and safety requirements inspectable?

---

## 88. Curator Acceptance

* Can the curator inspect memory origin and use?
* Can stale or conflicting memory be corrected without rewriting history?
* Can affected active decisions be identified?
* Can knowledge or memory review history be reconstructed?
* Is supersession explicit?

---

## 89. Maintainer Acceptance

* Can the maintainer compare agent or model versions?
* Can regressions be inspected by scientific task slice?
* Can failed examples be traced to cause?
* Can evaluation findings create remediation actions?
* Can release or restriction decisions be audited?

---

# Part XX — Product Anti-Patterns

## 90. Forbidden Product Patterns

* generic admin dashboard;
* raw event-log wall;
* full-page chatbot;
* trust score without explanation;
* model leaderboard without task context;
* approval inbox without scientific basis;
* memory list without source or scope;
* audit graph with no readable alternative;
* evaluation chart without failure examples;
* editable historical audit record;
* approval not tied to object version;
* automatic agent self-approval;
* decorative compliance badges;
* provenance available only after many unrelated interactions.

---

## 91. Forbidden Semantic Patterns

* treating memory as verified knowledge by default;
* treating evaluation score as scientific truth;
* treating approval as evidence quality;
* treating audit existence as reproducibility;
* treating model confidence as human approval;
* treating lack of logged evidence as evidence that nothing occurred;
* treating an override as replacement of the original decision;
* treating historical state as current state;
* treating a passed average metric as permission to ignore critical failures.

---

# Part XXI — Product Readiness Gate

## 92. Readiness Requirements

Page 04 may proceed to detailed UI and technical specification only when:

```text
Product mission approved
AND page boundaries approved
AND governance model approved
AND memory object model approved
AND audit event model approved
AND approval transition model approved
AND evaluation targets and dimensions approved
AND cross-page object/version identity defined
AND P0 workflows have no unresolved contradiction
```

---

## 93. Blocking Questions

Implementation is `BLOCKED` when any of the following remain unresolved:

* Which backend owns approval state?
* Which events are immutable audit events?
* Which memory types exist?
* Which memory changes require human review?
* Which roles may approve which transitions?
* What exact object version is being approved?
* Which evaluation suites and baselines exist?
* How are model, prompt, tool, and dataset versions identified?
* How is sensitive provenance permission-gated?
* How are historical decisions preserved when source knowledge or memory changes?

---

# Part XXII — Product Constitution

```text
Trust shall never be represented as an unexplained score.

Every consequential system output shall remain traceable to its inputs, memory, evidence, model, tools, parameters, version, and review state.

Every consequential state transition shall remain human governed according to explicit role and policy.

A proposal shall never appear approved, and an approval shall never appear executed unless the corresponding event occurred.

Approval shall always be object-specific, version-specific, attributable, and auditable.

Historical events shall not be silently rewritten.

Memory shall never become hidden scientific truth.

Every material use of memory shall be inspectable.

Memory correction shall create a new version rather than rewrite prior decisions.

Evaluation shall inspect scientific correctness, evidence fidelity, provenance, uncertainty, governance, reproducibility, and practical utility—not only linguistic quality.

Evaluation results shall remain linked to the exact agent, model, prompt, tool, data, and workflow versions evaluated.

Aggregate success shall not hide critical scientific, governance, or safety failure.

Override shall be exceptional, reasoned, attributable, and preserved alongside the original decision.

Page 04 shall operate as the Trust, Governance & Provenance Control Plane of the Synthetic Biology DBTL Engineering OS—not as a generic admin dashboard, raw log viewer, or model leaderboard.
```

---

# Part XXIII — Final Product Summary

Page 04 must support the canonical trust loop:

```text
Memory and Evidence
→ Agent or Human Action
→ Versioned Output
→ Provenance Record
→ Human Review
→ Approval or Rejection
→ Execution or Restriction
→ Observation
→ Evaluation
→ Governance Action
→ Updated Memory, Policy, Knowledge, or System Version
```

The page succeeds only when an authorized user can move from:

```text
Questionable Output
→ Exact Object and Version
→ Input and Memory Lineage
→ Model, Prompt, Tool, and Parameters
→ Human Changes
→ Approval History
→ Execution and Outcome
→ Evaluation
→ Corrective Action
```

without losing project context, scientific meaning, historical integrity, permission boundaries, or human accountability.
