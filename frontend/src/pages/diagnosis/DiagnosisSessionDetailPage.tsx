import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useNavigate, useParams, useSearchParams } from "react-router-dom";
import {
  ClipboardList, Lightbulb, BookOpen, Cpu, TestTube2, Gavel, History, Workflow, Plus, GitBranch,
} from "lucide-react";
import {
  approveDecision, createEvidenceItem, getAuditTrail, getMechanismGraph, getObservationGrounding, getReport, getSession, linkEvidence,
  listEngineeringProblems,
  listDecisions, listEvidence, listEvidenceItems, listHypotheses, listModelCapabilities, listTests, reviewEvidenceLink,
  runModel, sessionAction, DIAGNOSIS_SESSION_ACTIONS, type DiagnosisSessionAction,
} from "@/api/diagnosis";
import { EmptyState } from "@/components/common/EmptyState";
import { StatusBadge } from "@/components/common/StatusBadge";
import { diagnosisStatusToBadge } from "@/lib/workflowStatus";
import { useI18n, type DictKey } from "@/lib/i18n";

const ACTOR_ID = "frontend-user";

/** Which `status` values each pure state-transition action is legal from -
 * mirrors `DiagnosisLoopController`'s own `from_states` (harness/diagnosis/
 * loop.py) so the UI only ever offers actions the backend will accept,
 * instead of surfacing a wall of buttons that mostly 409. */
const ACTION_FROM_STATES: Record<DiagnosisSessionAction, string[]> = {
  mark_hypotheses_generated: ["observations_normalized"],
  mark_evidence_assessed: ["hypotheses_generated"],
  mark_model_evidence_pending: ["evidence_assessed"],
  mark_hypotheses_ranked: ["evidence_assessed", "model_evidence_pending", "model_conflicted"],
  enter_model_conflicted: ["model_evidence_pending", "hypotheses_ranked"],
  enter_test_selection_required: ["hypotheses_ranked"],
  select_test: ["test_selection_required"],
  enter_awaiting_test_result: ["test_planned"],
  ingest_test_result_and_update_belief: ["awaiting_test_result"],
  resolve_human_review: ["human_review_required"],
  reopen_diagnosis: ["evidence_limited", "closed", "handed_off_to_design"],
  close_diagnosis: ["evidence_limited", "actionable", "handed_off_to_design", "human_review_required"],
};

/** Was 7 individually-clickable tabs (one section visible at a time); consolidated per
 * user request into 2 pages so each groups its sections as stacked, scrollable panels
 * instead of hiding them behind further tab clicks - "process" is the working loop
 * (act on the session, review hypotheses/evidence, run models/tests), "governance" is
 * the output side (approve decisions, read the audit trail/report). */
type Tab = "process" | "governance";
const TABS: Tab[] = ["process", "governance"];
const TAB_ICON: Record<Tab, typeof ClipboardList> = { process: Workflow, governance: Gavel };

type Section = "overview" | "hypotheses" | "mechanismGraph" | "evidence" | "models" | "tests" | "decisions" | "audit";
const SECTION_ICON: Record<Section, typeof ClipboardList> = {
  overview: ClipboardList, hypotheses: Lightbulb, mechanismGraph: GitBranch, evidence: BookOpen, models: Cpu,
  tests: TestTube2, decisions: Gavel, audit: History,
};

export function DiagnosisSessionDetailPage() {
  const { projectId, sessionId } = useParams<{ projectId: string; sessionId: string }>();
  const { t } = useI18n();
  const [params, setParams] = useSearchParams();
  const tabParam = params.get("tab");
  const tab: Tab = TABS.includes(tabParam as Tab) ? (tabParam as Tab) : "process";
  function setTab(next: Tab) {
    const nextParams = new URLSearchParams(params);
    nextParams.set("tab", next);
    setParams(nextParams, { replace: true });
  }

  const sessionQuery = useQuery({
    queryKey: ["diagnosis-session", sessionId],
    queryFn: () => getSession(sessionId as string),
    enabled: !!sessionId,
  });
  const hypothesesQuery = useQuery({
    queryKey: ["diagnosis-hypotheses", sessionId],
    queryFn: () => listHypotheses(sessionId as string),
    enabled: !!sessionId,
  });

  if (sessionQuery.isLoading) return <div className="p-4"><EmptyState variant="loading" /></div>;
  if (sessionQuery.isError) return <div className="p-4"><EmptyState variant="failed" detail={String(sessionQuery.error)} /></div>;
  if (!sessionQuery.data) return <div className="p-4"><EmptyState variant="unavailable" /></div>;
  const session = sessionQuery.data;

  return (
    <div className="flex min-h-0 flex-1 flex-col">
      <h1 className="sr-only">{t("diagnosis.sessionTitle")}</h1>
      <div className="flex items-center gap-1 border-b border-border bg-surface px-3 py-2">
        {TABS.map((tb) => (
          <TabButton key={tb} active={tab === tb} onClick={() => setTab(tb)} icon={TAB_ICON[tb]} label={t(`diagnosis.page.${tb}` as DictKey)} />
        ))}
      </div>
      <div className="flex min-h-0 flex-1 flex-col overflow-y-auto p-4">
        <div className="mx-auto flex w-full max-w-4xl flex-col gap-4">
          <header className="flex items-center justify-between gap-2">
            <div>
              <h2 className="font-mono text-sm font-semibold text-ink">{session.diagnosisSessionId}</h2>
              <p className="mt-1 text-xs text-ink-muted">
                {t("diagnosis.dataSufficiency")}: {session.dataSufficiency} · {t("diagnosis.approvalState")}: {session.approvalState}
              </p>
            </div>
            <StatusBadge status={diagnosisStatusToBadge(session.status)} label={session.status} />
          </header>

          {tab === "process" && (
            <ProcessPage
              projectId={projectId as string}
              sessionId={session.diagnosisSessionId}
              status={session.status}
              hypotheses={hypothesesQuery.data}
              hypothesesLoading={hypothesesQuery.isLoading}
              hypothesesError={hypothesesQuery.isError}
              hypothesesErrorDetail={hypothesesQuery.error}
            />
          )}
          {tab === "governance" && <GovernancePage projectId={projectId as string} sessionId={session.diagnosisSessionId} />}
        </div>
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
      {t(`diagnosis.section.${section}` as DictKey)}
    </a>
  );
}

