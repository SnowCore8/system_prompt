# 文档模板：发布与维护

本文件为发布与维护类文档的可复制骨架；复制后应当替换示例内容，并删减页面不需要的部分；各章节所依据的规则
见 `dimensions-delivery.md`。

## 运行手册

用途：使值班读者在压力之下处置一项告警或操作。
必需章节：触发条件、影响、首个动作、步骤、验证、回滚、升级。

```markdown
# Runbook: payments queue backlog

Trigger: queue depth above 10,000 for 10 minutes; charge retries are delayed.

1. Confirm the alert and post the depth in the incident channel.
2. Check workers: `kubectl -n payments get deploy/worker`.
3. Scale to six: `kubectl -n payments scale deploy/worker --replicas=6`.

Verify: depth below 1,000 for ten minutes. Rollback: scale to three. Escalation: payments on-call decides.
```

常见错误：写“调查队列”，未给出精确命令与预期输出。

## 变更日志条目

用途：记录一组已发布的用户可见变更。
必需章节：版本与日期、分组条目、升级动作、issue 链接。

```markdown
## 2.3.0 - 2026-02-10

Added: `POST /v1/charges` accepts an `Idempotency-Key` header (issue #142).

Deprecated: `GET /v1/orders` in 2.3; use `/v2/orders`; removed in 3.0 (issue #151).

Upgrade: send `Idempotency-Key` on every charge request.
```

常见错误：粘贴提交标题，未写用户可见变更与升级所需动作。

## 发布说明

用途：宣布一次发布，以及用户必须采取的动作。
必需章节：版本与日期、升级动作、亮点、分类、链接。

```markdown
# Release 2.3.0

Released 2026-02-10.

Upgrade: send `Idempotency-Key` on every `POST /v1/charges` call.
Highlights: retries are safe by default. Fixed: totals no longer round half-cent
amounts down. Full categories and links: [changelog](CHANGELOG.md).
```

常见错误：重复每一条变更日志条目，读者无法识别哪些变化需要采取行动。

## 迁移指南

用途：使现有用户在不丢失数据的前提下自旧行为迁移至新行为。
必需章节：受影响受众、时间线、字段映射、步骤、验证、回滚。

```markdown
# Migrate from `amount` to `amount_cents`

Audience: charge integrators. `amount_cents` is an integer; `currency` is required.

Timeline: 2.3 accepts both fields; 3.0 rejects `amount` with `400 amount_removed`.
Mapping: `amount: 25.00` becomes `amount_cents: 2500` plus `currency: "USD"`.

Steps: back up the table; fill `amount_cents`; deploy both fields; verify 100
invoices; drop `amount` after 3.0. Rollback: restore the backup.
```

常见错误：仅发布映射，未为数据重写提供备份与回滚步骤。

## 弃用通知

用途：告知用户某条路径即将终止、其替代方案以及终止时点。
必需章节：弃用项、版本、替代方案、原因、迁移链接。

```markdown
# Deprecated: `GET /v1/orders`

Deprecated in 2.3; removed in 3.0. Replacement: `GET /v2/orders`.

Why: `v1` returns orders without line items and cannot paginate. Migration:
the [migration guide](docs/migrations/orders-v2.md) maps every `v1` field.
```

常见错误：写明移除发布而未写替代方案，用户无法规划变更。

## 安全、法律与支持

用途：说明支持范围、问题报告方式，以及该页面的负责人。
必需章节：策略章节及各自链接的负责人；披露与响应承诺的细节按
`security-compliance-conventions` 执行。

```markdown
# Security and Support Policy

Supported versions: 2.x receives security fixes; 1.x is end-of-life.

Report a vulnerability through the private channel in `SUPPORT.md`. Example
values: acknowledgement within two business days; the security owner sets the real commitment.

Owner: security team. Last reviewed: 2026-02-10. Legal and support terms: [SUPPORT.md](SUPPORT.md).
```

上述确认窗口与审查日期为示例值；真实承诺由安全负责人设定。

常见错误：发布无人监控的报告地址，报告者将放弃或转向公开渠道。

## 事故复盘

用途：解释一次事故及其影响，以及防止再次发生的行动。
必需章节：摘要、影响、时间线、根因、发现、行动项、负责人。

```markdown
# Postmortem: duplicate charges on 2026-02-03

Summary: a retry storm charged 214 invoices twice over six hours. Impact:
customers were double-charged; refunds finished the same day.

Timeline: queue backed up at 02:10; the alert fired at 02:40; the fix shipped
at 08:05. Root cause: retries had no idempotency key. Detection: queue depth
alert. Actions: add idempotency keys (owner: payments); add a duplicate-charge
alert (owner: platform).
```

常见错误：将事故复盘写成追责，读者将隐瞒细节，而非改进发现。
