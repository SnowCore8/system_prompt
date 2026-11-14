# API and Data Dimensions

Use this file with `SKILL.md`. Each section gives the rules, edge cases, and failure modes for one dimension. When a
project already has a contract, schema, or compatibility policy, read it first and apply the higher-precedence rule;
this file supplies the default and the reasoning. Section numbers match the dimension index in `SKILL.md`. Names of
resources, fields, tables, columns, indexes, and enum members come from the naming-conventions role; this file decides
what must exist, how it behaves, and how it changes.

## 1. API Design

The contract is the part of the service that code outside the repository can see, so it has the longest lifetime and
the slowest change cycle. Design it for the callers still on the previous version, not for the client being written
today.

- **Define the contract before the implementation.** Commit the machine-readable definition (OpenAPI, protobuf,
  GraphQL SDL, JSON Schema, or the equivalent IDL) with the service, and review its diff as the API change. Generate
  or validate server implementations and client stubs from it in CI; a schema generated from annotations after the
  fact is a description, not a contract. A hand edit that bypasses the IDL is drift, fixed in the same change rather
  than in a later cleanup. When a behavior cannot be expressed in the IDL (semantic constraints, conditional
  presence), record it in prose in the contract document and test it explicitly.
- **Model operations, not storage.** Path shape, resource names, HTTP method choice, and path-parameter casing
  follow the naming-conventions role; this dimension decides the request and response semantics. PUT replaces the
  whole representation and is idempotent; PATCH states its merge semantics (JSON Merge Patch or JSON Patch); batch
  endpoints define a per-item partial-failure result. Never expose an ORM entity, an internal join table, or a
  storage nullability quirk directly. Member and collection endpoints stay symmetric: the same operation returns the
  same shape whether the item is fetched alone or inside a list.
- **Make the error response a stable public type.** Every error carries a machine-readable `code`, a human-readable
  `message` safe to show, structured `details`, and a request identifier. Codes are unique and permanent: adding a
  code is compatible, changing its meaning or deleting it is not. Messages are for operators and end users, may
  change, and are never parsed by clients; the HTTP status carries the broad family. Validation details name the
  field path and the violated rule. Never put a stack trace, SQL fragment, secret, or personal data in an error.
  Return the same envelope for gateway and validation failures too, and expose the request identifier as a response
  header so a support ticket can be traced without the client body.
- **Fix collection behavior once and apply it everywhere.** Use cursor pagination for large or changing collections
  and page/offset only for small, stable ones, never both in one operation; enforce a maximum page size server-side.
  Document the default sort, make it deterministic, and break ties with a unique key so pages neither skip nor
  duplicate. Return the next cursor or link; make total counts optional because they are expensive; treat a full
  export as a separate job rather than a page. Allowlist filter fields, operators, and value formats, apply one
  documented policy to unknown filters, and index every field offered for filtering or sorting. Keep the default page
  size and default sort fixed within a version; changing either is a behavioral break even when the schema is
  unchanged.
- **Build retry safety and load control into the contract.** A POST or action endpoint that a client may retry
  accepts an `Idempotency-Key` scoped to the principal, and the service keeps the request fingerprint and stored
  response for a documented TTL: the same key and body replay the stored response, and the same key with a different
  body is a conflict. PUT and DELETE are idempotent by definition. Advertise rate limits with response headers,
  return 429 with `Retry-After`, separate burst limits from sustained quotas, budget per tenant and per principal,
  and expect clients to back off with jitter. A quota is never a correctness mechanism; use idempotency,
  reservations, or a queue instead. Scope the key to the endpoint and the principal, reject a reused key before the
  handler runs, and document the TTL in the contract rather than in code.
- **Make authentication and authorization boundaries explicit per operation.** Authenticate at the edge and
  authorize at the resource: every operation names the principal, tenant, and object it checks, and the tenant and
  owner come from the verified token, never from a request body or query parameter. Scope tokens narrowly, keep
  internal operations off the public gateway, return 401 for missing or invalid credentials, 403 for an
  authenticated caller that is denied, and 404 when resource existence is itself sensitive. An authorization change
  is a contract change and follows the same versioning and deprecation path. Internal and admin endpoints pass the
  same policy check as public ones; a debug bypass is a public endpoint with a different name.
