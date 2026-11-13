---
name: comment-conventions
description: Defines, reviews, and repairs code comments and doc comments in any programming project, covering API documentation embedded in source, inline and block comments, file headers, markers, deprecation notices, legal headers, tool directives, and commented-out code. Use when writing or revising a function, reviewing a diff for misleading comments, or fixing stale doc comments. Provides language-agnostic defaults with per-language overrides.
argument-hint: '[path or symbol]'
---

# Comment Conventions

Comments fail in three ways: they restate what the code already says, they go stale while the code moves on, and
they hide intent behind a summary of mechanics. A comment earns its maintenance cost only when it records what a
reader cannot recover from the code: the contract, the reason, the hazard, or the plan. This skill gives one
decision procedure and a complete rule set for every comment a project writes, from doc comments that generate the
API reference to markers, directives, legal headers, and commented-out code. It serves the writer adding a comment
and the reviewer judging one, because the same rules decide whether a comment should exist and whether it can be
trusted.

## Scope and Precedence

Apply the first rule that fits, and do not mix conventions inside one scope:

1. Mandatory language or documentation-tool convention and linter. Javadoc doclint, rustdoc, TSDoc, godoc comment
   placement, and a configured comment linter are not optional.
2. Existing project convention. Read the code, the doc-tool configuration, and the linter before inventing a rule.
3. This standard's defaults, when the two levels above are silent.
4. Personal preference, which never overrides the three levels above.

- Comments versus documentation. This skill covers comments embedded in source, API documentation generated from
  doc comments, markers, directives, and legal headers. Standalone documents (README, docs sites, ADRs,
  changelogs, API reference pages) are out of scope; a separate documentation skill owns them. When a comment grows
  into a document, move it and link it instead of copying it.
- Generated, vendored, and third-party code is exempt from style edits. Keep the generated marker and the upstream
  comments; regenerate or re-vendor instead of hand-editing, and record local patches outside the file.
- One natural language per repository. Declare it (English by default for libraries and open source, the team
  language for internal code), apply it to every comment type, and keep identifiers, API terms, and quoted
  upstream text in their original form.
- A comment change is a code change. Update it in the same commit, review it like code, update generated docs and
  doctests, and rerun the doc build; a doc comment on a public symbol is part of the API contract.
- When two rules conflict, state the conflict and the chosen rule; record the decision so the next change follows
  it.
- A comment is not a substitute for a test, a type, or a clear name. When correctness matters, encode it in code or
  in a test; a comment that only promises behavior the code does not enforce is a wish, not a contract.
- Review depth follows API visibility. A public symbol's doc comment gets the same review as its signature; an
  internal helper's comment is judged by whether it prevents a future mistake.

## Process

1. Decide whether a comment is needed at all. If the code already states the fact, delete the comment or improve
   the code; a missing comment is not a defect when the code is clear.
2. Classify the comment: doc comment, module or file header, inline why, block explanation, marker, deprecation,
   legal header, tool directive, or commented-out code. The classification decides the required fields and the
   checklist item that will judge it.
3. Read the surrounding code, the project convention, and the doc-tool configuration; find the linter rule that
   will judge the result. The doc build and the linter are the acceptance test, not decoration.
4. Write the content the reader cannot get from the code: the contract, the reason, the hazard, the external
   constraint, or the plan. Prefer one precise sentence to three vague ones.
5. Apply the form: correct syntax and position, required tags or sections, one natural language, the project's
   line width and punctuation.
6. Update every related comment in the same change: callers, generated docs, examples, deprecation notices, and
   markers that the change resolves.
7. Verify against the current code: re-read the comment after the final edit, run the doc build, doctests, and
   comment linter, and delete anything that no longer holds. Verification is what separates a comment from a guess.

## Core Rules

- **Explain why, not what.** A comment that repeats the code doubles the maintenance cost and goes stale first.
  State the reason, the contract, or the hazard; if the code can say it instead, rewrite the code.
