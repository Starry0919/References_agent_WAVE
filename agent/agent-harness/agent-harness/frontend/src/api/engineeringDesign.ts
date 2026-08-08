import { api, ApiError } from "./client";

/**
 * Engineering Design Generation and Decision Loop adapter
 * (harness/api/engineering_design.py, doc04). Unlike diagnosis, every
 * stage of the 18-state workflow (`DESIGN_WORKFLOW_STATES`) has an
 * explicit POST route meant to be driven step by step by a human/frontend
 * - this client mirrors that route-for-route.
 */

export interface DesignProject {
  designProjectId: string;
  projectId: string;
  chassis: string;
  chassisVersionOrGenotype: string;
  diagnosisSessionId: string;
  diagnosisDecisionId: string;
  diagnosisVersion: number;
  primaryMetrics: unknown[];
  secondaryMetrics: unknown[];
  hardConstraints: unknown[];
  preferencesOrWeights: unknown[];
  autonomyLevel: string;
  status: string;
  revisionCount: number;
  version: number;
  referenceDdrIds: string[];
}

export interface HandoffRecord {
  handoffId: string;
  designProjectId: string;
  diagnosisSessionId: string;
  diagnosisDecisionId: string;
  diagnosisVersion: number;
  handoffKind: string;
  decisionStatus: string;
  supportedHypotheses: unknown[];
  unresolvedAlternatives: unknown[];
  approvedForDesign: boolean;
  isStale: boolean;
  adapterProvenance: Record<string, unknown>;
  createdAt: number;
}

export interface Strategy {
  strategyId: string;
  strategyClass: string;
  engineeringObjective: string;
  mechanismTarget: string;
  rationale: string;
  status: string;
  excludedStrategyReasons: unknown[];
  evidenceLinks: Array<{ source_type: string; reference: string; detail?: string }>;
}

export interface CandidateDesign {
  designId: string;
  lineageId: string;
  designVersion: number;
  portfolioId: string | null;
  portfolioRole: string | null;
  strategyIds: string[];
  geneticModifications: unknown[];
  expectedMechanism: string;
  readiness: string;
  status: string;
  rejectionReasons: unknown[];
  buildTestPackageId: string | null;
}

function toProject(p: {
  design_project_id: string; project_id: string; chassis: string; chassis_version_or_genotype: string;
  diagnosis_session_id: string; diagnosis_decision_id: string; diagnosis_version: number; primary_metrics: unknown[];
  secondary_metrics: unknown[]; hard_constraints: unknown[]; preferences_or_weights: unknown[]; autonomy_level: string;
  status: string; revision_count: number; version: number; reference_ddr_ids: string[];
}): DesignProject {
  return {
    designProjectId: p.design_project_id, projectId: p.project_id, chassis: p.chassis,
    chassisVersionOrGenotype: p.chassis_version_or_genotype, diagnosisSessionId: p.diagnosis_session_id,
    diagnosisDecisionId: p.diagnosis_decision_id, diagnosisVersion: p.diagnosis_version, primaryMetrics: p.primary_metrics,
    secondaryMetrics: p.secondary_metrics, hardConstraints: p.hard_constraints, preferencesOrWeights: p.preferences_or_weights,
    autonomyLevel: p.autonomy_level, status: p.status, revisionCount: p.revision_count, version: p.version,
    referenceDdrIds: p.reference_ddr_ids,
  };
}

function toHandoff(h: {
  handoff_id: string; design_project_id: string; diagnosis_session_id: string; diagnosis_decision_id: string;
  diagnosis_version: number; handoff_kind: string; decision_status: string; supported_hypotheses: unknown[];
  unresolved_alternatives: unknown[]; approved_for_design: boolean; is_stale: boolean;
  adapter_provenance: Record<string, unknown>; created_at: number;
}): HandoffRecord {
  return {
    handoffId: h.handoff_id, designProjectId: h.design_project_id, diagnosisSessionId: h.diagnosis_session_id,
    diagnosisDecisionId: h.diagnosis_decision_id, diagnosisVersion: h.diagnosis_version, handoffKind: h.handoff_kind,
    decisionStatus: h.decision_status, supportedHypotheses: h.supported_hypotheses,
    unresolvedAlternatives: h.unresolved_alternatives, approvedForDesign: h.approved_for_design,
    isStale: h.is_stale, adapterProvenance: h.adapter_provenance, createdAt: h.created_at,
  };
}

