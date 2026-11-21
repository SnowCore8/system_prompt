# 命名维度：代码

本文件与 `SKILL.md` 配合使用。每一节规定一种命名产物的模式、示例与边界情况。项目约定与事实属于输入；本
skill 的规则优先，项目约定仅在本 skill 未规定时补充。本文件提供默认值与理由。

## 1. 文件与目录

- 名称使用小写；每种语言选定一种大小写：Python 与 Rust 模块用 `snake_case`，Web 模块、资产与文档用
  `kebab-case`，仅当语言要求时使用 `PascalCase`（Java、C#、Kotlin、Swift 的类型）。
- 按主要导出或职责命名文件，不得仅按层次命名：使用 `user_repository.py`，不得使用 `db.py`；使用
  `billing/invoice_calculator.go`，不得使用 `helpers.go`。
- 目录中，集合用复数名词（`users/`、`orders/`），单个功能用单数名词（`billing/`、`checkout/`）。除项目
  已记录两者的边界外，应当避免使用 `misc/`、`common/`、`utils/`。
- 名称不得含空格，不得含版本后缀（`v2` 用于 API 版本，不用于文件副本），不得使用 `final`、`new` 或
  `old`。
- 测试文件与被测单元同名，并使用语言后缀：`user_service_test.py`、`UserServiceTest.java`、
  `user-service.test.ts`、`user_service_test.go`。
- fixture 置于 `fixtures/` 或 `testdata/`；快照置于 `__snapshots__/` 或 `snapshots/`；基准文件置于
  `golden/`。
- 迁移文件带时间戳并保持有序：`20261114093000_add_order_status.sql`。
- 静态资产使用 kebab-case；相关时带上倍率或尺寸；不得编码营销活动或人名：`hero-image@2x.png`、
  `icon-close.svg`、`logo-dark.svg`。

| 好 | 差 | 原因 |
|---|---|---|
| `order_repository.py` | `repo2.py` | 说明概念与职责。 |
| `billing/invoice_calculator.go` | `helpers.go` | 笼统名称会吸引不相关的代码。 |
| `20261114093000_add_order_status.sql` | `migration.sql` | 顺序与意图可见。 |
| `user-service.test.ts` | `test1.ts` | 与被测单元和测试运行器的约定一致。 |

## 2. 包与命名空间

- Java 与 Kotlin：使用反向域名，全小写，不使用下划线：`com.example.billing`。
- Python：包名简短、小写，不使用连字符：`billing`、`billing.invoices`。
- Go：包名简短、小写，不使用下划线或混合大小写：`billing`。
- npm：小写；公开时加 scope：`@example/billing`。
- Rust：模块与 crate 使用 `snake_case`；同一路径中应当避免 crate 与模块同名。
- 按领域命名，不得按层次命名：`billing.payments`，不得使用 `services.managers`。
- 避免名称重复（stuttering）：使用 `billing.Invoice`，不应当使用 `billing.BillingInvoice`，但限定词能够消
  除歧义的除外。
- 公开接口置于具名包中；内部实现置于 `internal/`、`_private` 或未导出的模块中。

| 好 | 差 | 原因 |
|---|---|---|
| `com.example.billing` | `com.example.Billing_App` | Java 包小写、不用下划线。 |
| `billing.payments` | `services.managers` | 领域名能够经受重构，层次名则否。 |
| `internal/parser` | `misc/parser` | `internal` 说明了可见性契约。 |

## 3. 模块与导入

- 模块名对能力使用名词（`billing`、`auth`、`search`）；仅命令模块使用动词（`bootstrap`、`migrate`）。
- 语言允许的，每个文件一个主要导出；再导出应当出于有意，并记录公开接口。
- 导入别名应当简短且无歧义：`import numpy as np` 属于惯用写法；`import user as u` 不属于。
- 避免循环名称：`serialization.json` 优于 `json.json`；`billing.invoices` 优于 `invoices.invoices`。
- 内部模块使用语言支持的标记：`_internal`、`internal`、`private`，或不导出。

## 4. 类型与接口

