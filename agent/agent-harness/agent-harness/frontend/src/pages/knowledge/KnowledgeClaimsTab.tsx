import { useMemo, useState } from "react";
import { useParams, useSearchParams } from "react-router-dom";
import { useMutation, useQueries, useQuery, useQueryClient } from "@tanstack/react-query";
import { FlaskConical, GitCompare, Plus, ShieldCheck, XCircle } from "lucide-react";
import {
  APPLICABILITY_SCOPE_KEYS,
  MIN_INDEPENDENT_GROUPS_FOR_PROMOTION,
  PromotionRejectedError,
  countIndependentGroups,
  discoverProjectClaimIds,
  experimentIdsFromIndependenceGroups,
  experimentRunToEvidenceSummary,
  getClaim,
  promoteClaim,
  retractClaim,
  submitClaim,
  type KnowledgeClaim,
  type KnowledgeClaimStatus,
} from "@/api/knowledge";
import { getExperimentRun } from "@/api/experiments";
import { ApplicabilityPanel } from "@/components/knowledge/ApplicabilityPanel";
import { EmptyState } from "@/components/common/EmptyState";
import { EvidenceDrawer } from "@/components/workspace/EvidenceDrawer";
import { ObjectInspector } from "@/components/workspace/ObjectInspector";
import { ScientificObjectHeader } from "@/components/workspace/ScientificObjectHeader";
import { StatusBadge, type BadgeStatus } from "@/components/common/StatusBadge";
import { useUrlSelection } from "@/hooks/useUrlSelection";
import { useI18n, type DictKey } from "@/lib/i18n";
import type { EvidenceSummary } from "@/types/domain";

const STATUS_FILTERS: Array<{ id: KnowledgeClaimStatus | "all" | "insufficient_evidence"; labelKey: DictKey }> = [
  { id: "all", labelKey: "page3.filter.all" },
  { id: "project_candidate", labelKey: "badge.project_candidate" },
  { id: "lab_candidate", labelKey: "badge.lab_candidate" },
  { id: "lab_approved", labelKey: "badge.lab_approved" },
  { id: "retracted", labelKey: "badge.retracted" },
  { id: "insufficient_evidence", labelKey: "page3.filter.insufficientEvidence" },
];

const SCOPE_KEY_LABEL: Record<(typeof APPLICABILITY_SCOPE_KEYS)[number], DictKey> = {
  species: "applicability.species",
  strain_background: "applicability.strainBackground",
  genotype_context: "applicability.genotypeContext",
  medium: "applicability.medium",
  carbon_source: "applicability.carbonSource",
  cultivation_mode: "applicability.cultivationMode",
  assay: "applicability.assay",
};

const COMPARE_CAP = 4;

/**
 * Knowledge Production surface (Page 3 prompt §13-19, §26-27, §31-32): the
 * real KnowledgeClaim promotion ladder, rendered as one continuous object
 * lifecycle (submit -> promote/retract -> version history) rather than
 * disjoint tool entry points, per DSR-KC-001. Every field either traces to
 * a real HTTP response or is an explicit "unavailable via current API"
 * notice - see page3_backend_mapping_matrix.md for the exact per-field
 * audit (the GET route does not return supporting/contradicting
 * experiments, reviewers, or timestamps).
 */
