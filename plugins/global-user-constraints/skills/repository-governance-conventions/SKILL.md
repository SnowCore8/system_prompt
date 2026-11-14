---
name: repository-governance-conventions
description: Defines, reviews, and repairs the required files, hygiene, governance, and packaging practice of any repository, from community documents and metadata to branch, artifact, role, and publication policy. Use when creating a repository, auditing a public or internal repository, assigning maintainer roles and routing approval authority, or preparing and verifying a package release.
argument-hint: '[path or scope]'
---

# Repository Governance Conventions

Repository governance fails silently. A repository without a license looks complete until someone cannot legally use
it; an unowned directory merges unreviewed changes for months; a package builds on one maintainer's machine and then
fails in a clean environment; a dead project stays public with open issues and a green release badge. None of these
failures shows up in a diff, and each one is expensive when it is discovered. This skill gives one procedure and a
complete rule set for the required files and metadata of a repository, its hygiene, its decision process, and the
packaging and distribution it publishes. Governance is cheap at creation and expensive to retrofit: a missing license
costs a legal review once the project is popular, while adding it on day one costs one file and one decision.

## Scope and Precedence

Apply the first rule that fits, and do not mix standards inside one scope:

1. Organization-wide policy. A hosting platform setting, legal template, registry rule, or company policy that applies
   to every repository is not optional, and it wins over this skill and over a repository's local preference. A
   repository-level file that contradicts it is a defect, not a local exception.
2. Existing repository convention. Read the current file inventory, metadata, branch model, and manifest before
   inventing policy; follow a stricter local rule over this one, and record a local rule that relaxes this skill in
   `GOVERNANCE.md`.
3. This standard's defaults, when the two levels above are silent.
4. Personal preference, which never overrides the three levels above; a preference never justifies a missing required
   file.

- Required files and their metadata are this skill's ownership: which files must exist, where they sit, and which
  metadata fields they carry. The content and templates of the README, CONTRIBUTING guide, decision records, and other
  documents belong to the documentation skill, which also decides structure and voice; this skill requires the file at
  the recognized path and reachable from the repository entry points. License policy and the security file's content
  belong to the security and compliance skill; this skill owns the files' presence and their required metadata fields.
- Repository-level hygiene and layout are this skill's ownership; repository, package, and file names belong to the
  naming skill. Branch, pull request, review, reviewer counts, and CODEOWNERS mechanics belong to the VCS collaboration
  skill; this skill owns the roles and the governance decisions those mechanics enforce. Version numbers, release
  timing, and per-release-type approvals belong to the release-operations skill; release-note documents belong to the
  documentation skill; this skill owns manifest metadata, distribution channels, and archive or transfer.
- Repository settings and templates that support CI gates are this skill's ownership; the gate definitions and pass
  criteria belong to the testing and quality skill. A repository that cannot run its own required checks has a
  governance defect in addition to a test defect, so report the gap here and fix the gate with its owner.
- A repository is a product surface. The README, license, templates, package metadata, and default branch are read by
  users and by tools, so review a governance change like a product change rather than as housekeeping.
- Organization-wide policy wins on conflict. When a hosted setting or a company rule disagrees with a repository file
  here, state the difference, follow the organization policy, and fix the repository file so the next reader sees one
  rule.
- Generated metadata is exempt from hand-editing: a generated manifest field, a synced template, and a lock file are
  changed at their source of truth, regenerated, and verified.
- When two rules conflict, state the conflict and the chosen rule, and record the decision in `GOVERNANCE.md` or a
  decision record so the next change follows it.

## Process

1. Classify the repository as a public library, application, internal service, documentation-only project, or archived
   project. Record the type: it selects the required inventory, the metadata, and the review depth. Reclassify at every
   review, because a project that gains external users or stops shipping changes type.
2. Read the current state before changing anything: root files, hosting settings, protected branch rules, environment
   secrets, manifest, registry links, and archive status. Write down what exists and what is missing.
3. Compare the repository against the required inventory for its type. List missing, misplaced, stale, and invalid files
   and metadata, and name an owner and a due action for each. A present file with empty required fields counts as
   missing.
