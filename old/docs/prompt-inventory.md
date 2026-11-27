# 提示词与纯规则清单

本文件是提示词、纯规则、混合、代码与元数据的分类台账。内容领域与 skill 主责见 [content-map.md](content-map.md)；
阶段与门禁的定义由 `project-lifecycle-governance` 裁定。维护者：SnowCore8。阅读时机：修改 rules、skill、命令、
插件注入或仓库文档前。

## 分类

| 类别 | 含义 | 消费者 |
|---|---|---|
| P | 提示词：运行时进入模型上下文的内容 | 模型 |
| R | 纯规则：维护者、CI 或人类阅读，不自动进入模型上下文 | 人类/CI |
| H | 混合：同一文件或段落既被模型加载，又承载人类流程 | 两者 |
| C | 代码、脚本、测试、CI、宿主插件源码 | 运行时/CI |
| M | 清单、许可证、变更日志、第三方声明等元数据 | 宿主/平台/人类 |

## 台账

| 路径 | 类别 | 加载者或消费者 | 生命周期位置 | 结论 |
|---|---|---|---|---|
| `rules/global-user-constraints.md` | P | DSH systemPrompt；Qoder hook；Qwen contextFileName；命令按需读取 | 贯穿 S0–S6，G0 授权判定的依据 | 常驻约束与门禁判定唯一真源 |
| `AGENTS.md` | P | DSH/Qwen/Qoder 项目指令 | 本仓库每个变更的 S0–S5 执行要求 | 只放智能体项目指令 |
| `CONTRIBUTING.md` | R | 人类贡献者与维护者 | S0–S5 的变更流程与 G4 校验要求 | 人类文档，不进入模型上下文 |
| `GOVERNANCE.md` | R | 维护者、审查者 | 角色、决策权、R2 审查、例外、组合与升级 | 治理规则，不进入模型上下文 |
| `SECURITY.md` | R | 报告者、维护者 | 各阶段安全责任、披露与支持范围 | 安全策略，不进入模型上下文 |
| `GLOSSARY.md` | R | 维护者、文档作者 | 阶段、门禁、工件与度量术语的写法 | 术语与写作口径 |
| `README.md` | R | 人类、宿主市场页 | S1 的问题、S2 的内容结构与安装入口 | 仓库入口，不自动加载 |
| `CHANGELOG.md` | R | 人类/GitHub/npm | 已发布变更的版本记录 | 记录性内容只在此处 |
| `docs/*.md` | R | 维护者 | 加载规则、hook、发布、时间与校验规则的说明 | 不注入、不随包 |
| `plugins/qoder/README.md`、`plugins/qwen/README.md`、`plugins/dsh/README.md` | R | 使用者、维护者 | 三包在 S0 注入与 S5 发布的安装与行为说明 | 随包分发的人类文档 |
| `npm/qoder/README.md`、`npm/qwen/README.md` | R | 使用者 | S5 发布后的安装入口 | 随 npm 包分发 |
| `skills/*/SKILL.md` | P | 三端 skill 发现；正文按需加载 | 各 skill 的生命周期定位与门禁证据 | 21 个 skill 入口 |
| `skills/*/references/lifecycle.md` | P | skill 按需读取 | 该 skill 在 S0–S6 的阶段契约 | 阶段执行的证据清单 |
| `skills/*/references/*.md` | P | skill 按需读取 | 阶段内的规则、矩阵与检查表 | 结构与分布见 `content-map.md` |
| `skills/project-lifecycle-governance/references/*.md` | P | skill 按需读取 | 阶段、门禁、敏捷、角色、度量、组合、映射与模板 | 生命周期层细节 |
| `shared/commands/constraints-check.md` | P | Qoder/Qwen 命令；DSH 未注册 | 任一门禁前的自查 | 命令提示词 |
| `shared/scripts/*.js` | C | Qoder/Qwen hook | G0 前的常驻注入与压缩后提醒 | 提示词发射器，不是提示词正文 |
| `plugins/qoder/hooks/`、`plugins/qwen/hooks/` | C | 宿主运行时 | 会话启动、每轮提醒、压缩后与工具事件 | hook 配置 |
| `plugins/dsh/src/*.js` | C | 宿主运行时 | `systemPrompt.section` 注入与 skill 提供者 | 注入与 skill 提供者 |
| `scripts/`、`tests/`、`.github/` | C | 维护者/CI | G4 校验、S5 发布与回滚 | 不进入上下文、不随包 |
| `package.json`、三包清单、`plugins/marketplace.json` | M/C | npm、宿主、市场 | S5 发布的版本与组件声明 | 清单 description 面向人类/UI，不是提示词 |
| 许可证、第三方声明 | M | 人类/平台 | S5 分发元数据 | 分发元数据 |

