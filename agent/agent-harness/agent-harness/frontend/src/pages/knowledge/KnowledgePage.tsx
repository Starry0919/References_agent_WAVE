import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { Link, useParams, useSearchParams } from "react-router-dom";
import { Search, Dna, BookOpen, Layers, FileSearch, ShieldQuestion, ShieldCheck, Check, X, GripVertical, FlaskConical, Sprout, ExternalLink, EyeOff } from "lucide-react";
import { getEvidenceDocument, getGenerationHealth, listEvidenceMatchReports, searchEvidence, verifyDoi, type EvidenceDocumentDetail } from "@/api/evidence";
import { listDdrKnowledgeClaims, listEngineeringActions, type DdrKnowledgeClaim, type EngineeringAction } from "@/api/rules";
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
  const { projectId } = useParams<{ projectId: string }>();
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
        {tab === "extraction" && <PaperExtractionPage embedded projectId={projectId} />}
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

type KnowledgeSource = "rules" | "ddr" | "actions";
const KNOWLEDGE_SOURCES: KnowledgeSource[] = ["rules", "ddr", "actions"];

/** The three on-disk knowledge-base categories (`knowledge/biological_rules/`,
 * `knowledge/ddr_database/`, `knowledge/engineering_actions/`) are distinct
 * kinds of object, not three views of the same list:
 * - DDR database: one record per *paper*, its full trigger→reasoning→
 *   evidence→action decision chain (a case study tied to one citation).
 * - Biological rules: cross-paper heuristics *distilled from* multiple DDRs
 *   (no single-paper citation of their own - each cites the DDRs it
 *   generalizes from).
 * - Engineering actions: a catalog of concrete gene-level operations
 *   (target + modification + mechanism), most of which are established
 *   patterns rather than one verified experimental result - see each
 *   entry's own `evidence` field.
 * The filter below is multi-select (all three checked by default) since a
 * user comparing rules against their source DDRs, or actions against the
 * rule that recommends them, legitimately wants more than one category
 * visible at once. */
