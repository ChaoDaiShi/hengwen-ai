# Web Audit And CI Implementation Plan

## Goal

审查 `hengwen-web` 的用户界面和关键交互，修复可复现的响应式、可访问性、持久化与异步状态问题；同时为 `feature/myj` 建立前端 CI，并在 CI 通过后自动合并已验证提交到 `main`。

## Current State

- 前端为 React 19、TypeScript 6、Vite 8、Ant Design 6、Zustand 和 Vitest。
- 页面已有首页、分析中、报告、历史和设置，但分析计时器只挂在分析页，刷新或离开页面时流程状态不完整。
- 设置持久化只有设置字段，历史报告和分析任务无法在刷新后恢复。
- 仓库没有 GitHub Actions workflow。

## Scope

- 修复移动端导航、报告标题、问题对照布局和历史表格的可达性。
- 补充页面懒加载状态、报告问题空态、进行中任务恢复和设置表单回显。
- 统一文件扩展名解析并覆盖大小写、缺失和不支持扩展名边界。
- 新增根目录 `.github/workflows/hengwen-web-feature-myj.yml`，在 `feature/myj` 推送后执行 lint、test、format check、build，并用 GitHub API 合并通过验证的精确提交。

## Verification

```bash
pnpm run lint
pnpm run test
pnpm exec prettier --check src tests ../.github/workflows/hengwen-web-feature-myj.yml
pnpm run build
```

UI 需检查 `1440x900` 和 `390x844`，覆盖首页、分析中、报告、历史空态和设置回显。

## Risks And Rollback

- `main` 若启用了不允许 GitHub Actions 写入的分支保护，合并 job 会失败，需要仓库管理员允许 workflow token 写入或调整保护规则。
- 若合并期间 `feature/myj` 再次推进，workflow 会拒绝合并未经过本次 CI 的提交；新推送会触发新的 workflow。
