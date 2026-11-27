# 三平台 hook 与注入规则

维护者：SnowCore8；何时阅读：调整 Qoder、Qwen Code 或 DSH 的 hook、约束注入、压缩后恢复行为时。

本文件是 hook 事件、输出契约、注入落点与压缩/恢复时序的唯一权威。rules、skills、plugins 的目录与加载顺序见
[agent-tooling-loading.md](agent-tooling-loading.md)；时间块在本仓库的适配见 [time-awareness.md](time-awareness.md)；
三个包的安装与行为见 [Qoder](../plugins/qoder/README.md)、[Qwen Code](../plugins/qwen/README.md)、
[DSH](../plugins/dsh/README.md)。

## 结论摘要

| 平台 | hook 能力 | 常驻约束载体 | 压缩后 | 本仓库选择 |
| --- | --- | --- | --- | --- |
| Qoder | 原生 hooks，注册 29 个事件 | `SessionStart` 的 `additionalContext` 注入全文 | 压缩成功后触发 `SessionStart(source=compact)`；无 matcher 组与 `compact` matcher 组都会执行 | hook 注入 + sha256 去重 |
| Qwen Code | 原生 hooks，23 个事件 | 清单 `contextFileName` 在启动/刷新读取并缓存，随后每个请求随 system prompt 发送 | `contextFileName` 不受压缩影响；`SessionStart` 在 resume/compact 等 source 都触发 | 只用 `contextFileName` 承载约束 |
| DSH | 没有内建 Claude 风格 hooks；实验桥接包可选，默认不安装 | 插件 `ctx.systemPrompt.section()`；另有独立的 `dsh-agent-instructions` 指令链 | system prompt 压缩后重建；指令链在下一次 pre-step 重新折叠；桥接 hook 的 context 不会在压缩后重放 | `systemPrompt.section()` + 原生时间注入 |

## Qoder

### 事件与配置

Qoder 的 hook 配置位于 `<plugin>/hooks/hooks.json`，形状为 `{"hooks": {"<事件>": [...]}}`。事件组可带
`matcher`、`sequential`、`async`；条目字段含 `type`、`command`、`args`、`shell`、`env`、`timeout`、`if`。

| 类别 | 事件 |
| --- | --- |
| 工具 | `PreToolUse`、`PostToolUse`、`PostToolUseFailure`、`PermissionRequest`、`PermissionDenied` |
| 会话与用户 | `SessionStart`、`UserPromptSubmit`、`SessionEnd`、`Setup`、`InstructionsLoaded`、`CwdChanged`、`FileChanged`、`ConfigChange` |
| 压缩 | `PreCompact`、`PostCompact` |
| 停止与查询 | `Stop`、`StopFailure`、`QueryEnd`、`Notification` |
| 子代理与协作 | `SubagentStart`、`SubagentStop`、`TeammateIdle`、`TaskCreated`、`TaskCompleted`、`Elicitation`、`ElicitationResult`、`WorktreeCreate`、`WorktreeRemove` |
| 内部 | `ImagePrepare` |

文档站事件表与实现不完全一致：文档列 `PreModelSwitch`、`PostModelSwitch`，二进制没有；
实现有 `ImagePrepare`、`QueryEnd`，文档事件表未列。文档差异单独标注。

### SessionStart 与 matcher

- `SessionStart.source` 有 5 个值：`startup`、`resume`、`clear`、`new`、`compact`。matcher 匹配的是 `source`。
- 无 matcher、空串或 `*` 匹配全部 source；多个 matcher 组命中时全部执行，不是首个命中即停止。
- 多个 hook 的 `additionalContext` 会用空格合并为同一条上下文；配置完全相同的 hook 才会被去重。
- 因此 `matcher: "compact"` 组与无 matcher 组在 `source=compact` 时都会运行。

### 输出契约与执行

推荐输出：

```json
{
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": "注入到对话的文本"
  }
}
```

