# 注释维度：API 与公开契约

本文件应当与 `SKILL.md` 配合使用。每一节规定一种注释类型或隐患的规则、边界情况与失败模式。项目已有成文约
定或 linter 的，智能体应当先阅读并将其作为事实输入；本 skill 的规则优先，项目约定仅在本 skill 未规定时补
充。本文件提供默认值与理由。节号与 `SKILL.md` 中的维度索引对应。

## 1. 文档注释与公开 API 契约

- 文档注释是调用方能够看到的一切的公开契约：导出函数、类型、方法、协议实现与有文档的配置。
- 契约覆盖签名无法表达的内容：含义、前置条件、后置条件、错误行为、副作用、所有权与稳定性承诺。
- 应当以一句祈使式或第三人称摘要开头（“Return the invoice total in cents”），仅当调用方需要摘要无法承载
  的上下文时，方加一段正文。
- 不得重述签名。`@param user the user` 未增加任何内容；`@param email lower-cased and trimmed` 说明了前置
  条件。
- 应当把文档注释当作代码：审查其 diff，于同一次变更中随行为变更一并更新，公开含义变化时对其实施版本化。
- 应当注明某行为有意不规定（“iteration order is not guaranteed”），不得使读者推断契约。
- 应当把实现说明留于私有注释或函数体；不得向公开契约泄露内部缓存、加锁或字段布局。

| 好 | 差 | 原因 |
|---|---|---|
| `@param email Lower-cased and trimmed; rejects input without a local part.` | `@param email The email.` | 说明了签名无法承载的前置条件。 |
| `@returns 0 when no tax applies; never negative.` | `@returns the tax.` | 写出调用方必须处理的边界情况。 |
| `@throws InvoiceNotFoundError when the id is unknown.` | `@throws Exception on errors.` | 调用方能够处理具体类型，而非兜底异常。 |

## 3. 函数与方法

- 每个公开函数、方法与协议实现均应当有文档注释；私有辅助函数仅在名称与函数体确实留下空白时，方需要文档注释。
- 类型无法承载含义时应当记录参数：格式、编码、范围、可空性、所有权与默认行为。
- 应当记录返回值的含义与边界情况：为空与缺失、哨兵值、部分结果与顺序保证。
- 应当记录调用方需要处理的每一种错误，按类型与触发条件说明；不得列出内部且不会外泄的错误。
- 应当记录副作用（I/O、变更、事件、缓存写入），以及调用是否幂等、可重试或事务性。
- 调用顺序不显而易见的，应当于正文中放置一个示例；示例应当保持可运行（见第 11 节）。
- 以“This function...”开头的描述属于噪声；应当直接从动作及其对象开始。

| 好 | 差 | 原因 |
|---|---|---|
| `Read the current balance; the call may block up to timeout_ms.` | `Gets the balance.` | 说明 I/O 与上界。 |
| `Return matched orders sorted by created_at; empty when none match.` | `Returns orders.` | 排序与空状态属于契约的一部分。 |
| `Idempotent: a repeat with the same idempotency key returns the first result.` | `Safe to call.` | 说明了真实的重试契约。 |

## 4. 类型、字段、枚举与常量

- 类型的文档注释应当说明实例代表什么，以及其保证或要求的不变量；字段注释应当记录类型名称未能说明清楚的
  部分。
- 枚举成员含义无法从名称看出的，应当为其写文档；仅当线上值与代码名称不同时，方写明线上值。
- 字段注释应当包含单位、范围、null 的含义，以及值是可变的、派生的、缓存的，还是归接收者所有。
- 不得于描述中重复字段名；应当说明缺失的契约。
- 常量应当记录其来源与策略：数字从何而来、由谁负责、何时可以改变。
- 别名到另一种表示形式的类型应当说明边界（“仅用于线上格式”）以及映射发生之处。
- 不得于公开类型上记录私有表示（字段顺序、内部缓存、哈希种子）。

| 好 | 差 | 原因 |
|---|---|---|
| `OrderId` 是不透明的：不得解析、排序或显示它。 | `The order id.` | 说明了该表示形式的契约。 |
| `RetryCount` 每次尝试递增，并受 `MaxAttempts` 限制。 | `How many retries.` | 把字段与它们之间的不变量关联起来。 |
| `StatusRefunded` 是终态；不得再发生状态转换。 | `Refunded status.` | 写出调用方依赖的规则。 |

## 5. 单位、范围、可空性与所有权

- 类型无法强制单位时，应当于文档注释中按名称里的拼写写明单位：`timeout_ms`、`amount_cents`、
  `size_bytes`。