function BiologicalKnowledgeTab() {
  const { t } = useI18n();
  const { projectId } = useParams<{ projectId: string }>();
  const [params, setParams] = useSearchParams();
  const [filterText, setFilterText] = useState("");
  const [hideUnbacked, setHideUnbacked] = useState(false);
  // `params.has` (not just `!raw`) so an explicit "none selected" (`?sources=`,
  // an empty string) is distinguished from "the param was never set" (the
  // all-three default) - deselecting all three cards must leave the list
  // empty below, not silently snap back to showing everything.
  const activeSources = useMemo(() => {
    if (!params.has("sources")) return new Set<KnowledgeSource>(KNOWLEDGE_SOURCES);
    const raw = params.get("sources") ?? "";
    const parsed = raw.split(",").filter((s): s is KnowledgeSource => KNOWLEDGE_SOURCES.includes(s as KnowledgeSource));
    return new Set(parsed);
  }, [params]);
  function toggleSource(source: KnowledgeSource) {
    const next = new Set(activeSources);
    if (next.has(source)) next.delete(source);
    else next.add(source);
    const nextParams = new URLSearchParams(params);
    // Omit the param entirely when all three are active - keeps the default,
    // most-common state out of the URL instead of always appending `?sources=...`.
    if (next.size === KNOWLEDGE_SOURCES.length) nextParams.delete("sources");
    else nextParams.set("sources", [...next].join(","));
    setParams(nextParams, { replace: true });
  }

  const claimsQuery = useQuery({
    queryKey: ["ddr-knowledge-claims", projectId, filterText],
    queryFn: () => listDdrKnowledgeClaims(filterText, projectId),
    enabled: activeSources.has("rules"),
  });
  const ddrQuery = useQuery({
    queryKey: ["evidence-search", filterText, "local_ddr", projectId],
    queryFn: () => searchEvidence(filterText, "local_ddr", projectId),
    enabled: activeSources.has("ddr"),
  });
  const actionsQuery = useQuery({
    queryKey: ["engineering-actions", filterText, projectId],
    queryFn: () => listEngineeringActions(filterText, projectId),
    enabled: activeSources.has("actions"),
  });

  // "Unbacked" = no citable evidence at all (empty `evidenceDdrIds` for a
  // rule, null `evidence` for an action) - not the DDR database section,
  // whose entries are each the primary source record itself and so have
  // nothing to be "backed by".
  const visibleClaims = useMemo(
    () => (hideUnbacked ? claimsQuery.data?.filter((c) => c.evidenceDdrIds.length > 0) : claimsQuery.data),
    [claimsQuery.data, hideUnbacked],
  );
  const visibleActions = useMemo(
    () => (hideUnbacked ? actionsQuery.data?.filter((a) => !!a.evidence) : actionsQuery.data),
    [actionsQuery.data, hideUnbacked],
  );

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
          <KnowledgeArea
            icon={Dna}
            title={t("page3.source.rulesTitle")}
            detail={t("page3.source.rulesDetail")}
            path="knowledge/biological_rules/"
            active={activeSources.has("rules")}
            onToggle={() => toggleSource("rules")}
            count={activeSources.has("rules") ? claimsQuery.data?.length : undefined}
          />
          <KnowledgeArea
            icon={Layers}
            title={t("page3.source.ddrTitle")}
            detail={t("page3.source.ddrDetail")}
            path="knowledge/ddr_database/"
            active={activeSources.has("ddr")}
            onToggle={() => toggleSource("ddr")}
            count={activeSources.has("ddr") ? ddrQuery.data?.documents.length : undefined}
          />
          <KnowledgeArea
            icon={FlaskConical}
            title={t("page3.source.actionsTitle")}
            detail={t("page3.source.actionsDetail")}
            path="knowledge/engineering_actions/"
            active={activeSources.has("actions")}
            onToggle={() => toggleSource("actions")}
            count={activeSources.has("actions") ? actionsQuery.data?.length : undefined}
          />
        </div>
        <div className="flex flex-wrap items-center gap-2 border-t border-border px-4 py-3">
          <Search size={13} className="shrink-0 text-ink-faint" aria-hidden />
          <input
            value={filterText}
            onChange={(e) => setFilterText(e.target.value)}
            placeholder={t("page3.source.filterPlaceholder")}
            className="w-full min-w-0 flex-1 border-0 bg-transparent text-xs outline-none"
          />
          <button
            type="button"
            onClick={() => setHideUnbacked((v) => !v)}
            aria-pressed={hideUnbacked}
            className={`flex shrink-0 items-center gap-1.5 rounded-full border px-2.5 py-1.5 text-[11px] font-medium transition ${
              hideUnbacked ? "border-red-300 bg-red-50 text-state-risk" : "border-border bg-surface text-ink-muted hover:bg-surface-sunken"
            }`}
          >
            <EyeOff size={12} aria-hidden />
            {t("page3.hideUnbackedEntries")}
          </button>
        </div>
      </section>

      {activeSources.size === 0 && <EmptyState variant="no_result" title={t("page3.source.noneSelectedTitle")} />}

      {activeSources.has("rules") && (
        <section className="panel flex flex-col gap-3 p-4">
          <div>
            <h3 className="text-sm font-semibold text-ink">{t("page3.ddrKnowledgeClaimsTitle")}</h3>
            <p className="mt-1 text-[11px] text-ink-faint">{t("page3.ddrKnowledgeClaimsDetail")}</p>
          </div>
          {claimsQuery.isLoading && <EmptyState variant="loading" />}
          {claimsQuery.isError && <EmptyState variant="failed" detail={String(claimsQuery.error)} />}
          {claimsQuery.data && claimsQuery.data.length === 0 && <EmptyState variant="no_result" title={t("page3.ddrKnowledgeClaimsEmptyTitle")} />}
          {claimsQuery.data && claimsQuery.data.length > 0 && visibleClaims && visibleClaims.length === 0 && (
            <EmptyState variant="no_result" title={t("page3.noClaimsMatchFilter")} />
          )}
          {visibleClaims && visibleClaims.length > 0 && (
            <ul className="flex flex-col gap-2">
              {visibleClaims.map((c) => (
                <DdrKnowledgeClaimCard key={c.claimId} claim={c} projectId={projectId} />
              ))}
            </ul>
          )}
        </section>
      )}

      {activeSources.has("ddr") && (
        <section className="panel flex flex-col gap-3 p-4">
          <div>
            <h3 className="text-sm font-semibold text-ink">{t("page3.source.ddrTitle")}</h3>
            <p className="mt-1 text-[11px] text-ink-faint">{t("page3.source.ddrDetail")}</p>
          </div>
          {ddrQuery.isLoading && <EmptyState variant="loading" />}
          {ddrQuery.isError && <EmptyState variant="failed" detail={String(ddrQuery.error)} />}
          {ddrQuery.data && ddrQuery.data.documents.length === 0 && <EmptyState variant="no_result" />}
          {ddrQuery.data && ddrQuery.data.documents.length > 0 && (
            <ul className="grid gap-2 sm:grid-cols-2">
              {ddrQuery.data.documents.map((d) => (
                <li key={d.sourceId} className={`rounded-lg border p-3 text-xs ${d.relevant ? "border-accent bg-accent-soft/40" : "border-border bg-surface"}`}>
                  <div className="flex items-start justify-between gap-2">
                    <p className="font-medium text-ink">{d.title || t("page3.noTitle")}</p>
                    <div className="flex shrink-0 items-center gap-1.5">
                      {d.relevant && <span className="rounded-full border border-accent px-1.5 py-0.5 text-[10px] font-medium text-accent-strong">{t("page3.relevantToProject")}</span>}
                      {projectId && (
                        <Link to={`/projects/${projectId}/evidence/${d.sourceId}`} className="text-accent-strong">
                          <ExternalLink size={12} aria-hidden />
                        </Link>
                      )}
                    </div>
                  </div>
                  {/* Source: the DDR's own citation - this record's whole
                      reason for existing is that it's one paper's decision
                      chain, so the paper it came from must be visible here,
                      not just the internal DDR-NNN id. */}
                  <p className="mt-1 text-ink-muted">
                    {d.authors.join(", ") || t("page3.authorsNotReported")} · {d.publicationYear ?? t("page3.noDate")} · {d.journalOrRepository ?? t("page3.metadataOnly")}
                  </p>
                  {d.doiOrAccession && <p className="mt-0.5 font-mono text-[10px] text-ink-faint">{d.doiOrAccession}</p>}
                  <p className="mt-1 font-mono text-[10px] text-ink-faint">{d.sourceId}</p>
                </li>
              ))}
            </ul>
          )}
        </section>
      )}

      {activeSources.has("actions") && (
        <section className="panel flex flex-col gap-3 p-4">
          <div>
            <h3 className="text-sm font-semibold text-ink">{t("page3.source.actionsTitle")}</h3>
            <p className="mt-1 text-[11px] text-ink-faint">{t("page3.source.actionsDetail")}</p>
          </div>
          {actionsQuery.isLoading && <EmptyState variant="loading" />}
          {actionsQuery.isError && <EmptyState variant="failed" detail={String(actionsQuery.error)} />}
          {actionsQuery.data && actionsQuery.data.length === 0 && <EmptyState variant="no_result" />}
          {actionsQuery.data && actionsQuery.data.length > 0 && visibleActions && visibleActions.length === 0 && (
            <EmptyState variant="no_result" />
          )}
          {visibleActions && visibleActions.length > 0 && (
            <ul className="grid gap-2 sm:grid-cols-2">
              {visibleActions.map((a) => (
                <EngineeringActionCard key={a.actionId} action={a} />
              ))}
            </ul>
          )}
        </section>
      )}
    </div>
  );
}

