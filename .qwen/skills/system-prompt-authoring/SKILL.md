---
name: system-prompt-authoring
description: 起草、审计或重构编码代理的持久指令文件（AGENTS.md、CLAUDE.md、QWEN.md）。当用户要新建这类文件、判断现有文件哪些行该删该改，或要求把规则追溯到厂商文档时使用。机检脚本只验证 Markdown 格式，内容规则由人工判断。
argument-hint: '<target-file>'
---

# 起草或审计 system prompt

你为编码代理起草和审计持久指令文件。交付的文件是可直接加载的 Markdown：内容规则逐条人工核对，Markdown 格式由机检脚本（`script/check.py`）检查通过。

## 流程

1. 确认目标文件和任务类型：新建还是审计。路径或意图不清楚就问，不要猜。
2. 按“五个输入”收集信息。仓库里能查到的不问用户；确实拿不到的用默认写法，并在报告里说明这是假设。
3. 新建按“模板”填，删掉任务用不到的节；审计按“删行判据”逐行处理，同一约束只留一处。
4. 人工核对内容规则 S1–S13。脚本不判断这些规则；机检通过不代表内容合格。
5. 跑格式机检，修掉 `[错误]`；`[警告]` 逐条写下结论，“看着没问题”不算结论。
6. 报告按固定顺序写：文件路径；机检命令与输出原文；S1–S13 逐条结论；未解决项与假设。还有未解释的项时，不要说完成。

## 五个输入

| 输入 | 用于 | 拿不到时 |
|---|---|---|
| 角色与范围 | Role and Objective | 问：这个 agent 负责什么，什么算做完 |
| 任务与工具 | Instructions、Workflow | 问；仓库配置里能读到就先读 |
| 输出要求 | Output Format | 问：结构、长度、是否要贴命令输出 |
| 安全边界 | 红线、绝不 | 问：哪些操作要先确认，哪些绝对不能做 |
| 目标模型 | S13 的粒度取舍 | 按 S13 默认写法；不因模型未知放宽红线 |

构建与测试命令、目录约定、语言版本，从 `README`、`package.json`、`pyproject.toml`、`Makefile`、CI 配置里读，写进 `Context`。

## 内容规则 S1–S13

判定列说明由谁检查：机检只覆盖 S12 中可机械判定的格式项，其余由你人工判断。

| # | 要求 | 判定 | 出处 |
|---|---|---|---|
| S1 | 写清角色、范围、完成定义 | 人工 | OAI-41 §Prompt Structure；ANT-PBP §Give Claude a role；MS §Design checklist 1；§Role and scope |
| S2 | 每条禁止配替代行为或理由；红线可保留禁止式，但必须写理由 | 人工 | ANT-PBP §Control the format of responses；§Add context |
| S3 | 默认平实祈使句；强调只给红线，或实测被忽略的那一条 | 人工 | OAI-41 §Recommended Workflow；CC-BP §Write an effective CLAUDE.md；ANT-PBP §Tool usage |
| S4 | 请求模糊、超出范围、信息不足各给一个动作；单步任务至少给“无法处理” | 人工 | MS §Design checklist 4；§How system messages work |
| S5 | 不用编号声明优先级；不留无条件的对立要求 | 人工 | OAI-MS §Instructions and levels of authority |
| S6 | 输出格式写明结构、长度、格式 | 人工 | MS §Output contract；§Design checklist 3；GOOG §Core prompting principles |
| S7 | 示例 3–5 个，每个演示一条规则没写到的行为；边界情况并进示例。规则超过 50 条且无示例时才提示 | 人工 | ANT-PBP §Use examples effectively；ANT-CE §The anatomy of effective context |
| S8 | `Context` 只放模型无法从代码推导的信息 | 人工 | CC-BP §Write an effective CLAUDE.md（Include/Exclude 表） |
| S9 | 删掉答“不会做错”的行；偶尔才用的细则移进 skill | 人工 | CC-BP §Write an effective CLAUDE.md；§Avoid common failure patterns |
| S10 | 不写没确认存在的工具、命令、配置项 | 人工 | 推导；佐证 ANT-PBP §Minimizing hallucinations |
| S11 | 长文档不进指令文件；一段话不压在一行里 | 人工 | ANT-CE §Context retrieval；CC-BP Include/Exclude；单行限制为工程约束 |
| S12 | 无占位标记；无行尾空白与制表符；正文单行不超过 200 字；代码围栏成对；文件以换行结尾 | 人工 + 机检（占位标记人工） | 工程约束 |
| S13 | GPT 系给明确指令，推理模型只给目标与约束；模型未知时用平实祈使句 | 人工 | OAI-PE §Choosing a model；§Prompting reasoning models |

