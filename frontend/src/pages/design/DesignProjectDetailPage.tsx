import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, useParams, useSearchParams } from "react-router-dom";
import { ClipboardList, Lightbulb, Boxes, History, Gauge, Workflow } from "lucide-react";
import {
  confirmObjective, generatePortfolio, generateStrategies, getAuditTrail, getHistory, getProject,
  listCandidates, listHandoffs, listStrategies, markPlanningComplete, markTestPending, requestApproval,
  resolveEvidenceLink, setObjectives, startNextIteration, type CandidateDesign,
  type DesignPrior, type HistoricalPriorSource,
} from "@/api/engineeringDesign";
import { linkIdeaToDesign, listIdeas } from "@/api/ideas";
import { EmptyState } from "@/components/common/EmptyState";
import { StatusBadge } from "@/components/common/StatusBadge";
import { designStatusToBadge, candidateStatusToBadge, strategyStatusToBadge } from "@/lib/workflowStatus";
import { useUrlSelection } from "@/hooks/useUrlSelection";
import { useI18n, type DictKey } from "@/lib/i18n";
import { CandidateDetailDrawer } from "./CandidateDetailDrawer";
import { DesignMetricsTab } from "./DesignMetricsTab";

const ACTOR_ID = "frontend-user";

interface PrimaryMetricRow {
  metric: string;
  unit: string;
}

interface HardConstraintRow {
  type: string;
  constraint: string;
  value?: number;
}

/** Was 5 individually-clickable tabs; consolidated per the same user request
 * (and the same stacked-panel/anchor-nav pattern) as `DiagnosisSessionDetailPage`
 * - "process" is the working loop (set objectives, generate/review strategies
 * & portfolio, read validation metrics), "governance" is the read-only
 * history/audit trail. */
type Tab = "process" | "governance";
const TABS: Tab[] = ["process", "governance"];
const TAB_ICON: Record<Tab, typeof ClipboardList> = { process: Workflow, governance: History };

type Section = "overview" | "strategies" | "portfolio" | "metrics" | "history";
const SECTION_ICON: Record<Section, typeof ClipboardList> = {
  overview: ClipboardList, strategies: Lightbulb, portfolio: Boxes, metrics: Gauge, history: History,
};

export function DesignProjectDetailPage() {
  const { projectId, designProjectId } = useParams<{ projectId: string; designProjectId: string }>();
  const { t } = useI18n();
  const [params, setParams] = useSearchParams();
  const [selectedCandidateId, setSelectedCandidateId] = useUrlSelection("candidate");
  const tabParam = params.get("tab");
  const tab: Tab = TABS.includes(tabParam as Tab) ? (tabParam as Tab) : "process";
  function setTab(next: Tab) {
    const nextParams = new URLSearchParams(params);
    nextParams.set("tab", next);
    setParams(nextParams, { replace: true });
  }

  const projectQuery = useQuery({
    queryKey: ["design-project", designProjectId],
    queryFn: () => getProject(designProjectId as string),
    enabled: !!designProjectId,
  });
  const handoffsQuery = useQuery({
    queryKey: ["design-handoffs", designProjectId],
    queryFn: () => listHandoffs(designProjectId as string),
    enabled: !!designProjectId,
  });

  if (projectQuery.isLoading) return <div className="p-4"><EmptyState variant="loading" /></div>;
  if (projectQuery.isError) return <div className="p-4"><EmptyState variant="failed" detail={String(projectQuery.error)} /></div>;
  if (!projectQuery.data) return <div className="p-4"><EmptyState variant="unavailable" /></div>;
  const project = projectQuery.data;
  const latestHandoff = handoffsQuery.data?.[0] ?? null;

  return (
    <div className="flex min-h-0 flex-1 flex-col">
      <h1 className="sr-only">{t("design.projectTitle")}</h1>
      <div className="flex items-center gap-1 border-b border-border bg-surface px-3 py-2">
        {TABS.map((tb) => (
          <TabButton key={tb} active={tab === tb} onClick={() => setTab(tb)} icon={TAB_ICON[tb]} label={t(`design.page.${tb}` as DictKey)} />
        ))}
      </div>
      <div className="flex min-h-0 flex-1">
        <div className="flex min-h-0 flex-1 flex-col overflow-y-auto p-4">
          <div className="mx-auto flex w-full max-w-4xl flex-col gap-4">
            <header className="flex items-center justify-between gap-2">
              <div>
                <h2 className="font-mono text-sm font-semibold text-ink">{project.designProjectId}</h2>
                <p className="mt-1 text-xs text-ink-muted">{project.chassis} · {project.chassisVersionOrGenotype}</p>
              </div>
              <StatusBadge status={designStatusToBadge(project.status)} label={project.status} />
            </header>

            {tab === "process" && (
              <ProcessPage
                project={project} handoff={latestHandoff} projectId={projectId as string}
                selectedCandidateId={selectedCandidateId} onSelectCandidate={setSelectedCandidateId}
              />
            )}
            {tab === "governance" && <GovernancePage designProjectId={project.designProjectId} />}
          </div>
        </div>
        {selectedCandidateId && (
          <CandidateDetailDrawer
            designId={selectedCandidateId}
            designProjectId={project.designProjectId}
            onClose={() => setSelectedCandidateId(null)}
          />
        )}
      </div>
    </div>
  );
}

