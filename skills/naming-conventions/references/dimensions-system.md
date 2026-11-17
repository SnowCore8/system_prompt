# 命名维度：系统

本文件是 `SKILL.md` 维度索引中系统部分的细则；节号与索引一致，其他维度见同目录的 `dimensions-*.md`。

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
- 内部错误码稳定且有结构：`ERR_BILLING_INVOICE_NOT_FOUND`，由本 skill 规定前缀与结构；公开 API 的错误码按
  `api-and-data-conventions` 的 dot 格式（`resource.not_found`）。不要用一个错误码表示两种原因，也不要把
  内部错误码直接暴露为公开 API 错误码。
- 结果类型说明成功与失败：`Result<T, E>`、`Outcome<T>`、`PaymentResult`；字段为 `ok`、`value`、
  `error`。
- 局部错误变量为 `err` 或 `error`；短 catch 块里 `e` 可以接受；绝不用模块级的 `e`。
- 错误消息与标识符分开；消息中不要放机密、令牌或个人数据。
- 包装外部错误时带上上下文：带 `cause` 的 `InvoiceSyncError`，而不是裸抛出。

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
7. 更新命名表；变更日志更新属于 documentation-conventions。
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

- 文档文件用 kebab-case，固定文件名例外：`README.md`、`CONTRIBUTING.md`、`CHANGELOG.md`、
  `SECURITY.md`、`SUPPORT.md`、`LICENSE`；ADR 编号且稳定（`0001-use-postgres.md` 或
  `ADR-0001-use-postgres.md`）；绝不为已接受的 ADR 重新编号。
- 标题是稳定的锚点；不要重命名被链接的标题，除非同时提供重定向或更新链接。遵循项目的标题大小写
  （句首大写或词首大写），不要两者混用。
- 图表 ID 为 `fig-<name>` 或 `diagram-<name>`；节点 ID 使用领域或服务名（`order-service`、
  `billing-db`），而不是 `node1`。
- API 操作 ID 用 camelCase（`listOrders`、`createInvoice`）；代码示例为 `example_<action>`，并与它们
  说明的操作放在一起。
- 工单与 issue ID 属于链接、元数据或提交脚注，不应只作为标识符、文件名或测试名中的描述。
- 交叉引用使用命名表中的术语；文档术语与代码术语不一致就是缺陷。
