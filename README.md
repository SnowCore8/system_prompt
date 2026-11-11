# AI 编码代理 system prompt

本仓库维护全局约束规则、`system-prompt-authoring` skill，以及打包它们的用户级 Qoder 插件。规则正文与插件源是唯一真源；插件内 `rules` 软链指向根级 `rules/`，仓库只有一份规则。
`.qwen/` 是统一入口，`.qoder`、`.qoder-cn` 指向它。改规则、skill 或插件前先读本文件。维护者：仓库所有者。
插件的使用者文档（规则激活、hook、边界）见插件 [README](plugins/global-user-constraints/README.md)。

## 目录

| 路径 | 作用 |
|---|---|
| `plugins/global-user-constraints/` | 用户级 Qoder 插件包 |
| `plugins/marketplace.json` | 市场描述文件，承载 `category`/`tags` 等市场字段 |
| `rules/global-user-constraints.md` | 约束规则正文 |
| `.qwen/` | 统一入口（本身不匹配 `.qoder*` 模式）；`rules`、`plugins` 软链指向根级同名目录 |
| `.qoder` / `.qoder-cn` | 指向 `.qwen` 的软链 |
| `scripts/dist.sh` | 插件分发打包脚本 |

## 编辑

1. 改规则：编辑 `rules/global-user-constraints.md`。
2. 改 skill：编辑 `plugins/global-user-constraints/skills/system-prompt-authoring/`。
3. 只改软链目标，不另建副本。

## 验证

```bash
python3 plugins/global-user-constraints/skills/system-prompt-authoring/script/check.py --strict rules/global-user-constraints.md
python3 -m unittest discover -s plugins/global-user-constraints/skills/system-prompt-authoring/script
qodercn plugins validate plugins/global-user-constraints
```

机检只验证 Markdown 格式（依赖 `markdown-it-py`，无构建步骤）；内容规则 S1–S13 按 `SKILL.md` 人工核对。
`qodercn` 与 `qodercli` 是同一 CLI 的两个入口，按环境选用；`plugins validate` 的 `--strict` 让警告也计失败，`--json` 输出结构化报告。hook 测试见插件 README。

本地安装 smoke test 用临时目录，避免污染当前项目：

```bash
PLUGIN_ROOT="$(pwd)/plugins/global-user-constraints"
SMOKE_CWD="$(mktemp -d)"
qodercli --cwd "$SMOKE_CWD" plugin install --scope local "$PLUGIN_ROOT"
qodercli --cwd "$SMOKE_CWD" plugin list --json
```

## 打包

在仓库根目录运行 `scripts/dist.sh`：
脚本按 `HEAD` 推导版本 `0.1.<改动插件的提交数（不含 plugin.json）>`（迁移前 `.qoder/plugins/` 路径的提交一并计入，避免版本回退），写回 manifest（要随代码提交），按短 commit id 生成 `global-user-constraints-<commit>.zip` 到仓库根目录；同一 commit 重复运行版本不变，其余未提交改动让文件名追加 `-dirty`。
打包用 `cp -aL` 解引用软链（`rules/` 在 zip 内是真实文件），排除 `.DS_Store`、`__pycache__`、`.pyc`、`.qoder/settings.local.json` 与嵌套 `.qoder/`；临时目录在脚本退出时删除。
zip 根目录含 `.qoder-plugin/plugin.json` 与 `rules/global-user-constraints.md`；结构校验后默认运行 `qodercn plugins validate`（`--no-validate` 跳过）。zip 已在 `.gitignore` 忽略；成功后删除根目录旧 zip，只留本次产物。
