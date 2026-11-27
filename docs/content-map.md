# 内容地图

本文件记录套件的内容层级与 24 个 skill 的主责。唯一真源见 [AGENTS.md](../AGENTS.md)。

## 内容层级

| 层 | 内容 | 载体 |
|---|---|---|
| 章程 | 8 阶段与 8 门禁的不可跳过判定、十大规则域 | `rules/global-user-constraints.md` |
| 生命周期层 | 阶段活动、门禁判据、风险分级、角色、工件、度量、组合 | `skills/project-lifecycle/` |
| 专业 skill 层 | 各阶段的规则、维度与检查表 | 其余 23 个 skill |
| MCP | 章程条款审查与生命周期模板工具 | `mcp/` |

## 24 个 skill 的主责

| skill | 主责阶段 | 门禁 | 主责内容 |
|---|---|---|---|
| `project-lifecycle` | S0–S7 | G0–G7 | 阶段与门禁、风险分级与裁剪、角色、工件、度量、组合 |
| `requirements-engineering` | S0/S1 | G0/G1 | 受理、需求收集与分析、验收标准、DoR、收益基线 |
| `architecture-design` | S2–S4 | G2/G3/G4 | 边界、分层、依赖方向、框架选择、ADR |
| `planning-estimation` | S2 | G2 | 任务拆分、估算、关键路径、风险与依赖登记 |
| `implementation-practices` | S3 | G3 | 小步提交、增量可运行、WIP、调试纪律、DoD |
| `testing-quality` | S2–S5 | G2/G3/G4/G5 | 测试层级、质量门禁、覆盖率、静态分析、本地/CI 对齐 |
| `release-operations` | S5/S6 | G5/G6 | 版本、CI/CD、发布与回滚、监控告警、事故、备份恢复 |
| `maintenance-retirement` | S6/S7 | G6/G7 | 补丁、技术债、退役归档、交接、复盘 |
| `code-style` | S2–S4 | G2/G3/G4 | 格式、模块内布局、依赖版本、配置、错误与日志 |
| `naming` | S2–S5 | G2/G3/G4/G5 | 文件、代码、接口、数据、配置、提交、分支、标签命名 |
| `comments` | S2–S5 | G2/G3/G4/G5 | 行内注释、文档注释、标记、弃用、工具指令 |
| `refactoring` | S2–S5 | G2/G3/G4/G5 | 重构与修复判定、安全手法、小步提交、异味处理 |
| `code-review` | S2–S5 | G2/G3/G4/G5 | 审查深度、清单、作者与审查者职责、审查门禁 |
| `concurrency` | S2–S4/S6 | G2/G3/G4/G6 | 共享状态、同步原语、死锁、异步模型、并发测试 |
| `performance` | S1–S7 | G1/G2/G4/G6 | 测量、目标与预算、瓶颈、缓存索引取舍 |
| `debugging` | S0/S2–S7 | G0/G3/G4/G6 | 缺陷报告、复现、二分、根因、最小修复验证 |
| `api-data` | S2–S5 | G2/G3/G4/G5 | API 契约、错误、分页、幂等、授权边界、迁移与保留 |
| `security-compliance` | S0–S7 | G0/G2/G4/G5 | 威胁、凭据、供应链、SBOM、许可证、PII、披露 |
| `documentation` | S1–S7 | G1/G4/G5/G7 | 文档类型、同步、变更记录、文档站 |
| `project-structure` | S2–S4 | G2/G3/G4 | 目录与包边界、导入图、公开入口、生成目录 |
| `vcs-collaboration` | S2–S5 | G2/G3/G4/G5 | 分支模型、PR/MR、保护、CODEOWNERS、工作树 |
| `prompt-engineering` | S1/S2/S4 | G1/G2/G4 | 运行时提示词、输出契约、评测与回归 |
| `system-prompt-engineering` | S1/S2/S4 | G1/G2/G4 | 常驻指令文件的内容与格式 |
| `mcp-engineering` | S1/S2/S4 | G1/G2/G4 | MCP 服务器与工具设计、注册、安全、测试 |

每个 skill 的完整阶段契约见其 `references/lifecycle.md`；提示词台账见 [prompt-inventory.md](prompt-inventory.md)。
