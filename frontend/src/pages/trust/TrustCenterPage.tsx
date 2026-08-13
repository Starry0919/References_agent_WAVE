import { useQueries, useQuery } from "@tanstack/react-query";
import { ArrowLeft, BookOpen, ShieldCheck } from "lucide-react";
import { Link, useParams } from "react-router-dom";
import { getDdrProvenance } from "@/api/rules";
import { getEngineeringProvenanceGraph, getEvidenceObject } from "@/api/evidenceIntelligence";
import { EmptyState } from "@/components/common/EmptyState";
import { StatusBadge, type BadgeStatus } from "@/components/common/StatusBadge";
import { EvidenceObjectCard } from "@/components/evidence/EvidenceObjectCard";
import { ProvenanceGraphPanel } from "@/components/evidence/ProvenanceGraphPanel";
import { useI18n } from "@/lib/i18n";

const CONFIDENCE_BADGE: Record<"high" | "medium" | "low", BadgeStatus> = { high: "approved", medium: "needs_revision", low: "unclear" };

/**
 * Trust & Provenance Center (老师 §Phase5 Round 2): the minimal closure for
 * an empty `src/pages/trust` directory - given a DDR id (reachable from the
 * Applicability Report and Knowledge Claim cards), shows the full
 * non-fabricated chain: design action(s) -> rule(s) distilled from it ->
 * the DDR's own paper citation -> evidence grade. Reuses
 * `/api/paper-extraction/ddr/{id}/provenance` (harness/api/
 * paper_extraction.py::get_ddr_provenance) rather than re-deriving the
 * chain client-side.
 */