- `hookSpecificOutput` 存在时必须带 `hookEventName`；`additionalContext` 必须是字符串。
- 纯文本 stdout 只有在 `SessionStart` 与 `UserPromptSubmit` 会进入模型上下文；`systemMessage` 只给用户看。
- 退出码 0 成功；2 为阻塞，但只对支持阻塞的事件生效（`SessionStart` 不支持）；其他非零只记录。
- `timeout` 单位为秒；command 默认 600 秒，本仓库显式设为 10 秒。
- 插件 hook 可用 `QODER_PROJECT_DIR`、`QODER_PLUGIN_ROOT`、`QODER_PLUGIN_DATA`；`QODER_PLUGIN_*` 只在插件 hooks 内可用。

### 压缩、恢复与清除

压缩成功后的顺序是：`PreCompact` → `PostCompact` → `SessionStart(source=compact)`，随后把 SessionStart 输出追加到
压缩后的新历史。`PreCompact` 可阻止压缩；它的 `additionalContext` 只并入压缩指令，不保证摘要保留约束。
Qoder 的同步 `PostCompact.additionalContext` 不被消费、不进入对话；压缩后的注入点应使用 `SessionStart(source=compact)`。

- `resume`：仍触发 `SessionStart(source=resume)`；本仓库脚本按设计跳过全文注入。
- `clear` 与 `new`：分别触发 `SessionStart(source=clear)` 与 `SessionStart(source=new)`，本仓库不跳过。
- 静态 `.qoder/rules` 与 `AGENTS.md` 在压缩后会由 `refresh("compact")` 重新读取，不依赖 hook。
- hook 注入的全文与静态 rules 是两条来源；本仓库用项目/用户规则文件的 sha256 去重，避免 full-text 重复。

### 插件 rules 与限制

插件可以物理打包 `rules/`，但 CLI 不把它当 rules 自动加载，manifest 的 `rules` 字段被忽略；只含 `rules/` 的插件
会因没有可安装组件被拒。插件想让正文生效，只能由自己的 hook 或 command 读取。宿主原生方式仍是项目/用户 `.qoder/rules`
或 `AGENTS.md`。

### 本仓库用法

- `SessionStart` 的无 matcher 组运行 [inject-constraints.js](../shared/scripts/inject-constraints.js)：读取包内 `rules/`
  注入全文；`source=resume` 跳过；项目/用户同内容文件按 sha256 跳过。
- `SessionStart` 的 `compact` matcher 组运行 [inject-compact.js](../shared/scripts/inject-compact.js)：注入提醒与两行时间（时间戳与时区）。
- `UserPromptSubmit` 运行提醒 + 完整时间块；工具事件与 `SessionEnd` 由 [inject-clock.js](../shared/scripts/inject-clock.js) 处理。
- 由于两组在 compact 时都会执行，压缩后可能同时得到全文与提醒；全文是否出现取决于 sha256 去重。

## Qwen Code

### 事件与 matcher

Qwen Code 有 23 个 hook 事件：

| 类别 | 事件 |
| --- | --- |
| 工具 | `PreToolUse`、`PostToolUse`、`PostToolUseFailure`、`PostToolBatch`、`PermissionRequest`、`PermissionDenied` |
| 会话与用户 | `SessionStart`、`UserPromptSubmit`、`UserPromptExpansion`、`SessionEnd`、`SessionDelete`、`InstructionsLoaded`、`FileChanged` |
| 压缩 | `PreCompact`、`PostCompact` |
| 停止与显示 | `Stop`、`StopFailure`、`Notification`、`MessageDisplay` |
| 子代理与任务 | `SubagentStart`、`SubagentStop`、`TodoCreated`、`TodoCompleted` |

- `SessionStart.source` 源码有 5 个：`startup`、`resume`、`clear`、`compact`、`branch`；官方文档只列前 4 个。
- 无 matcher 匹配全部 source，包括 `compact`、`resume`、`clear`、`branch`。
- matcher 规则是精确比较、`|` 列表或非锚定正则；`matcher: "start"` 会匹配 `startup`，要精确应写 `^startup$`。
- Qwen 不会在 resume 时自动跳过 `SessionStart`；需要跳过时只能靠 matcher，例如 `startup|clear|compact`。

