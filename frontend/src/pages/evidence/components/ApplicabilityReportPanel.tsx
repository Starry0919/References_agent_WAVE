import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Compass, RefreshCw, ShieldCheck } from "lucide-react";
import { Link } from "react-router-dom";
import { assessDdrApplicability, listEvidenceMatchReports } from "@/api/evidence";
import { EmptyState } from "@/components/common/EmptyState";
import { StatusBadge, type BadgeStatus } from "@/components/common/StatusBadge";
import { useI18n } from "@/lib/i18n";

function matchToBadge(status: string): BadgeStatus {
  if (status === "match" || status === "direct_match" || status === "close_match") return "approved";
  if (status === "mismatch" || status === "cross_strain" || status === "cross_species" || status === "condition_mismatch") return "needs_revision";
  return "unclear";
}

/**
 * "适用范围 / 情境匹配报告" (老师 §Phase3): a historical DDR's
 * transferability to the *current* project's context - host/product
 * overlap plus an explicit list of what structural metadata the DDR
 * schema doesn't yet carry (so a low-confidence result reads as "we don't
 * have enough data" rather than a silent blank panel). Computed on demand
 * (project context can change) and persisted via the same
 * `EvidenceMatchReport` table/engine wet-lab evidence matching already
 * uses (harness/evidence_retrieval/service.py::assess_ddr_applicability).
 */
export function ApplicabilityReportPanel({ ddrId, projectId }: { ddrId: string; projectId: string | undefined }) {
  const { t } = useI18n();
  const qc = useQueryClient();

  const reportsQuery = useQuery({
    queryKey: ["evidence-match-reports", ddrId],
    queryFn: () => listEvidenceMatchReports(ddrId),
    enabled: !!ddrId,
  });

  const assessMutation = useMutation({
    mutationFn: () => assessDdrApplicability(ddrId, projectId as string),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["evidence-match-reports", ddrId] }),
  });

  const latest = assessMutation.data;

  return (
    <div className="panel flex flex-col gap-3 p-4">
      <div className="flex items-center justify-between">
        <h2 className="flex items-center gap-1.5 text-sm font-semibold text-ink">
          <Compass size={15} className="text-accent" aria-hidden /> {t("paperEvidence.applicability.title")}
        </h2>
        <div className="flex items-center gap-2">
          {projectId && (
            <Link
              to={`/projects/${projectId}/trust/${ddrId}`}
              className="flex items-center gap-1 rounded border border-border bg-surface px-2 py-1 text-[11px] font-medium text-accent-strong hover:bg-surface-sunken"
            >
              <ShieldCheck size={11} aria-hidden />
              {t("paperEvidence.applicability.viewProvenance")}
            </Link>
          )}
          <button
            type="button"
            disabled={!projectId || assessMutation.isPending}
            onClick={() => assessMutation.mutate()}
            className="flex items-center gap-1 rounded border border-border bg-surface px-2 py-1 text-[11px] font-medium text-ink-muted hover:bg-surface-sunken disabled:opacity-40"
          >
            <RefreshCw size={11} className={assessMutation.isPending ? "animate-spin" : ""} aria-hidden />
            {assessMutation.isPending ? t("paperEvidence.applicability.assessing") : t("paperEvidence.applicability.assessButton")}
          </button>
        </div>
      </div>

      {!projectId && <p className="text-[11px] text-ink-faint">{t("paperEvidence.applicability.noProjectDetail")}</p>}

      {latest && (
        <div className="flex flex-col gap-2 rounded-lg border border-accent/30 bg-accent-soft/40 p-3 text-[11px]">
          <div className="flex flex-wrap items-center gap-2">
            <StatusBadge status={matchToBadge(latest.overallMatchStatus)} label={latest.overallMatchStatus} />
            <span className="text-ink-muted">{t("paperEvidence.applicability.confidence")}: {(latest.confidence * 100).toFixed(0)}%</span>
          </div>
          <div className="flex flex-wrap gap-x-4 gap-y-1">
            <span>{t("paperEvidence.applicability.organismMatch")}: <strong className="font-medium text-ink">{latest.organismMatch}</strong></span>
            <span>{t("paperEvidence.applicability.productMatch")}: <strong className="font-medium text-ink">{latest.productMatch}</strong></span>
          </div>
          {latest.matchingFactors.length > 0 && (
            <div>
              <span className="label-caps">{t("paperEvidence.applicability.matchingFactors")}</span>
              <ul className="list-disc pl-4 text-ink-muted">
                {latest.matchingFactors.map((f, i) => <li key={i}>{f}</li>)}
              </ul>
            </div>
          )}
          {latest.designActions.length > 0 && (
            <div className="flex flex-wrap items-center gap-1.5">
              <span className="label-caps">{t("paperEvidence.applicability.designActions")}</span>
              {latest.designActions.map((a) => (
                <span key={a} className="rounded border border-border bg-surface px-1.5 py-0.5 font-mono text-[10px] text-ink-muted">{a}</span>
              ))}
            </div>
          )}
          {latest.ruleIds.length > 0 && (
            <div className="flex flex-wrap items-center gap-1.5">
              <span className="label-caps">{t("paperEvidence.applicability.transferableRules")}</span>
              {latest.ruleIds.map((r) => (
                <span key={r} className="rounded border border-border bg-surface px-1.5 py-0.5 font-mono text-[10px] text-accent-strong">{r}</span>
              ))}
            </div>
          )}
          {(latest.transferRisks.length > 0 || latest.downgradeReasons.length > 0) && (
            <div>
              <span className="label-caps">{t("paperEvidence.applicability.limitations")}</span>
              <ul className="list-disc pl-4 text-state-caution">
                {[...latest.downgradeReasons, ...latest.transferRisks].map((f, i) => <li key={i}>{f}</li>)}
              </ul>
            </div>
          )}
          {latest.missingDataForFullReport.length > 0 && (
            <p className="text-ink-faint">
              {t("paperEvidence.applicability.missingDataPrefix")} {latest.missingDataForFullReport.join(", ")}
            </p>
          )}
        </div>
      )}

      {reportsQuery.isLoading && <EmptyState variant="loading" />}
      {reportsQuery.data && reportsQuery.data.length === 0 && !latest && (
        <EmptyState variant="first_use" title={t("paperEvidence.applicability.emptyTitle")} detail={t("paperEvidence.applicability.emptyDetail")} />
      )}
      {reportsQuery.data && reportsQuery.data.length > 0 && (
        <div className="flex flex-col gap-1.5 border-t border-border pt-2">
          <span className="label-caps">{t("paperEvidence.applicability.history")}</span>
          {reportsQuery.data.map((r) => (
            <div key={r.matchReportId} className="flex flex-wrap items-center gap-2 text-[11px] text-ink-muted">
              <StatusBadge status={matchToBadge(r.overallMatchStatus)} label={r.overallMatchStatus} />
              <span>{t("paperEvidence.applicability.organismMatch")}: {r.organismMatch}</span>
              <span className="text-ink-faint">{new Date(r.createdAt * 1000).toLocaleString()}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
