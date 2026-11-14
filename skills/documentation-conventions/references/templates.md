# 文档模板

复制该文档类型的骨架，把示例内容替换为项目的真实内容，并删减页面不需要的部分。在 `dimensions.md`
中阅读匹配的维度，了解各章节背后的规则。

## README

用途：用一页让新读者建立方向，并把他们引导到下一步。
必需章节：名称与范围、安装、快速开始、配置、文档链接、许可证。

```markdown
# Invoice Service

Issues invoices and reconciles payments; requires Python 3.12 and PostgreSQL 16.

    pip install invoice-service
    invoice-service init --config config/dev.toml
    invoice-service serve

The health check is `GET /healthz`. See the [tutorial](docs/tutorials/first-invoice.md) and
[configuration reference](docs/reference/configuration.md). License: Apache-2.0.
```

常见错误：把 README 变成功能巡览，让第一条可运行命令落在首屏之下。

## CONTRIBUTING

用途：带新贡献者从全新克隆走到一次经过审查的变更。
必需章节：工具链、环境搭建、运行与测试、约定、审查预期。

```markdown
# Contributing

Setup: install Python 3.12 and Docker, then run `make bootstrap`.

    make run    # start the service
    make test   # run the tests

Branch as `feat/short-description` and commit as `type(scope): summary`.
Behavior changes need tests and docs; review takes two business days.
```

常见错误：只记录顺利路径的测试命令，贡献者无法复现 CI 失败。

## 架构概览

用途：向维护者展示系统如何组装，以及接下来该读哪里。
必需章节：背景、组件、边界、数据流、决策、已知限制。

```markdown
# Architecture

The API issues invoices synchronously; the worker reconciles payments asynchronously.

- `invoice-api`: HTTP API, validation, idempotency.
- `invoice-worker`: queue consumer, retries, reconciliation.
- PostgreSQL: invoices, payments, transactional outbox.
- Boundaries: `invoice-api` validates; `invoice-worker` handles retries.

The API commits an invoice and an outbox row together; the worker publishes
and retries with backoff (ADR-0003, ADR-0007). Known limit: one primary database.
```

常见错误：复述代码拥有的接口签名，而不是写明边界。

## ADR

用途：为未来的维护者保留一个决策、其背景与后果。
必需章节：状态、日期、背景、决策、后果、备选方案。

```markdown
# ADR-0007: Require idempotency keys for charge retries

Status: Accepted. Date: 2026-02-10. Context: a timeout retry can charge the same
invoice twice, and the provider cannot detect the duplicate.

Decision: every `POST /v1/charges` request requires an `Idempotency-Key`; the
API stores it for 24 hours and returns the original response.

Consequences: the key store adds one table; retries within 24 hours are safe.
Alternative: client-side deduplication, rejected because a crashed client retries.
```

常见错误：事后编辑已接受的决策，而不是写一条取代它的新 ADR。

## 设计文档或 RFC

用途：让审查者在动手构建之前评判一项提议的变更。
必需章节：问题、目标与非目标、提案、备选方案、风险、上线、未决问题。

```markdown
# RFC-0014: Split invoice rendering from billing

Problem: rendering changes ship with billing changes, so every release risks both.

Goal: versioned rendering without an API deploy. Non-goal: moving invoice history.

Proposal: the API emits an invoice event; a renderer consumes it and writes a PDF.
Alternative: render inside the API, rejected because it couples templates to deploys.
Risks: duplicate renders during the migration, deduped by invoice ID.
Rollout: shadow renders for two weeks, then switch. Open question: template owner.
```

常见错误：只提设计而不写非目标，审查者会重新打开 RFC 已经解决的范围问题。

## 教程

用途：教学习者从干净起点完成一个可工作的示例。
必需章节：预期结果、前提、编号步骤、最终结果、下一步。

```markdown
# Tutorial: issue your first invoice

You will create a customer, issue an invoice, and check its state in ten minutes; run `make run` first.

1. Create a customer: `invoice-service customers create --name Acme`.
2. Issue an invoice: `invoice-service invoices issue --customer cus_123
   --amount-cents 2500`.
3. Inspect it: `invoice-service invoices show inv_123`.

Result: state `open`, amount `2500` cents. Next: configuration reference.
```

