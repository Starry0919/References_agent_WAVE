# Synthetic Biology DBTL Engineering OS

# Page 04 — Trust & Provenance Center

# 03_Operating_Principles.md

> **Document type**: Page-specific scientific, governance, and runtime operating principles
> **Page**: Page 04 — Trust & Provenance Center
> **Product role**: Trust, Governance & Provenance Control Plane
> **Status**: Normative / Implementation-Binding
> **Parent contract**: Page Design Contract v1.2.0
> **Parent architecture**: Synthetic Biology DBTL Engineering OS Frontend Architecture v1.2
> **Parent product spec**: Page 04 `01_Product_Spec.md` v1.0.0
> **Parent UI spec**: Page 04 `02_UI_Spec.md` v1.0.0
> **Default UI language**: English
> **Specification language**: English, with implementation notes permitted in Chinese
> **Version**: 1.0.0
> **Last updated**: 2026-07-23

---

## Specification Header

```yaml
page_id: page-04
page_name: Trust & Provenance Center
spec_type: Operating Principles
version: 1.0.0
status: Approved
product_positioning: Trust, Governance & Provenance Control Plane
owners:
  - Product Owner
  - Scientific Product Lead
  - Governance Owner
  - Data Stewardship Owner
reviewers:
  - Principal Investigator
  - Synthetic Biology Reviewer
  - Dry-Lab Reviewer
  - Wet-Lab Reviewer
  - Governance Reviewer
  - Frontend Architect
  - Security and Privacy Reviewer
parent_contract: Page Design Contract v1.2.0
parent_architecture: Frontend Architecture Prompt v1.2
parent_product_spec: Page04/01_Product_Spec.md
parent_ui_spec: Page04/02_UI_Spec.md
dependencies:
  - 00_Page_Research.md
  - 01_Product_Spec.md
  - 02_UI_Spec.md
  - 04_Interaction_Spec.md
  - 05_Technical_Spec.md
  - 06_Content_Spec.md
  - 07_Acceptance_Spec.md
approved_exceptions: []
open_questions: []
```

---

# Part I — Operating Mission

## 1. Purpose

This document defines how Page 04 must operate as the system-wide:

> **Trust, Governance & Provenance Control Plane**

It establishes the rules governing:

* persistent memory;
* audit history;
* provenance;
* human approval;
* override;
* revocation;
* evaluation;
* regression;
* corrective action;
* governance handoff;
* cross-page trust state.

This document does not define only how the interface looks.

It defines:

> **What Page 04 is allowed to mean, how its objects change state, which transitions require human authority, how history is preserved, and how trust-related decisions affect the rest of the DBTL Engineering OS.**

---

## 2. Primary Operating Question

Every Page 04 operation must help answer:

> **Can this exact object, version, action, memory, or system output be trusted sufficiently for its intended use, and what evidence, history, authority, and evaluation support that conclusion?**

---

## 3. Operating Scope

These principles apply to:

* Memory;
* Audit Trail;
* Provenance Records;
* Human Review;
* Approval Requests;
* Approval Decisions;
* Overrides;
* Revocations;
* Evaluation Runs;
* Regression Findings;
* Trust Warnings;
* Governance Actions;
* Affected-Object Analysis;
* Cross-page governance state.

They apply to both:

* human-generated actions;
* agent-generated actions;
* automated system actions;
* external tool actions.

---

# Part II — Core Governance Invariants

## 4. Governing Invariants

The following invariants are mandatory.

### GOP-001 — Historical Integrity

Past system events, approvals, evaluations, memory versions, and provenance records must not be silently rewritten.

Corrections must create new records or versions.

---

### GOP-002 — Exact Object Identity

Every consequential governance action must apply to an exact object and exact version.

Approval, review, override, restriction, revocation, evaluation, or supersession must never apply only to an ambiguous display label.

---

### GOP-003 — Proposal Is Not Approval

Agent-generated, model-generated, or system-generated output remains a proposal unless an authorized human decision explicitly changes its status.

---

### GOP-004 — Approval Is Not Execution

Approval authorizes a transition but does not prove that execution occurred.

The following states remain distinct:

```text
Proposed
→ In Review
→ Approved
→ Scheduled
→ Executed
→ Observed
→ Evaluated
```

---

### GOP-005 — Memory Is Not Scientific Truth

Persistent memory may influence system behavior but must not automatically become verified knowledge.

Memory must preserve:

* type;
* source;
* scope;
* version;
* freshness;
* confidence;
* review status;
* usage history.

---

### GOP-006 — Trust Is Multidimensional

No single score may replace separate inspection of:

