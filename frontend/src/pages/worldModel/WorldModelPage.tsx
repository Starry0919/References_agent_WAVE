import { useQuery } from "@tanstack/react-query";
import { ArrowRight, Network } from "lucide-react";
import { Link, useParams } from "react-router-dom";
import { getWorldModelTransitionGraph, listWorldModelTransitions } from "@/api/worldModel";
import { EmptyState } from "@/components/common/EmptyState";

export function WorldModelPage() {
  const { projectId = "" } = useParams<{ projectId: string }>();
  const transitions = useQuery({ queryKey: ["world-model-transitions", projectId], queryFn: () => listWorldModelTransitions(projectId), enabled: !!projectId });
  const graph = useQuery({ queryKey: ["world-model-graph", projectId], queryFn: () => getWorldModelTransitionGraph(projectId), enabled: !!projectId });

  return <main className="min-h-full flex-1 overflow-y-auto bg-surface-sunken p-5">
    <div className="mx-auto flex max-w-5xl flex-col gap-4">
      <header><h1 className="flex items-center gap-2 text-xl font-semibold text-ink"><Network size={20} />Biological Engineering World Model</h1><p className="mt-1 text-sm text-ink-muted">E. coli K-12 · tryptophan improvement · maintain growth. Stored evidence-grounded transitions only; no state prediction.</p></header>
      {(transitions.isLoading || graph.isLoading) && <EmptyState variant="loading" />}
      {transitions.data?.transitions.length === 0 && <EmptyState variant="no_result" title="No represented transitions" detail="Transitions appear after an evidence-backed experiment, simulation, or curated record is explicitly stored." />}
      <section className="grid gap-3 md:grid-cols-2">
        {transitions.data?.transitions.map((item) => <article key={item.transition_id} className="panel p-4 text-xs">
          <div className="flex items-center justify-between"><span className="font-mono text-[10px] text-ink-faint">{item.transition_id}</span><span className="rounded border border-border px-1.5 py-0.5">{item.status} · {item.origin}</span></div>
          <div className="mt-3 flex items-center gap-2 text-sm font-medium text-ink"><span>{item.initial_state.summary || "Unknown initial state"}</span><ArrowRight size={14}/><span>{item.final_state.summary || "Unknown final state"}</span></div>
          <p className="mt-2 text-ink-muted">Perturbation: {item.perturbation.type || "unknown"} {item.perturbation.target || ""}</p>
          <p className="mt-1 text-ink-muted">Mechanism: {item.mechanism || "Unknown"}</p><p className="mt-1 text-ink-muted">Outcome: {item.outcome}; phenotype: {item.phenotype || "Unknown"}</p>
          {item.evidence_id && item.evidence_id.startsWith("ddr:") && <Link className="mt-2 inline-block text-accent-strong underline" to={`/projects/${projectId}/trust/${item.evidence_id.split(":")[1]}`}>Inspect provenance</Link>}
        </article>)}
      </section>
      {graph.data && graph.data.edges.length > 0 && <section className="panel p-4"><h2 className="text-sm font-semibold text-ink">State transition graph</h2><ul className="mt-2 space-y-1 text-xs text-ink-muted">{graph.data.edges.map((edge) => <li key={edge.transition_id}>{graph.data.nodes.find((n) => n.id === edge.source)?.label} → <strong>{edge.perturbation_type}</strong> → {graph.data.nodes.find((n) => n.id === edge.target)?.label} ({edge.outcome})</li>)}</ul></section>}
    </div>
  </main>;
}
