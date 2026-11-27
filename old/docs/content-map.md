# 内容结构地图

本文件描述内容层级、生命周期主线、21 个 skill 的主责与 references 结构，并记录相邻 skill 的边界归属。目录与
分发结构见 [README](../README.md)；提示词与纯规则的分类口径见 [prompt-inventory.md](prompt-inventory.md)；
阶段与门禁的定义由 `project-lifecycle-governance` 裁定，本文件只描述内容归属。

维护者：SnowCore8。阅读时机：新增 skill、调整生命周期映射、移动 references 或判断一条事实应放在哪里时。

## 1. 内容层级

| 层 | 内容 | 载体 | 类别 |
|---|---|---|---|
| 常驻约束（规则层） | 生命周期与门禁判定、授权、不可逆、诚实、意图、方法与交付 | `rules/global-user-constraints.md` | P |
| 生命周期层 | 阶段活动、门禁判据、风险分级、敏捷迭代、角色、工件、度量与组合 | `skills/project-lifecycle-governance/` | P |
| skill 入口 | 触发、适用边界、生命周期定位、门禁与证据、核心规则、审查清单 | `skills/*/SKILL.md`（21 个） | P |
| skill 细节 | 阶段契约、维度表、检查表、模板、操作手册、语言覆盖 | `skills/*/references/*.md` | P |
| 命令 | 手动审查当前请求、方案或命令 | `shared/commands/constraints-check.md` | P |
| 项目文档 | 加载规则、hook 与注入、发布、时间、校验规则、台账 | `docs/*.md` 与根文档 | R |
| 分发元数据 | 清单、hooks、许可证、第三方声明 | `plugins/`、`package.json`、根文件 | M/C |

层级之间只有一个方向：规则层约束生命周期层，生命周期层决定何时调用专业 skill，专业 skill 提供该阶段的
规则与证据。任何一层都不得复制另一层的正文。

## 2. 生命周期主线

S0–S6 的编号、门禁判据与风险分级以 `rules/global-user-constraints.md` 第 2 节和
`project-lifecycle-governance/references/gates.md` 为准；各 skill 在其主责阶段提供规则与证据。

| 阶段 | 主责 skill | 支持 skill | 出口门 |
|---|---|---|---|
| S0 受理 | `project-lifecycle-governance`、`security-compliance-conventions`、`repository-governance-conventions` | `documentation-conventions`、`vcs-collaboration-conventions` | G0 |
| S1 探索 | `project-lifecycle-governance`、`architecture-and-design-conventions`、`security-compliance-conventions` | `documentation-conventions`、`performance-conventions`、`prompt-authoring`、`system-prompt-authoring`、`skill-authoring` | G1 |
| S2 计划 | `project-lifecycle-governance`、`architecture-and-design-conventions`、`project-structure-conventions`、`api-and-data-conventions`、`testing-and-quality-conventions`、`release-operations-conventions` | `code-style-conventions`、`naming-conventions`、`concurrency-conventions`、`performance-conventions`、`security-compliance-conventions`、`vcs-collaboration-conventions`、`worktree-collaboration-conventions`、`documentation-conventions`、`repository-governance-conventions`、编写类 skill | G2 |
| S3 构建 | `code-style-conventions`、`naming-conventions`、`comment-conventions`、`refactoring-conventions`、`api-and-data-conventions`、`project-structure-conventions`、`architecture-and-design-conventions`、`testing-and-quality-conventions` | `concurrency-conventions`、`performance-conventions`、`debugging-conventions`、`vcs-collaboration-conventions`、`worktree-collaboration-conventions`、`documentation-conventions`、编写类 skill | G3 |
| S4 验证 | `testing-and-quality-conventions`、`security-compliance-conventions`、`release-operations-conventions`、`project-lifecycle-governance` | `performance-conventions`、`concurrency-conventions`、`debugging-conventions`、`architecture-and-design-conventions`、`api-and-data-conventions`、`documentation-conventions`、`vcs-collaboration-conventions`、`repository-governance-conventions`、编写类 skill | G4 |
| S5 发布 | `release-operations-conventions`、`repository-governance-conventions`、`security-compliance-conventions`、`project-lifecycle-governance` | `documentation-conventions`、`vcs-collaboration-conventions` | G5 |
| S6 收尾 | `project-lifecycle-governance`、`release-operations-conventions`、`documentation-conventions`、`repository-governance-conventions` | `debugging-conventions`、`performance-conventions`、`security-compliance-conventions`、`worktree-collaboration-conventions` | G6 |

