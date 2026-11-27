# 阶段与 skill 映射

本文件把 21 个 skill 放进同一条生命周期。主责阶段表示该 skill 最常被调用的位置；支持阶段表示它仍需
在门禁前提供证据。门禁编号与 `SKILL.md`、`stages.md` 一致。

## skill 归属

| skill | 主责阶段 | 门禁 | 生命周期职责与证据 |
|---|---|---|---|
| `project-lifecycle-governance` | S0–S6 | G0–G6 | 维护阶段、门禁、风险分级、角色、工件与度量；产出受理记录、门禁记录、收尾报告 |
| `security-compliance-conventions` | S0–S6 | G0/G2/G4/G5 | 威胁模型、机密与权限、依赖与供应链、SBOM、许可证、PII、披露路径；安全结论与例外记录 |
| `repository-governance-conventions` | S0/S1/S2/S5/S6 | G0/G1/G2/G5/G6 | 仓库类型、必需文件、角色与审批路由、打包与分发、归档与转移；清单与安装证据 |
| `documentation-conventions` | S1–S6 | G1/G4/G5/G6 | 问题与设计文档、指南、运行手册、变更记录、发布说明、收尾报告；可读性与事实一致性 |
| `architecture-and-design-conventions` | S1/S2/S4 | G1/G2/G4 | 模块边界、依赖方向、数据流、框架选择、ADR；设计评审与循环依赖结论 |
| `project-structure-conventions` | S2/S3 | G2/G3 | 目录、包与工作区边界、导入与构建图、公开入口、生成与第三方目录；结构门禁 |
| `api-and-data-conventions` | S2/S3/S4 | G2/G3/G4 | API 契约、错误与分页、幂等、授权边界、schema 迁移与保留；兼容性与迁移/回滚方案 |
| `code-style-conventions` | S2/S3 | G2/G3 | 格式化、模块内布局、依赖版本、配置、错误与日志；工具配置与审查基线 |
| `naming-conventions` | S2/S3 | G2/G3 | 文件、代码、接口、数据、配置、提交、分支、标签等名称；一致性与迁移影响 |
| `comment-conventions` | S3/S4 | G3/G4 | 行内注释、文档注释、文件头、弃用、法律头与工具指令；当前事实与审查结论 |
| `refactoring-conventions` | S3/S4 | G3/G4 | 重构与修复判定、安全手法、小步提交、代码异味；行为保持说明与回滚点 |
| `concurrency-conventions` | S2/S3/S4 | G2/G3/G4 | 共享状态、同步原语、死锁与活锁、异步模型、并发测试；竞态与压测证据 |
| `performance-conventions` | S1/S2/S4/S6 | G1/G2/G4/G6 | 性能目标、预算、基准、剖析、缓存与索引取舍；优化前后数据与回归阈值 |
| `debugging-conventions` | S3/S4/S6 | G3/G4/G6 | 缺陷报告、复现、二分、根因、最小修复与回归；事故根因与修复验证 |
| `testing-and-quality-conventions` | S2/S3/S4 | G2/G3/G4 | 测试层级、质量门禁、静态分析、本地/CI 对齐；测试策略、覆盖与 DoD 证据 |
| `release-operations-conventions` | S2/S5/S6 | G2/G5/G6 | 版本、变更管理、CI/CD、可观测性、事故响应、备份恢复；发布与回滚证据 |
| `vcs-collaboration-conventions` | S2/S3/S4/S5 | G2/G3/G4/G5 | 分支模型、PR/MR、审查深度、保护规则、CODEOWNERS；审查与合并记录 |
| `worktree-collaboration-conventions` | S2/S3/S6 | G2/G3/G6 | 工作树分配、单写者、基线、依赖、集成、恢复与清理；隔离与集成记录 |
| `prompt-authoring` | S1/S2/S4 | G1/G2/G4 | 运行时提示词、输出契约、示例、评测与回归；评测集与退化结论 |
| `system-prompt-authoring` | S1/S2/S4 | G1/G2/G4 | AGENTS/CLAUDE/QWEN 常驻指令、S1–S13、格式校验；最小性与校验输出 |
| `skill-authoring` | S1/S2/S4 | G1/G2/G4 | skill 包结构、触发、渐进披露、references 组织；触发测试与结构审查 |

