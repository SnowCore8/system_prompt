# Global User Constraints Plugin

把仓库根目录 `AGENTS.md` 的规则、`system-prompt-authoring` skill、手动审查命令和 secret 提交 hook 打成一个 Qoder 插件。

源文件：

- 规则源：`.qoder/plugins/global-user-constraints/rules/global-user-constraints.md`；根 `AGENTS.md` 是指向它的软链。
- skill 源：`.qoder/plugins/global-user-constraints/skills/system-prompt-authoring`；项目 `.qoder/skills/system-prompt-authoring` 是指向它的软链。

## 结构

| 路径 | 作用 |
|---|---|
| `.qoder-plugin/plugin.json` | 插件 manifest |
| `rules/global-user-constraints.md` | always-on 规则，内容来自 `AGENTS.md` |
| `skills/system-prompt-authoring/` | 起草与审计指令文件的 skill |
| `commands/constraints-check.md` | 手动触发约束审查 |
| `hooks/hooks.json` | PreToolUse hook 配置 |
| `scripts/check-secret-commit.py` | 拦截明显 secret 提交 |
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

Hook 只匹配 `Bash`、`Shell`、`PowerShell`、`cmd` 工具调用：

- 只在命令包含 `git commit` 时检查。
- 扫描命令文本和 `git diff --cached`；`-a`、`-am`、`--all` 时额外扫描 `git diff`。
- 命中明显的 private key、AWS/GitHub/Slack/Stripe/OpenAI/Google key、password/secret 赋值时，`exit 2` 阻止提交。
- 不打印 secret 原文，只报告疑似类型。
- 公开 key、publishable key、`.pub` 不在拦截范围；它们仍受“真正公开且安全”规则约束。
- 不是完整 secret 扫描器；二进制、历史提交、未跟踪文件不检查。

## 打包

```bash
cd .qoder/plugins/global-user-constraints
zip -r ../global-user-constraints-0.1.0.zip . \
  -x "**/.DS_Store" "__MACOSX/*" ".qoder/settings.local.json" ".qoder/**"
```

zip 根目录必须直接包含 `.qoder-plugin/plugin.json`。打包后校验：

```bash
python3 ~/.qoder/plugins/cache/qoder-bundler/qoder-create-plugin/skills/create-plugin/scripts/validate_qoder_plugin.py .qoder/plugins/global-user-constraints-0.1.0.zip
```

## 边界

- 这是用户级插件，不替代企业 `global-security-guard`；企业插件仍是 managed，用户不能关闭。
- 不要把 zip 或规则文件上传到公网平台；只走企业内网或已批准的分发通道。
- Hook 只拦明显 secret 提交，规则本身仍要求人工审查与真实输出验证。
