# Synthetic Biology DBTL Engineering OS

# Page 04 — Trust & Provenance Center

# 05_Acceptance_Spec.md

> **Document type**: Page-specific Acceptance, Verification and Release Specification
> **Page**: Page 04 — Trust & Provenance Center
> **Product role**: Trust, Governance & Provenance Control Plane
> **Status**: Normative / Release-Binding
> **Parent contract**: Page Design Contract v1.2.0
> **Parent architecture**: Synthetic Biology DBTL Engineering OS Frontend Architecture v1.2
> **Parent product spec**: Page 04 `01_Product_Spec.md`
> **Parent UI spec**: Page 04 `02_UI_Spec.md`
> **Parent operating principles**: Page 04 `03_Operating_Principles.md`
> **Parent technical spec**: Page 04 `04_Technical_Spec.md`
> **Default UI language**: English
> **Specification language**: English, with implementation notes permitted in Chinese
> **Version**: 1.0.0
> **Last updated**: 2026-07-23

---

## Specification Header

```yaml
page_id: page-04
page_name: Trust & Provenance Center
spec_type: Acceptance Spec
version: 1.0.0
status: Approved
product_positioning: Trust, Governance & Provenance Control Plane
owners:
  - Product Owner
  - Scientific Product Lead
  - Governance Owner
  - Frontend Architect
  - QA and Release Owner
reviewers:
  - Principal Investigator
  - Synthetic Biology Reviewer
  - Dry-Lab Reviewer
  - Wet-Lab Reviewer
  - Governance Reviewer
  - Security and Privacy Reviewer
  - Accessibility Reviewer
  - Performance Reviewer
parent_contract: Page Design Contract v1.2.0
parent_product_spec: Page04/01_Product_Spec.md
parent_ui_spec: Page04/02_UI_Spec.md
parent_operating_principles: Page04/03_Operating_Principles.md
parent_technical_spec: Page04/04_Technical_Spec.md
release_decisions:
  - READY
  - NEEDS_REVISION
  - REJECTED
approved_exceptions: []
open_questions: []
```

---

# Part I — Acceptance Mission

## 1. Purpose

This document defines how Page 04 is verified and whether it may be released.

It converts the Product, UI, Operating and Technical Specifications into:

* testable acceptance criteria;
* required evidence;
* release gates;
* rejection conditions;
* regression checks;
* completion-report requirements.

Page 04 must not be accepted because it looks complete.

It is accepted only when the implementation proves that users can safely inspect, govern and reconstruct consequential scientific and system state.

---

## 2. Acceptance Principle

The canonical acceptance question is:

> **Can an authorized user determine what happened, what exact object and version were affected, what evidence and provenance support the state, who had authority, what decision was made, what was executed, what was observed, and what evaluation or corrective action followed?**

---

## 3. Release Decisions

Only the following release decisions are valid.

### READY

All applicable gates pass, all critical failures equal zero, required verification has been run, and remaining limitations are explicitly non-blocking.

### NEEDS_REVISION

The implementation is directionally correct, but one or more correctable requirements remain incomplete, unverified or inconsistent.

### REJECTED

A system invariant, scientific-trust boundary, governance boundary, permission boundary, history-preservation rule or protected repository rule is violated.

Terms such as “mostly ready”, “substantially complete” or “good enough” are not valid release decisions.

---

# Part II — Acceptance Evidence Standard

## 4. Evidence Required for PASS

A criterion may be marked `PASS` only when supported by one or more of:

* executable automated test;
* passing repository-native command;
* runtime interaction verification;
* screenshot or recording at defined viewport;
* API or schema evidence;
* source-code reference;
* accessibility-tool output;
* performance measurement;
* backend audit record;
* documented manual test with actual result.

A claim without evidence must not be marked `PASS`.

---

## 5. Other Result States

Permitted criterion states:

* `PASS`
* `FAIL`
* `PARTIAL`
* `BLOCKED`
* `NOT APPLICABLE`
* `NOT AVAILABLE`
* `NOT RUN`

Definitions:

### PARTIAL

Some required behavior works, but material conditions or states remain incomplete.

### BLOCKED

Verification or implementation cannot proceed because of an identified external or contractual blocker.

### NOT APPLICABLE

The criterion genuinely does not apply to the approved implementation scope.

### NOT AVAILABLE

The repository or environment does not contain the necessary capability or tooling.

### NOT RUN

The test was possible but was not executed.

`NOT AVAILABLE` and `NOT RUN` are not equivalent to `PASS`.

---

## 6. No Inferred Acceptance

The following are prohibited:

* marking accessibility as passed because semantic HTML appears to be used;
* marking performance as passed from bundle size alone;
* marking permissions as passed because buttons are hidden;
* marking audit as passed because a timeline is visible;
* marking provenance as complete because a graph renders;
* marking approval as complete because a local state changes;
* marking evaluation as passed because an aggregate score is high;
* marking responsive behavior as passed from one desktop screenshot.

---

# Part III — Gate Structure

## 7. Page 04 Release Gates

Page 04 must pass:

```text
Gate 0 — Readiness
Gate 1 — Product and Scientific Semantics
Gate 2 — Governance and Human Authority
Gate 3 — Memory, Audit and Provenance
Gate 4 — Evaluation and Corrective Action
Gate 5 — UI, Interaction and Runtime States
Gate 6 — Technical Architecture and Backend Truthfulness
Gate 7 — Security, Privacy and Permissions
Gate 8 — Accessibility, Responsive and Performance
Gate 9 — Regression and Release
```

A lower gate failure may block dependent higher gates.

---

# Part IV — Gate 0: Readiness

## 8. Gate 0 Objective

Confirm that implementation and verification can begin without an unresolved foundational conflict.

---

## 9. Gate 0 Criteria

| ID     | Criterion                                                                                    | Acceptance evidence                        |
| ------ | -------------------------------------------------------------------------------------------- | ------------------------------------------ |
| G0-001 | Page 04 product role is defined as Trust, Governance & Provenance Control Plane              | Product spec and implemented page identity |
| G0-002 | Page boundary against Page 01, Page 02 and Page 03 is explicit                               | Cross-page responsibility matrix           |
| G0-003 | Repository root and real target frontend are confirmed                                       | Repository audit                           |
| G0-004 | Current route, shell, design tokens and state architecture are identified                    | File-path evidence                         |
| G0-005 | Backend governance capabilities are classified as supported, partial, unavailable or unknown | Capability matrix                          |
| G0-006 | Protected repository surfaces are identified                                                 | Protected-surface list                     |
| G0-007 | Existing uncommitted user changes are inspected                                              | Git status evidence                        |
| G0-008 | No unresolved contract conflict requires human decision                                      | Conflict matrix                            |
| G0-009 | Acceptance scenarios and test strategy are mapped to repository tooling                      | Test matrix                                |
| G0-010 | Missing backend capabilities have explicit safe degradation behavior                         | Capability-to-UI map                       |

### Gate 0 PASS condition

All applicable criteria pass and no Conditional Audit Gate remains unresolved.

---

# Part V — Gate 1: Product and Scientific Semantics

## 10. Gate 1 Objective

Verify that Page 04 is a governance control plane rather than a generic admin dashboard, activity log or analytics page.

