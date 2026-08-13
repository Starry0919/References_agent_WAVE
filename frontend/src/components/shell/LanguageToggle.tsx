import { Languages } from "lucide-react";
import { useI18n } from "@/lib/i18n";
import { queryClient } from "@/lib/queryClient";

export function LanguageToggle() {
  const { lang, setLang } = useI18n();
  const switchLanguage = () => {
    const next = lang === "zh-CN" ? "en-US" : "zh-CN";
    setLang(next);
    // API responses contain localized narrative and must not remain in the
    // previous-language React Query cache after a global language switch.
    void queryClient.invalidateQueries();
  };
  return (
    <button
      type="button"
      data-i18n-ignore
      onClick={switchLanguage}
      className="flex items-center gap-1 rounded border border-border px-2 py-1 text-xs text-ink-muted hover:border-accent hover:text-accent-strong"
    >
      <Languages size={13} aria-hidden />
      {lang === "zh-CN" ? "English" : "中文"}
    </button>
  );
}
