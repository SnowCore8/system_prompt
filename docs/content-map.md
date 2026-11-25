# 内容结构地图

维护者：SnowCore8。何时阅读：新增 skill、调整 domains、移动 references 或判断一条事实应放在哪里时。
本文件描述内容层级、领域划分、18 个 skill 的职责与 references 结构；目录与分发结构见 `README.md`，提示词/纯规则分类见 `docs/prompt-inventory.md`。

## 1. 内容层级

| 层 | 内容 | 载体 | 类别 |
|---|---|---|---|
| 常驻约束 | 授权、不可逆、诚实、意图、方法、交付与验收 | `rules/global-user-constraints.md` | P |
| skill 入口 | 触发、适用边界、流程、核心规则、审查清单 | `skills/*/SKILL.md`（18 个） | P |
| skill 细节 | 维度表、检查表、模板、操作手册、语言覆盖 | `skills/*/references/*.md`（51 个） | P |
| 命令 | 手动审查当前请求/方案/命令 | `shared/commands/constraints-check.md` | P |
| 项目文档 | 加载调研、发布、时间、校验规则、台账 | `docs/*.md` 与根文档 | R |
| 分发元数据 | 清单、hooks、许可证、第三方声明 | `plugins/`、`package.json`、根文件 | M/C |

## 2. 四个内容域

| 域 | skill | 负责 | 不负责 |
|---|---|---|---|
| 编写与文档 | `skill-authoring`、`prompt-authoring`、`system-prompt-authoring`、`documentation-conventions` | skill 包、运行时提示词、常驻指令文件、项目文档 | 具体业务契约、代码风格、代码注释 |
| 设计与代码 | `architecture-and-design-conventions`、`api-and-data-conventions`、`code-style-conventions`、`comment-conventions`、`naming-conventions`、`refactoring-conventions` | 模块边界、接口/数据、风格、注释、名称、安全重构 | 运行时正确性、测试策略、交付流程 |
| 运行正确性 | `concurrency-conventions`、`performance-conventions`、`debugging-conventions`、`testing-and-quality-conventions` | 并发、性能、缺陷诊断、测试与门禁 | 发布/回滚、仓库治理、安全披露 |
| 交付与治理 | `repository-governance-conventions`、`release-operations-conventions`、`vcs-collaboration-conventions`、`security-compliance-conventions` | 仓库卫生与打包、发布运维、Git 协作、安全合规 | 代码细节、具体门禁阈值、产品契约 |

## 3. 18 个 skill 的主责

### 3.1 编写与文档

| skill | 主责 | references |
|---|---|---|
| `skill-authoring` | skill 包结构、frontmatter、触发质量、渐进披露、references 组织 | templates、skill-load-order（2） |
| `prompt-authoring` | 运行时与产品提示词、输出契约、评测与回归 | evaluation、output-contract、templates（3） |
| `system-prompt-authoring` | `AGENTS.md`/`CLAUDE.md`/`QWEN.md` 的常驻指令内容与校验 | complex-logic、templates（2） |
| `documentation-conventions` | README、贡献指南、ADR、教程、运行手册、变更记录、文档站 | 3 组 dimensions + 3 组 templates + change-records（7） |

### 3.2 设计与代码

| skill | 主责 | references |
|---|---|---|
| `architecture-and-design-conventions` | 模块/组件边界、分层、依赖方向、数据流、ADR | dimensions、checklists、framework-changes（3） |
| `api-and-data-conventions` | API 契约、错误/分页/幂等/授权、schema 迁移与保留 | dimensions、checklists（2） |
| `code-style-conventions` | 格式、目录布局、依赖、配置、错误与日志 | dimensions、dimensions-errors、languages（3） |
| `comment-conventions` | 源码注释、文档注释、声明头、弃用与工具指令 | 3 组 dimensions + languages（4） |
| `naming-conventions` | 文件/代码/接口/数据/配置/提交消息的命名 | 3 组 dimensions + languages（4） |
| `refactoring-conventions` | 重构/修复判定、安全手法、代码异味、变更拆分 | dimensions、catalog、change-safety（3） |