4. Repair hygiene first: tracked versus ignored files, large and generated artifacts, stale branches and tags,
   submodules, vendored code, and workspace layout. Hygiene decides what every later review sees, so record every
   deletion and its reason.
5. Establish the governance: roles and the permission ladder, the decision model, the approval rules it routes to the
   owning skills, the proposal path, the code of conduct enforcement route, and release authority. Record it in
   `GOVERNANCE.md`, confirm every mergeable path resolves to an accountable role, and check that the roles match the
   permissions the host actually grants.
6. Repair packaging and distribution: manifest metadata, registry channels, signing and provenance, install
   verification, and the yank and deprecation path for published versions. Test the install from the registry, not from
   the workspace.
7. Verify the result: run the inventory and metadata checks, install from a clean environment, confirm the archive or
   transfer state, and record the evidence and the next review date. If an item cannot be fixed now, record an owner
   and a due date, mark the repository out of compliance, and report every open item.

## Core Rules

- **Required means valid, not merely present.** Put every required file at the path the host and the tooling recognize
  and fill the metadata fields it carries; a `SECURITY.md` outside the recognized path is missing for every tool, and a
  required file that names no owner is a stub in the right location.
- **License before the first public push.** Add the full license text under the exact `LICENSE` name, confirm the host
  detects the same license, and mirror the identifier into the package manifest; treat a license change as a legal
  decision for the owner, because a repository without a license grants no reuse rights.
- **Every mergeable path has an accountable role.** Ensure each top-level directory and release-critical file resolves
  to an active role; the VCS collaboration skill owns the CODEOWNERS mapping and validation mechanics, while an
  unassigned path is a governance failure because it merges without a responsible reviewer.
- **Name the decision model in writing.** State in `GOVERNANCE.md` whether decisions are maintainer-led, lazy
  consensus, or a vote, how long the comment window lasts, and what counts as approval; a model kept in memory blocks
  every new contributor and produces a dispute on the first contested change.
- **Route approvals; do not redefine them.** Take reviewer counts for code changes from the VCS collaboration skill and
  per-release-type approvals from the release-operations skill, adding only this skill's rule that a governance or
  ownership change needs two approvers; a local threshold that contradicts the owning skill is a defect.
- **Treat protection failures as governance failures.** An unprotected default branch, an unreviewed merge, or a
  rewritten history is a governance defect; the VCS collaboration skill defines the protection and history-repair
  mechanics.
- **Tracked and ignored are disjoint.** A fresh clone plus build leaves no tracked file modified and no ignored file
  needed to run; local configuration, credentials, build output, and editor state stay ignored.
- **Do not commit what the build produces.** Track generated code, compiled artifacts, vendored dependencies, and
  generated manifests only with a recorded source, command, and version; otherwise generate them in CI and ignore
  them. A lock file is an input when the tool requires it, so commit it under that rule and nowhere else.
- **Assets carry a size policy.** Set a size threshold, put files above it and per-build binaries in Git LFS or an
  artifact store, track them by pattern in `.gitattributes`, and do not rely on history rewriting to fix a slow clone.
- **Clean branches and tags on a schedule.** Delete merged branches within the stated window, give abandoned branches
  and long-lived branches an owner and an exit date, delete tags that never became a release, and never delete or move
  a published tag.
- **Tag, gate, then publish.** Create the tag on the approved release commit, build the artifact from that tag in a
  clean checkout, run the gates, and publish only after they pass; a failing gate deletes the tag before publication,
  and the tag becomes immutable once an artifact is published. Verify the installed artifact from an empty
  environment, and never rebuild a published version.
- **Published versions are immutable.** Never reuse, re-tag, or overwrite a version; deprecate a version with a
  replacement or yank it with a stated reason, then publish a new patch. A yanked version stays resolvable for pinned
  users and stops installing for new ones.
- **Record succession before it is needed.** Give at least two maintainers administrative access, name an inheritor in
  `MAINTAINERS.md`, remove access when a maintainer leaves, and move a long-inactive maintainer to emeritus with
  notice. Review access on a schedule and after every departure.
- **Archive, do not abandon.** When a project stops, set the archived flag, add a banner to the README, close or
  redirect the issue and support paths, keep releases and the license available, name the steward, and remove CI
  secrets and webhooks that no longer serve the project.

