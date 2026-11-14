# 命名维度

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

## 12. 异步、并发、流与回调

- 遵循语言：C# 用 `LoadAsync`，JavaScript 用 `load`（Promise 体现在类型上），Python 用
  `async def load`，Rust 用 `load` 并返回 future 类型。
- 回调为 `onX`（`onSave`、`onError`）；处理器为 `handleX`；监听器为 `onX` 或 `XListener`。
- 锁为 `lock` 或 `mutex`；守卫为 `guard`；锁对象不要用 `lockFlag` 与 `isLocked`。
- Worker 与池为 `worker`、`workerPool`、`queue`、`scheduler`；避免 `thread2` 与 `jobManager`。
- 流为 `stream`、`reader`、`writer`、`source`、`sink`；事件为 `onData`、`onEnd`、`onError`。
- 不要在名称中编码时机或实现（`delayedTask`、`asyncHelper`）；说明角色。
- future 或 Promise 的值在完成前叫 `pendingResult`；不要把未完成的值叫作 `result`。

## 13. 错误与结果

- 异常类要具体，并按语言以 `Error` 或 `Exception` 结尾：`InvoiceNotFoundError`、
  `PaymentDeclinedError`；避免用兜底的 `AppError` 表示所有失败。
- 错误码稳定且有结构：`ERR_BILLING_INVOICE_NOT_FOUND`；不要用一个错误码表示两种原因。
- 结果类型说明成功与失败：`Result<T, E>`、`Outcome<T>`、`PaymentResult`；字段为 `ok`、`value`、
  `error`。
- 局部错误变量为 `err` 或 `error`；短 catch 块里 `e` 可以接受；绝不用模块级的 `e`。
- 错误消息与标识符分开；消息中不要放机密、令牌或个人数据。
- 包装外部错误时带上上下文：带 `cause` 的 `InvoiceSyncError`，而不是裸抛出。

## 14. 测试与测试替身

- 测试名称说明行为与条件：`test_list_orders_returns_empty_for_new_user`、
  `should_reject_expired_card`；使用项目的测试运行器约定。
- 测试文件与被测单元同名：`user_service_test.py`、`UserServiceTest.java`、`user-service.test.ts`。
- fixture 与工厂要显式：`user_fixture`、`make_user`、`UserFactory`；避免 `data1`、`sample2`。
- 测试替身有精确含义：`Fake` 是可用的轻量实现，`Stub` 返回预设值，`Mock` 记录或验证交互，
  `Spy` 包装真实对象。不要把 stub 叫作 `Mock`。
- 基准测试用 `bench_` 或语言约定；属性测试遵循框架的发现约定（pytest 与 Hypothesis 使用
  `test_*`）；快照文件以 `.snap` 结尾。
- 测试名称不得只用一个工单号作为描述；把工单号放在函数体或元数据中。

## 15. HTTP、RPC 与 GraphQL

- HTTP 路径使用复数 kebab-case 资源：`/v1/order-items`；子资源嵌套其中：
  `/v1/orders/{orderId}/items`。
- 查询参数每个 API 使用一种大小写：`created_after`、`page_size`、`sort`、`order`；不要在一个 API
  中混用 `createdAfter` 与 `created_after`。
- JSON 字段遵循 schema 的大小写；布尔值 `is_`/`has_`，时间戳 `_at`，标识符 `<entity>_id`。
- RPC 方法为 `VerbNoun`：`GetOrder`、`ListOrders`、`CreateOrder`；请求与响应类型为
  `GetOrderRequest` 与 `GetOrderResponse`。
- GraphQL 类型用 PascalCase，字段用 camelCase，枚举用 UPPER_SNAKE；mutation 用动词短语
  （`createOrder`），input 以 `Input` 结尾。
- API 版本化、分页风格、CRUD 语义与错误 payload 字段属于 api-and-data-conventions 的策略；
  本节只定义命名语法。

## 16. JSON 与序列化

- 每个 schema 选定一种键大小写，并在生产者与消费者之间保持一致；只在边界处映射为语言的大小写。
- 键中不含空格；除非表达命名空间，避免点号；避免保留字与前导数字。
- 布尔值用 `is_`/`has_`；时间戳用 `_at` 并遵循 RFC 3339；ID 用 `<entity>_id`；枚举使用稳定取值。
- 数组用复数；用作映射的对象在字段名中写出键（`users_by_id`）。
- null 与缺失是不同状态；记录哪一种表示「缺失」，并且绝不使用字符串 `"null"`。
- 不要在键中编码类型（`str_name`、`int_count`）；除非协议要求，不要把一切包进 `data`。
- 判别字段为 `type` 或 `kind`，取值稳定且小写；不要把显示标签放进 payload。

## 17. 数据库与迁移

