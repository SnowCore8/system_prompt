# AI 编码代理 system prompt

本仓库维护全局约束规则、`system-prompt-authoring` skill，以及把它们打包在一起的用户级 Qoder 插件。
约束规则正文在 `rules/`，插件包在 `plugins/global-user-constraints/`，两者是本仓库的唯一真源；插件内的 `rules` 软链指向根级 `rules/`，仓库只有一份规则。
`.qwen/` 是统一入口，`.qoder`、`.qoder-cn` 指向它。改规则、改 skill 或改插件前先读本文件。维护者：仓库所有者。

插件的安装、规则激活、hook 行为与打包分发见插件 [README](plugins/global-user-constraints/README.md)。

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
```

机检只验证 Markdown 格式；内容规则 S1–S13 按 `SKILL.md` 人工核对。
插件校验、hook 测试与安装 smoke test 见插件 README「安装与校验」「Hook 测试」节。
