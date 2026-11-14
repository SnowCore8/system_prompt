---
name: vcs-collaboration-conventions
description: Defines, reviews, and repairs version control and collaboration practice for any repository: Git workflow and branching, pull and merge requests, code review, branch protection and permissions, and code ownership. Use when choosing a branch model, preparing or reviewing a pull request, setting review depth, configuring protected branches, or auditing CODEOWNERS coverage. Provides repository-agnostic defaults with team-size tradeoffs.
argument-hint: '[path or scope]'
---

# Version Control and Collaboration Conventions

Most teams do not lose code to bad algorithms; they lose it to collaboration failures. A pull request grows until
no reviewer can hold it, the history records merges nobody can explain, a directory loses its owner when its author
leaves, and a protected branch is bypassed once and then routinely. Each failure is cheap to prevent at the rules
stage and expensive to repair after a release depends on it. This skill gives one decision procedure and a complete
rule set for how a change travels from a working copy to the main branch and beyond: branch models and merge
methods, pull and merge request conventions, review depth, branch protection, and code ownership. It assumes Git and
a review-based hosting platform, and it stays neutral about the project's language and the platform's interface.

## Scope and Precedence

Apply the first rule that fits, and do not mix models inside one branch class:

1. Mandatory hosting-platform or organizational policy. Required checks, audit requirements, signed-commit rules,
   and a regulator's change-control rules are not optional.
2. Existing project convention. Read the branch model, merge settings, CODEOWNERS file, and contributor guide before
   proposing a rule; a documented local rule outranks this default.
3. This standard's defaults, when the two levels above are silent.
4. Personal preference, which never overrides the three levels above.

- The naming-conventions skill owns branch names, commit-message types and scopes, and tag names; this skill owns the
  workflow, the merge strategy, and the review process that consume them.
- This skill owns the requirement for pull request and issue templates and the decisions they must capture; the
  template is a document, and its prose follows the repository's documentation style.
- The release-operations-conventions skill owns release versioning, release timing, and CI/CD; this skill owns how a
  change reaches the main branch and which merge path it takes.
- The security-compliance-conventions skill owns access-control policy details; this skill owns branch protection and
  code-ownership mechanics, including required checks and bypass records. Signed-commit requirements come from
  hosting-platform or organizational policy at precedence level 1.
- The testing-and-quality-conventions skill owns the gates themselves; this skill owns which gates are required on
  protected branches and when a merge may proceed.
- Generated, vendored, and machine-produced paths are exempt from line-by-line review but not from the merge rules.
  Review the generator input, the regeneration command, and the generated marker; a hand edit to generated output
  never counts as a reviewed change.
- History is a public record: rewrite only under policy. Amend unpublished commits, force-push only a personal topic
  branch with a lease, and treat a rewritten protected branch as an incident even when the content is identical.
- A rule that lives only in a reviewer's memory is not a rule. Record the branch model, merge method, review depth,
  and ownership in the contributor guide or a linked policy file, and update it in the change that alters practice.
- When two rules conflict, state the conflict and the chosen rule, record the decision next to the branch model, and
  make the next change follow it.

## Process

1. Establish the current state: read the platform's branch settings, merge method, CODEOWNERS file, CI configuration,
   contributor guide, and the last twenty merge commits. Team size and release cadence decide the model before any
   rule is written.
2. Choose or confirm one branch model from the matrix below and write it down: branch classes, lifetime limits, merge
   method per class, release path, hotfix path, and tag policy.
3. Size the change before opening a branch. Keep one logical change per branch; when it exceeds the size budget,
   split it into a stack or hide it behind a feature flag, and link the parts in landing order.
4. Prepare the pull or merge request with its title, description, linked issue, risk class, verification evidence,
   and self-review. Mark it ready only when the required checks and the template are complete.
5. Route the review by ownership and risk: request the owning team plus the domain reviewer the risk class requires,
   and state the review depth in the request.