* scientific validity;
* evidence quality;
* provenance completeness;
* memory validity;
* human review;
* computational reproducibility;
* policy compliance;
* evaluation results;
* unresolved limitations.

---

### GOP-007 — Missing Information Is Explicit

Unknown, unavailable, restricted, legacy, stale, partial, or not evaluated must be displayed explicitly.

The system must not infer missing provenance, actors, parameters, approval, evidence, or evaluation results.

---

### GOP-008 — Human Authority Is Explicit

Consequential governance actions require a visible authorized actor and role.

The UI must not imply that all users have equal authority.

---

### GOP-009 — Governance Decisions Are Attributable

Every approval, rejection, change request, override, revocation, restriction, or release decision must preserve:

* actor;
* role;
* object;
* object version;
* action;
* reason;
* timestamp;
* downstream effect.

---

### GOP-010 — Correction Does Not Rewrite History

When a memory, knowledge object, evaluation, or decision is corrected:

* a new version is created;
* prior uses retain their historical reference;
* active affected objects may receive warnings;
* current truth changes only through explicit transition.

---

### GOP-011 — Evaluation Does Not Self-Authorize

A passed evaluation may support a release or approval decision, but it does not automatically authorize deployment, scientific acceptance, experiment execution, or knowledge promotion.

---

### GOP-012 — Critical Failure Cannot Be Averaged Away

A high aggregate score must not conceal:

* hallucinated citation;
* approval bypass;
* context mismatch;
* unsupported scientific claim;
* critical provenance gap;
* unsafe recommendation;
* unreproducible computation.

---

# Part III — Trust Object Model

## 5. Governed Object

A Governed Object is any object whose state, use, or transition has scientific, engineering, operational, or governance consequence.

Examples:

* Engineering Decision;
* Candidate Design;
* Simulation Result;
* Experiment Plan;
* Test Result;
* Scientific Claim;
* Knowledge Rule;
* Evidence Record;
* Memory Object;
* Agent Version;
* Model Version;
* Prompt Version;
* Tool Version;
* Evaluation Run;
* Approval Request.

Every governed object should support, where applicable:

```yaml
object_id:
object_type:
version:
current_status:
scientific_status:
governance_status:
owner:
created_by:
created_at:
updated_at:
provenance_id:
approval_state:
evaluation_state:
supersedes:
superseded_by:
```

---

## 6. Trust State Is Derived

Trust state must be derived from multiple source objects.

It must not be stored as an unexplained final label only.

Example:

```text
Evidence support: Moderate
Provenance completeness: Partial
Human approval: Approved
Reproducibility: Not verified
Memory validity: Current
Evaluation: Regression detected
```

Any summary label must remain expandable to these dimensions.

---

## 7. Governance State and Scientific State

Scientific state and governance state must remain distinct.

### Scientific State Examples

* Observed;
* Literature-reported;
* Predicted;
* Inferred;
* Proposed;
* Contradicted;
* Uncertain;
* Stale;
* Superseded.

### Governance State Examples

* Draft;
* Pending Review;
* In Review;
* Changes Requested;
* Approved;
* Rejected;
* Overridden;
* Revoked;
* Restricted;
* Quarantined;
* Expired;
* Resolved.

An object may simultaneously be:

```text
Scientific state: Predicted
Governance state: Approved for validation
```

It must not be displayed simply as “Approved” without qualification.

---

# Part IV — Page Context and Ownership

## 8. Persistent Page Context

Page 04 must preserve:

* project;
* DBTL cycle;
* source page;
* source stage;
* governed object;
* object version;
* selected event;
* selected approval;
* selected memory;
* selected evaluation;
* active filters;
* current governance work mode;
* open inspector or detail region.

---

## 9. Context Ownership

Each context field must have a single authoritative owner.

Recommended ownership:

```text
Project and cycle
→ Global workspace context

Object and version
→ Domain/server state

Approval and evaluation state
→ Governance backend

Selected item and open panels
→ Page UI state

Shareable filters and stable selection
→ URL state where appropriate
```

Page 04 must not create a second authoritative project, cycle, object, approval, or evaluation state.

---

## 10. Source Context Preservation

When Page 04 is opened from Page 01, Page 02, or Page 03, it must preserve:

```text
Source page
Source object
Source object version
Source selection
Governance question
Return location
```

Returning must not silently open a different version.

---

## 11. Historical Context

When inspecting historical state:

* the page must be read-only unless a new governance action is explicitly initiated;
* historical and current state must be visually distinct;
* current approval must not be inferred from historical approval;
* historical memory or evidence versions must remain identifiable.

---

# Part V — Attention and Governance Queue Principles

## 12. Attention Queue Purpose

The Attention Queue is not a generic inbox.

It exists to identify:

