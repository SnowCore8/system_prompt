# AI 编码代理 system prompt

本仓库维护全局约束规则、`system-prompt-authoring` skill，以及把它们打包在一起的用户级 Qoder 插件。
约束规则正文在 `rules/`，插件包在 `plugins/global-user-constraints/`，两者是本仓库的唯一真源；插件内的 `rules` 软链指向根级 `rules/`，仓库只有一份规则。
`.qwen/` 是统一入口，`.qoder`、`.qoder-cn` 指向它。改规则、改 skill 或改插件前先读本文件。维护者：仓库所有者。

插件的规则激活、hook 行为与边界见插件 [README](plugins/global-user-constraints/README.md)。

Markdown 没有构建步骤；格式机检依赖 `markdown-it-py`。

## 目录

| 路径 | 作用 |
|---|---|
| `plugins/global-user-constraints/` | 插件包：skill、审查命令、时间注入 hook、规则软链 |
| `plugins/global-user-constraints/.qoder-plugin/plugin.json` | 插件 manifest |
| `plugins/global-user-constraints/skills/system-prompt-authoring/` | skill 源 |
| `plugins/marketplace.json` | 本仓库插件的市场描述文件，承载 `category`/`tags` 等市场字段 |
| `rules/global-user-constraints.md` | 约束规则正文 |
| `.qwen/` | 统一入口目录（本身不匹配 `.qoder*` 模式）；`rules`、`plugins` 软链指向根级同名目录 |
| `.qoder` / `.qoder-cn` | 指向 `.qwen` 的软链，供对应工具约定读取同一份源 |
| `scripts/dist.sh` | 插件分发打包脚本 |

## 编辑

1. 改规则：编辑 `rules/global-user-constraints.md`。
2. 改 skill：编辑 `plugins/global-user-constraints/skills/system-prompt-authoring/`。
3. 不要另建副本。`.qwen` 下的 `rules`、`plugins` 只是入口软链，改目标，不改软链。

## 验证

```bash
python3 plugins/global-user-constraints/skills/system-prompt-authoring/script/check.py --strict rules/global-user-constraints.md
python3 -m unittest discover -s plugins/global-user-constraints/skills/system-prompt-authoring/script
qodercn plugins validate plugins/global-user-constraints
```

机检只验证 Markdown 格式；内容规则 S1–S13 按 `SKILL.md` 人工核对。
`qodercn` 与 `qodercli` 是同一 CLI 的两个入口，按环境选用其一；`plugins validate` 的 `--strict` 让警告也以退出码 1 结束，`--json` 输出结构化报告。
hook 测试见插件 README「Hook 测试」节。

本地安装 smoke test 使用临时目录，不要污染当前项目：

```bash
PLUGIN_ROOT="$(pwd)/plugins/global-user-constraints"
SMOKE_CWD="$(mktemp -d)"
qodercli --cwd "$SMOKE_CWD" plugin install --scope local "$PLUGIN_ROOT"
qodercli --cwd "$SMOKE_CWD" plugin list --json
```

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
