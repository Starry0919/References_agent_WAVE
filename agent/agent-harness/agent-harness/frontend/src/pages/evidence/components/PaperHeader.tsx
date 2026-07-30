import { Link } from "react-router-dom";
import { Download, ExternalLink, Microscope, Workflow } from "lucide-react";
import type { EvidenceDocumentDetail } from "@/api/evidence";
import { StatusBadge } from "@/components/common/StatusBadge";
import { useI18n } from "@/lib/i18n";

const CONFIDENCE_LABEL_KEY = {
  high: "paperEvidence.header.confidenceHigh",
  medium: "paperEvidence.header.confidenceMedium",
  low: "paperEvidence.header.confidenceLow",
} as const;

/**
 * Paper Header (抽取详情页面.md §"Section 1 - Paper Header"): identity +
 * extraction status/confidence + the four header actions. "View Evidence
 * Graph" and "Download Extraction JSON" only render when the record
 * actually has the underlying data (never a dead button).
 */
export function PaperHeader({
  detail,
  projectId,
  onDownloadJson,
  onViewGraph,
}: {
  detail: EvidenceDocumentDetail;
  projectId: string | undefined;
  onDownloadJson: () => void;
  onViewGraph: () => void;
}) {
  const { t } = useI18n();
  const authors = detail.authors.length > 0 ? detail.authors.join(", ") : null;
  const metaBits = [authors, detail.journalOrRepository, detail.publicationYear != null ? String(detail.publicationYear) : null].filter(Boolean);

  return (
    <div className="rounded-xl border border-border bg-surface px-5 py-4 shadow-sm">
      <div className="flex items-start gap-3">
        <div className="mt-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-accent/10 text-accent">
          <Microscope size={19} aria-hidden />
        </div>
        <div className="min-w-0 flex-1">
          <h1 className="text-lg font-semibold leading-6 text-ink">{detail.title || t("page3.noTitle")}</h1>
          <div className="mt-1 flex flex-wrap items-center gap-x-2 gap-y-0.5 text-xs text-ink-muted">
            {metaBits.length > 0 && <span>{metaBits.join(" · ")}</span>}
            {detail.doiOrAccession && (
              <a href={`https://doi.org/${detail.doiOrAccession}`} target="_blank" rel="noreferrer" className="font-mono text-accent-strong underline decoration-dotted underline-offset-2">
                DOI: {detail.doiOrAccession}
              </a>
            )}
            <span className="font-mono text-ink-faint">{detail.sourceId}</span>
          </div>
          <div className="mt-1.5 flex flex-wrap items-center gap-1.5">
            <StatusBadge status={detail.status === "completed" ? "completed" : "not_started"} label={detail.status === "completed" ? t("paperEvidence.header.statusCompleted") : t("paperEvidence.header.statusPending")} />
            {detail.evidenceConfidence && (
              <span className="rounded border border-border px-1.5 py-0.5 text-[11px] font-medium text-ink-muted">
                {t("paperEvidence.header.confidenceLabel")}: {t(CONFIDENCE_LABEL_KEY[detail.evidenceConfidence])}
              </span>
            )}
            {detail.extractionTaskId && (
              <Link
                to={`/projects/${projectId}/knowledge?tab=extraction&task=${detail.extractionTaskId}`}
                className="text-[11px] text-accent-strong underline decoration-dotted underline-offset-2"
              >
                {t("paperEvidence.fromExtractionTask")}: {detail.extractionTaskId}
              </Link>
            )}
          </div>
        </div>
      </div>

      <div className="mt-3 flex flex-wrap gap-1.5 border-t border-border pt-3">
        {detail.url && (
          <a
            href={detail.url}
            target="_blank"
            rel="noreferrer"
            className="flex items-center gap-1 rounded border border-border px-2 py-1 text-[11px] font-medium text-ink-muted hover:border-accent hover:text-accent"
          >
            <ExternalLink size={12} aria-hidden /> {t("paperEvidence.header.viewOriginal")}
          </a>
        )}
        {detail.rawRecord && (
          <button
            type="button"
            onClick={onDownloadJson}
            className="flex items-center gap-1 rounded border border-border px-2 py-1 text-[11px] font-medium text-ink-muted hover:border-accent hover:text-accent"
          >
            <Download size={12} aria-hidden /> {t("paperEvidence.header.downloadJson")}
          </button>
        )}
        {detail.evidenceGraph.nodes.length > 0 && (
          <button
            type="button"
            onClick={onViewGraph}
            className="flex items-center gap-1 rounded border border-border px-2 py-1 text-[11px] font-medium text-ink-muted hover:border-accent hover:text-accent"
          >
            <Workflow size={12} aria-hidden /> {t("paperEvidence.header.viewGraph")}
          </button>
        )}
      </div>
    </div>
  );
}
