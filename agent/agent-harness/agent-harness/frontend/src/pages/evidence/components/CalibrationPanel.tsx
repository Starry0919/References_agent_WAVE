import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { AlertTriangle, CheckCircle2, UserCheck } from "lucide-react";
import {
  getExtractionConflicts,
  submitExtractionAttempt,
  type DecisionChainStepDraft,
  type ExtractionConflict,
} from "@/api/evidence";
import { useI18n, type DictKey } from "@/lib/i18n";

const DESIGN_ACTIONS = ["M0", "M1", "M2", "M3", "M4", "M5", "M6", "M7", "M8", "M9", "M11"];
const EVIDENCE_GRADINGS = ["硬", "软"];
const REASON_NATURES = ["机理推断", "文献类比", "现成可得", "筛选得来", "事后合理化存疑"];

const inputCls = "w-full rounded border border-border bg-surface px-2 py-1 text-[11px] outline-none transition focus:border-accent focus:ring-2 focus:ring-accent/10";
const labelCls = "label-caps";

/** The only 4 fields `harness/paper_extraction/calibration.py::
 * detect_conflicts` (`_COMPARED_FIELDS`) actually compares between two
 * annotators - every other decision_chain field (target/trigger/evidence/
 * implementation/result/alternatives) is free-text description that
 * naturally varies in wording without being a real disagreement, and was
 * never part of conflict detection in the first place. The original
 * full-form UI asked a second annotator to retype all ~17 fields per step
 * regardless; this only asks about the 4 that can ever produce a flagged
 * conflict, defaulting every field to "agree with the first annotator" -
 * she only edits a field when she actively disagrees with it. */
const COMPARED_FIELDS = ["design_action", "evidence_grading", "reason_nature", "rule"] as const;
type ComparedField = (typeof COMPARED_FIELDS)[number];

const FIELD_LABEL_KEY: Record<ComparedField, DictKey> = {
  design_action: "paperEvidence.calibration.field.designAction",
  evidence_grading: "paperEvidence.calibration.field.evidenceGrading",
  reason_nature: "paperEvidence.calibration.field.reasonNature",
  rule: "paperEvidence.calibration.field.rule",
};

function decisionChainFromRaw(raw: unknown): DecisionChainStepDraft[] {
  if (!Array.isArray(raw) || raw.length === 0) return [];
  return raw.map((s, i) => {
    const r = (s ?? {}) as Record<string, unknown>;
    const target = (r.target ?? {}) as Record<string, unknown>;
    const trigger = (r.trigger ?? {}) as Record<string, unknown>;
    const evidence = (r.evidence ?? {}) as Record<string, unknown>;
    const result = (r.result ?? {}) as Record<string, unknown>;
    const alternatives = Array.isArray(r.alternatives) ? (r.alternatives as Array<Record<string, unknown>>) : [];
    return {
      step: Number(r.step ?? i + 1),
      design_action: String(r.design_action ?? "M3"),
      target: {
        gene: String(target.gene ?? ""),
        enzyme: String(target.enzyme ?? ""),
        pathway: String(target.pathway ?? ""),
        condition: String(target.condition ?? ""),
      },
      trigger: {
        observation: String(trigger.observation ?? ""),
        reasoning: String(trigger.reasoning ?? ""),
        source_location: String(trigger.source_location ?? ""),
      },
      evidence: {
        description: String(evidence.description ?? ""),
        source: String(evidence.source ?? ""),
        source_location: String(evidence.source_location ?? ""),
      },
      evidence_grading: String(r.evidence_grading ?? "软"),
      reason_nature: String(r.reason_nature ?? "事后合理化存疑"),
      alternatives: alternatives.map((a) => ({ approach: String(a.approach ?? ""), rejected_reason: String(a.rejected_reason ?? "") })),
      implementation: String(r.implementation ?? "其他"),
      implementation_detail: String(r.implementation_detail ?? ""),
      result: {
        metric: String(result.metric ?? ""),
        before: String(result.before ?? ""),
        after: String(result.after ?? ""),
        fold_change: String(result.fold_change ?? ""),
        quantified: Boolean(result.quantified),
      },
      rule: String(r.rule ?? ""),
    };
  });
}

