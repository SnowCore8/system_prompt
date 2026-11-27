---
name: skill-authoring
description: 定义、审查并重构可加载的 skill 包（SKILL.md 及其 references/scripts），覆盖结构、frontmatter、触发质量、渐进披露、references 组织、反模式与审查。适用于创建新 skill、审查现有 skill 的结构与触发质量，或把分散的规范整理成 skill；不适用于常驻指令文件（见 system-prompt-authoring）、运行时与产品提示词（见 prompt-authoring）、代码注释（见 comment-conventions）、内容事实本身（由对应领域 skill 管辖）与发布打包（见 release-operations-conventions）。
argument-hint: '[skill 目录或名称]'
---

# 编写与审查 skill

skill 是按需加载的规范包。它失效通常不是因为内容不足，而是因为触发不准、正文过载、事实散落在多处，或结构
不清。本 skill 规定 skill 的结构、写法与审查规则，使每个 skill 都满足四项要求：体量适度、规则可判定、可被
发现、边界清晰。

## 适用范围与优先级

效力依下列层级判断：高层覆盖低层，低层仅在高层未规定时补充；同一范围内不得混用标准。

1. 强制性的平台、法律、宿主与全局用户约束。宿主对 skill 的目录名、frontmatter 字段、`SKILL.md` 入口、
   加载与触发方式等强制要求，不可协商。
2. 本 skill 的规则。结构、写法与审查，以本文件与 `references/` 为准。
3. 仓库既有 skill 约定与事实。动笔前应当先阅读相邻 skill 的 `SKILL.md` 与 `references/`；这些内容属于
   事实输入，依本 skill 的规则处理。项目约定仅在本 skill 未规定时补充，不得覆盖本 skill。
4. 个人偏好，不得覆盖上述三层。

分工边界如下：

- 常驻指令文件（`AGENTS.md`、`CLAUDE.md`、`QWEN.md`）始终加载，由 `system-prompt-authoring` 管辖。
- 一次性或产品提示词一次交付，由 `prompt-authoring` 管辖；本 skill 仅管辖“按需触发加载、作为规范包维护”
  的 skill。
- 内容事实的写法由对应领域 skill 管辖，例如 API 契约由 `api-and-data-conventions` 管辖；本 skill 仅管辖
  承载结构。
- 项目文档与文档站由 `documentation-conventions` 管辖；发布节奏、版本与 CI 门禁由
  `release-operations-conventions` 与 `testing-and-quality-conventions` 管辖。

## 生命周期定位

上游输入：S1 的问题与读者、S2 的相邻 skill 边界结论与宿主字段约束。下游交接：S3 交付正文与 references，
S4 交付结构、触发与去重证据，供门禁与打包使用。升级与停止：与相邻 skill 争同一事实时交该事实的领域 skill
或在无管辖者时报 `project-lifecycle-governance` 裁决；宿主对目录名、frontmatter 与加载方式的要求无法满足时
停止并报告；一个 skill 承担两类读者时先拆分，拆不动即停止编写，不得混装。

| 阶段 | 本 skill 的职责 | 产出 / 证据 |
|---|---|---|
| S1 探索 | 判断是否值得新建：一类读者、一类任务、与相邻 skill 的边界 | 边界结论；不新建时的链接方案 |
| S2 计划 | 设计目录、frontmatter、正文与 references 的分工与行数预算 | 骨架、description 草稿、拆分计划 |
| S4 验证 | 校验结构、链接、去重与触发面，运行 Markdown 校验 | 校验输出、触发判断结论、去重结果 |

## 门禁与证据

| 门禁 | 必须提供的证据 | 不满足时 |
|---|---|---|
| G1 立项 | 一类读者、一类任务与相邻 skill 的边界结论；不新建时给出应链接的现有 skill | Hold：读者或边界不明时不建包 |
| G2 计划 | 目录与 frontmatter 方案、正文与 references 分工、行数与拆分预算 | Recycle：正文超预算仍塞细节的退回重划 |
| G4 验证 | Markdown 校验输出、`name` 与目录名一致、相对链接可解析、触发与排除项可判定 | Recycle：断链或触发面与边界不一致 |

`description` 的触发面无法只靠脚本判断，应当以典型任务句逐个核对“应当加载”与“不应当加载”两类判断，并把
结论写入交付。触发判断与边界声明不一致的，按验证未通过处理。

