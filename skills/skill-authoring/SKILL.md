---
name: skill-authoring
description: 定义、审查并重构可加载的 skill 包（SKILL.md 及其 references/scripts），覆盖 frontmatter、渐进披露、命名与触发词、适用边界、质量校验、打包与三端分发、反模式与审查清单。适用于创建新 skill、审查现有 skill 的结构与触发质量，或把分散的规范整理成 skill。不适用于常驻指令文件（见 system-prompt-authoring）、运行时与产品提示词（见 prompt-authoring）与代码注释（见 comment-conventions）。
argument-hint: '[skill 目录或名称]'
---

# 编写与审查 skill

skill 是给代理按需加载的规范包。它失败通常不是因为内容少，而是触发不准、正文过载、事实分散在多处、
打包时漏掉依赖或塞进不该有的文件。本 skill 给出 skill 的结构、写法、校验与分发规则，让每个 skill
都小、可判定、可发现、可打包。

## 适用范围与优先级

按以下层级判断效力，高层覆盖低层，低层只在高层未规定时补充；同一范围内不要混用标准。

1. 强制的平台、法律、宿主与全局用户约束。宿主对 skill 的目录名、frontmatter 字段、SKILL.md 入口、
   加载与触发方式等强制要求，不可协商。
2. 本 skill 的规则。结构、写法、校验与分发以本文件与 `references/` 为准。
3. 仓库既有 skill 约定与事实。动笔前先读相邻 skill 的 SKILL.md 与 references；这些是事实输入，按本
   skill 的规则处理。项目约定只在 skill 未规定时补充，不能覆盖本 skill。
4. 个人偏好，永远不能覆盖以上三层。

分工边界：

- 常驻指令文件（AGENTS.md、CLAUDE.md、QWEN.md）始终加载，归 `system-prompt-authoring`；
- 一次性或产品提示词一次交付，归 `prompt-authoring`；本 skill 只负责“按需触发加载、作为规范包分发的 skill”；
- 内容事实的写法归对应领域 skill（如 API 契约归 `api-and-data-conventions`），本 skill 只负责承载结构；
- 发布节奏、版本与 CI 门禁归 `release-operations-conventions` 与 `testing-and-quality-conventions`。

## 结构

一个 skill 是一个目录，入口必须是 `SKILL.md`：

```text
<skill-name>/
├── SKILL.md        # 必填；frontmatter + 正文
├── references/     # 可选；按维度或模板拆分的参考，正文只放入口与规则
└── scripts/        # 可选；与 skill 配套的可执行脚本，测试不得进入分发包
```

frontmatter 字段：

| 字段 | 必需 | 内容 |
|---|---|---|
| `name` | 是 | 与目录名完全一致；代理按它发现与匹配 |
| `description` | 是 | 一段话说明适用场景与触发条件，让代理判断何时加载 |
| `argument-hint` | 是 | 调用时可补充的上下文；单引号包裹方括号，如 `'[路径或名称]'` |

正文链接了 `references/dimensions*.md` 时，必须有「维度索引」一节；说明句、表头与行格式见
`references/templates.md`；不含维度文件的 skill 删掉该节。

## 流程

1. **确认要解决的一个问题。** 一个 skill 只服务一类读者与一类任务；写两份职责就拆成两个 skill。
2. **定触发条件。** 把 description 写成“适用于…”，而不是罗列功能；代理靠它决定要不要加载。
3. **写入口。** SKILL.md 开头说明适用范围、优先级与分工边界，再给核心规则。
4. **拆细节到 references。** 正文放决策程序与默认值；长模板、清单、维度规则移到 `references/`，正文只链接。
5. **配脚本时保持单向依赖。** 脚本只被 skill 调用；测试放仓库的 `tests/`，不进 `scripts/` 分发。
6. **校验。** 跑仓库的 Markdown 严格检查，确认 `name` 与目录名一致、链接与脚本路径可解析。
7. **打包验证。** 确认三端软链、zip 与 npm 包都包含该 skill，且没有测试、缓存或跨包文件。