- 类、结构体、record 与类型别名使用单数名词短语：`Invoice`、`OrderItem`、`UserId`。
- 接口命名能力或角色：`Readable`、`UserStore`、`PaymentGateway`。仅在 C# 及其约定要求的语言中使用 `I`
  前缀；不得将其带入 Python、Go 或 Rust。
- 抽象基类使用有意义的角色，不得使用默认的 `Base`：使用 `Repository` 或 `Storage`；项目已在使用该模式的
  除外，不得使用 `BaseRepository`。
- DTO 属于边界类型：`InvoiceDto`、`CreateOrderRequest`、`OrderResponse`。不得给领域类型添加 `Dto` 后缀。
- 泛型参数应当简短且符合惯例：`T`、`TKey`、`TValue`、`TResult`；角色不明显的，使用描述性名称
  （`TResponse`）。
- 类型别名说明领域含义：`type UserId = string`（尽可能使用品牌类型）、`type Cents = number`。
- 避免 `Impl`：改用技术或角色（`SqlUserRepository`、`InMemoryUserRepository`）。
- 不得在类型名中编码可空性或可选性；由类型系统表达（`User | null`）。

| 好 | 差 | 原因 |
|---|---|---|
| `UserStore` | Python 中的 `IUserStore` | Python 没有 `I` 约定。 |
| `SqlUserRepository` | `UserRepositoryImpl` | 命名机制，而不是无意义的后缀。 |
| `CreateOrderRequest` | `OrderData` | 说明边界与操作。 |

## 5. 枚举与联合类型

- 枚举类型使用单数：`OrderStatus`、`PaymentMethod`，不得使用 `OrderStatuses`。
- 成员保持稳定且描述性强：按语言使用 `PENDING`、`PAID`、`REFUNDED` 或 `Pending`、`Paid`、`Refunded`；
  不得使用 `STATUS_1`、`TYPE_A` 或数字字面量。
- 两态枚举通常即布尔值；仅当第三种状态可能出现，或取值本身属于领域术语时，使用枚举。
- 联合类型与可辨识联合使用 `kind` 或 `type` 判别字段，取值稳定且小写：
  `{ kind: "card" | "bank_transfer" }`。
- 不得以枚举成员充当显示标签；应当在表现层边界将其映射为本地化文本。

## 6. 函数与方法

- 使用说明效果的动词短语：`sendInvoice`、`parseConfig`、`listActiveUsers`、`calculateTotal`。
- 纯读取按语言使用名词或 `get` 访问器：`user` / `getUser`；I/O 读取使用 `fetchUser`、`loadUser` 或
  `findUser`；写入使用 `saveUser`、`updateUser`、`deleteUser`。
- 谓词以 `is`、`has`、`can`、`should` 或 `needs` 开头，并返回布尔值；`validate` 返回结果或抛出异常，
  `assert` 在失败时抛出异常。
- 工厂为 `createX` 或 `XFactory`；构建器为 `XBuilder`；转换器为 `toX` 与 `fromX`；解析器为 `parseX`；
  格式化器为 `formatX`。
- 异步命名遵循语言：C# 使用 `Async` 后缀，JavaScript 不使用，Python 依靠 `async def`。
- 一个函数对应一个动作。名称中需要 `and` 的，应当拆分函数。
- 避免没有宾语的 `do`、`handle`、`process`、`run`、`manage` 与 `execute`：使用
  `handlePaymentFailure`，不得使用 `handle`。

| 好 | 差 | 原因 |
|---|---|---|
| `listActiveUsers` | `getUsers2` | 说明过滤条件与动作。 |
| `fetchInvoice` | 对 HTTP 调用使用 `getInvoice` | 在许多代码库中 `fetch` 表示 I/O。 |
| `parseDuration` | `duration` | 动词区分解析与格式化。 |

## 7. 变量、参数与字段

- 使用名词；变量说明值本身，不说明类型：`invoice`、`pendingJobs`、`parsedConfig`。
- 长度随作用域变化：循环索引使用 `i` 即可；模块级不得使用 `i`。公开字段与参数需要完整单词。
- 参数使用领域术语，不得使用 `data`、`value`、`item` 或 `input`：`invoice`、`customer`、`timeoutMs`。
- 避免时间性名称（`temp`、`tmp`、`newUser`、`oldUser`）与编号名称（`user2`）；使用说明差异的限定词
  （`importedUser`、`cachedUser`）。