- 应当明确写出范围与包含关系：“0 到 100，包含两端”、“起点包含、终点不包含”；不得依赖读者的假设。
- 应当把 null、None、nil、undefined 与空定义为不同状态；说明每一种的含义，以及是否可能被返回。
- 在跟踪所有权的语言中，应当记录所有权、生命周期与修改权：谁释放该值、谁可以修改它、允许怎样的别名共
  享。
- 对于借用或引用的值，应当说明借用期限，以及调用返回后接收者是否仍持有引用。
- 对于集合，应当仅在顺序有保证时说明迭代顺序；否则应当声明顺序未指定。
- 数值的舍入、截断与溢出行为属于契约。

| 好 | 差 | 原因 |
|---|---|---|
| `Timeout in milliseconds; 0 means wait forever.` | `Timeout value.` | 单位与哨兵值是契约的一部分。 |
| `Return the slice borrowed from self; valid until the next mutation.` | `Returns a slice.` | 生命周期与别名规则决定安全用法。 |
| `Amount is an integer number of cents; never a float.` | `The amount.` | 表示形式与单位都是显式的。 |

## 6. 副作用、变更、并发与性能警告

- 应当说明每一个外部可观察的效果：网络、磁盘、数据库写入、事件发送、日志输出、全局状态，以及时钟或随机
  数的使用。
- 应当说明并发契约：线程安全、需要外部锁、必须在主线程运行，或不可重入。
- 应当在隐患之前而非之后警告：应当于同一条注释中说明条件、后果与必需动作。
- 应当记录对参数与接收者状态的修改，包括输入集合是被消费还是被保留。
- 性能说明必须可操作且有实测依据：“规则数量达到 n 时为 O(n^2)；规则只编译一次”胜于“慢”。
- 不得记录调用方无法依赖的临时实现细节（特定锁类型、缓冲区大小、线程数）。
- “WARNING”或“NOTE”前缀属于真正的标记：应当留给隐患与令人意外的行为，以免其失去分量。

| 好 | 差 | 原因 |
|---|---|---|
| `// Caller must hold the account lock; this method does not acquire it.` | `// Thread safe.` | 说明了实际的加锁契约。 |
| `// Emits one order.paid event after commit; consumers may see it twice.` | `// Sends event.` | 重复投递会改变消费者设计。 |
| `// WARNING: O(n^2) above 100 rules; precompile in the hot path.` | `// Slow.` | 界限与补救措施让说明可用。 |

## 7. 弃用声明

- 应当使用工具的标签实施弃用（`@deprecated`、`@Deprecated`、`#[deprecated]`），并于标记里用一句话写明替
  代项与迁移方式。
- 应当于标记里写明移除版本或日期，以及跟踪 issue；“很快会移除”不构成计划。
- 应当保持被弃用的符号可用且文档真实；不得留下已经与事实不符的弃用文档注释。
- 应当使用可搜索的稳定替代名称；API 形态变化时应当给出迁移片段。
- 不得把内部辅助函数标记为弃用以代替删除它；应当删除未使用的内部实现。
- 弃用时机、移除窗口与公告位置由 `release-operations-conventions` 裁定；本维度仅规定标记语法与替代项。

| 好 | 差 | 原因 |
|---|---|---|
| `@deprecated Use create_invoice; removed in v3.0 (issue #812).` | `@deprecated` | 写明路径、版本与跟踪项。 |
| `# Deprecated: use Store.put; the old key format is read-only.` | `# Old API.` | 说明替代项与仍保留的行为。 |
| `/** @deprecated Use totalCents; this getter rounds. */` | `/** Do not use. */` | 说明差异，而不只是禁令。 |

## 11. 文档注释中的代码示例

- 文档注释中的示例是否可执行取决于文档工具：支持 doctest 的工具（如 rustdoc、Sphinx doctest）会编译或
  运行示例，其中示例必须在每次构建时通过；其余工具的围栏示例标为非执行（`text` 或 `console`），不要求执行。
- 应当使用文档工具识别的语言标记（`python`、`rust`、`ts`）；有意不运行的片段应当标记为 `text` 或
  `console`。
- 应当展示最小完整设置：导入、必需的 fixture 与贴近实际的值；不得调用未写文档的辅助函数。
- 示例属于被执行的 doctest 时，应当精确写明期望输出，包括空白。
- 示例中不得使用机密、个人数据或生产 URL；应当使用 `example.test.invalid` 这类假值。
- API 大到无法完整演示时，应当仅展示一次调用，并链接独立指南，不得给出不完整的片段。
- 应当保持输出跨平台稳定：工具允许时，避免时间戳、随机 ID 与绝对路径。