* consequential unresolved governance work;
* trust failures;
* pending human decisions;
* provenance gaps;
* memory risks;
* evaluation regressions;
* expired approval;
* unresolved override;
* policy or role violation.

---

## 13. Attention Item Requirements

Every item must explain:

* what happened or is missing;
* which object and version are affected;
* why it matters;
* risk or consequence;
* required action;
* responsible owner;
* current status;
* age or deadline where applicable.

---

## 14. Attention Priority

Priority should be determined by explicit factors such as:

* scientific consequence;
* safety consequence;
* downstream scope;
* approval urgency;
* active use of stale or conflicting memory;
* critical evaluation regression;
* provenance severity;
* number of affected objects;
* irreversibility.

The system must not invent urgency from visual design alone.

---

## 15. Queue Resolution

An item may leave the active Attention Queue only when:

* the required governance action is completed;
* the issue is formally accepted as a known limitation;
* the item is superseded;
* the issue is demonstrated to be invalid;
* the relevant object is retired;
* the scope changes and the item is no longer applicable.

Resolution must create an audit event.

---

# Part VI — Human Approval Principles

## 16. Approval Lifecycle

The canonical lifecycle is:

```text
Draft Request
→ Submitted
→ Pending Reviewer
→ In Review
→ Changes Requested
→ Resubmitted
→ Approved | Rejected
→ Expired | Revoked | Superseded
```

Alternative backend states may be mapped through adapters, but semantic distinctions must remain.

---

## 17. Approval Request Creation

An approval request must identify:

* target object;
* exact target version;
* requested transition;
* requester;
* required reviewer role;
* reason approval is needed;
* supporting package;
* downstream effect.

An approval request must not be created for an unspecified future version.

---

## 18. Approval Package Completeness

A consequential approval package should contain:

1. object identity;
2. version;
3. requested transition;
4. scientific purpose;
5. change summary;
6. supporting evidence;
7. conflicting evidence;
8. assumptions;
9. uncertainties;
10. risks;
11. trade-offs;
12. limitations;
13. validation requirements;
14. downstream consequences;
15. prior review history;
16. provenance completeness.

If required content is absent, the state must be:

```text
Incomplete Review Package
```

or equivalent.

Approval controls may be blocked according to policy.

---

## 19. Reviewer Authority

Authority must be determined by the backend or approved policy source.

The frontend may display authority but must not independently grant it.

Possible authority states:

* Authorized;
* Not Authorized;
* Authorized with Conditions;
* Delegated;
* Expired;
* Unknown;
* Backend Unavailable.

---

## 20. Approval Decision

Approval must record:

```yaml
approval_id:
target_object_id:
target_version:
requested_transition:
reviewer_id:
reviewer_role:
decision:
reason:
conditions:
timestamp:
validity:
downstream_effect:
```

Approval applies only to the recorded target version and transition.

---

## 21. Rejection

Rejection must require a rationale.

It must not delete the request.

Rejected objects remain inspectable.

A revised version requires a new or resubmitted approval request according to backend policy.

---

## 22. Request Changes

A change request must identify:

* requested changes;
* reason;
* blocking or non-blocking status;
* reviewer;
* target version;
* resubmission requirements.

The original requested version remains historical.

---

## 23. Conditional Approval

Conditional approval must state:

* conditions;
* responsible owner;
* verification requirement;
* due date or validity window if applicable;
* consequences of unmet conditions.

Conditional approval must not appear equivalent to unconditional approval.

---

## 24. Override

Override is an exceptional governance action.

It requires:

* authorized role;
* explicit reason;
* original decision or policy;
* accepted risk;
* target object and version;
* scope;
* validity;
* downstream effect;
* later review when required.

The interface must display both:

* original decision;
* override decision.

---

## 25. Revocation

Approval may be revoked because of:

* new conflicting evidence;
* changed object version;
* safety issue;
* evaluation regression;
* invalid reviewer authority;
* expired approval;
* provenance failure;
* implementation deviation.

Revocation creates a new event and does not erase the original approval.

---

## 26. Approval Expiry

Approval validity must be re-evaluated when:

* object version changes;
* material input changes;
* evidence state changes;
* applicable knowledge is superseded;
* policy changes;
* validity time expires;
* execution context changes materially.

Expired approval must not be shown as current authorization.

---

# Part VII — Memory Operating Principles

## 27. Memory Purpose

Memory exists to support continuity, not to create hidden authority.

It may preserve:

* project context;
* prior decisions;
* user preferences;
* workflow state;
* prior results;
* learned patterns;
* model-generated summaries;
* governed scientific facts;
* temporary working context.

These memory types must remain distinguishable.

---

## 28. Memory Classes

Recommended classes:

