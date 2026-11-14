---
name: release-operations-conventions
description: Defines, reviews, and repairs release and operations practice for a software project, covering version policy, change management, CI/CD, observability, incident response, and backup and recovery. Use when cutting or approving a release, planning a rollout or rollback, designing telemetry and alerting, handling an incident, or proving a restore.
argument-hint: '[path or scope]'
---

# Release and Operations Conventions

Release and operations failures are the most expensive defects a project carries: a bad deploy harms users who never
saw the change, an undetected incident runs until a customer reports it, and an untested restore turns a recoverable
outage into permanent data loss. Each failure is cheap to prevent with a defined process and expensive to repair
after the fact, and each is a process gap rather than a coding error. This skill defines that process: how a version
is chosen and a release approved, how a change is announced and deprecated, how one artifact is built and promoted,
what telemetry proves that a release worked, how an incident is run, and how a restore is proven. It owns the
release process, the version policy, and the design of telemetry and recovery, and it hands every artifact it does
not own to the skill that does.

## Scope and Precedence

Apply the first rule that fits, and do not mix standards inside one scope:

1. Mandatory legal, regulatory, contractual, and platform requirements. Data-deletion duties, license obligations, a
   signed support window, and the deploy interface of the hosting platform are not optional; record each one where
   the release process reads it.
2. The project's written release policy and its live pipeline, environment, runbook, and alert configuration. Read
   the version source, CI configuration, environment definitions, and the last two incident records before
   inventing a rule.
3. This standard's defaults, when the two levels above are silent.
4. Personal preference, team habit, and the convenience of the current toolchain, which never override the three
   levels above.

- Version names and tags. The naming skill owns release tags, metric names, log and event field names, and version
  identifiers; this skill owns the release process, the version policy, and the telemetry design. Send naming
  questions there and process questions here.
- Release documents. The documentation skill owns changelog, release-note, runbook, and postmortem documents and
  their templates; this skill owns what must be recorded and when those documents are updated in the release and
  incident flow.
- Change to release. The version-control collaboration skill owns branches, pull requests, review, and ownership;
  this skill owns how a reviewed change becomes a release, including the approval and the freeze that gate it.
- Gates and stages. The testing and quality skill owns gate thresholds and coverage policy; this skill owns the
  pipeline stages, their required order, environment promotion, artifacts, and rollout controls.
- Product and API versions. The API and data skill owns API versioning and schema safety; this skill owns the
  product version, the compatibility promise, and the release cadence. A release that ships an API version follows
  both.
- Access and authority. The security and compliance skill owns credentials, secret storage, disclosure, retention
  policy, and compliance; this skill owns deploy permissions and rollback authority, and consumes the credentials
  that the security process issues.
- Infrastructure-managed settings are exempt. Retention, replication, autoscaling, and backup scheduling performed
  by a managed platform stay with the platform owner; cite the platform contract, do not copy its values into the
  project, and record the boundary in the service runbook.
- A release is not reversible by default. Every irreversible operation needs a tested rollback path or an explicit,
  recorded accepted risk; when a rollback is impossible, the approval level rises and the rollout narrows.
- When two rules conflict, state the conflict and the chosen rule, record the decision in the release policy, and
  apply the same choice to the next release.

## Process

1. Classify the change and the release. Name the artifact, the affected users, the compatibility impact, and the
   release type from the Release Model Matrix; a change that touches data, credentials, or the schema also names
   its security and data owners.
2. Read the current state. Open the version source, pipeline configuration, environment definitions, SLOs, alert
   rules, runbooks, and the last incident record before deciding anything; the process that exists constrains the
   process that should exist.
3. Decide the version and the compatibility promise. Apply the version-bump rule, name the previous version that
   must remain supported, and mark every breaking change and deprecation with its removal release.
4. Assemble the evidence. Confirm that the required gates passed, the artifact is reproducible, the rollout and
   rollback are written, and the telemetry that proves success exists before the first deploy.
5. Update the records in the same change. Record the release content, the approval, the rollout plan, and the
   rollback trigger; update every runbook, dashboard, alert, and document that the change makes stale.
6. Rehearse what has not been run. Promote through staging with production-shaped traffic and data, run a restore
   drill when the change touches stored data, and exercise the rollback path once where the release is
   irreversible.
7. Release, observe, and close. Deploy the approved artifact, watch the success metric for the full bake time, roll
   back on the written trigger without renegotiation, and record the outcome and the action items before the next
   release.

## Core Rules

- **Build once, promote the artifact.** The bytes that pass staging are the bytes that reach production; rebuilding
  per environment reintroduces untested differences and makes the rollback target ambiguous.
- **Version by impact, not by activity.** A patch fixes behavior without changing a contract, a minor adds a
  capability without breaking one, and a major changes a contract; a version that does not match its content
  invalidates every dependency constraint that reads it.
- **Make every release reversible or explicitly one-way.** Define the rollback path, its data implications, and the
  decision authority before the deploy; a release with neither a rollback nor an accepted risk is not approved.
