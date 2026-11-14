# Repository Governance Dimensions

Use this file with `SKILL.md`. Each section gives the rules, good and bad examples, and edge cases for one governance
dimension. When an organization policy or an existing repository convention already covers a point, read it first and
apply the higher-precedence rule; this file supplies the default and the reason. Section numbers match the dimension
index in `SKILL.md`, and `playbooks.md` turns each dimension into ordered checks. Read the section that matches the
repository decision in front of you. The dimensions run from what a reader sees first to what a consumer installs, so
repair an earlier dimension before trusting a later one: a missing owner or a wrong ignore rule hides the rest of the
audit.

## 1. Required Community Files and Metadata

A required file works only when it sits at a recognized path and carries the fields its purpose needs; presence alone
is a filename, not governance. The project type selects which rows apply, and the inventory in `playbooks.md` settles a
conflict between types.

- Place each required file where the host and the tools look for it: `README.md`, `LICENSE`, `SECURITY.md`,
  `CONTRIBUTING.md`, `CHANGELOG.md`, and `CODEOWNERS` at the root or the host's documented alternate location; issue
  and pull request templates under `.github/`; the docs index at `docs/README.md` or the docs root. A correctly named
  file in a different directory is missing for every tool that consumes it. The README exists at the recognized path
  and is reachable from the repository entry points; its content, structure, and prose follow the documentation role.
- Ship the full license text under the exact name `LICENSE`, with no `.md` or `.txt` suffix, and mirror the SPDX
  identifier into the package manifest. A name without terms, or a README line that says "MIT" with no file, leaves
  consumers and license scanners without terms; a license change is an owner decision, not an edit.
- Treat CONTRIBUTING, CODE_OF_CONDUCT, and SUPPORT as one contributor contract: CONTRIBUTING gives setup, test, and
  submission steps; CODE_OF_CONDUCT states expected behavior and a private enforcement contact; SUPPORT states what is
  in scope and sends security reports to the security file. A copied code of conduct with a blank contact line is
  worse than none, because it promises a route that does not exist.
- Own only the presence, location, and basic metadata of SECURITY.md: the file exists at the recognized path, is
  reachable, names its owner, and carries a review date. The security and compliance skill owns its required content,
  reporting commitments, and response window; the documentation skill owns its structure and prose. An internal
  service still needs the file, because its reports must not become public issues either.
- Route review and intake by consequence: every mergeable path resolves to an accountable role, with the CODEOWNERS
  mapping and validation mechanics owned by the VCS collaboration skill, which also owns the required fields of the
  issue and pull request templates. Require only fields a triager or reviewer uses, because an unused field teaches
  contributors to skip every field.
- Keep the remaining project records, with the fields their purpose needs: CHANGELOG lists user-visible changes by
  version and the upgrade action each one needs; GOVERNANCE states the decision model and thresholds; MAINTAINERS names
  active maintainers and an inheritor; CITATION.cff carries title, authors, version, date, license, and repository;
  `.github/FUNDING.yml` lists the sponsorship channels; the docs index maps reader tasks to core pages.
- Fix repository-wide file behavior in the root dotfiles: `.editorconfig` sets UTF-8, LF, final newline, trimmed
  trailing whitespace, and indentation; `.gitignore` covers local configuration, credentials, build output, caches, and
  editor state; `.gitattributes` sets end-of-line normalization, LFS patterns, and generated-file or export markers.
- Treat repository metadata as required fields: the description is one sentence that names the job, topics are the
  terms users search, the homepage is the product or docs entry point, the default branch is what protection and CI
  target, and visibility, releases, and discussions are deliberate settings. Mirror description and homepage in the
  package manifest so the repository page and the package page cannot disagree.

