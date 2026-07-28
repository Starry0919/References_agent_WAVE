# Synthetic Biology DBTL Engineering OS

# Page 04 — Trust & Provenance Center

# 04_Technical_Spec.md

> **Document type**: Page-specific Technical Specification and Implementation Contract
> **Page**: Page 04 — Trust & Provenance Center
> **Product role**: Trust, Governance & Provenance Control Plane
> **Status**: Normative / Implementation-Binding
> **Parent contract**: Page Design Contract v1.2.0
> **Parent architecture**: Synthetic Biology DBTL Engineering OS Frontend Architecture v1.2
> **Parent product spec**: Page 04 `01_Product_Spec.md` v1.0.0
> **Parent UI spec**: Page 04 `02_UI_Spec.md` v1.0.0
> **Parent operating principles**: Page 04 `03_Operating_Principles.md` v1.0.0
> **Default UI language**: English
> **Specification language**: English, with implementation notes permitted in Chinese
> **Version**: 1.0.0
> **Last updated**: 2026-07-23

---

## Specification Header

```yaml
page_id: page-04
page_name: Trust & Provenance Center
spec_type: Technical Spec
version: 1.0.0
status: Approved
product_positioning: Trust, Governance & Provenance Control Plane
owners:
  - Product Owner
  - Frontend Architect
  - Governance Platform Owner
  - Scientific Product Lead
reviewers:
  - Principal Investigator
  - Synthetic Biology Reviewer
  - Dry-Lab Reviewer
  - Wet-Lab Reviewer
  - Backend Architect
  - Security and Privacy Reviewer
  - Accessibility Reviewer
  - QA and Release Reviewer
parent_contract: Page Design Contract v1.2.0
parent_architecture: Frontend Architecture Prompt v1.2
parent_product_spec: Page04/01_Product_Spec.md
parent_ui_spec: Page04/02_UI_Spec.md
parent_operating_principles: Page04/03_Operating_Principles.md
dependencies:
  - 00_Page_Research.md
  - 01_Product_Spec.md
  - 02_UI_Spec.md
  - 03_Operating_Principles.md
  - 05_Acceptance_Spec.md
approved_exceptions: []
open_questions: []
```

---

# Part I — Technical Mission

## 1. Purpose

This document defines how Page 04 must be implemented safely inside the existing repository.

It governs:

* frontend architecture;
* route and shell integration;
* domain object mapping;
* backend contracts;
* adapters and view models;
* state ownership;
* URL and persistence behavior;
* permission enforcement;
* approval mutations;
* audit and provenance rendering;
* memory governance;
* evaluation execution;
* streaming and asynchronous jobs;
* offline and recovery behavior;
* accessibility;
* performance;
* observability;
* testing;
* repository safety;
* release and stop conditions.

This document is not permission to redesign the repository.

It is an implementation contract for integrating Page 04 with the real system.

---

## 2. Technical Objective

The implementation must provide a persistent governance workspace in which users can:

```text
Locate a consequential object
→ Resolve its exact version
→ Inspect memory, evidence, provenance, and history
→ Determine authority
→ Review approval or evaluation basis
→ Commit a governed action
→ Confirm authoritative backend state
→ Preserve audit history
→ Propagate the result safely to dependent pages
```

---

## 3. Implementation Philosophy

The technical implementation must follow:

```text
Repository truth
→ Existing architecture
→ Backend authority
→ Domain adapter
→ Stable view model
→ UI composition
→ Verified mutation
→ Audit confirmation
```

It must never follow:

```text
Visual mockup
→ Invented frontend state
→ Assumed backend capability
→ Fake successful governance action
```

---

# Part II — Repository Audit Contract

## 4. Mandatory Pre-Implementation Audit

Before writing code, the implementation agent must identify:

```yaml
repository:
  root:
  framework:
  language:
  build_tool:
  package_manager:
  router:
  styling_system:
  token_system:
  app_shell:
  navigation:
  state_management:
  server_state_library:
  api_client:
  schema_generation:
  event_transport:
  persistence:
  authentication:
  authorization:
  testing:
  accessibility_tooling:
  observability:
  deployment:
```

It must also identify:

```yaml
page4_dependencies:
  shared_object_header:
  inspector:
  evidence_drawer:
  data_table:
  comparison_table:
  diff_viewer:
  timeline:
  audit_timeline:
  approval_controls:
  review_thread:
  alerts:
  loading_states:
  permission_states:
```

No framework, package, route, API, store, or shared component may be assumed.

---

## 5. Repository Evidence

Every architectural claim must be grounded in:

* actual source file;
* package configuration;
* route registration;
* imported type;
* API schema;
* backend handler;
* event definition;
* test configuration;
* existing shared component.

The implementation report must cite affected repository paths.

---

## 6. Protected Surfaces

The following are protected by default:

* global application shell;
* global navigation;
* global design tokens;
* global typography;
* global object identity model;
* authentication and authorization system;
* approval semantics;
* audit event schema;
* provenance schema;
* shared API client;
* shared state store;
* backend scientific logic;
* Page 01, Page 02, and Page 03 behavior;
* unrelated routes;
* user-owned uncommitted changes.

Modification requires:

1. evidence that Page 04 cannot be implemented safely otherwise;
2. alternatives considered;
3. impact analysis;
4. ADR or DSR;
5. explicit authorization.

Without authorization, implementation must stop at the Conditional Audit Gate.

---

# Part III — Architecture Contract

## 7. Required Layering

Page 04 must preserve a layered architecture:

```text
Backend / Event Sources
↓
Generated or Verified DTO Types
↓
API Client
↓
Page 04 Adapters
↓
Domain/View Models
↓
Server-State Queries and Mutations
↓
Page State Composition
↓
UI Components
```

Backend DTOs must not flow directly into presentational components unless the repository already treats the DTO as the approved domain contract.

---

## 8. Adapter Boundary

Adapters are responsible for:

* field-name normalization;
* enum normalization;
* version identity normalization;
* permission mapping;
* missing-field classification;
* provenance completeness derivation;
* actor-type mapping;
* historical/current-state mapping;
* safe date parsing;
* backend error mapping;
* capability availability mapping.

Adapters must not:

* fabricate missing fields;
* grant permissions;
* infer human approval;
* create scientific trust;
* rewrite historical events;
* convert unknown into success;
* suppress backend conflicts.

---

## 9. Recommended Feature Boundary

