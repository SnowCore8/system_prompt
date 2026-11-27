# 阶段与 skill 映射

本文件把 24 个 skill 放进同一条生命周期。主责阶段表示该 skill 最常被调用的位置；支持阶段表示它仍需在
门禁前提供证据。门禁编号与 `SKILL.md`、`stages.md` 一致。

## 1. skill 归属

| skill | 主责阶段 | 门禁 | 生命周期职责与证据 |
|---|---|---|---|
| `project-lifecycle` | S0–S7 | G0–G7 | 维护阶段、门禁、风险分级、角色、工件与度量；产出受理记录、门禁记录、收尾报告 |
| `requirements-engineering` | S0/S1 | G0/G1 | 需求澄清、结果指标、选项与收益基线；需求说明与 G1 证据 |
| `planning-estimation` | S1/S2 | G1/G2 | 任务拆分、估算、里程碑与关键路径；计划与承诺证据 |
| `architecture-design` | S2/S4 | G2/G4 | 模块边界、依赖方向、框架选择、ADR；设计评审结论 |
| `project-structure` | S0/S1/S2/S5/S7 | G0/G1/G2/G5/G7 | 目录、包与工作区边界、仓库归档；结构与打包证据 |
| `api-data` | S2/S3/S4 | G2/G3/G4 | API 契约、schema 迁移、幂等与保留；兼容性与迁移证据 |
| `implementation-practices` | S2/S3 | G2/G3 | 实现与工程实践、库选择与复用；增量证据 |
| `code-style` | S2/S3 | G2/G3 | 格式化、依赖锁定、配置、错误与日志；工具配置与审查基线 |
| `naming` | S2/S3 | G2/G3 | 文件、代码、接口、数据与提交名称；一致性与变更影响 |
| `comments` | S3/S4 | G3/G4 | 行内注释、文档注释、法律头与工具指令；当前事实与审查结论 |
| `refactoring` | S3/S4 | G3/G4 | 重构与修复判定、安全手法、小步提交；行为保持说明 |
| `concurrency` | S2/S3/S4 | G2/G3/G4 | 共享状态、同步原语、异步模型、并发测试；竞态与压测证据 |
| `debugging` | S3/S4/S6 | G3/G4/G6 | 缺陷报告、复现、根因、最小修复与回归；事故根因证据 |
| `testing-quality` | S2/S3/S4 | G2/G3/G4 | 测试层级、质量门禁、静态分析、CI 对齐；测试策略与 DoD 证据 |
| `code-review` | S3/S4 | G3/G4 | 审查深度、意见处理与返工；审查结论与批准记录 |
| `security-compliance` | S0–S7 | G0/G1/G2/G4/G5 | 威胁模型、机密与权限、依赖与供应链、许可证、披露；安全结论与例外记录 |
| `performance` | S1/S2/S4/S6 | G1/G2/G4/G6 | 性能目标、预算、基准与剖析；优化前后数据与回归阈值 |
| `documentation` | S1–S7 | G1/G4/G5/G6/G7 | 需求与设计文档、运行手册、变更记录、收尾报告；一致性与事实证据 |
| `release-operations` | S2/S5/S6 | G2/G5/G6 | 版本、变更管理、CI/CD、可观测性、事故响应、备份恢复；发布与运维证据 |
| `vcs-collaboration` | S2–S5 | G2/G3/G4/G5 | 分支模型、PR/MR、审查、保护规则、工作树协作；审查与合并记录 |
| `maintenance-retirement` | S6/S7 | G6/G7 | 运维手册、退役与归档、交接与清理；退役证据 |
| `prompt-engineering` | S1/S2/S4 | G1/G2/G4 | 运行时提示词、输出契约、评测与回归；评测集与退化结论 |
| `system-prompt-engineering` | S1/S2/S4 | G1/G2/G4 | 常驻指令文件、最小性与校验；校验输出与结构结论 |
| `mcp-engineering` | S1/S2/S4 | G1/G2/G4 | MCP 服务器与工具、授权范围与验证；连接与安全证据 |

## 2. 阶段覆盖

| 阶段 | 主责 skill |
|---|---|
| S0 受理 | `project-lifecycle`、`requirements-engineering`、`security-compliance`、`project-structure` |
| S1 需求 | `project-lifecycle`、`requirements-engineering`、`planning-estimation`、`security-compliance` |
| S2 设计 | `architecture-design`、`planning-estimation`、`project-structure`、`api-data`、`testing-quality`、`release-operations`、`vcs-collaboration` |
| S3 构建 | `implementation-practices`、`code-style`、`naming`、`comments`、`refactoring`、`api-data`、`testing-quality` |
| S4 验证 | `testing-quality`、`code-review`、`security-compliance`、`performance`、`documentation`、`project-lifecycle` |
| S5 发布 | `release-operations`、`vcs-collaboration`、`project-structure`、`project-lifecycle` |
| S6 运维 | `release-operations`、`maintenance-retirement`、`security-compliance`、`performance`、`debugging`、`documentation` |
| S7 收尾 | `maintenance-retirement`、`project-lifecycle`、`release-operations`、`vcs-collaboration` |

支持阶段与证据重点见第 1 节的归属表；支持 skill 在主责阶段之外的证据责任，由各 skill 的
`references/lifecycle.md` 声明。

## 3. 工件归属

| 工件 | 主责 skill | 共同输入 |
|---|---|---|
| 受理记录 | `project-lifecycle` | `requirements-engineering`、`security-compliance` |
| 需求说明 | `requirements-engineering` | `project-lifecycle`、`security-compliance`、`documentation` |
| 计划与待办 | `planning-estimation` | `architecture-design`、`project-structure`、`testing-quality`、`release-operations` |
| 架构与 ADR | `architecture-design` | `api-data`、`project-structure`、`security-compliance` |
| 增量 | 交付团队 | `implementation-practices`、`code-style`、`naming`、`comments`、`refactoring`、`concurrency`、`performance` |
| 验证证据包 | `testing-quality` | `code-review`、`security-compliance`、`performance`、`debugging`、`documentation` |
| 发布记录 | `release-operations` | `project-structure`、`security-compliance`、`documentation`、`vcs-collaboration` |
| 运维手册与事故复盘 | `release-operations` | `maintenance-retirement`、`security-compliance`、`debugging` |
| 收尾报告 | `project-lifecycle` | `maintenance-retirement`、`documentation`、`release-operations` |

## 4. 使用方式

- 在 G0 先调用 `project-lifecycle` 确定阶段、风险级别与所需证据，再按上表加载对应 skill。
- 一个阶段可以调用多个 skill；以主责 skill 的结论为主，支持 skill 提供证据或约束。
- 跨阶段 skill 在每次门禁前检查其证据是否仍然有效；过时证据不得复用。
- skill 之间的边界争议按各 skill 的「适用范围与优先级」处理；生命周期归属争议由本 skill 裁定。
- 新增或改名 skill 时，同步更新本表与 `rules/global-user-constraints.md` 的 skill 索引。
