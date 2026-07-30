import { describe, expect, it } from "vitest";
import { calculatePaperExtractionProgress, PAPER_EXTRACTION_SKILLS } from "./progress";

const {
  skill01,
  skill02,
  skill03,
  skill04,
  skill05,
  skill06,
  skill07,
  skill08,
  skill09,
} = PAPER_EXTRACTION_SKILLS;

describe("calculatePaperExtractionProgress", () => {
  it("shows accepted-but-not-checkpointed work as preparation rather than zero", () => {
    const running = calculatePaperExtractionProgress("RUNNING", {}, {});
    const created = calculatePaperExtractionProgress("CREATED", {}, {});

    expect(running.percentage).toBe(1);
    expect(created.percentage).toBe(0);
  });

  it("weights the slow experiment-extraction stage and uses its real per-paper count", () => {
    const snapshot = calculatePaperExtractionProgress(
      "RUNNING",
      {
        [skill01]: "SUCCESS",
        [skill04]: "SUCCESS",
        [skill05]: "WARNING",
        [skill06]: "SUCCESS",
        [skill07]: "RUNNING",
      },
      { [skill07]: { completed: 1, total: 2 } },
    );

    expect(snapshot.percentage).toBe(54);
    expect(snapshot.currentSkillId).toBe(skill07);
    expect(snapshot.activeItemProgress).toEqual({ completed: 1, total: 2 });
    expect(snapshot.tone).toBe("active");
  });

  it("never lets a still-running stage consume its entire weight", () => {
    const snapshot = calculatePaperExtractionProgress(
      "RUNNING",
      {
        [skill01]: "SUCCESS",
        [skill04]: "SUCCESS",
        [skill05]: "SUCCESS",
        [skill06]: "SUCCESS",
        [skill07]: "RUNNING",
      },
      { [skill07]: { completed: 3, total: 3 } },
    );

    expect(snapshot.percentage).toBe(71);
    expect(snapshot.percentage).toBeLessThan(75);
  });

  it("reports exactly 100 percent only when the whole run is completed", () => {
    const states = {
      [skill01]: "SUCCESS",
      [skill04]: "SUCCESS",
      [skill05]: "WARNING",
      [skill06]: "SUCCESS",
      [skill07]: "SUCCESS",
      [skill08]: "SUCCESS",
      [skill09]: "SUCCESS",
      [PAPER_EXTRACTION_SKILLS.skill12]: "REVIEW_REQUIRED",
    };

    const running = calculatePaperExtractionProgress("RUNNING", states, {});
    const completed = calculatePaperExtractionProgress("COMPLETED", states, {});

    expect(running.percentage).toBe(99);
    expect(completed.percentage).toBe(100);
    expect(completed.tone).toBe("review");
  });

  it("stops at and highlights a failed stage", () => {
    const snapshot = calculatePaperExtractionProgress(
      "FAILED",
      {
        [skill01]: "SUCCESS",
        [skill04]: "SUCCESS",
        [skill05]: "WARNING",
        [skill06]: "WARNING",
        [skill07]: "SUCCESS",
        [skill08]: "FAILED",
      },
      {},
    );

    expect(snapshot.percentage).toBe(76);
    expect(snapshot.currentSkillId).toBe(skill08);
    expect(snapshot.currentStatus).toBe("FAILED");
    expect(snapshot.tone).toBe("failed");
  });

  it("represents missing upstream input as a blocked stage rather than completion", () => {
    const snapshot = calculatePaperExtractionProgress(
      "WAITING_REVIEW",
      {
        [skill01]: "SUCCESS",
        [skill04]: "SUCCESS",
        [skill05]: "BLOCKED",
      },
      {},
    );

    expect(snapshot.currentSkillId).toBe(skill05);
    expect(snapshot.tone).toBe("blocked");
    expect(snapshot.percentage).toBeLessThan(25);
  });

  it("infers auto-search and DOI validation stages when they appear in the checkpoint", () => {
    const snapshot = calculatePaperExtractionProgress(
      "RUNNING",
      {
        [skill01]: "SUCCESS",
        [skill02]: "SUCCESS",
        [skill03]: "RUNNING",
      },
      {},
    );

    expect(snapshot.stages.slice(0, 4).map((stage) => stage.skillId)).toEqual([
      skill01,
      skill02,
      skill03,
      skill04,
    ]);
    expect(snapshot.currentSkillId).toBe(skill03);
  });
});
