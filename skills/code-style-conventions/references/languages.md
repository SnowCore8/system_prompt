# 各语言风格约定

本文件应当在阅读 `SKILL.md` 之后使用。本文件规定每种语言的 formatter、linter、行宽与导入顺序默认值，以及
覆盖语言无关默认值的工具特定规则。此处数字均为默认值，项目配置为其提供实际取值（包括更严格的值）；使用
方式由 `SKILL.md` 的规则决定。

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
| Shell | shfmt | ShellCheck | 不限制 | 不适用；于顶部 source 库 |
| HTML / CSS | Prettier | Stylelint | 80 | 不适用；`@import` 位于其他规则之前 |
| YAML / JSON / TOML | Prettier, tombi | yamllint, tombi | 通常 80 | 不适用；锚点先定义后使用 |

## Python

- 应当以 Black（`line-length = 88`，`target-version` 设为支持的最旧 Python 版本）或与 Black 兼容的 Ruff
  format 格式化；以 `black --check` 或 `ruff format --check` 检查。不得于同一代码树上同时运行两者。
- 应当以 Ruff 执行 lint：默认规则族为 `E4`、`E7`、`E9` 与 `F`；启用 `I` 作 import 排序、启用 `UP` 作语法
  现代化，并于 `pyproject.toml` 中锁定一个 Ruff 版本。
- 导入顺序：标准库、第三方、第一方，每一块内排序，块间空一行。带 `profile = "black"` 的 isort 与 Ruff `I`
  实现相同顺序；使用 isort 时应当为其设置相同行宽。
- 默认使用双引号。Black 通过 `skip-string-normalization` 保留单引号；Ruff format 使用
  `quote-style = "preserve"`。两者均属于项目级设置，不得按文件设置。
- 类型检查属于独立门禁：mypy 或 pyright 属于测试一侧，不属于 formatter，其配置不改变风格规则。

## TypeScript 与 JavaScript

- 应当以 Prettier（`printWidth: 80`、`tabWidth: 2`、`semi: true`、`singleQuote: false`、
  `trailingComma: "all"`、`arrowParens: "always"`）自 `.prettierrc` 中读取配置来格式化，并于 CI 中以
  `prettier --check .` 检查。
- 应当以 flat config（`eslint.config.js`）配置的 ESLint 执行 lint，把 `eslint-config-prettier` 置于最后，
  使格式化规则不与 Prettier 冲突；`typescript-eslint` 的类型感知规则作为第二轮运行。
- Biome 属于单工具替代方案：formatter 加 linter、`lineWidth: 80`、`indentStyle: "space"`、双引号与自动
  整理 import。每个仓库应当于 Biome 与 Prettier 加 ESLint 之间二选一，不得把两套一起运行。
- 导入顺序：Node 内置模块、外部包、内部别名、父级与同级路径。`eslint-plugin-import` 或
  `simple-import-sort` 强制该顺序，`import/no-cycle` 捕获循环。
- 拆分会改变渲染输出时，JSX 文本、模板字面量与长字符串属于例外；Prettier 不处理上述内容，因此其中的长行
  不构成 lint 失败。

## Java

- 应当通过 Spotless 的 Maven 或 Gradle 插件使用 google-java-format 格式化：2 空格缩进、100 列上限、import
  排序、以 `--fix-imports-only` 移除未使用的 import。应当于 CI 中以 `spotlessCheck` 检查。
- 应当以 Checkstyle 执行 lint，使用 `google_checks.xml` 或项目规则集。Checkstyle 覆盖 formatter 不处理的
  import、代码块与声明，因此应当将其保留为门禁，不得仅作为报告。
- 应当运行 SpotBugs 检查字节码缺陷（null 处理、资源泄漏、错误的相等判断），并对高优先级发现失败；其属于缺
  陷门禁，不属于风格 formatter。
- 导入顺序：静态导入在前，随后是非静态导入，每一块按 ASCII 排序；无通配符导入，亦无未使用的导入，因
  google-java-format 与 Checkstyle 均会强制该顺序。
- google-java-format 不拆分长字符串字面量，因此超长字面量属于一项代码变更（资源文件或拼接），不构成格式化
  例外。

## Kotlin

- 应当以 `ktlint_official` 代码风格中的 ktlint 格式化：4 空格缩进与 `max_line_length = 140`。应当将两者放
  入 `.editorconfig`，使 IDE 与 ktlint 读到相同的值。
- 应当以 detekt（`maxLineLength` 默认 120）检查复杂度、风格与潜在缺陷；应当将其行宽与 ktlint 对齐，否则
  两个工具将对同一文件产生分歧。
