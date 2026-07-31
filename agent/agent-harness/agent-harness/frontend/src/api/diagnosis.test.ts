import { afterEach, describe, expect, it, vi } from "vitest";
import { api } from "./client";
import { createSession, getSession, listSessionsForProject, sessionAction } from "./diagnosis";

afterEach(() => {
  vi.restoreAllMocks();
});

describe("listSessionsForProject", () => {
  it("maps snake_case rows to camelCase and passes project_id as a query param", async () => {
    const getSpy = vi.spyOn(api, "get").mockResolvedValue({
      sessions: [
        {
          diagnosis_session_id: "DIAG-1", project_id: "PROJ-1", status: "intake", data_sufficiency: "insufficient",
          approval_state: "not_required", biological_system: { species: "E. coli" }, created_at: 100, updated_at: 100,
        },
      ],
    });
    const rows = await listSessionsForProject("PROJ-1");
    expect(getSpy).toHaveBeenCalledWith("/api/diagnosis/sessions?project_id=PROJ-1");
    expect(rows).toEqual([
      {
        diagnosisSessionId: "DIAG-1", projectId: "PROJ-1", status: "intake", dataSufficiency: "insufficient",
        approvalState: "not_required", biologicalSystem: { species: "E. coli" }, createdAt: 100, updatedAt: 100,
      },
    ]);
  });
});

describe("createSession", () => {
  it("defaults optional fields and sends actor/project ids untouched", async () => {
    const postSpy = vi.spyOn(api, "post").mockResolvedValue({ diagnosis_session_id: "DIAG-1", status: "intake" });
    const result = await createSession({ projectId: "PROJ-1", actorId: "frontend-user" });
    expect(postSpy).toHaveBeenCalledWith("/api/diagnosis/sessions", {
      project_id: "PROJ-1", actor_id: "frontend-user", workflow_run_id: null, triggering_failure_case_id: null,
      objective_id: null, biological_system: {}, baseline_observation_ids: [],
    });
    expect(result).toEqual({ diagnosisSessionId: "DIAG-1", status: "intake" });
  });
});

describe("getSession", () => {
  it("maps every field of the session detail shape", async () => {
    vi.spyOn(api, "get").mockResolvedValue({
      diagnosis_session_id: "DIAG-1", project_id: "PROJ-1", status: "hypotheses_ranked", data_sufficiency: "sufficient",
      approval_state: "not_required", active_hypothesis_set_version: 2, biological_system: { species: "E. coli" },
      baseline_observation_ids: ["OBS-1"], version: 3,
    });
    const session = await getSession("DIAG-1");
    expect(session).toEqual({
      diagnosisSessionId: "DIAG-1", projectId: "PROJ-1", status: "hypotheses_ranked", dataSufficiency: "sufficient",
      approvalState: "not_required", activeHypothesisSetVersion: 2, biologicalSystem: { species: "E. coli" },
      baselineObservationIds: ["OBS-1"], version: 3,
    });
  });
});

describe("sessionAction", () => {
  it("posts actor_id and kwargs to the action-specific route", async () => {
    const postSpy = vi.spyOn(api, "post").mockResolvedValue({ diagnosis_session_id: "DIAG-1", status: "test_planned" });
    const result = await sessionAction("DIAG-1", "select_test", "frontend-user", { test_id: "TEST-1" });
    expect(postSpy).toHaveBeenCalledWith("/api/diagnosis/sessions/DIAG-1/action/select_test", {
      actor_id: "frontend-user", kwargs: { test_id: "TEST-1" },
    });
    expect(result).toEqual({ diagnosisSessionId: "DIAG-1", status: "test_planned" });
  });
});
