import { api } from "./client";

/**
 * Unified Scientific Workflow Orchestrator adapter (harness/api/orchestrator.py).
 * `DiagnosisAdapter.start()`/`DesignAdapter.start()` (harness/orchestrator/
 * adapters.py) already auto-chain diagnosis (session -> hypotheses ->
 * decision) and design (handoff -> objectives -> strategies -> portfolio)
 * in one call each - this client exposes exactly those two calls plus
 * `createRun`, so a project can go from "just created" to "has a
 * candidate portfolio" without a human clicking through every stage of
 * the manual Diagnosis/Engineering-Design workbenches. Evaluation/
 * build/human-approval stay manual on purpose - those are the real,
 * required governance gates (see `record_human_gate_decision`), not
 * unwired automation.
 */
export interface WorkflowRun {
  workflowRunId: string;
  projectId: string;
  objectiveId: string | null;
  dbtlIterationId: string | null;
  status: string;
  currentPhase: string;
  currentModule: string | null;
  diagnosisRunRef: string | null;
  diagnosisHandoffRef: string | null;
  designProjectRef: string | null;
  designVersionRef: string | null;
  evaluationRunRef: string | null;
  simulationCampaignRef: string | null;
  experimentPlanRef: string | null;
  experimentRunRef: string | null;
  observationSetRef: string[];
  activeGateRef: string | null;
  pauseReason: string | null;
  blockedReason: string | null;
  checkpointRef: string | null;
  correlationId: string | null;
  createdAt: number;
  updatedAt: number;
  version: number;
}

interface RawRun {
  workflow_run_id: string; project_id: string; objective_id: string | null; dbtl_iteration_id: string | null;
  status: string; current_phase: string; current_module: string | null; diagnosis_run_ref: string | null;
  diagnosis_handoff_ref: string | null; design_project_ref: string | null; design_version_ref: string | null;
  evaluation_run_ref: string | null; simulation_campaign_ref: string | null; experiment_plan_ref: string | null;
  experiment_run_ref: string | null; observation_set_ref: string[]; active_gate_ref: string | null;
  pause_reason: string | null; blocked_reason: string | null; checkpoint_ref: string | null;
  correlation_id: string | null; created_at: number; updated_at: number; version: number;
}

function toRun(r: RawRun): WorkflowRun {
  return {
    workflowRunId: r.workflow_run_id, projectId: r.project_id, objectiveId: r.objective_id,
    dbtlIterationId: r.dbtl_iteration_id, status: r.status, currentPhase: r.current_phase,
    currentModule: r.current_module, diagnosisRunRef: r.diagnosis_run_ref, diagnosisHandoffRef: r.diagnosis_handoff_ref,
    designProjectRef: r.design_project_ref, designVersionRef: r.design_version_ref, evaluationRunRef: r.evaluation_run_ref,
    simulationCampaignRef: r.simulation_campaign_ref, experimentPlanRef: r.experiment_plan_ref,
    experimentRunRef: r.experiment_run_ref, observationSetRef: r.observation_set_ref, activeGateRef: r.active_gate_ref,
    pauseReason: r.pause_reason, blockedReason: r.blocked_reason, checkpointRef: r.checkpoint_ref,
    correlationId: r.correlation_id, createdAt: r.created_at, updatedAt: r.updated_at, version: r.version,
  };
}

/** `POST /api/orchestrator/runs`. */
export async function createRun(input: { projectId: string; actorId: string; targetProduct: string; host: string; dbtlIterationId?: string }): Promise<WorkflowRun> {
  const r = await api.post<RawRun>("/api/orchestrator/runs", {
    project_id: input.projectId, actor_id: input.actorId, target_product: input.targetProduct,
    host: input.host, dbtl_iteration_id: input.dbtlIterationId ?? null,
  });
  return toRun(r);
}

/** `GET /api/orchestrator/runs?project_id=` - most-recently-updated first. */
export async function listRuns(projectId: string): Promise<WorkflowRun[]> {
  const raw = await api.get<{ runs: RawRun[] }>(`/api/orchestrator/runs?project_id=${encodeURIComponent(projectId)}`);
  return raw.runs.map(toRun);
}

/** `GET /api/orchestrator/runs/{id}`. */
export async function getRun(workflowRunId: string): Promise<WorkflowRun> {
  const r = await api.get<RawRun>(`/api/orchestrator/runs/${workflowRunId}`);
  return toRun(r);
}