| Good | Bad | Why |
|---|---|---|
| `LICENSE` holds the full text and the manifest its SPDX identifier. | `LICENSE.md` contains only the license name. | Detection, legal review, and scanners need the terms and identifier. |
| `SECURITY.md` sits at the recognized path and records its owner. | The security route exists only in a README paragraph. | Tools and reporters look for the file; security owns the commitments. |
| `README.md` exists at the recognized path and links the entry points. | The entry documentation lives only in a wiki. | Tools and readers start at the recognized file; documentation owns its content. |
| Every mergeable path resolves to an accountable role. | Paths with no assigned role merge without a reviewer. | An unowned path is the governance failure; the VCS skill owns the mapping mechanics. |
| Issue forms require version, environment, reproduction, and logs. | Blank issues are enabled with no template. | Triagers spend the first reply collecting basics. |
| `.editorconfig` sets UTF-8, LF, and a final newline. | Editors write mixed CRLF and LF. | Diffs churn and scripts see carriage returns as data. |
| `.gitattributes` marks LFS patterns, generated files, and export filters. | `.gitignore` is used to hide tracked binaries. | Ignore rules never apply to files already tracked. |
| CHANGELOG groups entries by impact and states the required upgrade action. | The changelog is a dump of the commit log. | Readers cannot find the change that needs an upgrade step. |
| CITATION.cff carries title, authors, version, date, license, and repository. | A README sentence asks readers to "cite this project". | Citation tools need structured fields. |
| GOVERNANCE.md names the decision model, the comment window, and the tie-breaker. | "Maintainers decide." | A contested change stalls because no rule says how it ends. |
| CONTRIBUTING goes from a fresh clone to a passing test in one path. | CONTRIBUTING lists style rules only. | A new contributor cannot reproduce the build. |
| The code of conduct names a private enforcement contact. | A copied template leaves the contact blank. | Reports have nowhere to go and enforcement is theater. |
| Host description and manifest description are the same sentence. | The repository and package pages describe different projects. | Users and search results see two projects. |
| The default branch is the protected branch that CI and hosting settings target. | The default branch is unprotected and renamed in one tool. | Unreviewed changes reach what consumers install. |
| The docs index maps reader tasks to the core pages. | `docs/` holds dozens of unlinked files. | Readers cannot reach the page that would help them. |
| MAINTAINERS.md names current maintainers and an inheritor. | Admin access is the only record of who maintains. | Access is not a roster, so succession is unknown. |

## 2. Repository Hygiene

Hygiene is what every later review sees: the file tree, the history, and the branch list either support review or hide
the truth. Audit it on a schedule and before any transfer, because these facts are cheap to inspect early and
expensive to repair once users depend on them.

- Keep tracked and ignored files disjoint: a fresh clone plus build leaves no tracked file modified and no ignored file
  needed to run. Ignore local configuration, credentials, build output, caches, and editor state, and verify the result
  with a clean checkout instead of trusting the pattern list.
- Do not commit what the build produces. Generated code, compiled artifacts, and generated manifests are tracked only
  when consumers need them without the build tool, and then the file carries the generator name and version in its
  header, a CI check regenerates and diffs it, and nobody hand-edits it. A lock file is an input when the tool requires
  it; state that rule and follow it in every package.
- Set the size and asset policy before history grows: a default threshold near 10 MB, a required `.gitattributes`
  pattern for files above it, LFS available in every clone and CI job, release binaries attached to the release rather
  than the tree, runtime media optimized before commit, design sources kept in the design tool or in LFS, license and
  origin recorded for every asset, and `export-ignore` excluding source assets from packages. Migrating existing large
  objects rewrites history, so propose it as a coordinated change with a clone freeze instead of running it
  unilaterally, and treat an asset with no provenance as unshippable.
- Clean branches and tags on a schedule: delete merged branches within the stated window, give a long-lived branch an
  owner and an exit date in its description, remove branches with no commits for the stated stale period, tag releases
  on the release commit with annotated tags, delete tags that never became a release, and never move or delete a
  published release tag.
- Pin submodules and vendored code: a submodule points at a commit, names its purpose in the parent repository, and is
  reachable from CI; a vendored directory carries the upstream version, license, and patch list, so a future update is
  a repeatable procedure. Prefer a package dependency over a copy, and never track a moving branch or silently edit a
  vendored file.
- Structure a monorepo as a workspace: one root manifest and lock file, one package manifest per package directory,
  shared tooling configuration at the root, explicit package boundaries instead of deep relative imports, ownership
  per package in CODEOWNERS, and CI that selects affected packages from the changed paths. A monorepo without
  boundaries is a single project with many directories.
