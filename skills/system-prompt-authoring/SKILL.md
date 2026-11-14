---
name: system-prompt-authoring
description: 起草、审查或重构面向编码代理的常驻指令文件（AGENTS.md、CLAUDE.md、QWEN.md）。适用于：用户要创建此类文件、判断现有行该保留还是修改，或把规则追溯到厂商文档。校验脚本只校验 Markdown 格式；内容规则靠人工判断。
argument-hint: '<目标文件>'
---

# 起草或审查系统提示

你负责起草与审查面向编码代理的常驻指令文件。交付物是可直接加载的 Markdown：内容规则靠人工检查，Markdown
格式由校验脚本（`scripts/check.py`）校验。

## 范围与优先级

套用第一条适用的规则，同一范围内不要混用标准：

1. 平台或组织的强制策略。宿主规则、安全规则与受管配置都不是可选项。
2. 现有项目约定。先读仓库的指令文件，遵循更严格的本地规则。
3. 以上层级未规定时，采用本 skill 的默认值。
4. 个人偏好，它永远不能覆盖以上三级。

- 独立项目文档（结构、模板、行文）：`documentation-conventions`。
- 标识符与文件名：`naming-conventions`。
- 必需文件的存在与元数据：`repository-governance-conventions`。
- 凭据与机密：`security-compliance-conventions`。
- 门禁与 CI：`testing-and-quality-conventions` 与 `release-operations-conventions`。
- 一次性或产品提示词（非常驻指令）：`prompt-authoring`。
- skill 包（SKILL.md 及其 references/scripts）的结构与打包：`skill-authoring`。

## 流程

1. 确认目标文件、任务类型（新建文件还是审查）与意图：回答、评估还是改文件。提问只给答案；带目标的动作请求
   就去做；含糊的请求先给分析与选项。路径或意图不清楚时提问，不要猜。目标不是指令文件时，说明超出范围并
   停止。
2. 用「五项输入」收集信息。仓库能回答的不要问；确实拿不到时，采用默认值，并在报告中说明该假设。
3. 新建文件时，填写「模板」并删掉任务不需要的节。审查时，逐行套用「删除标准」，并让每条约束只出现在一处。
4. 人工检查内容规则 S1-S13。脚本不判断这些规则；格式校验通过不代表内容合格。
5. 运行格式校验并修复 `[错误]` 项。非 `--strict` 模式下，为每个 `[警告]` 项写出结论；`--strict` 模式下，
   每条警告都必须在源头消除，因为只写结论过不了门禁。
6. 按固定顺序报告：文件路径；校验脚本命令与逐字输出；S1-S13 逐项结论；未解决项与假设。报告保持简洁，只
   粘贴关键输出。若有项未解释清楚，不要说工作已完成。

用本会话已加载的用户全局约束；本 skill 只补充指令文件特有的规则。

## 五项输入

| 输入 | 用途 | 缺失时 |
|---|---|---|
| 角色与范围 | 角色与目标 | 提问：该代理负责什么，什么算完成？ |
| 任务与工具 | 指令、工作流 | 提问；有仓库配置时先读配置 |
| 输出要求 | 输出格式 | 提问：结构、长度、是否粘贴命令输出 |
| 安全边界 | 红线、Never | 提问：哪些操作需要确认，哪些绝不允许发生 |
| 目标模型 | S13 粒度 | 采用 S13 默认值；不要因为模型未知就放松红线 |

从 `README`、`package.json`、`pyproject.toml`、`Makefile` 或 CI 配置中读取构建与测试命令、目录约定与语言
版本，写入 `Context`。

## 内容规则 S1-S13

「校验方式」列说明每条规则由谁检查：校验脚本只覆盖 S12 中可机器校验的格式项，其余全部人工检查。