## 工作流

1. **确认所解决的一个问题。** 一个 skill 仅服务一类读者与一类任务；承担两项职责的，应当拆分为两个 skill。
2. **确定触发条件。** `description` 应当写成“适用于……，不适用于……”，不得罗列功能。
3. **编写入口。** `SKILL.md` 开头说明适用范围、优先级与分工边界，再给出核心规则。
4. **将细节拆至 `references/`。** 正文放置决策程序与默认值；长模板、清单与维度规则移入 `references/`，
   正文仅保留链接。
5. **脚本保持单一职责。** 脚本仅由 skill 调用；测试由项目测试套件承载，不放入 `scripts/`。
6. **校验。** 运行 Markdown 校验，确认 `name` 与目录名一致、相对链接与脚本路径可以解析，并复核触发判断。

## 结构

一个 skill 为一个目录，入口必须为 `SKILL.md`：

```text
<skill-name>/
├── SKILL.md        # 必填；frontmatter + 正文
├── references/     # 可选；按维度或模板拆分的参考，正文只放入口与规则
└── scripts/        # 可选；与 skill 配套的运行时脚本，测试不放入此处
```

frontmatter 字段如下：

| 字段 | 必需 | 内容 |
|---|---|---|
| `name` | 是 | 与目录名完全一致；智能体依该字段发现与匹配 |
| `description` | 是 | 一段话说明适用场景与触发条件，使智能体判断何时加载 |
| `argument-hint` | 是 | 调用时可以补充的上下文；以单引号包裹方括号，例如 `'[路径或名称]'` |

正文链接 `references/dimensions*.md` 的，必须有“维度索引”一节；说明句、表头与行格式见
[references/templates.md](references/templates.md)；不含维度文件的 skill 应当删除该节。

## 核心规则

- **目录名即名称。** `name` 必须等于目录名；改名的，应当同时修改目录与全部引用。
- **`description` 写触发条件与排除项，不写功能清单。** 使智能体能够直接判断“本次任务是否应当加载”，不得
  复述目录名。
- **入口应当简短。** `SKILL.md` 是路由与默认值，并非全文；正文不超过 250 行（不含 frontmatter），超出的
  细节移至 `references/`。
- **`references` 按主题管理。** 文件名按内容命名，下列为示例而非闭集：`dimensions.md`、`templates.md`、
  `languages.md`、`playbooks.md`、`gates.md`、`evaluation.md`、`checklist.md`、`checklists.md`。单个维度
  文件超过 300 行或 20 节时，按主题拆分为 `dimensions-<主题>.md`，该拆分规则仅适用于维度文件；清单只有
  一份时使用 `checklist.md`，多份时使用 `checklists.md`；索引详情列应当写明文件名与节号，节号与索引一致。
- **一项事实一个权威来源。** 共享事实仅在一处维护，其他 skill 以链接指向该处并注明“由 X 裁定”，不得复制。
- **规则可判定。** 应当避免使用“合理”“合适”，优先给出可观察条件、阈值与正反例。改写示例见
  [references/templates.md](references/templates.md)。
- **适用与不适用均须写明。** `description` 与正文边界应当一致；边界含糊将导致智能体在不应当加载时加载，或
  在重叠时选错。
- **脚本与测试分离。** `scripts/` 仅放置运行时脚本；测试由项目测试套件承载，不得混入 `scripts/`。

## 触发质量

`description` 是智能体决定是否加载的触发词，两个失败方向均须避免：

- 写得太宽泛：无关任务亦触发，加载成本消耗于不相干任务。
- 写得太窄：应当触发的任务从不加载，skill 形同虚设。

| 维度 | 合格 | 不合格 |
|---|---|---|
| 覆盖范围 | 写明一类读者与一类任务 | “全部场景”“通用 skill” |
| 排除项 | 写明不适用于何种情形 | 仅写适用，无边界 |
| 可判定 | 任务出现即可判断是否应当加载 | 仅有形容词或功能清单 |

正反例见 [references/templates.md](references/templates.md)。审查时应当取三个应加载与两个不应加载的任务句，
逐个判断，任一项判错即视为触发面需要修改。

## 渐进披露

- 正文第一屏应当回答：本 skill 的用途、加载时机与边界。
- 规则与默认值放置于正文；逐条展开、示例与边缘情况放置于 `references/`。
- 引用相对路径以 `SKILL.md` 所在目录为基准，移动目录后仍应可以解析。
- 脚本应当给出调用方式与必需参数；可执行示例应当能够在干净环境中运行。

