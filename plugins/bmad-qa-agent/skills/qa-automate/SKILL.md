---
name: qa-automate
description: >-
  Generate API and E2E tests for existing code. Auto-detect test framework,
  discover features, generate tests, run and verify.
  当用户说「生成测试」「自动化测试」「写测试」「test generation」时触发。
---

# QA Automate

Generate automated API and E2E tests for implemented code.

**Scope**: This skill generates tests ONLY. It does not perform code review or story validation.

---

## Step 1: Detect Test Framework

Scan the project for an existing test framework:

1. Check `package.json` dependencies for test frameworks (Playwright, Jest, Vitest, Cypress, pytest, etc.)
2. Look for existing test files to understand patterns and conventions
3. Use whatever framework the project already has

**If no framework exists:**
- Analyze source code to determine the project type (React, Vue, Node API, Python, etc.)
- Recommend the current best-practice framework for that stack
- Ask the user to confirm before proceeding

## Step 2: Identify Features to Test

Ask the user what to test, or auto-discover:

- A specific feature or component name
- A directory to scan (e.g., `src/components/`, `src/api/`)
- Auto-discover: scan route handlers, page components, or service modules

List discovered features and confirm scope with the user before generating.

## Step 3: Generate API Tests (if applicable)

For each API endpoint or service, generate tests that cover:

- **Status codes**: 200 (success), 400 (bad request), 404 (not found)
- **Response structure**: validate returned data shape and types
- **Happy path**: normal successful usage with valid input
- **Error cases**: 1-2 critical failures (missing required fields, unauthorized access)

Follow the project's existing test patterns. Use standard framework APIs only.

## Step 4: Generate E2E Tests (if UI exists)

For each UI feature, generate tests that cover:

- **User workflows**: end-to-end interaction flows (e.g., fill form, submit, see confirmation)
- **Semantic locators**: use roles, labels, and text content -- never CSS selectors or XPaths
- **User interactions**: clicks, form fills, navigation, keyboard input
- **Visible outcomes**: assert on what the user can see (text, elements, state changes)

Keep tests linear and simple. Follow the project's existing test patterns.

## Step 5: Run Tests

Execute all generated tests using the project's test command.

- If tests pass, proceed to summary
- If tests fail, **fix failures immediately** -- do not leave broken tests
- Re-run after fixes to confirm all pass

## Step 6: Output Summary

Generate a markdown summary:

```markdown
# Test Automation Summary

## Generated Tests

### API Tests
- [x] tests/api/endpoint.spec.ts - Endpoint validation

### E2E Tests
- [x] tests/e2e/feature.spec.ts - User workflow

## Coverage
- API endpoints: X/Y covered
- UI features: X/Y covered

## Next Steps
- Run tests in CI
- Add more edge cases as needed
```

---

## Validation Checklist

Before completing, verify all of the following:

### Test Generation
- [ ] API tests generated (if applicable)
- [ ] E2E tests generated (if UI exists)
- [ ] Tests use standard test framework APIs only
- [ ] Tests cover happy path
- [ ] Tests cover 1-2 critical error cases

### Test Quality
- [ ] All generated tests run successfully
- [ ] Tests use semantic locators (roles, labels, text) -- no CSS selectors or XPaths
- [ ] Tests have clear, descriptive names
- [ ] No hardcoded waits or sleeps (use framework wait utilities)
- [ ] Tests are independent (no execution order dependency)

### Output
- [ ] Test summary created
- [ ] Tests saved to appropriate project directories
- [ ] Summary includes coverage metrics

---

## Guidelines

**Do:**
- Use standard test framework APIs
- Focus on happy path + critical errors
- Write readable, maintainable tests
- Run tests to verify they pass
- Match existing project test patterns

**Avoid:**
- Complex fixture composition
- Over-engineering or unnecessary abstractions
- Custom test utilities or helper libraries
- Hardcoded waits, sleeps, or timeouts
- Tests that depend on execution order
