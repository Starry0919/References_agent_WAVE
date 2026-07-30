import type { RunResult } from "@/api/paperExtraction";

export const PAPER_EXTRACTION_SKILLS = {
  skill01: "skill01_requirement_parser",
  skill02: "skill02_literature_retrieval",
  skill03: "skill03_citation_validation",
  skill04: "skill04_pdf_acquisition",
  skill05: "skill05_pdf_parser",
  skill06: "skill06_markdown_cleaner",
  skill07: "skill07_experiment_extraction",
  skill08: "skill08_evidence_binding",
  skill09: "skill09_quality_evaluation",
  skill10: "skill10_k12_transfer",
  skill11: "skill11_engineering_proposal",
  skill12: "skill12_qc_human_review",
  skill13: "skill13_frontend_adapter",
} as const;

export type KnownPaperExtractionSkillId =
  (typeof PAPER_EXTRACTION_SKILLS)[keyof typeof PAPER_EXTRACTION_SKILLS];

export type ProgressTone =
  | "active"
  | "success"
  | "warning"
  | "review"
  | "blocked"
  | "failed";

export interface PaperExtractionProgressStage {
  skillId: string;
  status: string;
  isCurrent: boolean;
}

export interface PaperExtractionProgressSnapshot {
  percentage: number;
  currentSkillId: string | null;
  currentStatus: string;
  tone: ProgressTone;
  stages: PaperExtractionProgressStage[];
  activeItemProgress: { completed: number; total: number } | null;
}

const {
  skill01,
  skill02,
  skill03,
  skill04,
  skill05,
  skill06,
  skill07,
  skill08,
  skill09,
  skill10,
  skill11,
  skill12,
  skill13,
} = PAPER_EXTRACTION_SKILLS;

/**
 * A manual PDF run is the common path for this page. Auto-search and DOI
 * stages are inferred as soon as their checkpoint entries appear, while the
 * optional K12/engineering/frontend stages are appended only when the
 * backend actually schedules them.
 */
const UPLOAD_PLAN = [skill01, skill04, skill05, skill06, skill07, skill08, skill09, skill12];
const AUTO_SEARCH_PLAN = [skill01, skill02, skill03, skill04, skill05, skill06, skill07, skill08, skill09, skill12];
const DOI_PLAN = [skill01, skill03, skill04, skill05, skill06, skill07, skill08, skill09, skill12];
const OPTIONAL_SKILLS = [skill10, skill11, skill13];

/**
 * Weights reflect expected wall-clock work, not simply the number of stages.
 * Model-based experimental-design extraction is deliberately the largest
 * segment; otherwise a run would appear almost finished before its slowest
 * operation starts.
 */
const SKILL_WEIGHTS: Record<string, number> = {
  [skill01]: 5,
  [skill02]: 8,
  [skill03]: 7,
  [skill04]: 8,
  [skill05]: 12,
  [skill06]: 8,
  [skill07]: 42,
  [skill08]: 12,
  [skill09]: 8,
  [skill10]: 8,
  [skill11]: 10,
  [skill12]: 5,
  [skill13]: 4,
};

const COMPLETE_STATUSES = new Set(["SUCCESS", "WARNING", "REVIEW_REQUIRED"]);
const ACTIVE_STATUSES = new Set(["RUNNING", "IN_PROGRESS"]);
const FAILED_STATUSES = new Set(["FAILED", "ERROR"]);
const BLOCKED_STATUSES = new Set(["BLOCKED"]);
const OMITTED_STATUSES = new Set(["SKIPPED"]);

function normalizeStatus(status: string | undefined): string {
  return (status || "NOT_STARTED").toUpperCase();
}

function buildPlan(skillStates: Record<string, string>): string[] {
  const ids = Object.keys(skillStates);
  const base = ids.includes(skill02)
    ? AUTO_SEARCH_PLAN
    : ids.includes(skill03)
      ? DOI_PLAN
      : UPLOAD_PLAN;
  const optional = OPTIONAL_SKILLS.filter((skillId) => ids.includes(skillId));
  const known = new Set<string>([...base, ...optional]);
  const unexpected = ids.filter((skillId) => !known.has(skillId)).sort();

  // Optional stages run before QC except the final frontend adapter. Insert
  // them in their actual pipeline order instead of merely appending them.
  const beforeQc = optional.filter((skillId) => skillId !== skill13);
  const planWithoutQc = base.filter((skillId) => skillId !== skill12);
  return [...planWithoutQc, ...beforeQc, skill12, ...(optional.includes(skill13) ? [skill13] : []), ...unexpected];
}

