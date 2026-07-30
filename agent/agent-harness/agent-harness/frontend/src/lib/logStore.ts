/**
 * In-app diagnostic log (request: "看不到问题在哪里" - the user has no
 * devtools open and can't hand us a console/network trace, so the app
 * captures its own API calls, uncaught errors and unhandled promise
 * rejections into a small ring buffer that `DebugLogPanel` renders,
 * collapsed by default). Plain module-level pub/sub rather than React
 * context/state - `src/api/client.ts` (every `api.get/post/...` call) and
 * `ErrorBoundary` (a class component) both need to push into this without
 * being inside a React tree themselves.
 */

export type LogLevel = "info" | "warn" | "error";

export interface LogEntry {
  id: number;
  timestamp: number;
  level: LogLevel;
  source: string;
  summary: string;
  detail?: string;
}

const MAX_ENTRIES = 300;
let entries: LogEntry[] = [];
let nextId = 1;
const listeners = new Set<() => void>();

function emit(): void {
  for (const l of listeners) l();
}

export function pushLog(level: LogLevel, source: string, summary: string, detail?: string): void {
  entries = [...entries, { id: nextId++, timestamp: Date.now(), level, source, summary, detail }];
  if (entries.length > MAX_ENTRIES) entries = entries.slice(entries.length - MAX_ENTRIES);
  emit();
}

export function getLogEntries(): LogEntry[] {
  return entries;
}

export function clearLogEntries(): void {
  entries = [];
  emit();
}

export function subscribeLog(cb: () => void): () => void {
  listeners.add(cb);
  return () => listeners.delete(cb);
}

export function formatLogEntry(e: LogEntry): string {
  const time = new Date(e.timestamp).toLocaleTimeString();
  return `[${time}] [${e.level.toUpperCase()}] [${e.source}] ${e.summary}${e.detail ? `\n${e.detail}` : ""}`;
}

// Registered once at module load (this module is imported exactly once by
// the bundler; AppShell mounting DebugLogPanel on every route is what
// guarantees that import happens before anything else can throw).
if (typeof window !== "undefined") {
  window.addEventListener("error", (event) => {
    pushLog("error", "window", event.message || "Uncaught error", event.error?.stack);
  });
  window.addEventListener("unhandledrejection", (event) => {
    const reason = event.reason as unknown;
    const summary = reason instanceof Error ? reason.message : String(reason);
    const detail = reason instanceof Error ? reason.stack : undefined;
    pushLog("error", "promise", summary, detail);
  });
}