function toStrategy(s: {
  strategy_id: string; strategy_class: string; engineering_objective: string; mechanism_target: string;
  rationale: string; status: string; excluded_strategy_reasons: unknown[]; evidence_links: Strategy["evidenceLinks"];
}): Strategy {
  return {
    strategyId: s.strategy_id, strategyClass: s.strategy_class, engineeringObjective: s.engineering_objective,
    mechanismTarget: s.mechanism_target, rationale: s.rationale, status: s.status,
    excludedStrategyReasons: s.excluded_strategy_reasons, evidenceLinks: s.evidence_links,
  };
}

function toCandidate(c: {
  design_id: string; lineage_id: string; design_version: number; portfolio_id: string | null;
  portfolio_role: string | null; strategy_ids: string[]; genetic_modifications: unknown[]; expected_mechanism: string;
  readiness: string; status: string; rejection_reasons: unknown[]; build_test_package_id: string | null;
}): CandidateDesign {
  return {
    designId: c.design_id, lineageId: c.lineage_id, designVersion: c.design_version, portfolioId: c.portfolio_id,
    portfolioRole: c.portfolio_role, strategyIds: c.strategy_ids, geneticModifications: c.genetic_modifications,
    expectedMechanism: c.expected_mechanism, readiness: c.readiness, status: c.status,
    rejectionReasons: c.rejection_reasons, buildTestPackageId: c.build_test_package_id,
  };
}

export interface HandoffInput {
  diagnosisDecisionId: string;
  actorId: string;
  handoffKind?: string;
  humanApproved?: boolean;
  chassis?: string;
  chassisVersionOrGenotype?: string;
}

/** `POST /api/engineering-design/handoff`. */
export async function createHandoff(input: HandoffInput): Promise<{ project: DesignProject; handoff: HandoffRecord }> {
  const r = await api.post<{ project: Parameters<typeof toProject>[0]; handoff: Parameters<typeof toHandoff>[0] }>(
    "/api/engineering-design/handoff",
    {
      diagnosis_decision_id: input.diagnosisDecisionId, actor_id: input.actorId,
      handoff_kind: input.handoffKind ?? "diagnosis_decision", human_approved: input.humanApproved ?? null,
      chassis: input.chassis ?? null, chassis_version_or_genotype: input.chassisVersionOrGenotype ?? "unknown",
    },
  );
  return { project: toProject(r.project), handoff: toHandoff(r.handoff) };
}

/** `GET /api/engineering-design/projects/{id}`. */
export async function getProject(designProjectId: string): Promise<DesignProject> {
  const r = await api.get<Parameters<typeof toProject>[0]>(`/api/engineering-design/projects/${designProjectId}`);
  return toProject(r);
}

/** `GET /api/engineering-design/projects/{id}/handoff` - newest first; empty if none. */
export async function listHandoffs(designProjectId: string): Promise<HandoffRecord[]> {
  const raw = await api.get<{ handoffs: Parameters<typeof toHandoff>[0][] }>(`/api/engineering-design/projects/${designProjectId}/handoff`);
  return raw.handoffs.map(toHandoff);
}

export interface ObjectivesInput {
  primaryMetrics: unknown[];
  secondaryMetrics?: unknown[];
  hardConstraints: unknown[];
  preferencesOrWeights?: unknown[];
  availableResources?: Record<string, unknown>;
  expectedVersion: number;
  actorId: string;
}