## 阶段覆盖

| 阶段 | 主责 skill | 支持 skill |
|---|---|---|
| S0 受理 | `project-lifecycle-governance`、`security-compliance-conventions`、`repository-governance-conventions` | `documentation-conventions`、`vcs-collaboration-conventions` |
| S1 探索 | `project-lifecycle-governance`、`architecture-and-design-conventions`、`security-compliance-conventions` | `documentation-conventions`、`performance-conventions`、`prompt-authoring`、`system-prompt-authoring`、`skill-authoring` |
| S2 计划 | `project-lifecycle-governance`、`architecture-and-design-conventions`、`project-structure-conventions`、`api-and-data-conventions`、`testing-and-quality-conventions`、`release-operations-conventions` | `code-style-conventions`、`naming-conventions`、`concurrency-conventions`、`performance-conventions`、`security-compliance-conventions`、`vcs-collaboration-conventions`、`worktree-collaboration-conventions`、`documentation-conventions`、`prompt-authoring`、`system-prompt-authoring`、`skill-authoring`、`repository-governance-conventions` |
| S3 构建 | `code-style-conventions`、`naming-conventions`、`comment-conventions`、`refactoring-conventions`、`api-and-data-conventions`、`project-structure-conventions`、`architecture-and-design-conventions`、`testing-and-quality-conventions` | `concurrency-conventions`、`performance-conventions`、`debugging-conventions`、`vcs-collaboration-conventions`、`worktree-collaboration-conventions`、`documentation-conventions`、`prompt-authoring`、`system-prompt-authoring`、`skill-authoring` |
| S4 验证 | `testing-and-quality-conventions`、`security-compliance-conventions`、`release-operations-conventions`、`project-lifecycle-governance` | `performance-conventions`、`concurrency-conventions`、`debugging-conventions`、`architecture-and-design-conventions`、`api-and-data-conventions`、`documentation-conventions`、`vcs-collaboration-conventions`、`repository-governance-conventions`、`prompt-authoring`、`system-prompt-authoring`、`skill-authoring` |
| S5 发布 | `release-operations-conventions`、`repository-governance-conventions`、`security-compliance-conventions`、`project-lifecycle-governance` | `documentation-conventions`、`vcs-collaboration-conventions` |
| S6 收尾 | `project-lifecycle-governance`、`release-operations-conventions`、`documentation-conventions`、`repository-governance-conventions` | `debugging-conventions`、`performance-conventions`、`security-compliance-conventions`、`worktree-collaboration-conventions` |

## 工件归属

| 工件 | 主责 skill | 共同输入 |
|---|---|---|
| 受理记录 | `project-lifecycle-governance` | 安全、仓库治理 |
| 章程 / 探索简报 | `project-lifecycle-governance` | 架构、安全、文档、性能 |
| 计划 / 待办 | `project-lifecycle-governance` | 架构、结构、接口、测试、发布、版本控制 |
| 设计与 ADR | `architecture-and-design-conventions` | 接口、数据、结构、安全 |
| 增量 | 交付团队 | 代码风格、命名、注释、重构、并发、性能 |
| 验证证据 | `testing-and-quality-conventions` | 安全、性能、并发、调试、文档 |
| 发布记录 | `release-operations-conventions` | 仓库治理、安全、文档、版本控制 |
| 收尾报告 | `project-lifecycle-governance` | 文档、运营、安全、仓库治理 |

## 使用方式

- 在 G0 先调用 `project-lifecycle-governance` 确定阶段、风险级别与所需证据，再按上表加载对应 skill。
- 一个阶段可以调用多个 skill；以主责 skill 的结论为主，支持 skill 提供证据或约束。
- 跨阶段 skill 在每次门禁前检查其证据是否仍然有效；过时证据不得复用。
- skill 之间的边界争议按各 skill 的「适用范围与优先级」处理；生命周期归属争议由本 skill 裁定。
- 新增 skill 时，应同时更新本表、`docs/content-map.md` 与 `rules/global-user-constraints.md` 的 skill 索引。
