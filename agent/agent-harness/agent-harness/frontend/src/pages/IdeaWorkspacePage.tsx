import { useMutation, useQueries, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  ArrowRight,
  BookOpen,
  CheckCircle2,
  ChevronRight,
  CircleDashed,
  Dna,
  GitBranch,
  Lightbulb,
  Search,
  Send,
  ShieldQuestion,
  Sparkles,
  WandSparkles,
} from "lucide-react";
import { useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { listIdeas, type ProjectIdea } from "@/api/ideas";
import { getRun, listRuns, submitRun, type ExtractedIdea } from "@/api/paperExtraction";
import { EmptyState } from "@/components/common/EmptyState";
import { StatusBadge } from "@/components/common/StatusBadge";
import { useI18n, type DictKey } from "@/lib/i18n";
import { useBackendHealth } from "@/state/BackendHealth";
import { useProjectContext } from "@/state/useProjectContext";

type WorkspaceMode = "diagnosis" | "design";

function categoryLabel(category: ExtractedIdea["category"], t: (key: DictKey) => string): string {
  return t(`ideaCategory.${category}` as DictKey);
}

export function IdeaWorkspacePage() {
  const { projectId } = useParams<{ projectId: string }>();
  const { connected } = useBackendHealth();
  const { project } = useProjectContext();
  const { t } = useI18n();
  const [mode, setMode] = useState<WorkspaceMode>("diagnosis");
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [filterText, setFilterText] = useState("");
  const queryClient = useQueryClient();
  const ideasQuery = useQuery({
    queryKey: ["project", projectId, "ideas"],
    queryFn: () => listIdeas(projectId as string),
    enabled: Boolean(projectId && connected),
  });

  const ideas = useMemo(
    () => (ideasQuery.data ?? []).filter((idea) => idea.status !== "dismissed"),
    [ideasQuery.data],
  );
  const objective = project?.objectives.join(" · ") || project?.targetProduct || t("ideaWorkspace.noObjectiveDefined");
  const runsQuery = useQuery({
    queryKey: ["paper-extraction-runs", projectId],
    queryFn: () => listRuns(projectId),
    enabled: Boolean(projectId && connected),
    refetchInterval: 4_000,
  });
  const runResults = useQueries({
    queries: (runsQuery.data ?? []).slice(0, 6).map((run) => ({
      queryKey: ["paper-extraction-run", run.taskId],
      queryFn: () => getRun(run.taskId),
      refetchInterval: run.status === "completed" || run.status === "failed" ? false : 3_000,
    })),
  });
  const extractedIdeas = useMemo(
    () => runResults.flatMap((query) => query.data?.extractedIdeas ?? []),
    [runResults],
  );
  const retrievalMutation = useMutation({
    mutationFn: () => submitRun({
      projectId,
      // Skill01 (paper_extraction/vendor) is a deterministic regex parser,
      // not an LLM: it expects a short, keyword-dense research phrase (e.g.
      // a target organism plus objective), not an instructional sentence
      // written for a reader. A wrapper sentence explaining what to do with
      // the request gets shredded into 2-12 char Chinese n-grams and OR'd
      // into the literature search query as noise terms, drowning out the
      // real organism/objective keywords. Keep this to organism, strain and
      // objective only.
      userRequest: [project?.hostDefinition.species, project?.hostDefinition.strain, objective]
        .filter(Boolean).join(" "),
      organism: String(project?.hostDefinition.species ?? ""),
      strain: String(project?.hostDefinition.strain ?? ""),
      sourceType: "auto_search",
      resultLevel: "extract",
      documentKind: "auto",
    }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["paper-extraction-runs", projectId] }),
  });
  const selected = ideas.find((idea) => idea.ideaId === selectedId) ?? ideas[0] ?? null;

  if (!connected) return <div className="p-6"><EmptyState variant="disconnected" /></div>;

  return (
    <main className="min-h-full flex-1 overflow-y-auto bg-surface-sunken">
      <header className="border-b border-border bg-surface px-5 py-4">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <div className="mb-1 flex items-center gap-2 text-xs font-medium text-accent-strong">
              <Sparkles size={14} /> {t("ideaWorkspace.corePage")}
            </div>
            <h1 className="text-xl font-semibold text-ink">{t("nav.ideaWorkspace")}</h1>
            <p className="mt-1 max-w-4xl text-sm text-ink-muted">
              {t("ideaWorkspace.subtitle")}
            </p>
          </div>
          <button
            type="button"
            onClick={() => retrievalMutation.mutate()}
            disabled={retrievalMutation.isPending}
            className="flex items-center gap-1.5 rounded-lg bg-accent px-3 py-2 text-xs font-semibold text-white"
          >
            <WandSparkles size={14} />
            {retrievalMutation.isPending ? t("ideaWorkspace.startingRetrieval") : t("ideaWorkspace.getIdeas")}
          </button>
        </div>
        <div className="mt-4 flex items-start gap-3 rounded-lg border border-accent/20 bg-accent-soft px-4 py-3">
          <Dna size={16} className="mt-0.5 flex-none text-accent-strong" />
          <div>
            <span className="text-[11px] font-medium uppercase tracking-wide text-accent-strong">{t("ideaWorkspace.currentObjective")}</span>
            <p className="mt-0.5 text-sm font-medium text-ink">{objective}</p>
          </div>
        </div>
      </header>

      <div className="grid min-h-[calc(100vh-19rem)] items-stretch xl:grid-cols-[280px_minmax(0,1fr)_330px]">
        <aside className="h-full border-r border-border bg-surface">
          <div className="flex items-center justify-between border-b border-border px-4 py-3">
            <div>
              <h2 className="text-sm font-semibold text-ink">{t("ideaWorkspace.ideaPool")}</h2>
              <p className="mt-0.5 text-[11px] text-ink-muted">{ideas.length + extractedIdeas.length} {t("ideaWorkspace.pendingIdeasUnit")}</p>
            </div>
            <Lightbulb size={16} className="text-amber-600" />
          </div>
          {ideasQuery.isLoading && <div className="p-4"><EmptyState variant="loading" /></div>}
          {!ideasQuery.isLoading && ideas.length === 0 && (
            <div className="p-4">
              <EmptyState variant="first_use" title={t("ideaWorkspace.noIdeasTitle")} detail={t("ideaWorkspace.noIdeasDetail")} />
              <Link to={`/projects/${projectId}/knowledge?tab=extraction`} className="mt-3 flex items-center gap-1 text-xs font-medium text-accent-strong">
                {t("ideaWorkspace.goExtractFromKnowledge")} <ArrowRight size={13} />
              </Link>
            </div>
          )}
          <div className="divide-y divide-border">
            {ideas.map((idea, index) => (
              <button
                key={idea.ideaId}
                type="button"
                onClick={() => setSelectedId(idea.ideaId)}
                className={`w-full px-4 py-3 text-left transition-colors ${
                  selected?.ideaId === idea.ideaId ? "bg-accent-soft" : "hover:bg-surface-sunken"
                }`}
              >
                <div className="flex items-start gap-3">
                  <span className="mt-0.5 flex h-6 w-6 flex-none items-center justify-center rounded-md bg-amber-50 text-[11px] font-semibold text-amber-700">
                    {index + 1}
                  </span>
                  <div className="min-w-0 flex-1">
                    <p className="line-clamp-2 text-sm font-medium text-ink">{idea.freeText}</p>
                    <div className="mt-2 flex items-center justify-between gap-2">
                      <span className="truncate text-[11px] text-ink-muted">
                        {idea.targetGene || t("ideaWorkspace.targetPending")} · {idea.modificationType || t("ideaWorkspace.interventionPending")}
                      </span>
                      <ChevronRight size={13} className="flex-none text-ink-faint" />
                    </div>
                  </div>
                </div>
              </button>
            ))}
          </div>
        </aside>

        <section className="min-w-0 p-5">
          <RetrievedIdeas
            ideas={extractedIdeas}
            filterText={filterText}
            running={Boolean((runsQuery.data ?? []).some((run) => !["completed", "failed"].includes(run.status)))}
          />
          {!selected && extractedIdeas.length === 0 ? (
            <EmptyState variant="first_use" title={t("ideaWorkspace.selectIdeaTitle")} detail={t("ideaWorkspace.selectIdeaDetail")} />
          ) : (
            selected && <IdeaDetail idea={selected} mode={mode} onModeChange={setMode} projectId={projectId as string} />
          )}
        </section>
        <IdeaChat ideas={extractedIdeas} value={filterText} onChange={setFilterText} />
      </div>
    </main>
  );
}

