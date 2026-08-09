import type { Verdict } from "../types/report";
import { VERDICT_LABELS } from "../lib/verdict";

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
  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-baseline gap-2">
        <span className="font-mono text-[72px] font-normal leading-[1.1] text-ink max-md:text-[56px]">
          {score}
        </span>
        <span className="text-small text-ink-3">/ 100</span>
      </div>
      <div
        className="h-1 w-full overflow-hidden rounded-sm bg-line"
        role="progressbar"
        aria-valuenow={score}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label="规范得分"
      >
        <div
          className="h-full bg-accent transition-[width] duration-200 ease-out"
          style={{ width: `${score}%` }}
        />
      </div>
      <p className="m-0 text-body font-medium" style={{ color }}>
        {VERDICT_LABELS[verdict]}
      </p>
    </div>
  );
}
