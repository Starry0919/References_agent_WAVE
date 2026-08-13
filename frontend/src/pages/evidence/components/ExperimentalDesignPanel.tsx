import { FlaskConical } from "lucide-react";
import type { ExperimentalDesignStep } from "@/api/evidence";
import { EmptyState } from "@/components/common/EmptyState";
import { useI18n } from "@/lib/i18n";
import { ExperimentalStepCard } from "./ExperimentalStepCard";

/**
 * RIGHT COLUMN - Experimental Design Reconstruction (抽取详情页面.md
 * §"RIGHT COLUMN"). `activeDesignStep === "all"` highlights every card at
 * once, for when the left-hand narrative (problem/logic/evidence) cards -
 * which summarize across the whole design, not one intervention - are
 * selected.
 */
export function ExperimentalDesignPanel({
  steps,
  activeDesignStep,
  onSelectDesign,
  registerRef,
}: {
  steps: ExperimentalDesignStep[];
  activeDesignStep: number | "all" | null;
  onSelectDesign: (step: ExperimentalDesignStep) => void;
  registerRef: (step: number, el: HTMLDivElement | null) => void;
}) {
  const { t } = useI18n();
  return (
    <div className="flex min-w-0 flex-col gap-2">
      <div>
        <h2 className="flex items-center gap-1.5 text-sm font-semibold text-emerald-700">
          <FlaskConical size={15} aria-hidden /> {t("paperEvidence.design.title")}
        </h2>
        <p className="mt-0.5 text-[11px] text-ink-faint">{t("paperEvidence.design.subtitle")}</p>
      </div>
      {steps.length === 0 ? (
        <EmptyState variant="unavailable" title={t("paperEvidence.design.emptyTitle")} />
      ) : (
        steps.map((s) => (
          <ExperimentalStepCard
            key={s.step}
            step={s}
            active={activeDesignStep === s.step || activeDesignStep === "all"}
            onClick={() => onSelectDesign(s)}
            cardRef={(el) => registerRef(s.step, el)}
          />
        ))
      )}
    </div>
  );
}