- **A doc comment is a contract.** At every public boundary, document parameters, return values, errors, side
  effects, and invariants. Callers read the contract before the body, and changing it changes the API.
- **The code is the source of truth.** A comment that contradicts the current code is a defect; fix or delete it in
  the same change. Never leave a wrong comment because "the code is obvious".
- **No comment beats a wrong comment.** A missing explanation costs a look at the implementation; a false one costs
  a bug. Delete uncertain comments and recover the fact from the code or the author.
- **Delete code instead of commenting it out.** Version control keeps the history; a commented-out block rots,
  hides dead APIs, and confuses search. If disabling is temporary, mark owner, ticket, and expiry.
- **Markers carry what their kind requires.** `TODO`, `FIXME`, and `HACK` include an owner and a removal trigger;
  `NOTE` and `WARNING` state the condition, the consequence, and the required action. All follow the project's
  marker spelling.
- **Deprecation names the replacement and the removal.** Use the language's deprecation mechanism with a migration
  note and a version or date; a bare `@deprecated` leaves the caller without a path.
- **Tool directives are minimal and justified.** Start at the narrowest scope, one line and then one function; a
  file-level suppression needs a reason and a cleanup ticket, and nothing disables a rule repository-wide for one
  site.
- **Legal headers and generated markers stay byte-identical.** They are read by tools and licenses; do not
  reformat, translate, or hand-edit them, and never remove a third-party notice.
- **Document the non-obvious, not the familiar.** Record external constraints, workarounds, unsafe invariants,
  surprising edge cases, and measured performance bounds; skip the language tutorial. When an explanation grows
  past a paragraph, it belongs in a design note that the comment links.
- **State units, ranges, nullability, and ownership.** When the type cannot carry them, the doc comment must:
  milliseconds versus seconds, inclusive versus exclusive, absent versus empty, borrowed versus owned.
- **Attach the comment to its subject.** A doc comment sits on the declaration, an inline comment on the line or
  block it explains, and a file header on the file. A stranded comment is read against the wrong code, and a
  duplicated comment drifts from its twin.
- **Write in the format's voice.** Sentence case, complete sentences, correct punctuation, and the project's line
  width; doc-comment descriptions state behavior in the present tense and instructions in the imperative.
- **Density follows surprise, not line count.** Comment the non-obvious and leave the obvious alone; a file where
  every line carries a comment is as hard to read as one with none, and each comment is another thing to maintain.

## Comment Type Matrix

The comment type decides the syntax, the placement, and the required fields. Choose the type before writing, because
a doc comment and an inline comment obey different rules:

| Type | Purpose | Required form | Example |
|---|---|---|---|
| Doc comment (docstring) | Public contract of a declaration | Tool syntax directly above the declaration; summary, contract, tags | `"""Return the invoice total in cents."""` |
| File or module header | Purpose, scope, and invariants of the file | First comment after the legal header; no change history | `// Package billing reconciles invoices.` |
| Inline why | Explain a non-obvious choice on the next line | `//` or `#` above the line, same indent, one idea | `# Retry once: the gateway resets idle connections.` |
| Block explanation | Multi-line rationale, algorithm, external constraint | Project block syntax, wrapped, no decorative border | `/* The vendor caps a batch at 500 items. */` |
| API doc tags | Machine-readable fields for generated reference | Language tag syntax and order required by the tool | `@throws InvoiceNotFoundError when the id is unknown` |
| TODO | Owned, planned work | Marker plus owner, action, issue or removal trigger | `// TODO(maria): drop the shim after v2 ships (#512).` |
| FIXME / HACK / NOTE / WARNING | Defect, shortcut, context, or hazard | FIXME/HACK: wrong behavior, owner, removal trigger; NOTE/WARNING: condition, consequence, action | `// WARNING: caller must hold the lock.` |
| Deprecation marker | Migration path and removal plan | Language mechanism plus replacement and version | `@deprecated Use create_invoice; removed in v3.0.` |
| Legal header | License and copyright obligations | Exact SPDX and copyright lines in the required position | `// SPDX-License-Identifier: Apache-2.0` |
| Tool directive | Instruction to a linter, formatter, or generator | Exact tool syntax at the narrowest scope, with reason | `// eslint-disable-next-line no-console -- CLI output.` |
| Generated marker | Prevent hand edits and point to the generator | Tool-native marker at the top, byte-identical | `// Code generated by sqlc. DO NOT EDIT.` |
| Commented-out code | None: version control owns old code | Delete it; use the build system or a marked directive with expiry | `Delete it; history stays in version control` |

