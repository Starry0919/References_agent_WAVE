import { useState } from "react";
import { Link, useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { ArrowLeft, BookOpenCheck, FlaskConical, Microscope, ShieldCheck } from "lucide-react";
import { getEvidenceDocument } from "@/api/evidence";
import { DesignTab, QualityTab, ReasoningTab, TabButton } from "@/pages/paperExtraction/PaperResultTabs";
import { EmptyState } from "@/components/common/EmptyState";
import { useI18n } from "@/lib/i18n";

/**
 * Literature-evidence detail page (harness/api/generation.py::get_evidence_document,
 * real, backed by knowledge/ddr_database/*.json). Reached either by clicking
 * "详情" on a Literature Evidence list item (KnowledgePage's literature tab)
 * or automatically once a single-paper extraction run finishes
 * (PaperExtractionPage). Shows the agent's own parsing reasoning + the
 * paper's evidence-bound experimental design side by side with whatever
 * curated decision-chain content the DDR record also carries.
 */
export function PaperEvidenceDetailPage() {
  const { t } = useI18n();
  const { projectId, sourceId } = useParams<{ projectId: string; sourceId: string }>();
  const [tab, setTab] = useState<"reasoning" | "design" | "quality">("reasoning");

  const detailQuery = useQuery({
    queryKey: ["evidence-document", sourceId, "local_ddr"],
    queryFn: () => getEvidenceDocument(sourceId as string, "local_ddr"),
    enabled: !!sourceId,
  });

  const detail = detailQuery.data;
  const authors = detail && detail.authors.length > 0 ? detail.authors.join(", ") : null;
  const metaBits = detail ? [authors, detail.journalOrRepository, detail.publicationYear != null ? String(detail.publicationYear) : null].filter(Boolean) : [];

  return (
    <div className="flex min-h-0 flex-1 flex-col overflow-y-auto p-4">
      <Link to={`/projects/${projectId}/knowledge?tab=literature`} className="mb-3 flex w-fit items-center gap-1 text-xs text-ink-muted hover:text-ink">
        <ArrowLeft size={13} aria-hidden />
        {t("paperEvidence.backToList")}
      </Link>

      {detailQuery.isLoading && <EmptyState variant="loading" />}
      {detailQuery.isError && <EmptyState variant="failed" detail={String(detailQuery.error)} />}
      {!detailQuery.isLoading && !detail && <EmptyState variant="failed" title={t("paperEvidence.notFound")} />}

      {detail && (
        <div className="flex flex-col gap-4">
          <div className="rounded-xl border border-border bg-surface px-5 py-4 shadow-sm">
            <div className="flex items-start gap-3">
              <div className="mt-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-accent/10 text-accent">
                <Microscope size={19} aria-hidden />
              </div>
              <div className="min-w-0">
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
                {detail.extractionTaskId && (
                  <Link
                    to={`/projects/${projectId}/knowledge?tab=extraction&task=${detail.extractionTaskId}`}
                    className="mt-1.5 inline-block text-[11px] text-accent-strong underline decoration-dotted underline-offset-2"
                  >
                    {t("paperEvidence.fromExtractionTask")}: {detail.extractionTaskId}
                  </Link>
                )}
              </div>
            </div>
          </div>

          {detail.paperExtractionDetail ? (
            <div className="panel flex flex-col gap-3 p-4">
              <h2 className="flex items-center gap-1.5 text-sm font-semibold text-ink">
                <BookOpenCheck size={15} className="text-accent" aria-hidden /> {t("paperEvidence.extractionTitle")}
              </h2>
              <div className="flex gap-1 border-b border-border">
                <TabButton active={tab === "reasoning"} onClick={() => setTab("reasoning")} icon={<BookOpenCheck size={12} />} label={t("page5.result.tabReasoning")} />
                <TabButton
                  active={tab === "design"}
                  onClick={() => setTab("design")}
                  icon={<FlaskConical size={12} />}
                  label={t("page5.result.tabDesign")}
                  badge={detail.paperExtractionDetail.hasDesignContent ? undefined : "!"}
                />
                <TabButton active={tab === "quality"} onClick={() => setTab("quality")} icon={<ShieldCheck size={12} />} label={t("page5.result.tabQuality")} />
              </div>
              {tab === "reasoning" && <ReasoningTab paper={detail.paperExtractionDetail} />}
              {tab === "design" && <DesignTab paper={detail.paperExtractionDetail} />}
              {tab === "quality" && <QualityTab paper={detail.paperExtractionDetail} />}
            </div>
          ) : (
            <div className="panel flex items-start gap-2 p-3 text-[11px] text-ink-muted">
              <EmptyState variant="unavailable" title={t("paperEvidence.noAutoDetailTitle")} detail={t("paperEvidence.noAutoDetailDetail")} />
            </div>
          )}

          {detail.abstractOrSummary && (
            <div className="panel flex flex-col gap-1 p-4 text-xs">
              <h4 className="label-caps mb-1">{t("page3.detail.abstractOrSummary")}</h4>
              <p className="text-ink-muted">{detail.abstractOrSummary}</p>
            </div>
          )}

          <div className="panel flex flex-col gap-2 p-4 text-xs">
            <h4 className="label-caps mb-1">{t("page3.detail.extractedDesignTitle")}</h4>
            {!detail.engineeringDesign ? (
              <EmptyState variant="unavailable" title={t("page3.detail.noExtractedDesignTitle")} detail={t("page3.detail.noExtractedDesignDetail")} />
            ) : (
              <div className="flex flex-col gap-2">
                {detail.engineeringDesign.bottlenecks.length > 0 && (
                  <p><span className="font-medium text-ink-faint">{t("page3.detail.bottlenecks")}: </span>{detail.engineeringDesign.bottlenecks.join("; ")}</p>
                )}
                {detail.engineeringDesign.mechanisticExplanation && (
                  <p><span className="font-medium text-ink-faint">{t("page3.detail.mechanism")}: </span>{detail.engineeringDesign.mechanisticExplanation}</p>
                )}
                {detail.engineeringDesign.hypothesis && (
                  <p><span className="font-medium text-ink-faint">{t("page3.detail.hypothesis")}: </span>{detail.engineeringDesign.hypothesis}</p>
                )}
                {detail.engineeringDesign.expectedEffect && (
                  <p><span className="font-medium text-ink-faint">{t("page3.detail.expectedEffect")}: </span>{detail.engineeringDesign.expectedEffect}</p>
                )}
                {detail.engineeringDesign.actions.length > 0 && (
                  <div>
                    <h5 className="label-caps mb-1">{t("page3.detail.actionsTitle")}</h5>
                    <ul className="flex flex-col gap-2">
                      {detail.engineeringDesign.actions.map((a, i) => (
                        <li key={i} className="rounded border border-border p-2">
                          <p className="font-medium text-ink">{a.modificationType || "—"}</p>
                          <p className="text-ink-muted">{t("page3.detail.target")}: {a.target || "—"}{a.geneOrPathway ? ` (${a.geneOrPathway})` : ""}</p>
                          {a.rationale && <p className="text-ink-muted">{t("page3.detail.rationale")}: {a.rationale}</p>}
                          {a.expectedEffect && <p className="text-ink-muted">{t("page3.detail.expectedEffect")}: {a.expectedEffect}</p>}
                          {a.risk && <p className="text-state-caution">{t("page3.detail.risk")}: {a.risk}</p>}
                          {a.validation.length > 0 && <p className="text-ink-faint">{t("page3.detail.validation")}: {a.validation.join("; ")}</p>}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