## 生命周期中的加载位置

| 阶段与门禁 | 需要的提示词或规则 | 加载方式 |
|---|---|---|
| S0 / G0 | 全局用户约束、`AGENTS.md`、本仓库治理与安全文档 | 常驻注入或项目指令；治理与安全文档人工阅读 |
| S1 / G1 | `project-lifecycle-governance`、编写类 skill、架构与安全 skill | 按任务加载 skill 正文与 references |
| S2 / G2 | 架构、结构、接口、测试、发布与版本控制 skill 的计划章节 | 按任务加载；门禁模板取 `references/templates.md` |
| S3 / G3 | 代码、命名、注释、重构、并发、调试 skill | 按增量加载；正文只读必要小节 |
| S4 / G4 | 测试、安全、性能、文档 skill 的验证章节与校验脚本规则 | 校验命令与 `docs/markdown-check-rules.md` |
| S5 / G5 | 发布、仓库治理、版本控制与安全 skill 的发布章节 | 按 `release.md` 执行 |
| S6 / G6 | 生命周期治理与文档 skill 的收尾章节 | 收尾报告模板与复盘记录 |

## 当前边界

- `AGENTS.md` 只承载智能体项目指令；`CONTRIBUTING.md` 只承载人类贡献流程；`GOVERNANCE.md` 只承载角色、
  审查、例外与组合规则。
- `skill-authoring` 不管辖本仓库打包；`system-prompt-authoring` 不复制本仓库的 64 KiB、`check.sh` 或来源表。
- `documentation-conventions` 使用通用文档事实，不陈述本仓库的软链或 CHANGELOG 事实。
- 所有 skill references 为 P；`lifecycle.md` 与维度文件同为 P，只被对应 skill 读取。
- 机器校验规则在 [markdown-check-rules.md](markdown-check-rules.md)，不在 skill references 中重复。
- 发布 runbook 以 [release.md](release.md) 为准；README、CONTRIBUTING、GOVERNANCE 只保留摘要与链接。
- Qoder 插件 `rules/` 当前不被 CLI 加载；DSH 不注册 `constraints-check` 命令。
- 约束注入路径：Qoder 由 `SessionStart` hook 注入；Qwen 由清单 `contextFileName` 在启动/刷新读取一次，
  随后每请求随 system prompt 携带；DSH 由 bundle 经 `ctx.systemPrompt.section()` 注入。
- 阶段与门禁的判定文本只在 `rules/` 与 `project-lifecycle-governance` 中维护；docs 与包 README 只引用结论。

## 结构约定

- `AGENTS.md`：真实文件，只放智能体每次都要遵守的短规则。
- `CONTRIBUTING.md`：人类贡献、检出、校验与发布引用。
- `rules/`：单一常驻约束真源；不新增会被 Qwen/Qoder 自动加载的第二个 `.md`。
- `skills/`：`SKILL.md` 与 references 只放模型规范；维护者流程移至 `docs/` 或 `CONTRIBUTING.md`。
- `docs/`：维护者材料、加载与注入说明、发布手册与内容地图。
- `shared/`：命令提示词（P）与注入脚本（C）分离。
- 三端入口与安装包：由 `scripts/assemble.sh` 与 `scripts/materialize.sh` 从顶层真源生成，不提交软链。
- `tests/`、`scripts/`、`.github/`：C，不进入上下文。