### 28.1 Working Memory

Short-lived task or session context.

### 28.2 Workspace Memory

Project, cycle, selection, and workflow continuity.

### 28.3 Decision Memory

Prior choices, rationale, alternatives, and outcomes.

### 28.4 Scientific Memory

Scientific claims or structured findings with source and review state.

### 28.5 User Preference Memory

Non-scientific user workflow preferences.

### 28.6 Governance Memory

Policies, approval requirements, restrictions, and prior governance actions.

A single memory object must not silently change class.

---

## 29. Memory Lifecycle

```text
Candidate
→ Structured
→ Reviewed when required
→ Active
→ Used
→ Reassessed
→ Updated
→ Superseded | Restricted | Retired | Rejected
```

---

## 30. Memory Creation

Memory creation must preserve:

* origin;
* actor;
* timestamp;
* source object;
* source version;
* memory class;
* scope;
* confidence;
* review requirement;
* sensitivity.

Model-generated summaries must remain identified as model-generated.

---

## 31. Memory Scope

Memory may be scoped to:

* task;
* session;
* user;
* project;
* DBTL cycle;
* organism;
* strain;
* laboratory;
* governed global knowledge.

Scope mismatch must be detectable.

A strain-specific observation must not silently influence another strain without explicit transfer logic.

---

## 32. Memory Use

When a memory materially affects a scientific or governance output, the system must retain or expose:

* memory ID;
* memory version;
* retrieval reason;
* use context;
* affected output;
* source;
* scope;
* freshness;
* applicability;
* confidence.

---

## 33. Memory Freshness

Freshness may be determined from:

* time;
* source version;
* changed project context;
* new evidence;
* superseding memory;
* policy change;
* organism or condition mismatch.

Freshness must not be based only on the creation timestamp.

---

## 34. Memory Conflict

Conflicting memory must not be silently merged.

The system should preserve:

* both memory objects;
* conflict type;
* source of each;
* affected decisions;
* review status;
* resolution or unresolved state.

---

## 35. Memory Correction

Correction must create a new version.

Historical outputs retain the memory version originally used.

Active objects using invalid or superseded memory should be discoverable.

---

## 36. Memory Retirement

Retired memory:

* is not used for new outputs by default;
* remains historically inspectable;
* preserves prior usage;
* records retirement reason;
* identifies replacement when applicable.

---

## 37. Sensitive Memory

Sensitive memory must respect backend permission and privacy policy.

The UI must not leak restricted content through:

* summaries;
* search snippets;
* counts;
* exports;
* provenance previews;
* related-object lists.

---

# Part VIII — Audit Operating Principles

## 38. Audit Purpose

Audit history exists to reconstruct consequential scientific and governance activity.

It is not merely infrastructure telemetry.

---

## 39. Audit Event Threshold

An event should become a governed audit event when it changes or materially affects:

* object state;
* scientific interpretation;
* evidence linkage;
* memory;
* approval;
* evaluation;
* version;
* ownership;
* permissions;
* execution plan;
* result;
* governance action.

Low-level visual interactions need not become audit events unless required by policy.

---

## 40. Minimum Audit Event