| # | 要求 | 校验方式 | 来源 |
|---|---|---|---|
| S1 | 写明角色、范围与完成定义 | 人工 | OAI-41 §Prompt Structure；ANT-PBP §Give Claude a role；MS §Design checklist 1；§Role and scope |
| S2 | 每条禁止项都给出替代行为或理由；红线可以保持禁止性，但必须说明理由 | 人工 | ANT-PBP §Control the format of responses；§Add context |
| S3 | 默认使用平实的祈使句，强调只留给红线。当前模型能遵循平实表述，堆砌强调会导致过度套用 | 人工 | OAI-41 §Recommended Workflow；CC-BP (2026-11-14)；ANT-PBP §Tool usage |
| S4 | 为含糊、超范围与信息不足的请求各给出一个动作；单步任务至少要有「无法处理」分支 | 人工 | MS §Design checklist 4；§How system messages work |
| S5 | 不要用编号声明优先级；不要留下无条件的相互矛盾要求 | 人工 | OAI-MS §Instructions and levels of authority |
| S6 | 输出格式写明结构、长度与格式 | 人工 | MS §Output contract；§Design checklist 3；GOOG §Core prompting principles |
| S7 | 定义非平凡行为规则的提示词用 3-5 个示例；简短单一用途的提示词可以省略示例。每个示例展示规则未覆盖的行为；边界情况并入示例 | 人工 | ANT-PBP §Use examples effectively；ANT-CE §The anatomy of effective context |
| S8 | `Context` 只放模型无法从代码推导的信息 | 人工 | CC-BP (2026-11-14) |
| S9 | 删掉某行若不会阻止任何具体错误，就删掉它；只在部分任务用到的细节移入 skill | 人工 | CC-BP (2026-11-14) |
| S10 | 不要写未确认的工具、命令或配置键 | 人工 | 推导；ANT-PBP §Minimizing hallucinations 支持 |
| S11 | 长文档不要放进指令文件，改为链接；一行承载一条要求，禁止写成压缩的段落 | 人工 | ANT-CE §Context retrieval；CC-BP (2026-11-14)；行数限制是工程约束 |
| S12 | 不使用占位符；行尾不留空白或制表符；正文行最多 200 个字符；围栏成对；文件以换行结尾 | 人工 + 校验脚本（占位符人工） | 工程约束 |
| S13 | GPT 模型要给明确指令；推理模型只给目标与约束；模型未知时使用平实祈使句 | 人工 | OAI-PE §Choosing a model；§Prompting reasoning models |

以下是推导内容，并非厂商原文：完成定义（S1）、输出格式三要素（S6）、示例合并规则（S7）、单步豁免（S4）
与 S10。

S2 与 S3 合起来看：红线一节可以用「绝不」，但仍需给出理由。加粗标题属于导航，不算强调；S3 说的强调指加强
整句语气。对 S12，可机器校验的格式项以校验脚本结果为准，占位符等其余内容项人工检查。

S5 反对把编号当作隐含优先级。文件可以显式声明同节内的顺序（例如「靠前的规则优先」）；有声明时遵循声明，
没有声明时不要把编号当依据。

## 解决来源冲突

- **强调**：默认使用平实祈使句。OAI-41 指出，全大写与贿赂式激励"generally not necessary"；ANT-PBP 指出，
  为旧模型写的强硬措辞应当收回。当前指南（CC-BP，2026-11-14）指出，当前模型能遵循平实表述，堆砌强调多半
  会让它们过度套用规则；只强调红线。
- **粒度**：先写目标与约束。只有当顺序或完整性至关重要时才列出步骤，并说明跳过某步会怎样（ANT-PBP：
  "Prefer general instructions over prescriptive steps."）。对需要显式规划的非推理模型，按 OAI-41 增加
  `Reasoning Steps`。
- **长度**：没有总长度限制；单行限制见 S12。
- **禁止项**：保留红线并说明理由；其余都写出替代行为。
- **优先级**：编号本身不产生优先级；不要写「编号小的优先」。文件可以显式声明顺序；有声明就遵循。OAI-MS
  层级：root > system > developer > user > guideline；同层中较晚的消息覆盖较早的。
- **兜底**：说明信息不足时怎么做。只写「先调用工具」会让该分支没有定义。

## 删除标准

对每一行问：删掉它会不会导致一个具体错误。

若答案为「不会」，就删掉。CC-BP 当前页面（2026-11-14）指出，`CLAUDE.md` 只保留模型无法从代码推断的内容时
效果最好。标准是信号，而非字数（ANT-CE："minimal does not necessarily mean short"）。

`Context` 只放左列的内容：

| 纳入 | 排除 |
|---|---|
| 模型猜不出的 shell 命令 | 读代码就能知道的内容 |
| 与语言默认风格不同的风格要求 | 通用的语言约定 |
| 如何运行测试、用哪个运行器 | 详细的 API 文档（改为链接） |
| 仓库约定（分支命名、提交格式） | 快速变化的信息 |
| 项目特有的架构决策 | 长篇解释或教程 |
| 必需的环境变量 | 「写出整洁代码」这类不言自明的要求 |

