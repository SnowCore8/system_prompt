# Repository Governance Playbooks

Use this file with `SKILL.md` and `dimensions.md`. Each playbook is an ordered check for one governance task; the
dimensions file states the rule and this file turns it into steps. Apply the playbook for the repository's project
type, record the evidence for every item, and keep the exceptions in `GOVERNANCE.md`. A playbook item that does not
apply is recorded as "not applicable" with the reason, not silently skipped.

## New Repository Checklist

Create the repository in this order so the first push starts compliant; retrofitting these items later costs history
and a migration.

- Confirm the owning team, the purpose in one sentence, the project type, and the visibility before creating anything.
- Create under the organization that will outlive the project, not a personal account, and record the repository and
  package names approved by the naming skill.
- Set the description, topics, and homepage in the host settings; leave no field at a default value.
- Record the license decision from the owner and legal reviewer, then add the approved text at `LICENSE`.
- Add the README entry file at the recognized root path; the documentation role owns its content and structure.
- Add `.gitignore`, `.editorconfig`, and `.gitattributes` before the first commit, with the language and platform
  categories the project needs.
- Protect the default branch through the VCS collaboration skill's protection rules and reviewer counts; record the
  governance consequence that every merge resolves to an accountable role.
- Add `CODEOWNERS` for every mergeable path and let the VCS collaboration skill own its syntax, fallback, and
  validation mechanics.
- Add `SECURITY.md` at the recognized path before the repository becomes public; the security role owns its content and
  response commitments.
- Add `CONTRIBUTING.md` and `CODE_OF_CONDUCT.md` where the project-type inventory requires them; add `SUPPORT.md` when
  the issue tracker is the support route.
- Add issue forms and a pull request template where the project-type inventory requires them.
- Reserve the package name and the registry coordinates before the first release; the naming skill owns the name
  itself.
- Enable dependency alerts, secret scanning, and required status checks on the default branch.
- Schedule the first access review and inventory review, and record both dates.

## Required-File Inventory by Project Type

Use the project type column that matches the repository; "Required" means the file exists with the fields its purpose
needs, not merely that a filename exists. "Recommended" means add it when the condition applies, "Optional" is a
deliberate choice, and the archived column uses "Keep" to preserve, "Frozen" for no further edits, "Banner" for the
archive notice, and "Steward" for the named owner. A library is consumed by others, an application is deployed or
distributed, an internal service is used inside the organization, a docs-only repository publishes documentation, and
an archived repository is read-only.

| File or setting | Library | Application | Internal service | Docs-only | Archived |
|---|---|---|---|---|---|
| `README.md` | Required | Required | Required | Required | Banner |
| `LICENSE` | Required | Required | Required if shipped outside | Required | Keep |
| `CONTRIBUTING.md` | Required | Required | Recommended | Required | Not required |
| `CODE_OF_CONDUCT.md` | Required | Required | Not required | Recommended | Not required |
| `SECURITY.md` | Required | Required | Required | Required | Keep |
| `SUPPORT.md` | Required | Required | Optional | Optional | Not required |
| `CHANGELOG.md` | Required | Required | Recommended | Optional | Keep last entry |
| `CODEOWNERS` | Required | Required | Required | Recommended | Frozen |
| Issue templates | Required | Required | Optional | Optional | Not required |
| Pull request template | Required | Required | Recommended | Required | Not required |
| `.editorconfig` | Required | Required | Required | Required | Frozen |
| `.gitignore` | Required | Required | Required | Required | Frozen |
| `.gitattributes` | Required | Required | Required | Recommended | Frozen |
| `CITATION.cff` | Optional, research | Optional | Not required | Optional | Keep |
| `GOVERNANCE.md`, `MAINTAINERS.md` | Recommended | Recommended | Recommended | Optional | Steward |
| `.github/FUNDING.yml` | Optional | Optional | Not required | Optional | Not required |
| Docs index | Required with docs tree | Required with docs tree | Recommended | Required | Keep |
| Repository metadata | Required | Required | Required | Required | Description and homepage |

## Repository Metadata Settings

