# Release and Operations Dimensions

Use this file with `SKILL.md`. Each section states the rules, examples, and edge cases for one dimension; the
Good | Bad | Why table in each section shows the judgment behind the rule. When a project already has a release
policy, read it first and apply the higher-precedence rule; this file supplies the default and the reason. The
numbered sections match the Dimension Index in `SKILL.md`, and `references/playbooks.md` carries the procedures that
apply them.

## 1. Versioning and Release

- Treat semantic versioning as a compatibility statement, not a marketing number: a major version changes a public
  contract, a minor version adds capability without breaking one, and a patch version fixes behavior without changing
  one. Derive the bump from the most significant change in the release, never from the number of commits, and never
  let the release date decide it.
- Semantic versioning promises nothing before 1.0; this project's pre-1.0 policy supplies the promise. Before 1.0,
  a minor version may carry a breaking change and a patch version must stay compatible within its minor because the
  policy says so. Announce every breaking minor with the migration path, and reserve `1.0.0` for the point at which
  the project promises the contract.
- Keep one version source. Set the version from the release commit, embed it in the artifact, and let every
  environment report the same value; a promotion never rewrites it. A version computed from the branch at deploy
  time differs between environments and invalidates dashboards, support answers, and bug reports.
- Publish the cadence and the cutoff. A release train leaves on schedule, and a feature that misses the cutoff waits
  for the next train instead of delaying the release. Continuous delivery of a service still cuts a versioned release
  record, because the changelog, the support answer, and the rollback target all need one.
- Tag the approved release commit, then build the artifact from the tag. The naming skill owns tag syntax and
  artifact names; this process decides when the tag is created, which commit it points to, and which artifact digest
  it identifies. Create the tag on the approved release commit, build in a clean checkout, run the gates, and
  publish only after the gates pass and the artifact is verified to match the tag; delete the tag before publication
  if the gates fail, because a published artifact must trace to a tag that passed.
- Name the approver per release type, publish the freeze windows (financial close, peak season, holidays), and state
  the exception authority and the change classes still allowed inside a freeze. A hotfix is allowed during a freeze,
  but it needs the exception record, not a quiet bypass.
- Set release-note ownership and timing. The documentation skill owns the release-note and changelog documents; this
  process requires the user-visible behavior, required migration steps, removed deprecations, and known issues to be
  written before approval, and the final publication to match the artifact that shipped. A note written after the
  deploy cannot gate the go or no-go decision.
- Publish the compatibility promise: the supported versions, the fix window (for example the current major plus the
  previous major for security fixes), the minimum deprecation notice, and the upgrade path. A promise is a
  commitment; when it cannot be met, amend it in writing before the release, not after a customer asks.

| Good | Bad | Why |
|---|---|---|
| `1.4.0` for a new optional endpoint | `1.4.1` for a new endpoint | A patch that adds capability breaks the constraint consumers read. |
| `2.0.0` with a migration guide and a removal date | `1.9.9` labeled a small breaking change | A break must reach consumers before it lands. |
| Tag on the approved commit, artifact built from the tag | Artifact built first and tagged afterward | The tag must point at the commit whose build passed the gates. |
| Freeze dates published with the exception approver | Freeze known only to the release manager | A team that cannot see the freeze plans work inside it. |
| Release note approved with the release | Notes written after the deploy | The note cannot inform the go decision it describes. |
| Supported versions and fix window in the release policy | "Always upgrade to latest" | Consumers cannot plan a fix window from a slogan. |

The cadence follows the product and the audience; state the choice and its version behavior in the release policy:

| Cadence | Use when | Version behavior | Approval |
|---|---|---|---|
| Continuous deploys | Service with feature flags and fast rollback; users see small changes often | Each deploy is an immutable artifact; a version is cut from the train for the changelog and support | Automated gates plus the on-call owner |
| Weekly train | Product with a user-visible changelog and many contributors | One version per train from the cutoff commit | Release owner |
| Monthly or quarterly | Mobile app, regulated product, or a long external test cycle | Longer soak, wider freeze, and a formal sign-off | Product owner plus release owner |
| Long-term support line | Library or platform with external consumers | Patch-only line; new features go to the next major | Security owner plus release owner |

