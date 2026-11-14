# Documentation Dimensions

Use this file with `SKILL.md`. Each section gives the rules, examples, and edge cases for one documentation
dimension. When a project already has a convention, read it first and apply the higher-precedence rule; this file
supplies the default and the reason. Read the section that matches the document you are writing or reviewing.

## 1. README

- Open with one sentence that states what the project is, who it is for, and what it does; the project name alone is
  not a description.
- Include install, a quick start that produces a visible result, configuration with defaults, and links to deeper
  docs; omit the full feature tour, which ages fastest.
- State requirements (runtime version, OS, database) next to the install command; an unstated prerequisite is the most
  common first-run failure.
- Keep the README short and stable; detailed workflows belong in `docs/guides/`, and the README links to them.
- Include a license and a support path (issue tracker, discussion forum); a project with neither looks abandoned.
- Use badges only when they are live and meaningful; a broken build badge undermines the page that shows it.
- Test the quick start in a clean environment before each release; the README is the most-read page and the first to
  rot.

| Good | Bad | Why |
|---|---|---|
| "Issues invoices and reconciles payments." | "A powerful billing platform." | Names the job; a slogan is not. |
| Install names the runtime version and command. | Install omits the Python version. | Breaks the first run. |
| Quick start ends with a visible result. | Ends with "configuration is easy". | A result confirms the setup. |
| Links to the guide for real workflows. | Full workflow copied into the README. | Copies drift; one page stays right. |

## 2. Onboarding and CONTRIBUTING

- Put setup, run, test, lint, and build commands in one list that works from a fresh clone; link the tool docs only
  when a command needs an option.
- State the branch, commit, and review conventions and the expected review time; a contributor who does not know the
  rules pays for the gap in review.
- Include a first-change path: a small task, the files it touches, and the command that proves it works.
- Name code owners, the support channel, and the decision path for changes that span teams or repositories.
- Document the setup failure modes (missing system package, wrong runtime, busy port) with the exact fix for each.
- Keep contributor onboarding separate from user onboarding; the audiences, toolchains, and success criteria differ.
- Verify the setup on a clean machine or container whenever the toolchain changes; onboarding rots faster than any
  other page.
- Ask a new contributor to run the guide before the first release; the author cannot see the steps that were skipped.

## 3. Architecture and Design Docs

- Describe components, boundaries, data flow, and deployment shape at the level a new maintainer needs; link to code
  for interfaces instead of restating them.
- Record the constraints that shaped the design (scale, latency, compliance, team size) and link the ADRs that own
  each decision.
- Name the external systems and contracts the architecture depends on, with the owner of each contract.
- Keep one current architecture page; superseded diagrams are deleted or moved to a history file, never left beside
  the current one.
- Keep diagrams current; the format, source, and labeling rules are in section 13, Diagrams and Screenshots.
- Include a short known-limits section: what the design cannot do and what would have to change.
- Review the page when a component boundary moves or a new external dependency is added.

## 4. ADRs and Decision Records

- One decision per record, numbered and immutable; a changed decision is a new ADR that supersedes the old one.
- State the decision in one sentence at the top, then status, context, and consequences; a scanning reader can stop
  after the first line.
- Alternatives are required because they show what was rejected and why; a record without them invites a repeat
  debate.
- Record consequences honestly, including cost and accepted risk; an ADR that lists only benefits is advocacy.
- Date every record and link it from the architecture page and the change that implements it.
- Keep ADRs in the repository so they version with the code; a decision that lives only in chat is lost.
- Never rewrite an accepted ADR; append a superseding link and keep the original text intact.
- Reserve ADRs for decisions that constrain later work; a cheap, reversible choice is a code comment or a note.

| Good | Bad | Why |
|---|---|---|
| "Status: Superseded by ADR-0012" with a link. | Silently editing the accepted text. | Readers need the history too. |
| Consequences section lists cost and risk. | A benefits-only record. | Hidden costs are judged later. |
| Dated record linked from the implementation. | An undated file in a folder. | Date and link order decisions. |
| Rejected alternatives kept in the record. | A record without alternatives. | Rejections prevent re-litigation. |

