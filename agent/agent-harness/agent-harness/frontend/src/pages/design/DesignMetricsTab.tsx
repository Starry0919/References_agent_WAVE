import { useEffect, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { FlaskConical } from "lucide-react";
import {
  getMetricsSummary,
  listConsistencyRuns,
  runConsistencySample,
  setReferenceDdr,
  type CoverageByClassEntry,
  type MetricResult,
} from "@/api/evaluationMetrics";
import { EmptyState } from "@/components/common/EmptyState";
import { useI18n, type DictKey } from "@/lib/i18n";

/**
 * 260718 设计文档 §7 (验证方式) evaluation-metrics, scoped to one design
 * project - lives as a tab inside `DesignProjectDetailPage` (not a
 * standalone top-level page) since the metrics only ever mean anything in
 * the context of a specific scheme/candidate set, never in the abstract.
 * Structured to make the doc's own 3-layer split visible in the UI itself
 * (过程层/能力层/结果层), with 复现率 rendered separately and visibly
 * de-emphasized - the doc is explicit that it must never read as a
 * primary metric alongside the other four (harness/evaluation_metrics/
 * aggregator.py mirrors the same layering server-side).
 */
export function DesignMetricsTab({ designProjectId, referenceDdrIds }: { designProjectId: string; referenceDdrIds: string[] }) {
  const { t } = useI18n();
  const queryClient = useQueryClient();

  const summaryQuery = useQuery({
    queryKey: ["eval-metrics-summary", designProjectId],
    queryFn: () => getMetricsSummary(designProjectId),
  });

  function invalidateAfterLink() {
    queryClient.invalidateQueries({ queryKey: ["eval-metrics-summary", designProjectId] });
    queryClient.invalidateQueries({ queryKey: ["design-project", designProjectId] });
  }

  if (summaryQuery.isLoading) return <EmptyState variant="loading" />;
  if (summaryQuery.isError) return <EmptyState variant="failed" detail={String(summaryQuery.error)} />;
  if (!summaryQuery.data) return <EmptyState variant="unavailable" />;
  const summary = summaryQuery.data;

  return (
    <div className="flex flex-col gap-4">
      <p className="text-[11px] text-ink-faint">{t("metrics.subtitle")}</p>
      <ReferenceDdrPanel designProjectId={designProjectId} referenceDdrIds={referenceDdrIds} onLinked={invalidateAfterLink} />

      <section className="flex flex-col gap-2">
        <h3 className="label-caps">{t("metrics.layer.process")}</h3>
        <div className="grid gap-3 sm:grid-cols-2">
          <MetricStatTile title={t("metrics.groundingRate.title")} detail={t("metrics.groundingRate.detail")} metric={summary.process.groundingRate} />
          <div className="panel flex flex-col gap-1.5 p-4">
            <h4 className="text-sm font-semibold text-ink">{t("metrics.coverageCompleteness.title")}</h4>
            <p className="text-[11px] text-ink-faint">{t("metrics.coverageCompleteness.detail")}</p>
            {summary.process.coverageCompleteness.applicable ? (
              <>
                <p className="mt-1 text-2xl font-semibold text-ink">
                  {summary.process.coverageCompleteness.numerator} / {summary.process.coverageCompleteness.denominator}
                </p>
                <p className="mb-1 mt-1 text-[10px] font-medium uppercase tracking-wide text-ink-faint">{t("metrics.coverageCompleteness.chartTitle")}</p>
                <CoverageTiles coverageByClass={summary.process.coverageCompleteness.coverageByClass} />
              </>
            ) : (
              <EmptyState variant="unavailable" title={t("metrics.notApplicable")} detail={summary.process.coverageCompleteness.note} />
            )}
          </div>
        </div>
      </section>

      <section className="flex flex-col gap-2">
        <h3 className="label-caps">{t("metrics.layer.capability")}</h3>
        <div className="grid gap-3 sm:grid-cols-2">
          <MetricStatTile title={t("metrics.screeningAbility.title")} detail={t("metrics.screeningAbility.detail")} metric={summary.capability.screeningAbility} />
          <div className="panel flex flex-col gap-1.5 p-4">
            <h4 className="text-sm font-semibold text-ink">{t("metrics.reasonedNovelty.title")}</h4>
            <p className="text-[11px] text-ink-faint">{t("metrics.reasonedNovelty.detail")}</p>
            {summary.capability.reasonedNovelty.applicable ? (
              <>
                <p className="mt-1 text-2xl font-semibold text-ink">{Math.round((summary.capability.reasonedNovelty.value ?? 0) * 100)}%</p>
                <p className="text-[11px] text-ink-faint">{summary.capability.reasonedNovelty.numerator} / {summary.capability.reasonedNovelty.denominator}</p>
                {summary.capability.reasonedNovelty.novelGroundedGenes.length > 0 && (
                  <>
                    <p className="mt-1 text-[10px] font-medium uppercase tracking-wide text-ink-faint">{t("metrics.reasonedNovelty.genesTitle")}</p>
                    <div className="flex flex-wrap gap-1">
                      {summary.capability.reasonedNovelty.novelGroundedGenes.map((g) => (
                        <span key={g} className="rounded border border-accent bg-accent-soft px-1.5 py-0.5 font-mono text-[10px] text-accent-strong">{g}</span>
                      ))}
                    </div>
                  </>
                )}
              </>
            ) : (
              <EmptyState variant="unavailable" title={t("metrics.notApplicable")} detail={summary.capability.reasonedNovelty.note} />
            )}
          </div>
        </div>
        <ConsistencyPanel designProjectId={designProjectId} />
      </section>

      <section className="flex flex-col gap-2">
        <h3 className="label-caps">{t("metrics.layer.outcome")}</h3>
        <div className="panel flex items-start gap-3 p-4">
          <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-emerald-50 text-emerald-600">
            <FlaskConical size={18} aria-hidden />
          </div>
          <div>
            <h4 className="text-sm font-semibold text-ink">{t("metrics.outcome.title")}</h4>
            <p className="mt-1 text-[11px] leading-5 text-ink-muted">{t("metrics.outcome.detail")}</p>
          </div>
        </div>
      </section>

      <section className="flex flex-col gap-2">
        <h3 className="label-caps text-ink-faint">{t("metrics.layer.sanityCheck")}</h3>
        <div className="panel flex flex-col gap-1.5 p-3 opacity-70">
          <h4 className="text-xs font-semibold text-ink-muted">{t("metrics.reproductionRate.title")}</h4>
          <p className="text-[10px] text-ink-faint">{t("metrics.reproductionRate.detail")}</p>
          {summary.sanityCheck.reproductionRate.applicable ? (
            <p className="text-sm font-medium text-ink-muted">
              {Math.round((summary.sanityCheck.reproductionRate.value ?? 0) * 100)}% ({summary.sanityCheck.reproductionRate.numerator} / {summary.sanityCheck.reproductionRate.denominator})
            </p>
          ) : (
            <p className="text-[10px] text-ink-faint">{summary.sanityCheck.reproductionRate.note || t("metrics.notApplicable")}</p>
          )}
        </div>
      </section>
    </div>
  );
}

function MetricStatTile({ title, detail, metric }: { title: string; detail: string; metric: MetricResult }) {
  const { t } = useI18n();
  return (
    <div className="panel flex flex-col gap-1.5 p-4">
      <h4 className="text-sm font-semibold text-ink">{title}</h4>
      <p className="text-[11px] text-ink-faint">{detail}</p>
      {metric.applicable ? (
        <>
          <p className="mt-1 text-2xl font-semibold text-ink">{Math.round((metric.value ?? 0) * 100)}%</p>
          <p className="text-[11px] text-ink-faint">{metric.numerator} / {metric.denominator}</p>
          {metric.note && <p className="text-[10px] text-ink-faint">{metric.note}</p>}
        </>
      ) : (
        <EmptyState variant="unavailable" title={t("metrics.notApplicable")} detail={metric.note} />
      )}
    </div>
  );
}

const COVERAGE_STATUS_STYLE: Record<CoverageByClassEntry["status"], string> = {
  covered: "border-emerald-300 bg-emerald-50 text-emerald-700",
  excluded: "border-amber-300 bg-amber-50 text-amber-700",
  missing: "border-red-300 bg-red-50 text-state-risk",
};

function CoverageTiles({ coverageByClass }: { coverageByClass: CoverageByClassEntry[] }) {
  const { t } = useI18n();
  return (
    <div className="grid grid-cols-3 gap-1.5">
      {coverageByClass.map((c) => (
        <div key={c.strategyClass} title={c.reason || undefined} className={`rounded border px-1.5 py-1 text-[9px] font-medium leading-tight ${COVERAGE_STATUS_STYLE[c.status]}`}>
          <p className="truncate">{c.strategyClass}</p>
          <p className="mt-0.5 font-normal opacity-80">{t(`metrics.coverageCompleteness.status.${c.status}` as DictKey)}</p>
        </div>
      ))}
    </div>
  );
}

function ReferenceDdrPanel({ designProjectId, referenceDdrIds, onLinked }: { designProjectId: string; referenceDdrIds: string[]; onLinked: () => void }) {
  const { t } = useI18n();
  const [input, setInput] = useState(referenceDdrIds.join(", "));
  useEffect(() => setInput(referenceDdrIds.join(", ")), [designProjectId, referenceDdrIds]);

  const mutation = useMutation({
    mutationFn: (ids: string[]) => setReferenceDdr(designProjectId, ids),
    onSuccess: onLinked,
  });

  function submit() {
    const ids = input.split(",").map((s) => s.trim()).filter(Boolean);
    mutation.mutate(ids);
  }

  return (
    <section className="panel flex flex-col gap-2 p-4">
      <h3 className="text-sm font-semibold text-ink">{t("metrics.referenceDdr.title")}</h3>
      <p className="text-[11px] text-ink-faint">{t("metrics.referenceDdr.detail")}</p>
      <div className="flex flex-wrap items-center gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder={t("metrics.referenceDdr.placeholder")}
          className="min-w-56 flex-1 rounded-lg border border-border px-2.5 py-1.5 text-xs outline-none focus:border-accent"
        />
        <button
          type="button"
          disabled={mutation.isPending}
          onClick={submit}
          className="rounded-lg bg-accent px-3 py-1.5 text-xs font-medium text-white disabled:opacity-40"
        >
          {mutation.isPending ? t("metrics.referenceDdr.linking") : t("metrics.referenceDdr.link")}
        </button>
      </div>
      <p className="flex flex-wrap items-center gap-1 text-[11px] text-ink-faint">
        <span>{t(referenceDdrIds.length > 0 ? "metrics.referenceDdr.linked" : "metrics.referenceDdr.none")}:</span>
        {referenceDdrIds.map((id) => (
          <span key={id} className="rounded border border-border bg-surface px-1.5 py-0.5 font-mono text-[10px] text-ink-muted">{id}</span>
        ))}
      </p>
      {mutation.isError && <EmptyState variant="failed" detail={String(mutation.error)} />}
    </section>
  );
}

function ConsistencyPanel({ designProjectId }: { designProjectId: string }) {
  const { t } = useI18n();
  const [nSamples, setNSamples] = useState(5);

  const runsQuery = useQuery({
    queryKey: ["eval-metrics-consistency-runs", designProjectId],
    queryFn: () => listConsistencyRuns(designProjectId),
  });
  const runMutation = useMutation({
    mutationFn: () => runConsistencySample(designProjectId, nSamples, "frontend-user"),
    onSuccess: (run) => {
      runsQuery.refetch();
      void run;
    },
  });

  const latest = runMutation.data ?? runsQuery.data?.[0] ?? null;
  const history = runsQuery.data ?? [];

  return (
    <div className="panel flex flex-col gap-3 p-4">
      <div>
        <h4 className="text-sm font-semibold text-ink">{t("metrics.consistency.title")}</h4>
        <p className="mt-1 text-[11px] text-ink-faint">{t("metrics.consistency.detail")}</p>
      </div>
      <div className="flex flex-wrap items-center gap-2 text-xs">
        <label className="label-caps" htmlFor="consistency-n-samples">{t("metrics.consistency.nSamplesLabel")}</label>
        <input
          id="consistency-n-samples"
          type="number"
          min={1}
          max={10}
          value={nSamples}
          onChange={(e) => setNSamples(Math.max(1, Math.min(10, Number(e.target.value) || 1)))}
          className="w-16 rounded-lg border border-border px-2 py-1.5 text-xs outline-none"
        />
        <button
          type="button"
          disabled={runMutation.isPending}
          onClick={() => runMutation.mutate()}
          className="rounded-lg bg-accent px-3 py-1.5 text-xs font-medium text-white disabled:opacity-40"
        >
          {runMutation.isPending ? t("metrics.consistency.running") : t("metrics.consistency.run")}
        </button>
        <span className="text-[11px] text-ink-faint">{t("metrics.consistency.llmCallNote")}</span>
      </div>

      {runMutation.isError && <EmptyState variant="failed" detail={String(runMutation.error)} />}
      {runsQuery.isLoading && !latest && <EmptyState variant="loading" />}
      {!runMutation.isPending && !latest && runsQuery.data && history.length === 0 && (
        <EmptyState variant="first_use" title={t("metrics.consistency.noRuns")} />
      )}

      {latest && (
        <div className="flex flex-col gap-2">
          <p className="text-[11px] text-ink-faint">
            {t("metrics.consistency.samplesWithOutput")}: {latest.convergenceReport.samplesWithOutput} / {latest.nSamples}
          </p>
          {latest.convergenceReport.byStrategyClass.length > 0 ? (
            <>
              <p className="text-[10px] font-medium uppercase tracking-wide text-ink-faint">{t("metrics.consistency.byClassChartTitle")}</p>
              <div className="h-56 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={latest.convergenceReport.byStrategyClass.map((c) => ({ name: c.strategyClass, convergence: Math.round(c.convergence * 100) }))}
                    layout="vertical"
                    margin={{ left: 8, right: 24, top: 4, bottom: 4 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis type="number" domain={[0, 100]} unit="%" tick={{ fontSize: 10 }} />
                    <YAxis type="category" dataKey="name" width={150} tick={{ fontSize: 10 }} />
                    <Tooltip formatter={(v: number) => [`${v}%`, t("metrics.consistency.byClassChartTitle")]} />
                    <Bar dataKey="convergence" fill="#2563eb" radius={[0, 4, 4, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </>
          ) : (
            <EmptyState variant="unavailable" detail={latest.convergenceReport.note} />
          )}
        </div>
      )}

      {history.length > 1 && (
        <div>
          <p className="label-caps">{t("metrics.consistency.historyTitle")}</p>
          <ul className="mt-1 flex flex-col gap-1 text-[11px] text-ink-faint">
            {history.map((r) => (
              <li key={r.runId} className="flex items-center justify-between rounded border border-border px-2 py-1">
                <span className="font-mono">{r.runId}</span>
                <span>{r.nSamples} · {new Date(r.createdAt * 1000).toLocaleString()}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
