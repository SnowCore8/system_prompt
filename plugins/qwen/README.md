# 用户全局约束：Qwen Code 扩展

安装后 `SessionStart` 注入约束全文与当前时间，`UserPromptSubmit` 每次刷新时间；已经通过
`.qwen/rules`、`AGENTS.md` 或 `QWEN.md` 加载同一份约束时跳过。

## 结构

| 路径 | 作用 |
|---|---|
| `qwen-extension.json` | Qwen 扩展清单 |
| `hooks/qwen-hooks.json` | hook 配置，根目录用 `${CLAUDE_PLUGIN_ROOT}` |
| `rules/global-user-constraints.md` | 用户全局约束正文 |
| `skills/` | 十一个通用规范 skill |
| `commands/` | 手动审查命令 |
| `scripts/` | 约束与时间注入脚本 |

## 安装

```bash
qwen extensions install global-user-constraints-qwen-<版本>.zip
```

安装后开新会话；不需要手动复制规则。Qwen 会把 `${CLAUDE_PLUGIN_ROOT}` 替换成扩展根，
约束脚本同时接受根目录参数，不依赖环境变量。

## 行为

- `SessionStart`：约束全文 + 当前时间；去重路径包含 `~/.qwen/rules/`、`~/.qwen/AGENTS.md`、
  项目 `.qwen/rules/`、`AGENTS.md`、`QWEN.md`（从 cwd 向上查到 `.git`）。`source` 为 `resume`
  时跳过约束，`startup`/`clear`/`compact` 才注入。
- `UserPromptSubmit`：当前时间；Qwen 会把这段上下文包进 `<qwen:user-prompt-submit-context>` 标签。
- 规则缺失、payload 非法、事件不在范围内时静默退出 0。
- 解释器用 `python`（PATH 上需有 3.7+），`-X utf8` 固定 stdio 编码；`timeout` 为 10 秒。

## 安全边界

- hook 只读：读包内规则、去重候选文件与系统时间；不写盘、不联网、不持久化。
- 注入的约束全文会进入模型上下文；敏感内容不要写进规则正文。
- 安装即执行：只安装可信来源的包，并核对 SHA256 校验和。
