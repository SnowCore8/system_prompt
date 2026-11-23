# 语言注释约定

本文件应当在阅读 `SKILL.md` 之后使用。本文件以每种语言精确的注释语法、文档工具与主流风格，覆盖与语言无
关的默认值。项目配置的工具与 linter 属于事实输入；注释规则以 `SKILL.md` 为准，语言无唯一约定时，使用
其中的默认值。

## 矩阵

| 语言 | 文档注释 | 行注释 | 块注释 | 文档工具 |
|---|---|---|---|---|
| Python | `"""..."""` | `#` | 无；逐行用 `#` | Sphinx、pydoc |
| TypeScript / JavaScript | `/** ... */` | `//` | `/* ... */` | TSDoc / JSDoc、TypeDoc |
| Java | `/** ... */` | `//` | `/* ... */` | Javadoc |
| Kotlin | `/** ... */` | `//` | `/* ... */` | Dokka |
| C# | `/// <summary>` | `//` | `/* ... */` | XML docs、DocFX |
| Go | 声明上方的 `//` | `//` | `/* ... */`（少见） | godoc、`go doc` |
| Rust | 外部 `///`、内部 `//!` | `//` | `/* ... */`（少见） | rustdoc |
| C / C++ | `/** ... */` 或 `///` | `//` | `/* ... */` | Doxygen |
| Ruby | 方法上方的 `#` | `#` | `=begin` / `=end` | RDoc、YARD |
| PHP | `/** ... */` | `//` | `/* ... */` | phpDocumentor |
| Swift | `///` | `//` | `/* ... */` | DocC |
| Dart | `///` | `//` | `/* ... */` | dartdoc |
| SQL | `--` 头 | `--` | `/* ... */` | 无；schema 用 `COMMENT ON` |
| Shell | `#` 目的块 | `#` | 无；here-document 变通 | `--help`、man page |
| HTML / CSS | `<!-- -->`、`/* */` | 无；仅 Sass 用 `//` | `/* ... */` | 风格指南、静态站点 |
| YAML / TOML | `#` | `#` | 无 | schema 或配置参考 |
| Terraform / HCL | `#` | `#` 或 `//` | `/* ... */` | terraform-docs |
| Markdown / XML | `<!-- ... -->` | 无 | `<!-- ... -->` | 文档生成器、schema 文档 |

## Python

- docstring 使用 `"""..."""` 并以祈使式摘要开头；PEP 257 要求多行 docstring 的结束引号单独成行。
- 应当选定一种字段风格并保持一致：Sphinx reST（`:param name:`）、Google（`Args:`）或 NumPy；Sphinx
  autodoc 会解析所配置的风格。
- `#` 是唯一的行注释；除 docstring 与 `__doc__` 赋值外，未赋值的字符串字面量属于死代码；标记为 `# TODO(owner): ...`、`# FIXME:`、
  `# NOTE:`、`# HACK:`，指令为 `# noqa: E501`、`# type: ignore[code]`、`# fmt: off`。
- Sphinx 会把属性上方的 `#:` 注释读取为字段文档；仅应于 docstring 无法覆盖之处使用它们。

## TypeScript 与 JavaScript

- TSDoc 与 JSDoc 注释是声明上方的 `/** ... */`，包含 `@param`、`@returns`、`@throws`、`@remarks`、
  `@example`、`@deprecated`、`@internal`；TypeDoc 与 JSDoc 会渲染它们。
- `//` 是默认的行注释；`/* ... */` 用于临时禁用与许可证块，不用于 API 文档。
- 指令为 `// @ts-expect-error`（始终带理由）、文件顶部的 `/// <reference types="node" />` 或
  `/// <reference path="./types.d.ts" />`，以及 `// eslint-disable-next-line rule -- reason`；
  `// @ts-ignore` 是最后手段。
- 纯 JavaScript 中，`@typedef` 与 `@property` 描述对象形状；TypeScript 中应当优先用真实类型，不得用
  JSDoc。

