# Global User Constraints Plugin

把仓库根目录 `AGENTS.md` 的规则、`system-prompt-authoring` skill、手动审查命令，以及注入当前时间与会话级规则的 hook 打成一个 Qoder 插件。

源文件：

- 规则源：`.qoder/plugins/global-user-constraints/rules/global-user-constraints.md`；根 `AGENTS.md` 是指向它的软链。
- skill 源：`.qoder/plugins/global-user-constraints/skills/system-prompt-authoring`；项目 `.qoder/skills` 是指向整个插件 `skills/` 目录的软链。

## 结构

| 路径 | 作用 |
|---|---|
| `.qoder-plugin/plugin.json` | 插件 manifest |
| `rules/global-user-constraints.md` | 规则正文，内容来自 `AGENTS.md`；由 hook 在 `SessionStart`、`SubagentStart` 注入 |
| `skills/system-prompt-authoring/` | 起草与审计指令文件的 skill |
| `commands/constraints-check.md` | 手动触发约束审查 |
| `hooks/hooks.json` | 时间与规则注入 hook 配置 |
| `scripts/inject-context.py` | 向支持 `additionalContext` 的事件注入当前本地时间；在 `SessionStart`、`SubagentStart` 追加规则正文 |
| `scripts/test_inject_context.py` | hook 的表驱动测试 |
| `qoder.md` / `qoderwork.md` | 插件级系统指令；当前 CLI 1.1.81 未读取，保留以兼容其他运行时 |

## 安装与校验

离线校验：

```bash
python3 ~/.qoder/plugins/cache/qoder-bundler/qoder-create-plugin/skills/create-plugin/scripts/validate_qoder_plugin.py .qoder/plugins/global-user-constraints
```

本地安装 smoke test 使用临时目录，不要污染当前项目：

```bash
PLUGIN_ROOT="$(pwd)/.qoder/plugins/global-user-constraints"
SMOKE_CWD="$(mktemp -d)"
qodercli --cwd "$SMOKE_CWD" plugin install --scope local "$PLUGIN_ROOT"
qodercli --cwd "$SMOKE_CWD" plugin list --json
```

## Hook 行为

Hook 注册在 Qoder CLI 支持 `additionalContext` 的 9 个事件上，matcher 留空以匹配全部触发源：

- `SessionStart`、`UserPromptSubmit`、`PreToolUse`、`PostToolUse`、`PostToolUseFailure`
- `SubagentStart`、`Notification`、`CwdChanged`、`FileChanged`

- 解释器用 `python`（PATH 上需有，3.7+），并以 `-X utf8` 启动；Windows 只提供 `python.exe` 没有 `python3`，同时该参数固定 stdin/stdout 编码，避免 ANSI 代码页下中文注入失败。
- 读取 stdin 的事件 JSON，从 `hook_event_name` 取事件名。
- 输出 `hookSpecificOutput.hookEventName` 与 `hookSpecificOutput.additionalContext`，内容为 `当前时间：YYYY-MM-DD HH:MM:SS +HH:MM`。
- `SessionStart`、`SubagentStart` 的输出在时间后追加 `rules/global-user-constraints.md` 正文（去掉 YAML frontmatter），使约束在无 `AGENTS.md` 的项目里也进入上下文。规则文件不可读时只注入时间。
- 事件名不在支持列表、stdin 不是 JSON 对象时静默退出 0，不输出内容。
- 不支持 `additionalContext` 的事件（如 `Stop`、`PermissionRequest`、`PostCompact`、`InstructionsLoaded`）未注册。

## Hook 测试

```bash
python3 -B -m unittest discover -s .qoder/plugins/global-user-constraints/scripts -p 'test_*.py'
```

测试覆盖 9 个受支持事件的注入输出、`SessionStart`/`SubagentStart` 的规则注入、其余事件不注入规则、未支持事件和非法 payload 的静默行为。

## 打包

在仓库根目录运行分发脚本：

```bash
scripts/dist.sh
```

脚本按当前 `HEAD` 推导版本 `0.1.<改动插件的提交数>`，写回 manifest，再用短 commit id 生成 `global-user-constraints-<commit>.zip` 到仓库根目录；同一 commit 重复运行版本不变。
版本写回之外的未提交改动会让文件名追加 `-dirty`；写回的版本要随代码提交。
打包排除 `.DS_Store`、`__pycache__`、`.pyc`、`.qoder/settings.local.json` 和嵌套的 `.qoder/` 目录。
zip 根目录直接包含 `.qoder-plugin/plugin.json`；结构校验后默认调用 Qoder 离线校验器，`--no-validate` 可跳过。
zip 是生成物，已在 `.gitignore` 中忽略。

## 边界

- 这是用户级插件，不替代企业 `global-security-guard`；企业插件仍是 managed，用户不能关闭。
- 不要把 zip 或规则文件上传到公网平台；只走企业内网或已批准的分发通道。
- Hook 只注入当前时间与规则，不拦截工具调用；规则本身仍要求人工审查与真实输出验证。
- manifest 的 `rules` 字段保留给支持它的运行时；Qoder CLI 1.1.81 会忽略该字段（`plugin validate` 输出 `Unknown field 'rules' will be ignored`），所以规则改由 hook 注入。
