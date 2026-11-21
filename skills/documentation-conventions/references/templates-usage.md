# 文档模板：读者与使用

本文件为读者与使用类文档的可复制骨架；复制后应当替换示例内容，并删减页面不需要的部分；各章节所依据的规则
见 `dimensions-usage.md`。

## 教程

用途：指导学习者自干净起点完成一个可工作的示例。
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

常见错误：提供分支选项，将引导路径转化为读者自行作出的决定。

## 操作指南

用途：使实践者完成一项其已经理解的任务。
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

常见错误：解释概念而非步骤，读者阅读完毕仍未完成任务。

## 参考页

用途：陈述实践者在工作中所需的精确事实。
必需章节：概要、选项与默认值、约束、版本说明、示例。

```markdown
# `invoice-service invoices issue` reference

Issues an invoice and returns its ID. Synopsis:

    invoice-service invoices issue --customer CUSTOMER --amount-cents N

Options: `--customer` (string, required); `--amount-cents` (integer, required);
`--currency` (string, default `USD`). Version note: `--currency` is 2.3+.
Example: `invoice-service invoices issue --customer cus_123 --amount-cents 2500`.
```

常见错误：以散文替换精确类型与默认值，读者必须阅读代码方可使用该页面。

## API 参考页

用途：使集成者首次即可正确调用某一端点。
必需章节：方法与路径、认证、参数、响应、错误、示例。

```markdown
# POST /v1/charges

Creates a charge. Auth: bearer token in `Authorization`, scope `charges:write`.

Body: `invoice_id` (string, required), `amount_cents` (integer, required),
`idempotency_key` (string, required, unique per retry window).

Response: `201` with `id`, `state`; `409` if paid. Errors: `400 invalid_request`,
`402 charge_declined`. Example: send the idempotency header with the invoice ID.
```

常见错误：仅记录成功路径，使集成者在生产环境中发现错误码。

## 故障排查条目

用途：帮助受阻读者将可观察症状转化为修复方案。
必需章节：症状、原因、修复、预防、相关链接。

```markdown
## `charge_declined` on a valid card

Symptom: `POST /v1/charges` returns `402 charge_declined`.

Cause: the provider declined the risk check. Fix: log the `decline_code` and
ask for a different card. Prevention: validate with a zero-value authorization.
Related: [charge states](docs/concepts/charge-states.md).
```

常见错误：依内部原因组织条目，读者无法自所见的错误找到对应条目。

## 文档索引或地图

用途：将每位读者引导至回答其问题的页面。
必需章节：从这里开始的链接、按文档类型划分的章节、归属或反馈路径。

```markdown
# Invoice Service documentation

Start here: [tutorial](docs/tutorials/first-invoice.md), [contributing](CONTRIBUTING.md).

Guides: [retry a failed charge](docs/guides/retry-charge.md).
Reference: [configuration](docs/reference/configuration.md).
Operations: [payments queue backlog](docs/runbooks/payments-queue.md).
Feedback: [support](SUPPORT.md).
```

常见错误：新页面未列入索引，仅能通过直接链接到达，并逐渐失效。
