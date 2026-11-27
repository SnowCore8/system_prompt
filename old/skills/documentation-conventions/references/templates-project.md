# 文档模板：项目与内容

本文件为项目与内容类文档的可复制骨架；复制后应当替换示例内容；必需章节不得删除，仅可删减示例内容与说明；各章节所依据的规则
见 `dimensions-project.md`。

## README

用途：以单页为新读者建立方向，并引导其进入下一步。
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

常见错误：将 README 变为功能巡览，使首条可运行命令位于首屏之下。

## CONTRIBUTING

用途：引导新贡献者自全新克隆进入一次经过审查的变更。
必需章节：工具链、环境搭建、运行与测试、约定、审查预期。

```markdown
# Contributing

Setup: install Python 3.12 and Docker, then run `make bootstrap`.

    make run    # start the service
    make test   # run the tests

Branch as `feat/short-description` and commit as `type(scope): summary`.
Behavior changes need tests and docs; review takes two business days.
```

常见错误：仅记录顺利路径的测试命令，贡献者无法复现 CI 失败。

## GitHub issue 表单与 PR 模板

用途：在 issue 与 PR 入口收集处理请求所需的最小信息，并把安全与使用问题导向正确渠道。
必需章节：关闭空白 issue；至少一个缺陷表单；PR 模板包含验证证据、风险与回滚。

```yaml
# .github/ISSUE_TEMPLATE/bug.yml
name: Bug report
description: Report a reproducible defect
labels: ["bug"]
body:
  - type: textarea
    id: steps
    attributes:
      label: Steps to reproduce
      placeholder: "1. ...\n2. ..."
    validations:
      required: true
  - type: input
    id: version
    attributes:
      label: Version and environment
    validations:
      required: true
  - type: textarea
    id: expected
    attributes:
      label: Expected behavior
    validations:
      required: true
```

```yaml
# .github/ISSUE_TEMPLATE/config.yml
blank_issues_enabled: false
contact_links:
  - name: Usage questions
    url: https://github.com/OWNER/REPO/discussions
    about: Ask and answer usage questions
  - name: Report a vulnerability
    url: https://github.com/OWNER/REPO/security/advisories/new
    about: Report privately; do not open a public issue
```

```markdown
<!-- .github/pull_request_template.md -->
## What and why

Closes #<issue>

## Verification

Commands run and their results; screenshots for UI changes.

## Risk and rollback

Affected paths, rollout or flag plan, and the revert path.

## Checklist

- [ ] Tests cover the behavior change.
- [ ] Docs and changelog are updated.
- [ ] No secrets, debug output, or unrelated changes.
```

常见错误：表单要求用户公开漏洞细节；PR 模板只列复选框而没有验证证据与回滚。

## 架构概览

用途：向维护者说明系统的组装方式，以及接下来应当阅读的内容。
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

常见错误：复述代码所拥有的接口签名，未写明边界。

## ADR

用途：为后续维护者保留一项决策及其背景与后果。
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

常见错误：事后编辑已接受的决策，未编写取代该决策的新 ADR。

## 设计文档或 RFC

用途：使审查者在着手构建之前评判一项提议的变更。
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

常见错误：仅提出设计而未写非目标，审查者将重新提出 RFC 已经解决的范围问题。

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

常见错误：将概念写成步骤，读者照抄步骤而未掌握模型。

## 术语表

用途：为每个项目术语保留散文定义，并链接至项目命名表。
必需章节：按字母顺序的术语表、定义、命名表链接、负责人。

```markdown
# Glossary

| Term | Definition | Naming table |
|---|---|---|
| charge | One attempt to collect a payment. | `Charge` |
| invoice | A bill sent to a customer. | `Invoice` |
| settlement | The provider's payout to the merchant. | `Settlement` |

Owner: billing team. Canonical names, casing and banned synonyms live in the
project naming table; add a term here when it appears in a second document.
```

常见错误：允许每个团队保留各自的术语表，使同一术语出现两种定义。
