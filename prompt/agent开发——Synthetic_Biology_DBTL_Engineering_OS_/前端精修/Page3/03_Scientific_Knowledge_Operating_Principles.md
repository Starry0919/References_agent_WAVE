# Synthetic Biology DBTL Engineering OS

# Page 03 — Knowledge & Evidence Layer

# 03_Operating_Principles.md

> **Document type**: Page-specific operating contract
> **Page**: Page 03 — Knowledge & Evidence Layer
> **Product role**: Scientific Knowledge Production System
> **Status**: Normative / Implementation-Binding
> **Parent contract**: Page Design Contract v1.1.0
> **Parent architecture**: Synthetic Biology DBTL Engineering OS Frontend Architecture v1.2
> **Default UI language**: English
> **Specification language**: English, with implementation notes permitted in Chinese
> **Version**: 1.0.0
> **Last updated**: 2026-07-23

---

## Specification Header

```yaml
page_id: page-03
page_name: Knowledge & Evidence Layer
spec_type: Operating Principles
version: 1.0.0
status: Approved
product_positioning: Scientific Knowledge Production System
owners:
  - Product Owner
  - Scientific Product Lead
reviewers:
  - Synthetic Biology Reviewer
  - Dry-Lab Reviewer
  - Wet-Lab Reviewer
  - Frontend Architect
  - UX Reviewer
parent_contract: Page Design Contract v1.1.0
parent_architecture: Frontend Architecture Prompt v1.2
dependencies:
  - 00_Page_Research.md
  - 01_Product_Spec.md
  - 02_UI_Spec.md
  - 04_Technical_Spec.md
  - 05_Content_Spec.md
  - 06_Acceptance_Spec.md
approved_exceptions: []
open_questions: []
```

---

# Part I — Operating Identity

## 1. Purpose

This document defines how Page 03 operates as the **Scientific Knowledge Production System** of the Synthetic Biology DBTL Engineering Operating System.

It governs:

* how scientific information enters the system;
* how information becomes structured knowledge;
* how knowledge becomes reusable engineering intelligence;
* how evidence supports, limits, or contradicts claims;
* how users retrieve, inspect, compare, curate, review, reuse, and retire knowledge;
* how Page 03 supports the DBTL Engineering Workspace;
* how new experimental outcomes update the knowledge system;
* how scientific truth, provenance, uncertainty, and historical versions are preserved.

This document does not primarily define page appearance. Visual composition belongs to `02_UI_Spec.md`.

This document does not define React component implementation or backend architecture. Those belong to `04_Technical_Spec.md`.

This document defines the **operating behavior and scientific rules** that both UI and implementation must preserve.

---

## 2. Operating Mission

Page 03 exists to transform fragmented scientific information into structured, governed, reusable, and traceable engineering knowledge.

Its operating mission is:

```text
Scientific Information
→ Structured Knowledge
→ Validated Evidence
→ Biological Understanding
→ Engineering Rule
→ Reusable Engineering Action
→ DBTL Decision Support
→ Experimental Learning
→ Knowledge Evolution
```

The page must not operate as:

* a generic literature database;
* a PDF repository;
* a search-engine results page;
* a chatbot answering biological questions;
* a disconnected knowledge graph visualization;
* a passive archive of AI-generated summaries;
* an ungoverned RAG interface;
* a replacement for the DBTL Engineering Workspace.

---

## 3. Primary Operating Question

Every major workflow on Page 03 must help answer:

> **What reusable scientific knowledge supports, limits, contradicts, or changes this engineering decision?**

Secondary operating questions are:

1. What biological mechanism is represented?
2. What evidence supports or contradicts the mechanism?
3. How strong, direct, current, and transferable is the evidence?
4. Under what biological and experimental conditions is the knowledge valid?
5. What engineering rule or action can be derived?
6. What uncertainty, limitation, or failure pattern remains?
7. Can this knowledge safely participate in an engineering recommendation?
8. What new result would strengthen, weaken, update, or retire it?

---

## 4. Operating Position in the Product

Page 03 is one of four primary product areas:

```text
Page 01 — Project Command Center
Coordinates project, cycle, ownership, risk, and decisions.

Page 02 — DBTL Engineering Workspace
Diagnoses, designs, simulates, critiques, and prepares Build/Test plans.

Page 03 — Knowledge & Evidence Layer
Produces, validates, structures, and evolves reusable scientific knowledge.

Page 04 — Trust & Provenance Center
Audits memory, versions, approvals, evaluations, and system governance.
```

The relationship between Page 02 and Page 03 is:

```text
Page 02 requests scientific support
→ Page 03 retrieves and synthesizes governed knowledge
→ Page 02 uses that knowledge in a proposal
→ Human review governs the proposal
→ Experiment produces new observations
→ Page 03 updates evidence and knowledge
```

Page 03 supports engineering decisions but does not approve wet-lab execution.

---

# Part II — Operating Invariants

The following invariants are non-negotiable.

A feature, visual design, backend capability, or generated output that violates an invariant must not be implemented.

## 5. Invariant 001 — Identifiable Origin

Every consequential knowledge object must originate from an identifiable source.

Permitted origins include:

* primary literature;
* curated review;
* DDR;
* biological rule;
* internal experiment;
* external dataset;
* simulation;
* computational model;
* expert-curated knowledge;
* explicitly labeled user entry;
* explicitly labeled model-generated inference.

Knowledge without an identifiable origin cannot be treated as verified scientific knowledge.

---

## 6. Invariant 002 — Provenance Persistence

Provenance must remain attached to the knowledge object throughout:

* extraction;
* normalization;
* synthesis;
* comparison;
* recommendation;
* reuse;
* revision;
* deprecation;
* export.

Summaries must not sever knowledge from their original sources.

---

## 7. Invariant 003 — Observation Precedence

Inference must never overwrite observation.

The system must preserve distinctions among:

* observed;
* processed;
* predicted;
* inferred;
* literature reported;
* curated;
* user entered;
* model generated.

An inferred relationship may be linked to an observation but may not be displayed as the observation itself.

---

## 8. Invariant 004 — Contradictions Remain Visible

Supporting evidence must not erase conflicting evidence.

The system must preserve:

* supportive findings;
* contradictory findings;
* null findings;
* unresolved disagreement;
* non-transferable evidence;
* insufficient evidence.

A confidence score must never hide contradiction.

---

## 9. Invariant 005 — Context-Bounded Knowledge

Scientific knowledge is not universally valid by default.

Every reusable rule should preserve relevant context, including when available:

* organism;
* strain;
* genotype;
* growth condition;
* medium;
* substrate;
* oxygen state;
* temperature;
* engineering objective;
* measurement method;
* experimental scale;
* model assumptions;
* intervention strength;
* temporal stage.

A rule derived in one biological context must not be silently applied to another.

---

## 10. Invariant 006 — Governed Engineering Reuse

Knowledge may support a proposed engineering action.

Knowledge alone may not:

* approve an intervention;
* schedule wet-lab execution;
* change an approved design;
* silently replace a human decision;
* convert an inference into accepted fact.

Engineering reuse remains subject to role, version, evidence, and approval rules.

---

## 11. Invariant 007 — Version Preservation

Knowledge evolution must create new versions rather than overwrite historical scientific states.

The system must preserve:

* previous claim wording;
* previous confidence;
* previous evidence set;
* previous relationships;
* reviewer decisions;
* update rationale;
* effective dates;
* supersession relationships.

---

## 12. Invariant 008 — No Unsupported Synthesis

A generated synthesis must not introduce claims unsupported by its inputs.

When a synthesis includes general biological knowledge or model inference, that contribution must be explicitly labeled.

The system must never represent fluent prose as evidence.

---

## 13. Invariant 009 — Evidence Is Not Confidence

Evidence quality and confidence are separate dimensions.

Evidence quality concerns the source and strength of support.

Confidence concerns the system’s certainty in a particular claim, relationship, interpretation, or recommendation.

A high-confidence inference based on limited evidence must still show limited evidence quality.

---

## 14. Invariant 010 — Knowledge Must Be Reusable and Inspectable

A knowledge object is not complete merely because it can be read.

Consequential knowledge should be:

* structured;
* searchable;
* comparable;
* inspectable;
* versioned;
* linked;
* reusable;
* traceable;
* exportable where permitted.

---

## 15. Invariant 011 — DBTL Learning Must Be Possible

Every completed DBTL cycle must be capable of contributing new knowledge.

This does not mean every result automatically becomes an accepted rule.

It means every result can enter a governed update workflow involving:

```text
Observation
→ Evidence Candidate
→ Claim Review
→ Rule Update or New Rule
→ Version Creation
→ Runtime Availability
```

---

## 16. Invariant 012 — Runtime Consumption Does Not Redefine Knowledge

Page 02 may retrieve, reference, compare, and apply Page 03 knowledge.

Page 02 must not silently redefine:

* evidence strength;
* claim status;
* source provenance;
* accepted biological rule;
* knowledge version.

Changes to governed knowledge must return to Page 03’s curation and review workflow.

---

# Part III — Knowledge Object Operating Model

## 17. Knowledge Object Classes

Page 03 operates on structured scientific objects rather than documents alone.

### 17.1 Source Objects

* Paper
* Review
* Dataset
* Figure
* Supplementary Material
* DDR
* Experimental Result
* Simulation Result
* Model Output
* Expert Note
* User Entry

### 17.2 Biological Objects

* Organism
* Strain
* Genotype
* Gene
* Protein
* Metabolite
* Reaction
* Pathway
* Regulatory Interaction
* Cellular Process
* Phenotype

### 17.3 Knowledge Objects

* Scientific Claim
* Biological Mechanism
* Biological Rule
* Engineering Rule
* Design Pattern
* Failure Pattern
* Best Practice
* Assumption
* Limitation
* Open Question

### 17.4 Engineering Objects

* Engineering Goal
* Engineering Strategy
* Engineering Action
* Candidate Intervention
* Validation Criterion
* Trade-off
* Constraint

### 17.5 Governance Objects

* Evidence
* Evidence Set
* Confidence Assessment
* Review
* Version
* Provenance Record
* Contradiction Record
* Deprecation Record
* Audit Event

---

## 18. Minimum Knowledge Object Contract

Every consequential knowledge object must support:

```yaml
knowledge_id:
knowledge_type:
title:
summary:
status:
version:
organism:
strain:
biological_context:
engineering_context:
claim_or_rule:
mechanism:
supporting_evidence_ids:
conflicting_evidence_ids:
assumptions:
limitations:
confidence:
evidence_quality:
source_type:
source_reference:
provenance_id:
owner:
review_status:
created_at:
updated_at:
supersedes:
superseded_by:
```

Missing values must be represented explicitly.

The frontend must not invent absent metadata.

---

## 19. Knowledge Status Vocabulary

Knowledge objects use controlled lifecycle states:

* Draft
* Extracted
* Structured
* In Review
* Changes Requested
* Validated
* Accepted
* Limited
* Conflicting
* Deprecated
* Superseded
* Rejected
* Archived

These states are distinct from engineering decision states.

For example:

* an `Accepted` engineering rule may support a `Proposed` candidate design;
* a `Conflicting` mechanism may still be visible but must not be presented as settled;
* a `Deprecated` rule remains inspectable for historical traceability.

---

## 20. Scientific Nature Vocabulary

Every claim or result must declare its nature:

* Observed
* Processed
* Predicted
* Inferred
* Literature Reported
* Curated Rule
* Expert Curated
* User Entered
* Model Generated

The nature must remain visible in summary and detail contexts.

---

# Part IV — Knowledge Production Lifecycle

## 21. Lifecycle Overview

The canonical lifecycle is:

```text
Acquire
→ Extract
→ Normalize
→ Structure
→ Link
→ Evaluate
→ Validate
→ Publish
→ Reuse
→ Observe Outcome
→ Update
→ Supersede or Retire
```

No stage may silently imply completion of the next stage.

For example:

* extraction does not mean validation;
* validation does not mean universal applicability;
* publication does not mean wet-lab approval;
* reuse does not mean the original knowledge has been changed.

---

## 22. Stage 1 — Acquire

### Purpose

Bring identifiable scientific source material into the system.

### Permitted Inputs

* DOI or publication record;
* uploaded scientific document;
* database record;
* DDR;
* experimental result;
* simulation output;
* model output;
* expert-curated entry;
* internal validated dataset.

### Required Output

```yaml
source_id:
source_type:
title:
origin:
authors_or_actor:
publication_or_creation_date:
access_date:
version:
license_or_access_status:
project_or_global_scope:
ingestion_status:
provenance:
```

### Operating Rules

* Duplicate sources should be linked, not silently copied.
* Unavailable full text must be distinguished from absent evidence.
* A source may be indexed before scientific extraction is complete.
* Imported content must not automatically become accepted knowledge.
* User-entered text must remain labeled as user entered.
* AI-generated summaries must remain derivative objects linked to the source.

---

## 23. Stage 2 — Extract

### Purpose

Identify candidate scientific content from source material.

### Candidate Outputs

* entities;
* relationships;
* claims;
* mechanisms;
* conditions;
* interventions;
* phenotypes;
* measurements;
* limitations;
* failure observations;
* supporting passages;
* contradictory passages.

### Operating Rules

* Extraction must preserve source location where available.
* Extracted content is provisional.
* Extracted claims must not be labeled as curated rules.
* Unsupported entity resolution must be marked uncertain.
* Figures, tables, methods, results, and discussion statements must retain source section distinctions when known.
* Directly reported findings must be separated from author interpretation.

---

## 24. Stage 3 — Normalize

### Purpose

Convert extracted content into consistent system terminology and object identities.

### Normalization May Include

* gene identifier normalization;
* strain naming;
* organism taxonomy;
* unit normalization;
* synonym resolution;
* pathway naming;
* intervention classification;
* condition formatting;
* evidence-type classification.

### Operating Rules

* Original values and terms must remain accessible.
* Normalization must not alter scientific meaning.
* Ambiguous mappings require explicit uncertainty.
* Multiple possible entity mappings must not be arbitrarily collapsed.
* User-visible normalized labels should link back to original source terminology.

---

## 25. Stage 4 — Structure

### Purpose

Create structured scientific objects and relationships.

Canonical transformation:

```text
Source Statement
→ Claim
→ Subject
→ Relationship
→ Object
→ Condition
→ Evidence
→ Limitation
```

### Required Distinctions

* fact versus inference;
* mechanism versus association;
* observation versus recommendation;
* intervention versus outcome;
* condition versus universal statement;
* evidence versus explanation.

---

## 26. Stage 5 — Link

### Purpose

Connect related objects into inspectable knowledge networks.

Permitted relationships include:

* encodes;
* catalyzes;
* consumes;
* produces;
* activates;
* inhibits;
* regulates;
* competes with;
* requires;
* increases;
* decreases;
* causes;
* correlates with;
* supports;
* contradicts;
* derived from;
* applicable to;
* limited by;
* validated by;
* supersedes.

### Operating Rules

* Causal and correlational relationships must not be conflated.
* Relationship direction must be explicit.
* Each consequential relationship must expose its evidence.
* Unsupported graph edges are prohibited.
* Relationship confidence may differ from node confidence.

---

## 27. Stage 6 — Evaluate

### Purpose

Assess whether extracted and structured knowledge is scientifically usable.

Evaluation dimensions may include:

* source quality;
* experimental directness;
* biological relevance;
* strain match;
* condition match;
* sample adequacy;
* mechanistic support;
* reproducibility;
* independent replication;
* computational assumptions;
* transferability;
* recency;
* contradiction;
* completeness.

Evaluation must preserve individual dimensions where available rather than hiding all reasoning behind one score.

---

## 28. Stage 7 — Validate

### Purpose

Determine whether a knowledge object is accepted for governed reuse.

### Possible Outcomes

* Accepted
* Accepted with limitations
* Changes requested
* Conflicting
* Insufficient evidence
* Rejected
* Deferred

### Required Validation Record

```yaml
review_id:
knowledge_id:
knowledge_version:
reviewer:
reviewer_role:
decision:
rationale:
evidence_reviewed:
unresolved_risks:
limitations:
timestamp:
```

### Operating Rules

* Validation must be object- and version-specific.
* AI may assist review but cannot impersonate a human reviewer.
* Validation does not erase uncertainty.
* A validated claim may still have limited external transferability.
* Rejection must preserve the rejected version and rationale.

---

## 29. Stage 8 — Publish for Reuse

### Purpose

Make governed knowledge available to users and the DBTL Engineering Runtime.

### Publication Requirements

A reusable object must expose:

* current version;
* review status;
* scientific nature;
* biological context;
* evidence summary;
* contradictions;
* assumptions;
* limitations;
* provenance;
* permitted reuse scope.

### Reuse Tiers

```text
Tier A — Governed Reuse
Validated knowledge suitable for engineering decision support.

Tier B — Conditional Reuse
Usable only with visible limitations or context warnings.

Tier C — Exploratory Reuse
May support hypothesis generation, not terminal recommendation.

Tier D — Historical Only
Deprecated, superseded, rejected, or archived.
```

---

## 30. Stage 9 — Observe Outcome

When knowledge contributes to an engineering decision, the system should preserve:

* knowledge object and version used;
* engineering decision and version;
* conditions of use;
* model or agent involved;
* human approval;
* predicted outcome;
* observed outcome;
* deviation;
* downstream interpretation.

