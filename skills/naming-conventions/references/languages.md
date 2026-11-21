# 语言约定

本文件在 `SKILL.md` 之后阅读，以每种语言强制或主流的约定，覆盖与语言无关的默认值。项目约定与事实属于输入；
本 skill 的规则优先，项目约定仅在本 skill 未规定时补充。语言没有唯一约定的，使用 `SKILL.md` 中的默认值。

## 矩阵

| 语言 | 类型 | 函数或方法 | 变量或参数 | 常量 | 文件 | 测试 |
|---|---|---|---|---|---|---|
| Python | `PascalCase` | `snake_case` | `snake_case` | `UPPER_SNAKE` | `snake_case.py` | `test_*.py` |
| TypeScript / JavaScript | `PascalCase` | `camelCase` | `camelCase` | `UPPER_SNAKE` | `kebab-case.ts`, `PascalCase.tsx` | `*.test.ts` |
| Java | `PascalCase` | `camelCase` | `camelCase` | `UPPER_SNAKE` | `PascalCase.java` | `*Test.java` |
| Kotlin | `PascalCase` | `camelCase` | `camelCase` | `UPPER_SNAKE` | `PascalCase.kt` | `*Test.kt` |
| C# | `PascalCase` | `PascalCase` | `camelCase` | `PascalCase` | `PascalCase.cs` | `*Tests.cs` |
| Go | `PascalCase` 或 `MixedCaps` | `MixedCaps` | `mixedCaps` | `MixedCaps` | `snake_case.go` | `*_test.go` |
| Rust | `PascalCase` | `snake_case` | `snake_case` | `UPPER_SNAKE` | `snake_case.rs` | `#[cfg(test)]` 或 `tests/` |
| C / C++ | `PascalCase` | `snake_case` | `snake_case` | `UPPER_SNAKE` 或 `kConstant` | `snake_case.c`、`.h`、`.cc` | `*_test.cc` |
| Ruby | `PascalCase` | `snake_case` | `snake_case` | `UPPER_SNAKE` | `snake_case.rb` | `*_spec.rb` |
| PHP | `PascalCase` | `camelCase` | `camelCase` | `UPPER_SNAKE` | `PascalCase.php` | `*Test.php` |
| Swift | `PascalCase` | `camelCase` | `camelCase` | `camelCase` | `PascalCase.swift` | `*Tests.swift` |
| Dart | `PascalCase` | `camelCase` | `camelCase` | `lowerCamelCase` | `snake_case.dart` | `*_test.dart` |
| SQL | 表 `snake_case`、列 `snake_case` | 不适用 | 约束 `snake_case` | 不适用 | `YYYYMMDDHHMMSS_description.sql` | 迁移测试 |
| Shell | 不适用 | `snake_case` | `snake_case`，环境变量 `UPPER_SNAKE` | `UPPER_SNAKE` | `kebab-case.sh` | `*_test.sh` |
| HTML / CSS | 类 `kebab-case`、BEM | 不适用 | 自定义属性 `--kebab-case` | 不适用 | `kebab-case.css` | 视觉测试 |
| JSON / YAML | 对象 `PascalCase` 或 `snake_case` | 不适用 | 键每个 schema 一种大小写 | 不适用 | `kebab-case.json` | schema 测试 |

## Python

- 遵循 PEP 8：函数与变量用 `snake_case`，类用 `PascalCase`，常量用 `UPPER_SNAKE`。
- 模块与包用 `snake_case`；常规包为带 `__init__.py` 的目录，命名空间包（PEP 420）则省略该文件。
- 单个前导下划线表示内部使用；类层次结构需要的除外，避免双下划线名称改写。
- 接口不得使用 `I` 前缀；protocol 与 ABC 使用能力名称（`Readable`、`UserStore`）。
- 测试文件为 `test_*.py` 或 `*_test.py`；测试函数以 `test_` 开头并说明行为。
- 布尔值用 `is_`、`has_`、`can_`、`should_`、`needs_`；避免 `not_`。
- 类型提示用 `UserId` 别名表示领域标识符；不得遮蔽内置名称（`list`、`dict`、`id`）。

## TypeScript 与 JavaScript

- 变量、函数与方法用 `camelCase`；类、类型、接口、枚举与 React 组件用 `PascalCase`。
- 接口通常不加 `I` 前缀；类型别名用 `PascalCase`（`type UserId = string`）。
- 文件名遵循项目：模块用 `kebab-case.ts`，组件用 `PascalCase.tsx`，文件夹的公开接口用 `index.ts`。
- 测试为 `*.test.ts` 或 `*.spec.ts`；React 测试与组件使用相同的基本文件名。
- 首字母缩略词按单词处理：`userId`、`httpClient`、`parseUrl`；不得使用 `userID` 或 `HTTPClient`。
- 布尔变量与谓词使用 `is`、`has`、`can`、`should`；名为 `isX` 的函数必须返回布尔值。
- 仅真正的常量使用 `UPPER_SNAKE`；`const` 局部绑定仍用 `camelCase`。

