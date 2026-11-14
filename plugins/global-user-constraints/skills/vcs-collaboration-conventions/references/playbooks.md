# Collaboration Playbooks

Use these playbooks with `SKILL.md` and `references/dimensions.md`. Each playbook takes one recurring collaboration
decision from question to result; follow the steps in order, record the answer where the next person will read it,
and apply a stricter local policy when one exists.

## Branch Model Selection Worksheet

Answer these questions for the repository, then choose the first model that fits every answer:

1. Can every commit on the integration branch deploy to production without a separate stabilization step? If yes,
   prefer trunk-based.
2. Does a release need a code freeze, qualification, or a supported-version window? If yes, add release branches to
   trunk-based or choose release-train branches.
3. Must several shipped versions be supported for months, with fixes on each? If yes, choose GitFlow or per-version
   maintenance branches, and budget the forward-port work.
4. Do contributors lack write access to the repository? If yes, use fork-and-pull, protect the target branch, and
   require a maintainer to merge.
5. Is the team smaller than ten engineers with one deployable service? If yes, GitHub flow or plain trunk-based is
   enough; do not adopt GitFlow for its ceremony.
6. Does a regulator or customer require a release record separate from the commit history? If yes, keep release tags
   immutable and attach the record to the tag; do not simulate the audit with environment branches.

Record the outcome as branch classes, merge method per class, lifetime limit, hotfix path, and next review date.
The answer pattern selects the model:

| Answer pattern | Model |
|---|---|
| Every commit deployable, one environment, small team | Trunk-based, no release branches |
| Every commit deployable, versioned or pinned releases | Trunk-based with release branches |
| One production environment, review-based flow | GitHub flow |
| Code freeze, qualification, several supported versions | Release-train branches |
| Shipped or installed software with support windows | GitFlow |
| Untrusted contributors without write access | Fork-and-pull |

## Pull Request Description and Size Checklist

A description is complete when a reviewer can decide without opening the diff; a request is small enough when a
reviewer can hold it in one pass. Check both before requesting review.

Required decision content:

- Problem and impact: what breaks or is missing today, and who notices it.
- Approach: the change in two or three sentences, plus the rejected alternative when the choice is not obvious.
- Verification: commands run with their results, test names added, and manual steps or screenshots for UI changes.
- Risk and rollback: the risky hunks, the blast radius, the flag or revert path, and the migration or backfill plan.
- Linked issue and follow-ups: what this closes, what it defers, and which stacked request it depends on.

Size thresholds:

- Under 200 changed lines: normal review; one reviewer unless the risk class says otherwise.
- 200 to 400 changed lines: state why the change is one unit, and split when any part can land independently.
- 400 to 800 changed lines: split or stack before review; when it cannot be split, add a design note and a second
  reviewer.
- Over 800 changed lines: reject as one request unless it is mechanical (generated output, lockfile, rename) with
  the mechanical part isolated and the command that reproduces it.

Before requesting review:

- [ ] The title states the outcome and follows the commit format.
- [ ] The description answers the required content points.
- [ ] The linked issue closes only when its acceptance criteria are met.
- [ ] The diff contains no debug output, commented-out code, or unrelated edit.
- [ ] The author has read every hunk of the diff, including generated changes.
- [ ] The required checks are green, or the request stays a draft.

Self-review procedure before requesting review:

1. Read the diff hunk by hunk and mark every hunk the description does not explain.
2. Run the checks the review will run, including the linters and the documentation build.
3. Remove debug output, commented-out code, and unrelated edits from the diff.
4. Re-read the description against the final diff and correct stale statements before marking ready.

## Review Level Table

| Change class | Examples | Reviewers | Tests required | Docs required |
|---|---|---|---|---|
| Light | Comments, docs, formatting, test-only refactor, patch-level dependency update | 1 | Existing suite; a new test only when behavior changed | Update when a user-visible statement changes |
| Standard | Feature, bug fix, internal refactor, configuration default | 1 owner | A new or updated test proving the behavior, plus the affected suite | Update the page that documents the behavior |
| Risky | Auth, payments, permissions, crypto, data migration, public API, CI or release tooling | 2, including a domain or security owner | Unit, integration, negative and failure-path tests, and staging verification | Runbook, migration note, or API reference updated in the same request |

