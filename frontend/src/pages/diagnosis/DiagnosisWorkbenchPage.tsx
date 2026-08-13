import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Link, useParams, useSearchParams } from "react-router-dom";
import { Activity, AlertTriangle, ArrowRight, Beaker, CheckCircle2, ChevronDown, GitBranch, Play, ShieldQuestion } from "lucide-react";
import {
  getSession, listDecisions, listEvidence, listEvidenceItems, listHypotheses, listModelCapabilities,
  listSessionsForProject, listTests, type EvidenceItemRow, type EvidenceLinkRow, type HypothesisRow,
} from "@/api/diagnosis";
import { getProject } from "@/api/projects";
import { EmptyState } from "@/components/common/EmptyState";
import { StatusBadge } from "@/components/common/StatusBadge";
import { diagnosisStatusToBadge } from "@/lib/workflowStatus";

const AXES = [
  ["Pathway feasibility", ["pathway", "通路"]], ["Precursor supply", ["precursor", "PEP", "E4P", "前体"]],
  ["Cofactor / redox", ["cofactor", "redox", "NAD", "还原"]], ["Feedback regulation", ["feedback", "inhibition", "反馈", "抑制"]],
  ["Rate-limiting enzyme", ["enzyme", "rate-limit", "酶", "限速"]], ["Competing flux", ["competing", "carbon flux", "竞争", "旁路"]],
  ["Gene essentiality", ["essential", "必需"]], ["Toxicity / by-product", ["toxic", "by-product", "毒", "副产"]],
  ["Process conditions (M9)", ["fermentation", "process", "发酵", "工艺"]],
] as const;

function evidenceStatus(item?: EvidenceItemRow) {
  if (!item) return "UNRESOLVED";
  if (item.sourceType === "model_run") return "MODEL_COMPUTED";
  if (item.sourceType === "experiment") return "MEASURED";
  if (item.sourceType === "literature") return "LITERATURE_REPORTED";
  if (item.sourceType === "expert_rule") return "RULE_TRANSFER";
  return "DATABASE_FACT";
}