function SectionNav({ sections }: { sections: Section[] }) {
  const { t } = useI18n();
  return (
    <nav className="sticky top-0 z-10 -mx-4 flex flex-wrap gap-x-3 gap-y-1 border-b border-border bg-surface px-4 py-2 text-[11px]">
      {sections.map((s) => (
        <a key={s} href={`#${s}`} className="text-ink-faint hover:text-accent-strong">{t(`diagnosis.section.${s}` as DictKey)}</a>
      ))}
    </nav>
  );
}

function ProcessPage({
  projectId, sessionId, status, hypotheses, hypothesesLoading, hypothesesError, hypothesesErrorDetail,
}: {
  projectId: string;
  sessionId: string;
  status: string;
  hypotheses: Awaited<ReturnType<typeof listHypotheses>> | undefined;
  hypothesesLoading: boolean;
  hypothesesError: boolean;
  hypothesesErrorDetail: unknown;
}) {
  const sections: Section[] = ["overview", "hypotheses", "mechanismGraph", "evidence", "models", "tests"];
  const evidenceQuery = useQuery({ queryKey: ["diagnosis-evidence", sessionId], queryFn: () => listEvidence(sessionId) });
  const evidenceByHypothesis = new Map<string, Awaited<ReturnType<typeof listEvidence>>>();
  for (const e of evidenceQuery.data ?? []) {
    evidenceByHypothesis.set(e.hypothesisVersionId, [...(evidenceByHypothesis.get(e.hypothesisVersionId) ?? []), e]);
  }
  return (
    <div className="flex flex-col gap-6">
      <SectionNav sections={sections} />
      <div className="flex flex-col gap-2">
        <SectionHeader id="overview" section="overview" />
        <OverviewTab sessionId={sessionId} status={status} />
      </div>
      <div className="flex flex-col gap-2">
        <SectionHeader id="hypotheses" section="hypotheses" />
        <HypothesesTab
          sessionId={sessionId} hypotheses={hypotheses} isLoading={hypothesesLoading} isError={hypothesesError} error={hypothesesErrorDetail}
          evidenceByHypothesis={evidenceByHypothesis}
        />
      </div>
      <div className="flex flex-col gap-2">
        <SectionHeader id="mechanismGraph" section="mechanismGraph" />
        <MechanismGraphTab sessionId={sessionId} />
      </div>
      <div className="flex flex-col gap-2">
        <SectionHeader id="evidence" section="evidence" />
        <EvidenceTab projectId={projectId} sessionId={sessionId} hypotheses={hypotheses ?? []} />
      </div>
      <div className="flex flex-col gap-2">
        <SectionHeader id="models" section="models" />
        <ModelRunsTab projectId={projectId} sessionId={sessionId} />
      </div>
      <div className="flex flex-col gap-2">
        <SectionHeader id="tests" section="tests" />
        <TestsTab sessionId={sessionId} />
      </div>
    </div>
  );
}

function GovernancePage({ projectId, sessionId }: { projectId: string; sessionId: string }) {
  const sections: Section[] = ["decisions", "audit"];
  return (
    <div className="flex flex-col gap-6">
      <SectionNav sections={sections} />
      <div className="flex flex-col gap-2">
        <SectionHeader id="decisions" section="decisions" />
        <DecisionsTab projectId={projectId} sessionId={sessionId} />
      </div>
      <div className="flex flex-col gap-2">
        <SectionHeader id="audit" section="audit" />
        <AuditReportTab sessionId={sessionId} />
      </div>
    </div>
  );
}

