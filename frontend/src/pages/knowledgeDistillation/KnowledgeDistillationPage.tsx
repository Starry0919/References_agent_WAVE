import { useState } from "react";
import { useSearchParams } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { UploadCloud, Dna, AlertTriangle, History, ShieldCheck } from "lucide-react";
import {
  getRun,
  listRuns,
  submitRun,
  uploadSource,
  type EngineeringPrincipleView,
  type KnowledgeObjectView,
  type RunHistoryItem,
  type RunResult,
} from "@/api/knowledgeDistillation";
import { EmptyState } from "@/components/common/EmptyState";
import { StatusBadge, type BadgeStatus } from "@/components/common/StatusBadge";
import { useI18n } from "@/lib/i18n";

/**
 * Biological Knowledge Distillation (harness/api/knowledge_distillation.py,
 * real, vendoring the 13-step pipeline). Submit a textbook/chapter excerpt,
 * poll the async task, render Step13's frontend_view categories (concepts &
 * mechanisms / engineering principles / decision rules / design patterns /
 * failure patterns / governance) once it lands. `?kd_task=` in the URL keeps
 * the run refreshable - a distinct param from paperExtraction's `?task=`
 * since both modules are tabs on the same KnowledgePage and share one
 * search-params object.
 */
export function KnowledgeDistillationPage({ embedded = false }: { embedded?: boolean }) {
  const { t } = useI18n();
  const [params, setParams] = useSearchParams();
  const taskId = params.get("kd_task");
  const queryClient = useQueryClient();

  const runQuery = useQuery({
    queryKey: ["knowledge-distillation-run", taskId],
    queryFn: () => getRun(taskId as string),
    enabled: !!taskId,
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      return status === "RUNNING" || status === "CREATED" || status === undefined ? 3000 : false;
    },
  });

  const historyQuery = useQuery({
    queryKey: ["knowledge-distillation-history"],
    queryFn: () => listRuns(),
    enabled: !taskId,
    refetchInterval: !taskId ? 5000 : false,
  });

  const startNew = () => {
    const next = new URLSearchParams(params);
    next.delete("kd_task");
    setParams(next, { replace: true });
    queryClient.removeQueries({ queryKey: ["knowledge-distillation-run"] });
  };

  return (
    <div className={`flex min-h-0 flex-1 flex-col overflow-y-auto ${embedded ? "" : "p-4"}`}>
      <div className="mb-5 flex items-start justify-between gap-6 rounded-xl border border-border bg-surface px-5 py-4 shadow-sm">
        <div className="flex min-w-0 items-start gap-3">
          <div className="mt-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-emerald-50 text-emerald-600">
            <Dna size={19} aria-hidden />
          </div>
          <div className="min-w-0">
            <h1 className="text-lg font-semibold text-ink">{t("page6.title")}</h1>
            <p className="mt-1 max-w-4xl text-sm leading-5 text-ink-muted">{t("page6.subtitle")}</p>
          </div>
        </div>
        {taskId && (
          <button onClick={startNew} className="flex-shrink-0 rounded border border-border px-2.5 py-1.5 text-xs font-medium text-ink-muted hover:bg-surface-sunken">
            {t("page6.startNewRun")}
          </button>
        )}
      </div>

      {!taskId && (
        <div className="grid items-start gap-5 xl:grid-cols-[minmax(440px,0.9fr)_minmax(520px,1.1fr)]">
          <SubmissionForm
            onSubmitted={(id) => {
              const next = new URLSearchParams(params);
              next.set("kd_task", id);
              setParams(next, { replace: true });
              queryClient.invalidateQueries({ queryKey: ["knowledge-distillation-history"] });
            }}
          />
          <div className="min-w-0">
            <RunHistory
              items={historyQuery.data ?? []}
              isLoading={historyQuery.isLoading}
              onSelect={(id) => {
                const next = new URLSearchParams(params);
                next.set("kd_task", id);
                setParams(next, { replace: true });
              }}
            />
          </div>
        </div>
      )}

      {taskId && runQuery.isLoading && <EmptyState variant="loading" />}
      {taskId && runQuery.isError && <EmptyState variant="failed" detail={String(runQuery.error)} />}
      {taskId && runQuery.data && <RunView run={runQuery.data} />}
    </div>
  );
}

