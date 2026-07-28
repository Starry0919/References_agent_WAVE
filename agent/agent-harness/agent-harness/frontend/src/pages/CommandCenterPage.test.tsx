import { render, screen } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { I18nProvider } from "@/lib/i18n";
import { CommandCenterPage } from "./CommandCenterPage";

const mocks = vi.hoisted(() => ({
  health: vi.fn(), context: vi.fn(), status: vi.fn(), timeline: vi.fn(), ideas: vi.fn(),
}));
vi.mock("@/state/BackendHealth", () => ({ useBackendHealth: mocks.health }));
vi.mock("@/state/useProjectContext", () => ({ useProjectContext: mocks.context }));
vi.mock("@/api/projects", () => ({
  getProjectStatusView: (...args: unknown[]) => mocks.status(...args),
  getTimeline: (...args: unknown[]) => mocks.timeline(...args),
}));
vi.mock("@/api/ideas", () => ({ listIdeas: (...args: unknown[]) => mocks.ideas(...args) }));

function renderPage() {
  return render(
    <I18nProvider>
      <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
        <MemoryRouter initialEntries={["/projects/PROJ-1"]}>
          <Routes><Route path="/projects/:projectId" element={<CommandCenterPage />} /></Routes>
        </MemoryRouter>
      </QueryClientProvider>
    </I18nProvider>,
  );
}

beforeEach(() => {
  localStorage.setItem("dbtl-os.lang", "en-US");
  mocks.health.mockReturnValue({ connected: true });
  mocks.timeline.mockResolvedValue([]);
  mocks.status.mockResolvedValue({
    activeDesignVersion: "DV-1", nextActions: ["capture baseline design"], blockers: [],
  });
  mocks.ideas.mockResolvedValue([{
    ideaId: "IDEA-1", projectId: "PROJ-1", actorId: "pi",
    freeText: "Overexpress feedback-resistant trpE", targetGene: "trpE",
    modificationType: "overexpression", rationale: "increase pathway flux",
    status: "captured", linkedDesignProjectId: null, createdAt: 1_700_000_000,
  }]);
});

describe("CommandCenterPage dashboard", () => {
  it("renders the goal, idea sources and current ideas", async () => {
    mocks.context.mockReturnValue({
      projectLoading: false,
      project: {
        projectId: "PROJ-1", name: "VC Live Demo", status: "active",
        lifecycleStage: "PROJECT_CONTEXT_READY", targetProduct: "L-tryptophan",
        hostDefinition: { species: "Escherichia coli", strain: "K-12" },
        objectives: ["Increase L-tryptophan yield"], constraints: [],
        currentDesignVersionId: "DV-1", version: 2,
      },
      cycle: { cycleStateId: "CYCLE-1", currentState: "DESIGN", status: "running" },
    });
    renderPage();
    expect(screen.getByText("Increase L-tryptophan yield")).toBeInTheDocument();
    expect(await screen.findByText("Overexpress feedback-resistant trpE")).toBeInTheDocument();
    expect(screen.getByText("Idea sources")).toBeInTheDocument();
    expect(screen.getByText("capture baseline design")).toBeInTheDocument();
  });

  it("keeps the disconnected state", () => {
    mocks.health.mockReturnValue({ connected: false });
    mocks.context.mockReturnValue({ projectLoading: false, project: undefined, cycle: undefined });
    renderPage();
    expect(screen.getByText(/backend disconnected/i)).toBeInTheDocument();
  });
});
