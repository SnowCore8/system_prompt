# se-governance（Qoder 插件）

Qoder 插件：会话启动注入治理章程全文，提示提交时注入提醒与时间，压缩后恢复提醒；随包提供 24 个 skill
与门禁审查命令。

## 事件与注入

| 事件 | 注入内容 | 生命周期作用 |
|---|---|---|
| `SessionStart` | 章程全文；`source=resume` 跳过；缺失、读取失败或超过 64 KiB 时改输出提示 | S0 受理时有同一份章程可用 |
| `SessionStart`（`matcher: compact`） | 一句章程提醒与两行时间 | 压缩后恢复门禁判断依据 |
| `UserPromptSubmit` | `Never violate the se-governance charter.` 提醒加三行时间 | 每轮请求重申章程与时间基准 |
| `PreToolUse` / `PostToolUse` / `PostToolUseFailure` | 一行时间 | 记录工具动作的时间基准 |
| `SessionEnd` | 清理本 session 的时间状态 | 收尾时不留残留状态 |

- 去重：项目目录及其祖先的 `.qoder/rules/global-user-constraints.md`、`AGENTS.md`、`AGENTS.local.md`，
  以及用户配置根下的同名文件与 `AGENTS.md`，任一与正文 sha256 相同即跳过注入。
- hook 用 `node`（CI 覆盖 Node 22/24），超时 10 秒；payload 非法或事件不支持时静默退出 0。

## 命令

`constraints-check` 读取包内章程，审查当前请求、方案或待执行命令；只审查，不执行被审查对象。

## 验证

- 组装：`scripts/materialize.sh qoder /tmp/se-qoder`；校验：`qoderclicn plugins validate /tmp/se-qoder`。
- 冒烟：`qoderclicn --cwd /tmp plugins install --scope local /tmp/se-qoder`，开新会话确认章程已注入。

## MCP

配套 MCP 服务器 `@snowcore8/se-mcp` 可另行注册，见 [docs/mcp-usage.md](../../docs/mcp-usage.md)。
