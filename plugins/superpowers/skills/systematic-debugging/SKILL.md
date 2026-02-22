---
name: systematic-debugging
description: Use when encountering any bug, test failure, or unexpected behavior, before proposing fixes
---

# Systematic Debugging

## Overview

Random fixes waste time and create new bugs. Quick patches mask underlying issues.

**Core principle:** ALWAYS find root cause before attempting fixes. Symptom fixes are failure.

**Violating the letter of this process is violating the spirit of debugging.**

## The Iron Law

```
NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST
```

If you haven't completed Phase 1, you cannot propose fixes.

## The Four Phases

### Phase 1: Root Cause Investigation

**BEFORE attempting ANY fix:**

1. **Read Error Messages Carefully** - Don't skip past errors or warnings
2. **Reproduce Consistently** - Can you trigger it reliably?
3. **Check Recent Changes** - Git diff, recent commits, config changes
4. **Gather Evidence in Multi-Component Systems** - Add diagnostic instrumentation at component boundaries
5. **Trace Data Flow** - Where does bad value originate? Keep tracing up until source found.

### Phase 2: Pattern Analysis

1. Find working examples in same codebase
2. Compare against references completely
3. Identify differences between working and broken
4. Understand dependencies

### Phase 3: Hypothesis and Testing

1. Form single hypothesis with reasoning
2. Test minimally - smallest possible change
3. Verify before continuing
4. If 3+ fixes failed: question the architecture

### Phase 4: Implementation

1. Create failing test case
2. Implement single fix addressing root cause
3. Verify fix
4. If fix doesn't work, return to Phase 1

## Red Flags - STOP and Follow Process

- "Quick fix for now, investigate later"
- "Just try changing X and see if it works"
- Proposing solutions before tracing data flow
- "One more fix attempt" (when already tried 2+)

**ALL of these mean: STOP. Return to Phase 1.**

## Supporting Techniques

Available in this directory:
- **root-cause-tracing.md** - Trace bugs backward through call stack
- **defense-in-depth.md** - Add validation at multiple layers
- **condition-based-waiting.md** - Replace arbitrary timeouts with condition polling

**Related skills:**
- **superpowers:test-driven-development** - For creating failing test case
- **superpowers:verification-before-completion** - Verify fix worked before claiming success