This enables later evaluation of whether the knowledge transferred successfully.

---

## 31. Stage 10 — Update

New evidence may:

* strengthen an existing claim;
* weaken a claim;
* introduce contradiction;
* narrow applicable context;
* broaden applicable context;
* refine mechanism;
* split one rule into multiple conditional rules;
* merge redundant rules;
* create a new failure pattern;
* update confidence;
* trigger re-review.

Updates must produce a new version.

---

## 32. Stage 11 — Supersede or Retire

Knowledge may be superseded or retired when:

* a mechanism is disproven;
* evidence becomes materially contradictory;
* identifiers or biological interpretations change;
* the rule is replaced by a more precise conditional rule;
* the rule no longer meets governance requirements;
* the source is retracted;
* the computational model is invalidated;
* the knowledge is no longer applicable to supported workflows.

Retirement does not delete provenance or historical use.

---

# Part V — Evidence Operating Principles

## 33. Evidence as a First-Class Object

Evidence is not merely a citation string.

An evidence object should support:

```yaml
evidence_id:
evidence_type:
source_id:
source_location:
claim_id:
relationship:
  - supports
  - contradicts
  - limits
  - contextualizes
directness:
quality:
organism:
strain:
conditions:
measurement:
result:
uncertainty:
limitations:
provenance:
```

---

## 34. Evidence Relationship Types

Evidence may:

* support;
* contradict;
* partially support;
* contextualize;
* limit;
* fail to replicate;
* remain inconclusive.

The UI and data model must not force all evidence into binary support/reject categories.

---

## 35. Evidence Quality

Controlled values:

* Strong
* Moderate
* Limited
* Conflicting
* Unverified
* Not Available

Evidence quality should consider the evidence itself, not the reputation of the source alone.

A high-impact publication must not automatically receive `Strong` evidence status.

---

## 36. Confidence

Confidence must include:

* label or band;
* method;
* contributing evidence;
* contradicting evidence;
* assumptions;
* known uncertainty;
* last evaluation date.

Unsupported numeric precision is prohibited.

---

## 37. Evidence Aggregation

When multiple sources support one claim:

* preserve each source;
* preserve condition differences;
* preserve contradictory results;
* distinguish independent replication from repeated analysis of the same dataset;
* avoid double-counting duplicated datasets or publications;
* expose aggregation method.

---

## 38. Evidence Gap

The system must represent explicit evidence gaps, including:

* no direct evidence;
* no strain-specific evidence;
* no wet-lab validation;
* computational-only support;
* no independent replication;
* missing condition metadata;
* unresolved contradiction;
* outdated source;
* inaccessible source.

An evidence gap is a scientific state, not a generic empty state.

---

# Part VI — Knowledge Operations

## 39. Retrieve

### Definition

Locate knowledge relevant to a biological question, engineering goal, object, mechanism, or decision.

### Retrieval Inputs

* object;
* query;
* organism;
* strain;
* pathway;
* engineering objective;
* intervention;
* phenotype;
* condition;
* evidence threshold;
* review status;
* version or date.

### Retrieval Output

Structured knowledge objects, not only document links.

### Operating Rules

* Scope and active filters must remain visible.
* Results must state why they matched when possible.
* Search relevance must not be confused with evidence quality.
* Current, historical, deprecated, and conflicting objects must be distinguishable.
* No-result states must distinguish absent knowledge from filtering.

---

## 40. Inspect

### Definition

Examine the identity, mechanism, evidence, conditions, limitations, version, and provenance of one object.

### Inspection Depth

```text
Summary
→ Mechanism
→ Evidence
→ Contradiction
→ Applicability
→ Provenance
→ Raw Source
```

Inspection must preserve the user’s active workspace context.

---

## 41. Compare

### Definition

Compare multiple claims, mechanisms, engineering rules, design patterns, sources, or versions.

### Comparison Dimensions

* scientific claim;
* biological mechanism;
* context;
* evidence;
* confidence;
* contradiction;
* limitations;
* engineering utility;
* validation requirements;
* historical outcome.

### Operating Rules

* Comparisons must align equivalent dimensions.
* Missing values must remain explicit.
* A single composite score must not replace scientific dimensions.
* Users must be able to inspect the basis of a difference.

---

## 42. Explain

### Definition

Generate an inspectable explanation of why a claim, mechanism, relationship, or recommendation exists.

A valid explanation should include:

```text
Claim
→ Biological mechanism
→ Supporting evidence
→ Conflicting evidence
→ Assumptions
→ Limitations
→ Engineering implication
```

Model-generated explanation must remain labeled as generated synthesis.

---

## 43. Synthesize

### Definition

Combine multiple governed knowledge objects into a new structured synthesis.

### Synthesis Outputs May Include

* mechanism summary;
* evidence synthesis;
* conditional engineering rule;
* design pattern;
* failure pattern;
* unresolved question;
* validation recommendation.

### Operating Rules

* Inputs and versions must be recorded.
* Contradictions must remain visible.
* Unsupported consensus is prohibited.
* Synthesis begins as `Draft` or `In Review`.
* Generated synthesis cannot automatically become an accepted rule.

---

## 44. Infer

### Definition

Derive a provisional relationship, mechanism, or engineering implication not directly stated in source evidence.

### Required Labels

* Inferred
* Model Generated or Human Inferred
* Unverified or In Review

### Required Metadata

* inputs;
* reasoning method;
* assumptions;
* confidence;
* evidence gaps;
* falsification or validation path.

Inference may support hypothesis formation but cannot overwrite observed or curated knowledge.

---

## 45. Critique

### Definition

Identify weaknesses, contradictions, missing conditions, unsupported transitions, transferability problems, or unsafe engineering interpretation.

Critique must assess:

* claim precision;
* mechanism completeness;
* evidence directness;
* context match;
* contradiction;
* model assumptions;
* overgeneralization;
* missing validation;
* possible failure modes.