6. Land through the required path: use the merge queue or auto-merge when the repository configures them, otherwise
   merge with the branch class's method after every required check passes on the merge result, then delete the
   topic branch.
7. Audit on a schedule: confirm the landing, verify the deploy or release path, review bypass records, and repair
   CODEOWNERS coverage, stale approvals, and protection drift before the next change.

## Core Rules

- **One model per branch class.** State the branch model in the contributor guide and enforce it in the platform; a
  repository that mixes trunk merges, release-branch merges, and hotfix cherry-picks without documented boundaries
  produces history that no reviewer can reconstruct.
- **Keep branches short-lived and small.** Integrate within three working days and keep a reviewable diff under
  about 400 changed lines; a longer branch rebases daily, and a change that cannot be split behind a flag is a
  design signal rather than an excuse.
- **The main branch is always releasable.** Every commit on main builds, passes the required gates, and can be
  deployed; a red main branch blocks all merges and takes priority over new feature work.
- **One merge method per branch class.** Squash feature branches into trunk, use a merge commit for release
  promotion, and rebase only an unshared branch; mixing methods in one class makes blame, bisect, and revert
  unreliable.
- **History is append-only in public.** Never rewrite commits that others have based work on; repair a published
  mistake with a revert or a follow-up commit, and reserve force-push with a lease for a personal topic branch.
- **Review depth follows risk, not availability.** Classify each change as light, standard, or risky by its blast
  radius; auth, payments, permissions, data migrations, and public interfaces take the risky path with a second
  reviewer.
- **Every change lands through review and required checks.** A protected branch requires an approving review and
  green required checks on the merge result; an approval that predates a substantive push is stale and must be
  renewed.
- **Protection is the default; bypass is an incident.** Require reviews, checks, linear history where the merge
  method requires it, and no force-push on protected branches; record every administrative bypass with its actor,
  reason, and a post-merge review.
- **CODEOWNERS names a real owner for every mergeable path.** A path with no owner is a defect with a deadline; the
  fallback owner is the platform or repository maintainer team, never whoever edits the path next.
- **Gates run on the merged result, not only the author's copy.** The merge queue or pre-merge job tests the change
  against its base; a locally green run does not substitute for the required check.
- **A review comment carries a severity and an ask.** Mark each comment blocking, non-blocking, nit, or a question
  that needs an answer, and require the author to resolve every blocking thread with a reply or a linked fix;
  silence is not agreement.
- **Draft means not ready.** Open a draft for early feedback, then mark it ready only when the description,
  evidence, and self-review are complete; a draft is never reviewed for merge and is never merged.
- **Delete merged branches and freeze release tags.** Remove a topic branch after merge so the branch list reflects
  open work; never move, delete, or rebuild a published release tag, because published artifacts refer to it.
- **Ownership changes are reviewed like code.** A CODEOWNERS edit that grants or removes ownership needs a
  maintainer's review and lands in its own request, with two approvers per the repository-governance rule; an owner
  never approves a change that expands that owner's authority.

## Branch Model Matrix

Choose the lightest model that satisfies the release process; the model decides the merge method and the hotfix path.

| Model | Team and repo size | Merge method | Release path | When to choose |
|---|---|---|---|---|
| Trunk-based, no release branches | 2 to 15 engineers, one deployable service | Squash merge to trunk; rebase the topic branch | Trunk deploys continuously; a release is a tag on trunk | Continuous delivery, feature flags, strong CI |
| Trunk-based with release branches | 15 to 100 engineers, several deploy targets | Squash to trunk; merge commit to the release branch; cherry-pick hotfixes to both | Cut at freeze, tag the release commit, hotfix on the branch and forward-port | Versioned releases or customers pinned to a version |
| GitHub flow | 2 to 30 engineers, one production environment | Squash or merge commit, one per repository | Merge to main, deploy from main | Small teams starting review practice; no release train to run |
| Release-train branches | 30 to 200 engineers, scheduled releases | Merge commit for promotion; squash for small fixes | Release candidate branches, qualification, then tag; fixes cherry-picked | Regulated cadence, long QA, several supported versions |
| GitFlow | 10 to 100 engineers, shipped or installed software | Merge commit with `--no-ff`; hotfix branches | `develop` integrates, `release/*` stabilizes, `main` holds tagged releases, `hotfix/*` starts from the tag | Desktop or on-prem software with support windows |
| Fork-and-pull | Public repository, any contributor count | Maintainer fast-forwards or squash-merges the reviewed branch | Main carries releases; tags and notes announce them | Open source or untrusted contributors without write access |
| Per-version maintenance branches | 5 to 50 engineers supporting several releases | Squash to the maintenance branch; merge commit for promotion | One branch per supported version; cherry-pick fixes and forward-port to trunk | Long support windows run by a small team |