---

## 11. Product Acceptance Criteria

| ID       | Criterion                                                                                                         |
| -------- | ----------------------------------------------------------------------------------------------------------------- |
| PROD-001 | A first-time user can identify the page as the system’s trust, governance and provenance center within 30 seconds |
| PROD-002 | The page presents consequential governance work, not generic notifications                                        |
| PROD-003 | Users can identify the selected project, cycle, object and version                                                |
| PROD-004 | Users can identify the current governance question                                                                |
| PROD-005 | Users can distinguish current, historical, stale, superseded and restricted state                                 |
| PROD-006 | Users can understand the next required governance action                                                          |
| PROD-007 | Page 04 does not replace Page 01 project command, Page 02 engineering runtime or Page 03 knowledge production     |
| PROD-008 | The page supports direct inspection of attention, approvals, provenance, memory, audit and evaluation             |
| PROD-009 | Cross-page entry preserves source context                                                                         |
| PROD-010 | Returning to the source page does not silently switch object version                                              |

---

## 12. Scientific-State Acceptance Criteria

The implementation must distinguish, where applicable:

* Observed;
* Literature-reported;
* Predicted;
* Inferred;
* Proposed;
* Reviewed;
* Approved for a defined transition;
* Executed;
* Evaluated;
* Contradicted;
* Stale;
* Superseded;
* Unknown;
* Unavailable.

| ID      | Criterion                                                                    |
| ------- | ---------------------------------------------------------------------------- |
| SCI-001 | Predicted state is not displayed as observed                                 |
| SCI-002 | Proposed state is not displayed as approved                                  |
| SCI-003 | Approved state is not displayed as executed                                  |
| SCI-004 | Executed state is not displayed as successful                                |
| SCI-005 | Evaluation result is not displayed as scientific truth without context       |
| SCI-006 | Unknown and unavailable are explicitly displayed                             |
| SCI-007 | Scientific state and governance state are separate                           |
| SCI-008 | Evidence quality, confidence, approval and reproducibility remain separate   |
| SCI-009 | A global trust label remains expandable to its dimensions                    |
| SCI-010 | A critical scientific failure cannot be hidden by a positive aggregate label |

---

## 13. Gate 1 Mandatory Scenarios

### Scenario 1A — Predicted but approved for validation

Expected:

```text
Scientific state: Predicted
Governance state: Approved for validation
Execution state: Not executed
```

The UI must not reduce this to “Approved”.

### Scenario 1B — Executed but not evaluated

Expected:

```text
Execution state: Executed
Evaluation state: Not evaluated
```

The UI must not display success.

### Scenario 1C — Unknown provenance

Expected:

* provenance limitation visible;
* trust state remains partial or unknown;
* no fabricated source or actor.

---

# Part VI — Gate 2: Governance and Human Authority

## 14. Gate 2 Objective

Verify that consequential actions are human-governed, version-bound, permission-aware and attributable.

---

## 15. Approval Request Acceptance

| ID      | Criterion                                                               |
| ------- | ----------------------------------------------------------------------- |
| GOV-001 | Approval request identifies exact object ID                             |
| GOV-002 | Approval request identifies exact object version                        |
| GOV-003 | Requested transition is explicit                                        |
| GOV-004 | Requester is attributable                                               |
| GOV-005 | Required reviewer role is visible                                       |
| GOV-006 | Scientific purpose and downstream effect are visible                    |
| GOV-007 | Approval package completeness is visible                                |
| GOV-008 | Supporting and conflicting evidence are available where applicable      |
| GOV-009 | Assumptions, risks, limitations and validation requirements are visible |
| GOV-010 | Incomplete package is not represented as complete                       |

---

## 16. Reviewer Authority Acceptance

| ID       | Criterion                                                                     |
| -------- | ----------------------------------------------------------------------------- |
| AUTH-001 | Reviewer authority originates from backend or approved policy state           |
| AUTH-002 | Unauthorized users cannot execute approval actions                            |
| AUTH-003 | Read-only and conditional authority states are visible                        |
| AUTH-004 | Permission-service failure does not grant authority                           |
| AUTH-005 | Frontend role labels do not independently grant authority                     |
| AUTH-006 | Restricted approval content does not leak through disabled controls or errors |

---

## 17. Approval Mutation Acceptance

| ID      | Criterion                                                                   |
| ------- | --------------------------------------------------------------------------- |
| MUT-001 | Consequential action targets exact object and version                       |
| MUT-002 | Submission includes reason where required                                   |
| MUT-003 | Duplicate submission is prevented                                           |
| MUT-004 | Pending state is visible                                                    |
| MUT-005 | Final success appears only after authoritative backend confirmation         |
| MUT-006 | Timeout does not automatically appear as failure or success                 |
| MUT-007 | Idempotency or safe duplicate reconciliation is implemented where supported |
| MUT-008 | Resulting state is refetched or returned by backend                         |
| MUT-009 | Audit event or decision record is linked where required                     |
| MUT-010 | User notes are preserved after failure or conflict                          |

---

## 18. Approval Lifecycle Acceptance

The following transitions must remain semantically distinct:

```text
Draft
→ Submitted
→ Pending Reviewer
→ In Review
→ Changes Requested
→ Resubmitted
→ Approved | Rejected
→ Expired | Revoked | Superseded
```

| ID       | Criterion                                                                      |
| -------- | ------------------------------------------------------------------------------ |
| LIFE-001 | Unknown backend states are not silently mapped to approved states              |
| LIFE-002 | Rejection preserves the request and rationale                                  |
| LIFE-003 | Request Changes identifies requested changes and target version                |
| LIFE-004 | Conditional approval displays conditions and validity                          |
| LIFE-005 | Override remains visibly distinct from ordinary approval                       |
| LIFE-006 | Revocation preserves original approval history                                 |
| LIFE-007 | Expired approval is not displayed as current authorization                     |
| LIFE-008 | Object version change invalidates or re-evaluates approval according to policy |

---

## 19. Gate 2 Mandatory Scenarios

### Scenario 2A — Authorized approval

Expected:

* authority confirmed;
* exact version shown;
* action submitted once;
* backend confirmation received;
* audit event linked.

### Scenario 2B — Unauthorized approval

Expected:

* action unavailable;
* protected data safe;
* no local bypass;
* reason displayed safely.

### Scenario 2C — Object changes during review

Expected:

* submission blocked;
* current and reviewed versions shown;
* notes preserved;
* re-review required.

### Scenario 2D — Override

Expected:

* original decision visible;
* accepted risk visible;
* override scope and validity visible;
* authorized actor recorded.

### Scenario 2E — Mutation timeout

Expected:

* duplicate submission prevented;
* authoritative state refetched;
* unresolved state displayed if confirmation unavailable.

---

# Part VII — Gate 3: Memory, Audit and Provenance

## 20. Gate 3 Objective

Verify that persistent memory, historical activity and object lineage are inspectable without rewriting or fabricating history.

---

## 21. Memory Acceptance