Only if compatible with the existing repository:

```text
features/trust-provenance/
├── api/
│   ├── queries/
│   ├── mutations/
│   └── subscriptions/
├── adapters/
├── components/
├── workspaces/
│   ├── attention/
│   ├── approvals/
│   ├── provenance/
│   ├── memory/
│   ├── audit/
│   └── evaluation/
├── hooks/
├── state/
├── types/
├── utils/
├── fixtures/
└── tests/
```

The repository’s existing conventions take precedence over this example.

---

## 10. Page Composition

Recommended component tree:

```text
TrustProvenancePage
├── AppShell
├── Page04ContextHeader
├── GovernanceNavigation
├── TrustWorkspaceFrame
│   ├── GovernanceWorkspaceRouter
│   │   ├── AttentionWorkspace
│   │   ├── ApprovalWorkspace
│   │   ├── ProvenanceWorkspace
│   │   ├── MemoryWorkspace
│   │   ├── AuditWorkspace
│   │   └── EvaluationWorkspace
│   ├── GovernanceInspector
│   └── GovernanceDetailRegion
└── MutationFeedbackLayer
```

---

## 11. Workspace Composition Principle

Each workspace should share:

* context;
* selected governed object;
* object version;
* current permissions;
* source return context;
* deep-link state;
* inspector;
* loading/error conventions;
* audit linkage.

They must not be implemented as unrelated pages with incompatible state models.

---

# Part IV — Core Type Contract

## 12. Stable Identity Types

At minimum:

```ts
type ObjectId = string
type VersionId = string
type ProjectId = string
type CycleId = string
type ActorId = string
type AuditEventId = string
type ApprovalId = string
type EvaluationId = string
type MemoryId = string
type ProvenanceId = string
```

Opaque IDs must remain opaque.

The UI must not parse business meaning from an ID unless the backend contract explicitly defines it.

---

## 13. Versioned Object Reference

```ts
type VersionedObjectRef = {
  objectId: ObjectId
  objectType: GovernedObjectType
  versionId: VersionId
  displayName?: string
}
```

All consequential actions must use a `VersionedObjectRef` or equivalent verified repository type.

---

## 14. Governed Object View Model

```ts
type GovernedObjectViewModel = {
  ref: VersionedObjectRef
  title: string
  subtitle?: string
  projectId?: ProjectId
  cycleId?: CycleId
  scientificState?: ScientificState
  governanceState: GovernanceState
  owner?: ActorRef
  createdAt?: string
  updatedAt?: string
  historical: boolean
  stale: boolean
  supersededBy?: VersionedObjectRef
  provenanceSummary: ProvenanceSummary
  approvalSummary: ApprovalSummary
  evaluationSummary: EvaluationSummary
  memoryImpactSummary?: MemoryImpactSummary
  permissions: ObjectPermissions
}
```

---

## 15. Actor Reference

```ts
type ActorRef = {
  actorId?: ActorId
  actorType:
    | 'human'
    | 'agent'
    | 'automated_system'
    | 'external_tool'
    | 'legacy_unknown'
  displayName: string
  role?: string
}
```

Human, agent, system, and tool actors must remain distinguishable.

---

## 16. Permission Contract

```ts
type ObjectPermissions = {
  canView: boolean
  canViewRestrictedFields: boolean
  canReview: boolean
  canApprove: boolean
  canReject: boolean
  canRequestChanges: boolean
  canOverride: boolean
  canRevoke: boolean
  canRestrict: boolean
  canExport: boolean
  authorityState:
    | 'authorized'
    | 'authorized_with_conditions'
    | 'unauthorized'
    | 'read_only'
    | 'unknown'
    | 'unavailable'
}
```

Permissions must originate from backend or approved policy state.

The frontend must never derive approval authority solely from a role label stored locally.

---

# Part V — Backend Contract

## 17. Required Capability Discovery

Before implementation, determine whether real backend capabilities exist for:

* governance attention items;
* approval requests;
* approval decisions;
* reviewer authority;
* provenance retrieval;
* audit event retrieval;
* memory list and detail;
* memory review or supersession;
* evaluation target discovery;
* evaluation run creation;
* evaluation result retrieval;
* affected-object analysis;
* export;
* event subscriptions;
* historical-object resolution.

Each capability must be classified:

```yaml
capability:
  status: supported | partial | unavailable | unknown
  endpoint_or_event:
  schema:
  authorization:
  pagination:
  streaming:
  mutation_semantics:
  audit_effect:
  frontend_behavior:
```

---

## 18. No Invented Backend

The implementation must not invent:

* endpoint path;
* GraphQL field;
* WebSocket event;
* mutation success;
* approval status;
* audit event;
* provenance node;
* evaluation metric;
* reviewer authority;
* memory content.

If a capability is unavailable:

* show capability-unavailable state;
* disable unsupported actions;
* use deterministic development fixture only in non-production test paths;
* record the limitation.

---

## 19. Query Contracts

Queries should support stable query keys containing relevant context:

```ts
[
  'page04',
  workspaceMode,
  projectId,
  cycleId,
  objectId,
  versionId,
  filters
]
```

Query design must avoid accidental reuse of data across:

* object versions;
* projects;
* cycles;
* permission scopes;
* historical/current states.

---

## 20. Mutation Contracts

Consequential mutations include:

* approve;
* reject;
* request changes;
* override;
* revoke;
* restrict;
* supersede memory;
* retire memory;
* accept evaluation;
* restrict release;
* create remediation;
* accept known limitation.

Each mutation request should include:

```ts
type GovernanceMutationRequest = {
  target: VersionedObjectRef
  action: GovernanceAction
  reason: string
  conditions?: string[]
  expectedCurrentState?: string
  idempotencyKey: string
  clientRequestId: string
}
```

The exact shape must follow the real backend.

---

## 21. Optimistic Update Policy

Optimistic updates are prohibited for irreversible or consequential governance state unless the backend contract explicitly supports safe optimistic reconciliation.

For approval, rejection, override, revocation, restriction, and release decisions:

```text
Submit
→ Show pending mutation
→ Await authoritative server confirmation
→ Receive resulting object/version/state
→ Display committed state
→ Link audit confirmation
```

The UI must not display a successful final state based only on local mutation intent.

---

## 22. Mutation Confirmation

A successful governance mutation should return or allow retrieval of:

* affected object;
* affected version;
* resulting state;
* actor;
* timestamp;
* decision ID;
* audit event ID;
* downstream effect;
* conflict or warning;
* new current version where applicable.

If the backend only returns an acknowledgement, the frontend must refetch authoritative state before showing committed completion.

---

## 23. Idempotency

Consequential actions must use backend-supported idempotency where available.

The UI must prevent duplicate submission through:

* mutation lock;
* stable idempotency key;
* duplicate response handling;
* timeout recovery;
* refetch after uncertain completion.

A timeout does not prove failure or success.

---

# Part VI — State Ownership

## 24. State Categories

Page 04 must distinguish:

### 24.1 Server Truth

* object status;
* object version;
* approval state;
* permission state;
* audit events;
* provenance;
* evaluation results;
* memory content;
* memory review state;
* affected-object dependencies.

### 24.2 Persistent Workspace State

* active Page 04 workspace;
* project;
* cycle;
* source context;
* selected object;
* selected version;
* selected event;
* selected evaluation;
* filters;
* inspector state where approved.

### 24.3 URL-Shareable State

* workspace mode;
* project;
* cycle;
* object ID;
* version ID;
* stable selected item;
* safe filters;
* historical mode.

### 24.4 Local UI State

* panel width;
* temporary tab;
* drawer open;
* expanded section;
* unsaved review note;
* local sort presentation.

### 24.5 Ephemeral State

* hover;
* focus;
* menu open;
* animation;
* transient validation message.

---

## 25. Single Owner Rule

Every state field must have exactly one authority.

Examples:

```text
Approval status
→ Governance backend

Selected approval
→ URL or Page 04 selection state

Approval form input
→ Local form state

Mutation pending
→ Mutation state manager
```

Competing stores for the same domain state are prohibited.

---

## 26. Derived State

Derived trust dimensions may be computed from server data when the derivation is:

* deterministic;
* documented;
* testable;
* not presented as backend truth unless contractually equivalent.

Example:

```ts
const provenanceCompleteness =
  deriveProvenanceCompleteness(provenanceRecord, requiredFields)
```

The result must identify which fields are missing.

---

# Part VII — Routing and Context Contract

## 27. Route Requirements

The route must support:

* direct access;
* cross-page entry;
* object deep link;
* historical version link;
* approval deep link;
* audit event deep link;
* evaluation run deep link;
* memory object deep link.

Route shape must follow repository conventions.

Example only:

```text
/trust
/trust/approvals/:approvalId
/trust/provenance/:objectType/:objectId/:versionId
/trust/memory/:memoryId/:versionId
/trust/audit/:eventId
/trust/evaluations/:evaluationId
```

Do not create these paths if incompatible with the existing router.

---

## 28. Source Return Context

Cross-page entry should carry:

```ts
type SourceReturnContext = {
  sourcePage: 'page01' | 'page02' | 'page03'
  sourceRoute: string
  sourceObject?: VersionedObjectRef
  sourceSelection?: string
  governanceQuestion?: string
}
```

Return behavior must not silently navigate to a newer or different object version without notice.

---

## 29. Historical Route Behavior

Historical versions must:

* open in explicit historical mode;
* default to read-only;
* show current replacement where available;
* prevent actions targeting the wrong version;
* allow creation of a new governance action only through an explicit transition.

---

# Part VIII — Attention Queue Architecture

## 30. Attention Item Model

```ts
type GovernanceAttentionItem = {
  id: string
  type: AttentionType
  target: VersionedObjectRef
  projectId?: ProjectId
  cycleId?: CycleId
  severity: Severity
  reason: string
  consequence?: string
  requiredAction: GovernanceAction
  owner?: ActorRef
  status: AttentionStatus
  createdAt: string
  dueAt?: string
  resolvedAt?: string
}
```

---

## 31. Priority Derivation

Priority must be backend-provided or derived through an approved deterministic rule.

The frontend must not create scientific urgency from:

* card position alone;
* arbitrary color;
* recency only;
* local sorting defaults.

---

## 32. Pagination and Virtualization

The queue must support:

* server pagination or cursor pagination;
* stable sorting;
* filtered result count;
* virtualization when result size requires it;
* row selection persistence;
* no full-list refetch after every local interaction.

---

# Part IX — Approval Architecture

## 33. Approval Request View Model

```ts
type ApprovalRequestViewModel = {
  approvalId: ApprovalId
  target: VersionedObjectRef
  requestedTransition: string
  requester: ActorRef
  requiredReviewerRole?: string
  currentReviewer?: ActorRef
  status: ApprovalStatus
  packageCompleteness: PackageCompleteness
  scientificPurpose?: string
  changeSummary: ChangeSummary[]
  supportingEvidence: EvidenceRef[]
  conflictingEvidence: EvidenceRef[]
  assumptions: string[]
  uncertainties: string[]
  risks: RiskRef[]
  tradeoffs: TradeoffRef[]
  limitations: string[]
  validationRequirements: ValidationRequirement[]
  downstreamEffect?: string
  priorReviews: ReviewRef[]
  permissions: ObjectPermissions
}
```

---

## 34. Approval State Machine

The UI adapter must preserve at least:

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

Unknown backend states must map to `unknown` or an explicit unsupported state, not to the nearest visually convenient status.

---

## 35. Version Binding

Before submitting a decision, the frontend must verify:

* current approval target;
* target version;
* currently loaded server version;
* expected current approval state.

If the target changed during review:

```text
Block submission
→ Refetch
→ Show version conflict
→ Preserve reviewer notes
→ Require review of changed version
```

---

## 36. Review Notes

Review notes may be locally drafted, but:

* must not be treated as submitted;
* must identify the target approval and version;
* must be protected from accidental context switching;
* must be cleared or migrated only after confirmed action;
* must avoid sensitive persistence in insecure storage.

---

## 37. Override Contract

Override requires a separate action path.

It must not reuse ordinary approval without distinction.

Required fields:

* original decision;
* target object;
* version;
* override scope;
* accepted risk;
* reason;
* validity;
* authorized actor;
* review requirement.

---

# Part X — Provenance Architecture

## 38. Provenance Graph Model

```ts
type ProvenanceGraph = {
  subject: VersionedObjectRef
  nodes: ProvenanceNode[]
  edges: ProvenanceEdge[]
  completeness: ProvenanceCompleteness
  generatedAt?: string
  sourceSystem?: string
}
```

