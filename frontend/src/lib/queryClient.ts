import { QueryClient } from "@tanstack/react-query";

// Server state / query cache (State Ownership Matrix, prompt §18.2):
// design/evidence/approval/simulation results live here, keyed by
// project+object+version so selection changes never silently reuse a
// stale cache entry (prompt §18.3).
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      staleTime: 15_000,
      refetchOnWindowFocus: false,
    },
  },
});