| ID      | Criterion                                                                     |
| ------- | ----------------------------------------------------------------------------- |
| MEM-001 | Memory class is explicit                                                      |
| MEM-002 | Memory source and source version are visible                                  |
| MEM-003 | Memory scope is explicit                                                      |
| MEM-004 | Freshness is not based only on creation time                                  |
| MEM-005 | Material memory use is inspectable                                            |
| MEM-006 | Memory influence on consequential output is traceable                         |
| MEM-007 | Conflicting memories remain separate                                          |
| MEM-008 | Memory correction creates a new version                                       |
| MEM-009 | Historical outputs retain the memory version originally used                  |
| MEM-010 | Retired memory is excluded from new use by default                            |
| MEM-011 | Superseded memory identifies replacement where applicable                     |
| MEM-012 | Active objects affected by stale or superseded memory are discoverable        |
| MEM-013 | Sensitive memory is permission-protected                                      |
| MEM-014 | Sensitive memory does not leak through URL, cache, logs, analytics or exports |
| MEM-015 | Model-generated memory remains labeled as model-generated                     |

---

## 22. Audit Acceptance

| ID      | Criterion                                                        |
| ------- | ---------------------------------------------------------------- |
| AUD-001 | Consequential state changes create attributable audit events     |
| AUD-002 | Actor type distinguishes human, agent, system and external tool  |
| AUD-003 | Event records exact target and version                           |
| AUD-004 | Previous and new state are available where applicable            |
| AUD-005 | Reason and result are preserved where required                   |
| AUD-006 | Audit history is read-only by default                            |
| AUD-007 | Correction creates a new linked event                            |
| AUD-008 | Retry and duplicate events are distinguishable                   |
| AUD-009 | Event time and ingestion time can be distinguished when relevant |
| AUD-010 | Legacy missing fields are shown as unknown, not fabricated       |
| AUD-011 | Audit history supports pagination and filtering at scale         |
| AUD-012 | Raw payload is secondary, permission-gated and safely rendered   |
| AUD-013 | Audit history can reconstruct consequential object state changes |
| AUD-014 | Chronological proximity is not presented as causal proof         |

---

## 23. Provenance Acceptance

| ID       | Criterion                                                                                  |
| -------- | ------------------------------------------------------------------------------------------ |
| PROV-001 | Provenance is attached to an exact object version                                          |
| PROV-002 | Inputs and source objects are identifiable                                                 |
| PROV-003 | Agent, model, prompt and tool versions are visible where applicable                        |
| PROV-004 | Parameters are visible or explicitly missing                                               |
| PROV-005 | Intermediate and output artifacts are identifiable where applicable                        |
| PROV-006 | Human edits are attributed separately from generated output                                |
| PROV-007 | Review and approval stages are distinguishable                                             |
| PROV-008 | Missing provenance stages are explicit                                                     |
| PROV-009 | Restricted provenance does not leak content                                                |
| PROV-010 | Provenance completeness uses object-specific requirements                                  |
| PROV-011 | Provenance completeness is not equated automatically with reproducibility                  |
| PROV-012 | Reproducibility claims require sufficient input, version, parameter and environment detail |
| PROV-013 | External provenance shows synchronization and availability state                           |
| PROV-014 | Historical lineage remains available after supersession                                    |
| PROV-015 | Provenance graph has an accessible list or table alternative                               |

---

## 24. Gate 3 Mandatory Scenarios

### Scenario 3A — Memory superseded

Expected:

* old version remains;
* replacement visible;
* active dependent objects listed;
* no historical output rewritten.

### Scenario 3B — Conflicting memories

Expected:

* both retained;
* source and scope visible;
* conflict unresolved or explicitly resolved;
* silent merge prohibited.

### Scenario 3C — Legacy audit event

Expected:

* missing actor role shown as unknown;
* record remains inspectable;
* no invented metadata.

### Scenario 3D — Partial provenance

Expected:

* missing parameter set visible;
* provenance marked partial;
* reproducibility not marked verified.

### Scenario 3E — Human-edited AI output

Expected:

* generated version retained;
* editor and changed version visible;
* final output not attributed only to agent.

### Scenario 3F — Restricted provenance branch

Expected:

* safe restricted placeholder;
* chain remains understandable;
* no data leak.

---

# Part VIII — Gate 4: Evaluation and Corrective Action

## 25. Gate 4 Objective

Verify that evaluations are exact, contextual, reproducible where possible, and connected to governance actions without self-authorizing release.

---

## 26. Evaluation Target Acceptance

| ID       | Criterion                                    |
| -------- | -------------------------------------------- |
| EVAL-001 | Evaluation target type is explicit           |
| EVAL-002 | Target ID and version are explicit           |
| EVAL-003 | Intended use is explicit                     |
| EVAL-004 | Evaluation suite ID and version are explicit |
| EVAL-005 | Baseline is exact and not silently changed   |
| EVAL-006 | Data or golden set is identifiable           |
| EVAL-007 | Evaluator actor is attributable              |
| EVAL-008 | Scope and limitations are visible            |

---

## 27. Evaluation Run Acceptance

| ID      | Criterion                                                                                   |
| ------- | ------------------------------------------------------------------------------------------- |
| RUN-001 | Queued, running, partial, completed, failed, cancelled and invalid states are distinguished |
| RUN-002 | Long-running updates do not overwrite newer runs                                            |
| RUN-003 | Duplicate or late events are deduplicated                                                   |
| RUN-004 | Partial results are not displayed as final                                                  |
| RUN-005 | Failed or invalid runs remain inspectable                                                   |
| RUN-006 | Run provenance is available                                                                 |
| RUN-007 | Evaluation execution is not claimed if only local visualization occurred                    |
| RUN-008 | Cancellation and retry reflect real backend capability                                      |

---

## 28. Evaluation Metric Acceptance

| ID      | Criterion                                                  |
| ------- | ---------------------------------------------------------- |
| MET-001 | Metric name, value and unit are visible                    |
| MET-002 | Threshold and pass/fail interpretation are explicit        |
| MET-003 | Sample size and missing count are visible where available  |
| MET-004 | Uncertainty is shown where available                       |
| MET-005 | Calculation or suite version is identifiable               |
| MET-006 | Aggregate results can be decomposed by relevant slices     |
| MET-007 | Unofficial aggregate scores are not invented               |
| MET-008 | Different dimensions are not collapsed without explanation |

---

## 29. Critical Regression Acceptance

| ID      | Criterion                                                                      |
| ------- | ------------------------------------------------------------------------------ |
| REG-001 | Critical regression categories are explicit                                    |
| REG-002 | Critical failure examples are inspectable                                      |
| REG-003 | Average improvement cannot hide a critical regression                          |
| REG-004 | Release or acceptance is blocked according to policy                           |
| REG-005 | Remediation or authorized override path is visible                             |
| REG-006 | Override does not erase the original regression                                |
| REG-007 | A passed evaluation does not auto-authorize scientific acceptance or execution |
| REG-008 | Evaluation review remains distinct from evaluation computation                 |

---

## 30. Corrective Action Acceptance

| ID      | Criterion                                                       |
| ------- | --------------------------------------------------------------- |
| COR-001 | Evaluation finding can create remediation or investigation      |
| COR-002 | Corrective action identifies owner and target                   |
| COR-003 | Corrective action identifies affected version                   |
| COR-004 | Resolution creates an audit event                               |
| COR-005 | Known limitation acceptance is explicit and attributable        |
| COR-006 | Re-evaluation requirements are visible                          |
| COR-007 | Affected downstream objects are discoverable where supported    |
| COR-008 | Corrective action state is not confused with scientific outcome |

