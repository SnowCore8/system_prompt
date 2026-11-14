# Security and Compliance Checklists

Use these worksheets and runbooks with `SKILL.md` and `references/dimensions.md`. Each section is operational: fill
it in during design or review, attach the completed record to the change or release, and keep it with the project.
Replace example values with project values, and never record a real secret or real personal data in a completed
checklist; use fake values such as `security@example.test.invalid` and `example.test.invalid`.

## 1. Lightweight Threat-Model Worksheet

Fill one row per asset and trust boundary. The result is a one-page note, not a catalogue; time-box the exercise to
30-60 minutes and record residual risk instead of pretending it is zero.

| Field | Prompt | Example |
|---|---|---|
| Feature and owner | What is being built, and who owns the model? | Order export, billing team |
| Assets | What does the feature protect or expose, and what is each worth? | Customer addresses, export files, API token |
| Entry points | How does untrusted input reach the feature? | `POST /v1/exports`, webhook callback, file upload |
| Trust boundaries | Where does data or control pass between components with different trust? | Browser to API, API to object storage, worker to mail provider |
| Abuse cases | How would an attacker misuse the feature, and to what effect? | Read another tenant's export, cause a cost spike, inject a formula into a CSV |
| Existing controls | What already blocks each abuse case? | Tenant filter in the query, per-tenant rate limit, CSV formula escaping |
| Data classes | Which data classes does the feature store or transmit, and which is the highest? | Confidential addresses, internal metrics |
| Dependencies and processors | Which third-party services, packages, or processors participate? | Object storage, CSV library, mail provider |
| Gaps and residual risk | What remains, and who accepts it? | No per-object audit log; accepted by the billing lead until Q3 |
| Decision | Ship, ship with conditions, or block; what condition applies? | Ship with the audit log before public launch |
| Review date | When is the model revisited? | At the next trust-boundary change or in 6 months |

A model is complete when every asset and abuse case names a control, every gap has an owner and a date, and the
decision is recorded with the feature design. A model that lists generic risks without naming this feature's data
and entry points is a template, not a review.

## 2. Security Review Trigger Checklist

Route the change to the security reviewer when any line is true. When no line is true, record that this list was
checked in the change description.

- [ ] Authentication, session handling, password reset, or token issuance changes.
- [ ] The authorization model, roles, scopes, or tenant isolation changes.
- [ ] Cryptography, key management, hashing, or random-number use changes.
- [ ] A new external interface, webhook, public endpoint, or callback exists.
- [ ] A new processor, SDK, or hosted service receives project data.
- [ ] Payment, pricing, billing, or financial calculation logic changes.
- [ ] File upload, file parsing, archive extraction, or user-controlled URL fetching is added.
- [ ] Personal-data fields, analytics events, or consent behavior change.
- [ ] Administrative tooling, impersonation, or break-glass access is added or changed.
- [ ] Infrastructure identity, network rules, IAM policy, or secrets management changes.
- [ ] Deserialization, template rendering, dynamic code execution, or shell invocation changes.
- [ ] A new native dependency, install script, or build-time executable enters the supply chain.
- [ ] Distribution, licensing, notice, or export classification changes.
- [ ] An open security finding or disclosed vulnerability affects the change.
- [ ] The change touches production data, a backup restore path, or a deletion job.
- [ ] A new data export, bulk download, or report exposes records beyond their current audience.
- [ ] An upgrade changes native code, install behavior, or the effective license of a dependency.

## 3. Secret Lifecycle Register

Record every secret in one register and review it quarterly. The owner is a person or a team, never a ticket; a
secret without a next rotation date is overdue by default.

| Type | Storage | Rotation | Owner |
|---|---|---|---|
| CI deploy token | CI secret store, environment-scoped | 90 days, and immediately after exposure | Release owner |
| Service API key | Secret manager, injected at runtime | 180 days, with two-key overlap | Service owner |
| Database credential | Secret manager or dynamic database credentials | 90 days | Data owner |
| Signing key | KMS or HSM with key versioning | 365 days, with rollover overlap | Release owner |
| Encryption key | KMS with rotation enabled | Annual, with a re-encryption plan for old data | Security owner |
| OAuth client secret | Secret manager | 180 days | Identity owner |
| Developer access token | Identity provider, short-lived | 30 days maximum, revoked on role change | Identity team |
| Third-party integration key | Secret manager | 180 days | Integration owner |
| Webhook signing secret | Secret manager, two active values during rollover | 180 days | Endpoint owner |
| Local development secret | Git-ignored local file or developer vault | 90 days, never shared | Each developer |

