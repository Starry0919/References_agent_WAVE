import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Plus, FlaskConical, MoreVertical, Trash2, X } from "lucide-react";
import { createProject, deleteProject, listProjects, renameProject } from "@/api/projects";
import { EmptyState } from "@/components/common/EmptyState";
import { StatusBadge, type BadgeStatus } from "@/components/common/StatusBadge";
import { useBackendHealth } from "@/state/BackendHealth";
import { useI18n } from "@/lib/i18n";
import { LanguageToggle } from "@/components/shell/LanguageToggle";
import type { ProjectSummary } from "@/types/domain";

/**
 * The explicit project-switch entry point (prompt §6.2: "项目切换必须是
 * 显式操作"). This is the only screen that does not require a project in
 * context, so it lives outside AppShell's project-scoped nav.
 */
export function ProjectSwitcherPage() {
  const navigate = useNavigate();
  const { t } = useI18n();
  const { connected, checking } = useBackendHealth();
  const projectsQuery = useQuery({ queryKey: ["projects"], queryFn: listProjects, enabled: connected });
  const qc = useQueryClient();
  const [showCreate, setShowCreate] = useState(false);
  const [name, setName] = useState("");
  const [targetProduct, setTargetProduct] = useState("");

  const [menuOpenFor, setMenuOpenFor] = useState<string | null>(null);
  const [renamingId, setRenamingId] = useState<string | null>(null);
  const [renameValue, setRenameValue] = useState("");
  const [deleteTarget, setDeleteTarget] = useState<ProjectSummary | null>(null);
  const [selectionMode, setSelectionMode] = useState(false);
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [showBatchDeleteConfirm, setShowBatchDeleteConfirm] = useState(false);

  function exitSelectionMode() {
    setSelectionMode(false);
    setSelectedIds(new Set());
  }

  const createMutation = useMutation({
    mutationFn: () => createProject({ name, targetProduct, objectives: [], constraints: [], actorId: "frontend-user" }),
    onSuccess: (p) => {
      qc.invalidateQueries({ queryKey: ["projects"] });
      navigate(`/projects/${p.projectId}`);
    },
  });

  const renameMutation = useMutation({
    mutationFn: (input: { projectId: string; name: string }) => renameProject(input.projectId, input.name),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["projects"] });
      setRenamingId(null);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (projectId: string) => deleteProject(projectId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["projects"] });
      setDeleteTarget(null);
    },
  });

  const batchDeleteMutation = useMutation({
    mutationFn: (projectIds: string[]) => Promise.all(projectIds.map((id) => deleteProject(id))),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["projects"] });
      setShowBatchDeleteConfirm(false);
      exitSelectionMode();
    },
  });

  function toggleSelected(projectId: string) {
    setSelectedIds((cur) => {
      const next = new Set(cur);
      if (next.has(projectId)) next.delete(projectId);
      else next.add(projectId);
      return next;
    });
  }

  return (
    <div className="mx-auto flex h-full max-w-2xl flex-col gap-4 overflow-y-auto p-8">
      <div className="flex items-start justify-between gap-3">
        <div>
          <h1 className="text-lg font-semibold text-ink">{t("nav.appTitle")}</h1>
          <p className="text-sm text-ink-muted">{t("switcher.subtitle")}</p>
        </div>
        <div className="flex items-center gap-3">
          {connected && projectsQuery.data && projectsQuery.data.length > 0 && (
            <button
              onClick={() => (selectionMode ? exitSelectionMode() : setSelectionMode(true))}
              className={
                selectionMode
                  ? "flex items-center gap-1.5 rounded border border-border px-2.5 py-1.5 text-xs font-medium text-ink-muted hover:border-accent hover:text-accent-strong"
                  : "flex items-center gap-1.5 rounded border border-state-risk px-2.5 py-1.5 text-xs font-medium text-state-risk hover:bg-state-risk/10"
              }
            >
              {selectionMode ? (
                <>
                  <X size={14} /> {t("switcher.cancel")}
                </>
              ) : (
                <>
                  <Trash2 size={14} /> {t("switcher.batchDelete")}
                </>
              )}
            </button>
          )}
          <LanguageToggle />
        </div>
      </div>

      {checking && <EmptyState variant="loading" />}
      {!checking && !connected && (
        <EmptyState
          variant="disconnected"
          title={t("switcher.backendDisconnected")}
          detail={t("switcher.backendDisconnectedDetail")}
        />
      )}

      {connected && projectsQuery.isLoading && <EmptyState variant="loading" />}
      {connected && projectsQuery.isError && (
        <EmptyState variant="failed" detail={String(projectsQuery.error)} />
      )}
      {connected && projectsQuery.data && projectsQuery.data.length === 0 && !showCreate && (
        <EmptyState variant="first_use" title={t("switcher.noProjectsYet")} detail={t("switcher.noProjectsDetail")} />
      )}

      {connected && projectsQuery.data && projectsQuery.data.length > 0 && (
        <>
          {selectionMode && (
            <div className="flex items-center justify-between gap-3 px-1">
              <label className="flex items-center gap-2 text-xs font-medium text-ink-muted">
                <input
                  type="checkbox"
                  checked={selectedIds.size > 0 && selectedIds.size === projectsQuery.data.length}
                  onChange={(e) => setSelectedIds(e.target.checked ? new Set(projectsQuery.data!.map((p) => p.projectId)) : new Set())}
                />
                {selectedIds.size > 0 ? `${t("switcher.selectedCount")} ${selectedIds.size}` : t("switcher.selectAll")}
              </label>
              {selectedIds.size > 0 && (
                <button
                  onClick={() => setShowBatchDeleteConfirm(true)}
                  className="rounded px-2.5 py-1 text-xs font-medium text-state-risk hover:bg-surface-sunken"
                >
                  {t("switcher.batchDeleteSelected")}
                </button>
              )}
            </div>
          )}
          <ul className="flex flex-col gap-1.5">
          {projectsQuery.data.map((p) => (
            <li key={p.projectId} className="panel relative flex w-full items-center justify-between gap-3 px-3 py-2.5 hover:border-accent">
              {selectionMode && (
                <input
                  type="checkbox"
                  className="mr-1 flex-shrink-0"
                  checked={selectedIds.has(p.projectId)}
                  onChange={() => toggleSelected(p.projectId)}
                  aria-label={t("switcher.selectProject")}
                />
              )}
              {renamingId === p.projectId ? (
                <div className="flex flex-1 items-center gap-2">
                  <input
                    autoFocus
                    className="flex-1 rounded border border-border px-2 py-1 text-sm"
                    value={renameValue}
                    onChange={(e) => setRenameValue(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter" && renameValue.trim()) renameMutation.mutate({ projectId: p.projectId, name: renameValue.trim() });
                      if (e.key === "Escape") setRenamingId(null);
                    }}
                  />
                  <button
                    disabled={!renameValue.trim() || renameMutation.isPending}
                    onClick={() => renameMutation.mutate({ projectId: p.projectId, name: renameValue.trim() })}
                    className="rounded bg-accent px-2.5 py-1 text-xs font-medium text-white disabled:opacity-40"
                  >
                    {renameMutation.isPending ? t("switcher.saving") : t("switcher.save")}
                  </button>
                  <button onClick={() => setRenamingId(null)} className="rounded px-2.5 py-1 text-xs text-ink-muted">
                    {t("switcher.cancel")}
                  </button>
                </div>
              ) : (
                <>
                  <button
                    onClick={() => navigate(`/projects/${p.projectId}`)}
                    className="flex min-w-0 flex-1 items-center gap-2 text-left"
                  >
                    <FlaskConical size={14} className="flex-shrink-0 text-accent" aria-hidden />
                    <span className="min-w-0">
                      <span className="block truncate text-sm font-medium text-ink">{p.name}</span>
                      <span className="block font-mono text-[11px] text-ink-faint">{p.projectId}</span>
                    </span>
                  </button>
                  <div className="flex flex-shrink-0 items-center gap-2">
                    <StatusBadge status={p.status as BadgeStatus} label={`${p.status} · ${p.lifecycleStage}`} />
                    <button
                      aria-label={t("switcher.moreActions")}
                      onClick={() => setMenuOpenFor((cur) => (cur === p.projectId ? null : p.projectId))}
                      className="rounded p-1 text-ink-faint hover:bg-surface-sunken hover:text-ink"
                    >
                      <MoreVertical size={14} />
                    </button>
                  </div>
                  {menuOpenFor === p.projectId && (
                    <>
                      {/* click-away catcher */}
                      <div className="fixed inset-0 z-10" onClick={() => setMenuOpenFor(null)} />
                      <div className="panel absolute right-2 top-full z-20 mt-1 flex flex-col overflow-hidden py-1">
                        <button
                          onClick={() => {
                            setRenamingId(p.projectId);
                            setRenameValue(p.name);
                            setMenuOpenFor(null);
                          }}
                          className="px-3 py-1.5 text-left text-xs text-ink hover:bg-surface-sunken"
                        >
                          {t("switcher.rename")}
                        </button>
                        <button
                          onClick={() => {
                            setDeleteTarget(p);
                            setMenuOpenFor(null);
                          }}
                          className="px-3 py-1.5 text-left text-xs text-state-risk hover:bg-surface-sunken"
                        >
                          {t("switcher.delete")}
                        </button>
                      </div>
                    </>
                  )}
                </>
              )}
            </li>
          ))}
          </ul>
        </>
      )}

      {showBatchDeleteConfirm && (
        <div className="fixed inset-0 z-30 flex items-center justify-center bg-black/40 p-4">
          <div className="panel w-full max-w-sm p-4">
            <p className="text-sm font-medium text-ink">{t("switcher.batchDeleteConfirmTitle")}</p>
            <p className="mt-1 text-xs text-ink-muted">
              {(projectsQuery.data ?? [])
                .filter((p) => selectedIds.has(p.projectId))
                .slice(0, 5)
                .map((p) => p.name)
                .join("、")}
              {selectedIds.size > 5 ? ` ${t("switcher.batchDeleteAndMore").replace("{count}", String(selectedIds.size - 5))}` : ""}
            </p>
            <p className="mt-2 text-xs text-ink-muted">{t("switcher.batchDeleteConfirmDetail")}</p>
            {batchDeleteMutation.isError && <p className="mt-2 text-xs text-state-risk">{String(batchDeleteMutation.error)}</p>}
            <div className="mt-3 flex justify-end gap-2">
              <button
                onClick={() => setShowBatchDeleteConfirm(false)}
                disabled={batchDeleteMutation.isPending}
                className="rounded px-3 py-1.5 text-xs text-ink-muted"
              >
                {t("switcher.cancel")}
              </button>
              <button
                onClick={() => batchDeleteMutation.mutate([...selectedIds])}
                disabled={batchDeleteMutation.isPending}
                className="rounded bg-state-risk px-3 py-1.5 text-xs font-medium text-white disabled:opacity-40"
              >
                {batchDeleteMutation.isPending ? t("switcher.deleting") : t("switcher.batchDelete")}
              </button>
            </div>
          </div>
        </div>
      )}

      {deleteTarget && (
        <div className="fixed inset-0 z-30 flex items-center justify-center bg-black/40 p-4">
          <div className="panel w-full max-w-sm p-4">
            <p className="text-sm font-medium text-ink">{t("switcher.deleteConfirmTitle")}</p>
            <p className="mt-1 text-xs text-ink-muted">{deleteTarget.name}</p>
            <p className="mt-2 text-xs text-ink-muted">{t("switcher.deleteConfirmDetail")}</p>
            {deleteMutation.isError && <p className="mt-2 text-xs text-state-risk">{String(deleteMutation.error)}</p>}
            <div className="mt-3 flex justify-end gap-2">
              <button
                onClick={() => setDeleteTarget(null)}
                disabled={deleteMutation.isPending}
                className="rounded px-3 py-1.5 text-xs text-ink-muted"
              >
                {t("switcher.cancel")}
              </button>
              <button
                onClick={() => deleteMutation.mutate(deleteTarget.projectId)}
                disabled={deleteMutation.isPending}
                className="rounded bg-state-risk px-3 py-1.5 text-xs font-medium text-white disabled:opacity-40"
              >
                {deleteMutation.isPending ? t("switcher.deleting") : t("switcher.delete")}
              </button>
            </div>
          </div>
        </div>
      )}

      {connected && (
        <div className="panel p-3">
          {!showCreate ? (
            <button
              onClick={() => setShowCreate(true)}
              className="flex items-center gap-1.5 text-sm font-medium text-accent-strong"
            >
              <Plus size={14} /> {t("switcher.newProject")}
            </button>
          ) : (
            <div className="flex flex-col gap-2">
              <input
                className="rounded border border-border px-2 py-1.5 text-sm"
                placeholder={t("switcher.projectName")}
                value={name}
                onChange={(e) => setName(e.target.value)}
              />
              <input
                className="rounded border border-border px-2 py-1.5 text-sm"
                placeholder={t("switcher.targetProduct")}
                value={targetProduct}
                onChange={(e) => setTargetProduct(e.target.value)}
              />
              <div className="flex gap-2">
                <button
                  disabled={!name || !targetProduct || createMutation.isPending}
                  onClick={() => createMutation.mutate()}
                  className="rounded bg-accent px-3 py-1.5 text-xs font-medium text-white disabled:opacity-40"
                >
                  {createMutation.isPending ? t("switcher.creating") : t("switcher.createProject")}
                </button>
                <button onClick={() => setShowCreate(false)} className="rounded px-3 py-1.5 text-xs text-ink-muted">
                  {t("switcher.cancel")}
                </button>
              </div>
              {createMutation.isError && <p className="text-xs text-state-risk">{String(createMutation.error)}</p>}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
