import { createRun, startDesign, startDiagnosis, type WorkflowRun } from "@/api/orchestrator";

const ACTOR_ID = "frontend-user";

/** Fixed default chassis (E. coli K-12) per user direction: every project
 * should be able to run diagnosis + engineering design automatically from
 * its target product alone, without asking for a host organism up front. */
export const DEFAULT_HOST = "E. coli K-12";

const SUFFICIENT_DATA = {
  hasBaseline: true, hasGenotype: true, hasCondition: true, hasTime: true, hasQc: true, hasKeyPhenotype: true,
};

/** Creates a fresh `WorkflowRun` and drives it through diagnosis alone
 * (session -> hypotheses -> decision, `DiagnosisAdapter.start()` -
 * already a single auto-chaining call server-side). `phenotype`, when
 * given, should come from a real, already-retrieved knowledge-base idea
 * (`KnowledgeIdea.title`/`.summary`) rather than a generic placeholder -
 * it becomes the phenotype node's label in the mechanism graph, so a
 * concrete, evidence-sourced framing is more honest than an invented one.
 * Stops (without throwing) at `DIAGNOSIS` if the diagnosis adapter itself
 * stopped early (`data_required` needs more data, `human_review_required`
 * needs a human) - those are real, by-design checkpoints, not failures. */
export async function startAutoDiagnosis(projectId: string, targetProduct: string, phenotype?: string): Promise<WorkflowRun> {
  let run = await createRun({ projectId, actorId: ACTOR_ID, targetProduct, host: DEFAULT_HOST });
  run = await startDiagnosis(run.workflowRunId, {
    expectedVersion: run.version,
    actorId: ACTOR_ID,
    biologicalSystem: { species: "E. coli", strain: "K-12" },
    phenotype: phenotype || `${targetProduct} yield/titer below target`,
    targetProduct,
    host: DEFAULT_HOST,
    dataSufficiency: SUFFICIENT_DATA,
  });
  return run;
}

/** Drives a fresh `WorkflowRun` all the way from "just created" through
 * diagnosis and, if diagnosis reached a decision, through engineering
 * design (handoff -> objectives -> strategies -> portfolio,
 * `DesignAdapter.start()`). Evaluation/build/human-approval are never
 * auto-run - those are required governance gates, not unwired
 * automation. */
export async function autoRunDiagnosisAndDesign(projectId: string, targetProduct: string): Promise<WorkflowRun> {
  let run = await startAutoDiagnosis(projectId, targetProduct);
  if (run.currentPhase !== "DESIGN") return run;

  run = await startDesign(run.workflowRunId, {
    expectedVersion: run.version,
    actorId: ACTOR_ID,
    chassis: "E. coli",
    chassisVersionOrGenotype: "K-12",
    primaryMetrics: [{ metric: "titer", unit: "g/L" }],
    hardConstraints: [{ constraint: "no essential gene knockout", type: "no_essential_gene_knockout" }],
  });
  return run;
}