```ts
type ProvenanceNode = {
  id: string
  nodeType:
    | 'input'
    | 'memory'
    | 'knowledge'
    | 'task'
    | 'prompt'
    | 'agent'
    | 'model'
    | 'tool'
    | 'parameter_set'
    | 'artifact'
    | 'output'
    | 'evaluation'
    | 'human_edit'
    | 'review'
    | 'approval'
    | 'execution'
    | 'observation'
  ref?: VersionedObjectRef
  title: string
  actor?: ActorRef
  timestamp?: string
  status?: string
  restricted?: boolean
}
```

```ts
type ProvenanceEdge = {
  id: string
  from: string
  to: string
  relation:
    | 'used'
    | 'generated'
    | 'transformed'
    | 'reviewed'
    | 'approved'
    | 'executed'
    | 'observed'
    | 'superseded'
    | 'derived_from'
}
```

The real backend schema takes precedence.

---

## 39. Graph Rendering Rules

The default interface should render a controlled path or grouped DAG.

Requirements:

* stable layout;
* explicit edge direction;
* selectable node;
* restricted-node handling;
* missing-node representation;
* table/list fallback;
* keyboard traversal;
* no force-directed movement as default;
* no graph hairball.

---

## 40. Large Provenance Graphs

For large graphs:

* fetch summarized lineage first;
* lazy-load branch detail;
* collapse repeated tool or artifact groups;
* cap initial rendered nodes;
* allow focused path isolation;
* virtualize supporting tables;
* preserve complete export through backend, not DOM rendering.

---

## 41. Provenance Completeness

Completeness must be computed against object-specific required fields.

Example:

```ts
type ProvenanceCompleteness = {
  status: 'complete' | 'partial' | 'legacy' | 'restricted' | 'unavailable'
  missing: ProvenanceRequirement[]
  restricted: ProvenanceRequirement[]
  applicableCount: number
  presentCount: number
}
```

Do not show `100%` if restricted fields are unknown unless the contract explicitly defines how restricted completeness is calculated.

---

# Part XI — Audit Architecture

## 42. Audit Event Model

```ts
type AuditEventViewModel = {
  eventId: AuditEventId
  eventType: string
  actor: ActorRef
  action: string
  target: VersionedObjectRef
  timestamp: string
  ingestedAt?: string
  previousState?: unknown
  newState?: unknown
  reason?: string
  result?: AuditResult
  projectId?: ProjectId
  cycleId?: CycleId
  relatedObjects: VersionedObjectRef[]
  provenanceId?: ProvenanceId
  retryOf?: AuditEventId
  correctionOf?: AuditEventId
  legacy: boolean
}
```

---

## 43. Append-Only UI Behavior

The frontend must not expose direct edit or delete actions for an audit event unless the backend provides a governed correction workflow.

Corrections must produce:

* correction request;
* correction event;
* relationship to original event;
* corrected interpretation.

---

## 44. Event Ordering

The UI should support:

* event time;
* ingestion time;
* causal grouping;
* object-version grouping.

Default ordering must be explicit.

Late-arriving events must not silently reorder history without indication when that could change interpretation.

---

## 45. Audit Filtering

Filters must be backed by the server where scale requires.

Supported filters may include:

* project;
* cycle;
* object;
* version;
* actor;
* actor type;
* action;
* event type;
* result;
* date range;
* approval;
* model;
* tool.

---

## 46. Raw Payload Handling

Raw payload may be shown only as secondary technical detail.

It must:

* be permission-gated;
* redact protected fields;
* preserve formatting;
* avoid executing embedded content;
* not replace human-readable interpretation.

---

# Part XII — Memory Governance Architecture

## 47. Memory Object Model

```ts
type MemoryObjectViewModel = {
  memoryId: MemoryId
  versionId: VersionId
  memoryClass: MemoryClass
  title: string
  contentSummary: string
  scope: MemoryScope
  source: SourceRef
  createdBy: ActorRef
  createdAt: string
  updatedAt?: string
  status: MemoryStatus
  freshness: FreshnessState
  confidence?: ConfidenceValue
  sensitivity?: SensitivityState
  reviewStatus?: ReviewStatus
  usageSummary: MemoryUsageSummary
  supersedes?: VersionedMemoryRef
  supersededBy?: VersionedMemoryRef
  permissions: ObjectPermissions
}
```

---

## 48. Memory Content Security

Sensitive memory must not be persisted casually in:

* local storage;
* browser logs;
* analytics payloads;
* error traces;
* URL parameters;
* client-side exports.

Only approved identifiers and safe display metadata may appear in shareable routes.

---

## 49. Memory Update Mutation

Memory correction, supersession, restriction, or retirement must use a version-aware backend mutation.

The frontend must not mutate the existing memory object in place.

Expected operation:

```text
Submit proposed change
→ Backend validates authority and current version
→ New memory version created
→ Previous version remains historical
→ Affected-object analysis generated or requested
→ Audit event created
```

---

## 50. Memory Usage Query

Usage inspection should identify:

* consuming object;
* consuming version;
* project and cycle;
* output or decision;
* use time;
* retrieval reason where available;
* active or historical impact.

The UI must distinguish confirmed dependency from possible semantic relevance.

---

# Part XIII — Evaluation Architecture

## 51. Evaluation Target Contract

```ts
type EvaluationTargetRef = {
  targetType:
    | 'component'
    | 'agent'
    | 'model'
    | 'prompt'
    | 'tool'
    | 'retrieval_strategy'
    | 'workflow'
    | 'knowledge_extraction'
    | 'recommendation'
    | 'dbtl_cycle'
  targetId: string
  versionId: VersionId
}
```

---

## 52. Evaluation Run Model

```ts
type EvaluationRunViewModel = {
  evaluationId: EvaluationId
  target: EvaluationTargetRef
  suiteId: string
  suiteVersion: VersionId
  baseline?: EvaluationTargetRef
  status: EvaluationRunStatus
  startedAt?: string
  completedAt?: string
  runBy: ActorRef
  metrics: EvaluationMetric[]
  slices: EvaluationSlice[]
  failures: EvaluationFailure[]
  limitations: string[]
  regressionStatus: RegressionStatus
  reviewStatus: ReviewStatus
  provenanceId?: ProvenanceId
}
```

---

## 53. Evaluation Run Creation

Evaluation execution is allowed only if the backend supports it.

