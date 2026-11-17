# 各语言风格约定

在 `SKILL.md` 之后阅读本文件。它给出每种语言的 formatter、linter、行宽与导入顺序默认值，以及覆盖语言无关默认值的
工具特定规则。项目配置的值优先于这里的每个数字；当项目已设置更严格的值时，遵循项目。

## 矩阵

| 语言 | formatter | linter | 行宽 | 导入顺序 |
|---|---|---|---|---|
| Python | Black, Ruff format | Ruff | 88 | 标准库、第三方、第一方 |
| TypeScript / JavaScript | Prettier 或 Biome | ESLint 或 Biome | 80 | 内置、外部、内部、相对 |
| Java | google-java-format | Checkstyle, SpotBugs | 100 | 静态导入在前，随后按 ASCII 排序 |
| Kotlin | ktlint | detekt | 140（ktlint 官方）；detekt 默认 120，需显式对齐 | 字典序、IDE 分组 |
| C# | dotnet format | Roslyn analyzers, StyleCop | 120（审查规则） | `System` 在前，随后按字母顺序 |
| Go | gofmt, goimports | go vet, staticcheck | 不限制 | 标准库、第三方、本地前缀 |
| Rust | rustfmt | Clippy | 100 | 每个 `use` 块内按字母顺序 |
| C / C++ | clang-format | clang-tidy | 80（LLVM 与 Google），120（Microsoft） | 自身头文件、C、C++、第三方、项目 |
| Ruby | RuboCop | RuboCop | 120 | 默认不强制 |
| PHP | PHP-CS-Fixer | PHPCS | 120（软限制） | 字母顺序，每条语句一个 |
| Swift | swift-format | SwiftLint | 100 | 字母顺序，可选启用 `sorted_imports` |
| Dart | dart format | dart analyze | 80 | `dart:`、`package:`、相对路径 |
| SQL | sqlfluff format | sqlfluff | 80 | 不适用；CTE 自上而下 |
| Shell | shfmt | ShellCheck | 不限制 | 不适用；在顶部 source 库 |
| HTML / CSS | Prettier | Stylelint | 80 | 不适用；`@import` 位于其他规则之前 |
| YAML / JSON / TOML | Prettier, tombi | yamllint, tombi | 通常 80 | 不适用；锚点先定义后使用 |

## Python

- 用 Black（`line-length = 88`，`target-version` 设为支持的最旧 Python 版本）或与 Black 兼容的 Ruff format
  格式化；用 `black --check` 或 `ruff format --check` 检查。绝不要在同一棵树上同时运行两者。
- 用 Ruff 做 lint：默认规则族为 `E4`、`E7`、`E9` 与 `F`；启用 `I` 做 import 排序、启用 `UP` 做语法现代化，
  并在 `pyproject.toml` 中锁定一个 Ruff 版本。
- 导入顺序：标准库、第三方、第一方，每个块内排序，块间空一行。带 `profile = "black"` 的 isort 与 Ruff `I`
  实现相同顺序；使用 isort 时为其设置相同行宽。
- 默认使用双引号。Black 通过 `skip-string-normalization` 保留单引号；Ruff format 使用
  `quote-style = "preserve"`。两者都是项目级设置，不是按文件设置。
- 类型检查是独立门禁：mypy 或 pyright 属于测试一侧，而不属于 formatter，其配置不改变风格规则。

## TypeScript 与 JavaScript

- 用 Prettier（`printWidth: 80`、`tabWidth: 2`、`semi: true`、`singleQuote: false`、
  `trailingComma: "all"`、`arrowParens: "always"`）从 `.prettierrc` 中读取配置来格式化，并在 CI 中用
  `prettier --check .` 检查。
- 用 flat config（`eslint.config.js`）配置的 ESLint 做 lint，把 `eslint-config-prettier` 放在最后，使格式化规则
  不与 Prettier 冲突；`typescript-eslint` 的类型感知规则作为第二轮运行。
- Biome 是单工具替代方案：formatter 加 linter、`lineWidth: 80`、`indentStyle: "space"`、双引号与自动整理
  import。每个仓库在 Biome 与 Prettier 加 ESLint 之间二选一，绝不把两套一起运行。
- 导入顺序：Node 内置模块、外部包、内部别名、父级与同级路径。`eslint-plugin-import` 或
  `simple-import-sort` 强制该顺序，`import/no-cycle` 捕获循环。
- 当拆分会改变渲染输出时，JSX 文本、模板字面量与长字符串属于例外；Prettier 不处理它们，因此那里的长行不构成
  lint 失败。

## Java

- 通过 Spotless 的 Maven 或 Gradle 插件使用 google-java-format 格式化：2 空格缩进、100 列上限、import 排
  序、用 `--fix-imports-only` 移除未使用的 import。在 CI 中用 `spotlessCheck` 检查。
