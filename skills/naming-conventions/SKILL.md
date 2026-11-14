---
name: naming-conventions
description: 在任何编程项目中定义、审查或重构名称，覆盖文件、目录、包、类型、函数、变量、API、数据库、配置、测试、提交与资产。适用于启动项目或模块、命名新标识符、审查 diff 中的命名问题，或统一不一致的名称。提供与语言无关的默认值，并按语言给出覆盖规则。
argument-hint: '[路径或符号]'
---

# 命名规范

名称是代码库中阅读次数最多的接口。好的名称说明一个事物是什么或做什么，贴合语言，并在各层之间保持稳定；
糟糕的名称则迫使每个读者从实现反推意图。本 skill 给出一套决策流程，以及项目命名的每个产物所需的完整规则集。

## 范围与优先级

应用第一条匹配的规则，不要在同一范围内混用约定：

1. 语言或框架的强制约定。Go 导出标识符、C# 的 `I` 接口与 PEP 8 都不是可选项。
2. 现有项目约定与 lint 配置。发明规则之前先读代码与配置。
3. 上面两级都没有规定时，采用本标准的默认值。
4. 个人偏好，它永远不能覆盖上面三级。

- 生成代码、第三方引入代码、外部协议字段与第三方 schema 不受约束。保留它们的名称，在边界处隔离，
  并把映射记录到项目命名表中。
- 重命名是一次变更，而不是清理。先读完所有引用，待在授权范围内，更新测试、文档与 fixture，
  并把任何公开名称当作 API。
- 两条规则冲突时，说明冲突与选定的规则；记录该决定，让后续变更遵循它。

本 skill 负责名称选择、命名表与重命名机制；其他产物类别的策略与流程按职责归属：

- vcs-collaboration-conventions 负责提交与 pull request 流程、合并与审查策略、历史记录与审查深度。
- api-and-data-conventions 负责 API 版本化、分页风格、CRUD 语义、错误模型，以及数据库 schema 变更流程
  与迁移安全性。
- code-style-conventions 负责格式化工具与 linter 配置、行宽、配置的优先级与语义，以及错误与日志内容策略。
- testing-and-quality-conventions 负责测试策略、门禁、测试处置，以及跳过、隔离与豁免策略。
- release-operations-conventions 负责遥测设计、功能开关生命周期、CI/CD、发布时机，以及弃用声明的时间
  与位置。
- security-compliance-conventions 负责访问控制与权限策略，以及机密扫描、轮换与披露。
- repository-governance-conventions 负责包与分发元数据以及发布策略。
- documentation-conventions 负责变更日志与文档更新、发布说明文档以及文档站点。
- system-prompt-authoring 负责指令文件。

## 流程

1. 对产物分类：文件、目录、包、类型、函数、变量、常量、API 字段、数据库对象、配置键、测试、提交或资产。
2. 用项目领域语言为该概念命名。先查命名表与术语表是否已有现成术语。
3. 从下面的形式表中选择语法形式（名词、动词、形容词、复数）。
4. 为产物与语言选择大小写风格；覆盖规则见 `references/languages.md`。
5. 检查冲突、对称性、长度、可读性（能否读出声）、可搜索性，以及有误导性的编码。
6. 在超过一处使用新领域术语之前，先把它记录到项目命名表。
7. 重命名时，列出全部引用，选择别名或弃用路径，并核对完整 diff。

## 核心规则

- **一个概念，一个名称。** 一个名称对应一个概念。同一事物有多种叫法是缺陷；同一名称指两件事是冲突。
- **命名意图，而不是实现。** `activeUsers` 优于 `filteredList2`；`retryCount` 优于 `loopCounter`。
- **使用领域语言。** 优先采用用户与产品使用的词；记录被禁用的同义词。
- **遵循语言。** 不要从别的语言引入大小写或前缀；Python 里的 `IUserStore` 或 Go 里的
  `user_repository` 即使概念正确也是错的。
- **可搜索、可读出声。** 除循环索引外，避免单字母与双字母名称、吞掉元音的写法以及辅音连缀；
  审查时总得有人能把名称念出来。
- **不要编码类型。** 不用匈牙利命名法，也不加 `obj`、`str`、`arr`、`list` 后缀；只有当类型无法表达时
  才编码单位、范围或含义（`timeout_ms`、`amount_cents`）。
- **优先肯定式。** `isEnabled` 优于 `isNotDisabled`；不要构造双重否定。
- **集合用复数。** `users` 包含多个用户；`user` 是一个用户。映射写成 `usersById`，不要写 `userMap`。
- **按作用域控制名称长度。** 局部变量用一到两个词，公开 API 用两到四个词；长名称胜于含糊名称，
  但前提是每个词都承载含义。
