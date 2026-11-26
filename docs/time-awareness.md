# 时间感知设计

维护者：SnowCore8；何时阅读：修改或排查时间注入 hook 时。

Qoder 与 Qwen Code 都不向模型注入当前时间。模型只能靠对话里偶然出现的日期去猜，
跨天、排期、日志时间戳、节假日判断都会失准。本仓库用 hook 把时间变成显式的会话上下文。

## 设计

- 载体是 hook 的 `additionalContext`，不改写系统提示，也不依赖模型主动运行 `date`。
- 时机：
  - Qwen Code：`SessionStart` 与每次 `UserPromptSubmit`；
  - Qoder：`SessionStart` 安装用户级 rules；`source=compact` 时补约束提醒和一行压缩后时间；
    `UserPromptSubmit` 注入完整 DSH 时间块；`PreToolUse` / `PostToolUse` / `PostToolUseFailure`
    各注入一行时间；`SessionEnd` 清理状态。
- 采用 DSH `time-context` 的三行格式：

  `Time sampled while preparing turn <turn>, step <step>: <ISO 时间戳>[<IANA 时区>]`
  `Browser time zone for this request: <时区>. Interpret otherwise-unqualified dates and times in this zone.`
  `Elapsed since the preceding <model-visible message|step context>: <耗时|unavailable>.`

  Qoder hook 没有 turn/step/elapsed 字段；脚本用 `QODER_PLUGIN_DATA` 按 session 记录 turn 与上次注入时间，step 固定为 1。没有状态时输出 turn 1、step 1、unavailable；Qwen 的 SessionStart 同样从 turn 1 开始。

- 时区依次取 `TZ`（有 `zoneinfo`/tzdata 时）、`/etc/timezone`、`/etc/localtime` 的 zoneinfo 路径，最后用 `tzname()` 兜底；
  Windows 没有 `/etc`，有 tzdata 时用 IANA，否则显示系统时区名，仍保留有效 UTC 偏移。
  仍取不到时标 `UTC`。
- 成本约为每轮几十 token；工具事件只加一行。失败静默，不阻断会话。Qoder 会写插件数据目录的 clock 状态，并在 `SessionEnd` 清理；不写项目文件、不联网，超时 10 秒。

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

- Qwen 的约束注入只在 `SessionStart` 做一次，并做同内容去重；Qoder 通过 `SessionStart` 安装用户级 rules，不在 hook 注入全文。时间注入不去重，每轮都是新值。
- 时间由 `scripts/inject_clock.py` 负责：`UserPromptSubmit` 发完整 DSH 块，工具事件发一行时间。

## 验证

- `tests/hooks/test_inject_clock.py` 覆盖用户提示完整时间、工具事件一行时间、SessionEnd 清理、非法 payload 静默、双端 hooks 配置与清单版本。
- 仓库测试覆盖时间注入、工具事件时间、状态清理、静默失败与双端 hooks 配置。
- 宿主精确的 token 计费与 Windows 上 Qwen 扩展的 `python` 可用性尚未在仓库内验证。

## 关闭方式

删除对应 hooks 文件里的 `inject-clock` 条目即可，约束注入不受影响。
