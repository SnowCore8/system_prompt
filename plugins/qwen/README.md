# 全局用户约束：Qwen Code 扩展

本包把全局用户约束、21 个 skill 与一个手动审查命令安装到 Qwen Code。约束由清单的 `contextFileName` 承载，
启动或刷新时读取并随每个请求发送；skill 按阶段加载。本文件只说明安装、生命周期集成、行为与边界，规则以
包内 `constraints/global-user-constraints.md` 为准。

维护者：SnowCore8。

## 包结构

| 路径 | 作用 |
|---|---|
| `qwen-extension.json` | 扩展清单，`contextFileName` 指向约束正文，`skills`、`commands`、`hooks` 指向对应目录或文件 |
| `hooks/qwen-hooks.json` | hook 配置，根目录用 `${CLAUDE_PLUGIN_ROOT}`（Qwen 替换为扩展根） |
| `constraints/global-user-constraints.md` | 全局用户约束正文 |
| `skills/` | 21 个 skill，含生命周期治理与各专业规范 |
| `commands/` | 手动审查命令 `constraints-check` |
| `scripts/` | 时间注入脚本 |

安装后的包为上述自包含结构；发布包用 `scripts/materialize.sh qwen <目标目录>` 从顶层真源组装，不依赖软链。

## 安装

```bash
curl -fLO https://cdn.jsdelivr.net/npm/@snowcore8/qwen-global-user-constraints@<版本>/global-user-constraints-qwen-<版本>.zip
qwen extensions install global-user-constraints-qwen-<版本>.zip
```

安装后开新会话生效：`contextFileName` 在启动或刷新时读取并缓存，随后每请求随 system prompt 发送。

## 生命周期集成

约束不依赖 hook：`contextFileName` 在启动或刷新时读取一次，此后每个请求随 system prompt 携带，因此 G0 受理
与压缩后的门禁判断都以同一份正文为依据。skill 启动时注册为 `<ext>:<name>`，调用时载入正文；`references/`
在正文引用后按需读取。

| 事件或机制 | 注入内容 | 生命周期作用 |
|---|---|---|
| `contextFileName` | 约束正文全文，包在 `--- Context from: <路径> ---` 标记中 | 每个请求都可用的规则依据 |
| `SessionStart` | 当前时间 | 会话起点的时区与 turn 基准 |
| `UserPromptSubmit` | 当前时间，包进 `<qwen:user-prompt-submit-context>` 标签 | 每轮请求的时间基准 |
| skills 注册 | `name` 与 `description` 索引 | S1–S6 按阶段加载对应规范 |

- 项目 `.qwen/rules` 与扩展 `contextFileName` 同时启用时宿主不去重，会重复；二选一。
- Qwen 不提供插件数据目录，时间 hook 通常不落盘，turn 恒为 1、elapsed 为 `unavailable`。
- hook 用 `node`（CI 用 Node 20），超时 10 秒；payload 非法或事件不在范围内时静默退出 0。

## 命令

`constraints-check` 读取包内约束，审查当前请求、方案或待执行命令；只审查，不执行被审查对象。命令输出先给
结论，再引用条款编号；不通过时不给可执行步骤。

## 验证

- 组装：`scripts/materialize.sh qwen /tmp/qwen-package`，核对 `qwen-extension.json`、`constraints/` 与 `skills/`。
- 制品：下载 zip 与 `.sha256` 后核对，校验和与 Release 附件一致。
- 运行：开新会话确认 `constraints/global-user-constraints.md` 已随 system prompt 发送；`/skills` 面板可确认
  21 个 skill 已注册，`/extensions` 可查看启用状态。

## 边界

- 时间 hook 只读宿主 payload 与系统时间；不修改项目文件，不联网。
- 扩展不写项目或用户级 rules，不修改 `AGENTS.md`；Qwen 不读取 `<project>/.qwen/AGENTS.md`，本包也不提供。
- 注入内容会进入模型上下文，敏感内容不要写进规则正文；只安装可信来源的包并核对 SHA256。
- 扩展的 `rules/` 在 Qwen 中只接受带 `paths:` 的条件规则，因此本包把约束放在 `constraints/` 并用
  `contextFileName` 承载，不使用扩展规则目录。
