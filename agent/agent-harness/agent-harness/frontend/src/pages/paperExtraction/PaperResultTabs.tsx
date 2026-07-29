import { Info, Quote } from "lucide-react";
import type { DesignField, EvidenceQuote, PaperExtractionSummary, TargetStrain } from "@/api/paperExtraction";
import { EmptyState } from "@/components/common/EmptyState";
import { StatusBadge, type BadgeStatus } from "@/components/common/StatusBadge";
import { useI18n } from "@/lib/i18n";

/**
 * The reasoning/design/quality tab bodies for one paper's extraction
 * result - shared between the in-progress run view (PaperExtractionPage's
 * PaperResultCard, a small card per paper) and the standalone literature-
 * evidence detail page (PaperEvidenceDetailPage, the full page reached via
 * a "详情" button once the paper is saved as evidence) so the same agent-
 * reasoning/experimental-design UI isn't built twice.
 */

export function paperIdentityTitle(paper: PaperExtractionSummary, t: (k: Parameters<ReturnType<typeof useI18n>["t"]>[0]) => string): string {
  if (paper.identity.title) return paper.identity.title;
  return `${t("page5.result.untitledPaper")} (${paper.paperId})`;
}

export function TabButton({ active, onClick, icon, label, badge }: { active: boolean; onClick: () => void; icon: React.ReactNode; label: string; badge?: string }) {
  return (
    <button
      onClick={onClick}
      className={`flex items-center gap-1 border-b-2 px-2.5 py-1.5 text-xs font-medium transition ${
        active ? "border-accent text-accent" : "border-transparent text-ink-muted hover:text-ink"
      }`}
    >
      {icon}
      {label}
      {badge && <span className="ml-0.5 rounded-full bg-amber-100 px-1 text-[9px] font-bold text-state-caution">{badge}</span>}
    </button>
  );
}

function StrainRoleBadge({ role }: { role: string | null }) {
  const { t } = useI18n();
  if (!role) return null;
  const key = `page5.result.strainRole.${role}` as Parameters<ReturnType<typeof useI18n>["t"]>[0];
  return <span className="rounded bg-surface-sunken px-1.5 py-0.5 text-[10px] font-medium text-ink-muted">{t(key)}</span>;
}

function TargetStrainCard({ strain }: { strain: TargetStrain }) {
  const { t } = useI18n();
  return (
    <div className="panel flex flex-col gap-1 p-2.5 text-[11px]">
      <div className="flex flex-wrap items-center gap-1.5">
        <span className="font-medium text-ink">{strain.paperStrainNormalized ?? strain.paperStrainRaw ?? "?"}</span>
        <StrainRoleBadge role={strain.role} />
        {strain.confidence != null && <span className="text-ink-faint">{t("page5.result.confidence")}: {(strain.confidence * 100).toFixed(0)}%</span>}
      </div>
      {strain.paperStrainRaw && strain.paperStrainRaw !== strain.paperStrainNormalized && (
        <p className="text-ink-faint">{t("page5.result.originalLabel")}: {strain.paperStrainRaw}</p>
      )}
      {strain.lineageOrEngineeringContext && <p className="text-ink-muted">{strain.lineageOrEngineeringContext}</p>}
      {strain.reasoning && (
        <p className="text-ink-faint">
          <span className="font-medium">{t("page5.why")}: </span>
          {strain.reasoning}
        </p>
      )}
    </div>
  );
}

export function ReasoningTab({ paper }: { paper: PaperExtractionSummary }) {
  const { t } = useI18n();
  return (
    <div className="flex flex-col gap-3">
      {paper.articleType && (
        <div>
          <h4 className="label-caps mb-1">{t("page5.result.articleTypeTitle")}</h4>
          <div className="panel flex flex-wrap items-center gap-2 p-2.5 text-[11px]">
            <span className="font-medium text-ink">{t(`page5.result.articleType.${paper.articleType.articleType ?? "other"}` as Parameters<ReturnType<typeof useI18n>["t"]>[0])}</span>
            {paper.articleType.isPrimaryExperimentalStudy != null && (
              <StatusBadge
                status={paper.articleType.isPrimaryExperimentalStudy ? "available" : "unclear"}
                label={paper.articleType.isPrimaryExperimentalStudy ? t("page5.result.isPrimaryStudy") : t("page5.result.notPrimaryStudy")}
              />
            )}
            {paper.articleType.confidence != null && (
              <span className="text-ink-faint">{t("page5.result.confidence")}: {(paper.articleType.confidence * 100).toFixed(0)}%</span>
            )}
          </div>
        </div>
      )}
      {paper.targetStrains.length > 0 && (
        <div>
          <h4 className="label-caps mb-1">
            {t("page5.result.strainsTitle")} ({paper.targetStrains.length})
          </h4>
          <div className="grid grid-cols-1 gap-1.5 sm:grid-cols-2">
            {paper.targetStrains.map((s, i) => (
              <TargetStrainCard key={i} strain={s} />
            ))}
          </div>
        </div>
      )}
      {!paper.articleType && paper.targetStrains.length === 0 && <EmptyState variant="unavailable" title={t("page5.result.noReasoningYet")} />}
    </div>
  );
}

