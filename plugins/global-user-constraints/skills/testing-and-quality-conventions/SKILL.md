---
name: testing-and-quality-conventions
description: Defines, reviews, and repairs test strategy, quality gates, static analysis, and the local development environment for any programming project. Use when planning tests for a feature, deciding which checks gate a branch and at what threshold, triaging a flaky suite, or aligning a local environment with CI. Provides project-type defaults and explicit thresholds.
argument-hint: '[path or scope]'
---

# Testing and Quality Conventions

Quality practice fails in four predictable ways: tests assert nothing and prove only that the process started, gates
are waived under deadline pressure until nobody remembers what green means, the local environment drifts from CI
until a passing build on one machine says nothing about the other, and flaky tests are retried or ignored until a red
suite is treated as weather. Each failure is cheap to introduce and expensive to reverse, because the team reorganizes
its habits around the broken gate. This skill gives one decision procedure for choosing test layers, a gate set with
honest thresholds, a policy for static analysis and dependency checks, and a rule set for a local environment that
matches CI. It applies to any language, test runner, and CI system, and it treats the suite and the pipeline as one
contract rather than two unrelated chores. It serves the engineer adding tests, the reviewer judging a green build,
and the maintainer keeping the pipeline trustworthy.

## Scope and Precedence

Apply the first rule that fits, and do not mix policies inside one scope:

1. Mandatory platform, toolchain, and compliance requirement. Test runners, CI capabilities, package-manager
   constraints, and mandatory security or regulatory checks are not optional.
2. Existing project configuration and convention. Read the CI configuration, test runner settings, coverage
   configuration, and bootstrap scripts before inventing a threshold.
3. This standard's defaults, when the two levels above are silent.
4. Personal preference, which never overrides the three levels above.

- The naming-conventions skill owns test function, file, class, fixture, and test-double names. This skill owns which
  layers exist, what each layer asserts, and how the suite gates a branch.
- The comment-conventions skill owns comments and docstrings in tests. This skill owns the assertions, fixtures, and
  failure messages, and does not restate comment rules.
- The release-operations-conventions skill owns CI/CD pipelines, environment promotion, observability, and release.
  This skill owns which gates must exist, their thresholds, and how a failure is handled at the gate.
- The code-style-conventions skill owns formatter and linter style rules. This skill owns which static checks are
  gating and at what severity.
- The security-compliance-conventions skill owns dependency vulnerability policy. This skill owns where and when the
  vulnerability scan runs as a quality gate and how a blocking finding is reported.
- The api-and-data-conventions skill owns contract design. This skill owns the contract and regression test coverage
  that a contract change requires.
- Generated code, vendored code, migration scripts, and entry-point glue are exempt from coverage and style gates.
  Record each exclusion as path, reason, owner, and expiry; keep the generated marker, and never exclude a
  hand-written source tree.
- Adopting this standard in a legacy project is a staged change, not a rewrite. Baseline the existing violations with
  a reviewed count, hold every changed file to the new rule, and delete the baseline as it shrinks. Turning on every
  gate at blocking severity at once guarantees they are all disabled within a week.
- The suite is part of the change. A behavior change adds or updates its test in the same change, and a reviewer who
  cannot see the test for a behavior change treats the change as incomplete.
- A gate is a contract: changing its command, threshold, scope, or exclusion is a reviewed change with a stated
  reason, an owner, and a linked issue. Never lower a threshold in the same change that fails it.
- When two rules conflict, state the conflict and the chosen rule; record the decision in the project's quality policy
  so the next change follows it.

## Process

1. Classify the risk first. Name what breaks if this code fails: money, personal data, safety, availability, or
   internal convenience. Risk decides the required layers and whether a gate blocks or only reports; a payment path
   and a settings label do not get the same test budget.
