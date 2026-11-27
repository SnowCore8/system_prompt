# hook 与注入

本文件说明三端 hook 事件、注入时序与压缩后行为。真源为 `shared/scripts/`；Qoder 与 Qwen 的包清单引用
同一批脚本。

## 事件与注入

| 端 | 事件或机制 | 注入内容 |
|---|---|---|
| Qoder | `SessionStart` | 章程全文（`source=resume` 跳过；缺失或超过 64 KiB 时输出提示） |
| Qoder | `SessionStart`（`matcher: compact`） | 一句章程提醒与两行时间 |
| Qoder | `UserPromptSubmit` | `Never violate the se-governance charter.` 提醒加三行时间 |
| Qoder | `PreToolUse` / `PostToolUse` / `PostToolUseFailure` | 一行时间 |
| Qoder | `SessionEnd` | 清理本 session 的时间状态 |
| Qwen | `contextFileName` | 章程全文，包在 `--- Context from: <路径> ---` 标记中 |
| Qwen | `SessionStart` / `UserPromptSubmit` | 当前时间 |
| DSH | `systemPrompt.section()` | 章程 section；与用户级 AGENTS.md 同内容时按 sha256 去重 |

## 去重与路径

- Qoder 注入前把章程与用户配置根、项目目录及其祖先的 `rules/global-user-constraints.md`、`AGENTS.md`、
  `AGENTS.local.md` 做 sha256 比对，相同即跳过。
- Qwen 不提供插件数据目录，时间 hook 不落盘，turn 恒为 1。
- DSH 的用户级候选为 `DSH_HOME/AGENTS.md` 与 `DSH_AGENTS_HOME/AGENTS.md`。

## 故障语义

- 所有 hook 静默失败：payload 非法或事件不匹配时退出码 0，不阻断宿主会话。
- hook 超时 10 秒；不写日志、不访问网络、不启动子进程。
- 章程超过 64 KiB 硬上限时不注入全文，输出读取提示。

## 时间注入

时间块由 `shared/scripts/lib/time.js` 生成：用户提示用三行块（当前时间、时区、距上次注入的间隔与 turn），
工具事件用一行时间。`inject-compact.js` 在压缩后的 `SessionStart(source=compact)` 输出提醒与两行时间。