## 5. Tutorials and How-To Guides

- A tutorial teaches by doing: fixed prerequisites, numbered steps, one working result, and no choices; a how-to
  answers one task for a reader who already knows the basics.
- Open both with the outcome and an estimate of time or difficulty so the reader can decide whether to continue.
- Use the reader's vocabulary and the product's real UI labels; a tutorial that invents its own names confuses.
- Cut every step that is not required to reach the result; each extra step is another place to fail.
- Test the tutorial from a clean environment at every release; a broken tutorial is a broken first impression.
- Make each step atomic and show the expected result; a reader who cannot tell success from failure stops and asks.
- For how-to guides, add a verification step and the common failures; the task is not done until the reader can
  confirm it.
- Do not mix teaching with reference completeness; link to the reference when an option is outside the path.

## 6. Reference and API Reference Pages

- Reference is exhaustive and neutral: exact names, types, defaults, constraints, allowed values, and version notes,
  in a stable order.
- One entry per unit (function, flag, endpoint, field); do not merge unrelated units into one table row.
- For every endpoint, state authentication, parameters, response schema, error codes, rate limits, and version.
- Generated reference pages get their structure from this skill and their prose from the comment skill; do not
  duplicate generated details by hand.
- Keep examples minimal and runnable; a reference example shows the smallest correct call, not the whole feature set.
- Link each unit to the guide or tutorial that uses it; reference without a task is hard to apply.
- Version the reference with the API; an unversioned reference page is wrong for every release but one.

| Good | Bad | Why |
|---|---|---|
| `timeout_ms`, integer, default `30000`, range `1..600000`. | `timeout`: wait time. | States type, default, range. |
| One row per parameter with type and default. | One prose paragraph for all. | Tables scan; prose must be read. |
| Minimal request and expected response. | A full app hiding the endpoint call. | Isolates the documented unit. |
| Version note on every changed entry. | One reference for all versions. | Readers apply the wrong version. |

## 7. Explanation and Concept Docs

- Open with the one idea the page exists to convey; if the reader remembers one sentence, it should be that sentence.
- Explain the model and its vocabulary before any procedure; concept pages answer why and link out for how.
- Use one running example and keep it consistent across the page; a second example resets the reader's context.
- State the tradeoffs explicitly, including when the model is the wrong choice; a concept page that sells is
  marketing.
- Define each term on first use and link to the glossary; do not assume the reader shares the team's background.
- Separate the model from the current implementation; link the implementation page instead of describing internals.
- Keep the page stable; it changes when the model changes, not when an option is added.
- End with links to the tutorial that applies the model and the reference that lists the options.

## 8. Changelogs and Release Notes

- Group by version and date; inside a version, group by impact (added, changed, fixed, removed, security) and state
  upgrade actions near the top.
- Write for the user: what behavior changed and what the reader must do, not which files moved.
- Link each entry to the issue or pull request that explains it; the entry is a summary, not the only record.
- Mark deprecations and breaking changes explicitly with the removal version; never bury them under "changed".
- Keep one line per user-visible change; a paragraph per entry hides the list the reader came for.
- Keep an unreleased section for entries without a version, and move the entries when the release is cut.
- Never rewrite a released section to hide a regression; add a corrected entry that references the original.
- Generate release notes from the changelog where possible so the two cannot disagree.

| Good | Bad | Why |
|---|---|---|
| "`GET /v1/orders` removed in 3.0; use v2." | "Orders API cleaned up." | Reader needs action and release. |
| Entries grouped by version with a date. | One undated list since launch. | Version and date decide relevance. |
| Fixed entries link the issue and release. | "Various bug fixes." | A vague entry cannot be acted on. |
| Breaking changes listed first. | Breaking change under "changed". | Readers miss the required upgrade. |

## 9. Runbooks, Operations, and Postmortems

- One alert or operation per runbook, starting with trigger, impact, and the first action; the reader is under
  pressure and has minutes, not an afternoon.
- Show exact commands with environment, permissions, and expected output; never write "check the logs" without the
  command that checks them.