以下几条是推导，不要当成厂商原话：完成定义（S1）、输出格式三要素（S6）、示例合并规则（S7）、单步任务豁免（S4）、S10。

S2 与 S3 合用：红线段可以用“绝不”，但仍要写理由。标题式加粗只做导航，不算强调；S3 说的强调是整句加强语气。S12 中可由机器判定的格式项以机检结果为准，占位标记等内容项人工核对。

S5 反对把编号当作隐含优先级。文件可以显式声明同节排序（如“靠前者优先”）；有这种声明时按声明执行，没有时不要把编号当依据。

## 来源冲突时怎么选

- **强调**：默认平实祈使句。OAI-41 说全大写和贿赂式激励“generally not necessary”；CC-BP 说强调的行多了，没有一行突出；ANT-PBP 说为老模型写的强措辞要收回。只给红线，或实测被跳过的那一条加强语气，并写明是哪次观察。
- **粒度**：先写目标与约束。顺序或完整性关键时才列步骤，并说明漏掉会怎样（ANT-PBP：“Prefer general instructions over prescriptive steps.”）。非推理模型需要显式规划时，按 OAI-41 加 `Reasoning Steps`。
- **篇幅**：没有行数上限，按 S9 判断。
- **禁止式**：红线保留并写理由，其余写替代行为。
- **优先级**：编号本身不产生优先级，不要写“编号小的赢”。文件可以显式声明排序，有声明时按声明执行。OAI-MS 的层级是 root > system > developer > user > guideline，同级后消息覆盖前消息。
- **兜底**：写明信息不足时怎么做。只写“先调工具”，这个分支就没有定义。

## 删行判据

逐行问（CC-BP）：

> Would removing this cause Claude to make mistakes?

答“不会”就删。判据是高信号，不是字数（ANT-CE：“minimal does not necessarily mean short”）。

`Context` 只放左列的内容：

| 放 | 不放 |
|---|---|
| 模型猜不到的 shell 命令 | 读代码就能知道的事 |
| 与语言默认不同的风格要求 | 语言通用规范 |
| 测试怎么跑、用哪个运行器（runner） | 详细 API 文档（给链接） |
| 仓库约定（分支命名、提交格式） | 频繁变动的信息 |
| 项目特有的架构决策 | 逐文件说明 |
| 必需的环境变量 | “写干净的代码”这类自明要求 |

示例：3–5 个，每个演示一条规则没写到的行为，边界情况并进示例，不另列清单（ANT-CE 反对清单式堆砌，laundry list）。规则已经写清的行为不配示例。

## 各节怎么写

- **Role and Objective**：角色、范围、完成定义，三件事一到两句写完。
- **Instructions**：`始终` 写要做什么；`绝不` 只放红线，每条带理由；`不确定时` 覆盖 S4。正文用平实祈使句。
- **Workflow**：把步骤调换顺序会改变结果才写，并说明跳过某步会怎样。
- **Output Format**：结构、长度、格式都写。不给长度，模型就按自己的默认发挥；GOOG 说 Gemini 3 默认简短，要详细必须显式要求。
- **Examples**：每个用 `<example>` 包住，避免被读成指令。
- **Context**：按上面的表取舍；长文档给链接或路径，不贴进来。

`Reasoning Steps` 只给需要显式规划的非推理模型；`Final instructions` 是长提示末尾的可选复述。用不到就删。

## 机检

脚本只检查 Markdown 语法、排版与链接有效性；不读正文语义、不判断规则是否合理、不追溯来源。退出码：0 无错误，1 有错误，2 参数、依赖或文件问题。

### 用法

路径以本 skill 所在目录为基准，下面的 `<skill-dir>` 换成实际路径：

```bash
python3 <skill-dir>/script/check.py AGENTS.md
```

放进 CI 时加 `--strict`，警告也算失败，退出码 1：

```bash
python3 <skill-dir>/script/check.py --strict AGENTS.md
```

脚本依赖 `markdown-it-py`；缺依赖时直接报错并给出安装命令，不会自动安装。脚本自身用例用标准库 unittest：

```bash
python3 -m unittest discover -s <skill-dir>/script
```

### 规则

输出分三级：

| 级别 | 含义 | 影响退出码 |
|---|---|---|
| 错误 | 文件结构损坏 | 是 |
| 警告 | 格式有问题，需要修 | 否 |
| 建议 | 可改进项 | 否 |

每条给出位置（`L行号` 或 `全文`）、规则编号、原因、建议改法。

按结构、标题、列表、表格、链接、行内与版面分组。

