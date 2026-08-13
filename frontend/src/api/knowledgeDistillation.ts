import { api } from "./client";

/**
 * Biological Knowledge Distillation module (harness/api/knowledge_distillation.py
 * -> harness/knowledge_distillation/, vendoring the 13-step pipeline). Real,
 * async, file-backed - sibling of paperExtraction.ts, same polling shape,
 * but a different knowledge asset: EngineeringPrinciple/DecisionRule/
 * DesignPattern/ValidationStrategy/FailurePattern objects distilled from
 * textbook/monograph/guideline text, not ExperimentalCase objects from a
 * paper. Phase 1 (see biological_knowledge_distillation/README.md): only
 * pasted text or plain-text/Markdown uploads, no PDF/OCR yet.
 */

export interface SourceInput {
  text?: string;
  filePath?: string;
  title?: string;
  authors?: string[];
  publisher?: string;
  publicationYear?: number;
  isbn?: string[];
  doi?: string;
  edition?: string;
  chapter?: string;
  pageRange?: string;
  sourceType?: string;
}

export interface RunSubmission {
  projectId?: string;
  userRequest: string;
  sources: SourceInput[];
  targetDomain?: string[];
  targetOrganism?: string[];
  targetStrain?: string[];
  targetEngineeringGoal?: string[];
  requestedOutputLevel?: string[];
  requiresFrontendAdapter?: boolean;
  paperCaseArtifacts?: Array<Record<string, unknown>>;
  automatic?: boolean;
  humanReview?: boolean;
}

