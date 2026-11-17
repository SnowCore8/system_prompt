# 命名维度：代码

配合 `SKILL.md` 使用本文件。每一节给出一种产物的模式、示例与边界情况。项目已有约定时，先读它并应用
优先级更高的规则；本文件提供默认值与理由。

## 1. 文件与目录

- 用小写；每种语言选定一种大小写：Python 与 Rust 模块用 `snake_case`，Web 模块、资产与文档用
  `kebab-case`，只有语言要求时才用 `PascalCase`（Java、C#、Kotlin、Swift 的类型）。
- 按主要导出或职责命名文件，而不是只按层次命名：`user_repository.py`，而不是 `db.py`；
  `billing/invoice_calculator.go`，而不是 `helpers.go`。
- 目录中，集合用复数名词（`users/`、`orders/`），单个功能用单数名词（`billing/`、`checkout/`）。
  除非项目记录了两者的边界，避免 `misc/`、`common/`、`utils/`。
- 不含空格，不含版本后缀（`v2` 用于 API 版本，不用于文件副本），不用 `final`、`new` 或 `old`。
- 测试文件与被测单元同名并使用语言后缀：`user_service_test.py`、`UserServiceTest.java`、
  `user-service.test.ts`、`user_service_test.go`。
- fixture 放在 `fixtures/` 或 `testdata/`；快照放在 `__snapshots__/` 或 `snapshots/`；基准文件放在
  `golden/`。
- 迁移文件带时间戳并有序：`20261114093000_add_order_status.sql`。
- 静态资产用 kebab-case，相关时带上倍率或尺寸，绝不编码营销活动或人名：
  `hero-image@2x.png`、`icon-close.svg`、`logo-dark.svg`。

| 好 | 差 | 原因 |
|---|---|---|
| `order_repository.py` | `repo2.py` | 说明概念与职责。 |
| `billing/invoice_calculator.go` | `helpers.go` | 大杂烩名称会吸引不相关的代码。 |
| `20261114093000_add_order_status.sql` | `migration.sql` | 顺序与意图可见。 |
| `user-service.test.ts` | `test1.ts` | 与被测单元和测试运行器的约定一致。 |

## 2. 包与命名空间

- Java 与 Kotlin：反向域名，全小写，不用下划线：`com.example.billing`。
- Python：简短、小写的包名，不用连字符：`billing`、`billing.invoices`。
- Go：简短、小写的包名，不用下划线或混合大小写：`billing`。
- npm：小写，公开时加 scope：`@example/billing`。
- Rust：模块与 crate 用 `snake_case`；避免同一路径中 crate 与模块同名。
- 按领域命名，而不是按层次：`billing.payments`，而不是 `services.managers`。
- 避免名称重复（stuttering）：`billing.Invoice`，而不是 `billing.BillingInvoice`，除非限定词能消除歧义。
- 把公开接口放在具名包中；内部实现放进 `internal/`、`_private` 或未导出的模块。

| 好 | 差 | 原因 |
|---|---|---|
| `com.example.billing` | `com.example.Billing_App` | Java 包小写、不用下划线。 |
| `billing.payments` | `services.managers` | 领域名能经受重构，层次名不能。 |
| `internal/parser` | `misc/parser` | `internal` 说明了可见性契约。 |

## 3. 模块与导入

- 模块名对能力用名词（`billing`、`auth`、`search`），只有命令模块才用动词（`bootstrap`、`migrate`）。
- 语言允许时，每个文件一个主要导出；有意再导出，并记录公开接口。
- 导入别名简短且无歧义：`import numpy as np` 是惯用写法；`import user as u` 不是。
- 避免循环名称：`serialization.json` 优于 `json.json`；`billing.invoices` 优于 `invoices.invoices`。
- 内部模块使用语言支持的标记：`_internal`、`internal`、`private`，或不导出。

## 4. 类型与接口

- 类、结构体、record 与类型别名用单数名词短语：`Invoice`、`OrderItem`、`UserId`。
- 接口命名能力或角色：`Readable`、`UserStore`、`PaymentGateway`。只在 C# 及其约定要求的语言中使用
  `I` 前缀；不要把它带进 Python、Go 或 Rust。
- 抽象基类使用有意义的角色，而不是默认的 `Base`：`Repository` 或 `Storage`，除非项目已在使用该模式，
  否则不要用 `BaseRepository`。
- DTO 是边界类型：`InvoiceDto`、`CreateOrderRequest`、`OrderResponse`。不要给领域类型加 `Dto` 后缀。
- 泛型参数简短且符合惯例：`T`、`TKey`、`TValue`、`TResult`；角色不明显时用描述性名称（`TResponse`）。
- 类型别名说明领域含义：`type UserId = string`（尽可能使用品牌类型）、`type Cents = number`。
- 避免 `Impl`：改用技术或角色（`SqlUserRepository`、`InMemoryUserRepository`）。
- 不要在类型名中编码可空性或可选性；由类型系统表达（`User | null`）。