“编写类 skill”指 `prompt-authoring`、`system-prompt-authoring` 与 `skill-authoring`，它们在本仓库的 S1/S2/S4
承担提示词与 skill 包的设计与验证。完整的 skill 与阶段映射见
`project-lifecycle-governance/references/mappings.md`。

## 3. 21 个 skill 的主责

主责阶段取各 `SKILL.md` 的「生命周期定位」节；references 列按文件名去扩展名。

### 3.1 生命周期治理

| skill | 主责阶段 | 门禁 | 主责内容 | references |
|---|---|---|---|---|
| `project-lifecycle-governance` | S0–S6 | G0–G6 | 阶段与门禁、风险分级与裁剪、敏捷迭代、角色、工件、度量、组合与依赖 | lifecycle、stages、gates、agile、roles、metrics、portfolio、mappings、templates |

### 3.2 编写与文档

| skill | 主责阶段 | 门禁 | 主责内容 | references |
|---|---|---|---|---|
| `skill-authoring` | S1/S2/S4 | G1/G2/G4 | skill 包结构、frontmatter、触发质量、渐进披露、references 组织 | lifecycle、templates、skill-load-order |
| `prompt-authoring` | S1/S2/S4 | G1/G2/G4 | 运行时与产品提示词、输出契约、评测与回归 | lifecycle、evaluation、output-contract、templates |
| `system-prompt-authoring` | S1/S2/S4 | G1/G2/G4 | 常驻指令文件的内容规则（S1–S13）与格式校验 | lifecycle、complex-logic、templates |
| `documentation-conventions` | S1–S6 | G1/G4/G5/G6 | README、贡献指南、ADR、教程、操作指南、运行手册、变更记录、文档站 | lifecycle、dimensions-project、dimensions-usage、dimensions-delivery、templates-project、templates-usage、templates-delivery、change-records |

### 3.3 设计与代码

| skill | 主责阶段 | 门禁 | 主责内容 | references |
|---|---|---|---|---|
| `architecture-and-design-conventions` | S1–S4 | G1/G2/G3/G4 | 模块与组件边界、分层、依赖方向、数据流、接缝、框架选择与 ADR | lifecycle、dimensions、checklists、framework-changes |
| `project-structure-conventions` | S2–S4 | G2/G3/G4 | 项目目录、包与工作区边界、物理导入与构建图、包公开入口、生成与第三方目录 | lifecycle |
| `api-and-data-conventions` | S2–S5 | G2/G3/G4/G5 | API 契约、错误与分页、幂等、授权边界、schema 迁移与保留 | lifecycle、dimensions、checklists |
| `code-style-conventions` | S2–S4 | G2/G3/G4 | 格式、模块内部文件与资源布局、依赖版本管理、配置、错误与日志 | lifecycle、dimensions、dimensions-errors、languages |
| `naming-conventions` | S2–S5 | G2/G3/G4/G5 | 文件、代码、接口、数据、配置、提交、分支、标签与资产命名 | lifecycle、dimensions-code、dimensions-interface、dimensions-system、languages |
| `comment-conventions` | S2–S5 | G2/G3/G4/G5 | 源码注释、文档注释、声明头、弃用与工具指令 | lifecycle、dimensions-inline、dimensions-api、dimensions-policy、languages |
| `refactoring-conventions` | S2–S5 | G2/G3/G4/G5 | 重构与修复判定、安全手法、代码异味、变更拆分 | lifecycle、dimensions、catalog、change-safety |

