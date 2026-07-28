import type { LucideIcon } from "lucide-react";
import { ArrowRight, BookOpen, BrainCircuit, Check, Dna, FlaskConical, Lightbulb, Pencil, Target, X } from "lucide-react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState, type ReactNode } from "react";
import { Link, useParams } from "react-router-dom";
import { listIdeas } from "@/api/ideas";
import { getProjectStatusView, getTimeline, updateProjectContext } from "@/api/projects";
import { EmptyState } from "@/components/common/EmptyState";
import { StatusBadge } from "@/components/common/StatusBadge";
import { useI18n } from "@/lib/i18n";
import { useBackendHealth } from "@/state/BackendHealth";
import { useProjectContext } from "@/state/useProjectContext";
import type { CycleState, ProjectDetail } from "@/types/domain";

/**
 * Focused project dashboard: objective first, then real idea/source counts
 * and current progress. Detailed execution, governance and provenance stay
 * out of this page.
 */
export function CommandCenterPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const { project, projectLoading, cycle } = useProjectContext();
  const { connected } = useBackendHealth();
  const { t } = useI18n();
  const enabled = Boolean(projectId && connected);

  const ideasQuery = useQuery({
    queryKey: ["project", projectId, "ideas"],
    queryFn: () => listIdeas(projectId as string),
    enabled,
  });
  const timelineQuery = useQuery({
    queryKey: ["project", projectId, "timeline"],
    queryFn: () => getTimeline(projectId as string),
    enabled,
  });
  const statusQuery = useQuery({
    queryKey: ["project", projectId, "status-view"],
    queryFn: () => getProjectStatusView(projectId as string),
    enabled,
  });

  if (!connected) return <div className="p-6"><EmptyState variant="disconnected" /></div>;
  if (projectLoading) return <div className="p-6"><EmptyState variant="loading" /></div>;
  if (!project) return <div className="p-6"><EmptyState variant="failed" title={t("page1.projectNotFound")} /></div>;

  const ideas = ideasQuery.data ?? [];
  const timeline = timelineQuery.data ?? [];
  const evidenceCount = new Set(
    timeline.filter((event) => /evidence|paper|literature/i.test(event.entityType)).map((event) => event.entityId),
  ).size;
  const biologicalKnowledgeCount = new Set(
    timeline.filter((event) => /knowledgeclaim|biological/i.test(event.entityType)).map((event) => event.entityId),
  ).size;
  const activeIdeas = ideas.filter((idea) => idea.status !== "dismissed");
  const designCount = new Set([
    ...activeIdeas.map((idea) => idea.linkedDesignProjectId).filter(Boolean),
    ...timeline.filter((event) => /design/i.test(event.entityType)).map((event) => event.entityId),
  ]).size;
  const objective = project.objectives.length > 0 ? project.objectives.join("；") : project.targetProduct;
  const host = [project.hostDefinition.species, project.hostDefinition.strain].filter(Boolean).join(" · ");
  const status = statusQuery.data;

  return (
    <main className="flex flex-1 flex-col gap-5 overflow-y-auto bg-surface-sunken p-5">
      <ProjectGoalCard project={project} cycle={cycle} />
      {false && project && (<div className="hidden">
      <section className="overflow-hidden rounded-xl border border-border bg-gradient-to-br from-slate-950 to-slate-800 p-6 text-white shadow-sm">
        <div className="flex flex-wrap items-start justify-between gap-5">
          <div className="max-w-4xl">
            <p className="mb-2 flex items-center gap-2 text-xs font-medium uppercase tracking-[0.18em] text-emerald-300">
              <Target size={14} /> {t("dashboard.projectGoal")}
            </p>
            <h1 className="text-2xl font-semibold tracking-tight">{objective}</h1>
            <p className="mt-3 text-sm text-slate-300">
              {project!.name} · {host || t("dashboard.hostMissing")}
              {project!.targetProduct && ` · ${t("dashboard.targetProduct")} ${project!.targetProduct}`}
            </p>
          </div>
          <div className="flex flex-col items-end gap-2">
            <StatusBadge status={cycle ? "active" : "not_started"} label={cycle?.currentState ?? t("dashboard.noCycle")} />
            <span className="text-xs text-slate-400">{project!.lifecycleStage}</span>
          </div>
        </div>
        {project!.constraints.length > 0 && (
          <div className="mt-5 flex flex-wrap gap-2">
            {project!.constraints.map((constraint) => (
              <span key={constraint} className="rounded-full border border-white/15 bg-white/10 px-3 py-1 text-xs text-slate-200">
                {constraint}
              </span>
            ))}
          </div>
        )}
      </section>
      </div>)}

      <section className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <MetricCard icon={Lightbulb} label={t("dashboard.totalIdeas")} value={activeIdeas.length} detail={t("dashboard.totalIdeasDetail")} tone="amber" />
        <MetricCard icon={BookOpen} label={t("dashboard.references")} value={evidenceCount} detail={t("dashboard.referencesDetail")} tone="blue" />
        <MetricCard icon={Dna} label={t("dashboard.biologicalKnowledge")} value={biologicalKnowledgeCount} detail={t("dashboard.biologicalKnowledgeDetail")} tone="emerald" />
        <MetricCard icon={FlaskConical} label={t("dashboard.designs")} value={designCount} detail={t("dashboard.designsDetail")} tone="violet" />
      </section>

      <div className="grid gap-4 xl:grid-cols-[minmax(0,1.7fr)_minmax(300px,1fr)]">
        <section className="panel overflow-hidden">
          <div className="flex items-center justify-between border-b border-border px-4 py-3">
            <div>
              <h2 className="text-sm font-semibold text-ink">{t("dashboard.ideaList")}</h2>
              <p className="mt-0.5 text-xs text-ink-muted">{t("dashboard.ideaListDetail")}</p>
            </div>
            <Link to={`/projects/${projectId}/ideas`} className="flex items-center gap-1 text-xs font-medium text-accent-strong">
              {t("dashboard.goToIdeaWorkspace")} <ArrowRight size={13} />
            </Link>
          </div>
          {ideasQuery.isLoading && <div className="p-5"><EmptyState variant="loading" /></div>}
          {!ideasQuery.isLoading && activeIdeas.length === 0 && (
            <div className="p-5"><EmptyState variant="first_use" title={t("dashboard.noIdeas")} detail={t("dashboard.noIdeasDetail")} /></div>
          )}
          {activeIdeas.length > 0 && (
            <div className="divide-y divide-border">
              {activeIdeas.slice(0, 8).map((idea, index) => (
                <article key={idea.ideaId} className="grid gap-3 px-4 py-3 md:grid-cols-[36px_minmax(0,1fr)_150px]">
                  <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-amber-50 text-xs font-semibold text-amber-700">{index + 1}</span>
                  <div className="min-w-0">
                    <h3 className="text-sm font-medium text-ink">{idea.freeText}</h3>
                    <p className="mt-1 text-xs text-ink-muted">
                      {[idea.targetGene, idea.modificationType, idea.rationale].filter(Boolean).join(" · ") || t("dashboard.ideaPendingDetail")}
                    </p>
                  </div>
                  <div className="flex items-center justify-between gap-2 md:justify-end">
                    <span className="rounded-full bg-surface-sunken px-2 py-1 text-[11px] text-ink-muted">{t("dashboard.sourceHuman")}</span>
                    <StatusBadge status={idea.status === "linked_to_design" ? "approved" : "draft"} label={idea.status} />
                  </div>
                </article>
              ))}
            </div>
          )}
        </section>

        <div className="flex flex-col gap-4">
          <section className="panel p-4">
            <h2 className="text-sm font-semibold text-ink">{t("dashboard.sourceDistribution")}</h2>
            <div className="mt-4 flex flex-col gap-4">
              <SourceBar icon={BookOpen} label={t("dashboard.sourceLiterature")} value={evidenceCount} total={Math.max(1, evidenceCount + biologicalKnowledgeCount + activeIdeas.length)} />
              <SourceBar icon={BrainCircuit} label={t("dashboard.sourceBiologyBooks")} value={biologicalKnowledgeCount} total={Math.max(1, evidenceCount + biologicalKnowledgeCount + activeIdeas.length)} />
              <SourceBar icon={Lightbulb} label={t("dashboard.sourceHuman")} value={activeIdeas.length} total={Math.max(1, evidenceCount + biologicalKnowledgeCount + activeIdeas.length)} />
            </div>
            <Link to={`/projects/${projectId}/knowledge`} className="mt-5 flex items-center gap-1 text-xs font-medium text-accent-strong">
              {t("dashboard.openKnowledge")} <ArrowRight size={13} />
            </Link>
          </section>

          <section className="panel p-4">
            <h2 className="text-sm font-semibold text-ink">{t("dashboard.currentProgress")}</h2>
            <dl className="mt-3 grid grid-cols-[110px_minmax(0,1fr)] gap-x-3 gap-y-2 text-xs">
              <dt className="text-ink-muted">{t("dashboard.activeCycle")}</dt>
              <dd className="font-medium text-ink">{cycle?.cycleStateId ?? t("dashboard.noCycle")}</dd>
              <dt className="text-ink-muted">{t("dashboard.activeDesign")}</dt>
              <dd className="font-medium text-ink">{status?.activeDesignVersion ?? t("dashboard.none")}</dd>
              <dt className="text-ink-muted">{t("dashboard.nextAction")}</dt>
              <dd className="font-medium text-ink">{status?.nextActions[0] ?? t("dashboard.none")}</dd>
              <dt className="text-ink-muted">{t("dashboard.blockers")}</dt>
              <dd className={status?.blockers.length ? "font-medium text-state-risk" : "font-medium text-state-success"}>
                {status?.blockers.length ?? 0}
              </dd>
            </dl>
          </section>
        </div>
      </div>
    </main>
  );
}