- Include verification that the operation worked and a rollback that restores the previous state.
- Name the escalation path and the decision authority for when the rollback is worse than the outage.
- Link dashboards, alerts, and pipelines by stable name or ID; a link only the author can find is useless at 03:00.
- Review the runbook after every incident and every infrastructure change; an untested runbook is a guess.
- Write a postmortem after every severe incident and link it from the runbook; a runbook carries the procedure,
  a postmortem carries the narrative.

| Good | Bad | Why |
|---|---|---|
| Exact scale command with namespace and count. | "Scale the workers." | On-call should not design commands. |
| Rollback step with its own verification. | "Revert if needed." | Undoing needs a known path. |
| Named escalation channel and owner. | "Escalate to the team." | A reachable target and authority. |
| Expected output after each command. | "Check the logs." | The reader must know success. |

## 10. Security, Legal, and Support Docs

- Keep the security policy content in `SECURITY.md` and present it in scannable sections with links to its owner;
  the required content and response commitments are set by the security role.
- Never publish internal addresses, secrets, employee data, or customer data; use example values such as
  `example@test.invalid`.
- Legal pages (license, terms, privacy) are owned by legal, not engineering; link to them and never paraphrase them
  into a second document.
- Support pages state what is supported, the response target, and what is out of scope; a vague promise becomes an
  obligation.
- Keep the security policy, the support path, and the license reachable from the README and the docs home.
- Record the owner and the last review date on every risk-bearing page; security and legal text decays silently.
- Publish a disclosure timeline that tells the reporter when to expect an update.
- Review the security page against the actual incident process after every exercise; a policy nobody has walked
  through is a hypothesis.

## 11. Troubleshooting and FAQ

- Organize by the symptom the reader can observe, not by the cause they do not know yet.
- For each entry, give symptom, likely cause, fix, and prevention; link the issue tracker for known unfixed bugs.
- Put the exact error text and version in the heading so search and the browser find it.
- Delete entries that no longer apply; a page of obsolete fixes teaches readers to distrust the page.
- Keep FAQ entries to questions users actually ask, ordered by frequency; an FAQ is not a second documentation set.
- Date error messages and versions that appear only in old releases, or remove them.
- End each entry with the page to read next when the fix does not work.
- Link each entry from the error message or the CLI output where the code can do so; readers search the symptom, not
  the docs tree.

## 12. Migration and Deprecation Guides

- State the old and new behavior, the timeline, the removal version, and the support window for the old path.
- Provide a mapping table from removed names, fields, or endpoints to their replacements.
- Give a step-by-step migration with a backup before data is touched and a rollback for each irreversible step.
- Include a validation step that proves the migration worked, with the command or check the reader runs.
- Test the migration on a copy of production-shaped data before publishing the guide.
- Deprecation notices name the replacement and the removal release and appear where users see the old path.
- Warn at runtime or in generated clients where possible; a docs-only deprecation is found too late.
- Do not remove the old path before the announced release; a silent removal violates the published contract.

| Good | Bad | Why |
|---|---|---|
| Mapping table from `amount` to `amount_cents`. | "Update your integration." | The mapping is the work. |
| Removal in `v3.0` with a date and guide link. | "Will be removed soon." | "Soon" cannot be planned against. |
| Backup and rollback before the data rewrite. | A one-way migration script. | A failed migration loses data. |
| Validation command after the migration. | "Verify it worked." | The reader needs a pass condition. |

## 13. Diagrams and Screenshots

- Keep diagrams in a diffable text format (Mermaid, PlantUML, Graphviz) and store the source next to the rendered
  image.
- Label each diagram with scope, version, and date; an unlabeled diagram is read as current and misleads after a
  change.
- Choose the altitude the reader needs (context, container, component, sequence) and stop; one diagram for every
  audience becomes unreadable.
- Regenerate screenshots when the UI changes and crop to the relevant region; a stale screenshot contradicts the text
  and teaches the old interface.
- Keep the instruction in text, not only in an image; images cannot be searched, translated, or read by a screen
  reader.
- Give every image alt text that states its content; decorative images use an empty alt attribute.
- Store large binary sources outside the main repository and link them from the page.

