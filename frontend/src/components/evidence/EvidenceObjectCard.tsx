import type { ConfidenceLevel, EvidenceCharacterization, EvidenceObject } from "@/api/evidenceIntelligence";
import { StatusBadge, type BadgeStatus } from "@/components/common/StatusBadge";
import { useI18n } from "@/lib/i18n";

/**
 * Module 3 (Evidence Intelligence Infrastructure): a compact, reusable
 * rendering of one `EvidenceObject` - claim / host / product / intervention
 * / confidence / applicability / limitations. Meant to be dropped into any
 * page that already lists evidence (Knowledge & Evidence, diagnosis
 * evidence panels, Trust Center) rather than each page inventing its own
 * shape for the same fields.
 */
const CONFIDENCE_BADGE: Record<ConfidenceLevel, BadgeStatus> = {
  High: "approved",
  Medium: "needs_revision",
  Low: "unclear",
  Unknown: "not_started",
};

export function EvidenceObjectCard({ evidence, characterization }: { evidence: EvidenceObject; characterization?: EvidenceCharacterization }) {
  const { t } = useI18n();
  return (
    <li className="rounded-lg border border-border bg-surface p-3 text-xs">
      <div className="flex items-start justify-between gap-2">
        <p className="font-medium text-ink">{evidence.claim || t("evidenceObject.noClaim")}</p>
        <StatusBadge status={CONFIDENCE_BADGE[evidence.confidenceLevel]} label={`${t("evidenceObject.confidence")}: ${evidence.confidenceLevel}`} hint={evidence.confidenceBasis} />
      </div>

      <div className="mt-2 flex flex-wrap items-center gap-x-3 gap-y-1 text-[11px] text-ink-muted">
        <span className="font-mono text-ink-faint">{evidence.evidenceId}</span>
        <span>{evidence.evidenceOrigin}</span>
        <span>·</span>
        <span>{evidence.evidenceType}</span>
        {evidence.evidenceGrading && (
          <>
            <span>·</span>
            <span>{evidence.evidenceGrading}证据</span>
          </>
        )}
      </div>

      <div className="mt-1.5 flex flex-wrap gap-x-3 gap-y-1 text-[11px] text-ink-muted">
        {evidence.host && <span>{t("evidenceObject.host")}: {evidence.host}</span>}
        {evidence.product && <span>{t("evidenceObject.product")}: {evidence.product}</span>}
        {evidence.engineeringIntervention && <span>{t("evidenceObject.intervention")}: {evidence.engineeringIntervention}</span>}
      </div>

      {characterization && (
        <div className="mt-2 grid grid-cols-2 gap-x-3 gap-y-1 border-t border-border pt-2 text-[11px] text-ink-muted sm:grid-cols-4">
          <div><span className="label-caps">{t("evidenceObject.applicability")}</span><div className="text-ink">{characterization.applicability}</div></div>
          <div><span className="label-caps">{t("evidenceObject.uncertainty")}</span><div className="text-ink">{characterization.uncertainty}</div></div>
        </div>
      )}

      {evidence.applicabilityBoundary.length > 0 && (
        <p className="mt-1.5 text-[11px] text-ink-faint">{t("evidenceObject.applicabilityBoundary")}: {evidence.applicabilityBoundary.join("；")}</p>
      )}
      {evidence.limitations.length > 0 && (
        <p className="mt-1 text-[11px] text-ink-faint">{t("evidenceObject.limitations")}: {evidence.limitations.join("；")}</p>
      )}
      <p className="mt-1 text-[11px] text-ink-faint">{t("evidenceObject.source")}: {evidence.source}</p>
    </li>
  );
}
