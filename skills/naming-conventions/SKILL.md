---
name: naming-conventions
description: 定义、审查并重构任意编程项目的名称，覆盖文件、目录、包、类型、函数、变量、API、数据库、配置、测试、提交消息、分支、标签与资产。适用于启动项目或模块、命名新标识符、审查 diff 中的命名问题，或统一不一致的名称。提供与语言无关的默认值，并按语言给出覆盖规则。不适用于提交流程与分支流程（提交流程与分支流程见 vcs-collaboration-conventions；提交消息、分支与标签的命名归本 skill）、契约与 schema 演进（见 api-and-data-conventions）与格式化配置（见 code-style-conventions）。
argument-hint: '[路径或符号]'
---

# 命名规范

名称是代码库中阅读次数最多的接口。良好的名称说明一个事物是什么、做什么，贴合语言，并在各层之间保持稳定；不
良的名称则迫使每位读者从实现反推意图。本 skill 规定命名的决策流程，以及项目各类命名产物所需的完整规则集。

## 适用范围与优先级

效力依下列层级判断：高层覆盖低层，低层仅在高层未规定时补充：

1. 强制性的平台、语言、宿主与用户全局约束。Go 导出标识符、C# 的 `I` 接口与 PEP 8 均非可选事项。
2. 本 skill 的规则与默认值。
3. 既有项目约定与事实。项目约定仅在本 skill 未规定时补充；现有代码、命名表、lint 配置与语言版本作为输入，
   依本 skill 的规则处理，不得覆盖本 skill。
4. 个人偏好，不得覆盖上述三层。

- 生成代码、第三方引入代码、外部协议字段与第三方 schema 不受本规范约束。上述名称应当保留，在边界处隔离，
  并将映射记录于项目命名表。
- 重命名属于一次变更，不属于清理。代理应当先阅读全部引用，在授权范围内更新测试、文档与 fixture，并将任何公开名称视为 API。
- 同一效力层级的强制规则冲突时，代理应当报告用户裁决，不得自行选定。非强制的项目约定冲突，可以说明冲突与
  所选约定；跨层冲突依用户全局约束 §3.3 处理，并记录决定，使后续变更遵循该决定。

本 skill 规定名称、大小写、被禁用的同义词、文件名、目录名、锚点、ADR 编号、命名表与重命名机制；其他产物类
别的策略与流程，依下列职责归属：

- 提交与 PR 流程、合并与审查策略、历史记录与审查深度，由 vcs-collaboration-conventions 负责。
- API 版本化、分页风格、CRUD 语义、错误模型，以及数据库 schema 变更流程与迁移安全性，由 api-and-data-conventions 负责。
- 格式化工具与 linter 配置、行宽、配置的优先级与语义，以及错误与日志内容策略，由 code-style-conventions 负责。
- 测试策略、门禁、测试处置，以及跳过、隔离与豁免策略，由 testing-and-quality-conventions 负责。
- 遥测设计、功能开关生命周期、CI/CD、发布时机，以及弃用声明的时间与位置，由 release-operations-conventions 负责。
- 访问控制与权限策略，以及机密扫描、轮换与披露，由 security-compliance-conventions 负责。
- 包与分发元数据，由 repository-governance-conventions 负责；版本策略、发布流程与审批、上线与回滚，由
  release-operations-conventions 负责。
- 文档正文、变更日志、发布说明、文档站与术语表的散文定义，由 documentation-conventions 负责；名称、大小写、被禁用的同义词、文件名、目录名、锚点与 ADR 编号由本 skill 负责。
- 指令文件，由 system-prompt-authoring 负责。

## 流程

1. 对产物分类：文件、目录、包、类型、函数、变量、常量、API 字段、数据库对象、配置键、测试、提交或资产。
2. 以项目领域语言为该概念命名；代理应当先核查命名表与术语表是否已有现成术语。
3. 从形式表中选择语法形式（名词、动词、形容词、复数）。
4. 为产物与语言选择大小写风格；覆盖规则见 `references/languages.md`。
5. 检查冲突、对称性、长度、可读性（能否读出声）、可搜索性，以及有误导性的编码。
6. 新领域术语在超过一处使用前，应当先行记录于项目命名表。
7. 需要重命名时，代理应当列出全部引用，选择别名或弃用路径，并核对完整 diff。

## 核心规则

- **一个概念，一个名称。** 一个名称对应一个概念。同一事物有多种叫法，属于缺陷；同一名称指两件事，属于冲
  突。
- **命名意图，而不是实现。** `activeUsers` 优于 `filteredList2`；`retryCount` 优于 `loopCounter`。
- **使用领域语言。** 应当优先采用用户与产品使用的词；记录被禁用的同义词。
- **遵循语言。** 不得从其他语言引入大小写或前缀；Python 中的 `IUserStore` 或 Go 中的 `user_repository`，即
  使概念正确，亦属错误。
