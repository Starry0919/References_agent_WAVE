import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { I18nProvider } from "@/lib/i18n";
import { RunNewDiagnosisPage } from "./RunNewDiagnosisPage";

const mocks = vi.hoisted(() => ({
  getProject: vi.fn(), evidenceItems: vi.fn(), capabilities: vi.fn(), createRun: vi.fn(), getRun: vi.fn(), startDiagnosis: vi.fn(),
  projectObservations: vi.fn(),
  getSession: vi.fn(), hypotheses: vi.fn(), evidence: vi.fn(), decisions: vi.fn(), tests: vi.fn(), handoff: vi.fn(),
}));

vi.mock("@/api/projects", () => ({ getProject: (...args: unknown[]) => mocks.getProject(...args) }));
vi.mock("@/api/orchestrator", () => ({
  createRun: (...args: unknown[]) => mocks.createRun(...args), getRun: (...args: unknown[]) => mocks.getRun(...args), startDiagnosis: (...args: unknown[]) => mocks.startDiagnosis(...args),
}));
vi.mock("@/api/engineeringDesign", () => ({ createHandoff: (...args: unknown[]) => mocks.handoff(...args) }));
vi.mock("@/api/experiments", () => ({ listProjectObservations: (...args: unknown[]) => mocks.projectObservations(...args) }));
vi.mock("@/api/diagnosis", () => ({
  listEvidenceItems: (...args: unknown[]) => mocks.evidenceItems(...args), listModelCapabilities: (...args: unknown[]) => mocks.capabilities(...args),
  getSession: (...args: unknown[]) => mocks.getSession(...args), listHypotheses: (...args: unknown[]) => mocks.hypotheses(...args),
  listEvidence: (...args: unknown[]) => mocks.evidence(...args), listDecisions: (...args: unknown[]) => mocks.decisions(...args),
  listTests: (...args: unknown[]) => mocks.tests(...args),
}));

function renderPage() {
  return render(<I18nProvider><QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false }, mutations: { retry: false } } })}><MemoryRouter initialEntries={["/projects/PROJ-1/run_new_diagnose"]}><Routes><Route path="/projects/:projectId/run_new_diagnose" element={<RunNewDiagnosisPage/>}/></Routes></MemoryRouter></QueryClientProvider></I18nProvider>);
}

beforeEach(() => {
  localStorage.setItem("dbtl-os.lang", "en-US");
  mocks.getProject.mockResolvedValue({ projectId: "PROJ-1", name: "Tryptophan", status: "active", lifecycleStage: "DIAGNOSIS", targetProduct: "L-tryptophan", hostDefinition: { species: "Escherichia coli", strain: "K-12" }, objectives: [], constraints: [], currentDesignVersionId: null, version: 1 });
  mocks.evidenceItems.mockResolvedValue([]); mocks.capabilities.mockResolvedValue({ cobra: { available: false, reason: "not installed" } });
  mocks.projectObservations.mockResolvedValue([
    { observationId: "OBS-subject", metric: "titer", value: 8, unit: "g/L", conditionRef: { medium: "M9" }, qcStatus: "passed", sourceType: "instrument" },
    { observationId: "OBS-base", metric: "titer", value: 12, unit: "g/L", conditionRef: { medium: "M9" }, qcStatus: "passed", sourceType: "instrument" },
  ]);
  mocks.hypotheses.mockResolvedValue([]); mocks.evidence.mockResolvedValue([]); mocks.decisions.mockResolvedValue([]); mocks.tests.mockResolvedValue([]);
  mocks.getSession.mockResolvedValue({ diagnosisSessionId: "DIAG-1", projectId: "PROJ-1", status: "data_required", dataSufficiency: "partial", approvalState: "not_required", activeHypothesisSetVersion: 0, biologicalSystem: {}, baselineObservationIds: [], version: 1 });
  mocks.createRun.mockResolvedValue({ workflowRunId: "RUN-1", projectId: "PROJ-1", version: 1, diagnosisRunRef: null });
  mocks.startDiagnosis.mockResolvedValue({ workflowRunId: "RUN-1", projectId: "PROJ-1", version: 2, diagnosisRunRef: "DIAG-1", blockedReason: "data_required" });
});

describe("RunNewDiagnosisPage", () => {
  it("renders conservative scientific configuration from real project context", async () => {
    renderPage();
    expect(await screen.findByText("Run New Diagnosis")).toBeInTheDocument();
    expect(screen.getAllByText(/Escherichia coli/).length).toBeGreaterThan(0);
    expect(screen.getByText("0 / 1")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Start diagnosis" })).toBeDisabled();
    await waitFor(() => expect(screen.getByRole("checkbox", { name: "Genotype / chassis" })).toBeChecked());
    expect(screen.getByRole("checkbox", { name: "Baseline or comparator" })).not.toBeChecked();
  });

  it("uses the real gate result and renders a partial checkpoint", async () => {
    renderPage();
    fireEvent.change(await screen.findByLabelText("Diagnostic question or observed phenotype"), { target: { value: "Measured titer remains below baseline" } });
    fireEvent.change(screen.getByLabelText("Subject measurement"), { target: { value: "OBS-subject" } });
    fireEvent.change(screen.getByLabelText("Matched baseline"), { target: { value: "OBS-base" } });
    fireEvent.click(screen.getByRole("button", { name: "Start diagnosis" }));
    expect(await screen.findByText("The run stopped at a legitimate checkpoint.")).toBeInTheDocument();
    expect(mocks.startDiagnosis).toHaveBeenCalledWith("RUN-1", expect.objectContaining({ observationIds: ["OBS-subject"], baselineObservationIds: ["OBS-base"], dataSufficiency: expect.objectContaining({ hasBaseline: false, hasGenotype: true }) }));
    expect(screen.getByRole("button", { name: /Proceed to Engineering Design/ })).toBeDisabled();
  });
});
