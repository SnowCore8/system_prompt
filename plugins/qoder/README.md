# 全局用户约束：Qoder 插件

维护者：SnowCore8。本文只说明安装与运行行为，不定义规则；规则以包内 `rules/global-user-constraints.md` 为准。

## 结构与安装

| 路径 | 作用 |
|---|---|
| `.qoder-plugin/plugin.json` | 插件清单 |
| `hooks/hooks.json` | hook 配置，根目录用 `${QODER_PLUGIN_ROOT}` |
| `rules/global-user-constraints.md` | 全局用户约束正文 |
| `skills/` | 二十个通用规范 skill |
| `commands/` | 手动审查命令 |
| `scripts/` | 约束与时间注入脚本 |

安装后的包为上述自包含结构；发布包用 `scripts/materialize.sh qoder <目标目录>` 从顶层真源组装。
`qoderclicn plugins install` 只接受市场名、HTTPS zip URL 或本地目录，本地 zip 需先解压：

```bash
unzip global-user-constraints-qoder-<版本>.zip -d global-user-constraints-qoder-<版本>
qoderclicn plugins install ./global-user-constraints-qoder-<版本> --scope user
```

也可传 npm 安装包的直链（必须以 `.zip` 结尾；私有仓库 Release 不能匿名下载）：

```bash
qoderclicn plugins install \
  https://cdn.jsdelivr.net/npm/@snowcore8/qoder-global-user-constraints@<版本>/global-user-constraints-qoder-<版本>.zip \
  --scope user
```

安装后开新会话生效。本地市场先运行 `scripts/assemble.sh qoder` 与
`qoderclicn plugins validate plugins/qoder`；marketplace 来源传上级 `plugins/` 目录，不能只加
`plugins/marketplace.json`，否则安装报 ENOENT。

## 行为

- `SessionStart`：注入包内规则全文，`source=resume` 时跳过；规则缺失、读取失败或超过 40 KiB 时改输出提示。
- 去重：项目目录及其祖先的 `.qoder/rules/global-user-constraints.md`、`AGENTS.md`、`AGENTS.local.md`，
  以及用户配置根（`QODERCN_CONFIG_DIR`、`QODER_CONFIG_DIR`、`~/.qoder-cn`、`~/.qoder`）下的
  `rules/global-user-constraints.md`、`AGENTS.md`，任一与正文 sha256 相同即跳过注入。
- `UserPromptSubmit`：提醒 `Never violate global user constraints.` + 三行时间（turn、时区与间隔）；
  `source=compact` 另注入两行压缩后时间。
- `PreToolUse` / `PostToolUse` / `PostToolUseFailure`：只注入一行时间。
- `SessionEnd`：清理本 session 在插件数据目录的时间状态。
- hook 用 `node`（CI 用 Node 20），超时 10 秒；payload 非法或事件不支持时静默退出 0。

## 命令

`constraints-check` 读取包内规则，审查当前请求、方案或待执行命令；只审查，不执行被审查对象。

## 卸载

直接卸载插件即可；插件不写项目或用户级 rules，没有需要清理的约束文件。

## 安全边界

- 约束 hook 只读包内规则与去重候选文件；时间 hook 只写插件数据目录并在 `SessionEnd` 清理，不联网。
- 注入内容会进入模型上下文，敏感内容不要写进规则正文；只安装可信来源的包并核对 SHA256。