- 用 Checkstyle 做 lint，使用 `google_checks.xml` 或项目规则集。Checkstyle 覆盖 formatter 不处理的 import、
  代码块与声明，所以把它保留为门禁，而不是报告。
- 运行 SpotBugs 检查字节码缺陷（null 处理、资源泄漏、错误的相等判断），并对高优先级发现失败；它是缺陷门禁，
  不是风格 formatter。
- 导入顺序：静态导入在前，然后是非静态导入，每个块按 ASCII 排序；没有通配符导入，也没有未使用的导入，因为
  google-java-format 与 Checkstyle 都会强制它。
- google-java-format 不拆分长字符串字面量，因此超长字面量是一项代码变更（资源文件或拼接），而不是格式化例外。

## Kotlin

- 用 `ktlint_official` 代码风格中的 ktlint 格式化：4 空格缩进与 `max_line_length = 140`。把两者放进
  `.editorconfig`，让 IDE 与 ktlint 读到相同的值。
- 用 detekt（`maxLineLength` 默认 120）检查复杂度、风格与潜在缺陷；把它的行宽与 ktlint 对齐，否则两个工具会
  对同一文件产生分歧。
- 导入顺序：字典序，禁止通配符导入，`java`、`javax` 与 `kotlin` 按 IDE 布局分组；ktlint 的
  `import-ordering` 规则强制它。
- 声明与调用中允许尾随逗号（Kotlin 1.4+），`trailing-comma` 规则可以强制它们；尾随逗号让多行 diff 只做追加。
- 项目接受的 detekt 发现要通过基线记录，并附理由与负责人，绝不在配置中全局关闭。

## C#

- 用 `dotnet format`（空白与风格规则来自 `.editorconfig`）格式化，并在 CI 中用
  `dotnet format --verify-no-changes` 检查。它强制缩进与间距，但不强制列上限。
- 用 Roslyn 分析器（`CAxxxx`、`IDExxxx`）与 StyleCop.Analyzers（`SAxxxx`）做 lint，在 `.editorconfig` 中
  设置严重级别；`TreatWarningsAsErrors` 把选定的集合变成门禁。
- 行宽是审查规则（常用 120），因为 formatter 与分析器都不折行长行。
- 导入顺序：`System` 命名空间在前，其余按字母顺序，组间空行；global using 放在一个文件中，IDE0005 移除未使用
  的 using。
- StyleCop 的 using 指令位置规则（放在命名空间内或外）每个仓库选择一次，并通过 `.editorconfig` 应用，而不是
  按文件决定。

## Go

- 用 `gofmt` 格式化，这是强制的：用制表符缩进，没有列上限，不折行。当 `gofmt -l` 打印出文件时让 CI 失败；这
  门语言没有给风格争论留空间。
- 用 `goimports` 管理 import，它增删 import，并把标准库与第三方包分开分组；用 `-local` 指定模块前缀，组间空
  一行。
- 用 `go vet` 做贴近编译器的检查，用 `staticcheck`（`SA`、`S`、`ST` 规则族）检查缺陷与风格。两者都用与构建
  相同的 Go 版本运行。
- 没有行宽规则；长函数或长表达式是审查关注点，gofmt 不会拆分它们。
- 把生成的 `*.pb.go`、mock 与第三方引入树排除在 lint 之外，并让生产代码不出现点导入。

## Rust

- 用 rustfmt（`max_width = 100`、`hard_tabs = false`、设置 `edition`）格式化，并用 `cargo fmt --check`
  检查。覆盖项放在 `rustfmt.toml` 中，作用于工作区而不是单个 crate。
- 用 Clippy 做 lint：在 CI 中运行 `cargo clippy --all-targets -- -D warnings`。只允许在最窄的项上用
  `#[allow]` 并写明理由来放行特定 lint。
- 默认在 `use` 块内按字母顺序排列（`reorder_imports`）；`group_imports = "StdExternalCrate"` 是不稳定的
  nightly 选项，所以只在 nightly 工具链上启用，并在整个工作区保持一致。
- rustfmt 不格式化宏调用（如 `quote!` 或 `select!`）内部的代码；那段代码需手工格式化，并接受工具不会检查它。
- 让 `cargo fmt`、Clippy 与构建使用同一个工具链，并由 `rust-toolchain.toml` 锁定。

## C 与 C++

- 用已提交的 `.clang-format` 中的 clang-format 格式化：`BasedOnStyle` 选 LLVM 或 Google（80 列）、
  Chromium（80）或 Microsoft（120）。设置 `SortIncludes: true`、`IncludeBlocks: Regroup` 与
  `IncludeCategories`。