## File Inventory Matrix

The per-type inventory in `references/playbooks.md` is the authority for these conditions. "Owner" names the role
accountable for presence and metadata; document content and templates follow the documentation role, and security
policy content follows the security and compliance role.

| File or setting | Purpose | Required for | Owner |
|---|---|---|---|
| `README.md` | Be the recognized entry point for users and tools. | All active types; archived keeps a banner. | Repository owner |
| `LICENSE` | Grant reuse terms with the license text. | Libraries, applications, and docs-only; internal projects that ship outside; archived keeps it. | Repository owner with legal review |
| `CONTRIBUTING.md` | Open the contributor path. | Libraries, applications, and docs-only; recommended for internal services. | Maintainer |
| `CODE_OF_CONDUCT.md` | State the expected behavior and enforcement route. | Libraries and applications; recommended for docs-only. | Community manager |
| `SECURITY.md` | Make the security reporting path discoverable; content owned by security. | All active types; archived keeps it. | Security owner |
| `SUPPORT.md` | Publish the support route. | Libraries and applications; optional for internal services and docs-only. | Maintainer |
| `CHANGELOG.md` | Record what users must know per release. | Libraries and applications; recommended for internal services. | Release manager |
| `CODEOWNERS` | Make every mergeable path resolve to an accountable role; mechanics owned by VCS. | Libraries, applications, and internal services; recommended for docs-only. | Maintainer |
| `.github/ISSUE_TEMPLATE/` | Structure report intake. | Libraries and applications; optional for internal services and docs-only. | Maintainer |
| `.github/PULL_REQUEST_TEMPLATE.md` | Ask for the evidence a reviewer needs. | Libraries, applications, and docs-only; recommended for internal services. | Maintainer |
| `.editorconfig` | Fix editor defaults across the repository. | All active types; archived frozen. | Maintainer |
| `.gitignore` and `.gitattributes` | Keep local artifacts untracked and set line-ending and LFS behavior. | `.gitignore` all active types; `.gitattributes` for code repositories, recommended for docs-only. | Maintainer |
| `.github/FUNDING.yml`, `GOVERNANCE.md`, `MAINTAINERS.md`, `CITATION.cff` | Record sponsorship, roles, succession, and citation. | `GOVERNANCE.md` and `MAINTAINERS.md` recommended for code repositories, optional for docs-only; FUNDING optional; CITATION for research output. | Maintainer |
| Repository metadata | Set description, topics, homepage, default branch, visibility, releases, and discussions. | All active types; archived keeps description and homepage. | Repository owner |

## Dimension Index

Each dimension has detailed rules, examples, and edge cases in `references/dimensions.md`.

| Dimension | First rule |
|---|---|
| 1. Required community files and metadata | Every required file sits at the recognized path and carries the fields its purpose needs. |
| 2. Repository hygiene | Nothing tracked is generated, oversized, or locally configured, and stale branches have an owner. |
| 3. Governance and decision process | The decision model, routed approval rules, and successor are named in writing. |
| 4. Packaging and distribution | Publish a signed artifact from CI and prove it installs in an empty environment. |

## Anti-Patterns

| Anti-pattern | Why it fails | Fix |
|---|---|---|
| A license name in `LICENSE.md` with no license text | Host detection and legal review both fail, so consumers cannot rely on the terms. | Put the full text in `LICENSE` and confirm host detection. |
| `CODEOWNERS` names a role that no longer exists | The affected paths have no accountable reviewer and merge unowned. | Re-validate assignments each quarter against active roles. |
| Empty README on a public repository | Users file issues and wait for a product that does not exist. | Keep the repository private or archive it until the first working release. |
| Committing build output | History grows, clones slow down, and stale binaries ship from the tree. | Ignore outputs, build in CI, and attach artifacts to releases. |
| A large binary committed "just once" | Every clone and mirror carries it forever. | Move it to LFS or an artifact store before the first push. |
| Merged branches kept indefinitely | The branch list hides active work and invites cherry-picks from stale heads. | Delete after merge and keep a naming rule for long-lived branches. |
| Default-branch protection is absent | History rewrites and unreviewed merges can destroy reviewed work. | Enforce the VCS protection rules and treat the merge as unreviewed. |
| One maintainer with all access | The repository stalls or is lost when that person leaves. | Add a second administrator and name an inheritor. |
| `SECURITY.md` missing or off the recognized path | Reporters do not find the reporting route and may file a public issue. | Put the file at the recognized path and record its owner; security owns its content. |
| Publishing without a tagged, gated build | The artifact's inputs are unknown and cannot be rebuilt. | Publish only the CI artifact built from the approved tag after every gate passes. |
| Re-publishing a version after a bad release | Caches and lock files keep serving different content under one version. | Yank with a reason, then publish a patch version. |
| Archived repository left fully writable | Users assume it is maintained and open issues nobody answers. | Archive it, banner the README, and redirect support. |
| Transfer without redirects and metadata updates | Old links, clones, and package pages break. | Use host redirects and update manifest, docs, and package metadata. |
| Description differs between host and manifest | Search results and the package page describe different projects. | Keep one source and validate the mirror in CI. |

