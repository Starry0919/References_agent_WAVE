import { useSearchParams } from "react-router-dom";
import { History } from "lucide-react";
import { useI18n } from "@/lib/i18n";

/**
 * Version is URL-owned state (prompt §6.6 - "不得总是默认为 latest").
 * Reads/writes the `version` search param so refresh, deep-link and
 * back/forward all restore exactly the version being viewed, and viewing
 * a historical version never looks like editing latest.
 */
export function VersionSelector({ versions, latest }: { versions: number[]; latest: number }) {
  const [params, setParams] = useSearchParams();
  const { t } = useI18n();
  const selected = Number(params.get("version") ?? latest);
  const isHistorical = selected !== latest;

  return (
    <div className="flex items-center gap-2">
      <History size={13} className="text-ink-faint" aria-hidden />
      <select
        aria-label={t("version.objectVersion")}
        className="rounded border border-border bg-surface px-1.5 py-0.5 font-mono text-xs text-ink"
        value={selected}
        onChange={(e) => {
          const v = Number(e.target.value);
          const next = new URLSearchParams(params);
          if (v === latest) next.delete("version");
          else next.set("version", String(v));
          setParams(next, { replace: false });
        }}
      >
        {versions.map((v) => (
          <option key={v} value={v}>
            v{v}
            {v === latest ? ` ${t("version.latest")}` : ""}
          </option>
        ))}
      </select>
      {isHistorical && (
        <span className="rounded border border-amber-300 bg-amber-50 px-1.5 py-0.5 text-[11px] font-medium text-state-stale">
          {t("version.viewingHistorical")}
        </span>
      )}
    </div>
  );
}
