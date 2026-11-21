# 用户全局约束：Qoder 插件

维护者：SnowCore8；何时阅读：安装或排查本插件时。本文是插件描述，只说明安装与运行行为，
不定义规则；规则以包内 `rules/global-user-constraints.md` 为准。

安装后由 `SessionStart` hook 注入约束全文，并在 `SessionStart` 与 `UserPromptSubmit`
注入当前时间；已经通过规则或 `AGENTS.md` 加载同一份约束时自动跳过。

## 结构

| 路径 | 作用 |
|---|---|
| `.qoder-plugin/plugin.json` | Qoder 插件清单 |
| `hooks/hooks.json` | hook 配置，根目录用 `${QODER_PLUGIN_ROOT}` |
| `rules/global-user-constraints.md` | 用户全局约束正文 |
| `skills/` | 十八个通用规范 skill |
| `commands/` | 手动审查命令 |
| `scripts/` | 约束与时间注入脚本 |

## 安装

```bash
qoderclicn plugins install global-user-constraints-qoder-<版本>.zip --scope user
```

安装后开新会话；不需要手动复制规则。

## 行为

- `SessionStart`：读取 `rules/global-user-constraints.md` 注入全文（约 35 KB），注入前比对
  用户级 `~/.qoder-cn/rules/`（国际版 `~/.qoder/rules/`）、`AGENTS.md`、项目 `.qoder/rules/`
  与 `AGENTS.local.md`，同内容则跳过；`source` 为 `resume` 时也跳过，`startup`/`new`/`clear`/`compact`
  才注入；同一事件还会注入当前本地时间、UTC 偏移、时区与星期。
- `UserPromptSubmit`：只注入时间，保证长会话与压缩后仍然准确。
- 规则缺失、payload 非法、事件不在范围内时静默退出 0。
- 解释器用 `python`（PATH 上需有 3.9+），`-X utf8` 固定 stdio 编码；`timeout` 为 10 秒。

## 安全边界

- hook 只读：读包内规则、去重候选文件与系统时间；不写盘、不联网、不持久化。
- 注入的约束全文会进入模型上下文；敏感内容不要写进规则正文。
- 安装即执行：只安装可信来源的包，并核对 SHA256 校验和。