Rules: escalate a class rather than downgrade it when reviewers disagree; a light change that touches a risky path
becomes risky; record the class in the request; a risky change without its second reviewer waits instead of merging
with a promise of later review. A domain reviewer may join an unfamiliar area, but the owner's approval remains the
requirement, and only risky code changes require two approvals (governance and ownership changes take the
governance rule's two approvers).

## Review Comment Severity Taxonomy

| Severity | Prefix | Meaning | Author action | Merge effect |
|---|---|---|---|---|
| Blocking | `must:` | Defect, missing evidence, security or data risk | Fix and reply with the fix link | Blocks until resolved and approval renewed |
| Non-blocking | `should:` | Improvement worth doing now or explaining | Fix or reply with the reason not to | Does not block; the thread stays open until answered |
| Nit | `nit:` | Local preference or polish | Apply or ignore | Never blocks; the author decides |
| Question | `q:` | Question that needs an answer; asks for no change | Reply with evidence | Does not block |

Rules:

- Use exactly one severity per comment and write the ask, not only the observation: "move validation into the handler
  so the CLI path is covered" beats "this feels wrong".
- Treat an unmarked comment as `should:` and answer it; a review that is only nits is still a review, so mark them.
- Do not reopen a resolved thread without new evidence; open a new thread that references the resolved one.
- Take a disputed blocking comment to the decision owner for a ruling, never to a merge.
- Withdraw a comment the reviewer can no longer defend; a withdrawn comment is cheaper than an unresolved one.

## Branch Protection Rules Table

| Setting | Protected default | Exception and tradeoff |
|---|---|---|
| Required approvals | 1 for standard, 2 for risky paths; dismiss stale approvals on push | A solo-maintainer repository sets 0 and records a self-review, reported as a known gap |
| Required status checks | Build, test, lint, type check, secret scan, docs build where published | Skipping a check needs a policy change, not a per-request label |
| Linear history | Enabled on trunk when squash or rebase is the merge method | Release branches keep merge commits; configure per branch class |
| Force-push and deletion | Disabled on every protected branch and release tag | Revert forward; a rewrite of protected history is an incident |
| Administrator bypass | Off for the routine path; break-glass group only | Every bypass needs an actor, a reason, a request link, and a post-merge review |
| Conversation resolution | Required for blocking threads | Nits may stay unresolved after the author replies |
| Merge queue | Enabled when merge volume causes repeated integration failures | A low-volume repository runs the same checks on the head commit |
| Credentials | Never exposed to untrusted fork builds; storage policy belongs to the security process | A trusted branch receives only the credentials its job needs |

Exception path:

- Open the exception before using it and name the check being skipped, the reason, and the expiry.
- Record it in the request thread so the post-merge review can find it.
- Review the exception within one business day and decide whether the check or the policy needs to change.
- Repeat exceptions on the same check are a signal to fix the check, not to widen the policy.

Monthly audit:

1. Export the protected branch settings and required checks, and compare them with the documented policy.
2. List administrative merges, bypasses, and force-pushes since the last audit, and confirm each has a record and a
   post-merge review.
3. Confirm that tags created since the last audit point at release commits and that no tag was moved or deleted.
4. Report the counts and the fixes in the repository's operations notes; an unexamined bypass becomes the norm.

## CODEOWNERS Setup and Audit

Setup:

1. Confirm which locations the platform reads (`CODEOWNERS`, `.github/`, or `docs/`) and which one this repository
   uses; a file in the wrong location is silently ignored.
2. Start from the directory tree, not the team chart: list services, shared libraries, tooling, generated code,
   vendored code, and docs, then assign one team to each.
3. Place the broad fallback first and specific patterns after it, because the last matching pattern wins; a wildcard
   written last overrides every specific owner above it.
4. Prefer team handles, require owner review only on risky paths, and record the risk policy beside the pattern or in
   the repository's collaboration document.
5. Add a CI check that every changed path resolves to an owner and that every referenced team exists.

A minimal file, ordered so the specific patterns win:

```text
# Broad fallback first; the last matching pattern wins.
* @example-org/maintainers
/services/billing/** @example-org/billing-team
/infra/** @example-org/platform-team
/vendor/** @example-org/platform-team
```

Audit checklist:

- [ ] Every source directory resolves to a team, not only to the fallback.
- [ ] Every referenced team exists and has at least two members.
- [ ] Every required-review pattern matches at least one existing path.
- [ ] Generated and vendored trees point to the tooling owner, not to a service team.
- [ ] No path is owned only by a person who has left the organization.
- [ ] Ownership changes from the audit land in a maintainer-reviewed request.
- [ ] The audit result, interim owners, and next audit date are recorded.

Repair ownership drift:

- A reorganized team moves its patterns to the new handle in the same change that archives the old team.
- A removed service removes its patterns with the service, and the owner confirms the archive first.
- A team with fewer than two members gets a co-owner or points its paths at the parent team.
- A generated tree that acquired named owners resets to the tooling owner and deletes the accidental entries.

## History-Repair Decision Table

| Situation | Action | Approval | Risk |
|---|---|---|---|
| Unpushed commit has a wrong message or a missed file | Amend with `git commit --amend` | None; the commit never left the machine | Low; the commit is local and recoverable from the reflog |
| Several unpushed commits should become one or be split | `git reset --soft HEAD~n` and recommit | None; local history | Low; the working tree is preserved |
| An unpushed commit must be split into reviewable units | Interactive rebase on the local branch | None; local history | Low; verify the tree before pushing |
| Pushed topic branch needs a rewrite before review starts | Rebase, then push with `--force-with-lease` | The branch is personal and policy allows it | Medium; announce the push because comment anchors move |
| Pushed topic branch already reviewed and approved | Add follow-up commits; do not rewrite | Standard review of the delta | Medium; history stays append-only |
| Published main commit is wrong | `git revert` or a new fix commit | Normal review; never force-push main | Medium; the correction is visible forward |
| A credential was committed | Rotate it first, then follow the security incident process | Security owner; admin for any history rewrite | High; a rewrite does not un-leak a copied secret |
| Release tag points at the wrong commit | New patch tag from the fixed commit; keep the old tag | Release owner | High; installed artifacts must match their tag |
| Protected history must be rewritten | Freeze merges, take a backup, record the incident | Repository maintainer and a written record | High; every clone must reconcile |
| A reviewed stack must change its base commit | Rewrite the stack and announce the new head | Branch owner and every reviewer in the stack | Medium; each approval is renewed |
| A branch carries commits from several authors | Each author fixes their own commit | Each author | Medium; rewriting another person's commit needs their agreement |

Rules:

- Undo the smallest unit that fixes the problem, and prefer a forward fix over a rewrite.
- A lease is mandatory for every force-push; a bare `--force` is never approved.
- A rewritten branch that others based work on is an incident even when the content is correct.
- Announce a rewrite in the request thread and state which commits changed.

## Merge Queue and Auto-Merge Rules

Queue rules:

- Enqueue only after approval and when the head is green against the current base; the queue rebases and reruns the
  required checks, so a branch behind the base waits instead of merging stale.
- Never merge around the queue; a direct administrative merge while the queue is active follows the bypass path.
- On a queue failure, fix the request and push; re-request review when the fix is substantive, then re-enqueue
  rather than retrying the same entry and hoping for a different result.
- A request that waits in the queue for more than a day signals a slow or flaky check; fix the check or split the
  request instead of adding retries.

Auto-merge rules:

- Allow auto-merge to be enabled only after the required approving reviews exist; it is a scheduling convenience,
  never an early approval.
- Auto-merge inherits the branch's required checks, queue, and linear-history setting; it may not bypass a check or
  a stale approval.
- A risky path may use auto-merge only with the risky review count and a named rollback owner.
- Disable auto-merge when the base branch is red or a release freeze is active; the release owner controls freezes.
- Turn auto-merge off when the author cannot respond within the review turnaround, so the change does not land on a
  stale description.

Freeze rules:

- A release freeze pauses the queue for every request except the fixes the release owner names.
- A security incident bypasses the freeze only with the security owner's approval and a recorded exception.
- Reopen the queue after the freeze and re-enqueue each request after rebasing it onto the frozen tip.
