---
name: documentation-conventions
description: Defines, reviews, and restructures project documentation for any programming project, including READMEs, contribution guides, architecture and design docs, decision records, tutorials, how-to and reference pages, runbooks, changelogs, release and migration notes, security and support docs, and documentation sites. Use when starting a project or a documentation set, reviewing documentation for staleness and duplication, deciding where a fact belongs, or setting documentation rules for contributors.
argument-hint: '[path or doc type]'
---

# Documentation Conventions

Documentation fails less often from bad prose than from absence and drift: the page was never written, the fact went
stale when the code changed, the same answer lives in three files, the reader cannot find the page, or no one owns it.
Each failure is cheap to prevent at authoring time and expensive to repair after readers trust the wrong page. This
skill gives one decision procedure and a complete rule set for every document a project publishes: README and
contribution guides, architecture and design docs, decisions, tutorials and guides, reference and API pages, runbooks,
postmortems, changelogs and release notes, migration and deprecation guides, security and legal pages,
troubleshooting, glossaries, diagrams, and the documentation site that connects them. It applies to any language, framework, and docs toolchain,
and it treats documentation as part of the product rather than a side artifact.

## Scope and Precedence

Apply the first rule that fits, and do not mix standards inside one scope:

1. Mandatory publishing system or organizational standard. Docs site generator constraints, API reference tooling,
   legal disclosure templates, and mandatory company policies are not optional.
2. Existing project structure and convention. Read the docs tree, templates, heading style, and voice before writing;
   follow a stricter local rule over this one.
3. This standard's defaults, when the two levels above are silent.
4. Personal preference, which never overrides the three levels above.

- Source-code comments, docstrings, and doc comments are out of scope; a separate comment skill owns them. Generated
  reference pages built from doc comments get their structure from this skill and their prose from the comment skill.
- Generated documentation, vendored documentation, and copied third-party guides are exempt. Never hand-edit generated
  output, keep the generation marker, and record the upstream source in the page or the index.
- Keep one canonical home per fact. Link to that home from every other page; a second copy is a defect even while it is
  still accurate, because the first edit makes the two pages disagree.
- Update documentation in the same change as the behavior it describes. If the docs and the code land in separate
  commits, land them in one delivery and never leave the default branch describing the old behavior.
- Treat the docs tree as part of the product surface. A change that alters user-visible behavior includes its page,
  and a review that ignores documentation is an incomplete review.
- When two rules conflict, state the conflict and the chosen rule, and record the decision in the project's docs guide
  or an ADR so the next change follows it.

## Process

1. Identify the reader and the question. Name one primary reader and what they must do after reading; a page written
   for everyone answers no one.
2. Classify the document with the Doc Type Matrix. A tutorial, a how-to, a reference, and an explanation answer
   different questions; do not merge two types into one page.
3. Locate the canonical home. Search the repository and the docs site for the fact; if it exists, update that page and
   link to it instead of writing a second copy.
4. Read the project's existing structure and templates. Match the directory, filename, heading style, voice, and front
   matter convention of neighboring pages before drafting.
5. Draft the required sections for the type from `references/templates.md`. Put scope, prerequisites, and the outcome
   in the first screen, and cut every paragraph that does not serve the named reader.
6. Wire the page into navigation and ownership, delete or redirect what it replaces, and update the doc index.
7. Validate links, samples, and the docs build. Run every command, execute every code sample, open every link and
   anchor, check versions and paths, regenerate stale screenshots, and run the link checker and spell check. Review
   the rendered page, not only the source.

## Core Rules

- **Write for one reader and one question.** State who the page serves and what it answers; a page without a named
  reader drifts toward a feature list that serves nobody.
- **State the outcome first.** Put the result, the decision, or the next action in the first lines, then the context;
  readers scan for whether the page applies to them before they read details.
- **Keep one fact in one home.** Each fact belongs to exactly one page; link to it from everywhere else. Duplicated
  facts diverge on the first change and leave readers with two answers.
- **Update docs with the change.** Treat documentation as part of the change: same pull request, same review, same
  release. Stale docs are worse than missing docs because readers trust them.
- **Make examples runnable.** Show complete commands with the working directory, required variables, and expected
  result; an example that cannot be copied and run teaches nothing and costs an issue.
- **Paste real output and versions.** Copy output from an actual run and state the version that produced it; invented
  output hides incompatibilities and misleads readers on every other version.
- **Check every link and anchor.** Resolve links in the build and fix them in the same change; a dead link is a dead
  end that the author never noticed.
- **State applicability.** Name the product version, platform, deployment model, or audience the page serves;
  unversioned instructions rot silently when the next release changes behavior.
- **Name an owner and a review trigger.** Give each page an owning team and the event that forces a review (release,
  schema change, incident); an unowned page is fixed by nobody.
- **Delete or archive stale pages.** Remove what no longer applies and leave a redirect or tombstone naming the
  replacement; a stale page keeps ranking in search and keeps misleading readers.
- **Keep the public line visible.** Separate customer-facing pages from internal notes and mark the audience; an
  internal tradeoff written into public docs leaks information and confuses the reader.
