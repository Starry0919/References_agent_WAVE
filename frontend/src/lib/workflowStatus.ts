import type { BadgeStatus } from "@/components/common/StatusBadge";

/**
 * Maps the raw backend state-machine strings (diagnosis's 18-state
 * `DIAGNOSIS_STATES` / design's 18-state `DESIGN_WORKFLOW_STATES`, plus
 * candidate/strategy sub-statuses) onto the single project-wide
 * `BadgeStatus` vocabulary `StatusBadge` renders - per that component's
 * own docstring, no page may invent a local color mapping.
 */

const DIAGNOSIS_STATUS_MAP: Record<string, BadgeStatus> = {
  intake: "active",
  data_required: "blocked",
  observations_normalized: "active",
  hypotheses_generated: "active",
  evidence_assessed: "active",
  model_evidence_pending: "active",
  hypotheses_ranked: "active",
  test_selection_required: "active",
  test_planned: "active",
  awaiting_test_result: "waiting_for_experiment",
  belief_updated: "active",
  model_conflicted: "needs_revision",
  human_review_required: "waiting_for_human",
  actionable: "completed",
  evidence_limited: "partial",
  handoff_ready: "completed",
  handed_off_to_design: "completed",
  closed: "completed",
};

const DESIGN_STATUS_MAP: Record<string, BadgeStatus> = {
  diagnostic_blocked: "blocked",
  objective_draft: "draft",
  strategy_generated: "active",
  portfolio_generated: "active",
  evaluation_in_progress: "active",
  revision_required: "needs_revision",
  portfolio_evaluated: "active",
  planning_ready: "active",
  awaiting_human_approval: "waiting_for_human",
  approved_for_build: "approved",
  rejected: "rejected",
  build_in_progress: "active",
  test_pending: "waiting_for_experiment",
  tested: "active",
  learning_update: "active",
  next_iteration: "active",
  diagnosis_reopened: "stale",
  completed: "completed",
};

const CANDIDATE_STATUS_MAP: Record<string, BadgeStatus> = {
  proposed: "draft",
  revised: "draft",
  selected: "active",
  rejected: "rejected",
  approved_for_build: "approved",
  built: "completed",
  tested: "completed",
  retired: "superseded",
};

const STRATEGY_STATUS_MAP: Record<string, BadgeStatus> = {
  proposed: "draft",
  selected: "active",
  rejected: "rejected",
};

export function diagnosisStatusToBadge(status: string): BadgeStatus {
  return DIAGNOSIS_STATUS_MAP[status] ?? "unclear";
}

export function designStatusToBadge(status: string): BadgeStatus {
  return DESIGN_STATUS_MAP[status] ?? "unclear";
}

export function candidateStatusToBadge(status: string): BadgeStatus {
  return CANDIDATE_STATUS_MAP[status] ?? "unclear";
}

export function strategyStatusToBadge(status: string): BadgeStatus {
  return STRATEGY_STATUS_MAP[status] ?? "unclear";
}