The release policy records the semantic-version rule, the chosen cadence row, the freeze calendar, the support
window, and the approver per release type, and the repository entry point links that policy. A rule kept only in the
release manager's calendar cannot be applied by the next release.

## 2. Change Management

- Classify every change as breaking, behavior-changing, or internal at merge time, and record the classification
  where the release tooling reads it. The version bump, the notice window, and the approval level all derive from the
  class, not from the author's confidence, and one release should carry one class of change where possible because a
  bundle widens the rollback scope.
- Treat these as breaking: a removed or renamed public name; a changed required parameter, default, or response
  shape; a changed event schema; a changed permission, quota, or rate limit; and a changed behavior of a documented
  workflow. Update the test that asserts the old behavior in the same change; deleting it silently converts an
  intended break into an accident.
- Set the minimum notice per surface: one major release or six months for a public API, one minor release for a CLI
  flag, one release for an internal service contract, and one release for a configuration default. A deprecated path
  keeps working, receives critical fixes, and warns at use; removing it early is a breaking change with no notice.
- Announce on three paths: where the old path is used (runtime warning, interface note, documentation of the old
  path), where users plan upgrades (release note and migration guide), and directly to contract-bearing consumers who
  must act. Choose the audience and the channel for each path; relying on one channel is an assumption, not a
  communication plan.
- Give every feature flag an owner, a purpose, a default, and a removal release. New behavior defaults off, a flag
  never replaces a permission check, flags do not nest, and a name is never reused. The naming skill owns the name
  format; this process owns the lifecycle, and removal is part of the release where the ramp completes.
- Require a migration path with every break: a mapping from the old name, field, or behavior to the new one, a
  mechanical step where one is possible, a rollback for the migration itself, and a rehearsal on production-shaped
  data. Telling users to rewrite their client is not a migration path.
- Schedule the communication: announcement date, reminder at the midpoint, and removal date, with the reminder as a
  process step because the audience forgets. Measure reach by responses and support tickets, not by messages sent; a
  notice with no measured reach is a hope.
- Write the rollback criteria before the deploy: error rate, latency, business conversion, evidence of data
  corruption, and support volume. Prefer rollback when the cause is unknown and the previous version is healthy, and
  prefer a forward fix when a rollback would reverse a completed data migration. Cap the time from trigger to action
  and name the authority that calls it.

| Good | Bad | Why |
|---|---|---|
| Classification recorded on the change before merge | "It is probably not breaking" in review | The bump and the notice depend on the class. |
| Deprecated flag warns at use for one minor release | Flag removed in the next patch | Users lose a path with no planning window. |
| Three announcement paths with named audiences | One changelog line for a breaking API change | Most affected users never read the changelog. |
| Flag deleted with its old code path in one release | Flag kept after launch "just in case" | The second path stays untested and unmaintained. |
| Migration mapping table and a rehearsal record | "Update your integration accordingly" | The mapping is the work the user must do. |
| Rollback trigger and authority written before deploy | Debating the rollback during the incident | A decision made under pressure is slower and worse. |

The default notice periods by change class; a project may lengthen them, and shortening one needs a recorded
exception:

| Change class | Notice window | User action | Evidence of announcement |
|---|---|---|---|
| Breaking public API or data format | One major release or six months | Code or configuration change | Deprecation notice, runtime warning, migration guide link |
| Behavior change with visible output | One minor release | Review and adjust expectations | Release note and affected documentation |
| CLI flag or configuration key removal | One minor release | Script or configuration update | CLI warning plus reference page update |
| Internal service contract change | One release, coordinated across consumers | Deploy ordering or client update | Changelog entry for internal consumers |
| Data model change with backfill | The longest applicable deprecation window | Data migration | Migration guide and rehearsal record |

