import { api } from "./client";
import type { CycleState, ProjectDetail, ProjectStatusView, ProjectSummary, TimelineEvent } from "@/types/domain";

/**
 * Typed adapter over harness/api/projects.py (real, committed backend
 * router - Repository Truth Audit confirmed `GET/POST /api/projects*`
 * live and covered by the 341-test baseline). Field names here are
 * camelCase view-model names; the raw backend response is snake_case -
 * this file is the single place that translation happens (prompt §15.3).
 */

interface RawProjectSummary {
  project_id: string;
  name: string;
  status: string;
  lifecycle_stage: string;
}

interface RawProjectDetail {
  project_id: string;
  name: string;
  target_product: string;
  host_definition: Record<string, unknown>;
  objectives: string[];
  constraints: string[];
  status: string;
  lifecycle_stage: string;
  current_design_version_id: string | null;
  version: number;
  owners?: string[];
}

interface RawCycleState {
  cycle_state_id: string;
  current_state: string;
  status: string;
  pending_gate: string | null;
  active_design_version_id: string | null;
  active_experiment_plan_id: string | null;
  active_experiment_run_id: string | null;
  termination_reason: string | null;
}

interface RawTimelineEvent {
  seq: number;
  event_id: string;
  event_type: string;
  entity_type: string;
  entity_id: string;
  actor_type: string;
  actor_id: string;
  timestamp: number;
}

function toProjectSummary(r: RawProjectSummary): ProjectSummary {
  return { projectId: r.project_id, name: r.name, status: r.status, lifecycleStage: r.lifecycle_stage };
}

function toProjectDetail(r: RawProjectDetail): ProjectDetail {
  return {
    projectId: r.project_id,
    name: r.name,
    status: r.status,
    lifecycleStage: r.lifecycle_stage,
    targetProduct: r.target_product,
    hostDefinition: r.host_definition,
    objectives: r.objectives,
    constraints: r.constraints,
    currentDesignVersionId: r.current_design_version_id,
    version: r.version,
    owners: r.owners,
  };
}

function toCycleState(r: RawCycleState): CycleState {
  return {
    cycleStateId: r.cycle_state_id,
    currentState: r.current_state,
    status: r.status,
    pendingGate: r.pending_gate,
    activeDesignVersionId: r.active_design_version_id,
    activeExperimentPlanId: r.active_experiment_plan_id,
    activeExperimentRunId: r.active_experiment_run_id,
    terminationReason: r.termination_reason,
  };
}

function toTimelineEvent(r: RawTimelineEvent): TimelineEvent {
  return {
    seq: r.seq,
    eventId: r.event_id,
    eventType: r.event_type,
    entityType: r.entity_type,
    entityId: r.entity_id,
    actorType: r.actor_type,
    actorId: r.actor_id,
    timestamp: r.timestamp,
  };
}

export async function listProjects(): Promise<ProjectSummary[]> {
  const res = await api.get<{ projects: RawProjectSummary[] }>("/api/projects");
  return res.projects.map(toProjectSummary);
}

export async function getProject(projectId: string): Promise<ProjectDetail> {
  const res = await api.get<RawProjectDetail>(`/api/projects/${projectId}`);
  return toProjectDetail(res);
}

export async function getProjectStatus(projectId: string): Promise<Record<string, unknown>> {
  // build_project_status_view() shape is intentionally left as a typed
  // "unknown-but-real" record - the Command Center handoff (Deliverable 6)
  // flags formalizing this view model as Page 1 detailed-design input.
  return api.get<Record<string, unknown>>(`/api/projects/${projectId}/status`);
}

// ---- Typed Project Status View (Page 1 Command Center) --------------------
// Field names below mirror harness/memory/views.py::build_project_status_view
// exactly (confirmed by reading the real function, not guessed from the
// route). Formalizes the "Page 1 detailed-design input" flagged above:
// getProjectStatus() above stays as the raw passthrough; this is the typed
// view the Command Center actually renders.
interface RawQcState {
  total_observations: number;
  passed: number;
  failed: number;
  pending: number;
}

