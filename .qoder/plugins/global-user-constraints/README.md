# Global User Constraints Plugin

把仓库根目录 `AGENTS.md` 的规则、`system-prompt-authoring` skill、手动审查命令和每次事件注入当前时间的 hook 打成一个 Qoder 插件。

源文件：

- 规则源：`.qoder/plugins/global-user-constraints/rules/global-user-constraints.md`；根 `AGENTS.md` 是指向它的软链。
- skill 源：`.qoder/plugins/global-user-constraints/skills/system-prompt-authoring`；项目 `.qoder/skills` 是指向整个插件 `skills/` 目录的软链。

## 结构

| 路径 | 作用 |
|---|---|
| `.qoder-plugin/plugin.json` | 插件 manifest |
| `rules/global-user-constraints.md` | always-on 规则，内容来自 `AGENTS.md` |
| `skills/system-prompt-authoring/` | 起草与审计指令文件的 skill |
| `commands/constraints-check.md` | 手动触发约束审查 |
| `hooks/hooks.json` | 时间注入 hook 配置 |
| `scripts/inject-time.c` | 向支持 `additionalContext` 的事件注入当前本地时间 |
| `scripts/bin/` | 编译产物（`inject-time`、`inject-time.exe`），已被 `.gitignore` 忽略 |
| `qoder.md` / `qoderwork.md` | 插件级系统指令 |

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

- hook 直接启动 `scripts/bin/` 下的二进制，无运行时解释器依赖；POSIX 用 `inject-time`，Windows 包内为 `inject-time.exe`，由 `scripts/dist.sh` 按平台生成对应 `command`。
- 读取 stdin 的事件 JSON，取顶层 `hook_event_name`；嵌套值里的同名字段不会误匹配。
- 输出 `hookSpecificOutput.hookEventName` 与 `hookSpecificOutput.additionalContext`，内容为 `当前时间：YYYY-MM-DD HH:MM:SS +HH:MM`。
- 时间来自平台本地时间 API：POSIX 用 `localtime_r` + `%z`，Windows 用 `GetLocalTime` 与 UTC 差值计算偏移，含夏令时。
- 事件名不在支持列表、stdin 不是 JSON 对象时静默退出 0，不输出内容。
- 不支持 `additionalContext` 的事件（如 `Stop`、`PermissionRequest`、`PostCompact`、`InstructionsLoaded`）未注册。

## Hook 测试

```bash
scripts/build-hooks.sh
python3 -m unittest scripts.test_inject_time -v
```

测试运行 Linux 版二进制，覆盖 9 个受支持事件、未支持事件、非法与截断 payload、嵌套同名字段的静默或忽略行为。Windows 版二进制只做交叉编译，行为需在 Windows 上验证。

## 打包

在仓库根目录运行分发脚本：

```bash
scripts/dist.sh
```

脚本先调用 `scripts/build-hooks.sh` 编译两个平台的二进制，再按当前 `HEAD` 推导版本 `0.1.<改动插件的提交数>`，写回 manifest，用短 commit id 生成两个包到仓库根目录：

- `global-user-constraints-<commit>-linux-x64.zip`
- `global-user-constraints-<commit>-windows-x64.zip`

同一 commit 重复运行版本不变。版本写回之外的未提交改动会让文件名追加 `-dirty`；写回的版本要随代码提交。
每份 zip 只含本平台二进制，`hooks/hooks.json` 的 `command` 在打包时改写为对应文件名；Windows 用户解压后用 `plugin install` 安装该目录。
打包排除 `.DS_Store`、`__pycache__`、`.pyc` 和其他平台二进制；zip 根目录直接包含 `.qoder-plugin/plugin.json`，结构校验后默认调用 Qoder 离线校验器，`--no-validate` 可跳过。
zip 与 `scripts/bin/` 都是生成物，已在 `.gitignore` 中忽略。

## 边界

- 这是用户级插件，不替代企业 `global-security-guard`；企业插件仍是 managed，用户不能关闭。
- 不要把 zip 或规则文件上传到公网平台；只走企业内网或已批准的分发通道。
- Hook 只注入当前时间，不拦截工具调用；规则本身仍要求人工审查与真实输出验证。
