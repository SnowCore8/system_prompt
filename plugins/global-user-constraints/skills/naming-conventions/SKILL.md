---
name: naming-conventions
description: Define, review, or refactor names for any programming project across files, directories, packages, types, functions, variables, APIs, databases, configuration, tests, commits, and assets. Use when starting a project or module, naming a new identifier, reviewing a diff for naming problems, or reconciling inconsistent names. Provides language-agnostic defaults with per-language overrides.
argument-hint: '[path or symbol]'
---

# Naming Conventions

Names are the most-read interface in a codebase. A good name states what a thing is or does, fits the language, and
stays stable across layers; a bad name forces every reader to reconstruct intent from the implementation. This skill
gives one decision procedure and a complete rule set for every artifact a project names.

## Scope and Precedence

Apply the first rule that fits, and do not mix conventions inside one scope:

1. Mandatory language or framework convention. Go exported identifiers, C# `I` interfaces, and PEP 8 are not optional.
2. Existing project convention and lint configuration. Read the code and config before inventing a rule.
3. This standard's defaults, when the two levels above are silent.
4. Personal preference, which never overrides the three levels above.

- Generated code, vendored code, external protocol fields, and third-party schemas are exempt. Keep their names,
  isolate them at a boundary, and record the mapping in the project naming table.
- A rename is a change, not a cleanup. Read every reference first, stay inside the authorized scope, update tests,
  docs, and fixtures, and treat any public name as an API.
- When two rules conflict, state the conflict and the chosen rule; record the decision so the next change follows it.

## Process

1. Classify the artifact: file, directory, package, type, function, variable, constant, API field, database object,
   config key, test, commit, or asset.
2. Name the concept in the project's domain language. Check the naming table and glossary for an existing term.
3. Choose the grammatical form (noun, verb, adjective, plural) from the form table below.
4. Choose the case for the artifact and language; use `references/languages.md` for overrides.
5. Check collisions, symmetry, length, pronunciation, searchability, and misleading encodings.
6. Record a new domain term in the project naming table before using it in more than one place.
7. For a rename, list references, choose an alias or deprecation path, and verify the full diff.

## Core Rules

- **One concept, one name.** One name, one concept. Different names for one thing are a defect; one name for two
  things is a collision.
- **Name intent, not implementation.** `activeUsers` beats `filteredList2`; `retryCount` beats `loopCounter`.
- **Use the domain language.** Prefer the words the users and the product use; record synonyms that are banned.
- **Follow the language.** Do not import casing or prefixes from another language; a Python `IUserStore` or a Go
  `user_repository` is wrong even when the concept is right.
- **Be searchable and pronounceable.** Avoid one- and two-letter names outside loop indices, dropped vowels, and
  consonant clusters; someone must be able to say the name in a review.
- **Do not encode types.** No Hungarian notation and no `obj`, `str`, `arr`, `list` suffixes; encode units, ranges, or
  meaning only when the type cannot (`timeout_ms`, `amount_cents`).
- **Prefer positives.** `isEnabled` beats `isNotDisabled`; do not build double negatives.
- **Pluralize collections.** `users` contains users; `user` is one user. A map is `usersById`, not `userMap`.
- **Keep names short by scope.** One or two words for a local, two to four for a public API; a long name is better
  than a vague one, but only when the words carry meaning.
- **Do not rename outside the request.** Consistency is valuable, but mass renames are a separate, reviewed change.

## Casing Matrix

These are language-agnostic defaults. `references/languages.md` overrides them per language and framework.

| Artifact | Default case | Example |
|---|---|---|
| Package, namespace | lower case, dot-separated | `com.example.billing`, `app.users` |
| Module | snake_case or lowercase | `user_repository.py`, `billing` |
| Directory | kebab-case or lowercase | `order-items/`, `users/` |
| Source file | match the language and primary export | `user_repository.py`, `UserRepository.java` |
| Type, class, struct, record | PascalCase | `UserRepository`, `OrderItem` |
| Interface, protocol | PascalCase, capability or role | `UserStore`, `PaymentGateway`, `IUserStore` in C# |
| Enum type | PascalCase, singular | `OrderStatus` |
| Enum member | UPPER_SNAKE or PascalCase | `PENDING`, `Pending` |
| Function, method | camelCase or snake_case | `listActiveUsers`, `list_active_users` |
| Variable, parameter, field | camelCase or snake_case | `activeUsers`, `active_users` |
| Constant | UPPER_SNAKE_CASE | `MAX_RETRY_COUNT` |
| Boolean | `is`/`has`/`can`/`should`/`needs` + adjective | `isEnabled`, `hasChildren`, `canRetry` |
| Test function | behavior plus condition | `test_list_orders_returns_empty_for_new_user` |
| Test file | `<unit>_test` or `<unit>.test` | `user_service_test.py`, `UserServiceTest.java` |
| Database table | plural snake_case | `order_items` |
| Database column | singular snake_case | `created_at`, `customer_id` |
| Index, constraint | prefixed snake_case | `idx_orders_customer_id`, `uq_users_email` |
| API path | plural kebab-case | `/v1/order-items` |
| JSON field | one case per schema, usually camel or snake | `createdAt`, `created_at` |
| Environment variable | UPPER_SNAKE_CASE with app prefix | `APP_DATABASE_URL` |
| CLI flag | kebab-case | `--dry-run`, `--output-format` |
| CSS class | kebab-case or BEM | `order-item__price--discounted` |
| i18n key | dot-separated lower case | `orders.list.empty` |
| Commit type | lower case | `feat`, `fix`, `refactor`, `docs` |
| Branch | `type/short-description` | `feat/order-export` |
| Tag | SemVer with `v` prefix | `v1.4.0` |