function OverviewTab({ sessionId, status }: { sessionId: string; status: string }) {
  const { t } = useI18n();
  const queryClient = useQueryClient();
  const [resolution, setResolution] = useState("hypotheses_ranked");
  const [reason, setReason] = useState("");
  const groundingQuery = useQuery({ queryKey: ["diagnosis-grounding", sessionId], queryFn: () => getObservationGrounding(sessionId) });
  const problemsQuery = useQuery({ queryKey: ["diagnosis-engineering-problems", sessionId], queryFn: () => listEngineeringProblems(sessionId) });

  const availableActions = DIAGNOSIS_SESSION_ACTIONS.filter((a) => ACTION_FROM_STATES[a].includes(status));

  const actionMutation = useMutation({
    mutationFn: (input: { action: DiagnosisSessionAction; kwargs?: Record<string, unknown> }) =>
      sessionAction(sessionId, input.action, ACTOR_ID, input.kwargs ?? {}),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["diagnosis-session", sessionId] });
      queryClient.invalidateQueries({ queryKey: ["diagnosis-audit", sessionId] });
    },
  });

  return (
    <div className="flex flex-col gap-3">
    <section className="panel flex flex-col gap-3 p-4" aria-label="Observation grounding">
      <div className="flex items-center justify-between gap-3"><div><h3 className="text-sm font-semibold text-ink">Observation grounding</h3><p className="text-[11px] text-ink-faint">Measured Observation → Engineering Problem → Hypothesis</p></div><StatusBadge status={groundingQuery.data?.actionable ? "approved" : "blocked"} label={groundingQuery.data?.actionable ? "GROUNDED" : "DATA REQUIRED"} /></div>
      {(groundingQuery.data?.blockingReasons ?? []).length > 0 && <ul className="list-disc space-y-1 pl-5 text-xs text-amber-800">{groundingQuery.data?.blockingReasons.map((r) => <li key={r}>{r}</li>)}</ul>}
      {(problemsQuery.data ?? []).map((p) => <div key={p.engineeringProblemId} className="grid gap-2 rounded border border-border bg-surface-sunken p-3 sm:grid-cols-3"><div><p className="text-[10px] font-bold uppercase text-ink-faint">Measured observation</p><p className="text-sm">{p.metric}: {p.observedValue} {p.unit}</p><p className="text-[11px] text-ink-muted">Baseline: {p.expectedValue} {p.unit}; difference: {p.delta > 0 ? "+" : ""}{p.delta} {p.unit}</p></div><div><p className="text-[10px] font-bold uppercase text-ink-faint">Engineering problem</p><p className="text-sm">{p.abnormalityStatement}</p></div><div><p className="text-[10px] font-bold uppercase text-ink-faint">Hypothesis</p><p className="text-[11px] text-ink-muted">Causal explanations are listed separately below.</p></div></div>)}
    </section>
    <section className="panel flex flex-col gap-3 p-4">
      <h3 className="text-sm font-semibold text-ink">{t("diagnosis.overview.actionsTitle")}</h3>
      <p className="text-[11px] text-ink-faint">{t("diagnosis.overview.actionsDetail")}</p>
      {availableActions.length === 0 && <EmptyState variant="unavailable" title={t("diagnosis.overview.noActionsTitle")} />}
      <div className="flex flex-wrap gap-2">
        {availableActions
          .filter((a) => a !== "resolve_human_review" && a !== "reopen_diagnosis" && a !== "close_diagnosis")
          .map((a) => (
            <button
              key={a}
              type="button"
              disabled={actionMutation.isPending}
              onClick={() => actionMutation.mutate({ action: a })}
              className="rounded-lg border border-border bg-surface px-3 py-1.5 text-xs font-medium text-ink hover:bg-surface-sunken disabled:opacity-40"
            >
              {t(`diagnosis.action.${a}` as DictKey)}
            </button>
          ))}
      </div>

      {availableActions.includes("resolve_human_review") && (
        <div className="flex flex-wrap items-center gap-2 border-t border-border pt-2">
          <select value={resolution} onChange={(e) => setResolution(e.target.value)} className="rounded-lg border border-border bg-surface px-2 py-1.5 text-xs outline-none">
            <option value="hypotheses_ranked">hypotheses_ranked</option>
            <option value="evidence_limited">evidence_limited</option>
            <option value="closed">closed</option>
          </select>
          <button
            type="button"
            disabled={actionMutation.isPending}
            onClick={() => actionMutation.mutate({ action: "resolve_human_review", kwargs: { resolution } })}
            className="rounded-lg bg-accent px-3 py-1.5 text-xs font-medium text-white disabled:opacity-40"
          >
            {t("diagnosis.action.resolve_human_review")}
          </button>
        </div>
      )}

      {(availableActions.includes("reopen_diagnosis") || availableActions.includes("close_diagnosis")) && (
        <div className="flex flex-wrap items-center gap-2 border-t border-border pt-2">
          <input
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            placeholder={t("diagnosis.overview.reasonPlaceholder")}
            className="min-w-56 flex-1 rounded-lg border border-border px-2.5 py-1.5 text-xs outline-none focus:border-accent"
          />
          {availableActions.includes("reopen_diagnosis") && (
            <button
              type="button"
              disabled={actionMutation.isPending || !reason.trim()}
              onClick={() => actionMutation.mutate({ action: "reopen_diagnosis", kwargs: { reason } })}
              className="rounded-lg border border-border bg-surface px-3 py-1.5 text-xs font-medium text-ink hover:bg-surface-sunken disabled:opacity-40"
            >
              {t("diagnosis.action.reopen_diagnosis")}
            </button>
          )}
          {availableActions.includes("close_diagnosis") && (
            <button
              type="button"
              disabled={actionMutation.isPending || !reason.trim()}
              onClick={() => actionMutation.mutate({ action: "close_diagnosis", kwargs: { reason } })}
              className="rounded-lg border border-border bg-surface px-3 py-1.5 text-xs font-medium text-ink hover:bg-surface-sunken disabled:opacity-40"
            >
              {t("diagnosis.action.close_diagnosis")}
            </button>
          )}
        </div>
      )}
      {actionMutation.isError && <EmptyState variant="failed" detail={String(actionMutation.error)} />}
    </section></div>
  );
}

