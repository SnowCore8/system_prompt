---
name: security-compliance-conventions
description: Defines, reviews, and repairs security, credential, license, privacy, and vulnerability-disclosure practice for any project, covering threat models, secret storage and rotation, dependency supply chains, SBOMs and attribution notices, PII inventories, and coordinated disclosure. Use when starting a feature or project, reviewing a change for security or privacy impact, adding a dependency, handling a credential, preparing a release, or responding to a reported vulnerability.
argument-hint: '[path or scope]'
---

# Security and Compliance Conventions

Security and compliance failures are asymmetric. A missed naming rule costs a review comment and a later rename; a
credential committed to history, a copyleft library shipped in a binary, or personal data sent to an unapproved
processor cannot be repaired by later work, because the disclosure already happened. This skill defines the
project-side rules for secure development, credentials and secrets, licensing, privacy, and vulnerability
disclosure, together with the evidence each rule requires. It serves the engineer designing a feature, the reviewer
judging a change, and the maintainer preparing a release or answering a report. It sets project policy only: agent
conduct is governed by the host and user instruction layer and is not restated here. Where a question turns on a
statute or a contract, counsel decides; nothing in this skill is legal advice.

## Scope and Precedence

Apply the first rule that fits, and do not mix standards inside one scope:

1. Mandatory law, regulation, binding contract, license terms, and the host or user instruction layer. A statutory
   deadline, a data processing agreement, a license obligation, or an agent-level conduct rule is not optional.
2. Existing project policy: `SECURITY.md`, `LICENSE`, the data inventory, approved architecture decisions, and any
   stricter local rule. Read them before inventing a rule.
3. This standard's defaults, when the two levels above are silent.
4. Personal preference, which never overrides the three levels above.

- Agent behavior versus project policy. What an agent may place in its output, and when it must obtain consent for
  an irreversible action, is set by the host and user instruction layer; those rules outrank this skill and are not
  restated here. This skill sets project policy: what data may be stored, shipped, collected, or disclosed, and who
  approves each of those acts.
- Comment and documentation rules forbid secret values in comments, examples, and documents. This skill owns where
  the real value is stored, how it is scanned, rotated, and disclosed; apply both, and trace an exposed value to its
  storage entry instead of only deleting the visible copy.
- Release and incident-response roles own pipeline execution and incident command. This skill owns the security gates
  those pipelines run, the severity and remediation policy behind each gate, and the disclosure process before an
  incident becomes public.
- API and data roles own retention mechanics, deletion jobs, and migrations. This skill owns PII classification,
  privacy review, and the legal obligations the team adopts; retention policy is set here and implemented there.
- Repository governance owns only the presence, location, and basic metadata (owner, review date) of `SECURITY.md`;
  the documentation conventions own its page structure and prose. This skill owns the required content, the reporting
  and response commitments, and the advisory process published there.
- Testing and quality roles own where scans run as quality gates. This skill owns the severity policy, the
  remediation deadlines, and the decision to fix, accept, or block on a finding.
- Third-party code is report-only: vendored, generated, and externally maintained code is inventoried and scanned,
  never hand-edited. Report the issue upstream, or carry a documented patch in a separate fork and record it.
- Reporting outranks convenience. A failing scan, an unlicensed dependency, a privacy defect, or a suspected leak is
  reported even when it blocks a release; convenience never justifies silence, and a report is not a fix.
- When two rules conflict, state the conflict, follow the higher level, and record the decision with its owner so
  the next change follows it.

## Process

1. Classify the change and the data it touches: assets, entry points, trust boundaries, credential paths,
   dependencies, personal data, third-party code, and distribution targets. Work from the diff or the design, not
   from a generic checklist.
2. Read the obligations already in force: the project's `SECURITY.md` content, `LICENSE`, data inventory, and
   accepted-risk register. Note which obligation this change adds, changes, or removes.
3. Build or update a lightweight threat model for each new or changed trust boundary: assets, abuse cases, existing
   controls, residual risk, and owner. Record it with the design or in `docs/security/`.
4. Apply controls in order: secure defaults, server-side validation with context-appropriate encoding,
   authentication separated from authorization, scoped runtime credentials, dependency and license gates. Record
   anything deferred as security debt with an owner and a review date.