function TabButton({ active, onClick, icon: Icon, label }: { active: boolean; onClick: () => void; icon: typeof ClipboardList; label: string }) {
  return (
    <button
      onClick={onClick}
      className={`flex items-center gap-1.5 rounded px-2.5 py-1.5 text-xs font-medium ${
        active ? "bg-accent-soft text-accent-strong" : "text-ink-muted hover:bg-surface-sunken"
      }`}
    >
      <Icon size={13} aria-hidden />
      {label}
    </button>
  );
}

function SectionHeader({ id, section }: { id: Section; section: Section }) {
  const { t } = useI18n();
  const Icon = SECTION_ICON[section];
  return (
    <a id={id} href={`#${id}`} className="group flex scroll-mt-16 items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-ink-faint hover:text-ink-muted">
      <Icon size={13} aria-hidden />
      {t(`design.section.${section}` as DictKey)}
    </a>
  );
}

function SectionNav({ sections }: { sections: Section[] }) {
  const { t } = useI18n();
  return (
    <nav className="sticky top-0 z-10 -mx-4 flex flex-wrap gap-x-3 gap-y-1 border-b border-border bg-surface px-4 py-2 text-[11px]">
      {sections.map((s) => (
        <a key={s} href={`#${s}`} className="text-ink-faint hover:text-accent-strong">{t(`design.section.${s}` as DictKey)}</a>
      ))}
    </nav>
  );
}

function ProcessPage({
  project, handoff, projectId, selectedCandidateId, onSelectCandidate,
}: {
  project: Awaited<ReturnType<typeof getProject>>;
  handoff: Awaited<ReturnType<typeof listHandoffs>>[number] | null;
  projectId: string;
  selectedCandidateId: string | null;
  onSelectCandidate: (id: string | null) => void;
}) {
  const sections: Section[] = ["overview", "strategies", "portfolio", "metrics"];
  return (
    <div className="flex flex-col gap-6">
      <SectionNav sections={sections} />
      <div className="flex flex-col gap-2">
        <SectionHeader id="overview" section="overview" />
        <OverviewTab project={project} handoff={handoff} projectId={projectId} />
      </div>
      <div className="flex flex-col gap-2">
        <SectionHeader id="strategies" section="strategies" />
        <StrategiesTab designProjectId={project.designProjectId} handoffId={handoff?.handoffId ?? null} />
      </div>
      <div className="flex flex-col gap-2">
        <SectionHeader id="portfolio" section="portfolio" />
        <PortfolioTab designProjectId={project.designProjectId} onSelectCandidate={onSelectCandidate} selectedCandidateId={selectedCandidateId} />
      </div>
      <div className="flex flex-col gap-2">
        <SectionHeader id="metrics" section="metrics" />
        <DesignMetricsTab designProjectId={project.designProjectId} referenceDdrIds={project.referenceDdrIds} />
      </div>
    </div>
  );
}

