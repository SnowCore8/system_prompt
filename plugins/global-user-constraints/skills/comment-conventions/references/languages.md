# Language Comment Conventions

Read this file after `SKILL.md`. It overrides the language-agnostic defaults with the exact comment syntax, doc
tool, and dominant style per language. Follow the project's configured tool and linter; where a language has no
single convention, use the defaults in `SKILL.md`.

## Matrix

| Language | Doc comment | Line | Block | Doc tool |
|---|---|---|---|---|
| Python | `"""..."""` | `#` | none; use `#` per line | Sphinx, pydoc |
| TypeScript / JavaScript | `/** ... */` | `//` | `/* ... */` | TSDoc / JSDoc, TypeDoc |
| Java | `/** ... */` | `//` | `/* ... */` | Javadoc |
| Kotlin | `/** ... */` | `//` | `/* ... */` | Dokka |
| C# | `/// <summary>` | `//` | `/* ... */` | XML docs, DocFX |
| Go | `//` above the declaration | `//` | `/* ... */` (rare) | godoc, `go doc` |
| Rust | `///` outer, `//!` inner | `//` | `/* ... */` (rare) | rustdoc |
| C / C++ | `/** ... */` or `///` | `//` | `/* ... */` | Doxygen |
| Ruby | `#` above the method | `#` | `=begin` / `=end` | RDoc, YARD |
| PHP | `/** ... */` | `//` | `/* ... */` | phpDocumentor |
| Swift | `///` | `//` | `/* ... */` | DocC |
| Dart | `///` | `//` | `/* ... */` | dartdoc |
| SQL | `--` header | `--` | `/* ... */` | none; `COMMENT ON` for schema |
| Shell | `#` purpose block | `#` | none; here-document workaround | `--help`, man page |
| HTML / CSS | `<!-- -->`, `/* */` | none; Sass only `//` | `/* ... */` | style guide, static site |
| YAML / TOML | `#` | `#` | none | schema or config reference |
| Terraform / HCL | `#` | `#` or `//` | `/* ... */` | terraform-docs |
| Markdown / XML | `<!-- ... -->` | none | `<!-- ... -->` | doc generator, schema docs |

## Python

- Docstrings use `"""..."""` with an imperative summary; PEP 257 puts closing quotes of a multi-line docstring on
  their own line.
- Choose one field style and keep it: Sphinx reST (`:param name:`), Google (`Args:`), or NumPy; Sphinx autodoc
  parses the configured style.
- `#` is the only line comment and an unassigned string literal is dead code; markers are `# TODO(owner): ...`,
  `# FIXME:`, `# NOTE:`, `# HACK:`, directives are `# noqa: E501`, `# type: ignore[code]`, `# fmt: off`.
- Sphinx reads `#:` comments above attributes as field docs; use them only where a docstring cannot reach.

## TypeScript and JavaScript

- TSDoc and JSDoc comments are `/** ... */` above the declaration with `@param`, `@returns`, `@throws`,
  `@remarks`, `@example`, `@deprecated`, `@internal`; TypeDoc and JSDoc render them.
- `//` is the default line comment; `/* ... */` is for temporary disabling and license blocks, not API docs.
- Directives are `// @ts-expect-error` (always with a reason), a top-of-file `/// <reference types="node" />` or
  `/// <reference path="./types.d.ts" />`, and `// eslint-disable-next-line rule -- reason`; `// @ts-ignore` is a
  last resort.
- In plain JavaScript, `@typedef` and `@property` describe object shapes; in TypeScript, prefer real types to JSDoc.

## Java

- Javadoc `/** ... */` covers every public type and member; the first sentence is the summary shown in indexes.
- Tags are `@param`, `@return`, `@throws`, `@deprecated`, `@see`; inline forms are `{@link Type#member}`,
  `{@code text}`, and `{@literal}`.
- doclint requires closed block tags (`<ul>`, `<li>`, `<table>`, `<pre>`), escaped `<` and `&`, and no stray `</p>`
  (older doclint reports it as an error); `@todo` is not standard, so use a `TODO:` comment; `package-info.java`
  and `module-info.java` document packages and modules.
- `{@inheritDoc}` pulls the contract from the overridden method; use it instead of copying the parent doc comment.

## Kotlin

- KDoc `/** ... */` sits above the declaration with `@param`, `@return`, `@throws`, `@property`, `@receiver`,
  `@sample`, `@see`; link symbols with `[Foo]`, and Dokka renders it.
