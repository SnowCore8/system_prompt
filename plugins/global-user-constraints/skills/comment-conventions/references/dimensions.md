# Comment Dimensions

Use this file with `SKILL.md`. Each section gives the rule, the edge cases, and the failure mode for one comment
type or hazard. When a project already has a convention or a linter, read it first and apply the higher-precedence
rule; this file supplies the default and the reasoning. Section numbers match the dimension index in `SKILL.md`.

## 1. Doc Comments and Public API Contracts

- A doc comment is the published contract for everything a caller can see: exported functions, types, methods,
  protocol implementations, and documented configuration.
- The contract covers what the signature cannot: meaning, preconditions, postconditions, error behavior, side
  effects, ownership, and stability promises.
- Open with one summary sentence in the imperative or third person ("Return the invoice total in cents"), and add a
  body paragraph only when a caller needs context the summary cannot carry.
- Do not restate the signature. `@param user the user` adds nothing; `@param email lower-cased and trimmed` states
  a precondition.
- Treat the doc comment as code: review its diff, update it in the same change as the behavior, and version it when
  the public meaning changes.
- Say when a behavior is intentionally unspecified ("iteration order is not guaranteed") instead of leaving the
  reader to infer a contract.
- Keep implementation notes in a private comment or in the body; do not leak internal caching, locking, or field
  layout into a public contract.

| Good | Bad | Why |
|---|---|---|
| `@param email Lower-cased and trimmed; rejects input without a local part.` | `@param email The email.` | States a precondition the signature cannot carry. |
| `@returns 0 when no tax applies; never negative.` | `@returns the tax.` | Names the edge case callers must handle. |
| `@throws InvoiceNotFoundError when the id is unknown.` | `@throws Exception on errors.` | Callers can handle a specific type, not a catch-all. |

## 2. Module, File, and Value Headers

- A file or module header states the unit's purpose, scope, and invariants; it is not a place for a "what changed"
  history or a list of recent fixes.
- In Go, the package comment sits immediately above `package`, starts with `Package <name>`, and describes the whole
  package; a blank line would detach it.
- In Python, the module docstring is the first statement in the file and states the module's role and public entry
  points.
- In Rust and C/C++, file-level docs use `//!` or a `@file` block after the license header; do not duplicate the
  type docs there.
- A value or constant header explains the policy or source of the number ("matches the partner API limit"), not the
  literal itself.
- Header blocks carry no author names, dates, ticket numbers used as change history, or decorative banners.
- Link the standalone design document instead of copying it; a header that repeats a document goes stale in two
  places.

| Good | Bad | Why |
|---|---|---|
| `// Package billing reconciles invoices against the ledger.` | `// Billing package.` | Names the responsibility, not the folder. |
| `# Time zone used for every cut-off date in this module.` | `# tz` | States why the value exists. |
| `//! Parser for the v2 wire format; see docs/wire-format.md.` | `//! TODO: document module.` | Points to authority without duplicating it. |

## 3. Functions and Methods

- Every public function, method, and protocol implementation gets a doc comment; a private helper gets one only when
  the name and body leave a real gap.
- Document parameters when the type does not carry meaning: format, encoding, range, nullability, ownership, and
  default behavior.
- Document the return value's meaning and edge cases: empty versus absent, sentinel values, partial results, and
  ordering guarantees.
- Document every error a caller is expected to handle, by type and trigger; do not list errors that are internal
  and never escape.
- Document side effects (I/O, mutation, events, cache writes) and whether the call is idempotent, retryable, or
  transactional.
- Put an example in the body when the call sequence is not obvious; keep the example runnable (see section 11).
- A description that starts "This function..." is noise; start with the action and its object.

| Good | Bad | Why |
|---|---|---|
| `Read the current balance; the call may block up to timeout_ms.` | `Gets the balance.` | States the I/O and the bound. |
| `Return matched orders sorted by created_at; empty when none match.` | `Returns orders.` | Ordering and empty state are part of the contract. |
| `Idempotent: a repeat with the same idempotency key returns the first result.` | `Safe to call.` | States the actual retry contract. |

## 4. Types, Fields, Enums, and Constants