function GovernancePage({ designProjectId }: { designProjectId: string }) {
  return <HistoryTab designProjectId={designProjectId} />;
}

function OverviewTab({
  project, handoff, projectId,
}: {
  project: Awaited<ReturnType<typeof getProject>>;
  handoff: Awaited<ReturnType<typeof listHandoffs>>[number] | null;
  projectId: string;
}) {
  const { t } = useI18n();
  const queryClient = useQueryClient();
  const [primaryMetrics, setPrimaryMetrics] = useState<PrimaryMetricRow[]>([{ metric: "titer", unit: "g/L" }]);
  const [hardConstraints, setHardConstraints] = useState<HardConstraintRow[]>([]);

  function invalidate() {
    queryClient.invalidateQueries({ queryKey: ["design-project", project.designProjectId] });
  }

  const setObjectivesMutation = useMutation({
    mutationFn: () => setObjectives(project.designProjectId, {
      primaryMetrics: primaryMetrics.filter((m) => m.metric.trim()).map((m) => ({ metric: m.metric, unit: m.unit })),
      hardConstraints: hardConstraints.filter((c) => c.constraint.trim()).map((c) => (
        c.type === "max_modifications" ? { constraint: c.constraint, type: c.type, value: c.value } : { constraint: c.constraint, type: c.type }
      )),
      expectedVersion: project.version, actorId: ACTOR_ID,
    }),
    onSuccess: invalidate,
  });
  const confirmMutation = useMutation({
    mutationFn: () => confirmObjective(project.designProjectId, ACTOR_ID),
    onSuccess: invalidate,
  });
  const planningCompleteMutation = useMutation({ mutationFn: () => markPlanningComplete(project.designProjectId, ACTOR_ID), onSuccess: invalidate });
  const requestApprovalMutation = useMutation({ mutationFn: () => requestApproval(project.designProjectId, ACTOR_ID), onSuccess: invalidate });
  const testPendingMutation = useMutation({ mutationFn: () => markTestPending(project.designProjectId, ACTOR_ID), onSuccess: invalidate });
  const nextIterationMutation = useMutation({ mutationFn: () => startNextIteration(project.designProjectId, ACTOR_ID), onSuccess: invalidate });

  return (
    <div className="flex flex-col gap-4">
      <IdeaLinkPanel projectId={projectId} designProjectId={project.designProjectId} />

      <section className="panel flex flex-col gap-2 p-4">
        <h3 className="text-sm font-semibold text-ink">{t("design.overview.handoffTitle")}</h3>
        {handoff ? (
          <div className="text-[11px] text-ink-muted">
            <p className="font-mono text-ink-faint">{handoff.handoffId}</p>
            <p>{t("design.overview.decisionStatus")}: {handoff.decisionStatus} · {handoff.approvedForDesign ? t("design.overview.approvedForDesign") : t("design.overview.notApprovedForDesign")}</p>
            {handoff.isStale && <p className="text-state-caution">{t("design.overview.staleHandoff")}</p>}
          </div>
        ) : (
          <EmptyState variant="unavailable" title={t("design.overview.noHandoffTitle")} />
        )}
      </section>

      {project.status === "objective_draft" && (
        <section className="panel flex flex-col gap-3 p-4">
          <div>
            <h3 className="text-sm font-semibold text-ink">{t("design.overview.objectivesTitle")}</h3>
            <p className="mt-1 text-[11px] text-ink-faint">{t("design.overview.objectivesDetail")}</p>
          </div>

          <div className="flex flex-col gap-1.5">
            <label className="label-caps">{t("design.overview.primaryMetrics")}</label>
            {primaryMetrics.map((m, i) => (
              <div key={i} className="flex items-center gap-2">
                <input
                  value={m.metric}
                  onChange={(e) => setPrimaryMetrics((rows) => rows.map((r, ri) => (ri === i ? { ...r, metric: e.target.value } : r)))}
                  placeholder={t("design.overview.metricNamePlaceholder")}
                  className="flex-1 rounded-lg border border-border px-2.5 py-1.5 text-xs outline-none focus:border-accent"
                />
                <input
                  value={m.unit}
                  onChange={(e) => setPrimaryMetrics((rows) => rows.map((r, ri) => (ri === i ? { ...r, unit: e.target.value } : r)))}
                  placeholder={t("design.overview.metricUnitPlaceholder")}
                  className="w-24 rounded-lg border border-border px-2.5 py-1.5 text-xs outline-none focus:border-accent"
                />
                <button type="button" onClick={() => setPrimaryMetrics((rows) => rows.filter((_, ri) => ri !== i))} className="shrink-0 text-ink-faint hover:text-state-risk">✕</button>
              </div>
            ))}
            <button
              type="button"
              onClick={() => setPrimaryMetrics((rows) => [...rows, { metric: "", unit: "" }])}
              className="w-fit text-[11px] font-medium text-accent-strong hover:underline"
            >
              + {t("design.overview.addMetric")}
            </button>
          </div>

          <div className="flex flex-col gap-1.5">
            <label className="label-caps">{t("design.overview.hardConstraints")}</label>
            {hardConstraints.map((c, i) => (
              <div key={i} className="flex items-center gap-2">
                <select
                  value={c.type}
                  onChange={(e) => setHardConstraints((rows) => rows.map((r, ri) => (ri === i ? { ...r, type: e.target.value } : r)))}
                  className="w-40 shrink-0 rounded-lg border border-border bg-surface px-2 py-1.5 text-xs outline-none"
                >
                  <option value="no_essential_gene_knockout">{t("design.overview.constraintType.no_essential_gene_knockout")}</option>
                  <option value="max_modifications">{t("design.overview.constraintType.max_modifications")}</option>
                  <option value="manual_review">{t("design.overview.constraintType.manual_review")}</option>
                </select>
                <input
                  value={c.constraint}
                  onChange={(e) => setHardConstraints((rows) => rows.map((r, ri) => (ri === i ? { ...r, constraint: e.target.value } : r)))}
                  placeholder={t("design.overview.constraintLabelPlaceholder")}
                  className="flex-1 rounded-lg border border-border px-2.5 py-1.5 text-xs outline-none focus:border-accent"
                />
                {c.type === "max_modifications" && (
                  <input
                    type="number"
                    value={c.value ?? ""}
                    onChange={(e) => setHardConstraints((rows) => rows.map((r, ri) => (ri === i ? { ...r, value: e.target.value === "" ? undefined : Number(e.target.value) } : r)))}
                    placeholder={t("design.overview.constraintValuePlaceholder")}
                    className="w-20 shrink-0 rounded-lg border border-border px-2.5 py-1.5 text-xs outline-none focus:border-accent"
                  />
                )}
                <button type="button" onClick={() => setHardConstraints((rows) => rows.filter((_, ri) => ri !== i))} className="shrink-0 text-ink-faint hover:text-state-risk">✕</button>
              </div>
            ))}
            <button
              type="button"
              onClick={() => setHardConstraints((rows) => [...rows, { type: "no_essential_gene_knockout", constraint: "" }])}
              className="w-fit text-[11px] font-medium text-accent-strong hover:underline"
            >
              + {t("design.overview.addConstraint")}
            </button>
          </div>

          <div className="flex gap-2 border-t border-border pt-2">
            <button type="button" disabled={setObjectivesMutation.isPending} onClick={() => setObjectivesMutation.mutate()} className="w-fit rounded-lg border border-border bg-surface px-3 py-1.5 text-xs font-medium text-ink hover:bg-surface-sunken disabled:opacity-40">
              {t("design.overview.saveObjectives")}
            </button>
            <button type="button" disabled={confirmMutation.isPending} onClick={() => confirmMutation.mutate()} className="w-fit rounded-lg bg-accent px-3 py-1.5 text-xs font-medium text-white disabled:opacity-40">
              {t("design.overview.confirmObjective")}
            </button>
          </div>
          {(setObjectivesMutation.isError || confirmMutation.isError) && (
            <EmptyState variant="failed" detail={String(setObjectivesMutation.error ?? confirmMutation.error)} />
          )}
        </section>
      )}

      <section className="panel flex flex-col gap-2 p-4">
        <h3 className="text-sm font-semibold text-ink">{t("design.overview.actionsTitle")}</h3>
        <div className="flex flex-wrap gap-2">
          {project.status === "portfolio_evaluated" && (
            <ActionButton label={t("design.action.planningComplete")} pending={planningCompleteMutation.isPending} onClick={() => planningCompleteMutation.mutate()} />
          )}
          {project.status === "planning_ready" && (
            <ActionButton label={t("design.action.requestApproval")} pending={requestApprovalMutation.isPending} onClick={() => requestApprovalMutation.mutate()} />
          )}
          {project.status === "build_in_progress" && (
            <ActionButton label={t("design.action.testPending")} pending={testPendingMutation.isPending} onClick={() => testPendingMutation.mutate()} />
          )}
          {(project.status === "learning_update" || project.status === "rejected") && (
            <ActionButton label={t("design.action.nextIteration")} pending={nextIterationMutation.isPending} onClick={() => nextIterationMutation.mutate()} />
          )}
          {!["portfolio_evaluated", "planning_ready", "build_in_progress", "learning_update", "rejected"].includes(project.status) && (
            <EmptyState variant="unavailable" title={t("design.overview.noActionsTitle")} />
          )}
        </div>
      </section>
    </div>
  );
}