- 导入顺序：字典序，禁止通配符导入，`java`、`javax` 与 `kotlin` 按 IDE 布局分组；ktlint 的
  `import-ordering` 规则强制该顺序。
- 声明与调用中允许尾随逗号（Kotlin 1.4+），`trailing-comma` 规则可以强制它们；尾随逗号使多行 diff 仅作追
  加。
- 项目接受的 detekt 发现应当通过基线记录，并附理由与负责人，不得于配置中全局关闭。

## C#

- 应当以 `dotnet format`（空白与风格规则来自 `.editorconfig`）格式化，并于 CI 中以
  `dotnet format --verify-no-changes` 检查。其强制缩进与间距，但不强制列上限。
- 应当以 Roslyn 分析器（`CAxxxx`、`IDExxxx`）与 StyleCop.Analyzers（`SAxxxx`）执行 lint，于
  `.editorconfig` 中设置严重级别；`TreatWarningsAsErrors` 将选定的集合变为门禁。
- 行宽属于审查规则（常用 120），因 formatter 与分析器均不折行长行。
- 导入顺序：`System` 命名空间在前，其余按字母顺序，组间空一行；global using 置于一个文件中，IDE0005 移除
  未使用的 using。
- StyleCop 的 using 指令位置规则（置于命名空间内或外）应当由每个仓库选择一次，并通过 `.editorconfig` 应
  用，不得按文件决定。

## Go

- 应当以 `gofmt` 格式化，此为强制要求：以制表符缩进，无列上限，不折行。`gofmt -l` 打印出文件的，应当使
  CI 失败；该语言未给风格争论留空间。
- 应当以 `goimports` 管理 import，其增删 import，并把标准库与第三方包分开分组；应当以 `-local` 指定模块
  前缀，组间空一行。
- 应当以 `go vet` 执行贴近编译器的检查，以 `staticcheck`（`SA`、`S`、`ST` 规则族）检查缺陷与风格。两者均
  应当使用与构建相同的 Go 版本运行。
- 无行宽规则；长函数或长表达式属于审查关注点，gofmt 不会拆分它们。
- 应当将生成的 `*.pb.go`、mock 与第三方引入树排除于 lint 之外，并使生产代码不出现点导入。

## Rust

- 应当以 rustfmt（`max_width = 100`、`hard_tabs = false`、设置 `edition`）格式化，并以 `cargo fmt --check`
  检查。覆盖项应当置于 `rustfmt.toml` 中，作用于工作区而非单个 crate。
- 应当以 Clippy 执行 lint：于 CI 中运行 `cargo clippy --all-targets -- -D warnings`。仅应于最窄的项上以
  `#[allow]` 并写明理由来放行特定 lint。
- 默认于 `use` 块内按字母顺序排列（`reorder_imports`）；`group_imports = "StdExternalCrate"` 属于不稳定的
  nightly 选项，因此仅应于 nightly 工具链上启用，并于整个工作区保持一致。
- rustfmt 不格式化宏调用（如 `quote!` 或 `select!`）内部的代码；该段属于 formatter 不覆盖的例外，应当按
  rustfmt 文档手工处理。
- 应当使 `cargo fmt`、Clippy 与构建使用同一工具链，并由 `rust-toolchain.toml` 锁定。

## C 与 C++

- 应当以已提交的 `.clang-format` 中的 clang-format 格式化：`BasedOnStyle` 选 LLVM 或 Google（80 列）、
  Chromium（80）或 Microsoft（120）。应当设置 `SortIncludes: true`、`IncludeBlocks: Regroup` 与
  `IncludeCategories`。
- 应当以 `.clang-tidy` 中的 clang-tidy 执行 lint（`bugprone-*`、`modernize-*`、`performance-*`、
  `readability-*` 以及项目的 `cert-*` 子集），对变更文件使用 `compile_commands.json` 运行。
- include 顺序：匹配的头文件在前，随后是 C 系统头、C++ 标准库、第三方与项目头文件，按 `IncludeCategories`
  编码；系统头用尖括号，项目头用引号。
- 列上限来自所选风格（LLVM 与 Google 为 80，Microsoft 为 120）；预处理指令与长字符串字面量不会被
  formatter 折行。
- 应当于 CI 中锁定 clang-format 与 clang-tidy 版本，因次要版本会改变格式化并产生大量噪声。

## Ruby

- 应当以已提交的 `.rubocop.yml` 中的 RuboCop 格式化并 lint：`Layout/LineLength` 默认 `Max: 120`，
  `Style/StringLiterals` 默认单引号。应当自共享 gem 继承，不得列出每一个 cop。