function EngineeringActionCard({ action }: { action: EngineeringAction }) {
  const { t } = useI18n();
  const unbacked = !action.evidence;
  return (
    <li className={`rounded-lg border p-3 text-xs ${unbacked ? "border-red-300 bg-red-50" : action.relevant ? "border-accent bg-accent-soft/40" : "border-border bg-surface"}`}>
      <div className="flex items-start justify-between gap-2">
        <p className="font-medium text-ink">{action.actionType}</p>
        <div className="flex shrink-0 items-center gap-1.5">
          {action.relevant && <span className="rounded-full border border-accent px-1.5 py-0.5 text-[10px] font-medium text-accent-strong">{t("page3.relevantToProject")}</span>}
          <span className="font-mono text-[10px] text-ink-faint">{action.actionId}</span>
        </div>
      </div>
      {action.targetGene && <p className="mt-1 text-ink-muted">{t("page3.source.actionTarget")}: {action.targetGene}</p>}
      {action.mechanism && <p className="mt-1 text-[11px] text-ink-faint">{action.mechanism}</p>}
      {action.risk && <p className="mt-1 text-[11px] text-state-caution">{t("page5.risk")}: {action.risk}</p>}
      {/* Source: most catalog entries are an established general pattern,
          not one paper's verified result - this field says which, instead
          of the card implying every action is a citable experimental
          finding. Always shown (not just when present) so an unbacked
          entry is visibly flagged rather than silently omitting the line. */}
      <p className={`mt-1.5 border-t pt-1.5 text-[11px] ${unbacked ? "border-red-200 font-medium text-state-risk" : "border-border text-ink-faint"}`}>
        <span className="font-medium">{t("page3.source.label")}: </span>
        {action.evidence || t("page3.source.noEvidenceRecorded")}
      </p>
    </li>
  );
}