- **不要在请求之外重命名。** 一致性有价值，但批量重命名是另一次需要审查的变更。

## 大小写矩阵

以下是语言无关的默认值。`references/languages.md` 会按语言与框架覆盖它们。

| 产物 | 默认大小写 | 示例 |
|---|---|---|
| 包、命名空间 | 小写，点分隔 | `com.example.billing`, `app.users` |
| 模块 | snake_case 或全小写 | `user_repository.py`, `billing` |
| 目录 | kebab-case 或全小写 | `order-items/`, `users/` |
| 源文件 | 与语言及主要导出匹配 | `user_repository.py`, `UserRepository.java` |
| 类型、类、结构体、record | PascalCase | `UserRepository`, `OrderItem` |
| 接口、协议 | PascalCase，体现能力或角色 | `UserStore`, `PaymentGateway`, C# 中的 `IUserStore` |
| 枚举类型 | PascalCase，单数 | `OrderStatus` |
| 枚举成员 | UPPER_SNAKE 或 PascalCase | `PENDING`, `Pending` |
| 函数、方法 | camelCase 或 snake_case | `listActiveUsers`, `list_active_users` |
| 变量、参数、字段 | camelCase 或 snake_case | `activeUsers`, `active_users` |
| 常量 | UPPER_SNAKE_CASE | `MAX_RETRY_COUNT` |
| 布尔值 | `is`/`has`/`can`/`should`/`needs` + 形容词 | `isEnabled`, `hasChildren`, `canRetry` |
| 测试函数 | 行为加条件 | `test_list_orders_returns_empty_for_new_user` |
| 测试文件 | `<unit>_test` 或 `<unit>.test` | `user_service_test.py`, `UserServiceTest.java` |
| 数据库表 | 复数 snake_case | `order_items` |
| 数据库列 | 单数 snake_case | `created_at`, `customer_id` |
| 索引、约束 | 带前缀的 snake_case | `idx_orders_customer_id`, `uq_users_email` |
| API 路径 | 复数 kebab-case | `/v1/order-items` |
| JSON 字段 | 每个 schema 一种大小写，通常 camel 或 snake | `createdAt`, `created_at` |
| 环境变量 | 带应用前缀的 UPPER_SNAKE_CASE | `APP_DATABASE_URL` |
| CLI 标志 | kebab-case | `--dry-run`, `--output-format` |
| CSS 类 | kebab-case 或 BEM | `order-item__price--discounted` |
| i18n 键 | 点分隔小写 | `orders.list.empty` |
| 提交类型 | 小写 | `feat`, `fix`, `refactor`, `docs` |
| 分支 | `type/short-description` | `feat/order-export` |
| 标签 | 带 `v` 前缀的 SemVer | `v1.4.0` |

## 语法形式

| 概念 | 形式 | 示例 |
|---|---|---|
| 动作 | 动词短语 | `sendInvoice`, `parseConfig` |
| 谓词 | 布尔形容词 | `isExpired`, `hasAccess` |
| 资源或实体 | 单数名词 | `Invoice`, `Customer` |
| 集合 | 复数名词 | `invoices`, `activeUsers` |
| 映射 | 名词加 `by` 键 | `invoicesById`, `priceBySku` |
| 工厂 | `XFactory` 或 `createX` | `InvoiceFactory`, `createInvoice` |
| 构建器 | `XBuilder` | `InvoiceBuilder` |
| 仓库 | `XRepository` | `InvoiceRepository` |
| 服务 | 仅真正的领域服务用 `XService` | `BillingService` |
| 适配器或网关 | `XAdapter`、`XGateway` | `StripeAdapter`, `PaymentGateway` |
| DTO 或线上模型 | `XDto`、`XRequest`、`XResponse` | `InvoiceDto`, `CreateOrderRequest` |
| 错误 | `XError` 或 `XException` | `InvoiceNotFoundError` |
| 选项或配置 | `XOptions`、`XConfig` | `RetryOptions` |
| 结果 | `XResult`、`XOutcome` | `PaymentResult` |
| 标识符 | `id` 或 `<entity>_id` | `id`, `customer_id` |
| 时间戳 | `<event>_at` | `created_at`, `paid_at` |
| 时长 | `<quantity>_ms`、`_s` | `timeout_ms` |
| 计数 | `<thing>_count` | `retry_count` |
| 金额 | `<amount>_cents` 加货币 | `total_cents`, `currency` |
| 比率或百分比 | `_ratio`（0-1）或 `_pct`（0-100） | `success_ratio`, `discount_pct` |

## 维度索引

每个维度的详细模式、示例与边界情况见 `references/dimensions.md`。

维度列中的数字是该文件中的节号。

