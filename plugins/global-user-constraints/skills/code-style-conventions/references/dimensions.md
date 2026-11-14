# Code Style Dimensions

Use this file with `SKILL.md`. Each numbered section gives the defaults, the decision rule, and the edge cases for one
dimension; a configured tool or a documented project convention outranks every default here. Read the section that
matches the concern, and read `SKILL.md` first for the precedence order and for the boundaries against sibling skills.
Each section states a default, the tool that enforces it where one exists, and the edge case that decides when the
default does not apply.

## 1. Code Style and Formatting

Formatting is the one style class a machine can settle completely. Configure one formatter per language and file type,
run it everywhere, and spend review attention on the decisions no tool can make: width, structure, and exceptions. The
test of a formatting rule is whether a machine can decide it; if a person has to argue the case, the rule is a structure
or naming rule in disguise.

- Name exactly one formatter per file type, keep its configuration in the repository, and pin the tool version in the
  build image or pre-commit hook. Two formatters that rewrite the same file produce an endless loop of changes, and an
  unpinned formatter version reformats unrelated files on the day it updates. Run the check mode in CI and the write
  mode locally, from the same pinned command, so a formatting failure is caught before review.
- Treat formatter output as correct by construction. A reviewer who dislikes a wrapped argument changes the line width
  or the code itself; editing the formatting by hand is undone by the next run, wastes two reviews, and hides whether
  the author understood the rule. Review the configuration diff when the configuration changes, because that diff
  decides the next hundred formatting diffs.
- Set the width once in the formatter config: Black and Ruff format 88, Prettier 80, rustfmt 100,
  google-java-format 100, LLVM and Google clang-format 80, Microsoft clang-format 120, ktlint 140, and RuboCop 120.
  The project configuration wins over every number here, and a width is not a per-file or per-author setting.
- Decide quotes, semicolons, indentation, and trailing commas in configuration, not in code. Black and Ruff format
  normalize strings to double quotes, Prettier defaults to double quotes and semicolons, and Go requires tabs. A
  disagreement with the choice is a configuration change for the project, never an inline override in one file.
- Order imports in three groups: standard library, third-party, project. Sort inside a group, separate groups with one
  blank line, and ban wildcard imports. goimports, Ruff `I`, eslint-plugin-import, and clang-format `IncludeBlocks`
  enforce the grouping; an import that crosses two groups often signals a module boundary that is wrong. Pruning is a
  separate rule: goimports adds and removes imports, Ruff `F401` flags unused imports while `I` only sorts, isort
  removes redundant aliases with `remove-redundant-aliases` enabled, ESLint `no-unused-vars` flags unused bindings,
  and clang-format never removes an include.
- Keep block structure flat: one statement per line, braces in every language that makes them optional, early returns
  instead of `else` after a return, and no nesting deeper than three levels without extraction. A block that needs a
  comment to explain its shape is a function waiting to be extracted. Extract when a block no longer fits one screen or
  when its header comment states a different operation from the code around it.
- Run the formatter over the whole tree from one command and exclude generated, vendored, and build-output directories
  in that configuration. Reformatting generated code hides the real regeneration diff, and formatting vendored code
  turns every upstream patch into a conflict that a future maintainer cannot resolve.
- Configure editor defaults in a committed `.editorconfig`: UTF-8, LF endings, a final newline, no trailing whitespace
  except where Markdown needs it, and per-language indentation. Commit a minimal shared IDE settings file or ignore the
  IDE directory, because a formatter cannot fix a file that one editor saves with the wrong encoding. An editor plugin
  that reformats on save with its own settings is the most common source of mixed diffs; commit its settings or turn
  the plugin off for the repository.

