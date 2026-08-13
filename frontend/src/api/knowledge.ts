import { api, ApiError } from "./client";
import { getTimeline } from "./projects";
import type { ExperimentRunSummary } from "./experiments";
import type { EvidenceSummary } from "@/types/domain";

/**
 * KnowledgeClaim adapter (harness/api/learning.py, real, uncommitted,
 * covered by tests/projects/test_knowledge_claims.py). This is the real
 * `KnowledgeObject` substrate for Page 3 - see
 * docs/前端精修/page3_backend_mapping_matrix.md for the full audit. No
 * list-all route exists; `discoverProjectClaimIds` derives the id set from
 * the real project event ledger instead (derived_real, not a fixture).
 *
 * IMPORTANT field-availability note (read the actual FastAPI handler, not
 * guessed from the SQLAlchemy model): `GET /knowledge-claims/{id}` returns
 * only claim_id/statement/scope/status/independence_groups/evidence_grade/
 * promotion_record. It does NOT return project_id, supporting_experiments,
 * contradicting_experiments, reviewers, created_by, created_at, updated_at,
 * or supersedes_claim_id, even though all of those exist on the
 * `KnowledgeClaim` table. `null` on those fields below means exactly that -
 * "this read endpoint does not serialize this field" - never defaulted to
 * `[]`/`""` (an empty array would misrepresent "confirmed zero" for a field
 * that is actually just unavailable; System Invariant "No Unsupported
 * Synthesis" / §51 "禁止静默伪造字段").
 */

export const KNOWLEDGE_CLAIM_STATUSES = ["project_candidate", "lab_candidate", "lab_approved", "retracted"] as const;
export type KnowledgeClaimStatus = (typeof KNOWLEDGE_CLAIM_STATUSES)[number];

/** Mirrors harness/memory/knowledge_claims.py::MIN_INDEPENDENT_GROUPS_FOR_PROMOTION so the UI shows the exact threshold the server enforces, never a separately-invented number. */
export const MIN_INDEPENDENT_GROUPS_FOR_PROMOTION = 3;

export function countIndependentGroups(independenceGroups: string[][]): number {
  return independenceGroups.filter((g) => g.length > 0).length;
}

/** Every distinct experiment_run_id named anywhere in independence_groups - the only supporting-evidence ids the real detail endpoint actually exposes. */
export function experimentIdsFromIndependenceGroups(independenceGroups: string[][]): string[] {
  return [...new Set(independenceGroups.flat())];
}

export interface PromotionRecordEntry {
  status: string;
  actorId: string;
  at: number;
  reason: string;
}

export interface KnowledgeClaim {
  claimId: string;
  /** Known only because the caller supplied the project it discovered this claim under (via the project timeline) - not returned by GET itself. */
  projectId: string;
  statement: string;
  scope: Record<string, unknown>;
  /** Real, returned by GET. Each inner array is a set of mutually-non-independent experiment_run_ids (same batch/construction background); group *count* (not id count) is what the promotion threshold checks. */
  independenceGroups: string[][];
  evidenceGrade: string;
  status: KnowledgeClaimStatus | string;
  promotionRecord: PromotionRecordEntry[];
  /** null = "GET does not return this field" (see file header), not "confirmed empty". Populated only via `withSubmittedEcho` immediately after this browser session's own submission. */
  contradictingExperimentsAsSubmitted: string[] | null;
  reviewersAsSubmitted: string[] | null;
}

interface RawClaim {
  claim_id: string;
  statement: string;
  scope: Record<string, unknown>;
  independence_groups: string[][];
  evidence_grade: string;
  status: string;
  promotion_record: Array<{ status: string; actor_id: string; at: number; reason: string }>;
}

function toClaim(r: RawClaim, projectId: string): KnowledgeClaim {
  return {
    claimId: r.claim_id,
    projectId,
    statement: r.statement,
    scope: r.scope ?? {},
    independenceGroups: r.independence_groups ?? [],
    evidenceGrade: r.evidence_grade,
    status: r.status,
    promotionRecord: (r.promotion_record ?? []).map((p) => ({ status: p.status, actorId: p.actor_id, at: p.at, reason: p.reason })),
    contradictingExperimentsAsSubmitted: null,
    reviewersAsSubmitted: null,
  };
}

export async function getClaim(claimId: string, projectId: string): Promise<KnowledgeClaim | null> {
  try {
    const r = await api.get<RawClaim>(`/api/learning/knowledge-claims/${claimId}`);
    return toClaim(r, projectId);
  } catch (e) {
    if (e instanceof ApiError && e.status === 404) return null;
    throw e;
  }
}

/**
 * `GET /api/projects/{id}/timeline` is a real, complete event ledger
 * (harness/memory/event_store.py). KNOWLEDGE_CLAIM_SUBMITTED/PROMOTED/
 * DEMOTED/RETRACTED events (harness/memory/event_types.py) carry
 * entity_type="KnowledgeClaim" - filtering + de-duplicating this list is
 * the only real way to answer "which claims exist in this project" since
 * no dedicated list route exists (page3_backend_mapping_matrix.md).
 */
