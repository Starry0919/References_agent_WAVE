import { useEffect, useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, useNavigate, useParams, useSearchParams } from "react-router-dom";
import {
  AlertTriangle, ArrowLeft, ArrowRight, Check, Circle, Database, FlaskConical,
  GitBranch, LoaderCircle, Play, RefreshCw, ShieldCheck,
} from "lucide-react";
import {
  getSession, listDecisions, listEvidence, listEvidenceItems, listHypotheses,
  listModelCapabilities, listTests, type EvidenceItemRow, type EvidenceLinkRow, type HypothesisRow,
} from "@/api/diagnosis";
import { createHandoff } from "@/api/engineeringDesign";
import { listProjectObservations } from "@/api/experiments";
import { createRun, getRun, startDiagnosis, type WorkflowRun } from "@/api/orchestrator";
import { getProject } from "@/api/projects";
import { EmptyState } from "@/components/common/EmptyState";
import { StatusBadge, type BadgeStatus } from "@/components/common/StatusBadge";

const OBJECTIVES = [
  ["increase_production", "Increase production / titer"],
  ["increase_yield", "Increase yield"],
  ["reduce_byproduct", "Reduce by-product formation"],
  ["balance_growth", "Balance growth and production"],
  ["explain_phenotype", "Explain an unexpected phenotype"],
] as const;

const SCOPES = [
  ["pathway", "Pathway feasibility", ["pathway", "通路"]],
  ["precursor", "Precursor and cofactor supply", ["precursor", "cofactor", "redox", "pep", "e4p"]],
  ["regulation", "Regulation and enzyme constraints", ["feedback", "regulat", "enzyme", "inhibition"]],
  ["competition", "Competing flux and by-products", ["competing", "by-product", "carbon flux"]],
  ["toxicity", "Toxicity and growth burden", ["toxic", "growth", "burden"]],
  ["process", "Process and culture conditions", ["process", "fermentation", "culture", "condition"]],
] as const;

const DATA_FIELDS = [
  ["hasBaseline", "Baseline or comparator"], ["hasGenotype", "Genotype / chassis"],
  ["hasCondition", "Culture condition"], ["hasTime", "Time-point context"],
  ["hasQc", "QC status"], ["hasKeyPhenotype", "Key phenotype measurement"],
] as const;

type DataKey = typeof DATA_FIELDS[number][0];
type ScopeKey = typeof SCOPES[number][0];

function hostLabel(host: Record<string, unknown>) {
  return [host.species, host.strain].filter(Boolean).map(String).join(" · ") || "Not specified";
}

function evidenceLabel(item?: EvidenceItemRow) {
  if (!item) return "UNRESOLVED";
  if (item.sourceType === "experiment") return "MEASURED";
  if (item.sourceType === "model_run") return "MODEL COMPUTED";
  if (item.sourceType === "literature") return "LITERATURE REPORTED";
  if (item.sourceType === "expert_rule") return "RULE TRANSFER";
  return "DATABASE FACT";
}

