# Global User Constraints Plugin

把 `system-prompt-authoring` skill、手动审查命令和每次事件注入当前时间的 hook 打成一个 Qoder 插件。规则正文唯一真源在仓库根级 `rules/global-user-constraints.md`，打包时随包分发。插件安装后规则不会自动加载；按「安装与校验」中的规则激活步骤复制一次。

源文件：

- 规则源：`rules/global-user-constraints.md`（仓库根级，打包时随包分发）；`.qwen/rules` 软链指向它，`.qoder`、`.qoder-cn` 经 `.qwen` 解析到同一份。安装场景需按「安装与校验」复制到用户规则目录。
- 插件源：`plugins/global-user-constraints`；`.qwen/plugins` 软链指向根级 `plugins/`。
- skill 源：`plugins/global-user-constraints/skills/system-prompt-authoring`。

## 结构

| 路径 | 作用 |
|---|---|
| `rules/` | 约束规则正文（软链到根级 `rules/`，打包时解引用为真实文件） |
| `.qoder-plugin/plugin.json` | 插件 manifest |
| `skills/system-prompt-authoring/` | 起草与审计指令文件的 skill |
| `commands/constraints-check.md` | 手动触发约束审查 |
| `hooks/hooks.json` | 时间注入 hook 配置 |
| `scripts/inject-time.py` | 向支持 `additionalContext` 的事件注入当前本地时间 |
| `scripts/test_inject_time.py` | hook 的表驱动测试 |
| `qoder.md` / `qoderwork.md` | 插件级系统指令（宿主支持时加载；qodercli 1.1.81 的 `plugins validate` 不列此组件） |

## 安装与校验

校验插件目录（`--strict` 让警告也以退出码 1 结束，`--json` 输出结构化报告）。`qodercn` 与 `qodercli` 是同一 CLI 的两个入口，按环境选用其一：

```bash
qodercn plugins validate plugins/global-user-constraints
```

本地安装 smoke test 使用临时目录，不要污染当前项目：

```bash
PLUGIN_ROOT="$(pwd)/plugins/global-user-constraints"
SMOKE_CWD="$(mktemp -d)"
qodercli --cwd "$SMOKE_CWD" plugin install --scope local "$PLUGIN_ROOT"
qodercli --cwd "$SMOKE_CWD" plugin list --json
```

规则激活（安装场景必做）。复制源取决于安装方式：本地目录安装用仓库根级 `rules/`，zip 或市场安装用插件安装目录下的 `rules/`（含 `.qoder-plugin/plugin.json` 的目录）：

```bash
mkdir -p ~/.qoder-cn/rules
cp <插件目录>/rules/global-user-constraints.md ~/.qoder-cn/rules/
```

插件包内含 `rules/global-user-constraints.md`，但宿主不从包内加载约束：`qodercli 1.1.81` 的 `plugins validate` 只加载 skills/agents/commands/hooks，不加载 `rules/`。安装后仍要把规则复制到 `~/.qoder-cn/rules`，否则约束不生效。

## Hook 行为

Hook 注册在 Qoder CLI 支持 `additionalContext` 的 9 个事件上，matcher 留空以匹配全部触发源：

- `SessionStart`、`UserPromptSubmit`、`PreToolUse`、`PostToolUse`、`PostToolUseFailure`
- `SubagentStart`、`Notification`、`CwdChanged`、`FileChanged`

- 解释器用 `python`（PATH 上需有，3.7+），并以 `-X utf8` 启动；Windows 只提供 `python.exe` 没有 `python3`，同时该参数固定 stdin/stdout 编码，避免 ANSI 代码页下中文注入失败。
- 读取 stdin 的事件 JSON，从 `hook_event_name` 取事件名。
- 输出 `hookSpecificOutput.hookEventName` 与 `hookSpecificOutput.additionalContext`，内容为 `当前时间：YYYY-MM-DD HH:MM:SS +HH:MM`。
- 事件名不在支持列表、stdin 不是 JSON 对象时静默退出 0，不输出内容。
- 不支持 `additionalContext` 的事件（如 `Stop`、`PermissionRequest`、`PostCompact`、`InstructionsLoaded`）未注册。

## Hook 测试

```bash
python3 -B -m unittest discover -s plugins/global-user-constraints/scripts -p 'test_*.py'
```

测试覆盖 9 个受支持事件的注入输出、未支持事件和非法 payload 的静默行为。

## 打包

在仓库根目录运行分发脚本：

```bash
scripts/dist.sh
```

脚本按当前 `HEAD` 推导版本 `0.1.<改动插件的提交数（不含 plugin.json）>`（迁移前位于 `.qoder/plugins/` 的提交一并计入，避免版本回退），写回 manifest，再用短 commit id 生成 `global-user-constraints-<commit>.zip` 到仓库根目录；同一 commit 重复运行版本不变。
版本写回之外的未提交改动会让文件名追加 `-dirty`；写回的版本要随代码提交。
打包排除 `.DS_Store`、`__pycache__`、`.pyc`、`.qoder/settings.local.json` 和嵌套的 `.qoder/` 目录。
打包时先把插件目录复制到临时目录并用 `cp -aL` 解引用软链，`rules/` 在 zip 内是真实文件；临时目录在脚本退出时删除。
zip 根目录直接包含 `.qoder-plugin/plugin.json` 与 `rules/global-user-constraints.md`；结构校验后默认对插件目录运行 `qodercn plugins validate`，`--no-validate` 可跳过。
zip 是生成物，已在 `.gitignore` 中忽略。打包成功后脚本删除仓库根目录里的旧 zip，只保留本次产物。

## 边界

- 规则生效目录：`~/.qoder-cn/rules`、项目 `.qoder/rules`，以及向上遍历父目录的 `.qoder*/rules`；本仓库的规则正文在根级 `rules/`，经 `.qwen/rules` 软链供 `.qoder`、`.qoder-cn` 解析，`.qwen` 本身不匹配 `.qoder*` 模式。安装场景见「安装与校验」的规则激活步骤。
- 不要把插件、规则文件或 zip 上传到公网平台；只走企业内网或已批准的分发通道。
- Hook 只注入当前时间，不拦截工具调用；规则本身仍要求人工审查与真实输出验证。
