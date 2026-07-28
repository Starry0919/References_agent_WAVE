import { BACKEND_CAPABILITIES } from "@/registry/modules";
import { useBackendHealth } from "@/state/BackendHealth";
import { useI18n } from "@/lib/i18n";
import { StatusBadge, type BadgeStatus } from "./StatusBadge";

/**
 * Renders a backend capability's honest availability (prompt §4A.1 point
 * 6, §15.2 mapping matrix `Status` column) - never silently swapped for a
 * fabricated success state. Combines the static Repository-Audit roster
 * with the live `/api/health` connectivity probe: if the backend itself is
 * down, every capability downgrades to `unavailable` regardless of its
 * static rating.
 */
export function CapabilityState({ domain, compact }: { domain: string; compact?: boolean }) {
  const { connected, checking } = useBackendHealth();
  const { t } = useI18n();
  const entry = BACKEND_CAPABILITIES[domain];

  if (checking) return <StatusBadge status="unclear" label={t("capability.checking")} />;
  if (!connected) return <StatusBadge status="unavailable" label={t("capability.disconnected")} />;
  if (!entry) return <StatusBadge status="unclear" label={t("capability.unregistered")} />;

  const status: BadgeStatus = entry.availability;
  if (compact) return <StatusBadge status={status} />;
  return (
    <div className="flex items-start gap-2">
      <StatusBadge status={status} />
      <span className="text-xs text-ink-muted">{t(entry.reasonKey)}</span>
    </div>
  );
}