| Good | Bad | Why |
|---|---|---|
| Mermaid block with a version label. | Whiteboard photo with no date. | Text diagrams diff and can be fixed. |
| Screenshot of the current dialog, cropped. | A screenshot of an older UI. | A screenshot is read as current. |
| Alt text describing the image content. | Alt text: "screenshot.png". | Serves search and screen readers. |
| Diagram source kept next to the image. | Only the exported PNG is stored. | The diagram cannot be edited later. |

## 14. Links and Cross-References

- Link to the canonical page, not to a copy, and use the page title or action as the link text; "click here" tells
  the reader nothing.
- Use relative links inside the repository so they work in every branch and in local preview; absolute site URLs
  break in forks and previews.
- Check links in the docs build and treat a broken link as a failure, not a warning.
- Link to stable anchors; when a heading must change, update every inbound link in the same change and add a redirect
  where the site supports one.
- Use the same link text for the same target across pages so search and scanning recognize it.
- Prefer one strong cross-reference over a "see also" list; ten links push the decision back to the reader.
- Date external references and recheck them when the source changes; an external page may move or change meaning.
- Do not link a page from itself, and do not repeat the same link twice on one screen.

## 15. Navigation and Doc Index

- Keep the path shallow: a reader reaches any core page in two or three clicks from the documentation home.
- Group by reader task or doc type (tutorials, guides, reference, explanation), not by team or repository layout.
- Keep one index page that lists every published section; a page absent from the index is effectively unpublished.
- Name navigation entries by what the reader gets, not by an internal project or ticket name.
- Keep sidebar order stable across releases; moving entries breaks bookmarks and muscle memory.
- Remove draft and empty pages from navigation; a link to an unfinished page is a promise not kept.
- Keep the documentation home short and routing: what the product is, who the docs serve, and the three next steps.
- Review the index after adding, moving, or deleting a page; stale navigation is the first symptom of a stale docs
  set.

## 16. Terminology and Glossary

- Keep one glossary per project and use its terms in docs, code, and UI; it is the prose counterpart of the naming
  table.
- Own the glossary in one file; per-team glossaries drift and contradict each other.
- Define each term once and link to the definition; do not redefine it on every page.
- Include the canonical spelling, casing, and abbreviation form, not only the definition.
- Include terms that are ambiguous, translated, or specific to the domain; skip words with one obvious meaning.
- Record banned synonyms and use the canonical term everywhere; mixed terms make readers think the concepts differ.
- Update the glossary in the same change that renames a concept; a stale glossary spreads the old name.
- Keep entries to one sentence and in alphabetical order; a glossary that needs paragraphs is an explanation page.

| Good | Bad | Why |
|---|---|---|
| "Charge: one attempt to collect payment." | Same term defined on three pages. | One definition stops comparison. |
| Alphabetical list of one-line entries. | A glossary that reads like a chapter. | Looked up, not read through. |
| UI label matches the glossary term. | UI says "transaction", docs "charge". | Divergence suggests two concepts. |
| Banned synonyms recorded beside the term. | Three synonyms used at random. | Readers assume different concepts. |

## 17. Localization and Translation

- Write source docs in short sentences, one idea per sentence, and keep code, commands, identifiers, and product
  names out of translatable prose.
- Keep translation files next to the source or in the localization system, with one side defined as the source of
  truth; never hand-edit both.
- Version translations with the source; a translation of an old page is a wrong page in another language.
- Avoid culture-specific examples, dates, currency, and idioms; use ISO dates, explicit units, and plain language.
- Keep screenshots language-neutral where possible, and flag images with embedded text for re-translation.
- Mark untranslated pages explicitly instead of serving stale translated content; a wrong translation is trusted more
  than a missing one.
- Leave room for text expansion; German and Japanese labels are often longer than English ones.
- Review translated pages with a native speaker who can run the examples; machine translation that works is rare.

## 18. Versioning and Applicability

- State the product version in the page metadata or the first paragraph; a page without a version is assumed current.
- Publish docs per major version when behavior differs, keep the default route on the current version, and link older
  versions from a version selector.
