export type Severity = "error" | "warning" | "info";

export type Verdict = "pass" | "pending" | "fail";

export interface Issue {
  id: string;
  severity: Severity;
  title: string;
  location: string;
  summary: string;
  original: string;
  suggestion: string;
}

export interface Report {
  id: string;
  filename: string;
  fileType: ".docx" | ".pdf" | ".md";
  checkedAt: string;
  wordCount: number;
  score: number;
  verdict: Verdict;
  issues: Issue[];
}

export interface AnalysisTask {
  id: string;
  filename: string;
  fileType: Report["fileType"];
  stageIndex: number;
  progress: number;
  startedAt: string;
}

export interface Settings {
  orgName: string;
  standard: string;
  checkFormat: boolean;
  checkCitation: boolean;
  checkPlagiarism: boolean;
  autoReport: boolean;
}