- **Publish freeze windows and enforce them.** A freeze names the dates, the exception authority, and the change
  classes still allowed; an unstated freeze is discovered by the deploy that fails during it.
- **Automate the path, gate the exception.** The pipeline runs the same stages for every release, and a manual
  override needs an approver, a reason, and a recorded deviation from the standard path.
- **Publish the compatibility promise.** State which versions receive fixes, how long a deprecated path remains,
  and what an upgrade requires; a promise made in one release is a commitment for every following one.
- **Announce deprecation where users see the old path.** A changelog entry reaches too few people; emit a runtime
  warning, update the page that shows the old path, and name the removal release and date.
- **Treat flags as temporary.** Every flag has an owner, a default, a removal trigger, and a cleanup release; a flag
  that outlives its release becomes an untested branch and a permanent second code path.
- **Observe with signals that decide.** Name the success metric, the error rate, the latency, and the business
  signal that prove the release worked, and define the threshold that turns each into a rollback trigger.
- **Alert on symptoms that require action.** Page a human only for a condition that a human can act on, with a
  runbook; a noisy alert trains the rotation to ignore the one that matters.
- **Run every incident against a clock.** Record first alert, acknowledgement, mitigation, and resolution in
  minutes; an incident review without a timeline cannot separate detection from response.
- **Record and learn from every severe incident.** Severity determines the response, the communication cadence, and
  whether a postmortem is required; action items carry an owner and a date and are reviewed at the next release.
- **Prove the backup by restoring it.** An untested backup is a hypothesis; run a restore drill on a schedule and on
  every change to backup scope, and record the measured RPO and RTO.
- **State environment parity as a risk.** Staging and production differ in data, scale, and configuration; the
  release plan names which differences are accepted and how each one is tested.

## Release Model Matrix

Choose the row that matches the impact of the change, not the urgency of the request. The matrix is the default; a
project release policy may tighten it, never relax the rollback or approval columns.

| Release type | Version bump | Approvals | Rollout | Rollback | Communication |
|---|---|---|---|---|---|
| Major, breaking contract | Major | Release owner plus the owners of every consumer surface; security when data or access changes | Canary then full, with the migration window announced before rollout | Redeploy the previous major and reverse the migration, both tested | Release note with upgrade steps, deprecation list, and support window |
| Minor, backward-compatible feature | Minor | Release owner plus the service owner | Rolling deploy of the promoted artifact | Redeploy the previous version; no data reversal needed | Release note and changelog entry; no user action |
| Patch, backward-compatible fix | Patch | Release owner | Rolling deploy | Redeploy the previous patch | Changelog entry; release note only when the fix is visible |
| Pre-release, alpha, beta, or release candidate | Pre-release suffix | Release owner alone | Opt-in channel, never the default audience | Discard the pre-release; no rollback promise | Announcement that names the promotion criteria |
| Hotfix for a production defect | Patch | On-call lead plus release owner; security when the defect is exploitable | Fastest safe path, canary when the defect touches data | Redeploy the previous version; the fix stays on its branch for the retry | Incident channel update, then a release note and a postmortem when severe |
| Security fix | Patch, or major when the fix breaks a contract | Security owner plus release owner, coordinated with the disclosure schedule | Staged, with the disclosure date held until the fixed artifact is available | Roll forward by default; roll back only when the previous build is not the vulnerable one | Security advisory and release note, sent on the disclosed timeline |
| Rollback deployment | None | On-call authority, recorded after the decision | Immediately to the affected scope | None further; the previous artifact is already live and a forward fix follows as a new release | Status page update and incident note; changelog only for the forward fix |
| Configuration or flag change | None | Service owner | Staged percentage ramp | Flip the flag or restore the previous value | Note in the release record; user-facing only when behavior is visible |

## Dimension Index

Each dimension has detailed rules, examples, and edge cases in `references/dimensions.md`; the number in the
dimension column is the section number in that file.

| Dimension | First rule |
|---|---|
| 1. Versioning and release | Choose one product version per artifact and bump it by compatibility impact. |
| 2. Change management | Announce, deprecate, and remove a breaking change on a published schedule. |
| 3. CI/CD | One pipeline builds one reproducible artifact and promotes it through environments. |
| 4. Observability | Design telemetry so a release can be judged and an incident diagnosed. |
| 5. Incident response | Severity decides who is paged, who leads, and how often users hear from you. |
| 6. Backup and recovery | Back up what a restore needs and prove the restore on a schedule. |

## Anti-Patterns