## Java

- Javadoc 的 `/** ... */` 覆盖每个公开类型与成员；第一句是索引中显示的摘要。
- 标签为 `@param`、`@return`、`@throws`、`@deprecated`、`@see`；行内形式为 `{@link Type#member}`、
  `{@code text}` 与 `{@literal}`。
- doclint 要求块标签闭合（`<ul>`、`<li>`、`<table>`、`<pre>`）、转义 `<` 与 `&`，且不出现游离的 `</p>`
  （旧版 doclint 会把它报为错误）；`@todo` 不是标准写法，故使用 `TODO:` 注释；`package-info.java` 与
  `module-info.java` 用于记录包与模块。
- `{@inheritDoc}` 从被覆盖的方法继承契约；应当用它代替复制父类的文档注释。

## Kotlin

- KDoc 的 `/** ... */` 位于声明上方，包含 `@param`、`@return`、`@throws`、`@property`、`@receiver`、
  `@sample`、`@see`；以 `[Foo]` 链接符号，Dokka 会渲染它。
- `//` 永远不会进入 API 参考；块注释可以嵌套，`// region` 与 `// endregion` 只用于折叠小节。
- 标记为 `// TODO:`、`// FIXME:`、`// HACK:`；弃用使用 `@Deprecated("Use X")`，而非注释。
- Dokka 会把 `@sample` 函数渲染成示例；应当把示例保留在测试源码中，并从 KDoc 引用它。

## C#

- XML 文档注释使用 `///`，包含 `<summary>`、`<param name="x">`、`<returns>`、`<exception cref="T">`、
  `<remarks>`、`<example>`；DocFX 或 Sandcastle 会渲染它们。
- 每个成员应当撰写一句摘要；`<inheritdoc/>` 复用基类或接口的契约，而非复制它。
- `//` 与 `/* ... */` 是普通注释；启用 `GenerateDocumentationFile` 时，CS1591 会对缺少公开文档发出警
  告；`// TODO:` 不会被自动提取。
- CS1572 与 CS1573 会标记不匹配的 `<param>` 标签；在生成 XML 文档的地方启用这些警告。

## Go

- 文档注释是紧贴声明上方、中间无空行的 `//` 块；其从标识符名称开始，以句号结尾，由 `go doc` 与
  pkg.go.dev 渲染。
- 包注释位于 `package` 正上方，以 `// Package billing ...` 开头。
- `//go:` 指令（`//go:generate`、`//go:build`、`//go:embed`）在 `//` 后无空格；弃用使用精确的句子
  `// Deprecated: use X instead.`；TODO 遵循 `// TODO(owner): ...`。
- 每个包只保留一条包注释，置于一个文件中；在每个文件中重复会产生重复的包文档。

## Rust

- 外部文档注释使用 `///`，内部模块或 crate 文档使用 `//!`；rustdoc 的 `# Examples`、`# Panics`、
  `# Errors` 与 `# Safety` 小节承载契约。
- 带围栏的示例作为 doctest 运行（`# ` 隐藏设置）；每个 `unsafe` 块都需要 `// SAFETY:` 注释；
  `#[deprecated(since = "1.2.0", note = "use X")]` 承载弃用信息。
- 标记为 `// TODO:`、`// FIXME:`、`// HACK:`；`#[doc(hidden)]` 与 `#[allow(clippy::...)]` 替代注释抑
  制。
- `cargo doc --document-private-items` 也会渲染私有文档，所以私有文档注释也必须保持准确。

## C 与 C++

- Doxygen 占主导：`/** ... */` 或 `///`，包含 `@param`、`@return`、`@throws`、`@brief`、`@warning`、
  `@note`、`@deprecated` 与 `@file`。
- `//` 与 `/* ... */` 是注释形式；块注释不得嵌套，以反斜杠结尾的 `//` 会拼接下一行。
- 把头文件保护与许可证头放在 `@file` 上方；指令为 `// clang-format off`、`// NOLINT(rule)` 与
  `// fallthrough`；项目的 `.clang-format` 与 `.clang-tidy` 是事实输入，为这些默认值提供实际取值。