## Java

- 类、接口、枚举与 record 用 `PascalCase`；方法与变量用 `camelCase`；常量用 `UPPER_SNAKE`。
- 包为小写反向域名：`com.example.billing`；不得使用下划线或大写。
- 避免 `I` 接口前缀与 `Impl` 类后缀；按实现机制命名（`SqlInvoiceRepository`）。
- 测试类以 `Test` 结尾；测试方法说明行为（`shouldRejectExpiredCard`）。
- 首字母缩略词按单词大小写处理：`UserId`、`HttpClient`、`UrlParser`；`ID` 通常写作 `Id`。
- 边界处的 record 或 DTO 以 `Dto`、`Request` 或 `Response` 结尾；领域类型不得添加该类后缀。

## Kotlin

- 类与对象用 `PascalCase`；函数与属性用 `camelCase`；常量用 `UPPER_SNAKE`。
- 文件为 `PascalCase.kt`，通常以主要类命名；多个顶层声明仅在属于同一概念时，方可共用一个文件。
- 包名小写；不得使用下划线。
- 测试类以 `Test` 结尾；测试中允许使用反引号名称，但生产标识符仍用 `camelCase`。
- 首字母缩略词按单词处理：`UserId`、`HttpClient`、`parseUrl`。

## C#

- 类型、方法、属性、事件与常量用 `PascalCase`；参数与局部变量用 `camelCase`；私有字段用 `_camelCase`。
- 接口使用 `I` 前缀（`IUserStore`）；泛型参数为 `T`、`TKey`、`TValue`。
- 异步方法使用 `Async` 后缀（`LoadAsync`），但框架约定另有规定的除外。
- 测试类以 `Tests` 结尾；测试方法用 `Method_Scenario_Expected`。
- 首字母缩略词遵循 .NET 风格：`UserId`、`HttpClient`；仅两字母缩略词写成 `IOStream` 这种形式。
- 命名空间用 `PascalCase`，并与文件夹结构对应。

## Go

- 使用 `MixedCaps`：导出标识符首字母大写（`UserID`、`HTTPServer`），未导出标识符首字母小写（`userID`）。
- 包名简短、小写，不含下划线（`billing`，不得写作 `billing_service`）。
- getter 不得加 `Get` 前缀；字段或方法名即为名词（`user.Name()`），setter 可以使用 `Set`。
- 测试文件为 `*_test.go`；函数为 `TestXxx`、`BenchmarkXxx`、`ExampleXxx`；表驱动测试使用 `t.Run` 与描述
  性的用例名。
- 首字母缩略词的写法应当统一：`URL`、`ID`、`HTTP`、`API`、`JSON`；即 `UserID`、`HTTPServer`、
  `URLParser`。
- 错误变量用 `err`；包装错误用 `fmt.Errorf("...: %w", err)` 和哨兵值 `ErrNotFound`。

## Rust

- 函数、方法、变量、模块与 crate 名用 `snake_case`；类型、trait、枚举与变体用 `PascalCase`；常量与
  static 用 `UPPER_SNAKE`。
- 模块文件为 `snake_case.rs`；现代布局为 `module.rs` 与 `module/` 并列，`mod.rs` 为部分项目仍在使用的旧
  形式。
- 测试函数说明行为（`rejects_expired_card`）；集成测试置于 `tests/` 中，并使用公开 API。
- 布尔值用 `is_`、`has_`、`can_`；谓词返回 `bool`。
- 首字母缩略词在 snake_case 中按单词处理：`user_id`、`http_client`、`parse_url`。
- trait 命名能力（`Readable`、`Store`）；实现类型命名机制（`SqlStore`）。

## C 与 C++

- 没有统一约定；应当阅读项目。常见默认值为：函数与变量用 `snake_case`，类型用 `PascalCase`，宏与常量
  用 `UPPER_SNAKE`。
- 头文件保护用 `PROJECT_PATH_FILE_H` 或 `#pragma once`；选定一种并保持一致。
- 命名空间小写（`billing`）；嵌套命名空间用 `billing::internal`。
- 常量可以用 `kConstant`（Google 风格）或 `UPPER_SNAKE`；遵循项目，不得两种混用。
- 测试文件为 `*_test.cc` 或 `*_test.cpp`；测试名说明行为。
- 全局作用域不得使用前导下划线加大写字母；该写法为保留形式。

