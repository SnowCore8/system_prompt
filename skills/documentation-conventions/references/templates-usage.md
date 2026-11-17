# 文档模板：读者与使用

本文件是读者与使用类文档的可复制骨架；复制后替换示例内容并删减页面不需要的部分，各章节背后的规则见 `dimensions-usage.md`。

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