- 应当以 `rubocop -a` 自动修正安全项，以 `rubocop -A` 修正不安全项；应当审查 diff，因不安全的自动修正可能于边界情况下改变行为。
- 无默认的 require 顺序 cop；应当将 require 按标准库、gem、项目文件排序作为团队规则，并于顺序反复被破
  坏时启用检查。
- 应当于配置中设置 `TargetRubyVersion`；缺少该设置时，针对较新语法的 cop 将静默禁用，lint 结果取决于安装
  的 Ruby。
- 应当将生成代码、第三方引入包与 schema 转储排除于运行之外，并把排除列表保留于 `.rubocop.yml` 中。

## PHP

- 应当以 PHP-CS-Fixer 基于 `@PSR12` 规则集加项目规则（`array_syntax: short`、`single_quote`、
  `declare_strict_types`、`ordered_imports`、`no_unused_imports`）格式化；于 CI 中以 `--dry-run --diff`
  检查。
- 项目已使用 PHPCS 的，应当按 `PSR12` 执行 lint。应当于 PHP-CS-Fixer 与 PHPCS 中选定一个作为修正器，另一
  个保留为检查器，因两个修正器作用于同一棵树将互相冲突。
- 导入顺序：每条 `use` 语句一个类，按字母顺序，无未使用或重复的 import；PSR-12 把 `use` 声明置于命名空
  间之后。
- PSR-12 设定 120 字符软限制、4 空格缩进、LF 换行与每文件一个类；超长行属于提取的信号，不构成关闭限制的
  理由。
- 应当把两个工具接入 Composer 脚本，使贡献者于本地运行与 CI 相同的命令。

## Swift

- 应当以 `.swift-format`（`lineLength: 100`、`indentation: 2`）中的 swift-format 格式化，并以
  `swift-format lint --strict` 检查；该工具不排序 import。
- 应当以 `.swiftlint.yml` 中的 SwiftLint 执行 lint：`line_length` 默认于 120 警告、于 200 报错，而
  `sorted_imports` 等可选规则提供 swift-format 缺少的顺序检查。
- 导入顺序：每行一个模块，按字母顺序，`@testable import` 紧邻其模块；项目需要强制时启用
  `sorted_imports`。
- 应当保持一个 formatter 权威：项目使用 4 空格缩进的，应当于 `.swift-format` 中设置，不得使 swift-format
  与 SwiftLint 产生分歧。
- 应当于 CI 中锁定两个工具的版本，因默认规则集与格式化将随版本变化。

## Dart

- 应当以 `dart format` 格式化；默认页宽为 80 列，`--set-exit-if-changed` 使 CI 于代码未格式化时失败。
- 应当以 `analysis_options.yaml` 中的 `dart analyze` 执行 lint，继承 `package:lints/recommended.yaml` 或
  `package:flutter_lints/flutter.yaml`；启用 `directives_ordering`、`prefer_single_quotes` 与
  `unnecessary_import`。
- 导入顺序：`dart:` 库，随后 `package:` import，随后相对 import，组间空一行；`directives_ordering` 于每
  一组内排序。
- 尾随逗号控制 formatter 对参数列表与集合列表的布局，因此有意保持每行一项的列表将保留其尾随逗号。
- `*.g.dart` 与 `*.freezed.dart` 等生成文件应当于分析器配置中排除，并且仅应重新生成，不得编辑。

## SQL

- 应当以一个 `.sqlfluff` 配置运行 sqlfluff `format`：设置 `dialect` 与 `templater`（`jinja` 或 `dbt`）、
  关键字大小写与缩进；缺少 dialect 属于配置错误，不构成默认值。
- 应当以 sqlfluff 规则执行 lint，覆盖布局（`LT`）、大小写（`CP`）与解析错误，再加上项目启用的引用与别名
  规则；解析器将于数据库之前捕获无效 SQL。
- 默认行长为 80（`LT05`）；长字符串字面量、DDL 列清单与生成的 `VALUES` 列表应当带 `-- noqa: LT05` 并写
  明理由。
- 无导入顺序；CTE 应当按依赖顺序自上而下排列，每行一个子句，列表长到足以遮住源表时每行一个 `SELECT`
  列。
- 应当以 `.sqlfluffignore` 排除生成的 DDL 与迁移文件；迁移与 schema 变更属于
  `api-and-data-conventions`。

## Shell

