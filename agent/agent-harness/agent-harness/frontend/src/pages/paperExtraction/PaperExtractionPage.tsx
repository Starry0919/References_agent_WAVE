import { useEffect, useRef, useState } from "react";
import { Link, useNavigate, useParams, useSearchParams } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { UploadCloud, FlaskConical, ShieldCheck, AlertTriangle, Dna, ChevronDown, ChevronRight, FileSearch, History, Trash2, BookOpenCheck, Microscope, Info, HelpCircle, ExternalLink, Columns2 } from "lucide-react";
import {
  deleteRun, getRun, listRuns, submitRun, uploadPaper,
  type DetailPanel, type EvidenceItem, type ExtractionSummary,
  type K12AdaptationItem, type PaperExtractionSummary, type RunHistoryItem, type RunResult, type StepCard,
} from "@/api/paperExtraction";
import { CompareTab, DesignTab, paperIdentityTitle, QualityTab, ReasoningTab, TabButton } from "@/pages/paperExtraction/PaperResultTabs";
import { EmptyState } from "@/components/common/EmptyState";
import { StatusBadge, type BadgeStatus } from "@/components/common/StatusBadge";
import { useI18n } from "@/lib/i18n";

/**
 * Paper Experimental Design Extraction (harness/api/paper_extraction.py,
 * real, vendoring the 13-skill pipeline). Submit a research request against
 * a literature source, poll the async task, render Skill13's frontend_view
 * (summary / DBTL step cards / evidence / K12 adaptation / risk /
 * governance) once it lands. `?task=` in the URL keeps the run
 * refreshable, matching the Trust & Provenance page's `?run=` convention.
 */
