import { AlertTriangle } from "lucide-react";
import type { ProvenanceGraph, ProvenanceNodeKind } from "@/api/evidenceIntelligence";
import { EmptyState } from "@/components/common/EmptyState";
import { useI18n, type DictKey } from "@/lib/i18n";

/**
 * Module 3 Component 4 - Engineering Provenance Graph:
 *   Engineering Decision -> Engineering Strategy -> Mechanistic Rule ->
 *   Evidence Object -> Experiment -> Paper/Dataset
 *
 * Rendered as a grouped node list (tiers in chain order) + a compact edge
 * list, not a force-directed graph - this graph is small (a handful to a
 * few dozen nodes per anchor) and the existing evidence-provenance UI
 * (`EvidenceGraphModal.tsx`) already covers the within-paper flow-diagram
 * case; this reuses that page's list/card visual language instead of
 * introducing a second graph-rendering library.
 */
const TIER_ORDER: ProvenanceNodeKind[] = ["engineering_decision", "engineering_strategy", "mechanistic_rule", "evidence_object", "experiment", "paper"];

const TIER_LABEL_KEY: Record<ProvenanceNodeKind, DictKey> = {
  engineering_decision: "trust.provenanceGraph.kind.engineering_decision",
  engineering_strategy: "trust.provenanceGraph.kind.engineering_strategy",
  mechanistic_rule: "trust.provenanceGraph.kind.mechanistic_rule",
  evidence_object: "trust.provenanceGraph.kind.evidence_object",
  experiment: "trust.provenanceGraph.kind.experiment",
  paper: "trust.provenanceGraph.kind.paper",
};

export function ProvenanceGraphPanel({ graph }: { graph: ProvenanceGraph }) {
  const { t } = useI18n();
  const nodeById = new Map(graph.nodes.map((n) => [n.id, n]));

  if (graph.nodes.length === 0) {
    return <EmptyState variant="no_result" title={t("trust.provenanceGraph.emptyTitle")} detail={t("trust.provenanceGraph.emptyDetail")} />;
  }

  return (
    <div className="flex flex-col gap-3">
      {TIER_ORDER.filter((kind) => graph.nodes.some((n) => n.kind === kind)).map((kind) => (
        <div key={kind}>
          <span className="label-caps">{t(TIER_LABEL_KEY[kind])}</span>
          <ul className="mt-1 flex flex-col gap-1.5">
            {graph.nodes.filter((n) => n.kind === kind).map((n) => (
              <li key={n.id} className="rounded border border-border bg-surface px-2 py-1.5 text-xs">
                <p className="text-ink">{n.label}</p>
                <p className="mt-0.5 font-mono text-[10px] text-ink-faint">{n.id}</p>
              </li>
            ))}
          </ul>
        </div>
      ))}

      {graph.edges.length > 0 && (
        <div className="border-t border-border pt-2">
          <span className="label-caps">{t("trust.provenanceGraph.edges")}</span>
          <ul className="mt-1 flex flex-col gap-1 text-[11px] text-ink-muted">
            {graph.edges.map((e, i) => (
              <li key={`${e.source}->${e.target}-${i}`}>
                {(nodeById.get(e.source)?.label ?? e.source)} <span className="text-ink-faint">--{e.relation}--&gt;</span> {(nodeById.get(e.target)?.label ?? e.target)}
              </li>
            ))}
          </ul>
        </div>
      )}

      {graph.unresolved.length > 0 && (
        <div className="rounded border border-amber-300 bg-amber-50 p-2">
          <div className="flex items-center gap-1 text-[11px] font-medium text-state-caution">
            <AlertTriangle size={12} aria-hidden /> {t("trust.provenanceGraph.unresolvedTitle")}
          </div>
          <ul className="mt-1 list-disc pl-4 text-[11px] text-ink-muted">
            {graph.unresolved.map((u, i) => (
              <li key={i}>{u}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
