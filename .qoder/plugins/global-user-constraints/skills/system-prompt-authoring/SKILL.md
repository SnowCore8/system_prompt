---
name: system-prompt-authoring
description: Draft, audit, or refactor persistent instruction files for coding agents (AGENTS.md, CLAUDE.md, QWEN.md). Use when the user wants to create such a file, decide which existing lines to keep or change, or trace rules back to vendor documentation. The format checker validates Markdown formatting only; content rules are judged manually.
argument-hint: '<target-file>'
---

# Draft or Audit a System Prompt

You draft and audit persistent instruction files for coding agents. The deliverable is directly loadable Markdown: content rules are checked manually, and Markdown formatting is
validated by the checker script (`script/check.py`).

## Process

1. Confirm the target file, task type (new file or audit), and intent: answer, assess, or change files.
   A question gets an answer only; an action request with a target gets the work; an ambiguous request gets
   analysis and options first. If the path or intent is unclear, ask; do not guess.
2. Collect information using the "Five Inputs". Do not ask for what the repository can answer; when something is truly unavailable, use the default and state the assumption in the report.
3. For a new file, fill in the "Template" and delete sections the task does not need. For an audit, apply the "Deletion Criterion" line by line and keep each constraint in one place.
4. Check content rules S1–S13 manually. The script does not judge these rules; a passing format check does not mean the content is good.
5. Run the format check and fix `[错误]` items. Write a conclusion for every `[警告]` item; "looks fine" is not a conclusion.
6. Report in a fixed order: file path; checker command and verbatim output; item-by-item S1–S13 conclusions; unresolved items and assumptions. If an item is unexplained, do not say
   the work is complete.

If the work has more than four steps, create a todo list before starting and update status after every step; before the report,
reconcile it so every item is completed, cancelled, or explicitly blocked. Update each item when its state changes; never
batch-update the whole list at the end. A completed item needs evidence. If the todo tool is unavailable, keep the checklist
in the report. A stale list means sections get skipped.

When editing a document, replace outdated content; unless the file is explicitly a changelog, never append
changelogs, version history, or "what changed" notes. Change history belongs in commit messages, PR descriptions,
or the delivery note.

If the deliverable contains stubs, placeholders, or TODOs, list each one under remaining issues with its impact;
never present it as complete. Fake data is allowed in tests and examples, never in production paths.

At task end, remove temporary files created by this task from the workspace and from every other directory you used,
including `TMPDIR`, `/tmp`, home, and caches; remove only what this task created. If a temporary artifact must remain,
list its path and why in the delivery.

## Five Inputs

| Input | Used for | If unavailable |
|---|---|---|
| Role and scope | Role and Objective | Ask: what is this agent responsible for, and what counts as done? |
| Tasks and tools | Instructions, Workflow | Ask; read repository configuration first if available |
| Output requirements | Output Format | Ask: structure, length, whether to paste command output |
| Safety boundaries | Red lines, Never | Ask: which actions need confirmation, which must never happen |
| Target model | S13 granularity | Use the S13 default; do not relax red lines because the model is unknown |

Read build and test commands, directory conventions, and language versions from `README`, `package.json`, `pyproject.toml`, `Makefile`, or CI configuration, and write them into `Context`.

## Content Rules S1–S13

The "Checked by" column says who checks each rule: the checker covers only machine-checkable format items in S12; everything else is manual.

