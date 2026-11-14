# Testing and Quality Dimensions

Use this file with `SKILL.md`. Each section gives the decisions, examples, and edge cases for one quality
dimension. When a project already has a policy, read it first and apply the higher-precedence rule; this file supplies
the default and the reason. Read the section that matches the tests you are changing or the gate you are moving.

## 1. Test Strategy and Layering

Layering decides where each risk is proven. A suite with the wrong shape either takes an hour to answer a question a
unit test could answer in a millisecond, or reports green while the integration it never crossed is broken.

- Choose the shape by project type and failure cost. A domain service uses a pyramid: many unit tests, fewer
  integration tests, and a thin end-to-end layer for critical flows. A UI product with heavy client logic uses a
  trophy: solid unit and component layers with fewer, broader integration tests. A data pipeline or CLI uses mostly
  integration tests with contract checks at its inputs and outputs. Avoid the ice-cream cone, where end-to-end tests
  dominate and every failure is debugged through a browser. Record the chosen shape in the repository's testing
  note and revisit it when the main risk changes; a shape chosen once and never reviewed becomes folklore.
- Draw layer boundaries by what is real, not by directory name. A unit test replaces every I/O; a component test
  keeps its in-process collaborators real; an integration test crosses exactly one real boundary; an end-to-end test
  crosses from entry point to persistence; a contract test checks an interface agreement without deploying both
  sides. Check the classification by asking which dependency outage the test would notice: if stopping the database
  cannot fail it, it is a unit or component test whatever folder it lives in.
- Use contract tests for every pair of deployables that share a request and response shape. The consumer records
  expectations, the provider verifies them in its own pipeline, and either side fails when the shape changes. Do not
  substitute a shared staging environment for a contract test: staging is shared, slow, and drifts for reasons that
  have nothing to do with the contract. Keep the contract artifact with the consumer and bump it deliberately, so a
  provider change produces a migration window rather than a surprise outage.
- Never mock the unit under test, a value object, the project's own serialization, database constraints and
  migrations, an authorization decision, or the behavior the test claims to prove. A unit test may replace the
  project's repository with a fake when persistence is not the behavior under test; an integration test must use the
  real engine, because a mock there proves only that the mock was called. When a fake replaces the database, run the
  real migration path against it and verify the production dialect, or the tests will approve SQL that production
  rejects.
- Never make real in a test: payment capture, email or SMS delivery, external APIs with quotas or cost, production
  data, and anything that needs a person. Replace each with a sandbox, a fake adapter at the boundary, or a recorded
  contract artifact, and keep every replacement beside the other test doubles so the fake cannot spread into
  production code. Make each fake fail on an unexpected interaction, so a newly added production call cannot pass
  silently because no test thought to assert it.
- Build test data from factories that produce a valid default and accept per-test overrides. No test mutates a
  fixture another test shares. Isolate with a transaction rollback, a per-run schema, a container, or unique
  namespaces, and delete what cannot be rolled back; a test that leaves rows behind makes the next run
  order-dependent. Prefer explicit values in assertions over randomness; a randomized failure must print its seed
  and input, or the person who sees it cannot reproduce it.
- Promote a defect upward only when the lower layer cannot see it. Reproduce the production bug at the cheapest layer
  that can fail, add the regression test there, and add at most one end-to-end guard for the uncovered path.
  Duplicating the same assertion at three layers buys no signal and triples the maintenance. Record the promotion in
  the bug ticket, with the layer, the test, and the guard, so the next similar defect follows the same route.
- Enforce a runtime budget per layer. Keep the unit suite under 2 minutes, and hold the pull request test stage to
  the project-type budget up to 20 minutes. Apply the 10-second rule to unit, component, integration, and contract
  tests: one over 10 seconds needs a stated reason and a separate job. End-to-end and property tests follow the
  per-test budgets in the layer matrix instead. Split or demote a test that exceeds its budget instead of tolerating a
  suite everyone stops running. Measure the budget in CI on a standard runner, not on a developer laptop, because
  the laptop number is not the one the pull request waits for.