### 3.4 运行正确性

| skill | 主责阶段 | 门禁 | 主责内容 | references |
|---|---|---|---|---|
| `concurrency-conventions` | S2–S4/S6 | G2/G3/G4/G6 | 共享状态、同步原语、死锁与活锁、异步模型、并发测试 | lifecycle、dimensions、checklist |
| `performance-conventions` | S1–S6 | G1/G2/G4/G6 | 测量、目标与预算、瓶颈、缓存与索引取舍、优化纪律 | lifecycle、dimensions、checklists |
| `debugging-conventions` | S0/S2–S6 | G0/G3/G4/G6 | 缺陷报告、复现、二分、根因、最小修复验证 | lifecycle、dimensions、report-template、root-cause-discipline |
| `testing-and-quality-conventions` | S0–S5 | G1/G2/G3/G4/G5 | 测试层级、质量门禁、静态分析、本地/CI 对齐 | lifecycle、dimensions、gates、project-commands |

### 3.5 交付与治理

| skill | 主责阶段 | 门禁 | 主责内容 | references |
|---|---|---|---|---|
| `repository-governance-conventions` | S0–S2/S5/S6 | G0/G1/G2/G5/G6 | 必需文件、仓库卫生、打包实践、角色与审批路由 | lifecycle、dimensions、playbooks |
| `release-operations-conventions` | S2/S5/S6 | G2/G5/G6 | 版本、发布、CI/CD、可观测性、事故、备份恢复 | lifecycle、dimensions、playbooks |
| `vcs-collaboration-conventions` | S2–S5 | G2/G3/G4/G5 | Git 工作流、分支、PR/MR、审查、保护与所有权 | lifecycle、dimensions、playbooks |
| `worktree-collaboration-conventions` | S2/S3/S6 | G2/G3/G6 | 领导者智能体统一管理的工作树分配、隔离、集成、恢复与清理 | lifecycle、dimensions、playbooks |
| `security-compliance-conventions` | S0–S6 | G0/G2/G4/G5 | 威胁、凭据、供应链、SBOM、许可证、PII、披露 | lifecycle、dimensions、checklists |

## 4. 统一内部结构

每个 `SKILL.md` 以 `## 适用范围与优先级` 开始、以 `## 参考资料` 结束；正文不超过 250 行。通用段依次为：

- 适用范围与优先级：管辖什么、不管辖什么、冲突时的效力顺序。
- 生命周期定位：阶段职责表、上游输入、下游交接、升级与停止。
- 门禁与证据：各门禁需要提供的证据，以及证据不足时的处理。
- 工作流：从受理到交付的步骤与判定。
- 核心规则：该 skill 的强制性要求与例外。
- 领域矩阵：判定用的决策表、风险矩阵或类型矩阵。
- 维度索引：维度编号、首条规则与 references 的节号映射；有 `dimensions*.md` 时必须存在。
- 反模式、审查清单、示例。
- 参考资料：references 的相对链接与用途。

领域差异只允许增加判定表、矩阵或专门小节（如 `skill-authoring` 的触发质量、`system-prompt-authoring` 的
S1–S13、`prompt-authoring` 的输出契约、`documentation-conventions` 的事实归属、`naming-conventions` 的命名表）；
不得改变首尾段，也不得复制其他 skill 的正文。

## 5. references 类型