- A type's doc comment states what an instance represents and the invariants it guarantees or requires; field
  comments document the parts the type name does not make obvious.
- Document enum members when their meaning is not obvious from the name, and state the wire value only when it
  differs from the code name.
- Field comments carry units, ranges, null meaning, and whether the value is mutable, derived, cached, or owned by
  the receiver.
- Do not repeat the field name in its description; state the missing contract instead.
- A constant documents its source and policy: where the number comes from, who owns it, and when it may change.
- A type that aliases another representation states the boundary ("wire format only") and where the mapping
  happens.
- Do not document private representation (field order, internal caches, hash seeds) on a public type.

| Good | Bad | Why |
|---|---|---|
| `OrderId` is opaque: do not parse, sort, or display it. | `The order id.` | States the contract of the representation. |
| `RetryCount` increments per attempt and is capped by `MaxAttempts`. | `How many retries.` | Ties the fields to the invariant between them. |
| `StatusRefunded` is terminal; no further transitions are allowed. | `Refunded status.` | Names the rule callers depend on. |

## 5. Units, Ranges, Nullability, and Ownership

- When the type cannot enforce a unit, state it in the doc comment with the same spelling used in the name:
  `timeout_ms`, `amount_cents`, `size_bytes`.
- State ranges and inclusion explicitly: "0 to 100 inclusive", "start inclusive, end exclusive"; never rely on the
  reader's assumption.
- Define null, None, nil, undefined, and empty as distinct states; say what each one means and whether it may be
  returned.
- Document ownership, lifetime, and mutation rights in languages that track them: who frees the value, who may
  mutate it, and what aliasing is allowed.
- For borrowed or referenced values, state the borrow duration and whether the receiver keeps a reference after the
  call returns.
- For collections, state the iteration order only when it is guaranteed; otherwise say the order is unspecified.
- Rounding, truncation, and overflow behavior belong in the contract when the value is numeric.

| Good | Bad | Why |
|---|---|---|
| `Timeout in milliseconds; 0 means wait forever.` | `Timeout value.` | Unit and sentinel are part of the contract. |
| `Return the slice borrowed from self; valid until the next mutation.` | `Returns a slice.` | Lifetime and aliasing rules decide safe use. |
| `Amount is an integer number of cents; never a float.` | `The amount.` | Representation and unit are explicit. |

## 6. Side Effects, Mutation, Concurrency, and Performance Warnings

- State every externally observable effect: network, disk, database write, event emission, log output, global state,
  and clock or random use.
- State the concurrency contract: thread-safe, requires an external lock, must run on the main thread, or is not
  reentrant.
- Warn before the hazard, not after it: state the condition, the consequence, and the required action in one
  comment.
- Document mutation of arguments and receiver state, including whether an input collection is consumed or retained.
- Performance notes must be actionable and measured: "O(n^2) in the number of rules; compile the rules once" beats
  "slow".
- Do not document transient implementation details (a specific lock type, buffer size, thread count) that a caller
  cannot rely on.
- A "WARNING" or "NOTE" prefix is a real marker: keep it for hazards and surprising behavior so it does not lose
  force.

| Good | Bad | Why |
|---|---|---|
| `// Caller must hold the account lock; this method does not acquire it.` | `// Thread safe.` | States the actual locking contract. |
| `// Emits one order.paid event after commit; consumers may see it twice.` | `// Sends event.` | Duplicate delivery changes consumer design. |
| `// WARNING: O(n^2) above 100 rules; precompile in the hot path.` | `// Slow.` | Bounds and remedy make the note usable. |

## 7. Deprecation Notices

- Deprecate with the tool's tag (`@deprecated`, `@Deprecated`, `#[deprecated]`) and a sentence naming the
  replacement and the migration.
- State the removal version or date and the tracking issue; "will be removed soon" is not a plan.
- Keep the deprecated symbol working and truthfully documented; never leave a deprecated doc comment that is
  already false.
- Use a stable replacement name that can be searched, and give a migration snippet when the shape of the API
  changes.
- Deprecation is a public API change: this skill owns the tag, the migration note, and the source comment; the
  release-note announcement is owned by the documentation skill.