- **Use the type template before inventing a page.** Start from the required sections for the doc type and trim; a
  page designed from scratch usually lacks prerequisites, scope, or the next step.
- **Document the supported path first.** Lead with the recommended path that works, then alternatives; a menu of every
  option forces the reader to make a decision the documentation should have made.
- **State the current truth, not the history.** Keep current behavior in guides and reference; dates, migrations, and
  reasons belong in the changelog or ADR that owns them.

## Where a Fact Belongs

When two pages could hold a fact, choose the home by the question the reader is asking, not by where the fact was
learned. The table below is the default split; a project convention overrides it.

| Fact | Canonical home | Also linked from |
|---|---|---|
| What the project does, install, first run | `README.md` | Docs home, package registry page |
| Development setup and test commands | `CONTRIBUTING.md` | README, issue and PR templates |
| Current flags, defaults, and limits | Reference page | Guides, README examples |
| Why a design or technology was chosen | ADR | Architecture page, code comments |
| How an endpoint accepts and returns data | API reference | Guides, client libraries |
| How to recover a failing service | Runbook | Alert rule, incident template |
| What changed between releases | Changelog or release notes | Migration guide, support replies |
| How a task is done step by step | How-to guide | README, reference pages |
| What a domain term means | Glossary | Every page that uses the term |
| Why an incident happened | Postmortem | Changelog, troubleshooting page |

## Doc Type Matrix

| Document | Reader and question | Required content | Typical location |
|---|---|---|---|
| README | New user: what is it, how do I start? | Name and scope, install, quick start, configuration, documentation links, license | `README.md` |
| CONTRIBUTING | Contributor: how do I set up and submit? | Toolchain, setup, run and test, conventions, review expectations | `CONTRIBUTING.md` |
| Architecture overview | Maintainer: how is it built? | Context, components, boundaries, data flow, decisions, known limits | `docs/architecture/` |
| ADR | Maintainer: why was this decided? | Status, date, context, decision, consequences, alternatives | `docs/adr/` |
| Design doc or RFC | Reviewer: how will it work? | Problem, goals and non-goals, proposal, alternatives, risks, rollout, open questions | `docs/rfcs/` |
| Tutorial | Learner: how do I build one example? | Outcome, prerequisites, numbered steps, result, next step | `docs/tutorials/` |
| How-to guide | Practitioner: how do I do this task? | Goal, prerequisites, steps, verification, common failures | `docs/guides/` |
| Reference page | Practitioner: what are the options? | Synopsis, options and defaults, constraints, version notes, example | `docs/reference/` |
| API reference | Integrator: what can this endpoint do? | Method and path, authentication, parameters, response, errors, example | `docs/api/` |
| Concept or explanation | Learner: why does it work this way? | Idea, model, vocabulary, tradeoffs, examples, links | `docs/concepts/` |
| Runbook | On-call: what do I do now? | Trigger, impact, first action, procedure, verification, rollback, escalation | `docs/runbooks/` |
| Changelog and release notes | User: what changed? | Version and date, grouped entries, upgrade action, issue links, highlights, categories | `CHANGELOG.md` |
| Migration guide | Upgrader: how do I migrate? | Affected audience, timeline, field mapping, steps, verification, rollback | `docs/migrations/` |
| Troubleshooting and FAQ | Stuck user: what does it mean? | Symptom, cause, fix, prevention, related links | `docs/troubleshooting/` |
| Security, legal, support | Reporter: how do I report? | Page structure: policy sections and where each links; disclosures set by security role | `SECURITY.md` |
| Postmortem | Maintainer: why did this happen? | Summary, impact, timeline, root cause, detection, actions, owners | `docs/postmortems/` |

The matrix lists primary page types; the Deprecation Notice, Glossary, and Documentation Index templates cover pages
owned by dimensions 12, 16, and 15.

## Dimension Index

Each dimension has detailed rules, examples, and edge cases in `references/dimensions.md`.

| Dimension | First rule |
|---|---|
| 1. README | State what the project is and the first working command. |
| 2. Onboarding and CONTRIBUTING | One setup path from a fresh clone to a passing test. |
| 3. Architecture and design docs | Components, boundaries, data flow, and links to decisions. |
| 4. ADRs and decision records | One immutable decision with status and consequences. |
| 5. Tutorials and how-to guides | A tested path to one result, not a feature tour. |
| 6. Reference and API Reference Pages | Exhaustive, exact, versioned, generated where possible. |
| 7. Explanation and Concept Docs | The model and vocabulary behind the behavior. |
| 8. Changelogs and release notes | User-visible changes by version and impact. |
| 9. Runbooks, operations, and postmortems | Trigger, commands, verification, rollback, and incident lessons. |
| 10. Security, legal, and support docs | Current policy, reporting channel, supported scope. |
| 11. Troubleshooting and FAQ | Organize by the symptom the reader can search. |
| 12. Migration and deprecation guides | Replacement, timeline, mapping, and rollback. |
| 13. Diagrams and screenshots | Diffable source, labeled scope, regenerated with the UI. |
| 14. Links and cross-references | One canonical page per link, checked in the build. |
| 15. Navigation and doc index | Reach every core page in three clicks by reader task. |
| 16. Terminology and glossary | One term per concept, defined once and reused. |
| 17. Localization and translation | Short source sentences, versioned translations. |
| 18. Versioning and applicability | State the version and keep old docs reachable. |
| 19. Ownership, maintenance, and freshness | Every page has an owner and a review trigger. |
| 20. Templates and scaffolding | Start from the doc type template and trim. |
| 21. Documentation tests and sample validation | Run samples, links, and the build in CI. |
| 22. Docs site and tooling | One pinned generator, content as portable Markdown. |
| 23. Public and internal boundary | Separate audiences, never publish internal notes. |
| 24. Generated docs | Edit the source, regenerate, never hand-edit output. |
| 25. Documentation review | Review the reader's task, facts, and build before style. |
| 26. Archival and deletion | Redirect or tombstone, then remove stale copies. |