- **可搜索、可读出声。** 除循环索引外，应当避免单字母与双字母名称、省略元音的写法以及辅音连缀；审查时应当
  有人能够将名称读出声。
- **不得编码类型。** 不得采用匈牙利命名法，不得添加 `obj`、`str`、`arr`、`list` 后缀；仅当类型无法表达时，
  方得编码单位、范围或含义（`timeout_ms`、`amount_cents`）。
- **优先肯定式。** `isEnabled` 优于 `isNotDisabled`；不得构造双重否定。
- **集合用复数。** `users` 包含多个用户；`user` 表示一个用户。映射应当写作 `usersById`，不得写作 `userMap`。
- **按作用域控制名称长度。** 局部变量使用一到两个词，公开 API 使用两到四个词；长名称胜于含糊名称，前提是每
  个词都承载含义。
- **不得在请求之外重命名。** 一致性具有价值，但批量重命名属于另一次需要审查的变更。

## 大小写矩阵

下列默认值与语言无关。`references/languages.md` 按语言与框架覆盖上述默认值。

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
| 测试文件 | 被测单元名 + 语言测试标记 | `<unit>_test.py`, `<Unit>Test.java`, `<unit>.test.ts` |
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
| 标识符 | 代码 `<Entity>Id`；存储与 HTTP JSON 资源标识 `<entity>_id` | `CustomerId`, `customer_id` |
| 时间戳 | `<event>_at` | `created_at`, `paid_at` |
| 时长 | `<quantity>_ms`、`_s` | `timeout_ms` |
| 计数 | `<thing>_count` | `retry_count` |
| 金额 | `<amount>_cents` 加货币 | `total_cents`, `currency` |
| 比率或百分比 | `_ratio`（0-1）或 `_pct`（0-100） | `success_ratio`, `discount_pct` |

## 维度索引

每个维度的详细规则、示例与边界情况见 `references/` 中对应的维度文件；维度列中的编号就是该文件中的节号。