The change ledger records the class of every change, the notice window it takes, the announcement dates, the
deprecation pages, and the rollback criteria per release. A change whose class is known only to its author has no
notice and no migration path.

## 3. CI/CD

- Fix the pipeline stages and their required order: clean checkout of the tagged release commit, static checks, one
  build that records the artifact digest, tests against that artifact, integration and end-to-end checks, publish
  with signature and bill of materials, deploy to development, promote to staging, acceptance check, recorded
  approval, deploy to production, and post-deploy verification. Independent stages run in parallel, the build always
  precedes the tests, and the published artifact is the one that was tested.
- Order stages fastest-failure first: cheap, deterministic checks before slow, environment-dependent ones, and a
  failing stage stops everything after it. Fix a flaky stage or quarantine it with an owner and an expiry date;
  retrying until green converts a defect into noise and teaches the team to bypass the pipeline.
- Make the build hermetic: pin toolchain and dependency versions, use a lockfile against a registry of record, deny
  network access beyond that registry, and build from a clean checkout with no local state. Record the commit,
  toolchain, and lockfile with the artifact, and state explicitly where the build is not bit-reproducible.
- Publish each artifact to an immutable registry, tag it by digest as well as version, and never mutate or delete an
  artifact that a recorded release points to. Retain every production artifact at least for the rollback and support
  window, and retain pre-release artifacts long enough to debug the release they came from; an artifact retention
  shorter than the rollback window makes the documented rollback impossible. Cache only immutable dependencies keyed
  by the lockfile hash, never build outputs or test results across commits.
- Promote the same artifact through development, staging, and production, and keep environment definitions in
  version control with their differences listed and reviewed. Staging must be production-shaped: anonymized data,
  matching topology and dependencies where feasible. Promotion to production needs a recorded approval against a
  specific digest, and no manual configuration edit bypasses it.
- Choose the deploy strategy by risk and state: rolling for a stateless service with N-1 compatibility, blue-green
  for fast cutover and rollback where double capacity exists, and canary where a success metric and enough traffic
  can detect a bad release. Write the percentage, duration, success metric, and abort criteria before the deploy;
  every strategy needs a rollback that redeploys a retained artifact rather than rebuilding one.
- Keep database migrations compatible with the rollback: expand, migrate, contract, so the previous application
  version can run against the new schema for the length of the rollout. A migration that drops or renames a column in
  the same release as the code change removes the rollback option and must be approved as irreversible.
- The pipeline consumes credentials that the security process owns and must never expose them; never print one in a
  configuration diff, log, artifact label, or test output. A change to pipeline configuration or deploy permissions
  is a privileged change and needs the same review as code.

| Good | Bad | Why |
|---|---|---|
| Tests run against the built artifact | Tests run against the working tree, then a separate build ships | The shipped bytes were never tested. |
| Digest promoted to production with an approval record | Production deployed from a rebuilt branch | The deployed artifact is not the reviewed one. |
| Lockfile pinned and registry restricted | Floating dependency versions resolved at build time | A dependency change lands without a review. |
| Artifact retained through the support window | Last release overwritten in the registry | The documented rollback has no target. |
| Staging with anonymized production-shaped data | Staging with a different database engine | The release passes only on the environment it was tuned for. |
| Rollback job deploys a retained digest | Rollback means re-running the build | A rollback should not depend on the build being reproducible now. |

The stage contract; a stage that cannot produce its evidence does not pass:

| Stage | Required result | Fails when | Evidence recorded |
|---|---|---|---|
| Validate | Format, lint, and type checks pass | Any check reports a finding | Report plus exit code |
| Build | One artifact with a digest and bill of materials | Inputs are unpinned or the artifact is nondeterministic | Digest and input manifest |
| Verify | Unit, integration, and end-to-end checks pass on the artifact | A check fails on the artifact | Test report |
| Publish | Immutable, signed registry entry | A tag is mutated or the signature is missing | Signature and retention entry |
| Promote | Same digest deployed with the environment configuration applied | A rebuild or a manual configuration edit occurs | Approval and configuration diff |
| Verify production | Smoke checks and success metrics stay within threshold | A metric leaves the written range during the bake time | Deploy record and dashboard snapshot |