- `//` never reaches the API reference; block comments nest, and `// region` and `// endregion` only fold sections.
- Markers are `// TODO:`, `// FIXME:`, `// HACK:`; deprecation uses `@Deprecated("Use X")`, not a comment.
- Dokka renders `@sample` functions into examples; keep the sample in test sources and reference it from KDoc.

## C#

- XML documentation comments use `///` with `<summary>`, `<param name="x">`, `<returns>`,
  `<exception cref="T">`, `<remarks>`, `<example>`; DocFX or Sandcastle renders them.
- Write one summary sentence per member; `<inheritdoc/>` reuses a base or interface contract instead of copying it.
- `//` and `/* ... */` are ordinary comments; CS1591 warns about missing public docs when
  `GenerateDocumentationFile` is on; `// TODO:` is not extracted automatically.
- CS1572 and CS1573 flag mismatched `<param>` tags; enable those warnings where XML docs are generated.

## Go

- A doc comment is a `//` block directly above the declaration with no blank line; it starts with the identifier
  name, ends with a period, and is rendered by `go doc` and pkg.go.dev.
- The package comment goes immediately above `package` and starts `// Package billing ...`.
- `//go:` directives (`//go:generate`, `//go:build`, `//go:embed`) have no space after `//`; deprecation is the
  exact sentence `// Deprecated: use X instead.`; TODOs follow `// TODO(owner): ...`.
- Keep one package comment per package, in one file; repeating it in every file yields duplicate package docs.

## Rust

- Outer doc comments use `///` and inner module or crate docs use `//!`; rustdoc sections `# Examples`, `# Panics`,
  `# Errors`, and `# Safety` carry the contract.
- Fenced examples run as doctests (`# ` hides setup); every `unsafe` block needs a `// SAFETY:` comment;
  `#[deprecated(since = "1.2.0", note = "use X")]` carries deprecation.
- Markers are `// TODO:`, `// FIXME:`, `// HACK:`; `#[doc(hidden)]` and `#[allow(clippy::...)]` replace comment
  suppression.
- `cargo doc --document-private-items` renders private docs too, so private doc comments must stay accurate as well.

## C and C++

- Doxygen is dominant: `/** ... */` or `///` with `@param`, `@return`, `@throws`, `@brief`, `@warning`, `@note`,
  `@deprecated`, and `@file`.
- `//` and `/* ... */` are the comment forms; blocks do not nest, and a `//` ending in a backslash splices the
  next line.
- Keep header guards and license headers above `@file`; directives are `// clang-format off`, `// NOLINT(rule)`,
  and `// fallthrough`; project `.clang-format` and `.clang-tidy` outrank these defaults.
- Document macros beside their definition; Doxygen sees the definition and never the expansion at each call site.

## Ruby

- RDoc or YARD doc comments are `#` lines directly above the method or class, with `@param [Type] name`,
  `@return [Type]`, `@raise`, `@example`, and `@deprecated`.
- `=begin` and `=end` must start in column 1; prefer `#` except for large blocks; `:nodoc:` hides an internal API
  from generated docs.
- Magic comments come first (`# frozen_string_literal: true` after the shebang); directives are
  `# rubocop:disable Rule -- reason` and `# rubocop:todo`.
- A `#` comment separated from the method by a blank line is not a doc comment; keep the doc comment directly adjacent.

## PHP

- phpDocumentor docblocks are `/** ... */` above the declaration with `@param`, `@return`, `@throws`, `@var`,
  `@deprecated`, `@internal`, and `@see`.
- `//` and `#` both start line comments, so use `//` consistently; `/* ... */` documents nothing; PHP 8 attributes
  (`#[Route(...)]`) are code, not comments.
- Directives are `// @phpstan-ignore-next-line` and `// phpcs:ignore Rule -- reason`; Psalm suppresses with a
  `/** @psalm-suppress IssueName */` docblock on the enclosing declaration; deprecation is `@deprecated` plus
  `trigger_error(..., E_USER_DEPRECATED)`.
- The file docblock follows `declare(strict_types=1)`; a class docblock sits immediately above the class.

## Swift

- DocC uses `///` with `- Parameter name:`, `- Returns:`, `- Throws:` and callouts `> Important:`, `> Note:`,
  `> Warning:`.
- `// MARK: -`, `// TODO:`, and `// FIXME:` are Xcode conventions; `// swiftlint:disable rule` is a lint directive.
- `/* ... */` nests in Swift but is for temporary disabling; `@available(*, deprecated, message: "Use X.")` carries
  deprecation in the API.
