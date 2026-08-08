import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, useNavigate, useParams } from "react-router-dom";
import { Sparkles } from "lucide-react";
import { createSession, listSessionsForProject } from "@/api/diagnosis";
import { listKnowledgeIdeas } from "@/api/paperExtraction";
import { EmptyState } from "@/components/common/EmptyState";
import { StatusBadge } from "@/components/common/StatusBadge";
import { startAutoDiagnosis } from "@/lib/autoRun";
import { diagnosisStatusToBadge } from "@/lib/workflowStatus";
import { useI18n } from "@/lib/i18n";
import { useProjectContext } from "@/state/useProjectContext";

const ACTOR_ID = "frontend-user";

/** Diagnosis Loop entry point (doc03). The primary action is "诊断": one
 * click drives the full pipeline (session -> hypotheses -> evidence ->
 * ranking -> decision, `startAutoDiagnosis`/`DiagnosisAdapter.start()`),
 * grounded on whichever knowledge-base idea this project's target product
 * already matched (`listKnowledgeIdeas`) rather than an invented
 * phenotype string - a session created this way has real content across
 * every tab of `DiagnosisSessionDetailPage`. The old bare "create an empty
 * session" form is kept as a secondary, explicitly-manual fallback (no
 * content is generated for it - see that page's own hypotheses/tests
 * notes) since the manual per-state action buttons still need *some*
 * session to exist to demonstrate pure state transitions on. */
export function DiagnosisWorkbenchPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const { project } = useProjectContext();
  const { t } = useI18n();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [manualOpen, setManualOpen] = useState(false);
  const [species, setSpecies] = useState("");
  const [strain, setStrain] = useState("");

  const sessionsQuery = useQuery({
    queryKey: ["diagnosis-sessions", projectId],
    queryFn: () => listSessionsForProject(projectId as string),
    enabled: !!projectId,
  });

  const knowledgeIdeasQuery = useQuery({
    queryKey: ["paper-extraction-knowledge-ideas", projectId],
    queryFn: () => listKnowledgeIdeas(projectId),
    enabled: !!projectId,
  });
  const groundingIdea = (knowledgeIdeasQuery.data ?? []).find((i) => i.relevant) ?? null;

  const autoDiagnoseMutation = useMutation({
    mutationFn: () =>
      startAutoDiagnosis(
        projectId as string,
        project?.targetProduct ?? "",
        groundingIdea ? `${groundingIdea.title}: ${groundingIdea.summary}` : undefined,
      ),
    onSuccess: (run) => {
      queryClient.invalidateQueries({ queryKey: ["diagnosis-sessions", projectId] });
      if (run.diagnosisRunRef) navigate(`/projects/${projectId}/diagnosis/${run.diagnosisRunRef}`);
    },
  });

  const createMutation = useMutation({
    mutationFn: () =>
      createSession({
        projectId: projectId as string,
        actorId: ACTOR_ID,
        biologicalSystem: species || strain ? { species, strain } : {},
      }),
    onSuccess: (r) => {
      queryClient.invalidateQueries({ queryKey: ["diagnosis-sessions", projectId] });
      navigate(`/projects/${projectId}/diagnosis/${r.diagnosisSessionId}`);
    },
  });

  return (
    <div className="flex min-h-0 flex-1 flex-col">
      <h1 className="sr-only">{t("diagnosis.title")}</h1>
      <div className="flex min-h-0 flex-1 flex-col overflow-y-auto p-4">
        <div className="mx-auto flex w-full max-w-4xl flex-col gap-4">
          <header>
            <h2 className="text-base font-semibold text-ink">{t("diagnosis.title")}</h2>
            <p className="mt-1 text-sm text-ink-muted">{t("diagnosis.subtitle")}</p>
          </header>

          <section className="panel flex flex-col gap-3 p-4">
            <h3 className="text-sm font-semibold text-ink">{t("diagnosis.oneClick.title")}</h3>
            <p className="text-[11px] text-ink-faint">{t("diagnosis.oneClick.detail")}</p>
            {groundingIdea ? (
              <div className="rounded-lg border border-accent bg-accent-soft/40 p-2.5 text-xs">
                <p className="flex items-center gap-1 font-medium text-accent-strong"><Sparkles size={12} aria-hidden /> {t("diagnosis.oneClick.groundedOn")}</p>
                <p className="mt-1 text-ink-muted">{groundingIdea.title}</p>
              </div>
            ) : (
              !knowledgeIdeasQuery.isLoading && <p className="text-[11px] text-ink-faint">{t("diagnosis.oneClick.noGroundingIdea")}</p>
            )}
            <button
              type="button"
              disabled={autoDiagnoseMutation.isPending}
              onClick={() => autoDiagnoseMutation.mutate()}
              className="w-fit rounded-lg bg-accent px-3 py-1.5 text-xs font-medium text-white disabled:opacity-40"
            >
              {autoDiagnoseMutation.isPending ? t("diagnosis.oneClick.running") : t("diagnosis.oneClick.run")}
            </button>
            {autoDiagnoseMutation.isError && <EmptyState variant="failed" detail={String(autoDiagnoseMutation.error)} />}
          </section>

          <button type="button" onClick={() => setManualOpen((v) => !v)} className="w-fit text-[11px] font-medium text-ink-faint hover:text-ink-muted">
            {manualOpen ? t("diagnosis.newSession.hideManual") : t("diagnosis.newSession.showManual")}
          </button>
          {manualOpen && (
            <section className="panel flex flex-col gap-3 p-4">
              <h3 className="text-sm font-semibold text-ink">{t("diagnosis.newSession.title")}</h3>
              <p className="text-[11px] text-ink-faint">{t("diagnosis.newSession.manualNote")}</p>
              <div className="grid gap-2 sm:grid-cols-2">
                <input
                  value={species}
                  onChange={(e) => setSpecies(e.target.value)}
                  placeholder={t("diagnosis.newSession.species")}
                  className="rounded-lg border border-border px-2.5 py-1.5 text-xs outline-none focus:border-accent"
                />
                <input
                  value={strain}
                  onChange={(e) => setStrain(e.target.value)}
                  placeholder={t("diagnosis.newSession.strain")}
                  className="rounded-lg border border-border px-2.5 py-1.5 text-xs outline-none focus:border-accent"
                />
              </div>
              <button
                type="button"
                disabled={createMutation.isPending}
                onClick={() => createMutation.mutate()}
                className="w-fit rounded-lg border border-border bg-surface px-3 py-1.5 text-xs font-medium text-ink hover:bg-surface-sunken disabled:opacity-40"
              >
                {createMutation.isPending ? t("diagnosis.newSession.creating") : t("diagnosis.newSession.create")}
              </button>
              {createMutation.isError && <EmptyState variant="failed" detail={String(createMutation.error)} />}
            </section>
          )}

          <section className="flex flex-col gap-2">
            <h3 className="label-caps">{t("diagnosis.sessionListTitle")}</h3>
            {sessionsQuery.isLoading && <EmptyState variant="loading" />}
            {sessionsQuery.isError && <EmptyState variant="failed" detail={String(sessionsQuery.error)} />}
            {sessionsQuery.data && sessionsQuery.data.length === 0 && (
              <EmptyState variant="first_use" title={t("diagnosis.noSessionsTitle")} detail={t("diagnosis.noSessionsDetail")} />
            )}
            {sessionsQuery.data && sessionsQuery.data.length > 0 && (
              <ul className="flex flex-col gap-2">
                {sessionsQuery.data.map((s) => {
                  const bio = s.biologicalSystem as { species?: string; strain?: string };
                  return (
                    <li key={s.diagnosisSessionId}>
                      <Link
                        to={`/projects/${projectId}/diagnosis/${s.diagnosisSessionId}`}
                        className="panel flex items-center justify-between gap-2 p-3 text-xs hover:bg-surface-sunken"
                      >
                        <div>
                          <p className="font-mono text-[11px] text-ink-faint">{s.diagnosisSessionId}</p>
                          <p className="mt-0.5 text-ink-muted">
                            {bio?.species ?? t("diagnosis.unspecifiedSystem")}
                            {bio?.strain ? ` · ${bio.strain}` : ""}
                          </p>
                        </div>
                        <StatusBadge status={diagnosisStatusToBadge(s.status)} label={s.status} />
                      </Link>
                    </li>
                  );
                })}
              </ul>
            )}
          </section>
        </div>
      </div>
    </div>
  );
}
