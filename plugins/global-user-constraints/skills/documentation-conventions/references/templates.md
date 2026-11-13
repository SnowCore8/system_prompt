# Documentation Templates

Copy the skeleton for the document type, replace the example content with the project's real content, and trim what
the page does not need. Read the matching dimension in `references/dimensions.md` for the rules behind each section.

## README

Purpose: orient a new reader in one page and route them to the next step.
Required sections: name and scope, install, quick start, configuration, documentation links, license.

```markdown
# Invoice Service

Issues invoices and reconciles payments; requires Python 3.12 and PostgreSQL 16.

    pip install invoice-service
    invoice-service init --config config/dev.toml
    invoice-service serve

The health check is `GET /healthz`. See the [tutorial](docs/tutorials/first-invoice.md) and
[configuration reference](docs/reference/configuration.md). License: Apache-2.0.
```

Common mistake: turning the README into a feature tour so the first runnable command sits below the fold.

## CONTRIBUTING

Purpose: take a new contributor from a fresh clone to a reviewed change.
Required sections: toolchain, setup, run and test, conventions, review expectations.

```markdown
# Contributing

Setup: install Python 3.12 and Docker, then run `make bootstrap`.

    make run    # start the service
    make test   # run the tests

Branch as `feat/short-description` and commit as `type(scope): summary`.
Behavior changes need tests and docs; review takes two business days.
```

Common mistake: documenting only the happy-path test command, so contributors cannot reproduce a CI failure.

## Architecture Overview

Purpose: show a maintainer how the system is put together and where to read next.
Required sections: context, components, boundaries, data flow, decisions, known limits.

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

Common mistake: restating interface signatures that the code owns instead of naming the boundaries.

## ADR

Purpose: preserve one decision, its context, and its consequences for future maintainers.
Required sections: status, date, context, decision, consequences, alternatives.

```markdown
# ADR-0007: Require idempotency keys for charge retries

Status: Accepted. Date: 2026-02-10. Context: a timeout retry can charge the same
invoice twice, and the provider cannot detect the duplicate.

Decision: every `POST /v1/charges` request requires an `Idempotency-Key`; the
API stores it for 24 hours and returns the original response.

Consequences: the key store adds one table; retries within 24 hours are safe.
Alternative: client-side deduplication, rejected because a crashed client retries.
```

Common mistake: editing the accepted decision later instead of writing a new ADR that supersedes it.

## Design Doc or RFC

Purpose: let reviewers judge a proposed change before it is built.
Required sections: problem, goals and non-goals, proposal, alternatives, risks, rollout, open questions.

```markdown
# RFC-0014: Split invoice rendering from billing

Problem: rendering changes ship with billing changes, so every release risks both.

Goal: versioned rendering without an API deploy. Non-goal: moving invoice history.

Proposal: the API emits an invoice event; a renderer consumes it and writes a PDF.
Alternative: render inside the API, rejected because it couples templates to deploys.
Risks: duplicate renders during the migration, deduped by invoice ID.
Rollout: shadow renders for two weeks, then switch. Open question: template owner.
```

Common mistake: proposing the design without the non-goals, so reviewers re-open scope the RFC had settled.

## Tutorial

Purpose: teach a learner to complete one working example from a clean start.
Required sections: outcome, prerequisites, numbered steps, result, next step.

```markdown
# Tutorial: issue your first invoice

You will create a customer, issue an invoice, and check its state in ten minutes; run `make run` first.

1. Create a customer: `invoice-service customers create --name Acme`.
2. Issue an invoice: `invoice-service invoices issue --customer cus_123
   --amount-cents 2500`.
3. Inspect it: `invoice-service invoices show inv_123`.

Result: state `open`, amount `2500` cents. Next: configuration reference.
```

Common mistake: offering branching options, which turns a guided path into a decision the reader makes alone.

## How-To Guide

Purpose: get a practitioner through one task that they already understand.
Required sections: goal, prerequisites, steps, verification, common failures.

