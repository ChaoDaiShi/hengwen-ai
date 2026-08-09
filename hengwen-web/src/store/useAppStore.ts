import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { AnalysisTask, Report, Settings } from "../types/report";
import { SEED_REPORTS, createMockReport } from "../api/mock";
import { ANALYSIS_STAGES } from "../lib/analysisStages";

export const DEFAULT_SETTINGS: Settings = {
  orgName: "",
  standard: "本科毕业论文规范（默认）",
  checkFormat: false,
  checkCitation: false,
  checkPlagiarism: false,
  autoReport: false,
};

interface AppState {
  settings: Settings;
  reports: Report[];
  analysis: AnalysisTask | null;
  updateSettings: (patch: Partial<Settings>) => void;
  addReport: (report: Report) => void;
  startAnalysis: (input: {
    filename: string;
    fileType: Report["fileType"];
  }) => void;
  advanceAnalysis: () => void;
  completeAnalysis: () => Report | null;
  cancelAnalysis: () => void;
}

export const useAppStore = create<AppState>()(
  persist(
    (set, get) => ({
      settings: DEFAULT_SETTINGS,
      reports: SEED_REPORTS,
      analysis: null,

      updateSettings: (patch) =>
        set((state) => ({ settings: { ...state.settings, ...patch } })),

      addReport: (report) =>
        set((state) => ({ reports: [report, ...state.reports] })),

      startAnalysis: ({ filename, fileType }) =>
        set({
          analysis: {
            id: `task-${Date.now()}`,
            filename,
            fileType,
            stageIndex: 0,
            progress: ANALYSIS_STAGES[0].progress,
            startedAt: new Date().toISOString(),
          },
        }),

      advanceAnalysis: () =>
        set((state) => {
          if (!state.analysis) return state;
          const next = state.analysis.stageIndex + 1;
          if (next >= ANALYSIS_STAGES.length) return state;
          return {
            analysis: {
              ...state.analysis,
              stageIndex: next,
              progress: ANALYSIS_STAGES[next].progress,
            },
          };
        }),

      completeAnalysis: () => {
        const task = get().analysis;
        if (!task) return null;
        const report = createMockReport({
          filename: task.filename,
          fileType: task.fileType,
        });
        set((state) => ({
          reports: [report, ...state.reports],
          analysis: null,
        }));
        return report;
      },

      cancelAnalysis: () => set({ analysis: null }),
    }),
    {
      name: "hengwen-settings",
      partialize: (state) => ({
        settings: state.settings,
        reports: state.reports,
        analysis: state.analysis,
      }),
    },
  ),
);