export function KnowledgeClaimsTab() {
  const { t } = useI18n();
  const { projectId } = useParams<{ projectId: string }>();
  const qc = useQueryClient();
  const [selectedClaimId, setSelectedClaimId] = useUrlSelection();
  const [params, setParams] = useSearchParams();
  const [statusFilter, setStatusFilter] = useState<(typeof STATUS_FILTERS)[number]["id"]>("all");
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [evidence, setEvidence] = useState<{ items: EvidenceSummary[]; subject?: string }>({ items: [] });
  const [showSubmitForm, setShowSubmitForm] = useState(false);
  const [submittingAs, setSubmittingAs] = useState("frontend-user");
  const [reviewingAs, setReviewingAs] = useState("frontend-reviewer");
  const [lastSubmitted, setLastSubmitted] = useState<{ claimId: string; contradictingExperiments: string[]; createdBy: string } | null>(null);

  const compareIds = useMemo(() => (params.get("compare") ?? "").split(",").filter(Boolean), [params]);
  function setCompareIds(ids: string[]) {
    const next = new URLSearchParams(params);
    if (ids.length === 0) next.delete("compare");
    else next.set("compare", ids.join(","));
    setParams(next, { replace: true });
  }
  function toggleCompare(id: string) {
    if (compareIds.includes(id)) setCompareIds(compareIds.filter((x) => x !== id));
    else if (compareIds.length < COMPARE_CAP) setCompareIds([...compareIds, id]);
  }

  const idsQuery = useQuery({
    queryKey: ["knowledge-claim-ids", projectId],
    queryFn: () => discoverProjectClaimIds(projectId as string),
    enabled: !!projectId,
  });

  const claimQueries = useQueries({
    queries: (idsQuery.data ?? []).map((id) => ({
      queryKey: ["knowledge-claim", id, projectId],
      queryFn: () => getClaim(id, projectId as string),
      enabled: !!projectId,
    })),
  });
  const claimsLoading = idsQuery.isLoading || claimQueries.some((q) => q.isLoading);
  const claims: KnowledgeClaim[] = claimQueries.map((q) => q.data).filter((c): c is KnowledgeClaim => !!c);

  const counts = useMemo(() => {
    const c: Record<string, number> = { all: claims.length };
    for (const claim of claims) {
      c[claim.status] = (c[claim.status] ?? 0) + 1;
      if (countIndependentGroups(claim.independenceGroups) < MIN_INDEPENDENT_GROUPS_FOR_PROMOTION) {
        c.insufficient_evidence = (c.insufficient_evidence ?? 0) + 1;
      }
    }
    return c;
  }, [claims]);

  const filteredClaims = useMemo(() => {
    if (statusFilter === "all") return claims;
    if (statusFilter === "insufficient_evidence") {
      return claims.filter((c) => countIndependentGroups(c.independenceGroups) < MIN_INDEPENDENT_GROUPS_FOR_PROMOTION);
    }
    return claims.filter((c) => c.status === statusFilter);
  }, [claims, statusFilter]);

  const selectedClaim = claims.find((c) => c.claimId === selectedClaimId) ?? null;

  const submitMutation = useMutation({
    mutationFn: submitClaim,
    onSuccess: (r, vars) => {
      setLastSubmitted({ claimId: r.claimId, contradictingExperiments: vars.contradictingExperiments ?? [], createdBy: vars.createdBy });
      qc.invalidateQueries({ queryKey: ["knowledge-claim-ids", projectId] });
      setSelectedClaimId(r.claimId);
      setShowSubmitForm(false);
    },
  });

  const promoteMutation = useMutation({
    mutationFn: (input: { claimId: string; targetStatus: string; reason: string }) =>
      promoteClaim(input.claimId, { targetStatus: input.targetStatus, reviewerId: reviewingAs, reason: input.reason }),
    onSuccess: (_r, vars) => qc.invalidateQueries({ queryKey: ["knowledge-claim", vars.claimId, projectId] }),
  });

  const retractMutation = useMutation({
    mutationFn: (input: { claimId: string; reason: string }) => retractClaim(input.claimId, { reviewerId: reviewingAs, reason: input.reason }),
    onSuccess: (_r, vars) => qc.invalidateQueries({ queryKey: ["knowledge-claim", vars.claimId, projectId] }),
  });

  async function openEvidenceFor(claim: KnowledgeClaim) {
    const expIds = experimentIdsFromIndependenceGroups(claim.independenceGroups);
    if (expIds.length === 0) {
      setEvidence({ items: [], subject: claim.claimId });
      setDrawerOpen(true);
      return;
    }
    const runs = await Promise.all(expIds.map((id) => getExperimentRun(id)));
    const items = runs.filter((r): r is NonNullable<typeof r> => !!r).map((r) => experimentRunToEvidenceSummary(r, "supports"));
    setEvidence({ items, subject: claim.statement || claim.claimId });
    setDrawerOpen(true);
  }

  if (!projectId) return null;

  return (
    <div className="grid items-start gap-4 xl:grid-cols-[minmax(560px,1fr)_380px]">
      <div className="flex min-w-0 flex-1 flex-col gap-3">
        <div className="panel flex flex-wrap items-center justify-between gap-3 p-3">
          <div className="flex flex-wrap items-center gap-1.5">
            {STATUS_FILTERS.map((f) => (
              <button
                key={f.id}
                onClick={() => setStatusFilter(f.id)}
                className={`rounded-full border px-2.5 py-1.5 text-[11px] font-medium transition ${
                  statusFilter === f.id ? "border-accent bg-accent-soft text-accent-strong" : "border-border bg-surface text-ink-muted hover:bg-surface-sunken"
                }`}
              >
                {t(f.labelKey)} <span className="text-ink-faint">({counts[f.id] ?? 0})</span>
              </button>
            ))}
          </div>
          <button
            onClick={() => setShowSubmitForm((v) => !v)}
            className="flex items-center gap-1.5 rounded-lg bg-accent px-3 py-2 text-xs font-medium text-white shadow-sm"
          >
            <Plus size={13} /> {t("page3.submitClaimButton")}
          </button>
        </div>

        {showSubmitForm && (
          <SubmitClaimForm
            projectId={projectId}
            submittingAs={submittingAs}
            onSubmittingAsChange={setSubmittingAs}
            pending={submitMutation.isPending}
            error={submitMutation.isError ? String(submitMutation.error) : null}
            onSubmit={(vals) => submitMutation.mutate({ projectId, createdBy: submittingAs, ...vals })}
          />
        )}

        {compareIds.length > 0 && (
          <KnowledgeComparisonTray claimIds={compareIds} projectId={projectId} onRemove={(id) => toggleCompare(id)} onClear={() => setCompareIds([])} />
        )}

        <div
          className="panel flex min-h-[420px] flex-col overflow-y-auto p-3"
          tabIndex={0}
          role="region"
          aria-label={t("page3.tab.claims")}
        >
          {claimsLoading && <EmptyState variant="loading" />}
          {!claimsLoading && idsQuery.data && idsQuery.data.length === 0 && (
            <EmptyState
              variant="first_use"
              title={t("page3.noClaimsForProject")}
              detail={t("claim.noClaimsDiscoverableDetail")}
            />
          )}
          {!claimsLoading && filteredClaims.length === 0 && (idsQuery.data?.length ?? 0) > 0 && (
            <EmptyState variant="no_result" title={t("page3.noClaimsMatchFilter")} />
          )}
          {!claimsLoading && filteredClaims.length > 0 && (
            <ul className="flex flex-col gap-1.5">
              {filteredClaims.map((claim) => {
                const indepCount = countIndependentGroups(claim.independenceGroups);
                const insufficient = indepCount < MIN_INDEPENDENT_GROUPS_FOR_PROMOTION;
                return (
                  <li key={claim.claimId}>
                    <div
                      className={`flex flex-col gap-2 rounded-lg border px-3.5 py-3 text-left text-xs transition-colors ${
                        selectedClaimId === claim.claimId ? "border-accent bg-accent-soft" : "border-border bg-surface hover:bg-surface-sunken"
                      }`}
                    >
                      <button onClick={() => setSelectedClaimId(claim.claimId)} aria-pressed={selectedClaimId === claim.claimId} className="flex w-full items-start justify-between gap-2 text-left">
                        <span className="font-medium text-ink">{claim.statement || t("claim.noStatementRecorded")}</span>
                        <StatusBadge status={claim.status as BadgeStatus} />
                      </button>
                      <div className="flex flex-wrap items-center gap-2 text-[11px] text-ink-muted">
                        <span className="font-mono text-ink-faint">{claim.claimId}</span>
                        <span>{t("claim.evidenceGradeLabel")}: {claim.evidenceGrade}</span>
                        <span>{indepCount} {t("claim.independentGroupUnit")}</span>
                        {insufficient && <span className="rounded border border-amber-300 bg-amber-50 px-1 py-0.5 text-state-caution">{t("claim.belowPromotionThreshold")}{MIN_INDEPENDENT_GROUPS_FOR_PROMOTION})</span>}
                        <span>{claim.promotionRecord.length} {t("claim.versionUnit")}</span>
                        <button
                          type="button"
                          onClick={(e) => {
                            e.stopPropagation();
                            toggleCompare(claim.claimId);
                          }}
                          disabled={!compareIds.includes(claim.claimId) && compareIds.length >= COMPARE_CAP}
                          className={`ml-auto flex items-center gap-1 rounded border px-1.5 py-0.5 ${
                            compareIds.includes(claim.claimId) ? "border-accent text-accent-strong" : "border-border text-ink-faint hover:text-ink"
                          } disabled:opacity-40`}
                        >
                          <GitCompare size={11} /> {compareIds.includes(claim.claimId) ? t("page3.comparing_verb") : t("page3.compare")}
                        </button>
                      </div>
                    </div>
                  </li>
                );
              })}
            </ul>
          )}
        </div>
      </div>

      <div className="w-full min-w-0">
        <div className="panel flex min-h-[420px] max-h-[calc(100vh-230px)] flex-col overflow-y-auto xl:sticky xl:top-0">
          {selectedClaim ? (
            <KnowledgeClaimInspector
              claim={selectedClaim}
              submittedEcho={lastSubmitted?.claimId === selectedClaim.claimId ? lastSubmitted : null}
              reviewingAs={reviewingAs}
              onReviewingAsChange={setReviewingAs}
              onOpenEvidence={() => openEvidenceFor(selectedClaim)}
              onPromote={(targetStatus, reason) => promoteMutation.mutate({ claimId: selectedClaim.claimId, targetStatus, reason })}
              onRetract={(reason) => retractMutation.mutate({ claimId: selectedClaim.claimId, reason })}
              promotePending={promoteMutation.isPending}
              promoteError={promoteMutation.isError ? promoteMutation.error : null}
              retractPending={retractMutation.isPending}
              retractError={retractMutation.isError ? String(retractMutation.error) : null}
            />
          ) : (
            <ObjectInspector identity={null} />
          )}
        </div>
      </div>
      <EvidenceDrawer open={drawerOpen} onClose={() => setDrawerOpen(false)} items={evidence.items} subjectLabel={evidence.subject} projectId={projectId} />
    </div>
  );
}

