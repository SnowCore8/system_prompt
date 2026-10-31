# AI 编码代理 system prompt

本仓库维护全局约束、`system-prompt-authoring` skill、TS→C++ 翻译流水线的 agent 定义，以及把它们打包在一起的用户级 Qoder 插件。插件包是唯一事实源；根 `AGENTS.md`、项目 skills 和 agents 路径都是指向它的软链。改规则、改 skill、改 agent 或改插件前先读本文件。
安装插件后需按插件 README 复制规则到用户规则目录，规则才会生效。维护者：仓库所有者。

Markdown 没有构建步骤；格式机检依赖 `markdown-it-py`。插件 zip 由 `scripts/dist.sh` 打包，产物在仓库根目录。

## 目录

| 路径 | 作用 |
|---|---|
| `AGENTS.md` | 指向 `.qoder/plugins/global-user-constraints/rules/` 下规则文件的软链 |
| `.qoder/plugins/global-user-constraints/` | 插件包：规则、skill、agent、审查命令、时间注入 hook |
| `.qoder/plugins/global-user-constraints/rules/global-user-constraints.md` | 规则正文；经根 `AGENTS.md` 软链生效 |
| `.qoder/plugins/global-user-constraints/skills/system-prompt-authoring/` | skill 源 |
| `.qoder/plugins/global-user-constraints/agents/` | TS→C++ 翻译流水线的四个 agent 定义源 |
| `.qoder/plugins/global-user-constraints/workflows/` | TS→C++ 翻译流水线的工作流源 |
| `.qoder/plugins/marketplace.json` | 本仓库插件的市场描述文件，承载 `category`/`tags` 等市场字段 |
| `.qoder/skills/` | 指向插件 `skills/` 目录的软链 |
| `.qoder/agents/` | 指向插件 `agents/` 目录的软链 |
| `.qwen` | 指向 `.qoder` 的兼容软链，供只认 `.qwen` 的工具使用 |
| `scripts/dist.sh` | 分发脚本：按插件提交数生成版本，按当前 commit id 打包到仓库根目录 |

## 编辑

1. 改规则：编辑 `.qoder/plugins/global-user-constraints/rules/global-user-constraints.md`；`AGENTS.md` 跟随软链。
2. 改 skill：编辑 `.qoder/plugins/global-user-constraints/skills/system-prompt-authoring/`；`.qoder/skills` 跟随软链。
3. 改 agent：编辑 `.qoder/plugins/global-user-constraints/agents/`；`.qoder/agents` 跟随软链。
4. 不要另建副本。路径经软链解析时，改目标，不改副本。

## 验证

```bash
python3 .qoder/skills/system-prompt-authoring/script/check.py --strict AGENTS.md
python3 -m unittest discover -s .qoder/skills/system-prompt-authoring/script
qodercn plugins validate .qoder/plugins/global-user-constraints
```

机检只验证 Markdown 格式；内容规则 S1–S13 按 `SKILL.md` 人工核对。

## 分发

```bash
scripts/dist.sh
```

版本推导、`-dirty` 标记、zip 结构校验和旧 zip 清理的细节见插件 README 的「打包」节与 `scripts/dist.sh`。
版本写回要随代码提交；zip 是生成物，已在 `.gitignore` 中忽略。

插件包内容与 hook 行为见插件 [README](.qoder/plugins/global-user-constraints/README.md)。不要把规则文件、插件或 zip 上传到公网平台；走企业内网或已批准的通道。

插件规则生效目录：`~/.qoder-cn/rules`、项目 `.qoder/rules`，以及向上遍历父目录的 `.qoder*/rules`。本仓库的规则正文放在插件内，经根 `AGENTS.md` 软链引用。