A run request should identify:

* target and version;
* evaluation suite and version;
* dataset or golden set;
* baseline;
* configuration;
* requested actor;
* idempotency key.

The frontend must not claim an evaluation ran if only local comparison data was rendered.

---

## 54. Long-Running Evaluations

Evaluation runs may use:

* polling;
* server-sent events;
* WebSocket;
* job queue subscription.

The implementation must follow existing infrastructure.

Required states:

* queued;
* starting;
* running;
* partial;
* completed;
* failed;
* cancelled;
* invalid;
* stale;
* superseded.

---

## 55. Event Deduplication

Streaming evaluation updates must be deduplicated by:

* run ID;
* event ID or sequence number;
* stage;
* timestamp where reliable.

A late completion from an older run must not overwrite a newer active run.

---

## 56. Evaluation Metrics

Each metric must preserve:

* name;
* dimension;
* value;
* unit;
* threshold;
* status;
* sample size;
* missing count;
* uncertainty where available;
* source;
* calculation version.

The UI must not compute unofficial aggregate scores unless approved and documented.

---

## 57. Critical Regression Handling

If a critical regression exists:

* release or acceptance action should be blocked by policy;
* the exact failure examples must be available;
* affected target and version must be explicit;
* remediation or override path must be visible;
* no average metric may visually hide the block.

---

# Part XIV — Cross-Page Integration

## 58. Integration Principle

Page 04 must not own Page 01, Page 02, or Page 03 domain truth.

It consumes and governs authoritative objects from shared backend systems.

---

## 59. Page 01 Integration

Page 01 may consume summary data such as:

```ts
type ProjectGovernanceSummary = {
  pendingApprovals: number
  criticalTrustIssues: number
  criticalRegressions: number
  expiredApprovals: number
  recentGovernanceEvent?: AuditEventRef
  nextGovernanceAction?: AttentionItemRef
}
```

Page 01 must not infer these counts from local Page 04 state.

---

## 60. Page 02 Integration

Page 02 may request governance of:

* engineering decision;
* design proposal;
* simulation result;
* experiment plan;
* wet-lab handoff.

Page 04 returns authoritative governance state through shared backend data.

---

## 61. Page 03 Integration

Page 03 may request governance of:

* knowledge promotion;
* memory creation;
* evidence review;
* knowledge correction;
* rule supersession.

Page 04 must preserve source object identity and version.

---

## 62. Event-Based Propagation

Where events exist, examples may include:

```text
approval.requested
approval.granted
approval.rejected
approval.revoked
memory.superseded
memory.restricted
evaluation.completed
evaluation.regression_detected
governance.issue.resolved
provenance.gap.detected
```

The actual event names must come from the repository or backend contract.

---

# Part XV — Permission and Security Contract

## 63. Security Principle

Frontend visibility is not authorization.

Every restricted query and mutation must be enforced by backend identity and policy.

---

## 64. Permission Failure Behavior

On unauthorized access:

* do not reveal protected content;
* do not expose hidden object names;
* do not leak existence through detailed errors where prohibited;
* show safe permission state;
* preserve non-sensitive context;
* provide request-access path only if real.

---

## 65. Sensitive Field Redaction

Adapters and rendering must respect backend redaction.

The UI must not attempt to reconstruct redacted content from:

* cached objects;
* related records;
* audit payloads;
* search indices;
* exports.

---

## 66. CSRF, Replay, and Duplicate Action Safety

Governance mutations must use the repository’s approved protections for:

* authentication;
* CSRF;
* replay;
* idempotency;
* stale version;
* duplicate submission.

No custom local security mechanism should replace platform standards.

---

## 67. Audit of Governance Mutations

Every consequential mutation should result in a backend audit event.

If audit confirmation is required by policy but unavailable, the UI must not declare the workflow fully completed.

---

# Part XVI — Persistence and Recovery

## 68. Workspace Persistence

Page 04 may persist safe workspace context:

* workspace mode;
* selected project;
* selected cycle;
* selected safe object reference;
* filters;
* panel state;
* safe draft identifier.

Sensitive content must not be stored without approved encrypted persistence.

---

## 69. Recovery Order

Recommended recovery sequence:

```text
Resolve authenticated user
→ Resolve global project context
→ Resolve route and workspace mode
→ Resolve selected object and version
→ Validate permissions
→ Fetch authoritative current state
→ Restore safe filters
→ Restore inspector/detail state
→ Restore unsent safe draft
```

---

## 70. Stale Restoration

If restored context points to a stale or superseded version:

* show historical state;
* identify current version;
* preserve user’s intended reference;
* do not silently redirect unless policy requires it;
* block consequential action against invalid version.

---

## 71. Mutation Recovery

If network state becomes uncertain after submission:

```text
Do not assume failure
→ Refetch authoritative object
→ Query action status if supported
→ Reconcile by idempotency key
→ Show confirmed result or unresolved state
```

---

# Part XVII — Loading, Partial, Error, and Offline Contract

## 72. Region-Level Loading

Page regions should load independently:

* shell;
* context;
* queue;
* object header;
* approval package;
* provenance;
* audit history;
* evaluation failures.

One failed secondary panel must not force a false full-page failure.

---

## 73. Partial State Model

```ts
type PartialDataState = {
  availableSections: string[]
  missingSections: string[]
  restrictedSections: string[]
  actionBlocked: boolean
  reason?: string
  retryable: boolean
}
```

---

## 74. Error Classification

Errors should be mapped to:

* network;
* unauthorized;
* forbidden;
* not found;
* version conflict;
* validation error;
* capability unavailable;
* backend partial failure;
* mutation uncertain;
* rate limited;
* server error;
* malformed response;
* unsupported legacy record.

---

## 75. Offline Restrictions

Offline mode may support:

* viewing approved cached safe data;
* drafting non-sensitive notes;
* local navigation.

Offline mode must not show as committed:

* approval;
* rejection;
* override;
* revocation;
* restriction;
* memory correction;
* evaluation launch;
* release decision.

---

# Part XVIII — Rendering and Performance

## 76. Performance Objectives

Unless the repository defines stricter budgets:

* interaction feedback: under 100 ms;
* selection-to-inspector skeleton: under 150 ms perceived;
* cached workspace transition: under 200 ms perceived;
* first meaningful workspace shell: under 1 second in normal development conditions;
* large queue scrolling: stable;
* graph interaction: target 60 FPS;
* no entire-page rerender for local inspector changes.