export async function submitRun(input: RunSubmission): Promise<{ task_id: string; status: string }> {
  return api.post("/api/knowledge-distillation/tasks", {
    project_id: input.projectId ?? null,
    user_request: input.userRequest,
    sources: input.sources.map((s) => ({
      text: s.text ?? null,
      file_path: s.filePath ?? null,
      title: s.title ?? "",
      authors: s.authors ?? [],
      publisher: s.publisher ?? "",
      publication_year: s.publicationYear ?? null,
      isbn: s.isbn ?? [],
      doi: s.doi ?? "",
      edition: s.edition ?? "",
      chapter: s.chapter ?? "",
      page_range: s.pageRange ?? "",
      source_type: s.sourceType ?? "",
    })),
    target_domain: input.targetDomain ?? [],
    target_organism: input.targetOrganism ?? [],
    target_strain: input.targetStrain ?? [],
    target_engineering_goal: input.targetEngineeringGoal ?? [],
    requested_output_level: input.requestedOutputLevel ?? [],
    requires_frontend_adapter: input.requiresFrontendAdapter ?? true,
    paper_case_artifacts: input.paperCaseArtifacts ?? [],
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
  sourceCount: number;
  projectId: string | null;
}

export async function listRuns(projectId?: string): Promise<RunHistoryItem[]> {
  const r = await api.get<{
    tasks: Array<{ task_id: string; status: string; error: string | null; submitted_at: number; user_request: string; source_count: number; project_id: string | null }>;
  }>(`/api/knowledge-distillation/tasks${projectId ? `?project_id=${encodeURIComponent(projectId)}` : ""}`);
  return r.tasks.map((t) => ({
    taskId: t.task_id,
    status: t.status,
    error: t.error,
    submittedAt: t.submitted_at,
    userRequest: t.user_request,
    sourceCount: t.source_count,
    projectId: t.project_id,
  }));
}

export async function uploadSource(file: File): Promise<{ path: string; filename: string }> {
  const buffer = await file.arrayBuffer();
  let binary = "";
  const bytes = new Uint8Array(buffer);
  for (let i = 0; i < bytes.length; i++) binary += String.fromCharCode(bytes[i]);
  const contentBase64 = btoa(binary);
  return api.post("/api/knowledge-distillation/uploads", { filename: file.name, content_base64: contentBase64 });
}

/** A number or the confidenceBreakdown object (framework/unified-schema.json
 * #/$defs/confidenceBreakdown) - Step09/Step10 output the object form,
 * earlier steps a plain float. */
type ConfidenceValue = number | { value?: number; band?: string; rationale?: string };

function confidenceNumber(c: ConfidenceValue | undefined): number | null {
  if (typeof c === "number") return c;
  if (c && typeof c.value === "number") return c.value;
  return null;
}

export interface KnowledgeObjectView {
  id: string;
  nameZh: string;
  nameEn: string;
  definition: string;
  derivationType: string;
  confidence: number | null;
  requiresHumanReview: boolean;
  evidenceCount: number;
  sourceIds: string[];
}

export interface EngineeringPrincipleView extends KnowledgeObjectView {
  triggerConditions: string[];
  recommendedActions: string[];
  doNotGeneralizeTo: string[];
  alternatives: string[];
  pedagogicalSimplification: boolean;
}

function evidenceSourceIds(evidence: unknown): string[] {
  if (!Array.isArray(evidence)) return [];
  const ids = evidence.map((e) => (e && typeof e === "object" ? String((e as Record<string, unknown>).source_id ?? "") : "")).filter(Boolean);
  return Array.from(new Set(ids));
}

function toPrincipleView(raw: Record<string, unknown>): EngineeringPrincipleView {
  return {
    id: String(raw.principle_id ?? ""),
    nameZh: String(raw.name_zh ?? ""),
    nameEn: String(raw.name_en ?? ""),
    definition: String(raw.principle_statement_en ?? raw.principle_statement_zh ?? ""),
    derivationType: String(raw.derivation_type ?? "unknown"),
    confidence: confidenceNumber(raw.confidence as ConfidenceValue),
    requiresHumanReview: Boolean(raw.requires_human_review),
    evidenceCount: Array.isArray(raw.evidence) ? raw.evidence.length : 0,
    sourceIds: evidenceSourceIds(raw.evidence),
    triggerConditions: (raw.trigger_conditions as string[]) ?? [],
    recommendedActions: (raw.recommended_actions as string[]) ?? [],
    doNotGeneralizeTo: (raw.do_not_generalize_to as string[]) ?? [],
    alternatives: (raw.alternatives as string[]) ?? [],
    pedagogicalSimplification: Boolean(raw.pedagogical_simplification),
  };
}

function toKnowledgeObjectView(raw: Record<string, unknown>, idField: string): KnowledgeObjectView {
  return {
    id: String(raw[idField] ?? ""),
    nameZh: String(raw.name_zh ?? ""),
    nameEn: String(raw.name_en ?? raw.decision_topic ?? ""),
    definition: String(raw.definition_en ?? raw.definition_zh ?? raw.question_en ?? raw.design_intent ?? raw.target_claim ?? ""),
    derivationType: String(raw.derivation_type ?? "unknown"),
    confidence: confidenceNumber(raw.confidence as ConfidenceValue),
    requiresHumanReview: Boolean(raw.requires_human_review ?? raw.human_review_status === "pending"),
    evidenceCount: Array.isArray(raw.evidence) ? raw.evidence.length : 0,
    sourceIds: evidenceSourceIds(raw.evidence),
  };
}

export interface RunResult {
  taskId: string;
  status: "CREATED" | "RUNNING" | "WAITING_REVIEW" | "COMPLETED" | "FAILED";
  concepts: KnowledgeObjectView[];
  mechanisms: KnowledgeObjectView[];
  engineeringPrinciples: EngineeringPrincipleView[];
  decisionRules: KnowledgeObjectView[];
  designPatterns: KnowledgeObjectView[];
  failurePatterns: KnowledgeObjectView[];
  qualityReport: Record<string, unknown> | null;
  governance: Record<string, "allowed" | "review" | "blocked" | string> | null;
  stepStates: Record<string, string>;
  errors: Array<{ error_code?: string; message?: string; step?: string; [key: string]: unknown }>;
}

interface RawTaskResponse {
  task_id: string;
  status: string;
  error: string | null;
  step_states?: Record<string, string>;
  result: {
    task_id: string;
    status: RunResult["status"];
    biological_concepts?: Array<Record<string, unknown>>;
    biological_mechanisms?: Array<Record<string, unknown>>;
    engineering_principles?: Array<Record<string, unknown>>;
    decision_rules?: Array<Record<string, unknown>>;
    design_patterns?: Array<Record<string, unknown>>;
    failure_patterns?: Array<Record<string, unknown>>;
    quality_report?: Record<string, unknown>;
    governance?: Record<string, unknown>;
    step_states: Record<string, string>;
    errors: Array<Record<string, unknown>>;
  } | null;
}

export async function getRun(taskId: string): Promise<RunResult> {
  const r = await api.get<RawTaskResponse>(`/api/knowledge-distillation/tasks/${taskId}`);
  const result = r.result;
  return {
    taskId,
    status: (result?.status ?? (r.status === "failed" ? "FAILED" : "RUNNING")) as RunResult["status"],
    concepts: (result?.biological_concepts ?? []).map((c) => toKnowledgeObjectView(c, "knowledge_id")),
    mechanisms: (result?.biological_mechanisms ?? []).map((c) => toKnowledgeObjectView(c, "knowledge_id")),
    engineeringPrinciples: (result?.engineering_principles ?? []).map(toPrincipleView),
    decisionRules: (result?.decision_rules ?? []).map((c) => toKnowledgeObjectView(c, "decision_rule_id")),
    designPatterns: (result?.design_patterns ?? []).map((c) => toKnowledgeObjectView(c, "pattern_id")),
    failurePatterns: (result?.failure_patterns ?? []).map((c) => toKnowledgeObjectView(c, "failure_pattern_id")),
    qualityReport: result?.quality_report ?? null,
    governance: (result?.governance as RunResult["governance"]) ?? null,
    // Top-level `step_states` reflects the live on-disk checkpoint while the
    // run is still going (result?.step_states is only populated once the
    // whole pipeline finishes) - same rationale as paperExtraction.ts.
    stepStates: result?.step_states ?? r.step_states ?? {},
    errors: result?.errors ?? (r.error ? [{ message: r.error }] : []),
  };
}
