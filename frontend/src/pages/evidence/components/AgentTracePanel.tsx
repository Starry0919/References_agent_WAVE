import { Bot } from "lucide-react";
import type { AgentTraceStep } from "@/api/evidence";
import { EmptyState } from "@/components/common/EmptyState";
import { useI18n } from "@/lib/i18n";
import { ReasoningStepCard } from "./ReasoningStepCard";

/**
 * LEFT COLUMN - Agent Reasoning Trace (抽取详情页面.md §"LEFT COLUMN").
 * Sync state (`activeAgentStep`) is owned by the page so it can stay
 * coordinated with the right-hand ExperimentalDesignPanel.
 */
export function AgentTracePanel({
  steps,
  activeAgentStep,
  onSelectAgent,
  registerRef,
}: {
  steps: AgentTraceStep[];
  activeAgentStep: number | null;
  onSelectAgent: (step: AgentTraceStep) => void;
  registerRef: (step: number, el: HTMLDivElement | null) => void;
}) {
  const { t } = useI18n();
  return (
    <div className="flex min-w-0 flex-col gap-2">
      <div>
        <h2 className="flex items-center gap-1.5 text-sm font-semibold text-sky-700">
          <Bot size={15} aria-hidden /> {t("paperEvidence.trace.title")}
        </h2>
        <p className="mt-0.5 text-[11px] text-ink-faint">
          {t("paperEvidence.trace.subtitle")}
        </p>
      </div>
      {steps.length === 0 ? (
        <EmptyState
          variant="unavailable"
          title={t("paperEvidence.trace.emptyTitle")}
        />
      ) : (
        steps.map((s) => (
          <ReasoningStepCard
            key={s.step}
            step={s}
            active={activeAgentStep === s.step}
            onClick={() => onSelectAgent(s)}
            cardRef={(el) => registerRef(s.step, el)}
          />
        ))
      )}
    </div>
  );
}