2. Pick the cheapest layer that can catch the failure. Prefer a unit test to integration and integration to
   end-to-end, using the Test Layer Matrix below. When only an end-to-end test can fail, record why the seam cannot
   be tested lower in the test or the ticket, so the next reviewer does not reconstruct the decision.
3. Define the gate and the threshold before writing the test. Name the command, the event it runs on, the required
   status check, the threshold, and the owner. A check with no threshold and no owner is decoration. Publish the gate
   in the project's quality policy, so a contributor can read the rule before pushing.
4. Make the test deterministic. Remove wall-clock time, randomness, network access, ordering, shared state, and
   environment differences; inject a clock, seed the generator, isolate the data, and wait on a condition instead of
   sleeping. Run the suite twice locally and compare results; a test that passed once has not shown determinism.
5. Wire it locally and in CI from one definition. Add the target to the bootstrap or build script, call that target
   from CI, and confirm both paths read the same tool versions, environment variables, and service versions.
6. Verify the failure path. Break the code or the assertion once and confirm the gate fails with a readable message;
   a gate that cannot fail is not a gate. Keep the observed failure in the pull request, so the gate has a record of
   catching something rather than a claim that it does.
7. Document the waiver policy. State who may waive which gate, the required record, the maximum duration, and the
   review that removes it; an undocumented waiver becomes a permanent exclusion.

## Core Rules

- **A test must be able to fail.** Assert observable behavior with a specific expected value. A test that only
  asserts no exception, or asserts that a mock was called without checking the outcome, cannot distinguish working
  code from broken code. An assertion that cannot name the wrong value it would catch is not testing a behavior.
- **Test behavior at the public seam.** Call the unit through the interface its callers use. Do not test private
  helpers directly; a refactor that keeps behavior unchanged must not break the suite.
- **Mock at the process boundary, never inside it.** Replace the network, clock, randomness, filesystem, and
  third-party services. Use a fake or an in-memory adapter when persistence cannot be real in that layer. Never mock
  the unit under test, a value object, or the project's own serialization. A mock that needs a dozen setup lines is a
  sign the seam is in the wrong place.
- **One reason to fail per test.** Each test covers one behavior and reports one clear failure. A test with ten
  assertions reports the first and hides the other nine; table-driven cases keep one assertion each.
- **No weakened tests.** Never delete, skip, or loosen a test to make a build green. Fix the code or record the
  defect; a weakened test is a review rejection and, when it must ship, a waiver.
- **Determinism is a gate.** A test that depends on time, ordering, network, or shared state is quarantined, not
  retried. A suite whose result varies is not evidence.
- **Coverage is a floor, not a target.** Enforce change coverage and a project floor derived from the measured
  baseline. Do not chase 100%, and do not exclude source code to reach a number. A coverage number reviewed without
  the command and tool version that produced it is not reproducible.
- **Every gate has an owner and a failure path.** Name the owner, the threshold, and what happens on failure; an
  unowned gate is the first one waived.
- **Failures stop the merge.** A red required check blocks integration. Retry only for proven infrastructure errors,
  once, and keep the first failure visible; do not merge on a retry-only green.
- **Quarantine flaky tests with a deadline.** A flaky test gets an owner and a fix-by date, leaves the blocking
  suite, and is fixed or deleted by the deadline. Retries do not count as a fix.
- **A waiver is recorded and expires.** A waiver names the gate, scope, approver, reason, and expiry date. A waiver
  without an expiry is an exclusion, and an exclusion without an owner is a defect.
- **Static checks gate at a severity the team acts on.** New violations fail; existing violations are baselined and
  the baseline only shrinks. A check everyone ignores is worse than no check, because it trains people to scroll past
  red output. When a check is noisy, fix its configuration or its baseline instead of learning to ignore it.
- **Local and CI run the same commands.** A passing local run and a failing CI run is a parity defect, not an
  acceptable difference. Fix parity before adding checks.
- **Pin versions and clean up test data.** Pin tool versions, service images, and fixtures in the repository. Use
  synthetic data with a unique namespace per run, and remove what the run creates.

