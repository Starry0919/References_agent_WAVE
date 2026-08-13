import type { EvidenceDocumentDetail } from "@/api/evidence";

export const EVIDENCE_EXPORT_SCHEMA_VERSION = "wave.evidence-export.v1";

export function buildMachineReadableExport(detail: EvidenceDocumentDetail) {
  return {
    schema: "skill07.paper-detail.machine-readable.v2",
    metadata: {
      title: detail.title,
      authors: detail.authors,
      year: detail.publicationYear,
      journal: detail.journalOrRepository,
      doi: detail.doiOrAccession,
    },
    experiments: detail.experimentalDesign,
    logic: detail.agentTrace.map(
      ({ step, kind, title, input, operation, output, designStepRef }) => ({
        step,
        kind,
        title,
        input,
        reasoning_summary: operation,
        output,
        experiment_ref: designStepRef,
      }),
    ),
    claims: detail.experimentalDesign.map((step) => ({
      experiment: step.step,
      result: step.result,
      hypothesis: step.hypothesis,
      classification:
        "PAPER_FACT_OR_AGENT_INTERPRETATION_REQUIRES_FIELD_REVIEW",
    })),
    evidence: detail.evidenceProvenance,
    provenance: {
      extraction_task_id: detail.extractionTaskId,
      evidence_graph: detail.evidenceGraph,
    },
    reasoning: {
      type: "EVIDENCE_GROUNDED_SUMMARY_NOT_CHAIN_OF_THOUGHT",
      records: detail.agentTrace,
    },
    confidence: {
      document: detail.evidenceConfidence,
      per_record: detail.agentTrace.map((step) => ({
        step: step.step,
        confidence: step.confidence,
      })),
    },
  };
}

export function buildReviewExport(detail: EvidenceDocumentDetail) {
  return {
    schema: "skill07.paper-detail.review.v2",
    reviewer_role: "UNASSIGNED",
    review_status: detail.humanReviewStatus,
    decisions: [],
    unresolved: detail.experimentalDesign
      .filter((step) => !step.evidence.length || !step.result)
      .map((step) => ({
        experiment: step.step,
        reason: "Missing evidence or result; human review required",
      })),
    comments: [],
    evidence: detail.evidenceProvenance,
    validation: {
      calibration_status: detail.calibrationStatus,
      conflict_count: detail.conflictCount,
      extraction_attempts: detail.extractionAttempts,
    },
  };
}

/**
 * Build a self-contained, auditable download without mutating the source DDR.
 * `source_record` is the authoritative stored record; `normalized_view` is the
 * exact structured data used by the detail page and can be regenerated later.
 */
export function buildEvidenceExport(
  detail: EvidenceDocumentDetail,
  exportedAt = new Date().toISOString(),
) {
  const hardEvidenceSteps = detail.experimentalDesign.filter(
    (step) => step.evidenceGrading === "硬",
  ).length;
  const stepsWithConfidence = detail.agentTrace.filter(
    (step) => step.confidence != null,
  ).length;

  return {
    export_metadata: {
      schema_version: EVIDENCE_EXPORT_SCHEMA_VERSION,
      exported_at: exportedAt,
      source_system: "WAVE Agent Platform",
      source_id: detail.sourceId,
      extraction_task_id: detail.extractionTaskId,
      notes: [
        "source_record is the authoritative stored DDR and is preserved without modification.",
        "normalized_view contains the structured data rendered by the evidence detail page.",
        "agent_trace contains observable workflow records, not private chain-of-thought.",
        "UI controls and button labels are intentionally not research data and are not exported.",
      ],
    },
    bibliographic_record: {
      source_id: detail.sourceId,
      title: detail.title,
      authors: detail.authors,
      publication_year: detail.publicationYear,
      journal_or_repository: detail.journalOrRepository,
      doi_or_accession: detail.doiOrAccession,
      url: detail.url,
      abstract_or_summary: detail.abstractOrSummary,
    },
    status_snapshot: {
      extraction_status: detail.status,
      evidence_confidence: detail.evidenceConfidence,
      human_review_status: detail.humanReviewStatus,
      calibration_status: detail.calibrationStatus,
      conflict_count: detail.conflictCount,
      extraction_attempts: detail.extractionAttempts,
    },
    derived_summary: {
      agent_trace_step_count: detail.agentTrace.length,
      experimental_design_step_count: detail.experimentalDesign.length,
      hard_evidence_step_count: hardEvidenceSteps,
      steps_with_recorded_confidence: stepsWithConfidence,
      evidence_provenance_item_count: detail.evidenceProvenance.length,
    },
    normalized_view: {
      paper_extraction_detail: detail.paperExtractionDetail,
      engineering_design: detail.engineeringDesign,
      agent_trace: detail.agentTrace,
      experimental_design: detail.experimentalDesign,
      evidence_provenance: detail.evidenceProvenance,
      evidence_graph: detail.evidenceGraph,
    },
    source_record: detail.rawRecord,
  };
}
