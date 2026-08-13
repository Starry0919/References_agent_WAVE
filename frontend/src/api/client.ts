/**
 * Thin fetch wrapper. Same-origin in both dev (Vite proxy, see
 * vite.config.ts) and production (FastAPI serves the built SPA) - no base
 * URL, no CORS config needed anywhere (Repository Truth Audit: the real
 * backend has no CORSMiddleware, so same-origin is a hard requirement,
 * not a preference).
 *
 * Simulation/Demo Workspace (查缺补漏04): every existing api/*.ts function
 * calls `api.get`/`api.post`/etc with a plain `/api/...` path - none of
 * them know or need to know whether they're running inside the real
 * Workspace or the sandboxed Simulation Workspace. `setApiBasePath` is the
 * ONE seam that redirects every one of those calls to the mounted
 * simulation sub-app (`/api/simulation` -> `harness/simulation_demo/app.py`,
 * a physically separate database from the real project ledger - see that
 * module's docstring) instead of duplicating every api/*.ts function.
 * `SimulationModeBoundary` (frontend/src/pages/simulation/) is the only
 * caller: it sets this on mount and restores "" on unmount, scoped to the
 * `/simulation/*` route subtree.
 */
import { STORAGE_KEY as LANG_STORAGE_KEY } from "@/lib/i18n";
import { pushLog } from "@/lib/logStore";

let basePath = "";

/**
 * Backend content localization (harness/i18n.py): the diagnosis/design
 * generators produce free-text narrative (hypothesis statements, strategy
 * rationale, etc) server-side, once, at generation time - the frontend's
 * language toggle can't retranslate it after the fact. Sending the active
 * language on every request lets the backend generate that content in the
 * matching locale from the start. Reads localStorage directly (not
 * `useI18n()`) because this module has no React context of its own.
 */
function currentLocaleHeader(): string {
  const saved = localStorage.getItem(LANG_STORAGE_KEY);
  return saved === "en-US" || saved === "zh-CN" ? saved : "zh-CN";
}

export function setApiBasePath(path: string): void {
  basePath = path;
}

export class ApiError extends Error {
  status: number;
  body: unknown;
  constructor(status: number, message: string, body: unknown) {
    super(message);
    this.status = status;
    this.body = body;
  }
}

/** Thrown when fetch itself fails (network down, backend not running). */
export class NetworkUnavailableError extends Error {}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const method = (init?.method ?? "GET").toUpperCase();
  const startedAt = performance.now();
  const elapsed = () => `${Math.round(performance.now() - startedAt)}ms`;
  let res: Response;
  try {
    res = await fetch(basePath + path, {
      ...init,
      headers: {
        "Content-Type": "application/json",
        "X-Locale": currentLocaleHeader(),
        ...(init?.headers ?? {}),
      },
    });
  } catch (e) {
    const message = e instanceof Error ? e.message : "network error";
    pushLog("error", "api", `${method} ${basePath + path} — network unavailable (${elapsed()})`, message);
    throw new NetworkUnavailableError(message);
  }
  if (!res.ok) {
    let body: unknown = undefined;
    try {
      body = await res.json();
    } catch {
      // no JSON body
    }
    const detail =
      body && typeof body === "object" && "detail" in body
        ? String((body as { detail: unknown }).detail)
        : res.statusText;
    pushLog(
      "error",
      "api",
      `${method} ${basePath + path} — ${res.status} (${elapsed()})`,
      body ? `${detail}\n${JSON.stringify(body, null, 2)}` : detail,
    );
    throw new ApiError(res.status, detail, body);
  }
  pushLog("info", "api", `${method} ${basePath + path} — ${res.status} (${elapsed()})`);
  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

export const api = {
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, body?: unknown) =>
    request<T>(path, { method: "POST", body: body ? JSON.stringify(body) : undefined }),
  patch: <T>(path: string, body?: unknown) =>
    request<T>(path, { method: "PATCH", body: body ? JSON.stringify(body) : undefined }),
  delete: <T>(path: string) => request<T>(path, { method: "DELETE" }),
};
