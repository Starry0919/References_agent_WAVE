import { api, ApiError } from "./client";

/**
 * ExperimentPlan/ExperimentRun adapter (harness/api/experiments.py, real,
 * uncommitted). Real gap, documented not worked around: `CreatePlanBody`
 * accepts `hypotheses_tested`/`controls`/`factors`/`response_variables`/
 * `acceptance_criteria`/`protocol_ref_id` at creation, but `GET /plans/{id}`
 * only returns `experiment_plan_id`/`project_id`/`design_version_ids`/
 * `approval_state` - those fields are stored but not serialized back by
 * this read route. Build/Test Plan renders them as explicitly unavailable.
 */
export interface ExperimentPlanSummary {
  experimentPlanId: string;
  projectId: string;
  designVersionIds: string[];
  approvalState: string;
}

export async function getExperimentPlan(experimentPlanId: string): Promise<ExperimentPlanSummary | null> {
  try {
    const r = await api.get<{ experiment_plan_id: string; project_id: string; design_version_ids: string[]; approval_state: string }>(
      `/api/experiments/plans/${experimentPlanId}`,
    );
    return { experimentPlanId: r.experiment_plan_id, projectId: r.project_id, designVersionIds: r.design_version_ids ?? [], approvalState: r.approval_state };
  } catch (e) {
    if (e instanceof ApiError && e.status === 404) return null;
    throw e;
  }
}

export interface ExperimentRunSummary {
  experimentRunId: string;
  experimentPlanId: string;
  executionStatus: string;
  deviations: string[];
}

export async function getExperimentRun(experimentRunId: string): Promise<ExperimentRunSummary | null> {
  try {
    const r = await api.get<{ experiment_run_id: string; experiment_plan_id: string; execution_status: string; deviations: string[] }>(
      `/api/experiments/runs/${experimentRunId}`,
    );
    return { experimentRunId: r.experiment_run_id, experimentPlanId: r.experiment_plan_id, executionStatus: r.execution_status, deviations: r.deviations ?? [] };
  } catch (e) {
    if (e instanceof ApiError && e.status === 404) return null;
    throw e;
  }
}

export interface ObservationSummary {
  observationId: string;
  metric: string;
  value: number;
  unit: string;
  conditionRef: Record<string, unknown>;
  qcStatus: string;
  sourceType: string;
  timepoint?: Record<string, unknown> | null;
}

function toObservation(o: {
  observation_id: string; metric: string; value: number; unit: string;
  condition_ref: Record<string, unknown>; qc_status: string; source_type: string;
  timepoint?: Record<string, unknown> | null;
}): ObservationSummary {
  return {
    observationId: o.observation_id, metric: o.metric, value: o.value, unit: o.unit,
    conditionRef: o.condition_ref ?? {}, qcStatus: o.qc_status, sourceType: o.source_type,
    timepoint: o.timepoint ?? null,
  };
}

/** Real measured readouts (Page 2 prompt §8.8 "measurements/readouts"). */
export async function getObservations(experimentRunId: string): Promise<ObservationSummary[]> {
  const r = await api.get<{
    observations: Array<{ observation_id: string; metric: string; value: number; unit: string; condition_ref: Record<string, unknown>; qc_status: string; source_type: string }>;
  }>(`/api/experiments/runs/${experimentRunId}/observations`);
  return r.observations.map(toObservation);
}

/** Persisted project measurements available for diagnosis grounding. */
export async function listProjectObservations(projectId: string): Promise<ObservationSummary[]> {
  const r = await api.get<{
    observations: Array<{
      observation_id: string; metric: string; value: number; unit: string;
      condition_ref: Record<string, unknown>; timepoint: Record<string, unknown> | null;
      qc_status: string; source_type: string;
    }>;
  }>(`/api/experiments/observations?project_id=${encodeURIComponent(projectId)}`);
  return r.observations.map(toObservation);
}