- Do not mark internal helpers deprecated as a substitute for deleting them; delete unused internals.
- When the deprecation window ends, remove the symbol, its doc comment, and its references in one change.

| Good | Bad | Why |
|---|---|---|
| `@deprecated Use create_invoice; removed in v3.0 (issue #812).` | `@deprecated` | Names the path, the version, and the tracker. |
| `# Deprecated: use Store.put; the old key format is read-only.` | `# Old API.` | States the replacement and the remaining behavior. |
| `/** @deprecated Use totalCents; this getter rounds. */` | `/** Do not use. */` | Names the difference, not just the ban. |

## 8. TODOs and Planning Notes

- A TODO, FIXME, or HACK is a promise with an owner. Format it `MARKER(owner): action and reason`, plus an issue or
  a removal condition.
- Use markers by meaning: TODO for planned work, FIXME for known incorrect behavior, HACK for a deliberate
  shortcut, NOTE for context, WARNING for a hazard.
- Never leave a bare `TODO`, `FIXME`, `XXX`, or `???`; an anonymous marker is untracked debt that no review can
  resolve.
- Tie the marker to a trigger: a version, a date, or a dependency upgrade, not a vague "later".
- Keep the marker next to the code it constrains; a planning note at the top of the file is invisible to the reader
  of the line.
- A marker that is no longer true is a lying comment: delete it when the work lands, never tick it off.
- Scanner tools (todo-tree, issue linters) depend on exact marker spelling; use the project's configured style.

| Good | Bad | Why |
|---|---|---|
| `// TODO(maria): remove the retry shim after gateway v2 ships (#512).` | `// TODO: fix this later.` | Owner and trigger make the debt reviewable. |
| `// FIXME(maria): negative totals round toward zero; fix before v2.2.` | `// HACK.` | Owner and deadline make the fix reviewable. |
| `// HACK(devon): the vendor header requires a trailing space; do not trim.` | `// Weird.` | Owner plus reason explains why the shortcut must stay. |

## 9. Commented-Out Code

- Delete code instead of commenting it out; version control preserves the history and the removal stays
  reversible.
- Code disabled for a build variant belongs in the build system: a feature flag, a preprocessor guard, or
  configuration, not a comment.
- If a temporary disable is genuinely required during a migration, mark it with owner, ticket, and expiry, and add
  a check that fails after the date.
- Commented-out code confuses search results and coverage reports, and it hides unused imports and dead APIs.
- Do not comment out debug output "just in case"; use the logger at a configurable level instead.
- During review, treat a block of commented-out code as a removal request, not as a style question.
- Keep an intentional code sample only in a fenced, tested doc example (see section 11).
- Automated checks help: a comment scan that flags commented-out code in the diff is cheaper than arguing about each
  block.

## 10. Change History and Journal Comments

