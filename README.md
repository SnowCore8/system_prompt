# AI Coding Agent System Prompt

This repository has two kinds of source content: a global instruction baseline for coding agents, and a skill that audits that baseline. It also ships a packaged Qoder plugin under
`.qoder/plugins/global-user-constraints`. There is no build step; the format checker depends on `markdown-it-py`. Changing the Markdown or the script is the whole job.

## Files

| File | Purpose | When to read |
|---|---|---|
| `AGENTS.md` | Symlink to the canonical rule file at `.qoder/plugins/global-user-constraints/rules/global-user-constraints.md`; loaded at session start | When changing rules; when you want the agent to follow a rule |
| `README.md` | This file: what the repo contains and how to use it | First time in this repo |
| `.qoder/skills/system-prompt-authoring/SKILL.md` | Process for auditing and drafting `AGENTS.md`, the S1–S13 content rules, and format-check usage | Before changing `AGENTS.md` |
| `.qoder/skills/system-prompt-authoring/references/provenance.md` | Vendor-document quotes for each S1–S13 rule | When a rule's source is questioned |
| `.qoder/skills/system-prompt-authoring/references/complex-logic.md` | Decision tables, state tables, and complex-logic guidance | When rules involve multi-condition combinations or state transitions |
| `.qoder/skills/system-prompt-authoring/script/check.py` | Format checker; checks Markdown format only, not content rules | After changing `AGENTS.md` |
| `.qoder/skills/system-prompt-authoring/script/test_check.py` | Self-tests for `check.py` | When changing `check.py` |
| `.qoder/plugins/global-user-constraints` | Qoder plugin package: always-on rules, system-prompt-authoring skill, audit command, secret-commit hook | When distributing or installing the rules plugin |

## Usage

Put `AGENTS.md` at the target repository root. It is a symlink to the canonical rule file under
`.qoder/plugins/global-user-constraints/rules/`; edit the target. For distribution, use the plugin package
or its zip, not the symlink alone. When a tool only recognizes fixed filenames (`CLAUDE.md`, `QWEN.md`),
install it under that name or symlink it:

```bash
ln -s AGENTS.md CLAUDE.md
```

After changes, run the format check, then the self-tests:

```bash
python3 .qoder/skills/system-prompt-authoring/script/check.py AGENTS.md
python3 -m unittest discover -s .qoder/skills/system-prompt-authoring/script
```

The checker reports Markdown format issues only; check content quality manually against S1–S13 in `SKILL.md`.
