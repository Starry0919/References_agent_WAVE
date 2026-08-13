import { fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it } from "vitest";
import { I18nProvider, STORAGE_KEY, useI18n } from "@/lib/i18n";
import { LanguageToggle } from "./LanguageToggle";

function LanguageProbe() {
  const { lang } = useI18n();
  return <output>{lang}</output>;
}

describe("LanguageToggle", () => {
  beforeEach(() => localStorage.clear());

  it("switches state, persistent preference and document language in both directions", () => {
    render(
      <I18nProvider>
        <LanguageProbe />
        <LanguageToggle />
      </I18nProvider>,
    );

    expect(screen.getByText("zh-CN")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: /English/ }));
    expect(screen.getByText("en-US")).toBeInTheDocument();
    expect(localStorage.getItem(STORAGE_KEY)).toBe("en-US");
    expect(document.documentElement.lang).toBe("en-US");

    fireEvent.click(screen.getByRole("button", { name: /中文/ }));
    expect(screen.getByText("zh-CN")).toBeInTheDocument();
    expect(localStorage.getItem(STORAGE_KEY)).toBe("zh-CN");
    expect(document.documentElement.lang).toBe("zh-CN");
  });
});