常见错误：提供分支选项，把引导路径变成读者独自做的决定。

## 操作指南

用途：让实践者完成一项他们已经理解的任务。
必需章节：目标、前提、步骤、验证、常见失败。

```markdown
# How to retry a failed charge

Goal: retry a declined charge once; the invoice is `open`, the charge `failed`.

1. Find it: `invoice-service charges list --invoice inv_123`.
2. Retry it: `invoice-service charges retry ch_123`.
3. Confirm it: `invoice-service charges show ch_123`.

Verify: `invoice-service invoices show inv_123` reports `paid`.
Common failure: `409 charge_not_retryable` means it already succeeded.
```

常见错误：解释概念而不是步骤，读者读完仍没完成任务。

## 参考页

用途：陈述实践者在工作中需要的精确事实。
必需章节：概要、选项与默认值、约束、版本说明、示例。

```markdown
# `invoice-service invoices issue` reference

Issues an invoice and returns its ID. Synopsis:

    invoice-service invoices issue --customer CUSTOMER --amount-cents N

Options: `--customer` (string, required); `--amount-cents` (integer, required);
`--currency` (string, default `USD`). Version note: `--currency` is 2.3+.
Example: `invoice-service invoices issue --customer cus_123 --amount-cents 2500`.
```

常见错误：用散文替换精确类型与默认值，读者必须读代码才能使用页面。

## API 参考页

用途：让集成者第一次就正确调用一个端点。
必需章节：方法与路径、认证、参数、响应、错误、示例。

```markdown
# POST /v1/charges

Creates a charge. Auth: bearer token in `Authorization`, scope `charges:write`.

Body: `invoice_id` (string, required), `amount_cents` (integer, required),
`idempotency_key` (string, required, unique per retry window).

Response: `201` with `id`, `state`; `409` if paid. Errors: `400 invalid_request`,
`402 charge_declined`. Example: send the idempotency header with the invoice ID.
```

常见错误：只记录成功路径，让集成者在生产中发现错误码。

## 概念或解释

用途：在读者执行任务之前解释行为背后的模型。
必需章节：想法、模型、词汇、权衡、示例、链接。

```markdown
# Charge states

A charge moves through `pending`, `succeeded`, and `failed`; a retry reuses the
same charge until it succeeds or the retry window ends.

The model keeps one charge per attempt and an invoice-level balance, so a failed
charge never changes the total. Tradeoff: the balance needs a reconciliation job.
Example: [retry guide](docs/guides/retry-charge.md).
```

常见错误：把概念写成步骤，读者照抄步骤却没有学到模型。

## 运行手册

用途：让值班读者在压力下解决一个告警或操作。
必需章节：触发条件、影响、首个动作、步骤、验证、回滚、升级。

```markdown
# Runbook: payments queue backlog

Trigger: queue depth above 10,000 for 10 minutes; charge retries are delayed.

1. Confirm the alert and post the depth in the incident channel.
2. Check workers: `kubectl -n payments get deploy/worker`.
3. Scale to six: `kubectl -n payments scale deploy/worker --replicas=6`.

Verify: depth below 1,000 for ten minutes. Rollback: scale to three. Escalation: payments on-call decides.
```

常见错误：写“调查队列”而不是精确命令与预期输出。

## 变更日志条目

用途：记录一组已发布的用户可见变更。
必需章节：版本与日期、分组条目、升级动作、issue 链接。

```markdown
## 2.3.0 - 2026-02-10

Added: `POST /v1/charges` accepts an `Idempotency-Key` header (issue #142).

Deprecated: `GET /v1/orders` in 2.3; use `/v2/orders`; removed in 3.0 (issue #151).

Upgrade: send `Idempotency-Key` on every charge request.
```

常见错误：粘贴提交标题，而不是用户可见变更与升级所需动作。

## 发布说明

用途：宣布一次发布及其用户必须采取的动作。
必需章节：版本与日期、升级动作、亮点、分类、链接。

```markdown
# Release 2.3.0

Released 2026-02-10.

Upgrade: send `Idempotency-Key` on every `POST /v1/charges` call.
Highlights: retries are safe by default. Fixed: totals no longer round half-cent
amounts down. Full categories and links: [changelog](CHANGELOG.md).
```

