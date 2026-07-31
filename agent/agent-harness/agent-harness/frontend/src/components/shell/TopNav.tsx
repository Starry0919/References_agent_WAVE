import { NavLink, useParams } from "react-router-dom";
import { Gauge, LayoutDashboard, Library, Sparkles, Stethoscope, FlaskConical } from "lucide-react";
import type { LucideIcon } from "lucide-react";
import { useI18n, type DictKey } from "@/lib/i18n";
import { useBackendHealth } from "@/state/BackendHealth";
import { LanguageToggle } from "./LanguageToggle";

/**
 * Global primary navigation. The original IA contract (prompt §六.1) fixed
 * exactly four top-level pages; the Paper Experimental Design Extraction
 * module (harness/api/paper_extraction.py) is a fifth, later, real
 * capability - deliberately added to nav rather than left reachable only by
 * a raw URL, since an unlisted route is not meaningfully "integrated". No
 * icon-only labels either way (prompt: "文字名称不可被图标完全替代").
 */
const NAV_ITEMS: Array<{ id: string; icon: LucideIcon; labelKey: DictKey; path: (projectId: string) => string }> = [
  { id: "command-center", icon: LayoutDashboard, labelKey: "nav.commandCenter", path: (p) => `/projects/${p}` },
  { id: "idea-workspace", icon: Sparkles, labelKey: "nav.ideaWorkspace", path: (p) => `/projects/${p}/ideas` },
  { id: "diagnosis", icon: Stethoscope, labelKey: "nav.diagnosis", path: (p) => `/projects/${p}/diagnosis` },
  { id: "engineering-design", icon: FlaskConical, labelKey: "nav.engineeringDesign", path: (p) => `/projects/${p}/design` },
  { id: "knowledge", icon: Library, labelKey: "nav.knowledge", path: (p) => `/projects/${p}/knowledge` },
  { id: "eval-metrics", icon: Gauge, labelKey: "nav.evalMetrics", path: (p) => `/projects/${p}/metrics` },
];

export function TopNav() {
  const { projectId } = useParams<{ projectId: string }>();
  const { t } = useI18n();
  const { connected, checking } = useBackendHealth();

  return (
    <header className="flex h-12 flex-shrink-0 items-center justify-between gap-3 overflow-x-auto border-b border-border bg-surface px-4">
      <div className="flex items-center gap-6">
        <span className="text-[13px] font-semibold tracking-tight text-ink">{t("nav.appTitle")}</span>
        {projectId && (
          <nav className="flex items-center gap-1">
            {NAV_ITEMS.map((item) => (
              <NavLink
                key={item.id}
                to={item.path(projectId)}
                end={item.id === "command-center"}
                className={({ isActive }) =>
                  `flex items-center gap-1.5 rounded px-2.5 py-1.5 text-[13px] font-medium transition-colors ${
                    isActive ? "bg-accent-soft text-accent-strong" : "text-ink-muted hover:bg-surface-sunken hover:text-ink"
                  }`
                }
              >
                <item.icon size={14} aria-hidden />
                {t(item.labelKey)}
              </NavLink>
            ))}
          </nav>
        )}
      </div>
      <div className="flex flex-shrink-0 items-center gap-3">
        <span
          className={`flex items-center gap-1.5 rounded px-2 py-1 text-[11px] font-medium ${
            checking ? "text-ink-faint" : connected ? "text-state-success" : "text-state-risk"
          }`}
        >
          <span
            className={`h-1.5 w-1.5 rounded-full ${checking ? "bg-ink-faint" : connected ? "bg-state-success" : "bg-state-risk"}`}
            aria-hidden
          />
          {checking ? t("status.checking") : connected ? t("status.connected") : t("status.disconnected")}
        </span>
        <LanguageToggle />
      </div>
    </header>
  );
}