| 维度 | 第一条规则 |
|---|---|
| 1. 文件与目录 | 小写、不含空格，与主要导出或职责匹配。 |
| 2. 包与命名空间 | 反向域名或简短小写，公开接口保持稳定。 |
| 3. 模块与导入 | 能力名词，简短无歧义的别名，不出现循环名称。 |
| 4. 类型与接口 | 单数名词；能力或角色，C# 之外不用 `I` 前缀。 |
| 5. 枚举与联合类型 | 单数类型，成员稳定，不用数字名称。 |
| 6. 函数与方法 | 动词短语；一个动作；谓词用谓词名。 |
| 7. 变量、参数与字段 | 名词，长度随作用域，不加类型前缀。 |
| 8. 常量 | UPPER_SNAKE，名称含单位，不用魔法值。 |
| 9. 布尔值与谓词 | 肯定的 `is`/`has`/`can`/`should`；绝不出现非布尔的 `isX`。 |
| 10. 集合、映射、Set 与元组 | 复数名词，`by` 映射，显式写出键与值。 |
| 11. 数量、单位、时间、金额、比率、范围 | 单位后缀，ISO 货币，整数最小单位；时刻用 `_at`，时长用 `_ms`。 |
| 12. 异步、并发、流、回调 | 遵循语言约定；不惯用时不加 `Async` 后缀。 |
| 13. 错误与结果 | 具体的错误类与稳定错误码；绝不用兜底名称。 |
| 14. 测试与测试替身 | 行为加条件；`Fake`、`Stub`、`Mock`、`Spy` 含义不同。 |
| 15. HTTP、RPC 与 GraphQL | 复数资源，kebab 路径，每个 schema 一种 JSON 大小写。 |
| 16. JSON 与序列化 | 每个 schema 一种键大小写；在边界映射为代码的大小写。 |
| 17. 数据库与迁移 | 复数 snake 表名，单数列名，带前缀的索引与约束。 |
| 18. 配置与环境 | UPPER_SNAKE 环境变量，带前缀的键，名称中不含机密。 |
| 19. CLI | kebab 标志，动词命令，短标志保持一致。 |
| 20. 日志、事件、指标与追踪 | 稳定的 snake 字段，`object.action` 事件，带单位后缀的指标。 |
| 21. 资产、CSS、HTML 与 i18n | kebab 文件名，BEM 或工具类，点分隔键。 |
| 22. 提交、分支与标签 | `type(scope): summary`，`type/slug`，SemVer。 |
| 23. 功能开关与弃用 | 命名移除路径，而不是永久的 `legacy_` 前缀。 |
| 24. 缩写、首字母缩略词与复数 | 允许清单，缩略词按单词处理，不吞元音。 |
| 25. 对称与配对 | 处处使用同一组配对：`open/close`、`add/remove`。 |
| 26. 长度、作用域与可搜索性 | 长度随作用域；名称要足够独特，便于搜索。 |
| 27. 重命名与迁移 | 证据、引用、别名或弃用，范围受限的变更。 |
| 28. 豁免 | 生成、引入与外部名称保持不变；在边界处映射。 |
| 29. 基础设施与部署 | DNS 兼容的小写；环境与所有者写在资源标签中。 |
| 30. 权限、角色、作用域与审计动作 | `domain.action`；单一分隔符；按能力而非职位命名。 |
| 31. 已发布包与模块 | 遵循包仓库允许的字符与大小写。 |
| 32. 组件、Hooks 与 UI 状态 | PascalCase 组件，`useX` hooks，肯定的状态名。 |
| 33. 领域模型与领域事件 | 单数实体，过去时事件，祈使式命令。 |
| 34. 文档、图表与决策 | kebab 文件名，稳定锚点，编号 ADR。 |

## 反模式