| 维度 | 首条规则 | 详情 |
|---|---|---|
| 1. 文件与目录 | 名称小写、不含空格，并与主要导出或职责匹配。 | `references/dimensions-code.md` 第 1 节 |
| 2. 包与命名空间 | 采用反向域名或简短小写名称，公开接口保持稳定。 | `references/dimensions-code.md` 第 2 节 |
| 3. 模块与导入 | 以能力名词命名，别名简短且无歧义，不得出现循环名称。 | `references/dimensions-code.md` 第 3 节 |
| 4. 类型与接口 | 使用单数名词；体现能力或角色，C# 之外不得使用 `I` 前缀。 | `references/dimensions-code.md` 第 4 节 |
| 5. 枚举与联合类型 | 类型名用单数，成员保持稳定，不得使用数字名称。 | `references/dimensions-code.md` 第 5 节 |
| 6. 函数与方法 | 使用动词短语；一个名称对应一个动作；谓词使用谓词名。 | `references/dimensions-code.md` 第 6 节 |
| 7. 变量、参数与字段 | 使用名词，长度随作用域变化，不得添加类型前缀。 | `references/dimensions-code.md` 第 7 节 |
| 8. 常量 | 使用 UPPER_SNAKE，名称含单位，不得使用魔法值。 | `references/dimensions-code.md` 第 8 节 |
| 9. 布尔值与谓词 | 采用肯定的 `is`/`has`/`can`/`should`；不得出现非布尔的 `isX`。 | `references/dimensions-code.md` 第 9 节 |
| 10. 集合、映射、Set 与元组 | 使用复数名词；映射以 `by` 表示，显式写出键与值。 | `references/dimensions-code.md` 第 10 节 |
| 11. 数量、单位、时间、金额、比率、范围 | 使用单位后缀、ISO 货币与整数最小单位；时刻用 `_at`，时长用 `_ms`。 | `references/dimensions-code.md` 第 11 节 |
| 12. 异步、并发、流、回调 | 遵循语言约定；语言不惯用时，不得添加 `Async` 后缀。 | `references/dimensions-system.md` 第 12 节 |
| 13. 错误与结果 | 使用具体的错误类与稳定的错误码；不得使用兜底名称。 | `references/dimensions-system.md` 第 13 节 |
| 14. 测试与测试替身 | 名称包含行为与条件；`Fake`、`Stub`、`Mock`、`Spy` 含义不同。 | `references/dimensions-code.md` 第 14 节 |
| 15. HTTP、RPC 与 GraphQL | 资源用复数，路径用 kebab 风格，每个 schema 仅用一种 JSON 大小写。 | `references/dimensions-interface.md` 第 15 节 |
| 16. JSON 与序列化 | 每个 schema 仅用一种键大小写；在边界处映射为代码的大小写。 | `references/dimensions-interface.md` 第 16 节 |
| 17. 数据库与迁移 | 表名用复数 snake 风格，列名用单数，索引与约束带前缀。 | `references/dimensions-interface.md` 第 17 节 |
| 18. 配置与环境 | 环境变量用 UPPER_SNAKE，键带前缀，名称中不得含机密。 | `references/dimensions-interface.md` 第 18 节 |
| 19. CLI | 标志用 kebab 风格，命令用动词，短标志保持一致。 | `references/dimensions-interface.md` 第 19 节 |
| 20. 日志、事件、指标与追踪 | 字段用稳定的 snake 风格，事件用 `object.action`，指标带单位后缀。 | `references/dimensions-interface.md` 第 20 节 |
| 21. 资产、CSS、HTML 与 i18n | 文件名用 kebab 风格，类用 BEM 或工具类，键用点分隔。 | `references/dimensions-interface.md` 第 21 节 |
| 22. 提交、分支与标签 | 提交用 `type(scope): summary`，分支用 `type/slug`，标签用 SemVer。 | `references/dimensions-interface.md` 第 22 节 |
| 23. 功能开关与弃用 | 命名移除路径，不得使用永久的 `legacy_` 前缀。 | `references/dimensions-interface.md` 第 23 节 |
| 24. 缩写、首字母缩略词与复数 | 维护允许清单，缩略词按单词处理，不得省略元音。 | `references/dimensions-code.md` 第 24 节 |
| 25. 对称与配对 | 各处使用同一组配对：`open/close`、`add/remove`。 | `references/dimensions-code.md` 第 25 节 |
| 26. 长度、作用域与可搜索性 | 长度随作用域变化；名称应当足够独特，便于搜索。 | `references/dimensions-code.md` 第 26 节 |
| 27. 重命名与迁移 | 以证据为前提，列出引用，提供别名或弃用路径，变更范围受限。 | `references/dimensions-system.md` 第 27 节 |
| 28. 豁免 | 生成、引入与外部名称保持不变；在边界处映射。 | `references/dimensions-system.md` 第 28 节 |
| 29. 基础设施与部署 | 名称与小写 DNS 兼容；环境与所有者写入资源标签。 | `references/dimensions-system.md` 第 29 节 |
| 30. 权限、角色、作用域与审计动作 | 使用 `domain.action`；采用单一分隔符；按能力而非职位命名。 | `references/dimensions-system.md` 第 30 节 |
| 31. 已发布包与模块 | 遵循包仓库允许的字符与大小写。 | `references/dimensions-system.md` 第 31 节 |
| 32. 组件、Hooks 与 UI 状态 | 组件用 PascalCase，hooks 用 `useX`，状态名用肯定式。 | `references/dimensions-system.md` 第 32 节 |
| 33. 领域模型与领域事件 | 实体用单数，事件用过去时，命令用祈使式。 | `references/dimensions-system.md` 第 33 节 |
| 34. 文档、图表与决策 | 文件名用 kebab 风格，锚点保持稳定，ADR 编号。 | `references/dimensions-system.md` 第 34 节 |

## 反模式

| 反模式 | 为什么失败 | 修复 |
|---|---|---|
| `data`、`info`、`item`、`obj`、`temp`、`foo`、`bar` | 未表达任何信息，迫使读者阅读函数体。 | 命名概念本身：`invoice`、`parseResult`、`pendingJobs`。 |
| `Manager`、`Helper`、`Util`、`Common`、`Base` | 掩盖职责，并吸引不相关的代码。 | 命名角色：`BillingService`、`RetryPolicy`、`PathFormatter`。 |
| `userObj`、`strName`、`arrItems` | 编码了类型，重构后立即过时。 | `user`、`name`、`items`。 |
| `notReady`、`disableCache`、`isNotUnavailable` | 否定式名称迫使每个读取点反向理解。 | `isReady`、`cacheEnabled`、`isAvailable`。 |
| `usr`、`cfg`、`mgr`、`btn`、`msg` | 节省三个字符，增加一次查找。 | `user`、`config`、`manager`、`button`、`message`。 |
| 同一概念使用 `client` / `customer` / `buyer` | 读者无法判断三者是否存在区别。 | 选定一个领域术语，禁用其余说法。 |
| 同一层同时出现 `userId` 与 `user_id` | 破坏搜索与机械化重构。 | 每层仅用一种大小写；仅在边界处映射。 |
| 名为 `isActive` 却返回计数 | 名称表达的类型错误。 | `activeCount`。 |
| 在 `getX` 暗示 I/O 处，纯读取器使用 `getUser` | 暗示一次并不发生的读取。 | 使用 `user` 属性；I/O 使用 `fetchUser`；其余情形名词或 `get` 访问器均可。 |
| `UserServiceImpl` | 泄露实现，并增加噪声。 | `SqlUserRepository`、`StripePaymentGateway`。 |
| Python 或 Go 中的 `IUserStore` | 将 C# 约定带入拒绝该约定的语言。 | `UserStore` 或 `UserDirectory`。 |
| `user2`、`newUser`、`tempUser` | 带编号或时间性的名称立即过时。 | `importedUser`、`pendingUser`、`user`。 |
| 布尔值命名为 `flag`、`status`、`check` | 含义含糊，类型亦常常错误。 | `hasExported`、`isReady`、`isValid`。 |
| 仅使用 `do`、`handle`、`process`、`run` | 未说明处理何种对象或产出何种结果。 | `handlePaymentFailure`、`processRefund`、`runMigration`。 |

