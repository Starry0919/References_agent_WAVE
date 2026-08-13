import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Link, useParams, useSearchParams } from "react-router-dom";
import { ArrowRight, Ban, Boxes, ChevronDown, FlaskConical, GitMerge, Scale, ShieldCheck, SlidersHorizontal } from "lucide-react";
import { listHypotheses } from "@/api/diagnosis";
import {
  getProject as getDesignProject, listCandidates, listHandoffs, listProjectEvaluations, listStrategies,
  type CandidateDesign, type CandidateEvaluation, type Strategy,
} from "@/api/engineeringDesign";
import { listDesignProjectsForProject } from "@/api/evaluationMetrics";
import { getProject } from "@/api/projects";
import { EmptyState } from "@/components/common/EmptyState";
import { StatusBadge, type BadgeStatus } from "@/components/common/StatusBadge";
import { designStatusToBadge, candidateStatusToBadge } from "@/lib/workflowStatus";

type LoadedDesign = {
  project: Awaited<ReturnType<typeof getDesignProject>>;
  handoffs: Awaited<ReturnType<typeof listHandoffs>>;
  strategies: Strategy[];
  candidates: CandidateDesign[];
  evaluations: Record<string, CandidateEvaluation | null>;
};

function readable(value: unknown): string {
  if (value == null) return "Not recorded";
  if (typeof value === "string") return value;
  if (Array.isArray(value)) return value.map(readable).join("; ");
  if (typeof value === "object") return Object.entries(value as Record<string, unknown>).map(([k,v]) => `${k}: ${readable(v)}`).join("; ");
  return String(value);
}

function gateStatus(ev: CandidateEvaluation | null | undefined): {status: BadgeStatus; label: string} {
  if (!ev) return { status: "not_started", label: "PENDING EVALUATION" };
  if (ev.recommendation === "reject" || ev.recommendation === "rejected") return { status: "rejected", label: "FAILED GATE" };
  if (ev.requiredRevisions.length) return { status: "needs_revision", label: "REVISION REQUIRED" };
  return { status: "approved", label: ev.recommendation.toUpperCase() };
}