/** `POST /api/engineering-design/projects/{id}/objectives`. */
export async function setObjectives(designProjectId: string, input: ObjectivesInput): Promise<DesignProject> {
  const r = await api.post<Parameters<typeof toProject>[0]>(`/api/engineering-design/projects/${designProjectId}/objectives`, {
    primary_metrics: input.primaryMetrics, secondary_metrics: input.secondaryMetrics ?? [],
    hard_constraints: input.hardConstraints, preferences_or_weights: input.preferencesOrWeights ?? [],
    available_resources: input.availableResources ?? {}, expected_version: input.expectedVersion, actor_id: input.actorId,
  });
  return toProject(r);
}

/** `POST /api/engineering-design/projects/{id}/confirm-objective`. */
export async function confirmObjective(designProjectId: string, actorId: string): Promise<DesignProject> {
  const r = await api.post<Parameters<typeof toProject>[0]>(`/api/engineering-design/projects/${designProjectId}/confirm-objective`, { actor_id: actorId });
  return toProject(r);
}

/** `POST /api/engineering-design/projects/{id}/strategies`. */
export async function generateStrategies(designProjectId: string, handoffId: string, actorId: string): Promise<Strategy[]> {
  const raw = await api.post<{ strategies: Parameters<typeof toStrategy>[0][] }>(`/api/engineering-design/projects/${designProjectId}/strategies`, {
    handoff_id: handoffId, actor_id: actorId,
  });
  return raw.strategies.map(toStrategy);
}

/** `GET /api/engineering-design/projects/{id}/strategies`. */
export async function listStrategies(designProjectId: string): Promise<Strategy[]> {
  const raw = await api.get<{ strategies: Parameters<typeof toStrategy>[0][] }>(`/api/engineering-design/projects/${designProjectId}/strategies`);
  return raw.strategies.map(toStrategy);
}

export interface EvidenceLinkResolution {
  kind: string;
  title: string;
  referenceId: string;
  doi: string | null;
  note: string;
}

/** `GET /api/engineering-design/evidence-links/resolve`. */
export async function resolveEvidenceLink(sourceType: string, reference: string, detail = ""): Promise<EvidenceLinkResolution> {
  const r = await api.get<{ kind: string; title: string; reference_id: string; doi: string | null; note: string }>(
    `/api/engineering-design/evidence-links/resolve?source_type=${encodeURIComponent(sourceType)}&reference=${encodeURIComponent(reference)}&detail=${encodeURIComponent(detail)}`,
  );
  return { kind: r.kind, title: r.title, referenceId: r.reference_id, doi: r.doi, note: r.note };
}

/** `POST /api/engineering-design/projects/{id}/portfolio`. */
export async function generatePortfolio(designProjectId: string, actorId: string): Promise<{
  portfolioId: string; candidates: CandidateDesign[]; absentRoles: unknown[]; suppressedRepeats: unknown[];
}> {
  const r = await api.post<{ portfolio_id: string; candidates: Parameters<typeof toCandidate>[0][]; absent_roles: unknown[]; suppressed_repeats: unknown[] }>(
    `/api/engineering-design/projects/${designProjectId}/portfolio`,
    { actor_id: actorId },
  );
  return { portfolioId: r.portfolio_id, candidates: r.candidates.map(toCandidate), absentRoles: r.absent_roles, suppressedRepeats: r.suppressed_repeats };
}

/** `GET /api/engineering-design/projects/{id}/candidates`. */
export async function listCandidates(designProjectId: string): Promise<CandidateDesign[]> {
  const raw = await api.get<{ candidates: Parameters<typeof toCandidate>[0][] }>(`/api/engineering-design/projects/${designProjectId}/candidates`);
  return raw.candidates.map(toCandidate);
}

/** `GET /api/engineering-design/candidates/{id}`. */
export async function getCandidate(designId: string): Promise<CandidateDesign> {
  const r = await api.get<Parameters<typeof toCandidate>[0]>(`/api/engineering-design/candidates/${designId}`);
  return toCandidate(r);
}

export interface ReviseCandidateInput {
  actorId: string;
  modificationReason: string;
  geneticModifications?: unknown[];
  regulatoryArchitecture?: Record<string, unknown>;
  processModifications?: unknown[];
  expectedMechanism?: string;
  causalChain?: string[];
  interactionAndEpistasisAssumptions?: string[];
}

