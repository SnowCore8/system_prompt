# Version Control Dimensions

Use this file with `SKILL.md`. Each section gives the rules, decision tables, and edge cases for one collaboration
dimension, and its number matches the dimension index. When the repository already has a policy or a platform
setting, read it first and apply the higher-precedence rule; this file supplies the default and the reasoning.

## 1. Git Workflow and Branching

The branch model is a promise about how change reaches production. Choose it once per repository or branch class,
write it down, and let every other rule inherit it. A branch class is a group of branches that share a merge method
and a lifetime limit, such as trunk, release, hotfix, or maintenance.

- Choose by release path, not by fashion: trunk-based when every merge can deploy, release branches when a version is
  stabilized or supported, and GitFlow when several maintained versions ship to customers; a model copied from
  another team's repository usually fails on release cadence rather than on discipline, so justify the choice with
  the release process.
- Bound branch lifetime: integrate a topic branch within three working days, and treat five days as the point where
  the branch is rebased, re-reviewed, and split if it still cannot integrate; conflicts and integration risk grow
  with every day the branch stays open, and the review context is lost during the wait.
- Bound branch size: about 400 changed lines or ten files per reviewable change; split a mechanical rename,
  formatting sweep, lockfile update, or generated file from the behavioral change so each half can be reviewed,
  reverted, and bisected alone.
- Pick one merge method per branch class: squash to trunk, merge commit for release promotion, and rebase-and-merge
  only where the platform enforces linear history; mixing methods in one class makes blame, bisect, and revert
  report the wrong commit, and reviewers stop trusting the history they see.
- Land stacks from the bottom: after the parent merges, rebase each dependent branch onto the updated base, rerun
  its checks, and keep its position and its parent branch in the description so a reviewer reads the stack in order
  and never reviews a dependent change against a stale base.
- Resolve conflicts on the author's branch by rebasing onto the current base and rerunning the affected checks;
  merge the base into a topic branch only when the branch is shared, and never resolve a conflict inside the merge
  commit of a release branch, because the resolution then hides in a merge that nobody reviews line by line.
- Rewrite history only where it is private: amend unpushed commits, force-push with `--force-with-lease` and never
  bare `--force` on a personal branch, and treat a rewritten main or release branch as an incident with a record;
  the rule protects other people's work, not the author's convenience.
- Commit in reviewable units: one logical change per commit, each commit builds and passes the checks for its area,
  and fixups are squashed before merge so the landed commit states the change's reason rather than its repair
  sequence; a commit that mixes a rename, a dependency bump, and a behavior change cannot be reverted alone.

| Good | Bad | Why |
|---|---|---|
| Integrate a three-day branch daily | A three-week branch merged at the end | Conflicts and integration risk grow with branch age. |
| Squash features into trunk | Merge commits and squashes alternating on main | One method keeps blame and revert predictable. |
| Rebase a personal branch with `--force-with-lease` | `git push --force` to a shared branch | A lease refuses to overwrite work pushed since the last fetch. |
| Cut the hotfix from the release tag and cherry-pick to trunk | Edit the release branch directly and retag it | The fix must exist on both lines without moving history. |
| Split a rename from a behavior change | A 900-line diff that renames and changes logic | Each half is reviewable and revertable alone. |
| Amend an unpushed commit | Amend a reviewed commit already pushed | A rewritten published commit forces every dependent branch to reconcile. |
| Tag the release commit once | Rebuild the tag after adding one more fix | Published artifacts refer to the tag's exact commit. |
| Rebase the stack child after the parent lands | Keep the old base and merge later | Reviews and tests then apply to a state that no longer exists. |
| Cherry-pick a hotfix with `-x` to record its source | Copy the diff by hand between branches | Provenance survives the second application. |

Merge path by branch class:

