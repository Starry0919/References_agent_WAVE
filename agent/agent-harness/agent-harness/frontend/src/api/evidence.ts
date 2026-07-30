import { api, ApiError } from "./client";
import { toPaperExtractionSummary, type PaperExtractionSummary } from "./paperExtraction";

/**
 * Literature Evidence adapter (harness/api/generation.py, real,
 * uncommitted). This is the real vertical slice backing the Knowledge &
 * Evidence page's "Literature Evidence" domain search - source is the
 * local DDR knowledge base (`knowledge/ddr_database/*.json`), not a live
 * network literature API (Repository Truth Audit: no network retrieval
 * exists in this repo).
 */
export interface GenerationHealth {
  llm: { available: boolean; provider?: string; model?: string; reason?: string };
  crossref: { available: boolean; reason?: string };
  localDdr: { available: boolean; reason?: string };
}

export async function getGenerationHealth(): Promise<GenerationHealth> {
  const r = await api.get<{
    llm: { available: boolean; provider?: string; model?: string; reason?: string };
    crossref: { available: boolean; reason?: string };
    local_ddr: { available: boolean; reason?: string };
  }>("/api/generation/health");
  return { llm: r.llm, crossref: r.crossref, localDdr: r.local_ddr };
}

export interface EvidenceDocument {
  sourceId: string;
  title: string;
  authors: string[];
  publicationYear: number | null;
  journalOrRepository: string | null;
  doiOrAccession: string | null;
}

export interface EvidenceSearchResult {
  sourceName: string;
  totalAvailable: number;
  documents: EvidenceDocument[];
}

export async function searchEvidence(query: string, source: "local_ddr" | "crossref" = "local_ddr"): Promise<EvidenceSearchResult> {
  const params = new URLSearchParams({ query, source });
  const r = await api.get<{
    source_name: string;
    total_available: number;
    documents: Array<{
      source_id: string;
      title: string;
      authors: string[];
      publication_year: number | null;
      journal_or_repository: string | null;
      doi_or_accession: string | null;
    }>;
  }>(`/api/generation/evidence/search?${params.toString()}`);
  return {
    sourceName: r.source_name,
    totalAvailable: r.total_available,
    documents: r.documents.map((d) => ({
      sourceId: d.source_id,
      title: d.title,
      authors: d.authors,
      publicationYear: d.publication_year,
      journalOrRepository: d.journal_or_repository,
      doiOrAccession: d.doi_or_accession,
    })),
  };
}

export interface EngineeringAction {
  modificationType: string;
  target: string;
  geneOrPathway: string;
  rationale: string;
  expectedEffect: string;
  risk: string;
  validation: string[];
}

export interface ExtractedExperimentalDesign {
  problemStatement: string;
  bottlenecks: string[];
  mechanisticExplanation: string;
  hypothesis: string;
  expectedEffect: string;
  actions: EngineeringAction[];
}

/** One "Agent Analysis Record" card in the left-hand reasoning trace - an
 * observable workflow step, never raw chain-of-thought (harness/paper_
 * extraction/reasoning_view.py::build_agent_trace). `designStepRef` points
 * at the matching `ExperimentalDesignStep.step` for click-to-highlight sync,
 * or `"all"` for the narrative (problem/logic/evidence) cards that summarize
 * across every design step rather than one specific intervention. */
export interface AgentTraceStep {
  step: number;
  kind: "problem_understanding" | "intervention" | "logic_reconstruction" | "evidence_validation";
  title: string;
  status: string;
  input: string;
  operation: string;
  output: string | string[] | Record<string, string>;
  confidence: number | null;
  evidence: string[];
  designStepRef: number | "all" | null;
}

export interface ExperimentalDesignStep {
  step: number;
  title: string;
  problem: string;
  hypothesis: string;
  engineeringAction: { type: string; target: string; modification: string };
  method: string[];
  result: string;
  evidence: string[];
  evidenceGrading: string | null;
  /** 理由性质 (harness/paper_extraction/ddr_converter.py's reason_nature) -
   * gates whether `rule` may be non-null. Surfaced so a reviewer calibrating
   * a step can see *why* it was/wasn't allowed to produce a rule, not just
   * the evidence grade. */
  reasonNature: string | null;
  alternatives: Array<{ approach: string; rejectedReason: string }>;
  /** Generalizable heuristic distilled from this step - always null unless
   * reasonNature is 机理推断/文献类比 (mechanistic reasoning or reliable
   * literature analogy); never fabricated by the converter itself. */
  rule: string | null;
}

