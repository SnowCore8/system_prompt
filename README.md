# AI 编码代理 system prompt

本仓库维护全局约束规则、`system-prompt-authoring` skill，以及打包它们的用户级 Qoder 插件。规则正文与插件源是唯一真源，仓库只有一份规则。
改规则、skill 或插件前先读本文件。维护者：仓库所有者。
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
qoderclicn plugins validate plugins/global-user-constraints
```

机检只验证 Markdown 格式（依赖 `markdown-it-py`，无构建步骤）；内容规则 S1–S13 按 `SKILL.md` 人工核对。hook 测试见插件 README。
校验用 `qoderclicn` 而非入口脚本 `qodercn`：后者把首参当路径判断，仓库根有 `plugins/` 目录，会被当成 IDE 目标。

本地安装 smoke test 用临时目录，避免污染当前项目：

```bash
TMP="$(mktemp -d)"
qoderclicn --cwd "$TMP" plugins install --scope local "$PWD/plugins/global-user-constraints"
qoderclicn --cwd "$TMP" plugins list --json
```

## 打包

在仓库根目录运行 `scripts/dist.sh`，版本推导、软链解引用、排除项、结构校验与旧包清理见脚本 `--help`；脚本写回的 `.qoder-plugin/plugin.json` 版本随代码提交，zip 产物被 `.gitignore` 忽略。