```markdown
# How to retry a failed charge

Goal: retry a declined charge once; the invoice is `open`, the charge `failed`.

1. Find it: `invoice-service charges list --invoice inv_123`.
2. Retry it: `invoice-service charges retry ch_123`.
3. Confirm it: `invoice-service charges show ch_123`.

Verify: `invoice-service invoices show inv_123` reports `paid`.
Common failure: `409 charge_not_retryable` means it already succeeded.
```

Common mistake: explaining the concept instead of the procedure, so the reader finishes without the task.

## Reference Page

Purpose: state the exact facts a practitioner needs while working.
Required sections: synopsis, options and defaults, constraints, version notes, example.

```markdown
# `invoice-service invoices issue` reference

Issues an invoice and returns its ID. Synopsis:

    invoice-service invoices issue --customer CUSTOMER --amount-cents N

Options: `--customer` (string, required); `--amount-cents` (integer, required);
`--currency` (string, default `USD`). Version note: `--currency` is 2.3+.
Example: `invoice-service invoices issue --customer cus_123 --amount-cents 2500`.
```

Common mistake: replacing exact types and defaults with prose, so the reader must read the code to use the page.

## API Reference Page

Purpose: let an integrator call one endpoint correctly on the first attempt.
Required sections: method and path, authentication, parameters, response, errors, example.

```markdown
# POST /v1/charges

Creates a charge. Auth: bearer token in `Authorization`, scope `charges:write`.

Body: `invoice_id` (string, required), `amount_cents` (integer, required),
`idempotency_key` (string, required, unique per retry window).

Response: `201` with `id`, `state`; `409` if paid. Errors: `400 invalid_request`,
`402 charge_declined`. Example: send the idempotency header with the invoice ID.
```

Common mistake: documenting only the success path, leaving the integrator to discover error codes in production.

## Concept or Explanation

Purpose: explain the model behind the behavior before the reader performs a task.
Required sections: idea, model, vocabulary, tradeoffs, examples, links.

```markdown
# Charge states

A charge moves through `pending`, `succeeded`, and `failed`; a retry reuses the
same charge until it succeeds or the retry window ends.

The model keeps one charge per attempt and an invoice-level balance, so a failed
charge never changes the total. Tradeoff: the balance needs a reconciliation job.
Example: [retry guide](docs/guides/retry-charge.md).
```

Common mistake: writing the concept as a procedure, so the reader copies steps without learning the model.

## Runbook

Purpose: let the on-call reader resolve one alert or operation under pressure.
Required sections: trigger, impact, first action, procedure, verification, rollback, escalation.

```markdown
# Runbook: payments queue backlog

Trigger: queue depth above 10,000 for 10 minutes; charge retries are delayed.

1. Confirm the alert and post the depth in the incident channel.
2. Check workers: `kubectl -n payments get deploy/worker`.
3. Scale to six: `kubectl -n payments scale deploy/worker --replicas=6`.

Verify: depth below 1,000 for ten minutes. Rollback: scale to three. Escalation: payments on-call decides.
```

Common mistake: writing "investigate the queue" instead of the exact command and the expected output.

## Changelog Entry

Purpose: record one released set of user-visible changes.
Required sections: version and date, grouped entries, upgrade action, issue links.

```markdown
## 2.3.0 - 2026-02-10

Added: `POST /v1/charges` accepts an `Idempotency-Key` header (issue #142).

Deprecated: `GET /v1/orders` in 2.3; use `/v2`; removed in 3.0 (issue #151).

Upgrade: send `Idempotency-Key` on every charge request.
```

Common mistake: pasting commit subjects instead of user-visible changes and the action required to upgrade.

## Release Notes

Purpose: announce one release and the actions its users must take.
Required sections: version and date, upgrade action, highlights, categories, links.

```markdown
# Release 2.3.0

Released 2026-02-10.

Upgrade: send `Idempotency-Key` on every `POST /v1/charges` call.
Highlights: retries are safe by default. Fixed: totals no longer round half-cent
amounts down. Full categories and links: [changelog](CHANGELOG.md).
```

Common mistake: repeating every changelog entry so the reader cannot see which changes need action.

## Migration Guide

Purpose: move an existing user from the old behavior to the new one without data loss.
Required sections: affected audience, timeline, field mapping, steps, verification, rollback.

