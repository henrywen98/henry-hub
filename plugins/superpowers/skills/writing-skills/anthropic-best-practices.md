# Skill authoring best practices

> Learn how to write effective Skills that Claude can discover and use successfully.

Good Skills are concise, well-structured, and tested with real usage.

## Core principles

### Concise is key

The context window is a public good. Only add context Claude doesn't already have. Challenge each piece of information.

### Structure for scanning

Use headers, tables, and bullet points. Claude scans before reading in detail.

### Test with real usage

Deploy to a test environment and verify Claude discovers and follows the skill correctly.

## Skill metadata

- **name**: Use letters, numbers, and hyphens only
- **description**: Start with "Use when..." to describe triggering conditions, not the workflow

## SKILL.md structure

1. Overview with core principle
2. When to Use (with flowchart if decision is non-obvious)
3. Core Pattern or Process
4. Quick Reference
5. Common Mistakes
6. Red Flags