export function DiagnosisWorkbenchPage() {
  const { projectId = "" } = useParams<{ projectId: string }>();
  const [params, setParams] = useSearchParams();
  const project = useQuery({ queryKey: ["project", projectId], queryFn: () => getProject(projectId), enabled: !!projectId });
  const sessions = useQuery({ queryKey: ["diagnosis-sessions", projectId], queryFn: () => listSessionsForProject(projectId), enabled: !!projectId });
  const selectedId = params.get("session") || sessions.data?.[0]?.diagnosisSessionId || "";
  const session = useQuery({ queryKey: ["diagnosis-session", selectedId], queryFn: () => getSession(selectedId), enabled: !!selectedId });
  const hypotheses = useQuery({ queryKey: ["diagnosis-hypotheses", selectedId], queryFn: () => listHypotheses(selectedId), enabled: !!selectedId });
  const evidence = useQuery({ queryKey: ["diagnosis-evidence", selectedId], queryFn: () => listEvidence(selectedId), enabled: !!selectedId });
  const evidenceItems = useQuery({ queryKey: ["diagnosis-evidence-items", projectId], queryFn: () => listEvidenceItems(projectId), enabled: !!projectId });
  const decisions = useQuery({ queryKey: ["diagnosis-decisions", selectedId], queryFn: () => listDecisions(selectedId), enabled: !!selectedId });
  const tests = useQuery({ queryKey: ["diagnosis-tests", selectedId], queryFn: () => listTests(selectedId), enabled: !!selectedId });
  const capabilities = useQuery({ queryKey: ["diagnosis-model-capabilities"], queryFn: listModelCapabilities });

  const itemById = useMemo(() => new Map((evidenceItems.data ?? []).map((x) => [x.evidenceItemId, x])), [evidenceItems.data]);
  const linksByHyp = useMemo(() => {
    const m = new Map<string, EvidenceLinkRow[]>();
    for (const link of evidence.data ?? []) m.set(link.hypothesisVersionId, [...(m.get(link.hypothesisVersionId) ?? []), link]);
    return m;
  }, [evidence.data]);
  const lead = decisions.data?.[0]?.leadingHypothesisIds ?? [];
  const ranked = [...(hypotheses.data ?? [])].sort((a, b) => (lead.includes(a.hypothesisVersionId) ? -1 : 1) - (lead.includes(b.hypothesisVersionId) ? -1 : 1));
  const hard = (evidence.data ?? []).filter((l) => { const x = itemById.get(l.evidenceItemId); return x?.quality === "high" && x.directness === "direct"; }).length;
  const soft = (evidence.data ?? []).length - hard;
  const evaluatedAxes = AXES.filter(([, keys]) => ranked.some((h) => keys.some((k) => `${h.statement} ${h.mechanismClass}`.toLowerCase().includes(k.toLowerCase()))));

  if (project.isLoading || sessions.isLoading) return <div className="p-6"><EmptyState variant="loading" /></div>;
  if (project.isError || sessions.isError) return <div className="p-6"><EmptyState variant="failed" detail={String(project.error ?? sessions.error)} /></div>;
  if (!project.data) return <div className="p-6"><EmptyState variant="unavailable" title="Project context unavailable" /></div>;

  const host = [project.data.hostDefinition.species, project.data.hostDefinition.strain].filter(Boolean).join(" · ") || "Not specified";
  return (
    <main className="min-h-0 flex-1 overflow-y-auto bg-surface-sunken p-4 lg:p-6">
      <div className="mx-auto flex max-w-7xl flex-col gap-5">
        <header className="rounded-lg bg-[#162235] p-5 text-white shadow-sm">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div><p className="text-[11px] font-semibold uppercase tracking-[.18em] text-blue-200">Engineering problem map</p><h1 className="mt-1 text-2xl font-semibold">Diagnosis Workspace</h1><p className="mt-2 max-w-3xl text-sm text-slate-300">Why is this system not yet meeting the project goal, and which mechanisms remain plausible?</p></div>
            <div className="flex gap-2"><Link to={`/projects/${projectId}/run_new_diagnose`} className="flex items-center gap-2 rounded bg-accent px-3 py-2 text-xs font-semibold"><Play size={14}/>Run new diagnosis</Link></div>
          </div>
          <div className="mt-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
            <Context label="Host" value={host}/><Context label="Substrate" value="Not specified" warn/><Context label="Target product" value={project.data.targetProduct}/><Context label="Lifecycle" value={project.data.lifecycleStage}/><Context label="Evidence" value={`${hard} hard · ${soft} soft`}/>
          </div>
        </header>

        {(sessions.data?.length ?? 0) === 0 ? <EmptyState variant="first_use" title="No diagnosis result for this project" detail="Run diagnosis to create the first project-scoped engineering problem map." /> : (
          <>
            <section className="panel flex flex-wrap items-center justify-between gap-3 p-3">
              <div className="flex items-center gap-2"><Activity size={16} className="text-accent"/><span className="text-xs font-semibold">Current run</span><select value={selectedId} onChange={(e) => { params.set("session", e.target.value); setParams(params); }} className="rounded border border-border bg-surface px-2 py-1 font-mono text-xs">{sessions.data?.map((s) => <option key={s.diagnosisSessionId} value={s.diagnosisSessionId}>{s.diagnosisSessionId}</option>)}</select></div>
              <div className="flex items-center gap-2"><StatusBadge status={diagnosisStatusToBadge(session.data?.status ?? "pending")} label={session.data?.status ?? "loading"}/><Link className="text-xs font-semibold text-accent-strong hover:underline" to={`/projects/${projectId}/diagnosis/${selectedId}`}>Open operational record →</Link></div>
            </section>

            <section className="grid gap-4 lg:grid-cols-[1.45fr_.75fr]">
              <div className="panel p-4"><SectionTitle icon={AlertTriangle} eyebrow="Executive summary" title="Ranked engineering problems"/><div className="mt-4 grid gap-3 md:grid-cols-2">{ranked.slice(0,4).map((h, i) => <FindingCard key={h.hypothesisVersionId} h={h} rank={i+1} leading={lead.includes(h.hypothesisVersionId)} links={linksByHyp.get(h.hypothesisVersionId) ?? []} itemById={itemById}/>)}</div></div>
              <aside className="panel p-4"><SectionTitle icon={CheckCircle2} eyebrow="Coverage" title={`${evaluatedAxes.length}/${AXES.length} diagnostic axes evaluated`}/><div className="mt-3 space-y-2">{AXES.map(([axis, keys]) => { const h = ranked.find((x) => keys.some((k) => `${x.statement} ${x.mechanismClass}`.toLowerCase().includes(k.toLowerCase()))); return <div key={axis} className="flex items-start justify-between gap-3 border-b border-border pb-2 text-xs"><div><p className="font-medium text-ink">{axis}</p><p className="mt-0.5 text-ink-faint">{h?.statement || "No project-specific result"}</p></div><StatusBadge status={h ? "under_review" : "unavailable"} label={h ? "FINDING" : "NOT EVALUATED"}/></div>; })}</div></aside>
            </section>

            <section className="panel p-4"><SectionTitle icon={GitBranch} eyebrow="Hypothesis competition" title="Observation → candidate mechanism → discriminating evidence"/><p className="mt-2 text-xs text-ink-muted">Ranking expresses the current assessment; it does not prove the first mechanism causal.</p><div className="mt-3 space-y-2">{ranked.map((h, i) => <HypothesisRowView key={h.hypothesisVersionId} h={h} rank={i+1} links={linksByHyp.get(h.hypothesisVersionId) ?? []} itemById={itemById}/>)}</div></section>

            <section className="grid gap-4 lg:grid-cols-2">
              <div className="panel p-4"><SectionTitle icon={Beaker} eyebrow="Quantitative grounding" title="Measured / computed / predicted separation"/><div className="mt-3 rounded border border-amber-200 bg-amber-50 p-3 text-xs text-amber-900"><p className="font-semibold">No quantitative model result is attached to this diagnosis.</p><p className="mt-1">Theoretical yield, FBA flux, FVA range and growth impact are not evaluated. Model availability does not equal a project-specific computation.</p></div><div className="mt-3 flex flex-wrap gap-2">{Object.entries(capabilities.data ?? {}).map(([name, c]) => <StatusBadge key={name} status={c.available ? "active" : "unavailable"} label={`${name}: ${c.available ? "available" : "unavailable"}`}/>)}</div></div>
              <div className="panel p-4"><SectionTitle icon={ShieldQuestion} eyebrow="Decision boundary" title="What remains unresolved?"/><ul className="mt-3 space-y-2 text-xs text-ink-muted"><li>• {decisions.data?.[0]?.alternativesNotExcludedIds.length ?? 0} alternative mechanisms are explicitly not excluded.</li><li>• {tests.data?.length ?? 0} discriminating tests are recorded; absence does not imply validation is complete.</li><li>• Evidence against: {(evidence.data ?? []).filter((e) => e.relation === "contradicts").length} recorded links.</li><li>• Source calibration: rule transfer is soft evidence until project-matched validation.</li></ul></div>
            </section>

            <section className="rounded-lg border border-blue-200 bg-blue-50 p-4"><div className="flex flex-wrap items-center justify-between gap-3"><div><p className="text-[11px] font-semibold uppercase tracking-wider text-blue-700">Engineering consequence</p><h2 className="mt-1 font-semibold text-ink">Carry the gated diagnosis into candidate design—without erasing alternatives</h2><p className="mt-1 text-xs text-ink-muted">The design workspace consumes diagnosis version {decisions.data?.[0]?.diagnosisVersion ?? "—"}, its supported hypotheses, unresolved alternatives and uncertainty.</p></div><Link to={`/projects/${projectId}/design`} className="flex items-center gap-2 rounded bg-accent px-4 py-2 text-xs font-semibold text-white">Open Engineering Design <ArrowRight size={14}/></Link></div></section>
          </>
        )}
      </div>
    </main>
  );
}