A valid audit event should contain:

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
timestamp:
previous_state:
new_state:
reason:
result:
project_id:
cycle_id:
related_objects:
provenance_id:
```

Where a field is not applicable, it should be explicit rather than fabricated.

---

## 41. Actor Types

Actor type must distinguish:

* Human;
* Agent;
* Automated System;
* External Tool;
* Imported Historical Record;
* Unknown Legacy Actor.

---

## 42. Audit Append-Only Principle

The user-facing system treats audit history as append-only.

Corrections create new correction events.

Deletion requests, where legally or technically required, must themselves remain governed and auditable according to backend policy.

---

## 43. Audit Ordering

Audit history may be ordered by:

* event time;
* ingestion time;
* causal relationship;
* object version.

When event time and ingestion time differ materially, the difference should remain inspectable.

---

## 44. Duplicate and Retry Events

Repeated or retried operations must not appear as independent successful outcomes without explanation.

The system should distinguish:

* initial attempt;
* retry;
* duplicate delivery;
* cancellation;
* timeout;
* partial result;
* final result.

---

## 45. Causal Reconstruction

Page 04 should support reconstruction of:

```text
Trigger
→ Input
→ Actor
→ Action
→ State Change
→ Review
→ Approval
→ Execution
→ Result
```

Chronological proximity alone must not be treated as causal proof.

---

## 46. Audit Correction

If metadata is incorrect:

* preserve original record where policy requires;
* create correction event;
* record correcting actor;
* record reason;
* display corrected interpretation;
* preserve audit linkage.

---

# Part IX — Provenance Operating Principles

## 47. Provenance Purpose

Provenance explains how an object came to exist and change.

Audit answers:

> What happened?

Provenance answers:

> What inputs, transformations, actors, versions, tools, and decisions produced this object?

---

## 48. Canonical Provenance Chain

```text
User Input / Source Data / Memory
→ Retrieval
→ Task or Prompt
→ Agent
→ Model
→ Tool
→ Parameters
→ Intermediate Artifact
→ Output
→ Evaluation
→ Human Edit
→ Review
→ Approval
→ Execution
→ Observation
```

Not all objects require all stages.

Missing stages must remain explicit.

---

## 49. Provenance Identity

Each provenance-linked entity should use stable references:

* source object ID;
* source version;
* agent ID and version;
* model ID and version;
* prompt or task ID and version;
* tool ID and version;
* dataset ID and version;
* parameter set ID;
* output artifact ID;
* review ID;
* approval ID.

Display names alone are insufficient.

---

## 50. Provenance Completeness

Possible states:

* Complete;
* Partial;
* Missing Source;
* Missing Version;
* Missing Actor;
* Missing Parameters;
* Missing Evaluation;
* Missing Human Review;
* Restricted;
* Legacy;
* Unavailable.

“Complete” may be used only when all required provenance fields for that object class are present.

---

## 51. Computational Reproducibility

A computational output is reproducible only when sufficient information exists, such as:

* input;
* dataset version;
* model or tool;
* software version;
* parameters;
* random seed where applicable;
* environment or workflow version;
* output;
* execution status.

Provenance completeness and reproducibility are related but not identical.

---

## 52. Human Edit Provenance

Human edits to generated output must preserve:

* original generated version;
* editor;
* changed fields;
* time;
* reason where consequential;
* resulting version.

The system must not falsely attribute human-edited output entirely to the agent.

---

## 53. External Provenance

When provenance depends on an external system:

* retain external object reference;
* show synchronization status;
* show last verified time;
* show unavailable state when the system cannot be reached;
* do not fabricate external detail.

---

# Part X — Evaluation Operating Principles

## 54. Evaluation Purpose

Evaluation determines whether a defined system target performs acceptably for a defined scientific task under a defined evaluation suite.

Evaluation is always contextual.

---

## 55. Evaluation Target

Every evaluation must identify:

* target type;
* target ID;
* target version;
* intended use;
* scope;
* evaluation suite;
* baseline;
* evaluator;
* data or golden set;
* run time.

---

## 56. Evaluation Levels

Supported evaluation levels may include:

* Component;
* Agent;
* Workflow;
* Governance Process;
* Knowledge Extraction;
* Recommendation;
* Full DBTL Cycle;
* Outcome.

These levels must not be mixed without explanation.

---

## 57. Evaluation Dimensions

At minimum, dimensions should be selected from:

* scientific correctness;
* evidence fidelity;
* contradiction handling;
* context sensitivity;
* provenance completeness;
* uncertainty calibration;
* hallucination;
* tool-use correctness;
* retrieval quality;
* recommendation actionability;
* validation quality;
* governance compliance;
* reproducibility;
* robustness;
* latency;
* cost.

Not every evaluation requires all dimensions.

The selected dimensions must match the intended use.

---

## 58. Evaluation Run Lifecycle

```text
Draft
→ Configured
→ Scheduled
→ Running
→ Partially Completed
→ Completed
→ Reviewed
→ Accepted | Rejected | Accepted with Limitations
→ Superseded
```

Failed or invalid runs remain inspectable.

---

## 59. Evaluation Baseline

A baseline must identify an exact version.

Possible baselines:

* previous approved version;
* current production version;
* human-reviewed reference;
* golden output;
* policy threshold;
* previous workflow.

The baseline must not be silently changed between comparisons.

---

## 60. Golden Set Principles

A golden set should be:

* versioned;
* reviewed;
* scoped;
* representative;
* provenance-linked;
* explicit about ambiguity;
* explicit about acceptable alternatives;
* separated from evaluation target training where applicable.

---

## 61. Evaluation Slices

Aggregate results should be decomposable by meaningful slices, such as:

* organism;
* strain;
* engineering objective;
* evidence availability;
* complexity;
* intervention type;
* scientific domain;
* task stage;
* user role;
* failure severity.

---

## 62. Critical Regression

A critical regression is any regression that violates:

* scientific correctness;
* evidence traceability;
* approval safety;
* context integrity;
* provenance requirements;
* privacy or permission boundaries;
* wet-lab handoff safety.

Critical regression blocks approval or release unless an authorized override explicitly accepts the risk.

---

## 63. Failure Classification

Evaluation failures should support controlled categories:

* Retrieval Failure;
* Evidence Omission;
* Unsupported Claim;
* Hallucinated Citation;
* Context Mismatch;
* Entity Resolution Failure;
* Reasoning Failure;
* Tool Failure;
* Simulation Misuse;
* Uncertainty Failure;
* Governance Bypass;
* Provenance Gap;
* Reproducibility Failure;
* Schema Failure;
* Performance Failure.

---

## 64. Evaluation Review

Evaluation results do not become governance decisions until reviewed where required.

Review should inspect:

* test validity;
* suite version;
* data quality;
* failure examples;
* material regression;
* limitations;
* intended-use relevance;
* reproducibility.

---

## 65. Evaluation Outcome

Possible outcomes:

* Accepted;
* Accepted with Limitations;
* Changes Required;
* Restricted;
* Quarantined;
* Rollback Recommended;
* Re-evaluation Required;
* Invalid Evaluation;
* No Decision.

---

# Part XI — Governance Action Principles

## 66. Governance Actions

Page 04 may initiate or record:

* Approve;
* Reject;
* Request Changes;
* Override;
* Revoke;
* Restrict;
* Quarantine;
* Supersede;
* Retire;
* Request Evidence;
* Request Reproducibility Check;
* Request Re-evaluation;
* Create Investigation;
* Create Remediation;
* Accept Known Limitation.

---

## 67. Action Preconditions

Every governance action must define:

* actor authority;
* target;
* target version;
* current state;
* allowed transition;
* required rationale;
* required supporting information;
* downstream effect;
* reversibility;
* audit requirement.

---

## 68. Consequential Action Confirmation

Before committing a consequential action, the user must understand:

* exact object;
* exact version;
* intended transition;
* effect;
* whether reversible;
* who will be notified;
* downstream systems affected;
* reason requirement;
* approval or authority requirement.

---

## 69. Action Idempotency

Repeated submission must not create duplicate governance outcomes.

The UI and backend integration should account for:

* pending mutation;
* retry;
* timeout;
* duplicate response;
* stale response;
* already-completed action.

---

## 70. Action Failure

A failed governance action must not appear committed.

The interface must show:

* failure;
* saved review notes;
* whether retry is safe;
* current server state;
* object version;
* conflict information.

---

# Part XII — Cross-Page Operating Principles

## 71. Page 01 Integration

Page 04 provides Page 01 with:

* pending decision summary;
* critical trust warning;
* approval state;
* evaluation regression;
* recent consequential change;
* responsible owner.

Page 01 remains the project command view.

---

## 72. Page 02 Integration

Page 04 governs:

* engineering decision approvals;
* experiment-plan approvals;
* simulation provenance;
* critique resolution;
* wet-lab handoff readiness;
* execution deviation;
* prediction-to-observation evaluation.

Page 02 remains the engineering runtime.

---

## 73. Page 03 Integration

Page 04 governs:

* knowledge promotion;
* evidence review history;
* memory derived from knowledge;
* knowledge correction;
* provenance completeness;
* extraction and synthesis evaluation;
* affected decisions after knowledge supersession.

Page 03 remains the knowledge and evidence production environment.

---

## 74. Cross-Page State Propagation

A governance action may update another page only through real shared backend state or approved events.

The frontend must not simulate cross-page truth by local mutation alone.

---

## 75. Affected-Object Propagation

When an object is corrected, revoked, restricted, or superseded, the system should identify dependent active objects.

Examples:

```text
Superseded memory
→ active decisions using that memory