## 核心规则

- **目录名即名字。** `name` 必须等于目录名；改名要同时改目录、软链与所有引用。
- **description 写触发条件与排除项，不写功能清单。** 让代理一眼判断“这次任务该不该加载”，而不是复述目录名。
- **入口要短。** SKILL.md 是路由与默认值，不是全文；正文不超过 250 行（不含 frontmatter），超出的细节移入 references。
- **references 单文件按主题管理。** 文件名按内容命名，下列是示例而非闭集：`dimensions.md`、`templates.md`、
  `languages.md`、`playbooks.md`、`gates.md`、`evaluation.md`、`checklist.md`、`checklists.md`。单个维度文件
  超过 300 行或 20 节时按主题拆成 `dimensions-<主题>.md`，拆分规则只针对维度文件；清单只有一份时用
  `checklist.md`，多份时用 `checklists.md`；索引详情列写文件名与节号，节号沿用原编号。
- **一项事实一个权威来源。** 共享事实只在一处维护，其他 skill 链接过去并注明“由 X 裁定”，不复制。
- **规则可判定。** 少用“合理”“合适”，多给可观察条件、阈值与正反例；改写示例见 `references/templates.md`。
- **适用与不适用都写清。** description 与正文边界一致；边界含糊会让代理在不该加载时加载，或在重叠时选错。
- **脚本与测试分离。** `scripts/` 只放运行时脚本；测试放仓库 `tests/`，分发包内不得出现 `test_*`。
- **打包只含本 skill 内容。** 不夹带其他 skill、缓存、`__pycache__`、本地配置或未跟踪文件。
- **与分发同步。** 新增 skill 要同时接入三端软链、更新计数与测试断言，再发布。

## 触发质量

description 是代理决定是否加载的触发词，两个失败方向都要避免：

- 写得太宽泛：无关任务也触发，加载成本花在不相干任务上。
- 写得太窄：该触发的任务从不加载，skill 形同虚设。

| 维度 | 合格 | 不合格 |
|---|---|---|
| 覆盖范围 | 写清一类读者与一类任务 | “全部场景”“通用 skill” |
| 排除项 | 写清不适用于什么 | 只写适用，无边界 |
| 可判定 | 任务出现即可判断该不该加载 | 只有形容词或功能清单 |

正反例见 `references/templates.md`。

## 渐进披露

- 正文第一屏回答：这是干什么、何时加载、边界在哪。
- 规则与默认值放正文；逐条展开、示例与边缘情况放 references。
- 引用相对路径以 SKILL.md 所在目录为基准，保持打包后可解析。
- 脚本给出调用方式与必需参数；可执行示例要能在干净环境跑通。

什么该下沉、什么该留在正文：

| 内容 | 位置 |
|---|---|
| 干什么、何时加载、边界 | 正文 |
| 规则与默认值 | 正文 |
| 逐条展开、边缘情况、示例 | references |
| 长模板、清单、维度规则 | references |

## references 组织

- 一个文件一类内容：按维度（`dimensions.md` 或拆成的 `dimensions-<主题>.md`）、按模板（`templates.md`）、
  按技术栈（`languages.md`）、按操作手册（`playbooks.md`）、按门禁（`gates.md`）、按评测（`evaluation.md`）、
  按检查清单（`checklist.md` 或 `checklists.md`）分别拆，不堆在一个文件里；这些文件名是示例，不构成闭集。
- 文件命名用 kebab-case，名字描述内容，并与正文链接里的文件名完全一致。
- 一条事实只在一处：正文与各 references 之间、references 之间都不互相复制，其余用链接引用。

## 打包与分发

本仓库的三个包各自引用同一套真源，分两层：

- 项目级入口：`.dsh/skills/`、`.qoder/skills/`、`.qwen/skills/` 是普通目录，内含每个 skill 指向顶层
  `skills/<name>` 的相对软链。