function Context({label,value,warn=false}:{label:string;value:string;warn?:boolean}) { return <div className="rounded border border-white/10 bg-white/5 p-3"><p className="text-[10px] uppercase tracking-wider text-slate-400">{label}</p><p className={`mt-1 text-sm font-medium ${warn ? "text-amber-200" : "text-white"}`}>{value}</p></div>; }
function SectionTitle({icon:Icon,eyebrow,title}:{icon:typeof Activity;eyebrow:string;title:string}) { return <div className="flex items-start gap-2"><Icon size={17} className="mt-0.5 text-accent"/><div><p className="text-[10px] font-semibold uppercase tracking-wider text-ink-faint">{eyebrow}</p><h2 className="text-sm font-semibold text-ink">{title}</h2></div></div>; }
function FindingCard({h,rank,leading,links,itemById}:{h:HypothesisRow;rank:number;leading:boolean;links:EvidenceLinkRow[];itemById:Map<string,EvidenceItemRow>}) { const against=links.filter((l)=>l.relation==="contradicts"); return <article className={`rounded border p-3 ${leading ? "border-blue-300 bg-blue-50/40" : "border-border"}`}><div className="flex items-center justify-between"><span className="font-mono text-[10px] text-ink-faint">P{rank} · {h.mechanismClass || "unclassified"}</span><StatusBadge status={leading ? "under_review" : "not_started"} label={leading ? "LEADING" : "ALTERNATIVE"}/></div><h3 className="mt-2 text-sm font-semibold text-ink">{h.statement || h.hypothesisVersionId}</h3><div className="mt-3 flex flex-wrap gap-1.5"><StatusBadge status="unavailable" label="MECHANISTIC INFERENCE"/><StatusBadge status={links.some((l)=>itemById.get(l.evidenceItemId)?.quality==="high") ? "approved" : "under_review"} label={`${links.length} evidence for`}/><StatusBadge status={against.length ? "rejected" : "unavailable"} label={`${against.length} evidence against`}/></div></article>; }
function HypothesisRowView({h,rank,links,itemById}:{h:HypothesisRow;rank:number;links:EvidenceLinkRow[];itemById:Map<string,EvidenceItemRow>}) { const [open,setOpen]=useState(rank===1); const support=links.filter((l)=>l.relation!=="contradicts"), against=links.filter((l)=>l.relation==="contradicts"); return <article className="rounded border border-border"><button onClick={()=>setOpen(!open)} className="flex w-full items-start justify-between gap-3 p-3 text-left"><div className="flex gap-3"><span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-surface-sunken font-mono text-[10px]">H{rank}</span><div><p className="text-xs font-semibold text-ink">{h.statement || h.hypothesisVersionId}</p><p className="mt-1 text-[11px] text-ink-faint">{h.status} · confidence is qualitative · {h.falsifiers.length} falsifier(s)</p></div></div><ChevronDown size={15} className={open?"rotate-180":""}/></button>{open&&<div className="grid gap-3 border-t border-border bg-surface-sunken/40 p-3 md:grid-cols-3"><EvidenceColumn title="Evidence for" links={support} itemById={itemById}/><EvidenceColumn title="Evidence against" links={against} itemById={itemById}/><div><p className="label-caps">Discriminating test</p><p className="mt-2 text-xs text-ink-muted">{h.falsifiers.join("; ") || "No discriminating test specified; validation need remains open."}</p></div></div>}</article>; }
function EvidenceColumn({title,links,itemById}:{title:string;links:EvidenceLinkRow[];itemById:Map<string,EvidenceItemRow>}) { return <div><p className="label-caps">{title}</p>{links.length===0?<p className="mt-2 text-xs text-ink-faint">None recorded</p>:<ul className="mt-2 space-y-2">{links.map((l)=>{const item=itemById.get(l.evidenceItemId);return <li key={l.evidenceLinkId} className="text-xs text-ink-muted"><span className="font-semibold text-ink">{item?.sourceReference||l.evidenceItemId}</span> · {item?.quality||"unknown"}/{item?.directness||"unknown"}<p>{l.claim}</p><span className="font-mono text-[10px] text-accent-strong">{evidenceStatus(item)}</span></li>;})}</ul>}</div>; }
