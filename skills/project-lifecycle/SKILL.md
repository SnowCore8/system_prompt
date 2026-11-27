---
name: project-lifecycle
description: 定义、裁剪并执行软件工程生命周期治理：S0–S7 八阶段、G0–G7 八门禁、六种门禁决定、R0/R1/R2 分级与裁剪、角色、工件、度量、组合与依赖、DoR/DoD 与迭代。适用于受理请求、门禁决策、迭代规划、依赖登记与复盘收尾；不适用于代码风格、架构细节、测试实现、发布操作与安全控制。
argument-hint: '[阶段号、门禁号或风险级别]'
when-to-use: 受理新请求、召开门禁、分级风险、规划迭代、设计工件模板、登记依赖或组织复盘时加载。
---

# 软件工程生命周期治理

项目失效的常见原因不是文档少，而是决定没有证据、阶段被跳过、角色没有决策权。本 skill 把受理、需求、
设计、构建、验证、发布、运维与收尾组织成一条带门禁的生命周期：每个阶段有入口、产出与出口决定，每个
门禁只判断证据是否足以进入下一阶段。敏捷迭代在构建与验证阶段内提供短反馈循环，门禁负责承诺与风险
决策，两者互补而不互相替代。本 skill 裁定阶段、门禁、风险分级、角色、工件、度量与组合规则；各阶段内
的技术标准由对应专业 skill 规定。

## 适用范围与优先级

1. 效力顺序：`rules/global-user-constraints.md` 的强制条款最高，其次本 skill 的生命周期规则，再次各专业
   skill 的技术规则，最后是项目约定。授权（AUT）、保密（SEC）、不可逆（IRR）、诚实（HON）与意图（INT）
   条款不得因进度、阶段或迭代节奏而放松。
2. 管辖：阶段划分与出口条件、门禁判据与六种决定、风险分级与裁剪、角色与决策权、工件与模板、生命周期
   度量、组合与依赖、DoR/DoD 与迭代规则、交接与升级。本 skill 展开 GAT（门禁）、EXE（执行与迭代）、
   CHG（变更）与 UNC（不确定）域；OUT（输出）域的交付契约归 `prompt-engineering`，本 skill 提供记录
   模板。
3. 不管辖：代码风格（`code-style`）、命名（`naming`）、注释（`comments`）、实现实践（`implementation-practices`）、
   重构（`refactoring`）、并发（`concurrency`）、调试（`debugging`）、架构与 ADR 内容（`architecture-design`）、
   目录与包（`project-structure`）、接口与数据（`api-data`）、测试与质量门禁（`testing-quality`）、代码审查
   （`code-review`）、安全与合规（`security-compliance`）、性能（`performance`）、文档（`documentation`）、
   发布与运维操作（`release-operations`）、版本控制与工作树（`vcs-collaboration`）、退役与归档
   （`maintenance-retirement`）、需求工程（`requirements-engineering`）、计划与估算（`planning-estimation`）、
   提示词与 skill 包（`prompt-engineering`、`system-prompt-engineering`、`mcp-engineering`）。这些 skill 在
   本 skill 划定的阶段与门禁内提供证据与结论。
4. 冲突处理：本 skill 与专业 skill 结论冲突时，依第 1 条层级裁定；安全、授权与不可逆约束优先于进度与
   效率。阶段与门禁编号的解释权归本 skill。

## 生命周期定位

本 skill 是生命周期的主持者，不代替专业判断：它在 S0 固定请求与风险，在 S1/S2 组织需求与设计承诺，在
S3/S4 检查增量与证据，在 S5 组织上线，在 S6 跟踪运行，在 S7 组织收益复盘与归档。

| 阶段 | 职责 | 产出与证据 |
|---|---|---|
| S0 受理 | 复述并分类请求，确认授权、风险级别、停止条件与负责人 | 受理记录、风险依据 |
| S1 需求 | 澄清需求与用户，定义结果指标、收益基线与优先级，比较选项并给出建议 | 需求说明、G1 建议 |
| S2 设计 | 固定范围与验收标准，组织设计、测试、发布与回滚方案，登记依赖与风险 | 计划基线、ADR、风险与依赖登记 |
| S3 构建 | 按迭代交付可运行增量，维护 DoR/DoD 与 WIP，组织评审 | 增量、迭代记录、评审结论 |
| S4 验证 | 组织测试、安全、性能与独立审查，对照验收标准给出结论 | 验证证据包、验收结论 |
| S5 发布 | 组织发布准备、回滚演练、生产授权、可观测性与通告 | 发布记录、G5 决定 |
| S6 运维 | 跟踪运行指标与告警，组织事故响应与恢复演练，维护运行手册与值守 | 运行指标、事故记录、演练结果 |
| S7 收尾 | 对照收益基线复盘，退役与归档，交接运行责任与未关闭风险 | 收尾报告、行动项、交接记录 |

风险分级：R0 轻量（可逆、局部，如单文件措辞修正）；R1 标准（多文件、依赖变更、共享分支）；R2 关键
（生产、凭据、不可逆操作）。级别不明时取较高一级；范围或影响变化时重新分级并记录依据。

