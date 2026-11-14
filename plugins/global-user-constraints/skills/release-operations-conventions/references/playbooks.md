# Release and Operations Playbooks

Use this file with `SKILL.md` and `references/dimensions.md` when executing a release, a rollback, an incident, or a
restore drill. Each playbook is a procedure: the dimensions file holds the rules, and this file supplies the order,
the decision points, and the evidence to record. Adapt the thresholds to the project's written policy, and never
skip a step because it was skipped in practice before; the step that is always skipped is the one that fails first.

## Release Readiness Checklist

Run this checklist at go or no-go time against the artifact and the records, not from memory. Every unchecked item
is a blocker or a recorded accepted risk, and the person who accepts the risk is named in the release record.

- [ ] The change class and version bump are recorded, and the release type is chosen from the Release Model Matrix.
- [ ] The release branch is frozen; only approved changes may merge before the release commit is cut.
- [ ] The artifact was built once from the release tag in a clean checkout, and its digest is recorded with the tag
  and the input manifest.
- [ ] Every required gate passed on that artifact, not on an earlier build of the same branch.
- [ ] The previous healthy version is named, and its artifact is still retained in the registry.
- [ ] The rollout plan states the percentage, the bake time, the success metric, and the abort threshold.
- [ ] The rollback steps, the data impact, and the decision authority are written and were exercised in staging.
- [ ] Database migrations are backward compatible with the previous application version or approved as irreversible.
- [ ] The service dashboard shows the deployed version and is provisioned from the repository.
- [ ] Alerts for the affected service fire correctly in staging and name their runbooks.
- [ ] The release note and changelog entries are written and match the artifact that will ship.
- [ ] A restore drill passed when the change touches stored data, with measured RPO and RTO.
- [ ] The approver, deployer, and observer for the release window are named and available.
- [ ] The release record names the version, the digest, the approver, and the rollback target before the deploy.
- [ ] The freeze window and exception authority are checked, and any exception is recorded with its rollback plan.

## Version-Bump Decision Table

Apply the highest impact across all changes in the release and record the reason with the bump. When two rows
disagree, take the higher bump and write down why the lower one was rejected.

| Change in the release | Version bump | Edge case to record |
|---|---|---|
| Removed or renamed public name, endpoint, field, or event | Major | List every removed name and its replacement in the release note. |
| Changed required parameter, default, or response shape | Major | A default change that alters output is a break even when the signature is stable. |
| New optional capability, endpoint, or field | Minor | Confirm that old clients ignore it without breaking. |
| Deprecation added without removal | Minor | Name the removal release and the date in the deprecation notice. |
| Fix that restores documented behavior | Patch | Note the version where the wrong behavior appeared. |
| Fix that changes behavior users may depend on | Minor or major by contract | If the buggy behavior was documented, treat the fix as breaking. |
| Internal refactor with no external behavior | Patch, or no release | No release only when the artifact itself did not change. |
| Security fix for a vulnerability | Patch, or major if the fix breaks a contract | Follow the disclosure schedule; the version alone does not disclose. |
| Tooling, test, or documentation change | No version bump | Bump only if the shipped artifact or its metadata changed. |
| Breaking change before 1.0 | Minor | Keep the previous minor working for one release when users have integrations. |
| Several change classes in one release | The highest bump among them | Split the release rather than hiding a major inside a patch. |
| Added optional configuration key with a safe default | Minor | Removing a key or changing its default is a break, not a cleanup. |
| Changed error code, event name, or log field consumed downstream | Major | Treat a downstream consumer of the field as a public contract. |

- Bump by the highest impact in the release, never by the average or by the urgency of the request.
- Never ship a major change inside a patch release; split the release instead of relabeling it.
- Record the previous version and its support window together with the bump so the rollback target is explicit.
- When the impact is unclear, bump higher and state the assumption; a wrong lower bump breaks consumers silently.

## Rollback Runbook

