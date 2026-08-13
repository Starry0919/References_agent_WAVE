import { api } from "./client";

/**
 * Bottleneck Diagnosis Loop adapter (harness/api/diagnosis.py, doc03 §9).
 * Unlike engineering-design, most *content* here (hypotheses, tests,
 * decisions) is produced by `harness/orchestrator/adapters.py` driving the
 * service layer directly - the HTTP surface only exposes read access to
 * that content plus the narrow set of human-in-the-loop writes the router
 * actually defines (create session, link evidence, run a model, approve a
 * decision, and the pure state-transition `action` endpoint). Do not add
 * "generate hypotheses"/"create test" calls here - no such route exists.
 */

export interface DiagnosisSessionSummary {
  diagnosisSessionId: string;
  projectId: string;
  status: string;
  dataSufficiency: string;
  approvalState: string;
  biologicalSystem: Record<string, unknown>;
  createdAt: number;
  updatedAt: number;
}

export interface DiagnosisSessionDetail {
  diagnosisSessionId: string;
  projectId: string;
  status: string;
  dataSufficiency: string;
  approvalState: string;
  activeHypothesisSetVersion: number;
  biologicalSystem: Record<string, unknown>;
  baselineObservationIds: string[];
  version: number;
}

export interface ObservationGrounding {
  status: "grounded" | "data_required";
  blockingReasons: string[];
  observationIds: string[];
  engineeringProblemIds: string[];
  policyVersion: string;
  actionable: boolean;
}

export interface EngineeringProblemRow {
  engineeringProblemId: string;
  metric: string;
  observedValue: number;
  expectedValue: number;
  unit: string;
  delta: number;
  abnormalityStatement: string;
  observationIds: string[];
  comparisonObservationIds: string[];
  status: string;
}

export async function getObservationGrounding(diagnosisSessionId: string): Promise<ObservationGrounding> {
  const r = await api.get<{ status: "grounded" | "data_required"; blocking_reasons: string[]; observation_ids: string[]; engineering_problem_ids: string[]; policy_version: string; actionable: boolean }>(`/api/diagnosis/sessions/${diagnosisSessionId}/grounding`);
  return { status: r.status, blockingReasons: r.blocking_reasons, observationIds: r.observation_ids, engineeringProblemIds: r.engineering_problem_ids, policyVersion: r.policy_version, actionable: r.actionable };
}

export async function listEngineeringProblems(diagnosisSessionId: string): Promise<EngineeringProblemRow[]> {
  const r = await api.get<{ engineering_problems: Array<{ engineering_problem_id: string; metric: string; observed_value: number; expected_value: number; unit: string; delta: number; abnormality_statement: string; observation_ids: string[]; comparison_observation_ids: string[]; status: string }> }>(`/api/diagnosis/sessions/${diagnosisSessionId}/engineering-problems`);
  return r.engineering_problems.map((p) => ({ engineeringProblemId: p.engineering_problem_id, metric: p.metric, observedValue: p.observed_value, expectedValue: p.expected_value, unit: p.unit, delta: p.delta, abnormalityStatement: p.abnormality_statement, observationIds: p.observation_ids, comparisonObservationIds: p.comparison_observation_ids, status: p.status }));
}

export interface HypothesisRow {
  hypothesisVersionId: string;
  status: string;
  mechanismClass: string | null;
  statement: string | null;
  explanatoryCoverage: Record<string, unknown>;
  contradictions: unknown[];
  // Module 2 §7/§9: computed by the backend generator all along, but never
  // returned by this route until now (harness/api/diagnosis.py::list_hypotheses).
  falsifiers: string[];
  omicsLayers: string[];
}

// Module 2 §8: the Engineering Reasoning Graph, read-only (recomputed on
// demand server-side - harness/api/diagnosis.py::get_mechanism_graph).
export interface MechanismGraphNode {
  nodeId: string;
  nodeType: string;
  label: string;
  source: string;
}

export interface MechanismGraphEdge {
  sourceId: string;
  targetId: string;
  edgeType: string;
  sourceRef: string;
  applicabilityContext: Record<string, unknown>;
  isUnknownOrConflicting: boolean;
}