- Mark changed and removed options with the version in which they changed, and keep them in the reference until
  removal.
- Use one version scheme across docs, API, and releases; a docs "v2" that means something else confuses readers.
- Remove unsupported versions from the main navigation but keep them reachable for users who are still on them.
- Date anything time-sensitive: support windows, certificate expiry, migration deadlines, and end-of-life dates.
- Remove end-of-life pages from search indexing after the support window ends, but keep the URL alive so old links
  resolve.

| Good | Bad | Why |
|---|---|---|
| "Applies to 2.x; 1.x docs for 1.9." | No version on the page. | The reader cannot tell applicability. |
| "Removed in 3.0" marked in the reference. | A removed option silently deleted. | 2.x readers still need the entry. |
| One version number across docs and API. | Docs "v2" for API "2024-06". | Two schemes hide the mapping. |
| Older versions linked from a selector. | Only the current version published. | Users on old versions lose the docs. |

## 19. Ownership, Maintenance, and Freshness

- Give every page an owner (team or role) in front matter or the docs index; a page without an owner is maintained by
  no one.
- Define the review trigger per doc type: every release for runbooks and reference, on architecture change for design
  docs, annually for legal pages.
- Track the last review date and flag pages past their review interval; freshness is a maintenance signal, not a
  promise of correctness.
- Update the page in the change that alters behavior, and put the docs step in the same issue as the code.
- Delete or archive pages whose feature is removed; a page without a product is worse than no page.
- Review the most-read pages first; a dashboard built from search analytics beats reading the whole tree.
- Record known gaps as issues with an owner and a target release instead of leaving silent holes.
- Rotate the docs review among team members so the ownership does not become one person's private memory.

## 20. Templates and Scaffolding

- Keep one template per doc type in the repository and start every new page from it; a template removes decisions
  that should be common.
- Include the required sections and no optional ones; the author adds what the page needs and deletes nothing
  silently.
- Keep each template short enough to fill in ten minutes; a template that needs an editor is a document.
- Version templates and update existing pages at their next substantive edit, not in a mass rewrite.
- Generate the file from the template with a script or docs generator where the project supports it.
- Revise the template when a review round reveals the same missing section twice.
- Keep templates and the dimension rules in sync; when the rules change, the skeleton changes in the same review.

| Good | Bad | Why |
|---|---|---|
| Five-section ADR template the team fills in. | "Write it in whatever format fits." | Freedom blocks comparison. |
| Required sections marked in the template. | Twenty optional headings. | Optional headings get skipped. |
| Templates updated when review rules change. | A template nobody has read in years. | Teaches a stale structure. |
| Template generated by a script. | Every author retypes the heading. | Retyped structure drifts. |

## 21. Documentation Tests and Sample Validation

- Run code samples in CI: keep them in test files or extract them from the page, and fail when a sample stops working.
- Validate links, anchors, and image paths in the build; a dead-link check is cheap and catches the most common docs
  failure.
- Run commands against the minimum supported version in a clean container; an example that needs the newest release
  teaches the wrong setup.
- Spell-check and style-check with a project dictionary; a checker that flags every product term is turned off.
- Build the docs site on every change, not only at release; a build that runs late hides errors until the worst time.
- Review the rendered output for tables, code blocks, and navigation; source-only review misses rendering failures.
- Treat a failing docs check as a failing build, with the same urgency as a failing test.
- Keep the check configuration in the repository so a local run matches CI exactly.

## 22. Docs Site and Tooling

- Choose one generator and pin its version; MkDocs, Docusaurus, Sphinx, VitePress, and plain Markdown are all
  acceptable when the project can build and publish them reliably.
- Keep content as portable Markdown with relative links, so the site can move without rewriting pages.
- MkDocs fits small and medium docs sets with a simple navigation file and Markdown-first authors.
- Docusaurus fits versioned product docs that need a React site, blog, and translation in one build.
- Sphinx fits API and Python project docs that need generated reference pages and cross-references.
- VitePress fits a fast Markdown site with Vue components; plain Markdown fits projects with no site at all.
- Build in CI and publish from the artifact; never publish from a developer machine.
- Keep configuration, theme, and navigation in version control beside the content.

