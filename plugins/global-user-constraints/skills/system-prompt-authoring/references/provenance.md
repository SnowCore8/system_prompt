# Source Quotes

Evidence for the S1–S13 rule table in `SKILL.md`. Read only when a rule's source is questioned or a source has been updated. Links and versions are in the "Sources" section of `SKILL.md`.

Quotes keep the original English; omissions are marked with "…"; do not rewrite the original words.

## S1 Role, scope, and completion definition

- OAI-41 §5 General Advice > Prompt Structure: the first section of the template is `# Role and Objective`.
- ANT-PBP §General principles > Give Claude a role: "Setting a role in the system prompt focuses Claude's behavior and tone for your use case. Even a single sentence makes a difference…"
- MS §Design checklist > 1. Start with the assistant's job: "State the role and the expected outcome for a typical request."
- MS §Key concepts > Role and scope: "Define what the assistant is (role) and what it is and isn't allowed to do (scope)."
- "Completion definition" turns the expected outcome into a verifiable criterion; this is derived.

## S2 Add an alternative behavior or reason to a negative rule

- ANT-PBP §Output and formatting > Control the format of responses:
  "Tell Claude what to do instead of what not to do";
  "Instead of: 'Do not use markdown in your response'";
  "Try: 'Your response should be composed of smoothly flowing prose paragraphs.'"
- ANT-PBP §General principles > Add context to improve performance:
  "Your response will be read aloud by a text-to-speech engine,
  so never use ellipses since the text-to-speech engine will not know how to pronounce them."

## S3 Use strong emphasis only for red lines or a single observed failure

- OAI-41 §4 Instruction Following > Recommended Workflow:
  "It's generally not necessary to use all-caps or other incentives like bribes or tips.
  We recommend starting without these, and only reaching for these if necessary for your particular prompt."
- CC-BP §Configure your environment > Write an effective CLAUDE.md:
  "If Claude keeps skipping one instruction, add emphasis such as 'IMPORTANT' to that line alone.
  If you emphasize many lines, none of them stands out."
- ANT-PBP §Tool use > Tool usage: "The fix is to dial back any aggressive language."
- Red lines outrank ordinary requirements; this is derived.

## S4 Fallbacks for three situations

- MS §Design checklist > 4. Add a "when unsure" policy: "Tell the model what to do when: The user's request is ambiguous. The request is out of scope. The model lacks information."
- MS §How system messages work: "Make the 'fallback behavior' explicit (what the assistant does when it lacks information or the request is out of scope)."
- A single-step task needs only one "cannot process" branch; this is derived.

## S5 Numbering does not create priority

- OAI-MS §Overview > Instructions and levels of authority: Root > System > Developer > User > Guideline.
- OAI-MS §The chain of command > Follow all applicable instructions: "superseded by an instruction in a later message at the same level".

## S6 The three output-format elements

- MS §Key concepts > Output contract: "Keep the contract small and stable."
- MS §Design checklist > 3. Specify the output format: "If you need a specific format, specify it plainly and keep it consistent."
- GOOG §Gemini 3 > Core prompting principles:
  "By default, Gemini 3 models provide direct and efficient answers.
  If you need a more conversational or detailed response, you must explicitly request it in your instructions."
- "Structure, length, and format" combine the output contract and verbosity requirements; this is derived.

## S7 Three to five examples, with edge cases folded in

- ANT-PBP §General principles > Use examples effectively:
  "Include 3–5 examples for best results.";
  "Diverse: Cover edge cases and vary enough that Claude doesn't pick up unintended patterns.";
  "Structured: Wrap examples in `<example>` tags…"
- ANT-CE §The anatomy of effective context:
  "teams will often stuff a laundry list of edge cases into a prompt…
  We do not recommend this. Instead, we recommend working to curate a set of diverse, canonical examples…"

## S8 Context admission

CC-BP §Write an effective CLAUDE.md (Include/Exclude table):

- "Bash commands Claude can't guess" / "Anything Claude can figure out by reading code"
- "Testing instructions and preferred test runners" / "Detailed API documentation (link to docs instead)"
- "Architectural decisions specific to your project" / "Long explanations or tutorials"
- Rows 2, 4, and 6 of the SKILL table (style, repository conventions, environment variables) are derived engineering guidance, not quotations from CC-BP.

## S9 Delete line by line

CC-BP §Write an effective CLAUDE.md:

- "Keep it concise. For each line, ask: 'Would removing this cause Claude to make mistakes?' If not, cut it."
- "CLAUDE.md is loaded every session, so only include things that apply broadly."
- "For domain knowledge or workflows that are only relevant sometimes, use skills instead."

CC-BP §Avoid common failure patterns: "Bloated CLAUDE.md files cause Claude to ignore your actual instructions!"

## S10 Do not write unconfirmed interfaces

- Derived, based on S4.
- Supporting quote: ANT-PBP §Agentic systems > Minimizing hallucinations in agentic coding: "Never speculate about code you have not opened."

## S11 Long material does not belong in instruction files

- ANT-CE §Context retrieval and agentic search: "agents built with the 'just in time' approach maintain lightweight identifiers (file paths, stored queries, web links, etc.)"
- CC-BP Include/Exclude table: "Detailed API documentation (link to docs instead)".
- "One line should not carry a block of material" is an engineering constraint.

## S12 Format checks

- Engineering constraint; no external source. Markdown parseability and maintainability requirements.

## S13 Branch by model

- OAI-PE §Choosing a model: "GPT models are fast, cost-efficient, and highly intelligent, but benefit from more explicit instructions around how to accomplish tasks."
- OAI-PE §Prompting reasoning models:
  "Generally speaking, reasoning models will provide better results on tasks with only high-level guidance.
  This differs from GPT models, which benefit from very precise instructions."
- OAI-41 introduction: "GPT-4.1 is trained to follow instructions more closely and more literally than its predecessors…"
