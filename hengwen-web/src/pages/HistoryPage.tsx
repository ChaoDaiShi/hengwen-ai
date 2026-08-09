import { useNavigate } from "react-router-dom";
import { Empty, Table } from "antd";
import type { ColumnsType } from "antd/es/table";
import type { Report, Verdict } from "../types/report";
import StatusTag from "../components/StatusTag";
import { useAppStore } from "../store/useAppStore";
import { formatDateTime } from "../lib/format";

const emptyNode = (
  <div className="py-16 text-center">
    <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="尚无检查记录" />
  </div>
);

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
        <span className="font-mono text-body text-ink">{value}</span>
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
        <span className="text-small text-ink-2">{formatDateTime(value)}</span>
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
        pagination={{
          pageSize: 7,
          hideOnSinglePage: true,
          showSizeChanger: false,
        }}
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
