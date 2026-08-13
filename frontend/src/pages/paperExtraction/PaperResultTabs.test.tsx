import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it } from "vitest";
import { I18nProvider } from "@/lib/i18n";
import type { DesignField, PaperExtractionSummary } from "@/api/paperExtraction";
import { CompareTab } from "./PaperResultTabs";

// Assertions match English copy; force en-US (see ApplicabilityPanel.test.tsx precedent).
function renderTab(ui: React.ReactElement) {
  return render(<I18nProvider>{ui}</I18nProvider>);
}

function field(overrides: Partial<DesignField>): DesignField {
  return {
    key: "objective",
    label: "Objective",
    value: "improve titer",
    status: "reported",
    statusLabel: "Reported",
    confidence: null,
    evidence: [],
    reasoning: { extractionMethod: null, notes: null, inferenceMethod: null, inferenceRationale: null },
    verified: true,
    ...overrides,
  };
}

function summary(designFields: DesignField[]): PaperExtractionSummary {
  return {
    paperId: "paper_1",
    identity: { title: "Test Paper", authors: [], journal: null, year: null, doi: null },
    articleType: null,
    targetStrains: [],
    designFields,
    hasDesignContent: designFields.some((f) => f.status !== "unknown"),
    quality: {
      completeness: null,
      reproducibility: null,
      evidenceLevel: null,
      extractionConfidence: null,
      missingInformation: [],
      overallScore: null,
      confidenceLabel: null,
      recommendation: null,
      dimensions: {},
      risks: [],
    },
    coverage: {},
    governanceNote: null,
    evidenceSourceId: null,
  };
}

describe("CompareTab", () => {
  beforeEach(() => {
    localStorage.setItem("dbtl-os.lang", "en-US");
  });

  it("shows the empty state instead of a three-column grid when the paper has no design content", () => {
    renderTab(<CompareTab paper={summary([])} />);
    expect(screen.getByText("No structured experimental design content identified yet")).toBeInTheDocument();
  });

  it("renders the extraction method, notes and matching literal quote for a directly-reported field (skill07 notes path)", () => {
    const f = field({
      key: "medium",
      label: "Medium",
      value: "M9 minimal medium",
      reasoning: { extractionMethod: "hybrid", notes: "derived from Methods section", inferenceMethod: null, inferenceRationale: null },
      evidence: [{ evidenceId: "ev_1", quote: "Cells were grown in M9 minimal medium.", page: 3, sectionPath: ["Methods"], figureId: null, tableId: null }],
    });
    renderTab(<CompareTab paper={summary([f])} />);
    // column 1: extraction process
    expect(screen.getByText("Rule matching + model judgment")).toBeInTheDocument();
    expect(screen.getByText("derived from Methods section")).toBeInTheDocument();
    // column 2: agent's final claim
    expect(screen.getByText("M9 minimal medium")).toBeInTheDocument();
    // column 3: paper's own words
    expect(screen.getByText(/Cells were grown in M9 minimal medium\./)).toBeInTheDocument();
  });

  it("renders the inference rationale for an inferred field and flags the missing quote (skill07 inference path)", () => {
    const f = field({
      key: "hypothesis",
      label: "Hypothesis",
      status: "inferred",
      statusLabel: "Inferred",
      value: "flux redistribution relieves the bottleneck",
      reasoning: {
        extractionMethod: "model_inference",
        notes: null,
        inferenceMethod: "mechanistic reasoning",
        inferenceRationale: "consistent with known precursor-supply constraints",
      },
      evidence: [],
    });
    renderTab(<CompareTab paper={summary([f])} />);
    expect(screen.getByText("Model inference")).toBeInTheDocument();
    expect(screen.getByText(/consistent with known precursor-supply constraints/)).toBeInTheDocument();
    expect(screen.getByText(/mechanistic reasoning/)).toBeInTheDocument();
    // no supporting quote -> flagged, not silently omitted
    expect(screen.getByText(/No supporting quote found in the paper/)).toBeInTheDocument();
  });

  it("falls back to an explicit 'no process notes' message when a field's reasoning is entirely empty", () => {
    const f = field({
      key: "strain",
      label: "Strain",
      value: "E. coli MG1655",
      reasoning: { extractionMethod: null, notes: null, inferenceMethod: null, inferenceRationale: null },
    });
    renderTab(<CompareTab paper={summary([f])} />);
    expect(screen.getByText("No additional extraction-process notes were recorded for this field.")).toBeInTheDocument();
  });

  it("omits fields the pipeline never reported anything for (status='unknown') from the comparison rows", () => {
    const known = field({ key: "objective", value: "improve titer" });
    const unknown = field({ key: "instruments", label: "Instruments", value: null, status: "unknown", statusLabel: "Unknown" });
    renderTab(<CompareTab paper={summary([known, unknown])} />);
    expect(screen.getByText("improve titer")).toBeInTheDocument();
    expect(screen.queryByText("Instruments")).not.toBeInTheDocument();
  });
});