- 应当以 shfmt 格式化（`-i 4` 使用空格，或默认制表符；`-ln bash` 与 shebang 匹配），并于 CI 中以
  `shfmt -d` 检查；heredoc 主体与内嵌脚本应当保持不变。
- 应当以 ShellCheck 按 `--severity=warning` 执行 lint，对正在积极变更的脚本用 `style`；应当于代码中修复
  每一发现，不得无理由抑制。确需抑制时，使用 `# shellcheck disable=SC2086`，写明理由与清理条件，并保持最
  窄范围。
- 无导入顺序；应当于第一次使用之前，在顶部 source 库，并以 `set -euo pipefail` 开始脚本，使失败停止脚本。
- shfmt 仅格式化缩进与间距，无行长规则；应当按 ShellCheck 的要求给展开加引号，并于 bash 中使用 `[[ ]]`。
- 应当对每个脚本运行两个工具，包括 CI 辅助脚本，因未加引号的变量通常正出现于一行流水线步骤中。

## HTML 与 CSS

- 应当以 Prettier（`printWidth: 80`、`tabWidth: 2`、`singleQuote: false`、
  `htmlWhitespaceSensitivity: "css"`）格式化 HTML、CSS、SCSS 与 JSX，并以 `prettier --check` 检查。
- 应当以 Stylelint 与 `stylelint-config-standard` 执行 lint（重复选择器、无效十六进制颜色、简写冲突）。
  风格类规则已移出 Stylelint，因此 Prettier 负责格式化，Stylelint 负责正确性与约定。
- Stylelint 默认既不强制行长亦不强制属性顺序；项目需要时应当加入 `stylelint-order` 并选定一种顺序（字母顺
  序或同心顺序），不得混用两者。
- `@import` 规则位于其他规则之前；选择器、自定义属性与设计令牌的命名取项目已有的名称（由
  `naming-conventions` 管辖），不得使用工具默认值。
- 应当把内联样式、生成的邮件模板与第三方内嵌 HTML 排除于 Prettier 之外，因其布局归生成器或宿主所有。

## YAML、JSON 与 TOML

- 应当以 Prettier（`printWidth: 80`、`tabWidth: 2`）格式化 YAML 与 JSON，以 tombi 格式化 TOML；应当把
  80 作为通用行宽，并于工具文档中确认其当前默认值，不得假定。严格 JSON 无注释；JSONC 与 JSON5 仅在
  工具明确支持时应用，其余带注释的配置用 YAML 或 TOML。
- 应当以 yamllint 对 YAML 执行 lint（行长 80、2 空格缩进、真值检查），以 tombi 对 TOML 执行 lint；每个工
  具应当于仓库根保留一个配置文件。
- 无导入顺序；YAML 锚点先定义后使用，JSON 键遵循 schema 顺序，TOML 键应当保持在其表下分组。
- Prettier 保留 YAML 注释，但任何重新解析文件的工具均可能重写锚点与别名；应当把锚点密集文件上的格式化
  diff 作为审查项。
- 不得以项目 formatter 格式化锁文件或生成的 manifest；其字节布局归生成工具所有，重新格式化将重新打开一个
  仅应于依赖变化时变化的文件。

## 跨语言规则

- 每种文件类型应当仅运行一个 formatter。两个工具重叠的，应当于第二个工具中关闭格式化（
  `eslint-config-prettier`、关闭 Stylelint 风格规则），不得采用最后运行者。
- 应当于一个仓库内使跨工具的行宽保持一致：Black 88 与 isort 88，Prettier 对 JSON、HTML 与代码均用 80，
  ktlint 与 detekt 使用相同上限。
- 应当于构建镜像、pre-commit hook 与 CI 中锁定 formatter 与 linter 版本；版本升级属于独立变更，其产生的
  格式化 diff 应当像代码一样审查。
- 机械性发现应当优先使用工具的 fix 命令，审查其 diff 后再提交；工具能够修复的内容若手工修复，下一次运行
  仍将重现该问题。
- 每个工具的排除项应当集中于一处：生成树、第三方引入树、构建输出与第三方树。散落于注释与 CI 标志中的排
  除列表无法审查。
- 应当把强制 formatter（gofmt、`cargo fmt`、`dart format`、项目强制的 Black 或 Prettier）视为已定，不得
  耗费审查时间争论工具已经解决的问题。
- 静态类型检查器、安全扫描器与覆盖率属于独立门禁；本文件列出 formatter 与 linter，不涉及运行时分析。
- 多语言仓库应当为每种语言重复该模式，仅共享编辑器与 CI 配置；不得把一个语言的默认值强加到另一个语言上。
