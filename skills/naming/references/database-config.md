# 数据库与配置

## 1. 数据库与配置

- 表名用复数 snake_case：`order_items`；列名用单数 snake_case：`created_at`、`customer_id`。
- 主键用 `id`，外键用 `<表名单数>_id`；索引与约束带前缀：`idx_orders_customer_id`、`uq_users_email`。
- 环境变量用带应用前缀的 UPPER_SNAKE_CASE：`APP_DATABASE_URL`；名称不包含机密值。
- CLI 标志用 kebab-case：`--dry-run`、`--output-format`；短标志与长标志一一对应并保持一致。
- 配置键使用与所在格式匹配的大小写；同一个键在所有环境与文档中使用同一个名称。
- CSS 类用 kebab-case 或 BEM：`order-item__price--discounted`；i18n 键用点分隔小写：`orders.list.empty`。
- 日志、事件与指标字段用稳定的 snake_case，事件名用 `object.action` 形式，指标名带单位后缀。
