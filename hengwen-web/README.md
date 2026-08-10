# 衡文 Web

<p align="center">
  <img src="public/hengwen.png" alt="衡文 logo" width="128" height="128" />
</p>

衡文前端：面向正式文档的规范检查、质量审阅与修改建议界面。本目录是 `hengwen-web` 包的独立说明，仓库入口见 `../README.md`。

## 技术栈

- React 19 + TypeScript
- Vite 8 + Tailwind CSS 4
- Ant Design 6
- React Router 7
- Zustand + persist

## 页面

- `/` 首页：品牌区、上传入口、最近检查
- `/analyzing` 分析中：进度条与当前阶段
- `/report/:id` 报告页：得分、问题清单、原文 / 建议对照
- `/history` 历史记录
- `/settings` 设置

## 开发

```bash
pnpm install
pnpm run dev
```

## 质量验证

```bash
pnpm run lint
pnpm run test
pnpm run build
pnpm exec prettier --check src tests
```

## 目录

```text
src/
├── components/   # 上传、得分、问题列表、状态标签
├── hooks/        # 深色模式
├── layout/       # 全局布局与导航
├── lib/          # 业务工具与 mock 逻辑
├── pages/        # 路由页面
└── store/        # Zustand 全局状态
```
