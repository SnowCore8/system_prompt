---
name: code-style-conventions
description: Defines, reviews, and repairs code style, repository layout, dependency management, configuration handling, and error and log policy for any programming project. Use when choosing formatter and linter rules, adding or removing a dependency, separating environments and validating configuration, reviewing error handling and logging, isolating generated or vendored code, or reconciling inconsistent project layout.
argument-hint: '[path or scope]'
---

# Code Style Conventions

Style, layout, dependency, configuration, and error-handling failures compound: mechanical noise in a diff hides the
one behavioral change a reviewer needed to see; an implicit boundary between modules becomes hidden coupling that
every later change drags along; ambient configuration makes a service behave one way locally and another way in
production; and a swallowed error turns a visible failure into a silent one that surfaces days later. Each problem is
cheap to prevent with one rule and expensive to diagnose after release. This skill gives one decision procedure and a
complete rule set for the mechanical and structural side of code: formatting, source tree and module boundaries,
dependencies, configuration, error and log policy, and generated and third-party code. It serves the author setting up
a repository and the reviewer judging a diff, because the same rules decide where a fact belongs and whether a change
is safe. The rules are language-agnostic; the per-language reference supplies the tool defaults, and a project that
already enforces a different default keeps it. The skill applies in three modes: define the rules when a project
starts, review a change against them, and repair an existing repository in one scoped migration.

## Scope and Precedence

Apply the first rule that fits, and do not mix standards inside one scope:

1. Mandatory tool or project standard. A configured formatter, a linter rule set, `.editorconfig`, compiler warnings,
   and a documented project style guide are not optional; the tool output is the rule.
2. Existing project convention. Read the code, the configuration, and the build scripts before inventing a rule; a
   convention the code follows consistently still outranks this file even when no tool enforces it.
3. This standard's defaults, when the two levels above are silent.
4. Personal preference, which never overrides the three levels above.

- Naming belongs to the naming conventions skill. Identifiers, file and directory names, casing, and naming tables are
  out of scope here; this skill consumes those names and applies them to layout, format, and policy. When a rename and
  a reformat land together, split them, because the rename is the other skill's scope.
- Comments and doc comments belong to the comment conventions skill. The formatter decides how a comment block is
  indented; whether the comment should exist is that skill's decision.
- Standalone documentation and its templates belong to the documentation conventions skill. Configuration reference
  pages and runbooks are documents; the keys they describe follow this skill.
- API contract design and database schema and data-retention process belong to the api-and-data conventions skill.
  This skill covers general code craft inside a service, not the shape of its external contract.
- Tests, quality gates, and the development environment belong to the testing-and-quality conventions skill. A
  formatter or linter gate lives in CI; which gates are mandatory is that skill's decision.
- CI/CD pipelines, releases, observability field schemas, incident response, and backups belong to the
  release-operations conventions skill. Log levels and log content policy stay here; where logs are stored, indexed,
  and alerted on stays there.
- Instruction and prompt files belong to the system prompt authoring skill; they are not application code and do not
  follow this skill's formatter or lint rules. A prompt file reviewed for style is reviewed against its own skill.
- Generated and vendored code is exempt from edits but not from the rules below: keep the generation marker, keep
  vendored files untouched, exclude both from formatters and linters, and regenerate or re-vendor instead of editing.
- Enforcement stays in the repository. A rule without a formatter, linter, test, or review checkpoint erodes within
  a quarter; put the check where the change happens, keep it visible in CI, and name the command in the guide.
- A style change is a code change. Apply it in one scoped change, keep it out of a behavior change's diff, update the
  formatter or linter configuration that enforces it, update affected docs in the same delivery, and verify on a
  clean checkout. Do not reformat a file you touched for another reason, because the reviewer cannot separate the two
  changes.
- When two rules conflict, state the conflict first, follow the higher-precedence level, and record which rule the
  project deviates from. Following both halfway is a defect.

## Process