function EvidenceReviewControls({ link, sessionId }: { link: Awaited<ReturnType<typeof listEvidence>>[number]; sessionId: string }) {
  const { t } = useI18n();
  const queryClient = useQueryClient();
  const reviewMutation = useMutation({
    mutationFn: (verdict: "confirmed" | "incorrect") => reviewEvidenceLink(link.evidenceLinkId, verdict, ACTOR_ID),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["diagnosis-evidence", sessionId] }),
  });
  return (
    <div className="flex shrink-0 items-center gap-1" title={t("diagnosis.evidence.reviewHint")}>
      <button
        type="button"
        disabled={reviewMutation.isPending}
        onClick={() => reviewMutation.mutate("confirmed")}
        className={`rounded border px-1.5 py-0.5 text-[10px] disabled:opacity-40 ${link.reviewStatus === "confirmed" ? "border-emerald-300 bg-emerald-50 text-state-success" : "border-border text-ink-faint hover:bg-surface-sunken"}`}
      >
        ✓ {t("diagnosis.evidence.reviewConfirm")}
      </button>
      <button
        type="button"
        disabled={reviewMutation.isPending}
        onClick={() => reviewMutation.mutate("incorrect")}
        className={`rounded border px-1.5 py-0.5 text-[10px] disabled:opacity-40 ${link.reviewStatus === "incorrect" ? "border-red-300 bg-red-50 text-state-risk" : "border-border text-ink-faint hover:bg-surface-sunken"}`}
      >
        ✗ {t("diagnosis.evidence.reviewFlag")}
      </button>
    </div>
  );
}

