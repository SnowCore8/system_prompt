---
name: naming-conventions
description: 定义、审查并重构任意编程项目的名称，覆盖文件、目录、包、类型、函数、变量、API、数据库、配置、测试、提交消息、分支、发布标签、议题标签、资产与平台命名产物。适用于启动项目或模块、在 S2 计划中固定跨层名称契约、命名新标识符、审查 diff 中的命名问题、执行或审查重命名，或统一不一致的名称；提供与语言无关的默认值，并按语言给出覆盖规则。不适用于提交流程与分支流程（见 vcs-collaboration-conventions）、契约与 schema 演进（见 api-and-data-conventions）与格式化与 linter 配置（见 code-style-conventions）；提交消息、分支、发布标签与议题标签的命名由本 skill 裁定。
argument-hint: '[路径或符号]'
---

# 命名规范

名称是代码库中阅读次数最多的接口，良好的名称说明事物是什么、做什么，贴合语言，并在各层之间保持稳定。
本 skill 规定命名的决策流程与命名产物的完整规则集；阶段职责见 `## 生命周期定位`，门禁证据见 `## 门禁与证据`。

## 适用范围与优先级

效力依下列层级判断：高层覆盖低层，低层仅在高层未规定时补充。

1. 强制性的平台、语言、宿主与全局用户约束。Go 导出标识符、C# 的 `I` 接口与 PEP 8 均非可选事项。
2. 本 skill 的规则与默认值。
3. 既有项目约定与事实。现有代码、命名表、lint 配置与语言版本是输入，按本 skill 的规则处理；项目约定仅在
   本 skill 未规定时补充，不得覆盖本 skill。
4. 个人偏好，不得覆盖上述三层。

管辖与边界：

- 本 skill 裁定名称本身：术语、大小写、语法形式、被禁用的同义词、文件名、目录名、锚点、ADR 编号、命名表，
  以及提交消息、分支、发布标签与议题标签的名称。
- 生成代码、第三方引入代码、外部协议字段与第三方 schema 保留原名，在边界处隔离并把映射记入命名表。
- 提交流程、分支模型、合并与审查策略归 vcs-collaboration-conventions；API 版本化、分页、CRUD 语义、错误模型
  与 schema 迁移归 api-and-data-conventions；格式化工具、行宽与 linter 配置归 code-style-conventions。
- 测试策略、门禁与豁免归 testing-and-quality-conventions；遥测、开关生命周期、CI/CD 与弃用时机归
  release-operations-conventions；权限策略与机密归 security-compliance-conventions；包元数据与分发归
  repository-governance-conventions；文档正文、变更记录、发布说明与术语定义归 documentation-conventions，
  本 skill 只维护名称与命名约束。
- 强制规则冲突时报告用户裁决，不得自行选定；非强制约定冲突时说明冲突与所选约定并记录。
- 重命名属于一次变更，不属于清理：先读全部引用，在授权范围内更新测试、文档与 fixture，公开名称视为 API。

## 生命周期定位

上游输入来自 S2 的接口契约、数据模型、目录与包边界、发布与分支方案，它们决定需要哪些名称与跨层映射；
下游交接给 S3 的实现与审查、S4 的 lint 与一致性验证、S5 的标签与发布说明。

- 升级与停止：公开名称重命名、跨仓库共享标识符、需要版本化或弃用的名称变更，退回 G2 重新确认并取得授权；
  命名表与既有契约冲突且无法在授权范围内裁决时，停止改动并报告冲突双方。

| 阶段 | 本 skill 的职责 | 产出 / 证据 |
|---|---|---|
| S2 计划 | 把接口、数据、配置、目录与发布产物名称纳入设计，确定禁用同义词与命名 lint 规则 | 命名表、跨层名称清单、lint 规则 |
| S3 构建 | 按矩阵与维度规则命名新增标识符；重命名按证据、引用清单与回滚点执行 | diff 中的名称、命名表更新、引用清单 |
| S4 验证 | 核对跨层一致性与命名 lint 结果，检查公开名称的兼容路径 | lint 输出、跨层映射、别名或弃用证据 |
| S5 发布 | 核对发布标签、发布说明与变更记录中的名称 | 标签与说明的一致性检查 |

## 门禁与证据

| 门禁 | 必须提供的证据 | 不满足时 |
|---|---|---|
| G2 计划 | 命名表、跨层名称清单、命名 lint 规则、重命名影响与回滚说明 | 缺命名表或公开名称未定时 Hold，退回 S1/S2 |
| G3 构建 | 命名 lint 输出、diff 与大小写矩阵一致、重命名引用清单 | Recycle 到 S3；公开名称无别名或弃用路径时按 No-Go 阻断合并 |
| G4 验证 | 跨层一致性核对、lint 通过记录、弃用与别名证据 | 修复后重验；不可兼容的公开改名按 No-Go 处理 |
| G5 发布 | 标签、发布说明与命名表一致 | Hold 发布，修正名称后再过门 |

证据必须可复核：lint 命令与输出、diff 行号、命名表条目；计划与口头承诺不构成证据。