- **Decide synchronous versus asynchronous delivery explicitly.** A synchronous call returns the final state and is
  correct only when the work fits the caller's timeout. A long operation returns 202 with a status resource that has
  documented pending, success, and failure states, plus a cancel or retry path. Events and webhooks carry a stable
  type, schema version, event ID, timestamp, and causation ID; delivery is at least once, so consumers dedupe by
  event ID, tolerate out-of-order delivery, and verify a signature. Publish the retry schedule, dead-letter path, and
  replay procedure. The webhook receiver is an API in its own right: it acknowledges fast, processes idempotently,
  and exposes its failure and retry behavior; the event schema promises additive fields only and is versioned when a
  field disappears.
- **Plan compatibility, deprecation, and versioning together.** Additive changes (optional fields, new operations,
  new error codes) are compatible; removing or renaming a field, making an optional field required, narrowing a
  type, or extending a closed enum is breaking unless proven otherwise. Deprecate with a replacement, a
  `Deprecation` header, a `Sunset` date, a migration guide, and measured usage, then remove only when usage is zero
  or the announced date has passed. Version at the boundary that changes: a major path segment (`/v1`) for a public
  API, additive evolution for a coordinated internal IDL, and a media type or header only when every hop preserves
  it. Never version individual fields, and never keep two live names for one concept indefinitely. Record a support
  window in the contract (current major plus one previous major, or a fixed number of months) and measure field usage
  per caller, because one small consumer can block a removal indefinitely.

| Good | Bad | Why |
|---|---|---|
| `GET /v1/orders?status=paid&page_size=50` | `POST /v1/orders/search` with a filter body | A read stays a safe, retryable GET; wrapping it in POST hides semantics. |
| `{"code":"resource.not_found","details":{"resource":"order"}}` | `{"error":"Order 42 does not exist"}` | The code is stable and machine-readable; the message can change. |
| `202 Accepted` with `Location: /v1/jobs/{jobId}` | A 90-second request that clients time out and retry | Long work needs a status resource, not a longer timeout. |
| An `Idempotency-Key` with a stored response | "Clients should not retry" in a README | Gateways and users retry even when the client code does not. |
| Cursor plus a unique tiebreaker in the sort | `OFFSET 20000 LIMIT 20` on an active table | Offset pages drift when rows are inserted or deleted. |
| 401 for a missing token, 403 for a denied caller | 403 for every failure | Clients cannot tell whether to re-authenticate or stop. |
| Add `email_hash` beside `email`, deprecate the old field | Replace `email` with `email_hash` in place | Callers on the previous release break at deploy time. |

| Versioning strategy | Use when | Avoid when |
|---|---|---|
| Major path segment (`/v1`) | A public or partner API needs a clean breaking boundary and routing is simple | Internal calls where every client regenerates from one IDL in lockstep |
| Media type or `Accept` header | One URL serves different representations and every hop preserves the header | Shared caches, gateways, or mobile stacks that strip or normalize it |
| Additive evolution only | GraphQL, protobuf, or internal services with tolerant readers and coordinated releases | A removal, a rename, or a required input, which no additive rule makes safe |
| Feature flag or shadow endpoint | A migration window where old and new behavior run side by side | A substitute for a stable public version after the window closes |

## 2. Database and Schema Change

Schema changes are harder than code changes because old and new data coexist during rollout and every step touches
the live database. Assume zero downtime and a code-reversible path for every step up to the read switch; treat the
final drop as a destructive change with its own backup and approval gate, and treat the absence of either as a design
defect rather than a scheduling inconvenience.

- **Keep one ordered, immutable migration history.** Migrations live in the repository, are applied in order by the
  same tool in every environment, and are never edited after they apply anywhere; a correction is a new migration.
  The tool takes a lock so two deploys cannot race, test databases are built by running the whole history, and manual
  production DDL is a break-glass action followed by a migration that records it. Do not let an ORM autogenerate
  schema against the live database as the source of truth. Forward-only is the default; when the tool offers down
  migrations, still prefer a forward fix, because down scripts are rarely exercised against real data.
