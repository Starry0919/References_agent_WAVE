import type { AgentTraceStep } from "@/api/evidence";
import { useI18n, type DictKey } from "@/lib/i18n";

/**
 * One "Agent Analysis Record" card in the left-hand Agent Reasoning Trace
 * column (抽取详情页面.md's Step Card Design). Deliberately structured as
 * Input/Operation/Output/Confidence/Evidence - an observable workflow
 * record, never raw chain-of-thought.
 */

const KIND_LABEL_KEY: Record<AgentTraceStep["kind"], DictKey> = {
  problem_understanding: "paperEvidence.trace.kind.problemUnderstanding",
  intervention: "paperEvidence.trace.kind.intervention",
  logic_reconstruction: "paperEvidence.trace.kind.logicReconstruction",
  evidence_validation: "paperEvidence.trace.kind.evidenceValidation",
};

const LOGIC_KEYS: Record<string, DictKey> = {
  problem: "paperEvidence.trace.logic.problem",
  hypothesis: "paperEvidence.trace.logic.hypothesis",
  modification: "paperEvidence.trace.logic.modification",
  measurement: "paperEvidence.trace.logic.measurement",
  conclusion: "paperEvidence.trace.logic.conclusion",
};

function StepOutput({ output }: { output: AgentTraceStep["output"] }) {
  const { t } = useI18n();
  if (typeof output === "string") return <p>{output}</p>;
  if (Array.isArray(output)) {
    return (
      <ul className="list-disc space-y-0.5 pl-4">
        {output.map((o, i) => (
          <li key={i}>{o}</li>
        ))}
      </ul>
    );
  }
  const entries = Object.entries(output).filter(([, v]) => v);
  return (
    <ol className="flex flex-col gap-1">
      {entries.map(([k, v], i) => (
        <li key={k} className="flex gap-1.5">
          <span className="shrink-0 font-mono text-[10px] text-sky-600">
            {i + 1}.
          </span>
          <span>
            <span className="font-medium text-ink-faint">
              {t(
                LOGIC_KEYS[k] ??
                  ("paperEvidence.trace.logic.problem" as DictKey),
              )}
              :{" "}
            </span>
            {v}
          </span>
        </li>
      ))}
    </ol>
  );
}

export function ReasoningStepCard({
  step,
  active,
  onClick,
  cardRef,
}: {
  step: AgentTraceStep;
  active: boolean;
  onClick: () => void;
  cardRef?: (el: HTMLDivElement | null) => void;
}) {
  const { t } = useI18n();
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
        active
          ? "border-sky-400 bg-sky-50/70 shadow-sm ring-1 ring-sky-200"
          : "border-border bg-surface hover:border-sky-300"
      }`}
    >
      <div className="flex flex-wrap items-center justify-between gap-1.5">
        <div className="flex items-center gap-1.5">
          <span className="rounded bg-sky-100 px-1.5 py-0.5 font-mono text-[10px] font-semibold text-sky-700">
            {t("paperEvidence.trace.stepLabel")}{" "}
            {String(step.step).padStart(2, "0")}
          </span>
          <span className="font-semibold text-ink">{step.title}</span>
        </div>
        {step.confidence != null && (
          <span className="shrink-0 text-[10px] text-ink-faint">
            {t("page5.result.confidence")} {(step.confidence * 100).toFixed(0)}%
          </span>
        )}
      </div>
      <p className="mt-1 text-[10px] font-medium uppercase tracking-wide text-sky-600">
        {t(KIND_LABEL_KEY[step.kind])}
      </p>

      <div className="mt-2 flex flex-col gap-1.5 text-ink-muted">
        <div>
          <span className="label-caps">{t("paperEvidence.trace.input")}</span>
          <p>{step.input}</p>
        </div>
        <div>
          <span className="label-caps">
            {t("paperEvidence.trace.operation")}
          </span>
          <p>{step.operation}</p>
        </div>
        <div>
          <span className="label-caps">{t("paperEvidence.trace.output")}</span>
          <div className="mt-0.5 text-ink">
            <StepOutput output={step.output} />
          </div>
        </div>
        {step.evidence.length > 0 && (
          <div>
            <span className="label-caps">{t("page5.evidenceTitle")}</span>
            <ul className="mt-0.5 flex flex-col gap-0.5">
              {step.evidence.map((e, i) => (
                <li
                  key={i}
                  className="rounded bg-surface-sunken px-1.5 py-0.5 text-[10px] text-ink-faint"
                >
                  {e}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}