| Anti-pattern | Why it fails | Fix |
|---|---|---|
| Rebuilding the artifact per environment | The tested bytes differ from the shipped bytes and the rollback target is unknown | Build once, promote by digest, and never rebuild the same commit for production |
| Deploying inside a freeze with no exception record | The freeze loses its meaning and the exception cannot be reviewed | Record the exception, its authority, its reason, and its rollback plan |
| "Roll back if needed" with no command | The undo is designed during the outage, which is the worst time | Write the rollback steps, data impact, and verification before the deploy |
| Choosing the version bump after the tag | The bump reflects the release date rather than the compatibility change | Decide the bump from the change classification before merging |
| Changelog assembled from the commit log | Users cannot find the change that needs their action | Record user-visible changes and required actions; the log is not the record |
| Keeping a flag after full rollout | Two code paths remain, one of them untested and unmaintained | Give every flag a removal release and delete it when the ramp completes |
| Deprecation announced only in the changelog | Users see the removal at upgrade time, after their planning window closed | Announce where the old path is used, with the date and the replacement |
| Printing pipeline credentials into logs | A credential exposed by the pipeline is exposed to everyone who can read the log | Never expose credentials in pipeline logs, artifacts, or output; security owns where they come from |
| Alerting on every error | The rotation ignores pages and misses the one that matters | Alert on symptoms with a runbook and a threshold tied to an SLO |
| Scoring an SLO with no owner or review | The target drifts from user experience and nobody notices | Assign an owner, a review cadence, and an error-budget policy |
| Setting severity after the fact | Paging and communication drift with the responder's mood | Assign severity from the matrix at triage and change it only with evidence |
| Postmortem with no tracked actions | The same incident recurs while the document records regret | File action items with owners and dates and review them at the next release |
| Counting backups without restoring them | The backup may be corrupt, incomplete, or unreadable | Run a restore drill, measure RPO and RTO, and record the result |
| Deploying from personal credentials | The deploy cannot be tied to a role and rollback authority is unclear | Use role-based deploy identities and record the approver and the operator |
| Shipping a visible change through a config-only release | A behavior change bypasses versioning, compatibility review, and release notes | Classify the change by user impact and use the matching release type |

## Review Checklist

- [ ] The version bump matches the compatibility impact of the change.
- [ ] The release type, approvals, and rollout match the Release Model Matrix.
- [ ] The previous version and its support window are named.
- [ ] Breaking changes and deprecations name a removal release, a date, and a migration path.
- [ ] The pipeline builds once and promotes the same artifact to every environment.
- [ ] Build inputs are pinned and the artifact is reproducible from a clean checkout.
- [ ] Stages run cheapest-failure-first, and required gates pass before promotion.
- [ ] The pipeline consumes the credentials the security process owns and never exposes them in logs or artifacts.
- [ ] The rollback matches the documented steps and was exercised in staging.
- [ ] Every irreversible step has a tested rollback or a recorded accepted risk.
- [ ] Success metrics, thresholds, and the bake time are written before the deploy.
- [ ] Alerts page only for actionable, SLO-linked symptoms and each one has a runbook.
- [ ] Dashboards are versioned as code and name the deployed service.
- [ ] Logs, metrics, and traces carry a correlation ID and pass the masking rule.
- [ ] The on-call owner, escalation path, and incident commander role are current.
- [ ] Backup scope, retention, and encryption match the data classification.
- [ ] A restore drill passed inside the retention window, and RPO and RTO were measured.
- [ ] Release notes, changelog, runbook, and postmortem ownership and update timing are recorded.
- [ ] Freeze windows and the exception authority are published for the release period.

## Examples

<example>
Shipping a checkout change on a minor version: build the artifact once, promote the staging digest through a
5 percent canary, watch `checkout_success_ratio` and the error rate against the previous hour, and hold the full
rollout until the bake time completes; abort on the written threshold instead of debating it in the channel.
</example>

<example>
A library on 0.x adds a required argument to a public function. The minor version may carry the break under this
project's pre-1.0 policy, but not silently: bump to `0.8.0`, keep the old signature working with a deprecation
warning, announce the removal in `0.9.0`, and delete the old path only in that release.
</example>

<example>
A flag gates a new tax calculation. Create it defaulting to off with an owner and a removal release, ramp by tenant
group, hold at 100 percent for one release, then delete the old path and the flag in the next minor version and
remove the row from the flag inventory.
</example>

<example>
Checkout error rate crosses the SLO burn threshold at 02:10. The on-call acknowledges in four minutes, assigns
SEV-2, names an incident commander, and posts an update every 30 minutes; mitigate by rolling back to the previous
artifact, then fix forward, then file the postmortem with an owner for each action within five business days.
</example>

<example>
A migration adds a table. Before the release, restore the latest backup to a scratch instance, run the migration,
compare row counts and checksums, and record a restore time of 40 minutes against an RTO of one hour; the release
waits until the drill passes because recovery is a release criterion, not a separate project.
</example>

## References

Read [references/dimensions.md](references/dimensions.md) for the rule set behind each of the six dimensions:
versioning, change management, CI/CD, observability, incident response, and backup and recovery. Read the dimension
that matches the work before planning a release, designing telemetry, or handling an incident.
Read [references/playbooks.md](references/playbooks.md) when executing a release, a rollback, an incident, or a
restore drill, or when establishing the process; the playbooks carry the checklists, matrices, and runbook steps
that apply the rules. Read both before establishing a project's release policy; during routine work, read the
playbook for the task and the dimension behind it.