interface RawProjectStatusView {
  project_id: string;
  lifecycle_stage: string | null;
  active_design_version: string | null;
  active_construct: string | null;
  active_learning_cycle: string | null;
  latest_accepted_results: string[];
  waiting_for: string[];
  qc_state: RawQcState | null;
  blockers: string[];
  pending_human_gates: string[];
  next_actions: string[];
  last_material_change_at: number | null;
}

function toProjectStatusView(r: RawProjectStatusView): ProjectStatusView {
  return {
    projectId: r.project_id,
    lifecycleStage: r.lifecycle_stage ?? null,
    activeDesignVersion: r.active_design_version,
    activeConstruct: r.active_construct,
    activeLearningCycle: r.active_learning_cycle,
    latestAcceptedResults: r.latest_accepted_results ?? [],
    waitingFor: r.waiting_for ?? [],
    qcState: r.qc_state
      ? {
          totalObservations: r.qc_state.total_observations,
          passed: r.qc_state.passed,
          failed: r.qc_state.failed,
          pending: r.qc_state.pending,
        }
      : null,
    blockers: r.blockers ?? [],
    pendingHumanGates: r.pending_human_gates ?? [],
    nextActions: r.next_actions ?? [],
    lastMaterialChangeAt: r.last_material_change_at ?? null,
  };
}

export async function getProjectStatusView(projectId: string): Promise<ProjectStatusView> {
  const res = await api.get<RawProjectStatusView>(`/api/projects/${projectId}/status`);
  return toProjectStatusView(res);
}

export async function getActiveCycle(projectId: string): Promise<CycleState | null> {
  try {
    const res = await api.get<RawCycleState>(`/api/projects/${projectId}/cycle`);
    return toCycleState(res);
  } catch (e) {
    if (e instanceof Error && "status" in e && (e as { status?: number }).status === 404) return null;
    throw e;
  }
}

export async function getTimeline(projectId: string): Promise<TimelineEvent[]> {
  const res = await api.get<{ events: RawTimelineEvent[] }>(`/api/projects/${projectId}/timeline`);
  return res.events.map(toTimelineEvent);
}

export interface CreateProjectInput {
  name: string;
  targetProduct: string;
  objectives: string[];
  constraints: string[];
  actorId: string;
  hostDefinition?: Record<string, unknown>;
}

export async function createProject(input: CreateProjectInput): Promise<ProjectSummary> {
  const res = await api.post<RawProjectSummary & { version: number }>("/api/projects", {
    name: input.name,
    target_product: input.targetProduct,
    objectives: input.objectives,
    constraints: input.constraints,
    actor_id: input.actorId,
    host_definition: input.hostDefinition ?? {},
  });
  return toProjectSummary(res);
}

/** PATCH /api/projects/{project_id} (real, added alongside this rename UI). */
export async function renameProject(projectId: string, name: string, actorId = "frontend-user"): Promise<ProjectSummary> {
  const res = await api.patch<RawProjectSummary & { version: number }>(`/api/projects/${projectId}`, {
    name,
    actor_id: actorId,
  });
  return toProjectSummary(res);
}

export async function updateProjectContext(
  projectId: string,
  input: {
    hostDefinition: Record<string, unknown>;
    targetProduct: string;
    objectives: string[];
    constraints: string[];
    expectedVersion?: number;
  },
): Promise<ProjectDetail> {
  const res = await api.patch<RawProjectDetail>(`/api/projects/${projectId}`, {
    host_definition: input.hostDefinition,
    target_product: input.targetProduct,
    objectives: input.objectives,
    constraints: input.constraints,
    expected_version: input.expectedVersion,
    actor_id: "frontend-user",
  });
  return toProjectDetail(res);
}

/**
 * DELETE /api/projects/{project_id} (real, added alongside this delete UI).
 * Backend cascades across every project-scoped table it defines
 * (`harness.projects.service.delete_project`) - see that function's own
 * docstring for exactly what is and is not chased.
 */
export async function deleteProject(projectId: string): Promise<void> {
  await api.delete<{ deleted: boolean; project_id: string }>(`/api/projects/${projectId}`);
}
