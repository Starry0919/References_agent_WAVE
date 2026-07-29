import { api } from "./client";

/**
 * Paper Experimental Design Extraction module (harness/api/paper_extraction.py
 * -> harness/paper_extraction/, vendoring the 13-skill pipeline). Real,
 * async, file-backed - not a project-ledger-DB capability, matching the
 * simulation_demo precedent of a self-contained sub-system.
 */

export interface RunSubmission {
  projectId?: string;
  userRequest: string;
  organism?: string;
  strain?: string;
  sourceType: "auto_search" | "upload" | "doi" | "textbook";
  resultLevel?: "extract" | "compare" | "adapt" | "engineering_plan";
  documentKind?: "auto" | "paper" | "textbook";
  files?: string[];
  doi?: string[];
  automatic?: boolean;
  humanReview?: boolean;
}

export async function submitRun(input: RunSubmission): Promise<{ task_id: string; status: string }> {
  return api.post("/api/paper-extraction/tasks", {
    project_id: input.projectId ?? null,
    user_request: input.userRequest,
    organism: input.organism ?? "",
    strain: input.strain ?? "",
    source_type: input.sourceType,
    result_level: input.resultLevel ?? "extract",
    document_kind: input.documentKind ?? (input.sourceType === "textbook" ? "textbook" : "auto"),
    files: input.files ?? [],
    doi: input.doi ?? [],
    automatic: input.automatic ?? true,
    human_review: input.humanReview ?? true,
  });
}

export interface RunHistoryItem {
  taskId: string;
  status: string;
  error: string | null;
  submittedAt: number;
  userRequest: string;
  organism: string;
  strain: string;
  projectId: string | null;
}

/**
 * Run history (harness/api/paper_extraction.py::list_tasks, real). Without
 * this, the page had no way to show past/in-progress runs once the
 * `?task=` URL param was lost (navigating to another page and back reset
 * PaperExtractionPage to a blank submission form even though the backend
 * task kept running - the task itself was never actually lost, only the
 * frontend's pointer to it).
 */
export async function listRuns(projectId?: string): Promise<RunHistoryItem[]> {
  const r = await api.get<{
    tasks: Array<{ task_id: string; status: string; error: string | null; submitted_at: number; user_request: string; organism: string; strain: string; project_id: string | null }>;
  }>(`/api/paper-extraction/tasks${projectId ? `?project_id=${encodeURIComponent(projectId)}` : ""}`);
  return r.tasks.map((t) => ({
    taskId: t.task_id,
    status: t.status,
    error: t.error,
    submittedAt: t.submitted_at,
    userRequest: t.user_request,
    organism: t.organism,
    strain: t.strain,
    projectId: t.project_id,
  }));
}

export async function deleteRun(taskId: string): Promise<void> {
  await api.delete<{ deleted: boolean; task_id: string }>(`/api/paper-extraction/tasks/${taskId}`);
}

export async function uploadPaper(file: File): Promise<{ path: string; filename: string }> {
  const buffer = await file.arrayBuffer();
  let binary = "";
  const bytes = new Uint8Array(buffer);
  for (let i = 0; i < bytes.length; i++) binary += String.fromCharCode(bytes[i]);
  const contentBase64 = btoa(binary);
  return api.post("/api/paper-extraction/uploads", { filename: file.name, content_base64: contentBase64 });
}

export interface StepCard {
  stepId: string;
  planId: string;
  phase: "design" | "build" | "test" | "learn";
  title: string;
  shortDescription: string;
  sourceType: "literature" | "AI_generated" | null;
}

export interface DetailPanel {
  stepId: string;
  what: string;
  why: { literatureReason: string[]; engineeringReason: string[]; aiReason: string[] };
  how: { operation: string; input: unknown[]; output: unknown[] };
  evidenceIds: string[];
  validationCheckpoint: string;
  risk: string[];
}

export interface EvidenceItem {
  evidenceId: string;
  paper: string;
  section: string[];
  page: number | null;
  quote: string;
  confidence: string | number;
  extractionMethod: string;
}

export interface K12AdaptationItem {
  paperId: string;
  compatibility: string;
  transferability: string;
  confidence: string | number;
  reason: string[];
  validationRequired: string[];
}