5. Route required reviews before merge: security review for a trigger, privacy review for personal data or a new
   processor, license review for a dependency or distribution change, and counsel for a legal question. Do not merge
   while a required review is open.
6. Produce the release evidence: regenerated SBOM, notice file, license inventory, scan results, and residual risk.
   Attach it to the release, not to a chat thread or a passing comment.
7. Verify and hand off: rerun the gates, confirm remediation deadlines and accepted-risk expiry dates, update
   `SECURITY.md` content and advisories, and state what remains open with its owner.

## Core Rules

- **Model every trust boundary, proportionally.** A feature that takes untrusted input, crosses a service, or grants
  access gets a lightweight model of assets, entry points, abuse cases, controls, and residual risk; a feature that
  crosses no boundary records a one-line "no boundary crossed" note. The effort follows the risk, not a ceremony.
- **Default to deny and fail closed.** New permissions are absent, new fields are private, new flags are off, and
  new endpoints require authentication until opened deliberately. A control that fails open when its dependency is
  unavailable is a defect, even when every scan is clean.
- **Validate on the server and encode for the context.** Allowlist type, length, range, and format at each boundary;
  canonicalize before checking; parameterize queries; encode HTML, attributes, JavaScript, URLs, and shell
  arguments separately. Client-side validation is user experience, never a control.
- **Authenticate at the edge and authorize at the resource.** Every request gets a server-side permission decision
  for the specific object and tenant, independent of what the interface hides. Log denials on privileged actions,
  and require a stronger factor for administration and destructive operations.
- **Keep secret values out of the repository.** Commit only a reference to a secret: environment injection, a
  secret manager, or a platform secret store. `.env.example` carries variable names and non-functional fake values,
  and secret scanning covers commits, pull requests, history, and build logs.
- **Scope a credential to one job and give it an owner.** Issue one credential per service, job, and environment,
  limited to the resources and actions it needs. Record who owns it, what it can reach, and when it rotates; a shared
  administrator credential is a permanent finding, not a convenience.
- **Treat dependencies as code you ship.** Review a new dependency for maintenance, known vulnerabilities, license,
  transitive size, and install scripts. Pin it in a lockfile, fetch it from a verified registry, and ship the SBOM
  that lists it; an unused dependency is removed, not disabled.
- **Pass the license gate before the dependency lands.** Check the SPDX identifier and the transitive licenses
  against the allowed, review, and forbidden categories; an unidentified license is forbidden until a human
  identifies it. Every exception is written, owned, and dated.
- **Generate the SBOM and notice file for every release.** Build both from the dependency graph used for the
  artifact, include transitive components and required attribution, attach them to the release, and keep them for
  the support lifetime plus the retention period the team adopted.
- **Classify personal data before collecting it.** Each data element gets a class, a purpose, a system, a retention
  period, a recipient list, and a region in the data inventory before production traffic reaches it; collection
  hidden in logs or analytics is still collection.
- **Minimize personal data and bound its life.** No field without a documented purpose, no PII in logs, URLs, or
  event names, no production data in development or test. Pseudonymize where identity is not needed, and pair every
  retention period with the deletion path that enforces it.
- **Rate findings with a policy, not a scanner.** Assign severity from exploitability, exposure, and data
  sensitivity; give every finding an owner and a remediation deadline; record risk acceptance with an expiry and a
  compensating control. A scanner report without an owner is not a decision.
- **Disclose on a committed timeline.** Publish the reporting channel and scope, acknowledge within 2 business days
  and triage within 5, fix critical issues within 7 calendar days, and publish an advisory with a CVE identifier
  when the fix ships, or with the CVE request status if assignment is delayed. A silent fix leaves users unable to
  assess their exposure.
- **Report and never edit around the gate.** A suspected leak, an unknown license, or a privacy defect stops the
  affected step and is reported with the evidence; do not rewrite history, delete logs, or disable the gate as a
  workaround. Third-party code is reported upstream, not patched in place.

## Risk Control Matrix

Each row pairs an asset or obligation with the failure it faces, the minimum control, and the evidence a review
checks.