A critique should produce actionable review issues, not only negative prose.

---

## 46. Recommend

### Definition

Propose how governed knowledge may inform an engineering decision.

### Recommendation Must Expose

* engineering objective;
* proposed action or strategy;
* supporting knowledge objects and versions;
* biological mechanism;
* evidence quality;
* confidence;
* context match;
* expected benefit;
* trade-offs;
* risks;
* alternatives;
* validation requirement;
* approval requirement.

Recommendations are proposals, not approved actions.

---

## 47. Reuse

### Definition

Reference an existing governed knowledge object in another project, cycle, engineering decision, report, or analysis.

### Reuse Must Preserve

* object identity;
* version;
* original context;
* source;
* evidence;
* limitations;
* reuse timestamp;
* target object;
* adapting actor;
* any context transformation.

### Context Mismatch

When source and target context differ, the system must show a transferability warning.

---

## 48. Curate

### Definition

Human-governed correction, enrichment, classification, or validation of knowledge.

Permitted curation actions include:

* correct entity mapping;
* add missing condition;
* classify evidence;
* link contradiction;
* refine claim;
* merge duplicates;
* split overgeneralized rule;
* request review;
* accept or reject;
* deprecate;
* create replacement version.

Every consequential curation action must create an audit event.

---

## 49. Learn

### Definition

Convert new DBTL observations into candidate knowledge updates.

Canonical flow:

```text
Experimental Result
→ Observation Object
→ Compare with Prediction
→ Explain Deviation
→ Candidate Claim
→ Evidence Review
→ Knowledge Update
→ New Version
```

Learning must not mean automatic self-modification without review.

---

# Part VII — User Operating Modes

## 50. PI Mode

Primary questions:

* What knowledge materially affects the current project decision?
* Which recommendation is well supported?
* Where is uncertainty or contradiction?
* Which knowledge is reusable across projects?
* Which claims require review?

PI interactions prioritize:

* decision relevance;
* evidence quality;
* risk;
* unresolved conflict;
* approval or review needs;
* project impact.

The PI should not be required to navigate raw literature before understanding the engineering implication.

---

## 51. Dry-Lab Mode

Primary questions:

* What structured knowledge can constrain or inform modeling?
* What assumptions are present?
* Which values are observed, inferred, or simulated?
* What model, parameters, and evidence produced the result?
* What knowledge gaps affect prediction reliability?

Dry-lab interactions prioritize:

* machine-readable objects;
* computational provenance;
* condition matching;
* parameter traceability;
* version comparison;
* export or API reuse where permitted.

---

## 52. Wet-Lab Mode

Primary questions:

* Which biological mechanism supports this intervention?
* Is the action proposed or approved?
* What phenotype and trade-off should be monitored?
* What validation assay is required?
* What failure pattern has been observed previously?

Wet-lab interactions prioritize:

* actionable biological meaning;
* approved versus proposed distinction;
* strain and condition specificity;
* validation criteria;
* safety and governance;
* practical failure modes.

Page 03 must not present unapproved engineering knowledge as a wet-lab instruction.

---

## 53. Knowledge Curator Mode

Primary questions:

* What new knowledge needs review?
* Which extraction is ambiguous?
* Which evidence is duplicated or conflicting?
* Which rule requires versioning?
* Which knowledge should be deprecated?

Curator interactions prioritize:

* review queue;
* entity resolution;
* claim editing;
* evidence linking;
* contradiction management;
* version creation;
* auditability.

---

## 54. Engineering Runtime Mode

Page 02 or an AI runtime may request:

```yaml
request_id:
project_id:
cycle_id:
engineering_goal:
organism:
strain:
conditions:
selected_objects:
question:
required_evidence_quality:
include_conflicting_evidence:
version_policy:
```

Page 03 returns structured support objects, not unrestricted prose.

Recommended response:

```yaml
knowledge_bundle_id:
request_context:
claims:
mechanisms:
engineering_rules:
design_patterns:
failure_patterns:
supporting_evidence:
conflicting_evidence:
knowledge_gaps:
confidence:
limitations:
recommended_validation:
object_versions:
provenance:
```

---

# Part VIII — Context and Navigation Principles

## 55. Persistent Context

Page 03 must preserve, when entered from Page 02:

```text
Project
/ DBTL Cycle
/ Workspace Stage
/ Selected Engineering Object
/ Knowledge Query
/ Knowledge Object
/ Version
```

Opening knowledge detail must not destroy the originating engineering context.

---

## 56. Entry Points

Valid entry points include:

* primary navigation;
* global search;
* Page 02 Evidence Drawer;
* claim, mechanism, or rule link;
* project decision;
* review queue;
* contradiction alert;
* knowledge update notification;
* provenance record;
* deep link.

Each entry point must define the return path.

---

## 57. Exit and Handoff

Valid handoffs include:

* reference knowledge in Page 02;
* add knowledge to candidate design evidence;
* create a validation requirement;
* request curator review;
* open provenance in Page 04;
* create a new knowledge draft;
* compare knowledge versions;
* export a governed knowledge bundle.

A handoff must preserve object and version identity.

---

## 58. Selection Principles

* Single selection drives the Inspector.
* Multi-selection enables comparison.
* Selection must remain visible.
* Opening evidence must preserve the selected knowledge object.
* Changing selection must not reset unrelated filters.
* Selection state should be restorable where meaningful.
* Deleted, superseded, or inaccessible objects require explicit recovery states.

---

## 59. Deep-Linking Principles

Shareable URLs should encode meaningful state:

```text
/projects/:projectId/cycles/:cycleId/knowledge
/projects/:projectId/cycles/:cycleId/knowledge?object=:knowledgeId
/projects/:projectId/cycles/:cycleId/knowledge?object=:knowledgeId&version=:versionId
/knowledge/claims/:claimId
/knowledge/rules/:ruleId
/knowledge/patterns/:patternId
```

Permissions and project scope must still be enforced.