- Retire a credential only after traffic on the new value is verified and no audit log shows the old value in use.
- A secret that is not in the register has no rotation date; register it or remove it.
- Rotate any credential exposed in a log, artifact, screenshot, or ticket, even when the exposure looks harmless.
- Development and test credentials never carry production scopes or production data.

## 4. Dependency and Supply-Chain Control Checklist

Apply this list to every new dependency and to every upgrade that changes a maintained version; attach the answers
to the dependency review.

- [ ] The package name and source are verified against the intended project, not a lookalike.
- [ ] Maintainers and release history show active, credible ownership.
- [ ] The package is fetched from the configured registry and pinned in the lockfile with a hash.
- [ ] Direct and transitive dependency counts are acceptable for the value provided.
- [ ] No install script, post-install hook, or build-time download runs unless reviewed and approved.
- [ ] The license passes the gate, including transitive components.
- [ ] No known critical or high vulnerability lacks a documented mitigation.
- [ ] The version is supported upstream and not end-of-life.
- [ ] Native code, binaries, and prebuilt artifacts are identified and scanned.
- [ ] The build produces provenance or a signed artifact where the ecosystem supports it.
- [ ] Automated update pull requests are enabled and merged after tests.
- [ ] Container base images are minimal, pinned by digest, and scanned.
- [ ] Unused dependencies are removed rather than left installed.
- [ ] A private registry allowlist blocks packages outside the approved set.
- [ ] The SBOM is regenerated after the change and diffed against the previous release.

## 5. License Policy Categories

Record the category and the action in the license inventory. A category is not a legal opinion; counsel approves an
exception and the owner records it.

| Category | Examples | Action |
|---|---|---|
| Allowed | MIT, BSD-2-Clause, BSD-3-Clause, ISC, 0BSD, Apache-2.0 | Use it; preserve the license text, copyright lines, and any upstream `NOTICE`. |
| Review | MPL-2.0, LGPL-2.1, LGPL-3.0, EPL-2.0, CDDL-1.0, public-domain dedications with unclear patent terms | Route to the license owner and counsel; record linking, modification, and notice facts before approval. |
| Forbidden | GPL-2.0 and GPL-3.0 in distributed code, AGPL-3.0 also for network-served code, SSPL, BUSL-1.1, Commons Clause, non-commercial-only terms, no license | Do not add it; replace the dependency or obtain a written counsel-approved exception with an owner and expiry. |
| Unknown | Custom terms, copied source with no header, a version-pinned fork | Treat it as forbidden until a human identifies the terms and records the decision. |

- Record the license actually chosen for a dual-licensed package, not both licenses.
- Keep the upstream license file with vendored code and record every local patch.
- Check documentation and asset licenses separately from code licenses.
- Treat a license change in an existing dependency as a new dependency review.
- Share-alike content such as CC BY-SA is not merged into code without review; the obligation can reach the
  combined work.
- Generated clients and schemas from a third-party specification keep the upstream license and notice.

## 6. SBOM and Notice Checklist

Generate both artifacts from the same resolved dependency graph; a hand-maintained list is stale before the release
notes are written.

- [ ] The SBOM is generated in CI from the dependency graph used to build the artifact.
- [ ] Direct and transitive components include versions, package identifiers, licenses, and hashes.
- [ ] Container base images and operating-system packages are included.
- [ ] The SBOM format and specification version are recorded (SPDX or CycloneDX).
- [ ] The SBOM is attached to the release and stored with the artifact, not only in CI logs.
- [ ] The SBOM is diffed against the previous release and new components are reviewed.
- [ ] The notice file lists every component whose license requires attribution.
- [ ] Full license texts are included where required, and upstream `NOTICE` content is preserved.
- [ ] The notice file ships at the distribution root and inside packaged artifacts.
- [ ] The retention period is recorded and the SBOM is retrievable for every supported release.
- [ ] The SBOM matches the artifact: spot-check three components against the installed versions.
- [ ] The SBOM generator name and version are recorded with the release.
- [ ] Component hashes are spot-checked against the lockfile entries that built the artifact.
- [ ] Exceptions and review-category licenses link to their recorded approval.

## 7. PII Inventory and Privacy Review Worksheet

Fill one row per data element and one pass per flow. If a field cannot complete the row, it is not ready for
production.