---

## 31. Gate 4 Mandatory Scenarios

### Scenario 4A — Aggregate improvement with hallucinated citation

Expected:

* average improvement visible;
* hallucinated citation marked critical;
* release blocked;
* failure examples inspectable.

### Scenario 4B — Evaluation still running

Expected:

* no final result;
* partial metrics clearly marked;
* governance action unavailable if final evaluation required.

### Scenario 4C — Old run finishes late

Expected:

* old completion cannot replace newer current run;
* both runs remain inspectable.

### Scenario 4D — Evaluation accepted with limitations

Expected:

* limitations visible;
* reviewer and rationale recorded;
* not presented as unrestricted release.

---

# Part IX — Gate 5: UI, Interaction and Runtime States

## 32. Gate 5 Objective

Verify that the interface supports complex governance work without hiding state, losing context or creating false completion.

---

## 33. Information Architecture Acceptance

| ID     | Criterion                                                                                    |
| ------ | -------------------------------------------------------------------------------------------- |
| UI-001 | Page identity and selected context are visible                                               |
| UI-002 | Attention, Approval, Provenance, Memory, Audit and Evaluation workspaces are distinguishable |
| UI-003 | The selected governed object remains visible while inspecting detail                         |
| UI-004 | Inspector and detail regions preserve context                                                |
| UI-005 | Consequential action is visually distinct from inspection                                    |
| UI-006 | Historical mode is visibly distinct                                                          |
| UI-007 | Restricted and unavailable states are visibly distinct                                       |
| UI-008 | Page does not become a generic card wall                                                     |
| UI-009 | Information density supports scanning and deep inspection                                    |
| UI-010 | Raw technical metadata is progressively disclosed                                            |

---

## 34. Selection and Inspector Acceptance

| ID      | Criterion                                                                    |
| ------- | ---------------------------------------------------------------------------- |
| INT-001 | Selecting an object opens the correct Inspector                              |
| INT-002 | Selection remains stable during secondary loading                            |
| INT-003 | Inspector shows exact object and version                                     |
| INT-004 | Opening evidence, provenance or audit detail does not lose primary selection |
| INT-005 | Browser Back restores meaningful previous context                            |
| INT-006 | Deep link restores workspace and selected object                             |
| INT-007 | Historical deep link opens read-only by default                              |
| INT-008 | Return-to-source preserves source selection where possible                   |
| INT-009 | Stale deep link does not silently open a newer version                       |
| INT-010 | Missing selected object shows explicit recovery state                        |

---

## 35. Consequential Action Interaction Acceptance

| ID      | Criterion                                                        |
| ------- | ---------------------------------------------------------------- |
| ACT-001 | Exact action name is visible                                     |
| ACT-002 | Exact object and version are repeated before confirmation        |
| ACT-003 | Consequence and reversibility are explained                      |
| ACT-004 | Required rationale is validated                                  |
| ACT-005 | Disabled action explains why                                     |
| ACT-006 | Keyboard activation cannot accidentally double-submit            |
| ACT-007 | Mutation progress is announced                                   |
| ACT-008 | Failure preserves user input                                     |
| ACT-009 | Confirmed completion identifies resulting state                  |
| ACT-010 | Focus returns to a meaningful location after completion or error |

---

## 36. Required Runtime States

Every applicable region must support:

* Loading;
* Empty;
* Normal;
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
* Mutation Failed;
* Backend Capability Unavailable.

---

## 37. Runtime-State Acceptance

| ID        | Criterion                                                           |
| --------- | ------------------------------------------------------------------- |
| STATE-001 | Loading does not fabricate content                                  |
| STATE-002 | Empty state explains why content is empty                           |
| STATE-003 | Partial state identifies missing regions                            |
| STATE-004 | Partial state explains whether action is blocked                    |
| STATE-005 | Stale state shows last verified time or available equivalent        |
| STATE-006 | Offline mode does not show consequential action as committed        |
| STATE-007 | Unauthorized state does not expose protected data                   |
| STATE-008 | Superseded state identifies current replacement where available     |
| STATE-009 | Conflict state shows local and server versions                      |
| STATE-010 | Mutation failure does not display final success                     |
| STATE-011 | Capability unavailable does not silently use fixture data           |
| STATE-012 | Region-level failure does not falsely fail unrelated loaded regions |

---

## 38. Search, Filter and Queue Acceptance

| ID        | Criterion                                                            |
| --------- | -------------------------------------------------------------------- |
| QUEUE-001 | Attention items show reason, target, version, action and owner       |
| QUEUE-002 | Priority has an explicit basis                                       |
| QUEUE-003 | Filters preserve stable context                                      |
| QUEUE-004 | Server-side filtering or pagination is used at required scale        |
| QUEUE-005 | Resolution creates or links an audit event                           |
| QUEUE-006 | Resolved item does not disappear without explanation                 |
| QUEUE-007 | Counts match authoritative results or are marked partial             |
| QUEUE-008 | Sorting does not imply scientific causality or urgency without basis |

---

# Part X — Gate 6: Technical Architecture and Backend Truthfulness

## 39. Gate 6 Objective

Verify that Page 04 is integrated into the real repository without parallel truth, invented capabilities or unsafe architectural drift.

---

## 40. Architecture Acceptance

| ID       | Criterion                                                              |
| -------- | ---------------------------------------------------------------------- |
| TECH-001 | Existing framework, router and build system are reused                 |
| TECH-002 | Existing AppShell and navigation are reused                            |
| TECH-003 | Existing design tokens are reused                                      |
| TECH-004 | DTO-to-view-model adapter boundary exists where required               |
| TECH-005 | Backend DTOs are not redefined inconsistently                          |
| TECH-006 | Server, URL, persistent and local state ownership are explicit         |
| TECH-007 | No competing approval, audit, provenance or memory store is introduced |
| TECH-008 | Page-specific components remain inside approved feature boundary       |
| TECH-009 | Business logic is not hidden inside purely visual components           |
| TECH-010 | No unrelated repository refactor is introduced                         |

---

## 41. Backend Truthfulness Acceptance

| ID       | Criterion                                                   |
| -------- | ----------------------------------------------------------- |
| BACK-001 | All production queries use real supported APIs              |
| BACK-002 | All production mutations use real supported APIs            |
| BACK-003 | No invented endpoint, schema or event is presented as real  |
| BACK-004 | Unsupported capabilities show explicit unavailable state    |
| BACK-005 | Production does not silently fall back to fixtures          |
| BACK-006 | Fixtures are typed, deterministic and test/development-only |
| BACK-007 | Backend permissions remain authoritative                    |
| BACK-008 | Backend object version remains authoritative                |
| BACK-009 | Backend action result is confirmed before final display     |
| BACK-010 | API errors are mapped without fabricating meaning           |

---

## 42. State and Persistence Acceptance

