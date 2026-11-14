# API and Data Checklists

Use this file with `SKILL.md` during review, rollout, and cleanup. Each checklist applies at the moment named in its
heading: the design list before a contract change is approved, the playbook while a migration runs, the retention
worksheet when a dataset is created rather than when someone asks for deletion. An item that does not apply gets a
short reason instead of a check; an unchecked item is an open risk, not a formality.

## API Design Review Checklist

Run this list against the contract diff itself, not against memory of what the service is supposed to do.

- [ ] The operation, request, response, errors, and events are defined in the IDL, and the implementation matches the
  IDL in a CI check.
- [ ] Every consumer is listed: mobile clients, partner integrations, internal services, dashboards, reports,
  exports, and analytics jobs that read the old shape.
- [ ] The change is declared additive or breaking, with the version or compatibility policy that supports the
  declaration.
- [ ] A breaking change has a version boundary, a replacement, a deprecation window, and a usage measurement that can
  prove when removal is safe.
- [ ] Field presence and nullability are explicit: optional means absent is valid, and null is a documented state
  rather than an accident.
- [ ] Enums state how unknown values are handled, and clients are expected to tolerate values added later.
- [ ] Every error uses a stable code, the correct status family, a safe message, and structured details.
- [ ] Validation details name the field path and the violated rule, not a database column or an internal exception
  message.
- [ ] Collection endpoints enforce a maximum page size, a deterministic sort with a unique tiebreaker, and one
  pagination style.
- [ ] Filters and sorts are allowlisted, validated, and indexed, or the contract records the accepted cost of not
  indexing them.
- [ ] Retryable writes accept an idempotency key, and replay plus key-reuse behavior is covered by a test.
- [ ] Rate limits and quotas are documented, return limit headers and 429 with `Retry-After`, and budget per tenant
  and per principal.
- [ ] Authorization is object-level, and tenant, owner, and subject IDs come from the verified token rather than the
  request payload.
- [ ] The existence policy for 403 versus 404 is consistent across resources and tested for a caller who lacks
  access.
- [ ] A long operation returns 202 with a status resource, terminal states, and a documented retry or cancel path.
- [ ] Events and webhooks carry a type, schema version, event ID, timestamp, and signature, and consumers are
  replay-safe.
- [ ] The synchronous path fits the caller's timeout, or the contract states the timeout and the asynchronous
  alternative.
- [ ] The versioning decision is recorded, and a new version exists only for a breaking change that was proved
  breaking.
- [ ] The support window and sunset dates are recorded in the contract, not only in a planning document.
- [ ] The API reference, examples, changelog, and error catalogue are updated in the same change.
- [ ] Contract tests run the previous client version against the new schema, and both current versions during a dual
  run.
- [ ] A failed deploy has a rollback or forward-fix path that accounts for clients that cached the old schema or
  response.

## Error Model

Use one envelope for every error. The HTTP status carries the family, the code carries the exact cause, and the
client chooses behavior from the code rather than from the message text.

| Code family | HTTP status | Retryable | Example |
|---|---|---|---|
| validation | 400 | No | `validation.invalid_field`: a field is missing, malformed, or out of range. |
| authentication | 401 | No | `auth.unauthenticated`: the credential is missing, expired, or invalid. |
| authorization | 403 | No | `auth.forbidden`: the caller is known but lacks the permission. |
| not found or hidden | 404 | No | `resource.not_found`: the resource does not exist or is hidden from this caller. |
| conflict | 409 | No | `conflict.version_mismatch`: the resource changed since the caller read it. |
| semantic | 422 | No | `order.not_cancellable`: the request is well formed but the state forbids it. |
| rate limit | 429 | Yes, after `Retry-After` | `rate_limit.exceeded`: a budget or quota is exhausted. |
| dependency | 502 or 503 | Yes, with backoff | `dependency.unavailable`: an upstream dependency is failing. |
| internal | 500 | Only with an idempotency key | `internal.unexpected`: an unhandled failure; include the request ID only. |

- `code` is stable, unique, documented, and never reused for a different cause; adding one is compatible, renaming
  or removing one is a breaking change.
- `message` is safe to show to a user or an operator, is never parsed, and may be localized outside the contract
  boundary; an error message never contains a secret, a token, a stack trace, or personal data.
- `details` is a list of structured objects with a field path, a rule identifier, and the rejected value only when
  echoing it is safe; do not flatten details into the message.
- Every error response carries a request identifier in the body and in a response header, so support can correlate a
  report with logs without asking the caller for more.
