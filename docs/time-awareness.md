# 时间感知设计

维护者：SnowCore8；何时阅读：修改或排查时间注入 hook 时。

Qoder 与 Qwen Code 都不向模型注入当前时间。模型只能靠对话里偶然出现的日期去猜，
跨天、排期、日志时间戳、节假日判断都会失准。本仓库用 hook 把时间变成显式的会话上下文。
三端 hook 事件、注入落点与压缩语义见 [hooks-and-injection.md](hooks-and-injection.md)。

## 设计

- 载体是 hook 的 `additionalContext`，不改写系统提示，也不依赖模型主动运行 `date`。
- 时机：
  - Qwen Code：`SessionStart` 与每次 `UserPromptSubmit`；
  - Qoder：`SessionStart` 注入约束全文（`source=resume` 或配置根/项目已有同内容时跳过）；`source=compact` 时
    无 matcher 组与 compact 组都会执行，全文与提醒/时间合并为一条上下文，细节见 hooks 文档；
    `UserPromptSubmit` 注入完整 DSH 时间块；`PreToolUse` / `PostToolUse` / `PostToolUseFailure`
    各注入一行时间；`SessionEnd` 清理状态。
- 采用 DSH `time-context` 的三行格式：

  `Time sampled while preparing turn <turn>: <ISO 时间戳>[<IANA 时区>]`
  `Browser time zone for this request: <时区>. Interpret otherwise-unqualified dates and times in this zone.`
  `Elapsed since the preceding model-visible message: <耗时|unavailable>.`

  Qoder 没有逐步 step 字段，因此不再输出恒为 1 的 step；脚本用 `QODER_PLUGIN_DATA` 按 session 记录 turn 与上次注入时间。
  没有状态时输出 turn 1、unavailable。Qwen 不设置插件数据目录变量，时间 hook 通常不落盘，turn 通常为 1、elapsed 为
  `unavailable`。

  DSH 原版时间消息含 `turn N, step M` 与 `resolved`/`mixed`/`missing` 三种时区措辞；本页格式是 Qoder/Qwen 适配版。

- 时区依次取 `TZ`（用 `Intl.DateTimeFormat` 校验）、`Intl` 解析出的系统时区、`/etc/timezone`，
  最后用 UTC 整点偏移兜底；Windows 没有 `/etc`，走 `Intl` 与偏移。时间戳同时写入数值偏移与方括号内的时区名。
- 成本约为每轮几十 token；工具事件只加一行。失败静默，不阻断会话。Qoder 会写插件数据目录的 clock 状态，并在 `SessionEnd` 清理；Qwen 不设置插件数据目录，时间 hook 通常不落盘，其 hooks 也没有 `SessionEnd` 清理。两者都不写项目文件、不联网，超时 10 秒。

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

- Qwen 由清单的 `contextFileName` 在启动/刷新读取一次，随后每个请求随 system prompt 携带；Qoder 由 `SessionStart` hook 注入全文，不写用户级 rules。时间注入不去重，每轮都是新值。
- 时间由 `scripts/inject-clock.js` 负责：`UserPromptSubmit` 发完整 DSH 块，工具事件发一行时间。

## 验证

- `tests/hooks/inject-clock.test.js` 覆盖用户提示完整时间、工具事件一行时间、SessionEnd 清理、非法 payload 静默、双端 hooks 配置与清单版本。
- 宿主精确的 token 计费与 Windows 上 Qwen 扩展的 `node` 可用性尚未在仓库内验证。

## 关闭方式

删除对应 hooks 文件里的 `inject-clock` 条目即可，约束注入不受影响。