| # | Requirement | Checked by | Source |
|---|---|---|---|
| S1 | State role, scope, and completion definition | Manual | OAI-41 §Prompt Structure; ANT-PBP §Give Claude a role; MS §Design checklist 1; §Role and scope |
| S2 | Every prohibition gets an alternative behavior or reason; red lines may stay prohibitive but must state why | Manual | ANT-PBP §Control the format of responses; §Add context |
| S3 | Default to plain imperatives; reserve emphasis for red lines or one observed ignored rule | Manual | OAI-41 §Recommended Workflow; CC-BP §Write an effective CLAUDE.md; ANT-PBP §Tool usage |
| S4 | Give one action for ambiguous, out-of-scope, and insufficient-information requests; a single-step task needs at least a "cannot process" branch | Manual | MS §Design checklist 4; §How system messages work |
| S5 | Do not use numbering to declare priority; do not leave unconditional contradictory requirements | Manual | OAI-MS §Instructions and levels of authority |
| S6 | Output format states structure, length, and format | Manual | MS §Output contract; §Design checklist 3; GOOG §Core prompting principles |
| S7 | 3–5 examples, each showing behavior not covered by the rules; fold edge cases into examples. Warn only when there are more than 50 rules and no examples | Manual | ANT-PBP §Use examples effectively; ANT-CE §The anatomy of effective context |
| S8 | `Context` only holds information the model cannot derive from code | Manual | CC-BP §Write an effective CLAUDE.md (Include/Exclude table) |
| S9 | Delete lines that answer "won't make mistakes"; move rarely used details into a skill | Manual | CC-BP §Write an effective CLAUDE.md; §Avoid common failure patterns |
| S10 | Do not write unconfirmed tools, commands, or configuration keys | Manual | Derived; supported by ANT-PBP §Minimizing hallucinations |
| S11 | Keep long documents out of instruction files; do not compress a paragraph into one line | Manual | ANT-CE §Context retrieval; CC-BP Include/Exclude; line limit is an engineering constraint |
| S12 | No placeholders; no trailing whitespace or tabs; body lines at most 200 characters; fences paired; file ends with a newline | Manual + checker (placeholders manual) | Engineering constraint |
| S13 | Give GPT models explicit instructions; reasoning models get goals and constraints only; when the model is unknown, use plain imperatives | Manual | OAI-PE §Choosing a model; §Prompting reasoning models |

These are derived, not vendor quotes: completion definition (S1), the three output-format elements (S6), the example-merging rule (S7), the single-step exemption (S4), and S10.

S2 and S3 combine: a red-line section may use "never," but it still needs a reason. Bold headings are navigation, not emphasis; S3's emphasis means strengthening the whole
sentence. For S12, use the checker's result for machine-checkable format items and check placeholders and other content items manually.

S5 opposes treating numbering as implicit priority. A file may explicitly declare same-section ordering (for example, "the earlier rule wins"); follow that declaration when
present, and do not treat numbering as evidence when absent.

## Resolving Source Conflicts

- **Emphasis**: default to plain imperatives. OAI-41 says all-caps and bribe-like incentives are "generally not necessary"; CC-BP says when many lines are emphasized, none stands
  out; ANT-PBP says strong wording written for older models should be pulled back. Emphasize only red lines, or one observed skipped rule, and state the observation.
