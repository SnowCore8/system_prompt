# Naming Dimensions

Use this file with `SKILL.md`. Each section gives the pattern, examples, and edge cases for one artifact. When a
project already has a convention, read it first and apply the higher-precedence rule; this file supplies the default
and the reasoning.

## 1. Files and Directories

- Use lower case; choose one case per language: `snake_case` for Python and Rust modules, `kebab-case` for web
  modules, assets, and docs, `PascalCase` only where the language expects it (Java, C#, Kotlin, Swift types).
- Name a file after its primary export or responsibility, not its layer alone: `user_repository.py`, not `db.py`;
  `billing/invoice_calculator.go`, not `helpers.go`.
- Directories use plural nouns for collections (`users/`, `orders/`) and singular nouns for one feature
  (`billing/`, `checkout/`). Avoid `misc/`, `common/`, `utils/` unless the project documents their boundary.
- No spaces, no version suffixes (`v2` is for API versions, not file copies), no `final`, `new`, or `old`.
- Test files mirror the unit name and use the language suffix: `user_service_test.py`, `UserServiceTest.java`,
  `user-service.test.ts`, `user_service_test.go`.
- Fixtures live in `fixtures/` or `testdata/`; snapshots in `__snapshots__/` or `snapshots/`; golden files in
  `golden/`.
- Migrations are timestamped and ordered: `20261114093000_add_order_status.sql`.
- Static assets are kebab-case, include scale or size when relevant, and never encode a campaign or a person:
  `hero-image@2x.png`, `icon-close.svg`, `logo-dark.svg`.

| Good | Bad | Why |
|---|---|---|
| `order_repository.py` | `repo2.py` | States the concept and responsibility. |
| `billing/invoice_calculator.go` | `helpers.go` | A grab-bag name attracts unrelated code. |
| `20261114_add_order_status.sql` | `migration.sql` | Ordering and intent are visible. |
| `user-service.test.ts` | `test1.ts` | Mirrors the unit and the runner convention. |

## 2. Packages and Namespaces

- Java and Kotlin: reverse domain, all lower case, no underscores: `com.example.billing`.
- Python: short lower-case packages, no hyphens: `billing`, `billing.invoices`.
- Go: short lower-case package names, no underscores or mixed caps: `billing`.
- npm: lower-case, scoped when public: `@example/billing`.
- Rust: `snake_case` modules and crates; avoid a crate and a module with the same name in one path.
- Name by domain, not by layer: `billing.payments`, not `services.managers`.
- Avoid stuttering: `billing.Invoice`, not `billing.BillingInvoice`, unless the qualifier disambiguates.
- Keep the public surface in a named package; put internals in `internal/`, `_private`, or an unexported module.

| Good | Bad | Why |
|---|---|---|
| `com.example.billing` | `com.example.Billing_App` | Java packages are lower case, no underscores. |
| `billing.payments` | `services.managers` | Domain names survive refactors; layer names do not. |
| `internal/parser` | `misc/parser` | `internal` states the visibility contract. |

## 3. Modules and Imports

- Module names are nouns for a capability (`billing`, `auth`, `search`) and verbs only for a command module
  (`bootstrap`, `migrate`).
- One primary export per file when the language allows it; re-export deliberately and document the public surface.
- Import aliases are short and unambiguous: `import numpy as np` is conventional; `import user as u` is not.
- Avoid circular names: `serialization.json` is better than `json.json`; `billing.invoices` is better than
  `invoices.invoices`.
- Internal modules use a marker the language supports: `_internal`, `internal`, `private`, or no export.

## 4. Types and Interfaces

- Classes, structs, records, and type aliases use singular noun phrases: `Invoice`, `OrderItem`, `UserId`.
- An interface names a capability or a role: `Readable`, `UserStore`, `PaymentGateway`. Use `I` only in C# and
  languages whose convention requires it; do not import it into Python, Go, or Rust.
- Abstract base classes use a meaningful role, not `Base` as a default: `Repository` or `Storage`, not
  `BaseRepository` unless the project already uses that pattern.
- A DTO is a boundary type: `InvoiceDto`, `CreateOrderRequest`, `OrderResponse`. Do not suffix domain types with
  `Dto`.
- Generic parameters are short and conventional: `T`, `TKey`, `TValue`, `TResult`; use a descriptive name when the
  role is not obvious (`TResponse`).
- Type aliases state the domain meaning: `type UserId = string` (branded if possible), `type Cents = number`.
- Avoid `Impl`: use the technology or role (`SqlUserRepository`, `InMemoryUserRepository`).
- Do not encode nullability or optionality in the type name; the type system carries it (`User | null`).

| Good | Bad | Why |
|---|---|---|
| `UserStore` | `IUserStore` in Python | Python has no `I` convention. |
| `SqlUserRepository` | `UserRepositoryImpl` | Names the mechanism instead of a meaningless suffix. |
| `CreateOrderRequest` | `OrderData` | States the boundary and the operation. |

## 5. Enums and Unions

- Enum types are singular: `OrderStatus`, `PaymentMethod`, not `OrderStatuses`.
- Members are stable and descriptive: `PENDING`, `PAID`, `REFUNDED` or `Pending`, `Paid`, `Refunded` per language;
  never `STATUS_1`, `TYPE_A`, or a numeric literal.
- Two-state enums are usually booleans; use an enum when a third state is plausible or the values are domain terms.
- Union types and discriminated unions use a `kind` or `type` discriminant with stable lower-case values:
  `{ kind: "card" | "bank_transfer" }`.
- Do not use an enum member as a display label; map it to localized text at the presentation boundary.

## 6. Functions and Methods

- Use a verb phrase that states the effect: `sendInvoice`, `parseConfig`, `listActiveUsers`, `calculateTotal`.
- A pure read is a noun or a `get` accessor per language: `user` / `getUser`; an I/O read is `fetchUser`, `loadUser`,
  or `findUser`; a write is `saveUser`, `updateUser`, `deleteUser`.
- Predicates start with `is`, `has`, `can`, `should`, or `needs` and return a boolean; `validate` returns a result or
  throws, `assert` throws on failure.
- Factories are `createX` or `XFactory`; builders are `XBuilder`; converters are `toX` and `fromX`; parsers are
  `parseX`; formatters are `formatX`.
- Async naming follows the language: C# uses an `Async` suffix, JavaScript does not, Python relies on `async def`.
- One function, one action. If the name needs `and`, split the function.
- Avoid `do`, `handle`, `process`, `run`, `manage`, and `execute` without an object: `handlePaymentFailure`, not
  `handle`.

| Good | Bad | Why |
|---|---|---|
| `listActiveUsers` | `getUsers2` | States the filter and the action. |
| `fetchInvoice` | `getInvoice` for an HTTP call | `fetch` signals I/O in many codebases. |
| `parseDuration` | `duration` | The verb distinguishes parsing from formatting. |

## 7. Variables, Parameters, and Fields

- Use nouns; a variable states the value, not its type: `invoice`, `pendingJobs`, `parsedConfig`.
- Length follows scope: `i` for a loop index is fine; a module-level `i` is not. Public fields and parameters need
  full words.
- Parameters use the domain term, not `data`, `value`, `item`, or `input`: `invoice`, `customer`, `timeoutMs`.
- Avoid temporal names (`temp`, `tmp`, `newUser`, `oldUser`) and numbered names (`user2`); use a qualifier that
  states the difference (`importedUser`, `cachedUser`).
- Private fields follow the language: Python `_name`, C# `_camelCase`, Java `camelCase`; do not mix.
- Optional and nullable values are expressed by the type, not the name; `middleName`, not
  `optionalMiddleName`.
- A field that holds a boolean follows the boolean rules below; a field that holds a collection is plural.

## 8. Constants

- Constants use UPPER_SNAKE_CASE: `MAX_RETRY_COUNT`, `DEFAULT_TIMEOUT_MS`, `HTTP_PORT`.
- Include the unit when the value has one: `DEFAULT_TIMEOUT_MS`, not `DEFAULT_TIMEOUT`.
- Name the policy, not the literal: `MAX_RETRY_COUNT` rather than `THREE`; keep magic numbers out of logic.
- Group constants by domain (`billing/constants.py`) rather than one global `constants` module.
- A value that changes per environment is configuration, not a constant; name it as a config key.
- Enum members are not constants; use the enum type for a closed set.

## 9. Booleans and Predicates

- Use a positive prefix: `isEnabled`, `hasChildren`, `canRetry`, `shouldNotify`, `needsReview`.
- Never use `not`, `no`, or a negative verb unless the negative is the domain term: `isVisible` beats `isNotHidden`.
- Do not use `flag`, `status`, `check`, or `state` for a boolean; they hide the question being answered.
- A function named `isX` must return a boolean, not a count, string, or nullable. For three states, use an enum.
- Name the question, not the implementation: `hasAccess(user, resource)`, not `checkAccessFlag(user, resource)`.
- Avoid double negatives in conditions; if the negative is required, name the positive and negate at the use site.

| Good | Bad | Why |
|---|---|---|
| `isPaid` | `notUnpaid` | One positive read. |
| `hasExported` | `exportFlag` | States the condition. |
| `canRetry` | `retryStatus` | A boolean predicate, not a status bag. |

## 10. Collections, Maps, Sets, and Tuples

- Collections are plural nouns: `users`, `orderItems`, `pendingJobs`; the singular is one element.
- A map names its key and value: `usersById`, `priceBySku`, `ordersByCustomerId`; avoid `userMap`.
- A set names its contents: `activeUserIds`, `blockedDomains`; add `Set` only when the distinction from a list
  matters and is not clear from the type.
- Tuples and pairs name both sides: `(key, value)`, `(min, max)`, `(start, end)`; avoid `(a, b)` outside a
  one-line lambda.
- Loop indices are `i`, `j`, `k`; a named index (`userIndex`) is better when the body is long or nested.
- Empty and missing are different: `users` may be empty; `user` may be absent. Do not encode that in the name.
- Do not encode the implementation (`userLinkedList`, `itemArray`); the type states it.

## 11. Quantities, Units, Time, Money, Ratios, Ranges

- Every quantity carries its unit when the type does not: `timeout_ms`, `size_bytes`, `weight_kg`, `distance_m`,
  `temperature_c`.
- Instants use `<event>_at` in UTC (`created_at`, `paid_at`); dates use `_date`; durations use `_ms` or `_s`.
  Do not use `timestamp` without a unit or timezone rule.
- Money uses integer minor units plus an ISO 4217 currency: `amount_cents` and `currency`; never a float.
- Ratios are 0–1 (`success_ratio`); percentages are 0–100 (`discount_pct`); state the range in the naming table.
- Ranges name both ends and the inclusion rule: `min_`/`max_`, `start_`/`end_`, `from_`/`to_`; document whether the
  end is inclusive.
- Counts use `_count`; totals use `_total`; limits use `_limit`; avoid `num`, `qty`, `amt`.
- A value that combines quantity and unit in one string is a display value, not a domain value; name it
  `formatted_duration` and keep the numeric value separate.

| Good | Bad | Why |
|---|---|---|
| `timeout_ms` | `timeout` | The unit is part of the contract. |
| `amount_cents` + `currency` | `amount` | Money without a unit or currency is ambiguous. |
| `discount_ratio` | `discount` | States the range convention. |

## 12. Async, Concurrency, Streams, Callbacks

- Follow the language: C# `LoadAsync`, JavaScript `load` (the promise is in the type), Python `async def load`,
  Rust `load` with a future return type.
- A callback is `onX` (`onSave`, `onError`); a handler is `handleX`; a listener is `onX` or `XListener`.
- A lock is `lock` or `mutex`; a guard is `guard`; avoid `lockFlag` and `isLocked` for the lock object.
- Workers and pools are `worker`, `workerPool`, `queue`, `scheduler`; avoid `thread2` and `jobManager`.
- Streams are `stream`, `reader`, `writer`, `source`, `sink`; events are `onData`, `onEnd`, `onError`.
- Do not encode timing or implementation in a name (`delayedTask`, `asyncHelper`); state the role.
- A future or promise value is `pendingResult` until resolved; do not call an unresolved value `result`.

## 13. Errors and Results

- Exception classes are specific and end in `Error` or `Exception` per language: `InvoiceNotFoundError`,
  `PaymentDeclinedError`; avoid a catch-all `AppError` for every failure.
- Error codes are stable and structured: `ERR_BILLING_INVOICE_NOT_FOUND`; do not reuse a code for two causes.
- Result types state success and failure: `Result<T, E>`, `Outcome<T>`, `PaymentResult`; fields are `ok`, `value`,
  `error`.
- Local error variables are `err` or `error`; `e` is acceptable in a short catch block; never a module-level `e`.
- Error messages are separate from identifiers; do not put secrets, tokens, or personal data in a message.
- Wrap an external error with context: `InvoiceSyncError` with a `cause`, not a bare rethrow.

## 14. Tests and Test Doubles

- Test names state behavior and condition: `test_list_orders_returns_empty_for_new_user`,
  `should_reject_expired_card`; use the project's runner convention.
- Test files mirror the unit: `user_service_test.py`, `UserServiceTest.java`, `user-service.test.ts`.
- Fixtures and factories are explicit: `user_fixture`, `make_user`, `UserFactory`; avoid `data1`, `sample2`.
- Doubles have precise meanings: `Fake` is a working lightweight implementation, `Stub` returns canned values,
  `Mock` records or verifies interactions, `Spy` wraps a real object. Do not call a stub `Mock`.
- Benchmarks use `bench_` or the language convention; property tests use `prop_`; snapshot files end in `.snap`.
- Test names must not encode a ticket number as the only description; put the ticket in the body or metadata.

## 15. HTTP, RPC, and GraphQL

- HTTP paths use plural kebab-case resources: `/v1/order-items`; a subresource nests it:
  `/v1/orders/{orderId}/items`.
- Use methods for CRUD; a verb appears in the path only for an action that is not CRUD: `/v1/orders/{id}/cancel`.
- Version only the path or the media type, not each field: `/v1`, not `/orders/v1/create`.
- Query parameters use one case per API: `created_after`, `page_size`, `sort`, `order`; do not mix `createdAfter`
  and `created_after` in one API.
- Pagination uses `page`/`page_size` or `cursor`/`limit`, never both in one endpoint.
- JSON fields follow the schema case; booleans `is_`/`has_`, timestamps `_at`, identifiers `<entity>_id`.
- RPC methods are `VerbNoun`: `GetOrder`, `ListOrders`, `CreateOrder`; request and response types are
  `GetOrderRequest` and `GetOrderResponse`.
- GraphQL types are PascalCase, fields camelCase, enums UPPER_SNAKE; mutations are verb phrases
  (`createOrder`) and inputs end in `Input`.
- Error payloads use `code`, `message`, and `details`; codes are stable and not localized.

## 16. JSON and Serialization

- Choose one key case per schema and keep it across producers and consumers; map to the language case only at the
  boundary.
- Keys contain no spaces; avoid dots unless they express a namespace; avoid reserved words and leading digits.
- Booleans use `is_`/`has_`; timestamps use `_at` with RFC 3339; IDs use `<entity>_id`; enums use stable values.
- Arrays are plural; objects used as maps state the key in the field name (`users_by_id`).
- Null and absent are different states; document which one means “missing” and never use the string `"null"`.
- Do not encode types in keys (`str_name`, `int_count`); do not wrap everything in `data` unless the protocol
  requires it.
- A discriminator is `type` or `kind` with stable lower-case values; do not put a display label in the payload.

## 17. Databases and Migrations

- Tables are plural snake_case: `orders`, `order_items`; columns are singular: `created_at`, `customer_id`.
- A primary key is `id` unless the table uses a natural key; a foreign key is `<referenced_table>_id`.
- A join table is `<a>_<b>` in alphabetical order: `order_product`, not `product_order_link`.
- Indexes are `idx_<table>_<columns>`; unique constraints `uq_<table>_<columns>`; foreign keys
  `fk_<table>_<referenced_table>`; checks `ck_<table>_<rule>`.
- Views are `v_<name>`; materialized views `mv_<name>`; schemas are lower case.
- Audit columns are `created_at`, `updated_at`, `created_by`, `updated_by`; soft delete is `deleted_at`.
- Boolean columns are `is_`/`has_`; timestamps are `_at`; money is `<amount>_cents` plus `currency`.
- Migrations are timestamped, one logical change each, and never rename or drop a column without a backfill and a
  rollback plan.

## 18. Configuration and Environment

- Environment variables are UPPER_SNAKE_CASE with an application prefix: `APP_DATABASE_URL`, `APP_LOG_LEVEL`,
  `APP_HTTP_TIMEOUT_MS`.
- The name states the purpose, not the value or the provider: `APP_DATABASE_URL`, not `APP_POSTGRES_1`.
- No secret value in a name; the name may say `PASSWORD` or `TOKEN`, but the value comes from a secret store.
- Config keys use one separator per system: `http.timeout_ms` or `http_timeout_ms`; do not mix.
- Feature flags are `ff_<domain>_<name>` or `<domain>.<flag>`; an environment suffix belongs in the value, not the
  name.
- Document defaults, units, allowed values, and whether a restart is required.

## 19. CLI

- Commands are lower-case verbs (`create`, `list`, `delete`) and subcommands are lower-case nouns
  (`app user create`); pick one ordering and keep it.
- Flags are kebab-case: `--dry-run`, `--output-format`, `--no-color`; a short flag is one letter and never
  ambiguous (`-v` must not mean both verbose and version).
- Boolean flags default to false and use `--no-` to negate when the positive is the default.
- Positional arguments are documented as `<required>` and `[optional]`; their names match the help text.
- Exit codes are documented; `0` success, non-zero failure; do not encode a cause only in the number without a
  message.
- Environment variables for a CLI use the same `APP_` prefix and the same names as the service.

## 20. Logs, Events, Metrics, and Traces

- Log fields are stable snake_case: `timestamp`, `level`, `event`, `service`, `trace_id`, `span_id`, `user_id`;
  `message` is free text.
- Events are `object.action` in the past tense: `order.created`, `invoice.paid`; payload fields match the API
  schema.
- Metrics are `domain_operation_unit`: `http_request_duration_ms`, `queue_depth`, `cache_hits_total`; counters end
  in `_total`, histograms carry the unit, gauges state the current value.
- Trace identifiers are `trace_id` and `span_id`; never put a user ID or email in a metric name; keep cardinality
  bounded.
- Error logs include a stable `error_code` and a safe message; never log secrets, tokens, or full personal data.
- An event schema is versioned; do not rename an event field without a migration window.

## 21. Assets, CSS, HTML, and i18n

- Asset files are kebab-case and include scale or dimensions when relevant: `hero-image@2x.png`,
  `icon-close.svg`, `logo-dark.svg`.
- CSS classes are kebab-case; BEM is `block__element--modifier` (`order-item__price--discounted`); utility classes
  follow the framework's prefix.
- IDs are reserved for anchors and JavaScript hooks; a JS hook uses `js-` (`js-order-form`) and is not styled.
- Custom properties are `--color-bg`, `--space-md`, `--font-body`; no unexplained abbreviations.
- HTML data attributes are `data-` plus kebab-case (`data-order-id`); form field names follow the backend schema.
- i18n keys are dot-separated lower case: `orders.list.empty`, `checkout.payment.declined`; plural keys use the
  platform suffixes (`_one`, `_other`); never use an English sentence as a key.
- Accessible names match the visible label; alt text describes the image, not its filename.

## 22. Commits, Branches, and Tags

- A commit is `type(scope): imperative summary`; types are `feat`, `fix`, `refactor`, `docs`, `test`, `chore`,
  `perf`, `build`, and `ci`. The body states why; the footer references issues.
- The summary is imperative and lower case after the colon: `fix(invoice): reject expired cards`, not
  `Fixed the bug`.
- A branch is `type/short-description`: `feat/order-export`, `fix/expired-card`; lower case, hyphens, no spaces.
- A tag is SemVer with a `v` prefix: `v1.4.0`, `v1.4.0-rc.1`; never a date or a build number as the release tag.
- A PR title follows the commit convention; do not merge `WIP`, `tmp`, or a ticket number alone.

## 23. Feature Flags and Deprecation

- A flag states its scope and purpose: `ff_checkout_new_tax` or `checkout.new_tax`; default off, with an owner and a
  removal date in its description.
- Do not put an environment or a customer name in the flag name; that belongs in the targeting rules.
- A deprecated name gets a removal plan: prefer an annotation or a deprecation metadata field; if a prefix is
  required, use `deprecated_` or `legacy_` and record the replacement.
- Keep an alias for one release at most; document the mapping; remove the alias when the deprecation window ends.
- Never keep two live names for the same concept indefinitely; that is a collision, not compatibility.

## 24. Abbreviations, Acronyms, and Plurals

- Keep a short allowlist per project: `id`, `url`, `http`, `api`, `cpu`, `db`, `ui`, `cli`, `json`, `xml`, `sql`,
  `html`, `css`; expand everything else (`usr` to `user`, `cfg` to `config`, `mgr` to `manager`).
- Treat acronyms as words: `userId`, `httpClient`, `parseUrl`; Go uses initialisms (`UserID`, `HTTPServer`), C#
  keeps `Id` (`UserId`).
- Use regular plurals; uncountable nouns (`data`, `info`, `metadata`) take a qualifier (`dataSet`, `infoList`) when
  a collection is meant; never `datas` or `informations`.
- Avoid apostrophes and possessives in identifiers; `userIds`, not `user'sIds`.
- Identifiers are ASCII; avoid homoglyphs and non-ASCII lookalikes; a non-English domain term is transliterated or
  documented in the naming table.

## 25. Symmetry and Pairs

Use one pair consistently across a codebase; mixing `remove` and `delete` for the same operation is a defect.

| Pair | Pair | Pair |
|---|---|---|
| `open` / `close` | `add` / `remove` | `create` / `delete` |
| `start` / `stop` | `begin` / `end` | `lock` / `unlock` |
| `push` / `pop` | `encode` / `decode` | `serialize` / `deserialize` |
| `import` / `export` | `upgrade` / `downgrade` | `min` / `max` |
| `source` / `target` | `from` / `to` | `key` / `value` |
| `request` / `response` | `input` / `output` | `read` / `write` |
| `enable` / `disable` | `subscribe` / `unsubscribe` | `connect` / `disconnect` |
| `mount` / `unmount` | `allocate` / `free` | `acquire` / `release` |
| `increment` / `decrement` | `before` / `after` | `parent` / `child` |

## 26. Length, Scope, and Searchability

- One or two words for a local, two to three for a private member, two to four for a public API; a constant may be
  longer when each word carries meaning.
- One-letter names are limited to `i`, `j`, `k` for indices, `x`, `y` for coordinates, `e` for a caught error, and
  `_` for an unused value.
- A name must be unique enough to search: `userId` is searchable; `id` at module scope is not.
- A name must be pronounceable in a review; avoid `usrRprt` and consonant clusters.
- No numeric suffixes (`user2`, `handler3`); use a qualifier that states the difference.
- Longer is not better: remove words that repeat the type or the context (`UserUserRepository`, `IUserInterface`).

## 27. Renaming and Migration

1. State the evidence: ambiguity, collision, a renamed domain concept, or a rule violation. A rename without evidence
   is churn.
2. List every reference: code, tests, docs, fixtures, configs, database objects, API clients, dashboards, and alerts.
3. Choose the new name and the migration path: internal rename in one scoped change, or public alias plus
   deprecation, or a database expand-and-contract migration.
4. Update tests and docs in the same change; do not leave a stale name in an example.
5. Keep the diff reviewable: a rename commit should not carry behavior changes; a behavior change should not hide a
   rename.
6. Update the naming table and the changelog; remove the alias after the deprecation window.
7. Do not rewrite published history to hide a rename; add a follow-up commit that explains it.

## 28. Exemptions

- Generated code, vendored code, protocol buffers, OpenAPI-generated clients, and third-party schemas keep their
  names. Isolate them at a boundary and record the mapping.
- Mandatory language or framework conventions override this file, even when they conflict with a default here.
- An existing project convention wins over this standard; if it is harmful, propose a scoped migration, do not
  rename unrequested code.
- A public API name is a contract; rename it only with a versioned or deprecated path.
- If an anti-pattern is widespread, report it with a migration estimate; do not start a mass rename without
  authorization.

## 29. Infrastructure and Deployment

- DNS labels use lower-case letters, digits, and hyphens; start and end with an alphanumeric character; stay within
  63 characters; no underscores.
- Docker images are `<registry>/<org>/<service>:<tag>`; the tag is a SemVer or a commit SHA; `latest` is for local
  use only; container names are `<service>-<role>`.
- Kubernetes names are DNS-1123 lower kebab: `invoice-api`, `invoice-worker`; labels use the standard keys
  `app.kubernetes.io/name`, `app.kubernetes.io/component`, and `app.kubernetes.io/part-of`.
- ConfigMaps are `<service>-config`; Secrets are `<service>-secrets`; namespaces are lower case (`billing-prod`).
- Cloud resources include the application and environment in the name; tags carry `app`, `env`, `owner`, and
  `cost-center`; never put a secret in a resource name.
- Terraform resources are `snake_case`, modules are `kebab-case`, and state keys are `<env>/<service>/<component>`.
- CI jobs are lower kebab with a stage prefix (`test-unit`, `deploy-prod`); CI secrets use a `CI_` prefix.
- Environment names are `dev`, `staging`, and `prod`; do not create `production2` or `new-prod` as a second name for
  one environment.

## 30. Permissions, Roles, Scopes, and Audit Actions

- Permission and role identifiers use `domain.action`: `billing.invoice.read`, `billing.invoice.void`.
- Pick one separator per system (`.` or `:`) and keep it; `billing:invoice.read` mixes two grammars.
- Scopes use the same grammar as permissions (`orders:read` or `read:orders`); choose one order and document it.
- Role names describe a capability, not a job title: `billing_admin`, `support_readonly`; do not rely on a single
  `admin` role for everything.
- Permission constants use UPPER_SNAKE (`BILLING_INVOICE_READ`) only when the language requires constants; otherwise
  use the string identifier.
- Audit actions are `object.action` in the past tense (`invoice.voided`); the record includes actor, resource ID, and
  outcome.
- Do not encode a tenant, customer, or user ID in a permission name; those belong in policy data, not identifiers.

## 31. Published Packages and Modules

- npm: lower case and hyphens, scoped when public (`@example/invoice-core`); no upper case or spaces.
- PyPI: lower case and hyphens or underscores; the distribution name and the import name may differ, so document both.
- crates.io: lower case with underscores preferred; the crate name and the library name are usually identical.
- Maven: `groupId` is a reverse domain; `artifactId` is kebab-case (`invoice-core`).
- NuGet: package IDs are PascalCase (`Example.Billing`); the assembly name matches the package unless versioned.
- Go modules: the module path is lower case; package names are short and lower case with no underscores; a hyphen
  is allowed in the path, not in the package.
- Version tags are SemVer; a registry suffix (`-beta.1`) does not replace the version number.

## 32. Components, Hooks, and UI State

- Components are PascalCase and one per file: `OrderCard.tsx`, `InvoiceList.vue`; use `Page`, `Layout`, `Provider`,
  and `Dialog` suffixes for real roles, not `Wrapper` or `Container` by default.
- Custom hooks start with `use` (`useOrders`, `useDebouncedValue`); a hook name is a contract that it follows the
  rules of hooks. Return named state and actions (`data`, `isLoading`, `error`, `refetch`).
- Props use `onX` for callbacks, `isX`/`hasX` for booleans, `children` for composition, and `renderX` for render
  props; internal handlers are `handleX`.
- UI state names the question: `isLoading`, `hasError`, `selectedId`, `activeTab`; avoid bare `data`, `loading`, or
  `state`. Separate server state from local UI state in the name when both exist.
- Events are `onSubmit`, `onChange`, `onClose`; emitted domain events use past tense (`orderCreated`).
- Framework conventions win: Vue components are multi-word (`OrderCard`); Angular selectors are kebab-case
  (`app-order-card`) and services end in `Service`; React context is `OrderContext` and its hook `useOrderContext`.
- Avoid `Wrapper`, `Container`, and `Manager` for components; name what the user sees or what the component does.

## 33. Domain Models and Domain Events

- Entities are singular nouns (`Order`, `Customer`); value objects name the concept and its unit (`Money`,
  `DateRange`, `EmailAddress`, `Percentage`).
- Identifiers are `<Entity>Id` in code and `<entity>_id` in storage; do not expose a raw string named `id` across a
  domain API.
- An aggregate names the consistency boundary (`Order`), not `OrderAggregate`; repositories are `OrderRepository`.
- Domain events are past-tense (`OrderPlaced`, `InvoicePaid`); wire event types are `order.placed`; payload fields
  use domain terms, not database column names.
- Commands are imperative (`PlaceOrder`, `VoidInvoice`); queries are `GetOrder` or `ListOrders`; neither is a noun
  plus `Manager`.
- Policies and specifications name the rule (`RefundPolicy`, `EligibleForDiscount`); a policy returns a decision, not
  a boolean named `check`.
- Keep technical names (`Manager`, `Helper`, `Util`) out of the domain model; put orchestration in the application
  layer with a role name (`CheckoutService`, `InvoiceSync`).

## 34. Documentation, Diagrams, and Decisions

- Documentation files are kebab-case; ADRs are numbered and stable (`0001-use-postgres.md` or
  `ADR-0001-use-postgres.md`); never renumber an accepted ADR.
- Headings are stable anchors; do not rename a linked heading without a redirect or an updated link. Follow the
  project's heading case (sentence case or title case), not both.
- Diagram IDs are `fig-<name>` or `diagram-<name>`; node IDs use the domain or service name (`order-service`,
  `billing-db`), not `node1`.
- API operation IDs are camelCase (`listOrders`, `createInvoice`); code samples are `example_<action>` and live next
  to the operation they illustrate.
- Ticket and issue IDs belong in links, metadata, or commit footers, not in identifiers, filenames, or test names as
  the only description.
- Cross-references use the naming table's term; a document term that differs from the code term is a defect.