- Retryable families include `Retry-After` or a retry hint, and a 500 is retryable only when the request is
  idempotent under its key.
- The same envelope is returned by the application, the gateway, and the validation layer; an empty body with a 500
  is a contract violation.

## Pagination, Idempotency, and Versioning Decisions

Record one decision per row in the contract before implementation. The default stands until measured need overrides
it, and every endpoint in one API uses the same choice for the same row.

| Decision | Default | Choose otherwise when | Contract obligation |
|---|---|---|---|
| Pagination style | Cursor | Small, stable sets where users jump to a page number | Next cursor, stable sort, maximum page size |
| Page size | Fixed default and hard maximum | Report or export flows need larger pages | Default, maximum, and the error for exceeding it |
| Total count | Omitted | A user interface needs an exact count and accepts the cost | Accuracy guarantee and maximum latency |
| Filter grammar | Repeated query parameters | Deep compound queries are a real product requirement | Allowed fields, operators, value formats, unknown-parameter policy |
| Sort | Documented default plus a unique tiebreaker | A caller needs a different order | Allowed fields, direction, stability guarantee |
| Idempotency window | 24 hours for client-retried writes | Batch jobs or partners need a longer replay window | TTL, key scope, fingerprint-mismatch behavior |
| Versioning | Additive evolution inside one major version | A breaking change is approved for external callers | Major boundary, support window, migration guide |
| Deprecation window | At least 90 days for external clients, one major release for internal ones | A security or legal fix requires immediate removal | Sunset date, replacement, headers, usage threshold |
| Sync versus async | Synchronous when the work fits the request budget | Work exceeds the timeout or must survive a connection loss | 202 shape, status states, polling or webhook |
| Rate-limit scope | Per tenant and per principal | One workflow needs its own budget | Limits, headers, 429 body, `Retry-After` |

- Record each decision in the contract or its ADR; a decision that lives only in a reviewer's head is re-litigated on
  the next change.
- Revisit a decision when measurements change, and state the condition that would reopen it instead of leaving the
  question open.
- Consistency beats local optimization: an endpoint that paginates differently from its siblings is a new decision
  for the whole API, not a shortcut for one route.

## Expand-Contract Migration Playbook

Apply this playbook to any schema change that old code can observe. Never collapse the phases into one deploy, even
when the table is small today; the discipline is the plan for the day the table is large.

| Phase | Action | Rollback | Verification |
|---|---|---|---|
| Prepare | Count affected rows, estimate duration and lock, confirm backup and point-in-time recovery, choose a quiet window, get approval. | None yet; abort before the first write. | Counts and estimate match the plan; owner and window agreed. |
| Expand | Add the nullable column or table, or build the index concurrently; nothing reads or writes it yet. | Drop the new object; it is unused. | Old code and old queries are unaffected. |
| Dual-write | Deploy code that writes both forms and reads the old one. | Redeploy the previous release. | New rows populate both forms; error rate and latency unchanged. |
| Backfill | Run the batched, idempotent backfill with throttling and a saved cursor. | Stop the job; old form still serves reads. | Row coverage complete, mismatch count zero, replication lag recovered. |
| Validate | Reconcile mismatches, validate the constraint, then add NOT NULL or the unique index. | Drop the constraint; keep the nullable column. | Zero violating rows; constraint valid; old code still works. |
| Switch reads | Deploy code that reads the new form and keeps writing both. | Redeploy the code that reads the old form. | Parity checks, error rate, and latency are within bounds. |
| Contract | Stop writing the old form, then drop the old object after the deprecation window. | Restore from backup only; this phase needs the approval gate. | No references remain; row counts and docs are updated. |

### Pre-Flight

- Count the affected rows and record the count; a migration that starts without a number cannot be verified.
- Estimate the duration and the lock on production-sized data, and state which writes the lock blocks.
- Confirm a backup or point-in-time-recovery point exists and a restore was tested, not merely configured.
- Choose the window, the timezone, the owner, and the on-call contact before scheduling the migration.
- Define the stop condition: the error, lag, or lock-wait threshold that aborts the run.

### Rollback

- Phases up to and including the read switch are reversible by redeploying the previous code; keep the old column
  and the old read path until the deprecation window closes.
- The contract phase is irreversible: it needs a verified backup or point-in-time-recovery point and the approval
  gate before the drop.
- Prefer a forward fix over an inverse migration, because down scripts are rarely exercised against real data.
- Stop a backfill rather than reversing it; an idempotent batch can resume from its cursor.
- Rehearse the rollback on a staging clone before the production run.
- After new code has written data, rolling back code is safe only when both forms were kept consistent.

