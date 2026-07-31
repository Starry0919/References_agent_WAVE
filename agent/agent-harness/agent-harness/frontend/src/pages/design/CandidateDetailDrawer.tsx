import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { X } from "lucide-react";
import {
  bridgeToDesignVersion, draftBuildTestPackage, evaluatePortfolio, getCandidate, getLatestEvaluation,
  ingestOutcome, recordHumanDecision, requestCounterfactual, reviseCandidate, startBuild,
} from "@/api/engineeringDesign";
import { listModelCapabilities } from "@/api/diagnosis";
import { EmptyState } from "@/components/common/EmptyState";
import { StatusBadge } from "@/components/common/StatusBadge";
import { candidateStatusToBadge } from "@/lib/workflowStatus";
import { useI18n, type DictKey } from "@/lib/i18n";

const ACTOR_ID = "frontend-user";

type SubTab = "detail" | "evaluation" | "counterfactual" | "buildtest" | "approval" | "outcome";
const SUB_TABS: SubTab[] = ["detail", "evaluation", "counterfactual", "buildtest", "approval", "outcome"];

/** Docked candidate detail (same pattern as `components/workspace/
 * EvidenceDrawer.tsx`) - every per-candidate action in the doc04 loop
 * (revise, evaluate, counterfactual, build/test package, human approval,
 * bridge/build, outcome) lives here instead of as separate top-level
 * tabs, so `DesignProjectDetailPage` stays a 4-tab page. */
export function CandidateDetailDrawer({
  designId, designProjectId, onClose,
}: {
  designId: string;
  designProjectId: string;
  onClose: () => void;
}) {
  const { t } = useI18n();
  const [subTab, setSubTab] = useState<SubTab>("detail");
  const queryClient = useQueryClient();

  const candidateQuery = useQuery({ queryKey: ["design-candidate", designId], queryFn: () => getCandidate(designId) });

  function invalidateCandidate() {
    queryClient.invalidateQueries({ queryKey: ["design-candidate", designId] });
    queryClient.invalidateQueries({ queryKey: ["design-candidates", designProjectId] });
    queryClient.invalidateQueries({ queryKey: ["design-project", designProjectId] });
  }

  return (
    <aside className="flex w-[420px] flex-shrink-0 flex-col border-l border-border bg-surface">
      <div className="flex items-center justify-between border-b border-border px-3 py-2">
        <span className="font-mono text-xs font-semibold text-ink">{designId}</span>
        <button onClick={onClose} className="rounded p-1 text-ink-faint hover:bg-surface-sunken hover:text-ink" aria-label={t("common.close")}>
          <X size={14} />
        </button>
      </div>
      <div className="flex flex-wrap items-center gap-1 border-b border-border px-2 py-1.5">
        {SUB_TABS.map((tb) => (
          <button
            key={tb}
            onClick={() => setSubTab(tb)}
            className={`rounded px-2 py-1 text-[11px] font-medium ${subTab === tb ? "bg-accent-soft text-accent-strong" : "text-ink-muted hover:bg-surface-sunken"}`}
          >
            {t(`design.candidate.subtab.${tb}` as DictKey)}
          </button>
        ))}
      </div>
      <div className="flex min-h-0 flex-1 flex-col overflow-y-auto p-3">
        {candidateQuery.isLoading && <EmptyState variant="loading" />}
        {candidateQuery.isError && <EmptyState variant="failed" detail={String(candidateQuery.error)} />}
        {candidateQuery.data && (
          <>
            {subTab === "detail" && <DetailSection candidate={candidateQuery.data} onSaved={invalidateCandidate} />}
            {subTab === "evaluation" && <EvaluationSection candidate={candidateQuery.data} />}
            {subTab === "counterfactual" && <CounterfactualSection designId={designId} />}
            {subTab === "buildtest" && <BuildTestSection designId={designId} onSaved={invalidateCandidate} />}
            {subTab === "approval" && (
              <ApprovalSection candidate={candidateQuery.data} designProjectId={designProjectId} onChanged={invalidateCandidate} />
            )}
            {subTab === "outcome" && <OutcomeSection designId={designId} />}
          </>
        )}
      </div>
    </aside>
  );
}

function Field({ label, value }: { label: string; value: string }) {
  return (
    <p className="text-[11px]"><span className="font-medium text-ink-faint">{label}: </span><span className="text-ink-muted">{value}</span></p>
  );
}