export interface RiskItem {
  category: string;
  detail: string;
  source: string;
}

export interface FrontendView {
  summary: {
    title: string;
    objective: string;
    objectiveSource: string;
    targetSystem: string;
    strategySummary: string;
    k12Compatibility: string;
    confidence: string | number;
    qualityGrade: string;
    qcStatus: string;
    reviewStatus: string;
  } | null;
  stepCards: StepCard[];
  detailPanels: DetailPanel[];
  evidence: { items: EvidenceItem[]; status: string };
  quality: { completeness: unknown; evidenceQuality: unknown; reproducibility: unknown; confidence: unknown; grade: unknown; missingInformation: string[] };
  k12: { items: K12AdaptationItem[] };
  risk: { riskLevel: string; risks: RiskItem[]; mitigation: string[] };
  governance: { qcStatus: string; reviewStatus: string; approvalRequired: boolean; displayStates: string[]; publicationStatus: string };
}

export interface RunResult {
  taskId: string;
  status: "CREATED" | "RUNNING" | "WAITING_REVIEW" | "COMPLETED" | "FAILED";
  frontendView: FrontendView | null;
  extractionSummary: ExtractionSummary | null;
  literatureCandidateCount: number;
  experimentalDesignCount: number;
  skillStates: Record<string, string>;
  skillProgress: Record<string, { completed: number; total: number }>;
  errors: Array<{ code?: string; message?: string; skill?: string; [key: string]: unknown }>;
  warnings: Array<{ skill: string; message: string; sourceCode?: string }>;
  extractedIdeas: ExtractedIdea[];
}

export interface ExtractedIdea {
  ideaId: string;
  title: string;
  summary: string;
  category: "genome" | "expression" | "metabolism" | "regulation" | "protein" | "other";
  source: {
    paperId: string;
    title: string;
    journal: string;
    year: string;
    doi: string;
  };
  evidenceIds: string[];
  raw: Record<string, unknown>;
}

export interface EvidenceQuote {
  evidenceId: string;
  quote: string;
  page: number | null;
  sectionPath: string[];
  figureId: string | null;
  tableId: string | null;
}

export interface DesignField {
  key: string;
  label: string;
  value: unknown;
  status: "reported" | "inferred" | "unknown" | "not_applicable" | string;
  statusLabel: string;
  confidence: number | null;
  evidence: EvidenceQuote[];
  verified: boolean;
}

export interface TargetStrain {
  paperOrganism: string | null;
  paperStrainRaw: string | null;
  paperStrainNormalized: string | null;
  role: string | null;
  paperLabel: string | null;
  lineageOrEngineeringContext: string | null;
  status: string | null;
  confidence: number | null;
  reasoning: string | null;
}

export interface ArticleTypeGate {
  articleType: string | null;
  isPrimaryExperimentalStudy: boolean | null;
  confidence: number | null;
  evidence: string[];
}

export interface PaperQuality {
  completeness: number | null;
  reproducibility: number | null;
  evidenceLevel: number | null;
  extractionConfidence: number | null;
  missingInformation: unknown[];
  overallScore: number | null;
  confidenceLabel: string | null;
  recommendation: string | null;
  dimensions: Record<string, { score?: number; reason?: string; [key: string]: unknown }>;
  risks: unknown[];
}

export interface PaperExtractionSummary {
  paperId: string;
  identity: { title: string | null; authors: string[]; journal: string | null; year: number | string | null; doi: string | null };
  articleType: ArticleTypeGate | null;
  targetStrains: TargetStrain[];
  designFields: DesignField[];
  hasDesignContent: boolean;
  quality: PaperQuality;
  coverage: { totalFields?: number; reportedFields?: number; fieldsWithEvidence?: number; unknownFields?: number; reportedEvidenceCoverage?: number; overallFieldCoverage?: number };
  governanceNote: string | null;
  /** Set once this paper has been auto-saved into "文献证据" (Literature
   * Evidence) - see harness/paper_extraction/ddr_converter.py::
   * ensure_task_saved_as_evidence, triggered on a completed-task poll.
   * `null` while the run is still in progress or the save hasn't happened
   * yet; the id of the resulting `knowledge/ddr_database/*.json` record
   * (its `ddr_id`) once it has. */
  evidenceSourceId: string | null;
}

