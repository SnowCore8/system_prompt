# 全局用户约束：Qwen Code 扩展

维护者：SnowCore8。本文只说明安装与运行行为，不定义规则；规则以包内 `constraints/global-user-constraints.md` 为准。

安装后，清单的 `contextFileName` 在会话启动或刷新时读取并缓存，随后每个请求随 system prompt 发送；
`SessionStart` 与 `UserPromptSubmit` 的 hook 只注入当前时间。

## 结构

| 路径 | 作用 |
|---|---|
| `qwen-extension.json` | Qwen 扩展清单 |
| `hooks/qwen-hooks.json` | hook 配置，根目录用 `${CLAUDE_PLUGIN_ROOT}` |
| `constraints/global-user-constraints.md` | 全局用户约束正文；启动/刷新读取，随后每请求随 system prompt 发送，不使用 `rules/` |
| `skills/` | 二十个通用规范 skill |
| `commands/` | 手动审查命令 |
| `scripts/` | 时间注入脚本 |

以上为安装后的自包含结构；源码包只保留清单、hooks 与说明，使用 `scripts/materialize.sh qwen` 从顶层真源组装。

## 安装

```bash
qwen extensions install global-user-constraints-qwen-<版本>.zip
```

安装后开新会话；约束由清单的 `contextFileName` 在启动/刷新读取一次，随后每请求随 system prompt 携带，不需要复制规则。Qwen 会把
`${CLAUDE_PLUGIN_ROOT}` 替换成扩展根。

## 命令

`constraints-check` 读取包内 `constraints/global-user-constraints.md`，审查当前请求、方案或待执行命令；
只审查，不执行被审查对象。

## 行为

- `contextFileName`：启动/刷新读取 `constraints/global-user-constraints.md` 并缓存；每个请求随 system prompt 携带。
- `SessionStart`：注入当前时间。
- `UserPromptSubmit`：注入当前时间；Qwen 会把这段上下文包进 `<qwen:user-prompt-submit-context>` 标签。
- 同时启用项目 `.qwen/rules` 与扩展 `contextFileName` 时，宿主不做内容去重，会重复；二选一。
- payload 非法或事件不在范围内时静默退出 0。
- 解释器用 `node`（PATH 上需可用；CI 使用 Node 20）；`timeout` 为 10 秒。

## 安全边界

- 时间 hook 读取宿主 payload 与系统时间。Qwen 不设置插件数据目录变量；时间 hook 通常不落盘，
  turn 通常为 1、elapsed 为 `unavailable`。不修改项目文件，不联网。
- 注入的约束正文会进入模型上下文；敏感内容不要写进规则正文。
- 安装即执行：只安装可信来源的包，并核对 SHA256 校验和。