export function PaperExtractionPage({ embedded = false, projectId }: { embedded?: boolean; projectId?: string }) {
  const { t } = useI18n();
  const [params, setParams] = useSearchParams();
  const taskId = params.get("task");
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const { projectId: routeProjectId } = useParams<{ projectId: string }>();
  const resolvedProjectId = projectId ?? routeProjectId;

  // `ensure_task_saved_as_evidence` (harness/api/paper_extraction.py::get_task)
  // runs synchronously inside the same poll that first reports COMPLETED,
  // but swallows its own exceptions (logged server-side only) - if that one
  // save attempt fails, `evidenceSourceId` stays null in this response with
  // no client-visible error. Since polling used to stop the instant status
  // left RUNNING/CREATED, that failure was permanent from the frontend's
  // point of view: no later poll ever gave the (idempotent) save a second
  // try, so a single-paper run could finish with no "详情" button and no
  // auto-navigate. Keep polling a bounded number of extra times specifically
  // while that save is still pending, so a transient failure self-heals.
  const pendingSaveRetries = useRef(0);
  const runQuery = useQuery({
    queryKey: ["paper-extraction-run", taskId],
    queryFn: () => getRun(taskId as string),
    enabled: !!taskId,
    refetchInterval: (query) => {
      const data = query.state.data;
      const status = data?.status;
      if (status === "RUNNING" || status === "CREATED" || status === undefined) return 3000;
      if (status === "COMPLETED") {
        const papers = data?.extractionSummary?.papers ?? [];
        const savePending = papers.length === 1 && !papers[0].evidenceSourceId;
        if (savePending && pendingSaveRetries.current < 5) {
          pendingSaveRetries.current += 1;
          return 2000;
        }
      }
      return false;
    },
  });

  useEffect(() => {
    pendingSaveRetries.current = 0;
  }, [taskId]);

  // Requirement: once a single-paper run finishes, land the user straight
  // on that paper's new literature-evidence detail page instead of leaving
  // them looking at the same run view. Guarded by `navigatedForTaskId` so
  // this fires exactly once per task - refetches after completion (the
  // poll keeps running a few seconds past COMPLETED) must not re-navigate
  // if the user has since clicked away. Multi-paper runs are intentionally
  // left alone here: there is no single correct destination, so the user
  // picks via each paper's own "详情" button instead (see PaperResultCard).
  const navigatedForTaskId = useRef<string | null>(null);
  useEffect(() => {
    const run = runQuery.data;
    if (!run || !resolvedProjectId || !taskId) return;
    if (run.status !== "COMPLETED") return;
    if (navigatedForTaskId.current === taskId) return;
    const papers = run.extractionSummary?.papers ?? [];
    if (papers.length !== 1) return;
    const sourceId = papers[0].evidenceSourceId;
    if (!sourceId) return;
    navigatedForTaskId.current = taskId;
    navigate(`/projects/${resolvedProjectId}/evidence/${sourceId}`);
  }, [runQuery.data, resolvedProjectId, taskId, navigate]);

  // Ask #5: `?task=` is the only pointer to the active run - leaving this
  // page (any client-side navigation away and back) drops that URL param
  // and previously fell straight back to a blank SubmissionForm, even
  // though the backend task (thread-pool backed, see harness/paper_
  // extraction/service.py) kept running the whole time. History (backed
  // by a real `GET /api/paper-extraction/tasks`, not just this browser's
  // localStorage) is shown whenever no task is selected, so returning here
  // always has somewhere to click back into instead of looking reset.
  const historyQuery = useQuery({
    // Scoped to this project (harness/paper_extraction/service.py::list_tasks
    // already supports filtering by project_id) - without projectId in the
    // key/call, every project's "history" showed every OTHER project's runs
    // too, since project A's cached list would otherwise satisfy project B's
    // query.
    queryKey: ["paper-extraction-history", projectId],
    queryFn: () => listRuns(projectId),
    enabled: !taskId,
    refetchInterval: !taskId ? 5000 : false,
  });

  // Merge into the existing search params rather than replacing them
  // outright (`setParams({...})` clobbers the whole query string) - this
  // page is always embedded as a tab of KnowledgePage sharing one URL
  // (`?tab=extraction`), so a bare `setParams({task: id})` was dropping
  // `tab` and silently bouncing the user to KnowledgePage's default tab
  // ("知识主张"/Knowledge Claims) right after submitting a run. Matches the
  // merge pattern KnowledgeDistillationPage already uses for the same
  // shared-params situation.
  const startNew = () => {
    const next = new URLSearchParams(params);
    next.delete("task");
    setParams(next, { replace: true });
    queryClient.removeQueries({ queryKey: ["paper-extraction-run"] });
  };

  const [deleteTarget, setDeleteTarget] = useState<RunHistoryItem | null>(null);
  const deleteMutation = useMutation({
    mutationFn: (id: string) => deleteRun(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["paper-extraction-history"] });
      setDeleteTarget(null);
    },
  });

  return (
    <div className={`flex min-h-0 flex-1 flex-col overflow-y-auto ${embedded ? "" : "p-4"}`}>
      <div className="mb-5 flex items-start justify-between gap-6 rounded-xl border border-border bg-surface px-5 py-4 shadow-sm">
        <div className="flex min-w-0 items-start gap-3">
          <div className="mt-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-accent/10 text-accent">
            <FileSearch size={19} aria-hidden />
          </div>
          <div className="min-w-0">
            <h1 className="text-lg font-semibold text-ink">{t("page5.title")}</h1>
            <p className="mt-1 max-w-4xl text-sm leading-5 text-ink-muted">{t("page5.subtitle")}</p>
          </div>
        </div>
        {taskId && (
          <button onClick={startNew} className="flex-shrink-0 rounded border border-border px-2.5 py-1.5 text-xs font-medium text-ink-muted hover:bg-surface-sunken">
            {t("page5.startNewRun")}
          </button>
        )}
      </div>

      {!taskId && (
        <div className="grid items-start gap-5 xl:grid-cols-[minmax(440px,0.9fr)_minmax(520px,1.1fr)]">
          <SubmissionForm
            projectId={projectId}
            onSubmitted={(id) => {
              const next = new URLSearchParams(params);
              next.set("task", id);
              setParams(next, { replace: true });
              queryClient.invalidateQueries({ queryKey: ["paper-extraction-history"] });
            }}
          />
          <div className="min-w-0">
            <RunHistory
              items={historyQuery.data ?? []}
              isLoading={historyQuery.isLoading}
              onSelect={(id) => {
                const next = new URLSearchParams(params);
                next.set("task", id);
                setParams(next, { replace: true });
              }}
              onDeleteRequest={(item) => setDeleteTarget(item)}
            />
          </div>
        </div>
      )}

      {taskId && runQuery.isLoading && <EmptyState variant="loading" />}
      {taskId && runQuery.isError && <EmptyState variant="failed" detail={String(runQuery.error)} />}
      {taskId && runQuery.data && <RunView run={runQuery.data} />}

      {deleteTarget && (
        <div className="fixed inset-0 z-30 flex items-center justify-center bg-black/40 p-4">
          <div className="panel w-full max-w-sm p-4">
            <p className="text-sm font-medium text-ink">{t("page5.historyDeleteConfirmTitle")}</p>
            <p className="mt-1 line-clamp-2 text-xs text-ink-muted">{deleteTarget.userRequest}</p>
            <p className="mt-2 text-xs text-ink-muted">{t("page5.historyDeleteConfirmDetail")}</p>
            {deleteMutation.isError && <p className="mt-2 text-xs text-state-risk">{String(deleteMutation.error)}</p>}
            <div className="mt-3 flex justify-end gap-2">
              <button
                onClick={() => setDeleteTarget(null)}
                disabled={deleteMutation.isPending}
                className="rounded px-3 py-1.5 text-xs text-ink-muted"
              >
                {t("page5.historyDeleteCancel")}
              </button>
              <button
                onClick={() => deleteMutation.mutate(deleteTarget.taskId)}
                disabled={deleteMutation.isPending}
                className="rounded bg-state-risk px-3 py-1.5 text-xs font-medium text-white disabled:opacity-40"
              >
                {deleteMutation.isPending ? t("page5.historyDeleting") : t("page5.historyDelete")}
              </button>
            </div>
          </div>
        </div>
      )}
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

function RunHistory({
  items,
  isLoading,
  onSelect,
  onDeleteRequest,
}: {
  items: RunHistoryItem[];
  isLoading: boolean;
  onSelect: (taskId: string) => void;
  onDeleteRequest: (item: RunHistoryItem) => void;
}) {
  const { t } = useI18n();
  return (
    <section className="panel flex min-h-[360px] flex-col overflow-hidden">
      <div className="flex items-center justify-between border-b border-border px-4 py-3.5">
        <div className="flex items-center gap-2">
          <History size={16} className="text-accent" aria-hidden />
          <h3 className="text-sm font-semibold text-ink">{t("page5.historyTitle")}</h3>
        </div>
        {items.length > 0 && <span className="rounded-full bg-surface-sunken px-2 py-0.5 text-[11px] text-ink-muted">{items.length}</span>}
      </div>
      <div className="flex flex-1 flex-col p-3">
      {isLoading && <div className="flex min-h-56 items-center justify-center"><EmptyState variant="loading" /></div>}
      {!isLoading && items.length === 0 && <div className="flex min-h-56 items-center justify-center"><p className="text-xs text-ink-faint">{t("page5.historyEmpty")}</p></div>}
      {items.length > 0 && (
        <ul className="flex max-h-[520px] flex-col gap-2 overflow-y-auto pr-1">
          {items.map((item) => {
            const deletable = !["created", "running"].includes(item.status.toLowerCase());
            return (
              <li key={item.taskId} className="group relative">
                <button
                  onClick={() => onSelect(item.taskId)}
                  className={`flex w-full flex-col gap-2 rounded-lg border border-border bg-surface px-3.5 py-3 text-left text-xs transition hover:border-accent/40 hover:bg-surface-sunken ${deletable ? "pr-9" : ""}`}
                >
                  <div className="flex items-center justify-between gap-2">
                    <span className="line-clamp-2 pr-2 font-medium leading-5 text-ink">{item.userRequest}</span>
                    <StatusBadge status={historyStatusBadge(item.status)} label={t(`page5.status.${item.status.toUpperCase()}` as Parameters<ReturnType<typeof useI18n>["t"]>[0])} />
                  </div>
                  <div className="flex items-center gap-2 text-[11px] text-ink-faint">
                    <span className="font-mono">{item.taskId}</span>
                    <span>{item.organism} · {item.strain}</span>
                    <span>{new Date(item.submittedAt * 1000).toLocaleString()}</span>
                  </div>
                </button>
                {deletable && (
                  <button
                    aria-label={t("page5.historyDelete")}
                    onClick={(e) => {
                      e.stopPropagation();
                      onDeleteRequest(item);
                    }}
                    className="absolute right-2 top-2.5 rounded p-1.5 text-ink-faint opacity-0 transition hover:bg-surface-sunken hover:text-state-risk group-hover:opacity-100 group-focus-within:opacity-100"
                  >
                    <Trash2 size={13} aria-hidden />
                  </button>
                )}
              </li>
            );
          })}
        </ul>
      )}
      </div>
    </section>
  );
}

function SubmissionForm({ onSubmitted, projectId }: { onSubmitted: (taskId: string) => void; projectId?: string }) {
  const { t } = useI18n();
  const [userRequest, setUserRequest] = useState("");
  const [organism, setOrganism] = useState("");
  const [strain, setStrain] = useState("");
  const [sourceType, setSourceType] = useState<"auto_search" | "upload" | "doi" | "textbook">("auto_search");
  const [files, setFiles] = useState<string[]>([]);
  const [fileNames, setFileNames] = useState<string[]>([]);
  const [doiText, setDoiText] = useState("");

  const uploadMutation = useMutation({
    mutationFn: uploadPaper,
    onSuccess: (res) => {
      setFiles((prev) => [...prev, res.path]);
      setFileNames((prev) => [...prev, res.filename]);
    },
  });

  const submitMutation = useMutation({
    mutationFn: () =>
      submitRun({
        projectId,
        userRequest,
        organism,
        strain,
        sourceType,
        files: sourceType === "upload" || sourceType === "textbook" ? files : [],
        doi: sourceType === "doi" ? doiText.split("\n").map((v) => v.trim()).filter(Boolean) : [],
      }),
    onSuccess: (res) => onSubmitted(res.task_id),
  });

  const canSubmit =
    userRequest.trim().length > 0 &&
    (!["upload", "textbook"].includes(sourceType) || files.length > 0) &&
    (sourceType !== "doi" || doiText.trim().length > 0) &&
    !submitMutation.isPending;

  return (
    <section className="panel flex min-w-0 flex-col overflow-hidden">
      <div className="flex items-center gap-2 border-b border-border px-4 py-3.5">
        <FlaskConical size={16} className="text-accent" aria-hidden />
        <h2 className="text-sm font-semibold text-ink">{t("page5.form.userRequest")}</h2>
      </div>
      <div className="flex flex-col gap-4 p-4">
      <div className="flex flex-col gap-1">
        <label className="label-caps">{t("page5.form.userRequest")}</label>
        <textarea
          value={userRequest}
          onChange={(e) => setUserRequest(e.target.value)}
          placeholder={t("page5.form.userRequestPlaceholder")}
          rows={4}
          className="min-h-28 resize-y rounded-lg border border-border px-3 py-2.5 text-sm leading-5 outline-none transition focus:border-accent focus:ring-2 focus:ring-accent/10"
        />
      </div>
      <div className="grid gap-3 sm:grid-cols-2">
        <div className="flex flex-1 flex-col gap-1">
          <label className="label-caps">{t("page5.form.organism")}</label>
          <input value={organism} onChange={(e) => setOrganism(e.target.value)} className="rounded-lg border border-border px-3 py-2 text-xs outline-none transition focus:border-accent focus:ring-2 focus:ring-accent/10" />
        </div>
        <div className="flex flex-1 flex-col gap-1">
          <label className="label-caps">{t("page5.form.strain")}</label>
          <input value={strain} onChange={(e) => setStrain(e.target.value)} className="rounded-lg border border-border px-3 py-2 text-xs outline-none transition focus:border-accent focus:ring-2 focus:ring-accent/10" />
        </div>
      </div>
      <div className="flex flex-col gap-1">
        <label className="label-caps">{t("page5.form.sourceType")}</label>
        <select value={sourceType} onChange={(e) => setSourceType(e.target.value as typeof sourceType)} className="rounded-lg border border-border bg-surface px-3 py-2 text-xs outline-none transition focus:border-accent focus:ring-2 focus:ring-accent/10">
          <option value="auto_search">{t("page5.form.sourceAutoSearch")}</option>
          <option value="upload">{t("page5.form.sourceUpload")}</option>
          <option value="textbook">{t("page5.form.sourceTextbook")}</option>
          <option value="doi">{t("page5.form.sourceDoi")}</option>
        </select>
      </div>
        {(sourceType === "upload" || sourceType === "textbook") && (
        <div className="flex flex-col gap-1.5">
          <label className="flex w-fit cursor-pointer items-center gap-1.5 rounded border border-border px-2.5 py-1.5 text-xs font-medium text-ink-muted hover:bg-surface-sunken">
            <UploadCloud size={13} aria-hidden />
            {uploadMutation.isPending ? t("page5.form.uploading") : t("page5.form.uploadButton")}
            <input
              type="file"
              accept="application/pdf"
              className="hidden"
              disabled={uploadMutation.isPending}
              onChange={(e) => {
                const file = e.target.files?.[0];
                if (file) uploadMutation.mutate(file);
                e.target.value = "";
              }}
            />
          </label>
          {fileNames.length > 0 && (
            <p className="text-[11px] text-ink-faint">
              {fileNames.length} {t("page5.form.filesAttached")}: {fileNames.join(", ")}
            </p>
          )}
        </div>
      )}
      {sourceType === "doi" && (
        <div className="flex flex-col gap-1">
          <textarea
            value={doiText}
            onChange={(e) => setDoiText(e.target.value)}
            placeholder={t("page5.form.doiPlaceholder")}
            rows={2}
            className="rounded border border-border px-2 py-1.5 font-mono text-xs"
          />
        </div>
      )}
      {submitMutation.isError && <p className="text-[11px] text-state-risk">{String(submitMutation.error)}</p>}
      <button
        disabled={!canSubmit}
        onClick={() => submitMutation.mutate()}
        className="mt-1 w-full rounded-lg bg-accent px-4 py-2.5 text-sm font-medium text-white shadow-sm transition hover:brightness-95 disabled:opacity-40"
      >
        {submitMutation.isPending ? t("page5.form.submitting") : t("page5.form.submit")}
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

function RunView({ run }: { run: RunResult }) {
  const { t } = useI18n();
  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center gap-2">
        <StatusBadge status={runStatusBadge(run.status)} label={t(`page5.status.${run.status}`)} />
        <span className="font-mono text-[11px] text-ink-faint">{run.taskId}</span>
        <span className="text-[11px] text-ink-muted">
          {run.literatureCandidateCount} candidates · {run.experimentalDesignCount} designs
        </span>
      </div>

      {run.errors.length > 0 && (
        <div className="panel flex flex-col gap-1 border-red-300 bg-red-50 p-3">
          <h3 className="label-caps flex items-center gap-1 text-state-risk">
            <AlertTriangle size={12} /> {t("page5.errorsTitle")}
          </h3>
          {run.errors.map((e, i) => (
            <p key={i} className="text-[11px] text-state-risk">
              {e.skill ? `${e.skill}: ` : ""}
              {String(e.message ?? e.code ?? JSON.stringify(e))}
            </p>
          ))}
        </div>
      )}

      {Object.keys(run.skillStates).length > 0 && (
        <SkillProgress skillStates={run.skillStates} skillProgress={run.skillProgress} warnings={run.warnings} errors={run.errors} />
      )}

      {!run.frontendView && !run.extractionSummary?.papers.length && (run.status === "RUNNING" || run.status === "CREATED") && Object.keys(run.skillStates).length === 0 && (
        <EmptyState variant="loading" />
      )}
      {!run.frontendView && !run.extractionSummary?.papers.length && run.status === "FAILED" && <EmptyState variant="failed" />}

      {run.extractionSummary && run.extractionSummary.papers.length > 0 && <ExtractionResultSection summary={run.extractionSummary} />}

      {run.frontendView && (
        <>
          <SummaryCard view={run.frontendView} />
          <StepsSection stepCards={run.frontendView.stepCards} detailPanels={run.frontendView.detailPanels} />
          <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
            <EvidenceSection items={run.frontendView.evidence.items} />
            <K12Section items={run.frontendView.k12.items} />
          </div>
          <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
            <RiskSection risk={run.frontendView.risk} />
            <GovernanceSection governance={run.frontendView.governance} />
          </div>
        </>
      )}
    </div>
  );
}

/**
 * The primary results page for a completed (or in-progress) extraction:
 * for every paper, keeps the agent's own reasoning ("抽取思路" - how it
 * classified the article, which strains it found and why) visually
 * separate from the paper's own experimental design content ("实验设计
 * 思路" - objective/intervention/groups/conditions/outcomes, each with its
 * literal supporting quote). Independent human review (governance) is
 * shown as a non-blocking, informational panel - never a banner implying
 * the results below are unavailable or unapproved.
 */
function ExtractionResultSection({ summary }: { summary: ExtractionSummary }) {
  const { t } = useI18n();
  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between gap-2 border-b border-border pb-2">
        <h2 className="flex items-center gap-1.5 text-sm font-semibold text-ink">
          <Microscope size={15} className="text-accent" aria-hidden /> {t("page5.result.title")}
        </h2>
        <span className="text-[11px] text-ink-faint">
          {summary.papers.length} {t("page5.result.paperCount")}
        </span>
      </div>
      {summary.papers.map((paper) => (
        <PaperResultCard key={paper.paperId} paper={paper} />
      ))}
      {summary.reviewTasks.length > 0 && (
        <div className="panel flex items-start gap-2 border-border bg-surface-sunken p-3 text-[11px] text-ink-muted">
          <Info size={14} className="mt-0.5 shrink-0 text-ink-faint" aria-hidden />
          <div>
            <p className="font-medium text-ink-muted">{t("page5.result.independentReviewTitle")}</p>
            <p className="mt-0.5">{summary.governanceNote || t("page5.result.independentReviewHint")}</p>
            <p className="mt-1 text-ink-faint">
              {summary.reviewTasks.length} {t("page5.result.reviewTaskCount")}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

function PaperResultCard({ paper }: { paper: PaperExtractionSummary }) {
  const { t } = useI18n();
  const [tab, setTab] = useState<"reasoning" | "design" | "quality" | "compare">("reasoning");
  const { projectId } = useParams<{ projectId: string }>();
  const authors = paper.identity.authors.length > 0 ? paper.identity.authors.join(", ") : null;
  const metaBits = [authors, paper.identity.journal, paper.identity.year ? String(paper.identity.year) : null].filter(Boolean);
  return (
    <div className="panel flex flex-col gap-3 p-4">
      <div className="flex items-start justify-between gap-2">
        <div className="flex flex-col gap-1">
          <h3 className="text-sm font-semibold leading-5 text-ink">{paperIdentityTitle(paper, t)}</h3>
          <div className="flex flex-wrap items-center gap-x-2 gap-y-0.5 text-[11px] text-ink-faint">
            {metaBits.length > 0 && <span>{metaBits.join(" · ")}</span>}
            {paper.identity.doi && <span className="font-mono">DOI: {paper.identity.doi}</span>}
            <span className="font-mono">{paper.paperId}</span>
          </div>
        </div>
        {paper.evidenceSourceId && projectId && (
          <Link
            to={`/projects/${projectId}/evidence/${paper.evidenceSourceId}`}
            className="flex shrink-0 items-center gap-1 rounded border border-border px-2 py-1 text-[11px] font-medium text-ink-muted hover:bg-surface-sunken"
          >
            <ExternalLink size={11} aria-hidden />
            {t("common.viewDetail")}
          </Link>
        )}
      </div>

      <div className="flex gap-1 border-b border-border">
        <TabButton active={tab === "reasoning"} onClick={() => setTab("reasoning")} icon={<BookOpenCheck size={12} />} label={t("page5.result.tabReasoning")} />
        <TabButton active={tab === "design"} onClick={() => setTab("design")} icon={<FlaskConical size={12} />} label={t("page5.result.tabDesign")} badge={paper.hasDesignContent ? undefined : "!"} />
        <TabButton active={tab === "quality"} onClick={() => setTab("quality")} icon={<ShieldCheck size={12} />} label={t("page5.result.tabQuality")} />
        <TabButton active={tab === "compare"} onClick={() => setTab("compare")} icon={<Columns2 size={12} />} label={t("page5.result.tabCompare")} />
      </div>

      {tab === "reasoning" && <ReasoningTab paper={paper} />}
      {tab === "design" && <DesignTab paper={paper} />}
      {tab === "quality" && <QualityTab paper={paper} />}
      {tab === "compare" && <CompareTab paper={paper} />}
    </div>
  );
}

function skillStatusBadge(status: string): BadgeStatus {
  switch (status.toUpperCase()) {
    case "SUCCESS":
      return "completed";
    case "WARNING":
      return "partial";
    case "REVIEW_REQUIRED":
      return "waiting_for_human";
    case "RUNNING":
    case "IN_PROGRESS":
      return "active";
    case "FAILED":
    case "ERROR":
      return "failed";
    case "SKIPPED":
      return "absent";
    case "PENDING":
    case "NOT_STARTED":
      return "not_started";
    default:
      return "unclear";
  }
}

/** "skill07_experiment_extraction" -> "07 Experiment Extraction" - the
 * vendored pipeline's own step ids (`skillNN_name`), reused as the
 * display label rather than hand-maintaining a parallel list of the same
 * 13 names that would drift once the vendored module changes. Keys sort
 * lexicographically into the pipeline's real run order since NN is
 * zero-padded. */
export function skillLabel(skillId: string): string {
  const match = /^skill(\d+)_(.+)$/.exec(skillId);
  if (!match) return skillId;
  const [, num, name] = match;
  return `${num} ${name.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase())}`;
}

function SkillProgress({
  skillStates,
  skillProgress,
  warnings,
  errors,
}: {
  skillStates: Record<string, string>;
  skillProgress: Record<string, { completed: number; total: number }>;
  warnings: Array<{ skill: string; message: string; sourceCode?: string }>;
  errors: Array<{ skill?: string; message?: string; code?: string }>;
}) {
  const { t } = useI18n();
  const entries = Object.entries(skillStates).sort(([a], [b]) => a.localeCompare(b));
  return (
    <div className="flex flex-col gap-2">
      <h3 className="label-caps">{t("page5.progressTitle")}</h3>
      <ul className="flex flex-col gap-1">
        {entries.map(([skillId, status]) => {
          // Only present while this skill is still RUNNING (e.g. skill07
          // extracting papers one at a time, minutes each) - the engine
          // clears it once the stage finishes, so a finished/failed row
          // never shows a stale fraction.
          const progress = skillProgress[skillId];
          const label = progress && progress.total > 1 ? `${status} (${progress.completed}/${progress.total})` : status;
          const upperStatus = status.toUpperCase();
          const isWarning = upperStatus === "WARNING";
          const isReviewRequired = upperStatus === "REVIEW_REQUIRED";
          const isFailed = upperStatus === "FAILED";
          // Real per-warning messages (harness/paper_extraction's
          // engine.py now records each skill result's own `warnings`, not
          // just `errors`) - these are also what triggers REVIEW_REQUIRED
          // in the first place (skill01/08/09/12 always add a matching
          // warning alongside any review_request), so the same list covers
          // both statuses. Falls back to a generic hint only if this run
          // predates that (an old checkpoint with no `warnings` entries).
          const detail = warnings.filter((w) => w.skill === skillId).map((w) => w.message);
          // FAILED rows get their own error message inline too, not just in
          // the top-level errors panel - without this, "which stage broke
          // and why" required scrolling up and matching skill ids by eye.
          const failureDetail = errors.filter((e) => e.skill === skillId).map((e) => String(e.message ?? e.code ?? ""));
          const genericHint = isWarning
            ? t("page5.progress.warningHint")
            : isReviewRequired
              ? t("page5.progress.reviewRequiredHint")
              : undefined;
          const hint = isWarning || isReviewRequired ? (detail.length > 0 ? detail.join(" ") : genericHint) : undefined;
          const failureHint = isFailed && failureDetail.length > 0 ? failureDetail.join(" ") : undefined;
          return (
            <li key={skillId} className="flex flex-col gap-1 rounded border border-border bg-surface px-2.5 py-1.5 text-xs">
              <div className="flex items-center justify-between gap-2">
                <span className="text-ink">{skillLabel(skillId)}</span>
                <StatusBadge status={skillStatusBadge(status)} label={label} hint={hint ?? failureHint} />
              </div>
              {hint && (
                <p className="flex items-start gap-1 text-[11px] text-state-caution">
                  <HelpCircle size={12} className="mt-0.5 shrink-0" aria-hidden />
                  <span>{hint}</span>
                </p>
              )}
              {failureHint && (
                <p className="flex items-start gap-1 text-[11px] text-state-risk">
                  <AlertTriangle size={12} className="mt-0.5 shrink-0" aria-hidden />
                  <span>{failureHint}</span>
                </p>
              )}
            </li>
          );
        })}
      </ul>
    </div>
  );
}

function objectiveSourceLabel(source: string, t: (k: Parameters<ReturnType<typeof useI18n>["t"]>[0]) => string): string {
  if (source === "reported_in_literature") return t("page5.summary.objectiveSourceReported");
  if (source === "user_specified_not_literature_verified") return t("page5.summary.objectiveSourceUser");
  return t("page5.summary.objectiveSourceUnknown");
}

function SummaryCard({ view }: { view: NonNullable<RunResult["frontendView"]> }) {
  const { t } = useI18n();
  const s = view.summary;
  if (!s) return null;
  return (
    <div className="panel flex flex-col gap-2 p-4">
      <h2 className="text-sm font-semibold text-ink">{s.title}</h2>
      <div className="grid grid-cols-2 gap-x-4 gap-y-1.5 text-xs sm:grid-cols-3">
        <Field label={t("page5.summary.objective")} value={s.objective} hint={objectiveSourceLabel(s.objectiveSource, t)} />
        <Field label={t("page5.summary.targetSystem")} value={s.targetSystem} />
        <Field label={t("page5.summary.k12Compatibility")} value={s.k12Compatibility} />
        <Field label={t("page5.summary.confidence")} value={String(s.confidence)} />
        <Field label={t("page5.summary.qualityGrade")} value={s.qualityGrade} />
      </div>
    </div>
  );
}

function Field({ label, value, hint }: { label: string; value: string; hint?: string }) {
  return (
    <div>
      <div className="text-[10px] uppercase tracking-wide text-ink-faint">{label}</div>
      <div className="text-ink">{value}</div>
      {hint && <div className="text-[10px] italic text-ink-faint">{hint}</div>}
    </div>
  );
}

const PHASES: Array<StepCard["phase"]> = ["design", "build", "test", "learn"];

function StepsSection({ stepCards, detailPanels }: { stepCards: StepCard[]; detailPanels: DetailPanel[] }) {
  const { t } = useI18n();
  const [expanded, setExpanded] = useState<string | null>(null);
  const byId = new Map(detailPanels.map((p) => [p.stepId, p]));

  return (
    <div className="flex flex-col gap-2">
      <h3 className="label-caps flex items-center gap-1">
        <FlaskConical size={12} /> {t("page5.stepsTitle")}
      </h3>
      {stepCards.length === 0 && <EmptyState variant="first_use" title={t("page5.noStepsYet")} />}
      {stepCards.length > 0 && (
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {PHASES.map((phase) => (
            <div key={phase} className="flex flex-col gap-1.5">
              <div className="text-[11px] font-semibold uppercase tracking-wide text-ink-muted">{phase}</div>
              {stepCards
                .filter((c) => c.phase === phase)
                .map((card) => {
                  const isOpen = expanded === card.stepId;
                  const detail = byId.get(card.stepId);
                  return (
                    <div key={card.stepId} className="panel flex flex-col gap-1 p-2 text-xs">
                      <button className="flex items-start gap-1 text-left" onClick={() => setExpanded(isOpen ? null : card.stepId)}>
                        {isOpen ? <ChevronDown size={13} className="mt-0.5 flex-shrink-0" /> : <ChevronRight size={13} className="mt-0.5 flex-shrink-0" />}
                        <span className="font-medium text-ink">{card.title}</span>
                      </button>
                      <p className="pl-4 text-[11px] text-ink-muted">{card.shortDescription}</p>
                      {card.sourceType && (
                        <span className="ml-4 w-fit rounded bg-surface-sunken px-1.5 py-0.5 text-[10px] text-ink-faint">
                          {card.sourceType === "literature" ? t("page5.literature") : t("page5.aiGenerated")}
                        </span>
                      )}
                      {isOpen && detail && <StepDetail detail={detail} />}
                    </div>
                  );
                })}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function StepDetail({ detail }: { detail: DetailPanel }) {
  const { t } = useI18n();
  const why = [...detail.why.literatureReason, ...detail.why.engineeringReason, ...detail.why.aiReason].filter(Boolean);
  return (
    <div className="ml-4 mt-1 flex flex-col gap-1 border-l border-border pl-2 text-[11px] text-ink-muted">
      <p>
        <span className="font-medium text-ink-faint">{t("page5.what")}: </span>
        {detail.what}
      </p>
      {why.length > 0 && (
        <p>
          <span className="font-medium text-ink-faint">{t("page5.why")}: </span>
          {why.join("; ")}
        </p>
      )}
      <p>
        <span className="font-medium text-ink-faint">{t("page5.how")}: </span>
        {detail.how.operation}
      </p>
      {detail.risk.length > 0 && (
        <p>
          <span className="font-medium text-ink-faint">{t("page5.risk")}: </span>
          {detail.risk.join("; ")}
        </p>
      )}
      <p>
        <span className="font-medium text-ink-faint">{t("page5.validation")}: </span>
        {detail.validationCheckpoint}
      </p>
      {detail.evidenceIds.length > 0 && (
        <p className="font-mono text-[10px] text-ink-faint">{t("page5.evidenceTitle")}: {detail.evidenceIds.join(", ")}</p>
      )}
    </div>
  );
}

function EvidenceSection({ items }: { items: EvidenceItem[] }) {
  const { t } = useI18n();
  return (
    <div className="flex flex-col gap-2">
      <h3 className="label-caps">
        {t("page5.evidenceTitle")} ({items.length} {t("page5.evidenceCount")})
      </h3>
      {items.length === 0 && <EmptyState variant="unavailable" />}
      <ul className="flex max-h-64 flex-col gap-1.5 overflow-y-auto">
        {items.map((e) => (
          <li key={e.evidenceId} className="panel p-2 text-[11px]">
            <div className="flex items-center justify-between text-ink-faint">
              <span className="font-mono">{e.evidenceId}</span>
              <span>{e.paper} {e.page != null ? `· p.${e.page}` : ""}</span>
            </div>
            <p className="mt-0.5 text-ink-muted">&ldquo;{e.quote}&rdquo;</p>
          </li>
        ))}
      </ul>
    </div>
  );
}

function K12Section({ items }: { items: K12AdaptationItem[] }) {
  const { t } = useI18n();
  return (
    <div className="flex flex-col gap-2">
      <h3 className="label-caps flex items-center gap-1">
        <Dna size={12} /> {t("page5.k12Title")}
      </h3>
      {items.length === 0 && <EmptyState variant="unavailable" />}
      <ul className="flex flex-col gap-1.5">
        {items.map((item) => (
          <li key={item.paperId} className="panel p-2 text-[11px]">
            <div className="flex items-center justify-between">
              <span className="font-mono text-ink-faint">{item.paperId}</span>
              <span className="text-ink">{item.compatibility}</span>
            </div>
            <p className="text-ink-muted">{item.transferability} · {String(item.confidence)}</p>
            {item.validationRequired.length > 0 && <p className="text-ink-faint">{item.validationRequired.join("; ")}</p>}
          </li>
        ))}
      </ul>
    </div>
  );
}

function RiskSection({ risk }: { risk: NonNullable<RunResult["frontendView"]>["risk"] }) {
  const { t } = useI18n();
  return (
    <div className="flex flex-col gap-2">
      <h3 className="label-caps flex items-center gap-1">
        <AlertTriangle size={12} /> {t("page5.riskTitle")} — {t("page5.riskLevel")}: {risk.riskLevel}
      </h3>
      {risk.risks.length === 0 && <EmptyState variant="unavailable" />}
      <ul className="flex flex-col gap-1">
        {risk.risks.map((r, i) => (
          <li key={i} className="panel p-2 text-[11px]">
            <span className="font-medium text-ink">{r.category}</span>: <span className="text-ink-muted">{r.detail}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

function GovernanceSection({ governance }: { governance: NonNullable<RunResult["frontendView"]>["governance"] }) {
  const { t } = useI18n();
  return (
    <div className="flex flex-col gap-2">
      <h3 className="label-caps flex items-center gap-1">
        <ShieldCheck size={12} /> {t("page5.governanceTitle")}
      </h3>
      <div className="panel flex flex-wrap items-center gap-2 p-2 text-[11px]">
        <span>QC: {governance.qcStatus}</span>
        <span>Review: {governance.reviewStatus}</span>
        <span>{governance.publicationStatus}</span>
        {governance.displayStates.map((s) => (
          <span key={s} className="rounded bg-surface-sunken px-1.5 py-0.5 text-ink-faint">{s}</span>
        ))}
      </div>
    </div>
  );
}