When two models fit, choose the lighter one and revisit after a release cycle; the heavier model adds branches to
maintain and hotfix paths to remember. Record the choice, the date, and the next review trigger in the contributor
guide.

## Dimension Index

Each dimension has rules, decision tables, and edge cases in `references/dimensions.md`; `references/playbooks.md`
holds the worksheets and the step-by-step procedures for applying them.

| Dimension | First rule |
|---|---|
| 1. Git Workflow and Branching | Choose the lightest branch model the release process allows. |
| 2. Pull and Merge Request Conventions | A request is one reviewable change with one description and one decision. |
| 3. Code Review | Review depth follows risk, and every blocking comment names an action. |
| 4. Branch Protection and Permissions | Protect the branch, require the checks, and record every bypass. |
| 5. Code Ownership | Every mergeable path needs a named owner and a fallback owner. |

## Anti-Patterns

| Anti-pattern | Why it fails | Fix |
|---|---|---|
| Long-lived feature branch | Drifts from trunk, conflicts grow, integration risk hides until the end | Split into stacked requests or a flag; integrate daily |
| Mixed merge methods in one branch class | Blame, bisect, and revert stop matching the review history | Pick one method per class and enforce it in settings |
| Force-push to a shared branch | Erases teammates' commits and review comment anchors | Lease-protected force-push on a personal branch only; revert published mistakes |
| Rubber-stamp approval without reading the diff | Turns the merge gate into a ritual and hides defects | Request risk-specific evidence and review the self-review checklist |
| Request that mixes rename, formatting, and behavior | Not reviewable as one unit and not revertable alone | Isolate the mechanical change and land the behavior separately |
| Required check left advisory | A red check still merges, so the signal is decorative | Mark the check required and fail closed |
| "Just this once" direct push to main | Bypasses review and gates, then becomes the precedent | Deny by default; grant logged, time-boxed, post-reviewed exceptions |
| Draft marked ready without checks or description | Reviewers spend time on a request that cannot merge | Ready means green checks, complete description, and self-review |
| CODEOWNERS with a wildcard fallback only | The fallback team is notified, but path owners never are and orphan paths stay hidden | Assign real teams per path; audit coverage and orphan paths |
| Review comments with no severity or ask | The author cannot tell blocking from optional | Prefix `must:`, `should:`, `nit:`, or `q:` and name the requested action |
| Merging around the merge queue | The tested merge combination is not what lands | Let the queue order merges; re-enqueue after a fix |
| Moving a release tag to include one more fix | Published artifacts no longer match the tag | Cut a new patch version from the fixed commit |
| Approval left valid after a substantive push | The reviewer approved code that is no longer in the request | Dismiss stale approvals on push and re-review the delta |
| Ownership file edited by its new owner | Self-granted authority without a maintainer's review | Review ownership changes in a separate maintainer-reviewed request |
| Ownerless service after a reorganization | Nobody receives review requests and defects wait | Assign the fallback team on reorganization day and audit quarterly |
| CI credentials exposed to pull requests from forks | An outside contributor can read production credentials | Keep credentials out of untrusted fork builds; never print them in the pipeline |