## Anti-Patterns

| Anti-pattern | Why it fails | Fix |
|---|---|---|
| README that lists features | Reader cannot tell what to install first. | Lead with scope, install, quick start. |
| Plan described as shipped behavior | Readers build on behavior that does not exist. | Move plans to a design doc. |
| Same answer in README, wiki, and site | Copies diverge; none is current. | Keep one canonical page; link the rest. |
| Commands without a working directory | Commands fail or hit the wrong project. | Show directory, variables, output. |
| Terminal screenshots instead of text | Cannot be copied or searched. | Paste commands and output as text. |
| Dead links to moved pages | Readers stop at a 404 and distrust the set. | Check links in the build; redirect moves. |
| Changelog that repeats git log | Readers cannot find changes needing action. | Group by impact; state the action. |
| Runbook without rollback | Operator can start but not undo it. | Add verification and rollback. |
| Reference generated only from comments | Structure, auth, and examples go missing. | Hand-write the page shell. |
| Docs updated weeks after the code | The branch describes behavior that is gone. | Update the page in the change. |
| No owner and no review trigger | No one edits the page until a complaint. | Assign an owner and review trigger. |
| Wiki page of unrelated topics | A page without a reader serves no one. | Split by doc type; archive the rest. |
| Every option given equal weight | Reader must choose a path the docs should pick. | Lead with the supported path. |
| Deprecation without date or path | Users cannot plan, so they postpone. | State timeline, replacement, steps. |

## Review Checklist

- [ ] The page has one named reader and one question.
- [ ] The doc type matches the Doc Type Matrix.
- [ ] The fact has one canonical page and is linked, not copied.
- [ ] Scope, prerequisites, and outcome appear in the first screen.
- [ ] Commands include the working directory and required variables.
- [ ] Every code sample runs against the current version.
- [ ] Shown output is real and labeled with its version or environment.
- [ ] Every link and anchor resolves in the docs build.
- [ ] Applicable version, platform, and audience are stated.
- [ ] The page is reachable from the doc index or sidebar.
- [ ] The owning team and the review trigger are recorded.
- [ ] No stale page duplicates the content; replaced pages redirect.
- [ ] Public pages contain no internal addresses, secrets, or staff data.
- [ ] Terminology matches the glossary and the code names.
- [ ] Headings follow the project hierarchy and anchor conventions.
- [ ] Screenshots and diagrams match the current UI and are legible.
- [ ] The changelog states user-visible changes and required actions.
- [ ] The docs build, link check, and spell check pass.

## Examples

<example>
README: open with the one-sentence purpose, then install, a quick start that produces a visible result, configuration,
links to the docs site, and the license. Do not put a feature tour before the first runnable command, and test the
quick start on a clean environment before every release.
</example>

<example>
ADR-0007: record status `Accepted`, context (retries after a timeout duplicate charges), decision (require an
`Idempotency-Key` header on `POST /v1/charges`), and consequences (clients must send the header; retries within 24
hours return the original response). Link the rejected alternatives and the migration note for existing clients.
</example>

<example>
Runbook `payments-queue-backlog`: trigger is queue depth above 10,000 for 10 minutes; list impact, pre-checks, the
scale command, the drain verification, and the rollback. Name the escalation channel and its owner, and review the
runbook after every incident that uses it.
</example>

<example>
Deprecation notice: mark `GET /v1/orders` deprecated in `v2.3`, name `GET /v2/orders` as the replacement, state the
removal release `v3.0` and date, and show the request and response mapping. Announce it where users see the old
endpoint, not only in the changelog.
</example>

<example>
Three pages describe the retry policy with different numbers. Keep the reference page as the canonical source, move
the rationale to the ADR, turn the guide into one sentence plus a link, then delete the copies and fix inbound links.
Record the canonical page in the docs index so the next author finds it before writing a fourth copy.
</example>

## References

Read [references/dimensions.md](references/dimensions.md) for the full rule set by document dimension, and
[references/templates.md](references/templates.md) for copyable skeletons of every doc type in the Doc Type
Matrix. Read the matching dimension before writing or reviewing a page; read the template before creating a new
page of that type. Read both when establishing a project's documentation standards from scratch.
