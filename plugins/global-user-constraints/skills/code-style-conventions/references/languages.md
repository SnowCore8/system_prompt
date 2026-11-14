# Language Style Conventions

Read this file after `SKILL.md`. It supplies the formatter, linter, line width, and import-order default for each
language, plus the tool-specific rules that override the language-agnostic defaults. A configured project value wins
over every number here; when the project already sets a stricter value, follow the project.

## Matrix

| Language | Formatter | Linter | Line width | Import order |
|---|---|---|---|---|
| Python | Black, Ruff format | Ruff | 88 | stdlib, third-party, first-party |
| TypeScript / JavaScript | Prettier or Biome | ESLint or Biome | 80 | builtin, external, internal, relative |
| Java | google-java-format | Checkstyle, SpotBugs | 100 | static imports first, then ASCII-sorted |
| Kotlin | ktlint | detekt | 140 (ktlint official); detekt defaults to 120, align explicitly | lexicographic, IDE groups |
| C# | dotnet format | Roslyn analyzers, StyleCop | 120 as a review rule | `System` first, then alphabetical |
| Go | gofmt, goimports | go vet, staticcheck | no limit | stdlib, third-party, local prefix |
| Rust | rustfmt | Clippy | 100 | alphabetical per `use` block |
| C / C++ | clang-format | clang-tidy | 80 LLVM and Google, 120 Microsoft | own header, C, C++, third-party, project |
| Ruby | RuboCop | RuboCop | 120 | not enforced by default |
| PHP | PHP-CS-Fixer | PHPCS | 120 soft limit | alphabetical, one per statement |
| Swift | swift-format | SwiftLint | 100 | alphabetical, `sorted_imports` opt-in |
| Dart | dart format | dart analyze | 80 | `dart:`, `package:`, relative |
| SQL | sqlfluff format | sqlfluff | 80 | n/a; CTEs top-down |
| Shell | shfmt | ShellCheck | no limit | n/a; source libraries at the top |
| HTML / CSS | Prettier | Stylelint | 80 | n/a; `@import` before other rules |
| YAML / JSON / TOML | Prettier, tombi | yamllint, tombi | 80 common | n/a; anchors before use |

## Python

- Format with Black (`line-length = 88`, `target-version` set to the oldest supported Python) or with Ruff format,
  which is Black-compatible; check with `black --check` or `ruff format --check`. Never run both on one tree.
- Lint with Ruff: the default rule families are `E4`, `E7`, `E9`, and `F`; enable `I` for import sorting and `UP` for
  syntax modernization, and pin one Ruff version in `pyproject.toml`.
- Import order: standard library, third-party, first-party, each block sorted, one blank line between blocks. isort
  with `profile = "black"` and Ruff `I` implement the same order; set the same line length for isort when it is used.
- Double quotes are the default. Black keeps single quotes with `skip-string-normalization`; Ruff format uses
  `quote-style = "preserve"`. Each is a project-level setting, not a per-file one.
- Type checking is a separate gate: mypy or pyright belongs with tests, not with the formatter, and its configuration
  does not change the style rules.

## TypeScript and JavaScript

- Format with Prettier (`printWidth: 80`, `tabWidth: 2`, `semi: true`, `singleQuote: false`,
  `trailingComma: "all"`, `arrowParens: "always"`) from `.prettierrc`, and check with `prettier --check .` in CI.
- Lint with ESLint in flat config (`eslint.config.js`), with `eslint-config-prettier` last so formatting rules do not
  fight Prettier; `typescript-eslint` type-aware rules run as a second pass.
- Biome is a single-tool alternative: formatter plus linter, `lineWidth: 80`, `indentStyle: "space"`, double quotes,
  and organized imports. Choose Biome or Prettier plus ESLint per repository and never run the two pairs together.
- Import order: Node builtins, external packages, internal aliases, parent and sibling paths.
  `eslint-plugin-import` or `simple-import-sort` enforces the order, and `import/no-cycle` catches cycles.
- JSX text, template literals, and long strings are exempt where breaking them changes rendered output; Prettier
  leaves them alone, so a long line there is not a lint failure.

## Java

