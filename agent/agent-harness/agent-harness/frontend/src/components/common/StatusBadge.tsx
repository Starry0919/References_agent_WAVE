import {
  CheckCircle2,
  CircleDashed,
  Clock,
  AlertTriangle,
  Ban,
  XCircle,
  HelpCircle,
  History,
  type LucideIcon,
} from "lucide-react";
import { useI18n, type DictKey } from "@/lib/i18n";

/**
 * The single status->color/icon/text mapping for the whole app (prompt
 * §12.2, §13.4: "不允许每页用不同颜色表达不同语义"; "不要只依赖颜色传达
 * 状态；同时使用文本和图标"). Every page must render status through this
 * component instead of inventing a local badge.
 */
export type BadgeStatus =
  | "available"
  | "draft"
  | "generated"
  | "under_review"
  | "needs_revision"
  | "approved"
  | "rejected"
  | "active"
  | "completed"
  | "blocked"
  | "waiting_for_human"
  | "waiting_for_experiment"
  | "unavailable"
  | "out_of_domain"
  | "stale"
  | "superseded"
  | "failed"
  | "not_started"
  | "partial"
  | "absent"
  | "unclear"
  // Page 3 — real KnowledgeClaim statuses (harness/learning/models.py
  // KNOWLEDGE_CLAIM_STATUSES). Additive per ADR-KC-001; never remap an
  // existing entry.
  | "project_candidate"
  | "lab_candidate"
  | "lab_approved"
  | "retracted";

const CONFIG: Record<BadgeStatus, { labelKey: DictKey; icon: LucideIcon; className: string }> = {
  available: { labelKey: "badge.available", icon: CheckCircle2, className: "bg-emerald-50 text-state-success border-emerald-300" },
  draft: { labelKey: "badge.draft", icon: CircleDashed, className: "bg-surface-sunken text-ink-muted border-border" },
  generated: { labelKey: "badge.generated", icon: CircleDashed, className: "bg-accent-soft text-accent-strong border-accent" },
  under_review: { labelKey: "badge.under_review", icon: Clock, className: "bg-amber-50 text-state-caution border-amber-300" },
  needs_revision: { labelKey: "badge.needs_revision", icon: AlertTriangle, className: "bg-amber-50 text-state-caution border-amber-300" },
  approved: { labelKey: "badge.approved", icon: CheckCircle2, className: "bg-emerald-50 text-state-success border-emerald-300" },
  rejected: { labelKey: "badge.rejected", icon: XCircle, className: "bg-red-50 text-state-risk border-red-300" },
  active: { labelKey: "badge.active", icon: Clock, className: "bg-accent-soft text-accent-strong border-accent" },
  completed: { labelKey: "badge.completed", icon: CheckCircle2, className: "bg-emerald-50 text-state-success border-emerald-300" },
  blocked: { labelKey: "badge.blocked", icon: Ban, className: "bg-slate-100 text-state-blocked border-slate-300" },
  waiting_for_human: { labelKey: "badge.waiting_for_human", icon: Clock, className: "bg-amber-50 text-state-caution border-amber-300" },
  waiting_for_experiment: { labelKey: "badge.waiting_for_experiment", icon: Clock, className: "bg-amber-50 text-state-caution border-amber-300" },
  unavailable: { labelKey: "badge.unavailable", icon: Ban, className: "bg-slate-100 text-state-unavailable border-slate-300" },
  out_of_domain: { labelKey: "badge.out_of_domain", icon: AlertTriangle, className: "bg-slate-100 text-state-unavailable border-slate-300" },
  stale: { labelKey: "badge.stale", icon: History, className: "bg-amber-50 text-state-stale border-amber-300" },
  superseded: { labelKey: "badge.superseded", icon: History, className: "bg-slate-100 text-ink-muted border-slate-300" },
  failed: { labelKey: "badge.failed", icon: XCircle, className: "bg-red-50 text-state-risk border-red-300" },
  not_started: { labelKey: "badge.not_started", icon: CircleDashed, className: "bg-surface-sunken text-ink-faint border-border" },
  partial: { labelKey: "badge.partial", icon: HelpCircle, className: "bg-amber-50 text-state-caution border-amber-300" },
  absent: { labelKey: "badge.absent", icon: Ban, className: "bg-slate-100 text-state-unavailable border-slate-300" },
  unclear: { labelKey: "badge.unclear", icon: HelpCircle, className: "bg-slate-100 text-ink-muted border-slate-300" },
  project_candidate: { labelKey: "badge.project_candidate", icon: CircleDashed, className: "bg-surface-sunken text-ink-muted border-border" },
  lab_candidate: { labelKey: "badge.lab_candidate", icon: Clock, className: "bg-amber-50 text-state-caution border-amber-300" },
  lab_approved: { labelKey: "badge.lab_approved", icon: CheckCircle2, className: "bg-emerald-50 text-state-success border-emerald-300" },
  retracted: { labelKey: "badge.retracted", icon: History, className: "bg-slate-100 text-ink-muted border-slate-300" },
};

export function StatusBadge({ status, label, hint }: { status: BadgeStatus; label?: string; hint?: string }) {
  const { t } = useI18n();
  const cfg = CONFIG[status] ?? CONFIG.unclear;
  const Icon = cfg.icon;
  return (
    <span
      className={`inline-flex items-center gap-1 rounded border px-1.5 py-0.5 text-[11px] font-medium leading-none ${cfg.className} ${hint ? "cursor-help" : ""}`}
      title={hint}
    >
      <Icon size={12} strokeWidth={2} aria-hidden />
      {label ?? t(cfg.labelKey)}
    </span>
  );
}