内容位置如下：

| 内容 | 位置 |
|---|---|
| 用途、加载时机、边界 | 正文 |
| 规则与默认值 | 正文 |
| 逐条展开、边缘情况、示例 | `references/` |
| 长模板、清单、维度规则 | `references/` |

## references 组织

- 一个文件承载一类内容，不得堆叠于一个文件；文件类型、维度拆分与清单命名见核心规则“`references` 按主题
  管理”。
- 文件命名使用 kebab-case，名称描述内容，并与正文链接中的文件名完全一致。
- 一项事实仅在一处：正文与各 `references` 之间、`references` 之间，均不得互相复制，其余以链接引用。

## 反模式

| 反模式 | 失败原因 | 修复 |
|---|---|---|
| `description` 仅是名称的复述 | 智能体无法判断何时加载 | 写明“适用于……，不适用于……” |
| `SKILL.md` 塞满全部细节 | 加载成本高，规则被淹没 | 拆分至 `references/`，正文仅留入口 |
| 多个 skill 复制同一事实 | 副本分叉，各自为政 | 单一权威，其余链接 |
| 测试混入 `scripts/` | 测试与运行时脚本耦合，调用边界不清 | 测试交给项目测试套件，`scripts/` 只留运行时脚本 |
| 目录名与 `name` 不一致 | 发现与匹配错位 | 强制一致，由校验检查 |
| 正文仅使用形容词 | 无法审查与评测 | 改为可判定条件与示例 |
| 适用范围写“全部场景” | 触发泛滥或从不触发 | 写明读者、任务与排除项 |
| `description` 写得太窄 | 应当触发的任务从不加载 | 写明适用场景，不得仅列一个特例 |
| `references` 之间互相复制 | 修改一处遗漏另一处，副本分叉 | 一项事实仅在一处，其余链接 |

## 审查清单

- [ ] 一个 skill 仅服务一类读者与一类任务。
- [ ] `name` 与目录名一致，`description` 写明适用与不适用。
- [ ] `argument-hint` 存在，且为单引号包裹的方括号格式。
- [ ] `references/` 与 `scripts/` 仅在需要时存在，目录内无空占位文件。
- [ ] 触发质量合格：不宽泛、不狭窄、有排除项、可判定。
- [ ] `SKILL.md` 第一屏说明用途、触发与边界。
- [ ] 细节已拆至 `references/`，正文仅保留入口与默认值。
- [ ] 正文不超过 250 行（不含 frontmatter）。
- [ ] 正文与 `references/` 之间无重复的规则与默认值（示例、核对清单除外），清单仅有一处权威。
- [ ] `references` 文件名使用 kebab-case、与正文链接一致、无互相重复。
- [ ] 事实单一权威，交叉引用为链接而非复制。
- [ ] 规则可判定，带阈值或示例。
- [ ] `scripts/` 仅含运行时脚本，测试未混入。
- [ ] Markdown 校验通过，相对链接与脚本路径可以解析，三个应加载与两个不应加载的任务句判断正确。

## 示例

<example>
场景：新增 `prompt-authoring`，正文写了 400 行提示词规则。
问题：`SKILL.md` 过载，加载即消耗大量上下文。
修复：正文保留适用范围、优先级、工作流、核心规则与类型矩阵；将骨架与评测细节移至该 skill 的
`references/templates.md` 与 `references/evaluation.md`，正文以链接指向。
</example>

<example>
场景：三个 skill 各自复述“凭据不得写入提交”。
问题：修改规则须改三处，易于分叉。
修复：仅由 `security-compliance-conventions` 维护该条，其余 skill 链接至该处并说明“由安全规范裁定”。
</example>

## 参考资料

生命周期契约见 [references/lifecycle.md](references/lifecycle.md)；判断 skill 的阶段职责、门禁证据、交接升级
与裁剪度量时先读该文件。可复制骨架、frontmatter 模板、`description` 写法、目录布局与可判定改写见
[references/templates.md](references/templates.md)；新建 skill 或改写正文结构前读该文件。配套 skill 的加载
顺序与边界见 [references/skill-load-order.md](references/skill-load-order.md)；为一个项目制定规范、决定先加载
哪个 skill 时读该文件。