- Format with google-java-format through the Spotless Maven or Gradle plugin: 2-space indent, 100-column limit,
  imports sorted, unused imports removed with `--fix-imports-only`. Check with `spotlessCheck` in CI.
- Lint with Checkstyle using `google_checks.xml` or the project ruleset. Checkstyle covers imports, blocks, and
  declarations that the formatter does not, so keep it as a gate rather than a report.
- Run SpotBugs for bytecode defects (null handling, resource leaks, bad equality) and fail on high-priority findings;
  it is a bug gate, not a style formatter.
- Import order: static imports first, then non-static, each block ASCII-sorted; no wildcard imports and no unused
  imports, because google-java-format and Checkstyle both enforce it.
- google-java-format does not split long string literals, so an overlong literal is a code change (a resource file or
  a concatenation), not a formatting exception.

## Kotlin

- Format with ktlint in `ktlint_official` code style: 4-space indent and `max_line_length = 140`. Put both in
  `.editorconfig` so the IDE and ktlint read the same value.
- Lint with detekt (`maxLineLength` default 120) for complexity, style, and potential bugs; align its line length with
  ktlint or the two tools will disagree about the same file.
- Import order: lexicographic, no wildcard imports, `java`, `javax`, and `kotlin` grouped per the IDE layout;
  ktlint's `import-ordering` rule enforces it.
- Trailing commas are allowed in declarations and calls (Kotlin 1.4+) and the `trailing-comma` rule can enforce them;
  they keep multi-line diffs append-only.
- A detekt finding the project accepts is baselined with a reason and an owner, never disabled globally in the
  configuration.

## C#

- Format with `dotnet format` (whitespace and style rules from `.editorconfig`) and check with
  `dotnet format --verify-no-changes` in CI. It enforces indentation and spacing but not a column limit.
- Lint with Roslyn analyzers (`CAxxxx`, `IDExxxx`) and StyleCop.Analyzers (`SAxxxx`), with severities set in
  `.editorconfig`; `TreatWarningsAsErrors` turns the chosen set into a gate.
- Line width is a review rule (120 is common), because neither the formatter nor the analyzers wraps a long line.
- Import order: `System` namespaces first, then the rest alphabetically, blank lines between groups; global usings
  live in one file and IDE0005 removes unused usings.
- StyleCop's using-directive placement rule (inside or outside the namespace) is chosen once per repository and
  applied through `.editorconfig`, not per file.

## Go

- Format with `gofmt`, which is mandatory: tabs for indentation, no column limit, no line wrapping. Fail CI when
  `gofmt -l` prints a file; the language leaves no room for a style debate.
- Manage imports with `goimports`, which adds and removes imports and groups the standard library separately from
  third-party packages; use `-local` for the module prefix and one blank line between groups.
- Lint with `go vet` for compiler-adjacent checks and `staticcheck` (`SA`, `S`, `ST` families) for bugs and style.
  Run both with the same Go version as the build.
- There is no line-width rule; a long function or expression is a review concern, and gofmt will not split it.
- Exclude generated `*.pb.go`, mocks, and the vendor tree from linting, and keep dot imports out of production code.

## Rust

- Format with rustfmt (`max_width = 100`, `hard_tabs = false`, `edition` set) and check with `cargo fmt --check`.
  Overrides live in `rustfmt.toml` and apply to the workspace rather than to one crate.
- Lint with Clippy: `cargo clippy --all-targets -- -D warnings` in CI. Allow a specific lint only with `#[allow]` on
  the narrowest item and a written reason.
- Import order is alphabetical inside a `use` block by default (`reorder_imports`); `group_imports =
  "StdExternalCrate"` is an unstable nightly option, so enable it only on a nightly toolchain and keep it consistent
  across the workspace.
- rustfmt does not format code inside macro invocations such as `quote!` or `select!`; format that code by hand and
  accept that the tool will not check it.
- Keep `cargo fmt`, Clippy, and the build on one toolchain, pinned by `rust-toolchain.toml`.

## C and C++

- Format with clang-format from a committed `.clang-format`: `BasedOnStyle` LLVM or Google (80 columns), Chromium
  (80), or Microsoft (120). Set `SortIncludes: true`, `IncludeBlocks: Regroup`, and `IncludeCategories`.