A rollback is a planned operation, not an improvised one. Write this runbook for each service before the first
release that can fail, and rehearse the rollback in staging before it is needed in production.

### Trigger

- Roll back when a success metric leaves the threshold written in the rollout plan and no known external cause
  explains the trend.
- Roll back when the error rate or latency for the affected journey exceeds the pre-agreed level for the bake time.
- Roll back when data corruption, wrong results, or an authorization bypass is suspected, and stop writes before
  further damage.
- Roll back first when the cause is unknown and the previous version is healthy; investigate after the rollback.
- Do not roll back blind after an irreversible migration; use the written fallback and escalate to the data owner.

### Authority

- The on-call engineer may roll back a SEV1 or SEV2 without further approval and records the decision and its time.
- A planned rollback outside an incident needs the release owner's approval recorded in the release record.
- A rollback that reverses data or requires a restore needs the incident commander and the data owner, and the
  restore follows the backup playbook.
- A rollback that would reintroduce a known vulnerability needs the security owner; the default in that case is a
  forward fix.
- Record who decided, when, and why, in the release record or the incident timeline, before the next release starts.

### Rollback Steps

1. Confirm the incident and its severity, and name an incident commander if one is not already named.
2. Freeze further changes to the affected service, and stop the rollout at its current percentage.
3. Preserve evidence: snapshot the logs, record the failing request or correlation ID, and capture the current
   metric window before it ages out.
4. Identify the previous healthy artifact digest, and confirm that it is retained, signed, and deployable.
5. Check migration compatibility: if the new version wrote data the old version cannot read, stop and use the
   written fallback instead of a plain rollback.
6. Run the rollback job for the previous digest, or turn off the flag when the flag is the release unit.
7. Restore the configuration and flag defaults that the release changed, and confirm the effective values.
8. Verify the success metrics, the error rate, and the business signal against the pre-release baseline.
9. Confirm data integrity with the written checks, then post the mitigation and keep the incident open for the
   forward fix.
10. Record the rollback in the release record, file the follow-up, and schedule the forward fix as a new release.
11. Confirm through the deploy tooling that the rollout is stopped and that no new instances of the failed version
    are starting.
12. Set the approval level for the forward fix and keep the incident open until that fix ships or the risk is
    accepted in writing.

### Rollback Verification

- The service dashboard shows the previous version, and every success metric is back inside the baseline.
- The failing journey succeeds through the same check that detected the failure.
- No new errors or alerts appear after the rollback, watched for at least one bake interval.
- Data checks pass: row counts, checksums, and a sample read of records that the new version wrote.
- The version endpoint and the release record both name the previous version and digest, not the failed one.
- The incident channel and the status page report the mitigation and the next update time.

## Feature-Flag Lifecycle Table

A flag moves through these stages in order and leaves the code at the end, and the Emergency row can be entered
from any stage. The naming skill owns the flag name; this table owns the states, the exit criteria, and the evidence
that the state was reached.

| Stage | Action | Exit criterion | Evidence |
|---|---|---|---|
| Propose | Record the owner, purpose, default, removal release, and failure behavior | The change review approves the flag | Flag inventory row |
| Create | Implement both paths, default off, and test both | Staging proves that both paths work | Test report and inventory row |
| Validate | Enable for internal users or an opt-in cohort | Error and business metrics are equal or better | Cohort report |
| Ramp | Raise the percentage by segment with an abort threshold per step | Stable for the bake time at each step | Ramp log |
| Extend | Justify a longer ramp in writing, with a new removal release | The flag owner approves the extension | Inventory update |
| Full | Serve all traffic with the kill switch ready | No regression for one release, and the removal plan is confirmed | Dashboard and release record |
| Retire | Delete the old code path, then the flag, in the next release | The flag is absent from code, configuration, and inventory | Diff and inventory check |
| Emergency | Disable through the kill switch without a deploy | The incident is mitigated and the cause is understood | Incident record |

