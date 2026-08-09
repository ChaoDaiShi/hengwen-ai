import { useMemo, useState } from "react";
import { DownOutlined, RightOutlined } from "@ant-design/icons";
import type { Issue, Severity } from "../types/report";
import { diffText, type DiffPart } from "../lib/diffText";

const SEVERITY_ORDER: Severity[] = ["error", "warning", "info"];

const SEVERITY_META: Record<Severity, { label: string; color: string }> = {
  error: { label: "必须修改", color: "var(--error)" },
  warning: { label: "建议修改", color: "var(--warning)" },
  info: { label: "仅供参考", color: "var(--text-secondary)" },
};

function OriginalText({ parts }: { parts: DiffPart[] }) {
  return (
    <>
      {parts
        .filter((part) => part.type !== "add")
        .map((part, i) => (
          <span
            key={i}
            className={part.type === "del" ? "text-error line-through" : ""}
          >
            {part.text}
          </span>
        ))}
    </>
  );
}

function SuggestionText({ parts }: { parts: DiffPart[] }) {
  return (
    <>
      {parts
        .filter((part) => part.type !== "del")
        .map((part, i) => (
          <span key={i} className={part.type === "add" ? "text-success" : ""}>
            {part.text}
          </span>
        ))}
    </>
  );
}

interface IssueListProps {
  issues: Issue[];
}

export default function IssueList({ issues }: IssueListProps) {
  const [expanded, setExpanded] = useState<ReadonlySet<string>>(
    () => new Set(),
  );

  const groups = useMemo(
    () =>
      SEVERITY_ORDER.map((severity) => ({
        severity,
        meta: SEVERITY_META[severity],
        items: issues.filter((issue) => issue.severity === severity),
      })).filter((group) => group.items.length > 0),
    [issues],
  );

  const toggle = (id: string) =>
    setExpanded((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });

  return (
    <div className="flex flex-col gap-6">
      {groups.length === 0 && (
        <div className="border border-line bg-surface px-6 py-16 text-center">
          <p className="m-0 text-body text-ink-2">未发现需要处理的问题</p>
          <p className="m-0 mt-2 text-small text-ink-3">
            这份文档通过了当前启用的检查项
          </p>
        </div>
      )}
      {groups.map((group) => (
        <section key={group.severity}>
          <h3 className="mb-3 flex items-center gap-2 text-h3 font-medium text-ink">
            <span
              aria-hidden="true"
              className="inline-block h-2 w-2 rounded-full"
              style={{ backgroundColor: group.meta.color }}
            />
            {group.meta.label}
            <span className="text-small font-normal text-ink-3">
              {group.items.length}
            </span>
          </h3>
          <ul className="m-0 list-none p-0">
            {group.items.map((issue) => {
              const isOpen = expanded.has(issue.id);
              const parts = diffText(issue.original, issue.suggestion);
              return (
                <li key={issue.id} className="border-b border-line">
                  <button
                    type="button"
                    className="flex w-full min-h-[56px] items-center gap-3 bg-transparent px-2 py-2 text-left text-ink"
                    aria-expanded={isOpen}
                    onClick={() => toggle(issue.id)}
                  >
                    <span
                      aria-hidden="true"
                      className="inline-block h-2 w-2 shrink-0 rounded-full"
                      style={{ backgroundColor: group.meta.color }}
                    />
                    <span className="min-w-0 flex-1 break-words text-body">
                      {issue.title}
                    </span>
                    <span className="max-w-[28%] shrink-0 break-words text-right font-mono text-caption text-ink-3 max-md:max-w-[34%]">
                      {issue.location}
                    </span>
                    {isOpen ? (
                      <DownOutlined
                        className="shrink-0 text-caption text-ink-3"
                        aria-hidden="true"
                      />
                    ) : (
                      <RightOutlined
                        className="shrink-0 text-caption text-ink-3"
                        aria-hidden="true"
                      />
                    )}
                  </button>
                  {isOpen && (
                    <div className="border-t border-line px-2 py-4">
                      <p className="mb-3 text-small text-ink-3">
                        {issue.summary}
                      </p>
                      <div className="flex gap-6 max-md:flex-col max-md:gap-4">
                        <div className="flex-1">
                          <p className="mb-2 text-caption text-ink-3">原文</p>
                          <p className="m-0 text-small leading-[1.7] text-ink whitespace-pre-wrap">
                            <OriginalText parts={parts} />
                          </p>
                        </div>
                        <div className="w-px shrink-0 bg-line max-md:h-px max-md:w-full" />
                        <div className="flex-1">
                          <p className="mb-2 text-caption text-ink-3">建议</p>
                          <p className="m-0 text-small leading-[1.7] text-ink whitespace-pre-wrap">
                            <SuggestionText parts={parts} />
                          </p>
                        </div>
                      </div>
                    </div>
                  )}
                </li>
              );
            })}
          </ul>
        </section>
      ))}
    </div>
  );
}
