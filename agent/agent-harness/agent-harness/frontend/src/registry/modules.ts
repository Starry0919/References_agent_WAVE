import type { CapabilityAvailability } from "@/types/domain";
import type { DictKey } from "@/lib/i18n";

/**
 * Lightweight module registry (prompt §18.1). New top-level pages or
 * Workspace stages register here; AppShell/TopNav/WorkflowStageRail read
 * this list rather than hard-coding a second/third copy of nav+route+
 * capability state (the prompt explicitly forbids that drift).
 */
export interface TopLevelModule {
  id: string;
  route: string;
  labelKey: string;
  requiresProjectContext: boolean;
  navVisible: boolean;
}

export const TOP_LEVEL_MODULES: TopLevelModule[] = [
  { id: "command-center", route: "/projects/:projectId", labelKey: "nav.commandCenter", requiresProjectContext: true, navVisible: true },
  { id: "idea-workspace", route: "/projects/:projectId/ideas", labelKey: "nav.ideaWorkspace", requiresProjectContext: true, navVisible: true },
  { id: "knowledge", route: "/projects/:projectId/knowledge", labelKey: "nav.knowledge", requiresProjectContext: true, navVisible: true },
];


/**
 * Static capability roster from the Repository Truth Audit (Deliverable 4
 * has the full evidence trail). `available` = real endpoint exists and is
 * reachable when the backend is up; `partial` = real endpoint exists but a
 * needed query/list capability is missing; this is deliberately NOT a
 * runtime health check - CapabilityState components layer the live
 * /api/health probe on top of this static roster.
 */
export const BACKEND_CAPABILITIES: Record<string, { availability: CapabilityAvailability; reasonKey: DictKey }> = {
  projects: { availability: "available", reasonKey: "capability.reason.projects" },
  orchestrator: { availability: "partial", reasonKey: "capability.reason.orchestrator" },
  diagnosis: { availability: "available", reasonKey: "capability.reason.diagnosis" },
  engineering_design: { availability: "partial", reasonKey: "capability.reason.engineering_design" },
  virtual_cell: { availability: "partial", reasonKey: "capability.reason.virtual_cell" },
  scientific_evaluation: { availability: "partial", reasonKey: "capability.reason.scientific_evaluation" },
  evidence_generation: { availability: "available", reasonKey: "capability.reason.evidence_generation" },
  golden_set: { availability: "partial", reasonKey: "capability.reason.golden_set" },
  learning: { availability: "partial", reasonKey: "capability.reason.learning" },
  experiments: { availability: "partial", reasonKey: "capability.reason.experiments" },
  paper_extraction: { availability: "available", reasonKey: "capability.reason.paper_extraction" },
  memory: { availability: "absent", reasonKey: "capability.reason.memory" },
  consolidated_approvals: { availability: "absent", reasonKey: "capability.reason.consolidated_approvals" },
  reviewer_authority: { availability: "absent", reasonKey: "capability.reason.reviewer_authority" },
};
