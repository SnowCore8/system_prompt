# 用户全局约束：Qoder 插件

Qoder 插件包。安装后由 `SessionStart` hook 注入约束全文，并在 `SessionStart` 与
`UserPromptSubmit` 注入当前时间；已经通过规则或 `AGENTS.md` 加载同一份约束时自动跳过。

## 结构

| 路径 | 作用 |
|---|---|
| `.qoder-plugin/plugin.json` | Qoder 插件清单 |
| `hooks/hooks.json` | `command` + `args` 形式，根目录用 `${QODER_PLUGIN_ROOT}` |
| `rules/` | 约束正文，软链到仓库顶层 `rules/` |
| `skills/` | 十一个 skill，软链到仓库顶层 `skills/` |
| `commands/`、`scripts/` | 软链到仓库 `shared/` |

## 安装

Qoder 的 `plugins validate` 会拒绝解析到包外的路径，因此不要直接安装带软链的 `plugins/qoder`
目录。二选一：

- 下载 Release 里的 `global-user-constraints-qoder-<版本>.zip`，执行
  `qoderclicn plugins install <zip> --scope user`；
- 或先物化成自包含目录再安装：

  ```bash
  scripts/materialize.sh qoder /tmp/qoder-package
  qoderclicn plugins install /tmp/qoder-package --scope user
  ```

## 行为

- `SessionStart`：约束脚本读取 `rules/global-user-constraints.md` 注入全文（约 32 KB），
  注入前比对用户级 `~/.qoder-cn/rules/`（国际版 `~/.qoder/rules/`）、`AGENTS.md`、
  项目 `.qoder/rules/` 与 `AGENTS.local.md`，同内容则跳过；`source` 为 `resume` 时也跳过
  （历史里已有），`startup`/`new`/`clear`/`compact` 才注入；
  时间脚本注入当前本地时间、UTC 偏移、时区与星期。
- `UserPromptSubmit`：只注入时间，保证长会话与压缩后仍然准确。
- 规则缺失、payload 非法、事件不在范围内时静默退出 0。
- 解释器用 `python`（PATH 上需有 3.7+），`-X utf8` 固定 stdio 编码；`timeout` 为 10 秒。

## 安全边界

- hook 只读：读包内规则、去重候选文件与系统时间；不写盘、不联网、不持久化。
- 注入的约束全文会进入模型上下文；敏感内容不要写进规则正文。
- 安装即执行：只安装可信来源的包，并核对 SHA256 校验和。

## 测试

测试在仓库 `shared/scripts/`，从仓库根运行：

```bash
python3 -B -m unittest discover -s shared/scripts -p 'test_*.py'
scripts/check.sh
```
