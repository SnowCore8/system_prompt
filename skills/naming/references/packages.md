# 包与命名空间

## 1. 包与命名空间

- Java 与 Kotlin 用反向域名，全小写，不用下划线：`com.example.billing`；Python 包名简短小写，不用连字符；Go 包名简短小写，不用下划线或混合大小写。
- npm 包小写，公开时加 scope：`@example/billing`；Rust 模块与 crate 用 snake_case，同一路径中避免 crate 与模块同名。
- 按领域命名，不按层次命名：`billing.payments` 而非 `services.managers`。
- 避免名称重复（stuttering）：用 `billing.Invoice` 而非 `billing.BillingInvoice`，限定词能消除歧义的除外。
- 公开接口置于具名包中；公开入口与可见性边界（`internal/`、`_private` 等）由 `project-structure` 裁定，本维度只裁定包的名称形态。

| 好 | 差 | 原因 |
|---|---|---|
| `com.example.billing` | `com.example.Billing_App` | Java 包小写、不用下划线 |
| `billing.payments` | `services.managers` | 领域名经受得住重构，层次名则否 |
| `internal/parser` | `misc/parser` | `internal` 说明可见性契约 |
