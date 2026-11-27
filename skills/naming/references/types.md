# 类型与接口

## 1. 类型与接口

- 类、结构体、record 与类型别名用单数名词短语：`Invoice`、`OrderItem`、`UserId`。
- 接口命名能力或角色：`Readable`、`UserStore`、`PaymentGateway`；I 前缀仅用于 C# 及其约定要求的语言，不带入 Python、Go 或 Rust。
- 抽象基类用有意义的角色，不用默认的 `Base`：用 `Repository` 或 `Storage` 而非 `BaseRepository`。
- DTO 属于边界类型：`InvoiceDto`、`CreateOrderRequest`、`OrderResponse`；不给领域类型加 `Dto` 后缀。
- 泛型参数简短且符合惯例：`T`、`TKey`、`TValue`；角色不明显的用描述性名称。
- 避免 `Impl` 后缀，改用技术或角色：`SqlUserRepository`、`InMemoryUserRepository`。
- 不在类型名中编码可空性或可选性，由类型系统表达。