- Lint with clang-tidy from `.clang-tidy` (`bugprone-*`, `modernize-*`, `performance-*`, `readability-*`, and the
  project's `cert-*` subset), on changed files with a `compile_commands.json`.
- Include order: matching header first, then C system, C++ standard library, third-party, and project headers, as
  encoded in `IncludeCategories`; angle brackets for system headers, quotes for project headers.
- Column limits come from the chosen style (80 for LLVM and Google, 120 for Microsoft); preprocessor directives and
  long string literals are not wrapped by the formatter.
- Pin the clang-format and clang-tidy version in CI, because minor releases change formatting and produce large churn.

## Ruby

- Format and lint with RuboCop from a committed `.rubocop.yml`: `Layout/LineLength` defaults to `Max: 120` and
  `Style/StringLiterals` defaults to single quotes. Inherit from a shared gem rather than listing every cop.
- Autocorrect with `rubocop -a` for safe fixes and `rubocop -A` for unsafe ones; review the diff, because an unsafe
  autocorrect can change behavior in edge cases.
- There is no default require-order cop; keep requires ordered standard library, gems, then project files as a team
  rule, and enable a check when the order keeps breaking.
- Set `TargetRubyVersion` in the configuration; without it, cops for newer syntax disable silently and the lint result
  depends on the installed Ruby.
- Exclude generated code, the vendor bundle, and schema dumps from the run, and keep the exclusion list in
  `.rubocop.yml`.

## PHP

- Format with PHP-CS-Fixer on the `@PSR12` ruleset plus project rules (`array_syntax: short`, `single_quote`,
  `declare_strict_types`, `ordered_imports`, `no_unused_imports`); check with `--dry-run --diff` in CI.
- Lint with PHPCS against `PSR12` where the project already uses it. Choose PHP-CS-Fixer or PHPCS as the fixer and
  keep the other as a checker, because two fixers over one tree fight.
- Import order: one class per `use` statement, alphabetical, no unused or duplicate imports; PSR-12 places `use`
  declarations after the namespace.
- PSR-12 sets a 120-character soft limit, 4-space indentation, LF endings, and one class per file; an overlong line is
  a signal to extract, not to disable the limit.
- Wire both tools into Composer scripts so a contributor runs locally the same command CI runs.

## Swift

- Format with swift-format from `.swift-format` (`lineLength: 100`, `indentation: 2`) and check with
  `swift-format lint --strict`; the tool does not sort imports.
- Lint with SwiftLint from `.swiftlint.yml`: `line_length` warns at 120 and errors at 200 by default, and opt-in rules
  such as `sorted_imports` supply the order checks that swift-format lacks.
- Import order: one module per line, alphabetical, with `@testable import` next to its module; enable
  `sorted_imports` when the project wants that enforced.
- Keep one formatter authority: if the project uses 4-space indentation, set it in `.swift-format` instead of letting
  swift-format and SwiftLint disagree.
- Pin both tool versions in CI, because the default rule set and the formatting change between releases.

## Dart

- Format with `dart format`; the default page width is 80 columns, and `--set-exit-if-changed` makes CI fail on
  unformatted code.
- Lint with `dart analyze` from `analysis_options.yaml`, inheriting `package:lints/recommended.yaml` or
  `package:flutter_lints/flutter.yaml`; enable `directives_ordering`, `prefer_single_quotes`, and
  `unnecessary_import`.
- Import order: `dart:` libraries, then `package:` imports, then relative imports, with a blank line between groups;
  `directives_ordering` sorts inside each group.
- Trailing commas control the formatter's layout of argument and collection lists, so an intentional
  one-item-per-line list keeps its trailing comma.
- Generated files such as `*.g.dart` and `*.freezed.dart` are excluded in the analyzer configuration and regenerated,
  never edited.

## SQL

- Format with sqlfluff `format` from one `.sqlfluff` config: set `dialect` and `templater` (`jinja` or `dbt`), keyword
  capitalisation, and indentation; a missing dialect is a configuration error, not a default.
- Lint with sqlfluff rules for layout (`LT`), capitalisation (`CP`), and parsing errors, plus the reference and alias
  rules the project enables; the parser catches invalid SQL before a database does.
- The default line length is 80 (`LT05`); long string literals, DDL column lists, and generated `VALUES` lists carry a
  `-- noqa: LT05` with a reason.
- There is no import order; order CTEs top to bottom in dependency order, one clause per line, and one `SELECT` column
  per line once the list is long enough to hide the source tables.
- Exclude generated DDL and migration files with `.sqlfluffignore`; migrations and schema changes belong to the
  api-and-data conventions skill.

## Shell

- Format with shfmt (`-i 4` for spaces or the default tabs, `-ln bash` matching the shebang) and check with `shfmt -d`
  in CI; leave heredoc bodies and embedded scripts alone.
- Lint with ShellCheck at `--severity=warning`, or `style` for scripts under active change; fix every finding in the
  code rather than suppressing it, and disable a code with `# shellcheck disable=SC2086` plus a reason.
- There is no import order; source libraries at the top before first use, and start scripts with
  `set -euo pipefail` so a failure stops the script.
- shfmt formats indentation and spacing only and has no line-length rule; quote expansions and use `[[ ]]` in bash as
  ShellCheck requires.
- Run both tools on every script, including CI helpers, because a one-line pipeline step is where unquoted variables
  usually hide.

## HTML and CSS

- Format HTML, CSS, SCSS, and JSX with Prettier (`printWidth: 80`, `tabWidth: 2`, `singleQuote: false`,
  `htmlWhitespaceSensitivity: "css"`) and check with `prettier --check`.
- Lint with Stylelint and `stylelint-config-standard` (duplicate selectors, invalid hex colors, shorthand conflicts).
  Stylistic rules moved out of Stylelint, so Prettier owns formatting and Stylelint owns correctness and convention.
- Stylelint enforces neither line length nor property order by default; add `stylelint-order` with one ordering
  (alphabetical or concentric) when the project wants it, and never mix the two.
- `@import` rules precede other rules; selectors, custom properties, and design tokens follow the project's naming
  convention rather than a tool default.
- Exclude inline styles, generated email templates, and third-party embedded HTML from Prettier, because the
  generator or the host owns their layout.

## YAML, JSON, and TOML

- Format YAML and JSON with Prettier (`printWidth: 80`, `tabWidth: 2`) and TOML with tombi; use 80 as the common line
  width, and confirm the tool's current default in its documentation instead of assuming it. JSON has no comments,
  so a commented configuration file is YAML or TOML.
- Lint YAML with yamllint (line length 80, 2-space indentation, truthy-value check) and TOML with tombi; keep one
  configuration file per tool at the repository root.
- There is no import order; YAML anchors are defined before use, JSON keys follow the schema order, and TOML keys stay
  grouped under their table.
- Prettier preserves YAML comments, but anchors and aliases can be rewritten by any tool that reparses the file; treat
  a formatting diff on an anchor-heavy file as a review item.
- Do not format lockfiles or generated manifests with the project formatter; the generating tool owns their byte
  layout, and a reformat reopens a file that should only change when dependencies change.

## Cross-Language Rules

- Run exactly one formatter per file type. When two tools overlap, disable formatting in the second one
  (`eslint-config-prettier`, Stylelint stylistic rules off) instead of accepting whichever runs last.
- Keep one width across tools in one repository: Black 88 with isort 88, Prettier 80 for JSON and HTML as well as
  code, ktlint and detekt on the same maximum.
- Pin formatter and linter versions in the build image, the pre-commit hook, and CI; a version bump is its own change,
  and the formatting diff it produces is reviewed like code.
- Prefer the tool's fix command for mechanical findings, review its diff, then commit; a hand fix for something the
  tool can fix returns on the next run.
- Keep the exclusions in one place per tool: generated, vendored, build output, and third-party trees. An exclusion
  list spread across comments and CI flags cannot be audited.
- Treat a mandatory formatter (gofmt, `cargo fmt`, `dart format`, a project-enforced Black or Prettier) as settled and
  do not spend review time on a debate the tool already resolved.
- Static type checkers, security scanners, and coverage are separate gates; this file lists formatters and linters,
  not runtime analysis.
- A repository with several languages repeats the pattern per language and shares only the editor and CI
  configuration; do not force one language's defaults onto another.