export function RunNewDiagnosisPage() {
  const { projectId = "" } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const queryClient = useQueryClient();
  const project = useQuery({ queryKey: ["project", projectId], queryFn: () => getProject(projectId), enabled: !!projectId });
  const evidenceInventory = useQuery({ queryKey: ["diagnosis-evidence-items", projectId], queryFn: () => listEvidenceItems(projectId), enabled: !!projectId });
  const capabilities = useQuery({ queryKey: ["diagnosis-model-capabilities"], queryFn: listModelCapabilities });
  const projectObservations = useQuery({ queryKey: ["project-observations", projectId], queryFn: () => listProjectObservations(projectId), enabled: !!projectId });

  const [objectiveType, setObjectiveType] = useState("increase_production");
  const [question, setQuestion] = useState("");
  const [carbonSource, setCarbonSource] = useState("");
  const [knownMutations, setKnownMutations] = useState("");
  const [constraints, setConstraints] = useState("");
  const [observations, setObservations] = useState("");
  const [subjectObservationId, setSubjectObservationId] = useState("");
  const [baselineObservationId, setBaselineObservationId] = useState("");
  const [data, setData] = useState<Record<DataKey, boolean>>({ hasBaseline: false, hasGenotype: false, hasCondition: false, hasTime: false, hasQc: false, hasKeyPhenotype: false });
  const [scopes, setScopes] = useState<Record<ScopeKey, boolean>>({ pathway: true, precursor: true, regulation: true, competition: true, toxicity: true, process: true });
  const [workflow, setWorkflow] = useState<WorkflowRun | null>(null);
  const [requestStage, setRequestStage] = useState<"idle" | "creating" | "diagnosing">("idle");
  const savedRunId = searchParams.get("run") || "";
  const savedRun = useQuery({ queryKey: ["workflow-run", savedRunId], queryFn: () => getRun(savedRunId), enabled: !!savedRunId });

  useEffect(() => {
    if (project.data && Object.values(project.data.hostDefinition).some(Boolean)) {
      setData((current) => current.hasGenotype ? current : { ...current, hasGenotype: true });
    }
  }, [project.data]);

  useEffect(() => {
    if (savedRun.data?.projectId === projectId) setWorkflow(savedRun.data);
  }, [savedRun.data, projectId]);

  const diagnosisId = workflow?.diagnosisRunRef || "";
  const session = useQuery({ queryKey: ["diagnosis-session", diagnosisId], queryFn: () => getSession(diagnosisId), enabled: !!diagnosisId });
  const hypotheses = useQuery({ queryKey: ["diagnosis-hypotheses", diagnosisId], queryFn: () => listHypotheses(diagnosisId), enabled: !!diagnosisId });
  const evidence = useQuery({ queryKey: ["diagnosis-evidence", diagnosisId], queryFn: () => listEvidence(diagnosisId), enabled: !!diagnosisId });
  const decisions = useQuery({ queryKey: ["diagnosis-decisions", diagnosisId], queryFn: () => listDecisions(diagnosisId), enabled: !!diagnosisId });
  const tests = useQuery({ queryKey: ["diagnosis-tests", diagnosisId], queryFn: () => listTests(diagnosisId), enabled: !!diagnosisId });

  const run = useMutation({
    mutationFn: async () => {
      if (!project.data) throw new Error("Project context is unavailable.");
      const host = hostLabel(project.data.hostDefinition);
      setRequestStage("creating");
      const created = await createRun({ projectId, actorId: "frontend-user", targetProduct: project.data.targetProduct, host });
      setWorkflow(created);
      setSearchParams({ run: created.workflowRunId }, { replace: true });
      setRequestStage("diagnosing");
      const completed = await startDiagnosis(created.workflowRunId, {
        expectedVersion: created.version, actorId: "frontend-user", biologicalSystem: {
          ...project.data.hostDefinition,
          ...(carbonSource.trim() ? { carbon_source: carbonSource.trim() } : {}),
          ...(knownMutations.trim() ? { known_mutations: knownMutations.trim() } : {}),
        },
        phenotype: question.trim(), targetProduct: project.data.targetProduct, host,
        observationIds: [subjectObservationId], baselineObservationIds: [baselineObservationId],
        dataSufficiency: data,
        context: {
          objective_type: objectiveType,
          requested_diagnostic_scopes: Object.entries(scopes).filter(([, enabled]) => enabled).map(([scope]) => scope),
          observations: observations.trim() || null,
          user_constraints: constraints.trim() || null,
          source: "run_new_diagnose",
        },
      });
      setWorkflow(completed);
      setSearchParams({ run: completed.workflowRunId }, { replace: true });
      return completed;
    },
    onSuccess: (result) => {
      setRequestStage("idle");
      queryClient.invalidateQueries({ queryKey: ["diagnosis-sessions", projectId] });
      if (result.diagnosisRunRef) {
        for (const key of ["diagnosis-session", "diagnosis-hypotheses", "diagnosis-evidence", "diagnosis-decisions", "diagnosis-tests"]) {
          queryClient.invalidateQueries({ queryKey: [key, result.diagnosisRunRef] });
        }
      }
    },
    onError: () => setRequestStage("idle"),
  });

  const decision = decisions.data?.at(-1);
  const itemById = useMemo(() => new Map((evidenceInventory.data ?? []).map((item) => [item.evidenceItemId, item])), [evidenceInventory.data]);
  const linksByHyp = new Map<string, EvidenceLinkRow[]>();
  for (const link of evidence.data ?? []) linksByHyp.set(link.hypothesisVersionId, [...(linksByHyp.get(link.hypothesisVersionId) ?? []), link]);
  const ranked = useMemo(() => [...(hypotheses.data ?? [])].sort((a, b) => Number(decision?.leadingHypothesisIds.includes(b.hypothesisVersionId)) - Number(decision?.leadingHypothesisIds.includes(a.hypothesisVersionId))), [hypotheses.data, decision]);
  const completed = !!decision && ["actionable", "handoff_ready", "handed_off_to_design"].includes(session.data?.status ?? "");
  const partial = !!diagnosisId && !run.isPending && !completed;
  const pageStatus: { status: BadgeStatus; label: string } = run.isError ? { status: "failed", label: "FAILED" } : run.isPending ? { status: "active", label: "RUNNING" } : completed ? { status: "approved", label: "COMPLETED" } : partial ? { status: "partial", label: "PARTIAL" } : { status: "not_started", label: "READY" };

  const handoff = useMutation({
    mutationFn: () => createHandoff({ diagnosisDecisionId: decision!.decisionId, actorId: "frontend-user", chassis: hostLabel(project.data?.hostDefinition ?? {}), chassisVersionOrGenotype: String(project.data?.hostDefinition.strain ?? "unknown") }),
    onSuccess: (result) => navigate(`/projects/${projectId}/design?design=${encodeURIComponent(result.project.designProjectId)}`),
  });

  if (project.isLoading) return <div className="p-6"><EmptyState variant="loading" /></div>;
  if (project.isError || !project.data) return <div className="p-6"><EmptyState variant="failed" detail={String(project.error ?? "Project context unavailable")} /></div>;
  const host = hostLabel(project.data.hostDefinition);
  const availableModels = Object.values(capabilities.data ?? {}).filter((x) => x.available).length;
  const missing = DATA_FIELDS.filter(([key]) => !data[key]).map(([, label]) => label);
  const selectedSubject = projectObservations.data?.find((o) => o.observationId === subjectObservationId);
  const compatibleBaselines = (projectObservations.data ?? []).filter((o) =>
    o.observationId !== subjectObservationId
    && (!selectedSubject || (o.metric === selectedSubject.metric && o.unit === selectedSubject.unit
      && JSON.stringify(o.conditionRef) === JSON.stringify(selectedSubject.conditionRef)))
  );
  const groundingReady = !!subjectObservationId && !!baselineObservationId;

  return (
    <main className="min-h-0 flex-1 overflow-y-auto bg-surface-sunken p-4 lg:p-6">
      <div className="mx-auto flex max-w-7xl flex-col gap-5">
        <header className="rounded-lg bg-[#162235] p-5 text-white shadow-sm">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div><Link to={`/projects/${projectId}/diagnosis`} className="mb-3 inline-flex items-center gap-1 text-xs text-blue-200 hover:text-white"><ArrowLeft size={13}/> Diagnosis workspace</Link><p className="text-[11px] font-semibold uppercase tracking-[.18em] text-blue-200">Scientific diagnosis run</p><h1 className="mt-1 text-2xl font-semibold">Run New Diagnosis</h1><p className="mt-2 max-w-3xl text-sm text-slate-300">Frame the biological problem, attest available evidence, and run the governed diagnosis pipeline.</p></div>
            <StatusBadge status={pageStatus.status} label={pageStatus.label}/>
          </div>
          <div className="mt-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-4"><Context label="Host" value={host}/><Context label="Target product" value={project.data.targetProduct || "Not specified"}/><Context label="Project stage" value={project.data.lifecycleStage}/><Context label="Run ID" value={workflow?.workflowRunId || "Not created"}/></div>
        </header>

        <section className="grid gap-5 lg:grid-cols-[1.05fr_.95fr]">
          <div className="panel p-5">
            <SectionTitle index="01" title="Scientific objective" subtitle="Describe the observed engineering problem; do not enter the desired result as if it were measured."/>
            <label className="mt-4 block text-xs font-semibold">Objective type<select disabled={run.isPending} value={objectiveType} onChange={(e) => setObjectiveType(e.target.value)} className="mt-1 w-full rounded border border-border bg-surface px-3 py-2 text-sm">{OBJECTIVES.map(([value,label]) => <option key={value} value={value}>{label}</option>)}</select></label>
            <label className="mt-3 block text-xs font-semibold">Diagnostic question or observed phenotype<textarea disabled={run.isPending} value={question} onChange={(e) => setQuestion(e.target.value)} rows={4} placeholder={`Example: Under [recorded condition], ${project.data.targetProduct || "target product"} titer remains below [measured baseline].`} className="mt-1 w-full rounded border border-border bg-surface px-3 py-2 text-sm"/></label>
            <p className="mt-2 text-[11px] text-text-muted">Required. Use measured language where possible and keep unknown values explicit.</p>
          </div>

          <div className="panel p-5">
            <SectionTitle index="02" title="System context" subtitle="Project facts are read-only; optional fields are recorded as user-provided context."/>
            <div className="mt-4 grid gap-3 sm:grid-cols-2"><ReadOnly label="Host / strain" value={host}/><ReadOnly label="Target product" value={project.data.targetProduct || "Not specified"}/><Field label="Carbon source" value={carbonSource} onChange={setCarbonSource} disabled={run.isPending} placeholder="Not specified"/><Field label="Known mutations" value={knownMutations} onChange={setKnownMutations} disabled={run.isPending} placeholder="None recorded"/></div>
            <label className="mt-3 block text-xs font-semibold">Constraints<input disabled={run.isPending} value={constraints} onChange={(e) => setConstraints(e.target.value)} placeholder={project.data.constraints.join("; ") || "No additional constraints"} className="mt-1 w-full rounded border border-border bg-surface px-3 py-2 text-sm"/></label>
            <label className="mt-3 block text-xs font-semibold">Additional observations<input disabled={run.isPending} value={observations} onChange={(e) => setObservations(e.target.value)} placeholder="Optional; distinguish observations from interpretations" className="mt-1 w-full rounded border border-border bg-surface px-3 py-2 text-sm"/></label>
            <div className="mt-4 grid gap-3 sm:grid-cols-2">
              <ObservationSelect label="Subject measurement" value={subjectObservationId} observations={projectObservations.data ?? []} disabled={run.isPending} onChange={(value) => { setSubjectObservationId(value); setBaselineObservationId(""); }}/>
              <ObservationSelect label="Matched baseline" value={baselineObservationId} observations={compatibleBaselines} disabled={run.isPending || !subjectObservationId} onChange={setBaselineObservationId}/>
            </div>
            {!projectObservations.isLoading && (projectObservations.data?.length ?? 0) === 0 && <p className="mt-2 text-[11px] text-amber-800">No persisted project observations are available. Ingest and QC measurements before automatic diagnosis.</p>}
          </div>
        </section>

        <section className="grid gap-5 lg:grid-cols-[1.05fr_.95fr]">
          <div className="panel p-5"><SectionTitle index="03" title="Data sufficiency gate" subtitle="Check only data that actually exists and has been reviewed. Missing items cause a real, resumable data-required checkpoint."/><div className="mt-4 grid gap-2 sm:grid-cols-2">{DATA_FIELDS.map(([key,label]) => <CheckRow key={key} checked={data[key]} label={label} disabled={run.isPending} onChange={(checked) => setData((old) => ({ ...old, [key]: checked }))}/>)}</div>{missing.length || !groundingReady ? <div className="mt-3 flex gap-2 rounded border border-amber-300 bg-amber-50 p-3 text-xs text-amber-900"><AlertTriangle size={16} className="shrink-0"/><span>{missing.length ? `Current declaration is incomplete: ${missing.join(", ")}. ` : ""}{!groundingReady ? "Select a persisted subject measurement and matched baseline. " : ""}The backend will stop at a partial/data-required state until both declarations and linked records are complete.</span></div> : <div className="mt-3 flex gap-2 rounded border border-emerald-200 bg-emerald-50 p-3 text-xs text-emerald-900"><ShieldCheck size={16}/>All required categories and persisted measurement links are present.</div>}</div>
          <div className="panel p-5"><SectionTitle index="04" title="Requested diagnostic scope" subtitle="Scope is recorded as intent. Completion is reported only when persisted outputs support it."/><div className="mt-4 grid gap-2">{SCOPES.map(([key,label]) => <CheckRow key={key} checked={scopes[key]} label={label} disabled={run.isPending} onChange={(checked) => setScopes((old) => ({ ...old, [key]: checked }))}/>)}</div></div>
        </section>

        <section className="panel p-5"><SectionTitle index="05" title="Evidence and capability inventory" subtitle="Live counts from project evidence records and runtime capability detection."/><div className="mt-4 grid gap-3 sm:grid-cols-3"><Metric icon={Database} label="Evidence items" value={String(evidenceInventory.data?.length ?? 0)}/><Metric icon={FlaskConical} label="Available model adapters" value={`${availableModels} / ${Object.keys(capabilities.data ?? {}).length}`}/><Metric icon={GitBranch} label="Persisted diagnosis links" value={diagnosisId ? String(evidence.data?.length ?? 0) : "Not run"}/></div><p className="mt-3 text-[11px] text-text-muted">Availability does not mean a model was executed. This run invokes only capabilities wired into the existing diagnosis adapter.</p></section>

        <section className="panel p-5">
          <div className="flex flex-wrap items-center justify-between gap-3"><SectionTitle index="06" title="Execute and monitor" subtitle="Structured pipeline status; no hidden reasoning trace is shown."/><button disabled={!question.trim() || !groundingReady || run.isPending} onClick={() => run.mutate()} className="inline-flex items-center gap-2 rounded bg-accent px-4 py-2 text-xs font-semibold text-white disabled:cursor-not-allowed disabled:opacity-50">{run.isPending ? <LoaderCircle size={15} className="animate-spin"/> : run.isError ? <RefreshCw size={15}/> : <Play size={15}/>} {run.isPending ? "Diagnosis running…" : run.isError ? "Retry with current configuration" : "Start diagnosis"}</button></div>
          {run.isError && <div className="mt-4 rounded border border-red-200 bg-red-50 p-3 text-sm text-red-800">{run.error instanceof Error ? run.error.message : String(run.error)}</div>}
          <div className="mt-5 grid gap-2 md:grid-cols-4"><PipelineStep label="Goal framing" state={workflow ? "done" : requestStage === "creating" ? "running" : "idle"}/><PipelineStep label="Project context & data gate" state={run.isPending ? "running" : diagnosisId ? "done" : "idle"}/><PipelineStep label="Diagnosis service" state={requestStage === "diagnosing" ? "running" : diagnosisId ? (partial ? "partial" : "done") : "idle"}/><PipelineStep label="Decision integration" state={completed ? "done" : partial ? "partial" : "idle"}/></div>
          {partial && <div className="mt-4 rounded border border-amber-300 bg-amber-50 p-4"><p className="text-sm font-semibold text-amber-950">The run stopped at a legitimate checkpoint.</p><p className="mt-1 text-xs text-amber-900">Session status: <span className="font-mono">{session.data?.status ?? workflow?.blockedReason ?? "partial"}</span>. Add the missing data in the operational diagnosis record before interpreting mechanisms as ranked findings.</p><Link to={`/projects/${projectId}/diagnosis/${diagnosisId}`} className="mt-2 inline-flex items-center gap-1 text-xs font-semibold text-amber-950 hover:underline">Open operational record <ArrowRight size={13}/></Link></div>}
        </section>

        {!!diagnosisId && <section className="panel p-5"><SectionTitle index="07" title="Module coverage" subtitle="A module is completed only when the persisted output text contains a matching scientific mechanism."/><div className="mt-4 grid gap-2 sm:grid-cols-2 lg:grid-cols-3">{SCOPES.map(([key,label,keywords]) => { const matches = scopes[key] && ranked.some((h) => keywords.some((word) => `${h.statement} ${h.mechanismClass}`.toLowerCase().includes(word))); return <div key={key} className="rounded border border-border bg-surface p-3"><p className="text-xs font-semibold">{label}</p><p className={`mt-2 text-[10px] font-bold tracking-wide ${matches ? "text-emerald-700" : "text-slate-500"}`}>{matches ? "OUTPUT FOUND" : scopes[key] ? "NOT EVALUATED" : "OUT OF SCOPE"}</p></div>; })}</div></section>}

        {(ranked.length > 0 || completed) && <section className="panel p-5"><SectionTitle index="08" title="Emerging findings and decision map" subtitle="Ranked persisted hypotheses with provenance, uncertainty, and falsification paths."/><div className="mt-4 grid gap-3 lg:grid-cols-2">{ranked.map((hypothesis, index) => <Finding key={hypothesis.hypothesisVersionId} hypothesis={hypothesis} rank={index + 1} leading={decision?.leadingHypothesisIds.includes(hypothesis.hypothesisVersionId) ?? false} links={linksByHyp.get(hypothesis.hypothesisVersionId) ?? []} itemById={itemById}/>)}</div><div className="mt-4 rounded border border-border bg-surface-sunken p-3 text-xs text-text-secondary">Discriminating tests persisted for this run: <strong>{tests.data?.length ?? 0}</strong>{(tests.data?.length ?? 0) === 0 ? ". No test execution should be inferred." : ". Open the operational record for readiness and information-gain details."}</div>{completed && <div className="mt-5 rounded border border-emerald-200 bg-emerald-50 p-4"><div className="flex flex-wrap items-start justify-between gap-3"><div><p className="text-sm font-semibold text-emerald-950">Actionable diagnosis decision recorded</p><p className="mt-1 text-xs text-emerald-900">Stopping reason: {decision?.stoppingReason}. “Actionable” means sufficient for the next governed step, not proof of a unique true cause.</p></div><StatusBadge status="approved" label="ACTIONABLE"/></div></div>}</section>}

        <footer className="panel flex flex-wrap items-center justify-between gap-3 p-4"><div><p className="text-sm font-semibold">Next governed action</p><p className="text-xs text-text-muted">Engineering Design handoff is available only from a persisted diagnosis decision.</p></div><div className="flex gap-2"><Link to={`/projects/${projectId}/diagnosis${diagnosisId ? `?session=${encodeURIComponent(diagnosisId)}` : ""}`} className="rounded border border-border px-3 py-2 text-xs font-semibold">Back to Diagnosis</Link><button disabled={!decision || handoff.isPending} onClick={() => handoff.mutate()} className="inline-flex items-center gap-2 rounded bg-[#162235] px-3 py-2 text-xs font-semibold text-white disabled:opacity-40">{handoff.isPending ? <LoaderCircle size={14} className="animate-spin"/> : <ArrowRight size={14}/>}Proceed to Engineering Design</button></div>{handoff.isError && <p className="w-full text-xs text-red-700">Handoff failed: {handoff.error instanceof Error ? handoff.error.message : String(handoff.error)}</p>}</footer>
      </div>
    </main>
  );
}

