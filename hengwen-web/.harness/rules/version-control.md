# Version Control Rules

## Mandatory Delivery Sequence

每个实施类任务必须按以下顺序结束：

```text
VERIFY(PASS) -> STAGE -> REVIEW STAGED DIFF -> COMMIT -> PUSH -> DELIVER
```

commit 和 push 都是完成条件，不是可选的后续建议。只完成本地 commit、尚未 push 的任务不得标记完成。

## Scope Safety

- 提交前运行 `git status --short`，区分当前任务改动与用户已有改动。
- 使用准确路径执行 `git add <task-files...>`；工作树不干净时禁止使用 `git add .` 或 `git add -A`。
- 提交前必须运行 `git diff --staged --check` 和 `git diff --staged`。
- 不得暂存、修改、还原或删除不属于当前任务的文件。
- 不提交密钥、`.env`、本地运行报告、构建产物或依赖目录。

## Commit

- 一个任务至少产生一个聚焦 commit；只有任务天然包含可独立审阅阶段时才拆分多个 commit。
- commit message 应说明行为变化，推荐使用 `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:` 前缀。
- 禁止以 `WIP`、`update`、`changes` 等无法表达目的的消息完成任务。
- commit 后记录 `git rev-parse --short HEAD`。

## Push

- 有跟踪分支时运行 `git push`。
- 新分支运行 `git push -u origin <current-branch>`。
- 禁止使用 `--force`；确需改写远端历史时必须获得用户明确授权，并优先使用 `--force-with-lease`。
- push 失败时先检查认证、远端状态和非快进冲突。不得通过破坏性 reset、丢弃用户改动或强推绕过失败。

## Failure And Reporting

- commit 失败：修复提交前检查或 Git 配置后重试；无法自行解决则标记 `BLOCKED`。
- push 失败：保留本地 commit，报告原始错误摘要、commit hash 和所需权限或同步动作，状态为 `BLOCKED`。
- 最终交付必须包含 commit hash 及 `<remote>/<branch>`，让远端交付可核验。