export interface StartDiagnosisInput {
  expectedVersion: number;
  actorId: string;
  biologicalSystem: Record<string, unknown>;
  phenotype: string;
  targetProduct: string;
  host: string;
  observationIds: string[];
  baselineObservationIds: string[];
  dataSufficiency: {
    hasBaseline: boolean; hasGenotype: boolean; hasCondition: boolean;
    hasTime: boolean; hasQc: boolean; hasKeyPhenotype: boolean;
  };
  context?: Record<string, unknown>;
}

/** `POST /api/orchestrator/runs/{id}/diagnosis` - auto-chains session creation
 * through hypothesis generation to a `DiagnosisDecision` in one call
 * (`DiagnosisAdapter.start()`/`_run_hypothesis_pipeline`), stopping only at
 * the legitimate `data_required`/`human_review_required` checkpoints. */
export async function startDiagnosis(workflowRunId: string, input: StartDiagnosisInput): Promise<WorkflowRun> {
  const r = await api.post<RawRun>(`/api/orchestrator/runs/${workflowRunId}/diagnosis`, {
    expected_version: input.expectedVersion, actor_id: input.actorId,
    request: {
      biological_system: input.biologicalSystem, phenotype: input.phenotype, target_product: input.targetProduct,
      host: input.host,
      observation_ids: input.observationIds,
      baseline_observation_ids: input.baselineObservationIds,
      data_sufficiency: {
        has_baseline: input.dataSufficiency.hasBaseline, has_genotype: input.dataSufficiency.hasGenotype,
        has_condition: input.dataSufficiency.hasCondition, has_time: input.dataSufficiency.hasTime,
        has_qc: input.dataSufficiency.hasQc, has_key_phenotype: input.dataSufficiency.hasKeyPhenotype,
      },
    },
    context: input.context ?? {},
  });
  return toRun(r);
}

export interface StartDesignInput {
  expectedVersion: number;
  actorId: string;
  chassis: string;
  chassisVersionOrGenotype: string;
  primaryMetrics: unknown[];
  hardConstraints: unknown[];
  availableResources?: Record<string, unknown>;
  context?: Record<string, unknown>;
}

/** `POST /api/orchestrator/runs/{id}/design` - auto-chains handoff ingestion
 * through objective confirmation, strategy generation, and portfolio
 * generation in one call (`DesignAdapter.start()`). */
export async function startDesign(workflowRunId: string, input: StartDesignInput): Promise<WorkflowRun> {
  const r = await api.post<RawRun>(`/api/orchestrator/runs/${workflowRunId}/design`, {
    expected_version: input.expectedVersion, actor_id: input.actorId,
    request: {
      chassis: input.chassis, chassis_version_or_genotype: input.chassisVersionOrGenotype,
      primary_metrics: input.primaryMetrics, hard_constraints: input.hardConstraints,
      available_resources: input.availableResources ?? {},
    },
    context: input.context ?? {},
  });
  return toRun(r);
}

/** `POST /api/orchestrator/runs/{id}/design/evaluate-portfolio`. */
export async function evaluateDesignPortfolio(workflowRunId: string, expectedVersion: number, actorId: string): Promise<WorkflowRun> {
  const r = await api.post<RawRun>(`/api/orchestrator/runs/${workflowRunId}/design/evaluate-portfolio`, {
    expected_version: expectedVersion, actor_id: actorId,
  });
  return toRun(r);
}

export interface OrchestratorTransitionRow {
  transitionId: string;
  fromPhase: string;
  toPhase: string;
  reason: string;
  actorId: string;
  createdAt: number;
}

/** `GET /api/orchestrator/runs/{id}/audit-trail` - transitions only (gate decisions omitted; not needed by this UI yet). */
export async function getAuditTrail(workflowRunId: string): Promise<OrchestratorTransitionRow[]> {
  const raw = await api.get<{ transitions: Array<{ transition_id: string; from_phase: string; to_phase: string; reason: string; actor_id: string; created_at: number }> }>(
    `/api/orchestrator/runs/${workflowRunId}/audit-trail`,
  );
  return raw.transitions.map((t) => ({ transitionId: t.transition_id, fromPhase: t.from_phase, toPhase: t.to_phase, reason: t.reason, actorId: t.actor_id, createdAt: t.created_at }));
}