1. Find the configured authority. Locate the formatter and linter configuration, `.editorconfig`, package manifest,
   lockfile, configuration loader, and CI commands. Read the project style guide if one exists.
2. Classify the concern. Decide whether it is formatting, layout or a module boundary, a dependency, configuration,
   error or log policy, or generated and third-party code. A change that spans classes is a plan, not one edit, and a
   concern that fits two classes needs two changes with their own verification.
3. Decide whether the linter already enforces it. If a rule exists, fix the violation instead of documenting a
   convention. If no rule exists, either add one rule in its own configuration change or record the convention in the
   project style guide.
4. Make the smallest config or code change. Prefer one configuration line or one scoped code change; do not reformat
   unrelated files, and do not raise a tool version inside a style fix.
5. Verify on a clean checkout. Run the formatter check, the linter, the build, and the relevant tests through the
   project's documented commands, then paste the actual output and exit codes. A check that passes locally and fails
   in CI means the tool versions or the checkout state differ; align them before changing rules.
6. Update docs and config in the same change. A rule needs its enforcing configuration and one line in the project
   style guide; a dependency needs the manifest, lockfile, and license notice; a config key needs the reference page.
7. Review the diff. Confirm only intended files changed, no generated or vendored file was edited, no secret appears,
   no behavior change hides inside formatting, and the change can be reverted on its own. State the verification
   command and its exit code in the delivery instead of a claim that it passed.

## Core Rules

- **The formatter owns whitespace.** Run the configured formatter instead of hand-wrapping, aligning, or re-indenting;
  a hand edit is undone by the next run and becomes review noise in the meantime.
- **One line width, set in configuration.** Read the width from the formatter config and wrap code at it; keep string
  literals, URLs, hashes, and data tables unbroken because they cannot be split without changing meaning.
- **Mechanical changes are reviewed by tool output, not by eye.** A formatting-only change carries the formatter
  command in its description and nothing else; a behavior change never contains a reflow.
- **Import order states dependency structure.** Group imports as standard library, third-party, and project, sort
  inside a group, and ban wildcard imports; the ordering makes a boundary violation visible before a test fails.
- **Dependencies point one direction.** Domain and application code import no infrastructure; adapters implement
  interfaces the domain owns, so replacing a database or a queue never reaches into business rules.
- **Every module declares its public surface.** Expose named exports, keep the rest unimportable, and import another
  module only through its surface; an import of an internal path is a boundary violation, not a shortcut.
- **Use only declared dependencies.** Import a package because the manifest declares it, never because another
  dependency installed it; import what is declared and declare what is imported.
- **Adding a dependency is a design decision.** Check the standard library and existing dependencies first, then
  maintenance, known vulnerabilities, license, install footprint, and an exit path, and record the evidence.
- **Configuration has one documented precedence order.** Apply flags over environment variables over config files over
  compiled defaults, load and merge once at startup, and forbid modules from reading the environment on their own.
- **Validate configuration once, at startup.** Check required keys, types, ranges, and combinations against a schema,
  name the failing key, and refuse to start instead of failing later under load.
- **Secrets never enter code, configuration, logs, or errors.** Reference a secret by name and resolve it at runtime
  from the store security owns; mask or omit it everywhere it could be written down.
- **Catch only what you can handle.** Handle the failure, add context and keep the cause, or let it propagate; an empty
  catch and a log-and-rethrow both destroy the evidence the next responder needs.
- **Log once, structured, at a level that states who should act.** Emit stable fields at the boundary that decides the
  outcome; ERROR means a person must act, and no log line contains secrets or unmasked personal data.
- **Generated code is never hand-edited.** Change the generator, schema, or template and regenerate; keep a local
  patch outside the generated tree with an owner and an upstream reference, and remove it when upstream fixes it.

## Style Decision Matrix

