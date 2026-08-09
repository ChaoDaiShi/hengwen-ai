# Harness Development Loop Implementation Plan

> **For implementation agents:** Execute this plan task by task and verify the final documentation against the repository's real commands.

**Goal:** 建立一套从任务分级、复杂问题规划、前端实施、质量验证到失败修复的完整 agent 开发闭环。

**Architecture:** 使用 `AGENTS.md` 作为入口，由 `.harness/workflows` 定义状态机和分流，`.harness/agents` 定义职责与交接，`.harness/rules` 定义不可绕过的完成门禁。全部采用可被不同代码 agent 读取的 Markdown 协议，不依赖仓库中不存在的专用运行器。

**Tech Stack:** Markdown, React 19, TypeScript 6, Vite 8, Oxlint, Prettier

---

### Task 1: Establish The Entry And Project Context

**Files:**

- Modify: `AGENTS.md`
- Create: `.harness/README.md`
- Create: `.harness/knowledge/project.md`
- Modify: `.gitignore`

定义唯一入口、路径索引、优先级、项目边界和真实可用命令，并确保 harness 规范可被 Git 跟踪。

### Task 2: Define Agent Responsibilities

**Files:**

- Create: `.harness/agents/problem-planner.md`
- Create: `.harness/agents/frontend-developer.md`
- Create: `.harness/agents/quality-engineer.md`

隔离规划、实施和质量职责，定义输入、输出、交接格式和 PASS/FAIL/BLOCKED 结论。

### Task 3: Define Routing And The Closed Loop

**Files:**

- Create: `.harness/workflows/task-routing.md`
- Create: `.harness/workflows/development-loop.md`

明确简单任务跳过正式计划、复杂任务必须计划，并建立 `VERIFY -> FIX -> VERIFY` 修复循环和升级规则。

### Task 4: Define Frontend And Quality Gates

**Files:**

- Create: `.harness/rules/frontend.md`
- Create: `.harness/rules/quality-gates.md`

定义 UI/React/TypeScript 约束、桌面和移动验证、lint/format/build 命令及当前缺少测试脚本时的严格处理方式。

### Task 5: Verify The Harness

检查所有相对路径存在，搜索流程中的状态和角色引用，确认 `.harness` 文件未被忽略，并运行适用于文档改动的格式检查。由于本任务不修改生产代码，可按质量规则说明跳过生产构建。

### Task 6: Require Remote Delivery

**Files:**

- Modify: `AGENTS.md`
- Modify: `.harness/README.md`
- Modify: `.harness/workflows/development-loop.md`
- Create: `.harness/rules/version-control.md`

将 `COMMIT -> PUSH` 加入 `VERIFY` 与 `DELIVER` 之间，要求仅暂存当前任务文件，并把 commit hash 与远端分支作为完成证据。

### Task 7: Sync Before Development

**Files:**

- Modify: `.harness/rules/version-control.md`

把 `FETCH/PULL` 加入每个实施类任务的开端，要求开发前与远端同步，避免基于过期 `main` 或过期的本地分支继续开发。
