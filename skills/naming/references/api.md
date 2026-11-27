# API 与序列化

## 1. API 与序列化

- HTTP 资源用复数名词，路径用 kebab-case：`/v1/order-items`；查询参数用 snake_case：`created_after`。
- 每个 schema 只选一种 JSON 键大小写，通常 camelCase 或 snake_case；在边界处映射为代码的大小写，不在一个 schema 中混用。
- RPC 方法与 GraphQL 字段遵循各协议的命名习惯：方法名用动词，字段名用 camelCase。
- 标识符在代码中写作 `<Entity>Id`，在存储与 HTTP JSON 资源中写作 `<entity>_id`；时间戳用 `<event>_at`，时长与计数用 `<quantity>_ms`、`<thing>_count`。
- 金额用 `<amount>_cents` 并配货币字段；比率用 `_ratio`（0 到 1）或 `_pct`（0 到 100），范围写入名称或文档。
- 错误码稳定且每个原因一个码：`E_SYNC` 这类机器可读形式；对外错误码的目录由 `api-data` 的契约裁定，本文件只裁定码的命名形态。