## 工作流

1. 分类产物：文件、目录、包、类型、函数、变量、常量、API 字段、数据库对象、配置键、测试、提交、分支、标签或资产。
2. 以项目领域语言命名概念，先查命名表与术语表；未收录的新术语在第二处使用前登记。
3. 从语法形式表选择形式，再为产物与语言选择大小写；覆盖规则见 `references/languages.md`。
4. 检查冲突、对称性、长度、可读性（能否读出声）、可搜索性，以及有误导性的编码。
5. 需要重命名时，陈述证据、列出引用、选择别名或弃用路径与回滚点，核对 diff，更新测试与文档并运行 lint。

## 核心规则

- **一个概念，一个名称，并使用领域语言。** 同一事物有多种叫法属于缺陷，同一名称指两件事属于冲突；优先采用
  用户与产品使用的词，记录被禁用的同义词。
- **命名意图，而不是实现。** `activeUsers` 优于 `filteredList2`；`retryCount` 优于 `loopCounter`。
- **遵循语言。** 不得从其他语言引入大小写或前缀；Python 中的 `IUserStore` 与 Go 中的 `user_repository` 均属错误。
- **可搜索、可读出声。** 除循环索引外，避免单字母与双字母名称、省略元音的写法以及辅音连缀。
- **不得编码类型。** 不得采用匈牙利命名法，不得添加 `obj`、`str`、`arr`、`list` 后缀；仅当类型无法表达时，
  方得编码单位、范围或含义（`timeout_ms`、`amount_cents`）。
- **优先肯定式。** `isEnabled` 优于 `isNotDisabled`；不得构造双重否定。
- **集合用复数。** `users` 包含多个用户；映射写作 `usersById`，不得写作 `userMap`。
- **按作用域控制长度。** 局部变量一到两个词，公开 API 两到四个词；长名称胜于含糊名称，前提是每个词都承载含义。
- **不得在请求之外重命名。** 一致性具有价值，但批量重命名属于另一次需要审查的变更。
- **GitHub 命名产物使用受控词表。** 标签取小写受控集合，多词标签选定连字符或空格一种写法（GitHub 默认标签如
  `good first issue` 保留原写法）；仓库名小写 kebab；工作流、job 与复用 action 使用稳定标识，发布标题等于发布
  标签名；词表与维护人置于仓库中，新增条目先检查同义词。

## 项目命名表

项目启动时创建此表，保存于仓库中，并在术语扩散前先行增加一行；术语解释归项目术语表，本表只维护名称与命名约束。

| 术语 | 规范名称 | 避免 | 大小写 | 命名表维护人 |
|---|---|---|---|---|
| invoice | `Invoice` | bill、statement | PascalCase | billing |
| customer | `Customer` | client、buyer、account | PascalCase | CRM |
| amount | `amount_cents` | amount、total | snake_case | billing |

## 大小写矩阵

下列默认值与语言无关。`references/languages.md` 按语言与框架覆盖这些默认值。

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
| 发布标签 | 带 `v` 前缀的 SemVer | `v1.4.0` |

## 语法形式

| 概念 | 形式 | 示例 |
|---|---|---|
| 动作 | 动词短语 | `sendInvoice`, `parseConfig` |
| 谓词 | 布尔形容词 | `isExpired`, `hasAccess` |
| 资源或实体 | 单数名词 | `Invoice`, `Customer` |
| 集合 | 复数名词 | `invoices`, `activeUsers` |
| 映射 | 名词加 `by` 键 | `invoicesById`, `priceBySku` |
| 工厂、构建器与仓库 | `XFactory` 或 `createX`、`XBuilder`、`XRepository` | `InvoiceFactory`, `InvoiceBuilder`, `InvoiceRepository` |
| 服务、适配器与网关 | 仅真正的领域服务用 `XService`；外部集成用 `XAdapter`、`XGateway` | `BillingService`, `StripeAdapter`, `PaymentGateway` |
| DTO 或线上模型 | `XDto`、`XRequest`、`XResponse` | `InvoiceDto`, `CreateOrderRequest` |
| 错误 | `XError` 或 `XException` | `InvoiceNotFoundError` |
| 选项、配置与结果 | `XOptions`、`XConfig`、`XResult`、`XOutcome` | `RetryOptions`, `PaymentResult` |
| 标识符 | 代码 `<Entity>Id`；存储与 HTTP JSON 资源标识 `<entity>_id` | `CustomerId`, `customer_id` |
| 时间戳 | `<event>_at` | `created_at`, `paid_at` |
| 时长与计数 | `<quantity>_ms`、`_s`；`<thing>_count` | `timeout_ms`, `retry_count` |
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

