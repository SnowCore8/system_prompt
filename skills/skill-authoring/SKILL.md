---
name: skill-authoring
description: 定义、审查并重构可加载的 skill 包（SKILL.md 及其 references/scripts），覆盖 frontmatter、渐进披露、命名与触发词、适用边界、质量校验、打包与三端分发、反模式与审查清单。适用于创建新 skill、审查现有 skill 的结构与触发质量，或把分散的规范整理成 skill。常驻指令文件见 system-prompt-authoring，提示词见 prompt-authoring。
argument-hint: '[skill 目录或名称]'
---

# 编写与审查 skill

skill 是给代理按需加载的规范包。它失败通常不是因为内容少，而是触发不准、正文过载、事实分散在多处、
打包时漏掉依赖或塞进不该有的文件。本 skill 给出 skill 的结构、写法、校验与分发规则，让每个 skill
都小、可判定、可发现、可打包。

## 适用范围与优先级

适用第一条匹配的规则，不要在同一范围内混用标准：

1. 宿主对 skill 的强制约束：目录名、frontmatter 字段、SKILL.md 入口、加载与触发方式，不可协商。
2. 仓库既有 skill 的结构与写法。动笔前先读相邻 skill 的 SKILL.md 与 references，沿用其标题、语气与字段。
3. 上述未规定时，采用本 skill 的默认值。
4. 个人偏好，永远不能覆盖以上三级。

分工边界：

- 常驻指令文件（AGENTS.md、CLAUDE.md、QWEN.md）归 `system-prompt-authoring`；
- 一次性或产品提示词归 `prompt-authoring`；本 skill 只负责“作为规范包分发的 skill”；
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
| `argument-hint` | 否 | 调用时可补充的上下文，如 `[路径或名称]` |

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
- **description 写触发条件，不写摘要。** 让代理一眼判断“这次任务该不该加载”，而不是复述目录名。
- **入口要短。** SKILL.md 是路由与默认值，不是全文；正文超过一屏就拆 references。
- **一项事实一个权威。** skill 之间共享的事实只在一处维护，其他 skill 链接过去，不复制。
- **规则可判定。** 少用“合理”“合适”，多给可观察条件、阈值与正反例。
- **适用与不适用都写清。** 边界含糊会让代理在不该加载时加载，或在重叠时选错。
- **脚本与测试分离。** `scripts/` 只放运行时脚本；测试放仓库 `tests/`，分发包内不得出现 `test_*`。
- **打包只含本 skill 内容。** 不夹带其他 skill、缓存、`__pycache__`、本地配置或未跟踪文件。
- **与分发同步。** 新增 skill 要同时接入三端软链、更新计数与测试断言，再发布。

## 渐进披露

- 正文第一屏回答：这是干什么、何时加载、边界在哪。
- 规则与默认值放正文；逐条展开、示例与边缘情况放 references。
- 引用相对路径以 SKILL.md 所在目录为基准，保持打包后可解析。
- 脚本给出调用方式与必需参数；可执行示例要能在干净环境跑通。

## 打包与分发

本仓库的三个包各自引用同一套真源：

- 软链：`.dsh/skills/`、`.qoder/skills/`、`.qwen/skills/` 各自指向顶层 `skills/<name>`；
- Qoder/Qwen 的 zip 与 DSH 的 npm 包在打包时解引用为真实目录；
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

## 审查清单

- [ ] 一个 skill 只服务一类读者与一类任务。
- [ ] `name` 与目录名一致，description 写清适用与不适用。
- [ ] SKILL.md 第一屏说明用途、触发与边界。
- [ ] 细节已拆到 references，正文只保留入口与默认值。
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
修复：正文保留适用范围、优先级、流程、核心规则与类型矩阵；把骨架与评测细节移到 `references/templates.md`
与 `references/evaluation.md`，正文用相对路径链接。
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