## Review Checklist

- [ ] The project type is recorded and matches a row in the required-file inventory.
- [ ] `README.md`, `LICENSE`, and `SECURITY.md` are present at recognized paths for the required project type.
- [ ] `LICENSE` holds the full text and the host detects the same license.
- [ ] `CONTRIBUTING.md` covers setup, tests, and the submission path from a fresh clone.
- [ ] `CODE_OF_CONDUCT.md` names the enforcement contact and the escalation route.
- [ ] `SECURITY.md` is present at the recognized path and records its owner.
- [ ] Every mergeable path resolves to an accountable role, and assignments name only active roles.
- [ ] Issue and pull request templates ask for the fields a triager and a reviewer need.
- [ ] `.gitignore` covers local configuration, credentials, and build output.
- [ ] `.gitattributes` sets line endings, LFS patterns, and generated-file markers where needed.
- [ ] No tracked file exceeds the size policy; large assets use LFS or an artifact store.
- [ ] Generated and vendored files carry a marker and their source or version.
- [ ] Stale branches and unpublished tags are removed or carry an owner and a date.
- [ ] `GOVERNANCE.md` or `MAINTAINERS.md` states roles, decision model, routed approval rules, and succession.
- [ ] Manifest metadata matches repository metadata and the current version.
- [ ] The package installs and runs from a clean environment using only published artifacts.
- [ ] Release artifacts are signed and published only after every gate passes on the approved tag.
- [ ] Archived repositories are read-only, bannered, and unlinked from active documentation.
- [ ] Access is reviewed on schedule, and departed maintainers hold no permissions.
- [ ] The inventory review and the metadata review have an owner and a scheduled date.

## Examples

<example>
A public repository has no license. Add the full license text as `LICENSE`, confirm the host detection matches,
mirror the identifier into the package manifest, link the license from the README, and give that section an owner who
reviews it with each release.
</example>

<example>
`CODEOWNERS` has a catch-all fallback, but `infra/` has no accountable role. Assign an accountable role for `infra/`
and have the VCS owner validate the mapping and its fallback on a test pull request, then re-check every top-level
directory.
</example>

<example>
A release built on a laptop fails to import in a clean container because one dependency is undeclared. Add the
dependency, build in CI, install the produced artifact in an empty environment, then publish a patch version and
state the fix in the changelog; do not reuse the failed version.
</example>

<example>
A project stops. Set the archived flag, put a banner and the last supported version in the README, disable issues and
discussions, keep releases and the license available, and name the steward who answers security reports.
</example>

<example>
A repository moves to a new organization. Use the host redirect, update the manifest repository and homepage fields,
package metadata, CODEOWNERS, CI secrets, and documentation links, verify that an old clone URL still redirects, then
publish from the new location.
</example>

## References

Read [references/dimensions.md](references/dimensions.md) for the detailed rules, good and bad examples, and edge
cases of the four dimensions. Read [references/playbooks.md](references/playbooks.md) for the checklists: new
repository setup, required-file inventory by project type, metadata settings, hygiene audit, maintainer ladder, RFC
process, archive and transfer, packaging, and install verification. Read both when establishing governance from
scratch; during routine work, read the dimension that applies and the playbook for the task at hand, because the
dimension states the rule and the playbook turns it into ordered checks.