function KnowledgeClaimInspector({
  claim,
  submittedEcho,
  reviewingAs,
  onReviewingAsChange,
  onOpenEvidence,
  onPromote,
  onRetract,
  promotePending,
  promoteError,
  retractPending,
  retractError,
}: {
  claim: KnowledgeClaim;
  submittedEcho: { contradictingExperiments: string[]; createdBy: string } | null;
  reviewingAs: string;
  onReviewingAsChange: (v: string) => void;
  onOpenEvidence: () => void;
  onPromote: (targetStatus: string, reason: string) => void;
  onRetract: (reason: string) => void;
  promotePending: boolean;
  promoteError: unknown;
  retractPending: boolean;
  retractError: string | null;
}) {
  const { t } = useI18n();
  const [promoteTarget, setPromoteTarget] = useState<"lab_candidate" | "lab_approved">("lab_candidate");
  const [reason, setReason] = useState("");
  const indepCount = countIndependentGroups(claim.independenceGroups);
  const belowThreshold = indepCount < MIN_INDEPENDENT_GROUPS_FOR_PROMOTION;

  return (
    <div className="flex flex-col gap-3 p-3 text-xs">
      <ScientificObjectHeader objectType="KnowledgeClaim" title={claim.statement || claim.claimId} id={claim.claimId} status={claim.status as BadgeStatus} version={claim.promotionRecord.length} />
      <div className="flex items-center gap-3">
        <span>
          <span className="text-ink-faint">{t("claim.evidenceGrade")}</span> <span className="font-medium text-ink">{claim.evidenceGrade}</span>
        </span>
        <span className="text-ink-faint">·</span>
        <span>
          <span className="text-ink-faint">{t("claim.governanceStatus")}</span> <StatusBadge status={claim.status as BadgeStatus} />
        </span>
      </div>

      <ApplicabilityPanel scope={claim.scope} />

      <div className="flex flex-col gap-1">
        <h3 className="label-caps">{t("page3.supportingEvidence")}</h3>
        <div className="flex items-center justify-between">
          <span>
            {indepCount} {t("claim.independentGroupUnit")} / {MIN_INDEPENDENT_GROUPS_FOR_PROMOTION} {t("claim.requiredForLabReview")}
          </span>
          <button onClick={onOpenEvidence} className="flex items-center gap-1 text-accent-strong underline decoration-dotted underline-offset-2">
            <FlaskConical size={11} /> {t("page3.openEvidence")}
          </button>
        </div>
        {belowThreshold && (
          <p className="rounded border border-amber-300 bg-amber-50 px-2 py-1 text-state-caution">
            {t("claim.insufficientForPromotionDetail")}
          </p>
        )}
      </div>

      <div className="flex flex-col gap-1">
        <h3 className="label-caps">{t("page3.conflictingEvidence")}</h3>
        {submittedEcho ? (
          submittedEcho.contradictingExperiments.length > 0 ? (
            <ul className="list-disc pl-4">
              {submittedEcho.contradictingExperiments.map((id) => (
                <li key={id} className="font-mono text-[11px] text-state-risk">{id}</li>
              ))}
            </ul>
          ) : (
            <p className="text-ink-faint">{t("claim.noneRecordedAtSubmission")}</p>
          )
        ) : (
          <p className="text-ink-faint">
            {t("claim.contradictingUnavailableDetail")}
          </p>
        )}
      </div>

      <div className="flex flex-col gap-1">
        <h3 className="label-caps">{t("page3.versionHistory")}</h3>
        {claim.promotionRecord.length === 0 ? (
          <p className="text-ink-faint">{t("claim.noTransitionsRecorded")}</p>
        ) : (
          <ul className="flex flex-col gap-1 border-t border-border pt-1">
            {claim.promotionRecord.map((p, i) => (
              <li key={i} className="flex flex-col gap-0.5 border-b border-border pb-1 last:border-0">
                <div className="flex items-center justify-between">
                  <StatusBadge status={p.status as BadgeStatus} />
                  <span className="text-ink-faint">{new Date(p.at * 1000).toLocaleString()}</span>
                </div>
                <span className="text-ink-muted">{t("claim.by")} {p.actorId}{p.reason ? ` — ${p.reason}` : ""}</span>
              </li>
            ))}
          </ul>
        )}
      </div>

      <div className="flex flex-col gap-1">
        <h3 className="label-caps">{t("page3.engineeringReuse")}</h3>
        {claim.status === "lab_approved" ? (
          <p className="rounded border border-slate-300 bg-slate-50 px-2 py-1 text-ink-muted">
            {t("claim.reuseUnavailableDetail")}
          </p>
        ) : (
          <p className="text-ink-faint">{t("claim.onlyForLabApproved")} {claim.status}.</p>
        )}
      </div>

      <div className="flex flex-col gap-1.5 border-t border-border pt-2">
        <h3 className="label-caps flex items-center gap-1"><ShieldCheck size={12} /> {t("page3.promoteRetract")}</h3>
        <label className="flex flex-col gap-0.5">
          <span className="text-ink-faint">{t("claim.reviewingAs")}</span>
          <input value={reviewingAs} onChange={(e) => onReviewingAsChange(e.target.value)} className="rounded border border-border px-1.5 py-1 text-xs" />
        </label>
        <p className="text-[11px] text-ink-faint">{t("claim.reviewerMustDiffer")}</p>
        <textarea value={reason} onChange={(e) => setReason(e.target.value)} placeholder={t("claim.reasonPlaceholder")} className="min-h-[44px] rounded border border-border px-1.5 py-1 text-xs" />
        <div className="flex items-center gap-1.5">
          <select value={promoteTarget} onChange={(e) => setPromoteTarget(e.target.value as "lab_candidate" | "lab_approved")} className="rounded border border-border px-1.5 py-1 text-xs">
            <option value="lab_candidate">{t("badge.lab_candidate")}</option>
            <option value="lab_approved">{t("badge.lab_approved")}</option>
          </select>
          <button
            disabled={promotePending}
            onClick={() => onPromote(promoteTarget, reason)}
            className="flex items-center gap-1 rounded border border-emerald-300 bg-emerald-50 px-2 py-1 font-medium text-state-success disabled:opacity-40"
          >
            {t("page3.promote")}
          </button>
          <button
            disabled={retractPending || !reason.trim()}
            onClick={() => onRetract(reason)}
            className="flex items-center gap-1 rounded border border-red-300 bg-red-50 px-2 py-1 font-medium text-state-risk disabled:opacity-40"
          >
            <XCircle size={12} /> {t("page3.retract")}
          </button>
        </div>
        {promoteError ? (
          <p className="text-state-risk">{promoteError instanceof PromotionRejectedError ? promoteError.message : String(promoteError)}</p>
        ) : null}
        {retractError && <p className="text-state-risk">{retractError}</p>}
      </div>
    </div>
  );
}

