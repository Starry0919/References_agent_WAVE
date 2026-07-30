import { ArrowRight, ShieldCheck } from "lucide-react";
import type { EvidenceProvenanceItem } from "@/api/evidence";
import { EmptyState } from "@/components/common/EmptyState";
import { useI18n } from "@/lib/i18n";

/**
 * Bottom Evidence Provenance Panel (抽取详情页面.md §"Section 3 - Evidence
 * Provenance Panel"): Claim -> Evidence Source -> Extraction Confidence,
 * the aggregated answer to "每一步证据在哪里？" across the whole record.
 */
export function EvidenceProvenancePanel({ items, onSelectStep }: { items: EvidenceProvenanceItem[]; onSelectStep: (step: number) => void }) {
  const { t } = useI18n();
  return (
    <div className="panel flex flex-col gap-3 p-4">
      <h2 className="flex items-center gap-1.5 text-sm font-semibold text-ink">
        <ShieldCheck size={15} className="text-amber-600" aria-hidden /> {t("paperEvidence.provenance.title")}
      </h2>
      {items.length === 0 ? (
        <EmptyState variant="unavailable" title={t("paperEvidence.provenance.emptyTitle")} />
      ) : (
        <div className="flex flex-col divide-y divide-border">
          {items.map((it, i) => (
            <button
              key={i}
              type="button"
              onClick={() => it.step != null && onSelectStep(it.step)}
              className="grid grid-cols-1 gap-2 py-2.5 text-left text-[11px] first:pt-0 last:pb-0 sm:grid-cols-[1fr_auto_1fr_auto] sm:items-center"
            >
              <div>
                <span className="label-caps">{t("paperEvidence.provenance.claim")}</span>
                <p className="text-ink">{it.claim}</p>
              </div>
              <ArrowRight size={13} className="hidden text-ink-faint sm:block" aria-hidden />
              <div>
                <span className="label-caps">{t("paperEvidence.provenance.source")}</span>
                <p className="text-ink-muted">{it.source || "—"}</p>
              </div>
              <div className="flex items-center gap-1.5 justify-self-start sm:justify-self-end">
                {it.grading && (
                  <span className={`rounded px-1.5 py-0.5 text-[10px] font-medium ${it.grading === "硬" ? "bg-emerald-100 text-emerald-700" : "bg-amber-100 text-amber-700"}`}>
                    {it.grading}证据
                  </span>
                )}
                <span className="text-ink-faint">{it.confidence != null ? `${(it.confidence * 100).toFixed(0)}%` : "—"}</span>
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
