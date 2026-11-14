# Security and Compliance Dimensions

Use this file with `SKILL.md`. Each section covers one dimension of the standard: the controls a project adopts, the
failure each control prevents, and the evidence a reviewer expects. Read the section that matches the change; read
all five before a project's first security review, when writing the `SECURITY.md` content, or when building the data
inventory. The rules are defaults a team adopts, not legal conclusions: when a decision turns on a statute, a
contract, or a jurisdiction, route the question to counsel and record the answer with its owner.

## 1. Secure Development

Security is a property of the design before it is a property of the scan. Apply this dimension when a feature
crosses a trust boundary, when a new interface, permission, or data class exists, and when a dependency enters the
build; the output is a threat-model note, controls in code, and a review record.

- **Threat-model each feature lightly.** Spend 30-60 minutes on a one-page note: assets and their value, entry
  points, trust boundaries, abuse cases, existing controls, residual risk, and owner. A feature that crosses no
  boundary records one line saying so. Update the note when an entry point, data class, or trust boundary changes; a
  model from the first release is evidence of history, not of the current design.
- **Choose secure defaults.** New permissions are absent, new fields are private, new flags are off, and new
  endpoints require authentication until opened deliberately. Set secure cookie flags, require TLS, restrict CORS to
  named origins, enable rate limits, and keep debug output and verbose errors off in production. An operator who
  forgets to configure the system must get the safe behavior, not the exposed one.
- **Validate at every boundary.** Check allowlisted type, length, range, format, and encoding on the server;
  canonicalize before validating; cap body and upload size; validate file type by content rather than extension;
  reject unknown fields on sensitive endpoints. Where the server makes an outbound request from user input, use an
  allowlist to prevent server-side request forgery. Client validation is a convenience and is bypassed by editing
  the request.
- **Encode output for its context.** Encode HTML text, attributes, JavaScript, CSS, URLs, and shell arguments
  separately; rely on framework auto-escaping rather than manual escaping; use parameterized queries or an ORM for
  SQL; never pass user input to `eval`, a dynamic import, or a shell string. The same value can be safe in a text
  node and unsafe in an attribute or a URL, so the encoding decision belongs to the sink, not the source.
- **Separate authentication from authorization.** Authentication establishes who is calling; authorization decides
  which object and action the caller may touch. Enforce the decision on the server for every request, including
  direct API calls and internal service calls; filter by tenant in the query; log denials; require a stronger factor
  for administration, permission changes, and destructive actions. Hiding a control in the interface is not an
  authorization boundary.
- **Control the dependency and supply chain.** Before adding a dependency, check maintenance activity, known
  vulnerabilities, license, transitive count, native code, and install scripts. Pin it in a lockfile, fetch it from a
  verified registry, and disable install scripts unless reviewed. Generate updates automatically and merge them only
  after tests; remove unused dependencies; rebuild from minimal container images; verify signatures or provenance
  where the ecosystem supports them. A package name one character off is a working attack.
- **Route security review triggers before merge.** Require review for changes to authentication or permissions,
  cryptography, payments, file handling, new external interfaces, administrative tooling, personal-data fields,
  processors, infrastructure identity or network rules, deserialization, secret handling, and new native
  dependencies. Record the reviewer and the decision in the change; a review that happens after deployment is an
  incident review, not a gate.
- **Track security debt with an expiry.** Every accepted risk gets a register entry: description, impact, owner,
  compensating control, review date, and tracking identifier. Re-review the register at least quarterly and on any
  ownership change; an exception that expires without review becomes an unreviewed risk. Do not accept a risk in a
  chat thread where the next reviewer cannot find it.

| Good | Bad | Why |
|---|---|---|
| Default-deny permission with a per-resource check | Button hidden in the interface | Direct API calls skip presentation logic. |
| Allowlist validation with size caps | Client-side check only | The client is attacker-controlled. |
| Parameterized query | Manual quote escaping | Hand-escaping misses encodings and contexts. |
| Per-service scoped credential | Shared administrator token | One leak escalates everywhere and attribution is lost. |
| Pinned lockfile with a review gate | Open version range resolved at install | The build can select an unreviewed package. |
| Threat model updated with the boundary | Model written once at kickoff | The design moved and the model did not. |
| Risk register entry with an expiry | Risk accepted in a chat thread | No owner, no deadline, no record. |

Defaults a reviewer checks before reading code:

| Control | Safe default | Failure mode when left open |
|---|---|---|
| Access decision | Deny unless a permission grants the action | A forgotten check becomes an open endpoint. |
| New data field | Private, excluded from APIs and logs | A field added for one feature is exposed everywhere. |
| Feature flag | Off until intentionally enabled | Unfinished code reaches all users. |
| Error response | Generic message plus a correlation identifier | Stack traces, queries, and internal hosts leak. |
| Session cookie | `HttpOnly`, `Secure`, `SameSite=Lax` or stricter | Script access and cross-site requests are enabled. |
| Administrative route | Authenticated, authorized, rate limited, and audited | An internal tool becomes the easiest way in. |
| Resource limits | Request size, time, and rate capped | One client exhausts the service for everyone. |

## 2. Credentials and Secrets

A secret is the smallest, highest-value artifact a project holds: one readable value can grant every action its
scope allows. This dimension covers the whole lifecycle, from classification and storage to rotation and leak
response, and it applies to application credentials, CI tokens, signing keys, and local development values.

- **Tell a secret from a public identifier.** A secret is a password, private key, API secret, session token, webhook
  signing value, or a connection string that embeds credentials. A public key, publishable key, OAuth client
  identifier, or application identifier is not automatically public: confirm that exposure is safe, then restrict it
  by origin, scope, or rate limit. A publishable key with an unrestricted scope is a secret in practice.
- **Store secrets outside the repository.** Keep values in a secret manager or platform secret store and inject them
  at runtime through environment variables, mounted files, or a runtime API. Code holds a name, never a value;
  `.env.example` holds variable names and non-functional fake values. Kubernetes `Secret` objects are base64
  encoding, not encryption, so enable encryption at rest or use an external store for production values.
- **Apply least privilege and scoped tokens.** Issue one credential per service, job, and environment, with only the
  resources and actions it needs; separate read from write and test from production. Use short-lived tokens with
  audience restrictions where the platform supports them, and route human access through single sign-on with a
  logged break-glass path. A credential shared by several services cannot be rotated, attributed, or scoped safely.
- **Set a rotation cadence and one owner.** Every credential has an owner, a rotation interval, and a next rotation
  date in the inventory; rotate on schedule, on role or staff change, and on any suspicion of exposure. Keep two
  valid keys during an overlap window, deploy the new value, verify traffic, then retire the old one. Rotation that
  deletes the old key before clients reload breaks production and teaches teams to skip rotation.
- **Control CI secret exposure.** Inject CI secrets from the CI secret store at runtime, mask them in logs, and
  withhold them from untrusted fork builds; scope deploy credentials to one environment and one action. Prefer
  short-lived identity federation over a static cloud key; pin third-party actions to reviewed versions; keep secrets
  out of artifacts, caches, and test reports. Treat any value printed by a tool as exposed and rotate it.
- **Keep local development secrets local.** Keep development credentials separate from production, scoped to
  development data, and stored in a git-ignored file or a local secret store; never share a personal token as a team
  credential, and never point development at production data. A `.env.example` that documents every variable with
  fake values lets a contributor start without ever seeing a real secret.
- **Detect and respond to leaks in the right order.** Scan commits, pull requests, history, build logs, and release
  artifacts for secret patterns. On a hit, revoke or rotate first, within 24 hours and immediately for a
  production-critical credential; then audit its use, preserve the evidence, remove the value from artifacts and
  logs, and record the incident. Deleting the commit while the key remains valid removes evidence and leaves the
  exposure open.
- **Keep a secret inventory.** Register each secret with its purpose, owner, storage location, scope, rotation
  interval, and dependent services; review the register quarterly. A value that is not in the register has no owner
  and no rotation date, so it is registered or retired, not left running.

| Good | Bad | Why |
|---|---|---|
| Runtime injection from a secret manager | Value in a committed configuration file | Repository readers and history retain it. |
| Scoped per-service token | Shared administrator credential | One leak reaches every service. |
| Rotation with an overlap window | Delete the old key immediately | In-flight clients fail, and teams revert. |
| Short-lived CI identity federation | Long-lived static deploy key | The static key outlives the pipeline compromise. |
| `.env.example` with names and fake values | Example file with real development values | The example gets committed and copied. |
| Revoke first, then clean logs | Delete the commit first | The credential stays valid and evidence is gone. |

## 3. Licensing and Compliance