export interface EvidenceProvenanceItem {
  step: number | null;
  claim: string;
  source: string;
  grading: string | null;
  confidence: number | null;
}

export interface EvidenceGraph {
  nodes: Array<{ id: string; type: string; label: string }>;
  edges: Array<{ source: string; target: string; type: string }>;
}

export interface EvidenceDocumentDetail extends EvidenceDocument {
  url: string | null;
  abstractOrSummary: string;
  /** Only present for local_ddr documents whose curated record actually
   * carries this content - never fabricated for a crossref document that
   * has nothing but bibliographic metadata (Knowledge & Evidence page's
   * "点击一条文献证据查看详情" - see harness/api/generation.py::
   * get_evidence_document). */
  engineeringDesign: ExtractedExperimentalDesign | null;
  /** The agent's own parsing reasoning + evidence-bound experimental design
   * fields, present only for DDRs auto-saved from a paper_extraction run
   * (harness/paper_extraction/ddr_converter.py::ensure_task_saved_as_evidence).
   * `null` for hand-curated DDRs that predate that pipeline - the paper
   * evidence detail page falls back to `engineeringDesign` alone in that case. */
  paperExtractionDetail: PaperExtractionSummary | null;
  /** The paper_extraction task_id this evidence was saved from, if any -
   * lets the detail page link back to that run. */
  extractionTaskId: string | null;
  /** Dual-track Evidence Reasoning View (harness/paper_extraction/
   * reasoning_view.py) - derived from the same DDR's decision_chain, so
   * present for both hand-curated and pipeline-generated records; empty
   * arrays only for crossref documents or DDRs with no decision_chain at all. */
  agentTrace: AgentTraceStep[];
  experimentalDesign: ExperimentalDesignStep[];
  evidenceProvenance: EvidenceProvenanceItem[];
  evidenceGraph: EvidenceGraph;
  status: "completed" | "pending";
  evidenceConfidence: "high" | "medium" | "low" | null;
  humanReviewStatus: string | null;
  /** Dual-annotator calibration state (harness/paper_extraction/
   * calibration.py, 老师 §4.3 step 3: independent extraction → conflict
   * detection → calibration). `null`/`0`/`[]` for crossref documents and
   * for DDRs no second attempt has ever been recorded against. */
  calibrationStatus: string | null;
  conflictCount: number;
  extractionAttempts: Array<{ annotator: string; recordedAt: string; stepCount: number }>;
  /** The full underlying DDR JSON, for the "Download Extraction JSON"
   * header action - null for crossref documents (no such record exists). */
  rawRecord: Record<string, unknown> | null;
}