export interface ExtractionSummary {
  taskId: string;
  status: string | null;
  taskUnderstanding: Record<string, unknown>;
  papers: PaperExtractionSummary[];
  governanceNote: string;
  reviewTasks: unknown[];
}

function toEvidenceQuotes(raw: unknown): EvidenceQuote[] {
  if (!Array.isArray(raw)) return [];
  return raw.map((e) => {
    const r = e as Record<string, unknown>;
    return {
      evidenceId: String(r.evidence_id ?? ""),
      quote: String(r.quote ?? ""),
      page: (r.page as number | null) ?? null,
      sectionPath: (r.section_path as string[]) ?? [],
      figureId: (r.figure_id as string | null) ?? null,
      tableId: (r.table_id as string | null) ?? null,
    };
  });
}

function toDesignFields(raw: unknown): DesignField[] {
  if (!Array.isArray(raw)) return [];
  return raw.map((f) => {
    const r = f as Record<string, unknown>;
    return {
      key: String(r.key ?? ""),
      label: String(r.label ?? r.key ?? ""),
      value: r.value,
      status: String(r.status ?? "unknown"),
      statusLabel: String(r.status_label ?? r.status ?? "unknown"),
      confidence: (r.confidence as number | null) ?? null,
      evidence: toEvidenceQuotes(r.evidence),
      verified: Boolean(r.verified),
    };
  });
}

function toTargetStrains(raw: unknown): TargetStrain[] {
  if (!Array.isArray(raw)) return [];
  return raw.map((s) => {
    const r = s as Record<string, unknown>;
    return {
      paperOrganism: (r.paper_organism as string | null) ?? null,
      paperStrainRaw: (r.paper_strain_raw as string | null) ?? null,
      paperStrainNormalized: (r.paper_strain_normalized as string | null) ?? null,
      role: (r.role as string | null) ?? null,
      paperLabel: (r.paper_label as string | null) ?? null,
      lineageOrEngineeringContext: (r.lineage_or_engineering_context as string | null) ?? null,
      status: (r.status as string | null) ?? null,
      confidence: (r.confidence as number | null) ?? null,
      reasoning: (r.reasoning as string | null) ?? null,
    };
  });
}

function toArticleType(raw: unknown): ArticleTypeGate | null {
  if (!raw || typeof raw !== "object") return null;
  const r = raw as Record<string, unknown>;
  return {
    articleType: (r.article_type as string | null) ?? null,
    isPrimaryExperimentalStudy: (r.is_primary_experimental_study as boolean | null) ?? null,
    confidence: (r.confidence as number | null) ?? null,
    evidence: (r.evidence as string[]) ?? [],
  };
}

/**
 * Decodes one paper's entry from `extraction_summary.papers[i]` (backend:
 * harness/paper_extraction/result_summary.py::build_extraction_summary).
 * Exported so `api/evidence.ts` can decode the same shape from
 * `paper_extraction_detail` (the same dict, embedded verbatim into a saved
 * DDR's `extraction_meta`) without duplicating this mapping.
 */
