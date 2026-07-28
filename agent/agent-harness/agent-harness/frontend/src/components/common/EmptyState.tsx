import type { LucideIcon } from "lucide-react";
import { Loader2, Inbox, SearchX, AlertTriangle, WifiOff, Lock, XCircle, Ban, History, PauseCircle } from "lucide-react";
import { useI18n, type DictKey } from "@/lib/i18n";

/**
 * Every "no content" region on every page must pick one of these variants
 * (prompt §14.4 - "禁止将 empty state 统一写成 No data"). Each variant has
 * its own icon/copy so users can tell "nothing exists yet" apart from
 * "the backend is down" apart from "you don't have permission".
 */
export type EmptyVariant =
  | "loading"
  | "first_use"
  | "no_result"
  | "incomplete"
  | "disconnected"
  | "permission_denied"
  | "failed"
  | "unavailable"
  | "stale"
  | "partial";

const VARIANT: Record<EmptyVariant, { icon: LucideIcon; defaultTitleKey: DictKey; spin?: boolean }> = {
  loading: { icon: Loader2, defaultTitleKey: "empty.loading", spin: true },
  first_use: { icon: Inbox, defaultTitleKey: "empty.first_use" },
  no_result: { icon: SearchX, defaultTitleKey: "empty.no_result" },
  incomplete: { icon: AlertTriangle, defaultTitleKey: "empty.incomplete" },
  disconnected: { icon: WifiOff, defaultTitleKey: "empty.disconnected" },
  permission_denied: { icon: Lock, defaultTitleKey: "empty.permission_denied" },
  failed: { icon: XCircle, defaultTitleKey: "empty.failed" },
  unavailable: { icon: Ban, defaultTitleKey: "empty.unavailable" },
  stale: { icon: History, defaultTitleKey: "empty.stale" },
  partial: { icon: PauseCircle, defaultTitleKey: "empty.partial" },
};

export function EmptyState({
  variant,
  title,
  detail,
  action,
}: {
  variant: EmptyVariant;
  title?: string;
  detail?: string;
  action?: React.ReactNode;
}) {
  const { t } = useI18n();
  const cfg = VARIANT[variant];
  const Icon = cfg.icon;
  return (
    <div className="flex flex-col items-center justify-center gap-2 rounded border border-dashed border-border px-6 py-10 text-center">
      <Icon size={22} className={`text-ink-faint ${cfg.spin ? "animate-spin" : ""}`} aria-hidden />
      <p className="text-sm font-medium text-ink">{title ?? t(cfg.defaultTitleKey)}</p>
      {detail && <p className="max-w-md text-xs text-ink-muted">{detail}</p>}
      {action}
    </div>
  );
}
