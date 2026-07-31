import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, useNavigate, useParams, useSearchParams } from "react-router-dom";
import { listDesignProjectsForProject } from "@/api/evaluationMetrics";
import { createHandoff } from "@/api/engineeringDesign";
import { EmptyState } from "@/components/common/EmptyState";
import { StatusBadge } from "@/components/common/StatusBadge";
import { designStatusToBadge } from "@/lib/workflowStatus";
import { useI18n } from "@/lib/i18n";

const ACTOR_ID = "frontend-user";

/** Engineering Design Loop entry point (doc04). `POST /handoff` requires
 * an already-gated `diagnosis_decision_id` - there is no way to start a
 * design project without one, by design (Problem 4 is gated on Problem
 * 3's output). The form below either arrives pre-filled from the
 * Diagnosis workbench's "移交到工程设计" action (`?decisionId=`), or
 * accepts a decision id typed in directly for decisions that already
 * exist from an earlier orchestrator run. */
export function DesignWorkbenchPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const { t } = useI18n();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [params] = useSearchParams();

  const [decisionId, setDecisionId] = useState(params.get("decisionId") ?? "");
  const [chassis, setChassis] = useState("");
  const [chassisVersion, setChassisVersion] = useState("unknown");

  const projectsQuery = useQuery({
    queryKey: ["design-projects", projectId],
    queryFn: () => listDesignProjectsForProject(projectId as string),
    enabled: !!projectId,
  });

  const handoffMutation = useMutation({
    mutationFn: () =>
      createHandoff({
        diagnosisDecisionId: decisionId,
        actorId: ACTOR_ID,
        chassis: chassis || undefined,
        chassisVersionOrGenotype: chassisVersion,
      }),
    onSuccess: (r) => {
      queryClient.invalidateQueries({ queryKey: ["design-projects", projectId] });
      navigate(`/projects/${projectId}/design/${r.project.designProjectId}`);
    },
  });

  return (
    <div className="flex min-h-0 flex-1 flex-col">
      <h1 className="sr-only">{t("design.title")}</h1>
      <div className="flex min-h-0 flex-1 flex-col overflow-y-auto p-4">
        <div className="mx-auto flex w-full max-w-4xl flex-col gap-4">
          <header>
            <h2 className="text-base font-semibold text-ink">{t("design.title")}</h2>
            <p className="mt-1 text-sm text-ink-muted">{t("design.subtitle")}</p>
          </header>

          <section className="panel flex flex-col gap-3 p-4">
            <h3 className="text-sm font-semibold text-ink">{t("design.handoff.title")}</h3>
            <p className="text-[11px] text-ink-faint">{t("design.handoff.detail")}</p>
            <div className="grid gap-2 sm:grid-cols-2">
              <input
                value={decisionId}
                onChange={(e) => setDecisionId(e.target.value)}
                placeholder={t("design.handoff.decisionIdPlaceholder")}
                className="rounded-lg border border-border px-2.5 py-1.5 font-mono text-xs outline-none focus:border-accent sm:col-span-2"
              />
              <input
                value={chassis}
                onChange={(e) => setChassis(e.target.value)}
                placeholder={t("design.handoff.chassisPlaceholder")}
                className="rounded-lg border border-border px-2.5 py-1.5 text-xs outline-none focus:border-accent"
              />
              <input
                value={chassisVersion}
                onChange={(e) => setChassisVersion(e.target.value)}
                placeholder={t("design.handoff.chassisVersionPlaceholder")}
                className="rounded-lg border border-border px-2.5 py-1.5 text-xs outline-none focus:border-accent"
              />
            </div>
            <button
              type="button"
              disabled={handoffMutation.isPending || !decisionId.trim()}
              onClick={() => handoffMutation.mutate()}
              className="w-fit rounded-lg bg-accent px-3 py-1.5 text-xs font-medium text-white disabled:opacity-40"
            >
              {handoffMutation.isPending ? t("design.handoff.creating") : t("design.handoff.create")}
            </button>
            {handoffMutation.isError && <EmptyState variant="failed" detail={String(handoffMutation.error)} />}
          </section>

          <section className="flex flex-col gap-2">
            <h3 className="label-caps">{t("design.projectListTitle")}</h3>
            {projectsQuery.isLoading && <EmptyState variant="loading" />}
            {projectsQuery.isError && <EmptyState variant="failed" detail={String(projectsQuery.error)} />}
            {projectsQuery.data && projectsQuery.data.length === 0 && (
              <EmptyState variant="first_use" title={t("design.noProjectsTitle")} detail={t("design.noProjectsDetail")} />
            )}
            {projectsQuery.data && projectsQuery.data.length > 0 && (
              <ul className="flex flex-col gap-2">
                {projectsQuery.data.map((p) => (
                  <li key={p.designProjectId}>
                    <Link
                      to={`/projects/${projectId}/design/${p.designProjectId}`}
                      className="panel flex items-center justify-between gap-2 p-3 text-xs hover:bg-surface-sunken"
                    >
                      <span className="font-mono text-[11px] text-ink-faint">{p.designProjectId}</span>
                      <StatusBadge status={designStatusToBadge(p.status)} label={p.status} />
                    </Link>
                  </li>
                ))}
              </ul>
            )}
          </section>
        </div>
      </div>
    </div>
  );
}