export function toPaperExtractionSummary(raw: Record<string, unknown>): PaperExtractionSummary {
  const identity = (raw.identity as Record<string, unknown>) ?? {};
  const quality = (raw.quality as Record<string, unknown>) ?? {};
  const coverage = (raw.coverage as Record<string, unknown>) ?? {};
  const paperGovernance = (raw.governance as Record<string, unknown>) ?? {};
  return {
    paperId: String(raw.paper_id ?? ""),
    identity: {
      title: (identity.title as string | null) ?? null,
      authors: (identity.authors as string[]) ?? [],
      journal: (identity.journal as string | null) ?? null,
      year: (identity.year as number | string | null) ?? null,
      doi: (identity.doi as string | null) ?? null,
    },
    articleType: toArticleType(raw.article_type),
    targetStrains: toTargetStrains(raw.target_strains),
    designFields: toDesignFields(raw.design_fields),
    hasDesignContent: Boolean(raw.has_design_content),
    quality: {
      completeness: (quality.completeness as number | null) ?? null,
      reproducibility: (quality.reproducibility as number | null) ?? null,
      evidenceLevel: (quality.evidence_level as number | null) ?? null,
      extractionConfidence: (quality.extraction_confidence as number | null) ?? null,
      missingInformation: (quality.missing_information as unknown[]) ?? [],
      overallScore: (quality.overall_score as number | null) ?? null,
      confidenceLabel: (quality.confidence_label as string | null) ?? null,
      recommendation: (quality.recommendation as string | null) ?? null,
      dimensions: (quality.dimensions as Record<string, { score?: number; reason?: string }>) ?? {},
      risks: (quality.risks as unknown[]) ?? [],
    },
    coverage: {
      totalFields: coverage.total_fields as number | undefined,
      reportedFields: coverage.reported_fields as number | undefined,
      fieldsWithEvidence: coverage.fields_with_evidence as number | undefined,
      unknownFields: coverage.unknown_fields as number | undefined,
      reportedEvidenceCoverage: coverage.reported_evidence_coverage as number | undefined,
      overallFieldCoverage: coverage.overall_field_coverage as number | undefined,
    },
    governanceNote: (paperGovernance.note as string | null) ?? null,
    evidenceSourceId: (raw.evidence_source_id as string | null) ?? null,
  };
}

function toExtractionSummary(raw: unknown): ExtractionSummary | null {
  if (!raw || typeof raw !== "object") return null;
  const r = raw as Record<string, unknown>;
  const papersRaw = (r.papers as Array<Record<string, unknown>>) ?? [];
  const governance = (r.governance as Record<string, unknown>) ?? {};
  return {
    taskId: String(r.task_id ?? ""),
    status: (r.status as string | null) ?? null,
    taskUnderstanding: (r.task_understanding as Record<string, unknown>) ?? {},
    governanceNote: String(governance.note ?? ""),
    reviewTasks: (governance.review_tasks as unknown[]) ?? [],
    papers: papersRaw.map(toPaperExtractionSummary),
  };
}

interface RawTaskResponse {
  task_id: string;
  status: string;
  error: string | null;
  skill_states?: Record<string, string>;
  skill_progress?: Record<string, { completed: number; total: number }>;
  skill_warnings?: Array<Record<string, unknown>>;
  extraction_summary?: Record<string, unknown> | null;
  result: {
    task_id: string;
    status: RunResult["status"];
    experimental_designs: Array<Record<string, unknown>>;
    validated_papers?: Array<Record<string, unknown>>;
    literature_candidates: Array<Record<string, unknown>>;
    frontend_view?: {
      summary_view?: Record<string, unknown>;
      step_cards?: Array<Record<string, unknown>>;
      detail_panels?: Array<Record<string, unknown>>;
      evidence_view?: { items?: Array<Record<string, unknown>>; status?: string };
      quality_view?: Record<string, unknown>;
      k12_adaptation_view?: { items?: Array<Record<string, unknown>> };
      risk_view?: { risk_level?: string; risks?: Array<Record<string, unknown>>; mitigation?: string[] };
      governance_view?: Record<string, unknown>;
    };
    skill_states: Record<string, string>;
    errors: Array<Record<string, unknown>>;
  } | null;
}

