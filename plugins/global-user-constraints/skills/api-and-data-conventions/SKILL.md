---
name: api-and-data-conventions
description: Defines, reviews, and repairs API contracts and database/data-lifecycle practice across services, including resource and error design, pagination, idempotency, authorization boundaries, versioning, migrations, and retention. Use when adding or changing an endpoint, event, field, table, index, constraint, or deletion path, or when planning a breaking change or zero-downtime schema rollout.
argument-hint: '[path or scope]'
---

# API and Data Conventions

API contracts and database schemas are the interfaces with the longest lifetime in a system: outside callers build
against them, and the data behind them accumulates for years. A changed field breaks clients the author cannot see;
a dropped column, an unbatched migration, or a lock that queues every writer loses data or causes an outage; none of
these is repaired by reverting the code. This skill defines how to design, review, and change API contracts, how to
evolve databases without downtime, and how to retire data through its whole lifecycle. It serves the author of a new
endpoint or migration, the reviewer judging a schema diff, and the engineer planning a deprecation or an erasure path.

## Scope and Precedence

Apply the first rule that fits, and do not mix standards inside one scope:

1. Mandatory protocol, platform, or legal rule. HTTP semantics, the IDL in use (OpenAPI, protobuf, GraphQL), the
   database engine's behavior, and data-protection obligations are not optional.
2. Existing contract, schema, and published compatibility policy. Read the current API version, the migration
   tooling, the error catalogue, and the project's stated support window before inventing a rule.
3. This standard's defaults, when the two levels above are silent.
4. Personal preference, which never overrides the three levels above.

- **Names belong to the naming-conventions role.** It owns resource, field, table, column, index, and enum names;
  this skill owns the contract and process around them, and does not rename what that role governs. When a contract
  change needs a new name, ask that role for it rather than inventing a second vocabulary.
- **Standalone documentation belongs to the documentation-conventions role.** It owns API reference pages and other
  pages; this skill owns the design rules those pages describe, and the pages are updated with the contract. The
  design is reviewed here; the page is reviewed there.
- **Release operations belong to the release-operations-conventions role.** It owns product versioning, release
  process, and CI/CD; this skill owns API versioning policy inside the contract. It also owns incidents and backups;
  this skill owns destructive schema-change safety.
- **Test strategy belongs to the testing-and-quality-conventions role.** It owns test strategy and gates; this skill
  owns contract tests as a requirement, not the tooling that runs them. A contract test that nobody runs during a
  release is a comment.
- **Privacy policy belongs to the security-compliance-conventions role.** It owns privacy policy, the data
  inventory with PII classification and retention periods, and license; this skill consumes that inventory and owns
  enforcement: schema metadata, deletion propagation, backup expiry, and test-data handling.
- **Generated and third-party surfaces are exempt.** Generated clients and servers, vendored schemas, and external
  APIs keep their shape; isolate them behind an adapter, map them to the canonical contract at the boundary, and
  regenerate rather than hand-edit.
- **A contract change is a breaking change unless proven otherwise.** Proof is a consumer inventory plus a contract
  test against real clients; missing evidence that a field is used is not evidence that it is unused.
- **When two rules conflict, state the conflict and the chosen rule.** Record the decision in the contract or an ADR
  so the next change follows it instead of re-arguing the same question.

## Process

1. Identify the contract surface and the data touched: operations, request and response fields, events, tables,
   columns, indexes, and derived stores. Map every consumer, including mobile clients, partners, dashboards, exports,
   and analytics jobs that depend on the current shape. When the inventory is incomplete, finish it before proposing
   the change; an unlisted consumer is a future outage.
2. Check the current version and compatibility policy: the published version, the recorded support window, the
   deprecation state of neighboring fields, and the migration history that produced the current schema.
3. Choose additive or breaking: make the change in two deployable steps when the contract allows it, and introduce a
   version boundary only for a proven break. Prefer expansion plus a deprecation window over a simultaneous cutover.
   If you cannot describe the two-step path, the change is not ready.
4. Write the migration and rollout plan with rollback: schema phases, backfill batches, deploy order, feature-flag
   state, verification queries, and the forward-fix or restore path for each step. The plan names who executes, who
   watches, and who can stop it.
5. Verify against real clients and data: run contract tests with the previous client version, plan the statements on
   production-sized data, replay a sample of real requests, and confirm that old clients still work during the dual
   run. If a client cannot be tested, record it as an unverified compatibility risk instead of assuming that it
   tolerates the change.
6. Update docs and examples: the IDL, the error catalogue, API reference handoff, migration guide, changelog, and code
   samples; a contract change without its examples is incomplete. The migration guide addresses the caller's change,
   not the implementer's.
7. Review: run the checklists in `references/checklists.md`, obtain the required reviewers, record approval for
   destructive and breaking changes, and confirm the rollback path was tested rather than assumed. A review that
   approves a breaking change without usage evidence is incomplete.

## Core Rules

- **The published contract is the source of truth.** The IDL, schema, and error catalogue are reviewed like code; an
  implementation that disagrees with them is a defect fixed in the same change, never documented as an exception. A
  stale generated artifact is regenerated, not patched by hand.
