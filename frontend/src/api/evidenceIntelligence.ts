import { api, ApiError } from "./client";

/**
 * Module 3 (Evidence Intelligence Infrastructure, harness/evidence_
 * intelligence/ + harness/api/evidence_intelligence.py): a read-side
 * aggregation over evidence that already lives in `harness.diagnosis`
 * (`EvidenceItem`) and the DDR corpus (`decision_chain[i].evidence`) - not
 * a new evidence store. `confidenceLevel` is always one of High/Medium/Low/
 * Unknown, never a bare number (see `characterization.ts`'s docstring
 * precedent in the backend for why).
 */
export type ConfidenceLevel = "High" | "Medium" | "Low" | "Unknown";

export interface EvidenceReviewPointer {
  status: string;
  reviewableVia: string;
  note: string;
}

export interface EvidenceObject {
  evidenceId: string;
  claim: string;
  source: string;
  evidenceOrigin: string;
  evidenceType: string;
  host: string | null;
  product: string | null;
  engineeringIntervention: string | null;
  experimentalContext: Record<string, unknown>;
  result: Record<string, unknown>;
  applicabilityBoundary: string[];
  limitations: string[];
  confidenceLevel: ConfidenceLevel;
  confidenceBasis: string;
  originKind: "diagnosis_evidence_item" | "ddr_decision_step";
  originRef: Record<string, unknown>;
  review: EvidenceReviewPointer;
  evidenceGrading: string | null;
}

export interface EvidenceCharacterization {
  evidenceLevel: string;
  applicability: "High" | "Medium" | "Low" | "Unknown";
  limitation: string;
  uncertainty: "Low" | "Moderate" | "High" | "Unknown";
}

interface RawEvidenceObject {
  evidence_id: string;
  claim: string;
  source: string;
  evidence_origin: string;
  evidence_type: string;
  host: string | null;
  product: string | null;
  engineering_intervention: string | null;
  experimental_context: Record<string, unknown>;
  result: Record<string, unknown>;
  applicability_boundary: string[];
  limitations: string[];
  confidence_level: ConfidenceLevel;
  confidence_basis: string;
  origin_kind: "diagnosis_evidence_item" | "ddr_decision_step";
  origin_ref: Record<string, unknown>;
  review: { status: string; reviewable_via: string; note: string };
  evidence_grading: string | null;
  characterization?: { evidence_level: string; applicability: string; limitation: string; uncertainty: string };
}

function toEvidenceObject(r: RawEvidenceObject): EvidenceObject {
  return {
    evidenceId: r.evidence_id,
    claim: r.claim,
    source: r.source,
    evidenceOrigin: r.evidence_origin,
    evidenceType: r.evidence_type,
    host: r.host,
    product: r.product,
    engineeringIntervention: r.engineering_intervention,
    experimentalContext: r.experimental_context ?? {},
    result: r.result ?? {},
    applicabilityBoundary: r.applicability_boundary ?? [],
    limitations: r.limitations ?? [],
    confidenceLevel: r.confidence_level,
    confidenceBasis: r.confidence_basis,
    originKind: r.origin_kind,
    originRef: r.origin_ref ?? {},
    review: { status: r.review.status, reviewableVia: r.review.reviewable_via, note: r.review.note },
    evidenceGrading: r.evidence_grading,
  };
}

export async function getEvidenceObject(evidenceId: string): Promise<{ evidence: EvidenceObject; characterization: EvidenceCharacterization } | null> {
  try {
    const r = await api.get<RawEvidenceObject>(`/api/evidence-intelligence/evidence/${encodeURIComponent(evidenceId)}`);
    const c = r.characterization;
    return {
      evidence: toEvidenceObject(r),
      characterization: c
        ? { evidenceLevel: c.evidence_level, applicability: c.applicability as EvidenceCharacterization["applicability"], limitation: c.limitation, uncertainty: c.uncertainty as EvidenceCharacterization["uncertainty"] }
        : { evidenceLevel: r.evidence_type, applicability: "Unknown", limitation: "none recorded", uncertainty: "Unknown" },
    };
  } catch (e) {
    if (e instanceof ApiError && e.status === 404) return null;
    throw e;
  }
}

export interface EngineeringContextQuery {
  host?: string;
  product?: string;
  objective?: string;
  bottleneck?: string;
  interventionType?: string;
  experimentalContext?: string;
  query?: string;
}

export async function searchEvidenceObjects(ctx: EngineeringContextQuery, projectId?: string, limit = 20): Promise<{ total: number; evidence: EvidenceObject[] }> {
  const params = new URLSearchParams();
  if (ctx.host) params.set("host", ctx.host);
  if (ctx.product) params.set("product", ctx.product);
  if (ctx.objective) params.set("objective", ctx.objective);
  if (ctx.bottleneck) params.set("bottleneck", ctx.bottleneck);
  if (ctx.interventionType) params.set("intervention_type", ctx.interventionType);
  if (ctx.experimentalContext) params.set("experimental_context", ctx.experimentalContext);
  if (ctx.query) params.set("query", ctx.query);
  if (projectId) params.set("project_id", projectId);
  params.set("limit", String(limit));
  const r = await api.get<{ total: number; evidence: RawEvidenceObject[] }>(`/api/evidence-intelligence/search?${params.toString()}`);
  return { total: r.total, evidence: r.evidence.map(toEvidenceObject) };
}

/**
 * Component 4 - Engineering Provenance Graph:
 *   Engineering Decision -> Engineering Strategy -> Mechanistic Rule ->
 *   Evidence Object -> Experiment -> Paper/Dataset
 * `unresolved` lists hops the graph could not fill in (e.g. no rule yet
 * distilled) - surfaced explicitly rather than silently dropped.
 */
export type ProvenanceNodeKind = "engineering_decision" | "engineering_strategy" | "mechanistic_rule" | "evidence_object" | "experiment" | "paper";

export interface ProvenanceNode {
  id: string;
  kind: ProvenanceNodeKind;
  label: string;
  ref: Record<string, unknown>;
}

export interface ProvenanceEdge {
  source: string;
  target: string;
  relation: string;
}

export interface ProvenanceGraph {
  anchor: { anchor_type: string; anchor_id: string };
  nodes: ProvenanceNode[];
  edges: ProvenanceEdge[];
  unresolved: string[];
}

export async function getEngineeringProvenanceGraph(anchorType: "ddr" | "strategy" | "candidate", anchorId: string): Promise<ProvenanceGraph | null> {
  try {
    return await api.get<ProvenanceGraph>(`/api/evidence-intelligence/provenance-graph?${new URLSearchParams({ anchor_type: anchorType, anchor_id: anchorId }).toString()}`);
  } catch (e) {
    if (e instanceof ApiError && e.status === 404) return null;
    throw e;
  }
}