export async function discoverProjectClaimIds(projectId: string): Promise<string[]> {
  const events = await getTimeline(projectId);
  const ids = new Set<string>();
  for (const e of events) {
    if (e.entityType === "KnowledgeClaim") ids.add(e.entityId);
  }
  return [...ids];
}

/** Rejected-fabricated-reference events (GEN_HALLUCINATED_REFERENCE_REJECTED) for this project, from the same real timeline. */
export async function discoverHallucinatedReferenceRejections(projectId: string) {
  const events = await getTimeline(projectId);
  return events.filter((e) => e.eventType === "GEN_HALLUCINATED_REFERENCE_REJECTED");
}

export interface SubmitClaimInput {
  projectId: string;
  statement: string;
  scope: Record<string, unknown>;
  supportingExperiments: string[];
  independenceGroups: string[][];
  createdBy: string;
  contradictingExperiments?: string[];
  evidenceGrade?: "high" | "medium" | "low";
}

/** Always returns status="project_candidate" - the backend does not let a submitter choose the starting status (verified by reading submit_claim). The response itself is just {claim_id, status}; it does not echo back any submitted field. */
export async function submitClaim(input: SubmitClaimInput): Promise<{ claimId: string; status: string }> {
  const r = await api.post<{ claim_id: string; status: string }>("/api/learning/knowledge-claims", {
    project_id: input.projectId,
    statement: input.statement,
    scope: input.scope,
    supporting_experiments: input.supportingExperiments,
    independence_groups: input.independenceGroups,
    created_by: input.createdBy,
    contradicting_experiments: input.contradictingExperiments ?? [],
    evidence_grade: input.evidenceGrade ?? "low",
  });
  return { claimId: r.claim_id, status: r.status };
}

export class PromotionRejectedError extends Error {}

export interface PromoteClaimResult {
  claimId: string;
  status: string;
  promotionRecord: PromotionRecordEntry[];
}

/**
 * Surfaces the real 422 PromotionRejected reason (self-approval, <3
 * independent groups, or unaddressed conflict) verbatim rather than a
 * generic failure message. `POST .../promote` only returns
 * claim_id/status/promotion_record (not the full claim) - callers refetch
 * via `getClaim` on success rather than this function fabricating the
 * missing fields.
 */
export async function promoteClaim(claimId: string, input: { targetStatus: string; reviewerId: string; reason?: string }): Promise<PromoteClaimResult> {
  try {
    const r = await api.post<{ claim_id: string; status: string; promotion_record: Array<{ status: string; actor_id: string; at: number; reason: string }> }>(
      `/api/learning/knowledge-claims/${claimId}/promote`,
      { target_status: input.targetStatus, reviewer_id: input.reviewerId, reason: input.reason ?? "" },
    );
    return {
      claimId: r.claim_id,
      status: r.status,
      promotionRecord: r.promotion_record.map((p) => ({ status: p.status, actorId: p.actor_id, at: p.at, reason: p.reason })),
    };
  } catch (e) {
    if (e instanceof ApiError && e.status === 422) throw new PromotionRejectedError(e.message);
    throw e;
  }
}

export async function retractClaim(claimId: string, input: { reviewerId: string; reason: string }): Promise<{ claimId: string; status: string }> {
  const r = await api.post<{ claim_id: string; status: string }>(`/api/learning/knowledge-claims/${claimId}/retract`, {
    reviewer_id: input.reviewerId,
    reason: input.reason,
  });
  return { claimId: r.claim_id, status: r.status };
}

/** The 7 real scope dimensions per KnowledgeClaim's own field docstring (harness/learning/models.py) - fixed, not guessed. */
export const APPLICABILITY_SCOPE_KEYS = ["species", "strain_background", "genotype_context", "medium", "carbon_source", "cultivation_mode", "assay"] as const;

/**
 * Adapts a resolved ExperimentRun (harness/api/experiments.py) into the
 * shared EvidenceDrawer's view model (prompt §16/§30), the same pattern
 * `evidenceLinkToSummary` uses in api/diagnosis.ts. `strainMatch`/
 * `conditionMatch` stay "unknown" - `GET /experiments/runs/{id}` does not
 * return condition/strain data, only execution_status/deviations.
 */
export function experimentRunToEvidenceSummary(run: ExperimentRunSummary, relation: "supports" | "contradicts" = "supports"): EvidenceSummary {
  return {
    id: run.experimentRunId,
    kind: "observation",
    title: `Experiment run ${run.experimentRunId} — ${run.executionStatus}${run.deviations.length > 0 ? ` (${run.deviations.length} deviation${run.deviations.length === 1 ? "" : "s"})` : ""}`,
    relation,
    strainMatch: "unknown",
    conditionMatch: "unknown",
    contradictory: relation === "contradicts",
  };
}