- **Additive by default; breaking by decision.** Add optional fields, operations, and error codes freely; remove,
  rename, retype, or newly require something only behind a version boundary, a deprecation window, and measured
  usage. A deprecated field stays supported, documented, and tested until its removal date.
- **A contract change includes its consumers.** Update clients, generated SDKs, contract tests, examples, and docs in
  the same delivery; an old client that still works is tested, not assumed.
- **Machines read codes; humans read messages.** Keep error codes stable, unique, and permanent; keep messages safe
  and changeable; put field-level detail in structured details, never in a string a client parses. The error catalogue
  is a release artifact and grows by addition.
- **Every retried write has an idempotency contract.** Key scope, stored response, TTL, and replay behavior are
  specified and tested; never rely on clients not retrying.
- **Collections are bounded, ordered, and repeatable.** Enforce a maximum page size, a deterministic sort, one
  pagination style, allowlisted filters, and no unbounded export on the request path.
- **Authorization is checked per object, not per route.** Tenant and owner come from the verified token; 401, 403, and
  404 follow one documented existence policy. An endpoint that returns data before checking the object is a data leak
  with a test suite.
- **Long work and event delivery are designed, not improvised.** Long operations return 202 with a status resource;
  events are at least once, carry an ID and a schema version, and have dedupe, signature, retry, dead-letter, and
  replay paths.
- **Version and deprecate deliberately.** Version at the boundary that changes: a major path segment for public APIs,
  additive evolution for coordinated internal IDLs, a media type only when every hop preserves it. Deprecate with a
  replacement, `Deprecation` and `Sunset` headers, a migration guide, and per-caller usage measurement.
- **Schema changes expand, then contract.** Add the new structure, dual-write, backfill, validate, switch reads, then
  remove the old structure. Phases up to the read switch are code-reversible; the final drop is irreversible and
  needs a verified backup or point-in-time-recovery point plus the approval gate. A change that cannot complete
  inside the support window is split until it can.
- **Estimate the lock before executing DDL.** Name the lock, set timeouts, measure on production-sized data, run the
  migration as an explicit step in a quiet window, and watch replication lag and lock waits while it runs.
- **Destructive data changes need approval, a backup, and verification.** A migration or backfill is a production
  write: explicit consent, a consumer list, a recovery point, a dry run with counts, and a post-change query.
- **Every dataset has a class, a retention rule, and an owner.** Deletion propagates to every copy; soft delete is
  retention rather than deletion; backups, logs, and exports are copies with their own expiry and deletion path.
- **Test from migrations, with synthetic data.** Test databases are built from the migration history and upgraded
  from the previous release; production data never enters a non-production store unmasked.

## Change Risk Matrix

| Change | Compatibility | Required path | Verification |
|---|---|---|---|
| Add an optional response field | Compatible | Add it to the IDL and release the server before the clients | The previous client passes the contract test |
| Add an optional request field with a default | Compatible | Document the default and accept the field's absence | Old client payload test without the field |
| Add a required request field | Breaking | New version, or an optional window with a default until callers migrate | Consumer inventory and a dual-run test |
| Rename a field or endpoint | Breaking | New name beside an alias, dual-write and dual-read, deprecate the old | Usage reaches zero on the old name before removal |
| Remove a field or endpoint | Breaking | Deprecation window, sunset date, replacement, and usage proof | Client tests and per-caller telemetry |
| Change a field type or format | Breaking | New field beside the old, or a new major version | Round-trip test and consumer test |
| Add an enum value | Breaking for closed clients | New version, or a documented tolerant-client requirement | Test a client build that predates the value |
| Change the default page size or sort | Behavioral break | Announce and version it, or keep the old behavior behind a parameter | Client assertion on order and page contents |
| Add a nullable column | Compatible | Expansion phase only: add it, dual-write, backfill later | Migration on production-sized data; old code check |
| Add NOT NULL, UNIQUE, or foreign key | Blocking if data is dirty | Clean the data, add unvalidated, validate in a separate step | Violating-row query and lock estimate |
| Drop a column or table | Breaking and destructive | Stop readers, wait out deprecation, back up, obtain approval | No references remain; counts; a restore test |
| Backfill or build an index on a hot table | Operational risk | Batch with a throttle or build concurrently, outside peak hours | Replication lag, lock waits, total duration |

## Dimension Index

| Dimension | First rule | Detail |
|---|---|---|
| 1. API design | Define the contract before code; change it additively unless a version boundary is approved. | Section 1 in `references/dimensions.md` |
| 2. Database and schema change | Expand, backfill, validate, contract; estimate the lock before executing. | Section 2 in `references/dimensions.md` |
| 3. Data retention and lifecycle | Apply the data inventory at field level, enforce its periods, delete through every copy. | Section 3 in `references/dimensions.md` |

## Anti-Patterns