- 包内布局：`plugins/qoder/skills` 与 `plugins/qwen/skills` 是指向顶层 `skills/` 的包级软链，打包时解引用；
  DSH 由 `scripts/materialize.sh` 把 `skills/` 与 `rules/` 复制成真实目录，清单在仓库根 `package.json`。
- 每个包都必须包含全部 skill，计数一致；`dist.sh` 的 allowlist 拒绝测试与跨包文件。

## 反模式

| 反模式 | 为什么失败 | 修复 |
|---|---|---|
| description 只是名字换个说法 | 代理无法判断何时加载 | 写“适用于…，不适用于…” |
| SKILL.md 塞满所有细节 | 加载成本高，规则被淹没 | 拆 references，正文只留入口 |
| 多个 skill 复制同一事实 | 副本分叉，各自为政 | 单一权威，其余链接 |
| 脚本和测试混在 `scripts/` | 测试随包分发，污染用户环境 | 测试移入仓库 `tests/` |
| 目录名与 `name` 不一致 | 发现与匹配错位 | 强制一致，check 校验 |
| 打包漏接软链或计数不更新 | 三端 skill 数量漂移 | 新增 skill 同步三端与断言 |
| 正文只用形容词 | 无法审查与评测 | 换成可判定条件与示例 |
| 适用范围写“全部场景” | 触发泛滥或从不触发 | 写清读者、任务与排除项 |
| description 写得太窄 | 该触发的任务从不加载 | 写清适用场景，而非只列一个特例 |
| references 之间互相复制 | 改一处漏一处，副本分叉 | 一条事实只在一处，其余链接 |

## 审查清单

- [ ] 一个 skill 只服务一类读者与一类任务。
- [ ] `name` 与目录名一致，description 写清适用与不适用。
- [ ] description 触发质量合格：不宽泛、不窄、有排除项、可判定。
- [ ] SKILL.md 第一屏说明用途、触发与边界。
- [ ] 细节已拆到 references，正文只保留入口与默认值。
- [ ] 正文不超过 250 行（不含 frontmatter）。
- [ ] 正文与 references 之间没有逐字重复的段落，清单只有一处权威。
- [ ] references 文件名 kebab-case、与正文链接一致、无互相重复。
- [ ] 事实单一权威，交叉引用为链接而非复制。
- [ ] 规则可判定，带阈值或示例。
- [ ] `scripts/` 只含运行时脚本，测试在仓库 `tests/`。
- [ ] Markdown 严格检查通过，链接与脚本路径可解析。
- [ ] 三端软链已接入，计数与测试断言已更新。
- [ ] zip 与 npm 包包含该 skill，无测试、缓存或跨包文件。

## 示例

<example>
场景：新增 `prompt-authoring`，正文写了 400 行提示词规则。
问题：SKILL.md 过载，加载即消耗大量上下文。
修复：正文保留适用范围、优先级、流程、核心规则与类型矩阵；把骨架与评测细节移到 `prompt-authoring` 的
`references/templates.md` 与 `references/evaluation.md`（示例，文件属于另一 skill），正文用相对路径链接。
</example>

<example>
场景：三个 skill 各自复述“凭据不得写入提交”。
问题：改规则要改三处，容易分叉。
修复：只由 `security-compliance-conventions` 维护该条，其余 skill 链接过去并说明“由安全规范裁定”。
</example>

<example>
场景：skill 的 `scripts/` 里混入 `test_*.py`，随 zip 分发。
问题：用户环境出现无意义的测试文件，包体积与审查面变大。
修复：测试移入仓库 `tests/`，`dist.sh` 的 allowlist 对 `test_*` 直接报错。
</example>

## 参考资料

- SKILL.md 骨架与 frontmatter 模板：`references/templates.md`。
- 发布前检查清单与 check 映射：`references/checklist.md`。