export interface MechanismGraph {
  nodes: MechanismGraphNode[];
  edges: MechanismGraphEdge[];
  unknowns: string[];
}

export type EvidenceReviewStatus = "unreviewed" | "confirmed" | "incorrect";

export interface EvidenceLinkRow {
  evidenceLinkId: string;
  hypothesisVersionId: string;
  evidenceItemId: string;
  relation: string;
  claim: string;
  reviewStatus: EvidenceReviewStatus;
  reviewNote: string;
}

export interface EvidenceItemRow {
  evidenceItemId: string;
  sourceType: string;
  sourceReference: string | null;
  contentSummary: string;
  quality: string;
  directness: string;
  createdAt: number;
}

export interface ModelCapability {
  available: boolean;
  reason: string;
}

export interface ModelRunResult {
  modelRunId: string;
  capabilityStatus: string;
  runtimeStatus: string;
  outputs: Record<string, unknown>;
  logSummary: string;
}

export interface DiagnosticTestRow {
  testId: string;
  assay: string;
  status: string;
  discriminatesHypotheses: boolean;
  expectedInformationGain: string;
  plans: Array<{ planId: string; readiness: string }>;
}

export interface DecisionRow {
  decisionId: string;
  diagnosisVersion: number;
  stoppingReason: string;
  allowedNextAction: string;
  handoffStatus: string;
  leadingHypothesisIds: string[];
  alternativesNotExcludedIds: string[];
}

export interface DiagnosisTransitionRow {
  state: string;
  selectedNextState: string | null;
  gateResult: Record<string, unknown> | null;
  startedAt: number;
}

export interface ReportSection {
  title: string;
  content: Record<string, unknown>;
  traceIds: string[];
}

function toSessionSummary(r: {
  diagnosis_session_id: string; project_id: string; status: string; data_sufficiency: string;
  approval_state: string; biological_system: Record<string, unknown>; created_at: number; updated_at: number;
}): DiagnosisSessionSummary {
  return {
    diagnosisSessionId: r.diagnosis_session_id, projectId: r.project_id, status: r.status,
    dataSufficiency: r.data_sufficiency, approvalState: r.approval_state,
    biologicalSystem: r.biological_system, createdAt: r.created_at, updatedAt: r.updated_at,
  };
}

/** `GET /api/diagnosis/sessions?project_id=` - newest first. */
export async function listSessionsForProject(projectId: string): Promise<DiagnosisSessionSummary[]> {
  const raw = await api.get<{ sessions: Parameters<typeof toSessionSummary>[0][] }>(
    `/api/diagnosis/sessions?project_id=${encodeURIComponent(projectId)}`,
  );
  return raw.sessions.map(toSessionSummary);
}

export interface CreateSessionInput {
  projectId: string;
  actorId: string;
  workflowRunId?: string;
  triggeringFailureCaseId?: string;
  objectiveId?: string;
  biologicalSystem?: Record<string, unknown>;
  baselineObservationIds?: string[];
}

/** `POST /api/diagnosis/sessions`. */
export async function createSession(input: CreateSessionInput): Promise<{ diagnosisSessionId: string; status: string }> {
  const raw = await api.post<{ diagnosis_session_id: string; status: string }>("/api/diagnosis/sessions", {
    project_id: input.projectId, actor_id: input.actorId, workflow_run_id: input.workflowRunId ?? null,
    triggering_failure_case_id: input.triggeringFailureCaseId ?? null, objective_id: input.objectiveId ?? null,
    biological_system: input.biologicalSystem ?? {}, baseline_observation_ids: input.baselineObservationIds ?? [],
  });
  return { diagnosisSessionId: raw.diagnosis_session_id, status: raw.status };
}

