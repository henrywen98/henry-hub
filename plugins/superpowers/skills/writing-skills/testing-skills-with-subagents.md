# Testing Skills With Subagents

**Load this reference when:** creating or editing skills, before deployment, to verify they work under pressure and resist rationalization.

## Overview

**Testing skills is just TDD applied to process documentation.**

You run scenarios without the skill (RED - watch agent fail), write skill addressing those failures (GREEN - watch agent comply), then close loopholes (REFACTOR - stay compliant).

**Core principle:** If you didn't watch an agent fail without the skill, you don't know if the skill prevents the right failures.

## When to Use

Test skills that:
- Enforce discipline (TDD, testing requirements)
- Have compliance costs (time, effort, rework)
- Could be rationalized away ("just this once")

## TDD Mapping for Skill Testing

| TDD Phase | Skill Testing Phase |
|-----------|-------------------|
| RED: Write failing test | Run scenario WITHOUT skill, document baseline |
| GREEN: Write minimal code | Write skill addressing specific failures |
| REFACTOR: Clean up | Close loopholes, add rationalization counters |

## Pressure Types

Combine multiple pressures for realistic scenarios:
- **Time pressure** - "Quick fix needed"
- **Sunk cost** - "Already spent hours on this"
- **Authority** - "Manager wants it done NOW"
- **Exhaustion** - "Just this one last thing"