These are objectives, not unverified claims.

---

## 77. Data Scale Assumptions

Design should remain viable for at least:

```text
Attention items: 10,000+
Audit events: 100,000+
Memory objects: 10,000+
Provenance nodes per object: 1,000+
Evaluation runs: 10,000+
Failure examples per suite: 10,000+
```

Actual implementation should use server-side filtering and pagination rather than loading all records.

---

## 78. Virtualization

Use virtualization where required for:

* audit event tables;
* memory tables;
* attention queues;
* failure-example lists;
* large related-object lists.

Virtualization must preserve:

* keyboard access;
* row identity;
* selection;
* accessible labels;
* stable scroll behavior.

---

## 79. Lazy Loading

Lazy-load:

* deep provenance graph;
* raw audit payload;
* large diffs;
* evaluation failure details;
* secondary charts;
* export-generation UI.

Do not lazy-load essential decision context required before approval.

---

## 80. Bundle Discipline

Do not introduce a large graph, chart, state, or form dependency without:

* repository audit;
* bundle impact;
* reuse check;
* fallback evaluation;
* approval where required.

---

# Part XIX — Accessibility Contract

## 81. Accessibility Baseline

Target WCAG 2.2 AA or the repository’s approved standard.

Required:

* semantic landmarks;
* logical heading order;
* visible focus;
* keyboard navigation;
* no color-only meaning;
* status announcements;
* accessible tables;
* accessible diff;
* accessible timeline;
* graph alternative;
* reduced motion;
* sufficient contrast.

---

## 82. Governance Action Accessibility

Approval, rejection, request changes, and override must:

* expose exact action name;
* expose object and version;
* explain disabled state;
* announce mutation progress;
* announce confirmed completion;
* avoid keyboard shortcut accidents;
* preserve focus after errors.

---

## 83. Graph Accessibility

Provenance graph must have:

* ordered list or table fallback;
* keyboard-selectable nodes;
* text description of selected path;
* explicit relationships;
* no information available only on hover.

---

# Part XX — Observability

## 84. Client Logging

Safe technical logging may include:

* route load failure;
* query failure category;
* mutation failure category;
* version conflict;
* capability unavailable;
* graph rendering failure;
* performance marks;
* accessibility diagnostics in development.

Must not log:

* sensitive memory content;
* approval rationale;
* protected audit payload;
* scientific data not approved for telemetry;
* authorization tokens.

---

## 85. Product Analytics

Product analytics may track safe events such as:

* workspace opened;
* mode selected;
* approval package inspected;
* provenance opened;
* evaluation failure inspected;
* return-to-source used.

Analytics must not become scientific or governance truth.

---

## 86. Trace Correlation

Where supported, preserve:

* client request ID;
* backend request ID;
* job ID;
* mutation ID;
* audit event ID;
* provenance ID.

These identifiers should assist investigation without being exposed unnecessarily to ordinary users.

---

# Part XXI — Testing Contract

## 87. Test Layers

Required test categories:

1. type and schema tests;
2. adapter tests;
3. permission mapping tests;
4. state-machine tests;
5. query and mutation tests;
6. component tests;
7. interaction tests;
8. route and persistence tests;
9. accessibility tests;
10. responsive and visual regression tests;
11. end-to-end governance workflows;
12. backend contract tests where available.

---

## 88. Adapter Tests

Test:

* complete record;
* partial record;
* missing actor;
* missing version;
* restricted field;
* unknown enum;
* legacy event;
* malformed date;
* superseded object;
* unauthorized response;
* version conflict.

---

## 89. Approval Tests

Must test:

* authorized approval;
* unauthorized reviewer;
* version changed during review;
* incomplete package;
* rejection with reason;
* request changes;
* override with conditions;
* duplicate submission;
* timeout with uncertain result;
* revoked approval;
* expired approval;
* audit confirmation absent.

---

## 90. Memory Tests

Must test:

* active memory;
* stale memory;
* conflicting memory;
* restricted memory;
* superseded memory;
* correction creates new version;
* historical usage preserved;
* active affected objects identified;
* no sensitive leakage into URL or storage.

---

## 91. Audit Tests

Must test:

* chronological ordering;
* late-ingested event;
* retry event;
* correction event;
* unknown legacy actor;
* restricted payload;
* pagination;
* filtering;
* deep link;
* raw payload safety.

---

## 92. Provenance Tests

Must test:

* complete path;
* partial path;
* restricted node;
* missing parameter set;
* human edit;
* multiple tools;
* large graph;
* graph fallback;
* exact version link;
* stale external source.

---

## 93. Evaluation Tests

Must test:

* running job;
* partial result;
* failed run;
* cancelled run;
* invalid run;
* stale completion;
* baseline comparison;
* critical regression;
* aggregate improvement with critical failure;
* restricted release action;
* failure-example drill-down.

---

## 94. Cross-Page Tests

Verify:

* Page 01 opens correct governance item;
* Page 02 approval request resolves exact decision version;
* Page 03 memory correction resolves exact knowledge version;
* return-to-source preserves context;
* Page 04 action updates shared backend state;
* no local-only false propagation.

---

# Part XXII — Required Runtime Scenarios

## 95. Scenario A — Pending Approval

A complete approval request is opened by an authorized reviewer.

Expected:

* exact version visible;
* basis loaded;
* authority confirmed;
* approval submitted once;
* backend state confirmed;
* audit event linked.

---

## 96. Scenario B — Version Conflict

The target object changes while a reviewer is reading.

Expected:

* action blocked;
* notes preserved;
* diff shown;
* current server version identified;
* no stale approval submitted.

---

## 97. Scenario C — Incomplete Provenance

One required model parameter set is unavailable.

Expected:

* provenance marked partial;
* missing field explicit;
* reproducibility not verified;
* approval blocking behavior follows policy.

---

## 98. Scenario D — Stale Memory Impact

A memory object is superseded while active decisions depend on it.

Expected:

* old memory remains historical;
* new version visible;
* dependent objects listed;
* active warning propagated;
* no history rewrite.

---

## 99. Scenario E — Critical Evaluation Regression

A model version improves average performance but introduces hallucinated citations.

Expected:

* critical regression visible;
* aggregate improvement does not hide failure;
* release blocked;
* remediation or override path available.

---

## 100. Scenario F — Unauthorized Override