- **Use expand-contract for every change that old code can see.** The phases are: add the new structure without
  removing anything; deploy code that writes both forms and reads the old one; backfill existing rows; verify that
  both forms agree; switch reads to the new form; drop the old structure after a deprecation window. Each phase up to
  the read switch is a separate deploy and reversible by redeploying the previous code; the final drop is
  irreversible and waits for a verified backup or point-in-time-recovery point and the approval gate. An inverse
  migration is a last resort, not the plan. Keep the two forms consistent during dual-write and reconcile them before
  the switch; a count of mismatched rows is part of the exit criteria for the expansion phase.
- **Backfill in batches that are restartable and observable.** Select keyset ranges, not OFFSET windows; commit per
  batch; make the update idempotent (`WHERE new_column IS NULL`) so a rerun is safe; throttle by rows per second;
  record the last processed key; monitor replication lag, lock waits, CPU, and disk. Estimate the duration on
  production-sized data and define a stop condition and a dry-run count before starting. One UPDATE over a large
  table holds locks, bloats the table, and lags replicas for as long as it runs. A backfill is a production data
  write and needs its own approval, throttle, and kill switch, run in a quiet window with the owner watching.
- **Estimate the lock before executing DDL.** Name the lock the engine takes and what it blocks: on PostgreSQL,
  adding a column with a volatile default rewrites the table; a column type change that is not binary-coercible
  rewrites and blocks writes; a plain index build blocks writes while a concurrent build does not; and
  `VALIDATE CONSTRAINT` takes SHARE UPDATE EXCLUSIVE, which blocks other DDL and VACUUM but not reads or writes.
  Set `lock_timeout` and `statement_timeout`, retry, run the migration as its own deployment step, and watch the
  database while it runs. A migration that queues
  behind a long transaction and then blocks every writer is an outage, not a deploy detail. Run migrations as an
  explicit deployment step, never on application startup: a rolling deploy would multiply the lock attempts by the
  replica count.
- **Choose indexes and constraints from queries and invariants.** Index every foreign key and every hot filter and
  join; order composite columns by equality first and range second; use partial indexes for status and soft-delete
  predicates; remove duplicate and unused indexes because each one costs writes; build large indexes concurrently.
  Add constraints in the validating-off form, then validate in a separate step, and only after the data satisfies
  them. Enforce at the database the invariants the application cannot guarantee, including uniqueness under
  concurrency. A unique constraint is the only reliable duplicate check under concurrent writers; an application
  check-then-insert races and loses.
- **Time constraints after the data is clean.** Check for violating and orphan rows before adding NOT NULL, UNIQUE,
  FOREIGN KEY, or CHECK; add the constraint unvalidated, deploy code that writes valid rows, validate, then enforce.
  A constraint added before the backfill turns old data into a production failure as soon as old code writes, and a
  unique constraint added to dirty data leaves a half-applied migration. Deferrable constraints serve multi-statement
  transactions, not unordered writes. Count the violating rows before choosing the fix; sometimes the answer is data
  cleanup rather than a schema change.
- **Treat destructive changes as production changes with an approval gate.** Dropping or renaming a column or table,
  truncating, narrowing a type, and mass deletion can lose data that no code revert restores. Require explicit
  approval for each operation (a migration is a database write under the global constraints), a consumer list, a
  backup or point-in-time-recovery check, a quiet window, a dry run with affected row counts, and a post-change
  verification query. Prefer deprecation and a later drop over a rename in place. Write down the dropped object's
  definition and affected row counts in the approved request so a future restore attempt knows what to reconstruct.
- **Review and test migrations like code, including the upgrade path.** A migration review covers the file, the
  forward fix, the backfill, the estimated duration and lock, the verification query, and the data that will
  disappear. CI runs the full history on an empty database and upgrades a snapshot of the previous release to the
  new head; tests never start from an ORM-generated schema. Rehearse destructive or lock-heavy migrations on a
  production-sized copy with masked data, never on shared staging data that another team is using. CI fails when the
  migration history and the deployed schema snapshot diverge, so drift is caught before it reaches an environment.