/** `GET /api/diagnosis/sessions/{id}`. */
export async function getSession(diagnosisSessionId: string): Promise<DiagnosisSessionDetail> {
  const r = await api.get<{
    diagnosis_session_id: string; project_id: string; status: string; data_sufficiency: string;
    approval_state: string; active_hypothesis_set_version: number; biological_system: Record<string, unknown>;
    baseline_observation_ids: string[]; version: number;
  }>(`/api/diagnosis/sessions/${diagnosisSessionId}`);
  return {
    diagnosisSessionId: r.diagnosis_session_id, projectId: r.project_id, status: r.status,
    dataSufficiency: r.data_sufficiency, approvalState: r.approval_state,
    activeHypothesisSetVersion: r.active_hypothesis_set_version, biologicalSystem: r.biological_system,
    baselineObservationIds: r.baseline_observation_ids, version: r.version,
  };
}

/** `GET /api/diagnosis/sessions/{id}/hypotheses`. */
export async function listHypotheses(diagnosisSessionId: string): Promise<HypothesisRow[]> {
  const raw = await api.get<{
    hypotheses: Array<{
      hypothesis_version_id: string; status: string; mechanism_class: string | null; statement: string | null;
      explanatory_coverage: Record<string, unknown>; contradictions: unknown[];
      falsifiers?: string[]; omics_layers?: string[];
    }>;
  }>(`/api/diagnosis/sessions/${diagnosisSessionId}/hypotheses`);
  return raw.hypotheses.map((h) => ({
    hypothesisVersionId: h.hypothesis_version_id, status: h.status, mechanismClass: h.mechanism_class,
    statement: h.statement, explanatoryCoverage: h.explanatory_coverage, contradictions: h.contradictions,
    falsifiers: h.falsifiers ?? [], omicsLayers: h.omics_layers ?? [],
  }));
}

/** `GET /api/diagnosis/sessions/{id}/mechanism-graph`. */
export async function getMechanismGraph(diagnosisSessionId: string): Promise<MechanismGraph> {
  const raw = await api.get<{
    nodes: Array<{ node_id: string; node_type: string; label: string; source: string }>;
    edges: Array<{
      source_id: string; target_id: string; edge_type: string; source_ref: string;
      applicability_context: Record<string, unknown>; is_unknown_or_conflicting: boolean;
    }>;
    unknowns: string[];
  }>(`/api/diagnosis/sessions/${diagnosisSessionId}/mechanism-graph`);
  return {
    nodes: raw.nodes.map((n) => ({ nodeId: n.node_id, nodeType: n.node_type, label: n.label, source: n.source })),
    edges: raw.edges.map((e) => ({
      sourceId: e.source_id, targetId: e.target_id, edgeType: e.edge_type, sourceRef: e.source_ref,
      applicabilityContext: e.applicability_context, isUnknownOrConflicting: e.is_unknown_or_conflicting,
    })),
    unknowns: raw.unknowns,
  };
}

/** `GET /api/diagnosis/sessions/{id}/evidence`. */
export async function listEvidence(diagnosisSessionId: string): Promise<EvidenceLinkRow[]> {
  const raw = await api.get<{
    evidence_links: Array<{
      evidence_link_id: string; hypothesis_version_id: string; evidence_item_id: string; relation: string; claim: string;
      review_status: EvidenceReviewStatus; review_note: string;
    }>;
  }>(`/api/diagnosis/sessions/${diagnosisSessionId}/evidence`);
  return raw.evidence_links.map((e) => ({
    evidenceLinkId: e.evidence_link_id, hypothesisVersionId: e.hypothesis_version_id,
    evidenceItemId: e.evidence_item_id, relation: e.relation, claim: e.claim,
    reviewStatus: e.review_status, reviewNote: e.review_note,
  }));
}

/** `POST /api/diagnosis/evidence-links/{id}/review` - a human's spot-check of an
 * agent-created link; purely an audit annotation, never gates the diagnosis loop. */
export async function reviewEvidenceLink(evidenceLinkId: string, verdict: "confirmed" | "incorrect", actorId: string, note = ""): Promise<void> {
  await api.post(`/api/diagnosis/evidence-links/${evidenceLinkId}/review`, { verdict, actor_id: actorId, note });
}

export interface LinkEvidenceInput {
  hypothesisVersionId: string;
  evidenceItemId: string;
  relation: string;
  actorId: string;
  claim?: string;
  conditionMatch?: string;
}