function EvidenceQuoteCard({ evidence }: { evidence: EvidenceQuote }) {
  const { t } = useI18n();
  const loc = [evidence.sectionPath.join(" / "), evidence.page != null ? `p.${evidence.page}` : null, evidence.figureId, evidence.tableId].filter(Boolean).join(" · ");
  return (
    <div className="flex items-start gap-1.5 rounded border border-border bg-surface-sunken px-2 py-1.5 text-[10px] text-ink-muted">
      <Quote size={11} className="mt-0.5 shrink-0 text-ink-faint" aria-hidden />
      <div>
        <p>&ldquo;{evidence.quote}&rdquo;</p>
        {loc && <p className="mt-0.5 text-ink-faint">{loc}</p>}
      </div>
      <span className="ml-auto shrink-0 text-ink-faint">{t("page5.evidenceTitle")}</span>
    </div>
  );
}

function DesignFieldRow({ field }: { field: DesignField }) {
  const { t } = useI18n();
  const badgeStatus: BadgeStatus = field.status === "reported" ? "available" : field.status === "inferred" ? "under_review" : "unavailable";
  const displayValue = formatFieldValue(field.value);
  return (
    <div className="panel flex flex-col gap-1.5 p-2.5 text-[11px]">
      <div className="flex flex-wrap items-center justify-between gap-1.5">
        <span className="font-medium text-ink">{field.label}</span>
        <div className="flex items-center gap-1.5">
          {!field.verified && field.status !== "unknown" && (
            <span className="text-[10px] text-ink-faint" title={t("page5.result.unverifiedHint")}>
              {t("page5.result.unverified")}
            </span>
          )}
          <StatusBadge status={badgeStatus} label={field.statusLabel} />
        </div>
      </div>
      {field.status !== "unknown" ? (
        <p className="text-ink-muted">{displayValue}</p>
      ) : (
        <p className="italic text-ink-faint">{t("page5.result.fieldUnknown")}</p>
      )}
      {field.evidence.length > 0 && (
        <div className="flex flex-col gap-1">
          {field.evidence.map((e) => (
            <EvidenceQuoteCard key={e.evidenceId} evidence={e} />
          ))}
        </div>
      )}
    </div>
  );
}

function formatFieldValue(value: unknown): string {
  if (value == null) return "";
  if (typeof value === "string") return value;
  if (Array.isArray(value)) return value.map(formatFieldValue).join("; ");
  if (typeof value === "object") return JSON.stringify(value);
  return String(value);
}

export function DesignTab({ paper }: { paper: PaperExtractionSummary }) {
  const { t } = useI18n();
  if (!paper.hasDesignContent) {
    return (
      <EmptyState
        variant="incomplete"
        title={t("page5.result.noDesignContentTitle")}
        detail={t("page5.result.noDesignContentDetail")}
      />
    );
  }
  const reported = paper.designFields.filter((f) => f.status !== "unknown");
  const unknown = paper.designFields.filter((f) => f.status === "unknown");
  return (
    <div className="flex flex-col gap-2">
      {reported.map((f) => (
        <DesignFieldRow key={f.key} field={f} />
      ))}
      {unknown.length > 0 && (
        <details className="text-[11px] text-ink-faint">
          <summary className="cursor-pointer select-none">
            {unknown.length} {t("page5.result.unknownFieldsCollapsed")}
          </summary>
          <div className="mt-1.5 flex flex-col gap-1.5">
            {unknown.map((f) => (
              <DesignFieldRow key={f.key} field={f} />
            ))}
          </div>
        </details>
      )}
    </div>
  );
}

function ScoreMeter({ label, value }: { label: string; value: number | null }) {
  const pct = value != null ? Math.round(value * 100) : null;
  return (
    <div className="flex flex-col gap-1">
      <div className="flex items-center justify-between text-[10px] text-ink-faint">
        <span>{label}</span>
        <span>{pct != null ? `${pct}%` : "—"}</span>
      </div>
      <div className="h-1.5 overflow-hidden rounded-full bg-surface-sunken">
        <div
          className={`h-full rounded-full ${pct == null ? "" : pct >= 70 ? "bg-state-success" : pct >= 40 ? "bg-state-caution" : "bg-state-risk"}`}
          style={{ width: `${pct ?? 0}%` }}
        />
      </div>
    </div>
  );
}

export function QualityTab({ paper }: { paper: PaperExtractionSummary }) {
  const { t } = useI18n();
  const q = paper.quality;
  return (
    <div className="flex flex-col gap-3">
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        <ScoreMeter label={t("page5.result.completeness")} value={q.completeness} />
        <ScoreMeter label={t("page5.result.evidenceLevel")} value={q.evidenceLevel} />
        <ScoreMeter label={t("page5.result.reproducibility")} value={q.reproducibility} />
        <ScoreMeter label={t("page5.result.extractionConfidence")} value={q.extractionConfidence} />
      </div>
      {q.recommendation && (
        <div className="panel flex items-start gap-2 p-2.5 text-[11px] text-ink-muted">
          <Info size={13} className="mt-0.5 shrink-0 text-ink-faint" aria-hidden />
          <p>{q.recommendation}</p>
        </div>
      )}
      {q.missingInformation.length > 0 && (
        <div>
          <h4 className="label-caps mb-1">{t("page5.result.missingInfoTitle")}</h4>
          <ul className="flex flex-wrap gap-1">
            {q.missingInformation.map((m, i) => (
              <li key={i} className="rounded bg-surface-sunken px-1.5 py-0.5 text-[10px] text-ink-faint">
                {typeof m === "string" ? m : JSON.stringify(m)}
              </li>
            ))}
          </ul>
        </div>
      )}
      {paper.governanceNote && (
        <p className="text-[10px] italic text-ink-faint">{paper.governanceNote}</p>
      )}
    </div>
  );
}