function ActionButton({ label, pending, onClick }: { label: string; pending: boolean; onClick: () => void }) {
  return (
    <button type="button" disabled={pending} onClick={onClick} className="rounded-lg border border-border bg-surface px-3 py-1.5 text-xs font-medium text-ink hover:bg-surface-sunken disabled:opacity-40">
      {label}
    </button>
  );
}

/** Surfaces the idea -> scheme traceability chain (`ProjectIdea.
 * linked_design_project_id`, already a real field/endpoint - `harness/
 * ideas/service.py::link_idea_to_design` - just never called from any UI
 * before now). Shows which idea (if any) this design project originated
 * from, and lets a user record that link retroactively when the handoff
 * happened without going through an idea first. */
function IdeaLinkPanel({ projectId, designProjectId }: { projectId: string; designProjectId: string }) {
  const { t } = useI18n();
  const queryClient = useQueryClient();
  const [selectedIdeaId, setSelectedIdeaId] = useState("");

  const ideasQuery = useQuery({
    queryKey: ["project-ideas", projectId, designProjectId],
    queryFn: () => listIdeas(projectId, designProjectId),
  });
  const ideas = ideasQuery.data?.ideas ?? [];
  const recommendedIdeaId = ideasQuery.data?.recommendedIdeaId ?? null;
  const linkedIdea = ideas.find((i) => i.linkedDesignProjectId === designProjectId) ?? null;
  // Ranked by `listIdeas`'s relevance sort when a recommendation was found, so the
  // most likely idea already sorts first - the select is still a manual confirm-
  // click (`link_idea_to_design` stays honest bookkeeping), just pre-suggested.
  const linkableIdeas = ideas.filter((i) => i.status !== "dismissed" && i.linkedDesignProjectId !== designProjectId);
  const effectiveSelectedIdeaId = selectedIdeaId || recommendedIdeaId || "";

  const linkMutation = useMutation({
    mutationFn: () => linkIdeaToDesign(effectiveSelectedIdeaId, { designProjectId, actorId: ACTOR_ID }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["project-ideas", projectId, designProjectId] }),
  });

  return (
    <section className="panel flex flex-col gap-2 p-4">
      <h3 className="text-sm font-semibold text-ink">{t("design.overview.ideaLinkTitle")}</h3>
      {linkedIdea ? (
        <Link to={`/projects/${projectId}/ideas?selected=${encodeURIComponent(linkedIdea.ideaId)}`} className="rounded-lg border border-accent bg-accent-soft/40 p-2.5 text-xs text-accent-strong hover:bg-accent-soft">
          {linkedIdea.freeText}
        </Link>
      ) : !ideasQuery.isLoading && linkableIdeas.length === 0 ? (
        <EmptyState
          variant="first_use"
          title={t("design.overview.noIdeasTitle")}
          detail={t("design.overview.noIdeasDetail")}
          action={
            <Link to={`/projects/${projectId}/ideas`} className="rounded-lg bg-accent px-3 py-1.5 text-xs font-medium text-white hover:opacity-90">
              {t("design.overview.goCaptureIdea")}
            </Link>
          }
        />
      ) : (
        <div className="flex flex-wrap items-center gap-2">
          <select value={effectiveSelectedIdeaId} onChange={(e) => setSelectedIdeaId(e.target.value)} className="min-w-56 flex-1 rounded-lg border border-border bg-surface px-2.5 py-1.5 text-xs outline-none">
            <option value="">{t("design.overview.selectIdeaToLink")}</option>
            {linkableIdeas.map((i) => (
              <option key={i.ideaId} value={i.ideaId}>{i.ideaId === recommendedIdeaId ? `★ ${i.freeText} (${t("design.overview.ideaRecommended")})` : i.freeText}</option>
            ))}
          </select>
          <button
            type="button"
            disabled={linkMutation.isPending || !effectiveSelectedIdeaId}
            onClick={() => linkMutation.mutate()}
            className="rounded-lg bg-accent px-3 py-1.5 text-xs font-medium text-white disabled:opacity-40"
          >
            {linkMutation.isPending ? t("design.overview.linkingIdea") : t("design.overview.linkIdea")}
          </button>
        </div>
      )}
      {linkMutation.isError && <EmptyState variant="failed" detail={String(linkMutation.error)} />}
    </section>
  );
}