| Good | Bad | Why |
|---|---|---|
| Add nullable `tenant_id`, dual-write, backfill, then NOT NULL | Add `tenant_id NOT NULL` in one migration | The single step fails on existing rows and locks or rewrites the table. |
| `CREATE INDEX CONCURRENTLY idx_orders_tenant_id ...` | A plain `CREATE INDEX` in a transaction on a hot table | The plain build blocks writes for the whole build. |
| `ADD CONSTRAINT ... NOT VALID`, then `VALIDATE CONSTRAINT` | One `ADD CONSTRAINT` that validates every row while holding ACCESS EXCLUSIVE | `VALIDATE CONSTRAINT` takes SHARE UPDATE EXCLUSIVE on PostgreSQL: other DDL and VACUUM wait, reads and writes do not. |
| Batched backfill with a saved cursor and sleeps between batches | One `UPDATE` over the whole table | The single update holds locks, bloats, and lags replicas for minutes. |
| New column plus dual-write, old column dropped later | `ALTER TABLE ... RENAME COLUMN` | A rename breaks every reader on the old release during rollout. |
| A follow-up migration after a merged mistake | Editing an applied migration | Applied files are immutable; editing leaves environments with different schemas. |
| Restore or forward fix plus a verification query | "Revert the deploy" after a drop | A code revert cannot restore dropped data. |

| Operation | Lock and cost | Risk | Mitigation |
|---|---|---|---|
| Add nullable column with no default | Brief metadata lock | Low, but waits behind long transactions | Set `lock_timeout`, run as its own step |
| Add column with volatile default or change type | Table rewrite, writes blocked | High on large or busy tables | Add nullable, backfill, swap in a new column |
| Plain `CREATE INDEX` | Blocks writes for the build | High on hot tables | Build concurrently, outside a transaction |
| `ADD CONSTRAINT ... NOT VALID` | Brief lock, no row scan | Low | Follow with a separate validation step |
| `VALIDATE CONSTRAINT` (PostgreSQL) | SHARE UPDATE EXCLUSIVE; blocks DDL and VACUUM, not reads or writes | Low to medium, in proportion to scan time on large tables | Off-peak, `lock_timeout`, monitor waits |
| Batched `UPDATE` backfill | Row locks plus replication load | Medium, grows with batch size | Small batches, sleep, watch lag |
| `DROP COLUMN` or `DROP TABLE` | Brief metadata lock | Irreversible data loss | Stop readers first, back up, get approval |
| `TRUNCATE` | Access-exclusive lock | Destructive and fast | Approval, count first, never in a shared migration |

## 3. Data Retention and Lifecycle

A dataset outlives the request that created it, and every copy outlives the deletion of the record it came from.
The security-compliance role sets the class and the retention period in its data inventory; this section covers how
the schema and the API enforce and evidence them, not how the policy is decided.

- **Apply the data inventory at the field level.** Map each inventory class (public, internal, confidential, or
  restricted) onto the tables, collections, and fields that carry it, and record the mapping in schema
  metadata or the data dictionary because a column name does not classify its content. A derived field inherits the
  most restrictive class of its inputs, and an unclassified field is treated as restricted until the inventory
  covers it. The mapping drives access control, encryption, redaction at log time, and enforcement of the
  inventory's retention period.
- **Enforce the retention period the inventory sets.** For each dataset record the period it inherits, the trigger
  that starts the clock (created_at, account closure, contract end, last activity), the disposition (delete,
  anonymize, archive), and the owner. Never default to forever and never invent a period: legal minimums, maximums,
  exceptions, and holds belong to the security and legal roles, and this skill records how the schedule is
  implemented, reviewed yearly, and tested.
- **Treat deletion as a path through every copy, not one DELETE.** A deletion or erasure request starts in the
  primary store and propagates to the search index, cache, analytics or warehouse tables, event streams, logs, and
  exports; each destination has a mechanism and a measured lag. Run deletion jobs idempotently with retries and an
  audit record, verify with per-store counts or queries, and report the backup expiry date as the end of the process.
  A delete endpoint that clears one table while three copies remain is a compliance defect, not a partial success.
  Model deletion as an asynchronous pipeline: the API accepts the request, a job performs it, and a receipt reports
  per-store completion and any residual copies.