/** `POST /api/diagnosis/evidence-links`. */
export async function linkEvidence(input: LinkEvidenceInput): Promise<string> {
  const raw = await api.post<{ evidence_link_id: string }>("/api/diagnosis/evidence-links", {
    hypothesis_version_id: input.hypothesisVersionId, evidence_item_id: input.evidenceItemId,
    relation: input.relation, actor_id: input.actorId, claim: input.claim ?? "",
    condition_match: input.conditionMatch ?? "unknown",
  });
  return raw.evidence_link_id;
}

/** `GET /api/diagnosis/evidence-items?project_id=` - existing evidence items available to link
 * against a hypothesis, so the UI can offer a picker instead of a free-text id field. */
export async function listEvidenceItems(projectId: string): Promise<EvidenceItemRow[]> {
  const raw = await api.get<{
    evidence_items: Array<{
      evidence_item_id: string; source_type: string; source_reference: string | null;
      content_summary: string; quality: string; directness: string; created_at: number;
    }>;
  }>(`/api/diagnosis/evidence-items?project_id=${encodeURIComponent(projectId)}`);
  return raw.evidence_items.map((e) => ({
    evidenceItemId: e.evidence_item_id, sourceType: e.source_type, sourceReference: e.source_reference,
    contentSummary: e.content_summary, quality: e.quality, directness: e.directness, createdAt: e.created_at,
  }));
}

export interface CreateEvidenceItemInput {
  projectId: string;
  actorId: string;
  sourceType: string;
  contentSummary: string;
  sourceReference?: string;
  quality?: string;
  directness?: string;
}

/** `POST /api/diagnosis/evidence-items` - `evidenceItemId` is always server-generated; the
 * caller never supplies (or needs to remember) one. */
export async function createEvidenceItem(input: CreateEvidenceItemInput): Promise<string> {
  const raw = await api.post<{ evidence_item_id: string }>("/api/diagnosis/evidence-items", {
    project_id: input.projectId, actor_id: input.actorId, source_type: input.sourceType,
    content_summary: input.contentSummary, source_reference: input.sourceReference ?? null,
    quality: input.quality ?? "low", directness: input.directness ?? "indirect",
  });
  return raw.evidence_item_id;
}

/** `GET /api/diagnosis/model-capabilities`. */
export async function listModelCapabilities(): Promise<Record<string, ModelCapability>> {
  return api.get<Record<string, ModelCapability>>("/api/diagnosis/model-capabilities");
}

export interface RunModelInput {
  projectId: string;
  diagnosisSessionId: string;
  adapterName: string;
  actorId: string;
  inputs?: Record<string, unknown>;
  context?: Record<string, unknown>;
  constraintsObjectiveParameters?: Record<string, unknown>;
}

/** `POST /api/diagnosis/model-runs`. */
export async function runModel(input: RunModelInput): Promise<ModelRunResult> {
  const r = await api.post<{ model_run_id: string; capability_status: string; runtime_status: string; outputs: Record<string, unknown>; log_summary: string }>(
    "/api/diagnosis/model-runs",
    {
      project_id: input.projectId, diagnosis_session_id: input.diagnosisSessionId, adapter_name: input.adapterName,
      actor_id: input.actorId, inputs: input.inputs ?? {}, context: input.context ?? {},
      constraints_objective_parameters: input.constraintsObjectiveParameters ?? {},
    },
  );
  return { modelRunId: r.model_run_id, capabilityStatus: r.capability_status, runtimeStatus: r.runtime_status, outputs: r.outputs, logSummary: r.log_summary };
}

/** `GET /api/diagnosis/sessions/{id}/tests`. */
export async function listTests(diagnosisSessionId: string): Promise<DiagnosticTestRow[]> {
  const raw = await api.get<{
    tests: Array<{
      test_id: string; assay: string; status: string; discriminates_hypotheses: boolean;
      expected_information_gain: string; plans: Array<{ plan_id: string; readiness: string }>;
    }>;
  }>(`/api/diagnosis/sessions/${diagnosisSessionId}/tests`);
  return raw.tests.map((t) => ({
    testId: t.test_id, assay: t.assay, status: t.status, discriminatesHypotheses: t.discriminates_hypotheses,
    expectedInformationGain: t.expected_information_gain,
    plans: t.plans.map((p) => ({ planId: p.plan_id, readiness: p.readiness })),
  }));
}

