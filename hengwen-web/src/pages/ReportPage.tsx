import { useNavigate, useParams } from "react-router-dom";
import { Button } from "antd";
import ScoreCard from "../components/ScoreCard";
import IssueList from "../components/IssueList";
import StatusTag from "../components/StatusTag";
import { useAppStore } from "../store/useAppStore";
import { formatDateTime, formatWordCount } from "../lib/format";

export default function ReportPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const report = useAppStore((s) => s.reports.find((r) => r.id === id));

  if (!report) {
    return (
      <div className="flex min-h-[40svh] flex-col items-center justify-center gap-6 text-center">
        <p className="m-0 text-body text-ink-3">未找到该检查报告</p>
        <Button onClick={() => navigate("/")}>返回首页</Button>
      </div>
    );
  }

  const title = report.filename.replace(/\.[^.]+$/, "");

  return (
    <div className="flex flex-col gap-8">
      <header className="flex flex-col gap-3">
        <h1 className="m-0 font-serif text-display leading-[1.35] text-ink">
          {title}
        </h1>
        <p className="m-0 text-small text-ink-2">
          {report.filename} · 检查于 {formatDateTime(report.checkedAt)} ·{" "}
          {formatWordCount(report.wordCount)} 字
        </p>
      </header>

      <div className="flex items-start gap-12 max-md:flex-col max-md:gap-8">
        <aside className="w-[220px] shrink-0 border-t border-line pt-6 max-md:w-full max-md:pt-4">
          <p className="mb-4 text-caption text-ink-3">规范得分</p>
          <ScoreCard score={report.score} verdict={report.verdict} />
        </aside>

        <div className="min-w-0 flex-1">
          <div className="mb-4 flex items-center justify-between border-b border-line pb-3">
            <h2 className="m-0 text-h3 font-semibold text-ink">问题清单</h2>
            <StatusTag verdict={report.verdict} />
          </div>
          <IssueList issues={report.issues} />
        </div>
      </div>
    </div>
  );
}
