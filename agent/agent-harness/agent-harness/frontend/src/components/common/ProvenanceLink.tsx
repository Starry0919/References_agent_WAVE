import { Link } from "react-router-dom";
import { GitCommitHorizontal } from "lucide-react";

/**
 * A stable, copyable reference to a scientific object's identity/version
 * (prompt §4.1, §6.3 deep links). Renders id + version as a monospace
 * chip that deep-links to that object's canonical location.
 */
export function ProvenanceLink({
  id,
  version,
  to,
  label,
}: {
  id: string;
  version?: number | string;
  to: string;
  label?: string;
}) {
  return (
    <Link
      to={to}
      className="inline-flex items-center gap-1 rounded border border-border bg-surface-sunken px-1.5 py-0.5 font-mono text-[11px] text-ink-muted hover:border-accent hover:text-accent-strong"
      title={label ?? id}
    >
      <GitCommitHorizontal size={11} aria-hidden />
      {id}
      {version !== undefined && <span className="text-ink-faint">v{version}</span>}
    </Link>
  );
}
