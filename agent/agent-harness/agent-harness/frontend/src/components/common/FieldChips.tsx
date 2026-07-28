/**
 * Renders loosely-typed metric/constraint objects as small scannable
 * chips instead of a raw `JSON.stringify(...)` dump - the backend returns
 * these as free-form `Record<string, unknown>[]` (primary/secondary
 * metrics, hard constraints) or a flat `Record<string, unknown>` (objective
 * vectors, hard-constraint results), so nothing here assumes a fixed
 * schema; it just picks the most human-readable key it can find and falls
 * back to compact key:value pairs otherwise.
 */
const PRIMARY_KEYS = ["metric", "constraint", "name", "parameter", "endpoint"];
const SECONDARY_KEYS = ["unit", "type", "target", "direction", "value"];

function summarizeField(item: Record<string, unknown>): string {
  const primaryKey = PRIMARY_KEYS.find((k) => item[k] !== undefined && item[k] !== null && item[k] !== "");
  if (primaryKey) {
    const secondaryKey = SECONDARY_KEYS.find((k) => k !== primaryKey && item[k] !== undefined && item[k] !== null && item[k] !== "");
    const primary = String(item[primaryKey]);
    return secondaryKey ? `${primary} (${String(item[secondaryKey])})` : primary;
  }
  const entries = Object.entries(item).filter(([, v]) => v !== null && v !== undefined && v !== "");
  if (entries.length === 0) return "—";
  return entries.map(([k, v]) => `${k}: ${formatValue(v)}`).join(" · ");
}

function formatValue(v: unknown): string {
  if (v === null || v === undefined) return "—";
  if (typeof v === "object") return JSON.stringify(v);
  return String(v);
}

export function FieldChips({ items, emptyLabel }: { items: Record<string, unknown>[]; emptyLabel: string }) {
  if (items.length === 0) return <span className="text-ink-faint">{emptyLabel}</span>;
  return (
    <div className="flex flex-wrap gap-1">
      {items.map((item, i) => (
        <span key={i} className="rounded border border-border bg-surface-sunken px-1.5 py-0.5 text-[11px] text-ink">
          {summarizeField(item)}
        </span>
      ))}
    </div>
  );
}

export function KeyValueChips({ record, emptyLabel }: { record: Record<string, unknown>; emptyLabel: string }) {
  const entries = Object.entries(record);
  if (entries.length === 0) return <span className="text-ink-faint">{emptyLabel}</span>;
  return (
    <div className="flex flex-wrap gap-1">
      {entries.map(([k, v]) => (
        <span key={k} className="rounded border border-border bg-surface-sunken px-1.5 py-0.5 text-[11px] text-ink">
          <span className="text-ink-faint">{k}:</span> {formatValue(v)}
        </span>
      ))}
    </div>
  );
}
