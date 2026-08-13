import { api } from "./client";
export interface RuntimeTask { task_id: string; objective: string; current_stage: string; task_status: string; completed_steps: string[]; pending_steps: string[]; human_actions: Array<Record<string, unknown>>; failure: Record<string, unknown> | null; }
export interface RuntimeNode { node_id: string; capability_name: string; module_name: string; dependencies: string[]; status: string; requires_human_approval: boolean; }
export interface RuntimeExecution { execution_id: string; capability_name: string; module_or_tool: string; output_payload: Record<string, unknown>; error: Record<string, unknown> | null; started_at: number; }
export async function listRuntimeTasks(projectId: string) { return api.get<{ tasks: RuntimeTask[] }>(`/api/scientific-runtime/tasks?project_id=${encodeURIComponent(projectId)}`); }
export async function getRuntimeTask(taskId: string) { return api.get<{ task: RuntimeTask; graph: RuntimeNode[]; executions: RuntimeExecution[] }>(`/api/scientific-runtime/tasks/${encodeURIComponent(taskId)}`); }
export async function submitRuntimeDecision(taskId: string, decision: string, actorId: string, reason = "") { return api.post<RuntimeTask>(`/api/scientific-runtime/tasks/${encodeURIComponent(taskId)}/human-action`, { decision, actor_id: actorId, reason }); }
