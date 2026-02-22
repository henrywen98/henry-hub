---
name: writing-skills
description: Use when creating new skills, editing existing skills, or verifying skills work before deployment
---

# Writing Skills

## Overview

**Writing skills IS Test-Driven Development applied to process documentation.**

**Personal skills live in agent-specific directories (`~/.claude/skills` for Claude Code, `~/.agents/skills/` for Codex)**

You write test cases (pressure scenarios with subagents), watch them fail (baseline behavior), write the skill (documentation), watch tests pass (agents comply), and refactor (close loopholes).

**Core principle:** If you didn't watch an agent fail without the skill, you don't know if the skill teaches the right thing.

**REQUIRED BACKGROUND:** You MUST understand superpowers:test-driven-development before using this skill.

## What is a Skill?

A **skill** is a reference guide for proven techniques, patterns, or tools.

**Skills are:** Reusable techniques, patterns, tools, reference guides
**Skills are NOT:** Narratives about how you solved a problem once

## The Iron Law (Same as TDD)

```
NO SKILL WITHOUT A FAILING TEST FIRST
```

## SKILL.md Structure

Frontmatter (YAML) with name and description, then Overview, When to Use, Core Pattern, Quick Reference, Implementation, Common Mistakes.

## Claude Search Optimization (CSO)

**CRITICAL: Description = When to Use, NOT What the Skill Does**

Description should ONLY describe triggering conditions. Start with "Use when..." and NEVER summarize the skill's process or workflow.

## RED-GREEN-REFACTOR for Skills

1. **RED:** Run pressure scenario WITHOUT skill, document baseline behavior
2. **GREEN:** Write minimal skill addressing specific rationalizations, verify compliance
3. **REFACTOR:** Close loopholes, add counters, re-test until bulletproof

## Skill Creation Checklist

RED Phase -> GREEN Phase -> REFACTOR Phase -> Quality Checks -> Deployment

See testing-skills-with-subagents.md for complete testing methodology.