---

# Part IX — AI Operating Principles

## 60. AI Role

AI may:

* retrieve;
* extract;
* normalize;
* classify;
* compare;
* summarize;
* synthesize;
* identify contradiction;
* generate hypotheses;
* propose engineering implications;
* identify evidence gaps;
* draft knowledge objects;
* recommend validation questions.

AI must not:

* invent evidence;
* fabricate citations;
* hide contradictory sources;
* silently validate its own output;
* approve wet-lab action;
* overwrite human-curated knowledge;
* collapse uncertainty into unsupported certainty;
* promote a draft into an accepted rule without governance.

---

## 61. AI Output States

AI-generated output progresses through:

```text
Streaming or Processing
→ Generated Draft
→ Structured Draft
→ Human Review
→ Changes Requested or Validated
→ Accepted for Reuse
```

Partial streaming output is not a committed knowledge object.

---

## 62. AI Traceability

Every consequential AI output must expose, where available:

```yaml
provider:
model:
model_version:
prompt_or_task_reference:
tools_used:
retrieved_object_ids:
retrieved_versions:
parameters:
generation_timestamp:
generated_by:
review_status:
```

Sensitive prompt or system information may be protected, but sufficient reproducibility metadata must remain available to authorized users.

---

## 63. AI Self-Critique

Before a generated synthesis or recommendation is presented as review-ready, the system should evaluate:

* unsupported claims;
* missing citations;
* contradiction omission;
* condition mismatch;
* overgeneralization;
* weak transferability;
* missing validation;
* uncertain entity resolution;
* stale evidence;
* duplicated evidence.

Self-critique assists review but does not replace human review.

---

# Part X — Knowledge Evolution

## 64. Evolution Triggers

Knowledge review may be triggered by:

* new paper;
* new dataset;
* new DDR;
* new experimental result;
* new simulation result;
* failed experiment;
* unexpected phenotype;
* contradictory evidence;
* source correction;
* publication retraction;
* model update;
* curator correction;
* user-reported unsupported claim;
* repeated successful reuse;
* repeated failed transfer.

---

## 65. Evolution Effects

A trigger may produce:

* evidence addition;
* contradiction addition;
* confidence update;
* condition refinement;
* mechanism refinement;
* rule split;
* rule merge;
* new design pattern;
* new failure pattern;
* deprecation;
* supersession;
* review request;
* runtime warning.

---

## 66. No Silent Mutation

Any update that changes scientific meaning must:

1. create a new version;
2. record the previous version;
3. state the update reason;
4. identify changed evidence;
5. identify the actor;
6. state review status;
7. update downstream compatibility;
8. preserve historical references.

Existing engineering decisions should continue referencing the version used at decision time unless explicitly migrated.

---

## 67. Downstream Impact

When a knowledge object changes, the system should identify affected:

* projects;
* DBTL cycles;
* engineering decisions;
* candidate designs;
* reports;
* simulations;
* validation plans;
* accepted recommendations.

A change must not silently rewrite historical decisions.

The system may notify owners that newer knowledge exists.

---

## 68. Knowledge Retirement

Retired knowledge remains available for:

* historical inspection;
* audit;
* reproducibility;
* decision reconstruction;
* comparison;
* learning from failure.

Retired knowledge must not appear as the default current recommendation.

---

# Part XI — DBTL Integration

## 69. Design Stage Support

Page 03 may provide:

* biological mechanisms;
* bottleneck-related evidence;
* engineering rules;
* design patterns;
* candidate interventions;
* known trade-offs;
* failure patterns;
* comparable prior cases.

It must expose context match and limitations.

---

## 70. Build Stage Support

Page 03 may provide:

* construct-related knowledge;
* promoter or RBS rules;
* genotype dependencies;
* engineering action definitions;
* protocol references;
* implementation constraints;
* known toxicity or burden patterns.

It does not replace an approved build plan.

---

## 71. Test Stage Support

Page 03 may provide:

* phenotype expectations;
* validation criteria;
* measurement recommendations;
* assay knowledge;
* known confounders;
* failure signatures;
* expected trade-offs.

Test recommendations remain versioned and reviewable.

---

## 72. Learn Stage Support

Page 03 receives:

* observed results;
* prediction deviations;
* failed outcomes;
* successful transfer;
* new mechanism evidence;
* unexpected interactions;
* revised assumptions.

It transforms these into candidate knowledge updates through governance.

---

## 73. Closed-Loop Operating Model

```text
Knowledge
→ Engineering Proposal
→ Human Review
→ Approved Experiment
→ Observation
→ Comparison
→ Learning Candidate
→ Knowledge Review
→ New Knowledge Version
```

This closed loop is fundamental to the product.

---

# Part XII — Failure, Conflict, and Recovery

## 74. Source Failure

When a source cannot be accessed:

* preserve the source reference;
* label access state;
* distinguish unavailable full text from absent evidence;
* do not fabricate extracted content;
* allow retry or alternative source;
* retain prior validated knowledge unless invalidated.

---

## 75. Extraction Failure

When extraction fails:

* preserve imported source;
* show which sections or objects failed;
* do not create false structured objects;
* allow manual curation;
* allow safe retry;
* record extraction version and error.

---

## 76. Entity Ambiguity

When an entity cannot be uniquely resolved:

* preserve candidate mappings;
* show ambiguity;
* prevent silent relationship creation;
* allow curator resolution;
* retain original source term.

---

## 77. Contradictory Evidence

When evidence conflicts:

* show all material positions;
* preserve source context;
* avoid forced consensus;
* update claim status to `Conflicting` where appropriate;
* reduce or qualify confidence;
* identify discriminating experiments or conditions;
* allow review.

---

## 78. Stale Knowledge

Knowledge may be stale when:

* newer evidence exists;
* a model version is obsolete;
* source validity changed;
* review interval expired;
* downstream context changed;
* a replacement object exists.

