# Global User Constraints Plugin

把仓库根目录 `AGENTS.md` 的规则、`system-prompt-authoring` skill、手动审查命令和 secret 提交 hook 打成一个 Qoder 插件。

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
| `hooks/hooks.json` | PreToolUse hook 配置 |
| `scripts/check-secret-commit.py` | 拦截明显 secret 提交 |
| `scripts/test_check_secret_commit.py` | hook 的表驱动测试 |
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

- 只识别真实的 `git commit` 子命令；`git log --grep commit`、`echo git commit`、`--help`、`--dry-run` 不会触发检查。
- 扫描命令文本和 `git diff --cached`；`a` 作为独立短选项出现（如 `-a`、`-am`、`-av`）或使用 `--all` 时，额外扫描 `git diff`。
- 命中明显的 private key、AWS/GitHub/Slack/Stripe/OpenAI/Google key、password/secret 赋值时，`exit 2` 阻止提交。
- 不打印 secret 原文，只报告疑似类型。
- 公开 key、publishable key、`.pub` 不在拦截范围；它们仍受“真正公开且安全”规则约束。
- 不是完整 secret 扫描器；二进制、历史提交、未跟踪文件不检查，带路径的提交只检查暂存区。

## Hook 测试

```bash
python3 -B -m unittest discover -s .qoder/plugins/global-user-constraints/scripts -p 'test_*.py'
```

测试在临时 git 仓库中覆盖暂存/未暂存 secret、`-a`/`-am`/`--all`、非提交命令、help/dry-run、公开 key 和非法 payload。

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
- Hook 只拦明显 secret 提交，规则本身仍要求人工审查与真实输出验证。