### Verification

- Compare row counts and checksums before and after, per phase rather than only at the end.
- Read the same rows through the old and the new path and compare results for a sample and for known edge cases.
- Run the violating-row queries for every new constraint; a valid constraint does not prove the data is correct.
- Check replication lag, lock waits, error rate, and latency after the run, not only during it.
- Re-run the query plans for the hot queries; a new index or column can change a plan in either direction.

## Destructive-Change Approval Checklist

A destructive change drops, truncates, renames, narrows, or overwrites live data. Confirm every item in writing before
execution; a verbal approval does not cover a later, larger version of the change.

- [ ] The change is named: which object, in which environment, and what exactly disappears.
- [ ] Data loss is quantified: rows, size, and the values that cannot be reconstructed from another source.
- [ ] A backup or point-in-time-recovery point exists, and a restore from it was tested recently.
- [ ] The consumer list is complete: no live service, report, export, or analytics job still reads the object.
- [ ] The person with authority approved this exact operation, not a general cleanup effort.
- [ ] A deprecation window has passed, or a security or legal need justifies skipping it.
- [ ] The execution window, timezone, and on-call owner are agreed and the team is notified.
- [ ] A dry run reported the affected rows and the number matched the expectation.
- [ ] The script or migration is idempotent, or guarded by a precondition that fails closed.
- [ ] The stop condition is explicit: which error, lag, or duration aborts the run.
- [ ] The post-change verification query was written in advance and is run immediately after.
- [ ] Rollback is possible and tested for the code and schema, or the loss is accepted as irreversible in writing.
- [ ] Derived copies are handled: search, cache, warehouse, exports, and logs.
- [ ] Backups and their expiry were considered, and the deletion window is stated correctly.
- [ ] The operator, time, counts, and outcome are logged in the system of record.
- [ ] The dropped definition and counts are recorded in the approved request for a future reconstruction attempt.

## Data Retention Worksheet

Fill one row per dataset when the dataset is created and review the table yearly. The class and the period come from
the security data inventory; this worksheet records where they are enforced and how deletion happens. Retention
starts at the trigger, not at table creation, and an empty cell is an open risk.

| Data class | Location | Retention | Deletion mechanism | Owner |
|---|---|---|---|---|
| Public | Published content in the CMS and CDN | Until unpublish plus 30 days | Delete the row and purge the cache | Content team |
| Internal | Service configuration and telemetry in the primary database | 13 months rolling | Scheduled partition drop | Service owner |
| Confidential | Contracts and billing records in the primary database and warehouse | 7 years after contract end | Purge job per contract ID | Finance systems |
| Restricted | Customer profile in the primary database, search index, and cache | Account closure plus 30 days | Erasure job fans out to all stores | Identity team |
| Restricted | Support attachments in object storage | Ticket closure plus 90 days | Object delete plus receipt check | Support systems |

- The class and the period are copied from the inventory; never invent either, and never default to forever.
- The trigger names the event that starts the clock, such as an account closure or a last activity date.
- The deletion mechanism names the job, API, or policy that removes the data, not the intention to remove it.
- The owner is a team or role that can answer for the row during an audit; a shared owner means no owner.
- A legal hold set by the security or legal role suspends the row's schedule; record its scope, authority, and
  review date and lift it only on that role's direction.
- Every row is tested once: run the deletion mechanism on a sample and verify that the copy is gone from the store.

### Copy and Store Map

Deletion reaches the row only after it reaches every copy. The canonical copy and store map is in
`references/dimensions.md` section 3; use it for the per-store list and record the dataset-level rows above.

## Test-Data Rules

Fixture isolation, deterministic seed data, and credential scoping belong to the testing-and-quality-conventions
role. This list covers only what test data must never contain or become, and how it is retired.

- Generate synthetic data for tests, and never restore a production dump into a development, test, or staging store.
- When production data must leave production for debugging, mask it irreversibly, limit the extract, and delete it
  when the investigation closes.
- Build the test schema by running the migration history from empty, and also test the upgrade from the previous
  release; an ORM-generated schema hides migration defects.
- Fixtures contain no real email addresses, phone numbers, secrets, or internal addresses; reserved names such as
  `example.test.invalid` keep the rule visible.
- Non-production stores get a short retention and a scheduled reset, so stale personal data cannot accumulate.
- Snapshot and golden files are reviewed for personal data before they are committed, because they are copies too.
- Deletion and retention jobs are tested like any other code: a fixture and an assertion for each store the job is
  supposed to clear.
