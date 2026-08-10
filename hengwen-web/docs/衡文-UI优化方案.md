# 衡文 UI 优化方案

**版本** v1.0 ｜ **日期** 2026-08-10
**范围** hengwen-web（React 19 + TS + Vite 8 + antd v6 + Tailwind v4 + Zustand 5）
**基准** `docs/ui设计文档.md` v1.0 —— 简约 · 克制 · 有呼吸感
**执行原则：先删后补，不新增装饰。宁可空，不可贴。**

---

## 〇、总诊断

问题不在审美水平，在**执行纪律**：设计规范与 token 均已定义，但几乎没有消费者。

证据：

- `global.css` 变量完整，但 `--hw-shadow-paper` 已定义、全站 **0 使用**
- antd 默认样式残留：HistoryPage 分页器箭头、Empty 默认灰图标
- `index.html` 未加载任何 webfont，全文系统字体，无字体体系
- hero 照片级墨迹 logo（1254×1254 PNG，白底无透明 + `object-cover` 圆角裁切 = 贴纸感），违反映模式「名字即品牌」
- 导航 active 下划线悬空（`after:bottom-[-4px]`）
- 列表分数 16px 与 ScoreCard 72px 等宽分数断裂
- favicon 仍指 `/hengwen.png`，已存在的 `/favicon.svg`（黛蓝方 + 白字「衡」）未启用
- 三项规范动效（240ms / 600ms / stagger）全部缺失

优先级：**P0 止血 → P1 质感重建 → P2 防回退**。动效排最后——静态未立，不化妆。

---

## 一、四维评审摘要

### 1. 高级审美校准者 —— 整体 4/10

丑感构成 ≈ **60% 实现偏差 + 40% 系统层缺陷**：

| 构成 | 占比 | 说明 |
| --- | --- | --- |
| logo 照片级 | 30% | 实现偏差，最重单项 |
| 字体 token 缺失 | 15% | 系统层 |
| antd 默认残留 | 10% | 实现偏差 |
| shadow 无消费者 | 10% | 系统层 |
| 导航下划线 / favicon | 各 10% | 实现偏差 |
| antd 主题未整体接管 | 10% | 系统层 |
| 字号不成体系 | 5% | 系统层 |

**保留不动**：global.css token、深色模式（theme.ts 双主题）、ScoreCard 72px 等宽得分。

### 2. 批判与精炼者 —— 红线

最致命丑感 = hero 照片级 logo（违反映模式第 1、5 条 + 「名字即品牌」）。
不可妥协红线：**界面禁止任何照片级/素材级图形；图形只能是自绘几何或矢量线条；做不到就删——宁可空，不可贴。**

### 3. 灵感开拓者 —— 气质方向

- 气质：**批卷官案头（主）／度量衡器物（骨）／铅字校对（手）**
- 黛蓝按「一克石青」矿物颜料使用，克制地出现
- 五个杠杆：宋体品牌字、印章式得分、秤星刻度、朱批错线、黛蓝调纸影（`rgba(62,92,118,0.10)`）

### 4. 系统整合者 —— 根因与治理

根因 = 执行纪律（规范停在纸上）。红线六项，**任一命中即打回**：

1. 无字体体系
2. 纯平面零投影（shadow token 无消费）
3. 硬编码颜色
4. 系统默认图标
5. 动效缺失
6. 文档与实现背离

---

## 二、P0 立即止血（7 项，按序执行）

### ① 删除 hero 照片级 logo

删除：

```html
<img src="/hengwen.png" alt="衡文" className="mx-auto mb-8 h-28 w-28 rounded-[4px] object-cover max-md:h-24 max-md:w-24 max-md:mb-6" />
```

改为纯文字排版：品牌字「衡文」20px 宋体 + 标语「衡量，然后修改」。名字本身就是品牌，无需图形。

### ② 引入字体体系

`index.html` `<head>` 中加入（仅 400/600 两档，`font-display: swap`）：

```html
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link
  href="https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;600&display=swap"
  rel="stylesheet"
/>
```

CSS 侧：中文正文/标题 `font-family: "Noto Serif SC", "Songti SC", serif`；数字保持等宽（`font-mono` + `tabular-nums`），与 ScoreCard 同源。