interface FieldReview {
  disagree: boolean;
  value: string;
  note: string;
}

interface StepReview {
  original: DecisionChainStepDraft;
  fields: Record<ComparedField, FieldReview>;
}

function stepReviewFromOriginal(original: DecisionChainStepDraft): StepReview {
  const fields = {} as Record<ComparedField, FieldReview>;
  for (const field of COMPARED_FIELDS) {
    fields[field] = { disagree: false, value: String(original[field]), note: "" };
  }
  return { original, fields };
}

function ruleAllowedFor(reasonNature: string): boolean {
  return reasonNature === "机理推断" || reasonNature === "文献类比";
}

/** The decision_chain step this review state would submit as, applying each
 * field's agree/disagree state - agreed fields pass the first annotator's
 * value through verbatim, disagreed fields use the second annotator's typed
 * value. `rule` additionally respects the same reason_nature gating the
 * original single-annotator form did (never carries a rule value when the
 * *effective* reason_nature - post-override - doesn't allow one). */
function buildSubmissionStep(review: StepReview): DecisionChainStepDraft {
  const effectiveReasonNature = review.fields.reason_nature.disagree ? review.fields.reason_nature.value : review.original.reason_nature;
  const ruleAllowed = ruleAllowedFor(effectiveReasonNature);
  const notes: Record<string, string> = {};
  for (const field of COMPARED_FIELDS) {
    const fr = review.fields[field];
    if (fr.disagree && fr.note.trim()) notes[field] = fr.note.trim();
  }
  return {
    ...review.original,
    design_action: review.fields.design_action.disagree ? review.fields.design_action.value : review.original.design_action,
    evidence_grading: review.fields.evidence_grading.disagree ? review.fields.evidence_grading.value : review.original.evidence_grading,
    reason_nature: effectiveReasonNature,
    rule: ruleAllowed ? (review.fields.rule.disagree ? review.fields.rule.value : review.original.rule) : "",
    _disagreement_notes: Object.keys(notes).length > 0 ? notes : undefined,
  };
}

function FieldReviewRow({
  field,
  review,
  originalValue,
  disabled,
  onChange,
}: {
  field: ComparedField;
  review: FieldReview;
  originalValue: string;
  disabled?: boolean;
  onChange: (next: FieldReview) => void;
}) {
  const { t } = useI18n();
  const options = field === "design_action" ? DESIGN_ACTIONS : field === "evidence_grading" ? EVIDENCE_GRADINGS : field === "reason_nature" ? REASON_NATURES : null;
  return (
    <div className={`flex flex-col gap-1.5 rounded border border-border p-2 ${disabled ? "opacity-50" : ""}`}>
      <div className="flex items-center justify-between gap-2">
        <span className="text-[11px] font-medium text-ink">{t(FIELD_LABEL_KEY[field])}</span>
        <label className="flex items-center gap-1.5 text-[11px] text-ink-muted">
          <input
            type="checkbox"
            checked={review.disagree}
            disabled={disabled}
            onChange={(e) => onChange({ ...review, disagree: e.target.checked, value: e.target.checked ? review.value : originalValue })}
          />
          {t("paperEvidence.calibration.disagreeToggle")}
        </label>
      </div>
      {!review.disagree ? (
        <p className="truncate text-[11px] text-ink-faint" title={originalValue || "—"}>
          {originalValue || "—"}
        </p>
      ) : (
        <div className="flex flex-col gap-1">
          {options ? (
            <select className={inputCls} value={review.value} disabled={disabled} onChange={(e) => onChange({ ...review, value: e.target.value })}>
              {options.map((o) => (
                <option key={o} value={o}>
                  {o}
                </option>
              ))}
            </select>
          ) : (
            <textarea rows={2} className={inputCls} disabled={disabled} value={review.value} onChange={(e) => onChange({ ...review, value: e.target.value })} />
          )}
          <input
            className={inputCls}
            disabled={disabled}
            value={review.note}
            onChange={(e) => onChange({ ...review, note: e.target.value })}
            placeholder={t("paperEvidence.calibration.notePlaceholder")}
          />
        </div>
      )}
    </div>
  );
}

