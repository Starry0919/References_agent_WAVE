import { Outlet } from "react-router-dom";
import { TopNav } from "./TopNav";
import { ProjectContextBar } from "./ProjectContextBar";
import { ErrorBoundary } from "@/components/common/ErrorBoundary";
import { DebugLogPanel } from "@/components/common/DebugLogPanel";

/**
 * L0 in the component hierarchy (prompt §13.7): global nav, context and
 * layout slots only. Never imports a page-specific data hook - adding a
 * new top-level page must not touch this file (prompt §18.1).
 */
export function AppShell() {
  return (
    <div className="flex h-screen flex-col overflow-hidden">
      <TopNav />
      <ProjectContextBar />
      <main className="flex min-h-0 flex-1 flex-col overflow-hidden">
        <ErrorBoundary>
          <Outlet />
        </ErrorBoundary>
      </main>
      <DebugLogPanel />
    </div>
  );
}