Stale knowledge remains inspectable but must display a warning before reuse.

---

## 79. Permission Failure

When the user lacks permission:

* preserve navigation context;
* explain which content or action is restricted;
* do not expose protected metadata;
* provide an access-request path where available;
* do not imply the object does not exist if only access is restricted.

---

## 80. Update Conflict

When two users modify the same knowledge version:

* preserve both drafts;
* prevent silent last-write-wins behavior;
* show field-level differences;
* require merge or explicit selection;
* record the resolution.

---

## 81. Backend Unavailability

When backend services are unavailable:

* preserve current visible context;
* show cached status and timestamp;
* prevent false impression of freshness;
* disable unsafe mutations;
* preserve unsaved user input;
* allow safe retry;
* show what remains available.

---

# Part XIII — Governance and Permissions

## 82. Role-Based Capabilities

Illustrative capability model:

| Capability                            |  Viewer | Researcher |     Curator |    Reviewer |    PI/Admin |
| ------------------------------------- | ------: | ---------: | ----------: | ----------: | ----------: |
| View accepted knowledge               |     Yes |        Yes |         Yes |         Yes |         Yes |
| View conflicting/deprecated knowledge | Limited |        Yes |         Yes |         Yes |         Yes |
| Create draft                          |      No |        Yes |         Yes |         Yes |         Yes |
| Edit draft                            |      No |        Own |         Yes |         Yes |         Yes |
| Link evidence                         |      No |        Yes |         Yes |         Yes |         Yes |
| Request review                        |      No |        Yes |         Yes |         Yes |         Yes |
| Validate knowledge                    |      No |         No | Conditional |         Yes |         Yes |
| Deprecate knowledge                   |      No |         No |     Request | Conditional |         Yes |
| Override governance state             |      No |         No |          No |          No | With reason |

The actual permission model must follow the backend source of truth.

---

## 83. Review Principles

* Review is version-specific.
* Reviewer identity and role are visible.
* Review rationale is required for rejection, limitation, override, and deprecation.
* Self-review restrictions must follow project governance.
* AI-generated drafts require human review before governed reuse.
* Review history is immutable.

---

## 84. Override Principles

Override is exceptional.

An override must record:

* actor;
* role;
* affected object and version;
* original state;
* override state;
* reason;
* risks accepted;
* downstream impact;
* timestamp.

Override must not erase the original review.

---

# Part XIV — Persistent Workspace Principles

## 85. State Persistence

The following may persist when relevant:

* current project;
* cycle;
* knowledge scope;
* selected object;
* selected version;
* search query;
* filters;
* comparison set;
* inspector state;
* evidence drawer state;
* panel width;
* density mode;
* draft content;
* return context.

Persistence rules must distinguish:

* shareable state;
* user preference;
* temporary UI state;
* unsaved draft state;
* backend scientific state.

---

## 86. Restoration

When returning to Page 03, the system should restore:

* meaningful context;
* selected object if still accessible;
* active comparison;
* unsaved draft when safe;
* review queue position where appropriate.

If restoration is impossible, the system must explain why and recover to the nearest valid context.

---

# Part XV — Operational Metrics

## 87. Knowledge Production Metrics

Useful metrics may include:

* sources acquired;
* claims extracted;
* knowledge objects structured;
* objects awaiting review;
* objects accepted;
* contradictions identified;
* duplicate evidence resolved;
* rules reused;
* knowledge updates from experiments;
* deprecated objects;
* time from source acquisition to governed reuse.

These metrics must not reward low-quality automatic volume.

---

## 88. Scientific Quality Metrics

* provenance completeness;
* context completeness;
* evidence coverage;
* contradiction visibility;
* reviewer agreement;
* transfer success;
* validation success;
* unsupported-claim rate;
* stale-knowledge rate;
* erroneous entity-resolution rate.

---

## 89. Engineering Utility Metrics

* proportion of engineering decisions with governed knowledge support;
* reuse across projects or cycles;
* reduction in repeated manual literature work;
* recommendation acceptance after review;
* successful validation of knowledge-supported designs;
* identification of failure patterns before wet-lab execution;
* number of knowledge gaps converted into explicit validation tasks.

Metrics must not be treated as proof of scientific correctness by themselves.

---

# Part XVI — Priority Model

## 90. P0 — Mission-Critical

Page 03 cannot fulfill its mission without:

* structured knowledge objects;
* source and provenance;
* claim–evidence relationships;
* supporting and conflicting evidence;
* organism, strain, and context;
* knowledge status and version;
* retrieval and inspection;
* context-preserving entry from Page 02;
* governed reuse;
* explicit observed/predicted/inferred distinctions;
* loading, empty, partial, stale, conflict, and error states.

---

## 91. P1 — Complete Primary Workflow

* knowledge comparison;
* curator review;
* knowledge versioning;
* evidence quality and confidence;
* engineering rule and pattern objects;
* reuse into Page 02;
* knowledge update from experimental results;
* role-aware actions;
* deep links;
* audit events.

---

## 92. P2 — Important Secondary Capability

* advanced network exploration;
* automated contradiction discovery;
* impact analysis across projects;
* reusable knowledge bundles;
* rich export;
* curator analytics;
* model-assisted rule synthesis;
* transferability analysis.

---

## 93. P3 — Enhancement

* advanced spatial visualization;
* speculative relationship exploration;
* custom visual layout preferences;
* nonessential animation;
* decorative biological imagery;
* secondary recommendation conveniences.

P3 must never delay P0–P2 acceptance.

---

# Part XVII — Operating Anti-Patterns

## 94. Prohibited Product Patterns

Page 03 must not become:

* a search bar with paper cards;
* a full-page chatbot;
* a generic KPI dashboard;
* an unbounded knowledge graph hairball;
* a PDF reader with AI summary;
* a collection of disconnected tabs;
* a literature recommendation feed;
* an autonomous wet-lab instruction generator;
* a hidden RAG pipeline with no provenance;
* a confidence-score leaderboard.