- A flag is not a permission and never gates a security decision; authorization lives in the access model.
- No nested flags: a second flag on the same behavior needs a written reason and its own removal release.
- The removal release is set at creation; moving it requires the owner and a recorded reason.
- A flag that fails its ramp is turned off and removed, not left in a half-on state for the next release.
- A flag without an owner is disabled and removed at the next release, and the inventory is checked in the release
  review.

## Incident Severity and Paging Matrix

Assign severity at triage from user impact, page by severity, and change the severity only with new evidence recorded
in the timeline. When the level is ambiguous, start one level higher and downgrade after evidence justifies it.

| Severity | User impact | Paging | Update cadence | Postmortem |
|---|---|---|---|---|
| SEV1 | Full outage, data loss, or an actively exploited security issue | Page primary, secondary, and commander immediately; notify the executive sponsor | Every 15 to 30 minutes | Required within 5 business days |
| SEV2 | Major function or a large user subset degraded, with no workaround | Page primary; escalate to commander if unresolved in 15 minutes | Every 30 minutes | Required within 5 business days |
| SEV3 | The same impact as SEV2 where a workaround exists | Page during business hours or hand off to the next rotation | At start and at closure | Required when it repeats within a quarter |
| SEV4 | Minor or cosmetic impact, no user action needed | No page; ticket for the next business day | On closure | Not required |
| SEV5 | Question or request, no service impact | Queue, no page | As needed | Not required |

- Severity determines the page, the channel, and the communication cadence; it is not a judgment about who caused
  the problem or how hard the fix is.
- Never page at SEV3 without a written escalation reason, and record that reason in the timeline.
- A severity that changes during the incident keeps both values and the time of the change in the timeline.
- Never lower a severity to avoid a meeting or a report; the matrix exists to make that pressure visible.

## Incident Checklist

Run this checklist in the incident channel while the incident is open, not after it ends. Each unchecked item is a
reason the response is harder than it needs to be, and the scribe records the time of each check.

- [ ] Severity assigned from the matrix at triage and recorded with the time.
- [ ] Incident commander named for SEV1 or SEV2, and roles assigned for operations, communication, and scribing.
- [ ] Incident channel opened, with the audience and the scope stated.
- [ ] Impact described in user terms: who is affected, what fails, and what still works.
- [ ] First mitigation chosen before the root-cause investigation starts.
- [ ] Evidence preserved: logs, failing request ID, metric snapshot, and deployed version.
- [ ] Rollback or flag decision recorded with its time, its authority, and its expected effect.
- [ ] Updates posted on the severity's cadence, each stating impact and the next update time.
- [ ] Escalation triggered when the response exceeds the written timescale.
- [ ] Mitigation verified through the same signal that detected the problem.
- [ ] Closure criteria met: symptoms gone, metrics stable, and follow-ups filed.
- [ ] Timeline completed with first alert, acknowledgement, mitigation, and resolution.
- [ ] Customer-facing status page updated when users are affected, with the next update time.
- [ ] Decisions recorded in the timeline as they are made, including the options rejected.
- [ ] Postmortem scheduled when required, with the draft deadline and the reviewer.
- [ ] Action items filed with an owner, a due date, and a verification step.

## SLO Worksheet

Fill one worksheet per service and per user journey, store it with the service records, and review it when the
target misses or an incident changes the design. The example values show the form; replace them with measured
values from the project.

| Field | Rule | Example |
|---|---|---|
| Service and journey | One SLO per user journey, not per process | Checkout submission |
| SLI | Measurable from the user's side, with the source named | Ratio of successful valid checkout requests |
| Measurement | State the data source, the aggregation, and the window | Request logs and edge metrics in five-minute buckets |
| Target | Rounded to a level the team can defend from data | 99.9 percent success over 30 rolling days |
| Error budget | One minus the target, expressed in time for the window | 0.1 percent of 30 days, about 43 minutes |
| Burn alert | Page when the budget burns faster than the window allows | A burn rate of 14.4 in one hour pages the on-call |
| Ownership | Name the service owner and the review cadence | Checkout team, reviewed quarterly |
| Policy at exhaustion | State the consequence before the budget is spent | Feature release freeze until the budget recovers |
| Exclusions | Name dependencies that are measured separately | Payment provider outage excluded and tracked separately |
| Review trigger | State the event that forces a revision | Every SEV1 and every missed target |
| Dashboard query | Store the exact query that computes the SLI, versioned with the dashboard | Link to the versioned query |
| Review record | Record the target decision and its date at each review | Decision note linked from the service record |

