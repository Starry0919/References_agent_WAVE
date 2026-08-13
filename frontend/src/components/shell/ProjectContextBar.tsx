import { Link, useLocation, useParams } from "react-router-dom";
import { FlaskConical, ChevronRight } from "lucide-react";
import { useI18n } from "@/lib/i18n";
import { useProjectContext } from "@/state/useProjectContext";
import { StatusBadge } from "@/components/common/StatusBadge";

/**
 * Persistent Location Model (prompt §6.6): Project / DBTL Cycle / Stage /
 * Selected Object / Version, visible on every work page, never
 * reconstructed silently. Stage/Selected-Object come from the current
 * route (children render their own trailing crumb via `useMatches`-free
 * simple path parsing to keep this component route-agnostic).
 */
export function ProjectContextBar() {
  const { t } = useI18n();
  const { projectId } = useParams<{ projectId: string }>();
  const { project, projectLoading, cycle } = useProjectContext();
  const location = useLocation();

  if (!projectId) return null;

  const stageMatch = location.pathname.match(/\/workspace\/[^/]+\/([a-zA-Z-]+)/);
  const stage = stageMatch?.[1];

  return (
    <nav
      aria-label={t("nav.breadcrumb")}
      className="flex h-10 flex-shrink-0 items-center gap-4 border-b border-border bg-surface-sunken px-4 text-xs"
    >
      <div className="flex items-center gap-1.5 text-ink-muted">
        <FlaskConical size={13} aria-hidden />
        <span className="label-caps">{t("context.project")}</span>
        {projectLoading ? (
          <span className="text-ink-faint">…</span>
        ) : (
          <span className="font-medium text-ink">{project?.name ?? projectId}</span>
        )}
        <Link to="/projects" className="ml-1 text-accent-strong underline decoration-dotted underline-offset-2">
          {t("context.switchProject")}
        </Link>
      </div>

      {cycle && (
        <>
          <ChevronRight size={12} className="text-ink-faint" aria-hidden />
          <div className="flex items-center gap-1.5 text-ink-muted">
            <span className="label-caps">{t("context.cycle")}</span>
            <span className="font-mono text-[11px] text-ink">{cycle.cycleStateId}</span>
            <StatusBadge status={mapCycleStateToBadge(cycle.currentState)} label={cycle.currentState} />
          </div>
        </>
      )}

      {stage && (
        <>
          <ChevronRight size={12} className="text-ink-faint" aria-hidden />
          <div className="flex items-center gap-1.5 text-ink-muted">
            <span className="label-caps">{t("context.stage")}</span>
            <span className="font-medium capitalize text-ink">{stage.replace(/-/g, " ")}</span>
          </div>
        </>
      )}

      {project?.hostDefinition && Object.keys(project.hostDefinition).length > 0 && (
        <span className="ml-auto text-ink-faint">
          {String(project.hostDefinition.chassis ?? project.hostDefinition.organism ?? "")}
        </span>
      )}
    </nav>
  );
}

function mapCycleStateToBadge(state: string): import("@/components/common/StatusBadge").BadgeStatus {
  if (/complete/i.test(state)) return "completed";
  if (/wait/i.test(state)) return "waiting_for_human";
  if (/block|pause/i.test(state)) return "blocked";
  return "active";
}