export function TrustCenterPage() {
  const { projectId, ddrId } = useParams<{ projectId: string; ddrId: string }>();
  const { t } = useI18n();

  const query = useQuery({
    queryKey: ["ddr-provenance", ddrId],
    queryFn: () => getDdrProvenance(ddrId as string),
    enabled: !!ddrId,
  });

  // Module 3 (Evidence Intelligence Infrastructure): the same DDR, but
  // walked through harness/evidence_intelligence's Engineering Provenance
  // Graph builder instead of the flatter design-action/rule summary above -
  // adds the Evidence Object / Experiment tiers this page didn't show
  // before, without replacing the existing "why do we believe this" summary.
  const graphQuery = useQuery({
    queryKey: ["engineering-provenance-graph", "ddr", ddrId],
    queryFn: () => getEngineeringProvenanceGraph("ddr", ddrId as string),
    enabled: !!ddrId,
  });
  const evidenceIds = (graphQuery.data?.nodes ?? [])
    .filter((node) => node.kind === "evidence_object" && typeof node.ref.evidence_id === "string")
    .map((node) => node.ref.evidence_id as string);
  const evidenceQueries = useQueries({
    queries: evidenceIds.map((evidenceId) => ({
      queryKey: ["evidence-object", evidenceId],
      queryFn: () => getEvidenceObject(evidenceId),
    })),
  });

  return (
    <main className="min-h-full flex-1 overflow-y-auto bg-surface-sunken p-5">
      <div className="mx-auto flex max-w-4xl flex-col gap-4">
        <div>
          <Link to={`/projects/${projectId}/knowledge`} className="flex w-fit items-center gap-1 text-xs font-medium text-ink-muted hover:text-accent-strong">
            <ArrowLeft size={13} aria-hidden /> {t("trust.backToKnowledge")}
          </Link>
          <div className="mt-2 flex items-center gap-2">
            <ShieldCheck size={20} className="text-accent-strong" aria-hidden />
            <h1 className="text-xl font-semibold text-ink">{t("trust.title")}</h1>
          </div>
          <p className="mt-1 max-w-2xl text-sm text-ink-muted">{t("trust.subtitle")}</p>
        </div>

        {query.isLoading && <EmptyState variant="loading" />}
        {!query.isLoading && !query.data && (
          <EmptyState variant="failed" title={t("trust.notFoundTitle")} detail={t("trust.notFoundDetail")} />
        )}

        {query.data && (
          <>
            <section className="panel flex flex-col gap-3 p-4">
              <div className="flex flex-wrap items-start justify-between gap-2">
                <div>
                  <span className="font-mono text-[11px] text-ink-faint">{query.data.ddrId}</span>
                  <h2 className="mt-1 flex items-center gap-1.5 text-sm font-semibold text-ink">
                    <BookOpen size={14} className="text-accent" aria-hidden /> {query.data.paper.title ?? t("page3.noTitle")}
                  </h2>
                  <p className="mt-1 text-xs text-ink-muted">
                    {query.data.paper.authors.join(", ") || t("page3.authorsNotReported")} · {query.data.paper.publicationYear ?? t("page3.noDate")} · {query.data.paper.journalOrRepository ?? t("page3.metadataOnly")}
                  </p>
                  {query.data.paper.doiOrAccession && <p className="mt-0.5 font-mono text-[11px] text-ink-faint">{query.data.paper.doiOrAccession}</p>}
                </div>
                <StatusBadge status={CONFIDENCE_BADGE[query.data.confidence]} label={`${t("trust.confidence")}: ${query.data.confidence}`} />
              </div>

              <div className="flex flex-wrap gap-4 border-t border-border pt-3 text-xs">
                {query.data.designActions.length > 0 && (
                  <div>
                    <span className="label-caps">{t("trust.designActions")}</span>
                    <div className="mt-1 flex flex-wrap gap-1.5">
                      {query.data.designActions.map((a) => (
                        <span key={a} className="rounded border border-border bg-surface px-1.5 py-0.5 font-mono text-[10px] text-ink-muted">{a}</span>
                      ))}
                    </div>
                  </div>
                )}
                {query.data.evidenceGrades.length > 0 && (
                  <div>
                    <span className="label-caps">{t("trust.evidenceGrades")}</span>
                    <div className="mt-1 flex flex-wrap gap-1.5">
                      {query.data.evidenceGrades.map((g) => (
                        <span key={g} className="rounded border border-border bg-surface px-1.5 py-0.5 text-[10px] text-ink-muted">{g}</span>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              <Link to={`/projects/${projectId}/evidence/${query.data.ddrId}`} className="w-fit text-[11px] font-medium text-accent-strong underline decoration-dotted underline-offset-2">
                {t("common.viewDetail")}
              </Link>
            </section>

            <section className="panel flex flex-col gap-3 p-4">
              <h3 className="text-sm font-semibold text-ink">{t("trust.rulesTitle")}</h3>
              {query.data.rules.length === 0 ? (
                <EmptyState variant="no_result" title={t("trust.noRulesTitle")} detail={t("trust.noRulesDetail")} />
              ) : (
                <ul className="flex flex-col gap-2">
                  {query.data.rules.map((rule) => (
                    <li key={rule.claimId} className="rounded-lg border border-border bg-surface p-3 text-xs">
                      <div className="flex items-start justify-between gap-2">
                        <p className="font-medium text-ink">{rule.statement}</p>
                        <StatusBadge status={CONFIDENCE_BADGE[rule.confidence]} label={rule.confidence} />
                      </div>
                      <div className="mt-2 flex flex-wrap items-center gap-x-3 gap-y-1 text-[11px] text-ink-muted">
                        <span className="font-mono text-ink-faint">{rule.claimId}</span>
                        {rule.evidenceGrading && <span>{rule.evidenceGrading}证据</span>}
                        <span>{t("page3.claimEvidenceCount")}: {rule.evidenceCount}</span>
                      </div>
                      {rule.evidenceDdrIds.length > 1 && (
                        <div className="mt-1.5 flex flex-wrap gap-1.5">
                          {rule.evidenceDdrIds.map((id) => (
                            <Link
                              key={id}
                              to={`/projects/${projectId}/trust/${id}`}
                              className="rounded border border-border bg-surface-sunken px-1.5 py-0.5 font-mono text-[10px] text-accent-strong underline decoration-dotted underline-offset-2"
                            >
                              {id}
                            </Link>
                          ))}
                        </div>
                      )}
                      <p className="mt-1.5 text-[11px] text-ink-faint">{t("page3.claimBoundary")}: {rule.boundary}</p>
                    </li>
                  ))}
                </ul>
              )}
            </section>

            <section className="panel flex flex-col gap-3 p-4">
              <div>
                <h3 className="text-sm font-semibold text-ink">{t("trust.provenanceGraph.title")}</h3>
                <p className="mt-0.5 text-[11px] text-ink-muted">{t("trust.provenanceGraph.subtitle")}</p>
              </div>
              {graphQuery.isLoading && <EmptyState variant="loading" />}
              {!graphQuery.isLoading && graphQuery.data && <ProvenanceGraphPanel graph={graphQuery.data} />}
              {!graphQuery.isLoading && !graphQuery.data && (
                <EmptyState variant="no_result" title={t("trust.provenanceGraph.emptyTitle")} detail={t("trust.provenanceGraph.emptyDetail")} />
              )}
            </section>

            {evidenceIds.length > 0 && (
              <section className="panel flex flex-col gap-3 p-4">
                <div>
                  <h3 className="text-sm font-semibold text-ink">Evidence inspection and comparison</h3>
                  <p className="mt-0.5 text-[11px] text-ink-muted">Compare source, origin, applicability boundaries, limitations, and categorical confidence without creating a separate approval decision.</p>
                </div>
                {evidenceQueries.some((item) => item.isLoading) && <EmptyState variant="loading" />}
                <ul className="grid gap-2 md:grid-cols-2">
                  {evidenceQueries.map((item) => item.data).filter((item) => item !== null && item !== undefined).map((item) => (
                    <EvidenceObjectCard key={item.evidence.evidenceId} evidence={item.evidence} characterization={item.characterization} />
                  ))}
                </ul>
              </section>
            )}
          </>
        )}
      </div>
    </main>
  );
}
