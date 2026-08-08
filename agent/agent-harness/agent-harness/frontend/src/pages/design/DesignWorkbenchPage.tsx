import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, useNavigate, useParams, useSearchParams } from "react-router-dom";
import { listDesignProjectsForProject } from "@/api/evaluationMetrics";
import { createHandoff } from "@/api/engineeringDesign";
import { listDecisions, listHypotheses, listSessionsForProject } from "@/api/diagnosis";
import { linkIdeaToDesign, listIdeas } from "@/api/ideas";
import { EmptyState } from "@/components/common/EmptyState";
import { StatusBadge } from "@/components/common/StatusBadge";
import { designStatusToBadge } from "@/lib/workflowStatus";
import { useI18n } from "@/lib/i18n";

const ACTOR_ID = "frontend-user";

export interface DecisionOption {
  decisionId: string;
  sessionId: string;
  summary: string;
}

/** One decision per diagnosis session, reduced to a single readable
 * sentence (leading hypothesis statement + stopping reason, falling back
 * to stopping/next-action alone when no hypothesis text is available) -
 * this is what fills the decision picker below instead of making a user
 * hunt for a raw `decision_id` in another tab. */
async function loadDecisionOptions(projectId: string): Promise<DecisionOption[]> {
  const sessions = await listSessionsForProject(projectId);
  const options: DecisionOption[] = [];
  for (const s of sessions) {
    const [decisions, hypotheses] = await Promise.all([listDecisions(s.diagnosisSessionId), listHypotheses(s.diagnosisSessionId)]);
    const hypById = new Map(hypotheses.map((h) => [h.hypothesisVersionId, h]));
    for (const d of decisions) {
      const leadStatement = d.leadingHypothesisIds.map((id) => hypById.get(id)?.statement).find(Boolean);
      const summary = leadStatement
        ? `${leadStatement}（${d.stoppingReason}）`
        : `${d.stoppingReason} · ${d.allowedNextAction}`;
      options.push({ decisionId: d.decisionId, sessionId: s.diagnosisSessionId, summary });
    }
  }
  return options;
}

/** Engineering Design Loop entry point (doc04). `POST /handoff` requires
 * an already-gated `diagnosis_decision_id` - there is no way to start a
 * design project without one, by design (Problem 4 is gated on Problem
 * 3's output). The "诊断决策选择器" below lets a user pick from real
 * decisions (each reduced to one auto-generated sentence) instead of
 * copy-pasting a raw id; picking one or more auto-fills a create row per
 * pick (multi-select => multiple rows, one handoff each). A raw decision
 * id can still be typed in directly when nothing is selected, for
 * decisions from an earlier orchestrator run this project's own sessions
 * don't surface. */