function RetrievedIdeas({ ideas, filterText, running }: { ideas: ExtractedIdea[]; filterText: string; running: boolean }) {
  const { t } = useI18n();
  const words = filterText.trim().toLowerCase().split(/\s+/).filter(Boolean);
  const filtered = words.length === 0 ? ideas : ideas.filter((idea) => {
    const blob = `${idea.title} ${idea.summary} ${idea.source.title} ${categoryLabel(idea.category, t)}`.toLowerCase();
    return words.every((word) => blob.includes(word));
  });
  const groups = Object.entries(
    filtered.reduce<Record<string, ExtractedIdea[]>>((acc, idea) => {
      (acc[idea.category] ??= []).push(idea);
      return acc;
    }, {}),
  );
  if (ideas.length === 0 && !running) return null;
  return (
    <section className="mb-5">
      <div className="mb-3 flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-sm font-semibold text-ink">{t("ideaWorkspace.autoRetrievedTitle")}</h2>
          <p className="mt-0.5 text-xs text-ink-muted">
            {running ? t("ideaWorkspace.retrievingDetail") : `${filtered.length} ${t("ideaWorkspace.groupedByType")}`}
          </p>
        </div>
        {running && <span className="rounded-full bg-accent-soft px-3 py-1 text-[11px] font-medium text-accent-strong">{t("ideaWorkspace.processing")}</span>}
      </div>
      {groups.length > 1 && (
        <nav className="sticky top-0 z-10 mb-4 flex flex-wrap gap-2 rounded-lg border border-border bg-surface/95 p-2 shadow-sm backdrop-blur">
          {groups.map(([category, rows]) => (
            <a key={category} href={`#idea-category-${category}`} className="rounded-full bg-surface-sunken px-3 py-1.5 text-xs font-medium text-ink-muted hover:text-accent-strong">
              {categoryLabel(category as ExtractedIdea["category"], t)} · {rows.length}
            </a>
          ))}
        </nav>
      )}
      <div className="space-y-5">
        {groups.map(([category, rows]) => (
          <div key={category} id={`idea-category-${category}`} className="scroll-mt-14">
            <h3 className="mb-2 text-xs font-semibold text-ink">{categoryLabel(category as ExtractedIdea["category"], t)}</h3>
            <div className="grid gap-3 2xl:grid-cols-2">
              {rows.map((idea) => <ExtractedIdeaCard key={idea.ideaId} idea={idea} />)}
            </div>
          </div>
        ))}
      </div>
      {!running && filtered.length === 0 && (
        <EmptyState variant="no_result" title={t("ideaWorkspace.noMatchTitle")} detail={t("ideaWorkspace.noMatchDetail")} />
      )}
    </section>
  );
}