| Good | Bad | Why |
|---|---|---|
| `ruff format` in a pre-commit hook | A reviewer asking for Black at review time | A machine settles whitespace; humans review logic |
| `.editorconfig` with `end_of_line = lf` | CRLF on one machine and LF on another | Line endings stop appearing in every diff |
| `gen/` excluded from Prettier | Reformatting the generated client | Regeneration keeps a small, reviewable diff |
| Imports grouped stdlib, third-party, project | One alphabetical block | Dependency direction is visible before a test fails |
| `line-length = 100` in `pyproject.toml` | Hand-wrapping at 120 | The formatter rejoins hand-wrapped lines |
| Early return instead of an `else` chain | Deeply indented `else` branches | Reads top to bottom and lowers nesting |
| Formatter version pinned in the build image | A `latest` formatter version | Formatting cannot change without a commit |
| One statement per line | `x = 1; y = 2` on one line | Debuggers, coverage, and diffs treat statements separately |

A formatter cannot split a long string, URL, hash, or base64 blob; leave the line long and record the exception rather
than weakening the width for the whole project. A formatter version bump reformats unrelated files, so land the bump
as its own change. Markdown tables, generated data, and minified assets are outside this rule set. For a language with
no formatter, a lint rule is the next authority; for one with neither, write the rule in the project style guide with
one good and one bad example so the next change follows the same shape. A formatting disagreement is settled by a
configuration change with its own review, never by asking reviewers to remember an exception. A file on which the
formatter and the linter disagree is a configuration conflict to resolve, not a file to exempt.

## 2. Layout, Modules, and Boundaries

Layout is where the dependency graph becomes visible. A tree that mirrors the domain keeps changes local, while a tree
that mirrors tools forces one feature to touch every directory, and a boundary that exists only in a diagram is not a
boundary. Layout rules are cheap to state before the second feature exists and expensive to change once imports have
spread, so choose the axis early and write it down where the owner of the next file will look.

- Choose the organizing axis once per project. Feature-first means each feature owns its interface, domain logic, and
  persistence; layer-first means top-level entry, domain, and infrastructure directories. Feature-first keeps a change
  local and suits product code, layer-first suits a small service with one domain, and mixing the axes below the top
  level leaves readers guessing where the next file belongs.
- Keep entry points thin: `main.py`, `cmd/api/main.go`, `src/index.ts`, `Program.cs`. An entry point parses arguments,
  loads configuration, builds dependencies, and calls the application. It contains no business rule, no query, and no
  formatting logic, so replacing the transport or the startup sequence never changes behavior.
- Declare one public surface per module: `__all__` and a leading underscore in Python, `pub` and private modules in
  Rust, `internal/` packages in Go, package-private types in Java and C#, an `index.ts` barrel in TypeScript.
  Everything outside the surface is unimportable from another module, which turns a boundary violation into a build
  error instead of a review comment. A language without a visibility keyword enforces the surface with a package
  boundary plus a lint rule against deep imports.
- Point dependencies inward. Domain and application code import no infrastructure, framework, or third-party SDK;
  adapters implement interfaces the domain owns. The inversion is what lets a test replace a database with an
  in-memory implementation, and what keeps a vendor change away from business rules.
- Forbid import cycles and treat each one as a design finding. Detect cycles with `import-linter` in Python,
  `dependency-cruiser` or `import/no-cycle` in JavaScript, `jdeps` in Java, and the compiler in Go. Break a cycle by
  moving the shared type down or inverting with an interface, never by a suppression comment. `pydeps` and `madge`
  draw the graph, and `ArchUnit` or a small dependency test keeps the rule executable rather than advisory.
- Give a file one cohesive reason to change. Set a team threshold, for example warn at 300 and split at 500 lines of
  application code; split a file that grows a second responsibility even when it is under the count, and exempt
  generated files and data tables from the threshold because their length follows the generator, not the design. The
  threshold is a review trigger that starts a split conversation, not a hard gate that blocks an unrelated change.
- Allow shared code only with an owner and a written definition. A `common/`, `shared/`, or `utils/` module without a
  boundary becomes the place unrelated helpers accumulate and the usual source of cycles. Promote code into a named
  module after the third caller, or keep the duplication because it is cheaper than the coupling. When a shared helper
  must change for two callers at once, split it by responsibility instead of adding a mode flag.