function StrategiesTab({ designProjectId, handoffId }: { designProjectId: string; handoffId: string | null }) {
  const { t } = useI18n();
  const queryClient = useQueryClient();
  const strategiesQuery = useQuery({ queryKey: ["design-strategies", designProjectId], queryFn: () => listStrategies(designProjectId) });
  const generateMutation = useMutation({
    mutationFn: () => generateStrategies(designProjectId, handoffId as string, ACTOR_ID),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["design-strategies", designProjectId] }),
  });

  return (
    <section className="flex flex-col gap-3">
      <div className="panel flex items-center justify-between gap-2 p-4">
        <p className="text-[11px] text-ink-faint">{t("design.strategies.detail")}</p>
        <button
          type="button"
          disabled={generateMutation.isPending || !handoffId}
          onClick={() => generateMutation.mutate()}
          className="shrink-0 rounded-lg bg-accent px-3 py-1.5 text-xs font-medium text-white disabled:opacity-40"
        >
          {generateMutation.isPending ? t("design.strategies.generating") : t("design.strategies.generate")}
        </button>
      </div>
      {generateMutation.isError && <EmptyState variant="failed" detail={String(generateMutation.error)} />}
      {strategiesQuery.isLoading && <EmptyState variant="loading" />}
      {strategiesQuery.data && strategiesQuery.data.length === 0 && <EmptyState variant="first_use" title={t("design.strategies.emptyTitle")} />}
      {strategiesQuery.data && strategiesQuery.data.length > 0 && (
        <ul className="flex flex-col gap-2">
          {strategiesQuery.data.map((s) => (
            <li key={s.strategyId} className="panel flex flex-col gap-1 p-3 text-xs">
              <div className="flex items-start justify-between gap-2">
                <p className="font-medium text-ink">{s.engineeringObjective}</p>
                <StatusBadge status={strategyStatusToBadge(s.status)} label={s.status} />
              </div>
              <p className="text-ink-faint">{s.strategyClass} · {t("design.strategies.mechanismTarget")}: {s.mechanismTarget}</p>
              {s.rationale && <p className="text-ink-muted">{s.rationale}</p>}
              {s.designPrior && <HistoricalPriorBadge prior={s.designPrior} sources={s.historicalPriors} />}
              {s.evidenceLinks.length > 0 && <EvidenceLinksInline links={s.evidenceLinks} />}
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}

function EvidenceLinksInline({ links }: { links: Array<{ source_type: string; reference: string; detail?: string }> }) {
  const { t } = useI18n();
  const [resolved, setResolved] = useState<Record<number, string>>({});
  const resolveMutation = useMutation({
    mutationFn: (input: { index: number; link: { source_type: string; reference: string; detail?: string } }) =>
      resolveEvidenceLink(input.link.source_type, input.link.reference, input.link.detail ?? ""),
  });
  return (
    <div className="flex flex-wrap gap-1.5 border-t border-border pt-1.5">
      {links.map((l, i) => (
        <button
          key={i}
          type="button"
          onClick={async () => {
            const r = await resolveMutation.mutateAsync({ index: i, link: l });
            setResolved((prev) => ({ ...prev, [i]: `${r.title} — ${r.note}` }));
          }}
          title={resolved[i] ?? t("design.strategies.resolveEvidence")}
          className="rounded border border-border bg-surface px-1.5 py-0.5 font-mono text-[10px] text-ink-muted hover:bg-surface-sunken"
        >
          {l.reference}
        </button>
      ))}
    </div>
  );
}

// ELISER-inspired historical design memory (harness/engineering_design/
// strategy_prior_retrieval.py): a design_prior score of 0 with an empty
// supporting-source list is an honest "no historical precedent found"
// result, not a loading/error state - always rendered, never hidden.
function HistoricalPriorBadge({ prior, sources }: { prior: DesignPrior; sources: HistoricalPriorSource[] }) {
  const { t } = useI18n();
  const [expanded, setExpanded] = useState(false);
  return (
    <div className="border-t border-border pt-1.5">
      <button
        type="button"
        onClick={() => setExpanded((v) => !v)}
        className="flex items-center gap-1.5 rounded border border-border bg-surface px-1.5 py-0.5 text-[10px] text-ink-muted hover:bg-surface-sunken"
        title={t("design.strategies.historicalPriorHint")}
      >
        <History size={11} />
        {t("design.strategies.historicalPrior")}: {prior.score.toFixed(2)} ({prior.historical_frequency})
      </button>
      {expanded && (
        <ul className="mt-1.5 flex flex-col gap-1 pl-1">
          {sources.length === 0 && <li className="text-[10px] text-ink-faint">{t("design.strategies.noHistoricalPrior")}</li>}
          {sources.map((src, i) => (
            <li key={i} className="text-[10px] text-ink-faint">
              <span className="font-mono">{src.source_id}</span> [{src.evidence_grading}] — {src.basis_quote}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

function PortfolioTab({
  designProjectId, onSelectCandidate, selectedCandidateId,
}: {
  designProjectId: string;
  onSelectCandidate: (id: string | null) => void;
  selectedCandidateId: string | null;
}) {
  const { t } = useI18n();
  const queryClient = useQueryClient();
  const candidatesQuery = useQuery({ queryKey: ["design-candidates", designProjectId], queryFn: () => listCandidates(designProjectId) });
  const generateMutation = useMutation({
    mutationFn: () => generatePortfolio(designProjectId, ACTOR_ID),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["design-candidates", designProjectId] }),
  });

  const grouped = new Map<string, CandidateDesign[]>();
  for (const c of candidatesQuery.data ?? []) {
    const role = c.portfolioRole ?? "unassigned";
    grouped.set(role, [...(grouped.get(role) ?? []), c]);
  }

  return (
    <section className="flex flex-col gap-3">
      <div className="panel flex items-center justify-between gap-2 p-4">
        <p className="text-[11px] text-ink-faint">{t("design.portfolio.detail")}</p>
        <button
          type="button"
          disabled={generateMutation.isPending}
          onClick={() => generateMutation.mutate()}
          className="shrink-0 rounded-lg bg-accent px-3 py-1.5 text-xs font-medium text-white disabled:opacity-40"
        >
          {generateMutation.isPending ? t("design.portfolio.generating") : t("design.portfolio.generate")}
        </button>
      </div>
      {generateMutation.isError && <EmptyState variant="failed" detail={String(generateMutation.error)} />}
      {candidatesQuery.isLoading && <EmptyState variant="loading" />}
      {candidatesQuery.data && candidatesQuery.data.length === 0 && <EmptyState variant="first_use" title={t("design.portfolio.emptyTitle")} />}
      {[...grouped.entries()].map(([role, candidates]) => (
        <div key={role} className="flex flex-col gap-2">
          <h4 className="label-caps">{role}</h4>
          <div className="grid gap-2 sm:grid-cols-2">
            {candidates.map((c) => (
              <button
                key={c.designId}
                type="button"
                onClick={() => onSelectCandidate(c.designId)}
                className={`panel flex flex-col gap-1 p-3 text-left text-xs hover:bg-surface-sunken ${selectedCandidateId === c.designId ? "border-accent" : ""}`}
              >
                <div className="flex items-center justify-between gap-2">
                  <span className="font-mono text-[11px] text-ink-faint">{c.designId}</span>
                  <StatusBadge status={candidateStatusToBadge(c.status)} label={c.status} />
                </div>
                <p className="text-ink-muted">{c.expectedMechanism || t("design.portfolio.noMechanism")}</p>
                <p className="text-[10px] text-ink-faint">{t("design.portfolio.readiness")}: {c.readiness}</p>
              </button>
            ))}
          </div>
        </div>
      ))}
    </section>
  );
}

function HistoryTab({ designProjectId }: { designProjectId: string }) {
  const { t } = useI18n();
  const historyQuery = useQuery({ queryKey: ["design-history", designProjectId], queryFn: () => getHistory(designProjectId) });
  const auditQuery = useQuery({ queryKey: ["design-audit", designProjectId], queryFn: () => getAuditTrail(designProjectId) });

  return (
    <section className="flex flex-col gap-4">
      <div className="panel flex flex-col gap-2 p-4">
        <h3 className="text-sm font-semibold text-ink">{t("design.history.transitionsTitle")}</h3>
        {auditQuery.isLoading && <EmptyState variant="loading" />}
        {auditQuery.data && auditQuery.data.length === 0 && <EmptyState variant="first_use" />}
        {auditQuery.data && auditQuery.data.length > 0 && (
          <ul className="flex flex-col gap-1 text-[11px]">
            {auditQuery.data.map((tr, i) => (
              <li key={i} className="flex items-center justify-between rounded border border-border px-2 py-1">
                <span>{tr.state} {tr.selectedNextState ? `→ ${tr.selectedNextState}` : ""}</span>
                <span className="text-ink-faint">{new Date(tr.startedAt * 1000).toLocaleString()}</span>
              </li>
            ))}
          </ul>
        )}
      </div>
      <div className="panel flex flex-col gap-2 p-4">
        <h3 className="text-sm font-semibold text-ink">{t("design.history.lineageTitle")}</h3>
        {historyQuery.isLoading && <EmptyState variant="loading" />}
        {historyQuery.data && historyQuery.data.length === 0 && <EmptyState variant="first_use" />}
        {historyQuery.data && historyQuery.data.length > 0 && (
          <pre className="overflow-x-auto whitespace-pre-wrap rounded bg-surface-sunken p-2 text-[11px] text-ink-muted">
            {JSON.stringify(historyQuery.data, null, 2)}
          </pre>
        )}
      </div>
    </section>
  );
}
