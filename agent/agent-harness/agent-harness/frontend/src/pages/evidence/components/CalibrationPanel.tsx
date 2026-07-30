import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { AlertTriangle, CheckCircle2, Plus, Trash2, UserCheck } from "lucide-react";
import {
  blankDecisionChainStep,
  getExtractionConflicts,
  submitExtractionAttempt,
  type DecisionChainStepDraft,
  type ExtractionConflict,
} from "@/api/evidence";
import { useI18n, type DictKey } from "@/lib/i18n";

const DESIGN_ACTIONS = ["M0", "M1", "M2", "M3", "M4", "M5", "M6", "M7", "M8", "M9", "M11"];
const EVIDENCE_GRADINGS = ["硬", "软"];
const REASON_NATURES = ["机理推断", "文献类比", "现成可得", "筛选得来", "事后合理化存疑"];
const IMPLEMENTATIONS = ["KO", "CRISPRi", "过表达", "点突变", "启动子工程", "异源表达", "培养基优化", "发酵调控", "RBS工程", "辅因子工程", "动态调控", "其他"];

const inputCls = "w-full rounded border border-border bg-surface px-2 py-1 text-[11px] outline-none transition focus:border-accent focus:ring-2 focus:ring-accent/10";
const labelCls = "label-caps";

