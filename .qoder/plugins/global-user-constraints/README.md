# Global User Constraints Plugin

把仓库根目录 `AGENTS.md` 的规则、`system-prompt-authoring` skill、TS→C++ 翻译流水线的 agent 定义、手动审查命令和每次事件注入当前时间的 hook 打成一个 Qoder 插件。

源文件：

- 规则源：`.qoder/plugins/global-user-constraints/rules/global-user-constraints.md`；根 `AGENTS.md` 是指向它的软链。插件运行时不加载 `rules/`，该目录只是本仓库的规则事实源（见「边界」）。
- skill 源：`.qoder/plugins/global-user-constraints/skills/system-prompt-authoring`；项目 `.qoder/skills` 是指向整个插件 `skills/` 目录的软链。
- agent 源：`.qoder/plugins/global-user-constraints/agents`；项目 `.qoder/agents` 是指向它的软链。

## 结构

| 路径 | 作用 |
|---|---|
| `.qoder-plugin/plugin.json` | 插件 manifest |
| `rules/global-user-constraints.md` | 规则正文，仓库根 `AGENTS.md` 软链的目标；插件运行时不加载 |
| `skills/system-prompt-authoring/` | 起草与审计指令文件的 skill |
| `agents/` | TS→C++ 翻译流水线：`Translator.md`、`Critic.md`、`Fixer.md`、`Orchestrator.md` |
| `workflows/ts2cpp.js` | 把四个 agent 串成流水线的工作流脚本 |
| `commands/constraints-check.md` | 手动触发约束审查 |
| `hooks/hooks.json` | 时间注入 hook 配置 |
| `scripts/inject-time.py` | 向支持 `additionalContext` 的事件注入当前本地时间 |
| `scripts/test_inject_time.py` | hook 的表驱动测试 |
| `qoder.md` / `qoderwork.md` | 插件级系统指令 |

## 安装与校验

校验插件目录（`--strict` 让警告也以退出码 1 结束，`--json` 输出结构化报告）：

```bash
qodercn plugins validate .qoder/plugins/global-user-constraints
```

本地安装 smoke test 使用临时目录，不要污染当前项目：

```bash
PLUGIN_ROOT="$(pwd)/.qoder/plugins/global-user-constraints"
SMOKE_CWD="$(mktemp -d)"
qodercli --cwd "$SMOKE_CWD" plugin install --scope local "$PLUGIN_ROOT"
qodercli --cwd "$SMOKE_CWD" plugin list --json
```

## 工作流

`workflows/ts2cpp.js` 把四个 agent 串成一条流水线：Translate → Critique →（Fix → 再 Critique）→ Gate。

- 脚本是纯 JavaScript，首句必须是 `export const meta`；脚本本身没有文件、网络和 shell 权限，所有副作用都经 `agent()` 交给子代理，因此 Critics 写失败测试、Fixer 改代码都由各自子代理完成。
- 插件内注册名为 `global-user-constraints:ts2cpp`（`<plugin>:<meta.name>`）；用自然语言指名运行即可，例如「运行 global-user-constraints:ts2cpp，切片 xxx」。
- `args` 接受 `{ slice, tsPath, cppPath, maxRounds? }`，也可直接传切片描述字符串；`maxRounds` 默认 3。
- 只有 `severity` 为 `需修复` / `阻断放行` 的分歧进入修复循环，`记录` 的不修。
- 修复轮次用尽仍有未修分歧，或 Fixer 返回非「已修复」状态时，返回值 `escalated` 为 true，放行与否仍由 Orchestrator 门禁判定。
- 调用 agent 时先按裸名（`Translator` 等），遇到 `Unknown agent type` 时回退到 `global-user-constraints:` 前缀，兼容项目级 agent 与插件安装两种注册方式。

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
python3 -B -m unittest discover -s .qoder/plugins/global-user-constraints/scripts -p 'test_*.py'
```

测试覆盖 9 个受支持事件的注入输出、未支持事件和非法 payload 的静默行为。

## 打包

在仓库根目录运行分发脚本：

```bash
scripts/dist.sh
```

脚本按当前 `HEAD` 推导版本 `0.1.<改动插件的提交数>`，写回 manifest，再用短 commit id 生成 `global-user-constraints-<commit>.zip` 到仓库根目录；同一 commit 重复运行版本不变。
版本写回之外的未提交改动会让文件名追加 `-dirty`；写回的版本要随代码提交。
打包排除 `.DS_Store`、`__pycache__`、`.pyc`、`.qoder/settings.local.json` 和嵌套的 `.qoder/` 目录。
zip 根目录直接包含 `.qoder-plugin/plugin.json`；结构校验后默认对插件目录运行 `qodercn plugins validate`（校验对象是源目录，不是 zip；`qodercn` 不在 PATH 时跳过并提示），`--no-validate` 可跳过。
zip 是生成物，已在 `.gitignore` 中忽略。

## 边界

- 插件不能携带 always-on 规则：规则引擎只扫描 `~/.qoder-cn/rules`、项目 `.qoder/rules`，以及向上遍历父目录的 `.qoder*/rules`；插件目录不在扫描范围内，`rules` 也不是合法 manifest 键（会被判为 `unknown_field` 并忽略）。要在其他项目生效，需把规则文件放进上述任一目录，或改用 hook 注入。
- 这是用户级插件，不替代企业 `global-security-guard`；企业插件仍是 managed，用户不能关闭。
- 不要把 zip 或规则文件上传到公网平台；只走企业内网或已批准的分发通道。
- Hook 只注入当前时间，不拦截工具调用；规则本身仍要求人工审查与真实输出验证。
