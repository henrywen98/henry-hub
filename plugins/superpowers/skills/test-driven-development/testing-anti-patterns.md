# Testing Anti-Patterns

**Load this reference when:** writing or changing tests, adding mocks, or tempted to add test-only methods to production code.

## Overview

Tests must verify real behavior, not mock behavior. Mocks are a means to isolate, not the thing being tested.

**Core principle:** Test what the code does, not what the mocks do.

## The Iron Laws

```
1. NEVER test mock behavior
2. NEVER add test-only methods to production classes
3. NEVER mock without understanding dependencies
```

## Anti-Patterns

1. **Testing Mock Behavior** - Verify real component or unmock it
2. **Test-Only Methods in Production** - Move to test utilities
3. **Mocking Without Understanding** - Understand dependencies first, mock minimally
4. **Incomplete Mocks** - Mirror real API completely
5. **Integration Tests as Afterthought** - Tests are part of implementation

## The Bottom Line

**Mocks are tools to isolate, not things to test.**

If TDD reveals you're testing mock behavior, you've gone wrong.