| Concern | Default rule | Where the rule lives | Example |
|---|---|---|---|
| Formatting | Configured formatter rewrites files; reviewers never debate whitespace | Formatter config and pre-commit hook | `ruff format`, `prettier --write`, `gofmt -w` |
| Line width | One value per language read from config; wrap code at it | Formatter config | `line-length = 100`, `"printWidth": 100` |
| Import order | Standard library, third-party, project; sorted inside a group | Lint rule or formatter | Ruff `I001`, `import/order`, goimports |
| Block structure | Braces where optional; extract instead of nesting past three levels | Linter rule and review | `curly`, `max-depth`, early return |
| Module surface | Named public exports; internals unimportable across a boundary | Package config and lint rule | `__all__`, `internal/`, `pub(crate)` |
| Dependency direction | Infrastructure depends on domain; domain imports no infrastructure | Import rules and review | `dependency-cruiser`, `import-linter` |
| New dependency | Admission needs a need, health, license, and footprint check | Pull request checklist | `cargo deny`, `pip-audit`, license scan |
| Version pinning | Applications pin exact versions; libraries declare ranges; lockfile committed | Manifest and lockfile | `package-lock.json`, `uv.lock`, `go.sum` |
| Config policy | Flags over environment over file over default; validate at startup | Config loader and schema | `APP_PORT` overrides `config.yaml`; `APP_PORT=0` exits non-zero |
| Error wrapping | Add operation context, keep the typed cause, log once at the boundary | Code convention and lint rule | `raise InvoiceSyncError(...) from exc`, `%w` |
| Log content | Events with stable fields; no secrets, tokens, or full personal data | Logger config and review | `logger.error("invoice.sync_failed", error_code="E_SYNC")` |
| Generated code | Regenerate, never edit; CI fails when committed output differs | Generator config and CI job | `git diff --exit-code -- gen/` |

## Dimension Index

| No. | Dimension | First rule |
|---|---|---|
| 1 | Code style and formatting | One configured formatter owns whitespace; line width, quotes, and import order are config values. |
| 2 | Layout, modules, and boundaries | Pick one organizing axis, expose one public surface per module, and point dependencies inward. |
| 3 | Dependency management | Declare direct dependencies only, commit one lockfile, and admit a dependency against written criteria. |
| 4 | Configuration management | Fix the precedence order, validate the merged result at startup, and keep secrets out of every source. |
| 5 | Error handling and logging | Wrap with context and keep the cause; log once, structured, with stable fields and no personal data. |
| 6 | Generated and third-party code | Mark generated output, never edit it, regenerate in CI, and isolate vendored code with provenance. |

## Anti-Patterns

| Anti-pattern | Why it fails | Fix |
|---|---|---|
| Hand-wrapping lines to a width the formatter ignores | The next run rejoins them, so the diff is churn twice over | Set the width in config and let the formatter wrap |
| Reformatting a whole file inside a behavior change | The real change disappears into noise and rollback is all or nothing | Land formatting as its own scoped change first |
| Wildcard imports such as `from x import *` or `import java.util.*` | Hides where a name comes from and breaks when the dependency changes | Import names explicitly and enforce the rule |
| `utils/`, `helpers/`, or `common/` as an unowned directory | Attracts unrelated helpers, then cycles and unclear ownership | Name the responsibility and give the module an owner |
| Fixing an import cycle with a suppression comment | The coupling stays and the next cycle is hidden too | Invert with an interface or move the shared type down |
| Importing a transitive dependency directly | Disappears when the intermediate dependency changes; not declared | Declare the dependency or use the owning API |
| Deleting the lockfile to clear a conflict | Installs unreviewed versions and destroys reproducibility | Resolve the conflict, regenerate, and review the lock diff |
| Using `latest` or an unpinned tool in a production build | The build changes without a commit or review | Pin a version or image digest and bump deliberately |
| Branching on the environment inside business logic | Tests cover one branch and production runs another | Load typed config at the edge and inject it |
| Defaulting a required config key to an empty or plausible value | The service starts and fails at the first request instead of at boot | Validate at startup and name the missing key |
| Committing `.env` or a secret value "temporarily" | It persists in history after the temporary need ends | Reference the secret store and ignore the local file |
| Empty catch, or catch-log-rethrow at every layer | The failure disappears or duplicates while the cause is lost | Handle it, wrap it with context, or propagate it |
| Logging full requests, responses, or interpolated personal data | Copies personal data into log storage and alerts | Log stable fields, IDs, and masked values only |
| Editing a generated file directly | The next regeneration deletes the edit without a trace | Change the generator input and regenerate |
| Running the formatter over generated or vendored trees | Regeneration produces churn and upstream patches conflict | Exclude those trees and keep the exclusion visible |
| Committing build output the pipeline can rebuild | Every branch conflicts on a binary artifact with no provenance | Ignore the directory and rebuild it in the pipeline |