## Review Checklist

- [ ] The branch model, merge method per class, and hotfix path are documented and match platform settings.
- [ ] The change is one logical unit within the size budget, or its stack order is documented.
- [ ] The title states the outcome, and the description states the problem, approach, and risk.
- [ ] The request links the issue it closes and lists the follow-up work it defers.
- [ ] Verification evidence is pasted and matches the described behavior.
- [ ] The request stayed a draft until checks passed and self-review was complete.
- [ ] Required checks pass on the merge result, not only on the author's last push.
- [ ] Reviewer selection matches the owned paths and the risk class, with the owning team's approval.
- [ ] Every blocking comment is resolved with a reply or a linked fix.
- [ ] Approvals are current; a substantive push after approval triggered re-review.
- [ ] The merge method matches the branch class, and the landed history stays legible.
- [ ] No protected branch was force-pushed, and any force-push used a lease on a personal branch.
- [ ] Protection settings require reviews, checks, and linear history as the policy states.
- [ ] Any bypass or administrative merge has an actor, a reason, and a scheduled post-merge review.
- [ ] CODEOWNERS covers every changed path, and fallback owners resolve.
- [ ] Generated and vendored files were regenerated, with markers and generator inputs reviewed.
- [ ] Hotfixes used the hotfix path and were forward-ported to the main line.
- [ ] Merged branches are deleted and published release tags are unchanged.
- [ ] No secret, token, or personal datum appears in the diff, description, comments, or CI logs.
- [ ] Post-merge verification (deploy, health check, release note) is planned or complete.

## Examples

<example>
Trunk-based merge:
A three-day branch changes 180 lines, the required checks are green on the merge result, the owning team approved,
and the description links the issue and pastes the test output. Squash-merge it, delete the branch, and confirm the
deploy from main. A 900-line branch in the same repository is split into a stack before review starts, not after
review stalls, and each request in the stack names its parent and the branch it depends on.
</example>

<example>
Risky review:
A token-refresh change is classified as risky: two reviewers, one from the auth-owning team and one security
reviewer, plus the negative test that proves an expired refresh token is rejected. The author pastes the threat
scenario and the rollback switch into the description, and an unmarked comment is rewritten as `must:` before the
request leaves draft; a substantive push then dismisses both approvals.
</example>

<example>
History repair:
An unpushed commit has the wrong message, so amend it. A commit already pushed to the author's topic branch gets a
revert or a follow-up commit, or a lease-protected force-push only when policy allows rewriting that branch. Main
never receives a force-push: revert it, then land the corrected change through review. The revert keeps the original
message, and the repair commit names the commit it restores so a reader of history sees both halves.
</example>

<example>
CODEOWNERS audit:
The audit finds `services/billing/**` owned by a team that no longer exists and `vendor/**` owned by nobody. Assign
the fallback maintainer team to billing with a deadline, make the platform team the owner of vendored code, and add
a CI check that every changed path resolves to an owner. The audit result names the fixes, the interim owners, and
the next audit date, and generated paths stay owned by the generator's owner.
</example>

<example>
Hotfix path:
A supported release has a defect, so cut `hotfix/2.3.1` from tag `v2.3.0`, land the minimal fix through review with
the release owner's approval, tag `v2.3.1`, and cherry-pick the fix to main. The hotfix branch is not reused, and
the old tag is not moved. The release note names the fixed defect, and the new patch tag is protected like every
other release tag.
</example>

## References

Read [references/dimensions.md](references/dimensions.md) for the rules, decision tables, and failure modes behind
each of the five dimensions. Read [references/playbooks.md](references/playbooks.md) for the worksheets and tables
that apply them: branch model selection, pull request description and size, review levels and comment severity,
branch protection, CODEOWNERS setup and audit, history repair, and merge queue and auto-merge rules. Read both before
defining a repository's collaboration policy; during routine work, read the dimension that applies and the playbook
step that matches the task.