---

## 95. Prohibited Scientific Behaviors

* presenting inference as observation;
* hiding contradictory findings;
* applying evidence across strains without warning;
* double-counting duplicate datasets;
* treating publication prestige as evidence strength;
* generating unsupported exact confidence values;
* silently changing accepted rules;
* deleting deprecated knowledge history;
* using “no evidence” as “evidence of no effect”;
* treating model output as experimental validation.

---

## 96. Prohibited Implementation Behaviors

* inventing backend knowledge objects;
* using mock scientific data without visible labeling;
* bypassing adapters and parsing inconsistent payloads in components;
* creating local evidence status vocabularies;
* changing global object semantics inside Page 03;
* storing backend scientific truth only in frontend state;
* using graph rendering as the only accessible representation;
* allowing generated summaries to become accepted objects automatically;
* rewriting Page 02 decisions when knowledge versions change.

---

# Part XVIII — Operating Decision Rules

## 97. When Requirements Conflict

Apply this precedence:

1. Scientific truth and safety
2. Real backend capability and schema
3. Page Design Contract
4. Approved Page 03 Product and Content Specs
5. This Operating Principles document
6. Approved UI and Interaction Specs
7. Approved visual reference
8. Implementation convenience

Any unresolved conflict must be recorded and returned as `BLOCKED`.

---

## 98. When Knowledge Is Incomplete

The system should:

* preserve what is known;
* state what is missing;
* avoid fabricated completion;
* show whether the gap blocks reuse;
* suggest a scientifically valid next action;
* allow review or data acquisition.

---

## 99. When Knowledge Is Contradictory

The system should:

* preserve disagreement;
* compare biological contexts;
* identify possible causes;
* avoid forced synthesis;
* narrow the claim if justified;
* propose discriminating validation;
* require review before high-consequence reuse.

---

## 100. When Knowledge Is Applicable but Weak

The system may permit exploratory reuse when:

* the weak status is visible;
* the evidence gap is explicit;
* the recommendation remains proposed;
* validation is required;
* governance permits exploratory use.

---

## 101. When Knowledge Changes

The system must:

* create a new version;
* preserve historical references;
* identify downstream impact;
* notify affected owners where appropriate;
* avoid silently updating completed decisions;
* require re-review when scientific meaning materially changes.

---

# Part XIX — Completion and Stop Conditions

## 102. Operating Specification Completion Criteria

This operating specification is complete only when it defines:

* system identity;
* invariants;
* knowledge objects;
* lifecycle;
* evidence rules;
* operations;
* user roles;
* context behavior;
* AI behavior;
* knowledge evolution;
* DBTL integration;
* failure and recovery;
* governance;
* persistence;
* metrics;
* priorities;
* anti-patterns;
* conflict resolution;
* stop conditions.

---

## 103. Implementation Readiness Gate

Implementation may begin only when:

```text
Product Spec approved
AND Content Spec approved
AND UI Spec approved
AND Operating Principles approved
AND Interaction and Technical mappings are consistent
AND backend objects and schemas are inspected
AND P0 workflow has no unresolved contradiction
AND acceptance criteria exist
```

---

## 104. Runtime Stop Condition

The implementation agent must stop when:

```text
Approved Page 03 scope implemented
AND required tests pass
AND scientific states and provenance are truthful
AND Page 02 handoff works
AND knowledge review and reuse rules work
AND error and recovery states work
AND no blocking mock, placeholder, or unsupported claim remains
AND acceptance and regression gates pass
AND changed files, exceptions, risks, and deferred work are reported
```

The agent must not continue unrelated refactoring, visual polishing, or P3 expansion after this condition is satisfied.

---

# Part XX — Scientific Knowledge Operating Constitution

The following constitution governs all Page 03 behavior:

```text
Scientific knowledge shall always originate from identifiable sources.

Scientific knowledge shall always preserve provenance.

Observation shall never be overwritten by inference.

Prediction shall never be presented as experimental validation.

Supporting evidence shall never erase contradictory evidence.

Scientific knowledge shall always preserve biological and experimental context.

Knowledge without provenance shall not participate in governed engineering recommendations.

Every consequential claim shall expose evidence, assumptions, limitations, confidence, and version.

Every engineering rule shall remain traceable to scientific claims and evidence.

Every model-generated synthesis shall remain distinguishable from curated or observed knowledge.

Every accepted knowledge object shall remain reviewable and versioned.

Every material update shall preserve historical knowledge rather than silently overwrite it.

Every completed DBTL cycle shall be capable of contributing new evidence and candidate knowledge.

Knowledge evolution shall remain human governed.

The DBTL Engineering Runtime may consume governed knowledge but shall not silently redefine it.

Conflicting, limited, stale, deprecated, and unavailable knowledge shall remain explicitly visible.

Scientific usefulness shall be judged by correctness, traceability, context, reusability, and engineering value—not by information volume.

Page 03 shall operate as a persistent Scientific Knowledge Production System, not as a literature archive, generic search engine, chatbot, or autonomous decision maker.
```

---

# Part XXI — Final Operating Summary

Page 03 operates according to the following canonical loop:

```text
Acquire scientific sources
→ Extract candidate knowledge
→ Normalize scientific entities
→ Structure claims and mechanisms
→ Link evidence and contradictions
→ Evaluate quality and applicability
→ Validate through governance
→ Publish versioned reusable knowledge
→ Support DBTL engineering decisions
→ Observe experimental outcomes
→ Convert outcomes into candidate updates
→ Review, version, supersede, or retire knowledge
```

The page succeeds only when users can move from:

```text
Scientific Question
→ Biological Mechanism
→ Evidence
→ Contradiction
→ Engineering Rule
→ Reusable Action
→ Validation Requirement
→ Traceable DBTL Learning
```

without losing project context, scientific uncertainty, provenance, version identity, or human governance.