/** `POST /api/engineering-design/candidates/{id}/revise`. */
export async function reviseCandidate(designId: string, input: ReviseCandidateInput): Promise<CandidateDesign> {
  const r = await api.post<Parameters<typeof toCandidate>[0]>(`/api/engineering-design/candidates/${designId}/revise`, {
    actor_id: input.actorId, modification_reason: input.modificationReason,
    genetic_modifications: input.geneticModifications ?? null, regulatory_architecture: input.regulatoryArchitecture ?? null,
    process_modifications: input.processModifications ?? null, expected_mechanism: input.expectedMechanism ?? null,
    causal_chain: input.causalChain ?? null, interaction_and_epistasis_assumptions: input.interactionAndEpistasisAssumptions ?? null,
  });
  return toCandidate(r);
}

export interface PortfolioEvaluationResult {
  decision: Record<string, unknown>;
  evaluations: Record<string, {
    recommendation: string; paretoStatus: string | null; requiredRevisions: unknown[]; evaluatorFindings: unknown[];
    objectiveVector: unknown[]; hardConstraintResults: unknown[];
  }>;
  revisionGate: { status: string; violations: string[] };
}

/** `POST /api/engineering-design/portfolios/{id}/evaluate`. */
export async function evaluatePortfolio(portfolioId: string, actorId: string): Promise<PortfolioEvaluationResult> {
  const r = await api.post<{
    decision: Record<string, unknown>;
    evaluations: Record<string, { recommendation: string; pareto_status: string | null; required_revisions: unknown[]; evaluator_findings: unknown[]; objective_vector: unknown[]; hard_constraint_results: unknown[] }>;
    revision_gate: { status: string; violations: string[] };
  }>(`/api/engineering-design/portfolios/${portfolioId}/evaluate`, { actor_id: actorId });
  const evaluations: PortfolioEvaluationResult["evaluations"] = {};
  for (const [id, ev] of Object.entries(r.evaluations)) {
    evaluations[id] = {
      recommendation: ev.recommendation, paretoStatus: ev.pareto_status, requiredRevisions: ev.required_revisions,
      evaluatorFindings: ev.evaluator_findings, objectiveVector: ev.objective_vector, hardConstraintResults: ev.hard_constraint_results,
    };
  }
  return { decision: r.decision, evaluations, revisionGate: { status: r.revision_gate.status, violations: r.revision_gate.violations } };
}

export interface CandidateEvaluation {
  evaluationId: string;
  designVersion: number;
  objectiveVector: unknown[];
  hardConstraintResults: unknown[];
  evaluatorFindings: unknown[];
  paretoStatus: string | null;
  recommendation: string;
  requiredRevisions: unknown[];
}

/** `GET /api/engineering-design/candidates/{id}/evaluation` - null if none on record (404). */
export async function getLatestEvaluation(designId: string): Promise<CandidateEvaluation | null> {
  try {
    const r = await api.get<{
      evaluation_id: string; design_version: number; objective_vector: unknown[]; hard_constraint_results: unknown[];
      evaluator_findings: unknown[]; pareto_status: string | null; recommendation: string; required_revisions: unknown[];
    }>(`/api/engineering-design/candidates/${designId}/evaluation`);
    return {
      evaluationId: r.evaluation_id, designVersion: r.design_version, objectiveVector: r.objective_vector,
      hardConstraintResults: r.hard_constraint_results, evaluatorFindings: r.evaluator_findings,
      paretoStatus: r.pareto_status, recommendation: r.recommendation, requiredRevisions: r.required_revisions,
    };
  } catch (e) {
    if (e instanceof ApiError && e.status === 404) return null;
    throw e;
  }
}

export interface CounterfactualInput {
  adapterName: string;
  actorId: string;
  inputs?: Record<string, unknown>;
  context?: Record<string, unknown>;
  constraintsObjectiveParameters?: Record<string, unknown>;
}

