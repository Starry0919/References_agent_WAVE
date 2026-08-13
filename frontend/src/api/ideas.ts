import { api } from "./client";

/**
 * Idea Capture adapter (harness/api/ideas.py, real). A `ProjectIdea` is the
 * user's own free text - a genuinely new entity_type, never merged into or
 * confused with knowledge-base-derived content (EvidenceItem/
 * KnowledgeClaim). `linkToDesign` only records a hand-off; it never
 * fabricates a simulation result (see `harness/ideas/service.py`'s
 * docstring - real predictions still require a bridged DesignVersion).
 */
export type IdeaStatus = "captured" | "linked_to_design" | "dismissed";

export interface ProjectIdea {
  ideaId: string;
  projectId: string;
  actorId: string;
  freeText: string;
  targetGene: string | null;
  modificationType: string | null;
  rationale: string | null;
  status: IdeaStatus;
  linkedDesignProjectId: string | null;
  createdAt: number;
}

interface RawIdea {
  idea_id: string;
  project_id: string;
  actor_id: string;
  free_text: string;
  target_gene: string | null;
  modification_type: string | null;
  rationale: string | null;
  status: IdeaStatus;
  linked_design_project_id: string | null;
  created_at: number;
}

function toIdea(r: RawIdea): ProjectIdea {
  return {
    ideaId: r.idea_id,
    projectId: r.project_id,
    actorId: r.actor_id,
    freeText: r.free_text,
    targetGene: r.target_gene,
    modificationType: r.modification_type,
    rationale: r.rationale,
    status: r.status,
    linkedDesignProjectId: r.linked_design_project_id,
    createdAt: r.created_at,
  };
}

export async function captureIdea(
  projectId: string,
  input: { actorId: string; freeText: string; targetGene?: string; modificationType?: string; rationale?: string },
): Promise<ProjectIdea> {
  const r = await api.post<RawIdea>(`/api/projects/${projectId}/ideas`, {
    actor_id: input.actorId,
    free_text: input.freeText,
    target_gene: input.targetGene || null,
    modification_type: input.modificationType || null,
    rationale: input.rationale || null,
  });
  return toIdea(r);
}

export interface RankedIdeas {
  ideas: ProjectIdea[];
  /** Set only when `rankForDesignProjectId` was passed and at least one idea's free text
   * actually overlaps the design project's originating diagnosis hypotheses - never a
   * fabricated suggestion when nothing really matched. */
  recommendedIdeaId: string | null;
}

/** `rankForDesignProjectId`, when given, orders the result by relevance to that design
 * project's originating diagnosis hypotheses (`harness/ideas/matching.py`) instead of the
 * default newest-first order - lets the UI pre-suggest a likely idea instead of a blank pick. */
export async function listIdeas(projectId: string, rankForDesignProjectId?: string): Promise<RankedIdeas> {
  const suffix = rankForDesignProjectId ? `?rank_for_design_project_id=${encodeURIComponent(rankForDesignProjectId)}` : "";
  const r = await api.get<{ ideas: RawIdea[]; recommended_idea_id: string | null }>(`/api/projects/${projectId}/ideas${suffix}`);
  return { ideas: r.ideas.map(toIdea), recommendedIdeaId: r.recommended_idea_id };
}

export async function linkIdeaToDesign(ideaId: string, input: { designProjectId: string; actorId: string }): Promise<ProjectIdea> {
  const r = await api.post<RawIdea>(`/api/ideas/${ideaId}/link-to-design`, {
    design_project_id: input.designProjectId,
    actor_id: input.actorId,
  });
  return toIdea(r);
}

export async function dismissIdea(ideaId: string, actorId: string): Promise<ProjectIdea> {
  const r = await api.post<RawIdea>(`/api/ideas/${ideaId}/dismiss`, { actor_id: actorId });
  return toIdea(r);
}