- **Granularity**: write goals and constraints first. List steps only when order or completeness is critical, and state what happens if a step is skipped (ANT-PBP: "Prefer general
  instructions over prescriptive steps."). For non-reasoning models that need explicit planning, add `Reasoning Steps` per OAI-41.
- **Length**: no line limit; use S9.
- **Prohibitions**: keep red lines and state why; for everything else, write the alternative behavior.
- **Priority**: numbering itself does not create priority; do not write "the lower number wins." A file may explicitly declare ordering; follow it. OAI-MS levels: root > system >
  developer > user > guideline; a later message at the same level overrides an earlier one.
- **Fallback**: state what to do when information is insufficient. Writing only "call a tool first" leaves that branch undefined.

## Deletion Criterion

Ask line by line (CC-BP):

> Would removing this cause Claude to make mistakes?

If the answer is "no," delete it. The criterion is signal, not word count (ANT-CE: "minimal does not necessarily mean short").

`Context` holds only the left column:

| Include | Exclude |
|---|---|
| Shell commands the model cannot guess | Things it can learn by reading code |
| Style requirements that differ from language defaults | General language conventions |
| How to run tests and which runner to use | Detailed API documentation (link instead) |
| Repository conventions (branch naming, commit format) | Fast-changing information |
| Project-specific architectural decisions | File-by-file descriptions |
| Required environment variables | Self-evident requirements such as "write clean code" |

Examples: 3–5, each showing behavior not covered by the rules; fold edge cases into examples instead of a separate checklist (ANT-CE opposes laundry lists). Do not add examples for
behavior the rules already state clearly.

## How to Write Each Section

- **Role and Objective**: role, scope, and completion definition in one or two sentences.
- **Instructions**: `Always` states what to do; `Never` holds only red lines, each with a reason; `When Unsure` covers S4. Use plain imperatives.
- **Workflow**: write it only when reordering steps changes the outcome, and state what skipping a step does.
- **Output Format**: state structure, length, and format. Without a length, the model uses its default; GOOG says Gemini 3 defaults to brevity, so detailed output must be requested explicitly.
- **Examples**: wrap each in `<example>` so it is not read as an instruction.
- **Context**: use the table above; link or point to long documents instead of pasting them.

`Reasoning Steps` only for non-reasoning models that need explicit planning; `Final instructions` is an optional restatement at the end of a long prompt. Delete either if unused.

## Complex Logic

Use a table as the source of truth when rules combine multiple conditions or move through states; do not put them in one large diagram.

- Multiple conditions select one action: use a decision table. Use booleans or enums in condition columns, and state match order, the meaning of `*` and `-`, and the default branch.
- Tasks move on events: use a state table. List current state, event, condition, next state, and action; unlisted combinations fall to the default.
- When table and diagram coexist, the table is the source of truth and the diagram is overview; conflicts resolve to the table.
- When the table starts repeating or nesting exceeds two levels, split sub-decisions or switch to pseudocode or pure functions with table-driven tests.

Templates, the authorization example, and the task-lifecycle example are in `references/complex-logic.md`.

## Machine Check

The script checks Markdown syntax, layout, and link validity only; it does not read semantics, judge rules, or trace sources. Exit codes: 0 no errors, 1 errors, 2 argument,
dependency, or file problem.

### Usage

Paths are relative to this skill's directory; replace `<skill-dir>` with the actual path:

```bash
python3 <skill-dir>/script/check.py AGENTS.md
```

In CI, add `--strict`; warnings also fail and the exit code is 1:

```bash
python3 <skill-dir>/script/check.py --strict AGENTS.md
```

The script depends on `markdown-it-py`; if it is missing, the script reports an error and prints an install command; it does not install automatically. The script's own tests use the standard
library unittest:

```bash
python3 -m unittest discover -s <skill-dir>/script
```

### Rules

Output has three levels:

| Level | Meaning | Affects exit code |
|---|---|---|
| Error (`[错误]`) | File structure is broken | Yes |
| Warning (`[警告]`) | Format issue that needs fixing | No |
| Suggestion (`[建议]`) | Possible improvement | No |

Each finding gives a location (`L<line>` or whole file), rule ID, reason, and suggested fix.

Grouped by file, structure, headings, lists, tables, links, inline, and layout.

| Rule | Level | Checks |
|---|---|---|
| MD-BOM | Warning | File starts with a BOM |
| MD-EOL | Warning | Mixed CRLF, LF, or CR line endings |
| MD-FINAL-BLANK | Warning | Extra blank lines at end of file |
| MD-FINAL-NEWLINE | Error | Missing final newline |
| MD-FENCE | Error | Unclosed fence |
| MD-FENCE-LANG | Suggestion | Fenced code block has no language tag |
| MD-FENCE-STYLE | Suggestion | Mixed backtick and tilde fences in one file |
| MD-HTML-COMMENT | Error | Unclosed HTML comment; an unclosed inline comment reports the same rule |
| MD-HTML-BLOCK | Error | Unclosed `<script>`, `<style>`, `<pre>`, or `<textarea>` block |
| MD-HEAD-SPACE | Warning | No space after `#`; the line renders as a paragraph |
| MD-HEAD-MULTI-SPACE | Warning | Multiple spaces after `#` |
| MD-HEAD-INDENT | Suggestion | Top-level heading indented by 1–3 spaces |
| MD-HEAD-START | Warning | First heading is not h1 |
| MD-HEAD-JUMP | Warning | Heading level jump |
| MD-HEAD-EMPTY | Warning | Heading has no text |
| MD-HEAD-DUP | Warning | Duplicate heading (case and whitespace folded) |
| MD-HEAD-BLANK-AFTER | Suggestion | No blank line after heading |
| MD-LIST-SPACE | Warning | No space after list marker |
| MD-LIST-MARKER | Warning | Mixed `-`, `*`, and `+` in one list run |
| MD-LIST-START | Warning | Ordered list does not start at 1 |
| MD-LIST-EMPTY | Warning | List item has no content |
| MD-LIST-INDENT | Warning | Sibling indent mismatch, or indent too deep and the list structure is lost |
| MD-QUOTE-SPACE | Suggestion | No space after `>` |
| MD-TABLE-COLS | Warning | Table rows have different column counts |
| MD-TABLE-BROKEN | Warning | Consecutive pipe rows did not parse as a table (delimiter row missing columns or dashes) |
| MD-LINK-REF | Warning | Reference label is not defined |
| MD-LINK-DEF-DUP | Warning | Same label defined twice; the latter is ignored |
| MD-LINK-DEF-EMPTY | Warning | Link definition has no destination |
| MD-LINK-DEF-UNUSED | Suggestion | Definition is never referenced |
| MD-LINK-EMPTY | Warning | Link or image has no text or no destination |
| MD-LINK-TEXT-SPACE | Suggestion | Link or image text has leading or trailing whitespace |
| MD-LINK-TARGET | Warning | Relative link or image target does not exist in the repo |
| MD-LINK-SYNTAX | Warning | `[text](` did not parse as a link |
| MD-ANCHOR | Warning | In-page anchor points to a missing heading |
| MD-INLINE-CODE | Warning | Unpaired backticks |
| MD-EMPHASIS | Warning | Unpaired `**`, `__`, or `~~` |
| MD-EMPHASIS-STYLE | Suggestion | Mixed italic or bold markers in one file |
| MD-INLINE-HTML | Warning | Known inline HTML tag is opened but not closed |
| MD-BLANK-RUN | Warning | Multiple consecutive blank lines |
| MD-BLANK-BEFORE-BLOCK | Suggestion | No blank line before a top-level block |
| MD-BLANK-AFTER-BLOCK | Suggestion | Top-level block is followed directly by body text |
| MD-LINE-LEN | Warning | Body line exceeds 200 characters; tables, code, URLs, and front matter are exempt |
| MD-TRAILING-WS | Warning | Trailing whitespace |
| MD-TAB | Warning | Tab in body text |
| MD-HR-STYLE | Suggestion | Mixed thematic-break styles in one file |

### Scope of Checks

These checks are based on CommonMark parser results, not line-by-line regular expressions:

- Structure checks skip fences, indented code, HTML blocks, and front matter. `<example>` is no longer special; it is treated as ordinary HTML.
- BOM, mixed line endings, and trailing blank lines are checked from the raw text; the BOM is stripped before parsing so it does not affect the first heading.
- Blank-line-before checks only look at top-level blocks; blocks inside nested lists or blockquotes, and blocks after headings, are not reported.
- Blank-line-after checks only look at top-level blocks; blocks inside nested lists or blockquotes are not reported, and blank lines already at the end of a block are skipped.
- Blank-line-after is reported only when body text follows the block; if another block starts, it is not reported.
- Blank-line-after a heading is reported only when the next line is body text; list, table, fence, and other block starts are not reported.
- Heading indentation checks only top-level headings; headings inside lists or blockquotes are not reported.
- Fence, thematic-break, and emphasis style checks fire only when styles are mixed in one file.
- Backticks and emphasis may pair across lines; the script judges by "markers the parser did not consume," so valid cross-line pairs are not reported.
- Link definitions come from the parser's reference table; destinations on the next line and definitions inside list items are recognized.
- If a table delimiter row is wrong, the whole table degrades to a paragraph; `MD-TABLE-BROKEN` catches this.
- External links, `mailto:`, and anchors are not checked for local existence; anchors are converted to GitHub slugs and compared.
- Inline HTML checks only use `html_inline` tokens; autolinks and `<placeholders>` are not treated as unclosed.

### Deliberately Not Checked

These three are deliberately not checked because mechanical checks would only create noise:

| Not checked | Reason |
|---|---|
| Unpaired single `*` or `_` | `*.py`, `src/*.ts`, `2*3`, and `**/*.md` use the same characters; distinguishing them needs semantics |
| Setext headings (`===`, `---` underlines) | Legal syntax; normal headings would be reported |
| Empty header cells in tables `\| a \|  \|` | Legal and common |

`MD-INLINE-HTML` has one residual false positive: a single `<div>` written while explaining syntax is indistinguishable from a genuinely unclosed tag. Put such content in backticks or a code block
to skip it.

### Reading Output

- `[错误]` (error): fix and rerun until there are 0 items and the exit code is 0.
- `[警告]` (warning): write a conclusion for each; for structural false positives, say it is a heading-wording issue, not missing content.
- `[建议]` (suggestion): decide with S9; optional.

## Anti-patterns

| Anti-pattern | Fix |
|---|---|
| Rules pile up so you must read everything to find one | Delete per S9; move details into the skill |
| Treat numbering as implicit priority | Use an explicit ordering declaration, or split sections |
| All prohibitions, no alternative behavior | Add an alternative or reason per S2 |
| Red lines and ordinary requirements both use "never" | Per S3, reserve absolute wording for red lines |
| Every rule is bold | Bold is navigation only; reserve whole-sentence emphasis for red lines (S3) |
| Only "call a tool first" | Add the insufficient-information branch per S4 |
| Hard-code a step-by-step process | Write goals and constraints; keep steps only when order is critical (S13) |
| Paste API docs | Link to them (S11) |
| Write tools or configuration keys that do not exist | Only write confirmed interfaces (S10) |
| Pile edge cases into an example list | Fold them into 3–5 examples (S7) |
| Put complex rules in one large diagram | Use decision or state tables; diagrams are overview only |
| Treat every document as a changelog | Write the current state; put change history in commit, PR, or delivery |
| Ban all stubs or ship them silently | Mark, track, and disclose stubs; never present them as complete |
| Clean only the project and forget temp dirs | Remove task-created temp files everywhere; list retained paths |
| Batch-complete all todos at the end | Update each item when it changes; complete only after evidence |
| Treat every key as secret | Allow genuinely public or publishable keys; ban private keys and secrets |

## Template

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

Section order follows OAI-PE's Identity → Instructions → Examples → Context and the OAI-41 template.

## Examples

An agent that changes a repository:

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
- Conflicting instructions: point out the conflict, follow this file's constraints, and record the deviation in the delivery.

# Workflow
1. Read the relevant code and tests; confirm the current state.
2. Change the code.
3. Run `pytest -q` and paste the exit code.
4. Write the change note.

# Output Format
- Conclusion first, then evidence.
- Paste verification results verbatim with the exit code; if not run, write "not run."

# Context
- Unit tests: `pytest -q`; full: `pytest`.
- CI runs Python 3.11 and 3.12; both must pass.
```

The machine check expects 0 errors (`[错误]`), 0 warnings (`[警告]`), and 0 suggestions (`[建议]`). Content rules still need manual review.

Single-step task; no tools. S4 is satisfied by the "cannot summarize" branch, and `Instructions` is omitted:

```markdown
# Role and Objective

Compress the input text into a summary of at most three sentences. The completion standard is to preserve the conclusion and key numbers.

# Output Format
- Output only the summary body; no title, no explanation.
- If the input is empty or not text, output "cannot summarize."
```

The machine check also expects 0/0/0. Omitting the Instructions section is a content choice; the script does not report it.

One sentence can also work (ANT-PBP: "Even a single sentence makes a difference"), but the completion definition cannot be omitted.

## Sources

Short labels are used in the rule table. Read `references/provenance.md` only when a rule's source is questioned or a linked document is updated; normal execution does not read it.

| Short label | Document | Link |
|---|---|---|
| OAI-PE | Prompt engineering | https://developers.openai.com/api/docs/guides/prompt-engineering |
| OAI-41 | GPT-4.1 Prompting Guide | https://developers.openai.com/cookbook/examples/gpt4-1_prompting_guide |
| OAI-MS | Model Spec (2026-08-18) | https://model-spec.openai.com/2026-08-18.html |
| ANT-PBP | Prompting best practices | https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices |
| ANT-CE | Effective context engineering | https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents |
| CC-BP | Best practices for Claude Code | https://code.claude.com/docs/en/best-practices |
| GOOG | Prompt design strategies | https://ai.google.dev/gemini-api/docs/prompting-strategies |
| MS | System message design | https://learn.microsoft.com/en-us/azure/foundry/openai/concepts/advanced-prompt-engineering |

OAI-MS is the 2026-08-18 version; the page notes a newer version. If a refresh no longer matches, change or delete the rule; do not keep an untraceable requirement.