### 3.3 运行正确性

| skill | 主责 | references |
|---|---|---|
| `concurrency-conventions` | 共享状态、同步原语、死锁/活锁、异步模型、并发测试 | dimensions、checklist（2） |
| `performance-conventions` | 测量、目标与预算、瓶颈、缓存/索引取舍、优化纪律 | dimensions、checklists（2） |
| `debugging-conventions` | 缺陷报告、复现、二分、根因、最小修复验证 | dimensions、report-template、root-cause-discipline（3） |
| `testing-and-quality-conventions` | 测试层级、门禁、静态分析、本地/CI 对齐 | dimensions、gates、project-commands（3） |

### 3.4 交付与治理

| skill | 主责 | references |
|---|---|---|
| `repository-governance-conventions` | 必需文件、仓库卫生、打包实践、角色与审批路由 | dimensions、playbooks（2） |
| `release-operations-conventions` | 版本、发布、CI/CD、可观测性、事故、备份恢复 | dimensions、playbooks（2） |
| `vcs-collaboration-conventions` | Git 工作流、分支、PR/MR、审查、保护与所有权 | dimensions、playbooks（2） |
| `security-compliance-conventions` | 威胁、凭据、供应链、SBOM、许可证、PII、披露 | dimensions、checklists（2） |

## 4. 统一内部结构

每个 `SKILL.md` 以 `## 适用范围与优先级` 开始、以 `## 参考资料` 结束；正文不超过 250 行。通用段为：

- 适用范围与优先级
- 流程
- 核心规则
- 领域矩阵或维度索引
- 反模式
- 审查清单
- 示例
- 参考资料

领域差异仅允许增加判定表、矩阵或专门小节（如 `skill-authoring` 的触发质量、`system-prompt-authoring` 的 S1-S13、
`prompt-authoring` 的输出契约、`documentation-conventions` 的事实归属、`naming-conventions` 的命名表）；不得改变首尾段。

## 5. references 类型

| 类型 | 用途 | 例子 |
|---|---|---|
| `dimensions*.md` | 规则分维度展开，SKILL 的维度索引按节号引用 | api、naming、testing |
| `checklists.md` | 审查与排查工作表 | api、performance、security |
| `templates*.md` | 可直接套用的文件骨架 | documentation、system-prompt、skill |
| `playbooks.md` | 按场景组织的操作步骤 | repository、release、vcs |
| `languages.md` | 语言特定覆盖 | code-style、comment、naming |
| 单篇专题 | 迁移条款、根因、变更记录、项目命令 | architecture/framework-changes 等 |

## 6. 边界裁定

| 重叠对 | 归属 |
|---|---|
| `prompt-authoring` / `system-prompt-authoring` / `skill-authoring` / `documentation-conventions` | 运行时提示词 / 常驻指令文件 / skill 包 / 项目文档 |
| `architecture` / `api-and-data` / `performance` | 模块边界 / 契约与数据 / 性能调优（索引调优归 performance） |
| `code-style` / `naming` / `comment` / `security` | 格式与配置 / 名称 / 源码注释 / 依赖漏洞与许可证 |
| `testing` / `release-operations` / `vcs` | 测试与门禁 / 发布回滚 / 分支与 PR |
| `repository-governance` / `release-operations` / `vcs` / `security` | 必需文件与打包 / 发布运维 / 协作 / 安全合规 |
| `refactoring` / `architecture` / `code-style` | 安全改造手法 / 目标结构 / 表面风格 |
| `concurrency` / `performance` / `api-and-data` | 正确性 / 调优 / 幂等与重试 |

## 7. 例外与检查

- 专题 references 只陈述当前规则。
- `docs/markdown-check-rules.md` 是脚本规则表（R），不属于 skill 内容。
- 内容结构由 `tests/skill/test_skills_meta.py` 检查首尾段、250 行上限、维度索引与重复段落；全量门禁见 `scripts/check.sh`。