常见错误：重复每一条变更日志条目，读者看不出哪些变化需要行动。

## 迁移指南

用途：让现有用户在不丢失数据的情况下从旧行为迁移到新行为。
必需章节：受影响受众、时间线、字段映射、步骤、验证、回滚。

```markdown
# Migrate from `amount` to `amount_cents`

Audience: charge integrators. `amount_cents` is an integer; `currency` is required.

Timeline: 2.3 accepts both fields; 3.0 rejects `amount` with `400 amount_removed`.
Mapping: `amount: 25.00` becomes `amount_cents: 2500` plus `currency: "USD"`.

Steps: back up the table; fill `amount_cents`; deploy both fields; verify 100
invoices; drop `amount` after 3.0. Rollback: restore the backup.
```

常见错误：只发布映射，却没有为数据重写提供备份与回滚步骤。

## 弃用通知

用途：告诉用户某条路径即将终止、由什么替代以及何时。
必需章节：弃用项、版本、替代方案、原因、迁移链接。

```markdown
# Deprecated: `GET /v1/orders`

Deprecated in 2.3; removed in 3.0. Replacement: `GET /v2/orders`.

Why: `v1` returns orders without line items and cannot paginate. Migration:
the [migration guide](docs/migrations/orders-v2.md) maps every `v1` field.
```

常见错误：写明移除发布却不写替代方案，用户无法规划变更。

## 故障排查条目

用途：帮助卡住的读者把一个可观察症状变成修复。
必需章节：症状、原因、修复、预防、相关链接。

```markdown
## `charge_declined` on a valid card

Symptom: `POST /v1/charges` returns `402 charge_declined`.

Cause: the provider declined the risk check. Fix: log the `decline_code` and
ask for a different card. Prevention: validate with a zero-value authorization.
Related: [charge states](docs/concepts/charge-states.md).
```

常见错误：按内部原因组织条目，读者无法从看到的错误找到条目。

## 安全、法律与支持

用途：说明支持什么、如何报告问题，以及谁负责该页面。
必需章节：策略章节及各自链接的负责人；披露内容与响应承诺由
`security-compliance-conventions` 规定。

```markdown
# Security and Support Policy

Supported versions: 2.x receives security fixes; 1.x is end-of-life.

Report a vulnerability through the private channel in `SUPPORT.md`. Example
values: acknowledgement within two business days; the security owner sets the real commitment.

Owner: security team. Last reviewed: 2026-02-10. Legal and support terms: [SUPPORT.md](SUPPORT.md).
```

上面的确认窗口与审查日期是示例值；安全负责人设定真实承诺。

常见错误：发布没人监控的报告地址，报告者会放弃或转向公开渠道。

## 事故复盘

用途：解释一次事故、其影响，以及防止再次发生的行动。
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

常见错误：把事故复盘写成追责，读者会隐瞒细节而不是改进发现。

## 术语表

用途：为每个项目术语固定一个含义与一种拼写。
必需章节：按字母顺序的术语表、定义、被禁用的同义词、负责人。

```markdown
# Glossary

| Term | Definition | Avoid |
|---|---|---|
| charge | One attempt to collect a payment. | payment item |
| invoice | A bill sent to a customer. | bill |
| settlement | The provider's payout to the merchant. | payout |

Owner: billing team. Add a term when it appears in a second document.
```

常见错误：让每个团队保留自己的术语表，同一术语出现两个定义。

## 文档索引或地图

用途：把每位读者引导到回答其问题的页面。
必需章节：从这里开始的链接、按文档类型划分的章节、归属或反馈路径。

```markdown
# Invoice Service documentation

Start here: [tutorial](docs/tutorials/first-invoice.md), [contributing](CONTRIBUTING.md).

Guides: [retry a failed charge](docs/guides/retry-charge.md).
Reference: [configuration](docs/reference/configuration.md).
Operations: [payments queue backlog](docs/runbooks/payments-queue.md).
Feedback: [support](SUPPORT.md).
```

常见错误：新页面没有放进索引，只能通过直接链接到达，并慢慢腐烂。