| Good | Bad | Why |
|---|---|---|
| Pinned generator version and a CI build. | A build that works on one laptop. | Publishing must not need one machine. |
| Plain Markdown content with relative links. | Pages full of shortcodes. | Portable content survives a move. |
| Navigation stored in one reviewed file. | Navigation edited only in a web admin. | A file can be reverted. |
| Build in CI and publish the artifact. | Publish from a developer machine. | Reproducible builds need one path. |

## 23. Public and Internal Boundary

- Classify every page as public (customers, integrators) or internal (staff, operations) and record the audience in
  the repository or site configuration.
- Write public pages for an external reader: no internal hostnames, ticket IDs, staff names, or unshipped plans.
- Keep internal docs in a permissioned space; relying on an unlinked URL is not access control.
- Promote internal content to public only after review for secrets, accuracy, and support commitments.
- Name the reviewer for a boundary change; a page that changes audience needs an owner's approval.
- Keep shared vocabulary across the boundary so a public page and its internal counterpart use the same terms.
- Recheck the boundary when a repository or site changes visibility; a mirror can publish internal pages by accident.

| Good | Bad | Why |
|---|---|---|
| Public page links a public channel. | Public page names the on-call rotation. | Internal routing and names leak. |
| Internal runbook in a permissioned repo. | Runbook hidden by an unlisted URL. | An unlisted URL is found eventually. |
| Shared glossary across both spaces. | Different terms on each side. | Readers cannot map the two. |
| Audience recorded in site configuration. | Only the authors know. | New authors publish to the wrong side. |

## 24. Generated Docs

- Never edit generated output; change the source, the generator configuration, or the doc comment, then regenerate.
- Keep a visible generation marker with the command so the next reader knows the file is not hand-edited.
- Commit generated pages only when the review or hosting process requires it; otherwise build them at publish time.
- Document how to regenerate locally so contributors can rebuild before review.
- Pin the generator version and read generated diffs for noise; reformatting churn hides real changes in review.
- Review the human parts the generator cannot supply: overview, authentication, errors, examples, and version notes.
- Fix a wrong generated page at its source; patching the output reverts on the next build.
- Exclude generated output from formatting and lint rules that would fight the generator.

## 25. Documentation Review

- Review against the reader's task: can the named reader complete the task from this page?
- Check structure first (type, required sections, scope), then facts (commands, versions, links), then language.
- Run the build, link checks, and samples before review; the reviewer should not be the first to find a broken link.
- Ask for evidence in the review: command output, the rendered page, the link-check result.
- Keep the diff scoped to the reviewed page; a docs change that rewrites unrelated sections costs review time and
  hides the real change.
- Check that every changed behavior in the code diff has a matching docs change; a missing docs diff is a finding.
- Re-review pages after an incident or a breaking release and record the review date.
- Reject a page that documents an unshipped plan as current behavior; that is a fact error, not a style issue.

## 26. Archival and Deletion

- Delete a page when its feature or decision is gone; archive it when the history has lasting audit or archaeology
  value.
- Archive with a tombstone that states the date, the reason, and the replacement, and keep it out of main navigation.
- Redirect removed URLs to the replacement or the index; a 404 on an old docs URL loses readers and search ranking.
- Search for inbound links before deleting, inside the repository and in analytics.
- Keep archived docs read-only and mark them unmaintained; an archived page that still receives edits is not archived.
- Delete duplicate copies only after the canonical page is verified; a backup copy elsewhere recreates the problem.
- Record the deletion in the changelog when external readers could have bookmarked the page.

| Good | Bad | Why |
|---|---|---|
| Redirect from the old URL. | A 404 with no replacement. | The reader keeps the answer. |
| "Archived: replaced by the billing guide." | Page silently kept in navigation. | Reader cannot tell it is obsolete. |
| Inbound links updated before deletion. | Delete first, fix links later. | Later never comes; links stay dead. |
| Tombstone states date and replacement. | Archived folder with no explanation. | Readers reopen pages that are gone. |
