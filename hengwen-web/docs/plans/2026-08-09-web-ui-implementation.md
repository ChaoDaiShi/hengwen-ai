# Web UI Implementation Plan

## Goal

依据 `docs/ui设计文档.md` 从 Vite 脚手架落地完整 `hengwen-web` 前端 UI：设计 Token、antd 6 主题定制、路由、全局状态与全部五个页面（首页上传、分析中、报告、历史、设置），并提供可测试的业务逻辑与 mock 数据层。后端就绪后可无缝替换为真实 API。

## Current State

- `src/` 为 Vite/React 脚手架样板（`App.tsx` 计数器页），无产品代码。
- 依赖已安装：React 19、TypeScript 6、Vite 8、antd 6.5.3、react-router-dom 7.18、zustand 5、axios、@ant-design/icons 6.3。
- 后端 `../hengwen-api/` 仅空脚手架，无 API 契约。
- 无 `test` 脚本；质量门禁要求新增业务逻辑补测试基础设施。
- 分支 `feature/myj` 已与远端同步；用户新增未跟踪文件 `bun.lock`、`docs/ui设计文档.md`，必须保留。

## Assumptions And Open Decisions

- 后端无接口：以 `src/api/mock.ts` 作隔离 mock 数据层，类型契约定义在 `src/types/`，真实 API 仅替换数据源。
- 分析流程为模拟：上传合法文件 → 分阶段进度（克制文案）→ 生成 mock 报告。
- 判定规则：得分 ≥ 90 → 通过；≥ 75 → 存疑；否则 → 需修改。
- 测试：新增 `vitest` dev 依赖与 `test` 脚本，仅覆盖纯业务逻辑（判定、文本 diff、分析阶段推进）。
- 深色模式跟随系统 `prefers-color-scheme`（§11），与 antd `darkAlgorithm` 同步切换。
- 遵循 §3 字体栈、行高 ≥1.7、8pt 网格、得分等宽字体。
- 不引入禁用项：无渐变、无弹跳、无 emoji 功能图标、一屏一主按钮。

## Scope

- 引入 Tailwind CSS v4，重写全局样式 `src/global.css`：设计 Token（§10 CSS Variables）+ 基础排版 + 深色模式；页面样式以 utility class 实现。
- 新建 `src/theme.ts`：antd 6 `ConfigProvider` token 映射（colorPrimary=accent、borderRadius=4、fontSize=15、controlHeight=40、组件 token）。
- 路由与布局：`src/App.tsx`（BrowserRouter + Routes）、`src/layout/AppLayout.tsx`（品牌 + 导航）。
- 类型与数据：`src/types/report.ts`、`src/store/useAppStore.ts`（zustand + persist）、`src/api/mock.ts`。
- 页面：`HomePage / AnalyzingPage / ReportPage / HistoryPage / SettingsPage`。
- 组件：`UploadZone / ScoreCard / IssueList / StatusTag`。
- 工具：`src/lib/verdict.ts`、`src/lib/diffText.ts`、`src/lib/analysisStages.ts`。
- 测试：`src/lib/*.test.ts` + `test` 脚本 + vitest。
- 更新 `index.html`（zh-CN、标题「衡文」）。
- 清理脚手架残留：`src/App.css`、`src/assets/*`。

## Out Of Scope

- 后端 API 实现与联调。
- 真实文件解析与规范检查算法。
- 用户认证/权限。
- 上传文件持久化。

## Implementation Steps

### Step 1 — 设计基础

- 重写全局样式 `src/global.css`：§10 变量、字体、行高 1.7、reduce-motion、深色映射；Tailwind v4 `@theme` 绑定设计 Token。
- 新建 `src/theme.ts`：antd token + components token，按系统偏好切换 dark。
- 更新 `src/main.tsx`：ConfigProvider + antd App + BrowserRouter。
- 重写 `src/App.tsx`：路由表。
- 更新 `index.html`；删除 `src/App.css` 及脚手架样式。

完成条件：`npm run build` 通过；路由骨架可渲染。

### Step 2 — 类型、状态与数据层

- 新建 `src/types/report.ts`：Severity、Issue、Report、Settings、AnalysisStage 等。
- 新建 `src/lib/verdict.ts`、`src/lib/analysisStages.ts`、`src/lib/diffText.ts`（纯函数）。
- 新建 `src/store/useAppStore.ts`：settings（persist）、reports（含 mock 种子）、analysis 状态与动作。
- 新建 `src/api/mock.ts`：种子数据与分析模拟。

完成条件：类型无 `any`；纯函数边界明确；store 转换正确。

### Step 3 — 布局与首页

- `src/layout/AppLayout.tsx`：品牌「衡文」（宋体 20px）+ 导航（首页/历史/设置 NavLink）。
- `src/components/UploadZone.tsx`：大留白虚线上传区，仅 `.docx/.pdf/.md`。
- `src/pages/HomePage.tsx`：品牌 + 一句话说明 + 上传区 + 最近检查。

完成条件：可上传进入分析；最近检查渲染；桌面/移动不截断。

### Step 4 — 分析页

- `src/pages/AnalyzingPage.tsx`：4px accent 细进度条 + 阶段文案；离开可返回恢复。
- store 推进模拟：阶段序列 → 生成 mock 报告 → 跳转 `/report/:id`。

完成条件：上传后进入分析，完成后出现报告。

### Step 5 — 报告页

- `src/components/ScoreCard.tsx`：Display 等宽大数字 + 细进度条 + 单次结论。
- `src/components/IssueList.tsx`：按严重度分组，行高 56px，点击展开对照视图（原文/建议，绛红删除线、松绿新增）。
- `src/components/StatusTag.tsx`：语义色 Tag。
- `src/pages/ReportPage.tsx`：标题（宋体 Display）+ 元信息 + 得分区 + 问题清单。

完成条件：得分、分组计数、展开对照、深色/移动可用。

### Step 6 — 历史与设置页

- `src/pages/HistoryPage.tsx`：Table（文件/类型/得分/状态/时间），48px 行高，去斑马纹，得分等宽，状态 Tag，空态大留白，点击行进报告。
- `src/pages/SettingsPage.tsx`：分组表单（机构信息/检查项），间距 48px，标签 14px，输入 40px，Switch 默认关，保存主按钮。

完成条件：历史列表可进入报告；设置可保存并持久化。

### Step 7 — 测试与质量

- 新增 `vitest` dev 依赖与 `test` 脚本；为 `verdict`、`diffText`、`analysisStages` 写单元测试。
- 运行 `npm run test`、`npm run lint`、`npx prettier --check <changed-files>`、`npm run build`。
- 浏览器验证桌面 1440x900 与移动 390x844，覆盖交互与空/加载/错误态。

完成条件：全部门禁通过。

## Verification

```bash
npm run test
npm run lint
npx prettier --check <changed-files...>
npm run build
```

UI：桌面/移动视口、关键交互、控制台无错误。

## Risks And Rollback

- 风险：antd v6 token API 与旧版差异；分析模拟与真实 API 的衔接。缓解：先 build 验证；mock 层隔离。
- 回滚：整任务集中于 feature 分支，git revert 或还原 commit 即可。

## Handoff

```text
Classification: COMPLEX
Plan: docs/plans/2026-08-09-web-ui-implementation.md
Goal: 按 ui设计文档.md 落地完整 Web UI
Acceptance: 五页面可交互、门禁全过、桌面/移动无截断
Constraints: 遵守 ui设计文档.md 与 .harness 规则；保留用户未跟踪文件
First step: Step 1 设计基础
```