上游：用户与发起人、产品负责人、各专业 skill 的事实与结论。下游：交付团队、质量与安全、运营、审查者
与组合委员会。停止条件：授权不清、风险级别无法确定、关键依赖未确认、证据缺失或出现安全与不可逆风险
时，停止推进并报告；不得以“先做一点”绕过门禁。

## 门禁与证据

门禁是阶段之间的风险决策点：只判断现有证据是否足以承担下一阶段的风险。决定只有六种：Go（进入下一
阶段）、Conditional Go（附条件进入）、Hold（证据不足暂停）、Recycle（退回指定阶段返工）、No-Go（停止
或关闭）、Defer（仅组合层用于排队）。Conditional Go 必须写明条件、负责人、到期日与关闭证据；条件不得
是本门禁本应完成的证据。

| 门禁 | 必须提供的证据 | 不满足时 |
|---|---|---|
| G0 受理门 | 请求复述、授权依据、风险级别、停止条件、负责人 | 澄清或 Hold；不得开始修改 |
| G1 立项门 | 需求与用户、结果指标、收益基线、选项比较、初步安全判断 | Recycle 到需求或 No-Go |
| G2 计划门 | 范围与非范围、验收标准、设计或 ADR、测试策略、风险登记、回滚计划 | Hold 或 Recycle；不得带缺口构建 |
| G3 构建门 | 可运行增量、相关测试、评审结论、DoD 检查、文档更新 | Recycle 到构建 |
| G4 验证门 | 测试输出、安全与合规结论、性能证据、验收结论、独立审查 | Recycle 到构建或 Hold |
| G5 发布门 | 版本与制品、回滚演练、生产授权、可观测性、通告 | Hold；不得上线 |
| G6 运维门 | 监控告警、值守升级、恢复演练、事故记录与改进项 | Recycle 到运维；不得无人值守上线 |
| G7 收尾门 | 收益对照、偏差、复盘行动、退役与归档、交接、未关闭风险 | 继续整改或转为运维改进 |

证据必须来自实际执行：测试命令与真实输出、审查记录、演练记录、指标查询或明确批准。计划中的工作、口头
保证与“应该没问题”不构成证据；证据缺失或责任人缺失时，决定为 Hold 或 Recycle。R0 可合并门禁记录但不得
跳过验证；R1 不得省略独立审查；R2 不得自批、不得省略回滚演练、不得在证据缺失时 Go。门禁矩阵、决定语义
与证据标准见 `references/gates.md`；本 skill 自身在各门禁的检查方式见 `references/lifecycle.md`。

## 维度索引

| 编号 | 维度名 | 首条规则 | 详情 |
|---|---|---|---|
| 1 | 阶段流程 | 每个阶段必须有入口条件、可核验产出与明确的出口决定。 | `references/stages.md` 第 1 节 |
| 2 | 门禁决定 | 门禁决定只能是 Go、Conditional Go、Hold、Recycle、No-Go 或组合层 Defer 六种之一。 | `references/gates.md` 第 1 节 |
| 3 | 风险分级 | 风险级别分为 R0、R1、R2 三级，级别不明时应当取较高一级。 | `references/risk.md` 第 1 节 |
| 4 | 敏捷迭代 | 条目进入迭代前必须满足 DoR，增量交付时必须满足 DoD。 | `references/agile.md` 第 1 节 |
| 5 | 角色与决策权 | 角色可以兼任，但 R2 门禁的独立审查与批准不得由执行者兼任。 | `references/roles.md` 第 1 节 |
| 6 | 工件与证据 | 每项事实只允许保留一个权威归属，工件必须标注负责人与状态。 | `references/artifacts.md` 第 1 节 |
| 7 | 生命周期度量 | 指标必须可追溯到原始记录，不得用于个人排名。 | `references/metrics.md` 第 1 节 |
| 8 | 组合与依赖 | 关键依赖未经提供者书面确认时，相关门禁不得判为 Go。 | `references/portfolio.md` 第 1 节 |
| 9 | 模板与记录 | 模板字段不得删除授权、风险、验收、回滚与收益字段。 | `references/templates.md` 第 1 节 |

## 参考资料

本 skill 自身的阶段职责、门禁证据、交接与升级、裁剪与度量见 `references/lifecycle.md`；阶段活动与风险
裁剪见 [references/stages.md](references/stages.md)；风险分级与裁剪见 [references/risk.md](references/risk.md)；
门禁决定与矩阵见 [references/gates.md](references/gates.md)；迭代与 DoR/DoD 见
[references/agile.md](references/agile.md)；角色与决策权见 [references/roles.md](references/roles.md)；
工件清单与证据包见 [references/artifacts.md](references/artifacts.md)；指标口径见
[references/metrics.md](references/metrics.md)；组合、依赖与容量见
[references/portfolio.md](references/portfolio.md)；工件模板见 [references/templates.md](references/templates.md)；
24 个 skill 的阶段归属见 [references/mappings.md](references/mappings.md)。
