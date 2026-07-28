import type { ReactNode } from "react";
import { useI18n, type DictKey } from "@/lib/i18n";

/**
 * Structural helper enforcing the design-acceptance test from prompt
 * §3.4: every major panel must be able to answer Now / Why / Next / Basis
 * / State. Any of the five slots may be omitted only when it is genuinely
 * not applicable to that panel - never silently dropped.
 */
export function NowWhyNext({
  now,
  why,
  next,
  basis,
  state,
}: {
  now?: ReactNode;
  why?: ReactNode;
  next?: ReactNode;
  basis?: ReactNode;
  state?: ReactNode;
}) {
  const { t } = useI18n();
  const rows: Array<[DictKey, ReactNode | undefined]> = [
    ["common.now", now],
    ["common.why", why],
    ["common.next", next],
    ["common.basis", basis],
    ["common.state", state],
  ];
  const present = rows.filter(([, v]) => v !== undefined);
  if (present.length === 0) return null;
  return (
    <dl className="grid grid-cols-[auto_1fr] gap-x-3 gap-y-1.5 text-xs">
      {present.map(([labelKey, value]) => (
        <div key={labelKey} className="contents">
          <dt className="label-caps pt-0.5">{t(labelKey)}</dt>
          <dd className="text-ink">{value}</dd>
        </div>
      ))}
    </dl>
  );
}
