import { afterEach, describe, expect, it, vi } from "vitest";
import { api } from "./client";
import { createHandoff, getProject, listHandoffs, listStrategies } from "./engineeringDesign";

afterEach(() => {
  vi.restoreAllMocks();
});

describe("createHandoff", () => {
  it("sends the decision/actor ids and maps both the project and handoff halves of the response", async () => {
    const postSpy = vi.spyOn(api, "post").mockResolvedValue({
      project: {
        design_project_id: "DP-1", project_id: "PROJ-1", chassis: "E. coli", chassis_version_or_genotype: "K-12",
        diagnosis_session_id: "DIAG-1", diagnosis_decision_id: "DEC-1", diagnosis_version: 1, primary_metrics: [],
        secondary_metrics: [], hard_constraints: [], preferences_or_weights: [], autonomy_level: "recommend_only",
        status: "diagnostic_blocked", revision_count: 0, version: 1,
      },
      handoff: {
        handoff_id: "HANDOFF-1", design_project_id: "DP-1", diagnosis_session_id: "DIAG-1", diagnosis_decision_id: "DEC-1",
        diagnosis_version: 1, handoff_kind: "diagnosis_decision", decision_status: "actionable_stop",
        supported_hypotheses: [], unresolved_alternatives: [], approved_for_design: true, is_stale: false,
        adapter_provenance: {}, created_at: 100,
      },
    });
    const result = await createHandoff({ diagnosisDecisionId: "DEC-1", actorId: "frontend-user" });
    expect(postSpy).toHaveBeenCalledWith("/api/engineering-design/handoff", {
      diagnosis_decision_id: "DEC-1", actor_id: "frontend-user", handoff_kind: "diagnosis_decision",
      human_approved: null, chassis: null, chassis_version_or_genotype: "unknown",
    });
    expect(result.project.designProjectId).toBe("DP-1");
    expect(result.handoff.handoffId).toBe("HANDOFF-1");
    expect(result.handoff.approvedForDesign).toBe(true);
  });
});

describe("getProject / listHandoffs", () => {
  it("maps project fields from snake_case", async () => {
    vi.spyOn(api, "get").mockResolvedValue({
      design_project_id: "DP-1", project_id: "PROJ-1", chassis: "E. coli", chassis_version_or_genotype: "K-12",
      diagnosis_session_id: "DIAG-1", diagnosis_decision_id: "DEC-1", diagnosis_version: 1, primary_metrics: [{ metric: "titer" }],
      secondary_metrics: [], hard_constraints: [], preferences_or_weights: [], autonomy_level: "recommend_only",
      status: "objective_draft", revision_count: 0, version: 2,
    });
    const project = await getProject("DP-1");
    expect(project.status).toBe("objective_draft");
    expect(project.primaryMetrics).toEqual([{ metric: "titer" }]);
    expect(project.version).toBe(2);
  });

  it("returns an empty list rather than throwing when a project has no handoff yet", async () => {
    vi.spyOn(api, "get").mockResolvedValue({ handoffs: [] });
    const handoffs = await listHandoffs("DP-1");
    expect(handoffs).toEqual([]);
  });
});

describe("listStrategies", () => {
  it("maps strategy rows and keeps evidence_links as-is for inline resolution", async () => {
    vi.spyOn(api, "get").mockResolvedValue({
      strategies: [
        {
          strategy_id: "STRAT-1", strategy_class: "precursor_supply", engineering_objective: "increase PEP supply",
          mechanism_target: "aroG", rationale: "relieve precursor limitation", status: "proposed",
          excluded_strategy_reasons: [], evidence_links: [{ source_type: "curated_knowledge", reference: "ACT-005" }],
        },
      ],
    });
    const strategies = await listStrategies("DP-1");
    expect(strategies).toHaveLength(1);
    expect(strategies[0].strategyId).toBe("STRAT-1");
    expect(strategies[0].evidenceLinks).toEqual([{ source_type: "curated_knowledge", reference: "ACT-005" }]);
  });
});