- Apply an archive policy to dead projects: set the archived flag, make the repository read-only, banner the README
  with the last supported version and the reason, close or redirect issues and discussions, keep releases and the
  license available, state whether security reports are still accepted, and name the steward. Review the archive
  annually and link a maintained fork only when it is a separate, clearly identified project.
- Handle transfer, rename, mirrors, and forks as coordinated changes: transfer to the receiving organization with host
  redirects, then update the manifest, package metadata, CODEOWNERS, CI secrets, webhooks, and documentation links and
  verify that an old clone URL still redirects. Declare the canonical repository in a mirror and its sync direction,
  and treat a fork as a copy that is not a backup and not a distribution channel unless the project says so.

| Good | Bad | Why |
|---|---|---|
| `.gitignore` lists `.env`, `dist/`, `.cache/`, and editor directories. | A broad `*.json` ignore hides tracked configuration. | Broad patterns make required files invisible to the whole team. |
| A fresh clone plus build leaves the working tree clean. | The build rewrites a tracked generated manifest. | A tracked output produces constant unrelated changes. |
| A 200 MB media file lives in LFS or on the release page. | The video is committed to history once. | Every clone and mirror pays the cost forever. |
| Generated code carries the generator and version in its header. | A generated client is hand-edited in place. | The next regeneration silently removes the edit. |
| Merged branches are deleted within the stated window. | Hundreds of merged branches remain. | The branch list hides active work and invites stale cherry-picks. |
| An annotated tag marks the release commit. | The tag points at a later unrelated commit. | Installers build from a tree nobody tested. |
| A submodule is pinned to a commit and its purpose is recorded. | A submodule tracks a moving branch. | Builds differ by day and cannot be reproduced. |
| A vendored directory has upstream version, license, and patches. | A copy of upstream `main` carries local edits. | Provenance and the update path are unknown. |
| A monorepo has a root workspace manifest and package manifests. | Packages import through deep relative paths. | Boundaries break and CI cannot select affected packages. |
| An archived repository is read-only with a banner and last version. | Only the archive flag is set and issues stay open. | Users assume maintenance and get no answer. |
| A transfer keeps redirects and updates metadata and links. | Old links, clones, and package pages stop working. | Users cannot find the project after the move. |
| A fork documents the canonical repository and sync direction. | The fork carries unique fixes and is passed around. | Users install a stale or diverging copy. |
| CI installs LFS before checkout. | CI checks out LFS pointers as text. | Builds fail or ship broken files. |
| Release binaries are attached to the release. | Binaries are committed under `dist/`. | History bloats and stale artifacts ship from the tree. |
| `.gitattributes` normalizes text and excludes source assets from packages. | Mixed line endings and design sources ship in the package. | Diffs and package behavior differ per platform. |
| Dead code is removed with references checked first. | A bulk deletion runs without a reference check. | Broken links and imports surface after the cleanup. |

## 3. Governance and Decision Process

Governance is the written answer to who decides, how a decision is made, and who inherits the repository when the
current maintainers leave. Write it down before it is contested, because a rule invented during a dispute reads as an
interest rather than a policy.

- Define the ladder by capability, not by title: a contributor proposes changes, a reviewer approves a scoped change, a
  committer merges non-default branches and triages issues, and a maintainer merges the default branch, publishes
  releases, manages access, and appoints the other roles. Record each capability in `GOVERNANCE.md` and grant it
  through a host team rather than a personal account.
- Declare the decision model: maintainer-led for a single-team project, lazy consensus with a stated window for a
  community project, or a formal vote with quorum, majority, and tie-break for shared governance. Write down which
  model applies to which class of change, and record every decision with its rationale and the alternatives considered.
- Run proposals through a stated path: number the proposal, use a fixed template with problem, goals and non-goals,
  proposal, alternatives, risks, rollout, and open questions, keep a comment window, close with a final comment period,
  and record the accepted or rejected outcome. A design decided in a chat thread loses its rationale once the thread
  scrolls away.
- Route approval instead of setting it: reviewer counts for code changes come from the VCS collaboration skill,
  per-release-type approvals come from the release-operations skill, and this dimension adds only its own governance
  rule that a governance or ownership change needs two approvers and that an author never approves their own governance
  or ownership change. Record the routed rules in `GOVERNANCE.md` so readers see one policy.