## Dimension Index

Each dimension has detailed rules, examples, and edge cases in `references/dimensions.md`; the number in the
dimension column is the section number in that file.

| Dimension | First rule |
|---|---|
| 1. Doc comments and public contracts | Document the visible contract, not the signature. |
| 2. Module, file, and value headers | State the unit's purpose and invariants, never its history. |
| 3. Functions and methods | Document parameters, returns, errors, and side effects at the boundary. |
| 4. Types, fields, enums, constants | Document invariants and member meaning, not the field name. |
| 5. Units, ranges, nullability, ownership | State what the type cannot carry. |
| 6. Side effects, mutation, concurrency | State the effect, the hazard, and the required action. |
| 7. Deprecation notices | Name the replacement and the removal trigger. |
| 8. TODOs and planning notes | TODO/FIXME/HACK carry an owner and removal trigger. |
| 9. Commented-out code | Delete it; version control keeps the history. |
| 10. Change history and journal comments | The change log lives in version control. |
| 11. Code examples in doc comments | A doc example is executable documentation. |
| 12. Generated and vendored code markers | Regenerate or re-vendor; never hand-edit. |
| 13. Legal and license headers | Keep them byte-identical where the tool expects them. |
| 14. Tool directives | Narrowest scope, supported reason, cleanup ticket. |
| 15. Tests and fixtures | Explain the scenario, not the call sequence. |
| 16. Configuration and infrastructure | Use the format's comment syntax and state the constraint. |
| 17. Shell scripts | Document purpose, arguments, and non-obvious quoting. |
| 18. Markup, CSS, template comments | Comply with the format, and never ship secrets. |
| 19. i18n and localized comments | One declared language per repository. |
| 20. Secrets and privacy in comments | Comments are public; never store credentials. |
| 21. Density, width, punctuation, capitalization | Complete sentences, project line width, no decoration. |
| 22. Stale and lying comments | A false comment is a defect with a fix deadline. |
| 23. Refactoring and moving comments | Move the comment with the code. |
| 24. Comment review workflow | Read every comment in the diff against the code. |

## Anti-Patterns

| Anti-pattern | Why it fails | Fix |
|---|---|---|
| Comment restating the line (`// increment i`) | Duplicates the code and rots first | Delete it; rename the identifier if intent is unclear. |
| Stale comment that contradicts the code | Sends every reader the wrong way | Fix or delete it in the same change; audit after every behavior change. |
| Bare `// TODO: fix later` | No owner, no trigger, no review path | `TODO(owner): action and reason` plus an issue. |
| Commented-out code block | Hides dead APIs and confuses search and coverage | Delete it; rely on version control. |
| `@param user the user` | Repeats the signature and adds no contract | State format, range, nullability, or ownership. |
| Change history in a file header | Duplicates version control and goes stale immediately | Remove it; the commit message carries history. |
| Whole-file lint suppression without a reason | Hides every future violation and outlives its justification | Use file scope only when line or function scope cannot work; add the reason and a cleanup ticket. |
| Deprecation without a replacement | Leaves callers no migration path | Add the replacement, version, and removal ticket. |
| Commented-out debug output | Pollution that reappears in commits | Use the logger at a configurable level. |
| Warning that names no action | The reader cannot act on the hazard | State condition, consequence, and required action. |
| Secret or personal data in an example | Comments ship and leak with the source | Use `example.test.invalid` and placeholder identifiers. |
| Comment in a foreign language | Breaks the one-language rule and slows review | Use the declared repository language. |
| Comment instead of a named constant | Hides meaning from the code itself | Extract `DEFAULT_TIMEOUT_MS` and delete the note. |
| Doc comment copied across functions | The copies drift apart | Link one owner or write the contract once. |
| Author or date banner | Noise no tool or reader needs | Remove it; commit metadata owns that information. |
| Change entry in a comment (`// 2026-02-11: changed order`) | Duplicates commit history and rots on the next change | Remove it; the commit message owns the change. |