const CONFIDENCE_BADGE: Record<DdrKnowledgeClaim["confidence"], BadgeStatus> = { high: "approved", medium: "needs_revision", low: "unclear" };

function DdrKnowledgeClaimCard({ claim, projectId }: { claim: DdrKnowledgeClaim; projectId: string | undefined }) {
  const { t } = useI18n();
  const unbacked = claim.evidenceDdrIds.length === 0;
  return (
    <li className={`rounded-lg border p-3.5 text-xs ${unbacked ? "border-red-300 bg-red-50" : claim.relevant ? "border-accent bg-accent-soft/40" : "border-border bg-surface"}`}>
      <div className="flex items-start justify-between gap-2">
        <p className="font-medium text-ink">{claim.statement}</p>
        <div className="flex shrink-0 items-center gap-1.5">
          {claim.relevant && <span className="rounded-full border border-accent px-1.5 py-0.5 text-[10px] font-medium text-accent-strong">{t("page3.relevantToProject")}</span>}
          <StatusBadge status={CONFIDENCE_BADGE[claim.confidence]} label={claim.confidence} />
        </div>
      </div>
      <div className="mt-2 flex flex-wrap items-center gap-x-3 gap-y-1 text-[11px] text-ink-muted">
        <span className="font-mono text-ink-faint">{claim.claimId}</span>
        {claim.evidenceGrading && <span>{claim.evidenceGrading}证据</span>}
        <span>{t("page3.claimEvidenceCount")}: {claim.evidenceCount}</span>
        {claim.applicableModules.length > 0 && <span>{claim.applicableModules.join(", ")}</span>}
      </div>
      <div className={`mt-1.5 flex flex-wrap items-center gap-1.5 text-[11px] ${unbacked ? "text-state-risk" : "text-ink-faint"}`}>
        <span className="font-medium">{t("page3.source.label")}:</span>
        {claim.evidenceDdrIds.length > 0 ? (
          claim.evidenceDdrIds.map((id) =>
            projectId ? (
              <Link key={id} to={`/projects/${projectId}/evidence/${id}`} className="rounded border border-border bg-surface px-1.5 py-0.5 font-mono text-[10px] text-accent-strong underline decoration-dotted underline-offset-2">
                {id}
              </Link>
            ) : (
              <span key={id} className="rounded border border-border bg-surface px-1.5 py-0.5 font-mono text-[10px] text-ink-muted">{id}</span>
            ),
          )
        ) : (
          <span className="italic font-medium">{t("page3.source.noneRecorded")}</span>
        )}
      </div>
      <p className="mt-1.5 text-[11px] text-ink-faint">{t("page3.claimBoundary")}: {claim.boundary}</p>
      {projectId && claim.evidenceDdrIds.length > 0 && (
        <Link
          to={`/projects/${projectId}/trust/${claim.evidenceDdrIds[0]}`}
          className="mt-1.5 flex w-fit items-center gap-1 text-[11px] font-medium text-accent-strong hover:underline"
        >
          <ShieldCheck size={11} aria-hidden /> {t("paperEvidence.applicability.viewProvenance")}
        </Link>
      )}
    </li>
  );
}