## Test Layer Matrix

Use the cheapest layer that can fail for the risk. The speed budget is per test and per suite on a standard CI
runner; a test that exceeds it moves down a layer or is split. Treat the budget as a gate of its own: a test that
blows the budget is a maintenance defect even when it passes.

| Layer | Scope | Speed budget | What it may mock | Gate |
|---|---|---|---|---|
| Unit | One public function, class, or module; all I/O replaced | 100 ms per test; suite 2 min | Clock, randomness, network, filesystem, third-party clients | Required on every commit and pull request |
| Component | One module with its real in-process collaborators: router, renderer, serializer | 1 s per test; suite 5 min | Third-party network and platform services only | Required on pull request |
| Integration | One real boundary: database, queue, cache, or the project's own service over the wire | 5 s per test; suite 15 min | External providers outside the system boundary | Required on pull request for touched services |
| Contract | Request and response agreement between provider and consumer | 1 s per interaction; suite 3 min | The other side, replaced by a verified contract artifact | Required on pull request for the changed side |
| End-to-end | Entry point through persistence on a production-like stack | 60 s per test; suite 20 min | External providers via sandbox; nothing internal | Required on main; a subset on pull request |
| Smoke | Deployed artifact: health, login, one core transaction | 5 min in total | Nothing; it uses real dependencies | Required after deploy and on a schedule |
| Performance | Throughput and latency of a defined workload against a baseline | Budget per test; suite 60 min nightly | Nothing; fixed data set and pinned hardware | Required on main for critical paths, advisory otherwise |
| Property and fuzz | Generated inputs against parser, protocol, and calculation invariants | 30 s per property; suite 10 min | Same as unit; the generator supplies inputs | Nightly, plus changed parsers on pull request |

## Dimension Index

Each dimension has detailed rules, examples, and edge cases in `references/dimensions.md`; the number in the
dimension column is the section number in that file.

| Dimension | First rule |
|---|---|
| 1. Test strategy and layering | Choose the cheapest layer that can catch the failure and never mock what the layer is meant to prove. |
| 2. Quality gates and coverage | Gates block merges; coverage is a floor derived from a measured baseline, not a target. |
| 3. Static analysis and dependency checks | New violations fail, baselines only shrink, and secrets and vulnerable dependencies block. |
| 4. Local development environment | One command builds the environment, and local and CI read the same pins and targets. |

## Anti-Patterns

| Anti-pattern | Why it fails | Fix |
|---|---|---|
| Test with no assertion, or `assert True` | Proves the code ran, not that it worked; behavior can regress while the suite stays green | Assert an observable outcome for both the success and the failure case |
| Mocking the class under test | The test verifies the mock and a broken unit still passes | Test the real object and replace only its boundaries |
| Over-mocking every collaborator | The suite stays green while the system cannot run | Keep real collaborators in-process and fake only I/O boundaries |
| `sleep()` before asserting async work | Timing-dependent and slow; fails on a loaded runner | Wait on a condition or event with a bounded timeout |
| Passing coverage by excluding source | The number improves while untested code grows | Exclude only generated, vendored, migration, and entry-point glue, each recorded as path, reason, owner, and expiry |
| Waiving a red gate under release pressure | One waiver becomes a habit and the gate stops being a gate | Record a waiver with an owner and expiry; schedule the fix |
| Retrying a test until it passes | Hides a real race or a broken test and normalizes failure | Quarantine with an owner and a deadline, then fix the cause |
| Asserting that a private method was called | Locks the implementation; harmless refactors fail | Assert through the public interface and observable state |
| A whole-page snapshot as the only assertion | One unrelated change fails everything and reviewers approve blindly | Assert the fields or elements that carry the behavior |
| Testing against a shared development database | Order dependence and data drift make failures irreproducible | Create a per-run schema or container and drop it after |
| Floating tool versions such as `latest` | Local and CI disagree and the old failure returns | Pin versions in the repository and read them in both paths |
| Secrets or personal data in fixtures | Test data ships with the suite and leaks on the next share | Use synthetic values and `example.test.invalid` addresses |
| Lowering a threshold to land a change | The regression the gate exists to catch now passes | Fix the finding or record a scoped, time-boxed waiver |
| Skipping a flaky test with no owner | The regression it covered is now untested and nobody knows | Quarantine, assign an owner, and open the tracking issue |
| An end-to-end test for a unit rule | Slow, brittle, and debugged at the wrong layer | Move the assertion down and keep one end-to-end happy path |
| Updating the expected value to match current output | The test now certifies the bug and blocks the fix | Link the spec or issue that authorizes the new value, or fix the code |