Default shape by project type:

| Project type | Dominant layer | Supporting layers | Thin layer | Pull request budget |
|---|---|---|---|---|
| Domain service | Unit | Integration, contract per dependency | End-to-end on critical flows | 10 min |
| UI product | Component | Unit, contract for the API client | End-to-end on core journeys | 15 min |
| Data pipeline or batch job | Integration on a fixture data set | Unit for transforms, contract on inputs and outputs | Smoke on one full run | 20 min |
| CLI or library | Unit | Integration of the public interface | Smoke on the documented command | 5 min |
| Multi-service platform | Integration and contract | Unit for logic | End-to-end per service pair | 20 min |

| Good | Bad | Why |
|---|---|---|
| Repository test against the pinned database container | Repository test against a mocked ORM | The mock hides SQL, constraints, and migration failures |
| Table-driven unit test for the discount rule | End-to-end checkout for every discount case | The rule fails fastest where it lives |
| Consumer contract verified in provider CI | Shared staging environment treated as the contract | Staging drifts and fails for unrelated reasons |
| One fake payment adapter at the boundary | Mocking `PaymentClient` inside the service | Mocking inside the unit verifies the mock, not the charge |
| Regression test at the layer that first sees the bug | Same assertion at unit, integration, and end-to-end | Duplicates cost maintenance and add no signal |

## 2. Quality Gates and Coverage

A gate is where quality stops being a preference. The gate set must be small enough that everyone can name it and
strict enough that a green run means something; coverage is the most misused member of the set.

- Define the required gates per branch and make each one a required status check. On every pull request: format
  check, lint, type check, unit tests, integration tests for touched services, build, secrets scan, dependency audit
  at the blocking severity, contract verification for the changed side, and static application security testing on
  changed code. On main, add full end-to-end tests, the full coverage report, full contract verification, and the
  full static application security scan. On release, add smoke tests against the artifact and performance tests on
  critical paths. Name the pipeline job that implements each gate, and never let two jobs claim the same gate.
- Measure three coverage numbers and gate each honestly: line coverage for the project floor, branch coverage where
  conditions carry money, permissions, or data loss, and change coverage for the diff. Set the change floor at 80% of
  new and modified executable lines and the project floor from the measured baseline; a floor chosen from ambition
  fails the next pull request for work it did not touch. Ratchet the floor up only after measured coverage stays five
  points above it for a full release cycle, and require a scoped waiver for any fall below it.
- Exclude only generated, vendored, migration, and entry-point glue code, and record each entry as path, reason,
  owner, and expiry. Excluding hand-written logic requires a waiver, and a per-file coverage pragma needs a stated
  cause. A coverage run that excludes a file without that record is a defect, because the number then measures the
  exclusion rather than the code. Keep the exclusion list in the coverage configuration with the same review path as
  the threshold.
- Write waivers as records, not conversations. A waiver names one gate, the exact scope, an approver who is not the
  change author, the reason, an expiry no longer than 90 days, and a tracking issue. Re-review every waiver at
  expiry and either fix the finding or extend it with new evidence; a waiver renewed without evidence is an
  exclusion. Publish the open waiver list where the team reads build status, so a waived gate cannot quietly become
  the normal state.
- Handle failure through the gate, not around it. A red required check blocks merge, and the gate owner holds the
  escalation path, the dashboard, and the investigation. Retry only for a proven infrastructure error, at most once,
  and keep the first failure in the record; a pull request whose only green run came from a retry is not green.
  Review gate data every month for pass rate, duration, and waiver count, and treat a falling pass rate as a defect in
  the gate or the code rather than as noise.
- Detect flaky tests before users do: repeat the blocking suite in a scheduled job, for example 20 runs, and record
  every test whose result differs on the same commit. Quarantine a confirmed flake out of the blocking set into a
  scheduled job, assign one owner and a 14-day fix-by date, and cap quarantined tests at five or one percent of the
  suite, whichever is smaller. Treat a flake caused by a race in production code as a production defect, not as test
  noise, and do not substitute automatic retries for quarantine.
