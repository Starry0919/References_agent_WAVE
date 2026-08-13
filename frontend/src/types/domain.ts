/**
 * Global scientific object / status / provenance vocabulary (design prompt
 * §12, §4A.2). Every page must import status and provenance labels from
 * here rather than inventing per-page synonyms - this is the single
 * front-end terminology contract.
 */

// ---- Terminology contract (prompt §4A.2) -----------------------------
// UI copy must use these exact stage/domain nouns; adapters translate
// backend-native names into them, never the reverse.
export const STAGE_LABEL = {
  diagnose: "Diagnose",
  design: "Design",
  simulate: "Simulate",
  critique: "Critique",
  build_test_plan: "Build / Test Plan",
} as const;

export type WorkspaceStageId = keyof typeof STAGE_LABEL;
export const WORKSPACE_STAGE_ORDER: WorkspaceStageId[] = [
  "diagnose",
  "design",
  "simulate",
  "critique",
  "build_test_plan",
];

// ---- Global object status vocabulary (prompt §12.2) -------------------
export type ObjectStatus =
  | "draft"
  | "generated"
  | "under_review"
  | "needs_revision"
  | "approved"
  | "rejected"
  | "active"
  | "completed"
  | "blocked"
  | "waiting_for_human"
  | "waiting_for_experiment"
  | "unavailable"
  | "out_of_domain"
  | "stale"
  | "superseded"
  | "failed";

// ---- Stage/gate status used by the Workflow Stage Rail (prompt §8.10) --
export type StageStatus =
  | "completed"
  | "active"
  | "blocked"
  | "needs_revision"
  | "waiting_for_human"
  | "waiting_for_experiment"
  | "stale"
  | "unavailable"
  | "not_started"
  | "skipped_with_reason";

// ---- Object provenance / source marker (prompt §12.1) ------------------
export type ObjectSource =
  | "human-entered"
  | "imported"
  | "rule-derived"
  | "llm-drafted"
  | "evidence-retrieved"
  | "model-generated"
  | "experimentally-observed"
  | "human-approved";

// ---- Backend capability availability (prompt §15.2 mapping matrix) -----
export type CapabilityAvailability = "available" | "partial" | "absent" | "unclear" | "blocked";

export interface CapabilityDescriptor {
  domain: string;
  availability: CapabilityAvailability;
  reason?: string;
  mockAllowed?: boolean;
}

// ---- Identity / provenance envelope every scientific object carries ----
// (prompt §4.1 "stable identity" fields). Adapters attach this alongside
// the module-specific payload rather than flattening it away.
export interface ObjectIdentity {
  id: string;
  projectId?: string;
  cycleId?: string;
  objectType: string;
  version?: number;
  status?: string;
  createdAt?: string | number;
  updatedAt?: string | number;
  actorId?: string;
  sourceRefs?: string[];
  stale?: boolean;
  approvalState?: string;
}

// ---- Project / Cycle summary (Command Center + Context Bar) ------------
export interface ProjectSummary {
  projectId: string;
  name: string;
  status: string;
  lifecycleStage: string;
}

export interface ProjectDetail extends ProjectSummary {
  targetProduct: string;
  hostDefinition: Record<string, unknown>;
  objectives: string[];
  constraints: string[];
  currentDesignVersionId: string | null;
  version: number;
  owners?: string[];
}

export interface CycleState {
  cycleStateId: string;
  currentState: string;
  status: string;
  pendingGate: string | null;
  activeDesignVersionId: string | null;
  activeExperimentPlanId: string | null;
  activeExperimentRunId: string | null;
  terminationReason: string | null;
}

export interface TimelineEvent {
  seq: number;
  eventId: string;
  eventType: string;
  entityType: string;
  entityId: string;
  actorType: string;
  actorId: string;
  timestamp: number;
}

// ---- Unified Workflow Orchestrator run (drives the Stage Rail) ---------
// Backend phase order is DIAGNOSIS -> DESIGN -> EVALUATION -> SIMULATION ->
// HUMAN_REVIEW -> WAITING_FOR_EXPERIMENT -> OBSERVATION_INGESTION ->
// LEARNING (deliberate backend sequencing, confirmed in
// harness/orchestrator/service.py). The frontend's fixed stage order is
// Diagnose -> Design -> Simulate -> Critique -> Build/Test Plan (prompt
// §II) - EVALUATION (backend) === Critique (frontend term). The rail must
// show real phase/gate history, not force a fabricated linear order.
export type OrchestratorPhase =
  | "INTAKE"
  | "CONTEXT_VALIDATION"
  | "DIAGNOSIS"
  | "DESIGN"
  | "EVALUATION"
  | "SIMULATION"
  | "HUMAN_REVIEW"
  | "WAITING_FOR_EXPERIMENT"
  | "OBSERVATION_INGESTION"
  | "LEARNING"
  | "REDESIGN"
  | "COMPLETED"
  | "BLOCKED"
  | "FAILED";

