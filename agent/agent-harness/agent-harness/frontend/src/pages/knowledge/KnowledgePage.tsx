import { useCallback, useEffect, useRef, useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { useParams, useSearchParams } from "react-router-dom";
import { Search, Dna, BookOpen, Layers, FileSearch, ShieldQuestion, X, GripVertical, FlaskConical, Sprout } from "lucide-react";
import { getEvidenceDocument, getGenerationHealth, listEvidenceMatchReports, searchEvidence, verifyDoi, type EvidenceDocumentDetail } from "@/api/evidence";
import { EmptyState } from "@/components/common/EmptyState";
import { CapabilityState } from "@/components/common/CapabilityState";
import { StatusBadge, type BadgeStatus } from "@/components/common/StatusBadge";
import { useUrlSelection } from "@/hooks/useUrlSelection";
import { useI18n } from "@/lib/i18n";
import { KnowledgeClaimsTab } from "./KnowledgeClaimsTab";
import { PaperExtractionPage } from "@/pages/paperExtraction/PaperExtractionPage";
import { KnowledgeDistillationPage } from "@/pages/knowledgeDistillation/KnowledgeDistillationPage";

type Tab = "claims" | "biological" | "literature" | "extraction" | "distillation";
const TABS: Tab[] = ["claims", "biological", "literature", "extraction", "distillation"];

/**
 * Page 3 — Scientific Knowledge Production System (Page3 implementation
 * prompt, extending the Phase-0 Knowledge & Evidence Layer skeleton in
 * place). "Knowledge Claims" is the default tab — the real Knowledge
 * Production surface (production, not storage: prompt §6-8) — rather than
 * "Literature Evidence" being first, which would read as a paper-search
 * home and is one of the prompt's explicit failure modes (§12).
 *
 * Tab (and the Literature tab's selected source) live in the URL, not
 * local state - required for "click an evidence link -> land on the
 * corresponding reference literature" (part 2 of the evidence-link fix)
 * to actually produce a shareable/refreshable page rather than a
 * component-local selection that resets on navigation.
 */
export function KnowledgePage() {
  const [params, setParams] = useSearchParams();
  const tabParam = params.get("tab");
  const tab: Tab = TABS.includes(tabParam as Tab) ? (tabParam as Tab) : "claims";
  function setTab(next: Tab) {
    const nextParams = new URLSearchParams(params);
    nextParams.set("tab", next);
    if (next !== "literature") nextParams.delete("source");
    setParams(nextParams, { replace: true });
  }
  const healthQuery = useQuery({ queryKey: ["generation-health"], queryFn: getGenerationHealth });
  const { t } = useI18n();

  return (
    <div className="flex min-h-0 flex-1 flex-col">
      <h1 className="sr-only">{t("page3.title")}</h1>
      <div className="flex items-center gap-1 border-b border-border bg-surface px-3 py-2">
        <TabButton active={tab === "claims"} onClick={() => setTab("claims")} icon={Layers} label={t("page3.tab.claims")} />
        <TabButton active={tab === "biological"} onClick={() => setTab("biological")} icon={Dna} label={t("page3.tab.biological")} />
        <TabButton active={tab === "literature"} onClick={() => setTab("literature")} icon={BookOpen} label={t("page3.tab.literature")} />
        <TabButton active={tab === "extraction"} onClick={() => setTab("extraction")} icon={FileSearch} label={t("nav.paperExtraction")} />
        <TabButton active={tab === "distillation"} onClick={() => setTab("distillation")} icon={Sprout} label={t("nav.knowledgeDistillation")} />
        <div className="ml-auto flex items-center gap-3 text-[11px] text-ink-muted">
          {healthQuery.data && (
            <>
              <span>{t("page3.localDdr")}: <CapabilityState domain="evidence_generation" compact /></span>
              <span>Crossref: {healthQuery.data.crossref.available ? t("state.available") : t("state.unavailable")}</span>
            </>
          )}
        </div>
      </div>
      <div className="flex min-h-0 flex-1 flex-col overflow-y-auto p-4">
        {tab === "claims" && <KnowledgeClaimsTab />}
        {tab === "biological" && <BiologicalKnowledgeTab />}
        {tab === "literature" && <LiteratureEvidenceTab />}
        {tab === "extraction" && <PaperExtractionPage embedded />}
        {tab === "distillation" && <KnowledgeDistillationPage embedded />}
      </div>
    </div>
  );
}

function TabButton({ active, onClick, icon: Icon, label }: { active: boolean; onClick: () => void; icon: typeof Dna; label: string }) {
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

function BiologicalKnowledgeTab() {
  const { t } = useI18n();
  return (
    <div className="mx-auto flex w-full max-w-6xl flex-col gap-4">
      <section className="panel overflow-hidden">
        <div className="flex items-start gap-3 border-b border-border px-5 py-4">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-emerald-50 text-emerald-600">
            <Dna size={20} aria-hidden />
          </div>
          <div>
            <h2 className="text-base font-semibold text-ink">{t("page3.biologicalKnowledgeTitle")}</h2>
            <p className="mt-1 max-w-3xl text-sm leading-5 text-ink-muted">{t("page3.biologicalKnowledgeDetail")}</p>
          </div>
        </div>
        <div className="grid gap-3 p-4 md:grid-cols-3">
          <KnowledgeArea icon={Dna} title="Biological rules" path="knowledge/biological_rules/" />
          <KnowledgeArea icon={Layers} title="DDR database" path="knowledge/ddr_database/" />
          <KnowledgeArea icon={FlaskConical} title="Engineering actions" path="knowledge/engineering_actions/" />
        </div>
      </section>
      <div className="panel flex min-h-52 items-center justify-center p-5">
        <EmptyState variant="partial" title={t("page3.biologicalKnowledgeTitle")} detail={t("page3.biologicalKnowledgeDetail")} />
      </div>
    </div>
  );
}

function KnowledgeArea({ icon: Icon, title, path }: { icon: typeof Dna; title: string; path: string }) {
  return (
    <div className="rounded-lg border border-border bg-surface-sunken/40 p-4">
      <Icon size={16} className="text-accent" aria-hidden />
      <p className="mt-3 text-sm font-medium text-ink">{title}</p>
      <p className="mt-1 break-all font-mono text-[11px] text-ink-faint">{path}</p>
    </div>
  );
}

// Detail panel width bounds for the draggable literature list/detail split
// (request: panel was fixed at w-80 with no way to widen it or close it
// without losing the selection). Clamped in pixels rather than percent so
// it stays usable at narrow viewport widths too.
const LITERATURE_DETAIL_MIN_WIDTH = 320;
const LITERATURE_DETAIL_MAX_WIDTH = 900;
const LITERATURE_DETAIL_DEFAULT_WIDTH = 480;

function LiteratureEvidenceTab() {
  const { t } = useI18n();
  const { projectId } = useParams<{ projectId: string }>();
  const [query, setQuery] = useState("tryptophan");
  const [searchSource, setSearchSource] = useState<"local_ddr" | "crossref">("local_ddr");
  const [doi, setDoi] = useState("");
  const [actorId] = useState("frontend-user");
  // URL-driven (not local state) so a link with `?source=<id>` - e.g. from
  // EvidenceDrawer's "查看来源" action elsewhere in the app - lands
  // directly on that document, refresh-safe and shareable.
  const [selectedSourceId, setSelectedSourceId] = useUrlSelection("source");
  const [detailWidth, setDetailWidth] = useState(LITERATURE_DETAIL_DEFAULT_WIDTH);
  const splitRef = useRef<HTMLDivElement>(null);
  const draggingRef = useRef(false);
  const searchQuery = useQuery({
    queryKey: ["evidence-search", query, searchSource],
    queryFn: () => searchEvidence(query, searchSource),
    enabled: query.length > 0,
  });
  const detailQuery = useQuery({
    queryKey: ["evidence-document", selectedSourceId, searchSource],
    queryFn: () => getEvidenceDocument(selectedSourceId as string, searchSource),
    enabled: !!selectedSourceId,
  });
  const matchReportsQuery = useQuery({ queryKey: ["evidence-match-reports"], queryFn: () => listEvidenceMatchReports() });
  const verifyMutation = useMutation({
    mutationFn: () => verifyDoi({ projectId: projectId as string, doi, actorId }),
  });

  const handleResizeMove = useCallback((e: MouseEvent) => {
    if (!draggingRef.current || !splitRef.current) return;
    const rect = splitRef.current.getBoundingClientRect();
    const next = rect.right - e.clientX;
    setDetailWidth(Math.min(LITERATURE_DETAIL_MAX_WIDTH, Math.max(LITERATURE_DETAIL_MIN_WIDTH, next)));
  }, []);

  const stopResizing = useCallback(() => {
    draggingRef.current = false;
    document.body.style.cursor = "";
    document.body.style.userSelect = "";
  }, []);

  useEffect(() => {
    window.addEventListener("mousemove", handleResizeMove);
    window.addEventListener("mouseup", stopResizing);
    return () => {
      window.removeEventListener("mousemove", handleResizeMove);
      window.removeEventListener("mouseup", stopResizing);
    };
  }, [handleResizeMove, stopResizing]);

  function startResizing() {
    draggingRef.current = true;
    document.body.style.cursor = "col-resize";
    document.body.style.userSelect = "none";
  }

  return (
    <div className="flex flex-col gap-4">
      <section className="panel flex flex-col overflow-hidden">
        <div className="flex flex-wrap items-center gap-2 border-b border-border p-3">
          <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-accent/10 text-accent">
            <Search size={15} aria-hidden />
          </div>
          <input
            className="min-w-64 flex-1 rounded-lg border border-border px-3 py-2 text-sm outline-none transition focus:border-accent focus:ring-2 focus:ring-accent/10"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={t("page3.searchSources")}
          />
          <select value={searchSource} onChange={(e) => setSearchSource(e.target.value as "local_ddr" | "crossref")} className="min-w-44 rounded-lg border border-border bg-surface px-3 py-2 text-sm outline-none">
            <option value="local_ddr">{t("page3.localDdrOption")}</option>
            <option value="crossref">{t("page3.crossrefOption")}</option>
          </select>
        </div>
        <div className="min-h-64 p-3">
        {searchQuery.isLoading && <EmptyState variant="loading" />}
        {searchQuery.isError && <EmptyState variant="failed" detail={String(searchQuery.error)} />}
        {searchQuery.data && searchQuery.data.documents.length === 0 && !selectedSourceId && <EmptyState variant="no_result" />}
        {/* Show the split view whenever there are results to list OR a
            document is already selected via a deep link (`?source=...`)
            even if it doesn't happen to match the current search query -
            landing on a shared evidence link must not depend on first
            guessing the right search term. */}
        {((searchQuery.data && searchQuery.data.documents.length > 0) || selectedSourceId) && (
          <div ref={splitRef} className="flex min-h-[280px] flex-1">
            <ul className="flex min-w-0 flex-1 flex-col gap-2 overflow-y-auto pr-3">
              {(searchQuery.data?.documents ?? []).map((d) => (
                <li key={d.sourceId}>
                  <button
                    onClick={() => setSelectedSourceId(d.sourceId)}
                    aria-pressed={selectedSourceId === d.sourceId}
                    className={`w-full rounded-lg border p-3.5 text-left text-xs transition-colors ${
                      selectedSourceId === d.sourceId ? "border-accent bg-accent-soft" : "border-border bg-surface hover:bg-surface-sunken"
                    }`}
                  >
                    <p className="font-medium text-ink">{d.title || t("page3.noTitle")}</p>
                    <p className="text-ink-muted">{d.authors.join(", ") || t("page3.authorsNotReported")} · {d.publicationYear ?? t("page3.noDate")} · {d.journalOrRepository ?? t("page3.metadataOnly")}</p>
                    {d.doiOrAccession ? (
                      <p className="font-mono text-[11px] text-ink-faint">{d.doiOrAccession}</p>
                    ) : (
                      <p className="text-[11px] italic text-ink-faint">{t("page3.noDoiReported")}</p>
                    )}
                  </button>
                </li>
              ))}
            </ul>
            {/* Draggable resize handle - request: user wants to manually
                adjust the left/right split rather than a fixed w-80. */}
            <div
              role="separator"
              aria-orientation="vertical"
              aria-label={t("page3.detail.resizeHandle")}
              title={t("page3.detail.resizeHandle")}
              onMouseDown={(e) => {
                e.preventDefault();
                startResizing();
              }}
              className="group relative flex w-3 flex-shrink-0 cursor-col-resize items-center justify-center"
            >
              <div className="h-full w-px bg-border group-hover:bg-accent" />
              <GripVertical size={12} className="absolute text-ink-faint group-hover:text-accent" aria-hidden />
            </div>
            <div style={{ width: detailWidth }} className="min-w-0 flex-shrink-0">
              <LiteratureDetailPanel
                detail={detailQuery.data ?? null}
                isLoading={detailQuery.isLoading}
                hasSelection={!!selectedSourceId}
                onClose={() => setSelectedSourceId(null)}
              />
            </div>
          </div>
        )}
        </div>
      </section>

      <div className="grid items-start gap-4 xl:grid-cols-[minmax(380px,0.8fr)_minmax(520px,1.2fr)]">
      <div className="panel flex flex-col gap-3 p-4 text-xs">
        <h3 className="label-caps flex items-center gap-1"><ShieldQuestion size={12} /> {t("page3.verifyDoi")}</h3>
        <p className="text-ink-faint">{t("page3.crossrefResolutionDetail")}</p>
        <div className="flex items-center gap-2">
          <input value={doi} onChange={(e) => setDoi(e.target.value)} placeholder="10.xxxx/xxxxx" className="min-w-0 flex-1 rounded-lg border border-border px-3 py-2 font-mono outline-none focus:border-accent" />
          <button
            disabled={!doi.trim() || !projectId || verifyMutation.isPending}
            onClick={() => verifyMutation.mutate()}
            className="rounded-lg bg-accent px-3 py-2 font-medium text-white disabled:opacity-40"
          >
            {verifyMutation.isPending ? t("page3.checking") : t("page3.verify")}
          </button>
          {verifyMutation.data && (
            <StatusBadge status={verifyMutation.data.resolved ? "approved" : "rejected"} label={verifyMutation.data.resolved ? t("page3.resolvedByCrossref") : t("page3.couldNotResolve")} />
          )}
        </div>
      </div>

      <div className="panel flex min-h-44 flex-col gap-2 p-4">
        <h3 className="text-sm font-semibold text-ink">{t("page3.applicabilityReports")}</h3>
        <p className="text-[11px] text-ink-faint">{t("page3.applicabilityReportsDetail")}</p>
        {matchReportsQuery.isLoading && <EmptyState variant="loading" />}
        {matchReportsQuery.data && matchReportsQuery.data.length === 0 && (
          <EmptyState variant="first_use" title={t("page3.noMatchReportsYet")} detail={t("page3.noMatchReportsDetail")} />
        )}
        {matchReportsQuery.data && matchReportsQuery.data.length > 0 && (
          <ul className="flex flex-col gap-1.5">
            {matchReportsQuery.data.map((m) => (
              <li key={m.matchReportId} className="panel flex flex-col gap-1 p-2.5">
                <div className="flex items-center justify-between">
                  <span className="font-mono text-ink-faint">{m.evidenceId}</span>
                  <StatusBadge status={matchStatusToBadge(m.overallMatchStatus)} label={m.overallMatchStatus} />
                </div>
                <div className="flex flex-wrap gap-x-3 gap-y-0.5 text-[11px] text-ink-muted">
                  <span>{t("page3.organism")}: {m.organismMatch}</span>
                  <span>{t("page3.strain")}: {m.strainMatch}</span>
                  <span>{t("page3.genotype")}: {m.genotypeMatch}</span>
                  <span>{t("page3.medium")}: {m.mediumMatch}</span>
                  <span>{t("page3.condition")}: {m.conditionMatch}</span>
                  <span>{t("page3.directness")}: {m.directness}</span>
                </div>
                {m.transferRisks.length > 0 && <p className="text-[11px] text-state-caution">{t("page3.transferRisks")}: {m.transferRisks.join("; ")}</p>}
                {m.downgradeReasons.length > 0 && <p className="text-[11px] text-state-risk">{t("page3.downgraded")}: {m.downgradeReasons.join("; ")}</p>}
              </li>
            ))}
          </ul>
        )}
      </div>
      </div>
    </div>
  );
}

function CloseDetailButton({ onClose }: { onClose: () => void }) {
  const { t } = useI18n();
  return (
    <button
      onClick={onClose}
      aria-label={t("page3.detail.close")}
      title={t("page3.detail.close")}
      className="ml-auto flex-shrink-0 rounded p-1 text-ink-faint hover:bg-surface-sunken hover:text-ink"
    >
      <X size={14} />
    </button>
  );
}

function LiteratureDetailPanel({
  detail,
  isLoading,
  hasSelection,
  onClose,
}: {
  detail: EvidenceDocumentDetail | null;
  isLoading: boolean;
  hasSelection: boolean;
  onClose: () => void;
}) {
  const { t } = useI18n();
  if (!hasSelection) {
    return (
      <div className="panel h-full p-3">
        <EmptyState variant="first_use" title={t("page3.detail.noSelectionTitle")} detail={t("page3.detail.noSelectionDetail")} />
      </div>
    );
  }
  if (isLoading) {
    return (
      <div className="panel flex h-full flex-col gap-2 p-3">
        <div className="flex items-start justify-between">
          <EmptyState variant="loading" />
          <CloseDetailButton onClose={onClose} />
        </div>
      </div>
    );
  }
  if (!detail) {
    return (
      <div className="panel flex h-full flex-col gap-2 p-3">
        <div className="flex items-start justify-between">
          <EmptyState variant="failed" />
          <CloseDetailButton onClose={onClose} />
        </div>
      </div>
    );
  }

  return (
    <div className="panel flex h-full flex-col gap-2 overflow-y-auto p-3 text-xs">
      <div className="flex items-start justify-between gap-2">
        <p className="font-medium text-ink">{detail.title || t("page3.noTitle")}</p>
        <CloseDetailButton onClose={onClose} />
      </div>
      <p className="text-ink-muted">{detail.authors.join(", ") || t("page3.authorsNotReported")} · {detail.publicationYear ?? t("page3.noDate")} · {detail.journalOrRepository ?? t("page3.metadataOnly")}</p>
      {detail.doiOrAccession ? (
        <p className="font-mono text-[11px] text-ink-faint">
          {/^10\.\S+\/\S+$/.test(detail.doiOrAccession) ? (
            <a
              href={`https://doi.org/${detail.doiOrAccession}`}
              target="_blank"
              rel="noreferrer"
              className="text-accent-strong underline decoration-dotted underline-offset-2"
            >
              {detail.doiOrAccession}
            </a>
          ) : (
            detail.doiOrAccession
          )}
        </p>
      ) : (
        <p className="text-[11px] italic text-ink-faint">{t("page3.noDoiReported")}</p>
      )}
      {detail.url && (
        <a href={detail.url} target="_blank" rel="noreferrer" className="w-fit text-[11px] text-accent-strong underline decoration-dotted underline-offset-2">
          {t("page3.detail.openSource")}
        </a>
      )}

      {detail.abstractOrSummary && (
        <div className="mt-1 border-t border-border pt-2">
          <h4 className="label-caps mb-1">{t("page3.detail.abstractOrSummary")}</h4>
          <p className="text-ink-muted">{detail.abstractOrSummary}</p>
        </div>
      )}

      <div className="mt-1 border-t border-border pt-2">
        <h4 className="label-caps mb-1">{t("page3.detail.extractedDesignTitle")}</h4>
        {!detail.engineeringDesign ? (
          <EmptyState variant="unavailable" title={t("page3.detail.noExtractedDesignTitle")} detail={t("page3.detail.noExtractedDesignDetail")} />
        ) : (
          <div className="flex flex-col gap-2">
            {detail.engineeringDesign.bottlenecks.length > 0 && (
              <p><span className="font-medium text-ink-faint">{t("page3.detail.bottlenecks")}: </span>{detail.engineeringDesign.bottlenecks.join("; ")}</p>
            )}
            {detail.engineeringDesign.mechanisticExplanation && (
              <p><span className="font-medium text-ink-faint">{t("page3.detail.mechanism")}: </span>{detail.engineeringDesign.mechanisticExplanation}</p>
            )}
            {detail.engineeringDesign.hypothesis && (
              <p><span className="font-medium text-ink-faint">{t("page3.detail.hypothesis")}: </span>{detail.engineeringDesign.hypothesis}</p>
            )}
            {detail.engineeringDesign.expectedEffect && (
              <p><span className="font-medium text-ink-faint">{t("page3.detail.expectedEffect")}: </span>{detail.engineeringDesign.expectedEffect}</p>
            )}
            {detail.engineeringDesign.actions.length > 0 && (
              <div>
                <h5 className="label-caps mb-1">{t("page3.detail.actionsTitle")}</h5>
                <ul className="flex flex-col gap-2">
                  {detail.engineeringDesign.actions.map((a, i) => (
                    <li key={i} className="rounded border border-border p-2">
                      <p className="font-medium text-ink">{a.modificationType || "—"}</p>
                      <p className="text-ink-muted">{t("page3.detail.target")}: {a.target || "—"}{a.geneOrPathway ? ` (${a.geneOrPathway})` : ""}</p>
                      {a.rationale && <p className="text-ink-muted">{t("page3.detail.rationale")}: {a.rationale}</p>}
                      {a.expectedEffect && <p className="text-ink-muted">{t("page3.detail.expectedEffect")}: {a.expectedEffect}</p>}
                      {a.risk && <p className="text-state-caution">{t("page3.detail.risk")}: {a.risk}</p>}
                      {a.validation.length > 0 && <p className="text-ink-faint">{t("page3.detail.validation")}: {a.validation.join("; ")}</p>}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

function matchStatusToBadge(status: string): BadgeStatus {
  if (status === "direct_match" || status === "close_match") return "approved";
  if (status === "cross_strain" || status === "cross_species" || status === "condition_mismatch" || status === "endpoint_mismatch") return "needs_revision";
  if (status === "not_applicable") return "absent";
  return "unclear";
}