- Plan for succession and bus factor: at least two maintainers hold administrative access, an inheritor is named in
  `MAINTAINERS.md`, hosting access is escrowed or recoverable by the organization, an inactive maintainer moves to
  emeritus after notice, and access is reviewed quarterly and after every departure. A repository with one
  administrator is one absence away from being lost.
- Resolve conflict with a rule: discuss in the proposal, escalate to the maintainers, then to the named tie-breaker,
  and record the decision and dissenting view. Keep the status quo until a decision is recorded, do not merge a change
  that is still contested, and route personal-conduct matters to the code of conduct process rather than the technical
  thread.
- Make the code of conduct enforceable: reports go to a private channel, at least two responders handle them, a
  responder with a conflict of interest recuses, confidentiality is stated, outcomes range from a warning to a
  temporary or permanent ban, the outcome is recorded without personal data, and an appeal route exists. Publishing
  incident details to demonstrate enforcement harms the person the process protects.
- Set release authority explicitly: name who can tag, publish, and yank, defer the per-release-type approval rule to
  the release-operations skill, separate the author role from the publisher role for major releases, keep signing keys
  offline and rotated, and give the emergency release path a named authority and a mandatory retrospective. A package
  token on every maintainer's laptop makes every compromised account a release risk.

| Good | Bad | Why |
|---|---|---|
| The role ladder lists capabilities and the host team that grants each. | Roles are job titles with no permission mapping. | Expectations and permissions are both undefined. |
| Lazy consensus states a window and requires explicit objections. | "Silence means approval" for every change. | A contested change passes because nobody watched the thread. |
| A numbered RFC records the decision, rationale, and rejected options. | The design is decided in a chat thread. | The rationale is lost and the same debate returns. |
| Approval rules are routed to the owning skills; governance and ownership changes need two approvers. | One local threshold covers every change. | A local count contradicts the owning skills and slows or under-reviews changes. |
| Two administrators and a named inheritor exist. | One owner holds all access. | The project is lost when that person leaves. |
| A long-inactive maintainer moves to emeritus after notice. | Inactive accounts keep administrative access. | Dormant credentials remain exploitable. |
| A conflict escalates to maintainers and then a named tie-breaker. | An endless thread has no decision rule. | The project stalls and contributors leave. |
| Code of conduct reports go to a private response group. | Reports are handled in the public issue tracker. | The reporter and the report are exposed. |
| Enforcement outcomes are recorded without personal data. | Full incident details are copied into a public log. | The record harms the person it should protect. |
| Per-release-type approval comes from the release-operations skill. | Any maintainer approves their own release. | A locally invented approval rule conflicts with the release playbook. |
| An author cannot approve their own governance or ownership change. | The author approves their own governance change. | Independent approval protects the rules from self-serving edits. |
| Governance or ownership changes need two maintainers to approve. | One maintainer edits the governance file in a commit. | Two independent approvers keep the rules from being edited unilaterally. |
| A declined proposal is recorded with its reason. | Rejected proposals disappear without a decision. | The same proposal returns every quarter. |
| Access is reviewed quarterly and after each departure. | Access is granted at onboarding and never removed. | Permissions accumulate and outlive their justification. |
| The emergency release path has a named authority and a review. | The emergency path silently bypasses every gate. | Speed is preserved but the bypass is never audited. |
| Release authority is a role, not a person. | Only one person's token can publish. | A vacation or departure blocks every release. |

## 4. Packaging and Distribution

Packaging is the last mile of governance: a correct repository that publishes an unverifiable or uninstallable
artifact has still failed its users. Judge every rule from the consumer's side, because it is satisfied only when a
stranger can install and inspect the artifact.

- Reserve the package name and scope before the first release and keep one artifact per name; package and repository
  naming itself belongs to the naming skill. Publish rights belong to an organization team, not a personal account, and
  a rename publishes under the new name with a deprecation pointer from the old one.
- Make the manifest exact: name, version, description, SPDX license, repository URL, homepage, keywords, author or
  maintainer, supported runtime range, and a files allowlist. Validate it with the registry's own tooling before
  publish, derive the version from one source, and keep local paths, credentials, and development dependencies out of
  the published artifact.
