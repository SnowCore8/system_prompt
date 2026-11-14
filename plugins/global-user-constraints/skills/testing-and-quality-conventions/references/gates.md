# Quality Gates

This file is the operational companion to `SKILL.md`: stack-specific commands, default thresholds, and the templates
a team adapts when it defines its gate set. Read the stack section when configuring a pipeline, the coverage
worksheet when setting thresholds, the flaky workflow when a suite becomes unreliable, and the waiver template when a
gate must be bypassed. Every command is a default; adopt the project's actual tool, pin its version, and keep the
pipeline and the local target in one definition. Blocking means the required status check fails the merge; advisory
means the result is reported and reviewed but never blocks. A stack that needs a service the runner cannot provide
documents the substitute it runs instead.

## Gate Matrix by Stack

Each row names one required check, a default command, and the threshold that makes it fail. Run these on pull
requests unless the row says otherwise; a stack that cannot run a row without a paid service documents the
equivalent it runs instead.

Two required gates have no universal command, so each stack invokes its project tooling for them:

| Cross-stack gate | Default command | Default threshold |
|---|---|---|
| Contract verification | The contract target for the changed side, for example a `contract` test marker | Any failed interaction fails; both sides must pass before deploy |
| Static application security test | The scanner named by the security policy, for example `semgrep ci` | Blocking at the policy severity; changed code on pull requests, full scan on main |

List both as required status checks beside the stack rows.

### Python

| Gate | Default command | Default threshold |
|---|---|---|
| Format | `black --check .` or `ruff format --check .` | Any diff fails |
| Lint | `ruff check .` | New violations fail; the baseline only shrinks |
| Type check | `mypy --strict` on new modules, `mypy` on baselined modules | Any error fails; a new module must stay strict |
| Unit tests | `pytest -m "not integration" --cov --cov-branch` | Suite 2 min; change coverage 80% |
| Integration tests | `pytest -m integration` | Suite 15 min |
| Dependency audit | `pip-audit` against the lockfile | High or critical with a fix fails |
| Secrets scan | `gitleaks detect --no-banner` | Any finding fails |

### TypeScript and JavaScript

| Gate | Default command | Default threshold |
|---|---|---|
| Format | `prettier --check .` | Any diff fails |
| Lint | `eslint . --max-warnings=0` | Any error or warning fails |
| Type check | `tsc --noEmit` | Any error fails |
| Unit tests | `vitest run --coverage` | Suite 2 min; change coverage 80% |
| Integration tests | `vitest run --config vitest.integration.config.ts` | Suite 15 min |
| Dependency audit | `npm audit --audit-level=high` | High or critical fails |
| Secrets scan | `gitleaks detect --no-banner` | Any finding fails |

### Java

| Gate | Default command | Default threshold |
|---|---|---|
| Format | `./mvnw spotless:check` or `./gradlew spotlessCheck` | Any diff fails |
| Lint and analyzers | SpotBugs and Checkstyle through `./mvnw verify` | New violations fail; the baseline only shrinks |
| Type check | `javac -Xlint:all -Werror` as part of compile | Any warning fails |
| Unit tests | `./mvnw test` with Surefire | Suite 2 min; change coverage 80% |
| Integration tests | `./mvnw verify -P integration` with Failsafe | Suite 15 min |
| Coverage | JaCoCo report from the same run | Line floor from the baseline; 70% branches on critical modules |
| Dependency audit | `./mvnw dependency-check:check` | CVSS 7 or higher with a fix fails |
| Secrets scan | `gitleaks detect --no-banner` | Any finding fails |

### Go

| Gate | Default command | Default threshold |
|---|---|---|
| Format | `gofmt -l .` | Any file listed fails |
| Lint | `golangci-lint run` | New issues fail; the baseline only shrinks |
| Type check and vet | `go build ./...` and `go vet ./...` | Any error fails |
| Unit tests | `go test -race -coverprofile=coverage.out ./...` | Suite 2 min; change coverage 80% |
| Integration tests | `go test -race -tags=integration ./...` | Suite 15 min |
| Dependency audit | `govulncheck ./...` | Any reachable vulnerability fails |
| Secrets scan | `gitleaks detect --no-banner` | Any finding fails |

### Rust

