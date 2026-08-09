import type { Verdict } from "../types/report";

export const PASS_THRESHOLD = 90;
export const PENDING_THRESHOLD = 75;

export function scoreToVerdict(score: number): Verdict {
  if (score >= PASS_THRESHOLD) return "pass";
  if (score >= PENDING_THRESHOLD) return "pending";
  return "fail";
}

export const VERDICT_LABELS: Record<Verdict, string> = {
  pass: "通过",
  pending: "存疑",
  fail: "需修改",
};
