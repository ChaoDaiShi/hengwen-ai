export interface AnalysisStage {
  key: string;
  label: string;
  progress: number;
}

export const ANALYSIS_STAGES: AnalysisStage[] = [
  { key: "read", label: "正在读取文档…", progress: 20 },
  { key: "format", label: "正在检查格式规范…", progress: 45 },
  { key: "citation", label: "正在核查引用与文献…", progress: 70 },
  { key: "suggestion", label: "正在生成修改建议…", progress: 90 },
];

export function stageLabelFor(index: number): string {
  if (index < 0) return ANALYSIS_STAGES[0].label;
  if (index >= ANALYSIS_STAGES.length) return "分析完成";
  return ANALYSIS_STAGES[index].label;
}

export function progressFor(index: number): number {
  if (index < 0) return 0;
  if (index >= ANALYSIS_STAGES.length) return 100;
  return ANALYSIS_STAGES[index].progress;
}
