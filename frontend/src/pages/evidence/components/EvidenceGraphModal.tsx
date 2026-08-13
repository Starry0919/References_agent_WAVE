import { X } from "lucide-react";
import type { EvidenceGraph } from "@/api/evidence";
import { useI18n } from "@/lib/i18n";

/**
 * "View Evidence Graph" header action (抽取详情页面.md's header Actions
 * row). Renders the backend's minimal step-sequence + supporting-evidence
 * graph (harness/paper_extraction/reasoning_view.py::build_evidence_graph)
 * as a vertical flow diagram - not a general graph layout engine, just
 * enough structure to show how each design step's evidence connects.
 */
export function EvidenceGraphModal({ graph, onClose }: { graph: EvidenceGraph; onClose: () => void }) {
  const { t } = useI18n();
  const stepNodes = graph.nodes.filter((n) => n.type === "step");
  const evidenceByStep = new Map<string, string[]>();
  for (const e of graph.edges) {
    if (e.type !== "supports") continue;
    const evNode = graph.nodes.find((n) => n.id === e.source);
    if (!evNode) continue;
    const list = evidenceByStep.get(e.target) ?? [];
    list.push(evNode.label);
    evidenceByStep.set(e.target, list);
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-ink/40 p-4" onClick={onClose}>
      <div
        role="dialog"
        aria-modal="true"
        aria-label={t("paperEvidence.graph.title")}
        className="max-h-[85vh] w-full max-w-2xl overflow-y-auto rounded-xl border border-border bg-surface p-5 shadow-overlay"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-semibold text-ink">{t("paperEvidence.graph.title")}</h2>
          <button type="button" onClick={onClose} className="rounded p-1 text-ink-faint hover:bg-surface-sunken hover:text-ink" aria-label={t("paperEvidence.graph.close")}>
            <X size={16} aria-hidden />
          </button>
        </div>
        <p className="mt-1 text-[11px] text-ink-faint">{t("paperEvidence.graph.subtitle")}</p>

        <div className="mt-4 flex flex-col">
          {stepNodes.map((n, i) => (
            <div key={n.id} className="flex flex-col">
              <div className="flex items-center gap-2">
                <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-emerald-100 text-[11px] font-semibold text-emerald-700">{i + 1}</div>
                <div className="rounded border border-emerald-200 bg-emerald-50/60 px-2.5 py-1.5 text-[12px] font-medium text-ink">{n.label}</div>
              </div>
              {(evidenceByStep.get(n.id) ?? []).length > 0 && (
                <div className="ml-9 mt-1 flex flex-wrap gap-1.5 border-l-2 border-dashed border-border py-1 pl-3">
                  {(evidenceByStep.get(n.id) ?? []).map((ev, j) => (
                    <span key={j} className="rounded bg-amber-50 px-1.5 py-0.5 text-[10px] text-amber-800">
                      {ev}
                    </span>
                  ))}
                </div>
              )}
              {i < stepNodes.length - 1 && <div className="ml-3.5 h-4 w-px bg-border" />}
            </div>
          ))}
          {stepNodes.length === 0 && <p className="text-[11px] text-ink-faint">{t("paperEvidence.graph.empty")}</p>}
        </div>
      </div>
    </div>
  );
}