Revoked approval
→ scheduled Build/Test work

Critical model regression
→ outputs generated by that model version

Retracted evidence
→ claims and recommendations relying on it
```

Affected-object analysis must distinguish known dependency from inferred impact.

---

# Part XIII — Permission and Privacy Principles

## 76. Backend-Enforced Authority

Permissions, roles, and access must be enforced by the backend.

Frontend hiding is not security.

---

## 77. Permission States

The interface must support:

* Authorized;
* Unauthorized;
* Read-only;
* Conditional;
* Restricted Field;
* Unknown;
* Permission Service Unavailable.

---

## 78. Restricted Content

Restricted records must not leak through:

* search;
* breadcrumbs;
* related-object labels;
* event preview;
* export;
* count tooltip;
* URL;
* error messages.

---

## 79. Export

Governance exports must preserve:

* scope;
* object IDs;
* versions;
* timestamps;
* filters;
* actor attribution;
* provenance;
* approval status;
* limitation;
* export time.

Exports must not imply current validity when they represent historical state.

---

# Part XIV — Runtime State Principles

## 80. Required Runtime States

Every Page 04 capability must support where applicable:

* Loading;
* Normal;
* Empty;
* Partial;
* Stale;
* Offline;
* Error;
* Unauthorized;
* Restricted;
* Historical;
* Superseded;
* Conflict;
* Mutation Pending;
* Mutation Failed.

---

## 81. Loading

Loading must not fabricate content.

The page shell and available context should load independently from deeper detail.

Decision controls remain unavailable until required basis is loaded.

---

## 82. Partial Data

Partial data must identify:

* available content;
* missing content;
* impact on trust judgement;
* whether action is blocked;
* retry or owner.

---

## 83. Stale Data

Stale content must show:

* last verified time;
* reason;
* known newer version;
* affected action;
* refresh path;
* read-only state where required.

---

## 84. Offline

Offline mode must not allow approval or governance action to appear committed.

Draft notes may be preserved according to approved persistence rules.

---

## 85. Conflict

Version conflict must show:

* current local version;
* current server version;
* changed fields;
* safe recovery;
* copy or preserve user notes;
* prohibition on silent overwrite.

---

## 86. Historical and Superseded State

Historical and superseded objects must remain inspectable but should be read-only by default.

New action must target a current or explicitly selected version.

---

# Part XV — Agent and Automation Principles

## 87. Agent Role

Agents may:

* assemble approval packages;
* identify provenance gaps;
* summarize audit history;
* detect stale memory;
* run approved evaluations;
* classify failure patterns;
* suggest remediation;
* identify affected objects.

Agents may not:

* approve their own output;
* override human decisions;
* silently modify memory;
* rewrite audit history;
* suppress failed evaluation;
* mark an object trusted without basis;
* promote a proposal to execution without authority.

---

## 88. Agent Output State

Agent-generated governance output must be labeled as:

* Suggested;
* Draft;
* Candidate;
* Needs Review;
* Incomplete;
* Failed;
* Unavailable.

It must not be labeled as approved unless a separate human approval exists.

---

## 89. Automation Boundaries

Automation may perform reversible, low-risk actions when explicitly permitted by policy, such as:

* opening a review request;
* creating a draft remediation;
* flagging stale memory;
* scheduling an evaluation;
* linking existing provenance.

Consequential transitions remain human governed unless the approved policy explicitly defines otherwise.

---

## 90. Self-Evaluation

An agent may self-critique, but self-critique is not independent validation.

The system must distinguish:

* self-critique;
* automated evaluator;
* human review;
* observed outcome.

---

# Part XVI — Decision and Release Principles

## 91. Governance Readiness

A governed object is ready for a decision only when:

* target and version are known;
* requested transition is explicit;
* required package is sufficiently complete;
* authority is known;
* provenance status is visible;
* material risk and limitation are visible;
* unresolved blocking issue is identified.

---

## 92. Approval Readiness

Approval readiness does not mean scientific certainty.

It means the reviewer has sufficient information to make the defined governance decision.

---

## 93. Release Readiness

A model, agent, prompt, tool, or workflow version may be considered release-ready only when:

* intended use is defined;
* evaluation suite is complete;
* critical regressions are absent or formally overridden;
* provenance is complete enough;
* governance review is complete;
* limitations are visible;
* rollback or restriction path exists.

---

## 94. Wet-Lab Handoff Readiness

A scientific object may be marked ready for wet-lab handoff only when:

* exact version is approved;
* required controls exist;
* validation criteria exist;
* safety and feasibility are reviewed;
* provenance is sufficient;
* unresolved blocking critique is absent;
* downstream owner is identified.

---

# Part XVII — Stop and Refusal Principles

## 95. Operating Stop Conditions

Page 04 must stop or block an action when:

* target object or version is ambiguous;
* authority cannot be verified;
* required review package is materially incomplete;
* object changed during review;
* approval is expired;
* provenance is critically incomplete;
* evaluation has a critical unresolved regression;
* restricted data cannot be safely displayed;
* backend state conflicts with local state;
* audit or approval mutation cannot be confirmed;
* action would rewrite history;
* action would cause unauthorized execution.

---

## 96. Runtime Refusal Rules

The system must refuse to:

* fabricate provenance;
* fabricate audit events;
* fabricate human approval;
* fabricate evaluation results;
* treat agent self-review as independent approval;
* silently use stale memory;
* rewrite historical decisions;
* approve an unspecified version;
* mark planned work as executed;
* average away critical scientific failure;
* expose restricted governance data;
* permit unauthorized override.

---

# Part XVIII — Operating Metrics

## 97. Trust Operations Metrics

Operational metrics may include:

* open governance actions;
* provenance completeness;
* decision reconstruction time;
* stale-memory use;
* active objects using superseded sources;
* approval/version mismatch prevention;
* unresolved critical regressions;
* remediation completion;
* audit reconstruction success.

Metrics must be interpreted with context.

---

## 98. Anti-Gaming Principle

The system must not optimize for:

* fastest approval at the expense of review quality;
* lowest open-item count through premature resolution;
* highest average evaluation score by excluding difficult cases;
* highest provenance completeness through meaningless metadata;
* lowest memory-conflict count through silent merging.

---

# Part XIX — Operating Acceptance Matrix

## 99. Memory Operating Acceptance

| Capability        | Required behavior                             |
| ----------------- | --------------------------------------------- |
| Memory creation   | Source, scope, type, version, actor preserved |
| Memory use        | Material use is inspectable                   |
| Memory conflict   | Conflicting objects remain visible            |
| Memory correction | New version; history preserved                |
| Memory retirement | New use stops; history remains                |
| Sensitive memory  | Permission boundaries enforced                |

---

## 100. Audit Operating Acceptance

| Capability     | Required behavior                                |
| -------------- | ------------------------------------------------ |
| Event creation | Consequential event is attributable              |
| History        | Append-only from product perspective             |
| Correction     | New correction event                             |
| Actor          | Human, agent, system, or external actor explicit |
| Retry          | Retry and duplicate semantics visible            |
| Reconstruction | Object and causal history can be followed        |

---

## 101. Approval Operating Acceptance

| Capability | Required behavior                      |
| ---------- | -------------------------------------- |
| Request    | Exact object, version, transition      |
| Review     | Complete basis exposed                 |
| Authority  | Backend-enforced and visible           |
| Decision   | Attributable and reasoned              |
| Override   | Exceptional and audited                |
| Revocation | New event; original approval preserved |
| Expiry     | Invalid approval not shown as current  |

---

## 102. Evaluation Operating Acceptance

| Capability | Required behavior                               |
| ---------- | ----------------------------------------------- |
| Target     | Exact component and version                     |
| Suite      | Versioned and scoped                            |
| Baseline   | Explicit                                        |
| Dimensions | Separate, not hidden by aggregate               |
| Failures   | Concrete examples inspectable                   |
| Regression | Critical regression blocks release              |
| Outcome    | Creates governed action, not automatic approval |

---

# Part XX — Operating Constitution

```text
Page 04 shall govern consequential scientific and system state through exact object identity, explicit versioning, preserved history, human authority, and inspectable evidence.