## Grammatical Form

| Concept | Form | Example |
|---|---|---|
| Action | verb phrase | `sendInvoice`, `parseConfig` |
| Predicate | boolean adjective | `isExpired`, `hasAccess` |
| Resource or entity | singular noun | `Invoice`, `Customer` |
| Collection | plural noun | `invoices`, `activeUsers` |
| Map | noun plus `by` key | `invoicesById`, `priceBySku` |
| Factory | `XFactory` or `createX` | `InvoiceFactory`, `createInvoice` |
| Builder | `XBuilder` | `InvoiceBuilder` |
| Repository | `XRepository` | `InvoiceRepository` |
| Service | `XService` only for a real domain service | `BillingService` |
| Adapter or gateway | `XAdapter`, `XGateway` | `StripeAdapter`, `PaymentGateway` |
| DTO or wire model | `XDto`, `XRequest`, `XResponse` | `InvoiceDto`, `CreateOrderRequest` |
| Error | `XError` or `XException` | `InvoiceNotFoundError` |
| Options or config | `XOptions`, `XConfig` | `RetryOptions` |
| Result | `XResult`, `XOutcome` | `PaymentResult` |
| Identifier | `id` or `<entity>_id` | `id`, `customer_id` |
| Timestamp | `<event>_at` | `created_at`, `paid_at` |
| Duration | `<quantity>_ms`, `_s` | `timeout_ms` |
| Count | `<thing>_count` | `retry_count` |
| Money | `<amount>_cents` plus currency | `total_cents`, `currency` |
| Ratio or percentage | `_ratio` (0–1) or `_pct` (0–100) | `success_ratio`, `discount_pct` |

## Dimension Index

Each dimension has detailed patterns, examples, and edge cases in `references/dimensions.md`.

| Dimension | First rule |
|---|---|
| Files and directories | Lowercase, no spaces, match the primary export or responsibility. |
| Packages and namespaces | Reverse domain or short lowercase, stable public surface. |
| Types and interfaces | Singular noun; capability or role, not `I` prefix outside C#. |
| Enums and unions | Singular type, stable members, no numeric names. |
| Functions and methods | Verb phrase; one action; predicate names for predicates. |
| Variables and fields | Noun, scope-sized, no type prefixes. |
| Constants | UPPER_SNAKE, unit in the name, no magic values. |
| Booleans | Positive `is`/`has`/`can`/`should`; never a non-boolean `isX`. |
| Collections | Plural nouns, `by` maps, explicit keys and values. |
| Quantities and money | Unit suffix, ISO currency, integer minor units. |
| Time | `_at` for instants, `_ms` or `_s` for durations, UTC by default. |
| Async and concurrency | Follow language convention; no `Async` suffix where it is not idiomatic. |
| Errors and results | Specific error classes and stable codes; never catch-all names. |
| Tests and doubles | Behavior plus condition; `Fake`, `Stub`, `Mock`, `Spy` mean different things. |
| HTTP, RPC, GraphQL | Plural resources, kebab paths, one JSON casing per schema. |
| Databases | Plural snake tables, singular columns, prefixed indexes and constraints. |
| Configuration | UPPER_SNAKE env vars, prefixed keys, no secrets in names. |
| CLI | Kebab flags, verb commands, consistent short flags. |
| Logs, events, metrics | Stable snake fields, `object.action` events, unit-suffixed metrics. |
| Assets, CSS, i18n | Kebab files, BEM or utility classes, dot-separated keys. |
| Commits, branches, tags | `type(scope): summary`, `type/slug`, SemVer. |
| Infrastructure and deployment | DNS-compatible lower case; environment and owner live in tags. |
| Permissions and roles | `domain.action`; one separator; capabilities, not job titles. |
| Published packages | Follow the registry's allowed characters and casing. |
| Components and UI state | PascalCase components, `useX` hooks, positive state names. |
| Domain models and events | Singular entities, past-tense events, imperative commands. |
| Documentation and decisions | Kebab files, stable anchors, numbered ADRs. |
| Feature flags and deprecation | Named removal path, not a permanent `legacy_` prefix. |
| Abbreviations and acronyms | Allowlist, treat acronyms as words, no dropped vowels. |
| Symmetry and pairs | Use the same pair everywhere: `open/close`, `add/remove`. |
| Renaming and migration | Evidence, references, alias or deprecation, scoped change. |
| Exemptions | Generated, vendored, and external names stay; map them at the boundary. |