- 用 `.clang-tidy` 中的 clang-tidy 做 lint（`bugprone-*`、`modernize-*`、`performance-*`、
  `readability-*` 以及项目的 `cert-*` 子集），对变更文件使用 `compile_commands.json` 运行。
- include 顺序：匹配的头文件在前，然后是 C 系统头、C++ 标准库、第三方与项目头文件，按 `IncludeCategories`
  编码；系统头用尖括号，项目头用引号。
- 列上限来自所选风格（LLVM 与 Google 为 80，Microsoft 为 120）；预处理指令与长字符串字面量不会被 formatter
  折行。
- 在 CI 中锁定 clang-format 与 clang-tidy 版本，因为次要版本会改变格式化并产生大量噪声。

## Ruby

- 用已提交的 `.rubocop.yml` 中的 RuboCop 格式化并 lint：`Layout/LineLength` 默认 `Max: 120`，
  `Style/StringLiterals` 默认单引号。从共享 gem 继承，而不是列出每一个 cop。
- 用 `rubocop -a` 自动修正安全项，用 `rubocop -A` 修正不安全项；审查 diff，因为不安全的自动修正可能在边界情况
  下改变行为。
- 没有默认的 require 顺序 cop；把 require 按标准库、gem、项目文件排序作为团队规则，并在顺序反复被破坏时启用
  检查。
- 在配置中设置 `TargetRubyVersion`；缺少它时，针对较新语法的 cop 会静默禁用，lint 结果取决于安装的 Ruby。
- 把生成代码、第三方引入包与 schema 转储排除在运行之外，并把排除列表保留在 `.rubocop.yml` 中。

## PHP

- 用 PHP-CS-Fixer 基于 `@PSR12` 规则集加项目规则（`array_syntax: short`、`single_quote`、
  `declare_strict_types`、`ordered_imports`、`no_unused_imports`）格式化；在 CI 中用 `--dry-run --diff` 检查。
- 在项目已使用 PHPCS 的地方按 `PSR12` 做 lint。在 PHP-CS-Fixer 与 PHPCS 中选一个作为修正器，另一个保留为检查
  器，因为两个修正器作用于同一棵树会互相冲突。
- 导入顺序：每条 `use` 语句一个类，按字母顺序，没有未使用或重复的 import；PSR-12 把 `use` 声明放在命名空间
  之后。
- PSR-12 设定 120 字符软限制、4 空格缩进、LF 换行与每文件一个类；超长行是提取的信号，而不是关闭限制的理由。
- 把两个工具接入 Composer 脚本，让贡献者在本地运行与 CI 相同的命令。

## Swift

- 用 `.swift-format`（`lineLength: 100`、`indentation: 2`）中的 swift-format 格式化，并用
  `swift-format lint --strict` 检查；该工具不排序 import。
- 用 `.swiftlint.yml` 中的 SwiftLint 做 lint：`line_length` 默认在 120 警告、在 200 报错，而
  `sorted_imports` 等可选规则提供 swift-format 缺少的顺序检查。
- 导入顺序：每行一个模块，按字母顺序，`@testable import` 紧邻其模块；项目希望强制时启用 `sorted_imports`。
- 保持一个 formatter 权威：如果项目使用 4 空格缩进，就在 `.swift-format` 中设置它，而不是让 swift-format 与
  SwiftLint 产生分歧。
- 在 CI 中锁定两个工具的版本，因为默认规则集与格式化会随版本变化。

## Dart

- 用 `dart format` 格式化；默认页宽为 80 列，`--set-exit-if-changed` 让 CI 在代码未格式化时失败。
- 用 `analysis_options.yaml` 中的 `dart analyze` 做 lint，继承 `package:lints/recommended.yaml` 或
  `package:flutter_lints/flutter.yaml`；启用 `directives_ordering`、`prefer_single_quotes` 与
  `unnecessary_import`。
- 导入顺序：`dart:` 库，然后 `package:` import，然后相对 import，组间空一行；`directives_ordering` 在每个组
  内排序。
- 尾随逗号控制 formatter 对参数列表与集合列表的布局，因此有意保持每行一项的列表会保留其尾随逗号。
- `*.g.dart` 与 `*.freezed.dart` 等生成文件在分析器配置中被排除，并且只重新生成，绝不编辑。

## SQL

- 用一个 `.sqlfluff` 配置运行 sqlfluff `format`：设置 `dialect` 与 `templater`（`jinja` 或 `dbt`）、关键字
  大小写与缩进；缺少 dialect 是配置错误，不是默认值。
- 用 sqlfluff 规则做 lint，覆盖布局（`LT`）、大小写（`CP`）与解析错误，再加上项目启用的引用与别名规则；解析
  器会在数据库之前捕获无效 SQL。