示例：定义非平凡行为规则的提示词使用 3-5 个示例，每个示例展示规则未覆盖的行为；把边界情况并入示例，而不是
单独列清单（ANT-CE 反对罗列清单）。简短单一用途的提示词可以省略示例；示例可以把规则套用到具体案例，但它
必须补上规则本身无法定论的决策。

## 各节的写法

- **角色与目标（Role and Objective）**：用一两句话写清角色、范围与完成定义。
- **指令（Instructions）**：`Always` 写明要做什么；`Never` 只放红线，每条附理由；`When Unsure` 覆盖 S4。
  使用平实祈使句。
- **工作流（Workflow）**：仅当调整步骤顺序会改变结果时才写，并说明跳过某步会怎样。
- **输出格式（Output Format）**：写明结构、长度与格式。不写长度，模型就用默认值；GOOG 指出 Gemini 3 默认
  简短，因此详细输出必须显式要求。
- **示例（Examples）**：每个示例用 `<example>` 包裹，避免被当作指令读取。
- **上下文（Context）**：使用上面的表；长文档改为链接或指向，不要粘贴。

`Reasoning Steps` 只用于需要显式规划的非推理模型；`Final instructions` 是长提示词末尾的可选复述。用不到就
删掉。

## 复杂逻辑

规则涉及多个条件组合或在状态间迁移时，用表格作为事实来源；不要把它们放进一张大图。

- 多个条件选出一个动作：用判定表。条件列使用布尔值或枚举，并说明匹配顺序、`*` 与 `-` 的含义以及默认分支。
- 任务随事件迁移：用状态表。列出当前状态、事件、条件、下一状态与动作；未列出的组合落到默认。
- 表格与图并存时，表格是事实来源，图只是概览；冲突以表格为准。
- 表格开始重复或嵌套超过两层时，拆分下级判定，或改用伪代码，或改用带表驱动测试的纯函数。

模板、授权示例与任务生命周期示例见 [references/complex-logic.md](references/complex-logic.md)。

## 机器校验

脚本只校验 Markdown 语法、版式与链接有效性；不读语义、不判断规则、不追溯来源。退出码：0 无错误，1 有错误，
2 参数、依赖或文件问题。

### 用法

路径相对于本 skill 的目录；把 `<skill-dir>` 换成实际路径：

```bash
python3 <skill-dir>/scripts/check.py AGENTS.md
```

在 CI 中加上 `--strict`；警告也算失败，退出码为 1：

```bash
python3 <skill-dir>/scripts/check.py --strict AGENTS.md
```

`--strict` 下，任何警告都会使运行失败；必须在源头消除（对已记录的误报，改造该写法或修改校验脚本），因为
只记录解释并不会改变退出码。

脚本依赖 `markdown-it-py==4.2.0`；缺失时脚本报错并打印安装命令，不会自动安装。脚本自身的测试使用标准库
unittest：

```bash
python3 -B -m unittest discover -s tests/skill -p 'test_*.py'
```

### 规则

输出分三级：

| 级别 | 含义 | 影响退出码 |
|---|---|---|
| 错误（`[错误]`） | 文件结构已损坏 | 是 |
| 警告（`[警告]`） | 需要修复的格式问题 | 否（加 `--strict` 时为是） |
| 建议（`[建议]`） | 可能的改进 | 否 |

每条发现给出位置（`L<line>` 或整个文件）、规则 ID、原因与修复建议。

按级别分组，再按行排序。

