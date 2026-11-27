# 全局用户约束：Qoder 插件

维护者：SnowCore8。本文只说明安装与运行行为，不定义规则；规则以包内 `rules/global-user-constraints.md` 为准。

安装后 `SessionStart` 由 hook 注入约束全文，`UserPromptSubmit` 每轮提醒并注入当前时间；hook 不写用户级
rules，卸载时无需手动清理约束文件。项目或用户配置中已有同内容约束时，按 sha256 跳过注入。

## 结构

| 路径 | 作用 |
|---|---|
| `.qoder-plugin/plugin.json` | Qoder 插件清单 |
| `hooks/hooks.json` | hook 配置，根目录用 `${QODER_PLUGIN_ROOT}` |
| `rules/global-user-constraints.md` | 全局用户约束正文 |
| `skills/` | 二十个通用规范 skill |
| `commands/` | 手动审查命令 |
| `scripts/` | 约束与时间注入脚本 |

以上为安装后的自包含结构；源码包只保留清单、hooks 与说明。

- 发布包：使用 `scripts/materialize.sh qoder <目标目录>` 从顶层真源组装。
- 本地市场：先运行 `scripts/assemble.sh qoder` 填充本目录，并运行
  `qoderclicn plugins validate plugins/qoder` 确认组件齐全，再交给 Qoder 的 marketplace；生成目录不提交。

## 安装

`qoderclicn plugins install` 只接受市场名、远程 HTTPS zip URL 或本地目录；本地 zip 需先解压：

```bash
unzip global-user-constraints-qoder-<版本>.zip -d global-user-constraints-qoder-<版本>
qoderclicn plugins install ./global-user-constraints-qoder-<版本> --scope user
```

也可以直接传入 Release 附件的 HTTPS zip URL。安装后开新会话即可。约束由 `SessionStart` hook 注入，
不写入用户级或项目级 rules。

## 卸载

直接卸载插件即可。当前版本不写项目目录或用户级 rules，没有需要手动清理的约束文件；从 0.44.0
及更早版本升级的，见下节。

## 从 0.44.0 及更早版本升级

这些版本会在首次 `SessionStart` 把约束写入用户级 rules，且卸载不会删除。升级到本版本后，请手动删除一次：

```bash
rm ~/.qoder-cn/rules/global-user-constraints.md   # CN
rm ~/.qoder/rules/global-user-constraints.md       # 国际版
```

Windows 为 `%USERPROFILE%\.qoder-cn\rules\global-user-constraints.md` 或
`%USERPROFILE%\.qoder\rules\global-user-constraints.md`。之后约束完全由 `SessionStart` hook 注入。

## 命令

`constraints-check` 读取包内 `rules/global-user-constraints.md`，审查当前请求、方案或待执行命令；
只审查，不执行被审查对象。

## 行为

- `SessionStart`：读取包内 `rules/global-user-constraints.md` 注入全文；`source=resume` 时跳过。
- 去重：项目目录及其祖先（有 `.git` 时到 `.git` 为止，无 `.git` 时到文件系统根）的
  `.qoder/rules/global-user-constraints.md`、`AGENTS.md`、`AGENTS.local.md`；用户配置根
  （`QODERCN_CONFIG_DIR`、`QODER_CONFIG_DIR`、`~/.qoder-cn`、`~/.qoder`）下的
  `rules/global-user-constraints.md`、`AGENTS.md`。任一文件与正文 sha256 相同即跳过注入。
- 规则缺失、读取失败或正文超过 40 KiB：不注入全文，改为输出对应提示。
- `source=compact`：另由 `inject-compact.js` 注入 `Never violate global user constraints.` 与一行压缩后时间。
- `UserPromptSubmit`：提醒 `Never violate global user constraints.` + 完整 DSH 三行时间。
- `PreToolUse` / `PostToolUse` / `PostToolUseFailure`：注入一行时间，不注入完整时间块。
- `SessionEnd`：清理当前 session 在插件数据目录的时间状态，不注入上下文。
- payload 非法或事件不支持时静默退出 0。
- 解释器用 `node`（PATH 上需可用；CI 使用 Node 20）；`timeout` 为 10 秒。

## 安全边界

- 约束 hook 只读包内规则与去重候选文件；时间 hook 只写插件数据目录的 clock 状态，并在 `SessionEnd`
  清理。除该目录外不写盘、不联网。
- 注入的约束全文会进入模型上下文；敏感内容不要写进规则正文。
- 安装即执行：只安装可信来源的包，并核对 SHA256 校验和。
