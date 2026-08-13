import { beforeEach, describe, expect, it, vi } from "vitest";
import { getObservationGrounding, listEngineeringProblems } from "./diagnosis";
import { api } from "./client";

vi.mock("./client", () => ({ api: { get: vi.fn() } }));

describe("diagnosis observation grounding adapter", () => {
  beforeEach(() => vi.clearAllMocks());

  it("maps grounding blockers without converting them into observations", async () => {
    vi.mocked(api.get).mockResolvedValue({ status: "data_required", blocking_reasons: ["no persisted observation"], observation_ids: [], engineering_problem_ids: [], policy_version: "observation-grounding-v1", actionable: false });
    const result = await getObservationGrounding("DIAG-1");
    expect(result.actionable).toBe(false);
    expect(result.blockingReasons).toEqual(["no persisted observation"]);
  });

  it("keeps measured values and descriptive problem separate", async () => {
    vi.mocked(api.get).mockResolvedValue({ engineering_problems: [{ engineering_problem_id: "EPR-1", metric: "tryptophan_titer", observed_value: 8, expected_value: 12, unit: "g/L", delta: -4, abnormality_statement: "titer is 4 g/L below baseline", observation_ids: ["OBS-1"], comparison_observation_ids: ["OBS-0"], status: "grounded" }] });
    const [problem] = await listEngineeringProblems("DIAG-1");
    expect(problem.observedValue).toBe(8);
    expect(problem.abnormalityStatement).toContain("below baseline");
  });
});
