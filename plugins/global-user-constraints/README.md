# Global User Constraints Plugin

用户级 Qoder 插件，组件见「结构」。约束正文随包分发，但安装后必须按「规则激活」复制一次才能生效。

## 结构

| 路径 | 作用 |
|---|---|
| `rules/` | 用户全局约束正文与中文译本 |
| `.qoder-plugin/plugin.json` | 插件 manifest |
| `skills/system-prompt-authoring/` | 起草与审查指令文件的 skill |
| `commands/constraints-check.md` | 手动触发约束审查 |
| `hooks/hooks.json` | 时间注入 hook 配置 |
| `scripts/inject-time.py` | 向支持 `additionalContext` 的事件注入当前本地时间 |
| `scripts/test_inject_time.py` | hook 的表驱动测试 |
| `qoder.md` | 插件级指令文件（宿主支持时加载；`plugins validate` 不列此组件） |

## 规则激活

复制源取决于安装方式：源码目录安装用源码树根级 `rules/`，zip 或市场安装用插件安装目录下的 `rules/`（含 `.qoder-plugin/plugin.json` 的目录）：

```bash
mkdir -p ~/.qoder-cn/rules
cp <插件目录>/rules/global-user-constraints.md ~/.qoder-cn/rules/
```

中文译本 `rules/global-user-constraints.zh-CN.md` 可单独激活；不要与英文原文同时复制，避免同一规则被加载两次。

宿主不从包内加载约束：`plugins validate` 只校验 skills/agents/commands/hooks，不处理 `rules/`。

## Hook 行为

Hook 注册在支持 `additionalContext` 的 9 个事件上，matcher 留空匹配全部触发源；其余事件（如 `Stop`、`PermissionRequest`、`PostCompact`、`InstructionsLoaded`）未注册：

- `SessionStart`、`UserPromptSubmit`、`PreToolUse`、`PostToolUse`、`PostToolUseFailure`
- `SubagentStart`、`Notification`、`CwdChanged`、`FileChanged`

- 解释器用 `python`（PATH 上需有，3.7+），以 `-X utf8` 启动：Windows 只有 `python.exe` 没有 `python3`，且该参数固定 stdin/stdout 编码，避免 ANSI 代码页下中文注入失败。
- 读取 stdin 的事件 JSON，从 `hook_event_name` 取事件名；输出 `hookSpecificOutput.hookEventName` 与 `hookSpecificOutput.additionalContext`，内容为 `当前时间：YYYY-MM-DD HH:MM:SS +HH:MM`。
- 事件名不在支持列表、stdin 不是 JSON 对象时静默退出 0，不输出内容。

## Hook 测试

在插件目录下运行：

```bash
python3 -B -m unittest discover -s scripts -p 'test_*.py'
```

测试覆盖 9 个受支持事件的注入输出、未支持事件和非法 payload 的静默行为。

## 边界

- 约束生效目录：`~/.qoder-cn/rules`、项目 `.qoder/rules`，以及向上遍历父目录的 `.qoder*/rules`。
- 不要把插件、约束文件或 zip 上传到公网平台；只走企业内网或已批准的分发通道。
- Hook 不拦截工具调用；约束本身仍要求人工审查与真实输出验证。