- A 100 percent target is not an SLO; it leaves no budget for change and no room to learn.
- A budget expression that nobody has recomputed against the dashboard is not yet a measurement.
- An SLO with no owner, no error budget, and no exhaustion policy is a target, not a reliability commitment.
- Recalculate the budget after a target change and tell the teams whose release plans depend on it.

## Deploy-Strategy Selection Table

Choose the strategy by the cost of a bad release and the power to detect it, not by what the team used last time.
Record the choice and its parameters in the release record.

| Strategy | Use when | Rollback | Cost and risk |
|---|---|---|---|
| Rolling | Stateless service, enough capacity, and N-1 compatibility | Redeploy the previous digest | Low cost; two versions run during the rollout |
| Blue-green | Fast cutover and rollback are needed and double capacity exists | Switch traffic back to the previous stack | Double capacity; data written by the new version must be readable by the old |
| Canary | Enough traffic exists to detect a bad release through a success metric | Shift traffic back to the stable version | Medium cost; a low-traffic canary proves nothing |
| Recreate | Downtime is acceptable, the service is single-instance, or the change is migration-only | Redeploy the previous version after the downtime | Lowest cost; users see the outage |
| Shadow | A new path must be validated without user impact | Discard the shadow receivers | High cost; duplicated side effects must be prevented |

- Write the canary percentage, duration, success metric, and abort threshold in the release record before the first
  deploy.
- Exercise the rollback through the same strategy at least once in staging; a rollback that was never run is a plan.
- A blue-green cutover needs a data compatibility check before the switch, and both stacks need the same
  configuration.
- A rolling rollout needs readiness probes and connection draining, or the mixed-version window becomes an outage.
- Canary and blue-green both need the previous stack kept warm for the rollback window; sizing it away removes the
  rollback path.

## Backup and Restore Drill Checklist

Run this checklist quarterly, after every change to backup scope, and before a release that migrates data. Record
the result, the measured RPO and RTO, and every failed step in the drill record.

- [ ] The backup scope list is current and includes the stores that changed since the last drill.
- [ ] The latest backup completed, and its age and size are recorded.
- [ ] The encryption keys needed for the restore are available to the restore target.
- [ ] The restore target is isolated and encrypted, with production-sized storage.
- [ ] The timed restore starts, and the elapsed time is recorded per step.
- [ ] Full restore plus the required log replay or incremental reaches the chosen timestamp.
- [ ] Row counts, checksums, or document counts match the source at that timestamp.
- [ ] The application starts against the restored data and passes its smoke queries.
- [ ] A sample business record is read and compared with the expected value.
- [ ] Actual RPO is measured as the age of the newest recoverable data.
- [ ] Actual RTO is measured and compared with the target for that data class.
- [ ] Failed steps, missing permissions, and documentation gaps are recorded.
- [ ] The runbook and the disaster recovery plan are updated, and the next drill date is set.
- [ ] An alert exists for a backup that fails or is older than the RPO.
- [ ] A second person has followed the runbook and restored without asking its author.
- [ ] The restored dataset excludes records that the retention policy should already have deleted.
- [ ] The drill result, including the measured RPO and RTO, is stored with the service record.

The drill record is the evidence: keep the date, the participants, the measured RPO and RTO, the failing steps, and
the next drill date with the service record. A drill whose result is not recorded is repeated from the beginning.