- Treat weakening a test as a review defect. Deleting, skipping, or loosening an assertion to get green requires
  evidence that the behavior change is intended, and the review must ask for a replacement assertion. A skipped
  test with no owner and no issue is untested behavior that the coverage report will not show. When the expected
  value must change, link the specification or issue that authorizes the new behavior in the test or the change
  description.
- Report what the suite does not prove. Coverage measures execution, not verification; run mutation testing on
  modules that carry money or permissions, and state the unverified paths and known risks in the delivery instead of
  presenting a green run as proof of correctness. A reviewer who reads only the check marks will assume coverage
  that the suite does not have unless the gap is written down.

Required gates by branch:

| Gate | Pull request | Main | Release |
|---|---|---|---|
| Format, lint, type check | Required | Required | Required |
| Unit and component tests | Required | Required | Required |
| Integration tests | Required for touched services | Required | Required |
| Contract verification | Required for the changed side | Required | Required |
| Coverage report | Change coverage | Full report and floor | Full report and floor |
| Secrets scan | Required, no waiver | Required, no waiver | Required, no waiver |
| Dependency audit | Changed manifests and lockfiles | Full tree, plus nightly | Full tree |
| Static application security test | Changed code | Full scan | Full scan |
| End-to-end tests | Subset | Full | Full |
| Smoke and performance | Not run | Critical paths | Required on the artifact |

Coverage metrics and their default gates:

| Metric | What it proves | Default gate |
|---|---|---|
| Line coverage | Code was executed, not that it was verified | Project floor from the measured baseline |
| Branch coverage | Both sides of each condition ran | 70% on modules with money, permissions, or data loss |
| Change coverage | New and modified executable lines were exercised | 80% on every pull request |
| Mutation score | Tests detect deliberately injected defects | 60-70% on critical modules, scheduled job |
| Contract coverage | Every changed public operation has a contract test | 100% of changed operations |

| Good | Bad | Why |
|---|---|---|
| Floor set from the last measured main build | Floor raised to an aspirational 95% | The first pull request fails for old work |
| Ratchet raised when coverage stays above the floor | Floor lowered to merge a regression | The gate now protects less than before |
| Quarantine with an owner and a fix-by date | Skip marker with no issue | Untested behavior becomes invisible |
| Waiver with a 90-day expiry and a ticket | Permanent exclude in configuration | A temporary bypass becomes policy |
| Change coverage gated on the diff | Coverage gate on the whole repository only | Old green code hides untested new code |
| Mutation testing on the payment module | Line coverage target raised to 100% | Executed lines with no assertion prove nothing |

## 3. Static Analysis and Dependency Checks

Static checks are cheap evidence: they find whole classes of defects before a test runs. They stop being useful when
the output is noisy enough that people scroll past it, so the gate is only as good as its severity mapping.

- Gate type checking everywhere the stack supports it: Pyright or `mypy --strict` on new Python modules, `tsc
  --noEmit` with strict options, Go vet and build, Rust `cargo clippy -- -D warnings`, Java compiler warnings as
  errors, and C# analyzers with warnings as errors. Hold new modules to the strict setting from their first commit,
  and baseline existing modules with a migration ticket and an owner. A type checker that runs only in the editor is
  a suggestion; the gate is what makes it a rule.
- Map every tool's severity output to three buckets once, in configuration: error blocks the merge, warning must not
  grow and is reviewed, information never blocks. Do not re-map severities per pull request; a check whose level
  changes with the author is not a gate, and a warning that nobody reads is the same as a suppressed finding. Put
  the mapping in the tool configuration file, where the next person can find it and the review can see it change.
