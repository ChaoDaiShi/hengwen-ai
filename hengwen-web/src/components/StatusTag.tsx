import type { Verdict } from "../types/report";
import { VERDICT_LABELS } from "../lib/verdict";

const COLOR: Record<Verdict, string> = {
  pass: "var(--success)",
  pending: "var(--warning)",
  fail: "var(--error)",
};

export default function StatusTag({ verdict }: { verdict: Verdict }) {
  const color = COLOR[verdict];
  return (
    <span
      className="inline-flex items-center rounded-sm px-2 py-0.5 font-medium text-caption"
      style={{
        color,
        backgroundColor: `color-mix(in srgb, ${color} 10%, transparent)`,
      }}
    >
      {VERDICT_LABELS[verdict]}
    </span>
  );
}
