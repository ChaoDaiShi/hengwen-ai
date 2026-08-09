# Hengwen Web Agent Entry

本文件是 `hengwen-web` 的 agent 唯一入口。处理本目录及其子目录中的任务时，必须先进入 `.harness` 流程，不得跳过任务分级、验证或交接。

## Start Here

按以下顺序读取并执行：

1. 项目上下文：`.harness/knowledge/project.md`
2. 开发总流程：`.harness/workflows/development-loop.md`
3. 复杂度分流：`.harness/workflows/task-routing.md`
4. 质量门禁：`.harness/rules/quality-gates.md`
5. Git 交付规则：`.harness/rules/version-control.md`
6. 与任务匹配的 agent：`.harness/agents/`

完整索引见 `.harness/README.md`。

## Mandatory Routing

收到任务后，先由 `.harness/agents/problem-planner.md` 中的判定规则进行分级：

- `SIMPLE`：范围明确、风险低、改动局部，可由前端 agent 直接实施，不创建正式计划。
- `COMPLEX`：跨模块、需求模糊、涉及架构/状态/接口/迁移、风险较高，必须先由问题解决计划 agent 产出计划，再交给前端 agent。
- `BLOCKED`：缺少必要信息、依赖或权限，先收集证据并提出最小阻塞问题，不得猜测实现。

复杂任务的执行顺序固定为：

`问题解决计划 agent -> 用户确认（存在关键产品取舍时）-> UI/前端开发 agent -> 代码质量测试 agent -> 修复回路 -> 完成`

简单任务的执行顺序固定为：

`UI/前端开发 agent -> 代码质量测试 agent -> 修复回路 -> 完成`

## Non-negotiable Rules

- 修改前先读取相关代码、文档和 Git 状态，保留用户已有改动。
- UI 实现必须遵守 `docs/ui设计文档.md` 和 `.harness/rules/frontend.md`。
- 不以“代码看起来正确”代替验证；完成前必须执行 `.harness/rules/quality-gates.md` 中适用的全部门禁。
- 任一门禁失败都回到实施阶段；修复后重跑失败项及可能受影响的完整门禁。
- 没有测试脚本时不得谎报测试通过；应按质量规则记录测试缺口，且新增可测试业务逻辑时必须同时补测试能力或测试。
- 每次任务完成前必须依次执行 `commit -> push`；未成功推送到远端不得宣称任务完成。
- 最终交付必须报告改动、验证命令与结果、commit hash、push 目标、未验证项和残余风险。