- Bound complexity and duplication on changed code: cyclomatic complexity at most 10 per function, cognitive
  complexity at most 15, and duplication under 3% of lines with a 50-token minimum block (jscpd's default); the 3%
  ceiling is a team threshold.
  Report these on the diff, propagate them as review comments, and promote them to blocking after the codebase
  meets the threshold; turning them on blocking at adoption time blocks every pull request at once and gets the
  check disabled in a week. Exempt generated data tables and exhaustive dispatch code explicitly, with a reason
  in the configuration.
- Scan for secrets in the working tree before every commit and in CI, and scan history on a schedule. Any detection
  blocks the pipeline, including a likely false positive, which needs triage before it is suppressed. On a real
  finding, rotate the credential first and purge history under the security policy; deleting the line alone leaves
  the secret in every clone. Keep the scanner ruleset and its version pinned with the rest of the toolchain so a rule
  update is a reviewed change.
- Run the dependency audit in two places: on pull requests for changed manifests and lockfiles, and nightly for the
  full resolved tree. Fail the gate at the severity the vulnerability policy sets, and keep the policy owner
  separate from the engineer who disables the finding; the scan location and failure handling are this skill's
  responsibility, the vulnerability policy is not. Record accepted exceptions against the dependency and version,
  not against the whole tool, so a new dependency cannot inherit the exception.
- Hand security findings to their owner instead of renaming the check. A static application security test runs on
  changed code in CI; triage results, assign an owner to each finding, and block at the severity the security policy
  sets. A suppression is reviewed like code, with a reason and an expiry, and never silently added to a baseline.
  Route findings that need design work to the owning team's backlog and keep the gate result visible until the fix
  lands.
- Use the formatter as a gate in verify mode. CI runs the formatter's check mode and never rewrites files in the
  pipeline; tool choice, version pinning, and local auto-fix belong to the code-style-conventions role. Format before
  pushing and keep formatting-only edits in their own commit, so behavior reviews stay readable and a reformat from a
  tool upgrade never hides inside a feature change.
- Keep a baseline only for existing violations and only as a ratchet. Generate it once with the pinned tool version,
  review the count, and commit it beside the tool configuration. New violations fail, the baseline count only
  shrinks, and regenerating a baseline to absorb a new violation is a review defect. Re-measure after a tool upgrade
  in a separate change so that the new rules are reviewed as rules, not as anonymous baseline noise.

Baseline adoption order:

| Stage | What is enabled | Evidence required | Promotion rule |
|---|---|---|---|
| Existing code | The check runs and records its current violations | A reviewed baseline count and the pinned tool version | No new violation is allowed from the first day |
| New modules | The strict setting, with no baseline entries | A clean run on the strict setting in the first commit | The strict setting stays for the life of the module |
| Changed code | Zero-new-warnings check on the diff | A warning count that stays equal or falls | Blocking after a quarter with no regression |
| Whole repository | Blocking gate | A baseline at zero | The baseline file is deleted |

| Good | Bad | Why |
|---|---|---|
| New modules pass `mypy --strict` from the first commit | Strict mode enabled repo-wide with 4000 existing errors baselined | The strict rule never changes behavior |
| Warning count held at the current value and reviewed | Warnings ignored because "the build is green" | Warning noise grows into new defects |
| Suppression with a reason and an expiry date | Inline `# noqa` or `// nolint` with no reason | An unexplained suppression lives forever |
| Pre-commit secrets scan plus CI | Secrets scan once before release | A leaked credential is already in history |
| Formatter check in CI | CI runs the formatter and commits the fix | The diff under review is not the diff tested |
| Audit on changed lockfiles plus a nightly full scan | Audit only when someone remembers | New vulnerable transitive dependencies pass unnoticed |

## 4. Local Development Environment

A local environment is a product with one user: the next developer. If it takes a day to build by hand, people
improvise, and an improvised environment produces results that CI cannot reproduce.

- Provide one command from a fresh clone to a running environment: `./scripts/bootstrap`, `make setup`, or the
  project's equivalent. Make it idempotent, safe to re-run, loud about the missing prerequisite, and finish by
  printing the resolved tool and service versions so the first bug report includes them. Test the command on a clean
  clone or container whenever the toolchain changes; a bootstrap that only works on the author's machine is not a
  bootstrap.
- Pin every version in a file the repository owns: `.python-version`, `.nvmrc` or `packageManager`, `.tool-versions`,
  `rust-toolchain.toml`, `global.json`, committed lockfiles, and container images by digest or minor tag. CI reads the
  same pin files; duplicate version literals in a pipeline or a document always drift eventually. Review a pin bump
  like any dependency change, and state in the change why the new version is safe for the test matrix.
- Provide a devcontainer or an equivalent reproducible environment: a `devcontainer.json` with compose services, or
  Nix, Devbox, or a documented OS setup. Match the major and minor versions of the language runtime, database, queue,
  and cache that CI uses; a floating `latest` anywhere is a defect because it silently changes what the test proves.
  Prefer a container image that CI already uses, so local reproduction of a CI failure needs no translation.
- Keep one target between local and CI. CI calls `make test` rather than a second copy of the command in YAML.
  Enumerate the allowed differences, such as an ephemeral database or CI resource limits, and state them in the
  environment documentation. When a local pass fails in CI, fix the parity defect before touching the test; the
  difference is the bug until proven otherwise.
- Start test dependencies with healthchecks and wait for readiness with a bounded timeout. Create a dedicated test
  database or schema per run, apply migrations, and drop it after. Never run destructive tests against the shared
  development database, and never depend on data that a colleague happened to leave there. When a service cannot
  run locally, document the substitute and mark the tests that need the real service as integration tests.
- Commit `.env.example` with every required key, a fake default, and a one-line description; ignore `.env`. Validate
  configuration at startup and fail fast with the offending key, so a missing variable is a clear error rather than a
  default that silently changes behavior. Never put a secret or a personal value in an example file, fixture, or
  default; use synthetic values and `example.test.invalid` addresses, and scan the repository for violations of that
  rule.
- Version deterministic seed data in the repository, keep seeding idempotent, and keep it separate from test
  fixtures. Seed accounts use synthetic identities, and a `reset` target returns the environment to a known state
  that tests can rely on; data created by hand is not a fixture. Document which seed sets are safe for demos and
  which exist only to make the test suite start from a known state.
- Provide a healthcheck and a cleanup target: `make doctor` verifies tools, versions, ports, and service health;
  `make clean` stops containers, removes volumes, caches, and build artifacts. Run the same cleanup in CI teardown,
  and leave no container, process, or temporary database behind after a test run. A failed test run needs its
  evidence preserved before cleanup, so the cleanup command never runs while a debug session is using the services.

Local and CI parity matrix:

| Concern | Local | CI | Rule |
|---|---|---|---|
| Runtime version | Read from the pin file | Read from the same pin file | One source for each version |
| Database | Compose service, pinned image | Service container, same pinned image | Same major and minor version |
| Environment variables | `.env.example` plus a local `.env` | Variables set in CI configuration | Same keys; values differ only by environment |
| Test command | `make test` | `make test` | One definition, no copy in pipeline YAML |
| Test data | Seeded database plus a per-run schema | Per-run schema only | Synthetic data in both paths |
| Cleanup | `make clean` | Teardown job | Containers, volumes, and caches removed |

| Good | Bad | Why |
|---|---|---|
| Bootstrap script documented in the README | Six-step wiki page with unstated versions | The script survives; the page drifts |
| Image pinned to `postgres:16.4` | `postgres:latest` | CI and local can silently run different engines |
| Per-run schema created and dropped | Shared development database | Order dependence and data drift |
| `make test` called by CI | Test command copied into the pipeline | The copy drifts from the local target |
| `make doctor` prints resolved versions | "Works on my machine" | Versions are the first thing to compare |
| Seed data committed and idempotent | Manual SQL run once by one developer | Every later environment starts from a different state |
