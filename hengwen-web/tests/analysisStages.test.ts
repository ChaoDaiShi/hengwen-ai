import { describe, expect, it } from "vitest";
import {
  ANALYSIS_STAGES,
  progressFor,
  stageLabelFor,
} from "../src/lib/analysisStages";

describe("analysisStages", () => {
  it("defines at least four distinct stages", () => {
    expect(ANALYSIS_STAGES.length).toBeGreaterThanOrEqual(4);
  });

  it("uses restrained copy without AI-hype phrasing", () => {
    for (const stage of ANALYSIS_STAGES) {
      expect(stage.label.endsWith("…")).toBe(true);
      expect(stage.label).not.toContain("智能");
      expect(stage.label).not.toContain("请稍候");
    }
  });

  it("progress is monotonic and within bounds", () => {
    const progress = ANALYSIS_STAGES.map((s) => s.progress);
    for (let i = 1; i < progress.length; i++) {
      expect(progress[i]).toBeGreaterThan(progress[i - 1]);
    }
    expect(progress[progress.length - 1]).toBeLessThanOrEqual(90);
  });

  it("stageLabelFor clamps out-of-range indexes", () => {
    expect(stageLabelFor(-1)).toBe(ANALYSIS_STAGES[0].label);
    expect(stageLabelFor(ANALYSIS_STAGES.length)).toBe("分析完成");
  });

  it("progressFor maps completed run to 100", () => {
    expect(progressFor(-1)).toBe(0);
    expect(progressFor(ANALYSIS_STAGES.length)).toBe(100);
  });
});
