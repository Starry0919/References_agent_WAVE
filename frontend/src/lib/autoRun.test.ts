import { describe, expect, it } from "vitest";
import { selectAutomaticGroundingPair } from "./autoRun";

describe("selectAutomaticGroundingPair", () => {
  it("uses a newer QC-passed measurement with an older matched baseline", () => {
    const pair = selectAutomaticGroundingPair([
      { observationId: "OBS-new", metric: "titer", value: 8, unit: "g/L", conditionRef: { medium: "M9" }, qcStatus: "passed", sourceType: "instrument" },
      { observationId: "OBS-old", metric: "titer", value: 12, unit: "g/L", conditionRef: { medium: "M9" }, qcStatus: "passed", sourceType: "instrument" },
    ]);
    expect(pair.subject?.observationId).toBe("OBS-new");
    expect(pair.baseline?.observationId).toBe("OBS-old");
  });

  it("does not fabricate a pair from mismatched or failed measurements", () => {
    const pair = selectAutomaticGroundingPair([
      { observationId: "OBS-a", metric: "titer", value: 8, unit: "g/L", conditionRef: { medium: "M9" }, qcStatus: "failed", sourceType: "instrument" },
      { observationId: "OBS-b", metric: "yield", value: 0.2, unit: "g/g", conditionRef: { medium: "M9" }, qcStatus: "passed", sourceType: "instrument" },
    ]);
    expect(pair).toEqual({});
  });
});