| 规则 | 级别 | 校验内容 |
|---|---|---|
| MD-BOM | 警告 | 文件以 BOM 开头 |
| MD-EOL | 警告 | 混用 CRLF、LF 或 CR 行尾 |
| MD-FINAL-BLANK | 警告 | 文件末尾有多余空行 |
| MD-FINAL-NEWLINE | 错误 | 缺少末尾换行 |
| MD-FENCE | 错误 | 围栏未闭合 |
| MD-FENCE-LANG | 建议 | 围栏代码块没有语言标记 |
| MD-FENCE-STYLE | 建议 | 同一文件混用反引号与波浪号围栏 |
| MD-HTML-COMMENT | 错误 / 警告 | 块注释未闭合：错误；行内注释未闭合：警告（仅 `--strict` 下失败） |
| MD-HTML-BLOCK | 错误 | `<script>`、`<style>`、`<pre>` 或 `<textarea>` 块未闭合 |
| MD-HEAD-SPACE | 警告 | `#` 后无空格；该行会渲染成段落 |
| MD-HEAD-MULTI-SPACE | 警告 | `#` 后有多个空格 |
| MD-HEAD-INDENT | 建议 | 顶层标题缩进 1-3 个空格 |
| MD-HEAD-START | 警告 | 首个标题不是 h1 |
| MD-HEAD-JUMP | 警告 | 标题级别跳跃 |
| MD-HEAD-EMPTY | 警告 | 标题没有文本 |
| MD-HEAD-DUP | 警告 | 标题重复（忽略大小写与空白） |
| MD-HEAD-BLANK-AFTER | 建议 | 标题后无空行 |
| MD-LIST-SPACE | 警告 | 列表标记后无空格 |
| MD-LIST-MARKER | 警告 | 同一列表段混用 `-`、`*` 与 `+` |
| MD-LIST-START | 警告 | 有序列表不是从 1 开始 |
| MD-LIST-EMPTY | 警告 | 列表项没有内容 |
| MD-LIST-INDENT | 警告 | 同级缩进不一致，或缩进过深导致列表结构丢失 |
| MD-QUOTE-SPACE | 建议 | `>` 后无空格 |
| MD-TABLE-COLS | 警告 | 表格各行列数不一致 |
| MD-TABLE-BROKEN | 警告 | 连续的管道行未解析为表格（分隔行缺列或短横线有误） |
| MD-LINK-REF | 警告 | 引用的标签未定义 |
| MD-LINK-DEF-DUP | 警告 | 同一标签定义了两次；后者被忽略 |
| MD-LINK-DEF-EMPTY | 警告 | 链接定义没有目标 |
| MD-LINK-DEF-UNUSED | 建议 | 定义从未被引用 |
| MD-LINK-EMPTY | 警告 | 链接或图片没有文本或没有目标 |
| MD-LINK-TEXT-SPACE | 建议 | 链接或图片文本首尾有空白 |
| MD-LINK-TARGET | 警告 | 相对链接或图片目标在仓库中不存在 |
| MD-LINK-SYNTAX | 警告 | `[text](` 未解析为链接 |
| MD-ANCHOR | 警告 | 页内锚点指向不存在的标题 |
| MD-INLINE-CODE | 警告 | 反引号未配对 |
| MD-EMPHASIS | 警告 | `**`、`__` 或 `~~` 未配对 |
| MD-EMPHASIS-STYLE | 建议 | 同一文件混用斜体或加粗标记 |
| MD-INLINE-HTML | 警告 | 已知行内 HTML 标签只开未闭 |
| MD-BLANK-RUN | 警告 | 连续多个空行 |
| MD-BLANK-BEFORE-BLOCK | 建议 | 顶层块前无空行 |
| MD-BLANK-AFTER-BLOCK | 建议 | 顶层块后直接跟正文 |
| MD-LINE-LEN | 警告 | 正文行超过 200 个字符；表格、代码、URL 与 front matter 不受限 |
| MD-TRAILING-WS | 警告 | 行尾空白 |
| MD-TAB | 警告 | 正文中有制表符 |
| MD-HR-STYLE | 建议 | 同一文件混用分隔线样式 |

### 校验范围

这些校验基于 CommonMark 解析器的结果，而不是逐行正则：

- 结构类校验会跳过围栏、缩进代码、HTML 块与 front matter。`<example>` 按普通 HTML 处理。
- BOM、混用行尾与末尾空行按原始文本校验；解析前会去掉 BOM，因此它不影响首个标题。
- 空行前置校验只看顶层块；嵌套列表或引用块内的块、以及标题之后的块都不报告。
- 空行后置校验只看顶层块；嵌套列表或引用块内的块不报告，块末尾已有的空行会跳过。
- 仅当块后跟正文时才报告空行后置；若后面是另一个块，则不报告。
- 标题后的空行仅在下一行是正文时报告；列表、表格、围栏及其他块起始都不报告。
- 标题缩进只校验顶层标题；列表或引用块内的标题不报告。
- 围栏、分隔线与强调样式校验仅在同一个文件中混用样式时触发。
- 反引号与强调标记可以跨行配对；脚本按「解析器未消费的标记」判断，因此合法的跨行配对不会报告。
- 链接定义取自解析器的引用表；写在下一行的目标与列表项内的定义都能识别。
- 表格分隔行有误时，整张表会退化为段落；`MD-TABLE-BROKEN` 会捕获这种情况。
- 外部链接、`mailto:` 与锚点不校验本地是否存在；锚点会转换为 GitHub slug 后比对。
- 行内 HTML 校验只使用 `html_inline` token；自动链接与 `<placeholders>` 不会被当作未闭合。