| 规则号 | 级别 | 判什么 |
|---|---|---|
| MD-FENCE | 错误 | 围栏未闭合 |
| MD-FINAL-NEWLINE | 错误 | 文件末尾缺少换行 |
| MD-HTML-COMMENT | 错误 | HTML 注释未闭合，会吞掉文件剩余部分；行内未闭合报同一规则号 |
| MD-HTML-BLOCK | 错误 | `<script>`、`<style>`、`<pre>`、`<textarea>` 块未闭合 |
| MD-HEAD-SPACE | 警告 | `#` 后缺空格，整行按段落渲染 |
| MD-HEAD-START | 警告 | 首个标题不是 h1 |
| MD-HEAD-JUMP | 警告 | 标题层级跳跃 |
| MD-HEAD-EMPTY | 警告 | 标题没有文字 |
| MD-HEAD-DUP | 警告 | 标题重名（折叠大小写与空白后比较） |
| MD-LIST-SPACE | 警告 | 列表标记后缺空格 |
| MD-LIST-MARKER | 警告 | 同一段列表混用 `-`、`*`、`+` |
| MD-LIST-START | 警告 | 有序列表不是从 1 开始编号 |
| MD-LIST-EMPTY | 警告 | 列表项没有内容 |
| MD-LIST-INDENT | 警告 | 同级缩进不一致，或缩进过深丢失列表结构 |
| MD-TABLE-COLS | 警告 | 表格行之间列数不一致 |
| MD-TABLE-BROKEN | 警告 | 连续竖线行没被解析成表格（分隔行缺列或少横线） |
| MD-LINK-REF | 警告 | `[文字][标签]` 的标签没有定义 |
| MD-LINK-DEF-DUP | 警告 | 同一标签定义了两次，后者不生效 |
| MD-LINK-DEF-UNUSED | 建议 | 定义了却没人引用的标签 |
| MD-LINK-EMPTY | 警告 | 链接或图片缺文字、缺地址 |
| MD-LINK-TARGET | 警告 | 链接或图片的相对路径在仓库里不存在 |
| MD-LINK-SYNTAX | 警告 | `[文字](` 没被解析成链接 |
| MD-ANCHOR | 警告 | 页内锚点指向不存在的标题 |
| MD-INLINE-CODE | 警告 | 反引号没配对 |
| MD-EMPHASIS | 警告 | `**`、`__` 或 `~~` 没配对 |
| MD-INLINE-HTML | 警告 | 已知名 HTML 标签只开未关 |
| MD-BLANK-RUN | 警告 | 连续多个空行 |
| MD-LINE-LEN | 警告 | 正文单行超过 200 字；表格、代码、URL 与文件头元数据（front matter）除外 |
| MD-TRAILING-WS | 警告 | 行尾空白 |
| MD-TAB | 警告 | 正文含制表符 |

### 判定边界

这些判定都基于 CommonMark 解析结果，不是逐行正则：

- 结构检查剔除围栏、缩进代码块、HTML 块与文件头元数据（front matter）。`<example>` 不再单列，按普通 HTML 处理。
- 反引号与强调可以跨行配对，脚本按“解析器没消化掉的标记”判断，跨行合法配对不报。
- 链接定义从解析器的引用表读，地址写在下一行、定义写在列表项里都能识别。
- 表格分隔行写错时整张表会退化成段落，`MD-TABLE-BROKEN` 专门抓这种情况。
- 外链、`mailto:` 与锚点不查本地存在性；锚点按 GitHub 规则转成锚点标识（slug）后比对。
- 行内标签只看解析器产出的 `html_inline`，自动链接（autolink）与 `<占位符>` 不算未闭合。

### 不查项

以下三类刻意不查，因为机械判定只会产出噪声：

| 不查的写法 | 理由 |
|---|---|
| 单个 `*` 或 `_` 未配对 | `*.py`、`src/*.ts`、`2*3`、`**/*.md` 用的是同一个字符，区分要靠语义 |
| setext 标题（`===`、`---` 下划线式） | 合法语法，正常写标题就会被报出来 |
| 表格空表头单元格 `\| a \|  \|` | 合法且常用 |

`MD-INLINE-HTML` 有一处残留误报：正文里讲语法时写出单个 `<div>`，与真的漏写闭合标签无法区分。这类内容写进反引号或代码块即可跳过。

### 读输出

- `[错误]`：修掉并重跑，直到 0 项、退出码 0。
- `[警告]`：逐条写结论；结构类误判要说明是标题措辞问题，不是内容缺失。
- `[建议]`：按 S9 判断改不改，不强制。

## 反模式

| 反模式 | 改法 |
|---|---|
| 规则堆到要通读才能找到一条 | 按 S9 删；细则移进 skill |
| 把编号当隐含优先级 | 改成显式排序声明，或分节表达 |
| 通篇禁止，不给替代行为 | 按 S2 补替代行为或理由 |
| 红线和平常要求同用“绝不” | 按 S3 只给红线加绝对措辞 |
| 每条规则都加粗 | 加粗只做导航；整句强调留给红线（S3） |
| 只写“先调工具” | 按 S4 补信息不足分支 |
| 写死逐步流程 | 写目标与约束，只在顺序关键时留步骤（S13） |
| 贴 API 文档 | 给链接（S11） |
| 写了不存在的工具或配置项 | 只写确认过的接口（S10） |
| 把边界情况堆成示例清单 | 并进 3–5 个示例（S7） |

