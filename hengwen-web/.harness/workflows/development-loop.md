# Development Loop

## State Machine

```text
INTAKE -> DISCOVER -> CLASSIFY
CLASSIFY(SIMPLE) -> IMPLEMENT
CLASSIFY(COMPLEX) -> PLAN -> IMPLEMENT
CLASSIFY(BLOCKED) -> REQUEST_INPUT -> DISCOVER
IMPLEMENT -> SELF_REVIEW -> VERIFY
VERIFY(PASS) -> COMMIT -> PUSH -> DELIVER
VERIFY(FAIL) -> FIX -> SELF_REVIEW -> VERIFY
VERIFY(BLOCKED) -> DIAGNOSE -> VERIFY | REQUEST_INPUT
COMMIT(FAIL) -> DIAGNOSE -> COMMIT | REQUEST_INPUT
PUSH(FAIL) -> DIAGNOSE -> PUSH | REQUEST_INPUT
```

禁止从 `IMPLEMENT` 直接进入 `DELIVER`。

## 1. Intake

- 提炼用户目标、可观察验收条件和明确限制。
- 判断用户是在要求实施、评审、调查还是仅讨论；仅实施类任务进入完整开发 loop。

退出条件：目标可复述，且没有遗漏用户显式要求。

## 2. Discover

- 读取 `AGENTS.md`、相关 harness 文件、源码、文档和配置。
- 使用搜索确认调用链、组件边界、脚本和测试现状。
- 查看 Git 状态与目标文件 diff，标记必须保留的已有改动。
- 对缺陷先形成可复现步骤或最小证据。

退出条件：可以说明当前行为、目标行为、影响范围和验证方法。

## 3. Classify

执行 `task-routing.md`。输出分类、理由、是否需要计划及验证项。

- `SIMPLE`：直接进入实施，不为形式而写计划。
- `COMPLEX`：调用问题解决计划 agent，计划通过自检后再交给前端 agent。
- `BLOCKED`：只询问最小必要问题；获得信息后重新发现和分类。

## 4. Plan (Complex Only)

- 记录现状、范围、方案、步骤、测试、风险和回滚。
- 每一步必须可独立验证，明确文件路径和完成条件。
- 存在关键产品取舍时在实施前请求确认；纯技术选择由 agent 依据仓库惯例决策并记录。

退出条件：前端 agent 不需要重新猜测目标、顺序或验收方法。

## 5. Implement

- 前端 agent 按简单目标或复杂计划小步修改。
- 每完成一个行为单元执行最接近该改动的检查。
- 发现计划假设错误时更新计划；范围显著扩大时回到 `CLASSIFY`。
- 不修改与目标无关的用户工作树内容。

退出条件：所有验收条件均已实现，且没有已知未处理的代码路径。

## 6. Self Review

- 阅读最终 diff，而非仅回忆修改过程。
- 检查范围、类型、异常路径、交互状态、响应式和可访问性。
- 清理调试输出、死代码、临时数据和无意义注释。
- 形成 `frontend-developer.md` 规定的质量交接。

任何问题都直接回到 `IMPLEMENT`，修复后重新自查。

## 7. Verify

质量 agent 按 `rules/quality-gates.md` 执行：

1. 静态检查与格式检查。
2. 类型检查和生产构建。
3. 自动化测试及针对性回归。
4. UI 的桌面/移动视觉与交互检查。
5. 验收条件逐条核对。

所有证据必须来自当前最终代码。旧运行结果、部分运行结果或“预计通过”均无效。

## 8. Fix Loop

当 `VERIFY` 失败：

1. 质量 agent 返回可复现 finding 和期望结果。
2. 前端 agent 定位根因并做最小修复。
3. 先重跑直接失败项。
4. 再重跑受影响的完整门禁。
5. 返回 `VERIFY`，直到 `PASS`。

同一失败连续三轮未解决时，暂停重复尝试，回到 `DISCOVER` 重审假设；仍缺外部信息才进入 `REQUEST_INPUT`。

## 9. Commit And Push

质量 verdict 为 `PASS` 后，执行 `rules/version-control.md`：

1. 只暂存当前任务拥有的文件。
2. 检查 staged diff，确认没有夹带用户已有改动、密钥或生成物。
3. 创建语义清晰的 commit。
4. 将当前分支 push 到其跟踪远端；新分支使用 `git push -u origin <branch>`。
5. 记录 commit hash、当前分支和远端目标。

commit 或 push 失败时不得进入 `DELIVER`。先诊断并重试；若需要凭据、权限或人工解决远端冲突，则进入 `REQUEST_INPUT` 并标记 `BLOCKED`。

## 10. Deliver

最终交付必须简明列出：

- 实现的用户可见行为和关键文件
- 实际执行的验证命令及结果
- commit hash 和 push 的远端分支
- 未执行项及原因
- 已知限制或残余风险

只有质量 verdict 为 `PASS` 且 commit、push 均成功，才能宣称完成。`BLOCKED` 必须明确说明阻塞证据和所需下一步。