## 项目命名表

项目启动时应当创建此表，保存于仓库中，并在术语扩散前先行增加一行；术语解释见项目术语表（规则见 `documentation-conventions` 的 [术语与术语表维度](../documentation-conventions/references/dimensions-project.md) 第 16 节），本表只维护名称与命名约束，不复制定义：

| 术语 | 规范名称 | 避免 | 大小写 | 命名表维护人 |
|---|---|---|---|---|
| invoice | `Invoice` | bill、statement | PascalCase | billing |
| customer | `Customer` | client、buyer、account | PascalCase | CRM |
| amount | `amount_cents` | amount、total | snake_case | billing |

## 审查清单

- [ ] 术语与项目命名表或术语表一致。
- [ ] 大小写与语言及产物匹配。
- [ ] 语法形式与产物种类匹配。
- [ ] 不存在同义词、冲突或容易混淆的近似名称。
- [ ] 不存在未加限定的泛化词。
- [ ] 名称可读出声，且足够独特便于搜索。
- [ ] 长度与作用域匹配；未编码类型或实现。
- [ ] 布尔值为肯定式，且确为布尔类型。
- [ ] 集合为复数；映射写明其键。
- [ ] 单位、时间、金额、比率与范围均显式。
- [ ] 异步、错误、测试与 API 约定与所用技术栈匹配。
- [ ] 文件名与主要导出或职责匹配。
- [ ] 数据库、API、配置与日志名称在各层之间一致。
- [ ] 缩写均在允许清单中；首字母缩略词遵循语言规则。
- [ ] 对称配对使用相同的词。
- [ ] 公开重命名具有弃用或别名路径。
- [ ] 重命名具有回滚路径，且回滚顺序与上线顺序相反。
- [ ] 引用、测试、文档、fixture 与快照均已更新。
- [ ] 未在授权范围之外重命名。
- [ ] 命名表已更新。
- [ ] 项目配置命名 lint 规则的，该规则通过。

## 示例

<example>
场景：跨层命名一个新的 HTTP 资源。
做法：数据库表为 `orders`，列为 `customer_id`，主键为 `id`，索引为 `idx_orders_customer_id`；API 路径为
`/v1/orders`，查询参数为 `created_after`；JSON 字段为 `created_at`、`is_paid`；TypeScript 类型为 `Order`，
函数为 `listOrders`，布尔值为 `isPaid`；测试为 `list_orders_test` 或 `listOrders.test.ts`。
</example>

<example>
场景：重命名一个布尔值。
做法：将 `notDisabled` 改为 `isEnabled`；将 `flag` 改为 `hasExported`；可空布尔值改为三态枚举
（`Visibility.PUBLIC`、`Visibility.PRIVATE`、`Visibility.UNLISTED`），不得保留 `isPublic: boolean | null`。
</example>

<example>
场景：重命名一个含糊的服务。
做法：`UserManager` 同时负责查找与存储，该名称掩盖两项职责；应当将其拆分为负责查找的 `UserDirectory` 与
负责持久化的 `UserRepository`，并在一次受限的变更中更新全部调用点。
</example>

<example>
场景：命名数量值。
做法：将 `timeout` 改为 `timeout_ms`；将 `amount` 改为 `amount_cents` 加 `currency`；将 `discount` 改为
`discount_pct`（0-100）或 `discount_ratio`（0-1），并在命名表中记录该范围。
</example>

## 参考资料

按产物分类的完整规则集见 [references/dimensions-code.md](references/dimensions-code.md)、
[references/dimensions-interface.md](references/dimensions-interface.md) 与
[references/dimensions-system.md](references/dimensions-system.md)；按语言的大小写矩阵见
[references/languages.md](references/languages.md)。建立新项目的命名表之前，应当先阅读上述文件；日常工作
中，仅阅读适用的维度与适用的语言行。
