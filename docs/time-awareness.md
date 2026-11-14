# 时间感知设计

维护者：SnowCore8；何时阅读：修改或排查时间注入 hook 时。

Qoder 与 Qwen Code 都不向模型注入当前时间。模型只能靠对话里偶然出现的日期去猜，
跨天、排期、日志时间戳、节假日判断都会失准。本仓库用 hook 把时间变成显式的会话上下文。

## 设计

- 载体是 hook 的 `additionalContext`，不改写系统提示，也不依赖模型主动运行 `date`。
- 两个时机：
  - `SessionStart`：会话开始注入一次，保证第一轮就有时间；
  - `UserPromptSubmit`：每次提交提示前刷新，长会话、跨天与上下文压缩后仍然准确。
- 固定一行，便于模型与人工核对：

  ```text
  当前时间：YYYY-MM-DD HH:MM:SS +HH:MM（Asia/Shanghai，星期六）。需要日期或时间时以此为准；长会话以最近一次注入为准。
  ```

- 时区依次取 `TZ`、`/etc/timezone`、`/etc/localtime` 的 zoneinfo 路径，最后用 `tzname()` 兜底；
  取不到 IANA 名称时只留 UTC 偏移。
- 成本约每轮 30 token；失败静默，不阻断会话。hook 只读系统时间，不联网、不写盘，超时 10 秒。

## 双端接线

| 工具 | 清单 | hooks 文件 | 命令形式 |
| --- | --- | --- | --- |
| Qoder | `.qoder-plugin/plugin.json` | `hooks/hooks.json` | `command` + `args`，根目录 `${QODER_PLUGIN_ROOT}` |
| Qwen Code | `qwen-extension.json` | `hooks/qwen-hooks.json` | 单条 `command` 字符串，根目录 `${CLAUDE_PLUGIN_ROOT}` |

- 三包版本必须一致（本页只涉及 Qoder/Qwen 双端 hook）；`scripts/check.sh`、`scripts/dist.sh`
  与 release 工作流都会校验。
- Qwen 会自动加载 `<extension>/hooks/hooks.json`，这里用清单的 `hooks` 字段显式指向
  `qwen-hooks.json`，避免把只有 Qoder 才认的 `args` 形式喂给 Qwen。
- Qwen 的 `UserPromptSubmit` 上下文会被包进 `<qwen:user-prompt-submit-context>` 标签，这是宿主加的来源标记。

## 与约束注入的关系

- 约束注入只在 `SessionStart` 做一次，并做同内容去重；时间注入不去重，每轮都是新值。
- 时间由独立脚本 `scripts/inject-clock.py` 负责，约束脚本不再写时间，避免同一行出现两次。

## 验证

- `tests/hooks/test_inject_clock.py` 覆盖两个事件注入、其它事件静默、非法 payload 静默、双端 hooks 配置与清单版本。
- 已实测 Qoder 的 `SessionStart` `additionalContext` 能让模型读取并使用注入内容（用标记串验证）。
- 未验证：宿主精确的 token 计费；Windows 上 Qwen 扩展的 `python` 可用性。

## 关闭方式

删除对应 hooks 文件里的 `inject-clock` 条目即可，约束注入不受影响。