- 私有字段遵循语言：Python `_name`、C# `_camelCase`、Java `camelCase`；不得混用。
- 可选与可空值由类型表达，不由名称表达；写作 `middleName`，不得写作 `optionalMiddleName`。
- 保存布尔值的字段遵循下述布尔规则；保存集合的字段使用复数。

## 8. 常量

- 常量使用 UPPER_SNAKE_CASE：`MAX_RETRY_COUNT`、`DEFAULT_TIMEOUT_MS`、`HTTP_PORT`。
- 值带单位的，名称中包含单位：使用 `DEFAULT_TIMEOUT_MS`，不得使用 `DEFAULT_TIMEOUT`。
- 命名策略，不命名字面量：使用 `MAX_RETRY_COUNT`，不得使用 `THREE`；不得使魔法数字进入逻辑。
- 按领域分组常量（`billing/constants.py`），不得集中于一个全局的 `constants` 模块。
- 随环境变化的值属于配置，不属于常量；按配置键为其命名。
- 枚举成员不属于常量；封闭集合使用枚举类型。

## 9. 布尔值与谓词

- 使用肯定的前缀：`isEnabled`、`hasChildren`、`canRetry`、`shouldNotify`、`needsReview`。
- 否定词本身属于领域术语的除外，不得使用 `not`、`no` 或否定动词：`isVisible` 优于 `isNotHidden`。
- 不得将 `flag`、`status`、`check` 或 `state` 用作布尔值；上述名称掩盖正在回答的问题。
- 名为 `isX` 的函数必须返回布尔值，不得返回计数、字符串或可空值。存在三种状态的，使用枚举。
- 命名问题，不命名实现：使用 `hasAccess(user, resource)`，不得使用 `checkAccessFlag(user, resource)`。
- 条件中避免双重否定；必须使用否定的，给肯定式命名，并在使用处取反。

| 好 | 差 | 原因 |
|---|---|---|
| `isPaid` | `notUnpaid` | 一次肯定式阅读。 |
| `hasExported` | `exportFlag` | 说明条件本身。 |
| `canRetry` | `retryStatus` | 是布尔谓词，不是状态袋。 |

## 10. 集合、映射、Set 与元组

- 集合使用复数名词：`users`、`orderItems`、`pendingJobs`；单数形式表示一个元素。
- 映射同时命名键与值：`usersById`、`priceBySku`、`ordersByCustomerId`；避免 `userMap`。
- Set 按其内容命名：`activeUserIds`、`blockedDomains`；仅当与列表的区别重要且类型本身无法体现时，添加
  `Set`。
- 元组与配对命名两端：`(key, value)`、`(min, max)`、`(start, end)`；单行 lambda 之外避免
  `(a, b)`。
- 循环索引为 `i`、`j`、`k`；函数体较长或嵌套时，具名索引（`userIndex`）更好。
- 空与缺失不同：`users` 可以为空；`user` 可以不存在。不得在名称中编码这一区别。
- 不得编码实现（`userLinkedList`、`itemArray`）；类型已经说明实现。

## 11. 数量、单位、时间、金额、比率与范围

- 类型无法表达的，每个数量均带单位：`timeout_ms`、`size_bytes`、`weight_kg`、`distance_m`、
  `temperature_c`。
- 时刻使用 UTC 下的 `<event>_at`（`created_at`、`paid_at`）；日期使用 `_date`；时长使用 `_ms` 或
  `_s`。不得使用没有单位或时区规则的 `timestamp`。
- 金额使用整数最小单位加 ISO 4217 货币：`amount_cents` 与 `currency`；不得使用浮点数。
- 比率为 0-1（`success_ratio`）；百分比为 0-100（`discount_pct`）；应当在命名表中说明范围。
- 范围同时命名两端与包含规则：`min_`/`max_`、`start_`/`end_`、`from_`/`to_`；记录末端是否包含。
- 计数使用 `_count`；合计使用 `_total`；上限使用 `_limit`；避免 `num`、`qty`、`amt`。
- 将数量与单位合并在一个字符串中的值属于展示值，不属于领域值；应当命名为 `formatted_duration`，并单独
  保留数值。