function decisionChainFromRaw(raw: unknown): DecisionChainStepDraft[] {
  if (!Array.isArray(raw) || raw.length === 0) return [blankDecisionChainStep(1)];
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

function StepEditor({
  step,
  index,
  onChange,
  onRemove,
  canRemove,
}: {
  step: DecisionChainStepDraft;
  index: number;
  onChange: (next: DecisionChainStepDraft) => void;
  onRemove: () => void;
  canRemove: boolean;
}) {
  const { t } = useI18n();
  const ruleAllowed = step.reason_nature === "机理推断" || step.reason_nature === "文献类比";
  return (
    <div className="flex flex-col gap-2 rounded-lg border border-border p-2.5">
      <div className="flex items-center justify-between">
        <span className="rounded bg-emerald-100 px-1.5 py-0.5 font-mono text-[10px] font-semibold text-emerald-700">
          {t("paperEvidence.design.stepLabel")} {String(index + 1).padStart(2, "0")}
        </span>
        {canRemove && (
          <button type="button" onClick={onRemove} className="text-ink-faint hover:text-state-risk" aria-label={t("paperEvidence.calibration.removeStep")}>
            <Trash2 size={13} aria-hidden />
          </button>
        )}
      </div>

      <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
        <div>
          <label className={labelCls}>{t("paperEvidence.calibration.field.designAction")}</label>
          <select className={inputCls} value={step.design_action} onChange={(e) => onChange({ ...step, design_action: e.target.value })}>
            {DESIGN_ACTIONS.map((a) => (
              <option key={a} value={a}>
                {a}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className={labelCls}>{t("paperEvidence.calibration.field.evidenceGrading")}</label>
          <select className={inputCls} value={step.evidence_grading} onChange={(e) => onChange({ ...step, evidence_grading: e.target.value })}>
            {EVIDENCE_GRADINGS.map((g) => (
              <option key={g} value={g}>
                {g}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className={labelCls}>{t("paperEvidence.calibration.field.reasonNature")}</label>
          <select
            className={inputCls}
            value={step.reason_nature}
            onChange={(e) => {
              const reason_nature = e.target.value;
              const allowed = reason_nature === "机理推断" || reason_nature === "文献类比";
              onChange({ ...step, reason_nature, rule: allowed ? step.rule : "" });
            }}
          >
            {REASON_NATURES.map((r) => (
              <option key={r} value={r}>
                {r}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className={labelCls}>{t("paperEvidence.calibration.field.implementation")}</label>
          <select className={inputCls} value={step.implementation} onChange={(e) => onChange({ ...step, implementation: e.target.value })}>
            {IMPLEMENTATIONS.map((i) => (
              <option key={i} value={i}>
                {i}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
        <div>
          <label className={labelCls}>{t("paperEvidence.calibration.field.targetGene")}</label>
          <input className={inputCls} value={step.target.gene} onChange={(e) => onChange({ ...step, target: { ...step.target, gene: e.target.value } })} />
        </div>
        <div>
          <label className={labelCls}>{t("paperEvidence.calibration.field.targetEnzyme")}</label>
          <input className={inputCls} value={step.target.enzyme} onChange={(e) => onChange({ ...step, target: { ...step.target, enzyme: e.target.value } })} />
        </div>
        <div>
          <label className={labelCls}>{t("paperEvidence.calibration.field.targetPathway")}</label>
          <input className={inputCls} value={step.target.pathway} onChange={(e) => onChange({ ...step, target: { ...step.target, pathway: e.target.value } })} />
        </div>
        <div>
          <label className={labelCls}>{t("paperEvidence.calibration.field.targetCondition")}</label>
          <input className={inputCls} value={step.target.condition} onChange={(e) => onChange({ ...step, target: { ...step.target, condition: e.target.value } })} />
        </div>
      </div>

      <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
        <div>
          <label className={labelCls}>{t("paperEvidence.calibration.field.triggerObservation")}</label>
          <textarea
            rows={2}
            className={inputCls}
            value={step.trigger.observation}
            onChange={(e) => onChange({ ...step, trigger: { ...step.trigger, observation: e.target.value } })}
          />
        </div>
        <div>
          <label className={labelCls}>{t("paperEvidence.calibration.field.triggerReasoning")}</label>
          <textarea
            rows={2}
            className={inputCls}
            value={step.trigger.reasoning}
            onChange={(e) => onChange({ ...step, trigger: { ...step.trigger, reasoning: e.target.value } })}
          />
        </div>
      </div>

      <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
        <div>
          <label className={labelCls}>{t("paperEvidence.calibration.field.evidenceDescription")}</label>
          <textarea
            rows={2}
            className={inputCls}
            value={step.evidence.description}
            onChange={(e) => onChange({ ...step, evidence: { ...step.evidence, description: e.target.value } })}
          />
        </div>
        <div>
          <label className={labelCls}>{t("paperEvidence.calibration.field.evidenceSource")}</label>
          <input className={inputCls} value={step.evidence.source} onChange={(e) => onChange({ ...step, evidence: { ...step.evidence, source: e.target.value } })} />
        </div>
      </div>

      <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
        <div>
          <label className={labelCls}>{t("paperEvidence.calibration.field.resultMetric")}</label>
          <input className={inputCls} value={step.result.metric} onChange={(e) => onChange({ ...step, result: { ...step.result, metric: e.target.value } })} />
        </div>
        <div>
          <label className={labelCls}>{t("paperEvidence.calibration.field.resultBefore")}</label>
          <input className={inputCls} value={step.result.before} onChange={(e) => onChange({ ...step, result: { ...step.result, before: e.target.value } })} />
        </div>
        <div>
          <label className={labelCls}>{t("paperEvidence.calibration.field.resultAfter")}</label>
          <input className={inputCls} value={step.result.after} onChange={(e) => onChange({ ...step, result: { ...step.result, after: e.target.value } })} />
        </div>
        <div>
          <label className={labelCls}>{t("paperEvidence.calibration.field.resultFoldChange")}</label>
          <input className={inputCls} value={step.result.fold_change} onChange={(e) => onChange({ ...step, result: { ...step.result, fold_change: e.target.value } })} />
        </div>
      </div>

      <div>
        <label className={labelCls}>
          {t("paperEvidence.calibration.field.rule")}
          {!ruleAllowed && <span className="ml-1 font-normal normal-case text-ink-faint">({t("paperEvidence.design.ruleSuppressed")})</span>}
        </label>
        <textarea
          rows={2}
          disabled={!ruleAllowed}
          className={`${inputCls} disabled:cursor-not-allowed disabled:bg-surface-sunken disabled:text-ink-faint`}
          value={step.rule}
          onChange={(e) => onChange({ ...step, rule: e.target.value })}
        />
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
  const [steps, setSteps] = useState<DecisionChainStepDraft[]>(() => decisionChainFromRaw(rawRecord?.decision_chain));
  const [lastConflicts, setLastConflicts] = useState<ExtractionConflict[] | null>(null);

  const conflictsQuery = useQuery({
    queryKey: ["ddr-conflicts", ddrId],
    queryFn: () => getExtractionConflicts(ddrId),
    enabled: conflictCount > 0 && lastConflicts === null,
  });

  const displayedConflicts = lastConflicts ?? conflictsQuery.data ?? [];

  const submitMutation = useMutation({
    mutationFn: () => submitExtractionAttempt(ddrId, annotator.trim(), steps),
    onSuccess: (res) => {
      setLastConflicts(res.conflicts);
      setFormOpen(false);
      setAnnotator("");
      queryClient.invalidateQueries({ queryKey: ["ddr-conflicts", ddrId] });
      onSubmitted();
    },
  });

  function openForm() {
    setSteps(decisionChainFromRaw(rawRecord?.decision_chain));
    setFormOpen(true);
  }

  function updateStep(index: number, next: DecisionChainStepDraft) {
    setSteps((prev) => prev.map((s, i) => (i === index ? next : s)));
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
            {steps.map((s, i) => (
              <StepEditor
                key={i}
                step={s}
                index={i}
                canRemove={steps.length > 1}
                onChange={(next) => updateStep(i, next)}
                onRemove={() => setSteps((prev) => prev.filter((_, idx) => idx !== i))}
              />
            ))}
          </div>

          <button
            type="button"
            onClick={() => setSteps((prev) => [...prev, blankDecisionChainStep(prev.length + 1)])}
            className="flex w-fit items-center gap-1 rounded border border-dashed border-border px-2 py-1 text-[11px] text-ink-muted hover:bg-surface-sunken"
          >
            <Plus size={12} aria-hidden /> {t("paperEvidence.calibration.addStep")}
          </button>

          {submitMutation.isError && <p className="text-[11px] text-state-risk">{String(submitMutation.error)}</p>}

          <div className="flex items-center gap-2">
            <button
              type="button"
              disabled={annotator.trim().length === 0 || submitMutation.isPending}
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
