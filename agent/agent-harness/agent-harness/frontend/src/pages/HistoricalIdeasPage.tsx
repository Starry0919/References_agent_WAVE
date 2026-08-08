import { useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { ArrowLeft, BookOpen, History, Search, Sparkles } from "lucide-react";
import { listKnowledgeIdeas, type KnowledgeIdea } from "@/api/paperExtraction";
import { EmptyState } from "@/components/common/EmptyState";
import { useI18n, type DictKey } from "@/lib/i18n";
import { useBackendHealth } from "@/state/BackendHealth";

function categoryLabel(category: KnowledgeIdea["category"], t: (key: DictKey) => string): string {
  return t(`ideaCategory.${category}` as DictKey);
}

export function HistoricalIdeasPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const { connected } = useBackendHealth();
  const { t } = useI18n();
  const [query, setQuery] = useState("");

  const ideasQuery = useQuery({
    queryKey: ["paper-extraction-knowledge-ideas", "all"],
    queryFn: () => listKnowledgeIdeas(),
    enabled: connected,
  });

  const allIdeas = ideasQuery.data ?? [];

  const filteredIdeas = useMemo(() => {
    const terms = query.trim().toLowerCase().split(/\s+/).filter(Boolean);
    if (terms.length === 0) return allIdeas;
    return allIdeas.filter((idea) => {
      const blob = `${idea.title} ${idea.summary} ${idea.source.title} ${idea.source.journal} ${categoryLabel(idea.category, t)}`.toLowerCase();
      return terms.every((term) => blob.includes(term));
    });
  }, [allIdeas, query, t]);

  const groups = useMemo(() => {
    const map = filteredIdeas.reduce<Record<string, KnowledgeIdea[]>>((acc, idea) => {
      (acc[idea.category] ??= []).push(idea);
      return acc;
    }, {});
    // Sort categories by count desc
    return Object.entries(map).sort((a, b) => b[1].length - a[1].length);
  }, [filteredIdeas]);

  if (!connected) {
    return (
      <main className="min-h-full flex-1 overflow-y-auto bg-surface-sunken p-6">
        <EmptyState variant="disconnected" />
      </main>
    );
  }

  return (
    <main className="min-h-full flex-1 overflow-y-auto bg-surface-sunken">
      <header className="border-b border-border bg-surface px-5 py-4">
        <div className="flex flex-wrap items-center gap-3">
          <Link
            to={`/projects/${projectId}/ideas`}
            className="flex items-center gap-1 text-xs font-medium text-accent-strong"
          >
            <ArrowLeft size={14} /> {t("common.back")}
          </Link>
          <div className="h-4 w-px bg-border" />
          <div className="flex items-center gap-2">
            <History size={16} className="text-accent-strong" />
            <h1 className="text-lg font-semibold text-ink">{t("historicalIdeas.title")}</h1>
          </div>
        </div>
        <p className="mt-1 text-sm text-ink-muted">{t("historicalIdeas.subtitle")}</p>

        <div className="mt-4 flex items-center gap-2">
          <div className="flex flex-1 items-center gap-2 rounded-lg border border-border bg-surface px-3 py-2 focus-within:border-accent">
            <Search size={15} className="text-ink-faint" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder={t("historicalIdeas.searchPlaceholder")}
              className="min-w-0 flex-1 bg-transparent text-sm outline-none placeholder:text-ink-faint"
            />
            {query && (
              <button
                type="button"
                onClick={() => setQuery("")}
                className="text-[11px] font-medium text-ink-muted hover:text-accent-strong"
              >
                {t("common.clear")}
              </button>
            )}
          </div>
          <span className="shrink-0 text-xs text-ink-muted">
            {filteredIdeas.length} / {allIdeas.length}
          </span>
        </div>
      </header>

      <section className="p-5">
        {ideasQuery.isLoading && <EmptyState variant="loading" />}
        {!ideasQuery.isLoading && allIdeas.length === 0 && (
          <EmptyState
            variant="first_use"
            title={t("historicalIdeas.noIdeasTitle")}
            detail={t("historicalIdeas.noIdeasDetail")}
          />
        )}
        {!ideasQuery.isLoading && allIdeas.length > 0 && filteredIdeas.length === 0 && (
          <EmptyState
            variant="no_result"
            title={t("historicalIdeas.noMatchTitle")}
            detail={t("historicalIdeas.noMatchDetail")}
          />
        )}

        <div className="space-y-6">
          {groups.map(([category, ideas]) => (
            <div key={category}>
              <h2 className="mb-3 flex items-center gap-2 text-sm font-semibold text-ink">
                <Sparkles size={14} className="text-accent" />
                {categoryLabel(category as KnowledgeIdea["category"], t)}
                <span className="text-[11px] font-normal text-ink-muted">({ideas.length})</span>
              </h2>
              <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
                {ideas.map((idea) => (
                  <IdeaCard key={idea.ideaId} idea={idea} projectId={projectId as string} />
                ))}
              </div>
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}

function IdeaCard({ idea, projectId }: { idea: KnowledgeIdea; projectId: string }) {
  const evidenceSourceId = idea.ideaId; // DDR id itself is the evidence source id
  return (
    <article className="panel flex h-full flex-col overflow-hidden">
      <div className="flex flex-1 flex-col p-4">
        <div className="flex items-start justify-between gap-2">
          <span className="shrink-0 rounded-full bg-accent-soft px-2 py-0.5 text-[11px] font-medium text-accent-strong">
            {idea.source.year || "—"}
          </span>
          <span className="truncate text-[11px] text-ink-faint">
            {idea.evidenceIds.length} {idea.evidenceIds.length === 1 ? "evidence" : "evidences"}
          </span>
        </div>
        <h3 className="mt-2 text-sm font-semibold leading-5 text-ink">{idea.title}</h3>
        <p className="mt-1 line-clamp-3 text-xs leading-5 text-ink-muted">{idea.summary}</p>
      </div>
      <footer className="border-t border-border bg-surface-sunken px-4 py-3">
        <p className="flex items-start gap-2 text-xs text-ink-muted">
          <BookOpen size={12} className="mt-0.5 flex-none" />
          <span className="line-clamp-1">{idea.source.title}</span>
        </p>
        {evidenceSourceId && (
          <Link
            to={`/projects/${projectId}/evidence/${evidenceSourceId}`}
            className="mt-2 flex w-fit items-center gap-1 text-[11px] font-medium text-accent-strong hover:underline"
          >
            {idea.ideaId} <ArrowLeft size={11} className="rotate-180" />
          </Link>
        )}
      </footer>
    </article>
  );
}