| Asset or obligation | Threat or failure | Minimum control | Evidence |
|---|---|---|---|
| Source repository | A credential or personal data enters commit history and cannot be withdrawn | Secret scanning on push and in CI; `.gitignore` covers local config and data dumps; every diff reviewed for new files | Scan result on the pull request; rotation record if a hit is confirmed |
| Runtime credentials | A leaked long-lived key grants broad access to production | Secret manager injection, per-service scoped credentials, scheduled rotation with an owner | Credential inventory row with scope, owner, and next rotation date |
| Identities and permissions | A missing object-level check lets one tenant read another tenant's data | Server-side authorization at the resource, default deny, tenant filter tested per endpoint | Authorization test for the endpoint; review approval in the change |
| Dependencies and build | A malicious, typosquatted, or compromised package runs in the build | Reviewed dependency, pinned lockfile, verified registry, disabled install scripts, provenance check | Dependency review entry, lockfile diff, build attestation |
| Inbound licenses | Copyleft or unlicensed code is distributed inside the product | License gate on direct and transitive components, written exceptions only | License report per release; signed exception with owner and expiry |
| Outbound license and attribution | The product ships without required notices or with incompatible terms | `LICENSE` at the distribution root, generated notice file, inbound and outbound compatibility check | Release archive with license and notice files; SBOM |
| Personal data and telemetry | Unbounded collection creates regulatory and trust exposure | Purpose review before collection, event-schema allowlist, minimization, consent gate | Data inventory row and approved event schema |
| Data subject requests | A request is missed because data sits in logs, backups, or a processor | Published runbook, complete search map, processor deletion clauses | Request log with dates, systems searched, and completion |
| Vulnerability reports | A report is lost, or disclosure happens before users can patch | Monitored channel, acknowledgement and triage deadlines, embargo, advisory with a CVE identifier | Report timestamps, advisory, CVE identifier, credited reporter |
| Release pipeline | An unreviewed or unsigned artifact reaches users | Required review gate, signed artifact and provenance, least-privilege deploy identity | Pipeline run showing the gate and signature verification |
| Third-party code | A local patch is lost at the next vendor update, or an upstream flaw ships | Vendor boundary with recorded license and version; upstream report; documented fork patch | Vendor inventory entry; upstream issue reference; fork patch file |

## Dimension Index

Each dimension has the detailed controls, failure modes, and examples in `references/dimensions.md`.

| Dimension | First rule |
|---|---|
| 1. Secure development | Model each trust boundary, then default to deny and validate at every boundary. |
| 2. Credentials and secrets | Inject secret values at runtime, never commit them, and scope and rotate each credential. |
| 3. Licensing and compliance | Pass the license gate before code lands, then ship the SBOM and notices. |
| 4. Privacy | Classify personal data and record its purpose, flow, and retention before collecting it. |
| 5. Vulnerability disclosure | Publish the channel, meet the timelines, and disclose with an advisory and CVE. |

## Anti-Patterns

| Anti-pattern | Why it fails | Fix |
|---|---|---|
| A clean scan with no owner | A scanner proves only that its rules did not match; findings without an owner and date never close | Assign severity, owner, and deadline; register accepted risk |
| "Rotate the key later" | A leaked long-lived credential keeps working while the task is deferred | Revoke or rotate first, within 24 hours of suspicion, then clean up |
| One shared administrator credential | A single leak grants every action and leaves no attribution | One scoped credential per service, job, and environment |
| A committed `.env` file, "temporarily" | History keeps the value after the file is removed | Gitignore the real file, commit names only, scan history |
| Authorization enforced only in the interface | A direct API call bypasses the hidden button | Server-side object-level check on every request |
| Home-grown cryptography or session handling | Subtle flaws are invisible to review and tests | Use framework and approved libraries; require crypto review |
| "It is public on a repository host, so it is free" | A repository with no license is all rights reserved | License gate: identify the SPDX term or reject the package |
| A hand-maintained SBOM | It drifts at the first dependency change and hides new components | Generate it in CI from the lockfile and attach it to the release |
| "Add an analytics field, review it later" | Field-level collection escapes purpose limits and review | Event-schema review and inventory row before deployment |
| "Internal tool, so no threat model" | Internal tools become reachable, and administrative tools hold the highest privilege | Same triggers and defaults; model an assumed-compromised network |
| Critical fix in the next scheduled release | The exploitation window stays open for a release cycle | Out-of-band patch within 7 calendar days |
| Silent security fix | Users cannot assess exposure, and researchers duplicate the report | Advisory, CVE identifier, changelog entry, credit |
| Publishing before the fix ships | Users are exploited while the report is public | Hold the embargo, coordinate the date, publish with the fix |
| Patching vendored code in place | The patch disappears at the next vendor update | Report upstream, or maintain a documented fork patch |
| Accepting risk in a chat thread | No owner, no expiry, and no record for the next reviewer | Risk register entry with owner, expiry, and compensating control |

