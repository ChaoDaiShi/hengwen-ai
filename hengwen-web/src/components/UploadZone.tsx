import { App, Upload } from "antd";
import { InboxOutlined } from "@ant-design/icons";
import type { UploadProps } from "antd";
import { ACCEPTED_FILE_TYPES, fileTypeForName } from "../lib/file";

interface UploadZoneProps {
  onValidFile: (file: File) => void;
  disabled?: boolean;
}

export default function UploadZone({ onValidFile, disabled }: UploadZoneProps) {
  const { message } = App.useApp();
  const acceptAttr = ACCEPTED_FILE_TYPES.join(",");

  const beforeUpload: UploadProps["beforeUpload"] = (file) => {
    const fileType = fileTypeForName(file.name);
    if (!fileType) {
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