function toFrontendView(raw: RawTaskResponse["result"]): FrontendView | null {
  const fv = raw?.frontend_view;
  if (!fv || !fv.summary_view) return null;
  const s = fv.summary_view;
  return {
    summary: {
      title: String(s.title ?? "unknown"),
      objective: String(s.objective ?? "unknown"),
      objectiveSource: String(s.objective_source ?? "unknown"),
      targetSystem: String(s.target_system ?? "unknown"),
      strategySummary: String(s.strategy_summary ?? "unknown"),
      k12Compatibility: String(s.k12_compatibility ?? "unknown"),
      confidence: (s.confidence as string | number) ?? "unknown",
      qualityGrade: String(s.quality_grade ?? "unknown"),
      qcStatus: String(s.qc_status ?? "unknown"),
      reviewStatus: String(s.review_status ?? "unknown"),
    },
    stepCards: (fv.step_cards ?? []).map((c) => ({
      stepId: String(c.step_id ?? ""),
      planId: String(c.plan_id ?? ""),
      phase: c.phase as StepCard["phase"],
      title: String(c.title ?? "unknown"),
      shortDescription: String(c.short_description ?? ""),
      sourceType: (c.source_type as StepCard["sourceType"]) ?? null,
    })),
    detailPanels: (fv.detail_panels ?? []).map((p) => {
      const why = (p.why ?? {}) as Record<string, string[]>;
      const how = (p.how ?? {}) as Record<string, unknown>;
      return {
        stepId: String(p.step_id ?? ""),
        what: String(p.what ?? "unknown"),
        why: {
          literatureReason: why.literature_reason ?? [],
          engineeringReason: why.engineering_reason ?? [],
          aiReason: why.ai_reason ?? [],
        },
        how: { operation: String(how.operation ?? "unknown"), input: (how.input as unknown[]) ?? [], output: (how.output as unknown[]) ?? [] },
        evidenceIds: (p.evidence_ids as string[]) ?? [],
        validationCheckpoint: String(p.validation_checkpoint ?? "unknown"),
        risk: (p.risk as string[]) ?? [],
      };
    }),
    evidence: {
      items: (fv.evidence_view?.items ?? []).map((e) => ({
        evidenceId: String(e.evidence_id ?? ""),
        paper: String(e.paper ?? "unknown"),
        section: (e.section as string[]) ?? ["unknown"],
        page: (e.page as number | null) ?? null,
        quote: String(e.quote ?? "unknown"),
        confidence: (e.confidence as string | number) ?? "unknown",
        extractionMethod: String(e.extraction_method ?? "unknown"),
      })),
      status: fv.evidence_view?.status ?? "unknown",
    },
    quality: {
      completeness: fv.quality_view?.completeness ?? "unknown",
      evidenceQuality: fv.quality_view?.evidence_quality ?? "unknown",
      reproducibility: fv.quality_view?.reproducibility ?? "unknown",
      confidence: fv.quality_view?.confidence ?? "unknown",
      grade: fv.quality_view?.grade ?? "unknown",
      missingInformation: (fv.quality_view?.missing_information as string[]) ?? [],
    },
    k12: {
      items: (fv.k12_adaptation_view?.items ?? []).map((k) => ({
        paperId: String(k.paper_id ?? "unknown"),
        compatibility: String(k.compatibility ?? "unknown"),
        transferability: String(k.transferability ?? "unknown"),
        confidence: (k.confidence as string | number) ?? "unknown",
        reason: (k.reason as string[]) ?? [],
        validationRequired: (k.validation_required as string[]) ?? [],
      })),
    },
    risk: {
      riskLevel: fv.risk_view?.risk_level ?? "unknown",
      risks: (fv.risk_view?.risks ?? []).map((r) => ({
        category: String(r.category ?? "unknown"),
        detail: String(r.detail ?? "unknown"),
        source: String(r.source ?? "unknown"),
      })),
      mitigation: fv.risk_view?.mitigation ?? [],
    },
    governance: {
      qcStatus: String(fv.governance_view?.qc_status ?? "unknown"),
      reviewStatus: String(fv.governance_view?.review_status ?? "unknown"),
      approvalRequired: Boolean(fv.governance_view?.approval_required),
      displayStates: (fv.governance_view?.display_states as string[]) ?? [],
      publicationStatus: String(fv.governance_view?.publication_status ?? "unknown"),
    },
  };
}