- Move a file only when its responsibility changes location, and keep the move in its own change. A move commit that
  also edits logic is unreviewable because the tool shows a rewrite rather than a rename; a rename-only commit is
  reviewable in seconds and can be reverted on its own. A directory rename follows the same rule and updates ignore
  rules, CI paths, and references in one change, never as a side effect of a feature.

| Good | Bad | Why |
|---|---|---|
| Each feature owns its interface, domain, and store | Global `controllers/`, `services/`, `repositories/` | A feature change stays inside one directory |
| `internal/parser` imported only inside its module | Another module imports `internal/parser` | The boundary is enforced by the compiler |
| Domain imports no ORM or HTTP types | Domain entities import the ORM | Business rules stay testable and replaceable |
| `cmd/api/main.go` builds dependencies and calls in | `main` contains the SQL query | Startup can change without touching rules |
| Cycle broken by an interface owned by the domain | `// noqa` on a circular import | The coupling is removed rather than hidden |
| A 220-line `billing/invoice.py` | A 1800-line `billing/helpers.py` with five roles | One file, one reason to change |
| A named `pdf/` module | `utils/` holding formatting, dates, and parsing | Ownership and purpose are stated |
| Move and edit in separate changes | A rename hidden inside a refactor | Each change can be reviewed and reverted |

Single-file scripts and notebooks do not need a layout; apply the rules when a second module appears. A monorepo
repeats the same tree per package and shares only an explicitly named package, never a relative climb into another
package. Boundaries protect a rate of change: the domain is stable and adapters churn, so dependencies point at the
stable side. Ask of every change which side of a boundary owns the behavior; when the answer is two sides, the boundary
is in the wrong place and the change is about to edit both. A directory that exists to hold one file restates a name
rather than forming a module, and a module without a stated surface is only a folder.

## 3. Dependency Management

A dependency is code the project ships but does not maintain. Each one adds a version constraint, a license, an attack
surface, and a release cadence, so the manifest is a design document rather than a convenience list. The manifest and
the lockfile are reviewed together, and the lockfile diff is the evidence of what actually ships.

- Depend directly only. Import a package because the manifest declares it, not because another dependency installed it.
  A transitive import disappears at the next lock update, is invisible to the manifest review, and cannot be pinned
  independently by the application that relies on it. A dependency imported only by tests or scripts is still a
  declared dependency of the project.
- Commit exactly one lockfile per project and treat it as the build input: `package-lock.json` or `pnpm-lock.yaml`,
  `uv.lock` or `poetry.lock`, `go.sum`, `Cargo.lock`, `Gemfile.lock`, `composer.lock`. Install in frozen mode in CI
  with `npm ci`, `pnpm install --frozen-lockfile`, `uv sync --locked`, `cargo build --locked`, or
  `bundle install --frozen`; never delete a lockfile to make a conflict disappear. Resolve a lockfile conflict by
  regenerating on the target branch and reviewing the result, because a hand-edited lock entry is a state no tool can
  reproduce.
- Pin by role. Applications pin exact versions and image digests so a build changes only when a commit changes it;
  libraries declare a compatible range and test the lowest supported and the latest version. Pin CI tools and base
  images the same way and bump them deliberately, because a floating tool version is an unreviewed dependency. Every
  pin movement states its reason in the change, because an unexplained bump is indistinguishable from a mistake.
- Schedule updates instead of taking them opportunistically. Automated pull requests on a fixed cadence handle patch
  releases, while major versions get a deliberate review of the release notes, deprecations, and breaking changes. Run
  the full build and tests for the upgrade and keep it out of a feature change. Apply a minimum release age to automated
  updates, because a compromised maintainer account can publish a malicious release within minutes and a short delay
  turns an immediate install into a reviewed one.
