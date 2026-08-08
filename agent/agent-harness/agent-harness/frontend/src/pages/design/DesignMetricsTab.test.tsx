import { render, screen } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { I18nProvider } from "@/lib/i18n";
import type { EvaluationMetricsSummary } from "@/api/evaluationMetrics";
import { DesignMetricsTab } from "./DesignMetricsTab";

const mocks = vi.hoisted(() => ({
  summary: vi.fn(), consistencyRuns: vi.fn(), setReferenceDdr: vi.fn(), runConsistency: vi.fn(),
}));
vi.mock("@/api/evaluationMetrics", () => ({
  getMetricsSummary: (...args: unknown[]) => mocks.summary(...args),
  listConsistencyRuns: (...args: unknown[]) => mocks.consistencyRuns(...args),
  setReferenceDdr: (...args: unknown[]) => mocks.setReferenceDdr(...args),
  runConsistencySample: (...args: unknown[]) => mocks.runConsistency(...args),
}));

function renderTab(referenceDdrIds: string[] = []) {
  return render(
    <I18nProvider>
      <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
        <DesignMetricsTab designProjectId="DESIGNPROJ-1" referenceDdrIds={referenceDdrIds} />
      </QueryClientProvider>
    </I18nProvider>,
  );
}

const FULL_SUMMARY: EvaluationMetricsSummary = {
  designProjectId: "DESIGNPROJ-1",
  process: {
    groundingRate: { value: 0.5, numerator: 2, denominator: 4, applicable: true, note: "" },
    coverageCompleteness: {
      value: 3 / 9, numerator: 3, denominator: 9, applicable: true, note: "",
      coverageByClass: [
        { strategyClass: "feedback_relief", status: "covered", reason: "" },
        { strategyClass: "precursor_supply", status: "covered", reason: "" },
        { strategyClass: "dynamic_regulation", status: "excluded", reason: "not applicable" },
        { strategyClass: "competing_flux_control", status: "missing", reason: "" },
        { strategyClass: "cofactor_energy_balancing", status: "missing", reason: "" },
        { strategyClass: "resource_burden_management", status: "missing", reason: "" },
        { strategyClass: "transport_tolerance_engineering", status: "missing", reason: "" },
        { strategyClass: "process_condition_engineering", status: "missing", reason: "" },
        { strategyClass: "diagnostic_measurement_probe", status: "missing", reason: "" },
      ],
    },
  },
  capability: {
    screeningAbility: { value: 1 / 3, numerator: 1, denominator: 3, applicable: true, note: "" },
    reasonedNovelty: { value: 0.25, numerator: 1, denominator: 4, applicable: true, note: "", novelGroundedGenes: ["trpe"] },
  },
  sanityCheck: {
    reproductionRate: { value: 0.2, numerator: 1, denominator: 5, applicable: true, note: "" },
  },
};

beforeEach(() => {
  localStorage.setItem("dbtl-os.lang", "zh-CN");
  mocks.summary.mockReset();
  mocks.consistencyRuns.mockReset();
  mocks.consistencyRuns.mockResolvedValue([]);
});

describe("DesignMetricsTab", () => {
  it("renders metric tiles from a populated summary, scoped to the given design project", async () => {
    mocks.summary.mockResolvedValue(FULL_SUMMARY);
    renderTab(["DDR-001"]);

    expect(await screen.findByText("接地率")).toBeInTheDocument();
    expect(screen.getByText("50%")).toBeInTheDocument();
    expect(screen.getByText("2 / 4")).toBeInTheDocument();
    expect(mocks.summary).toHaveBeenCalledWith("DESIGNPROJ-1");

    expect(screen.getByText("3 / 9")).toBeInTheDocument();
    expect(screen.getByText("feedback_relief")).toBeInTheDocument();

    expect(screen.getByText("合理新颖")).toBeInTheDocument();
    expect(screen.getByText("trpe")).toBeInTheDocument();

    // 复现率 is rendered as a de-emphasized sanity-check card, never among the primary metrics.
    expect(screen.getByText("复现率")).toBeInTheDocument();
    expect(screen.getByText(/Sanity Check/)).toBeInTheDocument();

    expect(screen.getByText("DDR-001")).toBeInTheDocument();
  });

  it("shows an unavailable state for novelty/reproduction when not applicable", async () => {
    mocks.summary.mockResolvedValue({
      ...FULL_SUMMARY,
      capability: { ...FULL_SUMMARY.capability, reasonedNovelty: { value: null, numerator: 0, denominator: 0, applicable: false, note: "design project has no reference_ddr_ids linked yet", novelGroundedGenes: [] } },
      sanityCheck: { reproductionRate: { value: null, numerator: 0, denominator: 0, applicable: false, note: "design project has no reference_ddr_ids linked yet" } },
    });
    renderTab([]);

    expect(await screen.findByText("暂不可计算")).toBeInTheDocument();
  });
});