## Ruby

- 方法与变量用 `snake_case`；类与模块用 `PascalCase`；常量用 `UPPER_SNAKE`。
- 谓词方法以 `?` 结尾（`valid?`）；危险方法以 `!` 结尾（`save!`）；返回非布尔值的方法不得使用 `?`。
- 文件为 `snake_case.rb`；测试文件为 `*_spec.rb`（RSpec）或 `*_test.rb`（Minitest）。
- 用作命名空间的模块用 `PascalCase`；嵌套常量按模块名解析。
- 首字母缩略词按单词处理：`UserId`、`HttpClient`、`parse_url`。

## PHP

- 类、接口、trait 与枚举用 `PascalCase`；方法用 `camelCase`；变量用 `$camelCase`；常量用 `UPPER_SNAKE`。
- PSR-4 文件名与类名一致：`UserRepository.php`。
- 命名空间用 `PascalCase`，并与目录结构对应。
- 测试类以 `Test` 结尾；方法以 `test` 开头，或使用框架的属性约定。
- 首字母缩略词按单词处理：`UserId`、`HttpClient`、`parseUrl`。

## Swift

- 类型、协议与枚举用 `PascalCase`；函数、方法、属性与常量用 `camelCase`。
- 协议命名能力（`Readable`、`UserStore`）；不得使用 `I` 前缀。
- 文件为 `PascalCase.swift`；测试文件为 `*Tests.swift`；测试方法以 `test` 开头。
- 布尔值用 `is`、`has`、`can`；名为 `isX` 的属性为 `Bool`。
- 首字母缩略词按单词处理：`userId`、`httpClient`、`parseUrl`。

## Dart

- 类型用 `PascalCase`；函数、变量与常量用 `camelCase`；文件名用 `snake_case`。
- 测试文件为 `*_test.dart`；测试名说明行为。
- 私有标识符以 `_` 开头；库级私有按库划分，不按类划分。
- 首字母缩略词按单词处理：`userId`、`httpClient`、`parseUrl`。

## SQL

- 表用复数 `snake_case`；列用单数 `snake_case`；键与约束遵循 `dimensions-interface.md` 第 17 节。
- 审计列与软删除列用 `created_at`、`updated_at`、`deleted_at`；布尔值用 `is_`。
- 迁移文件为 `YYYYMMDDHHMMSS_description.sql`；每个文件仅含一次逻辑变更。
- 避免带引号的混合大小写标识符；该写法使每个查询区分大小写并且容易出错。
- 不得使用保留字作标识符；旧 schema 已经这样使用的，保留名称并始终加引号引用。

## Shell

- 函数与局部变量用 `snake_case`；环境变量与常量用 `UPPER_SNAKE`。
- 脚本文件为 `kebab-case.sh`；应当设为可执行并以 shebang 开头。
- 测试文件为 `*_test.sh`；测试函数说明行为，并使用 `set -euo pipefail`。
- 除循环索引外避免单字母变量；展开变量时加引号；名称中不得有空格。
- 命令名用动词（`build`、`deploy`）；标志用 kebab-case。

## HTML 与 CSS

- 类与 ID 用 `kebab-case`；BEM 为 `block__element--modifier`。
- 自定义属性为 `--color-bg`、`--space-md`；不得使用无法解释的缩写。
- JavaScript 钩子使用 `js-` 前缀，且不参与样式；ID 保留给锚点与标签。
- 文件为 `kebab-case.css` 或 `kebab-case.scss`；Sass 的 partial 以 `_` 开头。
- data 属性为 `data-` 加 kebab-case；可访问名称与可见标签一致。

## JSON 与 YAML

- 每个 schema 选定一种键大小写（`snake_case` 或 `camelCase`），并在生产者与消费者之间保持一致。
- 键中不得含空格；除表达命名空间外，避免点号；避免保留字。
- 时间戳用 `_at` 加 RFC 3339；ID 用 `<entity>_id`；布尔值用 `is_`/`has_`。
- YAML 文件使用 kebab-case 名称；锚点与别名按概念命名，不得命名为 `default`。
- 不得在键中编码类型；不得将 `data` 当作万能包装。

## 跨语言规则

- 不得在边界之间搬运大小写：应当在边缘将 `snake_case` JSON 映射为 `camelCase` 代码，不得在中间映射。
- 首字母缩略词遵循目标语言；Go 用 `UserID`，C# 用 `UserId`，Python 与 Rust 用 `user_id`。
- 公开名称在每种语言中均属于 API 契约；仅在提供弃用或版本化路径时，方可重命名。
- 框架强制某个名称时（生命周期钩子、ORM 列、测试发现），应当遵循框架并记录这条例外。
