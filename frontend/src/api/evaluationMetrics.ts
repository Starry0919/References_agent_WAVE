import { api, ApiError } from "./client";

/**
 * 260718 设计文档 §7 (验证方式) evaluation-metrics adapter
 * (harness/api/evaluation_metrics.py, harness/evaluation_metrics/*).
 * Every metric mirrors the backend's `{value, numerator, denominator,
 * applicable, note}` shape - `applicable=false` means "not enough data to
 * compute this yet", never a fabricated 0/1 (harness/golden_set/metrics.py's
 * `_metric()` convention, reused here).
 */

export interface MetricResult {
  value: number | null;
  numerator: number;
  denominator: number;
  applicable: boolean;
  note: string;
}

export interface CoverageByClassEntry {
  strategyClass: string;
  status: "covered" | "excluded" | "missing";
  reason: string;
}

export interface CoverageCompletenessMetric extends MetricResult {
  coverageByClass: CoverageByClassEntry[];
}

export interface ReasonedNoveltyMetric extends MetricResult {
  novelGroundedGenes: string[];
}

export interface EvaluationMetricsSummary {
  designProjectId: string;
  process: {
    groundingRate: MetricResult;
    coverageCompleteness: CoverageCompletenessMetric;
  };
  capability: {
    screeningAbility: MetricResult;
    reasonedNovelty: ReasonedNoveltyMetric;
  };
  sanityCheck: {
    reproductionRate: MetricResult;
  };
}

export interface DesignProjectSummary {
  designProjectId: string;
  status: string;
  referenceDdrIds: string[];
  createdAt: number;
}

export interface ConsistencySample {
  sampleIndex: number;
  fallbackUsed: boolean;
  strategies: Array<{ strategyClass: string; mechanismTarget: string }>;
}

export interface ConsistencyByClass {
  strategyClass: string;
  sampleCount: number;
  convergence: number;
}

export interface ConsistencyRun {
  runId: string;
  designProjectId: string;
  nSamples: number;
  samples: ConsistencySample[];
  convergenceReport: {
    samplesWithOutput: number;
    samplesWithOutputRate: number;
    byStrategyClass: ConsistencyByClass[];
    note: string;
  };
  createdBy: string;
  createdAt: number;
}

interface RawMetricResult {
  value: number | null;
  numerator: number;
  denominator: number;
  applicable: boolean;
  note: string;
}

function toMetric(r: RawMetricResult): MetricResult {
  return { value: r.value, numerator: r.numerator, denominator: r.denominator, applicable: r.applicable, note: r.note ?? "" };
}

interface RawCoverageByClassEntry {
  strategy_class: string;
  status: "covered" | "excluded" | "missing";
  reason: string;
}

interface RawCoverageCompletenessMetric extends RawMetricResult {
  coverage_by_class: RawCoverageByClassEntry[];
}

interface RawReasonedNoveltyMetric extends RawMetricResult {
  novel_grounded_genes: string[];
}

interface RawEvaluationMetricsSummary {
  design_project_id: string;
  process: { grounding_rate: RawMetricResult; coverage_completeness: RawCoverageCompletenessMetric };
  capability: { screening_ability: RawMetricResult; reasoned_novelty: RawReasonedNoveltyMetric };
  sanity_check: { reproduction_rate: RawMetricResult };
}

function toSummary(r: RawEvaluationMetricsSummary): EvaluationMetricsSummary {
  return {
    designProjectId: r.design_project_id,
    process: {
      groundingRate: toMetric(r.process.grounding_rate),
      coverageCompleteness: {
        ...toMetric(r.process.coverage_completeness),
        coverageByClass: r.process.coverage_completeness.coverage_by_class.map((c) => ({
          strategyClass: c.strategy_class,
          status: c.status,
          reason: c.reason,
        })),
      },
    },
    capability: {
      screeningAbility: toMetric(r.capability.screening_ability),
      reasonedNovelty: {
        ...toMetric(r.capability.reasoned_novelty),
        novelGroundedGenes: r.capability.reasoned_novelty.novel_grounded_genes ?? [],
      },
    },
    sanityCheck: {
      reproductionRate: toMetric(r.sanity_check.reproduction_rate),
    },
  };
}

