import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { I18nProvider } from "@/lib/i18n";
import { EmptyState } from "./EmptyState";

/**
 * Regression guard for prompt §14.4 ("禁止将 empty state 统一写成 No data"):
 * every variant this app actually uses must render distinguishable copy,
 * not a single generic placeholder. Wrapped in I18nProvider since default
 * titles now route through t() (Final Closure i18n coverage pass).
 */
function renderWithI18n(ui: React.ReactElement) {
  return render(<I18nProvider>{ui}</I18nProvider>);
}

describe("EmptyState", () => {
  it("gives the unavailable variant capability-specific copy, distinct from a generic empty list", () => {
    renderWithI18n(<EmptyState variant="unavailable" title="Unavailable via current API" detail="No route resolves this id." />);
    expect(screen.getByText("Unavailable via current API")).toBeInTheDocument();
    expect(screen.getByText("No route resolves this id.")).toBeInTheDocument();
  });

  it("falls back to each variant's own default title when none is passed, and different variants get different defaults", () => {
    const { rerender } = renderWithI18n(<EmptyState variant="disconnected" />);
    const disconnectedText = screen.getByText((_, el) => el?.tagName === "P" && el.className.includes("font-medium")).textContent;

    rerender(
      <I18nProvider>
        <EmptyState variant="stale" />
      </I18nProvider>,
    );
    const staleText = screen.getByText((_, el) => el?.tagName === "P" && el.className.includes("font-medium")).textContent;

    rerender(
      <I18nProvider>
        <EmptyState variant="failed" />
      </I18nProvider>,
    );
    const failedText = screen.getByText((_, el) => el?.tagName === "P" && el.className.includes("font-medium")).textContent;

    expect(disconnectedText).toBeTruthy();
    expect(staleText).toBeTruthy();
    expect(failedText).toBeTruthy();
    expect(new Set([disconnectedText, staleText, failedText]).size).toBe(3);
  });

  it("renders an optional action (e.g. retry / start) without requiring one", () => {
    renderWithI18n(<EmptyState variant="first_use" action={<button>Start orchestrated workflow</button>} />);
    expect(screen.getByRole("button", { name: "Start orchestrated workflow" })).toBeInTheDocument();
  });
});