| 类型 | 用途 | 例子 |
|---|---|---|
| `lifecycle.md` | 该 skill 的阶段契约：S0–S6 的输入、活动、输出与门禁，证据形态、交接、升级、裁剪与度量 | 21 个 skill 中的阶段契约文件 |
| `dimensions*.md` | 规则分维度展开，SKILL 的维度索引按节号引用 | api、naming、testing |
| `checklists.md`、`checklist.md` | 审查与排查工作表 | api、performance、security、concurrency |
| `templates*.md` | 可直接套用的文件骨架与门禁记录模板 | documentation、system-prompt、skill、lifecycle |
| `playbooks.md` | 按场景组织的操作步骤 | repository、release、vcs、worktree |
| `languages.md` | 语言特定覆盖 | code-style、comment、naming |
| 单篇专题 | 框架迁移、根因、变更记录、项目命令、阶段细节 | architecture/framework-changes、debugging/root-cause-discipline |

references 内只写该 skill 的规则与证据，不复述阶段与门禁定义；阶段契约引用
`project-lifecycle-governance` 的编号，不重新定义。

## 6. 边界裁定

| 重叠对 | 归属 |
|---|---|
| `prompt-authoring` / `system-prompt-authoring` / `skill-authoring` / `documentation-conventions` | 运行时提示词 / 常驻指令文件 / skill 包 / 项目文档 |
| `architecture` / `api-and-data` / `performance` | 模块边界 / 契约与数据 / 性能调优（索引调优归 performance） |
| `architecture` / `project-structure` / `code-style` | 逻辑边界与依赖方向 / 项目目录、包与工作区、物理导入与构建图 / 模块内部布局、格式与依赖版本 |
| `code-style` / `naming` / `comment` / `security` | 格式与配置 / 名称 / 源码注释 / 依赖漏洞与许可证 |
| `testing` / `release-operations` / `vcs` | 测试与门禁 / 发布回滚 / 分支与 PR |
| `vcs` / `worktree-collaboration` | 分支模型、PR 与合并策略 / 工作树分配、隔离与集成生命周期 |
| `repository-governance` / `release-operations` / `vcs` / `security` | 必需文件与打包 / 发布运维 / 协作 / 安全合规 |
| `refactoring` / `architecture` / `code-style` | 安全改造手法 / 目标结构 / 表面风格 |
| `concurrency` / `performance` / `api-and-data` | 正确性 / 调优 / 幂等与重试 |
| `project-lifecycle-governance` / `testing-and-quality` / `release-operations` | 阶段、门禁判定与风险分级 / 测试策略与门禁实现 / 发布与回滚操作 |
| 角色与决策权 | `project-lifecycle-governance` 的 `roles.md` 裁定；本仓库的具体承担者见根目录 `GOVERNANCE.md` |
| 工件内容与格式 | 类型与必需章节由 `project-lifecycle-governance` 的 `templates.md` 裁定，写作格式归 `documentation-conventions` |
| 度量口径 | 生命周期度量由 `project-lifecycle-governance` 的 `metrics.md` 裁定；性能指标归 `performance-conventions`，测试与门禁阈值归 `testing-and-quality-conventions` |
| 组合与依赖 | `project-lifecycle-governance` 的 `portfolio.md` 裁定排序、容量与退出；跨团队依赖的技术接口归 `api-and-data-conventions` |
| 例外登记 | 门禁例外的字段与限制由 `project-lifecycle-governance` 裁定；本仓库的登记与复核流程见根目录 `GOVERNANCE.md` |

## 7. 例外与检查

- 专题 references 只陈述当前规则；来源、日期与新旧对照不进入内容层。
- `docs/markdown-check-rules.md` 是脚本规则表（R），不属于 skill 内容。
- 内容结构由 `tests/skill/test_skills_meta.py` 检查首尾段、250 行上限、维度索引与逐字重复；
  `tests/skill/test_lifecycle_contract.py` 检查生命周期定位、门禁证据与 `lifecycle.md`；全量门禁见
  `scripts/check.sh`。
- 新增或改名 skill 时同步本节的主责表、`project-lifecycle-governance/references/mappings.md` 与
  [prompt-inventory.md](prompt-inventory.md)。