| Gate | Default command | Default threshold |
|---|---|---|
| Format | `cargo fmt --check` | Any diff fails |
| Lint | `cargo clippy --all-targets -- -D warnings` | Any warning fails |
| Type check | `cargo check --all-targets` | Any error fails |
| Unit tests | `cargo test --lib` with `cargo llvm-cov` | Suite 2 min; change coverage 80% |
| Integration tests | `cargo test --test integration` | Suite 15 min |
| Dependency audit | `cargo deny check advisories` | Any advisory fails |
| Secrets scan | `gitleaks detect --no-banner` | Any finding fails |

### C#

| Gate | Default command | Default threshold |
|---|---|---|
| Format | `dotnet format --verify-no-changes` | Any diff fails |
| Lint and analyzers | `dotnet build -p:TreatWarningsAsErrors=true` | Any analyzer warning fails |
| Type check | Roslyn compile with nullable reference types enabled | Any error fails |
| Unit tests | `dotnet test --collect:"XPlat Code Coverage"` | Suite 2 min; change coverage 80% |
| Integration tests | `dotnet test --filter Category=Integration` | Suite 15 min |
| Dependency audit | `dotnet list package --vulnerable --include-transitive` | High or critical fails |
| Secrets scan | `gitleaks detect --no-banner` | Any finding fails |

Name every row as a required status check in the pipeline, and run the test gate and the coverage gate from one
execution. A row that only appears in a dashboard is not a gate, and a row that runs but is not required is a
suggestion that the next deadline removes.

## Coverage Policy Worksheet

Fill this worksheet once per repository from measured values, review it quarterly and after every incident, and commit
it beside the coverage configuration. A policy that exists only in a dashboard is renegotiated in every review.

| Item | Default policy | How to set it |
|---|---|---|
| Project line floor | Measured main-branch coverage, rounded down to the nearest 5 | Read the last green main build report |
| Change floor | 80% of new and modified executable lines | Compute on the diff in the same run as the test results |
| Branch floor | 70% on modules that handle money, permissions, or data loss | List the module paths in the policy file |
| Mutation target | 60-70% on critical modules | Run the mutation tool on those modules in a scheduled job |
| Ratchet step | Raise the floor by 5 points | Raise when measured coverage stays 5 above the floor for a release cycle |
| Exclusion list | Generated, vendored, migration, and entry-point glue | Record the path, reason, owner, and expiry for each entry |
| Waiver limit | 90 days per waiver | Review at expiry, then remove it or renew it with evidence |
| Review cadence | Quarterly and after every incident | Re-measure with the pinned tool version and record the command |

- Compute change coverage as covered changed executable lines divided by all changed executable lines, measured on the
  same run that produced the test results; a separate coverage run can disagree with the suite it describes.
- Set the floor with the tool and configuration committed in the repository, because a local run and a CI run with
  different coverage tools produce numbers that are not comparable.
- Give the policy file an owner and a review trigger, so the numbers survive personnel changes and are not silently
  renegotiated by an unrelated pull request.
- Re-run the worksheet after a coverage tool upgrade, because a new tool can count generated lines or partial
  branches differently and turn a stable floor into an accidental failure.

## Flaky-Test Workflow

A test is flaky when the same commit fails on one run and passes on another in the same environment; a test that
fails only before a fix is not flaky. Move a flake through the stages below and keep it out of the blocking suite
until the cause is fixed.

| Stage | Trigger | Required action | Owner | Deadline |
|---|---|---|---|---|
| Detect | An observed intermittent failure or a repeat run with mixed results | Record the commit, the seed or input, and the failure rate | CI owner | Within 1 day |
| Confirm | A mixed result on an unchanged commit or under repeat | Open a ticket with logs and the repeat command | Test author | 2 days |
| Quarantine | A confirmed flake in the blocking suite | Remove it from the blocking set and add it to the scheduled quarantine job with the ticket | Test author | Same day |
| Assign | After quarantine | Name one fixing owner and a fix-by date | Team lead | 1 day |
| Fix or remove | Fix-by date reached | Fix the cause, or delete the test and record the coverage gap in the ticket | Fixing owner | 14 days |
| Re-enable | Fix merged | Run it 20 times green in CI, then return it to the blocking suite | Fixing owner | 2 days |

- Cap quarantined tests at five or one percent of the suite, whichever is smaller; a suite above the cap adds no new
  tests until it drops below.
- Keep the quarantine marker, the ticket, and the owner in the project's test configuration, so the next reader sees
  why the test is absent from the blocking set.