| ID          | Criterion                                                                 |
| ----------- | ------------------------------------------------------------------------- |
| PERSIST-001 | Project and cycle context restore correctly                               |
| PERSIST-002 | Selected workspace restores safely                                        |
| PERSIST-003 | Safe deep-link state is represented in URL where appropriate              |
| PERSIST-004 | Sensitive content is not placed in URL                                    |
| PERSIST-005 | Historical selection remains historical after refresh                     |
| PERSIST-006 | Stale persisted version is not silently upgraded                          |
| PERSIST-007 | Unsaved review input is protected according to approved persistence rules |
| PERSIST-008 | Competing stores do not overwrite server truth                            |
| PERSIST-009 | Logout or permission change clears protected cached state where required  |
| PERSIST-010 | Restoration order does not flash unauthorized content                     |

---

## 43. Mutation and Concurrency Acceptance

| ID       | Criterion                                                                         |
| -------- | --------------------------------------------------------------------------------- |
| CONC-001 | Duplicate action is prevented                                                     |
| CONC-002 | Stale object version blocks mutation                                              |
| CONC-003 | Local notes survive version conflict                                              |
| CONC-004 | Timeout recovery uses refetch or action-status reconciliation                     |
| CONC-005 | Late server response does not overwrite newer state                               |
| CONC-006 | Optimistic updates are not used for consequential state unless contractually safe |
| CONC-007 | Cache invalidation refreshes affected views                                       |
| CONC-008 | Cross-page state propagation uses backend truth or approved events                |
| CONC-009 | Page 01–03 are not updated by local Page 04 mutation alone                        |
| CONC-010 | Idempotency behavior is tested where supported                                    |

---

# Part XI — Gate 7: Security, Privacy and Permissions

## 44. Gate 7 Objective

Verify that restricted scientific, governance and memory content remains protected across all user-visible and technical surfaces.

---

## 45. Permission Acceptance

| ID      | Criterion                                                      |
| ------- | -------------------------------------------------------------- |
| SEC-001 | Backend enforces access                                        |
| SEC-002 | Frontend visibility is not treated as authorization            |
| SEC-003 | Unauthorized mutation is rejected by backend                   |
| SEC-004 | Permission failure does not leak hidden fields                 |
| SEC-005 | Restricted object existence is protected where policy requires |
| SEC-006 | Action availability updates after permission changes           |
| SEC-007 | Unknown permission state does not default to authorized        |
| SEC-008 | Delegated or conditional authority is represented accurately   |

---

## 46. Sensitive Data Acceptance

| ID       | Criterion                                                    |
| -------- | ------------------------------------------------------------ |
| PRIV-001 | Sensitive memory content is not logged                       |
| PRIV-002 | Approval rationale is not sent to unauthorized analytics     |
| PRIV-003 | Protected audit payload is not exposed through errors        |
| PRIV-004 | Restricted data is not embedded in URL parameters            |
| PRIV-005 | Restricted content is not exposed in search snippets         |
| PRIV-006 | Related-object labels do not leak protected identities       |
| PRIV-007 | Export applies the same permission boundaries as the UI      |
| PRIV-008 | Browser storage does not retain unapproved sensitive content |
| PRIV-009 | Cached restricted data is invalidated appropriately          |
| PRIV-010 | External links and rich content are rendered safely          |

---

## 47. Export Acceptance

| ID      | Criterion                                                               |
| ------- | ----------------------------------------------------------------------- |
| EXP-001 | Export scope is explicit                                                |
| EXP-002 | Object IDs and versions are retained                                    |
| EXP-003 | Filter state and export time are retained                               |
| EXP-004 | Historical exports do not imply current validity                        |
| EXP-005 | Restricted fields are removed or safely represented                     |
| EXP-006 | Export cannot bypass UI permissions                                     |
| EXP-007 | Approval, provenance and limitation state are retained where applicable |
| EXP-008 | Export generation failure does not appear as successful download        |

---

# Part XII — Gate 8: Accessibility, Responsive and Performance

## 48. Accessibility Acceptance

Target: WCAG 2.2 AA or repository-approved equivalent.

| ID       | Criterion                                                   |
| -------- | ----------------------------------------------------------- |
| A11Y-001 | Page has semantic landmarks                                 |
| A11Y-002 | Heading order is logical                                    |
| A11Y-003 | All interactive elements are keyboard reachable             |
| A11Y-004 | Visible focus is present                                    |
| A11Y-005 | Focus order follows task flow                               |
| A11Y-006 | Dialog and Drawer focus is trapped and restored correctly   |
| A11Y-007 | Escape closes dismissible layers                            |
| A11Y-008 | Status does not rely on color alone                         |
| A11Y-009 | Dynamic mutation and evaluation updates are announced       |
| A11Y-010 | Tables expose headers and relationships correctly           |
| A11Y-011 | Provenance graph has textual equivalent                     |
| A11Y-012 | Timeline has accessible chronological structure             |
| A11Y-013 | Disabled actions expose explanation                         |
| A11Y-014 | Reduced motion is respected                                 |
| A11Y-015 | Contrast meets approved standard                            |
| A11Y-016 | Touch targets meet approved minimum                         |
| A11Y-017 | Keyboard-only user can complete approval review workflow    |
| A11Y-018 | Keyboard-only user can inspect provenance and audit history |

---

## 49. Responsive Acceptance

Required viewport verification:

* 1920 px;
* 1600 px;
* 1440 px;
* 1280 px;
* tablet;
* mobile review mode.

| ID       | Criterion                                                                  |
| -------- | -------------------------------------------------------------------------- |
| RESP-001 | Desktop preserves multi-region governance workflow                         |
| RESP-002 | Inspector remains usable at 1280 px                                        |
| RESP-003 | Tablet provides drawer or mode-based access without unreadable compression |
| RESP-004 | Mobile preserves project/object identity                                   |
| RESP-005 | Mobile preserves critical warning and pending action                       |
| RESP-006 | Mobile allows approval review only when interaction remains safe           |
| RESP-007 | Tables have responsive or scroll-safe behavior                             |
| RESP-008 | Provenance graph degrades to list or focused path                          |
| RESP-009 | Long actor names and object titles do not break layout                     |
| RESP-010 | Restricted and stale banners remain visible at all target viewports        |
| RESP-011 | Consequential controls are not obscured by sticky regions                  |
| RESP-012 | No horizontal page overflow except controlled data regions                 |

---

## 50. Performance Acceptance

Performance must be measured against real or deterministic representative data.

| ID       | Criterion                                                             |
| -------- | --------------------------------------------------------------------- |
| PERF-001 | Initial shell does not wait for complete provenance or audit history  |
| PERF-002 | Secondary regions load independently                                  |
| PERF-003 | Large queues use pagination or virtualization                         |
| PERF-004 | Large audit histories do not render all records at once               |
| PERF-005 | Large provenance graphs use summary, focus or lazy loading            |
| PERF-006 | Inspector changes do not rerender the entire page unnecessarily       |
| PERF-007 | Duplicate queries are avoided                                         |
| PERF-008 | Streaming updates are batched or reconciled safely                    |
| PERF-009 | No significant memory leak occurs during repeated workspace switching |
| PERF-010 | Production bundle introduces no unapproved major dependency           |
| PERF-011 | Interaction feedback target is measured                               |
| PERF-012 | Runtime rendering is tested with representative data volume           |

