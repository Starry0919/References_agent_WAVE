import { createContext, useContext, type ReactNode } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/api/client";

/**
 * Backend connectivity / capability status: genuinely cross-page global
 * state that cannot be derived from the URL or a single query cache entry
 * (State Ownership Matrix, prompt §18.2 - "capability status" is named
 * explicitly as belonging in a global store). Polls the real
 * `GET /api/health` endpoint (harness/server.py) - if this fails, every
 * page must show a real "backend disconnected" state, never a silent
 * fallback to mock data (prompt §14.4).
 */

interface HealthPayload {
  ok: boolean;
  provider: string;
  model: string | null;
  tools: number;
}

interface BackendHealthValue {
  connected: boolean;
  checking: boolean;
  payload: HealthPayload | undefined;
  lastError: string | null;
}

const BackendHealthContext = createContext<BackendHealthValue | null>(null);

export function BackendHealthProvider({ children }: { children: ReactNode }) {
  const query = useQuery({
    queryKey: ["backend-health"],
    queryFn: () => api.get<HealthPayload>("/api/health"),
    refetchInterval: 30_000,
    retry: 0,
  });

  const value: BackendHealthValue = {
    connected: query.isSuccess && !!query.data?.ok,
    checking: query.isLoading,
    payload: query.data,
    lastError: query.error instanceof Error ? query.error.message : null,
  };

  return <BackendHealthContext.Provider value={value}>{children}</BackendHealthContext.Provider>;
}

export function useBackendHealth(): BackendHealthValue {
  const ctx = useContext(BackendHealthContext);
  if (!ctx) throw new Error("useBackendHealth must be used within BackendHealthProvider");
  return ctx;
}
