# 提示词与纯规则清单

本文件是提示词、纯规则、混合、代码与元数据的分类清单；内容领域与 skill 主责见 `docs/content-map.md`。
维护者：SnowCore8。阅读时机：修改 rules、skill、命令、插件注入或仓库文档前。

## 分类

| 类别 | 含义 | 消费者 |
|---|---|---|
| P | 提示词：运行时进入模型上下文的内容 | 模型 |
| R | 纯规则：维护者、CI 或人类阅读，不自动进入模型上下文 | 人类/CI |
| H | 混合：同一文件或段落既被模型加载，又承载人类流程 | 两者 |
| C | 代码、脚本、测试、CI、宿主插件源码 | 运行时/CI |
| M | 清单、许可证、变更日志、第三方声明等元数据 | 宿主/平台/人类 |

## 台账

| 路径 | 类别 | 加载者或消费者 | 结论 |
|---|---|---|---|
| `rules/global-user-constraints.md` | P | DSH systemPrompt；Qoder/Qwen rules 与 hook；命令按需读取 | 常驻约束唯一真源 |
| `AGENTS.md` | P | DSH/Qwen/Qoder 项目指令 | 只放代理项目指令 |
| `CONTRIBUTING.md` | R | 人类贡献者与维护者 | 人类文档，不进入模型上下文 |
| `skills/*/SKILL.md` | P | 三端 skill 发现；正文按需加载 | 19 个 skill 入口 |
| `skills/*/references/*.md` | P | skill 按需读取 | 51 个；维护者材料在 `docs/` |
| `shared/commands/constraints-check.md` | P | Qoder/Qwen 命令；DSH 未注册 | 命令提示词 |
| `shared/scripts/*.py` | C | Qoder/Qwen hook | 提示词发射器，不是提示词正文 |
| `plugins/dsh/src/index.js`、hooks | C | 宿主运行时 | 注入与 skill 提供者 |
| `docs/*` | R | 维护者 | 不注入、不随包 |
| `README.md`、`GOVERNANCE.md`、`SECURITY.md`、`GLOSSARY.md`、`CHANGELOG.md` | R | 人类/GitHub/npm | 不自动加载 |
| `scripts/`、`tests/`、`.github/` | C | 维护者/CI | 不进入上下文、不随包 |
| `package.json`、三包清单、`plugins/marketplace.json` | M/C | npm、宿主、市场 | 清单 description 面向人类/UI，不是提示词 |
| 许可证、第三方声明 | M | 人类/平台 | 分发元数据 |

## 当前边界

- `AGENTS.md` 只承载代理项目指令；`CONTRIBUTING.md` 只承载人类贡献与发布流程。
- `skill-authoring` 不管辖本仓库打包；`system-prompt-authoring` 不复制本仓库的 40 KiB、`check.sh` 或来源表。
- `documentation-conventions` 使用通用文档事实，不陈述本仓库的软链或 CHANGELOG 事实。
- 所有 skill references 为 P。
- 机器校验规则在 `docs/markdown-check-rules.md`，不在 skill references 中重复。
- 发布 runbook 以 `docs/release.md` 为准；README、CONTRIBUTING、GOVERNANCE 只保留摘要与链接。
- Qoder 插件 `rules/` 当前不被 CLI 加载；DSH 不注册 `constraints-check` 命令；DSH 与 Qoder/Qwen hook 均注入 rules 原文，宿主解析另行处理。

## 目标结构

- `AGENTS.md`：真实文件，只放代理每次都要遵守的短规则。
- `CONTRIBUTING.md`：人类贡献、检出与发布流程。
- `rules/`：单一常驻约束真源；不新增会被 Qwen/Qoder 自动加载的第二个 `.md`。
- `skills/`：SKILL.md 与 references 只放模型规范；维护者流程移至 `docs/` 或 CONTRIBUTING。
- `docs/`：维护者材料、调研、发布 runbook 与内容地图。
- `shared/`：命令提示词（P）与注入脚本（C）分离。
- 三端入口与安装包：由 `scripts/assemble.sh`/`scripts/materialize.sh` 从顶层真源生成，不提交软链。
- `tests/`、`scripts/`、`.github/`：C，不进入上下文。
