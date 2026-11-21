# 命名维度：接口

本文件为 `SKILL.md` 维度索引中接口部分的细则；节号与索引一致，其他维度见同目录的 `dimensions-*.md`。

## 15. HTTP、RPC 与 GraphQL

- HTTP 路径使用复数 kebab-case 资源：`/v1/order-items`；子资源嵌套其中：`/v1/orders/{orderId}/items`。
- 查询参数每个 API 使用一种大小写：`created_after`、`page_size`、`sort`、`order`；不得在一个 API 中混用
  `createdAfter` 与 `created_after`。
- JSON 字段遵循 schema 的大小写；布尔值用 `is_`/`has_`，时间戳用 `_at`，标识符用 `<entity>_id`。
- RPC 方法为 `VerbNoun`：`GetOrder`、`ListOrders`、`CreateOrder`；请求与响应类型为 `GetOrderRequest` 与
  `GetOrderResponse`。
- GraphQL 类型用 PascalCase，字段用 camelCase，枚举用 UPPER_SNAKE；mutation 用动词短语（`createOrder`），
  input 以 `Input` 结尾。
- API 版本化、分页风格、CRUD 语义与错误 payload 字段属于 api-and-data-conventions 的策略；本节仅定义命名
  语法。

## 16. JSON 与序列化

- 每个 schema 选定一种键大小写，并在生产者与消费者之间保持一致；仅在边界处映射为语言的大小写。
- 键中不得含空格；除表达命名空间外，避免点号；避免保留字与前导数字。
- 布尔值用 `is_`/`has_`；时间戳用 `_at` 并遵循 RFC 3339；ID 用 `<entity>_id`；枚举使用稳定取值。
- 数组用复数；用作映射的对象在字段名中写出键（`users_by_id`）。
- null 与缺失属于不同状态；记录以哪一种表示缺失，且不得使用字符串 `"null"`。
- 不得在键中编码类型（`str_name`、`int_count`）；除协议要求外，不得将一切内容包进 `data`。
- 判别字段为 `type` 或 `kind`，取值稳定且小写；不得将显示标签放入 payload。

## 17. 数据库与迁移

- 表用复数 snake_case：`orders`、`order_items`；列用单数：`created_at`、`customer_id`。
- 主键为 `id`，但表使用自然键的除外；外键为 `<referenced_table>_id`。
- 连接表按字母顺序写成 `<a>_<b>`：`order_product`，不得写作 `product_order_link`。
- 索引为 `idx_<table>_<columns>`；唯一约束为 `uq_<table>_<columns>`；外键为 `fk_<table>_<referenced_table>`；
  检查约束为 `ck_<table>_<rule>`。
- 视图为 `v_<name>`；物化视图为 `mv_<name>`；schema 名小写。
- 审计列为 `created_at`、`updated_at`、`created_by`、`updated_by`；软删除为 `deleted_at`。
- 布尔列为 `is_`/`has_`；时间戳为 `_at`；金额为 `<amount>_cents` 加 `currency`。
- 迁移文件带时间戳，且仅陈述一次逻辑变更：`20261114093000_add_order_status.sql`；schema 变更流程与迁移
  安全性属于 api-and-data-conventions。

## 18. 配置与环境

- 环境变量用带应用前缀的 UPPER_SNAKE_CASE：`APP_DATABASE_URL`、`APP_LOG_LEVEL`、`APP_HTTP_TIMEOUT_MS`。
- 名称说明用途，不说明取值或提供方：使用 `APP_DATABASE_URL`，不得使用 `APP_POSTGRES_1`。
- 名称中不得含机密值；名称可以出现 `PASSWORD` 或 `TOKEN`，但取值应当来自机密存储。
- 配置键每个系统仅用一种分隔符：`http.timeout_ms` 或 `http_timeout_ms`；不得混用。
- 功能开关为 `ff_<domain>_<name>` 或 `<domain>.<flag>`；环境后缀属于取值，不属于名称。
- 单位与允许值出现于名称或其文档中；默认值、取值范围与重启语义属于 code-style-conventions。

## 19. CLI