The pipeline definition records the stages, their order, the artifact digest rule, the retention window, the
environment differences, and the secret sources. An undocumented pipeline is rebuilt by guesswork at the first
platform change.

## 4. Observability

- Emit structured log events, one per request or state transition, with stable fields for time, level, service,
  version, event, correlation ID, and error code. Define the levels: error means an action is needed, warn means
  degraded but handled, info means a state change worth auditing, and debug stays off in production and is sampled
  when enabled. Log enough to diagnose a single request without logging secrets or unmasked personal data.
- Instrument the four signals for every service (traffic, errors, latency, saturation) plus one business metric per
  critical journey. Bound the cardinality: never use a user ID, request ID, email address, or raw URL as a metric
  label, and use histograms with explicit buckets rather than averages. The naming skill owns metric and field names;
  this process owns the design, units, and label policy.
- Propagate a correlation ID from the edge through every synchronous and asynchronous hop, include it in logs and
  error responses, and return it to the user for support. Sample every error and a percentage of successes, keep
  trace attributes free of secrets and personal data, and treat a boundary that drops the ID as a defect.
- Define SLIs from the user's experience: the success ratio of valid requests, latency at the percentile the
  experience requires, and the availability of the critical journey. Set one to three SLOs per service with a target
  and a rolling window, derive the error budget, and review the targets quarterly and after every incident.
- Write the error-budget policy before the budget burns: state what happens as it is consumed (feature releases
  freeze, reliability work takes priority, deploy approval rises for the affected service). An SLO without a
  consequence is a dashboard decoration, and a budget that nobody measures cannot be defended.
- Alert on user-visible symptoms or on the burn rate of an SLO, not on raw resource values, and give every alert a
  severity, an owner, a runbook, and an expected action. Delete or downgrade an alert that nobody acts on; route by
  severity so that a warning never pages a human at night.
- Keep dashboards as code: version each dashboard, review it like code, provision it from the pipeline, and give each
  service one dashboard with the four signals, the SLO state, the deployed version, and dependency health. A
  hand-edited dashboard is lost at the next provision, and a dashboard without the deployed version cannot explain a
  change.
- Set retention per signal from the incident, audit, and cost needs. Keep every signal long enough to diagnose an
  incident detected late: for example, 30 days of logs, 13 months of SLO aggregates, and a trace window measured in
  days. A retention window shorter than the detection window is a defect, and audit retention follows the
  retention policy that security owns.

| Good | Bad | Why |
|---|---|---|
| SLO based on successful user requests | SLO based on process uptime | A process can be up while every request fails. |
| Canary watched through the release success metric | Canary judged by "no errors in the log" | The absent signal is not a passing signal. |
| Alert names the runbook and the expected action | Alert says "CPU high" with no action | The responder cannot decide what to do. |
| Correlation ID returned to the user | A support ticket asking for the timestamp | Support cannot find the request without an ID. |
| Dashboards provisioned from the repository | Dashboard edited in the UI only | The next provision reverts it and nobody notices. |
| Masking applied before a log line leaves the process | Email addresses written to logs and masked on search | The data is already in the store and cannot be un-leaked. |

The signal contract; if a signal cannot answer its question, redesign it before the release:

| Signal | Question it answers | Example | Failure mode when absent |
|---|---|---|---|
| Log event | What happened to this request | `order.create.failed` with correlation ID and error code | Debugging restarts from guesswork |
| Metric | Is the service healthy now | Error ratio and latency histogram by endpoint | The rollout cannot be judged |
| Trace | Where the time went | Span tree from edge to database | The slow dependency hides for days |
| Business metric | Did users succeed | Checkout success ratio per release | Technical health masks a product failure |

The observability document records the SLIs, targets, windows, error-budget policy, alert severities and owners, the
dashboard source of truth, and the retention per signal. A dashboard that exists only in the tool has no review and
no history.

