# Hengwen Web Harness

`.harness` 是 `hengwen-web` 的 agent 协作协议。它定义任务如何分流、复杂问题如何先计划后实施、前端如何交付，以及质量检查失败后如何循环修复。

## Directory Map

```text
.harness/
├── README.md
├── agents/
│   ├── frontend-developer.md
│   ├── problem-planner.md
│   └── quality-engineer.md
├── knowledge/
│   └── project.md
├── rules/
│   ├── frontend.md
│   ├── quality-gates.md
│   └── version-control.md
└── workflows/
    ├── development-loop.md
    └── task-routing.md
```

## Source Of Truth

- 流程状态和循环：`workflows/development-loop.md`
- 简单/复杂任务判定：`workflows/task-routing.md`
- 角色职责与交接格式：`agents/*.md`
- 完成标准和命令：`rules/*.md`
- 提交和推送规则：`rules/version-control.md`
- 技术栈与项目约束：`knowledge/project.md`

当文档发生冲突时，优先级为：`AGENTS.md` > `rules/` > `workflows/` > `agents/` > `knowledge/`。发现冲突后应在当前任务中修正文档，不允许静默选择更宽松的规则。

## Core Loop

```text
INTAKE
  -> CLASSIFY
  -> [PLAN when COMPLEX]
  -> IMPLEMENT
  -> SELF_REVIEW
  -> VERIFY
  -> [FIX -> VERIFY while failing]
  -> COMMIT
  -> PUSH
  -> DELIVER
```

只有 `VERIFY` 中所有适用门禁通过，并且当前任务已成功 `COMMIT` 和 `PUSH`，任务才可进入 `DELIVER`。