- **Choose soft delete or hard delete explicitly and implement its obligations.** Soft delete (`deleted_at`) suits
  recovery windows and audit needs, but it is retention, not deletion: every read filters it or reads through a view,
  unique constraints use partial indexes, and a purge job exists with a date. Hard delete suits erasure requests and
  short-lived data with no audit requirement. An erasure that fans out across copies returns 202 with a status
  resource and a per-store receipt; return 204 only for a single-store synchronous hard delete with no restore path.
  Never describe a soft delete as erased. A soft-deleted row still counts for storage, export, backup cost, and
  access requests, so an erasure that leaves it in place is not complete.
- **Count backups as copies with their own retention and restore behavior.** Backups, snapshots, and point-in-time
  recovery contain deleted rows until they expire, so their retention bounds the true deletion window and is
  documented. An erasure process states the backup expiry date instead of claiming immediate removal; a restore must
  not resurrect data the retention schedule already purged, so the restore runbook includes a post-restore purge.
  Encryption at rest and the restore drill belong to the release and operations role. Backup retention longer than
  the inventory's period is a security decision with a recorded justification and a compensating control, never an
  unexamined default.
- **Control logs, analytics, and exports as data copies.** Logs are a copy written at high volume: redact personal
  data and secrets at write time, enforce the inventory's log retention, and never log full request or response
  bodies by default. Analytics and warehouse tables carry subject identifiers and need the same deletion
  propagation; event streams have their own retention; exports are copies with an expiry, a signed URL, an access
  log, and a deletion path. A copy that no one owns is a copy that no one deletes. Prefer structured fields with a
  redaction rule over free-text messages, because templates can be tested and messages cannot.
- **Never put production data in test or development.** Generate synthetic data, or mask it irreversibly before it
  leaves production; anonymization that can be reversed through a lookup table is not masking. Test fixtures contain
  no real people, secrets, or internal addresses, and example values use reserved names such as
  `example.test.invalid`. Non-production stores get a short retention and a periodic reset so stale copies do not
  accumulate. A production export used for debugging follows the same rules as a product export: expiry, access log,
  and deletion.
- **Keep archives and cold storage under the same rules.** Moving data to cold storage, an archive bucket, or an
  offline export changes the cost, not the obligations: access control, encryption, retention, deletion, and audit
  still apply. Record the archive format and schema so the data stays readable without the application, include a
  checksum, test a restore, and tie the archive's retention to the same schedule. A legal hold from the security or
  legal role suspends the schedule; record its scope, authority, and expiry against the dataset and lift it only on
  that role's direction. Cold or archived data may outlive hot data only when the inventory's period says so.

| Good | Bad | Why |
|---|---|---|
| `deleted_at` plus a purge job and filtered reads | `deleted_at` treated as deletion with no purge | The row and its personal data live forever under a different name. |
| A deletion job per store with per-store verification | `DELETE FROM users WHERE id = 42` only | Search, cache, warehouse, and logs still expose the person. |
| Synthetic fixtures from a generator | A nightly production dump restored in staging | Personal data spreads to every developer machine and backup. |
| Redacted logs that carry only a subject ID | Email and phone numbers in log messages | Log copies outlive the account and cannot be deleted reliably. |
| Bounded backup retention with a stated erasure window | "Backups are kept forever" | The deletion promise is false because the data is still recoverable. |
| Expiring export URL plus access log | A permanent public export link | Any holder can recall the full dataset after the purpose ends. |

| Store | Copy type | Deletion mechanism | Verification |
|---|---|---|---|
| Primary database | Source of truth | Delete or anonymize rows in a transaction | Row count and a read query |
| Search index | Derived | Delete by ID or reindex the affected scope | Query by subject ID |
| Cache | Derived, short-lived | Delete keys and let the TTL expire | Key existence check |
| Warehouse or analytics | Derived, append-only | Partition drop or a purge job per subject | Subject query and job log |
| Logs and traces | Event copies | Retention expiry plus redaction at write | Retention config and sample query |
| Backups and point-in-time recovery | Snapshot copies | Expiry only, no selective delete | Backup expiry date and restore test |
| Exports and files | Explicit extracts | Delete the object and invalidate the URL | Access log and object listing |