Recommended scale scenarios:

```text
Attention items: 10,000+
Audit events: 100,000+
Memory objects: 10,000+
Provenance nodes per object: 1,000+
Evaluation runs: 10,000+
Failure examples: 10,000+
```

If representative scale data is unavailable, mark the scale criterion `NOT RUN` or `NOT AVAILABLE`; do not claim `PASS`.

---

# Part XIII — Gate 9: Regression and Release

## 51. Regression Objective

Verify that implementing Page 04 did not weaken or change unrelated product, scientific, governance or technical behavior.

---

## 52. Regression Matrix

| Domain        | Required proof                                                              |
| ------------- | --------------------------------------------------------------------------- |
| Global Shell  | Navigation, layout and shared context unchanged except approved integration |
| Design System | No page-private token system or visual-language drift                       |
| Page 01       | Project command behavior remains intact                                     |
| Page 02       | Engineering workflow and human-gate semantics remain intact                 |
| Page 03       | Knowledge ownership and version governance remain intact                    |
| Backend       | No endpoint rename, schema break or scientific-logic change                 |
| Permissions   | No weaker access path introduced                                            |
| Approval      | No self-approval, silent approval or version ambiguity introduced           |
| Audit         | No editable or deletable history introduced                                 |
| Memory        | No in-place historical overwrite introduced                                 |
| Provenance    | No fabricated lineage introduced                                            |
| Evaluation    | No auto-release or hidden critical regression introduced                    |
| Accessibility | Shared focus, keyboard and semantics remain intact                          |
| Performance   | No material regression to existing pages                                    |
| Repository    | Unrelated user work remains untouched                                       |

---

## 53. Repository Diff Acceptance

The final diff must show:

* only approved Page 04 files;
* necessary route integration;
* necessary safe shared-component extensions;
* Page 04 tests and decision records;
* no unexplained backend changes;
* no unrelated formatting sweep;
* no unrelated dependency changes;
* no deletion of user-owned work.

Every modified shared file must have a documented reason and regression test.

---

# Part XIV — Required End-to-End Scenarios

## 54. Scenario A — Pending Approval Review

Steps:

1. Open Page 04 from Page 02.
2. Preserve project, cycle, decision and version.
3. Open approval package.
4. Inspect supporting and conflicting evidence.
5. Confirm reviewer authority.
6. Approve.
7. Confirm authoritative state.
8. Open linked audit event.
9. Return to Page 02.

Expected:

* exact context preserved;
* approval is version-bound;
* no local-only completion;
* audit record visible;
* Page 02 receives authoritative governance state.

---

## 55. Scenario B — Request Changes

Expected:

* reviewer specifies required changes;
* target version remains explicit;
* original request remains historical;
* notes survive failed submission;
* resubmission state is distinct.

---

## 56. Scenario C — Revoked Approval

Expected:

* original approval retained;
* revocation reason visible;
* affected scheduled work discoverable;
* current authorization removed.

---

## 57. Scenario D — Memory Conflict

Expected:

* two memories displayed separately;
* source, scope, version and confidence visible;
* affected decisions visible;
* no silent merge.

---

## 58. Scenario E — Memory Supersession

Expected:

* new version created;
* old version remains historical;
* current active-use warning generated where applicable;
* historical outputs retain old version.

---

## 59. Scenario F — Audit Reconstruction

User selects an executed experiment-related object.

Expected reconstruction:

```text
Trigger
→ Input
→ Actor
→ Decision
→ Approval
→ Execution
→ Observation
→ Evaluation
```

Missing stages remain explicit.

---

## 60. Scenario G — Partial Provenance

Expected:

* available lineage displayed;
* missing model parameter or source displayed explicitly;
* reproducibility remains unverified;
* approval blocking follows policy.

---

## 61. Scenario H — Critical Evaluation Regression

Expected:

* critical failure visible;
* aggregate success does not hide it;
* release blocked;
* remediation or override available only to authorized actor.

---

## 62. Scenario I — Offline Governance Review

Expected:

* safe loaded content remains readable;
* local draft behavior follows approved policy;
* consequential action disabled;
* reconnection refetches authoritative state.

---

## 63. Scenario J — Version Conflict

Expected:

* action blocked;
* server and reviewed versions shown;
* notes preserved;
* user cannot silently overwrite.

---

## 64. Scenario K — Unauthorized User

Expected:

* no protected content leak;
* no consequential action;
* safe explanation;
* direct URL does not bypass authorization.

---

## 65. Scenario L — Historical Object

Expected:

* historical state visibly marked;
* read-only by default;
* current replacement linked;
* no action accidentally targets current version.

---

## 66. Scenario M — Backend Partial Failure

Provenance service fails while approval package and audit history remain available.

Expected:

* loaded regions remain usable;
* provenance shown as unavailable;
* action blocked only if policy requires provenance;
* page not shown as completely failed.

---

## 67. Scenario N — Large Audit History

Expected:

* filtering and pagination remain responsive;
* selection remains stable;
* event detail opens correctly;
* keyboard navigation remains usable.

---

## 68. Scenario O — Restricted Provenance Export

Expected:

* export respects permission;
* restricted branch content is not leaked;
* limitation is represented;
* historical status remains clear.

---

# Part XV — Visual Acceptance

## 69. Visual Identity Acceptance

Page 04 must visually communicate:

* control;
* traceability;
* scientific seriousness;
* explicit state;
* human authority;
* layered inspection.

It must not resemble:

* a generic admin dashboard;
* a cybersecurity threat console;
* an email inbox;
* a social activity feed;
* a single-score trust dashboard;
* a chatbot;
* an animated graph showcase.

---

## 70. Visual Hierarchy Acceptance

Primary layer:

* page identity;
* current context;
* critical governance state;
* required action.

Secondary layer:

* object state;
* evidence/provenance status;
* owner;
* approval/evaluation summary.

Tertiary layer:

* raw event payload;
* detailed parameters;
* version diffs;
* low-level technical metadata.

---

## 71. Semantic Color Acceptance

Color must reuse global semantic tokens.

Acceptance requires:

* no page-private semantic palette;
* status also expressed through text, icon or shape;
* approval is not represented by color alone;
* critical regression remains visually distinct;
* unknown is not styled as neutral success;
* purple or decorative color does not become an undocumented trust meaning;
* historical and superseded states are distinguishable without relying only on opacity.

---

## 72. Visual Regression Viewports and States

Screenshots or equivalent verification should cover:

### Viewports

* 1920 × representative height;
* 1600;
* 1440;
* 1280;
* tablet;
* mobile review mode.

### States

* normal;
* loading;
* empty;
* partial;
* stale;
* unauthorized;
* historical;
* version conflict;
* critical regression;
* approval pending;
* mutation failure;
* restricted provenance.

---

# Part XVI — Code Quality and Test Acceptance

## 73. Required Verification Commands

Use repository-native commands for:

* formatting;
* lint;
* strict typecheck;
* unit tests;
* component tests;
* integration tests;
* end-to-end tests where available;
* production build;
* runtime route smoke test;
* accessibility test;
* bundle or performance analysis where available.

Do not invent command names.