Every dependency and every distribution carries license obligations. This dimension defines how a project admits
third-party code, chooses its own license, records what it ships, and routes the questions that belong to counsel.

- **Classify inbound licenses into allowed, review, and forbidden.** Allowed examples are MIT, BSD-2-Clause,
  BSD-3-Clause, ISC, 0BSD, and Apache-2.0, subject to attribution and notice obligations; review examples include
  MPL-2.0, LGPL-2.1, LGPL-3.0, EPL-2.0, CDDL-1.0, and public-domain dedications with unclear patent language;
  forbidden includes GPL-2.0 and GPL-3.0 in distributed code, AGPL-3.0 additionally for network-served code, SSPL,
  BUSL-1.1, Commons Clause, non-commercial-only terms, and code with no license. An unknown license is forbidden
  until a human identifies it and records the decision.
- **Check the whole tree, not the top of it.** Read the SPDX identifier from the package metadata and the license
  file, then check direct and transitive components, build tools, container base images, and vendored code.
  Copyleft obligations can hide several levels down, and a dual-licensed package forces an explicit choice. Record
  the resolved license per component, not a summary that cannot be audited later.
- **Choose the outbound license deliberately.** Default to a permissive license for reusable libraries, with a
  patent grant where the project can accept one, and decide copyleft only as an explicit product decision with
  counsel. Put the license in `LICENSE` at the distribution root, in package metadata, and in source headers where
  the ecosystem expects them; confirm that outbound terms are compatible with the inbound licenses and the
  contributions actually used. A license change is a release decision, not an edit.
- **Keep a license inventory.** Record each component with name, version, SPDX identifier, source, usage (runtime,
  build, development, optional), modification status, obligations, and owner. Regenerate it for every release; a
  development-only dependency is still recorded because it can become a shipped one. The inventory is the source of
  the notice file and the SBOM, never a separate hand-written list.
- **Generate an SBOM for every release.** Produce SPDX or CycloneDX JSON from the resolved dependency graph used to
  build the artifact, including transitive components, versions, package identifiers, licenses, and hashes. Attach
  it to the release, retain it for the support lifetime plus the retention period the team adopted, and diff it
  against the previous release so new components are visible. Include container base images and operating-system
  packages; a source-only SBOM understates what is deployed.
- **Ship notices and attribution.** Generate `NOTICE` or `THIRD_PARTY_NOTICES` from the inventory, include the full
  license text where the license requires it, preserve upstream `NOTICE` content for Apache-2.0 components, and
  record the copyright line the license requires. Put the notice file at the distribution root and inside packaged
  artifacts; attribution that lives only on a website fails the obligation for the binary that ships.
- **Settle contribution agreements.** Default to a Developer Certificate of Origin sign-off on every commit; use a
  contributor license agreement only when the organization requires one, and state which in `CONTRIBUTING`. The
  inbound license is the outbound license unless counsel approves otherwise; never merge code with unknown
  provenance, code copied from an incompatible source, or a contribution without the required sign-off.
- **Flag export and regulatory questions.** When a product uses cryptography, is distributed to regulated or
  sanctioned markets, or belongs to a regulated sector, route the classification question to counsel and record the
  decision or the "not applicable" determination. Do not write a legal conclusion into the repository; keep the
  documented decision and its owner, and revisit it when distribution or functionality changes.

| Good | Bad | Why |
|---|---|---|
| SPDX identifier checked against policy | "It is public on a repository host, so it is reusable" | No license means all rights are reserved. |
| Transitive license scan | Direct dependencies only | Copyleft obligations hide below the top level. |
| Apache-2.0 use with upstream `NOTICE` preserved | Source copied without the `NOTICE` file | The attribution obligation is violated on distribution. |
| Notice file generated from the inventory | Hand-copied attribution list | It drifts at the first dependency change. |
| Sign-off on every contribution | Merging unsigned code | Rights and provenance are unknown. |
| Counsel-approved exception with owner and expiry | Verbal approval from counsel | No record, and the exception outlives its context. |

Outbound defaults by distribution type, subject to counsel and the organization's policy:

| Project type | Default outbound license | Reason |
|---|---|---|
| Reusable library or SDK | Apache-2.0 | Permissive use plus an explicit patent grant. |
| Small internal tool released publicly | MIT | Short, permissive, and widely understood. |
| Hosted application | Proprietary or no license grant | The service is not distributed, so a source license is a separate decision. |
| Documentation and specifications | CC BY 4.0 | Content reuse with attribution; not for code. |
| Sample code inside documentation | Match the project license | Snippets are copied, so their terms must be clear. |