/** `GET /api/diagnosis/sessions/{id}/decisions`. */
export async function listDecisions(diagnosisSessionId: string): Promise<DecisionRow[]> {
  const raw = await api.get<{
    decisions: Array<{
      decision_id: string; diagnosis_version: number; stopping_reason: string; allowed_next_action: string;
      handoff_status: string; leading_hypothesis_ids: string[]; alternatives_not_excluded_ids: string[];
    }>;
  }>(`/api/diagnosis/sessions/${diagnosisSessionId}/decisions`);
  return raw.decisions.map((d) => ({
    decisionId: d.decision_id, diagnosisVersion: d.diagnosis_version, stoppingReason: d.stopping_reason,
    allowedNextAction: d.allowed_next_action, handoffStatus: d.handoff_status,
    leadingHypothesisIds: d.leading_hypothesis_ids, alternativesNotExcludedIds: d.alternatives_not_excluded_ids,
  }));
}

/** `POST /api/diagnosis/decisions/{id}/approve`. */
export async function approveDecision(decisionId: string, actorId: string, approved: boolean, reason = ""): Promise<{ decisionId: string; handoffStatus: string }> {
  const r = await api.post<{ decision_id: string; handoff_status: string }>(`/api/diagnosis/decisions/${decisionId}/approve`, {
    decision_id: decisionId, actor_id: actorId, approved, reason,
  });
  return { decisionId: r.decision_id, handoffStatus: r.handoff_status };
}

/** `GET /api/diagnosis/sessions/{id}/audit-trail`. */
export async function getAuditTrail(diagnosisSessionId: string): Promise<DiagnosisTransitionRow[]> {
  const raw = await api.get<{ transitions: Array<{ state: string; selected_next_state: string | null; gate_result: Record<string, unknown> | null; started_at: number }> }>(
    `/api/diagnosis/sessions/${diagnosisSessionId}/audit-trail`,
  );
  return raw.transitions.map((t) => ({ state: t.state, selectedNextState: t.selected_next_state, gateResult: t.gate_result, startedAt: t.started_at }));
}

/** `GET /api/diagnosis/sessions/{id}/report`. */
export async function getReport(diagnosisSessionId: string): Promise<ReportSection[]> {
  const raw = await api.get<{ sections: Array<{ title: string; content: Record<string, unknown>; trace_ids: string[] }> }>(
    `/api/diagnosis/sessions/${diagnosisSessionId}/report`,
  );
  return raw.sections.map((s) => ({ title: s.title, content: s.content, traceIds: s.trace_ids }));
}

/** Pure state-transition actions - `POST /api/diagnosis/sessions/{id}/action/{action}`. See this module's
 * docstring: these never author new content, only move `status` forward. */
export const DIAGNOSIS_SESSION_ACTIONS = [
  "mark_hypotheses_generated", "mark_evidence_assessed", "mark_model_evidence_pending", "mark_hypotheses_ranked",
  "enter_model_conflicted", "enter_test_selection_required", "select_test", "enter_awaiting_test_result",
  "ingest_test_result_and_update_belief", "resolve_human_review", "reopen_diagnosis", "close_diagnosis",
] as const;
export type DiagnosisSessionAction = (typeof DIAGNOSIS_SESSION_ACTIONS)[number];

export async function sessionAction(
  diagnosisSessionId: string,
  action: DiagnosisSessionAction,
  actorId: string,
  kwargs: Record<string, unknown> = {},
): Promise<{ diagnosisSessionId: string; status: string }> {
  const r = await api.post<{ diagnosis_session_id: string; status: string }>(
    `/api/diagnosis/sessions/${diagnosisSessionId}/action/${action}`,
    { actor_id: actorId, kwargs },
  );
  return { diagnosisSessionId: r.diagnosis_session_id, status: r.status };
}