---

## 74. Minimum Automated Test Coverage

At minimum, tests must cover:

### Adapters

* unknown enum;
* missing version;
* missing actor;
* restricted field;
* partial provenance;
* legacy event;
* malformed timestamp;
* unauthorized response.

### Approval

* authorized approve;
* unauthorized approve;
* request changes;
* override;
* revoke;
* duplicate submit;
* version conflict;
* mutation timeout.

### Memory

* stale;
* conflict;
* supersede;
* retire;
* affected-use link;
* sensitive-data protection.

### Audit

* ordering;
* retry;
* correction;
* raw-payload safety;
* pagination;
* filtering.

### Provenance

* complete;
* partial;
* restricted;
* human edit;
* large graph fallback.

### Evaluation

* running;
* partial;
* failed;
* stale completion;
* critical regression;
* accepted with limitations.

### Cross-page

* Page 01 entry;
* Page 02 approval entry;
* Page 03 knowledge-governance entry;
* return context;
* authoritative state refresh.

---

## 75. Static Quality Acceptance

| ID       | Criterion                                                |
| -------- | -------------------------------------------------------- |
| CODE-001 | Strict typecheck passes                                  |
| CODE-002 | Lint passes with repository-approved warning policy      |
| CODE-003 | Production build passes                                  |
| CODE-004 | No new unhandled runtime errors                          |
| CODE-005 | No unapproved `any` or unsafe type escape                |
| CODE-006 | No hidden fixture fallback                               |
| CODE-007 | No unexplained TODO or FIXME in completed scope          |
| CODE-008 | No secrets or sensitive content in code or logs          |
| CODE-009 | No duplicated global domain contract                     |
| CODE-010 | New dependencies are justified and approved              |
| CODE-011 | Shared-component changes remain backward compatible      |
| CODE-012 | Dead code and abandoned implementation paths are removed |

---

# Part XVII — Critical Failures

## 76. Automatic REJECTED Conditions

Any one of the following produces `REJECTED`:

### Scientific and Trust

* predicted shown as observed;
* proposed shown as approved;
* approved shown as executed;
* critical regression hidden by aggregate score;
* missing provenance fabricated;
* model-generated content shown as independently verified truth.

### Governance

* agent approves its own consequential output;
* frontend grants approval authority;
* approval does not target exact version;
* override is indistinguishable from ordinary approval;
* revoked approval remains displayed as current authorization;
* permission failure defaults to authorized.

### Memory and History

* memory correction overwrites previous version;
* historical audit event can be silently edited or deleted;
* stale or superseded memory is silently used without visibility;
* historical output is rewritten to reference a newer memory version.

### Backend Truthfulness

* fake endpoint or fake success used in production;
* fixture data silently appears as real governance data;
* local-only state is presented as cross-page truth;
* timeout causes duplicate consequential mutation.

### Security and Privacy

* restricted content leaks through UI, URL, logs, analytics, cache or export;
* unauthorized user can execute consequential action;
* direct route bypasses permission.

### Repository and Quality

* protected architecture modified without authorization;
* unrelated user work overwritten;
* build or strict typecheck fails;
* core workflow cannot be completed by keyboard;
* Page 01, Page 02, Page 03 or global shell is materially broken.

---

# Part XVIII — Gate Decision Rules

## 77. Individual Criterion Rules

A criterion passes only when:

1. implementation exists;
2. behavior was tested;
3. evidence is recorded;
4. no contradictory result exists.

---

## 78. Gate PASS Rule

A gate passes when:

* every mandatory criterion is `PASS` or approved `NOT APPLICABLE`;
* no critical failure exists;
* no unresolved blocker affects that gate;
* required scenario tests pass.

---

## 79. Gate PARTIAL Rule

A gate is `PARTIAL` when:

* some meaningful requirements pass;
* one or more non-critical requirements remain incomplete;
* release readiness is not established.

A `PARTIAL` mandatory gate prevents `READY`.

---

## 80. Gate BLOCKED Rule

A gate is `BLOCKED` when verification depends on:

* missing backend contract;
* missing permission model;
* unresolved protected-surface decision;
* unsafe schema conflict;
* unavailable required environment;
* unresolved user-code overlap.

A blocked mandatory gate prevents `READY`.

---

## 81. READY Rule

Release Decision may be `READY` only if:

```text
Gate 0 PASS
AND Gate 1 PASS
AND Gate 2 PASS
AND Gate 3 PASS
AND Gate 4 PASS
AND Gate 5 PASS
AND Gate 6 PASS
AND Gate 7 PASS
AND Gate 8 PASS
AND Gate 9 PASS
AND Critical Failures = 0
AND Required Verification Complete
AND Completion Report Emitted
```

---

## 82. NEEDS_REVISION Rule

Use `NEEDS_REVISION` when:

* correctable criteria remain `FAIL`, `PARTIAL`, `NOT RUN` or `BLOCKED`;
* implemented scope is useful but incomplete;
* required test evidence is absent;
* acceptance or regression is not fully established.

`NEEDS_REVISION` means implementation is not complete.

It must not be described as final completion.

---

## 83. REJECTED Rule

Use `REJECTED` when:

* any critical failure exists;
* a system invariant is violated;
* protected architecture is modified without approval;
* scientific truth or governance boundaries are weakened;
* production truth is fabricated;
* sensitive information is exposed.

---

# Part XIX — Required Completion Report

## 84. Standard Output

```yaml
outcome:
  release_decision: READY | NEEDS_REVISION | REJECTED
  critical_failures: 0

repository_audit:
  root:
  stack:
  router:
  app_shell:
  design_system:
  state_management:
  api_client:
  authentication:
  authorization:
  testing:
  git_status:
  protected_surfaces:

capability_matrix:
  attention:
  approvals:
  reviewer_authority:
  provenance:
  audit:
  memory:
  evaluation:
  affected_objects:
  exports:
  event_streaming:

implementation:
  route:
  workspaces:
  reused_components:
  extended_components:
  new_components:
  adapters:
  view_models:
  queries:
  mutations:
  events:
  persistence:
  unavailable_states:

files:
  created:
  modified:
  deleted:
  intentionally_untouched:

verification:
  format:
    command:
    result:
  lint:
    command:
    result:
  typecheck:
    command:
    result:
  unit_tests:
    command:
    result:
  integration_tests:
    command:
    result:
  end_to_end:
    command:
    result:
  build:
    command:
    result:
  runtime:
    method:
    result:
  accessibility:
    method:
    result:
  responsive:
    method:
    result:
  performance:
    method:
    result:
  visual_regression:
    method:
    result:
  console:
    result:

acceptance_gates:
  gate_0_readiness:
  gate_1_product_science:
  gate_2_governance:
  gate_3_memory_audit_provenance:
  gate_4_evaluation:
  gate_5_ui_interaction_runtime:
  gate_6_technical_backend:
  gate_7_security_privacy:
  gate_8_accessibility_responsive_performance:
  gate_9_regression_release:

mandatory_scenarios:
  scenario_1a:
  scenario_2a:
  scenario_2b:
  scenario_2c:
  scenario_2d:
  scenario_2e:
  scenario_3a:
  scenario_3b:
  scenario_3c:
  scenario_3d:
  scenario_3e:
  scenario_3f:
  scenario_4a:
  scenario_4b:
  scenario_4c:
  scenario_4d:
  scenario_a:
  scenario_b:
  scenario_c:
  scenario_d:
  scenario_e:
  scenario_f:
  scenario_g:
  scenario_h:
  scenario_i:
  scenario_j:
  scenario_k:
  scenario_l:
  scenario_m:
  scenario_n:
  scenario_o:

regression:
  global_shell:
  design_system:
  page_01:
  page_02:
  page_03:
  backend:
  permissions:
  approval:
  memory:
  audit:
  provenance:
  evaluation:
  accessibility:
  performance:
  repository:

known_limitations:
deferred_capabilities:
approved_exceptions:
decision_records:
stop_condition:
```