export function DesignWorkbenchPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const { t } = useI18n();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [params] = useSearchParams();

  const [manualDecisionId, setManualDecisionId] = useState(params.get("decisionId") ?? "");
  const [selectedDecisionIds, setSelectedDecisionIds] = useState<string[]>([]);
  const [chassis, setChassis] = useState("E. coli");
  const [chassisVersion, setChassisVersion] = useState("K-12");
  const [ideaId, setIdeaId] = useState(params.get("ideaId") ?? "");

  const projectsQuery = useQuery({
    queryKey: ["design-projects", projectId],
    queryFn: () => listDesignProjectsForProject(projectId as string),
    enabled: !!projectId,
  });
  const decisionOptionsQuery = useQuery({
    queryKey: ["diagnosis-decision-options", projectId],
    queryFn: () => loadDecisionOptions(projectId as string),
    enabled: !!projectId,
  });
  const ideasQuery = useQuery({
    queryKey: ["project-ideas", projectId],
    queryFn: () => listIdeas(projectId as string),
    enabled: !!projectId,
  });
  const linkableIdeas = (ideasQuery.data?.ideas ?? []).filter((i) => i.status !== "dismissed" && !i.linkedDesignProjectId);
  const ideaByDesignProjectId = new Map((ideasQuery.data?.ideas ?? []).filter((i) => i.linkedDesignProjectId).map((i) => [i.linkedDesignProjectId as string, i]));

  function toggleDecision(decisionId: string) {
    setSelectedDecisionIds((prev) => (prev.includes(decisionId) ? prev.filter((id) => id !== decisionId) : [...prev, decisionId]));
  }

  const handoffMutation = useMutation({
    mutationFn: async (diagnosisDecisionId: string) => {
      const result = await createHandoff({
        diagnosisDecisionId,
        actorId: ACTOR_ID,
        chassis: chassis || undefined,
        chassisVersionOrGenotype: chassisVersion,
      });
      if (ideaId) await linkIdeaToDesign(ideaId, { designProjectId: result.project.designProjectId, actorId: ACTOR_ID });
      return result;
    },
    onSuccess: (r) => {
      queryClient.invalidateQueries({ queryKey: ["design-projects", projectId] });
      queryClient.invalidateQueries({ queryKey: ["project-ideas", projectId] });
      navigate(`/projects/${projectId}/design/${r.project.designProjectId}`);
    },
  });

  const hasPickedDecisions = selectedDecisionIds.length > 0;

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

            <div className="flex flex-col gap-1.5">
              <h4 className="label-caps">{t("design.handoff.decisionPickerTitle")}</h4>
              <p className="text-[11px] text-ink-faint">{t("design.handoff.decisionPickerDetail")}</p>
              {decisionOptionsQuery.isLoading && <EmptyState variant="loading" />}
              {decisionOptionsQuery.data && decisionOptionsQuery.data.length === 0 && (
                <p className="text-[11px] text-ink-faint">{t("design.handoff.noDecisionsYet")}</p>
              )}
              {decisionOptionsQuery.data && decisionOptionsQuery.data.length > 0 && (
                <ul className="flex flex-col gap-1.5">
                  {decisionOptionsQuery.data.map((opt) => (
                    <li key={opt.decisionId}>
                      <label className="flex cursor-pointer items-start gap-2 rounded-lg border border-border p-2 text-xs hover:bg-surface-sunken">
                        <input
                          type="checkbox"
                          className="mt-0.5"
                          checked={selectedDecisionIds.includes(opt.decisionId)}
                          onChange={() => toggleDecision(opt.decisionId)}
                        />
                        <span className="text-ink-muted">{opt.summary}</span>
                      </label>
                    </li>
                  ))}
                </ul>
              )}
            </div>

            <div className="grid gap-2 border-t border-border pt-3 sm:grid-cols-2">
              {!hasPickedDecisions && (
                <input
                  value={manualDecisionId}
                  onChange={(e) => setManualDecisionId(e.target.value)}
                  placeholder={t("design.handoff.decisionIdPlaceholder")}
                  className="rounded-lg border border-border px-2.5 py-1.5 font-mono text-xs outline-none focus:border-accent sm:col-span-2"
                />
              )}
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
              <select
                value={ideaId}
                onChange={(e) => setIdeaId(e.target.value)}
                className="rounded-lg border border-border bg-surface px-2.5 py-1.5 text-xs outline-none sm:col-span-2"
              >
                <option value="">{t("design.handoff.noIdeaToLink")}</option>
                {linkableIdeas.map((i) => (
                  <option key={i.ideaId} value={i.ideaId}>{i.freeText}</option>
                ))}
              </select>
            </div>

            {hasPickedDecisions ? (
              <div className="flex flex-col gap-2">
                {selectedDecisionIds.map((decisionId) => {
                  const opt = decisionOptionsQuery.data?.find((o) => o.decisionId === decisionId);
                  return (
                    <div key={decisionId} className="flex items-center justify-between gap-2 rounded-lg border border-accent bg-accent-soft/30 p-2.5 text-xs">
                      <div className="min-w-0">
                        <p className="truncate font-mono text-[11px] text-ink-faint">{decisionId}</p>
                        {opt && <p className="mt-0.5 truncate text-ink-muted">{opt.summary}</p>}
                      </div>
                      <button
                        type="button"
                        disabled={handoffMutation.isPending}
                        onClick={() => handoffMutation.mutate(decisionId)}
                        className="shrink-0 rounded-lg bg-accent px-3 py-1.5 text-xs font-medium text-white disabled:opacity-40"
                      >
                        {t("design.handoff.create")}
                      </button>
                    </div>
                  );
                })}
              </div>
            ) : (
              <button
                type="button"
                disabled={handoffMutation.isPending || !manualDecisionId.trim()}
                onClick={() => handoffMutation.mutate(manualDecisionId)}
                className="w-fit rounded-lg bg-accent px-3 py-1.5 text-xs font-medium text-white disabled:opacity-40"
              >
                {handoffMutation.isPending ? t("design.handoff.creating") : t("design.handoff.create")}
              </button>
            )}
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
                {projectsQuery.data.map((p) => {
                  const idea = ideaByDesignProjectId.get(p.designProjectId);
                  return (
                    <li key={p.designProjectId}>
                      <Link
                        to={`/projects/${projectId}/design/${p.designProjectId}`}
                        className="panel flex items-center justify-between gap-2 p-3 text-xs hover:bg-surface-sunken"
                      >
                        <div>
                          <span className="font-mono text-[11px] text-ink-faint">{p.designProjectId}</span>
                          {idea && <p className="mt-0.5 text-ink-muted">{idea.freeText}</p>}
                        </div>
                        <StatusBadge status={designStatusToBadge(p.status)} label={p.status} />
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