function StepReviewCard({ index, review, onChange }: { index: number; review: StepReview; onChange: (next: StepReview) => void }) {
  const { t } = useI18n();
  const original = review.original;
  const effectiveReasonNature = review.fields.reason_nature.disagree ? review.fields.reason_nature.value : original.reason_nature;
  const ruleAllowed = ruleAllowedFor(effectiveReasonNature);

  function updateField(field: ComparedField, next: FieldReview) {
    onChange({ ...review, fields: { ...review.fields, [field]: next } });
  }

  return (
    <div className="flex flex-col gap-2 rounded-lg border border-border p-2.5">
      <span className="w-fit rounded bg-emerald-100 px-1.5 py-0.5 font-mono text-[10px] font-semibold text-emerald-700">
        {t("paperEvidence.design.stepLabel")} {String(index + 1).padStart(2, "0")}
      </span>

      {/* Read-only context from the first annotator's draft - the second
          annotator only needs to judge the 4 fields below against this, not
          re-type it. */}
      <details className="text-[11px] text-ink-muted">
        <summary className="cursor-pointer select-none text-ink-faint">{t("paperEvidence.calibration.readOnlyDraftTitle")}</summary>
        <div className="mt-1.5 grid grid-cols-1 gap-x-3 gap-y-1 rounded bg-surface-sunken p-2 sm:grid-cols-2">
          <p><span className="text-ink-faint">{t("paperEvidence.calibration.field.targetGene")}: </span>{original.target.gene || "—"}</p>
          <p><span className="text-ink-faint">{t("paperEvidence.calibration.field.targetPathway")}: </span>{original.target.pathway || "—"}</p>
          <p className="sm:col-span-2"><span className="text-ink-faint">{t("paperEvidence.calibration.field.triggerObservation")}: </span>{original.trigger.observation || "—"}</p>
          <p className="sm:col-span-2"><span className="text-ink-faint">{t("paperEvidence.calibration.field.triggerReasoning")}: </span>{original.trigger.reasoning || "—"}</p>
          <p className="sm:col-span-2"><span className="text-ink-faint">{t("paperEvidence.calibration.field.evidenceDescription")}: </span>{original.evidence.description || "—"}</p>
          <p><span className="text-ink-faint">{t("paperEvidence.calibration.field.implementation")}: </span>{original.implementation || "—"}</p>
          <p><span className="text-ink-faint">{t("paperEvidence.calibration.field.resultMetric")}: </span>{original.result.metric || "—"}</p>
        </div>
      </details>

      <div>
        <h4 className="label-caps mb-1">{t("paperEvidence.calibration.reviewFieldsTitle")}</h4>
        <div className="grid grid-cols-1 gap-1.5 sm:grid-cols-2">
          <FieldReviewRow field="design_action" review={review.fields.design_action} originalValue={original.design_action} onChange={(next) => updateField("design_action", next)} />
          <FieldReviewRow field="evidence_grading" review={review.fields.evidence_grading} originalValue={original.evidence_grading} onChange={(next) => updateField("evidence_grading", next)} />
          <FieldReviewRow field="reason_nature" review={review.fields.reason_nature} originalValue={original.reason_nature} onChange={(next) => updateField("reason_nature", next)} />
          <FieldReviewRow
            field="rule"
            review={review.fields.rule}
            originalValue={ruleAllowed ? original.rule : t("paperEvidence.design.ruleSuppressed")}
            disabled={!ruleAllowed}
            onChange={(next) => updateField("rule", next)}
          />
        </div>
      </div>
    </div>
  );
}

