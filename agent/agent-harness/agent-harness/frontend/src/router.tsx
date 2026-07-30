import { createBrowserRouter, Navigate } from "react-router-dom";
import { AppShell } from "@/components/shell/AppShell";
import { ProjectSwitcherPage } from "@/pages/ProjectSwitcherPage";
import { CommandCenterPage } from "@/pages/CommandCenterPage";
import { KnowledgePage } from "@/pages/knowledge/KnowledgePage";
import { IdeaWorkspacePage } from "@/pages/IdeaWorkspacePage";
import { PaperEvidenceDetailPage } from "@/pages/evidence/PaperEvidenceDetailPage";
import { TrustCenterPage } from "@/pages/trust/TrustCenterPage";

/**
 * Route contract (prompt §6.3). All object-bearing routes are addressable
 * and refresh-safe: project/cycle/stage/version live in the URL (path
 * segments or search params), never only in memory (prompt §22.4 "路由可
 * 刷新恢复").
 */
export const router = createBrowserRouter(
  [
    { path: "/", element: <Navigate to="/projects" replace /> },
    { path: "/projects", element: <ProjectSwitcherPage /> },
    {
      path: "/projects/:projectId",
      element: <AppShell />,
      children: [
        { index: true, element: <CommandCenterPage /> },
        { path: "ideas", element: <IdeaWorkspacePage /> },
        { path: "workspace", element: <Navigate to="../ideas" replace /> },
        { path: "knowledge", element: <KnowledgePage /> },
        { path: "paper-extraction", element: <Navigate to="../knowledge?tab=extraction" replace /> },
        { path: "evidence/:sourceId", element: <PaperEvidenceDetailPage /> },
        { path: "trust/:ddrId", element: <TrustCenterPage /> },
      ],
    },
    { path: "*", element: <Navigate to="/projects" replace /> },
  ],
  { basename: "/" },
);
