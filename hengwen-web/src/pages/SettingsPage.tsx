import { App, Button, Form, Input, Select, Switch } from "antd";
import type { Settings } from "../types/report";
import { useAppStore } from "../store/useAppStore";

const STANDARD_OPTIONS = [
  { value: "本科毕业论文规范（默认）", label: "本科毕业论文规范（默认）" },
  { value: "硕士毕业论文规范", label: "硕士毕业论文规范" },
  { value: "课程论文规范", label: "课程论文规范" },
  { value: "项目申报书规范", label: "项目申报书规范" },
];

export default function SettingsPage() {
  const { message } = App.useApp();
  const settings = useAppStore((s) => s.settings);
  const updateSettings = useAppStore((s) => s.updateSettings);
  const [form] = Form.useForm<Settings>();

  const onFinish = (values: Settings) => {
    updateSettings(values);
    message.success("设置已保存");
  };

  return (
    <div className="flex max-w-[560px] flex-col gap-12">
      <h1 className="m-0 text-h1 text-ink">设置</h1>
      <Form
        form={form}
        layout="vertical"
        initialValues={settings}
        onFinish={onFinish}
      >
        <section className="flex flex-col gap-4">
          <h2 className="m-0 text-h3 font-semibold text-ink">机构信息</h2>
          <Form.Item name="orgName" label="机构名称">
            <Input placeholder="例如：XX大学" />
          </Form.Item>
          <Form.Item name="standard" label="文档规范">
            <Select options={STANDARD_OPTIONS} />
          </Form.Item>
        </section>

        <section className="mt-12 flex flex-col gap-4">
          <h2 className="m-0 text-h3 font-semibold text-ink">检查项</h2>
          <Form.Item
            name="checkFormat"
            label="格式规范检查"
            valuePropName="checked"
          >
            <Switch />
          </Form.Item>
          <Form.Item
            name="checkCitation"
            label="引用与文献规范"
            valuePropName="checked"
          >
            <Switch />
          </Form.Item>
          <Form.Item
            name="checkPlagiarism"
            label="查重检测"
            valuePropName="checked"
          >
            <Switch />
          </Form.Item>
          <Form.Item
            name="autoReport"
            label="检查完成后自动生成报告"
            valuePropName="checked"
          >
            <Switch />
          </Form.Item>
        </section>

        <Form.Item className="mt-12">
          <Button type="primary" htmlType="submit">
            保存设置
          </Button>
        </Form.Item>
      </Form>
    </div>
  );
}