export async function getEvidenceDocument(sourceId: string, source: "local_ddr" | "crossref" = "local_ddr"): Promise<EvidenceDocumentDetail | null> {
  try {
    const params = new URLSearchParams({ source });
    const r = await api.get<{
      source_id: string;
      title: string;
      authors: string[];
      publication_year: number | null;
      journal_or_repository: string | null;
      doi_or_accession: string | null;
      url: string | null;
      abstract_or_summary: string;
      paper_extraction_detail: Record<string, unknown> | null;
      extraction_task_id: string | null;
      agent_trace: Array<{
        step: number;
        kind: AgentTraceStep["kind"];
        title: string;
        status: string;
        input: string;
        operation: string;
        output: string | string[] | Record<string, string>;
        confidence: number | null;
        evidence: string[];
        design_step_ref: number | "all" | null;
      }>;
      experimental_design: Array<{
        step: number;
        title: string;
        problem: string;
        hypothesis: string;
        engineering_action: { type: string; target: string; modification: string };
        method: string[];
        result: string;
        evidence: string[];
        evidence_grading: string | null;
        reason_nature: string | null;
        alternatives: Array<{ approach: string; rejected_reason: string }>;
        rule: string | null;
      }>;
      evidence_provenance: Array<{ step: number | null; claim: string; source: string; grading: string | null; confidence: number | null }>;
      evidence_graph: EvidenceGraph;
      status: "completed" | "pending";
      evidence_confidence: "high" | "medium" | "low" | null;
      human_review_status: string | null;
      calibration_status: string | null;
      conflict_count: number;
      extraction_attempts: Array<{ annotator: string; recorded_at: string; step_count: number }>;
      raw_record: Record<string, unknown> | null;
      engineering_design: {
        problem_statement: string;
        bottlenecks: string[];
        mechanistic_explanation: string;
        hypothesis: string;
        expected_effect: string;
        actions: Array<{
          modification_type: string;
          target: string;
          gene_or_pathway: string;
          rationale: string;
          expected_effect: string;
          risk: string;
          validation: string[];
        }>;
      } | null;
    }>(`/api/generation/evidence/documents/${sourceId}?${params.toString()}`);
    return {
      sourceId: r.source_id,
      title: r.title,
      authors: r.authors ?? [],
      publicationYear: r.publication_year,
      journalOrRepository: r.journal_or_repository,
      doiOrAccession: r.doi_or_accession,
      url: r.url,
      abstractOrSummary: r.abstract_or_summary,
      paperExtractionDetail: r.paper_extraction_detail ? toPaperExtractionSummary(r.paper_extraction_detail) : null,
      extractionTaskId: r.extraction_task_id,
      agentTrace: (r.agent_trace ?? []).map((s) => ({
        step: s.step,
        kind: s.kind,
        title: s.title,
        status: s.status,
        input: s.input,
        operation: s.operation,
        output: s.output,
        confidence: s.confidence,
        evidence: s.evidence ?? [],
        designStepRef: s.design_step_ref,
      })),
      experimentalDesign: (r.experimental_design ?? []).map((s) => ({
        step: s.step,
        title: s.title,
        problem: s.problem,
        hypothesis: s.hypothesis,
        engineeringAction: s.engineering_action,
        method: s.method ?? [],
        result: s.result,
        evidence: s.evidence ?? [],
        evidenceGrading: s.evidence_grading,
        reasonNature: s.reason_nature,
        alternatives: (s.alternatives ?? []).map((a) => ({ approach: a.approach, rejectedReason: a.rejected_reason })),
        rule: s.rule,
      })),
      evidenceProvenance: (r.evidence_provenance ?? []).map((e) => ({
        step: e.step,
        claim: e.claim,
        source: e.source,
        grading: e.grading,
        confidence: e.confidence,
      })),
      evidenceGraph: r.evidence_graph ?? { nodes: [], edges: [] },
      status: r.status ?? "pending",
      evidenceConfidence: r.evidence_confidence ?? null,
      humanReviewStatus: r.human_review_status ?? null,
      calibrationStatus: r.calibration_status ?? null,
      conflictCount: r.conflict_count ?? 0,
      extractionAttempts: (r.extraction_attempts ?? []).map((a) => ({ annotator: a.annotator, recordedAt: a.recorded_at, stepCount: a.step_count })),
      rawRecord: r.raw_record ?? null,
      engineeringDesign: r.engineering_design
        ? {
            problemStatement: r.engineering_design.problem_statement,
            bottlenecks: r.engineering_design.bottlenecks ?? [],
            mechanisticExplanation: r.engineering_design.mechanistic_explanation,
            hypothesis: r.engineering_design.hypothesis,
            expectedEffect: r.engineering_design.expected_effect,
            actions: (r.engineering_design.actions ?? []).map((a) => ({
              modificationType: a.modification_type,
              target: a.target,
              geneOrPathway: a.gene_or_pathway,
              rationale: a.rationale,
              expectedEffect: a.expected_effect,
              risk: a.risk,
              validation: a.validation ?? [],
            })),
          }
        : null,
    };
  } catch (e) {
    if (e instanceof ApiError && e.status === 404) return null;
    throw e;
  }
}

/**
 * One decision_chain step, as edited by a human annotator submitting an
 * independent extraction attempt (老师 §4.3 step 3). Same field shape as
 * `knowledge/ddr_database/schema_v2.json`'s `decision_chain` items - this
 * is a *draft*, not the reshaped `ExperimentalDesignStep` view above, since
 * `harness/paper_extraction/calibration.py::detect_conflicts` compares raw
 * decision_chain fields directly.
 */