## 5. Incident Response

- Set severity from user impact, not cause: SEV1 for a full outage, data loss, or an actively exploited security
  issue; SEV2 for a major function or a large user subset degraded with no workaround; SEV3 for the same impact
  where a workaround exists; SEV4 for minor impact; and SEV5 for a request with no service impact. Assign severity
  at triage, page according to the matrix, and change it only with new evidence while recording the change and the
  time.
- Staff a named primary and secondary on-call for every rotation, publish the schedule and the handoff notes, and
  define an escalation chain with timeouts; a page that nobody acknowledges escalates automatically. Review alert
  volume and on-call load monthly, because a rotation that is paged for noise stops reading pages.
- Name one incident commander for every SEV1 and SEV2. That person coordinates, decides, and communicates, and is
  not the person debugging; the roles are incident commander, operations lead, communications lead, and scribe. The
  commander declares severity, approves user-visible statements, and closes the incident.
- Communicate on a schedule: first update within the policy target for the severity (15 minutes for SEV1 and SEV2 is
  a common default), then every 30 minutes until resolution. State impact, what is being tried, and the next update
  time without speculation; the communications lead drafts and the commander approves before anything reaches users.
- Mitigate before analyzing root cause: stop the harm first with a rollback, a flag, a scale-out, a failover, or a
  rate limit. Preserve evidence before the mitigation destroys it by snapshotting logs, capturing the failing
  request, and recording times; a mitigation that hides the cause is acceptable while the cause is fixed, provided
  the evidence survives.
- Require a postmortem for every SEV1, SEV2, data-loss, and security incident. Draft it within five business days
  and cover impact, timeline, detection, contributing causes, what worked, and actions; the documentation skill owns
  the template, this process owns the requirement, the deadline, and the review meeting.
- Track every action with an owner, a due date, a tracking item, and a verification step, and review open actions at
  every release and at the next incident. A repeated incident reopens its actions at a higher priority, and an
  action that is not verified is not done.
- Apply the blameless policy: assume that people acted reasonably given the information, tooling, and time
  available. Name system causes rather than individuals as causes; accountability applies to follow-through on
  actions and to honest reporting of the timeline, not to punishment for a human error. A deliberate policy
  violation is still a management matter, and it is still not a technical root cause.

| Good | Bad | Why |
|---|---|---|
| Severity assigned at triage from the matrix | Severity raised after the fix out of embarrassment | The paging and communication level drifted late. |
| Commander coordinates while an engineer debugs | The debugging engineer also runs communications | Both jobs slow down and updates stop. |
| Status update states impact and next update time | "We are looking into it" with no time | Users cannot decide whether to wait. |
| Rollback first, root cause after the mitigation | Root cause hunt while the outage continues | Users absorb the cost of the investigation. |
| Action items with owner, date, and verification | Postmortem ends with lessons learned | Nothing changes and the incident repeats. |
| Postmortem describes the missing guardrail | Postmortem names the engineer who deployed | Naming a person hides the system cause. |

The incident roles; name someone explicitly rather than assuming the team will self-organize:

| Role | Owns | Does not own | Required at |
|---|---|---|---|
| Incident commander | Decisions, severity, coordination, closure | Debugging the system or writing code | SEV1 and SEV2 |
| Operations lead | The technical mitigation and the fix | User communication | SEV1 and SEV2 |
| Communications lead | Status page, internal channel, and update cadence | Technical decisions | SEV1, and SEV2 when users are affected |
| Scribe | Timeline, decisions, action items, and evidence references | Any decision | SEV1 and SEV2 |
| Executive sponsor | External commitments and staffing | Operational choices | SEV1 when external commitments exist |

The incident policy records the severity matrix, the paging targets, the rotation and escalation path, the update
cadence, and the postmortem deadline. A severity table that exists only in a chat message is rediscovered during
the next incident.

## 6. Backup and Recovery