- 在宏的定义旁边记录宏；Doxygen 只能识别定义，无法识别每个调用点处的展开结果。

## Ruby

- RDoc 或 YARD 文档注释是紧贴方法或类上方的 `#` 行，包含 `@param [Type] name`、`@return [Type]`、
  `@raise`、`@example` 与 `@deprecated`。
- `=begin` 与 `=end` 必须从第 1 列开始；除大块注释外优先使用 `#`；`:nodoc:` 使内部 API 不出现在生成的
  文档中。
- magic comment 置于最前面（shebang 之后的 `# frozen_string_literal: true`）；指令为
  `# rubocop:disable Rule -- reason` 与 `# rubocop:todo`。
- 与方法之间隔着空行的 `#` 注释不是文档注释；应当使文档注释紧贴声明。

## PHP

- phpDocumentor 的 docblock 是声明上方的 `/** ... */`，包含 `@param`、`@return`、`@throws`、`@var`、
  `@deprecated`、`@internal` 与 `@see`。
- `//` 与 `#` 均能够开始行注释，故统一使用 `//`；`/* ... */` 不承载文档；PHP 8 属性（`#[Route(...)]`）
  是代码，不是注释。
- 指令为 `// @phpstan-ignore-next-line` 与 `// phpcs:ignore Rule -- reason`；Psalm 以外层声明上的
  `/** @psalm-suppress IssueName */` docblock 抑制；弃用是 `@deprecated` 加
  `trigger_error(..., E_USER_DEPRECATED)`。
- 文件级 docblock 位于开头的 `<?php` 标签之后、`declare(strict_types=1)` 之前；命名空间紧随其后，
  类 docblock 紧贴类上方。

## Swift

- DocC 使用 `///`，包含 `- Parameter name:`、`- Returns:`、`- Throws:`，以及标注
  `> Important:`、`> Note:`、`> Warning:`。
- `// MARK: -`、`// TODO:` 与 `// FIXME:` 是 Xcode 约定；`// swiftlint:disable rule` 是 lint 指令。
- `/* ... */` 在 Swift 中可以嵌套，但只用于临时禁用；`@available(*, deprecated, message: "Use X.")`
  在 API 中承载弃用信息。
- DocC 符号引用链接使用双反引号；失效链接会以文档警告的形式出现，所以重命名后应当重新检查。

## Dart

- dartdoc 读取声明上方的 `///`；`//` 是行注释，`/* ... */` 是可嵌套的块注释，但 `///` 方为文档化的风
  格；`dart doc` 会渲染它。
- 在方括号中引用符号（`[Foo]`），并使用 `## Examples` 这类文档小节。
- 指令为带理由的 `// ignore: rule_name` 与 `// ignore_for_file: rule_name`；标记为
  `// TODO(owner): ...` 或 `// TODO: <issue>`，以及 `FIXME:` 与 `HACK:`。
- 在库的 `library;` 指令上为库撰写文档；dartdoc 会把该文档注释渲染为库页面。

## SQL

- `--` 是标准行注释，`/* ... */` 是标准块注释，后者在多数方言中不得嵌套；MySQL 接受 `#`，但可移植的
  迁移不得使用它。
- MySQL 的 `/*! ... */` 会执行其中的内容，不是注释；schema 文档置于 PostgreSQL 的
  `COMMENT ON TABLE ... IS '...'` 或迁移头中。
- 迁移头写明工单、意图与回滚；已应用的迁移不可变；使用 `-- TODO(owner): ...` 与 `-- noqa: rule`
  这类指令。
- 指令方言各不相同：sqlfluff 读取 `-- noqa: rule`，而 `/*+ ... */` 这类优化器提示是代码。

## Shell

