import { afterEach, describe, expect, it, vi } from "vitest";
import { api } from "./client";
import { getGenerationRecord, listEvidenceMatchReports, listGenerationRecords, verifyDoi } from "./evidence";

afterEach(() => {
  vi.restoreAllMocks();
});

describe("verifyDoi", () => {
  it("sends project_id/doi/actor_id and passes the real resolved flag through untouched", async () => {
    const postSpy = vi.spyOn(api, "post").mockResolvedValue({ doi: "10.9999/fabricated-xyz", resolved: false });
    const result = await verifyDoi({ projectId: "PROJ-1", doi: "10.9999/fabricated-xyz", actorId: "frontend-user" });
    expect(postSpy).toHaveBeenCalledWith("/api/generation/evidence/verify-doi", {
      project_id: "PROJ-1",
      doi: "10.9999/fabricated-xyz",
      actor_id: "frontend-user",
    });
    expect(result.resolved).toBe(false);
  });
});

describe("listEvidenceMatchReports", () => {
  it("maps every match dimension without dropping any (each is an independent applicability signal, not one merged score)", async () => {
    vi.spyOn(api, "get").mockResolvedValue({
      match_reports: [
        {
          match_report_id: "EVMATCH-1", evidence_id: "EVID-1", organism_match: "match", strain_match: "mismatch",
          genotype_match: "unknown", medium_match: "match", condition_match: "mismatch", timepoint_match: "unknown",
          intervention_match: "match", measurement_match: "match", directness: "indirect",
          overall_match_status: "cross_strain", transfer_risks: ["strain background differs"], downgrade_reasons: ["strain mismatch"], created_at: 100,
        },
      ],
    });
    const rows = await listEvidenceMatchReports();
    expect(rows).toHaveLength(1);
    expect(rows[0]).toEqual({
      matchReportId: "EVMATCH-1", evidenceId: "EVID-1", organismMatch: "match", strainMatch: "mismatch",
      genotypeMatch: "unknown", mediumMatch: "match", conditionMatch: "mismatch", timepointMatch: "unknown",
      interventionMatch: "match", measurementMatch: "match", directness: "indirect",
      overallMatchStatus: "cross_strain", transferRisks: ["strain background differs"], downgradeReasons: ["strain mismatch"], createdAt: 100,
    });
  });

  it("passes evidence_id as a query filter when provided", async () => {
    const getSpy = vi.spyOn(api, "get").mockResolvedValue({ match_reports: [] });
    await listEvidenceMatchReports("EVID-1");
    expect(getSpy).toHaveBeenCalledWith("/api/generation/evidence/match-reports?evidence_id=EVID-1");
  });
});

describe("listGenerationRecords / getGenerationRecord", () => {
  it("maps the full computational traceability chain (task/provider/model/prompt-template/validation/retry/fallback)", async () => {
    vi.spyOn(api, "get").mockResolvedValue({
      records: [
        {
          generation_id: "GEN-1", task_type: "hypothesis_generation", provider: "kimi", model_id: "kimi-k2",
          prompt_template_id: "PT-1", prompt_template_version: "3", output_schema_version: "1",
          validation_status: "valid", retry_count: 0, fallback_used: false, shared_model_risk: false,
          token_usage_if_available: null, latency: 1.2, created_at: 50,
        },
      ],
    });
    const rows = await listGenerationRecords();
    expect(rows[0].promptTemplateId).toBe("PT-1");
    expect(rows[0].validationStatus).toBe("valid");
  });

  it("getGenerationRecord returns null on 404 rather than throwing", async () => {
    const { ApiError } = await import("./client");
    vi.spyOn(api, "get").mockRejectedValue(new ApiError(404, "not found", undefined));
    expect(await getGenerationRecord("GEN-missing")).toBeNull();
  });
});
