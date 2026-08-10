import { useNavigate } from "react-router-dom";
import UploadZone from "../components/UploadZone";
import { useAppStore } from "../store/useAppStore";
import { VERDICT_LABELS } from "../lib/verdict";
import { formatDateTime } from "../lib/format";
import { fileTypeForName } from "../lib/file";

export default function HomePage() {
  const navigate = useNavigate();
  const startAnalysis = useAppStore((s) => s.startAnalysis);
  const reports = useAppStore((s) => s.reports);
  const analysis = useAppStore((s) => s.analysis);

  const recent = reports.slice(0, 5);

  const handleFile = (file: File) => {
    const fileType = fileTypeForName(file.name);
    if (!fileType) return;
    startAnalysis({ filename: file.name, fileType });
    navigate("/analyzing");
  };

  return (
    <div className="flex flex-col">
      <section className="pb-16 pt-16 text-center max-md:pb-12 max-md:pt-12">
        <img
          src="/hengwen.png"
          alt="衡文"
          className="mx-auto mb-8 h-28 w-28 rounded-[4px] object-cover max-md:h-24 max-md:w-24 max-md:mb-6"
        />
        <p className="m-0 text-h2 text-ink">衡量，然后修改</p>
        <p className="mx-auto mt-4 max-w-[420px] text-body text-ink-2">
          面向正式文档的规范检查、质量审阅与修改建议
        </p>
      </section>

      <section className="mx-auto w-full max-w-[640px]">
        {analysis && (
          <div className="mb-6 flex items-center justify-between gap-4 border border-line bg-surface px-5 py-4 max-md:items-start">
            <div className="min-w-0">
              <p className="m-0 text-body text-ink">有一项检查正在进行</p>
              <p
                className="m-0 truncate text-small text-ink-3"
                title={analysis.filename}
              >
                {analysis.filename}
              </p>
            </div>
            <button
              type="button"
              className="shrink-0 border-0 bg-transparent px-0 py-1 text-small font-medium text-accent underline decoration-transparent underline-offset-4 transition-[color,text-decoration-color] duration-150 hover:text-accent-hover hover:decoration-current"
              onClick={() => navigate("/analyzing")}
            >
              继续检查
            </button>
          </div>
        )}
        <UploadZone onValidFile={handleFile} disabled={Boolean(analysis)} />
      </section>

      <section className="mt-16" aria-label="最近检查">
        <h2 className="m-0 mb-6 text-h3 font-semibold text-ink">最近检查</h2>
        {recent.length === 0 ? (
          <p className="m-0 py-8 text-body text-ink-3">尚无检查记录</p>
        ) : (
          <ul className="m-0 list-none border-t border-line p-0">
            {recent.map((report) => (
              <li key={report.id}>
                <button
                  type="button"
                  className="flex w-full min-h-[56px] items-center gap-6 border-0 border-b border-line bg-transparent px-2 py-2 text-left font-sans text-ink transition-colors duration-150 hover:bg-hover"
                  onClick={() => navigate(`/report/${report.id}`)}
                >
                  <span className="flex-1 truncate text-body">
                    {report.filename}
                  </span>
                  <span className="hidden shrink-0 text-small text-ink-3 sm:inline">
                    {formatDateTime(report.checkedAt)} ·{" "}
                    {VERDICT_LABELS[report.verdict]}
                  </span>
                  <span className="shrink-0 min-w-10 text-right font-mono text-h3 text-ink">
                    {report.score}
                  </span>
                </button>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