/** `POST /api/engineering-design/candidates/{id}/counterfactual`. */
export async function requestCounterfactual(designId: string, input: CounterfactualInput): Promise<{
  runId: string; capabilityStatus: string; runtimeStatus: string; status: string; outputs: Record<string, unknown>;
}> {
  const r = await api.post<{ run_id: string; capability_status: string; runtime_status: string; status: string; outputs: Record<string, unknown> }>(
    `/api/engineering-design/candidates/${designId}/counterfactual`,
    {
      adapter_name: input.adapterName, actor_id: input.actorId, inputs: input.inputs ?? null,
      context: input.context ?? {}, constraints_objective_parameters: input.constraintsObjectiveParameters ?? {},
    },
  );
  return { runId: r.run_id, capabilityStatus: r.capability_status, runtimeStatus: r.runtime_status, status: r.status, outputs: r.outputs };
}

export interface DraftBuildTestInput {
  actorId: string;
  constructionConcept?: string;
  buildStepsOrMilestones?: unknown[];
  requiredMaterials?: string[];
  requiredCapabilitiesOrInstruments?: string[];
  controls?: unknown[];
  replicationPlan?: Record<string, unknown>;
  samplingPlan?: unknown[];
  qcCheckpoints?: string[];
  decisionRules?: string[];
  debugPlan?: string[];
  fallbackPlan?: string[];
  estimatedTimeCostAndRisk?: Record<string, unknown>;
}

/** `POST /api/engineering-design/candidates/{id}/build-test-package`. */
export async function draftBuildTestPackage(designId: string, input: DraftBuildTestInput): Promise<{
  packageId: string; readiness: string; missingInformationOrResources: unknown[];
}> {
  const r = await api.post<{ package_id: string; readiness: string; missing_information_or_resources: unknown[] }>(
    `/api/engineering-design/candidates/${designId}/build-test-package`,
    {
      actor_id: input.actorId, construction_concept: input.constructionConcept ?? "",
      build_steps_or_milestones: input.buildStepsOrMilestones ?? [], required_materials: input.requiredMaterials ?? [],
      required_capabilities_or_instruments: input.requiredCapabilitiesOrInstruments ?? [], controls: input.controls ?? [],
      replication_plan: input.replicationPlan ?? {}, sampling_plan: input.samplingPlan ?? [],
      qc_checkpoints: input.qcCheckpoints ?? [], decision_rules: input.decisionRules ?? [],
      debug_plan: input.debugPlan ?? [], fallback_plan: input.fallbackPlan ?? [],
      estimated_time_cost_and_risk: input.estimatedTimeCostAndRisk ?? {},
    },
  );
  return { packageId: r.package_id, readiness: r.readiness, missingInformationOrResources: r.missing_information_or_resources };
}

/** `POST /api/engineering-design/projects/{id}/planning-complete`. */
export async function markPlanningComplete(designProjectId: string, actorId: string): Promise<DesignProject> {
  const r = await api.post<Parameters<typeof toProject>[0]>(`/api/engineering-design/projects/${designProjectId}/planning-complete`, { actor_id: actorId });
  return toProject(r);
}

/** `POST /api/engineering-design/projects/{id}/request-approval`. */
export async function requestApproval(designProjectId: string, actorId: string): Promise<DesignProject> {
  const r = await api.post<Parameters<typeof toProject>[0]>(`/api/engineering-design/projects/${designProjectId}/request-approval`, { actor_id: actorId });
  return toProject(r);
}

export interface HumanDecisionInput {
  approverId: string;
  decision: "approved" | "rejected";
  approverRole?: string;
  conditions?: string[];
  reason?: string;
}

/** `POST /api/engineering-design/candidates/{id}/human-decision`. */
export async function recordHumanDecision(designId: string, input: HumanDecisionInput): Promise<{
  approvalId: string; candidateStatus: string; projectStatus: string;
}> {
  const r = await api.post<{ approval_id: string; candidate_status: string; project_status: string }>(
    `/api/engineering-design/candidates/${designId}/human-decision`,
    { approver_id: input.approverId, decision: input.decision, approver_role: input.approverRole ?? "", conditions: input.conditions ?? [], reason: input.reason ?? "" },
  );
  return { approvalId: r.approval_id, candidateStatus: r.candidate_status, projectStatus: r.project_status };
}