export function DesignWorkbenchPage() {
  const { projectId = "" } = useParams<{ projectId: string }>();
  const [params, setParams] = useSearchParams();
  const [openCandidate, setOpenCandidate] = useState<string | null>(null);
  const project = useQuery({ queryKey: ["project", projectId], queryFn: () => getProject(projectId), enabled: !!projectId });
  const summaries = useQuery({ queryKey: ["design-projects", projectId], queryFn: () => listDesignProjectsForProject(projectId), enabled: !!projectId });
  const designId = params.get("design") || summaries.data?.[0]?.designProjectId || "";
  const design = useQuery<LoadedDesign>({
    queryKey: ["design-workbench", designId], enabled: !!designId,
    queryFn: async () => {
      const [p, handoffs, strategies, candidates, evaluations] = await Promise.all([getDesignProject(designId), listHandoffs(designId), listStrategies(designId), listCandidates(designId), listProjectEvaluations(designId)]);
      return { project: p, handoffs, strategies, candidates, evaluations };
    },
  });
  const diagnosisSessionId = design.data?.project.diagnosisSessionId || "";
  const hypotheses = useQuery({ queryKey: ["diagnosis-hypotheses", diagnosisSessionId], queryFn: () => listHypotheses(diagnosisSessionId), enabled: !!diagnosisSessionId });
  const hypById = useMemo(() => new Map((hypotheses.data ?? []).map((h) => [h.hypothesisVersionId, h.statement || h.hypothesisVersionId])), [hypotheses.data]);

  if (project.isLoading || summaries.isLoading) return <div className="p-6"><EmptyState variant="loading" /></div>;
  if (project.isError || summaries.isError) return <div className="p-6"><EmptyState variant="failed" detail={String(project.error ?? summaries.error)} /></div>;
  if (!project.data) return <div className="p-6"><EmptyState variant="unavailable" title="Project context unavailable" /></div>;
  if ((summaries.data?.length ?? 0) === 0) return <main className="min-h-0 flex-1 overflow-y-auto p-6"><div className="mx-auto max-w-5xl"><EmptyState variant="first_use" title="No engineering design exists" detail="A gated diagnosis decision is required before design generation." action={<Link className="rounded bg-accent px-3 py-2 text-xs font-semibold text-white" to={`/projects/${projectId}/diagnosis`}>Open Diagnosis</Link>}/></div></main>;
  if (design.isLoading || !design.data) return <div className="p-6"><EmptyState variant={design.isError ? "failed" : "loading"} detail={design.isError ? String(design.error) : undefined}/></div>;

  const d = design.data;
  const handoff = d.handoffs[0];
  const selected = d.candidates.filter((c) => ["selected","approved_for_build","built","tested"].includes(c.status));
  const rejected = d.candidates.filter((c) => c.status === "rejected");
  const excluded = d.strategies.flatMap((s) => (s.excludedStrategyReasons ?? []).map((x) => ({ strategy: s, reason: x })));
  const evaluated = Object.values(d.evaluations).filter(Boolean).length;
  const host = [project.data.hostDefinition.species, project.data.hostDefinition.strain].filter(Boolean).join(" · ") || "Not specified";

  return <main className="min-h-0 flex-1 overflow-y-auto bg-surface-sunken p-4 lg:p-6"><div className="mx-auto flex max-w-7xl flex-col gap-5">
    <header className="rounded-lg bg-[#162235] p-5 text-white shadow-sm">
      <div className="flex flex-wrap items-start justify-between gap-4"><div><p className="text-[11px] font-semibold uppercase tracking-[.18em] text-blue-200">Evidence-grounded engineering decision chain</p><h1 className="mt-1 text-2xl font-semibold">Engineering Design Workspace</h1><p className="mt-2 max-w-3xl text-sm text-slate-300">Which interventions address the current diagnosis, why should they survive evaluation, and how will they be tested?</p></div><Link to={`/projects/${projectId}/design/${designId}`} className="rounded border border-white/20 bg-white/10 px-3 py-2 text-xs font-semibold">Open operational record →</Link></div>
      <div className="mt-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-5"><Context label="Host" value={host}/><Context label="Substrate" value="Not specified" warn/><Context label="Target" value={project.data.targetProduct}/><Context label="Optimization" value={readable(d.project.primaryMetrics)}/><Context label="Evaluation" value={`${evaluated}/${d.candidates.length} candidates`}/></div>
    </header>

    <section className="panel flex flex-wrap items-center justify-between gap-3 p-3"><div className="flex items-center gap-2"><SlidersHorizontal size={16} className="text-accent"/><span className="text-xs font-semibold">Design version</span><select value={designId} onChange={(e)=>{params.set("design",e.target.value);setParams(params)}} className="rounded border border-border px-2 py-1 font-mono text-xs">{summaries.data?.map((x)=><option key={x.designProjectId} value={x.designProjectId}>{x.designProjectId}</option>)}</select></div><div className="flex items-center gap-2"><StatusBadge status={designStatusToBadge(d.project.status)} label={d.project.status}/><StatusBadge status={handoff?.isStale?"stale":"approved"} label={handoff?.isStale?"STALE HANDOFF":`DIAGNOSIS v${d.project.diagnosisVersion}`}/></div></section>

    <section className="panel p-4"><Title icon={GitMerge} eyebrow="Diagnosis → intervention trace" title="Design remains anchored to the gated problem map"/><div className="mt-4 grid gap-3 lg:grid-cols-[1fr_auto_1fr_auto_1fr]">
      <TraceBox title="Supported diagnoses" items={(handoff?.supportedHypotheses ?? []).map((id)=>hypById.get(String(id))||String(id))}/><Arrow/><TraceBox title="Strategy space" items={d.strategies.map((s)=>`${s.strategyClass}: ${s.mechanismTarget}`)}/><Arrow/><TraceBox title="Candidate portfolio" items={d.candidates.map((c)=>`${c.portfolioRole}: ${c.expectedMechanism}`)}/>
    </div>{(handoff?.unresolvedAlternatives.length ?? 0)>0&&<div className="mt-3 rounded border border-amber-200 bg-amber-50 p-3 text-xs text-amber-900"><b>Unresolved diagnosis alternatives:</b> {handoff?.unresolvedAlternatives.map((id)=>hypById.get(String(id))||String(id)).join("; ")}. The information-gain candidate exists to discriminate these, not to claim production benefit.</div>}</section>

    <section className="panel overflow-hidden"><div className="p-4"><Title icon={Scale} eyebrow="Candidate comparison" title="Hard gates and soft dimensions stay decomposed"/></div><div className="overflow-x-auto"><table className="w-full min-w-[920px] text-left text-xs"><thead className="border-y border-border bg-surface-sunken text-[10px] uppercase tracking-wider text-ink-faint"><tr><th className="p-3">Candidate</th><th>Mechanistic support</th><th>Evidence</th><th>Predicted benefit</th><th>Essentiality</th><th>Trade-off</th><th>Feasibility</th><th>Decision</th></tr></thead><tbody>{d.candidates.map((c)=><CandidateRow key={c.designId} candidate={c} evaluation={d.evaluations[c.designId]} onOpen={()=>setOpenCandidate(openCandidate===c.designId?null:c.designId)} open={openCandidate===c.designId}/>)}</tbody></table></div></section>

    <section className="grid gap-4 lg:grid-cols-2"><div className="panel p-4"><Title icon={ShieldCheck} eyebrow="M11 evaluator-optimizer" title="Biological consistency before ranking"/><div className="mt-3 grid gap-2 sm:grid-cols-2">{["G1 Evidence completeness","G2 Essentiality","G3 Pathway integrity","G4 Internal conflict","G5 Evidence calibration","G6 Provenance","G7 Scope","G8 Feasibility"].map((g)=><div key={g} className="flex items-center justify-between rounded border border-border p-2 text-xs"><span>{g}</span><StatusBadge status={evaluated?"partial":"not_started"} label={evaluated?"SEE FINDINGS":"PENDING"}/></div>)}</div><p className="mt-3 text-[11px] text-ink-faint">No gate is inferred from candidate prose. Only persisted evaluator output can pass or fail a gate.</p></div>
      <div className="panel p-4"><Title icon={Ban} eyebrow="Rejected candidates / Why not" title="Exclusion is a first-class decision"/><div className="mt-3 space-y-2">{rejected.map((c)=><ReasonCard key={c.designId} title={c.designId} reason={readable(c.rejectionReasons)}/>)}{excluded.slice(0,6).map((x,i)=><ReasonCard key={i} title={readable((x.reason as Record<string,unknown>)?.strategy_class||"Excluded strategy")} reason={readable((x.reason as Record<string,unknown>)?.reason||x.reason)}/>)}{rejected.length===0&&excluded.length===0&&<EmptyState variant="unavailable" title="No rejection decision recorded"/>}</div></div></section>

    <section className="grid gap-4 lg:grid-cols-[1.15fr_.85fr]"><div className="panel p-4"><Title icon={Boxes} eyebrow="Selected engineering stack" title={selected.length?"Selected interventions and dependencies":"Awaiting evaluator and human selection"}/>{selected.length?selected.map((c)=><StackCard key={c.designId} c={c}/>):<div className="mt-3 rounded border border-dashed border-border p-4 text-xs text-ink-muted"><p className="font-semibold text-ink">No candidate is selected.</p><p className="mt-1">The portfolio contains proposals only. Run the evaluator, resolve blocking findings, and record the human decision before treating a combination as the engineering stack.</p></div>}<div className="mt-3 border-t border-border pt-3"><p className="label-caps">Dependencies / conflicts</p><ul className="mt-2 space-y-1 text-xs text-ink-muted">{d.candidates.flatMap((c)=>c.interactionAndEpistasisAssumptions.map((x)=>`${c.designId}: ${readable(x)}`)).slice(0,8).map((x,i)=><li key={i}>• {x}</li>)}{d.candidates.every((c)=>c.interactionAndEpistasisAssumptions.length===0)&&<li>No explicit dependency edges recorded; integration check is partial.</li>}</ul></div></div>
      <div className="panel p-4"><Title icon={FlaskConical} eyebrow="Experimental validation plan" title="Build → test → learn"/><div className="mt-3 space-y-3"><Step n="1" title="Construct readiness" text={d.candidates.some((c)=>c.buildTestPackageId)?"A build/test package exists for at least one candidate.":"No build/test package has been drafted."}/><Step n="2" title="Discriminating measurements" text="Measure target titer and growth; add precursor/flux assays only after a project-specific plan defines conditions and units."/><Step n="3" title="Decision rule" text="Compare engineered strains with the unmodified reference candidate; update hypothesis support from observed evidence, not expected mechanism."/><Step n="4" title="Process design (M9)" text={d.candidates.some((c)=>c.processModifications.length)?"Process modifications are present in the candidate record.":"Not proposed or evaluated for this project."}/></div></div></section>

    <section className="rounded-lg border border-blue-200 bg-blue-50 p-4"><div className="flex flex-wrap items-center justify-between gap-3"><div><p className="text-[11px] font-semibold uppercase tracking-wider text-blue-700">Traceability checkpoint</p><h2 className="mt-1 font-semibold">Diagnosis v{d.project.diagnosisVersion} → {d.strategies.length} strategies → {d.candidates.length} candidates → {evaluated} evaluations → {selected.length} selected</h2></div><Link to={`/projects/${projectId}/diagnosis`} className="flex items-center gap-2 text-xs font-semibold text-accent-strong">Review source diagnosis <ArrowRight size={14}/></Link></div></section>
  </div></main>;
}