| 好 | 差 | 原因 |
|---|---|---|
| `timeout_ms` | `timeout` | 单位是契约的一部分。 |
| `amount_cents` + `currency` | `amount` | 没有单位或货币的金额含义不明。 |
| `discount_ratio` | `discount` | 说明了范围约定。 |

## 14. 测试与测试替身

- 测试名称说明行为与条件：`test_list_orders_returns_empty_for_new_user`、`should_reject_expired_card`；
  使用项目的测试运行器约定。
- 测试文件按被测单元名加语言测试标记命名：`user_service_test.py`、`UserServiceTest.java`、
  `user-service.test.ts`。
- fixture 与工厂应当显式：`user_fixture`、`make_user`、`UserFactory`；避免 `data1`、`sample2`。
- 测试替身具有精确含义：`Fake` 是可用的轻量实现，`Stub` 返回预设值，`Mock` 记录或验证交互，`Spy` 包装
  真实对象。不得将 stub 称为 `Mock`。
- 基准测试使用 `bench_` 或语言约定；属性测试遵循框架的发现约定（pytest 与 Hypothesis 使用 `test_*`）；
  快照文件以 `.snap` 结尾。
- 测试名称不得仅以一个工单号作为描述；工单号应当置于函数体或元数据中。

## 24. 缩写、首字母缩略词与复数

- 每个项目维护一份简短的允许清单：`id`、`url`、`http`、`api`、`cpu`、`db`、`ui`、`cli`、`json`、
  `xml`、`sql`、`html`、`css`；其余一律展开（`usr` 展开为 `user`，`cfg` 展开为 `config`，`mgr` 展开
  为 `manager`）。
- 首字母缩略词按单词处理：`userId`、`httpClient`、`parseUrl`；Go 使用首字母大写缩写（`UserID`、
  `HTTPServer`），C# 保留 `Id`（`UserId`）。
- 使用规则复数；不可数名词（`data`、`info`、`metadata`）表示集合时加限定词（`dataSet`、`infoList`）；
  不得使用 `datas` 或 `informations`。
- 标识符中避免撇号与所有格；使用 `userIds`，不得写作 `user'sIds`。
- 标识符使用 ASCII；避免同形字符与非 ASCII 形近字符；非英语领域术语应当音译，或记录于命名表。

## 25. 对称与配对

在整个代码库中一致使用同一组配对；同一操作混用 `remove` 与 `delete` 属于缺陷。

| 配对 | 配对 | 配对 |
|---|---|---|
| `open` / `close` | `add` / `remove` | `create` / `delete` |
| `start` / `stop` | `begin` / `end` | `lock` / `unlock` |
| `push` / `pop` | `encode` / `decode` | `serialize` / `deserialize` |
| `import` / `export` | `upgrade` / `downgrade` | `min` / `max` |
| `source` / `target` | `from` / `to` | `key` / `value` |
| `request` / `response` | `input` / `output` | `read` / `write` |
| `enable` / `disable` | `subscribe` / `unsubscribe` | `connect` / `disconnect` |
| `mount` / `unmount` | `allocate` / `free` | `acquire` / `release` |
| `increment` / `decrement` | `before` / `after` | `parent` / `child` |

## 26. 长度、作用域与可搜索性

- 局部变量使用一到两个词，私有成员使用两到三个词，公开 API 使用两到四个词；每个词均承载含义的，常量
  可以更长。
- 单字母名称仅限于：索引用 `i`、`j`、`k`，坐标用 `x`、`y`，捕获的错误用 `e`，未使用的值用 `_`。
- 名称必须足够独特，便于搜索：`userId` 可搜索；模块作用域的 `id` 不可搜索。
- 名称必须能够在审查中读出声；避免 `usrRprt` 与辅音连缀。
- 不得使用数字后缀（`user2`、`handler3`）；使用说明差异的限定词。
- 更长并不更好：删除重复类型或上下文的词（`UserUserRepository`、`IUserInterface`）。
