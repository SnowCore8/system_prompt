# 全局用户约束：Qoder 插件

本包把全局用户约束、21 个 skill 与一个手动审查命令安装到 Qoder。约束在会话启动时进入上下文，skill 按阶段
加载；本文件只说明安装、生命周期集成、行为与边界，规则以包内 `rules/global-user-constraints.md` 为准。

维护者：SnowCore8。

## 包结构

| 路径 | 作用 |
|---|---|
| `.qoder-plugin/plugin.json` | 插件清单：`skills`、`commands`、`hooks` 指向对应目录或文件 |
| `hooks/hooks.json` | hook 配置，根目录用 `${QODER_PLUGIN_ROOT}` |
| `rules/global-user-constraints.md` | 全局用户约束正文 |
| `skills/` | 21 个 skill，含生命周期治理与各专业规范 |
| `commands/` | 手动审查命令 `constraints-check` |
| `scripts/` | 约束注入与时间注入脚本 |

安装后的包为上述自包含结构；发布包用 `scripts/materialize.sh qoder <目标目录>` 从顶层真源组装，不依赖软链。

## 安装

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

## 生命周期集成

Qoder CLI 不加载插件内的 `rules/`，因此约束由 hook 注入：G0 受理依赖 `SessionStart` 的全文注入，长会话靠
`UserPromptSubmit` 的提醒维持，压缩后由 `SessionStart(source=compact)` 补回。skill 由 `skills/` 自动发现，
启动只建立索引，正文在调用时读取。

| 事件 | 注入内容 | 生命周期作用 |
|---|---|---|
| `SessionStart` | 包内规则全文；`source=resume` 跳过；规则缺失、读取失败或超过 64 KiB 时改输出提示 | G0 受理时有同一份约束可用 |
| `SessionStart`（`matcher: compact`） | 一句约束提醒与两行时间 | 压缩后恢复门禁判断依据 |
| `UserPromptSubmit` | `Never violate global user constraints.` 提醒加三行时间（turn、时区与间隔） | 每轮请求重申约束与时间基准 |
| `PreToolUse` / `PostToolUse` / `PostToolUseFailure` | 一行时间 | 记录工具动作的时间基准 |
| `SessionEnd` | 清理本 session 在插件数据目录的时间状态 | 收尾时不留残留状态 |

- 去重：项目目录及其祖先的 `.qoder/rules/global-user-constraints.md`、`AGENTS.md`、`AGENTS.local.md`，
  以及用户配置根（`QODERCN_CONFIG_DIR`、`QODER_CONFIG_DIR`、`~/.qoder-cn`、`~/.qoder`）下的
  `rules/global-user-constraints.md`、`AGENTS.md`，任一与正文 sha256 相同即跳过注入。
- hook 用 `node`（CI 用 Node 20），超时 10 秒；payload 非法或事件不支持时静默退出 0。

## 命令

`constraints-check` 读取包内规则，审查当前请求、方案或待执行命令；只审查，不执行被审查对象。命令输出先给
结论，再引用条款编号；不通过时不给可执行步骤。

## 验证

- 组装：`scripts/materialize.sh qoder /tmp/qoder-package`；校验：`qoderclicn plugins validate /tmp/qoder-package`。
- 冒烟：`qoderclicn --cwd /tmp plugins install --scope local /tmp/qoder-package`，开新会话确认约束已注入、
  skill 可被发现。
- 制品：下载 zip 与 `.sha256` 后核对，校验和与 Release 附件一致。

## 边界

- 约束 hook 只读包内规则与去重候选文件；时间 hook 只写插件数据目录并在 `SessionEnd` 清理，不联网。
- 插件不写项目或用户级 rules，也不修改 `AGENTS.md`；卸载插件即可移除注入，没有需要清理的约束文件。
- 注入内容会进入模型上下文，敏感内容不要写进规则正文；只安装可信来源的包并核对 SHA256。
- 插件内的 `rules/` 只是注入源，不被 CLI 当作规则目录加载；宿主原生规则仍以项目或用户 `.qoder/rules` 为准。
