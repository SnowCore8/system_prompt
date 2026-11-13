# Language Conventions

Read this file after `SKILL.md`. It overrides the language-agnostic defaults with the mandatory or dominant
convention for each language. When a project already has a stricter local rule, follow the project; when the
language has no single convention, use the default in `SKILL.md`.

## Matrix

| Language | Type | Function or method | Variable or parameter | Constant | File | Test |
|---|---|---|---|---|---|---|
| Python | `PascalCase` | `snake_case` | `snake_case` | `UPPER_SNAKE` | `snake_case.py` | `test_*.py` |
| TypeScript / JavaScript | `PascalCase` | `camelCase` | `camelCase` | `UPPER_SNAKE` | `kebab-case.ts`, `PascalCase.tsx` | `*.test.ts` |
| Java | `PascalCase` | `camelCase` | `camelCase` | `UPPER_SNAKE` | `PascalCase.java` | `*Test.java` |
| Kotlin | `PascalCase` | `camelCase` | `camelCase` | `UPPER_SNAKE` | `PascalCase.kt` | `*Test.kt` |
| C# | `PascalCase` | `PascalCase` | `camelCase` | `PascalCase` | `PascalCase.cs` | `*Tests.cs` |
| Go | `PascalCase` or `MixedCaps` | `MixedCaps` | `mixedCaps` | `MixedCaps` | `snake_case.go` | `*_test.go` |
| Rust | `PascalCase` | `snake_case` | `snake_case` | `UPPER_SNAKE` | `snake_case.rs` | `#[cfg(test)]` or `tests/` |
| C / C++ | `PascalCase` | `snake_case` | `snake_case` | `UPPER_SNAKE` or `kConstant` | `snake_case.c`, `.h`, `.cc` | `*_test.cc` |
| Ruby | `PascalCase` | `snake_case` | `snake_case` | `UPPER_SNAKE` | `snake_case.rb` | `*_spec.rb` |
| PHP | `PascalCase` | `camelCase` | `camelCase` | `UPPER_SNAKE` | `PascalCase.php` | `*Test.php` |
| Swift | `PascalCase` | `camelCase` | `camelCase` | `camelCase` | `PascalCase.swift` | `*Tests.swift` |
| Dart | `PascalCase` | `camelCase` | `camelCase` | `lowerCamelCase` | `snake_case.dart` | `*_test.dart` |
| SQL | table `snake_case`, column `snake_case` | n/a | constraint `snake_case` | n/a | `YYYYMMDD_description.sql` | migration test |
| Shell | n/a | `snake_case` | `snake_case`, env `UPPER_SNAKE` | `UPPER_SNAKE` | `kebab-case.sh` | `*_test.sh` |
| HTML / CSS | class `kebab-case`, BEM | n/a | custom property `--kebab-case` | n/a | `kebab-case.css` | visual test |
| JSON / YAML | object `PascalCase` or `snake_case` | n/a | key one case per schema | n/a | `kebab-case.json` | schema test |

## Python

- Follow PEP 8: `snake_case` functions and variables, `PascalCase` classes, `UPPER_SNAKE` constants.
- Modules and packages are `snake_case`; a package is a directory with `__init__.py`.
- A single leading underscore marks internal use; avoid double-underscore name mangling unless the class hierarchy
  needs it.
- Do not use an `I` prefix for interfaces; protocols and ABCs use a capability name (`Readable`, `UserStore`).
- Test files are `test_*.py` or `*_test.py`; test functions start with `test_` and state the behavior.
- Booleans use `is_`, `has_`, `can_`, `should_`, `needs_`; avoid `not_`.
- Type hints use `UserId` aliases for domain identifiers; do not shadow built-ins (`list`, `dict`, `id`).

## TypeScript and JavaScript

- `camelCase` for variables, functions, and methods; `PascalCase` for classes, types, interfaces, enums, and React
  components.
- Interfaces usually drop the `I` prefix; a type alias is `PascalCase` (`type UserId = string`).
- File names follow the project: `kebab-case.ts` for modules, `PascalCase.tsx` for components, `index.ts` for a
  folder's public surface.