function KnowledgeArea({
  icon: Icon,
  title,
  detail,
  path,
  active,
  onToggle,
  count,
}: {
  icon: typeof Dna;
  title: string;
  detail: string;
  path: string;
  active: boolean;
  onToggle: () => void;
  count?: number;
}) {
  const { t } = useI18n();
  return (
    <button
      type="button"
      onClick={onToggle}
      aria-pressed={active}
      className={`flex flex-col items-start rounded-lg border p-4 text-left transition-colors ${
        active ? "border-accent bg-accent-soft/40" : "border-border bg-surface-sunken/40 hover:bg-surface-sunken"
      }`}
    >
      <div className="flex w-full items-start justify-between gap-2">
        <Icon size={16} className={active ? "text-accent-strong" : "text-accent"} aria-hidden />
        <span
          className={`flex h-4 w-4 shrink-0 items-center justify-center rounded border ${
            active ? "border-accent bg-accent text-white" : "border-border bg-surface"
          }`}
        >
          {active && <Check size={11} aria-hidden />}
        </span>
      </div>
      <p className="mt-3 text-sm font-medium text-ink">
        {title}
        {count !== undefined && <span className="ml-1.5 font-normal text-ink-faint">({count})</span>}
      </p>
      <p className="mt-1 text-[11px] leading-4 text-ink-muted">{detail}</p>
      <p className="mt-2 break-all font-mono text-[10px] text-ink-faint">{path}</p>
      <span className="mt-2 text-[10px] font-medium text-accent-strong">
        {active ? t("page3.source.shownInList") : t("page3.source.hiddenFromList")}
      </span>
    </button>
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
  // Empty query = full browse of the DDR corpus (老师 §Phase2: "空搜索：
  // 返回全部可用 DDR"), not an unset/loading state - starting blank rather
  // than pre-filled with "tryptophan" is what actually exercises that path
  // on first load instead of masking it behind a default keyword.
  const [query, setQuery] = useState("");
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
    // Always enabled (no `query.length > 0` gate) - an empty query is a
    // real, supported request ("browse everything"), not an unset input
    // to wait out (老师 §Phase2). `projectId` scopes DDR results to the
    // current project's host/product context for relevance ranking.
    queryKey: ["evidence-search", query, searchSource, projectId],
    queryFn: () => searchEvidence(query, searchSource, projectId),
  });
  const detailQuery = useQuery({
    queryKey: ["evidence-document", selectedSourceId, searchSource],
    queryFn: () => getEvidenceDocument(selectedSourceId as string, searchSource),
    enabled: !!selectedSourceId,
  });
  const matchReportsQuery = useQuery({
    queryKey: ["evidence-match-reports", projectId],
    queryFn: () => listEvidenceMatchReports(undefined, projectId),
    enabled: !!projectId,
  });
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
                <li key={d.sourceId} className="relative">
                  <button
                    onClick={() => setSelectedSourceId(d.sourceId)}
                    aria-pressed={selectedSourceId === d.sourceId}
                    className={`w-full rounded-lg border p-3.5 pr-24 text-left text-xs transition-colors ${
                      selectedSourceId === d.sourceId ? "border-accent bg-accent-soft" : "border-border bg-surface hover:bg-surface-sunken"
                    }`}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <p className="font-medium text-ink">{d.title || t("page3.noTitle")}</p>
                      {/* mr-1: the "详情" button sits absolutely-positioned
                          at right-2.5 outside this button's own pr-24 -
                          without this the badge, flush against that padded
                          edge, visually touches/overlaps it. */}
                      {d.relevant === true && (
                        <span className="mr-1 shrink-0 rounded-full border border-accent px-1.5 py-0.5 text-[10px] font-medium text-accent-strong">{t("page3.relevantToProject")}</span>
                      )}
                    </div>
                    <p className="text-ink-muted">{d.authors.join(", ") || t("page3.authorsNotReported")} · {d.publicationYear ?? t("page3.noDate")} · {d.journalOrRepository ?? t("page3.metadataOnly")}</p>
                    {d.doiOrAccession ? (
                      <p className="font-mono text-[11px] text-ink-faint">{d.doiOrAccession}</p>
                    ) : (
                      <p className="text-[11px] italic text-ink-faint">{t("page3.noDoiReported")}</p>
                    )}
                  </button>
                  {searchSource === "local_ddr" && (
                    <Link
                      to={`/projects/${projectId}/evidence/${d.sourceId}`}
                      onClick={(e) => e.stopPropagation()}
                      className="absolute right-2.5 top-3 flex items-center gap-1 rounded border border-border bg-surface px-1.5 py-1 text-[10px] font-medium text-ink-muted hover:bg-surface-sunken"
                    >
                      <ExternalLink size={10} aria-hidden />
                      {t("common.viewDetail")}
                    </Link>
                  )}
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
                projectId={projectId}
                isLocalDdr={searchSource === "local_ddr"}
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
        {!projectId && <p className="text-[11px] text-ink-faint">{t("paperEvidence.applicability.noProjectDetail")}</p>}
        {projectId && matchReportsQuery.isLoading && <EmptyState variant="loading" />}
        {projectId && matchReportsQuery.data && matchReportsQuery.data.length === 0 && (
          <EmptyState variant="first_use" title={t("page3.noMatchReportsYet")} detail={t("page3.noMatchReportsDetail")} />
        )}
        {matchReportsQuery.data && matchReportsQuery.data.length > 0 && (
          <ul className="flex flex-col gap-1.5">
            {matchReportsQuery.data.map((m) => {
              // DDR-sourced evidence only ever carries `organism` as a
              // structured comparable field (harness/evidence_retrieval/
              // service.py::assess_ddr_applicability) - strain/genotype/
              // medium/condition are permanently "unknown" for every DDR,
              // not a per-item signal. Showing all four every time buried
              // the one thing that actually varies (organism/directness/
              // the mismatch reasons below) under repeated noise.
              const dimensions: Array<[string, string]> = [
                [t("page3.strain"), m.strainMatch],
                [t("page3.genotype"), m.genotypeMatch],
                [t("page3.medium"), m.mediumMatch],
                [t("page3.condition"), m.conditionMatch],
              ];
              const knownDimensions = dimensions.filter(([, value]) => value !== "unknown");
              const uncomparableLabels = dimensions.filter(([, value]) => value === "unknown").map(([label]) => label);
              return (
                <li key={m.matchReportId} className="panel flex flex-col gap-1 p-2.5">
                  <div className="flex items-center justify-between">
                    <span className="font-mono text-ink-faint">{m.evidenceId}</span>
                    <StatusBadge status={matchStatusToBadge(m.overallMatchStatus)} label={m.overallMatchStatus} />
                  </div>
                  <div className="flex flex-wrap gap-x-3 gap-y-0.5 text-[11px] text-ink-muted">
                    <span>{t("page3.organism")}: {m.organismMatch}</span>
                    {knownDimensions.map(([label, value]) => <span key={label}>{label}: {value}</span>)}
                    <span>{t("page3.directness")}: {m.directness}</span>
                  </div>
                  {uncomparableLabels.length > 0 && (
                    <p className="text-[11px] text-ink-faint">
                      {t("paperEvidence.applicability.missingDataPrefix")} {uncomparableLabels.join(", ")}
                    </p>
                  )}
                  {/* "X could not be compared (missing metadata)" entries are
                      the same fact as `uncomparableLabels` above, restated
                      per-dimension - only show risks that say something new. */}
                  {(() => {
                    const meaningfulRisks = m.transferRisks.filter((r) => !r.endsWith("could not be compared (missing metadata)"));
                    return meaningfulRisks.length > 0 && (
                      <p className="text-[11px] text-state-caution">{t("page3.transferRisks")}: {meaningfulRisks.join("; ")}</p>
                    );
                  })()}
                  {m.downgradeReasons.length > 0 && <p className="text-[11px] text-state-risk">{t("page3.downgraded")}: {m.downgradeReasons.join("; ")}</p>}
                </li>
              );
            })}
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
  projectId,
  isLocalDdr,
}: {
  detail: EvidenceDocumentDetail | null;
  isLoading: boolean;
  hasSelection: boolean;
  onClose: () => void;
  projectId: string | undefined;
  isLocalDdr: boolean;
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

      {/* Only local_ddr documents have a matching PaperEvidenceDetailPage
          route (harness/api/generation.py::get_evidence_document) - this is
          where the 抽取思路/实验设计思路/质量与置信度/原文对照 tabs live,
          none of which fit in this narrow inline panel. Without this the
          panel above was a dead end: nothing here linked back out to them. */}
      {isLocalDdr && projectId && (
        <Link
          to={`/projects/${projectId}/evidence/${detail.sourceId}`}
          className="flex w-fit items-center gap-1 rounded border border-border bg-surface px-2 py-1 text-[11px] font-medium text-ink-muted hover:bg-surface-sunken"
        >
          <ExternalLink size={11} aria-hidden />
          {t("page3.detail.viewFullDetail")}
        </Link>
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
