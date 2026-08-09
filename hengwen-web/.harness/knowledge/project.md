# Project Knowledge

## Product

衡文是面向正式文档的规范检查、质量审阅和修改建议产品。界面应体现严谨、克制、清晰和可信赖，避免营销页式表达。

## Workspace Boundary

- 当前 harness 管辖：`hengwen-web/`
- 前端源码：`src/`
- 静态资源：`public/`、`src/assets/`
- UI 规范：`docs/ui设计文档.md`
- 相邻后端：`../hengwen-api/`

前端 agent 可以读取后端代码以确认接口契约，但修改 `../hengwen-api/` 前必须重新评估任务范围；跨前后端改动自动归类为 `COMPLEX`。

## Stack

- React 19
- TypeScript 6
- Vite 8
- Ant Design 6
- React Router 7
- Zustand
- Axios
- Oxlint
- Prettier

## Package Manager And Commands

仓库同时存在 `package-lock.json` 或 `bun.lock` 时，以当前已安装环境和用户明确要求为准；没有明确要求时，质量门禁使用 `npm`，因为 `package.json` 已定义对应脚本。

```bash
npm run lint
npm run build
npx prettier --check <changed-files...>
```

当前 `package.json` 尚未定义 `test` 脚本。不得将 `build` 冒充测试；测试要求按 `rules/quality-gates.md` 执行。