- Admit a dependency against written criteria: the standard library or an existing dependency cannot do it; the
  package is maintained, with recent releases, responsive issues, and more than one maintainer; no known unpatched
  vulnerability; the license is compatible and recorded; install size and transitive count are acceptable; and an
  owner can remove it. Record the evidence in the pull request, check that the package name and registry origin cannot
  be shadowed by a public package with the same name, and prefer a scoped name for anything internal.
- Remove completely. Delete usages and imports, remove the manifest entry, regenerate the lockfile, then remove
  configuration, environment variables, CI references, and credentials attached to it. A dependency removed from code
  but left in the manifest still ships, still gets scanned, and still produces update noise. Update the license notice
  and the SBOM in the same change when a dependency leaves, so the inventory never describes code that is gone.
- Route private registries through repository configuration: scope and registry in `.npmrc`, an index URL in
  `pip.conf` or the project's package manager config, a mirror in `settings.xml`, repositories in `composer.json`.
  Inject credentials from the environment or a CI secret store, never commit a token, and fail closed when the
  registry is unreachable instead of falling back to a public mirror.
- Hand license and vulnerability decisions to security. Run the scanner in CI with `pip-audit`, `npm audit`,
  `cargo audit`, `govulncheck`, `bundle audit`, or an SBOM and license scanner; record the allowed license set; and
  report a denied or unknown license for approval instead of approving it in code review. An SBOM per release gives
  that handoff a stable inventory and makes a withdrawn dependency visible after it shipped.

| Good | Bad | Why |
|---|---|---|
| A direct manifest entry per imported package | Importing a package that a dependency installed | The manifest states what the project relies on |
| One committed lockfile installed in frozen mode | Deleting the lockfile to clear a conflict | Installs are reproducible and reviewed |
| An application pins `1.4.2` | An application declares `^1.4.2` | A build changes only with a commit |
| A scheduled patch-update pull request | A silent auto-update in production | The change is tested and attributable |
| Admission evidence in the pull request | "It is popular, so it is safe" | Health, license, and footprint are checked |
| Registry and secret injected from CI | A token committed in `.npmrc` | Credentials never enter the repository |
| A license scanner gates the build | Reviewers approving a copyleft license | License risk becomes a recorded decision |
| Manifest entry removed with the last import | Unused dependency left in the manifest | Unused code stops shipping and scanning |

Development-only dependencies belong in the development scope and do not ship in the artifact. Peer and optional
dependencies follow the rules of the ecosystem that defines them. Workspace-internal packages order the build but are
not scanned as external dependencies. An air-gapped build vendors dependencies, and that vendor tree follows the
generated and third-party rules. Keep a dependency budget in both count and total transitive size; when the budget is
exceeded, remove one before adding the next. A pre-release or a commit hash is not a release: use it only when no
version exists, and record why the pin cannot move to a version.

## 4. Configuration Management

Configuration decides how one build behaves in each environment. When precedence is undocumented or validation is
deferred, the same commit behaves differently in two places and the difference appears only under production load.
Configuration is code that runs in every environment, so it receives the same review, versioning, and rollback path as
the code that reads it.

- Fix and document one precedence order: command-line flag, then environment variable, then local config file, then
  shared config file, then compiled default. Load and merge once at startup in that order, and keep one module
  responsible for reading every source so no feature invents a second ladder. Document the ladder in the README and
  exercise the merge with one test per level.
- Use the source that fits the setting's change frequency and secrecy. Safe compiled defaults live in code,
  checked-in environment files hold shared non-secret settings, environment variables or a config service hold
  deployment-specific values, and flags carry one-off operator intent. A secret is referenced by name and resolved
  from the secret store at runtime. When a value must be identical everywhere, it belongs in the shared file or a
  compiled constant, not repeated in each environment file.
