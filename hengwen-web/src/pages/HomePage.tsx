import { useNavigate } from "react-router-dom";
import UploadZone from "../components/UploadZone";
import { useAppStore } from "../store/useAppStore";
import { VERDICT_LABELS } from "../lib/verdict";
import { formatDateTime } from "../lib/format";

export default function HomePage() {
  const navigate = useNavigate();
  const startAnalysis = useAppStore((s) => s.startAnalysis);
  const reports = useAppStore((s) => s.reports);

  const recent = reports.slice(0, 5);

  const handleFile = (file: File) => {
    const dot = file.name.lastIndexOf(".");
    const fileType =
      dot >= 0 ? (file.name.slice(dot) as ".docx" | ".pdf" | ".md") : ".docx";
    startAnalysis({ filename: file.name, fileType });
    navigate("/analyzing");
  };

  return (
    <div className="flex flex-col">
      <section className="pb-16 pt-24 text-center max-md:pb-12 max-md:pt-16">
        <p className="m-0 text-h2 text-ink-2">衡量，然后修改</p>
      </section>

      <section className="mx-auto w-full max-w-[640px]">
        <UploadZone onValidFile={handleFile} />
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
                  <span className="hidden shrink-0 text-small text-ink-3 max-md:hidden">
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