## Anti-Patterns

| Anti-pattern | Why it fails | Fix |
|---|---|---|
| `data`, `info`, `item`, `obj`, `temp`, `foo`, `bar` | Says nothing; forces reading the body. | Name the concept: `invoice`, `parseResult`, `pendingJobs`. |
| `Manager`, `Helper`, `Util`, `Common`, `Base` | Hides responsibility and attracts unrelated code. | Name the role: `BillingService`, `RetryPolicy`, `PathFormatter`. |
| `userObj`, `strName`, `arrItems` | Encodes the type; goes stale after a refactor. | `user`, `name`, `items`. |
| `notReady`, `disableCache`, `isNotUnavailable` | Negative names invert every read site. | `isReady`, `cacheEnabled`, `isAvailable`. |
| `usr`, `cfg`, `mgr`, `btn`, `msg` | Saves three characters, costs a lookup. | `user`, `config`, `manager`, `button`, `message`. |
| `client` / `customer` / `buyer` for one concept | Readers cannot tell whether they differ. | Pick one domain term and ban the others. |
| `userId` and `user_id` in one layer | Breaks search and mechanical refactors. | One case per layer; map only at boundaries. |
| `isActive` returning a count | The name states the wrong type. | `activeCount`. |
| `getUser` for a pure getter | Implies I/O in many conventions. | `user` property, or `fetchUser` for I/O. |
| `UserServiceImpl` | Leaks the implementation and adds noise. | `SqlUserRepository`, `StripePaymentGateway`. |
| `IUserStore` in Python or Go | Imports a C# convention into a language that rejects it. | `UserStore` or `UserDirectory`. |
| `user2`, `newUser`, `tempUser` | Numbered or temporal names rot immediately. | `importedUser`, `pendingUser`, `user`. |
| `flag`, `status`, `check` for a boolean | Vague and often wrongly typed. | `hasExported`, `isReady`, `isValid`. |
| `do`, `handle`, `process`, `run` alone | Hides what is handled or produced. | `handlePaymentFailure`, `processRefund`, `runMigration`. |

## Project Naming Table

Create this table at project start, keep it in the repository, and add a row before a term spreads:

| Term | Definition | Canonical name | Avoid | Case | Owner |
|---|---|---|---|---|---|
| invoice | A bill issued to a customer | `Invoice` | bill, statement | PascalCase | billing |
| customer | A party that pays | `Customer` | client, buyer, account | PascalCase | CRM |
| amount | Money in minor units | `amount_cents` | amount, total | snake_case | billing |

## Review Checklist

- [ ] The term matches the project naming table or glossary.
- [ ] The case matches the language and the artifact.
- [ ] The grammatical form matches the kind.
- [ ] No synonym, collision, or confusing near-name.
- [ ] No generic word left unqualified.
- [ ] Booleans are positive and actually boolean.
- [ ] Collections are plural; maps name their key.
- [ ] Units, time, money, ratios, and ranges are explicit.
- [ ] Async, error, test, and API conventions match the stack.
- [ ] File names match the primary export or responsibility.
- [ ] Database, API, config, and log names agree across layers.
- [ ] Abbreviations are allowlisted; acronyms follow language rules.
- [ ] The name is pronounceable and searchable.
- [ ] Symmetric pairs use the same words.
- [ ] Deprecation or alias path exists for a public rename.
- [ ] References, tests, docs, fixtures, and snapshots are updated.
- [ ] No rename outside the authorized scope.
- [ ] The naming table is updated.
- [ ] The linter or formatter passes.

## Examples

<example>
Naming a new HTTP resource across layers:
Database table `orders`, column `customer_id`, primary key `id`, index `idx_orders_customer_id`;
API path `/v1/orders`, query `created_after`; JSON `created_at`, `is_paid`; TypeScript type `Order`,
function `listOrders`, boolean `isPaid`; test `list_orders_test` or `listOrders.test.ts`.
</example>

<example>
Renaming a boolean:
`notDisabled` becomes `isEnabled`; `flag` becomes `hasExported`; a nullable boolean becomes a tri-state enum
(`Visibility.PUBLIC`, `Visibility.PRIVATE`, `Visibility.UNLISTED`) instead of `isPublic: boolean | null`.
</example>

<example>
Renaming a vague service:
`UserManager` handles lookup and storage. The name hides two responsibilities; split it into `UserDirectory` for
lookup and `UserRepository` for persistence, and update call sites in one scoped change.
</example>

<example>
Naming quantities:
`timeout` becomes `timeout_ms`; `amount` becomes `amount_cents` plus `currency`; `discount` becomes `discount_pct`
(0–100) or `discount_ratio` (0–1), and the range is documented in the naming table.
</example>

## References

Read [references/dimensions.md](references/dimensions.md) for the full rule set by artifact and
[references/languages.md](references/languages.md) for the per-language casing matrix. Read both before establishing
a new project's naming table; during routine work, read the dimension that applies and the language row that applies.