| 好 | 差 | 原因 |
|---|---|---|
| `UserStore` | Python 里的 `IUserStore` | Python 没有 `I` 约定。 |
| `SqlUserRepository` | `UserRepositoryImpl` | 命名机制，而不是无意义的后缀。 |
| `CreateOrderRequest` | `OrderData` | 说明边界与操作。 |

## 5. 枚举与联合类型

- 枚举类型用单数：`OrderStatus`、`PaymentMethod`，而不是 `OrderStatuses`。
- 成员稳定且描述性强：按语言使用 `PENDING`、`PAID`、`REFUNDED` 或 `Pending`、`Paid`、`Refunded`；
  绝不用 `STATUS_1`、`TYPE_A` 或数字字面量。
- 两态枚举通常就是布尔值；第三种状态可能出现，或取值本身就是领域术语时，才用枚举。
- 联合类型与可辨识联合使用 `kind` 或 `type` 判别字段，取值稳定且小写：
  `{ kind: "card" | "bank_transfer" }`。
- 不要用枚举成员充当显示标签；在表现层边界把它映射为本地化文本。

## 6. 函数与方法

- 使用说明效果的动词短语：`sendInvoice`、`parseConfig`、`listActiveUsers`、`calculateTotal`。
- 纯读取按语言用名词或 `get` 访问器：`user` / `getUser`；I/O 读取用 `fetchUser`、`loadUser` 或
  `findUser`；写入用 `saveUser`、`updateUser`、`deleteUser`。
- 谓词以 `is`、`has`、`can`、`should` 或 `needs` 开头并返回布尔值；`validate` 返回结果或抛出异常，
  `assert` 在失败时抛出异常。
- 工厂为 `createX` 或 `XFactory`；构建器为 `XBuilder`；转换器为 `toX` 与 `fromX`；解析器为 `parseX`；
  格式化器为 `formatX`。
- 异步命名遵循语言：C# 用 `Async` 后缀，JavaScript 不用，Python 依靠 `async def`。
- 一个函数，一个动作。名称里需要 `and` 时，拆分函数。
- 避免没有宾语的 `do`、`handle`、`process`、`run`、`manage` 与 `execute`：用 `handlePaymentFailure`，
  而不是 `handle`。

| 好 | 差 | 原因 |
|---|---|---|
| `listActiveUsers` | `getUsers2` | 说明过滤条件与动作。 |
| `fetchInvoice` | 对 HTTP 调用使用 `getInvoice` | 在许多代码库中 `fetch` 表示 I/O。 |
| `parseDuration` | `duration` | 动词区分解析与格式化。 |

## 7. 变量、参数与字段

- 使用名词；变量说明值本身，而不是类型：`invoice`、`pendingJobs`、`parsedConfig`。
- 长度随作用域：循环索引用 `i` 没问题；模块级的 `i` 不行。公开字段与参数需要完整单词。
- 参数使用领域术语，而不是 `data`、`value`、`item` 或 `input`：`invoice`、`customer`、`timeoutMs`。
- 避免时间性名称（`temp`、`tmp`、`newUser`、`oldUser`）与编号名称（`user2`）；用说明差异的限定词
  （`importedUser`、`cachedUser`）。
- 私有字段遵循语言：Python `_name`、C# `_camelCase`、Java `camelCase`；不要混用。
- 可选与可空值由类型表达，而不是名称；写 `middleName`，不写 `optionalMiddleName`。
- 保存布尔值的字段遵循下面的布尔规则；保存集合的字段用复数。

## 8. 常量

- 常量用 UPPER_SNAKE_CASE：`MAX_RETRY_COUNT`、`DEFAULT_TIMEOUT_MS`、`HTTP_PORT`。
- 值带单位时在名称中包含单位：`DEFAULT_TIMEOUT_MS`，而不是 `DEFAULT_TIMEOUT`。
- 命名策略，而不是字面量：用 `MAX_RETRY_COUNT` 而不是 `THREE`；别让魔法数字进入逻辑。
- 按领域分组常量（`billing/constants.py`），而不是一个全局的 `constants` 模块。
- 随环境变化的值是配置，不是常量；按配置键为它命名。
- 枚举成员不是常量；封闭集合使用枚举类型。

## 9. 布尔值与谓词

- 使用肯定的前缀：`isEnabled`、`hasChildren`、`canRetry`、`shouldNotify`、`needsReview`。
- 除非否定词本身就是领域术语，绝不用 `not`、`no` 或否定动词：`isVisible` 胜于 `isNotHidden`。
- 不要把 `flag`、`status`、`check` 或 `state` 用作布尔值；它们掩盖了正在回答的问题。
- 名为 `isX` 的函数必须返回布尔值，而不是计数、字符串或可空值。三种状态时，用枚举。
- 命名问题，而不是实现：`hasAccess(user, resource)`，而不是 `checkAccessFlag(user, resource)`。
- 条件中避免双重否定；必须使用否定时，给肯定式命名，并在使用处取反。

| 好 | 差 | 原因 |
|---|---|---|
| `isPaid` | `notUnpaid` | 一次肯定式阅读。 |
| `hasExported` | `exportFlag` | 说明条件本身。 |
| `canRetry` | `retryStatus` | 是布尔谓词，不是状态袋。 |