Set each field once, validate it from outside the repository, and change it only as part of a reviewed change.

| Setting | Required value | Checked in |
|---|---|---|
| Description | One sentence that names the job; no slogan, no empty value. | Host settings and package manifest. |
| Topics | Search terms users actually type; no more than ten. | Host settings. |
| Homepage | The docs or product entry point, and it resolves. | Host settings and manifest. |
| Default branch | The protected branch that CI and branch protection target. | Branch protection. |
| Visibility | Public only when license, security, and conduct files are ready. | Access audit. |
| License detection | Matches the `LICENSE` file and the manifest SPDX identifier. | Host license detection and manifest. |
| Releases | Enabled; versioning, timing, and tags follow the release-operations skill. | Release list. |
| Discussions | Enabled only with an owner and a response expectation. | Host settings. |
| Issue tracker | Enabled with templates, or redirected to the support route. | Host settings. |
| Merge strategy | One allowed method that matches the branch model. | Branch protection. |
| Security features | Dependency alerts, secret scanning, and code scanning enabled where available. | Security settings. |
| Archived flag | Set only after the archive checklist completes. | Host settings. |

## Hygiene Audit Checklist

Run this audit on schedule and before a transfer, a major release, or a repository split; record each result with the
command that produced it and the owner of any exception.

- [ ] A fresh clone plus the documented build leaves the working tree clean.
- [ ] `.gitignore` covers local configuration, credentials, build output, caches, and editor state.
- [ ] No tracked file matches an ignore rule and no ignored file is required to run the project.
- [ ] Every tracked file over the size threshold is in LFS or an artifact store.
- [ ] LFS is installed before checkout in every CI job that needs it.
- [ ] No generated file is tracked without a generator marker, and regeneration produces no diff.
- [ ] No vendored directory lacks upstream version, license, and patch list.
- [ ] Every submodule points at a reachable commit and states its purpose.
- [ ] Merged branches older than the retention window are deleted.
- [ ] Long-lived branches carry an owner and an exit date.
- [ ] Unpublished tags are removed and published tags are immutable.
- [ ] Monorepo packages build and test independently and CI selects them from changed paths.
- [ ] The default branch applies the VCS collaboration skill's protection rules.
- [ ] Secret scanning findings are reported and owned; no history rewrite starts without the owner's decision.
- [ ] The archival or active state matches the README, support page, and metadata.

## Maintainer Ladder and Permissions

Grant capability through host teams, not personal accounts, and review the grants on the access-review schedule.

| Role | Can | Cannot | Granted by |
|---|---|---|---|
| Contributor | Report issues, open pull requests, comment on proposals. | Merge, publish, change settings or access. | Platform account. |
| Reviewer | Approve a scoped change, request changes, triage a labeled area. | Merge the default branch, publish, manage access. | Maintainer nomination. |
| Committer | Merge non-default branches, label and assign issues, close stale issues. | Publish a release, change protection, add members. | Maintainer vote. |
| Maintainer | Merge default branch, publish and yank releases, manage teams and settings, appoint roles. | Change governance alone; delete or transfer alone. | Maintainer decision plus organization owner. |
| Organization owner | Transfer, archive, delete, and set organization-wide policy. | Override day-to-day code decisions without the maintainers. | Organizational appointment. |
| Emeritus maintainer | Retain credit and an advisory voice. | Approve, publish, or hold any access. | Maintainer decision after inactivity notice. |

## RFC Process Steps

Use a proposal for a public interface change, a breaking change, a new external dependency with wide impact, a
repository split or merge, a governance change, a license change, or a release-model change.

1. Check whether the change needs a proposal; if it does not, record the decision in the pull request instead.
2. Copy the proposal template and assign the next number; never reuse a number.
3. Fill problem, goals and non-goals, proposal, alternatives, risks, rollout, and open questions; name the affected
   project types and users.
4. Open the proposal where contributors can read and comment, and announce it on the stated channel.
5. Hold the comment window and answer objections in the document, not only in comment threads.
6. Move to a final comment period with a stated end; a proposal with an unresolved blocking objection does not advance.
7. Decide under the recorded decision model with the named approvers, and record accepted, rejected, or withdrawn with
   the rationale.
