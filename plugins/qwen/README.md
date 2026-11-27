# se-governance（Qwen Code 扩展）

Qwen Code 扩展：`contextFileName` 随每个请求发送治理章程全文，`UserPromptSubmit` 注入当前时间；随包提供
24 个 skill 与门禁审查命令。

## 事件与注入

| 事件或机制 | 注入内容 | 生命周期作用 |
|---|---|---|
| `contextFileName` | 章程全文，包在 `--- Context from: <路径> ---` 标记中 | 每个请求都可用的规则依据 |
| `SessionStart` | 当前时间 | 会话起点的时区与 turn 基准 |
| `UserPromptSubmit` | 当前时间，包进 `<qwen:user-prompt-submit-context>` 标签 | 每轮请求的时间基准 |
| skills 注册 | `name` 与 `description` 索引 | S0–S7 按阶段加载对应规范 |

- 项目 `.qwen/rules` 与扩展 `contextFileName` 同时启用时宿主不去重，会重复；二选一。
- Qwen 不提供插件数据目录，时间 hook 不落盘，turn 恒为 1。
- hook 用 `node`（CI 覆盖 Node 22/24），超时 10 秒；payload 非法或事件不在范围内时静默退出 0。

## 命令

`constraints-check` 读取包内章程，审查当前请求、方案或待执行命令；只审查，不执行被审查对象。

## 验证

- 组装：`scripts/materialize.sh qwen /tmp/se-qwen`。
- 冒烟：`qwen extensions install se-governance-qwen-<version>.zip` 后开新会话确认章程与时间已注入。

## MCP

配套 MCP 服务器 `@snowcore8/se-mcp` 可另行注册，见 [docs/mcp-usage.md](../../docs/mcp-usage.md)。