- 默认行长为 80（`LT05`）；长字符串字面量、DDL 列清单与生成的 `VALUES` 列表带 `-- noqa: LT05` 并写明理由。
- 没有导入顺序；CTE 按依赖顺序自上而下排列，每行一个子句，当列表长到足以遮住源表时，每行一个 `SELECT` 列。
- 用 `.sqlfluffignore` 排除生成的 DDL 与迁移文件；迁移与 schema 变更属于 `api-and-data-conventions`。

## Shell

- 用 shfmt 格式化（`-i 4` 使用空格，或默认制表符；`-ln bash` 与 shebang 匹配），并在 CI 中用 `shfmt -d`
  检查；heredoc 主体与内嵌脚本保持不动。
- 用 ShellCheck 以 `--severity=warning` 做 lint，对正在积极变更的脚本用 `style`；在代码中修复每个发现而不是
  抑制它，并且用 `# shellcheck disable=SC2086` 加理由来禁用特定检查。
- 没有导入顺序；在第一次使用之前于顶部 source 库，并以 `set -euo pipefail` 开始脚本，让失败停止脚本。
- shfmt 只格式化缩进与间距，没有行长规则；按 ShellCheck 的要求给展开加引号，并在 bash 中使用 `[[ ]]`。
- 对每个脚本运行两个工具，包括 CI 辅助脚本，因为未加引号的变量通常就藏在一行流水线步骤里。

## HTML 与 CSS

- 用 Prettier（`printWidth: 80`、`tabWidth: 2`、`singleQuote: false`、
  `htmlWhitespaceSensitivity: "css"`）格式化 HTML、CSS、SCSS 与 JSX，并用 `prettier --check` 检查。
- 用 Stylelint 与 `stylelint-config-standard` 做 lint（重复选择器、无效十六进制颜色、简写冲突）。风格类规则
  已移出 Stylelint，因此 Prettier 负责格式化，Stylelint 负责正确性与约定。
- Stylelint 默认既不强制行长也不强制属性顺序；项目需要时加入 `stylelint-order` 并选定一种顺序（字母顺序或同
  心顺序），绝不混用两者。
- `@import` 规则位于其他规则之前；选择器、自定义属性与设计令牌遵循项目的命名约定，而不是工具默认值。
- 把内联样式、生成的邮件模板与第三方内嵌 HTML 排除在 Prettier 之外，因为其布局归生成器或宿主所有。

## YAML、JSON 与 TOML

- 用 Prettier（`printWidth: 80`、`tabWidth: 2`）格式化 YAML 与 JSON，用 tombi 格式化 TOML；把 80 作为通用
  行宽，并在工具文档中确认其当前默认值，而不是假定。严格 JSON 无注释；JSONC 与 JSON5 只用于工具明确支持时，
  其余带注释的配置用 YAML 或 TOML。
- 用 yamllint 对 YAML 做 lint（行长 80、2 空格缩进、真值检查），用 tombi 对 TOML 做 lint；每个工具在仓库根
  保留一个配置文件。
- 没有导入顺序；YAML 锚点先定义后使用，JSON 键遵循 schema 顺序，TOML 键保持分组在其表下。
- Prettier 保留 YAML 注释，但任何重新解析文件的工具都可能重写锚点与别名；把锚点密集文件上的格式化 diff 当作
  审查项。
- 不要用项目 formatter 格式化锁文件或生成的 manifest；其字节布局归生成工具所有，重新格式化会重新打开一个只应
  在依赖变化时变化的文件。

## 跨语言规则

- 每种文件类型只运行一个 formatter。当两个工具重叠时，在第二个工具中关闭格式化（`eslint-config-prettier`、
  关闭 Stylelint 风格规则），而不是接受最后运行的那一个。
- 在一个仓库内让跨工具的行宽保持一致：Black 88 与 isort 88，Prettier 对 JSON、HTML 与代码都用 80，ktlint
  与 detekt 使用相同上限。
- 在构建镜像、pre-commit hook 与 CI 中锁定 formatter 与 linter 版本；版本升级是独立变更，其产生的格式化
  diff 像代码一样审查。
- 机械性发现优先使用工具的 fix 命令，审查其 diff 后再提交；工具能修复的东西若手工修复，下一次运行还会回来。
- 每个工具的排除项集中在一处：生成树、第三方引入树、构建输出与第三方树。散落在注释与 CI 标志中的排除列表无法审
  查。
- 把强制 formatter（gofmt、`cargo fmt`、`dart format`、项目强制的 Black 或 Prettier）视为已定，不要花审查时
  间争论工具已经解决的问题。
- 静态类型检查器、安全扫描器与覆盖率是独立门禁；本文件列出 formatter 与 linter，不涉及运行时分析。
- 多语言仓库为每种语言重复该模式，只共享编辑器与 CI 配置；不要把一个语言的默认值强加到另一个语言上。