- Separate environments by data, not by branch: `config/dev.yaml`, `config/staging.yaml`, and `config/prod.yaml`
  selected by one environment variable. Production configuration is reviewed like code, deployed through the
  pipeline, and never edited in place on a running host where the next deployment silently reverts it. Select the file
  by an explicit environment variable, and make a missing file an error instead of a silent fallback to defaults.
- Do not branch on the environment inside business logic. Load typed configuration at the edge and inject it; a
  conditional such as `if env == "prod"` in a request handler means tests exercise one branch while production runs
  another, and the untested branch is where the incident happens.
- Validate the merged configuration once at startup against a schema: required keys present, type and range correct,
  URL parses, referenced path exists, mutually exclusive options rejected. Name the failing key, state the expected
  form, and exit non-zero before the process accepts traffic. Validate once and pass the result down; validating
  values from request parameters is a different boundary and does not replace startup validation.
- Give every optional key a documented default with a unit and a range, and give required keys no fallback at all.
  Remove hidden fallbacks in call sites such as `timeout or 30`, because they contradict the documented default and
  make behavior depend on whether the value was absent, empty, or zero.
- Pass a typed configuration object to modules instead of a dictionary or direct environment access. A module that
  reads `os.environ` or `process.env` bypasses the precedence ladder, skips validation, and makes its tests depend on
  the developer's shell. Dependency injection or a small config module both satisfy this; the property that matters is
  one read point for the whole application.
- Retire configuration that no longer controls a behavior: no code reads it, two keys control one behavior, or a
  boolean became a permanent path. One behavior has one key, and renaming a key is a migration with a compatibility
  window rather than a rename applied to every deployment at once. A removed key leaves a migration note in the
  reference page and in the change that stops reading it, not only in the configuration file.

| Good | Bad | Why |
|---|---|---|
| Documented flag over environment over file over default | Each module reads its own source | Behavior is predictable in every environment |
| A missing required key exits with its name | A missing URL defaults to an empty string | Failure appears at startup, not under load |
| A typed config object injected into modules | A dictionary passed through five layers | Access is checked and validated once |
| `config/prod.yaml` selected by one variable | `if env == "prod"` inside a handler | The same code path runs everywhere |
| A secret referenced by name | A value committed in `config.yaml` | Storage and rotation stay with security |
| One key per behavior | `TIMEOUT` and `TIMEOUT_MS` both read | No precedence puzzle between duplicate keys |
| Production config through the pipeline | A manual edit on the production host | The change is reviewed and reversible |
| `APP_PORT=0` rejected at startup | First request fails on a bad port | Range checks run before traffic arrives |

Secret storage, rotation, and access policy belong to security; this section owns precedence, validation, and the
fail-fast boundary. Test suites build an explicit configuration fixture rather than reading the developer's
environment, so a green test does not depend on an unexported variable. A long-lived boolean that still selects a
code path is configuration and retires through this section; a flag that changes deployment behavior belongs to
release operations. A configuration change that cannot be rolled back on its own is a deployment risk: keep the
previous value available until the new value shows the expected behavior, then remove it in a later change.

## 5. Error Handling and Logging

Errors and logs are the only witnesses to a production failure. An error that loses its cause, a catch that swallows
it, or a log line without fields turns the incident into a guess and the fix into a search. Handle an error where the
decision can be made and log it where the outcome is known, because a layer that can neither decide nor report only
adds noise.

- Choose one error style per layer: exceptions for unexpected and unrecoverable conditions, result or error values for
  expected domain outcomes such as validation, not-found, or a declined payment. Do not mix both styles in one API,
  and state the chosen style on the module's public surface so callers know whether to catch or inspect.
- Never swallow. Catch only to handle, to add context, or to convert to a result. An empty catch, a catch that logs
  and rethrows at every layer, and a catch-all that maps every failure to one generic error destroy the stack, the
  error type, and the evidence that a responder needs to tell a timeout from a validation bug. Catch the narrowest type
  available, because catching a base type turns a programming mistake into a handled case and hides the fix.