### 有意不校验的项

以下三项有意不校验，因为机械校验只会制造噪声：

| 不校验项 | 原因 |
|---|---|
| 未配对的单个 `*` 或 `_` | `*.py`、`src/*.ts`、`2*3` 与 `**/*.md` 使用相同字符；区分它们需要语义 |
| Setext 标题（`===`、`---` 下划线） | 合法语法；否则正常标题会被报告 |
| 表格中的空表头单元格 `\| a \|  \|` | 合法且常见 |

`MD-INLINE-HTML` 有一处残留误报：讲解语法时写下的单个 `<div>` 与真正未闭合的标签无法区分。把这类内容
放进反引号或代码块即可跳过。

### 阅读输出

- `[错误]`（错误）：修复并重跑，直到 0 项且退出码为 0。
- `[警告]`（警告）：非 `--strict` 模式下逐条写出结论（结构性误报要说明是标题措辞问题，不是内容缺失）；
  `--strict` 模式下在源头修复。
- `[建议]`（建议）：按 S9 决定；可选。

## 反模式

| 反模式 | 修复 |
|---|---|
| 规则堆到必须通读才能找到一条 | 按 S9 删除；把细节移入 skill |
| 把编号当作隐含优先级 | 使用显式顺序声明，或拆分小节 |
| 全是禁止项，没有替代行为 | 按 S2 补替代行为或理由 |
| 红线与普通要求都用「绝不」 | 按 S3，绝对措辞只留给红线 |
| 每条规则都加粗 | 加粗只用于导航；整句强调只留给红线（S3） |
| 只写「先调用工具」 | 按 S4 补信息不足分支 |
| 写死分步流程 | 写目标与约束；仅当顺序关键时保留步骤（解决来源冲突 > 粒度） |
| 粘贴 API 文档 | 改为链接（S11） |
| 写不存在的工具或配置键 | 只写已确认的接口（S10） |
| 把边界情况堆成示例清单 | 并入 3-5 个示例（S7） |
| 把复杂规则塞进一张大图 | 用判定表或状态表；图只作概览 |

## 审查清单

- [ ] 已确认目标文件与任务类型（新建文件还是审查）。
- [ ] 五项输入已收集，或每个缺失项都写成了明确的假设。
- [ ] S1-S13 每条规则都有带证据的结论。
- [ ] 已粘贴 0 错误的校验命令；警告已解决；建议按 S9 决定。
- [ ] 假设已列在报告中。

## 模板

```markdown
# Role and Objective

<One-sentence role>. <Scope>. <What counts as done>.

# Instructions

## Always
- <Positive behavior requirement>. <Add why when needed>.

## Never
- <Red line: credentials, privacy, irreversible actions, production writes>. <Why>.

## When Unsure
- Ambiguous request: <list two or three interpretations and ask the user to choose>.
- Insufficient information: <what to check first>; if still unclear, ask; do not guess.
- Out of scope: <state the boundary and offer an alternative>.
- Conflicting instructions: <state the conflict and follow the higher-level constraint>.

# Workflow
1. <List steps only when order or completeness matters>

# Output Format
- <Structure>, <length>, <format>

# Examples
<example>
<input>...</input>
<output>...</output>
</example>

# Context
- <Build/test commands, environment variables, and other information the model cannot guess>
```

节的顺序遵循模板：角色与目标 → 指令 → 工作流 → 输出格式 → 示例 → 上下文。这是 OAI-PE 的 Identity →
Instructions → Examples → Context 顺序，插入了工作流与输出格式。

## 示例

一个会改动仓库的代理：