function historyStatusBadge(status: string): BadgeStatus {
  switch (status.toLowerCase()) {
    case "created":
      return "not_started";
    case "running":
      return "active";
    case "waiting_review":
      return "waiting_for_human";
    case "completed":
      return "completed";
    case "failed":
      return "failed";
    default:
      return "unclear";
  }
}

function RunHistory({ items, isLoading, onSelect }: { items: RunHistoryItem[]; isLoading: boolean; onSelect: (taskId: string) => void }) {
  const { t } = useI18n();
  return (
    <section className="panel flex min-h-[360px] flex-col overflow-hidden">
      <div className="flex items-center justify-between border-b border-border px-4 py-3.5">
        <div className="flex items-center gap-2">
          <History size={16} className="text-accent" aria-hidden />
          <h3 className="text-sm font-semibold text-ink">{t("page6.historyTitle")}</h3>
        </div>
        {items.length > 0 && <span className="rounded-full bg-surface-sunken px-2 py-0.5 text-[11px] text-ink-muted">{items.length}</span>}
      </div>
      <div className="flex flex-1 flex-col p-3">
        {isLoading && <div className="flex min-h-56 items-center justify-center"><EmptyState variant="loading" /></div>}
        {!isLoading && items.length === 0 && <div className="flex min-h-56 items-center justify-center"><p className="text-xs text-ink-faint">{t("page6.historyEmpty")}</p></div>}
        {items.length > 0 && (
          <ul className="flex max-h-[520px] flex-col gap-2 overflow-y-auto pr-1">
            {items.map((item) => (
              <li key={item.taskId}>
                <button
                  onClick={() => onSelect(item.taskId)}
                  className="group flex w-full flex-col gap-2 rounded-lg border border-border bg-surface px-3.5 py-3 text-left text-xs transition hover:border-accent/40 hover:bg-surface-sunken"
                >
                  <div className="flex items-center justify-between gap-2">
                    <span className="line-clamp-2 pr-2 font-medium leading-5 text-ink">{item.userRequest}</span>
                    <StatusBadge status={historyStatusBadge(item.status)} label={t(`page5.status.${item.status.toUpperCase()}` as Parameters<ReturnType<typeof useI18n>["t"]>[0])} />
                  </div>
                  <div className="flex items-center gap-2 text-[11px] text-ink-faint">
                    <span className="font-mono">{item.taskId}</span>
                    <span>{item.sourceCount} {t("page6.sources").toLowerCase()}</span>
                    <span>{new Date(item.submittedAt * 1000).toLocaleString()}</span>
                  </div>
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
    </section>
  );
}

function SubmissionForm({ onSubmitted }: { onSubmitted: (taskId: string) => void }) {
  const { t } = useI18n();
  const [userRequest, setUserRequest] = useState("");
  const [sourceText, setSourceText] = useState("");
  const [title, setTitle] = useState("");
  const [engineeringGoal, setEngineeringGoal] = useState("");
  const [organism, setOrganism] = useState("");

  const uploadMutation = useMutation({
    mutationFn: uploadSource,
    onSuccess: (res) => setSourceText((prev) => (prev ? prev : `[[uploaded:${res.filename}]]`)),
    onError: () => undefined,
  });

  const submitMutation = useMutation({
    mutationFn: () =>
      submitRun({
        userRequest,
        sources: [{ text: sourceText, title, sourceType: "textbook" }],
        targetEngineeringGoal: engineeringGoal.trim() ? [engineeringGoal.trim()] : [],
        targetOrganism: organism.trim() ? [organism.trim()] : [],
      }),
    onSuccess: (res) => onSubmitted(res.task_id),
  });

  const canSubmit = userRequest.trim().length > 0 && sourceText.trim().length > 0 && !submitMutation.isPending;

  return (
    <section className="panel flex min-w-0 flex-col overflow-hidden">
      <div className="flex items-center gap-2 border-b border-border px-4 py-3.5">
        <Dna size={16} className="text-accent" aria-hidden />
        <h2 className="text-sm font-semibold text-ink">{t("page6.form.userRequest")}</h2>
      </div>
      <div className="flex flex-col gap-4 p-4">
        <div className="flex flex-col gap-1">
          <label className="label-caps">{t("page6.form.userRequest")}</label>
          <textarea
            value={userRequest}
            onChange={(e) => setUserRequest(e.target.value)}
            placeholder={t("page6.form.userRequestPlaceholder")}
            rows={2}
            className="min-h-16 resize-y rounded-lg border border-border px-3 py-2.5 text-sm leading-5 outline-none transition focus:border-accent focus:ring-2 focus:ring-accent/10"
          />
        </div>
        <div className="flex flex-col gap-1">
          <label className="label-caps">{t("page6.form.sourceTitle")}</label>
          <input
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder={t("page6.form.sourceTitlePlaceholder")}
            className="rounded-lg border border-border px-3 py-2 text-xs outline-none transition focus:border-accent focus:ring-2 focus:ring-accent/10"
          />
        </div>
        <div className="flex flex-col gap-1">
          <div className="flex items-center justify-between">
            <label className="label-caps">{t("page6.form.sourceText")}</label>
            <label className="flex w-fit cursor-pointer items-center gap-1.5 rounded border border-border px-2 py-1 text-[11px] font-medium text-ink-muted hover:bg-surface-sunken">
              <UploadCloud size={12} aria-hidden />
              {uploadMutation.isPending ? "…" : t("page6.form.sourceText")}
              <input
                type="file"
                accept=".md,.txt"
                className="hidden"
                disabled={uploadMutation.isPending}
                onChange={async (e) => {
                  const file = e.target.files?.[0];
                  e.target.value = "";
                  if (!file) return;
                  const text = await file.text();
                  setSourceText(text);
                }}
              />
            </label>
          </div>
          <textarea
            value={sourceText}
            onChange={(e) => setSourceText(e.target.value)}
            placeholder={t("page6.form.sourceTextPlaceholder")}
            rows={8}
            className="min-h-40 resize-y rounded-lg border border-border px-3 py-2.5 font-mono text-xs leading-5 outline-none transition focus:border-accent focus:ring-2 focus:ring-accent/10"
          />
          <p className="text-[11px] text-ink-faint">{t("page6.form.pdfNotSupported")}</p>
        </div>
        <div className="grid gap-3 sm:grid-cols-2">
          <div className="flex flex-1 flex-col gap-1">
            <label className="label-caps">{t("page6.form.engineeringGoal")}</label>
            <input
              value={engineeringGoal}
              onChange={(e) => setEngineeringGoal(e.target.value)}
              placeholder={t("page6.form.engineeringGoalPlaceholder")}
              className="rounded-lg border border-border px-3 py-2 text-xs outline-none transition focus:border-accent focus:ring-2 focus:ring-accent/10"
            />
          </div>
          <div className="flex flex-1 flex-col gap-1">
            <label className="label-caps">{t("page6.form.targetOrganism")}</label>
            <input
              value={organism}
              onChange={(e) => setOrganism(e.target.value)}
              className="rounded-lg border border-border px-3 py-2 text-xs outline-none transition focus:border-accent focus:ring-2 focus:ring-accent/10"
            />
          </div>
        </div>
        {submitMutation.isError && <p className="text-[11px] text-state-risk">{String(submitMutation.error)}</p>}
        <button
          disabled={!canSubmit}
          onClick={() => submitMutation.mutate()}
          className="mt-1 w-full rounded-lg bg-accent px-4 py-2.5 text-sm font-medium text-white shadow-sm transition hover:brightness-95 disabled:opacity-40"
        >
          {submitMutation.isPending ? t("page6.form.submitting") : t("page6.form.submit")}
        </button>
      </div>
    </section>
  );
}

function runStatusBadge(status: RunResult["status"]): BadgeStatus {
  switch (status) {
    case "CREATED":
      return "not_started";
    case "RUNNING":
      return "active";
    case "WAITING_REVIEW":
      return "waiting_for_human";
    case "COMPLETED":
      return "completed";
    case "FAILED":
      return "failed";
    default:
      return "unclear";
  }
}

function governanceBadge(value: string): BadgeStatus {
  if (value === "allowed") return "approved";
  if (value === "review") return "waiting_for_human";
  if (value === "blocked") return "blocked";
  return "unclear";
}

function StepProgress({ stepStates }: { stepStates: Record<string, string> }) {
  const { t } = useI18n();
  const entries = Object.entries(stepStates).sort(([a], [b]) => a.localeCompare(b));
  return (
    <section className="panel p-3">
      <h3 className="label-caps mb-2">{t("page6.progressTitle")}</h3>
      <div className="flex flex-wrap gap-1.5">
        {entries.map(([step, state]) => (
          <span
            key={step}
            className={`rounded px-2 py-1 text-[11px] font-medium ${
              state === "SUCCESS" ? "bg-emerald-50 text-emerald-700"
              : state === "SKIPPED" ? "bg-surface-sunken text-ink-faint"
              : state === "REVIEW_REQUIRED" ? "bg-amber-50 text-amber-700"
              : state === "FAILED" || state === "BLOCKED" ? "bg-red-50 text-state-risk"
              : "bg-accent/10 text-accent"
            }`}
          >
            {step.replace(/^step\d+_/, "")}: {state}
          </span>
        ))}
      </div>
    </section>
  );
}

function derivationLabel(t: ReturnType<typeof useI18n>["t"], derivationType: string): string {
  switch (derivationType) {
    case "explicit_in_source":
      return t("page6.derivationExplicit");
    case "normalized_from_source":
      return t("page6.derivationNormalized");
    case "cross_source_synthesis":
      return t("page6.derivationSynthesis");
    case "model_inference":
      return t("page6.derivationInference");
    default:
      return derivationType;
  }
}

function PrincipleCard({ p }: { p: EngineeringPrincipleView }) {
  const { t } = useI18n();
  return (
    <li className="rounded-lg border border-border p-3 text-xs">
      <div className="flex items-start justify-between gap-2">
        <p className="font-medium text-ink">{p.nameEn || p.nameZh || p.id}</p>
        <span className={`shrink-0 rounded px-1.5 py-0.5 text-[10px] font-medium ${p.derivationType === "model_inference" ? "bg-amber-50 text-amber-700" : "bg-emerald-50 text-emerald-700"}`}>
          {derivationLabel(t, p.derivationType)}
        </span>
      </div>
      {p.definition && <p className="mt-1.5 text-ink-muted">{p.definition}</p>}
      {p.triggerConditions.length > 0 && (
        <p className="mt-1.5"><span className="font-medium text-ink-faint">{t("page6.trigger")}: </span>{p.triggerConditions.join("; ")}</p>
      )}
      {p.recommendedActions.length > 0 && (
        <p className="mt-1"><span className="font-medium text-ink-faint">{t("page6.actions")}: </span>{p.recommendedActions.join("; ")}</p>
      )}
      {p.alternatives.length > 0 && (
        <p className="mt-1 text-ink-faint"><span className="font-medium">{t("page6.alternatives")}: </span>{p.alternatives.join("; ")}</p>
      )}
      {p.doNotGeneralizeTo.length > 0 && (
        <p className="mt-1 text-state-caution"><span className="font-medium">{t("page6.doNotGeneralize")}: </span>{p.doNotGeneralizeTo.join("; ")}</p>
      )}
      <div className="mt-2 flex flex-wrap items-center gap-2 text-[11px] text-ink-faint">
        {p.confidence !== null && <span>{t("page6.confidence")}: {p.confidence.toFixed(2)}</span>}
        <span>{p.evidenceCount} {t("page6.evidenceCount")}</span>
        {p.requiresHumanReview && <span className="font-medium text-amber-700">{t("page6.needsHumanReview")}</span>}
      </div>
    </li>
  );
}

function ObjectCard({ o }: { o: KnowledgeObjectView }) {
  const { t } = useI18n();
  return (
    <li className="rounded-lg border border-border p-3 text-xs">
      <div className="flex items-start justify-between gap-2">
        <p className="font-medium text-ink">{o.nameEn || o.nameZh || o.id}</p>
        <span className={`shrink-0 rounded px-1.5 py-0.5 text-[10px] font-medium ${o.derivationType === "model_inference" ? "bg-amber-50 text-amber-700" : "bg-emerald-50 text-emerald-700"}`}>
          {derivationLabel(t, o.derivationType)}
        </span>
      </div>
      {o.definition && <p className="mt-1.5 text-ink-muted">{o.definition}</p>}
      <div className="mt-2 flex flex-wrap items-center gap-2 text-[11px] text-ink-faint">
        {o.confidence !== null && <span>{t("page6.confidence")}: {o.confidence.toFixed(2)}</span>}
        <span>{o.evidenceCount} {t("page6.evidenceCount")}</span>
        {o.requiresHumanReview && <span className="font-medium text-amber-700">{t("page6.needsHumanReview")}</span>}
      </div>
    </li>
  );
}

function CategorySection({ titleKey, items, render, emptyKey }: { titleKey: Parameters<ReturnType<typeof useI18n>["t"]>[0]; items: unknown[]; render: (item: never, i: number) => JSX.Element; emptyKey?: Parameters<ReturnType<typeof useI18n>["t"]>[0] }) {
  const { t } = useI18n();
  if (items.length === 0 && !emptyKey) return null;
  return (
    <section className="panel p-3">
      <h3 className="label-caps mb-2 flex items-center justify-between">
        <span>{t(titleKey)}</span>
        <span className="rounded-full bg-surface-sunken px-2 py-0.5 text-[11px] text-ink-muted">{items.length}</span>
      </h3>
      {items.length === 0 ? (
        <p className="text-[11px] text-ink-faint">{emptyKey ? t(emptyKey) : ""}</p>
      ) : (
        <ul className="flex flex-col gap-2">{items.map((item, i) => render(item as never, i))}</ul>
      )}
    </section>
  );
}

function RunView({ run }: { run: RunResult }) {
  const { t } = useI18n();
  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center gap-2">
        <StatusBadge status={runStatusBadge(run.status)} label={t(`page5.status.${run.status}`)} />
        <span className="font-mono text-[11px] text-ink-faint">{run.taskId}</span>
      </div>

      {run.errors.length > 0 && (
        <div className="panel flex flex-col gap-1 border-red-300 bg-red-50 p-3">
          <h3 className="label-caps flex items-center gap-1 text-state-risk">
            <AlertTriangle size={12} /> {t("page5.errorsTitle")}
          </h3>
          {run.errors.map((e, i) => (
            <p key={i} className="text-[11px] text-state-risk">
              {e.step ? `${e.step}: ` : ""}
              {String(e.message ?? e.error_code ?? JSON.stringify(e))}
            </p>
          ))}
        </div>
      )}

      {Object.keys(run.stepStates).length > 0 && <StepProgress stepStates={run.stepStates} />}

      {run.governance && (
        <section className="panel p-3">
          <h3 className="label-caps mb-2 flex items-center gap-1"><ShieldCheck size={12} /> {t("page6.governance")}</h3>
          <div className="flex flex-wrap gap-1.5">
            {Object.entries(run.governance).map(([key, value]) => (
              <StatusBadge key={key} status={governanceBadge(String(value))} label={`${key}: ${value}`} />
            ))}
          </div>
          {run.qualityReport?.overall_status ? (
            <p className="mt-2 text-[11px] text-ink-faint">{t("page6.qualityStatus")}: {String(run.qualityReport.overall_status)}</p>
          ) : null}
        </section>
      )}

      <CategorySection titleKey="page6.principles" items={run.engineeringPrinciples} emptyKey="page6.noPrinciplesYet" render={(p, i) => <PrincipleCard key={i} p={p as EngineeringPrincipleView} />} />
      <div className="grid gap-4 md:grid-cols-2">
        <CategorySection titleKey="page6.concepts" items={[...run.concepts, ...run.mechanisms]} render={(o, i) => <ObjectCard key={i} o={o as KnowledgeObjectView} />} />
        <CategorySection titleKey="page6.decisionRules" items={run.decisionRules} render={(o, i) => <ObjectCard key={i} o={o as KnowledgeObjectView} />} />
        <CategorySection titleKey="page6.designPatterns" items={run.designPatterns} render={(o, i) => <ObjectCard key={i} o={o as KnowledgeObjectView} />} />
        <CategorySection titleKey="page6.failurePatterns" items={run.failurePatterns} render={(o, i) => <ObjectCard key={i} o={o as KnowledgeObjectView} />} />
      </div>

      {run.status === "RUNNING" && Object.keys(run.stepStates).length === 0 && <EmptyState variant="loading" />}
      {run.status === "COMPLETED" && run.engineeringPrinciples.length === 0 && run.concepts.length === 0 && (
        <EmptyState variant="no_result" title={t("page6.noRunYet")} />
      )}
    </div>
  );
}
