import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAppStore } from "../store/useAppStore";
import { ANALYSIS_STAGES, stageLabelFor } from "../lib/analysisStages";

export default function AnalyzingPage() {
  const navigate = useNavigate();
  const analysis = useAppStore((s) => s.analysis);

  useEffect(() => {
    if (!useAppStore.getState().analysis) {
      navigate("/", { replace: true });
      return;
    }

    const timer = window.setInterval(() => {
      const state = useAppStore.getState();
      if (!state.analysis) {
        window.clearInterval(timer);
        return;
      }
      if (state.analysis.stageIndex >= ANALYSIS_STAGES.length - 1) {
        window.clearInterval(timer);
        const report = useAppStore.getState().completeAnalysis();
        if (report) navigate(`/report/${report.id}`, { replace: true });
      } else {
        state.advanceAnalysis();
      }
    }, 900);

    return () => window.clearInterval(timer);
  }, [navigate]);

  if (!analysis) return null;

  return (
    <div className="flex min-h-[50svh] flex-col items-center justify-center gap-6 text-center">
      <div className="flex w-full max-w-[360px] flex-col items-center gap-6">
        <div
          className="h-1 w-full overflow-hidden rounded-sm bg-line"
          role="progressbar"
          aria-valuenow={analysis.progress}
          aria-valuemin={0}
          aria-valuemax={100}
          aria-label="检查进度"
        >
          <div
            className="h-full bg-accent transition-[width] duration-200 ease-out"
            style={{ width: `${analysis.progress}%` }}
          />
        </div>
        <p className="m-0 text-body text-ink">
          {stageLabelFor(analysis.stageIndex)}
        </p>
        <p
          className="m-0 truncate text-small text-ink-3"
          title={analysis.filename}
        >
          {analysis.filename}
        </p>
        <p className="m-0 text-caption text-ink-3">
          可离开本页，稍后返回将继续检查
        </p>
      </div>
    </div>
  );
}