### contextFileName 的真实语义

`contextFileName` 可以是字符串或字符串数组，默认扩展目录下的 `QWEN.md`；不存在的文件会被过滤。

- 文件在会话启动或刷新时读取一次，缓存在 `userMemory`；不是每个请求重新读盘。
- 每个请求重建 system prompt 时都携带这段缓存，位置在 base 与媒体指引之后、`appendPrompt` 与 autoMemory 之前。
- 每个文件包在 `--- Context from: <路径> ---` 与 `--- End of Context from: <路径> ---` 之间；文件间用空行连接。
- 没有显式的文件体积上限，只受模型上下文窗口限制；40 KiB 正文会成为每轮固定成本。
- 压缩只替换对话历史，不改变 system prompt 的 context 缓存，所以压缩后约束仍在且不会重复拼接。
- safe mode 跳过 context/rules 加载；扩展 context 不受 workspace trust 门槛限制。

### hook 注入落点

- `SessionStart.additionalContext` 进入 **system instruction**，包在 `<qwen:session-start-context hidden="true">` 中；
  新值替换旧块，不会在多次 SessionStart 间累积。
- `UserPromptSubmit.additionalContext` 进入当轮 **用户消息 part**，包在 `<qwen:user-prompt-submit-context>` 中；
  完全相同的 payload 在本会话只会追加一次。
- 纯文本 stdout 只有 `SessionStart`、`UserPromptSubmit`、`UserPromptExpansion` 会提升为上下文；其他事件只作 system message。
- `PostCompact` 的输出与退出码被忽略；`PreCompact` 的 `additionalContext` 会并入压缩提示词，上限 4000 字符。
- command hook 默认超时 60 秒；本仓库 `timeout: 10` 即 10 秒。退出码 0/2/其他的语义与 Qoder 类似。

### 环境变量与扩展清单

Qwen 为 command hook 设置的目录变量只有 `QWEN_PROJECT_DIR`、`CLAUDE_PROJECT_DIR`、`GEMINI_PROJECT_DIR`；
`${CLAUDE_PLUGIN_ROOT}` 是命令字符串加载时的替换，不是运行期环境变量。**Qwen 不设置** `QODER_PLUGIN_DATA` 或
`CLAUDE_PLUGIN_DATA`。扩展清单的 `hooks` 可以是内联对象或文件路径；没有时回退 `hooks/hooks.json`。

### 压缩、恢复与清除（Qwen）

- `SessionStart` 在 startup/resume/clear/compact/branch 都会触发；`resume` 不会自动跳过。
- 自动压缩会异步重发 `SessionStart(compact)`，手工压缩通过 `startChat(..., Compact)` 重发；手工路径在没有新输出时会恢复压缩前 context。
- `contextFileName` 由 system prompt 重建保证，不依赖 SessionStart。
- `clear` 清空对话但保留 `userMemory`，约束仍加载。

### 重复矩阵

| 载体 | 进入位置 | 触发 | 去重 |
| --- | --- | --- | --- |
| `contextFileName` | system prompt 的 context 层 | 每请求携带 | 只按同一物理文件 realpath 去重 |
| `.qwen/rules` baseline | system prompt 的 context 层 | 每请求携带 | 只按同一物理文件 realpath 去重 |
| `.qwen/rules` 条件规则 | 命中工具路径时注入 | 本会话一次 | 按规则级 once |
| `SessionStart` hook | system instruction 的 session-start 块 | 每次 SessionStart | 新值替换旧块；无内容去重 |
| `UserPromptSubmit` hook | 当轮用户消息 part | 每次提示 | 完全相同 payload 本会话只送一次 |

宿主没有跨载体内容去重。本仓库开发态会同时生成 `.qwen/rules` 与安装包里的 `constraints/`，两者是复制件，
同时启用会重复；生产安装只应保留其中一种。

### 本仓库用法与已知限制

