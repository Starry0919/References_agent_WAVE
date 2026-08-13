import { describe, expect, it } from "vitest";
import type { EvidenceDocumentDetail } from "@/api/evidence";
import { buildEvidenceExport } from "./evidenceExport";

function detail(): EvidenceDocumentDetail {
  return {
    sourceId: "DDR-014",
    title: "Test paper",
    authors: ["A"],
    publicationYear: 2026,
    journalOrRepository: "Journal",
    doiOrAccession: "10.1/test",
    relevant: null,
    url: "https://doi.org/10.1/test",
    abstractOrSummary: "Summary",
    engineeringDesign: null,
    paperExtractionDetail: null,
    extractionTaskId: "task-1",
    agentTrace: [{ step: 1, kind: "intervention", title: "Step", status: "completed", input: "i", operation: "o", output: "x", confidence: 0.82, evidence: ["E1"], designStepRef: 1 }],
    experimentalDesign: [{ step: 1, title: "Design", problem: "p", hypothesis: "h", engineeringAction: { type: "edit", target: "g", modification: "m" }, method: [], result: "r", evidence: ["E1"], evidenceGrading: "硬", reasonNature: "机理推断", alternatives: [], rule: null }],
    evidenceProvenance: [{ step: 1, claim: "c", source: "E1", grading: "硬", confidence: 0.9 }],
    evidenceGraph: { nodes: [], edges: [] },
    status: "completed",
    evidenceConfidence: "high",
    humanReviewStatus: null,
    calibrationStatus: "accepted",
    conflictCount: 0,
    extractionAttempts: [],
    rawRecord: { ddr_id: "DDR-014", metadata: { organism: null } },
  };
}

describe("buildEvidenceExport", () => {
  it("preserves the raw DDR and exports the normalized page data", () => {
    const source = detail();
    const exported = buildEvidenceExport(source, "2026-08-10T00:00:00.000Z");

    expect(exported.source_record).toBe(source.rawRecord);
    expect(exported.normalized_view.agent_trace[0].confidence).toBe(0.82);
    expect(exported.status_snapshot.evidence_confidence).toBe("high");
    expect(exported.derived_summary.hard_evidence_step_count).toBe(1);
    expect(exported.export_metadata.schema_version).toBe("wave.evidence-export.v1");
  });
});