- DocC symbol links use doubled backticks; broken links surface as doc warnings, so recheck them after a rename.

## Dart

- dartdoc reads `///` above declarations; `//` is a line comment and `/* ... */` a nestable block comment, but
  `///` is the documented style; `dart doc` renders it.
- Reference symbols in brackets (`[Foo]`) and use doc sections such as `## Examples`.
- Directives are `// ignore: rule_name` and `// ignore_for_file: rule_name` with the reason; markers are
  `// TODO(owner): ...` or `// TODO: <issue>`, with `FIXME:` and `HACK:`.
- Document a library on its `library;` directive; dartdoc renders that doc comment as the library page.

## SQL

- `--` is the standard line comment and `/* ... */` the standard block comment, which does not nest in most
  dialects; MySQL accepts `#`, but portable migrations should not use it.
- MySQL `/*! ... */` executes its contents and is not a comment; schema docs belong in PostgreSQL
  `COMMENT ON TABLE ... IS '...'` or in the migration header.
- A migration header states ticket, intent, and rollback; applied migrations are immutable; use
  `-- TODO(owner): ...` and directives such as `-- noqa: rule`.
- Directive dialects differ: sqlfluff reads `-- noqa: rule`, while optimizer hints such as `/*+ ... */` are code.

## Shell

- `#` is the only comment syntax and must start a word, so `echo value#suffix` is not a comment.
- Start with a shebang and a block stating purpose, usage, arguments, and required environment variables; explain
  `set -euo pipefail` and any deliberate exception at the setting.
- ShellCheck directives are `# shellcheck disable=SC2086` (with a reason) and `# shellcheck shell=bash`; there is
  no block form, and `: <<'END' ... END` is a rare workaround.
- A `# shellcheck disable=SC2086` line applies to the next command; place it immediately above that command.

## HTML and CSS

- HTML comments are `<!-- text -->`; they cannot contain `--` or nest, and they remain in served source unless the
  build strips them.
- Plain CSS has only `/* ... */`; `//` is invalid there, while Sass and SCSS treat `//` as silent and `/* ... */`
  as emitted.
- JSX and TSX comments are `{/* ... */}`; templates add `{# #}` (Jinja), `<%# %>` (ERB), and `{{! }}` (Handlebars);
  Stylelint and Prettier directives go on the narrowest node with a reason.
- Legacy IE conditional comments are obsolete; use feature detection in code, not a markup comment.

## YAML and TOML

- Both use `#` to end of line; a `#` inside a quoted scalar is data, and YAML needs whitespace before `#`.
- Keep the comment above the key it explains; end-of-line comments wrap poorly in nested structures.
- JSON has no comment syntax: never use `//` or `/* ... */` in strict JSON; explain in the schema, a sibling
  Markdown file, or a `description` field; JSONC and JSON5 are only for config tools that document support.
- `$comment` is a legal JSON Schema key, while a `_comment` data key pollutes the schema; Helm uses `#` in YAML
  and `{{/* ... */}}` for Go-template comments.

## Terraform and HCL

- `#` is the canonical single-line comment (`//` parses but misses the style guide); `/* ... */` is a block
  comment.
- `description` attributes are documentation that `terraform-docs` renders; a `#` above a block carries rationale,
  and references or `moved` blocks express dependencies.
- Scanner directives are `# trivy:ignore:<ID>`, `#tfsec:ignore:<rule>`, and `# tflint-ignore: <rule>`; only tflint
  documents an inline reason, so put the reason in an adjacent comment for the other two.
- Terraform has no deprecation annotation: the source comment states the replacement and removal, while the README
  announcement belongs to the documentation skill.

## Markdown and XML

- Markdown comments are `<!-- ... -->`; rendered output strips them but the source keeps them, so never put
  secrets or private notes there.
- Tooling directives are `<!-- markdownlint-disable rule -->` and `<!-- prettier-ignore -->`, kept next to the
  affected block.
- XML comments cannot contain `--`, cannot nest, and cannot precede the XML declaration; C# XML documentation is
  the main XML doc-comment system; front matter is data, not a comment.
- Keep Markdown comments on their own line; inside a table row or fence they can break the block or render literally.

## Cross-Language Rules

- Match comment syntax to the file's language, not to the project or the editor default.
- Place a doc comment exactly where the tool reads it; one line off turns it into prose that generated docs drop.
- Use the language's marker spelling and the project's configured scanner.
- Carry deprecation in the language mechanism where one exists, and in the doc comment otherwise.
- Line width, natural language, and capitalization follow the project rule in every file type.