| Field | Prompt | Example |
|---|---|---|
| Data element | What is collected, in what form, and at what granularity? | Customer email address, exact string |
| Subject | Whose data is it, and can it include minors or employees? | End customers of business accounts |
| Source | Where does it come from, and is the source authorized? | Checkout form, support import |
| Purpose | Which named purpose requires it, and who owns that purpose? | Order receipt and support lookup, commerce team |
| Systems and flows | Where is it stored, and which systems does it traverse? | Orders database, email processor, support tool |
| Processors and region | Which vendors receive it, under which agreement and in which region? | Mail provider in the approved region |
| Retention and deletion | How long is it kept, and what deletes it? | 24 months, nightly deletion job plus processor deletion |
| Access | Which roles can read it, and is access logged? | Support read-only, audited |
| Classification | Public, internal, confidential, or restricted? | Confidential |
| Consent or lawful basis | What is the recorded basis, and who confirmed it? | Contract performance, confirmed by counsel |
| Retention owner | Who runs the deletion, and where is the evidence it ran? | Data platform role, monthly job report |

Review the completed inventory against this list before the change merges:

- [ ] The purpose is specific, and the data is not reused for an unrecorded purpose.
- [ ] Collection is minimized: no field lacks a purpose, and no direct identifier can be replaced.
- [ ] Consent, where required, is opt-in, versioned, and gated before collection starts.
- [ ] The inventory row, flow map, and retention period exist before production traffic.
- [ ] Processors and transfers have an agreement, a region, and a deletion commitment.
- [ ] No personal data appears in logs, analytics properties, URLs, test fixtures, or screenshots.
- [ ] A data subject request can be satisfied from the inventory, including processor copies.

## 8. Data Subject Request Runbook

Use the inventory as the search map. The adopted response target is 30 days or the statutory deadline counsel
confirms, whichever is shorter; record the dates even when the request is refused.

1. Log the request: date received, channel, requester, right requested, and the deadline.
2. Verify identity with a method proportionate to the data; do not collect extra data to verify.
3. Classify the request: access, correction, deletion, portability, objection, or restriction.
4. Search every system in the inventory: primary stores, warehouses, logs, backups, and processors. Record each
   system searched and each one excluded, with the reason.
5. Apply legal holds and third-party rights; counsel decides when a record must be kept or withheld.
6. Fulfil the request: export in the requested format, correct the record, or delete on the documented schedule.
   Where deletion is refused, give the reason the law or a hold requires.
7. Notify processors and confirm completion; record what was sent and when.
8. Respond to the requester within the deadline and record the outcome, including any refusal and its reason.

## 9. Vulnerability Disclosure Runbook and Timeline

These are the commitments published in the `SECURITY.md` content. Put slack in the calendar, not in the table.

| Stage | Deadline | Action | Owner |
|---|---|---|---|
| Receipt | T+0 | Log the report and reply with the channel and the timeline. | Security contact |
| Acknowledgement | 2 business days | Confirm receipt and name the person handling it. | Security contact |
| Triage | 5 business days | Reproduce, scope versions, assign severity and owner, agree the next milestone. | Security reviewer |
| Update | Every 10 business days | Send status, blockers, and any revised date. | Report owner |
| Critical fix | 7 calendar days | Ship an out-of-band patch and backport to supported versions. | Engineering owner |
| High fix | 30 calendar days | Ship in the next patch release. | Engineering owner |
| Medium fix | 90 calendar days | Schedule within the release train. | Engineering owner |
| Low fix | 180 calendar days | Bundle with other work. | Engineering owner |
| Advisory | 2 business days after the fixed release | Publish the advisory, CVE identifier, affected and fixed versions, workaround, and credit. | Security owner |
| Embargo end | Report date plus 90 calendar days | Publish, or extend only with the reporter's agreement and a recorded reason. | Security owner |

- A duplicate or already-fixed report gets a reply and a reference to the advisory, with credit where it helped.
- An out-of-scope report gets a reply explaining why, with the scope entry that applies.
- A dependency vulnerability follows the maintainer's advisory, and the project publishes its own notice when its
  users are affected.
- An actively exploited issue shortens the embargo to the time needed to ship the fix and briefs the incident owner.
- A report against an unsupported version still gets a reply; the team decides whether to fix, document a
  workaround, or advise an upgrade.
- The advisory is linked from the `SECURITY.md` content and from the release notes for the fixed version.