- 命令用小写动词（`create`、`list`、`delete`），子命令用小写名词（`app user create`）；选定一种顺序并保持
  一致。
- 标志用 kebab-case：`--dry-run`、`--output-format`、`--no-color`；短标志仅一个字母，且不得产生歧义
  （`-v` 不得同时表示 verbose 与 version）。
- 布尔标志默认为 false；肯定式为默认值的，用 `--no-` 取反。
- 位置参数按 `<required>` 与 `[optional]` 记录；其名称与帮助文本一致。
- 退出码应当记录：`0` 表示成功，非零表示失败；不得仅在数字中编码原因而不给出消息。
- CLI 的环境变量使用与服务相同的 `APP_` 前缀与相同名称。

## 20. 日志、事件、指标与追踪

- 日志字段为稳定的 snake_case：`timestamp`、`level`、`event`、`service`、`trace_id`、`span_id`、
  `user_id`；`message` 为自由文本。
- 事件为过去时的 `object.action`：`order.created`、`invoice.paid`；payload 字段与 API schema 一致。
- 指标为 `domain_operation_unit`：`http_request_duration_ms`、`queue_depth`、`cache_hits_total`；计数器以
  `_total` 结尾，直方图带单位，gauge 说明当前值。
- 追踪标识符为 `trace_id` 与 `span_id`；遥测设计（包括指标标签与基数）属于 release-operations-conventions。
- 日志带稳定的 `error_code`；日志内容策略（包括机密与个人数据）属于 code-style-conventions。
- 事件字段名在同一 schema 版本内保持稳定；事件 schema 版本化属于 api-and-data-conventions。

## 21. 资产、CSS、HTML 与 i18n

- 资产文件用 kebab-case；相关时包含倍率或尺寸：`hero-image@2x.png`、`icon-close.svg`、`logo-dark.svg`。
- CSS 类用 kebab-case；BEM 为 `block__element--modifier`（`order-item__price--discounted`）；工具类遵循
  框架前缀。
- ID 保留给锚点与 JavaScript 钩子；JS 钩子使用 `js-`（`js-order-form`），且不参与样式。
- 自定义属性为 `--color-bg`、`--space-md`、`--font-body`；不得使用无法解释的缩写。
- HTML data 属性为 `data-` 加 kebab-case（`data-order-id`）；表单字段名遵循后端 schema。
- i18n 键为点分隔的小写：`orders.list.empty`、`checkout.payment.declined`；复数键使用平台后缀（`_one`、
  `_other`）；不得以英文句子作键。
- 可访问名称与可见标签一致；alt 文本描述图片内容，不描述文件名。

## 22. 提交、分支与标签

- 提交为 `type(scope): imperative summary`；类型有 `feat`、`fix`、`refactor`、`docs`、`test`、`chore`、
  `perf`、`build` 与 `ci`。
- 摘要用祈使句，冒号后小写：`fix(invoice): reject expired cards`，不得写作 `Fixed the bug`。
- 分支为 `type/short-description`：`feat/order-export`、`fix/expired-card`；小写、连字符、无空格。
- 标签为带 `v` 前缀的 SemVer：`v1.4.0`、`v1.4.0-rc.1`；不得以日期或构建号作为发布标签。
- 提交正文与脚注的构成、pull request 标题、合并门禁与历史策略属于 vcs-collaboration-conventions；本节仅
  定义名称。

## 23. 功能开关与弃用

- 开关名称说明其范围与用途：`ff_checkout_new_tax` 或 `checkout.new_tax`。生命周期规则（包括默认状态、
  负责人与移除日期）属于 release-operations-conventions。
- 不得将环境或客户名放入开关名称；该内容属于定向规则。
- 被弃用的名称应当具有可搜索的替代名称；必须使用前缀的，使用 `deprecated_` 或 `legacy_`，并记录映射关系。
- 别名属于兼容层，不属于第二个规范名称；应当记录映射关系。
- 不得无限期保留同一概念的两个在用名称；该情形属于冲突，不属于兼容性。
- 移除窗口与公告由 `release-operations-conventions` 裁定，代码内标记格式由 `comment-conventions` 裁定。