function ExtractedIdeaCard({ idea }: { idea: ExtractedIdea }) {
  const { t } = useI18n();
  return (
    <article className="panel overflow-hidden">
      <div className="p-4">
        <div className="flex items-start justify-between gap-3">
          <span className="rounded-full bg-accent-soft px-2 py-1 text-[11px] font-medium text-accent-strong">
            {categoryLabel(idea.category, t)}
          </span>
          <span className="text-[11px] text-ink-faint">{idea.evidenceIds.length} {t("ideaWorkspace.evidenceLocatedUnit")}</span>
        </div>
        <h4 className="mt-3 text-sm font-semibold leading-5 text-ink">{idea.title}</h4>
        <div className="mt-3 rounded-lg bg-surface-sunken p-3">
          <p className="text-[11px] font-semibold text-ink-muted">{t("ideaWorkspace.summaryLabel")}</p>
          <p className="mt-1 text-xs leading-5 text-ink">{idea.summary}</p>
        </div>
      </div>
      <footer className="border-t border-border bg-surface-sunken px-4 py-3">
        <p className="flex items-start gap-2 text-xs font-medium text-ink"><BookOpen size={13} className="mt-0.5 flex-none text-accent-strong" /> {idea.source.title}</p>
        <p className="mt-1 pl-5 text-[11px] text-ink-muted">
          {[idea.source.journal, idea.source.year, idea.source.doi && `DOI ${idea.source.doi}`].filter(Boolean).join(" · ")}
        </p>
      </footer>
    </article>
  );
}