8. Link the implementation pull requests and the release that carries the change, and update the docs index.
9. Keep rejected proposals in the record with their reasons; reopen one only with new evidence.

## Archive and Transfer Checklist

Archive when the project stops; transfer when ownership moves. Both are irreversible enough to need the owner's
approval and a written record.

### Archive

- Announce the archive on the project channel and in the README banner with the last supported version and date.
- Set the archived flag and confirm issues, pull requests, and discussions accept no new entries.
- Close open issues and pull requests with a stated reason and point to the maintained fork or support route when one
  exists.
- Keep releases, tags, and the license available, and state that pinned versions remain installable.
- Ask the security role whether reports are still accepted, record the answer and its end date, and date the archive
  notice.
- Remove or rotate CI secrets, webhooks, deploy keys, and publishing tokens.
- Name the steward who owns the archived repository and its annual review.
- Keep the description, homepage, and topics accurate; an archived repository is still found by search.

### Transfer

- Confirm the receiving organization owns the name and accepts the maintenance obligations.
- Audit access, applications, webhooks, deploy keys, and package publish rights before the move.
- Transfer with redirects enabled and verify that old clone and web URLs still resolve.
- Update the manifest repository and homepage fields, package metadata, CODEOWNERS, and documentation links.
- Re-run CI in the new location, re-add secrets, and rotate every token that touched the old organization.
- Verify publishing under the new owner and confirm the registry shows the new repository URL.
- Announce the transfer and keep the old name claimed or redirecting for as long as the host allows.
- Remove the old organization's access after the redirect and publishing checks pass.

## Packaging and Release Publication Checklist

Publish only the artifact CI built from the approved tag after every gate passes; every item below is evidence that the
artifact is the one intended.

- [ ] The version is bumped in its single source and no other copy disagrees.
- [ ] The changelog entry states user-visible changes and upgrade actions.
- [ ] The manifest metadata is complete and valid for the registry.
- [ ] The tag is created on the approved release commit.
- [ ] The artifact is built in CI from that tag in a clean checkout.
- [ ] The full test suite passes against the built artifact.
- [ ] The install test passes in an empty environment from the staging registry.
- [ ] Every gate passes before publication; a failing gate deletes the tag before any publication.
- [ ] The artifact contents are inspected; no local paths, test data, or development dependencies are inside.
- [ ] The license, README, and required files are present in the artifact.
- [ ] Checksums, signature, and provenance are generated.
- [ ] The staged artifact digest matches the published artifact digest.
- [ ] Publishing runs with a package-scoped token from the protected release environment.
- [ ] The release-note document, owned by documentation, links the changelog and the artifact digest.
- [ ] Registry metadata is re-checked from a consumer account after publishing.
- [ ] Documentation, support pages, and the announcement reflect the release.
- [ ] A failed release is yanked or patched, never overwritten or rebuilt under the same version.

## Install Verification Script Outline

Run this outline in a disposable container or virtual environment after publication; Python is shown as one concrete
toolchain, so substitute the ecosystem's install and smoke commands. The exit code and the printed version are the
evidence to record with the tested runtime matrix.

```bash
#!/usr/bin/env bash
set -euo pipefail

package="example-package"
version="1.2.3"
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT

# Start from an empty environment: no project checkout, no local path override.
python3 -m venv "$work/venv"

# Install only the published artifact, pinned to the released version.
"$work/venv/bin/python" -m pip install --no-cache-dir "${package}==${version}"

# Assert the resolved version and that the public entry point loads.
"$work/venv/bin/python" -c "import importlib.metadata as m; print(m.version('example-package'))"
"$work/venv/bin/python" -c "import example_package; print(example_package.__name__)"

# List installed distributions to catch development dependencies that leaked in.
"$work/venv/bin/python" -m pip freeze
```

- Repeat the outline on every runtime and operating system in the supported matrix.
- For a command-line package, replace the import check with the help command and one documented example invocation.
- Compare the installed artifact digest with the published digest; a mismatch stops the announcement and starts an
  incident.