| Branch class | Merge method | Hotfix path |
|---|---|---|
| Topic branch to trunk | Squash merge after required checks | Not applicable; trunk deploys continuously |
| Release branch to main | Merge commit after the release check | Fix on the release branch, forward-port to trunk |
| Feature branch into develop (GitFlow) | Merge commit with `--no-ff` | Hotfix from the release tag, merged to main and develop |
| Forked contribution | Maintainer squash-merge after review | Maintainer applies the fix on the normal branch |
| Published release | Tag on the release commit | New patch tag from a hotfix branch; never move the old tag |
| Hotfix for a supported version | Merge commit into the release branch, never squash | The fix reaches users without a feature release |
| Security fix prepared privately | Merge commit after the security owner's review | Disclosure timing stays controlled |

When trunk and a release branch need different rules, split the policy by branch class instead of asking reviewers
to remember an exception; record the split once and test it at the next release.

## 2. Pull and Merge Request Conventions

A pull or merge request is the unit of review, the unit of revert, and the record of why a change exists. Treat its
title, description, and state as part of the change rather than as paperwork around it. The request is also the audit
record: what changed, who approved it, which checks ran, and why the risk was accepted.

- Title states the outcome in the repository's commit format; the naming-conventions skill owns the type and scope
  grammar, and this skill owns the requirement that the title says what changes and why. A title that is only a
  ticket number, "fixes", or "WIP" forces the reviewer to open the diff to learn the purpose.
- Description answers four questions in order: what problem this solves, how it solves it, what was verified, and
  what could go wrong; add rejected alternatives when the choice is not obvious, and never describe only the code's
  mechanics, because the reviewer needs the intent that the diff cannot express.
- Link the issue the change closes, plus its dependencies and follow-ups: a partial fix links without a closing
  keyword so the issue stays open until its acceptance criteria are met, and a closing keyword is a promise that the
  merge completes the work.
- Require the repository's template, because an empty description is a request for rejection, not a minor style
  issue; this skill owns the requirement for the template and the decisions it captures, including verification
  evidence and rollback, while the template prose follows the repository's documentation style.
- Open a draft when early feedback is useful, and mark it ready only when the description is complete, self-review
  is done, and the required checks are green; a draft stays out of review queues, is never approved for merge, and
  is closed rather than parked when the work stops.
- Keep the request reviewable: under 400 changed lines and one logical change; when it must grow, split it and stack
  the parts, because review quality falls faster than review time rises once a diff passes a few hundred lines.
- Handle review state deliberately: approve only with evidence, request changes with a numbered list of required
  fixes, and comment for open questions; push fixes as commits during review rather than rewriting the branch, and
  never merge while a blocking thread is open.
- Require checks and the queue before merge, and merge only when every condition holds: owner approval, green
  required checks on the merge result, no unresolved blocking thread, no newer base commit that invalidates the
  tested result, and a merge method that matches the branch class.

| Good | Bad | Why |
|---|---|---|
| Title states the outcome: `fix(invoice): reject expired cards` | `Fixed stuff (#412)` | Purpose is visible before the diff. |
| Description lists problem, approach, verification, and risk | `See the ticket` | The reviewer can check the claim, not just the code. |
| `Closes #412` only when acceptance is complete | `Closes #412` on a partial fix | A closing keyword closes the issue on merge. |
| Request under 400 changed lines | A 1,400-line "small refactor" | Review attention collapses past a few hundred lines. |
| Draft until green and described | Ready with an empty description | Reviewers queue work that cannot merge. |
| Push fixups during review, squash at merge | Force-push mid-review without notice | Review comments lose their anchors. |
| Required checks on the merge result | Green on the author's head only | The merge combination is what ships. |
| Stack order stated in every description | Three requests with no stated order | Reviewers cannot know what lands first. |
| Verification pastes the failing and the passing run | "Tested locally" | The evidence is checkable. |

Request state and the allowed action:

| State | Allowed action | Condition |
|---|---|---|
| Draft | Review for early feedback only | Not eligible for approval or merge |
| Ready, checks pending | Read the diff; hold the approval until checks finish | Blocking comments may be opened now |
| Approved, substantive push | Re-review the delta, then renew the approval | An approval is stale after a push by policy |
| In the merge queue | Wait; fix and re-enqueue on failure | Never merge around the queue |
| Approved, base moved | Rebase, rerun the checks, keep the approval if no conflict resolution changed code | The tested result must match what merges |
| Auto-merge enabled | Wait for the queue; do not merge by hand | The setting is a promise, not an override |
| Merged | Delete the branch and verify the deploy | Corrections go through a new request |

A request that cannot be described in the four description questions is not ready to review; a template that
discourages evidence is a defect in the template, not in the author.

## 3. Code Review

Review is where a second person decides whether the change is correct, safe, and maintainable. Invest attention in
proportion to the cost of being wrong, and make every comment actionable. The review record also protects the
author: an approval with its evidence shows that someone with the area's knowledge accepted the risk.

- Classify risk before choosing reviewers: light for docs, comments, test-only changes, and formatting; standard for
  an ordinary feature or bug fix; risky for auth, payments, permissions, crypto, data migrations, public interfaces,
  dependency upgrades, and CI or release tooling, because those failures are expensive and hard to see in a diff.
- Select reviewers by ownership first and expertise second: the owning team's review is required where CODEOWNERS
  requires it, and a reviewer who has not read the changed area is a commenter, not an approver, because approval
  asserts a judgment that only familiarity supports.
- Set the count by risk: one for light, one owner for standard, and two including a domain or security reviewer for
  risky; a repository where every change needs the same two people has a staffing problem, not a review policy, and
  the fix is more owners rather than fewer reviews.
- Set turnaround expectations: first response within one business day, a small delta re-reviewed the same day, and a
  stalled review reassigned after a day rather than keeping the author blocked. Turnaround is part of the policy
  because an unreviewed change rots while it waits.
- Separate blocking from non-blocking: prefix each comment `must:` to block the merge, `should:` to request a fix or
  an explanation, `nit:` for local preference, and `q:` for a question that needs an answer but asks for no change;
  an unmarked comment counts as `should:` and still needs a reply, so the author can always tell what stands
  between the change and merge.
- Review the change, not only the diff: check correctness against the issue, a test that fails without the change,
  error and failure paths, security and privacy, performance at the expected scale, compatibility, and documentation
  impact; the diff shows what changed, not whether the change is right.
- Author responsibilities: keep the description current, answer every comment, push small fixups during review, mark
  a thread resolved only after the fix or the agreed decision, and request re-review after a substantive change
  rather than assuming the old approval still applies.
- Handle disagreements by escalating to the owning team's decision owner and recording the decision in the request
  or an ADR; never merge while a blocking thread is open, and never resolve a thread just to end the disagreement.

| Good | Bad | Why |
|---|---|---|
| `must: reject a token without an audience claim` | "Not sure about this" | Severity and the requested action are explicit. |
| Owner team approves the auth path | Approval from outside the owned area | Ownership carries knowledge the diff does not show. |
| A test fails before the fix and passes after | Merge a behavior change with no new test | The test proves the behavior changed as claimed. |
| Reassign a stalled review after one day | Wait two weeks for the same reviewer | The author is blocked and another reviewer can unblock. |
| Resolve a thread after the fix and a reply | Click resolve to clear the queue | Silent resolution hides an unanswered objection. |
| Escalate to the decision owner and record it | Merge while a blocking thread is open | A recorded decision outlives the review. |
| Review the migration's rollback step | Approve because CI is green | CI proves nothing about recovery. |
| Reply to a nit with a reason | Ignore the nit silently | An answered thread needs no enforcement. |

Review state and its effect on merge:

| State | Meaning | Author action | Merge effect |
|---|---|---|---|
| Approve | Reviewer is satisfied with the change | Resolve remaining nits | Allowed after required checks |
| Approve with comments | Non-blocking suggestions only | Address or reply to each | Allowed |
| Request changes | A blocking defect or missing evidence | Fix and re-request review | Blocked until a renewed approval |
| Comment | A question or information, not a verdict | Reply with evidence | Not an approval |
| Stale approval | A substantive push happened after approval | Request re-review of the delta | Blocked until renewed |
| Review dismissed | A push or a policy event cleared it | Re-request and re-address the raised points | Blocked until a new approval |
| Reviewer unreachable | The requested owner does not respond | Reassign to the owning team's fallback | Waiting is not a review state |

Review is not proofreading: a comment about spelling belongs last, and a correctness question outranks every style
preference in the same pass.

## 4. Branch Protection and Permissions

Protection turns a shared convention into an enforced one. Configure the smallest set of rules that keeps the
protected branches releasable, and treat every exception as a logged, reviewed event. A protected branch is only as
strong as its weakest exception, so the exception path is part of the design rather than an escape from it.

- Protect the integration branches and every supported release branch: no direct pushes, no deletion, no force-push,
  and no routine bypass; keep the protected set a short, named list in the repository settings so an audit can check
  it against the policy.
- Require the checks that actually guard a release: build, unit and integration tests, lint, type check, secret scan,
  and the documentation build where docs publish; a check nobody enforces is decoration, so promote it to required
  or delete it instead of leaving a green-looking signal that means nothing.
- Grade required checks by branch class: trunk requires the full set, a release branch adds packaging and release
  checks, and a maintenance branch may require build, tests, and the release owner's approval only; one global list
  either blocks releases on irrelevant work or under-checks the branch that ships.
- Enforce linear history where the merge method depends on it, namely squash or rebase into trunk; allow merge
  commits on release branches, and set the choice explicitly instead of accepting the platform default, because the
  history rule and the merge method must agree.
- Protect tags as well as branches: a published release tag is immutable, only the release automation or the release
  owner creates tags, a tag whose gates fail is deleted before publication and not restored, and a deleted or moved
  published tag is restored from the record rather than rebuilt on a guess, because installed artifacts refer to the
  exact tagged commit.
- Apply least privilege with the five platform roles plus the service roles below, and set merge permissions
  explicitly: read for outsiders, triage for issue and review coordination, write for contributors, maintain for
  owners, and admin for a small break-glass group; an author merges after approval unless the branch class requires
  a maintainer merge.
- Treat credentials as owned by the security process and consumed by the pipeline: keep only the CI-local rule that
  credentials never reach untrusted fork builds, because a secret a workflow can print is a secret a fork request
  can exfiltrate.
- Record the exception path: a bypass needs an actor, a reason, a link to the request, and a post-merge review within
  one business day; audit administrative actions monthly and report the count in the repository's operations notes,
  because an unexamined bypass becomes the normal path.

| Good | Bad | Why |
|---|---|---|
| Reviews and checks required on main | "Admins can merge anything" | The exception becomes the normal path. |
| Protect release tags | Let the release script create and move tags | Published artifacts must match their tag. |
| Credentials kept out of untrusted fork builds | Repository-wide secrets used by every workflow | A fork request can read repository secrets. |
| Log every bypass with a reason | Silent administrative merge | The next incident cannot explain the gap. |
| Maintain for owners, admin for a break-glass group | Everyone is admin | Least privilege limits the blast radius. |
| Linear history on trunk | Merge commits and squashes mixed on main | History matches the review model. |
| Require the docs build when docs publish | Merge documentation that never renders | The published page is the product. |
| Separate the release token from the deploy token | One token can tag and deploy | Two permissions limit one compromise. |

Role and the actions it may take:

| Role | Branch actions | Settings and permission actions |
|---|---|---|
| Read | View code, issues, and check results | None |
| Triage | Manage issues and review requests; no code push | None |
| Write | Push topic branches and open requests | None |
| Maintain | Merge to protected branches; manage non-protected settings | Request changes from an admin |
| Admin | Bypass protection; edit settings, rules, and tags | Time-boxed, logged, post-reviewed |
| Release automation | Tag and publish release artifacts | No settings changes; scoped token only |
| Security team | Read all actions and audit logs | Set the secret and password policy |

