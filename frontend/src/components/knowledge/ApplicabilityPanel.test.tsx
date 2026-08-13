import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it } from "vitest";
import { I18nProvider } from "@/lib/i18n";
import { ApplicabilityPanel } from "./ApplicabilityPanel";

// Assertions match English copy; force en-US (Final Closure i18n pass).
function renderPanel(ui: React.ReactElement) {
  return render(<I18nProvider>{ui}</I18nProvider>);
}

describe("ApplicabilityPanel", () => {
  beforeEach(() => {
    localStorage.setItem("dbtl-os.lang", "en-US");
  });

  it("renders literal 'Unknown' for every missing scope dimension, never omitting the row (prompt §17: unknown must not read as universal)", () => {
    renderPanel(<ApplicabilityPanel scope={{ species: "E. coli" }} />);
    expect(screen.getByText("Species")).toBeInTheDocument();
    expect(screen.getByText("E. coli")).toBeInTheDocument();
    // The other 6 dimensions must each render "Unknown", not be dropped.
    expect(screen.getAllByText("Unknown")).toHaveLength(6);
  });

  it("treats an empty string the same as a missing key (both unknown, not a fabricated blank fact)", () => {
    renderPanel(<ApplicabilityPanel scope={{ species: "", medium: "glucose minimal medium" }} />);
    expect(screen.getByText("glucose minimal medium")).toBeInTheDocument();
    expect(screen.getAllByText("Unknown")).toHaveLength(6);
  });
});