export interface DecisionChainStepDraft {
  step: number;
  design_action: string;
  target: { gene: string; enzyme: string; pathway: string; condition: string };
  trigger: { observation: string; reasoning: string; source_location: string };
  evidence: { description: string; source: string; source_location: string };
  evidence_grading: string;
  reason_nature: string;
  alternatives: Array<{ approach: string; rejected_reason: string }>;
  implementation: string;
  implementation_detail: string;
  result: { metric: string; before: string; after: string; fold_change: string; quantified: boolean };
  rule: string;
}

export function blankDecisionChainStep(step: number): DecisionChainStepDraft {
  return {
    step,
    design_action: "M3",
    target: { gene: "", enzyme: "", pathway: "", condition: "" },
    trigger: { observation: "", reasoning: "", source_location: "" },
    evidence: { description: "", source: "", source_location: "" },
    evidence_grading: "软",
    reason_nature: "事后合理化存疑",
    alternatives: [],
    implementation: "其他",
    implementation_detail: "",
    result: { metric: "", before: "", after: "", fold_change: "", quantified: false },
    rule: "",
  };
}

export interface ExtractionConflict {
  step: number | null;
  field: string;
  valuesByAnnotator: Record<string, unknown>;
}

/**
 * Submits one annotator's independent decision_chain draft for a saved DDR
 * (harness/api/paper_extraction.py::submit_extraction_attempt →
 * calibration.record_extraction_attempt). Recomputes conflicts across every
 * attempt recorded so far and flips `calibration_status` to `"disputed"`
 * the moment any field disagrees - the response mirrors that immediately so
 * the panel doesn't need a second round-trip to show it.
 */
export async function submitExtractionAttempt(
  ddrId: string,
  annotator: string,
  decisionChain: DecisionChainStepDraft[],
): Promise<{ ddrId: string; attempts: number; conflicts: ExtractionConflict[]; calibrationStatus: string }> {
  const r = await api.post<{ ddr_id: string; attempts: number; conflicts: Array<{ step: number | null; field: string; values_by_annotator: Record<string, unknown> }>; calibration_status: string }>(
    `/api/paper-extraction/ddr/${ddrId}/attempts`,
    { annotator, decision_chain: decisionChain },
  );
  return {
    ddrId: r.ddr_id,
    attempts: r.attempts,
    conflicts: r.conflicts.map((c) => ({ step: c.step, field: c.field, valuesByAnnotator: c.values_by_annotator })),
    calibrationStatus: r.calibration_status,
  };
}

/** Read-only conflict recompute (harness/api/paper_extraction.py::
 * get_extraction_conflicts) - does not require submitting a new attempt. */
export async function getExtractionConflicts(ddrId: string): Promise<ExtractionConflict[]> {
  const r = await api.get<{ ddr_id: string; conflicts: Array<{ step: number | null; field: string; values_by_annotator: Record<string, unknown> }>; total: number }>(
    `/api/paper-extraction/ddr/${ddrId}/conflicts`,
  );
  return r.conflicts.map((c) => ({ step: c.step, field: c.field, valuesByAnnotator: c.values_by_annotator }));
}

/**
 * Real Crossref DOI resolution (harness/evidence_retrieval/service.py::
 * verify_doi) - a fabricated/unresolvable DOI comes back `resolved: false`
 * and is recorded server-side as a GEN_HALLUCINATED_REFERENCE_REJECTED
 * event (surfaced in ComputationalTraceabilityTab), never silently
 * accepted (System Invariant 9 "No Unsupported Synthesis").
 */
export async function verifyDoi(input: { projectId: string; doi: string; actorId: string }): Promise<{ doi: string; resolved: boolean }> {
  return api.post<{ doi: string; resolved: boolean }>("/api/generation/evidence/verify-doi", {
    project_id: input.projectId,
    doi: input.doi,
    actor_id: input.actorId,
  });
}

/**
 * EvidenceMatchReport (harness/evidence_retrieval/models.py) - the real
 * backing for Applicability Context / cross-strain "context mismatch"
 * signal (Page 3 prompt §17, Scenario E). directness/overall_match_status
 * are never collapsed to a single color - see MatchReportCard.
 */
export interface EvidenceMatchReportSummary {
  matchReportId: string;
  evidenceId: string;
  organismMatch: string;
  strainMatch: string;
  genotypeMatch: string;
  mediumMatch: string;
  conditionMatch: string;
  timepointMatch: string;
  interventionMatch: string;
  measurementMatch: string;
  directness: string;
  overallMatchStatus: string;
  transferRisks: string[];
  downgradeReasons: string[];
  createdAt: number;
}