function IdeaChat({ ideas, value, onChange }: { ideas: ExtractedIdea[]; value: string; onChange: (value: string) => void }) {
  const { t } = useI18n();
  const [draft, setDraft] = useState("");
  const [messages, setMessages] = useState<Array<{ role: "user" | "assistant"; text: string }>>([
    { role: "assistant", text: t("ideaWorkspace.chatIntro") },
  ]);
  function send() {
    const text = draft.trim();
    if (!text) return;
    const terms = extractFilterTerms(text);
    onChange(terms.join(" "));
    const matched = ideas.filter((idea) => {
      const blob = `${idea.title} ${idea.summary} ${categoryLabel(idea.category, t)}`.toLowerCase();
      return terms.every((term) => blob.includes(term.toLowerCase()));
    }).length;
    setMessages((current) => [...current, { role: "user", text }, {
      role: "assistant",
      text: `${t("ideaWorkspace.chatReplyPrefix")}${matched}${t("ideaWorkspace.chatReplySuffix")}`,
    }]);
    setDraft("");
  }
  return (
    <aside className="flex h-full min-h-[32rem] flex-col border-l border-border bg-surface">
      <header className="border-b border-border px-4 py-3">
        <h2 className="flex items-center gap-2 text-sm font-semibold text-ink"><Sparkles size={15} className="text-accent-strong" /> {t("ideaWorkspace.chatAssistantTitle")}</h2>
        <p className="mt-1 text-[11px] text-ink-muted">{t("ideaWorkspace.chatAssistantSubtitle")}</p>
      </header>
      {value && (
        <div className="border-b border-border bg-accent-soft px-4 py-2 text-xs text-accent-strong">
          {t("ideaWorkspace.currentFilterPrefix")}{value}
          <button type="button" onClick={() => onChange("")} className="ml-2 font-semibold">{t("ideaWorkspace.clearFilter")}</button>
        </div>
      )}
      <div className="flex-1 space-y-3 overflow-y-auto p-4">
        {messages.map((message, index) => (
          <div key={index} className={`max-w-[90%] rounded-xl px-3 py-2 text-xs leading-5 ${message.role === "user" ? "ml-auto bg-accent text-white" : "bg-surface-sunken text-ink"}`}>
            {message.text}
          </div>
        ))}
      </div>
      <div className="border-t border-border p-3">
        <div className="flex items-end gap-2 rounded-xl border border-border bg-surface px-3 py-2 focus-within:border-accent">
          <textarea
            rows={2}
            value={draft}
            onChange={(event) => setDraft(event.target.value)}
            onKeyDown={(event) => { if (event.key === "Enter" && !event.shiftKey) { event.preventDefault(); send(); } }}
            placeholder={t("ideaWorkspace.chatPlaceholder")}
            className="min-h-10 flex-1 resize-none bg-transparent text-xs outline-none"
          />
          <button type="button" onClick={send} className="flex h-8 w-8 flex-none items-center justify-center rounded-lg bg-accent text-white" aria-label={t("ideaWorkspace.sendAriaLabel")}>
            <Send size={14} />
          </button>
        </div>
        <p className="mt-2 text-[10px] text-ink-faint">{t("ideaWorkspace.enterToSendHint")}</p>
      </div>
    </aside>
  );
}

function extractFilterTerms(input: string): string[] {
  const known = [
    "基因组工程", "基因敲除", "敲除", "过表达", "代谢工程", "代谢", "合成调控",
    "调控", "蛋白工程", "组学", "转录组", "代谢组", "失败分析", "失败",
    "多轮迭代", "DBTL", "机制", "E.coli K-12", "E.coli B",
  ];
  const matches = known.filter((term) => input.toLowerCase().includes(term.toLowerCase()));
  if (matches.length > 0) return [...new Set(matches.map((term) => {
    if (term === "代谢工程") return "代谢";
    if (term === "基因敲除") return "敲除";
    if (term === "合成调控") return "调控";
    if (term === "蛋白工程") return "蛋白";
    if (term === "失败分析") return "失败";
    return term;
  }))];
  return input
    .replace(/只看|筛选|请|帮我|想要|需要|相关|思路|方案|有|的/g, " ")
    .split(/\s+/)
    .filter((term) => term.length > 1)
    .slice(0, 5);
}