- 表用复数 snake_case：`orders`、`order_items`；列用单数：`created_at`、`customer_id`。
- 主键为 `id`，除非表使用自然键；外键为 `<referenced_table>_id`。
- 连接表按字母顺序写成 `<a>_<b>`：`order_product`，而不是 `product_order_link`。
- 索引为 `idx_<table>_<columns>`；唯一约束为 `uq_<table>_<columns>`；外键为
  `fk_<table>_<referenced_table>`；检查约束为 `ck_<table>_<rule>`。
- 视图为 `v_<name>`；物化视图为 `mv_<name>`；schema 名小写。
- 审计列为 `created_at`、`updated_at`、`created_by`、`updated_by`；软删除为 `deleted_at`。
- 布尔列为 `is_`/`has_`；时间戳为 `_at`；金额为 `<amount>_cents` 加 `currency`。
- 迁移文件带时间戳并只陈述一次逻辑变更：`20261114093000_add_order_status.sql`；
  schema 变更流程与迁移安全性属于 api-and-data-conventions。

## 18. 配置与环境

- 环境变量用带应用前缀的 UPPER_SNAKE_CASE：`APP_DATABASE_URL`、`APP_LOG_LEVEL`、
  `APP_HTTP_TIMEOUT_MS`。
- 名称说明用途，而不是取值或提供方：用 `APP_DATABASE_URL`，而不是 `APP_POSTGRES_1`。
- 名称中不含机密值；名称可以出现 `PASSWORD` 或 `TOKEN`，但取值来自机密存储。
- 配置键每个系统只用一种分隔符：`http.timeout_ms` 或 `http_timeout_ms`；不要混用。
- 功能开关为 `ff_<domain>_<name>` 或 `<domain>.<flag>`；环境后缀属于取值，不属于名称。
- 单位与允许值出现在名称或其文档中；默认值、取值范围与重启语义属于 code-style-conventions。

## 19. CLI

- 命令用小写动词（`create`、`list`、`delete`），子命令用小写名词（`app user create`）；选定一种
  顺序并保持一致。
- 标志用 kebab-case：`--dry-run`、`--output-format`、`--no-color`；短标志只有一个字母且绝不产生
  歧义（`-v` 不能同时表示 verbose 与 version）。
- 布尔标志默认为 false，肯定式为默认值时用 `--no-` 取反。
- 位置参数按 `<required>` 与 `[optional]` 记录；其名称与帮助文本一致。
- 退出码要记录：`0` 成功，非零失败；不要只在数字中编码原因而不给消息。
- CLI 的环境变量使用与服务相同的 `APP_` 前缀与相同名称。

## 20. 日志、事件、指标与追踪

- 日志字段是稳定的 snake_case：`timestamp`、`level`、`event`、`service`、`trace_id`、`span_id`、
  `user_id`；`message` 是自由文本。
- 事件为过去时的 `object.action`：`order.created`、`invoice.paid`；payload 字段与 API schema 一致。
- 指标为 `domain_operation_unit`：`http_request_duration_ms`、`queue_depth`、`cache_hits_total`；
  计数器以 `_total` 结尾，直方图带单位，gauge 说明当前值。
- 追踪标识符为 `trace_id` 与 `span_id`；遥测设计（包括指标标签与基数）属于
  release-operations-conventions。
- 日志带稳定的 `error_code`；日志内容策略（包括机密与个人数据）属于 code-style-conventions。
- 事件字段名在同一 schema 版本内保持稳定；事件 schema 版本化属于 api-and-data-conventions。

## 21. 资产、CSS、HTML 与 i18n

- 资产文件用 kebab-case，相关时包含倍率或尺寸：`hero-image@2x.png`、`icon-close.svg`、
  `logo-dark.svg`。
- CSS 类用 kebab-case；BEM 为 `block__element--modifier`（`order-item__price--discounted`）；
  工具类遵循框架前缀。
- ID 保留给锚点与 JavaScript 钩子；JS 钩子使用 `js-`（`js-order-form`）且不参与样式。
- 自定义属性为 `--color-bg`、`--space-md`、`--font-body`；不要无法解释的缩写。
- HTML data 属性为 `data-` 加 kebab-case（`data-order-id`）；表单字段名遵循后端 schema。
- i18n 键为点分隔的小写：`orders.list.empty`、`checkout.payment.declined`；复数键使用平台后缀
  （`_one`、`_other`）；绝不用英文句子作键。
- 可访问名称与可见标签一致；alt 文本描述图片内容，而不是文件名。

## 22. 提交、分支与标签

- 提交为 `type(scope): imperative summary`；类型有 `feat`、`fix`、`refactor`、`docs`、`test`、
  `chore`、`perf`、`build` 与 `ci`。
