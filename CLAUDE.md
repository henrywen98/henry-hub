# Henry Hub Marketplace

Personal Claude Code plugin marketplace (`henrywen98/henry-hub`).

## Project Structure

```
henry-hub/
├── .claude-plugin/marketplace.json   # Marketplace registry (plugin list)
├── plugins/<name>/                   # Each plugin is self-contained
│   ├── .claude-plugin/plugin.json    # Plugin manifest
│   ├── README.md                     # Chinese documentation
│   ├── skills/                       # Auto-discovered skills
│   ├── commands/                     # Auto-discovered commands
│   ├── agents/                       # Auto-discovered agents
│   └── hooks/                        # Auto-discovered hooks
├── docs/plans/                       # Design & implementation docs
└── README.md                         # Marketplace overview (Chinese)
```

## Plugin Manifest Rules (plugin.json)

**Critical:** All plugins use **auto-discovery** for components. Do NOT add explicit path arrays like `"skills": [...]` or `"commands": [...]` to plugin.json — this causes validation errors (e.g. `skills: Invalid input`).

Correct plugin.json format:
```json
{
  "name": "plugin-name",
  "version": "1.0.0",
  "description": "Plugin description"
}
```

Optional fields: `author`, `homepage`, `repository`, `license`, `keywords`.

Auto-discovery scans these directories automatically:
- `skills/` — Skill .md files
- `commands/` — Command .md files
- `agents/` — Agent .md files
- `hooks/` — hooks.json

## Known Issues

- `test-case-generator` plugin.json has `"skills": ["skills/generate-test-cases.md"]` which causes install failure. Fix: remove the `skills` field, rely on auto-discovery.

## Adding a New Plugin

1. Create `plugins/<name>/` directory
2. Create `plugins/<name>/.claude-plugin/plugin.json` with name, version, description only
3. Place components in standard directories (`skills/`, `commands/`, etc.)
4. Create `plugins/<name>/README.md` in Chinese
5. Add entry to `.claude-plugin/marketplace.json` plugins array
6. Update root `README.md` plugin table

## Skill File Conventions

Two patterns exist in this repo:

| Pattern | Example | Used By |
|---------|---------|---------|
| Nested: `skills/<name>/SKILL.md` | `skills/doc-coauthoring/SKILL.md` | Most plugins (12) |
| Flat: `skills/<name>.md` | `skills/generate-test-cases.md` | test-case-generator |

Prefer the **nested pattern** (`skills/<plugin-name>/SKILL.md`) for new plugins, consistent with the majority.

## Plugin Categories

| Category | Plugins |
|----------|---------|
| Document Processing | docx, pdf, pptx, xlsx |
| Requirements & Workflow | doc-coauthoring, prd-workflow, gen-requirement-doc, ai-pm-feedback-collector, github-issue-generator |
| Testing | test-case-generator, comprehensive-test-generation |
| Dev Tools | batch-commit, ssot-prompt-engineer, code-simplifier (fork), superpowers (fork) |

## Forked Plugins

- `code-simplifier` — forked from Anthropic official, has `agents/` only
- `superpowers` — forked from obra/superpowers v4.3.1, full plugin (skills, agents, commands, hooks)

When updating forks, preserve the original `author`, `license`, and attribution.

## Conventions

- All plugin README.md files are in **Chinese**
- Plugin names use **kebab-case**
- Marketplace registry: `.claude-plugin/marketplace.json`
- Each plugin is self-contained and independently installable
- Do not put `owner` info in individual plugin.json, only in marketplace.json
