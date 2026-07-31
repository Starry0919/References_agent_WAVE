import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useNavigate, useParams, useSearchParams } from "react-router-dom";
import {
  ClipboardList, Lightbulb, BookOpen, Cpu, TestTube2, Gavel, History,
} from "lucide-react";
import {
  approveDecision, getAuditTrail, getReport, getSession, linkEvidence, listDecisions, listEvidence,
  listHypotheses, listModelCapabilities, listTests, runModel, sessionAction,
  DIAGNOSIS_SESSION_ACTIONS, type DiagnosisSessionAction,
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

type Tab = "overview" | "hypotheses" | "evidence" | "models" | "tests" | "decisions" | "audit";
const TABS: Tab[] = ["overview", "hypotheses", "evidence", "models", "tests", "decisions", "audit"];
const TAB_ICON: Record<Tab, typeof ClipboardList> = {
  overview: ClipboardList, hypotheses: Lightbulb, evidence: BookOpen, models: Cpu,
  tests: TestTube2, decisions: Gavel, audit: History,
};

export function DiagnosisSessionDetailPage() {
  const { projectId, sessionId } = useParams<{ projectId: string; sessionId: string }>();
  const { t } = useI18n();
  const [params, setParams] = useSearchParams();
  const tabParam = params.get("tab");
  const tab: Tab = TABS.includes(tabParam as Tab) ? (tabParam as Tab) : "overview";
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
          <TabButton key={tb} active={tab === tb} onClick={() => setTab(tb)} icon={TAB_ICON[tb]} label={t(`diagnosis.tab.${tb}` as DictKey)} />
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

          {tab === "overview" && <OverviewTab sessionId={session.diagnosisSessionId} status={session.status} />}
          {tab === "hypotheses" && <HypothesesTab hypotheses={hypothesesQuery.data} isLoading={hypothesesQuery.isLoading} isError={hypothesesQuery.isError} error={hypothesesQuery.error} />}
          {tab === "evidence" && <EvidenceTab sessionId={session.diagnosisSessionId} hypotheses={hypothesesQuery.data ?? []} />}
          {tab === "models" && <ModelRunsTab projectId={projectId as string} sessionId={session.diagnosisSessionId} />}
          {tab === "tests" && <TestsTab sessionId={session.diagnosisSessionId} />}
          {tab === "decisions" && <DecisionsTab projectId={projectId as string} sessionId={session.diagnosisSessionId} />}
          {tab === "audit" && <AuditReportTab sessionId={session.diagnosisSessionId} />}
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

function OverviewTab({ sessionId, status }: { sessionId: string; status: string }) {
  const { t } = useI18n();
  const queryClient = useQueryClient();
  const [resolution, setResolution] = useState("hypotheses_ranked");
  const [reason, setReason] = useState("");

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
    </section>
  );
}

function HypothesesTab({
  hypotheses, isLoading, isError, error,
}: {
  hypotheses: Awaited<ReturnType<typeof listHypotheses>> | undefined;
  isLoading: boolean;
  isError: boolean;
  error: unknown;
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
          {hypotheses.map((h) => (
            <li key={h.hypothesisVersionId} className="panel flex flex-col gap-1 p-3 text-xs">
              <div className="flex items-start justify-between gap-2">
                <p className="font-medium text-ink">{h.statement ?? h.hypothesisVersionId}</p>
                <StatusBadge status="active" label={h.status} />
              </div>
              {h.mechanismClass && <p className="text-ink-faint">{t("diagnosis.hypotheses.mechanismClass")}: {h.mechanismClass}</p>}
              {h.contradictions.length > 0 && (
                <p className="text-state-caution">{t("diagnosis.hypotheses.contradictions")}: {JSON.stringify(h.contradictions)}</p>
              )}
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}

function EvidenceTab({ sessionId, hypotheses }: { sessionId: string; hypotheses: Awaited<ReturnType<typeof listHypotheses>> }) {
  const { t } = useI18n();
  const queryClient = useQueryClient();
  const [hypothesisVersionId, setHypothesisVersionId] = useState("");
  const [evidenceItemId, setEvidenceItemId] = useState("");
  const [relation, setRelation] = useState("supports");
  const [claim, setClaim] = useState("");

  const evidenceQuery = useQuery({ queryKey: ["diagnosis-evidence", sessionId], queryFn: () => listEvidence(sessionId) });
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
      <div className="panel flex flex-col gap-2 p-4">
        <h3 className="text-sm font-semibold text-ink">{t("diagnosis.evidence.linkTitle")}</h3>
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
          <input value={evidenceItemId} onChange={(e) => setEvidenceItemId(e.target.value)} placeholder={t("diagnosis.evidence.evidenceItemIdPlaceholder")} className="rounded-lg border border-border px-2.5 py-1.5 text-xs outline-none focus:border-accent sm:col-span-2" />
          <input value={claim} onChange={(e) => setClaim(e.target.value)} placeholder={t("diagnosis.evidence.claimPlaceholder")} className="rounded-lg border border-border px-2.5 py-1.5 text-xs outline-none focus:border-accent sm:col-span-2" />
        </div>
        <button
          type="button"
          disabled={linkMutation.isPending || !hypothesisVersionId || !evidenceItemId.trim()}
          onClick={() => linkMutation.mutate()}
          className="w-fit rounded-lg bg-accent px-3 py-1.5 text-xs font-medium text-white disabled:opacity-40"
        >
          {linkMutation.isPending ? t("diagnosis.evidence.linking") : t("diagnosis.evidence.link")}
        </button>
        {linkMutation.isError && <EmptyState variant="failed" detail={String(linkMutation.error)} />}
      </div>

      {evidenceQuery.isLoading && <EmptyState variant="loading" />}
      {evidenceQuery.isError && <EmptyState variant="failed" detail={String(evidenceQuery.error)} />}
      {evidenceQuery.data && evidenceQuery.data.length === 0 && <EmptyState variant="first_use" title={t("diagnosis.evidence.emptyTitle")} />}
      {evidenceQuery.data && evidenceQuery.data.length > 0 && (
        <ul className="flex flex-col gap-2">
          {evidenceQuery.data.map((e) => (
            <li key={e.evidenceLinkId} className="panel flex flex-col gap-1 p-3 text-xs">
              <div className="flex items-center justify-between gap-2">
                <span className="font-mono text-[11px] text-ink-faint">{e.evidenceItemId}</span>
                <StatusBadge status={e.relation === "contradicts" ? "rejected" : "approved"} label={e.relation} />
              </div>
              {e.claim && <p className="text-ink-muted">{e.claim}</p>}
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}

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
      <div className="panel flex flex-col gap-2 p-4">
        <h3 className="text-sm font-semibold text-ink">{t("diagnosis.models.capabilitiesTitle")}</h3>
        {capsQuery.isLoading && <EmptyState variant="loading" />}
        {capsQuery.data && (
          <div className="flex flex-wrap gap-2">
            {Object.entries(capsQuery.data).map(([name, cap]) => (
              <span key={name} className={`rounded border px-2 py-1 text-[11px] ${cap.available ? "border-emerald-300 bg-emerald-50 text-state-success" : "border-slate-300 bg-slate-100 text-state-unavailable"}`} title={cap.reason}>
                {name}
              </span>
            ))}
          </div>
        )}
      </div>

      <div className="panel flex flex-col gap-2 p-4">
        <h3 className="text-sm font-semibold text-ink">{t("diagnosis.models.runTitle")}</h3>
        <select value={adapterName} onChange={(e) => setAdapterName(e.target.value)} className="w-fit rounded-lg border border-border bg-surface px-2 py-1.5 text-xs outline-none">
          <option value="">{t("diagnosis.models.selectAdapter")}</option>
          {capsQuery.data && Object.keys(capsQuery.data).map((name) => <option key={name} value={name}>{name}</option>)}
        </select>
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

      <div className="panel flex flex-col gap-2 p-4">
        <h3 className="text-sm font-semibold text-ink">{t("diagnosis.audit.reportTitle")}</h3>
        {reportQuery.isLoading && <EmptyState variant="loading" />}
        {reportQuery.data && reportQuery.data.length > 0 && (
          <div className="flex flex-col gap-3">
            {reportQuery.data.map((s) => (
              <div key={s.title}>
                <h4 className="label-caps">{s.title}</h4>
                <pre className="mt-1 overflow-x-auto whitespace-pre-wrap rounded bg-surface-sunken p-2 text-[11px] text-ink-muted">
                  {JSON.stringify(s.content, null, 2)}
                </pre>
              </div>
            ))}
          </div>
        )}
      </div>
    </section>
  );
}
