# AI 编码代理 system prompt

本仓库维护全局约束、`system-prompt-authoring` skill、TS→C++ 翻译流水线的 agent 定义，以及把它们打包在一起的用户级 Qoder 插件。
插件包在 `plugins/global-user-constraints/`，约束规则正文在 `rules/`，两者是本仓库的唯一真源；插件内的 `rules` 软链指向根级 `rules/`，打包时解引用，仓库仍只有一份规则。
`.qwen/` 是统一入口，`.qoder`、`.qoder-cn` 指向它，三个点目录解析到同一份源。改规则、改 skill、改 agent 或改插件前先读本文件。
安装插件后需按插件 README 把规则复制到用户规则目录，规则才会生效。维护者：仓库所有者。

Markdown 没有构建步骤；格式机检依赖 `markdown-it-py`。插件 zip 由 `scripts/dist.sh` 打包，产物在仓库根目录。

## 目录

| 路径 | 作用 |
|---|---|
| `plugins/global-user-constraints/` | 插件包：skill、agent、审查命令、时间注入 hook、工作流、规则软链 |
| `plugins/global-user-constraints/.qoder-plugin/plugin.json` | 插件 manifest |
| `plugins/global-user-constraints/skills/system-prompt-authoring/` | skill 源 |
| `plugins/global-user-constraints/agents/` | TS→C++ 翻译流水线的四个 agent 定义源 |
| `plugins/global-user-constraints/workflows/` | TS→C++ 翻译流水线的工作流源 |
| `plugins/marketplace.json` | 本仓库插件的市场描述文件，承载 `category`/`tags` 等市场字段 |
| `rules/global-user-constraints.md` | 约束规则正文 |
| `.qwen/` | 统一入口目录；`rules`、`plugins` 软链指向根级同名目录 |
| `.qoder` / `.qoder-cn` | 指向 `.qwen` 的软链，供对应工具约定读取同一份源 |
| `scripts/dist.sh` | 分发脚本：按插件提交数生成版本，按当前 commit id 打包到仓库根目录 |

## 编辑

1. 改规则：编辑 `rules/global-user-constraints.md`。
2. 改 skill：编辑 `plugins/global-user-constraints/skills/system-prompt-authoring/`。
3. 改 agent：编辑 `plugins/global-user-constraints/agents/`。
4. 不要另建副本。`.qwen` 下的 `rules`、`plugins` 只是入口软链，改目标，不改软链。

## 验证

```bash
python3 plugins/global-user-constraints/skills/system-prompt-authoring/script/check.py --strict rules/global-user-constraints.md
python3 -m unittest discover -s plugins/global-user-constraints/skills/system-prompt-authoring/script
qodercn plugins validate plugins/global-user-constraints
```

机检只验证 Markdown 格式；内容规则 S1–S13 按 `SKILL.md` 人工核对。

## 分发

```bash
scripts/dist.sh
```

版本推导、`-dirty` 标记、规则软链解引用、zip 结构校验和旧 zip 清理的细节见插件 README 的「打包」节与 `scripts/dist.sh`。
版本写回要随代码提交；zip 是生成物，已在 `.gitignore` 中忽略。

插件包内容与 hook 行为见插件 [README](plugins/global-user-constraints/README.md)。不要把规则文件、插件或 zip 上传到公网平台；走企业内网或已批准的通道。

约束规则生效目录：`~/.qoder-cn/rules`、项目 `.qoder/rules`，以及向上遍历父目录的 `.qoder*/rules`。本仓库把规则正文放在根级 `rules/`，经 `.qwen/rules` 软链供 `.qoder`、`.qoder-cn` 解析；`.qwen` 本身不匹配 `.qoder*` 模式，只作为软链入口。
