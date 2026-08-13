import { MapPin } from "lucide-react";
import { APPLICABILITY_SCOPE_KEYS } from "@/api/knowledge";
import { useI18n, type DictKey } from "@/lib/i18n";

const KEY_LABEL: Record<(typeof APPLICABILITY_SCOPE_KEYS)[number], DictKey> = {
  species: "applicability.species",
  strain_background: "applicability.strainBackground",
  genotype_context: "applicability.genotypeContext",
  medium: "applicability.medium",
  carbon_source: "applicability.carbonSource",
  cultivation_mode: "applicability.cultivationMode",
  assay: "applicability.assay",
};

/**
 * Applicability Context (Page 3 prompt §17): knowledge is scoped by
 * default, not universal. Every one of the 7 real `KnowledgeClaim.scope`
 * dimensions is always shown; a missing/null value renders literally
 * "Unknown" rather than being omitted (an omitted row could be misread as
 * "not applicable"/"universal", which §17 explicitly forbids).
 */
export function ApplicabilityPanel({ scope }: { scope: Record<string, unknown> }) {
  const { t } = useI18n();
  return (
    <div className="flex flex-col gap-1.5">
      <div className="flex items-center gap-1.5 text-[11px] font-medium text-ink-muted">
        <MapPin size={12} aria-hidden />
        {t("applicability.title")}
      </div>
      <dl className="grid grid-cols-[auto_1fr] gap-x-3 gap-y-1 text-xs">
        {APPLICABILITY_SCOPE_KEYS.map((key) => {
          const raw = scope[key];
          const known = raw !== undefined && raw !== null && raw !== "";
          return (
            <div className="contents" key={key}>
              <dt className="text-ink-faint">{t(KEY_LABEL[key])}</dt>
              <dd className={known ? "text-ink" : "italic text-ink-faint"}>{known ? String(raw) : t("applicability.unknown")}</dd>
            </div>
          );
        })}
      </dl>
    </div>
  );
}