function SectionTitle({ index, title, subtitle }: { index: string; title: string; subtitle: string }) { return <div><p className="text-[10px] font-bold uppercase tracking-[.16em] text-accent-strong">{index}</p><h2 className="mt-1 text-base font-semibold text-text-primary">{title}</h2><p className="mt-1 text-xs text-text-muted">{subtitle}</p></div>; }
function Context({ label, value }: { label: string; value: string }) { return <div className="rounded border border-white/15 bg-white/5 px-3 py-2"><p className="text-[10px] uppercase tracking-wide text-slate-400">{label}</p><p className="mt-1 truncate text-xs font-semibold" title={value}>{value}</p></div>; }
function ReadOnly({ label, value }: { label: string; value: string }) { return <div><p className="text-xs font-semibold">{label}</p><div className="mt-1 rounded border border-border bg-surface-sunken px-3 py-2 text-sm text-text-secondary">{value}</div></div>; }
function Field({ label, value, onChange, disabled, placeholder }: { label: string; value: string; onChange: (value: string) => void; disabled: boolean; placeholder: string }) { return <label className="text-xs font-semibold">{label}<input disabled={disabled} value={value} onChange={(e) => onChange(e.target.value)} placeholder={placeholder} className="mt-1 w-full rounded border border-border bg-surface px-3 py-2 text-sm"/></label>; }
function ObservationSelect({ label, value, observations, disabled, onChange }: { label: string; value: string; observations: Array<{ observationId: string; metric: string; value: number; unit: string; qcStatus: string }>; disabled: boolean; onChange: (value: string) => void }) { return <label className="text-xs font-semibold">{label}<select disabled={disabled} value={value} onChange={(e) => onChange(e.target.value)} className="mt-1 w-full rounded border border-border bg-surface px-3 py-2 text-sm"><option value="">Select persisted observation</option>{observations.map((o) => <option key={o.observationId} value={o.observationId} disabled={o.qcStatus !== "passed"}>{o.metric}: {o.value} {o.unit} · QC {o.qcStatus}</option>)}</select></label>; }
function CheckRow({ checked, label, disabled, onChange }: { checked: boolean; label: string; disabled: boolean; onChange: (checked: boolean) => void }) { return <label className="flex cursor-pointer items-center gap-2 rounded border border-border bg-surface px-3 py-2 text-xs"><input type="checkbox" checked={checked} disabled={disabled} onChange={(e) => onChange(e.target.checked)} className="accent-blue-600"/><span>{label}</span></label>; }
function Metric({ icon: Icon, label, value }: { icon: typeof Database; label: string; value: string }) { return <div className="rounded border border-border bg-surface p-3"><Icon size={16} className="text-accent-strong"/><p className="mt-3 text-[10px] uppercase tracking-wide text-text-muted">{label}</p><p className="mt-1 text-lg font-semibold">{value}</p></div>; }
function PipelineStep({ label, state }: { label: string; state: "idle" | "running" | "done" | "partial" }) { const Icon = state === "done" ? Check : state === "running" ? LoaderCircle : state === "partial" ? AlertTriangle : Circle; return <div className={`flex items-center gap-2 rounded border p-3 ${state === "done" ? "border-emerald-200 bg-emerald-50" : state === "running" ? "border-blue-200 bg-blue-50" : state === "partial" ? "border-amber-200 bg-amber-50" : "border-border bg-surface"}`}><Icon size={15} className={state === "running" ? "animate-spin text-blue-700" : ""}/><div><p className="text-xs font-semibold">{label}</p><p className="text-[10px] uppercase text-text-muted">{state === "idle" ? "not started" : state}</p></div></div>; }
function Finding({ hypothesis, rank, leading, links, itemById }: { hypothesis: HypothesisRow; rank: number; leading: boolean; links: EvidenceLinkRow[]; itemById: Map<string, EvidenceItemRow> }) { return <article className="rounded border border-border bg-surface p-4"><div className="flex items-start justify-between gap-2"><div><p className="text-[10px] font-bold uppercase tracking-wide text-text-muted">Rank {rank} · {hypothesis.mechanismClass || "unclassified"}</p><h3 className="mt-2 text-sm font-semibold leading-6">{hypothesis.statement || "Statement unavailable"}</h3></div>{leading && <StatusBadge status="approved" label="LEADING"/>}</div><div className="mt-3 flex flex-wrap gap-1">{links.map((link) => { const item = itemById.get(link.evidenceItemId); return <span key={link.evidenceLinkId} title={`${item?.quality ?? "unknown"} / ${item?.directness ?? "unknown"}`} className="rounded bg-surface-sunken px-2 py-1 text-[9px] font-bold text-text-muted">{evidenceLabel(item)}</span>; })}{links.length === 0 && <span className="rounded bg-amber-50 px-2 py-1 text-[9px] font-bold text-amber-800">UNRESOLVED EVIDENCE</span>}</div><p className="mt-3 text-[11px] text-text-muted">Status: {hypothesis.status}. Contradictions: {hypothesis.contradictions.length || "none recorded"}.</p>{hypothesis.falsifiers.length > 0 && <details className="mt-2"><summary className="cursor-pointer text-[11px] font-semibold text-accent-strong">Falsification paths</summary><ul className="mt-2 list-disc space-y-1 pl-4 text-[11px] text-text-secondary">{hypothesis.falsifiers.map((x) => <li key={x}>{x}</li>)}</ul></details>}</article>; }
