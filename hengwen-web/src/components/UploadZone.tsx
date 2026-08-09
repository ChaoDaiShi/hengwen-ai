import { App, Upload } from "antd";
import { InboxOutlined } from "@ant-design/icons";
import type { UploadProps } from "antd";

const ACCEPTED_EXTENSIONS = [".docx", ".pdf", ".md"] as const;

type AcceptedExtension = (typeof ACCEPTED_EXTENSIONS)[number];

function extensionOf(name: string): string | null {
  const dot = name.lastIndexOf(".");
  if (dot < 0) return null;
  return name.slice(dot).toLowerCase();
}

interface UploadZoneProps {
  onValidFile: (file: File) => void;
  disabled?: boolean;
}

export default function UploadZone({ onValidFile, disabled }: UploadZoneProps) {
  const { message } = App.useApp();
  const acceptAttr = ACCEPTED_EXTENSIONS.join(",");

  const beforeUpload: UploadProps["beforeUpload"] = (file) => {
    const ext = extensionOf(file.name);
    if (!ext || !ACCEPTED_EXTENSIONS.includes(ext as AcceptedExtension)) {
      message.error("仅支持 .docx / .pdf / .md 文件");
      return Upload.LIST_IGNORE;
    }
    onValidFile(file);
    return Upload.LIST_IGNORE;
  };

  return (
    <Upload.Dragger
      className="upload-zone"
      accept={acceptAttr}
      showUploadList={false}
      beforeUpload={beforeUpload}
      disabled={disabled}
    >
      <div className="flex flex-col items-center gap-4 py-6">
        <InboxOutlined className="text-[32px] text-ink-3" aria-hidden="true" />
        <p className="m-0 text-h3 text-ink">拖拽文档至此，或点击选择文件</p>
        <p className="m-0 text-small text-ink-3">支持 .docx / .pdf / .md</p>
      </div>
    </Upload.Dragger>
  );
}