function DetailSection({ candidate, onSaved }: { candidate: Awaited<ReturnType<typeof getCandidate>>; onSaved: () => void }) {
  const { t } = useI18n();
  const [reason, setReason] = useState("");
  const [expectedMechanism, setExpectedMechanism] = useState(candidate.expectedMechanism);
  const reviseMutation = useMutation({
    mutationFn: () => reviseCandidate(candidate.designId, { actorId: ACTOR_ID, modificationReason: reason, expectedMechanism }),
    onSuccess: () => { onSaved(); setReason(""); },
  });

  return (
    <div className="flex flex-col gap-2 text-xs">
      <div className="flex items-center gap-2">
        <StatusBadge status={candidateStatusToBadge(candidate.status)} label={candidate.status} />
        <span className="text-ink-faint">v{candidate.designVersion}</span>
      </div>
      <Field label={t("design.candidate.readiness")} value={candidate.readiness} />
      <Field label={t("design.candidate.portfolioRole")} value={candidate.portfolioRole ?? "—"} />
      <Field label={t("design.candidate.expectedMechanism")} value={candidate.expectedMechanism || "—"} />
      {candidate.geneticModifications.length > 0 && (
        <pre className="overflow-x-auto whitespace-pre-wrap rounded bg-surface-sunken p-2 text-[10px]">{JSON.stringify(candidate.geneticModifications, null, 2)}</pre>
      )}
      <div className="mt-1 flex flex-col gap-1.5 border-t border-border pt-2">
        <h4 className="label-caps">{t("design.candidate.reviseTitle")}</h4>
        <textarea value={expectedMechanism} onChange={(e) => setExpectedMechanism(e.target.value)} rows={2} className="rounded-lg border border-border px-2 py-1.5 text-[11px] outline-none focus:border-accent" />
        <input value={reason} onChange={(e) => setReason(e.target.value)} placeholder={t("design.candidate.modificationReasonPlaceholder")} className="rounded-lg border border-border px-2 py-1.5 text-[11px] outline-none focus:border-accent" />
        <button type="button" disabled={reviseMutation.isPending || !reason.trim()} onClick={() => reviseMutation.mutate()} className="w-fit rounded-lg border border-border bg-surface px-2.5 py-1 text-[11px] font-medium hover:bg-surface-sunken disabled:opacity-40">
          {reviseMutation.isPending ? t("design.candidate.revising") : t("design.candidate.revise")}
        </button>
        {reviseMutation.isError && <EmptyState variant="failed" detail={String(reviseMutation.error)} />}
      </div>
    </div>
  );
}

function EvaluationSection({ candidate }: { candidate: Awaited<ReturnType<typeof getCandidate>> }) {
  const { t } = useI18n();
  const latestQuery = useQuery({ queryKey: ["design-candidate-evaluation", candidate.designId], queryFn: () => getLatestEvaluation(candidate.designId) });
  const evalMutation = useMutation({
    mutationFn: () => evaluatePortfolio(candidate.portfolioId as string, ACTOR_ID),
    onSuccess: () => latestQuery.refetch(),
  });

  return (
    <div className="flex flex-col gap-2 text-xs">
      <button
        type="button"
        disabled={evalMutation.isPending || !candidate.portfolioId}
        onClick={() => evalMutation.mutate()}
        className="w-fit rounded-lg bg-accent px-2.5 py-1.5 text-[11px] font-medium text-white disabled:opacity-40"
      >
        {evalMutation.isPending ? t("design.candidate.evaluating") : t("design.candidate.evaluatePortfolio")}
      </button>
      {evalMutation.isError && <EmptyState variant="failed" detail={String(evalMutation.error)} />}
      {evalMutation.data && (
        <div className="text-[11px] text-ink-muted">
          {t("design.candidate.thisCandidate")}: {evalMutation.data.evaluations[candidate.designId]?.recommendation ?? "—"}
        </div>
      )}

      {latestQuery.isLoading && <EmptyState variant="loading" />}
      {latestQuery.data ? (
        <div className="flex flex-col gap-1 border-t border-border pt-2">
          <Field label={t("design.candidate.recommendation")} value={latestQuery.data.recommendation} />
          <Field label={t("design.candidate.paretoStatus")} value={latestQuery.data.paretoStatus ?? "—"} />
          {latestQuery.data.requiredRevisions.length > 0 && (
            <p className="text-state-caution">{t("design.candidate.requiredRevisions")}: {JSON.stringify(latestQuery.data.requiredRevisions)}</p>
          )}
          <pre className="overflow-x-auto whitespace-pre-wrap rounded bg-surface-sunken p-2 text-[10px]">{JSON.stringify(latestQuery.data.evaluatorFindings, null, 2)}</pre>
        </div>
      ) : (
        !latestQuery.isLoading && <EmptyState variant="unavailable" title={t("design.candidate.noEvaluationTitle")} />
      )}
    </div>
  );
}

