import { afterEach, describe, expect, it, vi } from "vitest";
import { api, ApiError } from "./client";
import {
  PromotionRejectedError,
  countIndependentGroups,
  discoverProjectClaimIds,
  experimentIdsFromIndependenceGroups,
  experimentRunToEvidenceSummary,
  getClaim,
  promoteClaim,
  retractClaim,
  submitClaim,
} from "./knowledge";

afterEach(() => {
  vi.restoreAllMocks();
});

describe("countIndependentGroups", () => {
  it("counts only non-empty groups (mirrors harness/memory/knowledge_claims.py::count_independent_groups)", () => {
    expect(countIndependentGroups([["A", "B"], [], ["C"]])).toBe(2);
    expect(countIndependentGroups([])).toBe(0);
  });
});

describe("experimentIdsFromIndependenceGroups", () => {
  it("flattens and de-duplicates ids across groups", () => {
    expect(experimentIdsFromIndependenceGroups([["A", "B"], ["B", "C"]])).toEqual(["A", "B", "C"]);
  });
});

describe("discoverProjectClaimIds", () => {
  it("derives the claim id set from KnowledgeClaim timeline events only, de-duplicated (no dedicated list endpoint exists)", async () => {
    vi.spyOn(api, "get").mockResolvedValue({
      events: [
        { seq: 1, event_id: "E1", event_type: "KNOWLEDGE_CLAIM_SUBMITTED", entity_type: "KnowledgeClaim", entity_id: "CLAIM-1", actor_type: "human", actor_id: "u", timestamp: 1 },
        { seq: 2, event_id: "E2", event_type: "DESIGN_VERSION_CREATED", entity_type: "DesignVersion", entity_id: "DV-1", actor_type: "human", actor_id: "u", timestamp: 2 },
        { seq: 3, event_id: "E3", event_type: "KNOWLEDGE_CLAIM_PROMOTED", entity_type: "KnowledgeClaim", entity_id: "CLAIM-1", actor_type: "human", actor_id: "u", timestamp: 3 },
        { seq: 4, event_id: "E4", event_type: "KNOWLEDGE_CLAIM_SUBMITTED", entity_type: "KnowledgeClaim", entity_id: "CLAIM-2", actor_type: "human", actor_id: "u", timestamp: 4 },
      ],
    });
    const ids = await discoverProjectClaimIds("PROJ-1");
    expect(ids).toEqual(["CLAIM-1", "CLAIM-2"]);
  });
});

describe("getClaim", () => {
  it("never defaults contradicting_experiments/reviewers to [] - GET does not return them, so they stay explicitly null (not a fabricated 'confirmed empty')", async () => {
    vi.spyOn(api, "get").mockResolvedValue({
      claim_id: "CLAIM-1",
      statement: "ptsG attenuation increases tryptophan titer",
      scope: { species: "E. coli" },
      independence_groups: [["EXP-1", "EXP-2"], ["EXP-3"]],
      evidence_grade: "medium",
      status: "lab_candidate",
      promotion_record: [{ status: "project_candidate", actor_id: "u1", at: 1, reason: "submitted" }],
    });
    const claim = await getClaim("CLAIM-1", "PROJ-1");
    expect(claim?.contradictingExperimentsAsSubmitted).toBeNull();
    expect(claim?.reviewersAsSubmitted).toBeNull();
    expect(claim?.projectId).toBe("PROJ-1");
    expect(claim?.independenceGroups).toEqual([["EXP-1", "EXP-2"], ["EXP-3"]]);
  });

  it("returns null on 404 rather than throwing", async () => {
    vi.spyOn(api, "get").mockRejectedValue(new ApiError(404, "not found", undefined));
    expect(await getClaim("CLAIM-missing", "PROJ-1")).toBeNull();
  });
});

describe("submitClaim", () => {
  it("sends the exact real request shape and never asserts a starting status other than what the server assigns", async () => {
    const postSpy = vi.spyOn(api, "post").mockResolvedValue({ claim_id: "CLAIM-9", status: "project_candidate" });
    const result = await submitClaim({
      projectId: "PROJ-1",
      statement: "statement",
      scope: { species: "E. coli" },
      supportingExperiments: ["EXP-1"],
      independenceGroups: [["EXP-1"]],
      createdBy: "frontend-user",
      contradictingExperiments: ["EXP-9"],
      evidenceGrade: "low",
    });
    expect(postSpy).toHaveBeenCalledWith("/api/learning/knowledge-claims", {
      project_id: "PROJ-1",
      statement: "statement",
      scope: { species: "E. coli" },
      supporting_experiments: ["EXP-1"],
      independence_groups: [["EXP-1"]],
      created_by: "frontend-user",
      contradicting_experiments: ["EXP-9"],
      evidence_grade: "low",
    });
    expect(result).toEqual({ claimId: "CLAIM-9", status: "project_candidate" });
  });
});

describe("promoteClaim", () => {
  it("surfaces a 422 PromotionRejected as a typed PromotionRejectedError, not a generic failure", async () => {
    vi.spyOn(api, "post").mockRejectedValue(new ApiError(422, "actor 'u' submitted this claim and cannot also promote it", undefined));
    await expect(promoteClaim("CLAIM-1", { targetStatus: "lab_candidate", reviewerId: "u", reason: "" })).rejects.toBeInstanceOf(PromotionRejectedError);
  });

  it("passes reviewer_id/target_status/reason through untouched on success", async () => {
    const postSpy = vi.spyOn(api, "post").mockResolvedValue({ claim_id: "CLAIM-1", status: "lab_candidate", promotion_record: [] });
    await promoteClaim("CLAIM-1", { targetStatus: "lab_candidate", reviewerId: "frontend-reviewer", reason: "3 independent groups" });
    expect(postSpy).toHaveBeenCalledWith("/api/learning/knowledge-claims/CLAIM-1/promote", {
      target_status: "lab_candidate",
      reviewer_id: "frontend-reviewer",
      reason: "3 independent groups",
    });
  });
});

describe("retractClaim", () => {
  it("sends reviewer_id/reason and returns the real status", async () => {
    const postSpy = vi.spyOn(api, "post").mockResolvedValue({ claim_id: "CLAIM-1", status: "retracted" });
    const result = await retractClaim("CLAIM-1", { reviewerId: "frontend-reviewer", reason: "superseded by newer data" });
    expect(postSpy).toHaveBeenCalledWith("/api/learning/knowledge-claims/CLAIM-1/retract", {
      reviewer_id: "frontend-reviewer",
      reason: "superseded by newer data",
    });
    expect(result).toEqual({ claimId: "CLAIM-1", status: "retracted" });
  });
});

describe("experimentRunToEvidenceSummary", () => {
  it("never claims a strain/condition match the underlying endpoint does not return", () => {
    const summary = experimentRunToEvidenceSummary({ experimentRunId: "EXP-1", experimentPlanId: "PLAN-1", executionStatus: "completed", deviations: [] });
    expect(summary.strainMatch).toBe("unknown");
    expect(summary.conditionMatch).toBe("unknown");
    expect(summary.kind).toBe("observation");
  });

  it("surfaces deviation count in the title rather than hiding it", () => {
    const summary = experimentRunToEvidenceSummary({ experimentRunId: "EXP-2", experimentPlanId: "PLAN-1", executionStatus: "completed", deviations: ["temp excursion"] });
    expect(summary.title).toContain("1 deviation");
  });
});