function SubmitClaimForm({
  submittingAs,
  onSubmittingAsChange,
  pending,
  error,
  onSubmit,
}: {
  projectId: string;
  submittingAs: string;
  onSubmittingAsChange: (v: string) => void;
  pending: boolean;
  error: string | null;
  onSubmit: (vals: {
    statement: string;
    scope: Record<string, unknown>;
    supportingExperiments: string[];
    independenceGroups: string[][];
    contradictingExperiments: string[];
    evidenceGrade: "high" | "medium" | "low";
  }) => void;
}) {
  const { t } = useI18n();
  const [statement, setStatement] = useState("");
  const [scope, setScope] = useState<Record<string, string>>({});
  const [groups, setGroups] = useState<string[]>([""]);
  const [contradicting, setContradicting] = useState("");
  const [grade, setGrade] = useState<"high" | "medium" | "low">("low");

  function submit() {
    const independenceGroups = groups.map((g) => g.split(",").map((s) => s.trim()).filter(Boolean)).filter((g) => g.length > 0);
    const supportingExperiments = [...new Set(independenceGroups.flat())];
    const scopeClean: Record<string, unknown> = {};
    for (const [k, v] of Object.entries(scope)) if (v.trim()) scopeClean[k] = v.trim();
    onSubmit({
      statement,
      scope: scopeClean,
      supportingExperiments,
      independenceGroups,
      contradictingExperiments: contradicting.split(",").map((s) => s.trim()).filter(Boolean),
      evidenceGrade: grade,
    });
  }

  return (
    <div className="panel flex flex-col gap-2 p-3 text-xs">
      <h3 className="label-caps">{t("page3.submitClaim")}</h3>
      <p className="text-ink-faint">{t("claim.alwaysStartsCandidate")}</p>
      <label className="flex flex-col gap-0.5">
        <span className="text-ink-faint">{t("claim.submittingAs")}</span>
        <input value={submittingAs} onChange={(e) => onSubmittingAsChange(e.target.value)} className="rounded border border-border px-1.5 py-1" />
      </label>
      <label className="flex flex-col gap-0.5">
        <span className="text-ink-faint">{t("claim.statement")}</span>
        <textarea value={statement} onChange={(e) => setStatement(e.target.value)} className="min-h-[52px] rounded border border-border px-1.5 py-1" placeholder={t("claim.statementPlaceholder")} />
      </label>
      <fieldset className="grid grid-cols-2 gap-1.5">
        <legend className="label-caps mb-1 w-full">{t("claim.applicabilityScope")}</legend>
        {APPLICABILITY_SCOPE_KEYS.map((key) => (
          <label key={key} className="flex flex-col gap-0.5">
            <span className="text-ink-faint">{t(SCOPE_KEY_LABEL[key])}</span>
            <input
              value={scope[key] ?? ""}
              onChange={(e) => setScope((s) => ({ ...s, [key]: e.target.value }))}
              className="rounded border border-border px-1.5 py-1"
              placeholder={t("claim.unknownIfBlank")}
            />
          </label>
        ))}
      </fieldset>
      <div className="flex flex-col gap-1">
        <span className="text-ink-faint">{t("claim.independentGroups")} {MIN_INDEPENDENT_GROUPS_FOR_PROMOTION} {t("claim.groupsRequired")}</span>
        {groups.map((g, i) => (
          <input
            key={i}
            value={g}
            onChange={(e) => setGroups((gs) => gs.map((x, idx) => (idx === i ? e.target.value : x)))}
            className="rounded border border-border px-1.5 py-1 font-mono"
            placeholder="EXPRUN-001, EXPRUN-002"
          />
        ))}
        <button type="button" onClick={() => setGroups((gs) => [...gs, ""])} className="self-start text-accent-strong underline decoration-dotted">
          {t("claim.addIndependentGroup")}
        </button>
      </div>
      <label className="flex flex-col gap-0.5">
        <span className="text-ink-faint">{t("claim.contradictingIds")}</span>
        <input value={contradicting} onChange={(e) => setContradicting(e.target.value)} className="rounded border border-border px-1.5 py-1 font-mono" />
      </label>
      <label className="flex flex-col gap-0.5">
        <span className="text-ink-faint">{t("claim.evidenceGrade")}</span>
        <select value={grade} onChange={(e) => setGrade(e.target.value as "high" | "medium" | "low")} className="rounded border border-border px-1.5 py-1">
          <option value="low">{t("claim.gradeLow")}</option>
          <option value="medium">{t("claim.gradeMedium")}</option>
          <option value="high">{t("claim.gradeHigh")}</option>
        </select>
      </label>
      <button disabled={pending || !statement.trim()} onClick={submit} className="self-start rounded bg-accent px-3 py-1.5 font-medium text-white disabled:opacity-40">
        {pending ? t("page3.submitting") : t("page3.submitAsProjectCandidate")}
      </button>
      {error && <p className="text-state-risk">{error}</p>}
    </div>
  );
}