## 4. Privacy

Privacy work starts before a field is collected and ends only when the data is deleted. This dimension covers
classification, inventory, purpose, minimization, retention, data subject requests, processors, transfers, and
breach notification; where a rule depends on jurisdiction, counsel decides and the decision is recorded.

- **Classify personal data.** Classify each element by sensitivity and access, using public, internal, confidential,
  and restricted. Names, email addresses, phone numbers, account identifiers, and support messages are confidential;
  government identifiers, financial accounts, health information, precise location, and authentication secrets are
  restricted. Treat IP addresses, device identifiers, and pseudonymous identifiers as personal data in the
  inventory, and let counsel settle jurisdiction-specific classification.
- **Map the inventory and the flows.** Record for each element: subject, source, purpose, system, storage location,
  recipients and processors, region, retention, and access roles. Tabulate or draw the flows between service,
  warehouse, logs, backups, and vendors; the map is what makes a deletion request or a breach assessment possible.
  A new field, system, vendor, or export adds an inventory row before production traffic reaches it.
- **State the purpose and record consent where required.** Collect for a named purpose and do not reuse the data for
  a new purpose without review; let counsel determine the lawful basis and where consent is required. Marketing
  consent is opt-in and never pre-checked, cookie and SDK categories are gated on the matching consent, and a
  consent record captures the version, timestamp, and scope. "We may use data for any purpose" states no purpose.
- **Minimize what exists.** Remove any field without a documented purpose; prefer internal identifiers over direct
  identifiers; hash, truncate, or aggregate where the identity is not needed; keep personal data out of logs, URLs,
  query strings, error messages, event names, and test fixtures. Treat each analytics event as a data collection:
  name its purpose and owner, review its property schema, truncate IP addresses, never capture page text or form
  input, and gate it on the same consent decision as the SDK that sends it.
- **Bound retention and hand off the mechanism.** Set a retention period per element in the inventory and define the
  deletion path, including backups, caches, logs, and processor copies. The data and platform roles own deletion jobs
  and migrations; this standard sets the policy and requires evidence that the job ran. A legal hold is a counsel
  decision; until counsel lifts it, deletion for that element pauses and the reason is recorded.
- **Handle data subject requests.** Publish an intake channel, verify the requester's identity, and respond within
  the team's adopted 30 days or the statutory deadline counsel sets, whichever is shorter. Search every system in
  the inventory, including logs and processors, deliver the result in the requested format, and record the date,
  systems searched, and outcome. Deletion requests propagate to processors and backups on the documented schedule.
- **Review processors and transfers.** No processor receives personal data before a data processing agreement, a
  security review, a documented data location, and a deletion commitment; keep the subprocessor list current and
  reassess annually. A cross-border transfer needs the mechanism counsel approves, a storage region, and a rule for
  remote support access; copying production data to a laptop or a local development database is a transfer that
  bypasses every control.
- **Prepare breach notification before the breach.** On detection, classify and contain within 24 hours, preserve
  the evidence, and brief the incident owner and counsel. Counsel sets the legal notification deadline and the
  recipients; the team prepares the facts and the timeline, notifies parties the contract requires, and prevents any
  public statement before approval. Complete a post-incident review that records the gap and the control that
  prevents a repeat.

| Class | Examples | Handling |
|---|---|---|
| Public | Published documentation, marketing pages | No restriction beyond the approval to publish |
| Internal | Internal metrics, non-sensitive configuration | Authenticated staff access |
| Confidential | Name, email address, phone number, account identifier, support message | Role-based access, encryption in transit and at rest, no logs |
| Restricted | Government identifier, financial account, health data, precise location, credential | Explicit approval, field-level encryption, audited access, minimum retention |

| Good | Bad | Why |
|---|---|---|
| Inventory row with purpose, retention, and region | "It is only an email address" | Every identifier carries obligations and a deletion path. |
| Event schema reviewed before deployment | Field added by the analytics team | Collection escapes purpose and review. |
| Pseudonymous identifier in analytics | Raw email in an event property | The warehouse becomes a second identity store. |
| Consent gate before the SDK loads | Banner that only informs | Consent recorded after collection does not authorize it. |
| Deletion verified against backups and processors | Delete from the primary table only | Copies survive in logs, backups, and vendors. |
| Processor reviewed before data flows | SDK added and disclosed later | Data already left under unagreed terms. |
| Counsel sets the notification deadline | Team guesses the deadline and notifies publicly | A wrong disclosure creates its own liability. |