| 反模式 | 为什么失败 | 修复 |
|---|---|---|
| `data`、`info`、`item`、`obj`、`temp`、`foo`、`bar` | 什么也没说，迫使读者去读函数体。 | 命名概念本身：`invoice`、`parseResult`、`pendingJobs`。 |
| `Manager`、`Helper`、`Util`、`Common`、`Base` | 隐藏职责，并吸引不相关的代码。 | 命名角色：`BillingService`、`RetryPolicy`、`PathFormatter`。 |
| `userObj`、`strName`、`arrItems` | 编码了类型，重构后立刻过时。 | `user`、`name`、`items`。 |
| `notReady`、`disableCache`、`isNotUnavailable` | 否定式名称让每个读取点都要反向理解。 | `isReady`、`cacheEnabled`、`isAvailable`。 |
| `usr`、`cfg`、`mgr`、`btn`、`msg` | 省了三个字符，多了一次查找。 | `user`、`config`、`manager`、`button`、`message`。 |
| 同一概念用 `client` / `customer` / `buyer` | 读者分不清它们是否有区别。 | 选定一个领域术语，禁用其余说法。 |
| 同一层里同时出现 `userId` 与 `user_id` | 破坏搜索与机械化重构。 | 每层一种大小写；只在边界处映射。 |
| 名为 `isActive` 却返回计数 | 名称表达的类型是错的。 | `activeCount`。 |
| 在 `getX` 暗示 I/O 的地方，纯读取器却用 `getUser` | 暗示了一次并不发生的读取。 | 用 `user` 属性；I/O 用 `fetchUser`；其余情况名词或 `get` 访问器都可以。 |
| `UserServiceImpl` | 泄露实现，还增加噪音。 | `SqlUserRepository`、`StripePaymentGateway`。 |
| Python 或 Go 里的 `IUserStore` | 把 C# 约定带进拒绝它的语言。 | `UserStore` 或 `UserDirectory`。 |
| `user2`、`newUser`、`tempUser` | 带编号或时间性的名称会立刻腐化。 | `importedUser`、`pendingUser`、`user`。 |
| 布尔值命名为 `flag`、`status`、`check` | 含糊，而且类型常常就是错的。 | `hasExported`、`isReady`、`isValid`。 |
| 只有 `do`、`handle`、`process`、`run` | 隐藏了处理了什么或产出了什么。 | `handlePaymentFailure`、`processRefund`、`runMigration`。 |

## 项目命名表

项目启动时创建此表，保存在仓库中，并在术语扩散前先加一行：

| 术语 | 定义 | 规范名称 | 避免 | 大小写 | 负责人 |
|---|---|---|---|---|---|
| invoice | 开给客户的账单 | `Invoice` | bill、statement | PascalCase | billing |
| customer | 付款的一方 | `Customer` | client、buyer、account | PascalCase | CRM |
| amount | 以最小货币单位表示的金额 | `amount_cents` | amount、total | snake_case | billing |

## 审查清单

- [ ] 术语与项目命名表或术语表一致。
- [ ] 大小写与语言和产物匹配。
- [ ] 语法形式与产物种类匹配。
- [ ] 没有同义词、冲突或容易混淆的近似名称。
- [ ] 没有未加限定的泛化词。
- [ ] 布尔值是肯定式的，而且确实是布尔类型。
- [ ] 集合是复数；映射写明其键。
- [ ] 单位、时间、金额、比率与范围都是显式的。
- [ ] 异步、错误、测试与 API 约定与所用技术栈匹配。
- [ ] 文件名与主要导出或职责匹配。
- [ ] 数据库、API、配置与日志名称在各层之间一致。
- [ ] 缩写都在允许清单中；首字母缩略词遵循语言规则。
- [ ] 名称可读出声、可搜索。
- [ ] 对称的配对使用相同的词。
- [ ] 公开重命名有弃用或别名路径。
- [ ] 重命名有回滚路径，回滚顺序与上线顺序相反。
- [ ] 引用、测试、文档、fixture 与快照都已更新。
- [ ] 没有在授权范围之外重命名。
- [ ] 命名表已更新。
- [ ] 项目若配置了命名 lint 规则，该规则通过。

## 示例

<example>
跨层命名一个新的 HTTP 资源：
数据库表 `orders`，列 `customer_id`，主键 `id`，索引 `idx_orders_customer_id`；
API 路径 `/v1/orders`，查询参数 `created_after`；JSON `created_at`、`is_paid`；TypeScript 类型 `Order`，
函数 `listOrders`，布尔值 `isPaid`；测试 `list_orders_test` 或 `listOrders.test.ts`。
</example>

<example>
重命名一个布尔值：
`notDisabled` 改为 `isEnabled`；`flag` 改为 `hasExported`；可空布尔值改为三态枚举
（`Visibility.PUBLIC`、`Visibility.PRIVATE`、`Visibility.UNLISTED`），而不是 `isPublic: boolean | null`。
</example>

<example>
重命名一个含糊的服务：
`UserManager` 同时处理查找与存储。这个名称掩盖了两项职责；把它拆成负责查找的 `UserDirectory`
和负责持久化的 `UserRepository`，并在一次受限的变更中更新所有调用点。
</example>

<example>
命名数量值：
`timeout` 改为 `timeout_ms`；`amount` 改为 `amount_cents` 加 `currency`；`discount` 改为
`discount_pct`（0-100）或 `discount_ratio`（0-1），并在命名表中记录该范围。
</example>

## 参考资料

按产物分类的完整规则集见 [references/dimensions.md](references/dimensions.md)，按语言的大小写矩阵见
[references/languages.md](references/languages.md)。建立新项目的命名表之前先读这两份文件；日常工作中，
读适用的维度与适用的语言行。