function ConflictList({ conflicts }: { conflicts: ExtractionConflict[] }) {
  const { t } = useI18n();
  if (conflicts.length === 0) return null;
  return (
    <div className="flex flex-col gap-1.5 rounded-lg border border-amber-300 bg-amber-50/60 p-2.5">
      <p className="flex items-center gap-1.5 text-[11px] font-semibold text-state-caution">
        <AlertTriangle size={13} aria-hidden />
        {t("paperEvidence.calibration.conflictsTitle")} ({conflicts.length})
      </p>
      <ul className="flex flex-col gap-1">
        {conflicts.map((c, i) => (
          <li key={i} className="rounded bg-surface px-2 py-1 text-[11px]">
            <span className="font-medium text-ink">
              {c.step != null ? `${t("paperEvidence.design.stepLabel")} ${c.step}` : t("paperEvidence.calibration.stepCountMismatch")} · {c.field}
            </span>
            <div className="mt-0.5 flex flex-wrap gap-x-3 gap-y-0.5 text-ink-muted">
              {Object.entries(c.valuesByAnnotator).map(([annotator, value]) => (
                <span key={annotator}>
                  <span className="text-ink-faint">{annotator}: </span>
                  {value == null || value === "" ? "—" : JSON.stringify(value)}
                  {c.notes?.[annotator] && <span className="italic text-ink-faint"> ({c.notes[annotator]})</span>}
                </span>
              ))}
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}

const STATUS_STYLES: Record<string, string> = {
  pending: "bg-surface-sunken text-ink-faint border-border",
  in_progress: "bg-accent-soft text-accent-strong border-accent",
  calibrated: "bg-emerald-50 text-state-success border-emerald-300",
  disputed: "bg-amber-50 text-state-caution border-amber-300",
};

const STATUS_LABEL_KEYS: Record<string, DictKey> = {
  pending: "paperEvidence.calibration.status.pending",
  in_progress: "paperEvidence.calibration.status.in_progress",
  calibrated: "paperEvidence.calibration.status.calibrated",
  disputed: "paperEvidence.calibration.status.disputed",
};

/**
 * Dual-annotator calibration panel (老师 §4.3 step 3: "规则字段由两人独立
 * 写、再对齐,统一标注口径" - independent extraction → conflict detection →
 * calibration). Backend (harness/paper_extraction/calibration.py) and its
 * two API routes existed and were tested before this panel; this is the
 * first UI that lets a second reviewer actually submit a draft and see
 * where it disagrees with the first, closing the "backend-only" gap noted
 * in WORK_A_ALIGNMENT_REPORT.md §8.
 *
 * Simplified review flow (request: the original per-step form asked for
 * all ~17 decision_chain fields, retyped from scratch, when conflict
 * detection only ever compares 4 of them - see COMPARED_FIELDS above): the
 * second annotator sees the first annotator's draft read-only and only
 * agrees/flags-and-corrects the 4 fields that can actually produce a
 * conflict, each with an optional one-line rationale for why she disagrees.
 */
export function CalibrationPanel({
  ddrId,
  rawRecord,
  calibrationStatus,
  conflictCount,
  attempts,
  onSubmitted,
}: {
  ddrId: string;
  rawRecord: Record<string, unknown> | null;
  calibrationStatus: string | null;
  conflictCount: number;
  attempts: Array<{ annotator: string; recordedAt: string; stepCount: number }>;
  onSubmitted: () => void;
}) {
  const { t } = useI18n();
  const queryClient = useQueryClient();
  const [formOpen, setFormOpen] = useState(false);
  const [annotator, setAnnotator] = useState("");
  const [reviews, setReviews] = useState<StepReview[]>(() => decisionChainFromRaw(rawRecord?.decision_chain).map(stepReviewFromOriginal));
  const [lastConflicts, setLastConflicts] = useState<ExtractionConflict[] | null>(null);

  const conflictsQuery = useQuery({
    queryKey: ["ddr-conflicts", ddrId],
    queryFn: () => getExtractionConflicts(ddrId),
    enabled: conflictCount > 0 && lastConflicts === null,
  });

  const displayedConflicts = lastConflicts ?? conflictsQuery.data ?? [];

  const submitMutation = useMutation({
    mutationFn: () => submitExtractionAttempt(ddrId, annotator.trim(), reviews.map(buildSubmissionStep)),
    onSuccess: (res) => {
      setLastConflicts(res.conflicts);
      setFormOpen(false);
      setAnnotator("");
      queryClient.invalidateQueries({ queryKey: ["ddr-conflicts", ddrId] });
      onSubmitted();
    },
  });

  function openForm() {
    setReviews(decisionChainFromRaw(rawRecord?.decision_chain).map(stepReviewFromOriginal));
    setFormOpen(true);
  }

  return (
    <div className="panel flex flex-col gap-3 p-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h2 className="flex items-center gap-1.5 text-sm font-semibold text-ink">
          <UserCheck size={15} className="text-accent" aria-hidden /> {t("paperEvidence.calibration.title")}
        </h2>
        <span className={`rounded border px-1.5 py-0.5 text-[10px] font-medium ${STATUS_STYLES[calibrationStatus ?? "pending"] ?? STATUS_STYLES.pending}`}>
          {t(STATUS_LABEL_KEYS[calibrationStatus ?? "pending"] ?? STATUS_LABEL_KEYS.pending)}
        </span>
      </div>
      <p className="text-[11px] text-ink-muted">{t("paperEvidence.calibration.subtitle")}</p>

      {attempts.length === 0 ? (
        <p className="text-[11px] italic text-ink-faint">{t("paperEvidence.calibration.noAttempts")}</p>
      ) : (
        <ul className="flex flex-col gap-1">
          {attempts.map((a, i) => (
            <li key={i} className="flex items-center gap-2 rounded bg-surface-sunken px-2 py-1 text-[11px] text-ink-muted">
              <CheckCircle2 size={12} className="text-emerald-600" aria-hidden />
              <span className="font-medium text-ink">{a.annotator}</span>
              <span>· {a.stepCount} {t("paperEvidence.design.stepLabel")}</span>
              <span className="text-ink-faint">· {new Date(a.recordedAt).toLocaleString()}</span>
            </li>
          ))}
        </ul>
      )}

      <ConflictList conflicts={displayedConflicts} />

      {!formOpen && (
        <button
          type="button"
          onClick={openForm}
          className="w-fit rounded-lg border border-border px-3 py-1.5 text-[11px] font-medium text-ink-muted hover:bg-surface-sunken"
        >
          {t("paperEvidence.calibration.newAttemptButton")}
        </button>
      )}

      {formOpen && (
        <div className="flex flex-col gap-3 rounded-lg border border-accent/40 bg-accent-soft/20 p-3">
          <div>
            <label className={labelCls}>{t("paperEvidence.calibration.field.annotator")}</label>
            <input className={inputCls} value={annotator} onChange={(e) => setAnnotator(e.target.value)} placeholder={t("paperEvidence.calibration.annotatorPlaceholder")} />
          </div>

          <div className="flex flex-col gap-2">
            {reviews.map((review, i) => (
              <StepReviewCard key={i} index={i} review={review} onChange={(next) => setReviews((prev) => prev.map((r, idx) => (idx === i ? next : r)))} />
            ))}
          </div>

          {submitMutation.isError && <p className="text-[11px] text-state-risk">{String(submitMutation.error)}</p>}

          <div className="flex items-center gap-2">
            <button
              type="button"
              disabled={annotator.trim().length === 0 || reviews.length === 0 || submitMutation.isPending}
              onClick={() => submitMutation.mutate()}
              className="rounded-lg bg-accent px-3 py-1.5 text-[11px] font-medium text-white shadow-sm transition hover:brightness-95 disabled:opacity-40"
            >
              {submitMutation.isPending ? t("paperEvidence.calibration.submitting") : t("paperEvidence.calibration.submit")}
            </button>
            <button type="button" onClick={() => setFormOpen(false)} className="text-[11px] text-ink-faint hover:text-ink">
              {t("paperEvidence.calibration.cancel")}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
