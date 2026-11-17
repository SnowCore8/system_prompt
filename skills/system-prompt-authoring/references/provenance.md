# 来源引文

`SKILL.md` 中 S1-S13 规则表的证据。仅在某个规则的来源被质疑或某个来源已更新时阅读。链接与版本见
`SKILL.md` 的「参考资料」一节。

引文保留英文原文；省略处用「...」标出。来源核验于 2026-11-14。CC-BP 引用版本冻结于 2026-11-12
（不再跟随外部页面更新）；若 2026-11-14 核验时引文措辞已不存在，则由下面的转述替代，删除日期未知。
引文标点统一为 ASCII。

## S1 角色、范围与完成定义

- OAI-41 §5 General Advice > Prompt Structure：模板的第一节是 `# Role and Objective`。
- ANT-PBP §General principles > Give Claude a role:
  "Setting a role in the system prompt focuses Claude's behavior
  and tone for your use case. Even a single sentence makes a difference..."
- MS §Design checklist > 1. Start with the assistant's job:
  "State the role and the expected outcome for a typical
  request."
- MS §Key concepts > Role and scope:
  "Define what the assistant is (role) and what it is and isn't allowed to do
  (scope)."
- 「完成定义」把预期结果转化为可验证的标准；这是推导内容。

## S2 为禁止性规则补充替代行为或理由

- ANT-PBP §Output and formatting > Control the format of responses:
  "Tell Claude what to do instead of what not to do";
  "Instead of: 'Do not use markdown in your response'";
  "Try: 'Your response should be composed of smoothly flowing prose paragraphs.'"
- ANT-PBP §General principles > Add context to improve performance:
  "Your response will be read aloud by a text-to-speech engine,
  so never use ellipses since the text-to-speech engine will not know how to pronounce them."

## S3 仅在红线处使用强强调

- OAI-41 §4 Instruction Following > Recommended Workflow:
  "It's generally not necessary to use all-caps or other incentives like bribes or tips.
  We recommend starting without these, and only reaching for these if necessary for your
  particular prompt."
- CC-BP (2026-11-14)：引用版本冻结于 2026-11-12；2026-11-14 核验时引文措辞已不存在，删除日期未知。该规则作为
  推导性指导保留。当前指南指出：旧模型有时需要这种强调，当前模型能遵循平实表述，堆砌强调多半会让它们过度
  套用规则。
- ANT-PBP §Tool use > Tool usage:
  "The fix is to dial back any aggressive language."
- 红线的效力高于普通要求；这是推导内容。

## S4 三种情形的兜底

- MS §Design checklist > 4. Add a "when unsure" policy:
  "Tell the model what to do when: The user's request is
  ambiguous. The request is out of scope. The model lacks information."
- MS §How system messages work:
  "Make the 'fallback behavior' explicit (what the assistant does when it lacks
  information or the request is out of scope)."
- 单步任务只需要一个「cannot process」分支；这是推导内容。

## S5 编号不产生优先级

- OAI-MS §Overview > Instructions and levels of authority:
  Root > System > Developer > User > Guideline.
- OAI-MS §The chain of command > Follow all applicable instructions:
  "superseded by an instruction in a later message at the same level".

## S6 输出格式的三个要素

- MS §Key concepts > Output contract:
  "Keep the contract small and stable."
- MS §Design checklist > 3. Specify the output format:
  "If you need a specific format, specify it plainly and keep it consistent."
- GOOG §Gemini 3 > Core prompting principles:
  "By default, Gemini 3 models provide direct and efficient answers.
  If you need a more conversational or detailed response, you must explicitly request it in your
  instructions."
- 「结构、长度与格式」合并了输出契约与冗长度要求；这是推导内容。

## S7 三到五个示例，并并入边界情况

- ANT-PBP §General principles > Use examples effectively:
  "Include 3-5 examples for best results.";
  "Diverse: Cover edge cases and vary enough that Claude doesn't pick up unintended patterns.";
  "Structured: Wrap examples in `<example>` tags..."
- ANT-CE §The anatomy of effective context:
  "teams will often stuff a laundry list of edge cases into a prompt...
  We do not recommend this. Instead, we recommend working to curate a set of diverse, canonical
  examples..."
- 简短单一用途的提示词可以省略示例；这是推导内容。

## S8 上下文准入

- CC-BP (2026-11-14)：引用版本冻结于 2026-11-12；2026-11-14 核验时所引的 Include/Exclude 各行已不存在，
  删除日期未知。该规则作为推导性指导保留。当前指南指出：`CLAUDE.md` 只保留 Claude 无法从代码推断的内容时
  效果最好：准确的校验命令、有误导性的代码模式、不在仓库中的决策，以及已经纠正过两次的内容。
- `SKILL.md` 表中的第 2、4、6 行（风格、仓库约定、环境变量）是推导出的工程指导，并非 CC-BP 的引文。

## S9 逐行删除

- CC-BP (2026-11-14)：引用版本冻结于 2026-11-12；2026-11-14 核验时所引的删除检验与文件臃肿警告已不存在，
  删除日期未知。该规则作为推导性指导保留。当前指南指出：`CLAUDE.md` 每个会话都会加载，每一行都会在每个
  任务上占用注意力，团队流程与知识应放在 skill 中。
- 逐行检验由此推导：删掉某行若不会阻止具体错误，就删除该行。

## S10 不写未确认的接口

- 推导内容，基于 S4。
- 支持性引文：ANT-PBP §Agentic systems > Minimizing hallucinations in agentic coding:
  "Never speculate about code you have not opened."

## S11 长材料不属于指令文件

- ANT-CE §Context retrieval and agentic search:
  "agents built with the 'just in time' approach maintain lightweight
  identifiers (file paths, stored queries, web links, etc.)"
- CC-BP (2026-11-14)：引用版本冻结于 2026-11-12；2026-11-14 核验时所引的 Include/Exclude 措辞已不存在，删除
  日期未知。该规则作为推导性指导保留。当前指南指出：只写 Claude 无法通过阅读仓库找到的内容。
- 「一行不应承载整块材料」是工程约束。

## S12 格式校验

- 工程约束；没有外部来源。Markdown 可解析性与可维护性要求。

## S13 按模型分支

- OAI-PE §Choosing a model:
  "GPT models are fast, cost-efficient, and highly intelligent, but benefit from more
  explicit instructions around how to accomplish tasks."
- OAI-PE §Prompting reasoning models:
  "Generally speaking, reasoning models will provide better results on tasks with only high-level
  guidance. This differs from GPT models, which benefit from very precise instructions."
- OAI-41 introduction:
  "GPT-4.1 is trained to follow instructions more closely and more literally than its
  predecessors..."
