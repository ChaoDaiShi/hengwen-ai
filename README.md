# 衡文 HenWen AI

<p align="center">
  <img src="hengwen-web/public/favicon.svg" alt="衡文 favicon" width="128" height="128" />
</p>

衡文（衡量、审阅文章）是一套面向正式文档的规范检查、质量审阅与修改建议工具。它覆盖毕业论文、课程论文、竞赛报告、项目申报书、科研材料及其他正式文档，重点提供格式合规、引用规范、查重提示与修改建议。

## 仓库结构

```text
.
├── hengwen-web/   # React 19 + Vite 8 + Ant Design 6 前端
└── hengwen-api/   # FastAPI + SQLAlchemy 后端脚手架
```

## 当前实现

- 文档选择与上传入口（`.docx` / `.pdf` / `.md`）
- 分析进度占位流程与恢复入口
- 报告页：规范得分、严重度分组问题清单、原文与建议对照
- 历史记录、设置页与本地持久化
- 深色模式、响应式布局与可访问性基础

## 快速开始

### 前端

```bash
cd hengwen-web
pnpm install
pnpm run dev
```

### 后端

```bash
cd hengwen-api
uv sync
uv run hengwen-api
```

后端目前为接口脚手架，前端数据层使用 mock，后续可按 `hengwen-api` 的接口契约接入。

## 质量验证

```bash
cd hengwen-web
pnpm run lint
pnpm run test
pnpm run build
```

## Logo

站内品牌以宋体文字「衡文」呈现，Web 站点 favicon 为 `hengwen-web/public/favicon.svg`（黛蓝方 + 白字「衡」）。