```markdown
# Migrate from `amount` to `amount_cents`

Audience: charge integrators. `amount_cents` is an integer; `currency` is required.

Timeline: 2.3 accepts both fields; 3.0 rejects `amount` with `400 amount_removed`.
Mapping: `amount: 25.00` becomes `amount_cents: 2500` plus `currency: "USD"`.

Steps: back up the table; fill `amount_cents`; deploy both fields; verify 100
invoices; drop `amount` after 3.0. Rollback: restore the backup.
```

Common mistake: publishing the mapping without a backup and a rollback step for the data rewrite.

## Deprecation Notice

Purpose: tell users that a path is ending, what replaces it, and when.
Required sections: deprecated item, versions, replacement, reason, migration link.

```markdown
# Deprecated: `GET /v1/orders`

Deprecated in 2.3; removed in 3.0. Replacement: `GET /v2/orders`.

Why: `v1` returns orders without line items and cannot paginate. Migration:
the [migration guide](docs/migrations/orders-v2.md) maps every `v1` field.
```

Common mistake: naming the removal release but not the replacement, so users cannot plan the change.

## Troubleshooting Entry

Purpose: help a stuck reader turn one observable symptom into a fix.
Required sections: symptom, cause, fix, prevention, related links.

```markdown
## `charge_declined` on a valid card

Symptom: `POST /v1/charges` returns `402 charge_declined`.

Cause: the provider declined the risk check. Fix: log the `decline_code` and
ask for a different card. Prevention: validate with a zero-value authorization.
Related: [charge states](docs/concepts/charge-states.md).
```

Common mistake: organizing entries by internal cause, so readers cannot find the entry from the error they see.

## Security, Legal, and Support

Purpose: state what is supported, how to report a problem, and who owns the page.
Required sections: supported versions, reporting channel, response time, support scope, owner, review date.

```markdown
# Security and Support Policy

Supported versions: 2.x receives security fixes; 1.x is end-of-life.

Report a vulnerability through the private channel in `SUPPORT.md`; we
acknowledge reports within two business days and publish a timeline.

Owner: security team. Last reviewed: 2026-02-10. Legal and support terms: [SUPPORT.md](SUPPORT.md).
```

Common mistake: publishing a reporting address that no one monitors, so reporters give up or go public.

## Postmortem

Purpose: explain one incident, its impact, and the actions that prevent a repeat.
Required sections: summary, impact, timeline, root cause, detection, actions, owners.

```markdown
# Postmortem: duplicate charges on 2026-02-03

Summary: a retry storm charged 214 invoices twice over six hours. Impact:
customers were double-charged; refunds finished the same day.

Timeline: queue backed up at 02:10; the alert fired at 02:40; the fix shipped
at 08:05. Root cause: retries had no idempotency key. Detection: queue depth
alert. Actions: add idempotency keys (owner: payments); add a duplicate-charge
alert (owner: platform).
```

Common mistake: writing the postmortem as blame, so readers hide details instead of improving detection.

## Glossary

Purpose: fix one meaning and one spelling for every project term.
Required sections: alphabetical term table, definitions, banned synonyms, owner.

```markdown
# Glossary

| Term | Definition | Avoid |
|---|---|---|
| charge | One attempt to collect a payment. | payment item |
| invoice | A bill sent to a customer. | bill |
| settlement | The provider's payout to the merchant. | payout |

Owner: billing team. Add a term when it appears in a second document.
```

Common mistake: letting each team keep its own glossary, which produces two definitions of the same term.

## Documentation Index or Map

Purpose: route every reader to the page that answers their question.
Required sections: start-here links, sections by doc type, ownership or feedback path.

```markdown
# Invoice Service documentation

Start here: [tutorial](docs/tutorials/first-invoice.md), [contributing](CONTRIBUTING.md).

Guides: [retry a failed charge](docs/guides/retry-charge.md).
Reference: [configuration](docs/reference/configuration.md).
Operations: [payments queue backlog](docs/runbooks/payments-queue.md).
Feedback: [support](SUPPORT.md).
```

Common mistake: leaving a new page out of the index, so it is reachable only by direct link and slowly rots.