- Tests are `*.test.ts` or `*.spec.ts`; React tests use the same basename as the component.
- Acronyms are words: `userId`, `httpClient`, `parseUrl`; do not use `userID` or `HTTPClient`.
- Boolean variables and predicates use `is`, `has`, `can`, `should`; a function named `isX` must return a boolean.
- Constants are `UPPER_SNAKE` only for true constants; a `const` local binding is still `camelCase`.

## Java

- `PascalCase` classes, interfaces, enums, and records; `camelCase` methods and variables; `UPPER_SNAKE` constants.
- Packages are lower-case reverse domain: `com.example.billing`; no underscores or capitals.
- Avoid an `I` interface prefix and an `Impl` class suffix; name the implementation by mechanism
  (`SqlInvoiceRepository`).
- Test classes end in `Test`; test methods state behavior (`shouldRejectExpiredCard`).
- Acronyms are capitalized as words: `UserId`, `HttpClient`, `UrlParser`; `ID` is usually `Id`.
- A record or DTO at a boundary ends in `Dto`, `Request`, or `Response`; a domain type does not.

## Kotlin

- `PascalCase` classes and objects; `camelCase` functions and properties; `UPPER_SNAKE` constants.
- Files are `PascalCase.kt`, usually named after the primary class; multiple top-level declarations may share a
  file only when they are one concept.
- Packages are lower-case; no underscores.
- Test classes end in `Test`; backticked test names are allowed in tests but production identifiers stay
  `camelCase`.
- Acronyms are words: `UserId`, `HttpClient`, `parseUrl`.

## C#

- `PascalCase` types, methods, properties, events, and constants; `camelCase` parameters and locals; private fields
  use `_camelCase`.
- Interfaces use the `I` prefix (`IUserStore`); generic parameters are `T`, `TKey`, `TValue`.
- Async methods use the `Async` suffix (`LoadAsync`) unless the framework convention says otherwise.
- Test classes end in `Tests`; test methods use `Method_Scenario_Expected`.
- Acronyms follow .NET style: `UserId`, `HttpClient`, `IOStream` only where the acronym is two letters.
- Namespaces are `PascalCase` and mirror the folder structure.

## Go

- Use `MixedCaps`: exported identifiers start upper case (`UserID`, `HTTPServer`), unexported start lower case
  (`userID`).
- Package names are short, lower case, and have no underscores (`billing`, not `billing_service`).
- Do not use `Get` prefixes on getters; the field or method name is the noun (`user.Name()`), and setters may use
  `Set`.
- Test files are `*_test.go`; functions are `TestXxx`, `BenchmarkXxx`, `ExampleXxx`; table tests use `t.Run` with a
  descriptive case name.
- Initialisms are capitalized consistently: `URL`, `ID`, `HTTP`, `API`, `JSON`; `UserID`, `HTTPServer`, `URLParser`.
- Error variables are `err`; wrapped errors use `fmt.Errorf("...: %w", err)` and a sentinel `ErrNotFound`.

## Rust

- `snake_case` functions, methods, variables, modules, and crate names; `PascalCase` types, traits, enums, and
  variants; `UPPER_SNAKE` constants and statics.
- Module files are `snake_case.rs`; `mod.rs` is legacy, prefer `module/` plus `module/mod.rs` only when the project
  uses it.
- Test functions state behavior (`rejects_expired_card`); integration tests live in `tests/` and use the public API.
- Booleans use `is_`, `has_`, `can_`; a predicate returns `bool`.
- Acronyms are words in snake_case: `user_id`, `http_client`, `parse_url`.
- A trait names a capability (`Readable`, `Store`); an implementation type names the mechanism (`SqlStore`).

## C and C++

- There is no universal convention; read the project. Common defaults: `snake_case` functions and variables,
  `PascalCase` types, `UPPER_SNAKE` macros and constants.
- Header guards are `PROJECT_PATH_FILE_H` or `#pragma once`; pick one and keep it.
- Namespaces are lower-case (`billing`); nested namespaces use `billing::internal`.
- Constants may use `kConstant` (Google style) or `UPPER_SNAKE`; follow the project, not both.
- Test files are `*_test.cc` or `*_test.cpp`; test names state behavior.
- Do not use a leading underscore followed by a capital at global scope; it is reserved.