- 摘要用祈使句，冒号后小写：`fix(invoice): reject expired cards`，而不是 `Fixed the bug`。
- 分支为 `type/short-description`：`feat/order-export`、`fix/expired-card`；小写、连字符、无空格。
- 标签为带 `v` 前缀的 SemVer：`v1.4.0`、`v1.4.0-rc.1`；绝不用日期或构建号作为发布标签。
- 提交正文与脚注的构成、pull request 标题、合并门禁与历史策略属于 vcs-collaboration-conventions；
  本节只定义名称。

## 23. 功能开关与弃用

- 开关名称说明其范围与用途：`ff_checkout_new_tax` 或 `checkout.new_tax`。生命周期规则（包括默认
  状态、负责人与移除日期）属于 release-operations-conventions。
- 不要把环境或客户名放进开关名称；那属于定向规则。
- 被弃用的名称要有移除计划：优先用注解或弃用元数据字段；必须用前缀时，使用 `deprecated_` 或
  `legacy_` 并记录替代项。
- 别名最多保留一个发布周期；记录映射关系；弃用窗口结束时移除别名。
- 绝不无限期保留同一概念的两个在用名称；那是冲突，不是兼容性。

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

## 27. 重命名与迁移

1. 陈述证据：歧义、冲突、领域概念改名或规则违规。没有证据的重命名只是折腾。
2. 列出所有引用：代码、测试、文档、fixture、配置、数据库对象、API 客户端、看板与告警。
3. 选定新名称与迁移路径：在一次受限变更内完成内部重命名，或使用公开别名加弃用，或对数据库做
   扩展—收缩式迁移（expand-and-contract）。
4. 定义回滚路径。内部重命名靠一次只做重命名、可独立 revert 的提交回滚；公开名称保留旧别名直到
   所有消费方切换，回滚是重新指向旧名称；数据库扩展—收缩的回滚是先停写新列、再删除新列，绝不在
   消费方切完前删除旧列。回滚顺序与上线顺序相反：先回消费方，再回提供方。
5. 在同一次变更中更新测试与文档；不要在示例中留下过时的名称。
6. 保持 diff 可审查：重命名提交不应携带行为变更；行为变更也不应掩盖重命名。
7. 更新命名表，并在弃用窗口结束后移除别名；变更日志更新属于 documentation-conventions。
8. 历史策略（包括是否重写已发布历史）属于 vcs-collaboration-conventions。

## 28. 豁免

- 生成代码、第三方引入代码、protobuf、OpenAPI 生成的客户端与第三方 schema 保留其名称。在边界处
  隔离它们，并记录映射。
- 语言或框架的强制约定覆盖本文件，即使与本文件的默认值冲突。
- 现有项目约定优先于本标准；如果它有害，提出一次受限迁移，不要重命名未被请求的代码。
- 公开 API 名称是契约；只有提供版本化或弃用路径时才能重命名。
- 反模式如果普遍存在，报告它并给出迁移估算；未经授权不要发起批量重命名。

## 29. 基础设施与部署

- DNS 标签使用小写字母、数字与连字符；以字母或数字开头和结尾；不超过 63 个字符；不用下划线。
- Docker 镜像为 `<registry>/<org>/<service>:<tag>`；tag 是 SemVer 或提交 SHA，容器名为
  `<service>-<role>`。版本与分发策略属于 release-operations-conventions 与
  repository-governance-conventions。
- Kubernetes 名称是 DNS-1123 小写 kebab：`invoice-api`、`invoice-worker`；标签使用标准键
  `app.kubernetes.io/name`、`app.kubernetes.io/component` 与 `app.kubernetes.io/part-of`。
- ConfigMap 为 `<service>-config`；Secret 为 `<service>-secrets`；命名空间小写（`billing-prod`）。
- 云资源名称包含应用与环境；标签携带 `app`、`env`、`owner` 与 `cost-center`；绝不在资源名称中
  放机密。
- Terraform 资源用 `snake_case`，模块用 `kebab-case`，state 键为 `<env>/<service>/<component>`。
- CI 任务用带阶段前缀的小写 kebab（`test-unit`、`deploy-prod`）；CI 机密使用 `CI_` 前缀。
  CI/CD 与机密处理策略属于 release-operations-conventions 与 security-compliance-conventions。
- 环境名为 `dev`、`staging` 与 `prod`；不要用 `production2` 或 `new-prod` 作为同一环境的第二个名称。

## 30. 权限、角色、作用域与审计动作

- 权限与角色标识符使用 `domain.action`：`billing.invoice.read`、`billing.invoice.void`。
- 每个系统选定一种分隔符（`.` 或 `:`）并保持一致；`billing:invoice.read` 混用了两种语法。
- 作用域使用与权限相同的语法（`orders:read` 或 `read:orders`）；选定一种顺序并记录。
- 角色名描述能力，而不是职位：`billing_admin`、`support_readonly`。访问控制策略（包括存在多少个
  admin 角色）属于 security-compliance-conventions。
