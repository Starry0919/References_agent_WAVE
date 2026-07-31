import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useParams, useSearchParams } from "react-router-dom";
import { ClipboardList, Lightbulb, Boxes, History } from "lucide-react";
import {
  confirmObjective, generatePortfolio, generateStrategies, getAuditTrail, getHistory, getProject,
  listCandidates, listHandoffs, listStrategies, markPlanningComplete, markTestPending, requestApproval,
  resolveEvidenceLink, setObjectives, startNextIteration, type CandidateDesign,
} from "@/api/engineeringDesign";
import { EmptyState } from "@/components/common/EmptyState";
import { StatusBadge } from "@/components/common/StatusBadge";
import { designStatusToBadge, candidateStatusToBadge, strategyStatusToBadge } from "@/lib/workflowStatus";
import { useUrlSelection } from "@/hooks/useUrlSelection";
import { useI18n, type DictKey } from "@/lib/i18n";
import { CandidateDetailDrawer } from "./CandidateDetailDrawer";

const ACTOR_ID = "frontend-user";

type Tab = "overview" | "strategies" | "portfolio" | "history";
const TABS: Tab[] = ["overview", "strategies", "portfolio", "history"];
const TAB_ICON: Record<Tab, typeof ClipboardList> = { overview: ClipboardList, strategies: Lightbulb, portfolio: Boxes, history: History };

export function DesignProjectDetailPage() {
  const { designProjectId } = useParams<{ projectId: string; designProjectId: string }>();
  const { t } = useI18n();
  const [params, setParams] = useSearchParams();
  const [selectedCandidateId, setSelectedCandidateId] = useUrlSelection("candidate");
  const tabParam = params.get("tab");
  const tab: Tab = TABS.includes(tabParam as Tab) ? (tabParam as Tab) : "overview";
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
          <TabButton key={tb} active={tab === tb} onClick={() => setTab(tb)} icon={TAB_ICON[tb]} label={t(`design.tab.${tb}` as DictKey)} />
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

            {tab === "overview" && <OverviewTab project={project} handoff={latestHandoff} />}
            {tab === "strategies" && <StrategiesTab designProjectId={project.designProjectId} handoffId={latestHandoff?.handoffId ?? null} />}
            {tab === "portfolio" && (
              <PortfolioTab designProjectId={project.designProjectId} onSelectCandidate={setSelectedCandidateId} selectedCandidateId={selectedCandidateId} />
            )}
            {tab === "history" && <HistoryTab designProjectId={project.designProjectId} />}
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

function OverviewTab({ project, handoff }: { project: Awaited<ReturnType<typeof getProject>>; handoff: Awaited<ReturnType<typeof listHandoffs>>[number] | null }) {
  const { t } = useI18n();
  const queryClient = useQueryClient();
  const [primaryMetricsText, setPrimaryMetricsText] = useState('[{"metric": "titer", "unit": "g/L"}]');
  const [hardConstraintsText, setHardConstraintsText] = useState("[]");

  function invalidate() {
    queryClient.invalidateQueries({ queryKey: ["design-project", project.designProjectId] });
  }

  const setObjectivesMutation = useMutation({
    mutationFn: () => {
      let primaryMetrics: unknown[]; let hardConstraints: unknown[];
      try {
        primaryMetrics = JSON.parse(primaryMetricsText);
        hardConstraints = JSON.parse(hardConstraintsText);
      } catch {
        throw new Error(t("design.overview.invalidJson"));
      }
      return setObjectives(project.designProjectId, { primaryMetrics, hardConstraints, expectedVersion: project.version, actorId: ACTOR_ID });
    },
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
        <section className="panel flex flex-col gap-2 p-4">
          <h3 className="text-sm font-semibold text-ink">{t("design.overview.objectivesTitle")}</h3>
          <p className="text-[11px] text-ink-faint">{t("design.overview.objectivesDetail")}</p>
          <label className="label-caps">{t("design.overview.primaryMetrics")}</label>
          <textarea value={primaryMetricsText} onChange={(e) => setPrimaryMetricsText(e.target.value)} rows={3} className="rounded-lg border border-border px-2.5 py-1.5 font-mono text-[11px] outline-none focus:border-accent" />
          <label className="label-caps">{t("design.overview.hardConstraints")}</label>
          <textarea value={hardConstraintsText} onChange={(e) => setHardConstraintsText(e.target.value)} rows={3} className="rounded-lg border border-border px-2.5 py-1.5 font-mono text-[11px] outline-none focus:border-accent" />
          <div className="flex gap-2">
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