Memory shall improve continuity without becoming hidden scientific truth.

Every material memory use shall remain inspectable.

Memory correction shall create a new version and shall not rewrite prior decisions.

Audit history shall be append-only from the product perspective.

Every consequential audit event shall preserve actor, action, object, version, time, reason, and result where applicable.

Provenance shall identify the inputs, actors, transformations, models, tools, parameters, artifacts, reviews, and approvals that produced an object.

Missing provenance shall be explicit.

Proposal, review, approval, execution, observation, and evaluation shall remain semantically distinct.

Approval shall be object-specific, version-specific, transition-specific, attributable, and role-aware.

Approval shall not imply execution.

Override shall remain exceptional, reasoned, visible, and auditable.

Evaluation shall be scoped to an exact target, version, suite, baseline, and intended use.

Evaluation shall not reduce scientific trust to a single aggregate score.

Critical scientific, provenance, or governance failure shall not be averaged away.

Agent-generated governance output shall remain a draft or proposal until reviewed according to policy.

Agents shall not approve their own consequential outputs.

Corrections, revocations, restrictions, supersession, and remediation shall preserve historical context.

Cross-page governance state shall propagate only through authoritative shared backend state or approved events.

Page 04 shall stop and refuse actions when identity, version, authority, provenance, permission, or decision basis is insufficient.
```

---

# Part XXI — Final Operating Summary

The canonical Page 04 operating loop is:

```text
Identify Governance Need
→ Select Exact Object and Version
→ Inspect Memory, Evidence, Provenance, and History
→ Determine Authority and Required Transition
→ Review Risk, Limitation, and Consequence
→ Approve, Reject, Request Changes, Restrict, or Override
→ Record Immutable Audit Event
→ Propagate Authoritative State
→ Observe Outcome
→ Evaluate
→ Create Corrective or Learning Action
```

Page 04 succeeds only when the system can preserve a complete and trustworthy chain from:

```text
What the system remembered
→ What the system or human did
→ What exact object changed
→ Why the change occurred
→ Who reviewed and authorized it
→ What was executed
→ What outcome occurred
→ Whether the process and outcome were acceptable
→ What governance action follows
```

without silently rewriting history, inventing provenance, confusing approval with execution, allowing agents to self-authorize, or hiding critical uncertainty.