---

## 85. Completion Report Truthfulness

The completion report must:

* use real commands;
* use real results;
* identify tests not run;
* identify missing tooling;
* identify blocked capabilities;
* identify files changed;
* identify intentionally untouched protected files;
* avoid claiming visual or accessibility PASS without verification;
* avoid claiming full backend integration when unavailable states remain.

---

# Part XX — Final Acceptance Checklist

## 86. Product and Scientific Checklist

* [ ] Page identity is immediately clear
* [ ] Selected object and version are visible
* [ ] Scientific and governance states are separated
* [ ] Proposal, approval, execution and evaluation are separated
* [ ] Trust dimensions remain inspectable
* [ ] Unknown and unavailable are explicit

---

## 87. Governance Checklist

* [ ] Reviewer authority is backend-controlled
* [ ] Approval is version-bound
* [ ] Mutation is authoritative and idempotent
* [ ] Override is exceptional and visible
* [ ] Revocation preserves history
* [ ] Approval expiry is respected
* [ ] Agent cannot self-approve

---

## 88. Memory Checklist

* [ ] Memory type, scope, source and version are visible
* [ ] Material memory use is traceable
* [ ] Conflicts remain visible
* [ ] Corrections create versions
* [ ] Sensitive memory is protected
* [ ] Affected objects are discoverable

---

## 89. Audit Checklist

* [ ] Audit events are attributable
* [ ] History is append-only from product perspective
* [ ] Correction creates new event
* [ ] Retry and duplicate semantics are visible
* [ ] Historical reconstruction is possible
* [ ] Restricted payload remains protected

---

## 90. Provenance Checklist

* [ ] Exact object version is linked
* [ ] Inputs, actors, tools and parameters are inspectable
* [ ] Human edits are attributed
* [ ] Missing stages are explicit
* [ ] Reproducibility is not overstated
* [ ] Accessible fallback exists

---

## 91. Evaluation Checklist

* [ ] Exact target and version
* [ ] Exact suite and baseline
* [ ] Long-running states handled
* [ ] Critical regression cannot be averaged away
* [ ] Failure examples inspectable
* [ ] Evaluation does not self-authorize release
* [ ] Corrective action is linked

---

## 92. Runtime Checklist

* [ ] Loading
* [ ] Empty
* [ ] Partial
* [ ] Error
* [ ] Offline
* [ ] Unauthorized
* [ ] Restricted
* [ ] Stale
* [ ] Historical
* [ ] Superseded
* [ ] Conflict
* [ ] Mutation Pending
* [ ] Mutation Failed
* [ ] Capability Unavailable

---

## 93. Technical Checklist

* [ ] Existing architecture reused
* [ ] State ownership is explicit
* [ ] No parallel domain truth
* [ ] No invented API
* [ ] No production fixture fallback
* [ ] Safe mutation reconciliation
* [ ] Cross-page state is authoritative
* [ ] Protected surfaces preserved

---

## 94. Quality Checklist

* [ ] Formatter result recorded
* [ ] Lint passes
* [ ] Strict typecheck passes
* [ ] Required tests pass
* [ ] Production build passes
* [ ] Runtime verified
* [ ] Accessibility verified
* [ ] Responsive behavior verified
* [ ] Performance measured
* [ ] Visual regression checked
* [ ] Console contains no critical errors
* [ ] Critical failures equal zero

---

# Part XXI — Stop Condition

## 95. Final Stop Condition

```text
Repository Audit complete
AND Specification Mapping complete
AND Capability Matrix complete
AND Protected Surfaces preserved
AND Page 04 implemented
AND Real Backend Integration verified
AND Unsupported Capabilities explicitly degraded
AND Governance Mutations authoritative
AND Approval Version Binding verified
AND Memory Versioning preserved
AND Audit Immutability preserved
AND Provenance Gaps explicit
AND Evaluation Regressions handled
AND Security and Permission Gates PASS
AND Runtime States PASS
AND Accessibility PASS
AND Responsive PASS
AND Performance verified
AND Regression PASS
AND Lint PASS
AND Typecheck PASS
AND Tests PASS
AND Production Build PASS
AND Critical Failures = 0
AND Completion Report emitted
→ READY
→ STOP
```

If correctable requirements remain:

```text
NEEDS_REVISION
```

If any critical trust, governance, history, security or repository rule is violated:

```text
REJECTED
```

After `READY`, no further refactoring, redesign, optimization, renaming or scope expansion is permitted.

---

# Part XXII — Acceptance Constitution

```text
Page 04 shall not be accepted because it appears complete.

It shall be accepted only when authoritative backend state, exact object identity, exact version identity, human authority, memory lineage, audit history, provenance, evaluation and corrective action can be inspected and verified.

Proposal, approval, execution, observation and evaluation shall remain distinct.

Scientific state and governance state shall remain distinct.

Memory shall not become hidden truth.

Memory correction shall create a new version.

Audit correction shall create a new event.

Provenance gaps shall remain visible.

Critical evaluation regression shall not be hidden by an aggregate score.

Approval shall be version-bound, attributable and backend-authoritative.

Agents shall not approve their own consequential outputs.

Restricted content shall not leak through any user-visible or technical surface.

Production shall not fabricate APIs, data, evidence, permissions, approval, audit, provenance or evaluation.

READY shall be declared only when every mandatory gate passes and every critical failure equals zero.
```

---

# Part XXIII — Final Acceptance Summary

The canonical Page 04 acceptance chain is:

```text
Verify Repository and Backend Reality
→ Verify Product and Scientific Semantics
→ Verify Human Governance
→ Verify Memory Integrity
→ Verify Audit Immutability
→ Verify Provenance Completeness and Gaps
→ Verify Evaluation and Regression Handling
→ Verify Runtime and Interaction
→ Verify Permissions and Privacy
→ Verify Accessibility, Responsive and Performance
→ Verify Cross-Page and Repository Regression
→ Emit Factual Completion Report
→ READY
→ STOP
```

Page 04 is complete only when an authorized user can safely answer:

```text
What exact object and version am I reviewing?
What is known, predicted, proposed, approved, executed or evaluated?
What memory influenced it?
What evidence and provenance support it?
Who acted and who had authority?
What changed and why?
What was the outcome?
What failed?
What requires correction?
What remains uncertain or unavailable?
```

without fabricated truth, hidden uncertainty, overwritten history, ambiguous authority, unauthorized access or unverified acceptance.