function KnowledgeComparisonTray({ claimIds, projectId, onRemove, onClear }: { claimIds: string[]; projectId: string; onRemove: (id: string) => void; onClear: () => void }) {
  const { t } = useI18n();
  const queries = useQueries({
    queries: claimIds.map((id) => ({ queryKey: ["knowledge-claim", id, projectId], queryFn: () => getClaim(id, projectId) })),
  });
  const claims = queries.map((q) => q.data).filter((c): c is KnowledgeClaim => !!c);
  const loading = queries.some((q) => q.isLoading);

  const rows: Array<[string, (c: KnowledgeClaim) => string]> = [
    [t("table.status"), (c) => c.status],
    [t("claim.evidenceGrade"), (c) => c.evidenceGrade],
    [t("claim.independentGroupsCol"), (c) => `${countIndependentGroups(c.independenceGroups)} / ${MIN_INDEPENDENT_GROUPS_FOR_PROMOTION}`],
    [t("claim.versions"), (c) => String(c.promotionRecord.length)],
    ...APPLICABILITY_SCOPE_KEYS.map((k): [string, (c: KnowledgeClaim) => string] => [t(SCOPE_KEY_LABEL[k]), (c) => String(c.scope[k] ?? t("claim.unknownValue"))]),
  ];

  return (
    <div className="panel flex flex-col gap-2 p-3 text-xs">
      <div className="flex items-center justify-between">
        <h3 className="label-caps flex items-center gap-1"><GitCompare size={12} /> {t("page3.comparing_verb")} {claimIds.length} {t("page3.knowledgeClaims")}</h3>
        <button onClick={onClear} className="text-ink-faint hover:text-ink">{t("page3.clear")}</button>
      </div>
      {loading && <EmptyState variant="loading" />}
      {!loading && claims.length > 0 && (
        <div className="overflow-x-auto">
          <table className="w-full min-w-[480px] text-left text-[11px]">
            <thead>
              <tr className="text-ink-faint">
                <th className="pb-1 font-normal">{t("table.field")}</th>
                {claims.map((c) => (
                  <th key={c.claimId} className="pb-1 font-normal">
                    <div className="flex items-center gap-1 font-mono">
                      {c.claimId}
                      <button onClick={() => onRemove(c.claimId)} className="text-ink-faint hover:text-state-risk" aria-label={`${t("claim.removeFromComparison")} ${c.claimId}`}>
                        <XCircle size={11} />
                      </button>
                    </div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map(([label, get]) => {
                const values = claims.map(get);
                const differs = new Set(values).size > 1;
                return (
                  <tr key={label} className={`border-t border-border ${differs ? "bg-amber-50" : ""}`}>
                    <td className="py-1 pr-2 text-ink-faint">{label}</td>
                    {values.map((v, i) => (
                      <td key={i} className="py-1 pr-2 text-ink">{v}</td>
                    ))}
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
