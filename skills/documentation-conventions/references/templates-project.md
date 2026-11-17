# 文档模板：项目与内容

本文件是项目与内容类文档的可复制骨架；复制后替换示例内容并删减页面不需要的部分，各章节背后的规则见 `dimensions-project.md`。

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
