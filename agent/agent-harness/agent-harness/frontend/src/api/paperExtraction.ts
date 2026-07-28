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
  literatureCandidateCount: number;
  experimentalDesignCount: number;
  skillStates: Record<string, string>;
  skillProgress: Record<string, { completed: number; total: number }>;
  errors: Array<{ code?: string; message?: string; skill?: string; [key: string]: unknown }>;
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

interface RawTaskResponse {
  task_id: string;
  status: string;
  error: string | null;
  skill_states?: Record<string, string>;
  skill_progress?: Record<string, { completed: number; total: number }>;
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