/** `POST /api/engineering-design/candidates/{id}/bridge-to-design-version`. */
export async function bridgeToDesignVersion(designId: string, actorId: string, versionLabel?: string): Promise<string> {
  const r = await api.post<{ design_version_id: string }>(`/api/engineering-design/candidates/${designId}/bridge-to-design-version`, {
    actor_id: actorId, version_label: versionLabel ?? null,
  });
  return r.design_version_id;
}

/** `POST /api/engineering-design/projects/{id}/candidates/{designId}/start-build`. */
export async function startBuild(designProjectId: string, designId: string, actorId: string): Promise<CandidateDesign> {
  const r = await api.post<Parameters<typeof toCandidate>[0]>(`/api/engineering-design/projects/${designProjectId}/candidates/${designId}/start-build`, { actor_id: actorId });
  return toCandidate(r);
}

/** `POST /api/engineering-design/projects/{id}/test-pending`. */
export async function markTestPending(designProjectId: string, actorId: string): Promise<DesignProject> {
  const r = await api.post<Parameters<typeof toProject>[0]>(`/api/engineering-design/projects/${designProjectId}/test-pending`, { actor_id: actorId });
  return toProject(r);
}

export interface OutcomeInput {
  actorId: string;
  observedResults: unknown[];
  constructionVerified: boolean;
  assayQcPassed: boolean;
  experimentRunId?: string;
  constraintViolations?: string[];
  outcomeUpdate?: string;
}

/** `POST /api/engineering-design/candidates/{id}/outcome`. */
export async function ingestOutcome(designId: string, input: OutcomeInput): Promise<{
  outcomeId: string; failureClassification: string; decidedNextAction: string | null; nextIterationReason: string | null;
  residuals: unknown[]; failureCaseId: string | null;
}> {
  const r = await api.post<{
    outcome_id: string; failure_classification: string; decided_next_action: string | null; next_iteration_reason: string | null;
    residuals: unknown[]; failure_case_id: string | null;
  }>(`/api/engineering-design/candidates/${designId}/outcome`, {
    actor_id: input.actorId, observed_results: input.observedResults, construction_verified: input.constructionVerified,
    assay_qc_passed: input.assayQcPassed, experiment_run_id: input.experimentRunId ?? null,
    constraint_violations: input.constraintViolations ?? [], outcome_update: input.outcomeUpdate ?? "",
  });
  return {
    outcomeId: r.outcome_id, failureClassification: r.failure_classification, decidedNextAction: r.decided_next_action,
    nextIterationReason: r.next_iteration_reason, residuals: r.residuals, failureCaseId: r.failure_case_id,
  };
}

/** `POST /api/engineering-design/projects/{id}/next-iteration`. */
export async function startNextIteration(designProjectId: string, actorId: string): Promise<DesignProject> {
  const r = await api.post<Parameters<typeof toProject>[0]>(`/api/engineering-design/projects/${designProjectId}/next-iteration`, { actor_id: actorId });
  return toProject(r);
}

/** `GET /api/engineering-design/projects/{id}/history`. */
export async function getHistory(designProjectId: string): Promise<unknown[]> {
  const raw = await api.get<{ lineage: unknown[] }>(`/api/engineering-design/projects/${designProjectId}/history`);
  return raw.lineage;
}

export interface DesignTransitionRow {
  state: string;
  selectedNextState: string | null;
  gateResult: Record<string, unknown> | null;
  startedAt: number;
}

/** `GET /api/engineering-design/projects/{id}/audit-trail`. */
export async function getAuditTrail(designProjectId: string): Promise<DesignTransitionRow[]> {
  const raw = await api.get<{ transitions: Array<{ state: string; selected_next_state: string | null; gate_result: Record<string, unknown> | null; started_at: number }> }>(
    `/api/engineering-design/projects/${designProjectId}/audit-trail`,
  );
  return raw.transitions.map((t) => ({ state: t.state, selectedNextState: t.selected_next_state, gateResult: t.gate_result, startedAt: t.started_at }));
}