- Qwen 包只用清单 `contextFileName` 承载约束，没有约束 hook；`SessionStart` 与 `UserPromptSubmit` 只保留时间 hook。
- Qwen 不提供插件数据目录，[inject-clock.js](../shared/scripts/inject-clock.js) 在 Qwen 下不会写状态；因此 turn 固定为 1，
  elapsed 为 `unavailable`。这是当前实现的已知限制，不是宿主文档承诺。
- 时间格式与关闭方式见 [time-awareness.md](time-awareness.md)。

## DeepSeek Harness

### 原生 hook 与实验桥接

DSH 没有内建的 Claude 风格 hooks。需要兼容 `hooks.json` 时，挂载实验包 `@deepseek-ai/dsh-hooks-claude-code`；
它默认不安装，读取进程级 `configPath`，只运行 `type: command` 的 hook。支持 7 个事件：
`SessionStart`、`UserPromptSubmit`、`PreToolUse`、`PostToolUse`、`Stop`、`SubagentStart`、`SubagentStop`。

- `SessionStart` 在当前 checkout 只会产生 `startup` 与 `resume`；类型里有 `clear`/`compact`，但没有生产者。
- 没有 `PreCompact`、`PostCompact`、`SessionEnd`；压缩不会重放桥接的 SessionStart context。
- 桥接的 context 是 **user 消息**，不是 system prompt section；resume 时会再次注入，可能与旧 context 重复。
- 桥接不读 `plugin.json`；`claude-code-mods` 也不是 hooks 桥接，mods 的 `hooks.json` 需要另挂该实验包。

### systemPrompt.section 的渲染语义

插件在 `apply(ctx)` 中调用 `ctx.systemPrompt.section({name, order, text, interpolate})` 注册 section。

- 注册一次；每次 proposed step 的 `agent/pre-step` 前装配一次，section 回调在该次装配中求值；重试复用装配，不重跑回调。
- 每次模型尝试只提交与已提交 projection 的差异：文本未变不写，变化追加带 replacement 提示的 section，压缩后重建完整 system head。
- `order` 升序；同 order 按名称排序；同名 section 只有一个生效者，外层 scope 先遍历、内层同名覆盖。
- 压缩后下一次模型尝试重建完整 system head；恢复时从日志对账，文本未变不重复提交。
- `interpolate: false` 可避免规则正文里的模板变量被展开。

### 指令链、时间与 skills

`dsh-agent-instructions` 是独立机制：它把 `AGENTS.md`/`CLAUDE.md` 作为 user-role 指令消息注入，首次 eligible pre-step 发一条
`<system-reminder>`，之后只在成功的 `read`/`write`/`edit` 触碰后追加 `Updated instructions from: <路径>`；预算按用户链与
项目链分别计算，默认 65536 字节。压缩遮蔽 baseline 后，下一次 pre-step 会重新折叠；恢复时按可见 identity 对账。

- `dsh-time-context` 是 preset 插件，不是所有组合都有：Web 的 `standard`/`ptc` 挂载，`minimal` 与 `dsh-base` 不含。
- 时间在 `agent/pre-step` 追加 user 消息；默认刷新间隔 10 分钟，`0` 表示每个 eligible step 都注入；压缩后没有立即补注入。
- skill catalog 在首次 `agent/pre-step` 注入一条 `<available_skills>` 持久 user 消息；正文只在 `skill` 工具调用时读取。

### 注入选型

| 需求 | DSH 做法 |
| --- | --- |
| 常驻约束 | `ctx.systemPrompt.section()`，随每次 assembly 进入系统提示，压缩后重建 |
| 会话启动的对话式上下文 | `agent/pre-step` 折叠消息，或 `agent/created` 中 `agent.inject()` |
| 工具执行后的上下文 | `tools/post-execute` 返回 `additionalContexts`；`tools/pre-execute` 没有 context 通道 |
| 停止边界续跑 | `agent/turn-stopping` 中 `agent.steer()` |
| 压缩前后 | 没有可阻断的 `PreCompact`/`PostCompact`；只能观察 `session/event`，或依赖 section 重建与指令链重折叠 |