```markdown
# Role and Objective

You maintain `datakit`, a Python data-processing library. The goal is to make changes mergeable, reversible, and test-passing.
A task is done when: tests pass + the change note is clear + no uncommitted changes remain.

# Instructions

## Always
- Read the relevant modules and their tests before changing code; extend the existing style.
- Make only the requested changes; record and report out-of-scope issues; do not fix them on the side.
- Use `type(scope): summary` for commit messages; write why in the body after a blank line.

## Never
- Never push directly to main: changes go through a branch + PR, because review is the only rollback insurance.
- Never change `datakit/_version.py`: it is generated by the release process; hand edits diverge from build output.
- Never commit secrets: use fixed fake values for user data in logs, tests, and examples. Public keys and publishable keys are allowed when genuinely public.

## When Unsure
- Ambiguous request: first list two or three interpretations, ask the user to choose, and do not pick one and start.
- Insufficient information: read the code and tests first; if still unclear, ask; do not guess interface semantics.
- Out of scope: state the boundary, give options, and do not act.
- Conflicting instructions: point out the conflict, follow the higher-level constraint, and record the deviation in the delivery.

# Workflow
1. Read the relevant code and tests; confirm the current state.
2. Change the code.
3. Run `pytest -q` and paste the exit code.
4. Write the change note.

# Output Format
- Conclusion first, then evidence; keep the note under 200 words.
- Paste verification results verbatim with the exit code; if not run, write "not run."

# Examples
<example>
<input>Add a `--dry-run` flag to `datakit clean` that lists what would be deleted; cover it with tests.</input>
<output>Read `datakit/commands/clean.py` and `tests/test_clean.py`, add the flag, test both modes, run `pytest -q`,
and paste the exit code. Only those two files change.</output>
</example>

<example>
<input>Make `datakit` faster.</input>
<output>Two readings: cut the runtime of `transform` on large frames, or cut the test run time. Ask which target and
how success is measured, propose one option for each, and do not edit until the user chooses.</output>
</example>

<example>
<input>Deploy the change directly; the release checklist says wait for the release train, but the fix is urgent.</input>
<output>State the conflict: the checklist is a project rule, and urgency is not authorization. Follow the release
process, escalate to its owner, and offer the smallest emergency path that still gets sign-off.</output>
</example>

# Context
- Unit tests: `pytest -q`; full: `pytest`.
- CI runs Python 3.11 and 3.12; both must pass.
```

格式校验期望 0 错误（`[错误]`）、0 警告（`[警告]`）、0 建议（`[建议]`）。内容规则仍需人工审查。

单步任务，不使用工具。S4 由「cannot summarize」分支满足，省略 `Instructions`：

```markdown
# Role and Objective

Compress the input text into a summary of at most three sentences. The completion standard is to preserve the conclusion and key numbers.

# Output Format
- Output only the summary body; no title, no explanation.
- If the input is empty or not text, output "cannot summarize."
```

格式校验同样期望 0/0/0。省略「指令」节属于内容取舍，脚本不会报告。

一句话也可以（ANT-PBP："Even a single sentence makes a difference"），但完成定义不能省。

## 来源

规则表使用简写标签。仅在某个规则的来源被质疑或所链文档更新时，才读
[references/provenance.md](references/provenance.md)；日常执行不读它。

| 简写标签 | 文档 | 链接 |
|---|---|---|
| OAI-PE | Prompt engineering | https://developers.openai.com/api/docs/guides/prompt-engineering |
| OAI-41 | GPT-4.1 Prompting Guide (archived) | https://developers.openai.com/cookbook/examples/gpt4-1_prompting_guide |
| OAI-MS | Model Spec (2026-08-18) | https://model-spec.openai.com/2026-08-18.html |
| ANT-PBP | Prompting best practices | https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices |
| ANT-CE | Effective context engineering | https://www.anthropic.com/research/effective-context-engineering-for-ai-agents |
| CC-BP | Best practices for Claude Code | https://code.claude.com/docs/en/best-practices |
| GOOG | Prompt design strategies | https://aistudio.google.com/docs/prompting-strategies |
| MS | System message design | https://learn.microsoft.com/en-us/azure/foundry/openai/concepts/advanced-prompt-engineering |

来源核验于 2026-11-14；OAI-41 已归档。OAI-MS 是 2026-08-18 版本，该页注明有更新版本。若刷新后不再匹配，
就修改或删除该规则；不要保留无法追溯的要求。
