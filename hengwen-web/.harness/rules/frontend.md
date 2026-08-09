# Frontend Rules

## Tooling

- 包管理器统一为 pnpm（`package.json` 已声明 `packageManager: pnpm`），安装/新增依赖一律使用 `pnpm install` / `pnpm add`；禁止使用 npm、yarn、bun 安装依赖。
- 依赖锁定文件只维护 `pnpm-lock.yaml`，随提交更新；发现其他包管理器锁文件（`package-lock.json`、`bun.lock` 等）不得使用，应移除并切换为 pnpm。
- 新增依赖前先检查是否已有等价依赖；安装后必须跑 `pnpm run build` 与 `pnpm run test` 验证。
- 运行项目脚本统一使用 `pnpm run <script>`（如 `pnpm run dev`、`pnpm run lint`），传递参数用 `pnpm run <script> -- <args>`。

## Product And Visual Direction

- 以 `docs/ui设计文档.md` 为产品视觉基准：严谨、克制、安静、可信赖。
- 业务工具界面优先清晰的信息层级和高效任务流，不制作营销式首屏或装饰性卡片墙。
- 使用 Ant Design 6 token 和已有组件体系；避免散落、重复且无法统一调整的样式常量。
- 容器圆角不超过 8px，除非现有组件规范明确要求。
- 不使用渐变、装饰光斑、高饱和大色块或无功能价值的动画。

## Interaction Completeness

- 异步界面必须设计 loading、empty、error、success 和 retry 状态。
- 表单必须有标签、校验、提交中和失败反馈；危险操作需要匹配风险的确认机制。
- 图标按钮使用项目已有图标库，并提供可访问名称或 tooltip。
- 键盘焦点、颜色对比、语义结构和点击目标尺寸必须可用。
- 桌面和移动端均不得出现文字截断、控件位移、遮挡或不可达操作。

## React And TypeScript

- 保持组件职责清晰；派生值优先计算，不无必要复制到 state。
- effect 只用于外部同步，并正确处理依赖、竞态和卸载。
- 公共数据结构定义明确类型；禁止用 `any`、类型断言或 `@ts-ignore` 掩盖契约问题。
- 请求错误必须进入用户可理解的状态，并保留诊断所需信息；禁止空 `catch`。
- 性能优化必须由真实渲染成本或测量支持，不提前堆叠 memo 化。

## UI Verification

任何用户可见改动至少检查：

- 桌面视口：`1440x900`
- 移动视口：`390x844`
- 默认状态和受本次改动影响的 loading/empty/error/disabled 状态
- 主要点击、输入、提交、导航和返回路径

截图只是证据的一部分；还必须验证交互和浏览器控制台错误。纯文档、配置或不可见重构可标记 UI 检查为不适用，并说明原因。
