import { useEffect, useRef, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { ArrowLeft, BookOpenCheck, ChevronDown, Columns2, FlaskConical, ShieldCheck } from "lucide-react";
import { getEvidenceDocument, type AgentTraceStep, type ExperimentalDesignStep } from "@/api/evidence";
import { CompareTab, DesignTab, QualityTab, ReasoningTab, TabButton } from "@/pages/paperExtraction/PaperResultTabs";
import { EmptyState } from "@/components/common/EmptyState";
import { useI18n } from "@/lib/i18n";
import { PaperHeader } from "./components/PaperHeader";
import { AgentTracePanel } from "./components/AgentTracePanel";
import { ExperimentalDesignPanel } from "./components/ExperimentalDesignPanel";
import { EvidenceProvenancePanel } from "./components/EvidenceProvenancePanel";
import { ApplicabilityReportPanel } from "./components/ApplicabilityReportPanel";
import { EvidenceGraphModal } from "./components/EvidenceGraphModal";
import { CalibrationPanel } from "./components/CalibrationPanel";

interface SyncState {
  agentStep: number | null;
  designStep: number | "all" | null;
  origin: "agent" | "design" | null;
}

/**
 * Literature-evidence detail page (harness/api/generation.py::get_evidence_document,
 * real, backed by knowledge/ddr_database/*.json). Reached either by clicking
 * "详情" on a Literature Evidence list item (KnowledgePage's literature tab)
 * or automatically once a single-paper extraction run finishes
 * (PaperExtractionPage). This is the "Dual-track Evidence Reasoning View"
 * (prompt/小组件_模块/论文实验设计思路的抽取/抽取详情页面.md) - a synced
 * Agent Reasoning Trace (left) against an Experimental Design Reconstruction
 * (right), not a plain paper-summary page.
 */
export function PaperEvidenceDetailPage() {
  const { t } = useI18n();
  const queryClient = useQueryClient();
  const { projectId, sourceId } = useParams<{ projectId: string; sourceId: string }>();
  const [tab, setTab] = useState<"reasoning" | "design" | "quality" | "compare">("reasoning");
  const [moreOpen, setMoreOpen] = useState(false);
  const [graphOpen, setGraphOpen] = useState(false);
  const [active, setActive] = useState<SyncState>({ agentStep: null, designStep: null, origin: null });

  const agentRefs = useRef<Record<number, HTMLDivElement | null>>({});
  const designRefs = useRef<Record<number, HTMLDivElement | null>>({});

  const detailQuery = useQuery({
    queryKey: ["evidence-document", sourceId, "local_ddr"],
    queryFn: () => getEvidenceDocument(sourceId as string, "local_ddr"),
    enabled: !!sourceId,
  });

  const detail = detailQuery.data;

  useEffect(() => {
    if (active.origin === "agent" && typeof active.designStep === "number") {
      designRefs.current[active.designStep]?.scrollIntoView({ behavior: "smooth", block: "nearest" });
    } else if (active.origin === "design" && active.agentStep != null) {
      agentRefs.current[active.agentStep]?.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }
  }, [active]);

  function selectAgent(step: AgentTraceStep) {
    setActive({ agentStep: step.step, designStep: step.designStepRef, origin: "agent" });
  }

  function selectDesign(step: ExperimentalDesignStep) {
    const match = detail?.agentTrace.find((a) => a.designStepRef === step.step);
    setActive({ agentStep: match?.step ?? null, designStep: step.step, origin: "design" });
  }

  function selectDesignByStepNumber(stepNum: number) {
    const s = detail?.experimentalDesign.find((d) => d.step === stepNum);
    if (s) selectDesign(s);
  }

  function handleDownloadJson() {
    if (!detail?.rawRecord) return;
    const blob = new Blob([JSON.stringify(detail.rawRecord, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${detail.sourceId}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }

  const hasDualTrack = !!detail && (detail.agentTrace.length > 0 || detail.experimentalDesign.length > 0);

  return (
    <div className="flex min-h-0 flex-1 flex-col overflow-y-auto p-4">
      <Link to={`/projects/${projectId}/knowledge?tab=literature`} className="mb-3 flex w-fit items-center gap-1 text-xs text-ink-muted hover:text-ink">
        <ArrowLeft size={13} aria-hidden />
        {t("paperEvidence.backToList")}
      </Link>

      {detailQuery.isLoading && <EmptyState variant="loading" />}
      {detailQuery.isError && <EmptyState variant="failed" detail={String(detailQuery.error)} />}
      {!detailQuery.isLoading && !detail && <EmptyState variant="failed" title={t("paperEvidence.notFound")} />}

      {detail && (
        <div className="flex flex-col gap-4">
          <PaperHeader detail={detail} projectId={projectId} onDownloadJson={handleDownloadJson} onViewGraph={() => setGraphOpen(true)} />

          {detail.abstractOrSummary && (
            <details className="panel p-3 text-xs">
              <summary className="cursor-pointer select-none font-medium text-ink">{t("page3.detail.abstractOrSummary")}</summary>
              <p className="mt-2 text-ink-muted">{detail.abstractOrSummary}</p>
            </details>
          )}

          {hasDualTrack ? (
            <div className="grid grid-cols-1 gap-4 lg:grid-cols-[45%_55%] lg:items-start">
              <AgentTracePanel
                steps={detail.agentTrace}
                activeAgentStep={active.agentStep}
                onSelectAgent={selectAgent}
                registerRef={(step, el) => {
                  agentRefs.current[step] = el;
                }}
              />
              <ExperimentalDesignPanel
                steps={detail.experimentalDesign}
                activeDesignStep={active.designStep}
                onSelectDesign={selectDesign}
                registerRef={(step, el) => {
                  designRefs.current[step] = el;
                }}
              />
            </div>
          ) : (
            <div className="panel flex items-start gap-2 p-3 text-[11px] text-ink-muted">
              <EmptyState variant="unavailable" title={t("paperEvidence.noAutoDetailTitle")} detail={t("paperEvidence.noAutoDetailDetail")} />
            </div>
          )}

          {detail.evidenceProvenance.length > 0 && <EvidenceProvenancePanel items={detail.evidenceProvenance} onSelectStep={selectDesignByStepNumber} />}

          <ApplicabilityReportPanel ddrId={detail.sourceId} projectId={projectId} />

          {detail.rawRecord && (
            <CalibrationPanel
              ddrId={detail.sourceId}
              rawRecord={detail.rawRecord}
              calibrationStatus={detail.calibrationStatus}
              conflictCount={detail.conflictCount}
              attempts={detail.extractionAttempts}
              onSubmitted={() => queryClient.invalidateQueries({ queryKey: ["evidence-document", sourceId, "local_ddr"] })}
            />
          )}

          {detail.paperExtractionDetail && (
            <details className="panel p-4" open={moreOpen} onToggle={(e) => setMoreOpen((e.target as HTMLDetailsElement).open)}>
              <summary className="flex cursor-pointer select-none items-center gap-1.5 text-sm font-semibold text-ink">
                <ChevronDown size={14} className={`transition-transform ${moreOpen ? "" : "-rotate-90"}`} aria-hidden />
                {t("paperEvidence.extractionTitle")}
              </summary>
              <div className="mt-3 flex flex-col gap-3">
                <div className="flex gap-1 border-b border-border">
                  <TabButton active={tab === "reasoning"} onClick={() => setTab("reasoning")} icon={<BookOpenCheck size={12} />} label={t("page5.result.tabReasoning")} />
                  <TabButton
                    active={tab === "design"}
                    onClick={() => setTab("design")}
                    icon={<FlaskConical size={12} />}
                    label={t("page5.result.tabDesign")}
                    badge={detail.paperExtractionDetail.hasDesignContent ? undefined : "!"}
                  />
                  <TabButton active={tab === "quality"} onClick={() => setTab("quality")} icon={<ShieldCheck size={12} />} label={t("page5.result.tabQuality")} />
                  <TabButton active={tab === "compare"} onClick={() => setTab("compare")} icon={<Columns2 size={12} />} label={t("page5.result.tabCompare")} />
                </div>
                {tab === "reasoning" && <ReasoningTab paper={detail.paperExtractionDetail} />}
                {tab === "design" && <DesignTab paper={detail.paperExtractionDetail} />}
                {tab === "quality" && <QualityTab paper={detail.paperExtractionDetail} />}
                {tab === "compare" && <CompareTab paper={detail.paperExtractionDetail} />}
              </div>
            </details>
          )}
        </div>
      )}

      {graphOpen && detail && <EvidenceGraphModal graph={detail.evidenceGraph} onClose={() => setGraphOpen(false)} />}
    </div>
  );
}
