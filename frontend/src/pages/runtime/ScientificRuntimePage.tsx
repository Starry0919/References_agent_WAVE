import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Activity, ArrowRight } from "lucide-react";
import { useParams } from "react-router-dom";
import { getRuntimeTask, listRuntimeTasks, submitRuntimeDecision } from "@/api/scientificRuntime";
import { EmptyState } from "@/components/common/EmptyState";

export function ScientificRuntimePage() {
  const { projectId = "" } = useParams<{ projectId: string }>(); const qc = useQueryClient();
  const tasks = useQuery({ queryKey: ["runtime-tasks", projectId], queryFn: () => listRuntimeTasks(projectId), enabled: !!projectId });
  const activeId = tasks.data?.tasks[0]?.task_id;
  const detail = useQuery({ queryKey: ["runtime-task", activeId], queryFn: () => getRuntimeTask(activeId as string), enabled: !!activeId });
  const decide = useMutation({ mutationFn: ({ decision }: { decision: string }) => submitRuntimeDecision(activeId as string, decision, "frontend-reviewer"), onSuccess: () => qc.invalidateQueries({ queryKey: ["runtime-task", activeId] }) });
  if (tasks.isLoading) return <EmptyState variant="loading" />;
  if (!activeId) return <EmptyState variant="no_result" title="No scientific task" detail="Create a task through the Scientific Runtime API to track a human-governed multi-module workflow." />;
  const data = detail.data;
  return <main className="min-h-full flex-1 overflow-y-auto bg-surface-sunken p-5"><div className="mx-auto flex max-w-5xl flex-col gap-4">
    <header><h1 className="flex items-center gap-2 text-xl font-semibold text-ink"><Activity size={20}/>Scientific Agent Runtime</h1><p className="mt-1 text-sm text-ink-muted">Execution control plane only; scientific reasoning remains in Modules 2–4.</p></header>
    {data && <><section className="panel p-4"><div className="flex justify-between gap-3"><div><span className="font-mono text-[10px] text-ink-faint">{data.task.task_id}</span><h2 className="mt-1 font-semibold text-ink">{data.task.objective}</h2></div><span className="h-fit rounded border border-border px-2 py-1 text-xs">{data.task.task_status} · {data.task.current_stage}</span></div>{data.task.failure && <p className="mt-2 text-xs text-state-danger">Failure: {String(data.task.failure.message ?? "unknown")}</p>}</section>
    <section className="panel p-4"><h2 className="text-sm font-semibold text-ink">Task graph</h2><div className="mt-3 flex flex-wrap items-center gap-2">{data.graph.map((n, i) => <div key={n.node_id} className="flex items-center gap-2"><div className="rounded border border-border bg-surface px-2 py-1.5 text-xs"><div className="font-medium text-ink">{n.capability_name}</div><div className="text-[10px] text-ink-faint">{n.module_name} · {n.status}</div></div>{i < data.graph.length - 1 && <ArrowRight size={12} className="text-ink-faint"/>}</div>)}</div></section>
    <section className="panel p-4"><h2 className="text-sm font-semibold text-ink">Execution history</h2>{data.executions.length === 0 ? <p className="mt-2 text-xs text-ink-muted">No capability executions recorded.</p> : <ul className="mt-2 space-y-2 text-xs">{data.executions.map(e => <li key={e.execution_id} className="rounded border border-border p-2"><span className="font-medium">{e.capability_name}</span> via {e.module_or_tool}</li>)}</ul>}</section>
    {data.task.task_status === "human_review" && <section className="panel p-4"><h2 className="text-sm font-semibold text-ink">Human action required</h2><div className="mt-3 flex gap-2"><button className="btn-primary" onClick={() => decide.mutate({decision:"approve"})}>Approve</button><button className="btn-secondary" onClick={() => decide.mutate({decision:"request_modification"})}>Request modification</button><button className="btn-secondary" onClick={() => decide.mutate({decision:"reject"})}>Reject</button></div></section>}</>}
  </div></main>;
}