## Ruby

- `snake_case` methods and variables; `PascalCase` classes and modules; `UPPER_SNAKE` constants.
- Predicate methods end in `?` (`valid?`); dangerous methods end in `!` (`save!`); do not use `?` on a method that
  returns a non-boolean.
- Files are `snake_case.rb`; test files are `*_spec.rb` (RSpec) or `*_test.rb` (Minitest).
- Modules used as namespaces are `PascalCase`; nested constants are resolved by the module name.
- Acronyms are words: `UserId`, `HttpClient`, `parse_url`.

## PHP

- `PascalCase` classes, interfaces, traits, and enums; `camelCase` methods; `$camelCase` variables; `UPPER_SNAKE`
  constants.
- PSR-4 file names match the class name: `UserRepository.php`.
- Namespaces are `PascalCase` and mirror the directory structure.
- Test classes end in `Test`; methods start with `test` or use the framework's attribute convention.
- Acronyms are words: `UserId`, `HttpClient`, `parseUrl`.

## Swift

- `PascalCase` types, protocols, and enums; `camelCase` functions, methods, properties, and constants.
- Protocols name a capability (`Readable`, `UserStore`); do not use an `I` prefix.
- Files are `PascalCase.swift`; test files are `*Tests.swift`; test methods start with `test`.
- Booleans use `is`, `has`, `can`; a property named `isX` is a `Bool`.
- Acronyms are words: `userId`, `httpClient`, `parseUrl`.

## Dart

- `PascalCase` types; `camelCase` functions, variables, and constants; `snake_case` file names.
- Test files are `*_test.dart`; test names state behavior.
- Private identifiers start with `_`; library privacy is per library, not per class.
- Acronyms are words: `userId`, `httpClient`, `parseUrl`.

## SQL

- Tables are plural `snake_case`; columns are singular `snake_case`; keys and constraints follow the database rules
  in `dimensions.md`.
- Use `created_at`, `updated_at`, `deleted_at` for audit and soft-delete columns; `is_` for booleans.
- Migration files are `YYYYMMDDHHMMSS_description.sql`; one logical change per file.
- Avoid quoted mixed-case identifiers; they make every query case-sensitive and error-prone.
- Do not use reserved words as identifiers; if a legacy schema does, keep the name and quote it consistently.

## Shell

- Functions and local variables are `snake_case`; environment variables and constants are `UPPER_SNAKE`.
- Script files are `kebab-case.sh`; make them executable and start with a shebang.
- Test files are `*_test.sh`; test functions state behavior and use `set -euo pipefail`.
- Avoid one-letter variables except loop indices; quote expansions; do not use spaces in names.
- Command names are verbs (`build`, `deploy`); flags are kebab-case.

## HTML and CSS

- Classes and IDs are `kebab-case`; BEM is `block__element--modifier`.
- Custom properties are `--color-bg`, `--space-md`; no unexplained abbreviations.
- JavaScript hooks use `js-` and are not styled; IDs are reserved for anchors and labels.
- Files are `kebab-case.css` or `kebab-case.scss`; partials start with `_` in Sass.
- Data attributes are `data-` plus kebab-case; accessible names match the visible label.

## JSON and YAML

- Choose one key case per schema (`snake_case` or `camelCase`) and keep it across producers and consumers.
- Keys contain no spaces; avoid dots unless they express a namespace; avoid reserved words.
- Timestamps are `_at` with RFC 3339; IDs are `<entity>_id`; booleans are `is_`/`has_`.
- YAML files use kebab-case names; anchors and aliases are named by their concept, not `default`.
- Do not encode types in keys; do not use `data` as a universal wrapper.

## Cross-Language Rules

- Do not import casing across a boundary: map `snake_case` JSON to `camelCase` code at the edge, not in the middle.
- Acronyms follow the target language; `UserID` in Go, `UserId` in C#, `user_id` in Python and Rust.
- A public name is an API contract in every language; rename it only with a deprecation or versioning path.
- When a framework mandates a name (lifecycle hooks, ORM columns, test discovery), follow the framework and record
  the exception.