| 阶段 | 反模式 | 为什么失败 | 修复 |
|---|---|---|---|
| S2 | `data`、`info`、`item`、`obj`、`temp`、`foo`、`bar` | 未表达任何信息，迫使读者阅读函数体。 | 命名概念本身：`invoice`、`parseResult`、`pendingJobs`。 |
| S2 | `Manager`、`Helper`、`Util`、`Common`、`Base` | 掩盖职责，并吸引不相关的代码。 | 命名角色：`BillingService`、`RetryPolicy`、`PathFormatter`。 |
| S2 | 同一概念使用 `client` / `customer` / `buyer` | 读者无法判断三者是否存在区别。 | 选定一个领域术语，禁用其余说法。 |
| S3 | `userObj`、`strName`、`arrItems` | 编码了类型，重构后立即过时。 | `user`、`name`、`items`。 |
| S3 | `notReady`、`disableCache`、`isNotUnavailable` | 否定式名称迫使每个读取点反向理解。 | `isReady`、`cacheEnabled`、`isAvailable`。 |
| S3 | `usr`、`cfg`、`mgr`、`btn`、`msg` | 节省三个字符，增加一次查找。 | `user`、`config`、`manager`、`button`、`message`。 |
| S3 | `UserServiceImpl` | 泄露实现，并增加噪声。 | `SqlUserRepository`、`StripePaymentGateway`。 |
| S3 | 跨层或跨语言混用大小写与前缀（`userId` 与 `user_id`，Python 中的 `IUserStore`） | 破坏搜索与机械化重构，并把一种语言的约定带入另一种。 | 每层用一种大小写，边界处映射；`I` 前缀仅用于 C#。 |
| S3 | `user2`、`newUser`、`tempUser` | 带编号或时间性的名称立即过时。 | `importedUser`、`pendingUser`、`user`。 |
| S3 | 布尔值命名为 `flag`、`status`、`check` | 含义含糊，类型亦常常错误。 | `hasExported`、`isReady`、`isValid`。 |
| S3 | 仅使用 `do`、`handle`、`process`、`run` | 未说明处理何种对象或产出何种结果。 | `handlePaymentFailure`、`processRefund`、`runMigration`。 |
| S4 | 公开名称直接改名，无别名或弃用路径 | 调用方无从迁移，改名等同破坏契约。 | 提供别名并记录移除条件，按 G2 重新确认。 |

## 审查清单

计划与命名表（G2）：

- [ ] 术语与命名表或术语表一致，新术语已登记禁用同义词。
- [ ] 大小写与语法形式同语言及产物匹配，跨层映射只发生在边界。
- [ ] 重命名有证据、引用清单、别名或弃用路径与回滚顺序。

构建（G3）：

- [ ] 不存在同义词、冲突、容易混淆的近似名称或未加限定的泛化词。
- [ ] 名称可读出声且足够独特便于搜索；长度与作用域匹配，未编码类型或实现。
- [ ] 布尔值为肯定式且确为布尔类型；集合为复数，映射写明其键。
- [ ] 单位、时间、金额、比率与范围均显式；异步、错误、测试与 API 约定与所用技术栈匹配。
- [ ] 文件名与主要导出或职责匹配；数据库、API、配置与日志名称在各层之间一致。
- [ ] 缩写均在允许清单中；对称配对使用相同的词；未在授权范围之外重命名。

验证与发布（G4/G5）：

- [ ] 公开重命名具有弃用或别名路径，引用、测试、文档、fixture 与快照均已更新。
- [ ] 命名表与 GitHub 标签词表已更新且与新增标识符一致；命名 lint 通过；发布标签与发布说明名称一致。

## 示例

<example>
场景：跨层命名一个新的 HTTP 资源。
做法：数据库表为 `orders`，列为 `customer_id`，主键为 `id`，索引为 `idx_orders_customer_id`；API 路径为
`/v1/orders`，查询参数为 `created_after`；JSON 字段为 `created_at`、`is_paid`；TypeScript 类型为 `Order`，
函数为 `listOrders`，布尔值为 `isPaid`；测试为 `list_orders_test` 或 `listOrders.test.ts`。
</example>

<example>
场景：重命名一个布尔值或数量值。
做法：将 `notDisabled` 改为 `isEnabled`，将 `flag` 改为 `hasExported`；可空布尔值改为三态枚举
（`Visibility.PUBLIC`、`Visibility.PRIVATE`、`Visibility.UNLISTED`），不得保留 `isPublic: boolean | null`。
将 `timeout` 改为 `timeout_ms`，将 `amount` 改为 `amount_cents` 加 `currency`，并在命名表中记录 `discount_pct`
（0-100）或 `discount_ratio`（0-1）的范围。
</example>

## 参考资料

- [references/lifecycle.md](references/lifecycle.md)：进入 S2 命名设计、准备门禁记录或判断升级与裁剪时阅读。
- [references/dimensions-code.md](references/dimensions-code.md)、
  [references/dimensions-interface.md](references/dimensions-interface.md)、
  [references/dimensions-system.md](references/dimensions-system.md)：按维度编号查阅完整规则；命名新标识符或审查
  diff 中的名称时阅读对应维度。
- [references/languages.md](references/languages.md)：确认语言与框架的大小写、文件与测试约定时阅读；建立命名表
  之前应先读完维度文件。
