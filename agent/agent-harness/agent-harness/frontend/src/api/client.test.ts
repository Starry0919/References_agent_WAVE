import { afterEach, describe, expect, it, vi } from "vitest";
import { api, setApiBasePath } from "./client";

afterEach(() => {
  setApiBasePath("");
  vi.unstubAllGlobals();
});

describe("setApiBasePath (Simulation/Demo Workspace base-path switch)", () => {
  it("prefixes every request path once a base path is set", async () => {
    const fetchMock = vi.fn().mockResolvedValue(new Response(JSON.stringify({ ok: true }), { status: 200 }));
    vi.stubGlobal("fetch", fetchMock);

    setApiBasePath("/api/simulation");
    await api.get("/api/projects");

    expect(fetchMock).toHaveBeenCalledWith("/api/simulation/api/projects", expect.anything());
  });

  it("restores the real (unprefixed) path once the base path is cleared", async () => {
    const fetchMock = vi.fn().mockResolvedValue(new Response(JSON.stringify({ ok: true }), { status: 200 }));
    vi.stubGlobal("fetch", fetchMock);

    setApiBasePath("/api/simulation");
    setApiBasePath("");
    await api.get("/api/projects");

    expect(fetchMock).toHaveBeenCalledWith("/api/projects", expect.anything());
  });

  it("applies the base path to post/patch/delete the same way as get", async () => {
    const fetchMock = vi.fn().mockResolvedValue(new Response(JSON.stringify({ ok: true }), { status: 200 }));
    vi.stubGlobal("fetch", fetchMock);

    setApiBasePath("/api/simulation");
    await api.post("/api/orchestrator/runs", { project_id: "PROJ-1" });

    expect(fetchMock).toHaveBeenCalledWith("/api/simulation/api/orchestrator/runs", expect.objectContaining({ method: "POST" }));
  });
});