export async function getRun(taskId: string): Promise<RunResult> {
  const r = await api.get<RawTaskResponse>(`/api/paper-extraction/tasks/${taskId}`);
  const result = r.result;
  return {
    taskId,
    status: (result?.status ?? (r.status === "failed" ? "FAILED" : "RUNNING")) as RunResult["status"],
    frontendView: toFrontendView(result),
    // Built from the checkpoint directly (harness/paper_extraction/result_summary.py),
    // so - unlike frontendView above - it's available for every result_level,
    // not just "engineering_plan", and updates paper-by-paper as the run
    // progresses rather than only once the whole pipeline finishes.
    extractionSummary: toExtractionSummary(r.extraction_summary),
    literatureCandidateCount: result?.literature_candidates?.length ?? 0,
    experimentalDesignCount: result?.experimental_designs?.length ?? 0,
    // Top-level `skill_states` reflects the run's live on-disk checkpoint
    // while it's still going (result?.skill_states is only ever populated
    // once the whole pipeline finishes) - lets the page show which step is
    // currently running instead of an undifferentiated spinner.
    skillStates: result?.skill_states ?? r.skill_states ?? {},
    // Only ever populated while RUNNING (see harness/api/paper_extraction.py) -
    // a finished result has nothing in progress, so this naturally clears itself.
    skillProgress: r.skill_progress ?? {},
    errors: result?.errors ?? (r.error ? [{ message: r.error }] : []),
    // Per-skill warning detail (harness/paper_extraction/vendor/.../workflow/engine.py's
    // `state["warnings"]`) - lets the UI explain *why* a step is WARNING
    // (e.g. "Figure/table count differs from parser content list.")
    // instead of just showing the bare status.
    warnings: (r.skill_warnings ?? []).map((w) => ({
      skill: String(w.skill ?? ""),
      message: String(w.message ?? w.source_code ?? "warning"),
      sourceCode: w.source_code != null ? String(w.source_code) : undefined,
    })),
    extractedIdeas: toExtractedIdeas(result),
  };
}

function textValue(value: unknown): string {
  if (typeof value === "string") return value;
  if (Array.isArray(value)) return value.map(textValue).filter(Boolean).join("；");
  if (value && typeof value === "object") {
    const record = value as Record<string, unknown>;
    return textValue(record.value ?? record.statement ?? record.description ?? record.summary ?? "");
  }
  return "";
}

function firstText(record: Record<string, unknown>, keys: string[]): string {
  for (const key of keys) {
    const value = textValue(record[key]);
    if (value && value !== "unknown") return value;
  }
  return "";
}

function toExtractedIdeas(raw: RawTaskResponse["result"]): ExtractedIdea[] {
  if (!raw) return [];
  const papers = [...(raw.validated_papers ?? []), ...(raw.literature_candidates ?? [])];
  const paperMap = new Map<string, Record<string, unknown>>(papers.map((paper) => [String(paper.paper_id ?? paper.id ?? ""), paper]));
  return (raw.experimental_designs ?? []).map((design, index) => {
    const fields = (design.fields && typeof design.fields === "object" ? design.fields : design) as Record<string, unknown>;
    const paperId = String(design.paper_id ?? design.source_paper_id ?? fields.paper_id ?? "");
    const paper: Record<string, unknown> = paperMap.get(paperId) ?? {};
    const blob = JSON.stringify(fields).toLowerCase();
    const category: ExtractedIdea["category"] =
      /knockout|knock-out|deletion|crispr|genome/.test(blob) ? "genome"
      : /overexpress|expression|promoter/.test(blob) ? "expression"
      : /metabolic|pathway|flux|fermentation/.test(blob) ? "metabolism"
      : /regulat|sensor|circuit|riboswitch/.test(blob) ? "regulation"
      : /protein|enzyme|mutation|directed evolution/.test(blob) ? "protein"
      : "other";
    return {
      ideaId: String(design.design_id ?? design.experimental_design_id ?? `${raw.task_id}:${index}`),
      title: firstText(fields, ["design_objective", "objective", "title", "research_question", "hypothesis"]) || `实验设计思路 ${index + 1}`,
      summary: firstText(fields, ["design_logic", "mechanism_logic", "rationale", "hypothesis", "workflow", "experimental_design"]) || "抽取结果中尚未提供可直接展示的总结。",
      category,
      source: {
        paperId,
        title: String(paper.title ?? design.paper_title ?? "来源题名未报告"),
        journal: String(paper.journal ?? paper.venue ?? "期刊未报告"),
        year: String(paper.year ?? paper.publication_year ?? "年份未报告"),
        doi: String((paper.identifiers as Record<string, unknown> | undefined)?.doi ?? paper.doi ?? ""),
      },
      evidenceIds: (design.evidence_ids as string[] | undefined) ?? (fields.evidence_ids as string[] | undefined) ?? [],
      raw: design,
    };
  });
}