## 5. Vulnerability Disclosure

Disclosure is a process with promises attached: a reporter must reach a human, the team must meet the timelines it
publishes, and users must be able to patch before the details become public. This dimension covers the channel, the
rating, the fix, the advisory, credit, CVE handling, bounty boundaries, and the embargo.

- **Publish the channel and the scope.** The `SECURITY.md` content names a monitored reporting address, an encrypted
  channel where available, supported versions, in-scope components, out-of-scope categories such as social
  engineering and physical access, the safe-harbor terms for good-faith research, and the response commitments
  below. Repository governance owns only the file's presence, location, and basic metadata (owner, review date), and
  the documentation conventions own its page structure and prose; this standard owns the content and the
  commitments it publishes. Confirm that the
  address resolves and the channel is monitored at least quarterly.
- **Acknowledge and triage on the clock.** Acknowledge a report within 2 business days, complete initial triage
  within 5 business days, and give the reporter a severity, an owner, and the next milestone. Send a status update
  at least every 10 business days while the report is open, and record the timestamps in the report log. A report
  that receives no acknowledgement is a reporter who goes public or gives up.
- **Rate severity with a published scale.** Assign CVSS v3.1 or v4.0 with the metric vector recorded, then adjust
  for exposure, exploit availability, data sensitivity, and compensating controls in the advisory notes. Severity
  drives the remediation deadline: critical 7 calendar days, high 30, medium 90, low 180 or the next scheduled minor
  release. A disagreement is escalated to the security owner and the rating is recorded, not negotiated in the
  report thread.
- **Coordinate the fix and the release.** Reproduce the issue, fix it on a private branch or fork, add a regression
  test in the same change, and ship an out-of-band patch for critical and high findings rather than waiting for the
  scheduled release. Backport to every supported version, coordinate with the maintainers of a vulnerable dependency
  or downstream distributor, and give major customers advance notice under the embargo where a contract requires
  it.
- **Publish an advisory with the fix.** After the fixed release, publish an advisory with the CVE identifier,
  affected and fixed versions, severity and vector, impact, workarounds, and reporter credit; add the entry to the
  changelog and release notes. Publish within 2 business days of the release and before the embargo ends, and keep
  exploitation details out of the advisory until users have had a patch window.
- **Keep credit predictable.** Offer credit by name or handle and link, default to crediting every reporter who
  followed the process, and honor a request to stay anonymous. Credit is independent of a bounty payment and of the
  severity; a duplicate report that helped confirm the issue can still be credited. Never use credit, or its
  withdrawal, as leverage in a dispute.
- **Request a CVE identifier.** Request a CVE through the project's CNA or an authorized CNA before publishing the
  advisory; include the affected versions, the weakness type, and a description of the impact. Record the identifier
  in the advisory, the changelog, and the release notes. If assignment is delayed, publish the advisory with the
  request status and update it when the identifier is assigned.
- **Set bounty and embargo boundaries explicitly.** Run a bounty program only where budget, rules, and a triage
  process exist; state in-scope assets, prohibited tests, reward criteria, and that access to other people's data is
  never authorized. The embargo default is 90 calendar days from the report; shorten it for active exploitation or a
  publicly known issue, extend it only with the reporter's agreement and a recorded reason, and if another party
  publishes first, publish the mitigation and advisory immediately rather than holding the embargo alone.

| Good | Bad | Why |
|---|---|---|
| Monitored channel with published commitments | Security mailbox nobody reads | Reports are lost, and researchers publish instead. |
| Fix and advisory on the same day | Silent patch with no advisory | Users cannot assess exposure or verify the fix. |
| CVSS vector recorded in the advisory | Severity chosen by intuition | No comparable basis and no audit trail. |
| CVE requested before publication | Advisory without an identifier | Downstream scanners and customers cannot track it. |
| Credit offered and opt-out honored | Reporter's name published without consent | Trust is broken with the next researcher. |
| Published embargo with a recorded end date | Indefinite embargo with no date | Reporters escalate to public disclosure. |