## 10. 集合、映射、Set 与元组

- 集合用复数名词：`users`、`orderItems`、`pendingJobs`；单数形式表示一个元素。
- 映射同时命名键与值：`usersById`、`priceBySku`、`ordersByCustomerId`；避免 `userMap`。
- Set 按其内容命名：`activeUserIds`、`blockedDomains`；只有与列表的区别重要且类型本身看不出来时，
  才加 `Set`。
- 元组与配对命名两端：`(key, value)`、`(min, max)`、`(start, end)`；单行 lambda 之外避免 `(a, b)`。
- 循环索引为 `i`、`j`、`k`；函数体较长或嵌套时，具名索引（`userIndex`）更好。
- 空与缺失不同：`users` 可以为空；`user` 可以不存在。不要在名称中编码这一区别。
- 不要编码实现（`userLinkedList`、`itemArray`）；类型已经说明。

## 11. 数量、单位、时间、金额、比率与范围

- 类型无法表达时，每个数量都带上单位：`timeout_ms`、`size_bytes`、`weight_kg`、`distance_m`、
  `temperature_c`。
- 时刻用 UTC 下的 `<event>_at`（`created_at`、`paid_at`）；日期用 `_date`；时长用 `_ms` 或 `_s`。
  不要使用没有单位或时区规则的 `timestamp`。
- 金额使用整数最小单位加 ISO 4217 货币：`amount_cents` 与 `currency`；绝不用浮点数。
- 比率是 0-1（`success_ratio`）；百分比是 0-100（`discount_pct`）；在命名表中说明范围。
- 范围同时命名两端与包含规则：`min_`/`max_`、`start_`/`end_`、`from_`/`to_`；记录末端是否包含。
- 计数用 `_count`；合计用 `_total`；上限用 `_limit`；避免 `num`、`qty`、`amt`。
- 把数量与单位合并在一个字符串里的值是展示值，不是领域值；命名为 `formatted_duration`，并把数值
  单独保留。

| 好 | 差 | 原因 |
|---|---|---|
| `timeout_ms` | `timeout` | 单位是契约的一部分。 |
| `amount_cents` + `currency` | `amount` | 没有单位或货币的金额含义不明。 |
| `discount_ratio` | `discount` | 说明了范围约定。 |

## 14. 测试与测试替身

- 测试名称说明行为与条件：`test_list_orders_returns_empty_for_new_user`、
  `should_reject_expired_card`；使用项目的测试运行器约定。
- 测试文件按被测单元名加语言测试标记命名：`user_service_test.py`、`UserServiceTest.java`、`user-service.test.ts`。
- fixture 与工厂要显式：`user_fixture`、`make_user`、`UserFactory`；避免 `data1`、`sample2`。
- 测试替身有精确含义：`Fake` 是可用的轻量实现，`Stub` 返回预设值，`Mock` 记录或验证交互，
  `Spy` 包装真实对象。不要把 stub 叫作 `Mock`。
- 基准测试用 `bench_` 或语言约定；属性测试遵循框架的发现约定（pytest 与 Hypothesis 使用
  `test_*`）；快照文件以 `.snap` 结尾。
- 测试名称不得只用一个工单号作为描述；把工单号放在函数体或元数据中。

## 24. 缩写、首字母缩略词与复数

- 每个项目维护一份简短的允许清单：`id`、`url`、`http`、`api`、`cpu`、`db`、`ui`、`cli`、`json`、
  `xml`、`sql`、`html`、`css`；其余一律展开（`usr` 展开为 `user`，`cfg` 展开为 `config`，`mgr`
  展开为 `manager`）。
- 首字母缩略词按单词处理：`userId`、`httpClient`、`parseUrl`；Go 使用首字母大写缩写
  （`UserID`、`HTTPServer`），C# 保留 `Id`（`UserId`）。
- 使用规则复数；不可数名词（`data`、`info`、`metadata`）表示集合时加限定词（`dataSet`、
  `infoList`）；绝不用 `datas` 或 `informations`。
- 标识符中避免撇号与所有格；用 `userIds`，不写 `user'sIds`。
- 标识符使用 ASCII；避免同形字符与非 ASCII 形近字符；非英语领域术语要音译，或记录到命名表中。

## 25. 对称与配对

在整个代码库中一致地使用同一组配对；同一操作混用 `remove` 与 `delete` 是缺陷。

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

- 局部变量用一到两个词，私有成员用两到三个词，公开 API 用两到四个词；每个词都承载含义时，常量可以
  更长。
- 单字母名称仅限：索引用 `i`、`j`、`k`，坐标用 `x`、`y`，捕获的错误用 `e`，未使用的值用 `_`。
- 名称必须足够独特，便于搜索：`userId` 可搜索；模块作用域的 `id` 不行。
- 名称必须能在审查中读出声；避免 `usrRprt` 与辅音连缀。
- 不用数字后缀（`user2`、`handler3`）；用说明差异的限定词。
- 更长并不更好：删掉重复类型或上下文的词（`UserUserRepository`、`IUserInterface`）。