## Review Checklist

- [ ] The formatter check passes without rewriting any file.
- [ ] The configured linter passes with the project rule set.
- [ ] No code line exceeds the configured width, and no hand-wrapped line will be rejoined.
- [ ] Imports are grouped and sorted; no wildcard and no unused import remains.
- [ ] Each module has an explicit public surface and no internal import crosses it.
- [ ] No import cycle exists; dependencies point from infrastructure toward the domain.
- [ ] Every imported package is declared directly in the manifest.
- [ ] A dependency addition or removal carries the admission evidence and the lockfile change.
- [ ] The lockfile is committed and CI installs in frozen mode.
- [ ] Configuration precedence is documented and the merged configuration is validated at startup.
- [ ] Required configuration has no silent fallback in call sites.
- [ ] No secret value appears in code, configuration, fixtures, logs, or examples.
- [ ] Caught errors add context and keep the cause; no empty catch and no log-and-rethrow.
- [ ] Internal failures map to the public contract's codes at the boundary, with no parallel catalogue.
- [ ] Logs are structured, carry the agreed fields, and use the level that matches who must act.
- [ ] No secret, token, full request body, or unmasked personal data appears in a log line.
- [ ] Generated files carry a marker and were regenerated, not edited; vendored files are untouched.
- [ ] The configuration and documentation that describe the behavior changed in the same delivery.
- [ ] The change is one scoped commit that can be reverted without touching another concern.
- [ ] No build output, cache, or vendored file appears in the diff unless it is a reviewed input.

## Examples

<example>
A pull request changes one function and also reflows 400 lines of a second file. Split it: commit the formatter run on
the second file as a mechanical change with only the formatter command, then land the behavior change against a clean
file so the diff shows the logic.
</example>

<example>
A service reads `APP_DATABASE_URL` from the environment and falls back to an empty string when it is absent. Replace
the fallback with startup validation that names the key and exits non-zero; prove the failure with a test fixture
that uses `db.example.test.invalid` and no real address.
</example>

<example>
One feature module imports a repository from another feature to reuse a query. Move the query behind an interface
owned by the domain package, or promote the shared type into its own module; never import the other feature's
internal path.
</example>

<example>
A generated API client needs a timeout field. Change the generator template or the schema input, regenerate, and
commit the input and the output together; the generated file stays untouched by hand.
</example>

<example>
A dependency promises to replace 30 lines of parsing. Check the standard library and existing dependencies first,
then maintenance status, license, and install footprint; record the reason in the pull request next to the manifest
and lockfile change.
</example>

## References

Read [references/dimensions.md](references/dimensions.md) for the full rule set behind the six dimensions, one
numbered section each with defaults, good and bad examples, and edge cases. Read it when setting up a repository,
choosing a boundary, or deciding a policy that the formatter and linter do not cover, and read the matching section
before changing a rule in that dimension.

Read [references/languages.md](references/languages.md) for the formatter, linter, line width, and import-order
defaults per language. Read the language row before adding a tool to a project, read the whole matrix when a
repository spans several languages, and treat a project-specific configured value as overriding the row. When a
project has no configured tool chain, start from the matrix row for its main language and add one formatter before
adding any second rule.
