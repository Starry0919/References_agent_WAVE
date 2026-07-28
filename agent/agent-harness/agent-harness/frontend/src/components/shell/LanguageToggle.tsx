import { Languages } from "lucide-react";
import { useI18n } from "@/lib/i18n";

export function LanguageToggle() {
  const { lang, setLang, t } = useI18n();
  return (
    <button
      type="button"
      onClick={() => setLang(lang === "zh-CN" ? "en-US" : "zh-CN")}
      className="flex items-center gap-1 rounded border border-border px-2 py-1 text-xs text-ink-muted hover:border-accent hover:text-accent-strong"
    >
      <Languages size={13} aria-hidden />
      {t("lang.toggle")}
    </button>
  );
}
