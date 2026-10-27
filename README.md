# AI Coding Agent System Prompt

This repository maintains the global constraints, the `system-prompt-authoring` skill, and a user-level Qoder plugin
that packages both. The plugin package is the single source of truth; root `AGENTS.md` and the project skills path are links
to it. Read this first when changing rules, the skill, or the plugin. Maintainer: repository owner.

There is no build step for the Markdown; the format checker depends on `markdown-it-py`. Packaging the plugin zip is a separate step.

## Layout

| Path | Role |
|---|---|
| `AGENTS.md` | Symlink to the canonical rule file under `.qoder/plugins/global-user-constraints/rules/` |
| `.qoder/plugins/global-user-constraints/` | Canonical plugin package: rules, skill, audit command, secret-commit hook |
| `.qoder/plugins/global-user-constraints/rules/global-user-constraints.md` | Canonical always-on rule text |
| `.qoder/plugins/global-user-constraints/skills/system-prompt-authoring/` | Canonical skill source |
| `.qoder/skills/` | Symlink to the plugin's `skills/` directory |
| `.qwen` | Compatibility symlink to `.qoder` for tools that only recognize `.qwen` |

## Edit

1. Edit rules in `.qoder/plugins/global-user-constraints/rules/global-user-constraints.md`; `AGENTS.md` follows the link.
2. Edit the skill in `.qoder/plugins/global-user-constraints/skills/system-prompt-authoring/`; `.qoder/skills` follows the link.
3. Do not create a second copy. If a path resolves through a link, edit the target, not a copy.

## Verify

```bash
python3 .qoder/skills/system-prompt-authoring/script/check.py --strict AGENTS.md
python3 -m unittest discover -s .qoder/skills/system-prompt-authoring/script
```

The checker validates Markdown format only. Content rules S1–S13 are checked manually using `SKILL.md`.

## Distribute

See the plugin [README](.qoder/plugins/global-user-constraints/README.md) for building and validating the user-level plugin zip.
Do not upload rule files, the plugin, or its zip to public platforms; use an approved internal channel.

The enterprise `global-security-guard` plugin is separate and managed; this repository does not disable or replace it.