- Treat a flake caused by a race in production code as a production defect with incident severity, not as test noise.
- Do not substitute automatic retries for quarantine; a retry hides the failure from the metric that would catch it.
- Export the quarantine list next to the build status, so the team sees the debt without opening each ticket and a
  quarantine that outlives its deadline is visible in review.

## Static Analysis Severity and Baseline

Map each tool's output to these buckets once, in the tool configuration, and keep the mapping under review with the
rest of the quality policy.

| Check | Default severity | Gate effect | Baseline policy |
|---|---|---|---|
| Type check | Error | Blocks the merge | Allowed per module with a migration ticket; new modules stay strict |
| Lint errors | Error | Blocks the merge | Allowed per file; the count may not grow |
| Lint warnings | Warning | Fails the zero-new-warnings check | Existing warnings baselined; the count may not grow |
| Complexity and duplication | Warning on changed code | Review comment; blocking after adoption | Change-level only; no repository-wide baseline |
| Secrets scan | Error | Blocks immediately | No baseline; triage false positives and rotate real findings |
| Dependency audit | Error at the policy severity | Blocks per the vulnerability policy | No baseline; the policy owner accepts exceptions |
| Static application security test | Error at the policy severity | Blocks when the security policy requires it | Per-finding acceptance with an owner and an expiry |
| Formatter | Error | Blocks when the working tree differs | No baseline; format before committing |

- Generate a baseline with the tool version pinned in the repository, review the count, and commit the file beside the
  tool configuration so the baseline and the rules that produced it move together.
- Review every baseline change like code: a shrink is welcome, and a growth needs a linked reason, an owner, and an
  expiry rather than a regenerated file.
- Keep suppressions local, at line or function scope, with a reason and an expiry; a file-level suppression needs a
  named owner and a cleanup ticket.
- Re-measure after a tool upgrade and review the diff before regenerating, because new rules find new violations that
  deserve their own decision.
- Record every accepted finding with its owner, the rule that produced it, and a review date, so the security and
  quality review can read the same list instead of reconstructing it from tool output.

## Local Environment Checklist

Run this checklist against a fresh clone before changing the bootstrap or the pipeline:

- [ ] One command from a fresh clone reaches a running environment and prints the resolved versions.
- [ ] The bootstrap is idempotent and names the missing prerequisite when it fails.
- [ ] Runtime, package manager, and service versions come from pinned files.
- [ ] Container images are pinned by digest or minor tag; no `latest` anywhere.
- [ ] A devcontainer or equivalent reproduces the CI toolchain.
- [ ] `.env.example` lists every required key with a fake default; `.env` is ignored.
- [ ] Configuration validation fails fast at startup with the offending key.
- [ ] Test services expose healthchecks and tests wait with a bounded timeout.
- [ ] The test database or schema is created per run and dropped after.
- [ ] Seed data is deterministic, idempotent, and synthetic.
- [ ] The test command is the same target that CI runs.
- [ ] `make doctor` checks tools, ports, and service health.
- [ ] `make clean` removes containers, volumes, caches, and build artifacts.
- [ ] The bootstrap and the CI setup read the same pinned configuration files.
- [ ] A failed service start leaves a clear error, and the recovery step is documented.
- [ ] The full pull request gate set runs on a fresh clone without undocumented steps.
- [ ] No secret, token, or personal datum appears in committed local configuration.

## Waiver Template

Copy this template into the repository's quality policy or the pull request, fill every field, and delete the record
when the fix lands or the expiry passes.

```markdown
## Waiver: <gate> on <scope>

- Approver: <code owner, not the change author>
- Reason: <the failure and why it cannot be fixed in this change>
- Scope: <paths, jobs, or branch the waiver covers>
- Expiry: <YYYY-MM-DD, no more than 90 days out>
- Tracking: <issue key>
- Remediation: <change that removes the waiver>
```

- A waiver without an expiry date or without a named approver is invalid and is rejected in review.
- A waiver covers exactly one gate and one scope; two gates need two records.
- Never waive a secrets-scan finding or a blocked dependency vulnerability; rotate the credential, purge the history,
  or use the policy owner's exception process instead.
- At expiry, remove the waiver or renew it with new evidence; a waiver renewed without evidence is an exclusion.
- Record the waiver in the repository or the pull request, not in chat, so the next reviewer can find it and judge it.
- Land the waiver record and any gate configuration change in the same reviewed change, so the bypass and the rule
  that made it necessary are visible together.
