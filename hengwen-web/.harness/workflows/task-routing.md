# Task Routing

每个开发任务必须先分级，但分级过程应轻量。简单任务不写正式计划，复杂任务必须先计划。

## Decision Tree

依次判断：

1. 是否缺少无法从仓库推导的必要产品信息、凭据或权限？是则 `BLOCKED`。
2. 是否触发任一复杂条件？是则 `COMPLEX`。
3. 是否满足全部简单条件？是则 `SIMPLE`。
4. 无法确定时按 `COMPLEX` 处理。

## Complex Triggers

命中任意一项即为 `COMPLEX`：

- 跨越两个或更多业务模块，或同时修改前端与后端。
- 新增/重构路由架构、全局状态、权限、认证、持久化或请求基础设施。
- API 契约、数据模型、迁移或兼容策略尚未明确。
- 涉及多个异步状态、并发、竞态、缓存、重试或长流程交互。
- 需求存在两个以上合理方案，且选择会显著影响用户行为或维护成本。
- 预计修改 5 个以上生产文件，或无法在一个小型、独立 diff 中完成。
- 修复无法稳定复现，根因未知，或曾经修复失败。
- 涉及安全、隐私、支付、不可逆数据操作或高影响性能问题。
- 需要新增第三方依赖、构建能力或测试基础设施。

## Simple Conditions

只有全部满足才是 `SIMPLE`：

- 目标和验收行为明确。
- 修改局限在单一组件或紧密相关的小范围文件。
- 不改变公共契约、架构、权限或持久化数据。
- 实现方案由现有代码模式直接给出。
- 失败可轻易回滚，验证命令和场景明确。

典型示例：文案修正、局部样式修复、明确的单组件缺陷、已有模式下的小型字段展示。

## Classification Output

```text
Classification: SIMPLE | COMPLEX | BLOCKED
Reason: <one or two concrete sentences>
Plan required: yes | no
Verification: <commands and user-visible scenarios>
```

分级不是一次性标签。实施中一旦发现复杂触发条件，立即停止扩展改动，将任务升级为 `COMPLEX` 并补计划。