- Wrap with context and keep the cause: `raise InvoiceSyncError(invoice_id=...) from exc` in Python,
  `fmt.Errorf("sync invoice %s: %w", id, err)` in Go, `throw new InvoiceSyncException("...", cause)` in Java. Add the
  operation and a safe identifier, and never replace the cause with a formatted string that discards the stack.
- Give boundary errors stable codes: one code per cause, machine-readable, localized only at display time. Map
  internal errors to public codes at the API edge, and never leak stack traces, SQL, internal hostnames, or exception
  class names to a client, because those reveal topology and implementation details. The public code catalogue, its
  envelope, and the code values are part of the external contract that the api-and-data role defines; map internal
  failures onto those codes at the boundary and do not keep a parallel catalogue here.
- Log an event once, at the boundary that decides the outcome, with stable fields such as `timestamp`, `level`,
  `event`, `service`, `trace_id`, and `error_code`. Lower layers return errors and do not log what an upper layer will
  log again; duplicate lines multiply volume and make the first occurrence ambiguous. The event name is stable and
  low-cardinality, while variable data belongs in fields rather than in the event string.
- Use the level that states who must act: ERROR for a failed user-visible operation that needs a person, WARN for a
  degraded but handled condition worth a look, INFO for lifecycle and business events, DEBUG for diagnostics that stay
  off in production, TRACE only for short investigations. A level is not decoration, and no log level replaces a
  metric or an alert. The level belongs to the outcome rather than to the exception type: the same timeout is WARN
  when it is retried and ERROR when it ends the request.
- Never log secrets, tokens, passwords, cookies, authorization headers, session identifiers, encryption keys, full
  request or response bodies, or full personal data. Log an identifier or a masked value: `user_id` rather than an
  email, `a***@example.test.invalid` rather than a real address, and the last four digits only when a business rule
  requires them.
- Return actionable messages: say what failed and what the caller or user can do, include a correlation ID, and keep
  stack traces and internal topology in the log. At startup, fail with the configuration key or dependency name that
  blocked startup instead of a generic message that sends the responder to the logs without a lead. Name the component,
  the operation, and the correlation ID in the log, and name only the failed step and the next action in the response.

| Good | Bad | Why |
|---|---|---|
| Context added, original cause kept | A bare rethrow or a new message-only error | The chain points at the real failure |
| A handled catch with a recovery path | An empty catch block | A failure is either fixed or surfaced |
| Stable public error code at the API edge | A raw exception returned as HTTP 500 | Clients can act and internals stay private |
| Structured event with named fields | An interpolated sentence with five values | Queries and alerts can match fields |
| ERROR only when a person must act | Every failure logged at ERROR | Severity keeps its meaning |
| `user_id` in the log line | Email, phone, or address in the log | Personal data stays out of log storage |
| One log line at the outcome boundary | The same error logged at four layers | Volume stays down and the cause stays clear |
| Startup names the blocking key | A generic "cannot start" message | The responder has a lead without searching |

Cancellation, timeouts, and shutdown signals are expected conditions rather than errors, and retries must not emit a
fresh error line for each attempt without a final outcome. Library code returns errors and lets the caller decide what
to log. The field schema, dashboards, and alert rules for logs and traces belong to release operations; this section
owns level selection and content policy. Classify failures as retryable or fatal and retry only at one boundary with a
backoff and a cap, because a retry storm multiplies error volume and can turn a partial outage into a full one. A
health check that logs every probe is noise, while one that hides why it is unhealthy is a blind spot.

## 6. Generated and Third-Party Code

Generated and vendored code is owned by a generator or an upstream project, not by this project's style rules. Treat
both as build inputs with provenance, or the next regeneration silently erases every hand edit. The rule is simple:
generated code changes by changing its source, and vendored code changes by changing its version.