- Declare the distribution channels: one primary registry is the canonical channel for the versions the
  release-operations skill defines, a private or staging registry serves internal promotion, mirrors state their sync
  direction, and package visibility is a deliberate public or private setting. Credentials live only in the CI
  environment, and promotion from staging to production repeats the same install test rather than copying trust.
- Sign and attest every artifact: publish checksums, sign the artifact or the tag with a key stored outside the
  repository, and attach build provenance that names the source commit, the build platform, and the dependency set.
  Consumers and automated installers can then verify what they receive, and a compromised build host is detectable
  after the fact.
- Verify the install from an empty environment: a fresh container or virtual environment with no project checkout, no
  local path overrides, and no cache; install the exact published version from the registry, confirm the resolved
  version, run one smoke test through the public entry point, confirm the license and required files ship in the
  artifact, and record the output with the runtime versions tested.
- Publish in the order the release-operations skill defines: the tag is created on the approved release commit, the
  artifact is built from that tag in a clean checkout, the gates run, and publication happens only after they pass;
  a failing gate deletes the tag before publication and the tag becomes immutable once the artifact is published.
  Sign, stage, and inspect the artifact before publishing, link the
  release-note document owned by documentation to the artifact digest, never move the tag after publishing, and never
  rebuild a published version.
- Define the yank and deprecation path: yank or deprecate only for a security defect, an uninstallable artifact, or a
  legal problem; publish the reason, keep a yanked version resolvable for already-pinned users while blocking new
  installs where the registry supports it, name the replacement and its removal date for deprecations, and never delete
  a published version. A deleted version destroys reproducibility for everyone who pinned it.
- Apply the same discipline to container images when the project ships one: a registry namespace owned by the
  organization, an immutable digest plus a version tag, no `latest` reference in production, multi-architecture builds
  from CI with source and revision labels, a scheduled base-image rebuild, a vulnerability scan before publish, and a
  signature checked by the deployment platform. The security and compliance skill owns the SBOM content; this
  dimension requires the pipeline to produce it and the release record to reference it.

| Good | Bad | Why |
|---|---|---|
| The package name is reserved before the first release. | The first release picks a name that is already taken. | Publishing blocks at the worst possible moment. |
| Publish rights belong to an organization team. | One person's account holds the only publish token. | The package cannot be released while that person is away. |
| The manifest carries SPDX license, repository, runtime range, and files. | Manifest fields are guessed or left empty. | Registries and scanners cannot classify or verify the package. |
| The version has one source and is copied by the build. | The version is bumped in three files. | A release ships inconsistent versions. |
| The primary registry is declared and promotion is recorded. | Artifacts are uploaded to several registries by hand. | One channel can serve a different build. |
| The artifact is signed and carries provenance. | Checksums appear only on the release page. | Consumers cannot verify what they install. |
| The install test starts from an empty environment and the registry. | The install is checked in the project checkout. | Undeclared dependencies and local paths go unnoticed. |
| Publication happens only after every gate passes; a failing gate deletes the tag. | The artifact is published before the gates finish. | A failed gate must not leave a published version behind. |
| The tag is created on the approved release commit and the artifact is built from it. | The tag is moved after publishing. | The tag no longer identifies the shipped tree. |
| The release-note document, owned by documentation, links the artifact digest. | The release body is a generated commit list. | Users need documented upgrade actions, not a commit list. |
| The smoke test covers the declared runtime and OS matrix. | One runtime on one OS is tested. | Installation fails on a supported platform. |
| A yanked version states the reason and the replacement. | The broken version is deleted from the registry. | Pinned users cannot reproduce a build. |
| A deprecation names a successor and a removal date. | The deprecation note has no replacement. | Users cannot plan the upgrade. |
| Production containers pin an immutable digest. | Production references the `latest` tag. | A new push silently changes what runs. |
| Multi-architecture images are built in CI with source labels. | The image is hand-built on a laptop. | The image is not reproducible and has no provenance. |
| The base image is rebuilt and scanned on a schedule. | An old base image is kept for convenience. | Known vulnerabilities ship with every new image. |
| Internal packages are promoted from staging after the install test. | The internal build is installed from the development registry. | Unverified artifacts reach production. |
