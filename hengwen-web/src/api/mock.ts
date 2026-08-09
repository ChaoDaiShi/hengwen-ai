import type { Issue, Report, Severity } from "../types/report";

const now = () => new Date().toISOString();

const issue = (
  severity: Severity,
  title: string,
  location: string,
  summary: string,
  original: string,
  suggestion: string,
): Issue => ({
  id: `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
  severity,
  title,
  location,
  summary,
  original,
  suggestion,
});

export const SEED_REPORTS: Report[] = [
  {
    id: "seed-001",
    filename: "基于深度学习的情感分析研究.docx",
    fileType: ".docx",
    checkedAt: "2026-08-08T14:32:00.000Z",
    wordCount: 12480,
    score: 87,
    verdict: "pending",
    issues: [
      issue(
        "error",
        "参考文献著录格式不符合 GB/T 7714",
        "参考文献 · 条目 12",
        "作者名后缺少出版年，卷期页码顺序有误",
        "张三. 情感分析综述. 计算机学报, 2020",
        "张三. 情感分析综述[J]. 计算机学报, 2020, 43(5): 112-130.",
      ),
      issue(
        "error",
        "章节标题未使用规范样式",
        "第 3 章 · 第 1 节",
        "标题字体与正文字体混用，未套用标题样式",
        "3.1 数据集的构建与预处理方法研究",
        "3.1 数据集构建与预处理",
      ),
      issue(
        "warning",
        "摘要未包含关键词",
        "摘要 · 文末",
        "摘要结尾缺少中文关键词三至五个",
        "……本研究验证了模型的有效性。",
        "……本研究验证了模型的有效性。\n关键词：深度学习；情感分析；文本分类",
      ),
      issue(
        "warning",
        "图 3-2 编号与正文引用不符",
        "第 3 章 · 第 47 行",
        "正文引用图 3-3，但图中实际编号为图 3-2",
        "如图 3-3 所示，准确率随轮次上升。",
        "如图 3-2 所示，准确率随轮次上升。",
      ),
      issue(
        "info",
        "可用被动语态使表述更正式",
        "第 2 章 · 第 15 行",
        "第一人称表述可改为被动语态",
        "我们设计了对比实验来验证假设。",
        "设计了对比实验以验证假设。",
      ),
    ],
  },
  {
    id: "seed-002",
    filename: "城市交通拥堵治理对策研究.pdf",
    fileType: ".pdf",
    checkedAt: "2026-08-07T09:05:00.000Z",
    wordCount: 9632,
    score: 94,
    verdict: "pass",
    issues: [
      issue(
        "warning",
        "引用文献出版年份与原文不符",
        "§2.3 · 第 47 行",
        "正文引用为 2021，文献列表中为 2020",
        "据 Wang（2021）的研究表明……",
        "据 Wang（2020）的研究表明……",
      ),
      issue(
        "info",
        "术语「智能网联」前后不一致",
        "§4.1 · 第 12 行",
        "前文使用「智能网联汽车」，此处简写为「智联汽车」",
        "智联汽车在交叉口的通行效率显著提升。",
        "智能网联汽车在交叉口的通行效率显著提升。",
      ),
    ],
  },
];

const GENERATED_TEMPLATES: Array<{
  score: number;
  verdict: Report["verdict"];
  issues: Issue[];
}> = [
  {
    score: 91,
    verdict: "pass",
    issues: [
      issue(
        "warning",
        "结论部分缺少研究展望",
        "结论 · 最后一段",
        "建议在结论末尾补充两至三句研究展望",
        "……研究达到了预期目标。",
        "……研究达到了预期目标。未来可进一步探讨多模态数据的融合方法。",
      ),
      issue(
        "info",
        "缩写首次出现未给出全称",
        "摘要 · 第 3 行",
        "LSTM 首次出现时未注明全称",
        "采用 LSTM 模型进行序列建模。",
        "采用长短期记忆网络（LSTM）模型进行序列建模。",
      ),
    ],
  },
  {
    score: 78,
    verdict: "pending",
    issues: [
      issue(
        "error",
        "目录页码与正文不一致",
        "目录 · 第 4 行",
        "目录第 3 章页码为 42，正文实际起始页为 45",
        "3　研究方法…………………………………… 42",
        "3　研究方法…………………………………… 45",
      ),
      issue(
        "error",
        "表格未编号且缺少题注",
        "第 4 章 · 表 4",
        "表格上方缺少编号与题注",
        "【表格区域】",
        "表 4-1 各算法性能对比\n【表格区域】",
      ),
      issue(
        "warning",
        "中英文摘要页眉缺失",
        "页眉 · 第 2 页",
        "英文摘要页缺少校名页眉",
        "（页眉为空）",
        "XX大学硕士学位论文（英文摘要页页眉）",
      ),
      issue(
        "warning",
        "引文句号位置错误",
        "§2.5 · 第 89 行",
        "句号应置于引号外",
        "作者指出「该方法有效」。",
        "作者指出「该方法有效」。",
      ),
      issue(
        "info",
        "可用同义替换避免重复用词",
        "§3.2 · 第 21 行",
        "「重要」在段落中重复三次",
        "实验结果具有重要意义，对后续工作十分重要。",
        "实验结果具有重要意义，对后续工作十分关键。",
      ),
    ],
  },
];

export function createMockReport(input: {
  filename: string;
  fileType: Report["fileType"];
  wordCount?: number;
}): Report {
  const template =
    GENERATED_TEMPLATES[Math.floor(Math.random() * GENERATED_TEMPLATES.length)];
  return {
    id: `report-${Date.now()}`,
    filename: input.filename,
    fileType: input.fileType,
    checkedAt: now(),
    wordCount: input.wordCount ?? 8000 + Math.floor(Math.random() * 6000),
    score: template.score,
    verdict: template.verdict,
    issues: template.issues.map((item) => ({
      ...item,
      id: `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
    })),
  };
}