- Put generated output in a declared directory or filename pattern such as `gen/`, `generated/`, `*.pb.go`,
  `*_generated.py`, or `*.g.dart`, and add a machine-detectable header naming the generator, its version, and the
  command. Use the ecosystem marker such as `// Code generated by protoc-gen-go. DO NOT EDIT.` or `@generated`, so
  tools can exclude the file automatically instead of a hand-maintained list.
- Never hand-edit generated code. Change the schema, template, or generator invocation, regenerate, and commit the
  input together with the output. A hand edit survives until the next generation and then disappears without a review
  trail, so the fix is lost the moment someone else regenerates. Record the generator version in the header so a
  reviewer can tell which regeneration produced the file.
- When a local change is unavoidable, keep it outside the generated tree: a patch file under `patches/`, an adapter,
  or a wrapper with a pinned upstream version, an owner, an issue link, and a removal condition. The build applies the
  patch, and CI fails if it stops applying instead of shipping a silent divergence.
- Review the inputs, not the generated lines. Review the schema or template diff, the generator version bump, and a
  summary of the regeneration. A large generated diff is expected when the input changed and is suspicious when the
  input did not, which is exactly the signal a line-by-line review of generated code cannot give.
- Regenerate in CI and fail on drift. Run the generator in a job, compare the working tree with the committed output
  using `git diff --exit-code` or the tool's check mode, and report the command that reproduces the output. Stale
  generated code becomes a build failure rather than a review finding that a later change silently contradicts. Use the
  generator's own check mode when it has one; `git diff --exit-code` is the fallback for generators without one.
- Keep vendored code in one isolated directory with provenance: upstream source, version or commit, license text, and
  the reason for vendoring in a manifest or README. Import it through one boundary so a later replacement or upgrade
  touches one file, and treat a copied snippet as vendored code that needs the same provenance and license record.
  Record why the dependency was vendored rather than declared, and revisit that reason at every upgrade.
- Exclude generated and vendored code from formatters, linters, coverage thresholds, and style review, and keep the
  exclusions in tool configuration where they can be audited. Exclusion from tests, search, or security analysis is a
  separate decision, because a style exemption does not imply that unread code is unexamined code. Each exclusion
  carries a comment naming the generator or the upstream project, so a later reader can tell why the file is outside.
- Distinguish generated source from build output. A lockfile or a generated client is committed because it is an input
  to reproduction and review; build directories, caches, compiled binaries, and package-manager trees are ignored and
  rebuilt. A committed build artifact becomes a merge conflict on every branch, and its provenance is undefined. Keep
  ignore rules at the repository root and confirm that a clean clone can rebuild every ignored artifact.

| Good | Bad | Why |
|---|---|---|
| A header naming generator, version, and command | An unmarked file that looks hand-written | Tools and readers can identify and exclude it |
| CI regenerates and diffs the committed output | Stale generated code committed by hand | Drift fails the build instead of a review |
| A patch directory with owner and issue link | A hand-edited vendor file | The patch is visible and removable |
| A vendor manifest with version and license | Vendor code with no provenance | Upgrade and license questions are answerable |
| The generator tree excluded from the formatter | Formatting the generated client | Regeneration produces no churn |
| `dist/` ignored and rebuilt | Build output committed | No merge conflicts on binary artifacts |
| Generator input and version reviewed | Generated lines reviewed one by one | Review attention goes where the decision is |
| A copied snippet with source and license | An unlicensed copy of upstream code | Attribution and license obligations are met |

Generated documentation and migration files are documents and schema changes owned by the documentation and
api-and-data conventions skills; they still carry markers and provenance. IDE-generated and scaffolding output is
generated code even when the project retains it. Regeneration must be deterministic: pin the generator version, sort
its inputs, and exclude timestamps, absolute paths, and machine names from the output so a no-change run produces no
diff. A generated client's public API is an API contract, so the api-and-data review covers the schema while a code
review covers the adapter and error mapping around it. When a generator cannot be pinned, record the output hash in CI
so an unexplained regeneration fails the build.