export type OrchestratorRunStatus =
  | "active"
  | "paused"
  | "waiting"
  | "blocked"
  | "completed"
  | "failed"
  | "cancelled";

export interface WorkflowRun {
  workflowRunId: string;
  projectId: string;
  objectiveId: string | null;
  dbtlIterationId: string | null;
  status: OrchestratorRunStatus;
  currentPhase: OrchestratorPhase;
  currentModule: string | null;
  diagnosisRunRef: string | null;
  diagnosisHandoffRef: string | null;
  designProjectRef: string | null;
  designVersionRef: string | null;
  evaluationRunRef: string | null;
  simulationCampaignRef: string | null;
  experimentPlanRef: string | null;
  experimentRunRef: string | null;
  activeGateRef: string | null;
  pauseReason: string | null;
  blockedReason: string | null;
  correlationId: string;
  createdAt: number;
  updatedAt: number;
  version: number;
}

// ---- Project status view (Command Center — harness/memory/views.py::
// build_project_status_view). Real, computed server-side from the live
// tables (current design/construct/learning-cycle pointers, latest design
// versions, open failure cases, QC summary, pending human gates, next-
// action hints). This is NOT a diagnosis-level "bottleneck" object — no
// read endpoint exists yet for `diag_bottleneck_value_assessments` (see
// docs/前端精修/page1_design_handoff.md) — so Command Center renders this
// view's `blockers` as ledger-level risk, not as a diagnosed bottleneck.
export interface QcSummary {
  totalObservations: number;
  passed: number;
  failed: number;
  pending: number;
}

export interface ProjectStatusView {
  projectId: string;
  lifecycleStage: string | null;
  activeDesignVersion: string | null;
  activeConstruct: string | null;
  activeLearningCycle: string | null;
  latestAcceptedResults: string[];
  waitingFor: string[];
  qcState: QcSummary | null;
  blockers: string[];
  pendingHumanGates: string[];
  nextActions: string[];
  lastMaterialChangeAt: number | null;
}

// ---- Trust & Provenance — Attention item (prompt §31) -------------------
// No backend attention-derivation endpoint exists (Repository Truth Audit /
// Page 4 capability matrix: `attention` = absent). Items here are derived
// client-side by `lib/attentionDerivation.ts` from real, already-fetched
// fields only (ProjectStatusView.blockers/pendingHumanGates/qcState,
// CycleState, WorkflowRun.blockedReason/pauseReason) via one documented,
// deterministic rule — never colored/randomly ordered (prompt §31 "不得由
// 颜色或前端随机排序定义"). This is explicitly a client-derived view, not a
// second governance truth: every item traces to the exact real field it
// came from and is labeled as such in the UI.
export type AttentionSeverity = "critical" | "high" | "medium" | "low";

export interface AttentionItem {
  id: string;
  issueType: "cycle_blocked" | "open_failure_case" | "pending_human_gate" | "qc_failure" | "workflow_run_blocked" | "workflow_run_paused";
  severity: AttentionSeverity;
  objectType: string;
  objectId: string;
  reason: string;
  sourcePage: "command-center" | "workspace";
  recommendedNextInspection: string;
}

// ---- Evidence (prompt §8.9 Evidence Drawer contract) --------------------
export interface EvidenceSummary {
  id: string;
  kind: "paper" | "ddr" | "biological_rule" | "model_result" | "observation" | "unknown";
  title: string;
  relation?: string;
  strainMatch?: "exact" | "partial" | "unknown" | "mismatch";
  conditionMatch?: "exact" | "partial" | "unknown" | "mismatch";
  quality?: string;
  sourceLink?: string;
  /** What `sourceLink` actually is, so the drawer can build a real route
   * (Literature Evidence tab vs Diagnose stage) instead of guessing -
   * see `harness.engineering_design.evidence_resolution`. Absent when the
   * item was never run through that resolver (kept optional so existing
   * producers of EvidenceSummary don't all need updating at once). */
  sourceLinkKind?: "paper" | "diagnosis_hypothesis" | "general_knowledge" | "unknown";
  /** Resolver commentary shown in place of a link when there isn't a real
   * one to give (e.g. "general engineering-knowledge pattern, not tied to
   * a specific paper") - never a fabricated citation. */
  note?: string;
  contradictory?: boolean;
}
