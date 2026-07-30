import { useState } from "react";
import { AlertTriangle, Info, ListTree, Quote, SquareCheck } from "lucide-react";
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

type I18nKey = Parameters<ReturnType<typeof useI18n>["t"]>[0];

const _EXTRACTION_METHOD_KEYS = new Set(["rule", "rule_based", "hybrid", "model_inference", "direct_quote", "not_applicable"]);

/** Small mobile-only caption ("Column N: ...") repeated at the top of every
 * card, so the field's still-legible once the 3-column grid collapses to a
 * single column below `lg` and the shared header row (which only exists
 * once, above the whole grid) scrolls out of view. */
function CardCaption({ icon, label }: { icon: React.ReactNode; label: string }) {
  return (
    <span className="label-caps mb-0.5 flex items-center gap-1 lg:hidden">
      {icon}
      {label}
    </span>
  );
}

/**
 * Column 1 of one CompareRow: skill07's per-field extraction_method/notes
 * (plus `inference.rationale` when the field's status is "inferred") - the
 * closest thing this pipeline logs to "the process language before the
 * final result" for a single field, since the underlying LLM call returns
 * only a final JSON object and this codebase never persists a raw
 * chain-of-thought to replay verbatim.
 */
function AgentReasoningCard({ field, active, onSelect }: { field: DesignField; active: boolean; onSelect: () => void }) {
  const { t } = useI18n();
  const r = field.reasoning;
  const methodLabel = r.extractionMethod
    ? _EXTRACTION_METHOD_KEYS.has(r.extractionMethod)
      ? t(`page5.result.extractionMethod.${r.extractionMethod}` as I18nKey)
      : r.extractionMethod
    : null;
  const hasContent = Boolean(methodLabel || r.notes || r.inferenceRationale);
  return (
    <button
      type="button"
      onClick={onSelect}
      className={`panel flex flex-col gap-1.5 p-2.5 text-left text-[11px] transition ${active ? "border-accent ring-1 ring-accent" : ""}`}
    >
      <CardCaption icon={<ListTree size={11} aria-hidden />} label={t("page5.result.compare.processColumn")} />
      {hasContent ? (
        <div className="flex flex-col gap-1 text-ink-muted">
          {methodLabel && (
            <p>
              <span className="font-medium text-ink-faint">{t("page5.result.compare.extractionMethodLabel")}: </span>
              {methodLabel}
              {field.confidence != null && <span className="text-ink-faint"> · {(field.confidence * 100).toFixed(0)}%</span>}
            </p>
          )}
          {r.notes && <p>{r.notes}</p>}
          {r.inferenceRationale && (
            <p className="text-ink-faint">
              <span className="font-medium">{t("page5.result.compare.inferenceLabel")}{r.inferenceMethod ? ` (${r.inferenceMethod})` : ""}: </span>
              {r.inferenceRationale}
            </p>
          )}
        </div>
      ) : (
        <p className="italic text-ink-faint">{t("page5.result.compare.noProcessNote")}</p>
      )}
    </button>
  );
}

/**
 * Column 2 of one CompareRow: the agent's structured, extracted claim for
 * this field - same value/status a DesignFieldRow shows, minus its inlined
 * evidence quotes (those move to column 3).
 */
function AgentClaimCard({ field, active, onSelect }: { field: DesignField; active: boolean; onSelect: () => void }) {
  const { t } = useI18n();
  const badgeStatus: BadgeStatus = field.status === "reported" ? "available" : field.status === "inferred" ? "under_review" : "unavailable";
  const displayValue = formatFieldValue(field.value);
  return (
    <button
      type="button"
      onClick={onSelect}
      className={`panel flex flex-col gap-1.5 p-2.5 text-left text-[11px] transition ${active ? "border-accent ring-1 ring-accent" : ""}`}
    >
      <CardCaption icon={<SquareCheck size={11} aria-hidden />} label={t("page5.result.compare.agentColumn")} />
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
    </button>
  );
}

/** Column 3 of one CompareRow: the paper's own words backing (or not
 * backing) the paired claim in column 2 - the same EvidenceQuote records
 * DesignFieldRow already carries, just surfaced on their own instead of
 * nested under the claim. */
function PaperQuoteCard({ field, active, onSelect }: { field: DesignField; active: boolean; onSelect: () => void }) {
  const { t } = useI18n();
  return (
    <button
      type="button"
      onClick={onSelect}
      className={`panel flex flex-col gap-1.5 p-2.5 text-left text-[11px] transition ${active ? "border-accent ring-1 ring-accent" : ""}`}
    >
      <CardCaption icon={<Quote size={11} aria-hidden />} label={t("page5.result.compare.paperColumn")} />
      {field.evidence.length > 0 ? (
        <div className="flex flex-col gap-1">
          {field.evidence.map((e) => (
            <EvidenceQuoteCard key={e.evidenceId} evidence={e} />
          ))}
        </div>
      ) : (
        <div className="flex items-start gap-1.5 text-ink-faint">
          <AlertTriangle size={12} className="mt-0.5 shrink-0 text-state-caution" aria-hidden />
          <p className="italic">{t("page5.result.compare.noQuote")}</p>
        </div>
      )}
    </button>
  );
}

/**
 * "第一栏是agent抽取的思路（过程语言），第二栏是agent最终抽取的结论，第
 * 三栏是抽取出来的论文原文" three-column audit view: for each design field
 * skill08 evidence-bound, the agent's per-field process narrative (column
 * 1), its structured final claim (column 2) and the paper's literal quote
 * (column 3) sit in the same row so a reviewer can check all three against
 * each other field by field, instead of the single inline claim+quote card
 * DesignTab renders. Clicking any card in a row highlights the whole row -
 * there is no separate scroll-sync (unlike AgentTracePanel/
 * ExperimentalDesignPanel) since a paper's field list is short enough to
 * stay fully visible without it.
 */
export function CompareTab({ paper }: { paper: PaperExtractionSummary }) {
  const { t } = useI18n();
  const [activeKey, setActiveKey] = useState<string | null>(null);
  if (!paper.hasDesignContent) {
    return <EmptyState variant="incomplete" title={t("page5.result.noDesignContentTitle")} detail={t("page5.result.noDesignContentDetail")} />;
  }
  const reported = paper.designFields.filter((f) => f.status !== "unknown");
  return (
    <div className="flex flex-col gap-3">
      <p className="text-[11px] text-ink-faint">{t("page5.result.compare.hint")}</p>
      <div className="grid grid-cols-1 items-stretch gap-x-3 gap-y-3 lg:grid-cols-[minmax(0,1fr)_minmax(0,1fr)_minmax(0,1fr)]">
        <h4 className="label-caps hidden items-center gap-1 lg:flex">
          <ListTree size={12} aria-hidden />
          {t("page5.result.compare.processColumn")}
        </h4>
        <h4 className="label-caps hidden items-center gap-1 lg:flex">
          <SquareCheck size={12} aria-hidden />
          {t("page5.result.compare.agentColumn")}
        </h4>
        <h4 className="label-caps hidden items-center gap-1 lg:flex">
          <Quote size={12} aria-hidden />
          {t("page5.result.compare.paperColumn")}
        </h4>
        {reported.map((f) => {
          const active = activeKey === f.key;
          const toggle = () => setActiveKey(active ? null : f.key);
          return (
            <div key={f.key} className="contents">
              <AgentReasoningCard field={f} active={active} onSelect={toggle} />
              <AgentClaimCard field={f} active={active} onSelect={toggle} />
              <PaperQuoteCard field={f} active={active} onSelect={toggle} />
            </div>
          );
        })}
      </div>
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
