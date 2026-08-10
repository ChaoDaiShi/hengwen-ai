# 衡文 UI 优化实施计划

## Goal

依据 `docs/衡文-UI优化方案.md` 与 `docs/hengwen-UI优化方案.md`，完成 P0 止血与 P1 质感重建，使文档中的验收清单在 `hengwen-web` 当前代码中可逐条核验。

## Current State

- `index.html` 仍引用照片级 `/hengwen.png` 作为 favicon，未加载 webfont。
- `public/favicon.svg` 不存在；现有设计文档要求「黛蓝方 + 白字衡」。
- `HomePage` hero 与 `AppLayout` 头部使用照片级 PNG。
- 导航 active 使用 `after:bottom-[-4px]` 悬空下划线。
- `--hw-shadow-paper` 零消费；列表分数 16px；antd Empty / Pagination 保留默认观感。
- 无动效 token，存在 `duration-150/200` 字面量；无路由过渡、评分滚动与列表 stagger。
- `theme.ts` 未启用 cssVar，`borderRadius` 为 4，字体体系与 global.css 不一致。

## Assumptions And Open Decisions

- P0 与 P1 按文档原样执行；P2 的 CI / lint 机器拦截属长期治理，不作为本次验收项。
- 站内品牌统一以宋体文字呈现，`public/hengwen.png` 停止引用但保留文件，避免删除用户历史资产。
- antd 图标属于项目既有图标库，允许继续使用；antd 默认 Empty 图与分页箭头属于默认样式，必须替换。

## Scope

- `index.html`：favicon 切换、Noto Serif SC 400/600 引入。
- `public/favicon.svg`：新增黛蓝方白字「衡」。
- `src/global.css`：字体接续、动效 token、keyframes、纸影、reduced-motion 降级。
- `src/theme.ts`：cssVar 模式、宋体、8px 圆角、纸影透传、表格行高。
- `src/layout/AppLayout.tsx`、`src/pages/*`、`src/components/*`：P0 与 P1 视觉实现。
- `README.md`、`hengwen-web/README.md`：同步 favicon / 品牌说明。

## Out Of Scope

- 后端 `hengwen-api`、路由/接口/状态结构变更。
- P2 Playwright 截图基线、oxlint 硬编码拦截规则。
- 印章式得分、秤星刻度、朱批错线等可选进阶。

## Implementation Steps

1. `index.html`：加入 Google Fonts 400/600；favicon 改为 `/favicon.svg`。
2. `public/favicon.svg`：新建 32px 黛蓝圆角方、白色「衡」。
3. `src/global.css`：补充 `--hw-duration-micro/fast/score`、`--hw-ease-out`，映射 `@theme`；新增 `page-in` / `item-in` keyframes；base 字体切到宋体栈；reduced-motion 追加 `animation-delay: 0ms`。
4. `src/theme.ts`：`fontFamily` 与 `fontFamilyCode` 同源；`borderRadius` 8；`boxShadow` / `boxShadowSecondary` 指向 `var(--hw-shadow-paper)`；启用 `cssVar`；Table 行高达标。
5. `src/layout/AppLayout.tsx`：删除头部 PNG，品牌字改宋体 `text-h2`；active 改 `font-semibold text-accent`；header 消费纸影；`useLocation` 包裹路由过渡。
6. `src/pages/HomePage.tsx`：hero 改为宋体「衡文」+ 标语；最近检查分数 20px + `tabular-nums`；列表 stagger；继续检查横幅加纸影。
7. `src/pages/HistoryPage.tsx`：Empty 换自绘单线条图标 + 文案；Pagination `itemRender` 纯文字「上一页 / 下一页」；分数 20px + `tabular-nums`。
8. `src/pages/ReportPage.tsx`、`AnalyzingPage.tsx`：元数据数字 `tabular-nums`；进度条轮换 token 类。
9. `src/components/ScoreCard.tsx`：纸影卡片化、`tabular-nums`、600ms count-up（尊重 reduced-motion）。
10. `src/components/IssueList.tsx`：条目 stagger、行高 ≥48px、动效 token 化。
11. README 两份：品牌与 favicon 说明同步。

## Verification

- `pnpm run lint`、`pnpm run test`、`pnpm run build`、`pnpm exec prettier --check` 全部通过。
- 桌面 1440x900 / 移动 390x844 截图核验：首页、历史、报告、分析中、设置。
- `rg hengwen.png src -r` 为 0；`rg --hw-shadow-paper src -r` ≥ 2。
- 深色模式逐页目检，无纯黑背景、无不达标对比度。

## Risks And Rollback

- GitHub 网络不稳定可能导致 fetch / push 阻塞；本地改动均以小步、可逆文件编辑为主，回滚可基于当前 commit 定点 checkout。
- webfont 依赖 Google Fonts 外网；字体加载失败时回退到系统宋体栈，不影响布局与可读性。

## Handoff

Classification: COMPLEX
Plan: `hengwen-web/docs/plans/2026-08-10-ui-optimization.md`
Goal: 按 UI 优化方案完成 P0 / P1 落地并通过全部质量门禁。
Acceptance: P0 七项与 P1 动效三件套、8pt 审计、antd 主题接管逐条可核验；lint / test / build / prettier 通过。
Constraints: 不新增装饰与第三方依赖；保留用户已有改动；不把构建产物或锁文件以外文件混入提交。
First step: 修改 `index.html` 与新建 `public/favicon.svg`。