function HypothesesTab({
  sessionId, hypotheses, isLoading, isError, error, evidenceByHypothesis,
}: {
  sessionId: string;
  hypotheses: Awaited<ReturnType<typeof listHypotheses>> | undefined;
  isLoading: boolean;
  isError: boolean;
  error: unknown;
  evidenceByHypothesis: Map<string, Awaited<ReturnType<typeof listEvidence>>>;
}) {
  const { t } = useI18n();
  return (
    <section className="flex flex-col gap-2">
      <p className="text-[11px] text-ink-faint">{t("diagnosis.hypotheses.note")}</p>
      {isLoading && <EmptyState variant="loading" />}
      {isError && <EmptyState variant="failed" detail={String(error)} />}
      {hypotheses && hypotheses.length === 0 && <EmptyState variant="first_use" title={t("diagnosis.hypotheses.emptyTitle")} />}
      {hypotheses && hypotheses.length > 0 && (
        <ul className="flex flex-col gap-2">
          {hypotheses.map((h) => {
            const links = evidenceByHypothesis.get(h.hypothesisVersionId) ?? [];
            return (
              <li key={h.hypothesisVersionId} className="panel flex flex-col gap-1 p-3 text-xs">
                <div className="flex items-start justify-between gap-2">
                  <p className="font-medium text-ink">{h.statement ?? h.hypothesisVersionId}</p>
                  <StatusBadge status="active" label={h.status} />
                </div>
                {h.mechanismClass && <p className="text-ink-faint">{t("diagnosis.hypotheses.mechanismClass")}: {h.mechanismClass}</p>}
                {h.omicsLayers.length > 0 && (
                  <p className="text-ink-faint">{t("diagnosis.hypotheses.omicsLayers")}: {h.omicsLayers.join(", ")}</p>
                )}
                {h.falsifiers.length > 0 && (
                  <p className="text-ink-muted">{t("diagnosis.hypotheses.falsifiers")}: {h.falsifiers.join("; ")}</p>
                )}
                {h.contradictions.length > 0 && (
                  <p className="text-state-caution">{t("diagnosis.hypotheses.contradictions")}: {JSON.stringify(h.contradictions)}</p>
                )}
                {links.length > 0 ? (
                  <ul className="flex flex-col gap-1.5 border-t border-border pt-1.5">
                    {links.map((l) => (
                      <li key={l.evidenceLinkId} className="flex items-start justify-between gap-2">
                        <div className="flex items-start gap-1.5">
                          <StatusBadge status={l.relation === "contradicts" ? "rejected" : "approved"} label={l.relation} />
                          <span className="text-ink-muted">{l.claim}</span>
                        </div>
                        <EvidenceReviewControls link={l} sessionId={sessionId} />
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="border-t border-border pt-1.5 text-ink-faint">{t("diagnosis.hypotheses.noEvidence")}</p>
                )}
              </li>
            );
          })}
        </ul>
      )}
    </section>
  );
}

// Module 2 (Engineering Decision Intelligence Layer) §8: the Engineering
// Reasoning Graph, rendered as a grouped node/edge list - no graph/network
// library exists in this frontend, and adding one is out of scope for this
// round, so a structured list (not a node-link diagram) is the honest
// minimal exposure per the source prompt's Phase 4 "do not redesign".
function MechanismGraphTab({ sessionId }: { sessionId: string }) {
  const { t } = useI18n();
  const graphQuery = useQuery({ queryKey: ["diagnosis-mechanism-graph", sessionId], queryFn: () => getMechanismGraph(sessionId) });

  if (graphQuery.isLoading) return <EmptyState variant="loading" />;
  if (graphQuery.isError) return <EmptyState variant="failed" detail={String(graphQuery.error)} />;
  const graph = graphQuery.data;
  if (!graph) return <EmptyState variant="unavailable" />;

  const nodesByType = new Map<string, typeof graph.nodes>();
  for (const n of graph.nodes) {
    nodesByType.set(n.nodeType, [...(nodesByType.get(n.nodeType) ?? []), n]);
  }
  const nodeLabel = new Map(graph.nodes.map((n) => [n.nodeId, n.label]));

  return (
    <section className="panel flex flex-col gap-3 p-4 text-xs">
      <p className="text-[11px] text-ink-faint">{t("diagnosis.mechanismGraph.note")}</p>
      {graph.unknowns.length > 0 && (
        <ul className="flex flex-col gap-1 border-l-2 border-state-caution pl-2 text-state-caution">
          {graph.unknowns.map((u, i) => <li key={i}>{u}</li>)}
        </ul>
      )}
      {[...nodesByType.entries()].map(([nodeType, nodes]) => (
        <div key={nodeType} className="flex flex-col gap-1">
          <h4 className="font-mono text-[10px] uppercase tracking-wide text-ink-faint">{nodeType} ({nodes.length})</h4>
          <ul className="flex flex-col gap-0.5 pl-2">
            {nodes.map((n) => (
              <li key={n.nodeId} className="text-ink-muted">
                <span className="text-ink">{n.label}</span>{" "}
                <span className="text-ink-faint">[{n.source}]</span>
              </li>
            ))}
          </ul>
        </div>
      ))}
      {graph.edges.length > 0 && (
        <div className="flex flex-col gap-1 border-t border-border pt-2">
          <h4 className="font-mono text-[10px] uppercase tracking-wide text-ink-faint">{t("diagnosis.mechanismGraph.edges")} ({graph.edges.length})</h4>
          <ul className="flex flex-col gap-0.5 pl-2">
            {graph.edges.map((e, i) => (
              <li key={i} className="text-ink-muted">
                {nodeLabel.get(e.sourceId) ?? e.sourceId} → {nodeLabel.get(e.targetId) ?? e.targetId}
                {" "}<span className="text-ink-faint">({e.edgeType}, {e.sourceRef}{e.isUnknownOrConflicting ? ", unverified" : ""})</span>
                {typeof e.applicabilityContext.rule === "string" && e.applicabilityContext.rule && (
                  <span className="block pl-3 text-[11px] text-ink-faint">↳ {e.applicabilityContext.rule}</span>
                )}
              </li>
            ))}
          </ul>
        </div>
      )}
    </section>
  );
}

const EVIDENCE_SOURCE_TYPES = ["literature", "expert_rule", "llm_reasoning", "model_run", "experiment_result", "observation"];
const EVIDENCE_QUALITIES = ["high", "medium", "low"];
const EVIDENCE_DIRECTNESS = ["direct", "indirect"];

function evidenceItemLabel(item: Awaited<ReturnType<typeof listEvidenceItems>>[number]): string {
  const summary = item.contentSummary.trim();
  const truncated = summary.length > 64 ? `${summary.slice(0, 64)}…` : summary;
  return truncated ? `${truncated} (${item.sourceType})` : `${item.evidenceItemId} (${item.sourceType})`;
}

function EvidenceTab({
  projectId, sessionId, hypotheses,
}: {
  projectId: string;
  sessionId: string;
  hypotheses: Awaited<ReturnType<typeof listHypotheses>>;
}) {
  const { t } = useI18n();
  const queryClient = useQueryClient();
  const [showLink, setShowLink] = useState(false);
  const [hypothesisVersionId, setHypothesisVersionId] = useState("");
  const [evidenceItemId, setEvidenceItemId] = useState("");
  const [relation, setRelation] = useState("supports");
  const [claim, setClaim] = useState("");
  const [showCreate, setShowCreate] = useState(false);
  const [newSourceType, setNewSourceType] = useState("expert_rule");
  const [newContentSummary, setNewContentSummary] = useState("");
  const [newQuality, setNewQuality] = useState("low");
  const [newDirectness, setNewDirectness] = useState("indirect");

  const evidenceItemsQuery = useQuery({
    queryKey: ["diagnosis-evidence-items", projectId],
    queryFn: () => listEvidenceItems(projectId),
    enabled: !!projectId,
  });

  const createItemMutation = useMutation({
    mutationFn: () => createEvidenceItem({
      projectId, actorId: ACTOR_ID, sourceType: newSourceType, contentSummary: newContentSummary,
      quality: newQuality, directness: newDirectness,
    }),
    onSuccess: (newEvidenceItemId) => {
      queryClient.invalidateQueries({ queryKey: ["diagnosis-evidence-items", projectId] });
      setEvidenceItemId(newEvidenceItemId);
      setNewContentSummary("");
      setShowCreate(false);
    },
  });

  const linkMutation = useMutation({
    mutationFn: () => linkEvidence({ hypothesisVersionId, evidenceItemId, relation, actorId: ACTOR_ID, claim }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["diagnosis-evidence", sessionId] });
      setEvidenceItemId("");
      setClaim("");
    },
  });

  return (
    <section className="flex flex-col gap-3">
      <p className="text-[11px] text-ink-faint">{t("diagnosis.evidence.redirectNote")}</p>

      <div className="panel flex flex-col gap-2 p-4">
        <button
          type="button"
          onClick={() => setShowLink((v) => !v)}
          className="flex w-fit items-center gap-1 text-xs font-medium text-accent-strong hover:underline"
        >
          <Plus size={13} aria-hidden />
          {t("diagnosis.evidence.linkTitle")}
        </button>
        {showLink && (
          <div className="flex flex-col gap-2 border-t border-border pt-2">
            <p className="text-[11px] text-ink-faint">{t("diagnosis.evidence.linkDetail")}</p>
            <div className="grid gap-2 sm:grid-cols-2">
              <select value={hypothesisVersionId} onChange={(e) => setHypothesisVersionId(e.target.value)} className="rounded-lg border border-border bg-surface px-2 py-1.5 text-xs outline-none">
                <option value="">{t("diagnosis.evidence.selectHypothesis")}</option>
                {hypotheses.map((h) => (
                  <option key={h.hypothesisVersionId} value={h.hypothesisVersionId}>{h.statement ?? h.hypothesisVersionId}</option>
                ))}
              </select>
              <select value={relation} onChange={(e) => setRelation(e.target.value)} className="rounded-lg border border-border bg-surface px-2 py-1.5 text-xs outline-none">
                <option value="supports">supports</option>
                <option value="contradicts">contradicts</option>
                <option value="is_consistent_with">is_consistent_with</option>
                <option value="does_not_discriminate">does_not_discriminate</option>
              </select>
              <select
                value={evidenceItemId}
                onChange={(e) => setEvidenceItemId(e.target.value)}
                className="rounded-lg border border-border bg-surface px-2 py-1.5 text-xs outline-none sm:col-span-2"
              >
                <option value="">{t("diagnosis.evidence.selectItem")}</option>
                {evidenceItemsQuery.data?.map((item) => (
                  <option key={item.evidenceItemId} value={item.evidenceItemId}>{evidenceItemLabel(item)}</option>
                ))}
              </select>
              <input value={claim} onChange={(e) => setClaim(e.target.value)} placeholder={t("diagnosis.evidence.claimPlaceholder")} className="rounded-lg border border-border px-2.5 py-1.5 text-xs outline-none focus:border-accent sm:col-span-2" />
            </div>
            <button
              type="button"
              disabled={linkMutation.isPending || !hypothesisVersionId || !evidenceItemId}
              onClick={() => linkMutation.mutate()}
              className="w-fit rounded-lg bg-accent px-3 py-1.5 text-xs font-medium text-white disabled:opacity-40"
            >
              {linkMutation.isPending ? t("diagnosis.evidence.linking") : t("diagnosis.evidence.link")}
            </button>
            {linkMutation.isError && <EmptyState variant="failed" detail={String(linkMutation.error)} />}
          </div>
        )}
      </div>

      <div className="panel flex flex-col gap-2 p-4">
        <button
          type="button"
          onClick={() => setShowCreate((v) => !v)}
          className="flex w-fit items-center gap-1 text-xs font-medium text-accent-strong hover:underline"
        >
          <Plus size={13} aria-hidden />
          {t("diagnosis.evidence.createNew")}
        </button>
        {showCreate && (
          <div className="flex flex-col gap-2 border-t border-border pt-2">
            <div className="grid gap-2 sm:grid-cols-2">
              <select value={newSourceType} onChange={(e) => setNewSourceType(e.target.value)} className="rounded-lg border border-border bg-surface px-2 py-1.5 text-xs outline-none">
                {EVIDENCE_SOURCE_TYPES.map((st) => <option key={st} value={st}>{st}</option>)}
              </select>
              <select value={newQuality} onChange={(e) => setNewQuality(e.target.value)} className="rounded-lg border border-border bg-surface px-2 py-1.5 text-xs outline-none">
                {EVIDENCE_QUALITIES.map((q) => <option key={q} value={q}>{t(`diagnosis.evidence.quality.${q}` as DictKey)}</option>)}
              </select>
              <select value={newDirectness} onChange={(e) => setNewDirectness(e.target.value)} className="rounded-lg border border-border bg-surface px-2 py-1.5 text-xs outline-none">
                {EVIDENCE_DIRECTNESS.map((d) => <option key={d} value={d}>{t(`diagnosis.evidence.directness.${d}` as DictKey)}</option>)}
              </select>
              <input
                value={newContentSummary}
                onChange={(e) => setNewContentSummary(e.target.value)}
                placeholder={t("diagnosis.evidence.contentSummaryPlaceholder")}
                className="rounded-lg border border-border px-2.5 py-1.5 text-xs outline-none focus:border-accent sm:col-span-2"
              />
            </div>
            <button
              type="button"
              disabled={createItemMutation.isPending || !newContentSummary.trim()}
              onClick={() => createItemMutation.mutate()}
              className="w-fit rounded-lg border border-border bg-surface px-3 py-1.5 text-xs font-medium text-ink hover:bg-surface-sunken disabled:opacity-40"
            >
              {createItemMutation.isPending ? t("diagnosis.evidence.creating") : t("diagnosis.evidence.create")}
            </button>
            {createItemMutation.isError && <EmptyState variant="failed" detail={String(createItemMutation.error)} />}
          </div>
        )}
      </div>
    </section>
  );
}

/** Curated one-line explanations for the fixed adapter set (harness/diagnosis/
 * model_adapters/*.py docstrings) - the backend's `cap.reason` string is a
 * technical availability reason (still shown as a hover title), not an
 * explanation of what the adapter does or when to pick it. */
const MODEL_ADAPTER_INFO: Record<string, DictKey> = {
  gem_fba: "diagnosis.models.adapter.gem_fba",
  gem_fba_iml1515: "diagnosis.models.adapter.gem_fba_iml1515",
  vecoli: "diagnosis.models.adapter.vecoli",
  kinetic_resource: "diagnosis.models.adapter.kinetic_resource",
};

function ModelRunsTab({ projectId, sessionId }: { projectId: string; sessionId: string }) {
  const { t } = useI18n();
  const [adapterName, setAdapterName] = useState("");
  const [inputsText, setInputsText] = useState("{}");

  const capsQuery = useQuery({ queryKey: ["diagnosis-model-capabilities"], queryFn: listModelCapabilities });
  const runMutation = useMutation({
    mutationFn: () => {
      let inputs: Record<string, unknown> = {};
      try {
        inputs = JSON.parse(inputsText || "{}");
      } catch {
        throw new Error(t("diagnosis.models.invalidJson"));
      }
      return runModel({ projectId, diagnosisSessionId: sessionId, adapterName, actorId: ACTOR_ID, inputs });
    },
  });

  return (
    <section className="flex flex-col gap-3">
      <p className="text-[11px] text-ink-faint">{t("diagnosis.models.purpose")}</p>
      <div className="panel flex flex-col gap-2 p-4">
        <h3 className="text-sm font-semibold text-ink">{t("diagnosis.models.capabilitiesTitle")}</h3>
        {capsQuery.isLoading && <EmptyState variant="loading" />}
        {capsQuery.data && (
          <ul className="flex flex-col gap-1.5">
            {Object.entries(capsQuery.data).map(([name, cap]) => (
              <li key={name} className="flex items-start gap-2 text-[11px]">
                <span
                  className={`shrink-0 rounded border px-2 py-1 font-mono ${cap.available ? "border-emerald-300 bg-emerald-50 text-state-success" : "border-slate-300 bg-slate-100 text-state-unavailable"}`}
                  title={cap.reason}
                >
                  {name}
                </span>
                <span className="text-ink-muted">{MODEL_ADAPTER_INFO[name] ? t(MODEL_ADAPTER_INFO[name]) : cap.reason}</span>
              </li>
            ))}
          </ul>
        )}
      </div>

      <div className="panel flex flex-col gap-2 p-4">
        <h3 className="text-sm font-semibold text-ink">{t("diagnosis.models.runTitle")}</h3>
        <select value={adapterName} onChange={(e) => setAdapterName(e.target.value)} className="w-fit rounded-lg border border-border bg-surface px-2 py-1.5 text-xs outline-none">
          <option value="">{t("diagnosis.models.selectAdapter")}</option>
          {capsQuery.data && Object.keys(capsQuery.data).map((name) => <option key={name} value={name}>{name}</option>)}
        </select>
        {adapterName && MODEL_ADAPTER_INFO[adapterName] && (
          <p className="text-[11px] text-ink-faint">{t(MODEL_ADAPTER_INFO[adapterName])}</p>
        )}
        <textarea
          value={inputsText}
          onChange={(e) => setInputsText(e.target.value)}
          rows={4}
          className="rounded-lg border border-border px-2.5 py-1.5 font-mono text-[11px] outline-none focus:border-accent"
          placeholder="{}"
        />
        <button
          type="button"
          disabled={runMutation.isPending || !adapterName}
          onClick={() => runMutation.mutate()}
          className="w-fit rounded-lg bg-accent px-3 py-1.5 text-xs font-medium text-white disabled:opacity-40"
        >
          {runMutation.isPending ? t("diagnosis.models.running") : t("diagnosis.models.run")}
        </button>
        {runMutation.isError && <EmptyState variant="failed" detail={String(runMutation.error)} />}
        {runMutation.data && (
          <div className="rounded-lg border border-border bg-surface-sunken p-2 text-[11px]">
            <p>{t("diagnosis.models.runtimeStatus")}: {runMutation.data.runtimeStatus}</p>
            <pre className="mt-1 overflow-x-auto whitespace-pre-wrap">{JSON.stringify(runMutation.data.outputs, null, 2)}</pre>
          </div>
        )}
      </div>
    </section>
  );
}

function TestsTab({ sessionId }: { sessionId: string }) {
  const { t } = useI18n();
  const testsQuery = useQuery({ queryKey: ["diagnosis-tests", sessionId], queryFn: () => listTests(sessionId) });
  return (
    <section className="flex flex-col gap-2">
      <p className="text-[11px] text-ink-faint">{t("diagnosis.tests.note")}</p>
      {testsQuery.isLoading && <EmptyState variant="loading" />}
      {testsQuery.isError && <EmptyState variant="failed" detail={String(testsQuery.error)} />}
      {testsQuery.data && testsQuery.data.length === 0 && <EmptyState variant="first_use" title={t("diagnosis.tests.emptyTitle")} />}
      {testsQuery.data && testsQuery.data.length > 0 && (
        <ul className="flex flex-col gap-2">
          {testsQuery.data.map((tst) => (
            <li key={tst.testId} className="panel flex flex-col gap-1 p-3 text-xs">
              <div className="flex items-center justify-between gap-2">
                <p className="font-medium text-ink">{tst.assay || tst.testId}</p>
                <StatusBadge status="active" label={tst.status} />
              </div>
              <p className="text-ink-faint">{t("diagnosis.tests.infoGain")}: {tst.expectedInformationGain} · {t("diagnosis.tests.discriminates")}: {tst.discriminatesHypotheses ? "yes" : "no"}</p>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}

function DecisionsTab({ projectId, sessionId }: { projectId: string; sessionId: string }) {
  const { t } = useI18n();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const decisionsQuery = useQuery({ queryKey: ["diagnosis-decisions", sessionId], queryFn: () => listDecisions(sessionId) });
  const approveMutation = useMutation({
    mutationFn: (input: { decisionId: string; approved: boolean }) => approveDecision(input.decisionId, ACTOR_ID, input.approved),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["diagnosis-decisions", sessionId] }),
  });

  return (
    <section className="flex flex-col gap-2">
      {decisionsQuery.isLoading && <EmptyState variant="loading" />}
      {decisionsQuery.isError && <EmptyState variant="failed" detail={String(decisionsQuery.error)} />}
      {decisionsQuery.data && decisionsQuery.data.length === 0 && <EmptyState variant="first_use" title={t("diagnosis.decisions.emptyTitle")} />}
      {decisionsQuery.data && decisionsQuery.data.length > 0 && (
        <ul className="flex flex-col gap-2">
          {decisionsQuery.data.map((d) => (
            <li key={d.decisionId} className="panel flex flex-col gap-2 p-3 text-xs">
              <div className="flex items-center justify-between gap-2">
                <span className="font-mono text-[11px] text-ink-faint">{d.decisionId} · v{d.diagnosisVersion}</span>
                <StatusBadge status={d.handoffStatus === "approved" || d.handoffStatus === "handed_off" ? "approved" : d.handoffStatus === "rejected" ? "rejected" : "active"} label={d.handoffStatus} />
              </div>
              <p className="text-ink-muted">{t("diagnosis.decisions.stoppingReason")}: {d.stoppingReason}</p>
              <p className="text-ink-faint">{t("diagnosis.decisions.allowedNextAction")}: {d.allowedNextAction}</p>
              <div className="flex flex-wrap gap-2 border-t border-border pt-2">
                <button
                  type="button"
                  disabled={approveMutation.isPending}
                  onClick={() => approveMutation.mutate({ decisionId: d.decisionId, approved: true })}
                  className="rounded-lg border border-emerald-300 bg-emerald-50 px-2.5 py-1 text-[11px] font-medium text-state-success hover:bg-emerald-100 disabled:opacity-40"
                >
                  {t("diagnosis.decisions.approve")}
                </button>
                <button
                  type="button"
                  disabled={approveMutation.isPending}
                  onClick={() => approveMutation.mutate({ decisionId: d.decisionId, approved: false })}
                  className="rounded-lg border border-red-300 bg-red-50 px-2.5 py-1 text-[11px] font-medium text-state-risk hover:bg-red-100 disabled:opacity-40"
                >
                  {t("diagnosis.decisions.reject")}
                </button>
                {d.allowedNextAction === "handoff_to_design" && (
                  <button
                    type="button"
                    onClick={() =>
                      navigate(
                        `/projects/${projectId}/design?decisionId=${encodeURIComponent(d.decisionId)}&sessionId=${encodeURIComponent(sessionId)}`,
                      )
                    }
                    className="ml-auto rounded-lg bg-accent px-2.5 py-1 text-[11px] font-medium text-white"
                  >
                    {t("diagnosis.decisions.handoffToDesign")}
                  </button>
                )}
              </div>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}

function AuditReportTab({ sessionId }: { sessionId: string }) {
  const { t } = useI18n();
  const auditQuery = useQuery({ queryKey: ["diagnosis-audit", sessionId], queryFn: () => getAuditTrail(sessionId) });
  const reportQuery = useQuery({ queryKey: ["diagnosis-report", sessionId], queryFn: () => getReport(sessionId) });

  return (
    <section className="flex flex-col gap-4">
      <div className="panel flex flex-col gap-2 p-4">
        <h3 className="text-sm font-semibold text-ink">{t("diagnosis.audit.transitionsTitle")}</h3>
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

      <div className="panel flex flex-col gap-3 p-4">
        <h3 className="text-sm font-semibold text-ink">{t("diagnosis.audit.reportTitle")}</h3>
        {reportQuery.isLoading && <EmptyState variant="loading" />}
        {reportQuery.data && reportQuery.data.length > 0 && (
          <div className="flex flex-col gap-3">
            {reportQuery.data.map((s) => (
              <div key={s.title} className="rounded-lg border border-border p-3">
                <h4 className="text-xs font-semibold text-ink">{s.title}</h4>
                <ReportContent content={s.content} />
              </div>
            ))}
          </div>
        )}
      </div>
    </section>
  );
}

const REPORT_LABEL_OVERRIDE: Record<string, string> = {
  status: "状态", data_sufficiency: "数据充分性", stopping_reason: "停止原因", allowed_next_action: "允许的下一步动作",
  note: "说明", biological_system: "生物系统", baseline_observation_ids: "基线观测", leading_hypothesis_ids: "主导假设",
  alternatives_not_excluded_ids: "未排除的备选假设", contradictions: "矛盾点", confidence_representation: "置信度",
  uncertainty: "不确定性", evidence_references: "证据引用",
};

function reportFieldLabel(key: string): string {
  return REPORT_LABEL_OVERRIDE[key] ?? key.replace(/_/g, " ");
}

/** Report sections come back as an arbitrary-shaped dict (harness/diagnosis/
 * report.py's `ReportSection.content`) - renders it as readable label:value
 * rows instead of a raw JSON dump, so a non-technical reader can actually
 * follow the diagnosis's own narrative summary. Falls back to a compact
 * inline join for primitives/arrays and one level of nested key:value for
 * objects; never silently drops a field. */
function ReportContent({ content }: { content: Record<string, unknown> }) {
  const entries = Object.entries(content).filter(([, v]) => v !== null && v !== undefined && v !== "");
  if (entries.length === 0) return <p className="mt-1 text-[11px] text-ink-faint">—</p>;
  return (
    <dl className="mt-2 flex flex-col gap-1.5 text-[11px]">
      {entries.map(([key, value]) => (
        <div key={key} className="flex flex-col gap-0.5 sm:flex-row sm:gap-2">
          <dt className="shrink-0 font-medium text-ink-faint sm:w-40">{reportFieldLabel(key)}</dt>
          <dd className="min-w-0 flex-1 text-ink-muted"><ReportValue value={value} /></dd>
        </div>
      ))}
    </dl>
  );
}

function ReportValue({ value }: { value: unknown }) {
  if (Array.isArray(value)) {
    if (value.length === 0) return <span className="italic text-ink-faint">—</span>;
    if (value.every((v) => typeof v !== "object" || v === null)) return <span>{value.join("、")}</span>;
    return (
      <ul className="flex flex-col gap-1">
        {value.map((v, i) => (
          <li key={i} className="rounded border border-border bg-surface-sunken px-1.5 py-1">
            {typeof v === "object" && v !== null ? <ReportContent content={v as Record<string, unknown>} /> : String(v)}
          </li>
        ))}
      </ul>
    );
  }
  if (value !== null && typeof value === "object") return <ReportContent content={value as Record<string, unknown>} />;
  return <span>{String(value)}</span>;
}
