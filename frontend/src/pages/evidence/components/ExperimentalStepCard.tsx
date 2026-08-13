import type { ExperimentalDesignStep } from "@/api/evidence";
import { useI18n } from "@/lib/i18n";

/**
 * One "Experimental Step" SOP card in the right-hand Experimental Design
 * Reconstruction column (抽取详情页面.md's WHY/HOW step structure) - a
 * synthetic-biology SOP entry, not a plain summary paragraph.
 */
export function ExperimentalStepCard({
  step,
  active,
  onClick,
  cardRef,
}: {
  step: ExperimentalDesignStep;
  active: boolean;
  onClick: () => void;
  cardRef?: (el: HTMLDivElement | null) => void;
}) {
  const { t } = useI18n();
  const gradingClass =
    step.evidenceGrading === "硬" ? "bg-emerald-100 text-emerald-700" : step.evidenceGrading === "软" ? "bg-amber-100 text-amber-700" : "bg-surface-sunken text-ink-faint";
  return (
    <div
      ref={cardRef}
      onClick={onClick}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          onClick();
        }
      }}
      className={`cursor-pointer rounded-lg border p-3 text-[11px] transition ${
        active ? "border-violet-400 bg-violet-50/70 shadow-sm ring-1 ring-violet-200" : "border-border bg-surface hover:border-violet-300"
      }`}
    >
      <div className="flex flex-wrap items-center justify-between gap-1.5">
        <div className="flex items-center gap-1.5">
          <span className="rounded bg-emerald-100 px-1.5 py-0.5 font-mono text-[10px] font-semibold text-emerald-700">
            {t("paperEvidence.design.stepLabel")} {String(step.step).padStart(2, "0")}
          </span>
          <span className="font-semibold text-ink">{step.title}</span>
        </div>
        {step.evidenceGrading && <span className={`shrink-0 rounded px-1.5 py-0.5 text-[10px] font-medium ${gradingClass}`}>{step.evidenceGrading}证据</span>}
      </div>

      <div className="mt-2 rounded border border-emerald-200 bg-emerald-50/50 p-2">
        <p className="label-caps text-emerald-700">{t("paperEvidence.design.why")}</p>
        <p className="mt-1">
          <span className="font-medium text-ink-faint">{t("paperEvidence.design.problem")}: </span>
          {step.problem || "—"}
        </p>
        <p className="mt-1 flex items-start gap-1 text-emerald-700">
          <span aria-hidden>↓</span>
        </p>
        <p>
          <span className="font-medium text-ink-faint">{t("paperEvidence.design.hypothesis")}: </span>
          {step.hypothesis || "—"}
        </p>
      </div>

      <div className="mt-2 rounded border border-violet-200 bg-violet-50/50 p-2">
        <p className="label-caps text-violet-700">{t("paperEvidence.design.how")}</p>
        <p className="mt-1">
          <span className="font-medium text-ink-faint">{t("paperEvidence.design.modification")}: </span>
          {[step.engineeringAction.type, step.engineeringAction.target, step.engineeringAction.modification].filter(Boolean).join(" · ") || "—"}
        </p>
        {step.method.length > 0 && (
          <p className="mt-1">
            <span className="font-medium text-ink-faint">{t("paperEvidence.design.validation")}: </span>
            {step.method.join("; ")}
          </p>
        )}
        {step.result && (
          <p className="mt-1">
            <span className="font-medium text-ink-faint">{t("paperEvidence.design.result")}: </span>
            {step.result}
          </p>
        )}
      </div>

      {step.evidence.length > 0 && (
        <div className="mt-2">
          <span className="label-caps">{t("page5.evidenceTitle")}</span>
          <ul className="mt-0.5 flex flex-col gap-0.5">
            {step.evidence.map((e, i) => (
              <li key={i} className="rounded bg-surface-sunken px-1.5 py-0.5 text-[10px] text-ink-faint">
                {e}
              </li>
            ))}
          </ul>
        </div>
      )}

      {(step.reasonNature || step.alternatives.length > 0 || step.rule) && (
        <div className="mt-2 rounded border border-sky-200 bg-sky-50/50 p-2">
          {step.reasonNature && (
            <p>
              <span className="label-caps text-sky-700">{t("paperEvidence.design.reasonNature")}: </span>
              <span className="font-medium text-ink">{step.reasonNature}</span>
            </p>
          )}
          {step.alternatives.length > 0 && (
            <div className="mt-1">
              <span className="label-caps text-sky-700">{t("paperEvidence.design.alternatives")}</span>
              <ul className="mt-0.5 flex flex-col gap-0.5">
                {step.alternatives.map((a, i) => (
                  <li key={i} className="text-ink-faint">
                    {a.approach}
                    {a.rejectedReason && <span> — {a.rejectedReason}</span>}
                  </li>
                ))}
              </ul>
            </div>
          )}
          <div className="mt-1">
            <span className="label-caps text-sky-700">{t("paperEvidence.design.rule")}: </span>
            {step.rule ? <span>{step.rule}</span> : <span className="italic text-ink-faint">{t("paperEvidence.design.ruleSuppressed")}</span>}
          </div>
        </div>
      )}
    </div>
  );
}
