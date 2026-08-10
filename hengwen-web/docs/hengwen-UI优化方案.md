# 衡文 UI 优化 · 系统整合方案

> 版本：v1.0 ｜ 整合四份评审（灵感 / 校准 / 批判 / 系统）后的收敛方案
> 根因诊断：丑感的 ~80% 来自「该删的没删、该接的没接」——设计规范与 CSS token 全部已定义，但全站零消费者。**不是设计水平问题，是执行纪律问题。**

---

## ① 三阶段落地方案

### P0 立即止血（0.5 天 · 只做减法与接线，不新增任何装饰）

| # | 任务 | 文件 | 验收标准 |
|---|------|------|----------|
| 1 | **删除 hero 照片级墨迹 logo**，改纯文字品牌：20px 宋体「衡文」+ 标语「衡量，然后修改」 | `src/pages/HomePage.tsx` | `grep hengwen.png src -r` 引用 = 0；hero 区无任何 `<img>` / 图形元素 |
| 2 | **favicon 切换**到已存在的 `public/favicon.svg`（黛蓝方 + 「衡」） | `index.html` | 浏览器标签页显示黛蓝方「衡」 |
| 3 | **接入 webfont**：Noto Serif SC 仅 400/600 两档，`font-display: swap` | `index.html` | 「衡文」以宋体渲染；无 FOIT；Network 可见字体请求 |
| 4 | **antd 默认残留清零**：分页器箭头、Empty 灰图标 → 显式配置/自绘线性/纯文案 | `src/pages/HistoryPage.tsx`、`src/theme.ts` | 页面上任何 antd 默认样式都无法被认出 |
| 5 | **接通纸影**：`--hw-shadow-paper` 至少接到 2 处消费端（ScoreCard 卡片、导航/弹层） | `src/components/ScoreCard.tsx` 等 | `grep --hw-shadow-paper src -r` 引用 ≥ 2；页面出现轻微纸影层次 |
| 6 | **列表分数对齐**：16px → 20px + `tabular-nums`，与 ScoreCard 72px 同一 `font-mono` 身份 | `src/pages/HomePage.tsx`、`src/pages/HistoryPage.tsx` | 首页 / 历史 / 报告三处分数视觉同族、数字对齐 |
| 7 | **修导航悬空下划线**（`after:bottom-[-4px]`）→ 贴 baseline 或改「字重 600 + 颜色」区分 active | `src/layout/AppLayout.tsx` | 下划线不再悬空；active 态清晰 |

**P0 总验收**：`pnpm build` 通过；深色模式无回归；不新增任何新组件、新图形、新颜色。

---

### P1 质感重建（2–3 天 · 让 token 变成体验）

1. **动效三件套**（全部受 `global.css` 已有 `prefers-reduced-motion` 降级保护）：
   - 路由切页 240ms（`src/App.tsx` 或 CSS View Transitions）
   - ScoreCard 得分滚动 600ms ease-out（count-up，`src/components/ScoreCard.tsx`）
   - 列表条目淡入 stagger 40–80ms（HomePage 最近检查、`src/components/IssueList.tsx`）
   - 时长抽成 motion token：`global.css` 新增 `--hw-duration-fast/base/score` + `--hw-ease-out`，`@theme` 映射
   - 验收：三项动效均存在；reduced-motion 下全部禁用；`grep` 无硬编码 duration（token 定义处除外）
2. **8pt 网格 + 硬编码清零审计**：`grep -rnE "#[0-9a-fA-F]{3,8}|rgb\(" src --include="*.tsx"` → 除 token 外 0 命中；非 8 倍数间距逐一解释或修正
3. **antd 主题整体接管**：`src/theme.ts` 启用 cssVar 模式，`fontFamily / borderRadius(8) / colorPrimary(黛蓝)` 与 `global.css` 同源
   - 验收：Table / Empty / Pagination 与自绘组件同字体、同色系
4. **深色模式逐页验收**：5 个页面 × 明暗 2 模式走查；正文对比度 ≥ 4.5:1；无纯黑背景；截图留档

---

### P2 长期防回退（随 CI 落地 · 持续）

1. **静态拦截**（oxlint 已有，扩充规则）：
   - 禁 tsx 硬编码颜色 / 非 token 动效时长
   - Empty / Pagination 必须显式配置（杜绝默认图标回归）
2. **视觉回归**（新增 Playwright）：
   - 5 页面 × 明暗 = 10 张基线截图进 CI；pixelmatch diff 阈值告警（关键区域 0.1%）
3. **文档升级**（`docs/ui设计文档.md`）：
   - 增「落地合规表」：规范 ↔ token ↔ 组件/文件 ↔ 验收命令
   - 反模式红线逐条标注机器校验手段（哪条 grep / lint / 截图能拦）
   - 新增 PR 模板审美 checklist（是否素材级图形 / antd 默认样式 / 硬编码颜色 / 动效取 token / 深色已验），缺省不可合并

---

## ② 教训沉淀机制（三层防线）

**人（PR checklist）→ 静态（lint 规则）→ 视觉（截图 diff）**

- **规则即文档**：每条反模式红线配一条可执行校验，写进设计文档合规表。规范从「建议」变「断言」。
- **token 单一事实源**：CSS 变量是唯一颜色/间距/动效来源；antd 经 `cssVar` 映射；任何 tsx 硬编码 = CI 失败。
- **grep 即验收**：关键红线直接写成可跑命令（`grep hengwen.png` = 0、`grep --hw-shadow-paper` ≥ 2）。

---

## ③ 一句话长期建议

**「丑感的根因不是缺设计，是规范无人执行——把每条红线焊成 lint 规则和截图基线，比任何一次大改版都管用。」**
