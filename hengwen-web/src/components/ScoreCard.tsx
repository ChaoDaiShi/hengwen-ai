import type { Verdict } from "../types/report";
import { VERDICT_LABELS } from "../lib/verdict";
import { useCountUp } from "../hooks/useCountUp";

const VERDICT_COLOR: Record<Verdict, string> = {
  pass: "var(--success)",
  pending: "var(--warning)",
  fail: "var(--error)",
};

interface ScoreCardProps {
  score: number;
  verdict: Verdict;
}

export default function ScoreCard({ score, verdict }: ScoreCardProps) {
  const color = VERDICT_COLOR[verdict];
  const displayed = useCountUp(score);

  return (
    <div className="flex flex-col gap-4 border border-line bg-surface p-6 shadow-paper">
      <div className="flex items-baseline gap-2">
        <span className="font-mono text-[72px] font-normal leading-[1.1] tabular-nums text-ink max-md:text-[56px]">
          {displayed}
        </span>
        <span className="text-small tabular-nums text-ink-3">/ 100</span>
      </div>
      <div
        className="h-1 w-full overflow-hidden rounded-sm bg-line"
        role="progressbar"
        aria-valuenow={displayed}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label="规范得分"
      >
        <div
          className="h-full bg-accent transition-[width] duration-fast ease-out"
          style={{ width: `${displayed}%` }}
        />
      </div>
      <p className="m-0 text-body font-medium" style={{ color }}>
        {VERDICT_LABELS[verdict]}
      </p>
    </div>
  );
}