- Version control history is the change log; do not restate it in comments ("2026-03-01: added retry", "changed by
  Sam").
- Do not keep author tags, dates, or per-line version markers as the project's history; commit metadata carries
  that information.
- A rationale future readers need is present-tense context ("the vendor rejects empty bodies"), not a journal
  entry.
- Legacy projects with a mandated change header: follow the existing format in existing files, and do not
  introduce it in new files without a project decision.
- Do not add version numbers in file headers unless a release tool generates and verifies them.
- When a decision supersedes an old one, replace the old comment with the current rule; do not stack a second
  history line on top.

## 11. Code Examples in Doc Comments

- A fenced example in a doc comment is executable documentation: the doc tool compiles or runs it, so it must
  pass on every build.
- Use the language tag the doc tool recognizes (`python`, `rust`, `ts`); mark deliberately non-running snippets as
  `text` or `console`.
- Show the minimal complete setup: imports, required fixtures, and a realistic value; never call an undocumented
  helper.
- State the expected output exactly, including whitespace, when the example is an executed doctest.
- Do not use secrets, personal data, or production URLs in examples; use fake values such as
  `example.test.invalid`.
- When an API is too large to demonstrate fully, show one call and link the standalone guide instead of a partial
  snippet.
- Keep output stable across platforms: avoid timestamps, random IDs, and absolute paths where the tool allows it.

## 12. Generated and Vendored Code Markers

- Never hand-edit generated files; change the generator or the source of truth, regenerate, and commit the output
  with its marker.
- Keep the tool's generated marker at the top exactly as emitted ("Code generated by ... DO NOT EDIT."); tools and
  reviewers rely on it.
- Generated documentation comments belong to the generator's templates; fix the template, not the instance.
- Vendored third-party code keeps its upstream comments, headers, and license verbatim; record the version and the
  local patch set outside the file.
- If local patches are unavoidable, keep them minimal, marked with a patch note, and reapplied by the vendoring
  process.
- Exclude generated and vendored paths from comment-density and style checks; they are not review targets.
- A comment in a generated file that contradicts the generator is a bug in the generator; fix the source.

| Good | Bad | Why |
|---|---|---|
| `// Code generated by sqlc. DO NOT EDIT.` | `// Generated, but tweak the types here if needed.` | Any hand edit is lost on the next run. |
| `// Patch: upstream v2.3.0; our fix tracked in issue #644.` | `// Modified.` | Names the baseline and the tracked delta. |
| `// Source: schema.sql; regenerate with make gen-db.` | `// Auto.` | Gives the generator and the command. |

## 13. Legal and License Headers

- Place the license header exactly where the license tool or project policy requires it: usually the first lines
  of the file, before imports and doc comments.
- Use SPDX identifiers in the project's standard form, for example `SPDX-License-Identifier: Apache-2.0`; do not
  paraphrase the license text.
- Keep copyright lines from the originating owner; adding a contributor line follows the project's policy, not
  personal preference.
- Never strip or reformat a third-party header in vendored code; preserve the notice and add the project's NOTICE
  entry.
- Let the license tool (reuse, licensee, addlicense, a formatter plugin) write and update the header; never
  handcraft variants.
- A legal header is not a substitute for the license file; link the full text instead of pasting it into every
  file.
- Removing a header is a legal and build change; it needs the project owner's decision, not a cleanup pass.
- Generated files receive the header from the generator template; fix the template rather than each output file.

## 14. Tool Directives

- A directive is code for a machine: match the tool's exact syntax and scope, and place it where the tool reads
  it.
- Use the narrowest scope that works: one line, then one function, then one file; never disable a rule repository
  wide to fix one site.
- Always give the reason in the form the tool supports (`-- reason` for ESLint, a nearby comment for others); an
  unexplained suppression cannot be audited.
- Suppression is not a fix: leave a ticket or a note stating when it can be removed.
- Directive families: lint disables (`eslint-disable-next-line`, `# noqa`, `//nolint`, `@SuppressWarnings`),
  formatter off (`prettier-ignore`, `# fmt: off`, `clang-format off`), coverage ignores (`pragma: no cover`),
  type ignores (`@ts-expect-error`, `# type: ignore`).
- Prefer an annotation or attribute over a comment where the language supports it; configuration belongs in the
  config file, not beside one call.
- A stale directive that suppresses nothing is dead weight; remove it before it hides the next real violation.

| Good | Bad | Why |
|---|---|---|
| `// eslint-disable-next-line no-console -- CLI output is the product.` | `/* eslint-disable */` | Scope and reason are explicit. |
| `x = stub.field  # type: ignore[attr-defined]  # vendor stub lacks it` | `x = stub.field  # type: ignore` | Both the code and the justification are present. |
| `//nolint:errcheck // close error is reported by the caller` | `//nolint` | Disables only the rule that is understood. |

## 15. Tests and Fixtures

- A test comment states the scenario and why the case exists (regression, boundary, contract), not which methods
  are called.
- Name the behavior in the test name; use the comment for why the behavior matters and the link to the bug or
  decision.
- Explain non-obvious arrangement: why a fixture is large, why the clock is frozen, why a retry is expected.
- Comment an assertion only when the expected value needs provenance ("matches the ledger rounding rule").
- Skip and expected-failure reasons go in the framework's reason field or an adjacent comment; an unexplained skip
  is a silent deletion.
- Fixture data comments state the scenario and never contain real personal data; use fake values and note the
  generator when one exists.
- Do not comment out a failing test; fix it, skip it with a reason and a ticket, or delete it.

## 16. Configuration and Infrastructure

- Each format has its own comment syntax and persistence rule; use the language matrix, not the source language's
  syntax.
- YAML and TOML use `#`; keep the comment above the key it explains and never inside a quoted scalar.
- Dockerfile comments use `#` above the instruction; a full-line comment inside a continued instruction is removed
  by the parser, and a trailing `#` after command text on the same line is part of the shell command.
- SQL migrations carry a header comment with ticket, intent, and rollback note; an applied migration is immutable,
  so corrections arrive as a new file.
- Terraform and HCL use `#`; put the durable explanation in the `description` attribute so `terraform-docs`
  carries it.
- Infrastructure comments state why a setting exists and what breaks without it; do not restate the value.
- Never put credentials, tokens, account identifiers, or internal hostnames in a config comment; reference a
  secret store instead.

| Good | Bad | Why |
|---|---|---|
| `# Keep 1 replica during the backfill; the writer serializes.` | `# replicas = 1` | Explains the temporary constraint. |
| `-- 20261114_add_status: add status for audit; rollback drops it.` | `-- migration` | Intent and rollback are visible. |
| `variable "ttl_days" { description = "Retention; 0 disables expiry." }` | `description = "TTL"` | The doc tool carries the contract. |

## 17. Shell Scripts

- Start with a shebang and a short purpose block: what the script does, its arguments, and the environment it
  needs.
- Comments begin with `#` and must start a word; `echo value#suffix` is not a comment.
- Shell has no block comments; the `: <<'END' ... END` here-document trick is a workaround, not a convention, and
  it must never wrap commands that would execute.
- Explain non-obvious flags, quoting requirements, and error-handling choices next to the line, not in a separate
  legend.
- Document the effect of `set -euo pipefail` and any deliberate exception next to the setting.
- Use linter directives such as `# shellcheck disable=SC2086` with a reason and the narrowest scope.
- Do not leave commented-out commands as usage documentation; put the intended usage in a `usage()` function or
  `--help`.

## 18. Markup, CSS, and Template Comments

- HTML comments (`<!-- ... -->`) ship to the browser; never put secrets, personal data, or internal URLs in them,
  and strip them in production where the build tooling supports it.
- An HTML comment cannot contain `--` and cannot nest; split the comment or use a different delimiter.
- CSS comments use only `/* ... */`; `//` is invalid in plain CSS and valid in Sass/SCSS as a silent comment that
  is not emitted.
- Choose emitted or silent form deliberately in Sass: `/* */` survives to the browser, `//` is for maintainers
  only.
- Template engines add their own syntax: `{# #}` for Jinja, `<%# %>` for ERB, `{{! }}` for Handlebars; never wrap
  a comment in the output language's syntax inside a template.
- JSX and TSX comments are `{/* ... */}`; a bare `//` inside JSX text is rendered as text.
- Use comments for structure, accessibility intent, and conditional inclusion; keep marketing copy and legal
  notices in content or in the build tool.

## 19. i18n and Localized Comments

- Declare one natural language for comments per repository and apply it to every file; mixed-language comments are
  a review defect.
- Keep identifiers, API field names, protocol terms, and quoted upstream text in their original language; never
  translate a symbol name in prose.
- In a localized codebase, use the declared language for domain, regulatory, or legal context that local teams
  need.
- Do not use comments as a translation source for user-facing text; user text belongs in resource files and i18n
  keys.
- Avoid non-ASCII characters when the toolchain, encoding, or terminal breaks them; document the encoding policy
  where it matters.
- Keep punctuation consistent with the declared natural language; the identifier casing rules of the code still
  apply.
- When a comment references a localized document, cite its path and section, not a translated title that may
  change.

## 20. Secrets and Privacy in Comments

- Treat comments as public: they ship in source, generated docs, debug symbols, and packages; never place
  credentials, tokens, keys, or connection strings in them.
- Commented-out code is a common leak channel; check it for embedded credentials before removing it.
- Never add real names, emails, phone numbers, addresses, customer IDs, or production URLs to an example; use
  `example.test.invalid` and placeholder identifiers.
- Do not describe the internal network, service topology, or hostnames in a public or vendored comment.
- Redact incident details in comments; point to the private tracker instead of pasting the report.
- A secret found in a comment is an incident: remove it, rotate it, and follow the disclosure process; deleting
  the line is not enough once it is committed.
- Scan for secret patterns in the pre-commit hook and CI, with comments included in the detection scope.
- When redacting, replace the value with an obvious placeholder such as `REDACTED`; an empty value reads as genuine
  absence.

## 21. Comment Density, Line Width, Punctuation, and Capitalization

- Write comments in complete sentences with sentence case and end punctuation; keep one idea per comment.
- Follow the project's line-width limit (commonly 100 or 120 columns) and wrap continuation lines to it; never
  reflow unrelated comments.
- Separate a block comment from the code it describes with one blank line; keep an end-of-line comment only for a
  short, line-local note.
- Capitalize the first word and follow the comment language's punctuation; reserve all caps for established
  markers such as `NOTE:` and `WARNING:`.
- Avoid ASCII art, banner separators, and alignment padding; they break with formatting tools and create diff
  noise.
- Comment density tracks surprise, not line count: comment the non-obvious; both dense per-line narration and zero
  comments are review findings.
- Keep comments ASCII where the toolchain demands it and strip trailing whitespace; let the formatter own
  indentation.

| Good | Bad | Why |
|---|---|---|
| `// Reuse the pooled client: TLS handshakes dominate this path.` | `// get client` | Explains the choice, not the call. |
| `# Start inclusive, end exclusive; empty when start equals end.` | `# range` | States the convention a reader would guess wrong. |
| `/* The partner API treats 429 as retryable after 30 s. */` | `/* 30 s */` | Keeps the external constraint with the value. |

## 22. Stale and Lying Comments

- A false comment is worse than no comment; it sends the reader confidently in the wrong direction and is a defect
  with a fix deadline.
- Every behavior change includes a comment audit: search for the old function name, parameter, default, return
  type, and error text.
- Comments that reference removed code, deleted files, old versions, or dead tickets must be deleted, not kept for
  context.
- A comment that is true but no longer necessary (a trivial restatement) is also stale; delete it when the code is
  clear.
- Automate detection: doctests run in CI, link checkers catch dead references, and doc-tool warnings fail the build
  only when CI promotes them (`RUSTDOCFLAGS=-D warnings`, Sphinx `-W`, doclint as errors).
- In review, read the comment first and the code second; if the two disagree, the change is incomplete.
- A TODO or deprecation that outlives its trigger is a lying comment; flag overdue markers with a scheduled check.
- Cite symbols and sections, not line numbers or file paths, in a comment; line references rot on the next edit.

## 23. Refactoring and Moving Comments

- Move a comment with the code it explains; a doc comment belongs to the declaration, not to the call site or the
  old file.
- When extracting a function, move the contract to the new declaration and keep only the call-site rationale at
  the caller.
- When inlining a function, absorb its contract into the surrounding doc comment only if the promise still holds;
  otherwise delete it.
- When splitting a function, split its documented contract by responsibility; do not copy the whole comment to
  both halves.
- Update every reference when a symbol, parameter, or section moves: generated doc links, anchors, and cross-file
  pointers.
- Do not "preserve for history" a comment about code that moved; version control tracks the move and a stale copy
  is a lie.
- After a rename, search comments, docs, and examples for the old name; a comment that still uses it is a defect.
- When code moves into generated or third-party code, delete the old comment and record the rationale in the
  tracker or a design note.

## 24. Comment Review Workflow

- In the diff, read every added or changed comment and ask which line of code it protects.
- Check the contract: signature, parameters, returns, errors, side effects, and edge cases still match.
- Check the form: syntax, tags, line width, natural language, and marker spelling.
- Check the hazards: secrets, personal data, internal addresses, and copied third-party text.
- Verify the doc build, doctests, and comment linter; a comment-only change still runs them.
- Remove markers whose trigger has passed; turn untracked TODOs into linked issues or delete them.
- When a comment duplicates a standalone document, link the document and keep only the delta the reader needs.
- Report comment defects separately from behavior defects so the author can tell what must change.