### 本仓库接线

[plugins/dsh/src/index.js](../plugins/dsh/src/index.js) 在 `apply` 时读取包内 `rules/global-user-constraints.md`，
以 name `global-user-constraints`、order 400、`interpolate: false` 注册 section；只对两个用户级 `AGENTS.md` 做 sha256 去重，
且是加载时快照，文件变化需重载插件。skills 以 rank 700、source `bundled` 注册 provider；时间不由本包注入。

## 对照表

| 维度 | Qoder | Qwen Code | DSH |
| --- | --- | --- | --- |
| hook 可用性 | 原生 | 原生 | 无内建；实验桥接可选 |
| 事件数 | 29 | 23 | 桥接 7 |
| SessionStart source | startup/resume/clear/new/compact | startup/resume/clear/compact/branch | 桥接仅 startup/resume |
| 无 matcher 是否覆盖 compact | 是 | 是 | 桥接无 compact 生产者 |
| compact 后重注入 | 触发 SessionStart(compact) | 触发 SessionStart(compact)；contextFileName 另保证 | systemPrompt 重建；桥接不重放 |
| 约束注入载体 | hook additionalContext | contextFileName 进 system prompt | systemPrompt.section |
| 注入落点 | 对话上下文 | SessionStart 进 system instruction；UserPromptSubmit 进 user 消息 | system 消息 |
| 跨载体内容去重 | 仓库脚本按 sha256 | 宿主只按 realpath/相同 payload | 仓库只按两个用户 AGENTS.md 的 sha256 |
| 默认超时 | command 600 秒 | command 60 秒 | 桥接 command 自带 timeout |
| 插件数据目录 | QODER_PLUGIN_DATA | 不提供 | 无对应 hook 契约 |

## 本仓库映射与取舍

| 平台 | 约束载体 | 触发/发送 | 压缩后 | 代价与风险 |
| --- | --- | --- | --- | --- |
| Qoder | `SessionStart` hook 注入全文 | 会话启动、clear/new、compact 重注入；resume 跳过 | 依赖 hook 重触发；静态 rules 另刷新 | 每次会话注入一次全文；插件 rules 不被宿主加载 |
| Qwen | `contextFileName` | 启动/刷新读一次，每请求随 system prompt 发送 | 不受压缩影响 | 每轮固定 token 成本；与 `.qwen/rules` 同时存在会重复 |
| DSH | `systemPrompt.section` | 每次 assembly 求值，admission 只提交差异 | 重建 system head | 加载时快照；只对两个用户 AGENTS.md 去重 |

选择依据：Qoder 插件 rules 不被 CLI 加载，只能 hook 注入；Qwen 的 `contextFileName` 在压缩后仍随 system prompt 发送，
比 hook 的 SessionStart 注入更稳；DSH 的 section 是系统提示的正式载体，压缩后由 admission 重建。时间注入是独立需求，
不复用约束载体。

## 未验证与已知矛盾

- Qoder compact/resume 全链路、37 KiB 上下文的实际计费与截断、`name` 的 UI 显示未验证。
- Qoder 同步 `PostCompact.additionalContext` 不进入对话是源码结论，未做端到端验证；异步路径未验证。
- Qwen `branch` source 只在源码确认，官方文档未列；自动压缩的异步 SessionStart 存在竞态，未验证。
- DSH 桥接的 resume 重复、PTC 下 PostToolUse 上下文丢失、time-context 压缩后 10 分钟空档均为源码推断。
- DSH 当前 checkout 没有 `clear`/`compact` 的 SessionStart 生产者；`clear` 行为无法验证。
- DSH 实验包 README 的事件计数为 23/30，与本仓库统计不一致，不作为本仓库断言。
- Qwen 不设置插件数据目录；本仓库时间 hook 在 Qwen 下没有跨轮状态，turn 与 elapsed 受限。

本文件与 `scripts/check.sh` 的 Markdown 校验一起维护。
