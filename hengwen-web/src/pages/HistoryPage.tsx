import { useNavigate } from "react-router-dom";
import { Table } from "antd";
import type { ColumnsType, TablePaginationConfig } from "antd/es/table";
import type { Report, Verdict } from "../types/report";
import StatusTag from "../components/StatusTag";
import { useAppStore } from "../store/useAppStore";
import { formatDateTime } from "../lib/format";

const emptyNode = (
  <div className="flex flex-col items-center gap-4 py-16 text-center">
    <svg
      width="40"
      height="40"
      viewBox="0 0 40 40"
      fill="none"
      aria-hidden="true"
      className="text-ink-3"
    >
      <rect
        x="9"
        y="6"
        width="22"
        height="28"
        rx="2"
        stroke="currentColor"
        strokeWidth="1.5"
      />
      <path
        d="M14 14h12M14 19h12M14 24h8"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
      />
    </svg>
    <p className="m-0 text-body text-ink-3">尚无检查记录</p>
  </div>
);

const pagination: TablePaginationConfig = {
  pageSize: 7,
  hideOnSinglePage: true,
  showSizeChanger: false,
  className: "hw-pagination",
  itemRender: (_page, type, originalElement) => {
    if (type === "prev") {
      return <span className="text-body text-ink-2">上一页</span>;
    }
    if (type === "next") {
      return <span className="text-body text-ink-2">下一页</span>;
    }
    if (type === "jump-prev" || type === "jump-next") {
      return <span className="px-2 text-ink-3">…</span>;
    }
    return originalElement;
  },
};

export default function HistoryPage() {
  const navigate = useNavigate();
  const reports = useAppStore((s) => s.reports);

  const columns: ColumnsType<Report> = [
    {
      title: "文件",
      dataIndex: "filename",
      key: "filename",
      ellipsis: true,
      render: (value: string) => (
        <span className="text-body text-ink">{value}</span>
      ),
    },
    {
      title: "类型",
      dataIndex: "fileType",
      key: "fileType",
      width: 100,
      responsive: ["md"],
      render: (value: Report["fileType"]) => (
        <span className="font-mono text-small text-ink-2">{value}</span>
      ),
    },
    {
      title: "得分",
      dataIndex: "score",
      key: "score",
      width: 100,
      render: (value: number) => (
        <span className="font-mono text-h2 tabular-nums text-ink">{value}</span>
      ),
    },
    {
      title: "状态",
      dataIndex: "verdict",
      key: "verdict",
      width: 120,
      render: (value: Verdict) => <StatusTag verdict={value} />,
    },
    {
      title: "时间",
      dataIndex: "checkedAt",
      key: "checkedAt",
      width: 180,
      responsive: ["lg"],
      render: (value: string) => (
        <span className="text-small tabular-nums text-ink-2">
          {formatDateTime(value)}
        </span>
      ),
    },
  ];

  return (
    <div className="flex flex-col gap-6">
      <h1 className="m-0 text-h1 text-ink">历史记录</h1>
      <Table<Report>
        rowKey="id"
        columns={columns}
        dataSource={reports}
        locale={{ emptyText: emptyNode }}
        pagination={pagination}
        onRow={(record) => ({
          onClick: () => navigate(`/report/${record.id}`),
          onKeyDown: (event) => {
            if (event.key === "Enter" || event.key === " ") {
              event.preventDefault();
              navigate(`/report/${record.id}`);
            }
          },
          tabIndex: 0,
          className:
            "cursor-pointer focus-visible:outline-2 focus-visible:outline-offset-[-2px] focus-visible:outline-accent",
        })}
      />
    </div>
  );
}