function Context({label,value,warn=false}:{label:string;value:string;warn?:boolean}){return <div className="rounded border border-white/10 bg-white/5 p-3"><p className="text-[10px] uppercase tracking-wider text-slate-400">{label}</p><p className={`mt-1 text-sm font-medium ${warn?"text-amber-200":"text-white"}`}>{value}</p></div>}
function Title({icon:Icon,eyebrow,title}:{icon:typeof Boxes;eyebrow:string;title:string}){return <div className="flex gap-2"><Icon size={17} className="mt-0.5 text-accent"/><div><p className="text-[10px] font-semibold uppercase tracking-wider text-ink-faint">{eyebrow}</p><h2 className="text-sm font-semibold">{title}</h2></div></div>}
function TraceBox({title,items}:{title:string;items:string[]}){return <div className="rounded border border-border bg-surface-sunken/60 p-3"><p className="label-caps">{title}</p><ul className="mt-2 space-y-1 text-xs text-ink-muted">{items.length?items.slice(0,5).map((x,i)=><li key={i}>• {x}</li>):<li>Not recorded</li>}</ul></div>}
function Arrow(){return <ArrowRight className="m-auto hidden text-ink-faint lg:block" size={18}/>}
function CandidateRow({candidate:c,evaluation,onOpen,open}:{candidate:CandidateDesign;evaluation:CandidateEvaluation|null;onOpen:()=>void;open:boolean}){const g=gateStatus(evaluation);return <><tr onClick={onOpen} className="cursor-pointer border-b border-border hover:bg-surface-sunken"><td className="p-3"><div className="flex items-center gap-2"><ChevronDown size={13} className={open?"rotate-180":""}/><div><p className="font-mono text-[11px]">{c.designId}</p><StatusBadge status={candidateStatusToBadge(c.status)} label={c.portfolioRole||c.status}/></div></div></td><td className="max-w-48 pr-3">{c.expectedMechanism||"Not stated"}</td><td>{c.evidenceLinks.length} links<br/><span className="text-ink-faint">RULE / KNOWLEDGE</span></td><td>Not quantified</td><td><StatusBadge status={evaluation?"partial":"not_started"} label={evaluation?"CHECK FINDINGS":"NOT EVALUATED"}/></td><td>{c.tradeoffProfile?"Recorded":"Not assessed"}</td><td>{c.buildabilityAssessment?"Assessed":c.readiness}</td><td><StatusBadge status={g.status} label={g.label}/></td></tr>{open&&<tr className="border-b border-border bg-surface-sunken/50"><td colSpan={8} className="p-4"><div className="grid gap-4 md:grid-cols-4"><Detail title="Engineering action" value={readable(c.geneticModifications)}/><Detail title="Causal chain" value={readable(c.causalChain)}/><Detail title="Trade-offs / conflicts" value={readable(c.tradeoffProfile||c.uncertaintyAndModelConflicts)}/><Detail title="Evidence provenance" value={c.evidenceLinks.map((x)=>`${x.source_type}:${x.reference}`).join("; ")||"No links"}/></div></td></tr>}</>}
function Detail({title,value}:{title:string;value:string}){return <div><p className="label-caps">{title}</p><p className="mt-2 text-xs text-ink-muted">{value}</p></div>}
function ReasonCard({title,reason}:{title:string;reason:string}){return <div className="rounded border border-red-200 bg-red-50/50 p-3 text-xs"><p className="font-semibold text-state-risk">{title}</p><p className="mt-1 text-ink-muted">{reason}</p></div>}
function StackCard({c}:{c:CandidateDesign}){return <div className="mt-3 rounded border border-emerald-200 bg-emerald-50/40 p-3 text-xs"><p className="font-semibold">{c.designId} · v{c.designVersion}</p><p className="mt-1 text-ink-muted">{readable(c.geneticModifications)}</p></div>}
function Step({n,title,text}:{n:string;title:string;text:string}){return <div className="flex gap-3"><span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-accent-soft text-[11px] font-bold text-accent-strong">{n}</span><div><p className="text-xs font-semibold">{title}</p><p className="mt-0.5 text-xs text-ink-muted">{text}</p></div></div>}