## Review Checklist

- [ ] The comment adds information the code does not state.
- [ ] Every doc comment matches the current signature, behavior, and errors.
- [ ] Public parameters, returns, errors, side effects, and invariants are documented.
- [ ] Units, ranges, nullability, and ownership are explicit where the type cannot carry them.
- [ ] The summary line is one sentence in the project's tense and ends with punctuation.
- [ ] Inline comments sit above or beside the line they explain, at the same indentation.
- [ ] Every TODO, FIXME, and HACK has an owner and a tracked issue or removal trigger.
- [ ] No commented-out code or debug output is left in the change.
- [ ] Deprecations name a replacement and a removal version or date.
- [ ] Legal headers and generated markers are intact and unmodified.
- [ ] Tool directives are minimal and include a reason and a cleanup plan.
- [ ] No secret, token, personal datum, or internal address appears in any comment.
- [ ] The comment language is the declared repository language, with identifiers unchanged.
- [ ] Line width, punctuation, capitalization, and spacing match the project.
- [ ] Code examples in doc comments were executed and produce the stated output.
- [ ] Generated and vendored files were regenerated, not hand-edited.
- [ ] Comments moved or deleted by a refactor left no orphan or stale reference.
- [ ] The doc build, doctests, and comment linter pass.
- [ ] Comments that duplicate a standalone document are linked, not copied.
- [ ] Every behavior change in the diff includes its comment update.

## Examples

<example>
Doc comment for a public function:
`"""Charge the invoice and return the payment id; raise PaymentDeclinedError when the gateway declines."""`
Add `Args:` and `Raises:` sections when the project uses Google style, and never repeat type hints in prose.
The comment states both the successful result and the failure a caller must handle; the body does not repeat it.
</example>

<example>
Inline why above a non-obvious statement:
`# Sort by created_at, not id: imports can insert older rows after the initial load.`
Write it directly above the sort call; if the comparator name already says this, delete the comment.
One idea per comment; a second reason gets its own line and its own review.
</example>

<example>
Concurrency warning on a lock-free read:
`// WARNING: the snapshot may be stale; take the write lock before comparing versions.`
State the condition, the consequence, and the required action in that order, and link the full history to the
issue. Never bury a hazard inside a paragraph of description.
</example>

<example>
Marker with an owner and a removal trigger:
`// TODO(maria): drop the retry shim when gateway v2 is the only client (#512, target v2.4).`
A bare `// TODO: fix this` fails review; work that is not tracked does not stay in the code.
The issue number and version make the marker removable by someone who is not its author.
</example>

<example>
Stale doc comment repair:
The comment says `Return the cached user or None`, but the function now raises `UserNotFoundError`.
Rewrite the contract in the same change, update the caller comment that still promises null, and fix the doctest
that asserts `is None`. Search the repository for the old promise; a behavior change usually leaves more than one
stale comment.
</example>

## References

Read [references/dimensions.md](references/dimensions.md) for the full rule set by comment type and hazard, and
[references/languages.md](references/languages.md) for exact syntax, doc tools, and marker conventions per
language. Read both before establishing a project's comment policy and linter configuration; during routine work,
read the dimension that applies and the language row that applies. When a reference file disagrees with this file,
the language file wins for syntax and the dimension file wins for the rule; report the conflict instead of
blending both.