## Review Checklist

- [ ] Each test states one behavior and can fail for that reason alone.
- [ ] Assertions check observable outcomes, values, and error paths, not only that a call returned.
- [ ] The lowest sufficient layer covers the behavior, and every end-to-end test is justified.
- [ ] Only process boundaries are mocked; the unit under test and the project's own contracts are real.
- [ ] The test is deterministic: injected clock, seeded randomness, no sleep, no ordering dependence.
- [ ] Test data is synthetic, namespaced per run, and removed after the run.
- [ ] Factories build the minimum valid state; no test mutates a shared fixture.
- [ ] Every required gate names its command, owner, and threshold in CI configuration.
- [ ] Coverage gates combine change coverage with a project floor derived from a measured baseline.
- [ ] This change does not lower a threshold, widen an exclusion, or grow a baseline.
- [ ] Static checks fail on new violations and the baseline did not grow.
- [ ] New direct dependencies pass the audit at the blocking severity, and the secrets scan is clean.
- [ ] Every flaky test touched by this change has an owner and a fix-by date.
- [ ] The bootstrap reaches the same tool and service versions that CI uses.
- [ ] Local and CI run the same target command, not two copies of it.
- [ ] Failure output names the failing test, the input, and the expected and actual value.
- [ ] A waiver, if present, names the gate, scope, approver, reason, expiry, and tracking issue.
- [ ] Every exclusion is one of generated, vendored, migration, or entry-point glue, recorded as path, reason,
  owner, and expiry.
- [ ] New tests finish within the speed budget of their layer in the pull request pipeline.
- [ ] The new test was observed failing before the fix and passing after it.

## Examples

<example>
A unit test for an invoice total:
`assert calculate_total(items) == 1800` over a table of empty, single-item, and boundary cases. The tax client
is replaced at the boundary; mocking the calculation would test the mock, not the arithmetic.
</example>

<example>
A contract test for an order service:
the consumer records `POST /v1/orders` expectations and the provider verifies them in its own pipeline. A field
rename fails the provider before an end-to-end test could ever see it.
</example>

<example>
Coverage on a change:
the pull request adds 120 executable lines and covers 96, so change coverage is 80% and passes; the project floor
of 75% stays untouched because the measured baseline is unchanged. Lowering the floor would hide the drop.
</example>

<example>
A flaky login test:
it passes alone and fails in the full suite because an earlier test leaves a session open. Quarantine moves it out
of the blocking set with an owner and a 14-day deadline; the fix is per-test isolation, not a retry loop.
</example>

<example>
Local parity:
`make test` and the CI job run the same target against the pinned database image, so a local pass and a CI failure
point at a real defect. Reimplementing the test command in CI configuration is how the two paths drift apart.
</example>

## References

Read [references/dimensions.md](references/dimensions.md) for the full rule set behind the four dimensions, and
[references/gates.md](references/gates.md) for stack-specific commands, default thresholds, the coverage worksheet,
the flaky-test workflow, and the waiver template. Read both before defining a project's gate set; during routine
work, read the dimension that applies and the stack section that applies.