function IdeaDetail({
  idea,
  mode,
  onModeChange,
  projectId,
}: {
  idea: ProjectIdea;
  mode: WorkspaceMode;
  onModeChange: (mode: WorkspaceMode) => void;
  projectId: string;
}) {
  const { t } = useI18n();
  return (
    <div className="mx-auto flex max-w-6xl flex-col gap-4">
      <section className="panel p-5">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div className="max-w-4xl">
            <div className="mb-2 flex items-center gap-2">
              <span className="rounded-full bg-amber-50 px-2 py-1 text-[11px] font-medium text-amber-700">{t("ideaWorkspace.humanEntered")}</span>
              <StatusBadge status={idea.status === "linked_to_design" ? "approved" : "draft"} label={idea.status === "linked_to_design" ? t("ideaWorkspace.statusInDesign") : t("ideaWorkspace.statusPendingReview")} />
            </div>
            <h2 className="text-lg font-semibold text-ink">{idea.freeText}</h2>
            {idea.rationale && <p className="mt-2 text-sm leading-6 text-ink-muted">{idea.rationale}</p>}
          </div>
          <Link to={`/projects/${projectId}/knowledge`} className="flex items-center gap-1 text-xs font-medium text-accent-strong">
            {t("ideaWorkspace.viewSourceEvidence")} <BookOpen size={13} />
          </Link>
        </div>
        <dl className="mt-4 grid gap-3 border-t border-border pt-4 sm:grid-cols-3">
          <Fact label={t("ideaWorkspace.interventionTarget")} value={idea.targetGene || t("ideaWorkspace.pendingDiagnosis")} />
          <Fact label={t("ideaWorkspace.interventionType")} value={idea.modificationType || t("ideaWorkspace.pendingDiagnosis")} />
          <Fact label={t("ideaWorkspace.designLink")} value={idea.linkedDesignProjectId || t("ideaWorkspace.noDesignYet")} />
        </dl>
      </section>

      <div className="flex w-fit rounded-lg border border-border bg-surface p-1">
        <ModeButton active={mode === "diagnosis"} icon={Search} label={t("ideaWorkspace.modeDiagnosis")} onClick={() => onModeChange("diagnosis")} />
        <ModeButton active={mode === "design"} icon={GitBranch} label={t("ideaWorkspace.modeDesign")} onClick={() => onModeChange("design")} />
      </div>

      {mode === "diagnosis" ? <DiagnosisPanel idea={idea} /> : <DesignPanel idea={idea} />}
    </div>
  );
}

function DiagnosisPanel({ idea }: { idea: ProjectIdea }) {
  const { t } = useI18n();
  const hasTarget = Boolean(idea.targetGene);
  const hasIntervention = Boolean(idea.modificationType);
  const hasRationale = Boolean(idea.rationale);
  return (
    <div className="grid gap-4 lg:grid-cols-2">
      <section className="panel p-5">
        <h3 className="flex items-center gap-2 text-sm font-semibold text-ink"><ShieldQuestion size={16} /> {t("ideaWorkspace.coreDiagnosisTitle")}</h3>
        <p className="mt-1 text-xs text-ink-muted">{t("ideaWorkspace.coreDiagnosisSubtitle")}</p>
        <div className="mt-4 space-y-3">
          <CheckRow done={hasTarget} title={t("ideaWorkspace.checkTargetTitle")} detail={hasTarget ? idea.targetGene as string : t("ideaWorkspace.checkTargetPendingDetail")} />
          <CheckRow done={hasIntervention} title={t("ideaWorkspace.checkInterventionTitle")} detail={hasIntervention ? idea.modificationType as string : t("ideaWorkspace.checkInterventionPendingDetail")} />
          <CheckRow done={hasRationale} title={t("ideaWorkspace.checkMechanismTitle")} detail={hasRationale ? idea.rationale as string : t("ideaWorkspace.checkMechanismPendingDetail")} />
        </div>
      </section>
      <section className="panel p-5">
        <h3 className="text-sm font-semibold text-ink">{t("ideaWorkspace.diagnosisConclusionTitle")}</h3>
        <div className="mt-4 rounded-lg border border-amber-200 bg-amber-50 p-4">
          <p className="text-xs font-semibold text-amber-800">
            {hasTarget && hasIntervention && hasRationale ? t("ideaWorkspace.readyForDesignComparison") : t("ideaWorkspace.infoIncomplete")}
          </p>
          <p className="mt-2 text-xs leading-5 text-amber-700">
            {t("ideaWorkspace.diagnosisConclusionDetail")}
          </p>
        </div>
        <Link to="/projects" className="mt-4 flex items-center gap-1 text-xs font-medium text-accent-strong">
          {t("ideaWorkspace.diagnosisRecordsBackend")} <ArrowRight size={13} />
        </Link>
      </section>
    </div>
  );
}