When a platform cannot enforce a rule, replace the rule with a scheduled manual check and name its owner; an
unenforced rule that everyone believes is enforced is worse than no rule.

## 5. Code Ownership

Ownership answers who must review a path and who is accountable when it fails. Encode it where the platform can
enforce it, keep it current, and never let a path exist without a named owner. Ownership is not the same as
expertise: the owner is accountable for review coverage, not for knowing every line.

- Treat CODEOWNERS as executable policy: owners are requested automatically, and a required-review rule makes owner
  approval a merge condition; verify the platform reads the file from a supported location and that the last
  matching pattern wins, because a file in the wrong location is silently ignored.
- Cover every mergeable path: a root fallback for the repository, a team per service or domain, and explicit
  patterns for shared libraries, configuration, CI, release scripts, generated trees, and vendored code; a path that
  no pattern matches is an orphan, and the next change to it has nobody to review it.
- Name teams, not individuals: a team handle survives a person leaving, distributes review load, and avoids a
  vacation blocking a merge; a person is named only where a path genuinely has one maintainer, and that entry gets
  an expiry review rather than becoming permanent.
- Own by domain, not by file type: a service team owns its code, tests, configuration, and migrations, while a
  platform team owns shared CI, the build tool, generated code, and vendored dependencies; a change to generated or
  vendored trees is reviewed as a regeneration with the generator input, never as a hand-edited diff.
- Make ownership required only where risk justifies it: require owner review for auth, financial, privacy,
  infrastructure, and public interface paths, and keep ownership advisory elsewhere so a two-person team can still
  merge without waiting for a stranger.
- Keep a fallback owner: when the owning team is unavailable or dissolved, the platform or repository maintainer team
  receives the request; the fallback is documented and exercised, not discovered during an incident when the clock
  is already running.
- Audit coverage after every reorganization and quarterly: find orphaned paths, stale handles, teams with no members,
  and required-review rules that match no path, then fix coverage in a dedicated request with a named owner and a
  deadline.
- Transfer or retire ownership deliberately: a transfer moves patterns and team membership in one reviewed change,
  and a retired service removes its paths with the owner confirming the archive, so no review request ever targets a
  dead handle and no deleted code keeps an owner.

| Good | Bad | Why |
|---|---|---|
| Team handle for a service path | Personal handle for a service | A team survives people leaving. |
| Required owner review on the auth path | Advisory ownership on password reset | Risk decides where required review applies. |
| Fallback maintainer team for an orphan path | No owner until someone complains | The next change has a destination. |
| Review the generator input and regenerate | Hand edit a file under `vendor/` | Tooling owns generated trees, not the diff. |
| Quarterly audit with named fixes and deadlines | A wildcard rule and nothing else | Wildcards hide orphaned paths. |
| Ownership transfer in a maintainer-reviewed request | The new owner approves their own grant | Authority changes are reviewed. |
| Specific pattern placed after the broad fallback | Broad pattern last, overriding every specific owner | The last matching pattern wins. |
| The owner confirms the archive before paths are removed | Remove the paths first and retire later | The owner signs off on the loss. |

Path type and its ownership contract:

| Path type | Owner | Review requirement |
|---|---|---|
| Source by domain | Owning service team | Owner approval where the risk policy says so |
| Shared library or SDK | Owning platform or library team | One owner plus one consumer for public changes |
| CI, build, and release scripts | Platform team | Required for every change |
| Generated code | Generator owner | Regeneration proof; no line-by-line review |
| Vendored dependency | Platform or dependency owner | Pinned version, license, and advisory check |
| Documentation and templates | Documentation owner | Advisory unless the page is published |
| Infrastructure as code | Platform team | Plan output reviewed with the change |
| Retired service | Archive owner until deletion | Removal reviewed by the former owner |

An ownership rule that names no fallback is a single point of failure; test it by asking who would review the path
if the owner disappeared tomorrow, and fix the answer before the next change arrives.
