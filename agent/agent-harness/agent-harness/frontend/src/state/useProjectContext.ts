import { useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { getActiveCycle, getProject } from "@/api/projects";

/**
 * Project/Cycle are URL-owned navigation state (State Ownership Matrix,
 * prompt §18.2): this hook reads `:projectId` from the route (never from
 * a global store) and layers server-state query caching on top, keyed by
 * project id so switching projects never silently serves stale data
 * (prompt §18.3).
 */
export function useProjectContext() {
  const { projectId } = useParams<{ projectId: string }>();

  const projectQuery = useQuery({
    queryKey: ["project", projectId],
    queryFn: () => getProject(projectId as string),
    enabled: !!projectId,
  });

  const cycleQuery = useQuery({
    queryKey: ["project", projectId, "cycle"],
    queryFn: () => getActiveCycle(projectId as string),
    enabled: !!projectId,
  });

  return {
    projectId,
    project: projectQuery.data,
    projectLoading: projectQuery.isLoading,
    projectError: projectQuery.error,
    cycle: cycleQuery.data,
    cycleLoading: cycleQuery.isLoading,
  };
}
