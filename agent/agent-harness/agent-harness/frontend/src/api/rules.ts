import { api, ApiError } from "./client";

/**
 * DDR-backed Knowledge Claims (harness/api/paper_extraction.py::
 * list_knowledge_claims_from_rules, harness/paper_extraction/
 * rule_distillation.py::rule_as_knowledge_claim_view). Distinct from
 * `@/api/knowledge`'s `KnowledgeClaim` (harness/learning/models.py), which
 * aggregates wet-lab experiment runs, not literature DDRs - this is the
 * "多个 DDR 支持的可迁移知识" object the Knowledge & Evidence Layer design
 * doc calls for, built by reshaping the existing rule library
 * (`knowledge/biological_rules/rules.json`) rather than a new schema.
 */
export interface DdrKnowledgeClaim {
  claimId: string;
  statement: string;
  evidenceDdrIds: string[];
  evidenceCount: number;
  evidenceGrading: string | null;
  confidence: "high" | "medium" | "low";
  boundary: string;
  applicableModules: string[];
  calibrationStatus: string | null;
  /** Only set when the query was scoped with `project_id` - target-product
   * text overlap with the project's own context. `null` = no project
   * context supplied. */
  relevant: boolean | null;
}

interface RawDdrClaim {
  claim_id: string;
  statement: string;
  evidence_ddr_ids: string[];
  evidence_count: number;
  evidence_grading: string | null;
  confidence: "high" | "medium" | "low";
  boundary: string;
  applicable_modules: string[];
  calibration_status: string | null;
  relevant?: boolean;
}

/**
 * Trust & Provenance minimal closure (harness/api/paper_extraction.py::
 * get_ddr_provenance, 老师 §Phase5 Round 2): the full "why do we believe
 * this" chain for one DDR - design action(s) -> rule(s) distilled from it
 * -> the DDR's own paper citation -> evidence grading. Composed entirely
 * from data that already exists (the DDR record + rules.json), no new
 * schema.
 */
export interface DdrProvenance {
  ddrId: string;
  paper: {
    title: string | null;
    authors: string[];
    publicationYear: number | null;
    journalOrRepository: string | null;
    doiOrAccession: string | null;
  };
  designActions: string[];
  evidenceGrades: string[];
  ruleIds: string[];
  rules: DdrKnowledgeClaim[];
  confidence: "high" | "medium" | "low";
}

interface RawDdrProvenance {
  ddr_id: string;
  paper: {
    title: string | null;
    authors: string[];
    publication_year: number | null;
    journal_or_repository: string | null;
    doi_or_accession: string | null;
  };
  design_actions: string[];
  evidence_grades: string[];
  rule_ids: string[];
  rules: RawDdrClaim[];
  confidence: "high" | "medium" | "low";
}

export async function getDdrProvenance(ddrId: string): Promise<DdrProvenance | null> {
  try {
    const r = await api.get<RawDdrProvenance>(`/api/paper-extraction/ddr/${ddrId}/provenance`);
    return {
      ddrId: r.ddr_id,
      paper: {
        title: r.paper.title,
        authors: r.paper.authors ?? [],
        publicationYear: r.paper.publication_year,
        journalOrRepository: r.paper.journal_or_repository,
        doiOrAccession: r.paper.doi_or_accession,
      },
      designActions: r.design_actions ?? [],
      evidenceGrades: r.evidence_grades ?? [],
      ruleIds: r.rule_ids ?? [],
      rules: (r.rules ?? []).map((c) => ({
        claimId: c.claim_id,
        statement: c.statement,
        evidenceDdrIds: c.evidence_ddr_ids,
        evidenceCount: c.evidence_count,
        evidenceGrading: c.evidence_grading,
        confidence: c.confidence,
        boundary: c.boundary,
        applicableModules: c.applicable_modules,
        calibrationStatus: c.calibration_status,
        relevant: c.relevant ?? null,
      })),
      confidence: r.confidence,
    };
  } catch (e) {
    if (e instanceof ApiError && e.status === 404) return null;
    throw e;
  }
}

/** One entry from `knowledge/engineering_actions/action_database.json` - the
 * third knowledge-base category (harness/paper_extraction/
 * engineering_actions_catalog.py), alongside biological rules (above) and
 * the DDR database (@/api/evidence's `searchEvidence(..., "local_ddr")`). A
 * catalog of well-established engineering operations (gene target +
 * modification + mechanism), not necessarily traceable to one specific
 * paper - see `evidence` for whether this entry is a verified experimental
 * result or a general pattern. */
export interface EngineeringAction {
  actionId: string;
  actionType: string;
  targetGene: string | null;
  modification: string | null;
  replacement: string | null;
  biologicalEffect: string | null;
  mechanism: string | null;
  expectedEffect: string | null;
  risk: string | null;
  applicableConditions: string[];
  evidence: string | null;
  /** Only set when the query was scoped with `project_id` - target-product
   * text overlap with the project's own context, same convention as
   * `DdrKnowledgeClaim.relevant` and `EvidenceDocument.relevant`. `null` =
   * no project context supplied. */
  relevant: boolean | null;
}

interface RawEngineeringAction {
  action_id: string;
  action_type: string;
  target_gene: string | null;
  modification: string | null;
  replacement: string | null;
  biological_effect: string | null;
  mechanism: string | null;
  expected_effect: string | null;
  risk: string | null;
  applicable_conditions?: string[];
  evidence: string | null;
  relevant?: boolean;
}

export async function listEngineeringActions(query = "", projectId?: string): Promise<EngineeringAction[]> {
  const params = new URLSearchParams();
  if (query) params.set("query", query);
  if (projectId) params.set("project_id", projectId);
  const qs = params.toString();
  const r = await api.get<{ actions: RawEngineeringAction[]; total: number }>(`/api/paper-extraction/engineering-actions${qs ? `?${qs}` : ""}`);
  return r.actions.map((a) => ({
    actionId: a.action_id,
    actionType: a.action_type,
    targetGene: a.target_gene,
    modification: a.modification,
    replacement: a.replacement,
    biologicalEffect: a.biological_effect,
    mechanism: a.mechanism,
    expectedEffect: a.expected_effect,
    relevant: a.relevant ?? null,
    risk: a.risk,
    applicableConditions: a.applicable_conditions ?? [],
    evidence: a.evidence,
  }));
}

export async function listDdrKnowledgeClaims(query = "", projectId?: string): Promise<DdrKnowledgeClaim[]> {
  const params = new URLSearchParams();
  if (query) params.set("query", query);
  if (projectId) params.set("project_id", projectId);
  const qs = params.toString();
  const r = await api.get<{ claims: RawDdrClaim[]; total: number }>(`/api/paper-extraction/knowledge-claims${qs ? `?${qs}` : ""}`);
  return r.claims.map((c) => ({
    claimId: c.claim_id,
    statement: c.statement,
    evidenceDdrIds: c.evidence_ddr_ids,
    evidenceCount: c.evidence_count,
    evidenceGrading: c.evidence_grading,
    confidence: c.confidence,
    boundary: c.boundary,
    applicableModules: c.applicable_modules,
    calibrationStatus: c.calibration_status,
    relevant: c.relevant ?? null,
  }));
}