function ProjectGoalCard({ project, cycle }: { project: ProjectDetail; cycle: CycleState | null | undefined }) {
  const { t } = useI18n();
  const queryClient = useQueryClient();
  const [editing, setEditing] = useState(false);
  const [species, setSpecies] = useState(String(project.hostDefinition.species ?? "Escherichia coli"));
  const [strain, setStrain] = useState(String(project.hostDefinition.strain ?? "K-12"));
  const [description, setDescription] = useState(String(project.hostDefinition.description ?? ""));
  const [targetProduct, setTargetProduct] = useState(project.targetProduct);
  const [objectiveText, setObjectiveText] = useState(project.objectives.join("\n"));
  const [constraintText, setConstraintText] = useState(project.constraints.join("\n"));
  const objective = project.objectives.length > 0 ? project.objectives.join("；") : project.targetProduct;
  const effectiveSpecies = String(project.hostDefinition.species ?? "Escherichia coli");
  const effectiveStrain = String(project.hostDefinition.strain ?? "K-12");
  const isDefaultHost = project.hostDefinition.defaulted === true;
  const saveMutation = useMutation({
    mutationFn: () => updateProjectContext(project.projectId, {
      hostDefinition: { species: species.trim() || "Escherichia coli", strain: strain.trim() || "K-12", description: description.trim() },
      targetProduct: targetProduct.trim(),
      objectives: objectiveText.split("\n").map((value) => value.trim()).filter(Boolean),
      constraints: constraintText.split("\n").map((value) => value.trim()).filter(Boolean),
      expectedVersion: project.version,
    }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["project", project.projectId] });
      setEditing(false);
    },
  });

  return (
    <>
      <section className="flex-none overflow-visible rounded-2xl border border-slate-700 bg-gradient-to-br from-slate-950 via-slate-900 to-slate-800 text-white shadow-sm">
        <div className="grid items-stretch gap-6 p-6 lg:grid-cols-[minmax(0,1fr)_minmax(340px,420px)]">
          <div className="min-w-0">
            <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.18em] text-emerald-300">
              <Target size={15} /> {t("dashboard.projectGoal")}
            </div>
            <h1 className="mt-3 whitespace-normal break-words text-3xl font-semibold leading-tight tracking-tight">{objective}</h1>
            <p className="mt-2 text-sm text-slate-400">{project.name}</p>
            {project.constraints.length > 0 && (
              <div className="mt-5 flex flex-wrap gap-2">
                {project.constraints.map((constraint) => (
                  <span key={constraint} className="rounded-full border border-white/15 bg-white/10 px-3 py-1 text-xs text-slate-200">{constraint}</span>
                ))}
              </div>
            )}
          </div>
          <div className="h-full min-w-0 rounded-xl border border-white/10 bg-white/[0.06] p-4">
            <div className="flex items-center justify-between">
              <h2 className="flex items-center gap-2 text-sm font-semibold"><Dna size={15} className="text-emerald-300" /> {t("context.projectContext")}</h2>
              <button type="button" onClick={() => setEditing(true)} className="flex items-center gap-1 rounded-lg border border-white/15 px-2.5 py-1.5 text-xs text-slate-200 hover:bg-white/10">
                <Pencil size={12} /> {t("common.edit")}
              </button>
            </div>
            <dl className="mt-4 grid grid-cols-[76px_minmax(0,1fr)] gap-x-3 gap-y-3 text-xs">
              <dt className="text-slate-400">{t("design.chassis")}</dt>
              <dd className="font-medium">{effectiveSpecies} · {effectiveStrain}</dd>
              <dt className="text-slate-400">{t("dashboard.targetProduct")}</dt>
              <dd className="font-medium">{project.targetProduct || t("context.notFilled")}</dd>
              <dt className="text-slate-400">{t("context.currentStage")}</dt>
              <dd><StatusBadge status={cycle ? "active" : "not_started"} label={cycle?.currentState ?? t("context.notStartedYet")} /></dd>
            </dl>
            {isDefaultHost && <p className="mt-3 rounded-lg bg-amber-400/10 px-3 py-2 text-[11px] text-amber-200">{t("context.defaultHostNotice")}</p>}
          </div>
        </div>
      </section>

      {editing && (
        <div className="fixed inset-0 z-40 flex items-center justify-center bg-slate-950/60 p-4 backdrop-blur-sm">
          <div className="w-full max-w-2xl rounded-2xl border border-border bg-surface p-5 shadow-2xl">
            <div className="flex items-start justify-between">
              <div><h2 className="text-base font-semibold text-ink">{t("context.editModalTitle")}</h2><p className="mt-1 text-xs text-ink-muted">{t("context.editModalDetail")}</p></div>
              <button type="button" onClick={() => setEditing(false)} className="rounded p-1 text-ink-muted hover:bg-surface-sunken"><X size={16} /></button>
            </div>
            <div className="mt-5 grid gap-4 sm:grid-cols-2">
              <Field label={t("context.chassisSpecies")}><input value={species} onChange={(e) => setSpecies(e.target.value)} placeholder="Escherichia coli" className="w-full rounded-lg border border-border px-3 py-2 text-sm" /></Field>
              <Field label={t("context.strain")}><input value={strain} onChange={(e) => setStrain(e.target.value)} placeholder="K-12" className="w-full rounded-lg border border-border px-3 py-2 text-sm" /></Field>
              <Field label={t("dashboard.targetProduct")}><input value={targetProduct} onChange={(e) => setTargetProduct(e.target.value)} placeholder="L-tryptophan" className="w-full rounded-lg border border-border px-3 py-2 text-sm" /></Field>
              <Field label={t("context.chassisDescription")}><input value={description} onChange={(e) => setDescription(e.target.value)} placeholder={t("context.chassisDescriptionPlaceholder")} className="w-full rounded-lg border border-border px-3 py-2 text-sm" /></Field>
              <Field label={t("context.objectivesLabel")} wide><textarea rows={3} value={objectiveText} onChange={(e) => setObjectiveText(e.target.value)} className="w-full resize-y rounded-lg border border-border px-3 py-2 text-sm" /></Field>
              <Field label={t("context.constraintsLabel")} wide><textarea rows={3} value={constraintText} onChange={(e) => setConstraintText(e.target.value)} className="w-full resize-y rounded-lg border border-border px-3 py-2 text-sm" /></Field>
            </div>
            {saveMutation.isError && <p className="mt-3 text-xs text-state-risk">{String(saveMutation.error)}</p>}
            <div className="mt-5 flex justify-end gap-2">
              <button type="button" onClick={() => setEditing(false)} className="rounded-lg px-4 py-2 text-xs font-medium text-ink-muted">{t("common.cancel")}</button>
              <button type="button" onClick={() => saveMutation.mutate()} disabled={!targetProduct.trim() || saveMutation.isPending} className="flex items-center gap-1.5 rounded-lg bg-accent px-4 py-2 text-xs font-semibold text-white disabled:opacity-50">
                <Check size={14} /> {saveMutation.isPending ? t("common.saving") : t("context.saveButton")}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

function Field({ label, wide = false, children }: { label: string; wide?: boolean; children: ReactNode }) {
  return <label className={wide ? "sm:col-span-2" : ""}><span className="mb-1.5 block text-xs font-medium text-ink">{label}</span>{children}</label>;
}

const tones = {
  amber: "bg-amber-50 text-amber-700",
  blue: "bg-blue-50 text-blue-700",
  emerald: "bg-emerald-50 text-emerald-700",
  violet: "bg-violet-50 text-violet-700",
};

function MetricCard({ icon: Icon, label, value, detail, tone }: { icon: LucideIcon; label: string; value: number; detail: string; tone: keyof typeof tones }) {
  return (
    <article className="panel flex items-center gap-4 p-4">
      <span className={`flex h-10 w-10 items-center justify-center rounded-xl ${tones[tone]}`}><Icon size={19} /></span>
      <div>
        <p className="text-2xl font-semibold leading-none text-ink">{value}</p>
        <p className="mt-1.5 text-xs font-medium text-ink">{label}</p>
        <p className="mt-0.5 text-[11px] text-ink-faint">{detail}</p>
      </div>
    </article>
  );
}

function SourceBar({ icon: Icon, label, value, total }: { icon: LucideIcon; label: string; value: number; total: number }) {
  const percent = Math.round((value / total) * 100);
  return (
    <div>
      <div className="mb-1.5 flex items-center justify-between text-xs">
        <span className="flex items-center gap-2 font-medium text-ink"><Icon size={13} className="text-ink-muted" /> {label}</span>
        <span className="tabular-nums text-ink-muted">{value}</span>
      </div>
      <div className="h-1.5 overflow-hidden rounded-full bg-surface-sunken">
        <div className="h-full rounded-full bg-accent transition-[width]" style={{ width: `${percent}%` }} />
      </div>
    </div>
  );
}