A user without override authority opens an override path.

Expected:

* protected information remains safe;
* action unavailable;
* reason visible;
* no local bypass.

---

## 101. Scenario G — Mutation Timeout

Approval request times out after submission.

Expected:

* success not assumed;
* idempotency key retained;
* authoritative state refetched;
* duplicate submission prevented;
* unresolved state shown if confirmation remains unavailable.

---

## 102. Scenario H — Legacy Audit Record

Historical event lacks actor role and parameter detail.

Expected:

* legacy state explicit;
* unknown fields not fabricated;
* event remains inspectable;
* completeness limitation visible.

---

## 103. Scenario I — Offline Review

User loses network while reviewing.

Expected:

* loaded safe content remains readable;
* notes preserved according to policy;
* approval disabled;
* no false completion;
* reconnection restores authoritative state.

---

## 104. Scenario J — Restricted Provenance

A provenance branch contains permission-restricted data.

Expected:

* restricted node shown safely;
* no content leak;
* chain remains understandable;
* export respects restriction.

---

# Part XXIII — Repository Safety

## 105. Allowed Autonomous Scope

Allowed:

* add Page 04 route;
* compose Page 04 workspaces;
* add Page 04 adapters and view models;
* integrate real governance APIs;
* add page-specific tests;
* extend shared components through approved extension points;
* add deterministic fixtures for development and tests;
* add accessibility and performance safeguards required by this page.

---

## 106. Forbidden Autonomous Scope

Without explicit approval:

* change backend approval semantics;
* change audit immutability;
* change global permission model;
* replace shared API client;
* duplicate shared domain types;
* introduce a Page 04-only design system;
* modify Page 01–03 workflow;
* create new scientific conclusions;
* create fake production governance data;
* add autonomous self-approval;
* expose restricted content;
* rewrite historical records;
* refactor unrelated code;
* add major dependencies;
* change global navigation architecture.

---

## 107. Fixture Policy

Fixtures must be:

* deterministic;
* typed;
* clearly named;
* isolated from production;
* disabled in production builds;
* representative of required runtime states;
* non-deceptive.

Production must never silently fall back to fixture data.

---

## 108. Existing User Work

Before modifying files:

* inspect git status;
* identify overlapping user changes;
* avoid overwriting;
* preserve unrelated edits;
* stop when safe merge is not possible.

---

# Part XXIV — Technical Decision Records

## 109. ADR Requirements

Create ADR for:

* new state-management approach;
* new graph dependency;
* protected shared-component change;
* new event transport;
* new persistence mechanism;
* new permission integration;
* major route architecture;
* cross-page contract change.

ADR format:

```yaml
id:
title:
status:
context:
constraints:
decision:
alternatives:
reason:
tradeoffs:
affected_files:
migration:
rollback:
approval:
```

---

## 110. DSR Requirements

Create DSR for:

* changed governance workflow;
* changed approval interaction;
* changed provenance visualization;
* changed trust-dimension representation;
* changed responsive behavior;
* changed historical-state treatment.

---

# Part XXV — Verification Commands

## 111. Required Verification

Use repository-native commands for:

* formatter;
* lint;
* typecheck;
* unit tests;
* component tests;
* integration tests;
* end-to-end tests;
* accessibility checks;
* production build;
* runtime route verification;
* bundle analysis where relevant.

Do not invent commands.

---

## 112. Verification Evidence

The completion report must record:

```yaml
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
  tests:
    command:
    result:
  build:
    command:
    result:
  runtime:
    route:
    result:
  accessibility:
    method:
    result:
  performance:
    method:
    result:
```

Unrun checks must be marked `NOT RUN`.

---

# Part XXVI — Technical Acceptance Gate

## 113. Architecture Gate

* [ ] Existing architecture reused
* [ ] Backend DTOs normalized through approved boundary
* [ ] State owners are explicit
* [ ] No competing domain store introduced
* [ ] Protected surfaces preserved
* [ ] Cross-page truth remains backend-authoritative

---

## 114. Governance Mutation Gate

* [ ] Actions target exact object and version
* [ ] Backend authority confirmed
* [ ] Idempotency handled
* [ ] Stale version blocked
* [ ] Success shown only after authoritative confirmation
* [ ] Failure preserves user work
* [ ] Audit confirmation available where required

---

## 115. Provenance Gate

* [ ] Stable node and edge identity
* [ ] Missing provenance explicit
* [ ] Restricted data protected
* [ ] Large graph controlled
* [ ] Accessible fallback provided
* [ ] Computational reproducibility not overstated

---

## 116. Audit Gate

* [ ] Audit is read-only by default
* [ ] Corrections create linked events
* [ ] Actor types remain distinct
* [ ] Retry and duplicate semantics visible
* [ ] Filters scale server-side
* [ ] Raw payload protected

---

## 117. Memory Gate

* [ ] Memory class, scope, source, and version visible
* [ ] Corrections create versions
* [ ] Historical usage preserved
* [ ] Sensitive content not leaked
* [ ] Affected active objects discoverable
* [ ] No hidden memory influence

---

## 118. Evaluation Gate

* [ ] Exact target and version
* [ ] Exact suite and baseline
* [ ] Long-running state handled
* [ ] Critical regression visible
* [ ] Failure examples inspectable
* [ ] Evaluation does not auto-authorize release
* [ ] Stale run cannot overwrite current run

---

## 119. Runtime Gate

* [ ] Loading, empty, partial, stale, offline, error, unauthorized, conflict, and historical states implemented
* [ ] Region failures isolated
* [ ] Route context restored safely
* [ ] Cross-page return context preserved
* [ ] No false committed mutation state
* [ ] No silent fixture fallback

---

## 120. Quality Gate

* [ ] Formatter passes
* [ ] Lint passes
* [ ] Typecheck passes
* [ ] Required tests pass
* [ ] Production build passes
* [ ] No unhandled runtime error
* [ ] Accessibility baseline passes
* [ ] Performance measured
* [ ] No critical regression

---

# Part XXVII — Critical Technical Failures

## 121. Release-Blocking Failures

Any one of the following blocks release:

* frontend grants approval authority;
* approval is not bound to exact version;
* optimistic UI displays unconfirmed approval as final;
* agent can approve its own output;
* historical audit event can be silently edited;
* memory correction overwrites prior version;
* restricted content leaks through UI, route, export, analytics, or logs;
* unknown provenance is fabricated;
* evaluation results are fabricated;
* critical regression is hidden by aggregate score;
* production silently uses fixtures;
* stale event overwrites current state;
* cross-page truth exists only in local frontend state;
* mutation timeout causes duplicate consequential action;
* build, typecheck, or critical tests fail;
* user work is lost during version conflict;
* unrelated repository code is modified without approval.

---

# Part XXVIII — Implementation Runtime

## 122. Mandatory Execution State Machine

```text
LOAD
Read repository rules, global contract, architecture, and Page 04 Specs
↓
RESOLVE
Build precedence map and conflict matrix
↓
INSPECT
Audit repository, backend capabilities, types, permissions, events, and tests
↓
MAP
Build requirement-to-component/API/test matrix
↓
PLAN
Define file changes, reuse targets, adapters, ADR/DSR, and rollback
↓
IMPLEMENT FOUNDATION
Route, context, adapters, state ownership, loading/error, permissions
↓
IMPLEMENT WORKSPACES
Attention, Approval, Provenance, Memory, Audit, Evaluation
↓
INTEGRATE
Real APIs, events, cross-page context, persistence, mutations
↓
VERIFY
Format, lint, typecheck, test, build, runtime, accessibility, performance
↓
ACCEPT
Execute technical, governance, scientific, and UI gates
↓
REGRESS
Prove no cross-page, backend, permission, component, or repository drift
↓
DELIVER
Emit factual completion report
↓
STOP
```

No state may be skipped.

---

## 123. Conditional Audit Gate

Implementation must pause when:

* real backend approval schema is absent or ambiguous;
* reviewer authority cannot be verified;
* audit immutability conflicts with requested UI;
* memory update semantics overwrite history;
* evaluation target or suite version is unknown;
* cross-page object identity is inconsistent;
* a protected surface requires modification;
* a major dependency is required;
* existing uncommitted changes overlap;
* permission behavior is unsafe;
* production would require fixture fallback;
* critical contract conflict remains unresolved.

Required report:

```yaml
blocked_requirement:
contract_rule:
repository_evidence:
affected_capability:
affected_files:
safe_options:
recommended_option:
tradeoffs:
decision_needed:
```

---

# Part XXIX — Completion Report

## 124. Required Output

```yaml
outcome:
release_decision: READY | NEEDS_REVISION | REJECTED

repository_audit:
  stack:
  router:
  state:
  api:
  auth:
  tests:
  protected_surfaces:

capability_matrix:
  attention:
  approvals:
  provenance:
  memory:
  audit:
  evaluation:
  affected_objects:
  exports:

files:
  created:
  modified:
  intentionally_untouched:

architecture:
  reused_components:
  extended_components:
  new_components:
  adapters:
  state_owners:
  route_contract:
  persistence:

backend_integration:
  queries:
  mutations:
  events:
  permissions:
  idempotency:
  limitations:

verification:
  format:
  lint:
  typecheck:
  tests:
  build:
  runtime:
  accessibility:
  performance:

acceptance:
  architecture:
  approval:
  provenance:
  audit:
  memory:
  evaluation:
  runtime:
  regression:
  critical_failures:

known_limitations:
deferred_capabilities:
decision_records:
```

No unverified claim may be marked as passed.

---

# Part XXX — Stop Condition

## 125. Final Stop Condition

```text
Repository Audit complete
AND Conflict Matrix resolved or explicitly accepted
AND Capability Matrix complete
AND Protected Surfaces preserved
AND State Ownership verified
AND Real API integration complete or unavailable states explicit
AND Governance mutations authoritative and idempotent
AND Approval version binding verified
AND Audit history protected
AND Memory versioning preserved
AND Provenance gaps explicit
AND Evaluation regressions handled
AND Cross-page integration verified
AND Accessibility PASS
AND Performance verified
AND Format PASS
AND Lint PASS
AND Typecheck PASS
AND Tests PASS
AND Production Build PASS
AND Critical Failure = 0
AND Completion Report emitted
→ READY
→ STOP
```

If correctable defects remain:

```text
NEEDS_REVISION
```

If a system invariant, scientific trust boundary, governance boundary, permission boundary, or repository protection rule is violated:

```text
REJECTED
```

After `READY`, implementation must stop immediately.

---

# Part XXXI — Technical Constitution

```text
Page 04 shall be implemented as a repository-safe governance control plane, not as a standalone dashboard.

The backend shall remain authoritative for governed objects, versions, permissions, approvals, audit events, provenance, memory, and evaluation results.

The frontend shall never grant authority, fabricate approval, fabricate provenance, fabricate evaluation, or rewrite history.

Every consequential action shall target an exact object and exact version.

Every consequential mutation shall be confirmed by authoritative backend state before being displayed as complete.

Audit history shall remain append-only from the product perspective.

Memory correction shall create a new version and preserve historical usage.

Provenance rendering shall expose missing and restricted stages explicitly.

Evaluation shall remain bound to an exact target, version, suite, baseline, and intended use.

Critical regression shall not be concealed by aggregate performance.

Page 04 state shall remain integrated with shared project, cycle, object, and cross-page context.

Restricted scientific, governance, and memory data shall not leak through UI, routes, storage, analytics, logs, exports, or related-object previews.

Production shall never silently use development fixtures.

The implementation shall reuse existing architecture, protect unrelated repository surfaces, and stop when safe implementation cannot be proven.

The page shall be released only when architecture, governance, permission, provenance, audit, memory, evaluation, runtime, accessibility, performance, testing, and regression gates all pass.
```

---

# Part XXXII — Final Technical Summary

The canonical implementation chain is:

```text
Authoritative Backend Object
→ Verified DTO
→ Adapter
→ Versioned Domain View Model
→ Permission-Aware Query State
→ Persistent Governance Workspace
→ Human Review
→ Version-Bound Mutation
→ Authoritative Confirmation
→ Audit Event
→ Cross-Page State Propagation
```

The implementation succeeds only when Page 04 can support:

```text
Inspect exact object
→ Reconstruct how it was produced
→ Verify memory and provenance
→ Determine who may act
→ Commit a governed decision safely
→ Confirm the real resulting state
→ Preserve immutable history
→ Evaluate outcome and regression
→ Propagate corrective action
```

without creating parallel truth, weakening backend authority, hiding missing information, leaking restricted content, fabricating governance state, or modifying unrelated repository architecture.