interface RawDesignProjectSummary {
  design_project_id: string;
  status: string;
  reference_ddr_ids: string[];
  created_at: number;
}

/** `GET /api/evaluation-metrics/by-project/{project_id}` (harness/api/evaluation_metrics.py::list_design_projects_for_project) - resolves the outer project id (the frontend route param) to its engineering-design project row(s), newest first. */
export async function listDesignProjectsForProject(projectId: string): Promise<DesignProjectSummary[]> {
  const raw = await api.get<{ design_projects: RawDesignProjectSummary[] }>(`/api/evaluation-metrics/by-project/${projectId}`);
  return raw.design_projects.map((r) => ({
    designProjectId: r.design_project_id, status: r.status, referenceDdrIds: r.reference_ddr_ids, createdAt: r.created_at,
  }));
}

/** `GET /api/evaluation-metrics/projects/{design_project_id}/summary` - null if the design project does not exist (404). */
export async function getMetricsSummary(designProjectId: string): Promise<EvaluationMetricsSummary | null> {
  try {
    const raw = await api.get<RawEvaluationMetricsSummary>(`/api/evaluation-metrics/projects/${designProjectId}/summary`);
    return toSummary(raw);
  } catch (e) {
    if (e instanceof ApiError && e.status === 404) return null;
    throw e;
  }
}

/** `POST /api/evaluation-metrics/projects/{design_project_id}/reference-ddr` - links this design project to its source paper's DDR id(s), enabling 合理新颖/复现率. */
export async function setReferenceDdr(designProjectId: string, ddrIds: string[]): Promise<string[]> {
  const raw = await api.post<{ reference_ddr_ids: string[] }>(`/api/evaluation-metrics/projects/${designProjectId}/reference-ddr`, { ddr_ids: ddrIds });
  return raw.reference_ddr_ids;
}

function toConsistencyRun(r: {
  run_id: string; design_project_id: string; n_samples: number;
  samples: Array<{ sample_index: number; fallback_used: boolean; strategies: Array<{ strategy_class: string; mechanism_target: string }> }>;
  convergence_report: { samples_with_output: number; samples_with_output_rate: number; by_strategy_class: Array<{ strategy_class: string; sample_count: number; convergence: number }>; note: string };
  created_by: string; created_at: number;
}): ConsistencyRun {
  return {
    runId: r.run_id, designProjectId: r.design_project_id, nSamples: r.n_samples,
    samples: r.samples.map((s) => ({ sampleIndex: s.sample_index, fallbackUsed: s.fallback_used, strategies: s.strategies.map((st) => ({ strategyClass: st.strategy_class, mechanismTarget: st.mechanism_target })) })),
    convergenceReport: {
      samplesWithOutput: r.convergence_report.samples_with_output,
      samplesWithOutputRate: r.convergence_report.samples_with_output_rate,
      byStrategyClass: r.convergence_report.by_strategy_class.map((c) => ({ strategyClass: c.strategy_class, sampleCount: c.sample_count, convergence: c.convergence })),
      note: r.convergence_report.note,
    },
    createdBy: r.created_by, createdAt: r.created_at,
  };
}

/** `POST /api/evaluation-metrics/projects/{design_project_id}/consistency-runs` - draws n_samples independent LLM samples of the same design task; each call is a real model request (see harness/evaluation_metrics/consistency_sampler.py), so keep n_samples modest. */
export async function runConsistencySample(designProjectId: string, nSamples: number, actorId: string): Promise<ConsistencyRun> {
  const raw = await api.post<Parameters<typeof toConsistencyRun>[0]>(`/api/evaluation-metrics/projects/${designProjectId}/consistency-runs`, { n_samples: nSamples, actor_id: actorId });
  return toConsistencyRun(raw);
}

/** `GET /api/evaluation-metrics/projects/{design_project_id}/consistency-runs` - most recent first. */
export async function listConsistencyRuns(designProjectId: string): Promise<ConsistencyRun[]> {
  const raw = await api.get<{ runs: Parameters<typeof toConsistencyRun>[0][] }>(`/api/evaluation-metrics/projects/${designProjectId}/consistency-runs`);
  return raw.runs.map(toConsistencyRun);
}