## Review Checklist

- [ ] Every new or changed trust boundary has a threat model or a one-line "none crossed" note.
- [ ] Assets, entry points, and abuse cases are named, with controls and residual risk.
- [ ] Server-side validation covers type, length, range, and format for every new input.
- [ ] Output is encoded for its context; queries are parameterized and shell calls avoid interpolation.
- [ ] Authorization is enforced per resource and tenant, not only in the interface.
- [ ] Secure defaults are on: deny, private fields, disabled flags, no debug in production.
- [ ] No secret value, key, token, `.env` file, or credential-bearing connection string is in the diff.
- [ ] Every changed credential has a scope, an owner, a rotation interval, and a next rotation date.
- [ ] CI secrets are masked, scoped per environment, and withheld from untrusted fork builds.
- [ ] Secret scanning covers commits, pull requests, history, and build logs.
- [ ] Every new dependency is reviewed, pinned, and carries an allowed license or a recorded exception.
- [ ] The SBOM and notice file are regenerated and attached to the release.
- [ ] Personal data fields have inventory entries with purpose, retention, recipients, and region.
- [ ] No PII appears in logs, URLs, analytics events, test fixtures, or screenshots.
- [ ] Processor, cross-border, or consent changes have privacy review and counsel where required.
- [ ] Findings have severity, owner, and deadline; accepted risks have an expiry.
- [ ] Vulnerability reports are acknowledged and triaged within the committed timelines.
- [ ] Third-party code is reported upstream rather than hand-edited.
- [ ] The `SECURITY.md` content, advisory, and release notes match the shipped state.

## Examples

<example>
Adding a file-upload endpoint: assets are user files and storage credentials; the trust boundary is browser to API.
Abuse cases are oversized files, executable content, decompression bombs, and path traversal. Controls are a
content-type allowlist, a size cap, image re-encoding, storage outside the web root, and a scan before serving.
Residual risk and its owner go in the threat-model note.
</example>

<example>
A dependency carries LGPL-3.0, so the license gate moves it to review. The review records dynamic linking, no source
modification, the notice obligation, and the owner, and counsel approves the use before merge. If an existing MIT
alternative covers the need, prefer it and drop the review.
</example>

<example>
Analytics asks for a `user_email` property on a checkout event. Privacy review rejects it: the event needs only the
internal account identifier and the order value. The event schema is updated, the purpose is recorded, and the
property never reaches production.
</example>

<example>
A researcher reports remote code execution on a Friday. Acknowledge within 2 business days, triage within 5, and
rate it critical. The fix ships within 7 calendar days, the CVE identifier is assigned, and the advisory publishes
with the release, the affected and fixed versions, and the reporter's credit.
</example>

<example>
A build log prints a deployment token. Revoke and rotate the token first, then audit its use, scrub the log, remove
the value from any artifact or cache, and record the incident. Do not rewrite history as the first step; the token
stays valid either way.
</example>

## References

Read [references/dimensions.md](references/dimensions.md) for the detailed rule set behind each dimension, one
section per dimension with examples and a Good/Bad/Why table. Read
[references/checklists.md](references/checklists.md) for the worksheets, registers, timelines, and runbooks used to
execute a review or a disclosure. Read both before a project's first security or privacy review; during routine
work, read only the dimension and checklist that match the change.
