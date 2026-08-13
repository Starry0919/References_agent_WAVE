import { useEffect, useState } from "react";
import { ChevronDown, Copy, Terminal, Trash2, X } from "lucide-react";
import { clearLogEntries, formatLogEntry, getLogEntries, subscribeLog, type LogEntry, type LogLevel } from "@/lib/logStore";
import { useI18n } from "@/lib/i18n";

const LEVEL_DOT: Record<LogLevel, string> = {
  info: "bg-ink-faint",
  warn: "bg-state-caution",
  error: "bg-state-risk",
};

/**
 * Always-available, collapsed-by-default log console (request: the user
 * has no devtools open and can't hand us an error trace - this makes every
 * API call/failure and uncaught error visible inside the app itself, so
 * they can expand it, copy it, and paste it back to us instead of guessing
 * what broke). Mounted once in AppShell so it's present on every project
 * page, fixed above everything else in the stacking order.
 */
export function DebugLogPanel() {
  const { t } = useI18n();
  const [expanded, setExpanded] = useState(false);
  const [entries, setEntries] = useState<LogEntry[]>(() => getLogEntries());
  const [copied, setCopied] = useState(false);

  useEffect(() => subscribeLog(() => setEntries(getLogEntries())), []);

  const errorCount = entries.filter((e) => e.level === "error").length;
  const ordered = [...entries].reverse();

  async function copyAll() {
    const text = ordered.map(formatLogEntry).join("\n\n");
    try {
      await navigator.clipboard.writeText(text || t("debugLog.empty"));
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      // clipboard permission denied - nothing more we can do silently
    }
  }

  if (!expanded) {
    return (
      <button
        onClick={() => setExpanded(true)}
        className="fixed bottom-3 right-3 z-40 flex items-center gap-1.5 rounded-full border border-border bg-surface px-3 py-1.5 text-[11px] font-medium text-ink-muted shadow-md hover:bg-surface-sunken"
      >
        <Terminal size={12} aria-hidden />
        {t("debugLog.title")}
        {errorCount > 0 && (
          <span className="flex h-4 min-w-4 items-center justify-center rounded-full bg-state-risk px-1 text-[10px] font-semibold text-white">
            {errorCount}
          </span>
        )}
      </button>
    );
  }

  return (
    <div className="fixed bottom-0 right-0 z-40 flex h-80 w-full max-w-xl flex-col overflow-hidden border border-border bg-surface shadow-2xl sm:bottom-3 sm:right-3 sm:rounded-lg">
      <div className="flex items-center justify-between gap-2 border-b border-border bg-surface-sunken px-3 py-2">
        <div className="flex items-center gap-1.5 text-xs font-semibold text-ink">
          <Terminal size={13} aria-hidden />
          {t("debugLog.title")}
          <span className="rounded-full bg-surface px-1.5 py-0.5 text-[10px] font-normal text-ink-faint">{entries.length}</span>
        </div>
        <div className="flex items-center gap-1">
          <button onClick={copyAll} title={t("debugLog.copy")} className="rounded p-1.5 text-ink-faint hover:bg-surface hover:text-ink">
            <Copy size={13} aria-hidden />
          </button>
          <button onClick={clearLogEntries} title={t("debugLog.clear")} className="rounded p-1.5 text-ink-faint hover:bg-surface hover:text-ink">
            <Trash2 size={13} aria-hidden />
          </button>
          <button onClick={() => setExpanded(false)} title={t("debugLog.collapse")} className="rounded p-1.5 text-ink-faint hover:bg-surface hover:text-ink">
            <ChevronDown size={13} aria-hidden />
          </button>
          <button onClick={() => setExpanded(false)} title={t("debugLog.close")} className="rounded p-1.5 text-ink-faint hover:bg-surface hover:text-ink">
            <X size={13} aria-hidden />
          </button>
        </div>
      </div>
      {copied && <div className="bg-accent-soft px-3 py-1 text-[11px] text-accent-strong">{t("debugLog.copied")}</div>}
      <div className="flex-1 overflow-y-auto p-2">
        {ordered.length === 0 && <p className="p-3 text-center text-[11px] text-ink-faint">{t("debugLog.empty")}</p>}
        <ul className="flex flex-col gap-1">
          {ordered.map((e) => (
            <LogRow key={e.id} entry={e} />
          ))}
        </ul>
      </div>
    </div>
  );
}

function LogRow({ entry }: { entry: LogEntry }) {
  const [open, setOpen] = useState(false);
  const time = new Date(entry.timestamp).toLocaleTimeString();
  return (
    <li className="rounded border border-border bg-surface-sunken/40 px-2 py-1.5 text-[11px]">
      <button
        onClick={() => entry.detail && setOpen((o) => !o)}
        className={`flex w-full items-start gap-2 text-left ${entry.detail ? "cursor-pointer" : "cursor-default"}`}
      >
        <span className={`mt-1 h-1.5 w-1.5 shrink-0 rounded-full ${LEVEL_DOT[entry.level]}`} aria-hidden />
        <span className="shrink-0 font-mono text-ink-faint">{time}</span>
        <span className="shrink-0 rounded bg-surface px-1 text-ink-faint">{entry.source}</span>
        <span className={`min-w-0 flex-1 break-all font-mono ${entry.level === "error" ? "text-state-risk" : "text-ink-muted"}`}>{entry.summary}</span>
      </button>
      {open && entry.detail && (
        <pre className="mt-1.5 max-h-40 overflow-y-auto whitespace-pre-wrap break-all rounded bg-surface p-2 font-mono text-[10px] text-ink-faint">{entry.detail}</pre>
      )}
    </li>
  );
}