- `#` 是唯一的注释语法，且必须开启一个词，所以 `echo value#suffix` 不是注释。
- 应当以 shebang 开头，并撰写一个说明用途、用法、参数与必需环境变量的块；在设置旁边解释
  `set -euo pipefail` 与任何有意的例外。
- ShellCheck 指令为 `# shellcheck disable=SC2086`（带理由）与 `# shellcheck shell=bash`；无块形
  式，`: <<'END' ... END` 是少见的变通做法。
- `# shellcheck disable=SC2086` 行作用于下一条命令；应当将其紧贴于对应命令上方。

## HTML 与 CSS

- HTML 注释是 `<!-- text -->`；它们不得包含 `--`，亦不得嵌套，并且除非构建时剥离，否则会留在所提供
  的源码中。
- 纯 CSS 只有 `/* ... */`；`//` 在该处无效，而 Sass 与 SCSS 把 `//` 当作静默注释、把 `/* ... */` 当
  作输出注释。
- JSX 与 TSX 注释是 `{/* ... */}`；模板另有 `{# #}`（Jinja）、`<%# %>`（ERB）与 `{{! }}`
  （Handlebars）；Stylelint 与 Prettier 指令应当放在最窄的节点上并给出理由。
- 旧式 IE 条件注释已过时；应当在代码中使用特性检测，而非标记注释。

## YAML 与 TOML

- 两者均使用 `#` 直到行尾；带引号标量内的 `#` 是数据，YAML 亦要求 `#` 前有空白。
- 应当把注释放在它所解释的键上方；行尾注释在嵌套结构中折行效果很差。
- JSON 无注释语法：严格 JSON 中不得使用 `//` 或 `/* ... */`；应当在 schema、同级的 Markdown 文件
  或 `description` 字段中说明；JSONC 与 JSON5 只用于明确声明支持的配置工具。
- `$comment` 是合法的 JSON Schema 键，而 `_comment` 数据键会污染 schema；Helm 在 YAML 中使用 `#`，
  并用 `{{/* ... */}}` 表示 Go 模板注释。

## Terraform 与 HCL

- `#` 是规范的单行注释（`//` 能够解析，但不符合风格指南）；`/* ... */` 是块注释。
- `description` 属性是 `terraform-docs` 会渲染的文档；块上方的 `#` 承载理由，引用或 `moved` 块表达依
  赖关系。
- 扫描器指令为 `# trivy:ignore:<ID>`、`#tfsec:ignore:<rule>` 与 `# tflint-ignore: <rule>`；只有
  tflint 支持行内理由，所以另外两个应当把理由写在旁边的注释里。
- Terraform 1.15+ 的 `variable` 与 `output` 块有 `deprecated` 参数；更早版本或 provider 参数则在源码
  注释中写明替代项与移除计划。发布说明文档属于 documentation-conventions；声明的时间与位置属于
  release-operations-conventions。

## Markdown 与 XML

- Markdown 注释是 `<!-- ... -->`；渲染输出会剥离它们，但源码会保留，所以不得在其中放置机密或私有说明。
- 工具指令为 `<!-- markdownlint-disable rule -->` 与 `<!-- prettier-ignore -->`，放在受影响的块旁边。
- XML 注释不得包含 `--`，不得嵌套，亦不得位于 XML 声明之前；C# 的 XML 文档是主要的 XML 文档注释体
  系；front matter 是数据，不是注释。
- Markdown 注释单独成行；置于表格行或围栏内部时，它们可能破坏块结构或按字面渲染。

## 跨语言规则

- 注释语法匹配文件的语言，而非项目或编辑器默认值。
- 应当把文档注释精确放在工具读取它的位置；偏移一行即成为生成文档将丢弃的正文。
- 使用语言的标记拼写与项目配置的扫描器。
- 存在语言机制时，以机制承载弃用；否则以文档注释承载。
- 行宽、自然语言与大小写自项目配置读取；本 skill 未规定时按项目约定补充，在每种文件类型中都是如此。
