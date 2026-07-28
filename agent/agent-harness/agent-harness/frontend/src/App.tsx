import { QueryClientProvider } from "@tanstack/react-query";
import { RouterProvider } from "react-router-dom";
import { queryClient } from "@/lib/queryClient";
import { I18nProvider } from "@/lib/i18n";
import { BackendHealthProvider } from "@/state/BackendHealth";
import { router } from "@/router";

export function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BackendHealthProvider>
        <I18nProvider>
          <RouterProvider router={router} />
        </I18nProvider>
      </BackendHealthProvider>
    </QueryClientProvider>
  );
}