- 只有语言要求常量时，权限常量才用 UPPER_SNAKE（`BILLING_INVOICE_READ`）；否则使用字符串标识符。
- 审计动作为过去时的 `object.action`（`invoice.voided`）；记录包含操作者、资源 ID 与结果。
- 不要在权限名称中编码租户、客户或用户 ID；那些属于策略数据，而不是标识符。

## 31. 已发布包与模块

- npm：小写与连字符，公开时加 scope（`@example/invoice-core`）；不用大写或空格。
- PyPI：小写，用连字符或下划线；分发名与导入名可能不同，两者都要记录。
- crates.io：小写，优先用下划线；crate 名与库名通常相同。
- Maven：`groupId` 是反向域名；`artifactId` 用 kebab-case（`invoice-core`）。
- NuGet：包 ID 用 PascalCase（`Example.Billing`）；程序集名与包名一致，除非做了版本化。
- Go modules：模块路径小写；包名简短、小写且不含下划线；连字符可以出现在路径中，不能出现在包名中。
- 版本标签是 SemVer；包仓库后缀（`-beta.1`）不能替代版本号。

## 32. 组件、Hooks 与 UI 状态

- 组件用 PascalCase，每个文件一个：`OrderCard.tsx`、`InvoiceList.vue`；`Page`、`Layout`、`Provider`
  与 `Dialog` 后缀只用于真实角色，默认不要用 `Wrapper` 或 `Container`。
- 自定义 hook 以 `use` 开头（`useOrders`、`useDebouncedValue`）；hook 名称意味着它遵循 hooks 规则。
  返回具名状态与动作（`data`、`isLoading`、`error`、`refetch`）。
- Props 中用 `onX` 表示回调，`isX`/`hasX` 表示布尔值，`children` 表示组合，`renderX` 表示渲染
  属性；内部处理器为 `handleX`。
- UI 状态命名问题本身：`isLoading`、`hasError`、`selectedId`、`activeTab`；避免裸的 `data`、
  `loading` 或 `state`。服务端状态与本地 UI 状态同时存在时，在名称中区分。
- 事件为 `onSubmit`、`onChange`、`onClose`；对外发出的领域事件用过去时（`orderCreated`）。
- 框架约定优先：Vue 组件用多词（`OrderCard`）；Angular 选择器用 kebab-case（`app-order-card`），
  服务以 `Service` 结尾；React context 为 `OrderContext`，其 hook 为 `useOrderContext`。
- 组件的名称避免 `Wrapper`、`Container` 与 `Manager`；命名用户看到的东西，或组件所做的事。

## 33. 领域模型与领域事件

- 实体用单数名词（`Order`、`Customer`）；值对象命名概念及其单位（`Money`、`DateRange`、
  `EmailAddress`、`Percentage`）。
- 标识符在代码中为 `<Entity>Id`，在存储中为 `<entity>_id`；不要在领域 API 中暴露名为 `id` 的裸字符串。
- 聚合命名一致性边界（`Order`），而不是 `OrderAggregate`；仓库为 `OrderRepository`。
- 领域事件用过去时（`OrderPlaced`、`InvoicePaid`）；线上事件类型为 `order.placed`；payload 字段
  使用领域术语，而不是数据库列名。
- 命令用祈使式（`PlaceOrder`、`VoidInvoice`）；查询为 `GetOrder` 或 `ListOrders`；两者都不是
  名词加 `Manager`。
- 策略与规约命名规则（`RefundPolicy`、`EligibleForDiscount`）；策略返回决策，而不是名为 `check`
  的布尔值。
- 把技术性名称（`Manager`、`Helper`、`Util`）挡在领域模型之外；编排放在应用层，并用角色名
  （`CheckoutService`、`InvoiceSync`）。

## 34. 文档、图表与决策

- 文档文件用 kebab-case；ADR 编号且稳定（`0001-use-postgres.md` 或
  `ADR-0001-use-postgres.md`）；绝不为已接受的 ADR 重新编号。
- 标题是稳定的锚点；不要重命名被链接的标题，除非同时提供重定向或更新链接。遵循项目的标题大小写
  （句首大写或词首大写），不要两者混用。
- 图表 ID 为 `fig-<name>` 或 `diagram-<name>`；节点 ID 使用领域或服务名（`order-service`、
  `billing-db`），而不是 `node1`。
- API 操作 ID 用 camelCase（`listOrders`、`createInvoice`）；代码示例为 `example_<action>`，并与它们
  说明的操作放在一起。
- 工单与 issue ID 属于链接、元数据或提交脚注，不应只作为标识符、文件名或测试名中的描述。
- 交叉引用使用命名表中的术语；文档术语与代码术语不一致就是缺陷。