- Back up every data store that cannot be reconstructed, including the primary database, object storage, and
  message data whose loss changes state. Include configuration and infrastructure state that is not in version
  control and the metadata needed to decrypt and restore data. Derived data may be rebuilt when the rebuild time
  fits the RTO, and that choice is recorded with the RTO.
- Set the frequency from the RPO and apply the retention that the retention policy requires, covering the recovery
  window, the rollback window, and the compliance obligation. Keep at least one immutable, off-site copy so that a
  deletion, a compromised credential, or a regional failure cannot destroy every copy. A retention period that
  expires before the next drill cannot be tested and is therefore not a recovery plan.
- Publish the recovery point objective (the newest data a restore may lose) and the recovery time objective (how
  long a restore may take) per data class, run a restore drill at least quarterly and after every change to backup
  scope, restore to an isolated environment, and measure the actual duration against the target. Record the result,
  the failed step, and the gap; a drill that restores only part of the data tests only part of the plan.
- Verify restores, not backup jobs: compare checksums or row counts, run application-level smoke queries, confirm
  that the encryption keys are available to the restore target, and check that the restored state is the expected
  point in time. A successful backup job is not evidence that the restore works, and an unverified backup is a
  hypothesis.
- Encrypt backups at rest and in transit, store keys separately from the data, restrict restore permission to a
  named role, and log every restore. Never copy production data to an unencrypted scratch environment; the security
  skill owns the key policy and access review, and this process enforces them in the drill.
- Define the point-in-time recovery window and granularity, test recovery to a timestamp before and after a bad
  write, and document which operations PITR cannot reverse. A PITR window shorter than the time it takes to detect
  data corruption is useless, and the detection time comes from the observability rules.
- Name the disaster recovery owner, the contact tree, the failover criteria, the alternate region, and the
  data-loss statement for a regional failure. Exercise the plan annually and after any infrastructure change; the
  documentation skill owns the plan document, and this process owns its content, its review date, and the exercise.
- Resolve data deletion against backup retention in writing: a deletion either propagates to backups or the policy
  states the maximum time a deleted record survives in one. The security skill owns the retention policy and the
  legal obligation, the API and data skill owns the deletion mechanism, and this process owns the backup schedule
  and the restore path that satisfy both. A restore overwrites live data, so it needs the authority of a destructive
  change, with the current state archived first and a verification plan approved before it starts.

| Good | Bad | Why |
|---|---|---|
| Restore drill quarterly with measured RTO | Backup dashboard green with no restore attempt | A green job does not prove readable, complete data. |
| Immutable copies in a second region | One copy in the same account and region | A single credential or region failure destroys both. |
| Deletion policy states backup expiry | Deleted record reappears from a six-month backup | Users asked for deletion and did not get it. |
| Restore to production is a destructive change | Restore run by whoever finds the script | The current data can be overwritten without approval. |
| PITR tested before and after a bad write | PITR enabled and never exercised | The window and granularity are assumptions. |
| DR plan exercised annually with a named owner | Plan written once and filed | The contact tree and failover steps are stale. |

The recovery objective by data class; a class without an objective has no backup decision behind it:

| Data class | RPO | Backup method | Retention | Restore test |
|---|---|---|---|---|
| Transactional store | Minutes | Continuous log shipping plus daily full | Support window plus one quarter | Full restore quarterly |
| Object storage and user files | One hour | Versioning plus cross-region replication | Version window per policy | Sample restore quarterly |
| Configuration and infrastructure state | None if versioned | Version control plus state snapshots | Indefinite history | Restore to scratch on change |
| Audit and compliance records | No loss accepted | Append-only store plus export | Per compliance policy | Annual restore check |
| Derived and analytics data | One day | Rebuild from the source of truth | Rebuild window | Rebuild instead of restore |

The recovery plan records the scope, the RPO and RTO per data class, the retention, the key ownership, the drill
schedule and results, the disaster recovery owner, and the deletion policy as it applies to backups. A plan that
nobody has exercised is a hypothesis with a filename.
