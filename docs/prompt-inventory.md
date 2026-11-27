# 提示词台账

本文件登记 24 个 skill 的触发面（description 摘要）与主责，供核对触发冲突与覆盖缺口。

| skill | 触发场景 | 排除场景（不适用于） |
|---|---|---|
| `project-lifecycle` | 阶段、门禁、风险分级、裁剪、角色、工件、度量、组合 | 各阶段的技术规则细节 |
| `requirements-engineering` | 受理与需求收集、验收标准、DoR、收益基线 | 设计、实现细节 |
| `architecture-design` | 模块边界、分层、依赖方向、框架选择、ADR | 目录与包物理边界、并发细节 |
| `planning-estimation` | 任务拆分、估算、关键路径、风险与依赖登记 | 实施与测试细节 |
| `implementation-practices` | 小步提交、增量可运行、WIP、调试纪律、DoD | 风格、命名等专项规范 |
| `testing-quality` | 测试层级、质量门禁、覆盖率、静态分析 | 并发正确性、性能调优 |
| `release-operations` | 版本、CI/CD、发布回滚、监控告警、事故、备份 | 退役与交接 |
| `maintenance-retirement` | 补丁、技术债、退役归档、交接、复盘 | 新功能发布 |
| `code-style` | 格式、模块内布局、依赖版本、配置、错误与日志 | 命名、注释 |
| `naming` | 文件、代码、接口、数据、配置、提交、分支、标签命名 | 注释内容、文档结构 |
| `comments` | 行内注释、文档注释、标记、弃用、工具指令 | 独立文档与文档站 |
| `refactoring` | 重构与修复判定、安全手法、异味处理 | 并发、性能专项 |
| `code-review` | 审查深度、清单、作者与审查者职责、审查门禁 | 分支保护与权限管理 |
| `concurrency` | 共享状态、同步原语、死锁、异步模型、并发测试 | 并发性能调优 |
| `performance` | 测量、目标与预算、瓶颈、缓存索引取舍 | 并发正确性 |
| `debugging` | 缺陷报告、复现、二分、根因、最小修复验证 | 测试策略规划 |
| `api-data` | API 契约、错误、分页、幂等、授权边界、迁移与保留 | 接口命名、性能调优 |
| `security-compliance` | 威胁、凭据、供应链、SBOM、许可证、PII、披露 | 发布流程操作 |
| `documentation` | 项目文档类型、同步、变更记录、文档站 | 代码注释 |
| `project-structure` | 目录与包边界、导入图、公开入口、生成目录 | 模块逻辑分层 |
| `vcs-collaboration` | 分支模型、PR/MR、保护、CODEOWNERS、工作树 | 发布批准与回滚 |
| `prompt-engineering` | 运行时提示词、输出契约、评测与回归 | 常驻指令文件 |
| `system-prompt-engineering` | 常驻指令文件的内容与格式 | 运行时提示词、skill 包 |
| `mcp-engineering` | MCP 服务器与工具设计、注册、安全、测试 | 宿主平台自身功能 |

触发描述以各 `SKILL.md` 的 frontmatter 为准；本表为汇总索引。
