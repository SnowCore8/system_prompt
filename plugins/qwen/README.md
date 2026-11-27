# 全局用户约束：Qwen Code 扩展

维护者：SnowCore8。本文只说明安装与运行行为，不定义规则；规则以包内
`constraints/global-user-constraints.md` 为准。

## 结构与安装

| 路径 | 作用 |
|---|---|
| `qwen-extension.json` | 扩展清单，`contextFileName` 指向约束正文 |
| `hooks/qwen-hooks.json` | hook 配置，根目录用 `${CLAUDE_PLUGIN_ROOT}`（Qwen 替换为扩展根） |
| `constraints/global-user-constraints.md` | 全局用户约束正文 |
| `skills/` | 二十个通用规范 skill |
| `commands/` | 手动审查命令 |
| `scripts/` | 时间注入脚本 |

安装后的包为上述自包含结构；发布包用 `scripts/materialize.sh qwen <目标目录>` 从顶层真源组装。

```bash
curl -fLO https://cdn.jsdelivr.net/npm/@snowcore8/qwen-global-user-constraints@<版本>/global-user-constraints-qwen-<版本>.zip
qwen extensions install global-user-constraints-qwen-<版本>.zip
```

安装后开新会话生效：`contextFileName` 在启动或刷新时读取并缓存，随后每请求随 system prompt 发送。

## 行为

- `SessionStart` / `UserPromptSubmit`：只注入当前时间；后者会被包进
  `<qwen:user-prompt-submit-context>` 标签。
- 项目 `.qwen/rules` 与扩展 `contextFileName` 同时启用时宿主不去重，会重复；二选一。
- hook 用 `node`（CI 用 Node 20），超时 10 秒；payload 非法或事件不在范围内时静默退出 0。

## 命令

`constraints-check` 读取包内约束，审查当前请求、方案或待执行命令；只审查，不执行被审查对象。

## 安全边界

- 时间 hook 只读宿主 payload 与系统时间；Qwen 不提供插件数据目录，通常不落盘，turn 为 1、
  elapsed 为 `unavailable`；不修改项目文件，不联网。
- 注入内容会进入模型上下文，敏感内容不要写进规则正文；只安装可信来源的包并核对 SHA256。