### ③ 接线 `--hw-shadow-paper`

```css
--hw-shadow-paper: 0 1px 2px rgba(28,27,25,0.04), 0 4px 12px rgba(28,27,25,0.06);
```

至少 2 处消费：ScoreCard 卡片、antd 弹层/下拉（经 ConfigProvider `theme.token` 或 `cssVar` 映射）。让 token 有消费者。

### ④ antd ConfigProvider 全面接管

- 分页器：去掉默认箭头，改纯文字「上一页 / 下一页」或自绘线性箭头
- Empty：默认灰图标 → 纯文案或自绘单线条图标
- **验收标准：页面上任何 antd 默认样式不能被认出**

### ⑤ 列表分数统一

首页列表分数 16px → **20–24px**，与 ScoreCard 72px 同一字体身份（mono）+ `tabular-nums`，建立「得分」的视觉连续性。

### ⑥ 修复导航悬空下划线

```html
'after:absolute after:bottom-[-4px] after:left-0 after:right-0 after:h-0.5 after:bg-accent after:content-[""]'
```

`after:bottom-[-4px]` 悬空 → 改为贴 baseline，或直接去掉下划线，active 改用字重 600 + 黛蓝区分。

### ⑦ 启用 favicon

`index.html`：

```html
<link rel="icon" type="image/svg+xml" href="/favicon.svg" />
```

（`public/favicon.svg` 已存在：黛蓝方 + 白字「衡」）

---

## 三、P1 质感重建

### 动效三件套（时长抽成 motion token）

- 切页 / 条目：**240ms** ease-out
- 得分展示：**600ms**
- 列表条目淡入：240ms + stagger 40–80ms
- `@media (prefers-reduced-motion: reduce)` 全部降级为瞬间切换

### 硬编码清零（8pt 网格审计）

- 颜色、间距全面审计：间距取 8 的倍数
- 卡片 padding ≥24px；列表行高 ≥48px；中文正文行高 ≥1.7
- 动效时长抽成 `--hw-duration-*` token，禁字面量

### 深色模式逐页验收

- 对比度 ≥4.5:1，无纯黑背景
- 深浅双主题统一走 `theme.ts` + ConfigProvider，禁止页面内硬编码

---

## 四、P2 防回退（机器拦截）

1. **ESLint**：拦截硬编码颜色（`#hex` 只允许出现在 global.css）、硬编码间距、动效时长字面量
2. **Playwright 截图基线**：主要页面 × 明暗双模，进 CI，diff 即告警
3. **文档治理**：`docs/ui设计文档.md` 增加「落地合规表」；PR 模板加入审美检查项
4. **单一事实源**：CSS 变量为 token 唯一来源，antd 经 `cssVar` 映射，禁止两套并存

---

## 五、可选进阶（灵感者提案，非必须）

> 原则：以下三项任一实现若产生廉价感，立即撤回。不做，也比做错好。

- **印章式得分**：ScoreCard 96px 方印、2px 边框、3° 旋转、印泥重影、「落印」动效 scale 1.08 → 1
- **秤星刻度**：列表分数以 `repeating-linear-gradient` 打星 + 三角准星
- **朱批错线**：问题清单错误行以朱笔 SVG 标注

---

## 六、验收清单（合稿）

- [ ] 首页一屏内无照片级 / 素材级图形
- [ ] 全站唯一强调色 = 黛蓝 `#3E5C76`，占比 ≤5%
- [ ] 页面上任何 antd 默认样式不能被认出
- [ ] 字体体系生效（宋体中文 + 等宽数字），仅 400/600 两档
- [ ] `--hw-shadow-paper` 有 ≥2 处消费
- [ ] 间距遵循 8pt；卡片 padding ≥24px；行高 ≥48px / 1.7
- [ ] 动效三件套落地，且 `prefers-reduced-motion` 降级生效
- [ ] favicon 为 `/favicon.svg`
- [ ] 深色模式逐页验收通过（对比度 ≥4.5:1，无纯黑背景）
- [ ] 无硬编码颜色 / 间距 / 动效时长残留

---

*终稿由四位成员合议产出：高级审美校准者（诊断与打分）· 批判与精炼者（红线与减法）· 灵感开拓者（气质与杠杆）· 系统整合者（治理与防回退）。*