| Anti-pattern | Why it fails | Fix |
|---|---|---|
| Expose the storage model as the API | Callers couple to tables and every migration becomes an API break. | Design the wire contract and map it at the boundary. |
| Error message as the only signal | Clients string-match text or break when a message changes. | Stable code plus structured details. |
| Offset pagination on a changing collection | Pages skip and duplicate rows as data shifts underneath. | Cursor pagination with a deterministic sort. |
| "Clients should retry" without keys | A retried POST duplicates orders or charges. | Idempotency key with a stored response. |
| 200 with an error body | Gateways, caches, and client libraries treat it as success. | The correct 4xx or 5xx status. |
| 429 without `Retry-After` | Clients hammer the service and make throttling worse. | 429 with limit headers and `Retry-After`. |
| 403 for every failure | Clients cannot tell re-authenticate from stop, and debugging slows. | 401 unauthenticated, 403 denied, 404 when existence is hidden. |
| "We will version later" | Compatibility debt compounds while clients multiply. | Set the versioning policy before the first external consumer. |
| Silent enum extension | Exhaustive clients crash or mis-handle the new value. | Version it or document the tolerant-client requirement. |
| A large ALTER inside the deploy pipeline | A lock wait queues every writer behind it. | Explicit migration step, `lock_timeout`, concurrent index builds. |
| Editing an applied migration | Environments diverge and history no longer explains the schema. | Add a follow-up migration. |
| One UPDATE as the backfill | Long transaction, bloat, replication lag, and blocked writes. | Batched keyset backfill with a throttle. |
| A production dump in staging | Personal data spreads to every machine and backup. | Synthetic or irreversibly masked data. |
| A delete that only sets a flag | Data and personal records live forever under another name. | Purge job, filtered reads, and a retention rule. |
| "We might need it" retention | Data kept indefinitely with no owner or legal basis. | Class, period, trigger, owner, and a yearly review. |
| Rate limits as concurrency control | Legitimate retries fail while correctness depends on luck. | Idempotency, reservations, or a queue. |

## Review Checklist

- [ ] The contract change is in the IDL, and the implementation matches it in a CI check.
- [ ] Every affected consumer is listed, including clients outside this repository.
- [ ] Additive or breaking is declared with the compatibility policy; a breaking change has a version boundary, a
  deprecation window, a migration guide, and a recorded support window.
- [ ] New errors use a stable code, the correct status family, and structured details.
- [ ] Collections are bounded, deterministically ordered, and use one pagination style.
- [ ] Filters and sorts are allowlisted and indexed, or the accepted cost is recorded.
- [ ] Retryable writes have an idempotency contract and a replay test.
- [ ] Rate limits and quotas are documented with headers, 429, and `Retry-After`.
- [ ] Authorization is object-level, tenant IDs come from the token, and the 404/403 policy is consistent.
- [ ] Long operations and events define status states, delivery guarantees, dedupe, and replay behavior.
- [ ] The migration follows expand-contract and every phase is independently deployable.
- [ ] Backfills are batched, idempotent, restartable, and throttled.
- [ ] Lock impact and duration were measured on production-sized data.
- [ ] Constraints validate only after the data satisfies them.
- [ ] Destructive changes have approval, a consumer list, a backup, and a verification query.
- [ ] Every new field, table, and collection has a class, a retention period, and a deletion path.
- [ ] Deletion propagates to search, cache, analytics, logs, and backups; soft deletes have a purge job.
- [ ] Test data is synthetic, and the test schema is built from the migration history.
- [ ] Docs, examples, changelog, and the error catalogue are updated in the same change.
- [ ] The change has a rollback or forward-fix path, or a verified restore path for an irreversible drop.

## Examples

<example>
Add an optional `tracking_number` to the order response: add it to the IDL, release the server before the clients,
and run the previous client version against the new schema. No version boundary is needed because absence remains a
valid state. Verify both directions: old client without the field, new client with it.
</example>

<example>
Rename `customer_email` to `email`: add `email` beside the old field, populate both, switch readers, publish a
deprecation with a sunset date, and measure per-caller usage. Drop the old field only after usage reaches zero, with
the removal announced one release ahead.
</example>

<example>
Add a required `tenant_id` to a large orders table: add it nullable, deploy dual-write code, backfill in keyset
batches with `lock_timeout` set, validate a `NOT VALID` constraint, then enforce NOT NULL. Each step is a separate
deploy with its own rollback, and the backfill duration is measured on production-sized data first.
</example>

<example>
Handle an erasure request: delete or anonymize rows in the primary store, remove documents from the search index,
invalidate cache keys, queue warehouse and log purge jobs, and record the backup expiry date that ends the process.
Verify per store, not only in the database.
</example>

<example>
Change the `status` query parameter to a required filter in v2: publish `/v2/orders`, keep `/v1` served for the
recorded support window, publish the migration guide, and return `Deprecation` and `Sunset` headers on v1. Remove v1
only when every caller has migrated or the sunset date arrives. Both versions write the same records; only the
contract differs.
</example>

## References

Read [references/dimensions.md](references/dimensions.md) for the rules, edge cases, and examples behind the three
dimensions; read it before designing a new contract, planning a schema change, or reviewing a retention and deletion
design.

Read [references/checklists.md](references/checklists.md) for the API review list, error model, decision tables,
expand-contract playbook, destructive-change approval, retention worksheet, and test-data rules; read it during review
and rollout.