function partialStageFraction(
  skillId: string,
  status: string,
  skillProgress: RunResult["skillProgress"],
): number {
  if (COMPLETE_STATUSES.has(status)) return 1;
  if (ACTIVE_STATUSES.has(status)) {
    const itemProgress = skillProgress[skillId];
    if (itemProgress && itemProgress.total > 0) {
      const ratio = itemProgress.completed / itemProgress.total;
      // A stage that still reports RUNNING must retain some visible work.
      return Math.min(0.9, Math.max(0.08, ratio));
    }
    // "Reached and working" is real information, but is not a time estimate.
    return 0.12;
  }
  // A failed/blocked stage was entered, but did not complete.
  if (FAILED_STATUSES.has(status) || BLOCKED_STATUSES.has(status)) return 0.08;
  return 0;
}

function resolveCurrentSkill(
  plan: string[],
  states: Record<string, string>,
  runStatus: RunResult["status"],
): string | null {
  const withStatus = plan.map((skillId) => ({
    skillId,
    status: normalizeStatus(states[skillId]),
  }));
  const active = withStatus.find(({ status }) => ACTIVE_STATUSES.has(status));
  if (active) return active.skillId;
  const stopped = withStatus.find(({ status }) => FAILED_STATUSES.has(status) || BLOCKED_STATUSES.has(status));
  if (stopped) return stopped.skillId;

  if (runStatus === "COMPLETED") return withStatus.at(-1)?.skillId ?? null;
  if (runStatus === "FAILED") {
    return [...withStatus].reverse().find(({ status }) => status !== "NOT_STARTED")?.skillId ?? withStatus[0]?.skillId ?? null;
  }

  const next = withStatus.find(({ status }) => status === "PENDING" || status === "NOT_STARTED");
  if (next) return next.skillId;
  return [...withStatus].reverse().find(({ status }) => status !== "SKIPPED")?.skillId ?? null;
}

function resolveTone(runStatus: RunResult["status"], currentStatus: string, states: Record<string, string>): ProgressTone {
  if (runStatus === "FAILED" || FAILED_STATUSES.has(currentStatus)) return "failed";
  if (BLOCKED_STATUSES.has(currentStatus)) return "blocked";
  if (runStatus === "WAITING_REVIEW" || currentStatus === "REVIEW_REQUIRED") return "review";
  if (runStatus === "COMPLETED") {
    return Object.values(states).some((status) => normalizeStatus(status) === "WARNING") ? "warning" : "success";
  }
  return "active";
}

export function calculatePaperExtractionProgress(
  runStatus: RunResult["status"],
  skillStates: RunResult["skillStates"],
  skillProgress: RunResult["skillProgress"],
): PaperExtractionProgressSnapshot {
  const plan = buildPlan(skillStates);
  const included = plan.filter((skillId) => !OMITTED_STATUSES.has(normalizeStatus(skillStates[skillId])));
  const totalWeight = included.reduce((sum, skillId) => sum + (SKILL_WEIGHTS[skillId] ?? 4), 0);
  const earnedWeight = included.reduce((sum, skillId) => {
    const status = normalizeStatus(skillStates[skillId]);
    return sum + (SKILL_WEIGHTS[skillId] ?? 4) * partialStageFraction(skillId, status, skillProgress);
  }, 0);

  let percentage = totalWeight > 0 ? Math.round((earnedWeight / totalWeight) * 100) : 0;
  if (runStatus === "COMPLETED") percentage = 100;
  else percentage = Math.min(99, Math.max(0, percentage));
  // Submission has been accepted and the worker may be creating its first
  // checkpoint. Showing 1% distinguishes that short preparation window from
  // a task that has not started at all, without pretending a stage completed.
  if (runStatus === "RUNNING" && percentage === 0) percentage = 1;

  const currentSkillId = resolveCurrentSkill(plan, skillStates, runStatus);
  const currentStatus = currentSkillId ? normalizeStatus(skillStates[currentSkillId]) : normalizeStatus(runStatus);
  const progress = currentSkillId ? skillProgress[currentSkillId] : undefined;
  const activeItemProgress = progress && progress.total > 1
    ? { completed: progress.completed, total: progress.total }
    : null;

  return {
    percentage,
    currentSkillId,
    currentStatus,
    tone: resolveTone(runStatus, currentStatus, skillStates),
    stages: plan.map((skillId) => ({
      skillId,
      status: normalizeStatus(skillStates[skillId]),
      isCurrent: skillId === currentSkillId,
    })),
    activeItemProgress,
  };
}
