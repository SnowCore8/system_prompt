# 规范出处原句

`SKILL.md` 规则表 S1–S13 的核对依据。只在某条规则被质疑、或来源更新后需要复核时读。链接与版本见 `SKILL.md` 的“来源”一节。

引文保留英文原句；省略处用“…”标出，不改写原词。

## S1 角色、范围、完成定义

- OAI-41 §5 General Advice > Prompt Structure：模板首节为 `# Role and Objective`。
- ANT-PBP §General principles > Give Claude a role：“Setting a role in the system prompt focuses Claude's behavior and tone for your use case. Even a single sentence makes a difference…”
- MS §Design checklist > 1. Start with the assistant's job：“State the role and the expected outcome for a typical request.”
- MS §Key concepts > Role and scope：“Define what the assistant is (role) and what it is and isn't allowed to do (scope).”
- “完成定义”是把 expected outcome 推进成可验证判据，属于推导。

## S2 否定式补替代行为或理由

- ANT-PBP §Output and formatting > Control the format of responses：
  “Tell Claude what to do instead of what not to do”；
  “Instead of: ‘Do not use markdown in your response’”；
  “Try: ‘Your response should be composed of smoothly flowing prose paragraphs.’”
- ANT-PBP §General principles > Add context to improve performance：
  “Your response will be read aloud by a text-to-speech engine,
  so never use ellipses since the text-to-speech engine will not know how to pronounce them.”

## S3 强语气只给红线或实测被忽略的单条

- OAI-41 §4 Instruction Following > Recommended Workflow：
  “It's generally not necessary to use all-caps or other incentives like bribes or tips.
  We recommend starting without these, and only reaching for these if necessary for your particular prompt.”
- CC-BP §Configure your environment > Write an effective CLAUDE.md：
  “If Claude keeps skipping one instruction, add emphasis such as ‘IMPORTANT’ to that line alone.
  If you emphasize many lines, none of them stands out.”
- ANT-PBP §Tool use > Tool usage：“The fix is to dial back any aggressive language.”
- 红线优先于普通要求，属推导。

## S4 兜底三种情况

- MS §Design checklist > 4. Add a “when unsure” policy：“Tell the model what to do when: The user's request is ambiguous. The request is out of scope. The model lacks information.”
- MS §How system messages work：“Make the ‘fallback behavior’ explicit (what the assistant does when it lacks information or the request is out of scope).”
- 单步任务只需一个“无法处理”分支，属推导。

## S5 编号不产生优先级

- OAI-MS §Overview > Instructions and levels of authority：Root > System > Developer > User > Guideline。
- OAI-MS §The chain of command > Follow all applicable instructions：“superseded by an instruction in a later message at the same level”。

## S6 输出格式三要素

- MS §Key concepts > Output contract：“Keep the contract small and stable.”
- MS §Design checklist > 3. Specify the output format：“If you need a specific format, specify it plainly and keep it consistent.”
- GOOG §Gemini 3 > Core prompting principles：
  “By default, Gemini 3 models provide direct and efficient answers.
  If you need a more conversational or detailed response, you must explicitly request it in your instructions.”
- “结构、长度、格式”三要素是把 output contract 与 verbosity 要求合并后的判据，属推导。

## S7 示例 3–5 个，边界并进示例

- ANT-PBP §General principles > Use examples effectively：
  “Include 3–5 examples for best results.”；
  “Diverse: Cover edge cases and vary enough that Claude doesn't pick up unintended patterns.”；
  “Structured: Wrap examples in `<example>` tags…”
- ANT-CE §The anatomy of effective context：
  “teams will often stuff a laundry list of edge cases into a prompt…
  We do not recommend this. Instead, we recommend working to curate a set of diverse, canonical examples…”

## S8 Context 准入

CC-BP §Write an effective CLAUDE.md（Include/Exclude 表）：

- “Bash commands Claude can't guess” / “Anything Claude can figure out by reading code”
- “Testing instructions and preferred test runners” / “Detailed API documentation (link to docs instead)”
- “Architectural decisions specific to your project” / “Long explanations or tutorials”

## S9 逐行删减

CC-BP §Write an effective CLAUDE.md：

- “Keep it concise. For each line, ask: ‘Would removing this cause Claude to make mistakes?’ If not, cut it.”
- “CLAUDE.md is loaded every session, so only include things that apply broadly.”
- “For domain knowledge or workflows that are only relevant sometimes, use skills instead.”

CC-BP §Avoid common failure patterns：“Bloated CLAUDE.md files cause Claude to ignore your actual instructions!”

## S10 不写未确认的接口

- 推导，依据 S4。
- 佐证 ANT-PBP §Agentic systems > Minimizing hallucinations in agentic coding：“Never speculate about code you have not opened.”

## S11 长资料不进指令文件

- ANT-CE §Context retrieval and agentic search：“agents built with the ‘just in time’ approach maintain lightweight identifiers (file paths, stored queries, web links, etc.)”
- CC-BP Include/Exclude 表：“Detailed API documentation (link to docs instead)”。
- “单行不承载成段材料”为工程约束。

## S12 格式检查

- 工程约束，无外部出处。Markdown 可解析性与可维护性要求。

## S13 按模型分叉

- OAI-PE §Choosing a model：“GPT models are fast, cost-efficient, and highly intelligent, but benefit from more explicit instructions around how to accomplish tasks.”
- OAI-PE §Prompting reasoning models：
  “Generally speaking, reasoning models will provide better results on tasks with only high-level guidance.
  This differs from GPT models, which benefit from very precise instructions.”
- OAI-41 引言：“GPT-4.1 is trained to follow instructions more closely and more literally than its predecessors…”