function CounterfactualSection({ designId }: { designId: string }) {
  const { t } = useI18n();
  const [adapterName, setAdapterName] = useState("");
  const [inputsText, setInputsText] = useState("{}");
  const capsQuery = useQuery({ queryKey: ["diagnosis-model-capabilities"], queryFn: listModelCapabilities });
  const mutation = useMutation({
    mutationFn: () => {
      let inputs: Record<string, unknown> = {};
      try {
        inputs = JSON.parse(inputsText || "{}");
      } catch {
        throw new Error(t("design.candidate.invalidJson"));
      }
      return requestCounterfactual(designId, { adapterName, actorId: ACTOR_ID, inputs });
    },
  });

  return (
    <div className="flex flex-col gap-2 text-xs">
      <select value={adapterName} onChange={(e) => setAdapterName(e.target.value)} className="w-fit rounded-lg border border-border bg-surface px-2 py-1.5 text-[11px] outline-none">
        <option value="">{t("diagnosis.models.selectAdapter")}</option>
        {capsQuery.data && Object.keys(capsQuery.data).map((name) => <option key={name} value={name}>{name}</option>)}
      </select>
      <textarea value={inputsText} onChange={(e) => setInputsText(e.target.value)} rows={3} className="rounded-lg border border-border px-2 py-1.5 font-mono text-[11px] outline-none focus:border-accent" />
      <button type="button" disabled={mutation.isPending || !adapterName} onClick={() => mutation.mutate()} className="w-fit rounded-lg bg-accent px-2.5 py-1.5 text-[11px] font-medium text-white disabled:opacity-40">
        {mutation.isPending ? t("design.candidate.running") : t("design.candidate.runCounterfactual")}
      </button>
      {mutation.isError && <EmptyState variant="failed" detail={String(mutation.error)} />}
      {mutation.data && (
        <div className="border-t border-border pt-2">
          <Field label={t("design.candidate.runtimeStatus")} value={mutation.data.runtimeStatus} />
          <pre className="mt-1 overflow-x-auto whitespace-pre-wrap rounded bg-surface-sunken p-2 text-[10px]">{JSON.stringify(mutation.data.outputs, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}

function BuildTestSection({ designId, onSaved }: { designId: string; onSaved: () => void }) {
  const { t } = useI18n();
  const [constructionConcept, setConstructionConcept] = useState("");
  const [requiredMaterials, setRequiredMaterials] = useState("");
  const mutation = useMutation({
    mutationFn: () =>
      draftBuildTestPackage(designId, {
        actorId: ACTOR_ID, constructionConcept,
        requiredMaterials: requiredMaterials.split(",").map((s) => s.trim()).filter(Boolean),
      }),
    onSuccess: onSaved,
  });

  return (
    <div className="flex flex-col gap-2 text-xs">
      <label className="label-caps">{t("design.candidate.constructionConcept")}</label>
      <textarea value={constructionConcept} onChange={(e) => setConstructionConcept(e.target.value)} rows={3} className="rounded-lg border border-border px-2 py-1.5 text-[11px] outline-none focus:border-accent" />
      <label className="label-caps">{t("design.candidate.requiredMaterials")}</label>
      <input value={requiredMaterials} onChange={(e) => setRequiredMaterials(e.target.value)} placeholder="pKD46, pCP20" className="rounded-lg border border-border px-2 py-1.5 text-[11px] outline-none focus:border-accent" />
      <button type="button" disabled={mutation.isPending} onClick={() => mutation.mutate()} className="w-fit rounded-lg bg-accent px-2.5 py-1.5 text-[11px] font-medium text-white disabled:opacity-40">
        {mutation.isPending ? t("design.candidate.drafting") : t("design.candidate.draftBuildTest")}
      </button>
      {mutation.isError && <EmptyState variant="failed" detail={String(mutation.error)} />}
      {mutation.data && (
        <div className="border-t border-border pt-2 text-[11px] text-ink-muted">
          <Field label={t("design.candidate.readiness")} value={mutation.data.readiness} />
          {mutation.data.missingInformationOrResources.length > 0 && (
            <p className="text-state-caution">{t("design.candidate.missingInfo")}: {JSON.stringify(mutation.data.missingInformationOrResources)}</p>
          )}
        </div>
      )}
    </div>
  );
}

function ApprovalSection({
  candidate, designProjectId, onChanged,
}: {
  candidate: Awaited<ReturnType<typeof getCandidate>>;
  designProjectId: string;
  onChanged: () => void;
}) {
  const { t } = useI18n();
  const [decision, setDecision] = useState<"approved" | "rejected">("approved");
  const [reason, setReason] = useState("");

  const decisionMutation = useMutation({
    mutationFn: () => recordHumanDecision(candidate.designId, { approverId: ACTOR_ID, decision, reason }),
    onSuccess: onChanged,
  });
  const bridgeMutation = useMutation({
    mutationFn: () => bridgeToDesignVersion(candidate.designId, ACTOR_ID),
    onSuccess: onChanged,
  });
  const startBuildMutation = useMutation({
    mutationFn: () => startBuild(designProjectId, candidate.designId, ACTOR_ID),
    onSuccess: onChanged,
  });

  return (
    <div className="flex flex-col gap-2 text-xs">
      <div className="flex items-center gap-2">
        <select value={decision} onChange={(e) => setDecision(e.target.value as "approved" | "rejected")} className="rounded-lg border border-border bg-surface px-2 py-1.5 text-[11px] outline-none">
          <option value="approved">approved</option>
          <option value="rejected">rejected</option>
        </select>
        <input value={reason} onChange={(e) => setReason(e.target.value)} placeholder={t("design.candidate.reasonPlaceholder")} className="min-w-0 flex-1 rounded-lg border border-border px-2 py-1.5 text-[11px] outline-none focus:border-accent" />
      </div>
      <button type="button" disabled={decisionMutation.isPending} onClick={() => decisionMutation.mutate()} className="w-fit rounded-lg bg-accent px-2.5 py-1.5 text-[11px] font-medium text-white disabled:opacity-40">
        {decisionMutation.isPending ? t("design.candidate.recordingDecision") : t("design.candidate.recordDecision")}
      </button>
      {decisionMutation.isError && <EmptyState variant="failed" detail={String(decisionMutation.error)} />}

      {candidate.status === "approved_for_build" && (
        <div className="flex flex-wrap gap-2 border-t border-border pt-2">
          <button type="button" disabled={bridgeMutation.isPending} onClick={() => bridgeMutation.mutate()} className="rounded-lg border border-border bg-surface px-2.5 py-1 text-[11px] font-medium hover:bg-surface-sunken disabled:opacity-40">
            {t("design.candidate.bridgeToDesignVersion")}
          </button>
          <button type="button" disabled={startBuildMutation.isPending} onClick={() => startBuildMutation.mutate()} className="rounded-lg border border-border bg-surface px-2.5 py-1 text-[11px] font-medium hover:bg-surface-sunken disabled:opacity-40">
            {t("design.candidate.startBuild")}
          </button>
        </div>
      )}
      {bridgeMutation.data && <Field label={t("design.candidate.designVersionId")} value={bridgeMutation.data} />}
    </div>
  );
}

function OutcomeSection({ designId }: { designId: string }) {
  const { t } = useI18n();
  const [observedResultsText, setObservedResultsText] = useState("[]");
  const [constructionVerified, setConstructionVerified] = useState(true);
  const [assayQcPassed, setAssayQcPassed] = useState(true);
  const [outcomeUpdate, setOutcomeUpdate] = useState("");

  const mutation = useMutation({
    mutationFn: () => {
      let observedResults: unknown[];
      try {
        observedResults = JSON.parse(observedResultsText);
      } catch {
        throw new Error(t("design.candidate.invalidJson"));
      }
      return ingestOutcome(designId, { actorId: ACTOR_ID, observedResults, constructionVerified, assayQcPassed, outcomeUpdate });
    },
  });

  return (
    <div className="flex flex-col gap-2 text-xs">
      <label className="label-caps">{t("design.candidate.observedResults")}</label>
      <textarea value={observedResultsText} onChange={(e) => setObservedResultsText(e.target.value)} rows={3} className="rounded-lg border border-border px-2 py-1.5 font-mono text-[11px] outline-none focus:border-accent" />
      <label className="flex items-center gap-1.5"><input type="checkbox" checked={constructionVerified} onChange={(e) => setConstructionVerified(e.target.checked)} /> {t("design.candidate.constructionVerified")}</label>
      <label className="flex items-center gap-1.5"><input type="checkbox" checked={assayQcPassed} onChange={(e) => setAssayQcPassed(e.target.checked)} /> {t("design.candidate.assayQcPassed")}</label>
      <input value={outcomeUpdate} onChange={(e) => setOutcomeUpdate(e.target.value)} placeholder={t("design.candidate.outcomeUpdatePlaceholder")} className="rounded-lg border border-border px-2 py-1.5 text-[11px] outline-none focus:border-accent" />
      <button type="button" disabled={mutation.isPending} onClick={() => mutation.mutate()} className="w-fit rounded-lg bg-accent px-2.5 py-1.5 text-[11px] font-medium text-white disabled:opacity-40">
        {mutation.isPending ? t("design.candidate.submittingOutcome") : t("design.candidate.submitOutcome")}
      </button>
      {mutation.isError && <EmptyState variant="failed" detail={String(mutation.error)} />}
      {mutation.data && (
        <div className="border-t border-border pt-2 text-[11px] text-ink-muted">
          <Field label={t("design.candidate.failureClassification")} value={mutation.data.failureClassification} />
          <Field label={t("design.candidate.decidedNextAction")} value={mutation.data.decidedNextAction ?? "—"} />
        </div>
      )}
    </div>
  );
}