## 模板

```markdown
# Role and Objective
<角色一句话>。<负责范围>。<什么算做完>。

# Instructions

## 始终
- <正向表述的行为要求>。<必要时补一句为什么>。

## 绝不
- <红线：凭证、隐私、不可逆操作、生产写入>。<为什么>。

## 不确定时
- 请求模糊：<列出两三种理解，问用户选哪个>。
- 信息不足：<先查什么>；查不到再问，不要猜。
- 超出范围：<说明边界，给替代方案>。
- 指令冲突：<指出冲突，按更高层约束执行>。

# Workflow
1. <仅在顺序或完整性重要时列步骤>

# Output Format
- <结构>、<长度>、<格式>

# Examples
<example>
<input>...</input>
<output>...</output>
</example>

# Context
- <构建/测试命令、环境变量等模型猜不到的信息>
```

节序按 OAI-PE 的 Identity → Instructions → Examples → Context 和 OAI-41 的模板。

## 示例

会改动仓库的 agent：

```markdown
# Role and Objective
你维护 `datakit` 这个 Python 数据处理库。目标是让改动可合并、可回滚、测试通过。
一个任务算做完：测试通过 + 变更说明写清 + 没有遗留未提交改动。

# Instructions

## 始终
- 改代码前先读相关模块和覆盖它的测试，按现有写法扩展。
- 只做需求要求的改动；发现范围外的问题记录并报告，不顺手改。
- 提交信息用 `type(scope): 摘要`，空行后写为什么改。

## 绝不
- 绝不直接推 main：改动走分支 + PR，因为评审是唯一的回滚保险。
- 绝不改 `datakit/_version.py`：它由发版流程生成，手改会和构建结果不一致。
- 绝不提交凭证：日志、测试、示例里的用户数据用固定假值。

## 不确定时
- 请求模糊：先按最可能的解释列出两三种理解，问用户选哪个，不自行选定后动手。
- 信息不足：先读代码和测试；仍不确定就问，不猜接口语义。
- 超出范围：说明边界，给出可选方案，不动手。
- 指令冲突：指出冲突点，按本文件的约束执行，并在交付里记录偏离。

# Workflow
1. 读相关代码与测试，确认现状。
2. 改代码。
3. 跑 `pytest -q`，贴出退出码。
4. 写变更说明。

# Output Format
- 先给结论，再给依据。
- 验证结果原样贴出，含退出码；没跑就写“没跑”。

# Context
- 单测：`pytest -q`；全量：`pytest`。
- CI 跑 Python 3.11 与 3.12，两版都要过。
```

机检预期是 `[错误]` 0、`[警告]` 0、`[建议]` 0。内容规则仍要人工核对。

单步任务，不调用工具。S4 由“无法摘要”分支满足，`Instructions` 省略：

```markdown
# Role and Objective
你把输入文本压缩成不超过三句的中文摘要。做完的标准是保留结论与关键数字。

# Output Format
- 只输出摘要正文，不加标题、不加解释。
- 输入为空或不是文本时，输出“无法摘要”。
```

机检同样预期 0/0/0。缺少指令节是内容层的取舍，脚本不会报。

一句话也能起作用（ANT-PBP：“Even a single sentence makes a difference”），但完成定义不能省。

## 来源

短标签用在规则表里。只在某条规则的来源被质疑、或链接文档更新后才读 `references/provenance.md`；正常执行不读。

| 短标签 | 文档 | 链接 |
|---|---|---|
| OAI-PE | Prompt engineering | https://developers.openai.com/api/docs/guides/prompt-engineering |
| OAI-41 | GPT-4.1 Prompting Guide | https://developers.openai.com/cookbook/examples/gpt4-1_prompting_guide |
| OAI-MS | Model Spec（2026-08-18） | https://model-spec.openai.com/2026-08-18.html |
| ANT-PBP | Prompting best practices | https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices |
| ANT-CE | Effective context engineering | https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents |
| CC-BP | Best practices for Claude Code | https://code.claude.com/docs/en/best-practices |
| GOOG | Prompt design strategies | https://ai.google.dev/gemini-api/docs/prompting-strategies |
| MS | System message design | https://learn.microsoft.com/en-us/azure/foundry/openai/concepts/advanced-prompt-engineering |

OAI-MS 引的是 2026-08-18 版，页面已提示有更新版本。重抓后对不上，就改规则或删规则，不留无法追溯的要求。