function DesignPanel({ idea }: { idea: ProjectIdea }) {
  const { t } = useI18n();
  return (
    <div className="grid gap-4 lg:grid-cols-3">
      <DesignStep number="01" title={t("ideaWorkspace.designStepGoalTitle")} content={idea.targetGene ? `${t("ideaWorkspace.designStep1WithTargetPrefix")}${idea.targetGene}${t("ideaWorkspace.designStep1WithTargetSuffix")}` : t("ideaWorkspace.designStep1NoTarget")} />
      <DesignStep number="02" title={t("ideaWorkspace.designStepInterventionTitle")} content={idea.modificationType ? `${t("ideaWorkspace.designStep2WithModPrefix")}${idea.modificationType}${t("ideaWorkspace.designStep2WithModSuffix")}` : t("ideaWorkspace.designStep2NoMod")} />
      <DesignStep number="03" title={t("ideaWorkspace.designStepValidationTitle")} content={t("ideaWorkspace.designStep3Content")} />
      <section className="panel p-5 lg:col-span-3">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h3 className="text-sm font-semibold text-ink">{t("ideaWorkspace.designNotSimTitle")}</h3>
            <p className="mt-1 text-xs text-ink-muted">{t("ideaWorkspace.designNotSimDetail")}</p>
          </div>
          <StatusBadge status={idea.linkedDesignProjectId ? "approved" : "not_started"} label={idea.linkedDesignProjectId ? t("ideaWorkspace.hasDesignProject") : t("ideaWorkspace.waitingForDesign")} />
        </div>
      </section>
    </div>
  );
}

function Fact({ label, value }: { label: string; value: string }) {
  return <div><dt className="text-[11px] text-ink-muted">{label}</dt><dd className="mt-1 truncate text-sm font-medium text-ink">{value}</dd></div>;
}

function ModeButton({ active, icon: Icon, label, onClick }: { active: boolean; icon: typeof Search; label: string; onClick: () => void }) {
  return (
    <button type="button" onClick={onClick} className={`flex items-center gap-2 rounded-md px-4 py-2 text-xs font-semibold ${active ? "bg-accent text-white" : "text-ink-muted hover:text-ink"}`}>
      <Icon size={14} /> {label}
    </button>
  );
}

function CheckRow({ done, title, detail }: { done: boolean; title: string; detail: string }) {
  const Icon = done ? CheckCircle2 : CircleDashed;
  return (
    <div className="flex gap-3 rounded-lg border border-border p-3">
      <Icon size={17} className={done ? "mt-0.5 flex-none text-state-success" : "mt-0.5 flex-none text-amber-600"} />
      <div><p className="text-xs font-semibold text-ink">{title}</p><p className="mt-1 text-xs leading-5 text-ink-muted">{detail}</p></div>
    </div>
  );
}

function DesignStep({ number, title, content }: { number: string; title: string; content: string }) {
  return (
    <section className="panel p-5">
      <span className="text-xs font-semibold text-accent-strong">{number}</span>
      <h3 className="mt-2 text-sm font-semibold text-ink">{title}</h3>
      <p className="mt-2 text-xs leading-5 text-ink-muted">{content}</p>
    </section>
  );
}
