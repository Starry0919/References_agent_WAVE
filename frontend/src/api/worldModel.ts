import { api } from "./client";

export interface StateTransition {
  transition_id: string;
  initial_state: { summary?: string; entities_involved?: string[] };
  perturbation: { type?: string; target?: string; description?: string };
  final_state: { summary?: string; entities_involved?: string[] };
  observed_changes: Array<Record<string, unknown>>;
  mechanism: string;
  phenotype: string | null;
  context: Record<string, unknown>;
  origin: string;
  status: string;
  evidence_id: string | null;
  outcome: string;
  uncertainty: Record<string, unknown> | null;
}

export interface TransitionGraph {
  nodes: Array<{ id: string; label: string; snapshot_id: string | null; entities_involved: string[] }>;
  edges: Array<{ source: string; target: string; transition_id: string; perturbation_type: string; origin: string; status: string; outcome: string }>;
}

export async function listWorldModelTransitions(projectId: string) {
  return api.get<{ total: number; transitions: StateTransition[] }>(`/api/world-model/transitions?project_id=${encodeURIComponent(projectId)}`);
}

export async function getWorldModelTransitionGraph(projectId: string) {
  return api.get<TransitionGraph>(`/api/world-model/transition-graph?project_id=${encodeURIComponent(projectId)}`);
}