export async function listEvidenceMatchReports(evidenceId?: string): Promise<EvidenceMatchReportSummary[]> {
  const params = evidenceId ? `?${new URLSearchParams({ evidence_id: evidenceId }).toString()}` : "";
  const r = await api.get<{
    match_reports: Array<{
      match_report_id: string;
      evidence_id: string;
      organism_match: string;
      strain_match: string;
      genotype_match: string;
      medium_match: string;
      condition_match: string;
      timepoint_match: string;
      intervention_match: string;
      measurement_match: string;
      directness: string;
      overall_match_status: string;
      transfer_risks: string[];
      downgrade_reasons: string[];
      created_at: number;
    }>;
  }>(`/api/generation/evidence/match-reports${params}`);
  return r.match_reports.map((m) => ({
    matchReportId: m.match_report_id,
    evidenceId: m.evidence_id,
    organismMatch: m.organism_match,
    strainMatch: m.strain_match,
    genotypeMatch: m.genotype_match,
    mediumMatch: m.medium_match,
    conditionMatch: m.condition_match,
    timepointMatch: m.timepoint_match,
    interventionMatch: m.intervention_match,
    measurementMatch: m.measurement_match,
    directness: m.directness,
    overallMatchStatus: m.overall_match_status,
    transferRisks: m.transfer_risks ?? [],
    downgradeReasons: m.downgrade_reasons ?? [],
    createdAt: m.created_at,
  }));
}

/**
 * LLMGenerationRecord (harness/llm_generation/models.py) - the real
 * backing for Computational Traceability (Page 3 prompt §20): every AI-
 * derived output must show model/version/params/validation status, never
 * just a bare "AI generated" label.
 */
export interface GenerationRecordSummary {
  generationId: string;
  taskType: string;
  provider: string;
  modelId: string;
  promptTemplateId: string;
  promptTemplateVersion: string;
  outputSchemaVersion: string;
  validationStatus: string;
  retryCount: number;
  fallbackUsed: boolean;
  sharedModelRisk: boolean;
  tokenUsageIfAvailable: Record<string, unknown> | null;
  latency: number | null;
  createdAt: number;
}

interface RawGenerationRecord {
  generation_id: string;
  task_type: string;
  provider: string;
  model_id: string;
  prompt_template_id: string;
  prompt_template_version: string;
  output_schema_version: string;
  validation_status: string;
  retry_count: number;
  fallback_used: boolean;
  shared_model_risk: boolean;
  token_usage_if_available: Record<string, unknown> | null;
  latency: number | null;
  created_at: number;
}

function toGenerationRecordSummary(r: RawGenerationRecord): GenerationRecordSummary {
  return {
    generationId: r.generation_id,
    taskType: r.task_type,
    provider: r.provider,
    modelId: r.model_id,
    promptTemplateId: r.prompt_template_id,
    promptTemplateVersion: r.prompt_template_version,
    outputSchemaVersion: r.output_schema_version,
    validationStatus: r.validation_status,
    retryCount: r.retry_count,
    fallbackUsed: r.fallback_used,
    sharedModelRisk: r.shared_model_risk,
    tokenUsageIfAvailable: r.token_usage_if_available,
    latency: r.latency,
    createdAt: r.created_at,
  };
}

export async function listGenerationRecords(taskType?: string): Promise<GenerationRecordSummary[]> {
  const params = taskType ? `?${new URLSearchParams({ task_type: taskType }).toString()}` : "";
  const r = await api.get<{ records: RawGenerationRecord[] }>(`/api/generation/records${params}`);
  return r.records.map(toGenerationRecordSummary);
}

export interface GenerationRecordDetail extends GenerationRecordSummary {
  rawOutputArtifactRef: string | null;
  parsedOutputRef: string | null;
}

export async function getGenerationRecord(generationId: string): Promise<GenerationRecordDetail | null> {
  try {
    const r = await api.get<RawGenerationRecord & { raw_output_artifact_ref: string | null; parsed_output_ref: string | null }>(
      `/api/generation/records/${generationId}`,
    );
    return { ...toGenerationRecordSummary(r), rawOutputArtifactRef: r.raw_output_artifact_ref, parsedOutputRef: r.parsed_output_ref };
  } catch (e) {
    if (e instanceof ApiError && e.status === 404) return null;
    throw e;
  }
}
