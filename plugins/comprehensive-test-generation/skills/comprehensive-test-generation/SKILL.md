---
name: comprehensive-test-generation
description: >-
  This skill should be used when the user asks to "generate test cases",
  "生成测试用例", "write e2e tests", "写E2E测试", "generate comprehensive tests",
  "全面测试", "补全测试覆盖", "test coverage gap analysis", "generate playwright tests",
  "写测试", "write tests for", "add tests", "add test coverage", "create test plan",
  "测试计划", "test strategy", "测试策略", "提高测试覆盖率", "test my code",
  or asks to create automated tests from requirements, feature specs, API
  endpoints, or existing code. Also triggered after completing
  superpowers:subagent-driven-development or superpowers:executing-plans when
  comprehensive test coverage is needed before finishing the branch.
---

# Comprehensive Test Generation

Generate holistic test suites from requirements and existing code through a structured four-phase process. Each phase is designed for context efficiency — the master strategy stays lean, sub-agents are self-sufficient.

**Relationship to TDD:** TDD ensures per-task correctness during implementation (red-green-refactor). This skill ensures global requirement coverage after implementation — "did we test everything the spec requires? What edge cases did the coding AI miss?"

**Core principles:**
1. A test strategy designed before code generation produces better tests than ad-hoc writing.
2. Distributed planning beats centralized planning — a short master strategy + self-sufficient sub-agents beats a monolithic 1000-line plan.
3. Evidence-based gap analysis: compare requirements against existing tests before generating new ones.

<HARD-GATE>
Do NOT generate any test code until a master strategy (with requirements coverage matrix) has been written to a file AND the user has reviewed it. No exceptions.
</HARD-GATE>

## Integration with Superpowers

This skill serves as the quality gate between implementation and verification in the superpowers workflow:

```
brainstorming → writing-plans → subagent-driven-dev (TDD per task)
                                        ↓
                              comprehensive-test-generation  ← here
                                        ↓
                              verification-before-completion → finishing-branch
```

**Integrated mode detection:** If `docs/plans/*.md` design documents exist and recent commits are on a feature branch, automatically enter integrated mode — read the design doc for requirements, use `git diff main...HEAD` for code scope, and scan existing test files for coverage baseline.

**Standalone mode:** When no design doc context is detected, or when invoked independently, accept any input type (PRD documents, code paths, verbal description) and run the full Phase 1 exploration.

## Process Flow

```
Phase 1: EXPLORE (understand what to test)
  └─ Scope confirmed? ──no──> EXPLORE (clarify)
  └─ yes
Phase 2: DESIGN (write master strategy ≤200 lines with coverage matrix)
  └─ User approved strategy? ──no──> DESIGN (revise)
  └─ yes
Phase 3: GENERATE (self-sufficient sub-agents)
  └─ Each agent: check existing tests → explore source → design TCs → write code
  └─ All agents complete
Phase 4: VERIFY & HANDOFF
  └─ Run tests → quality audit → coverage report
  └─ Handoff to verification-before-completion
```

## Checklist

Create a task for each item and complete in order:

1. **Detect mode** — check for design docs and feature branch to determine integrated vs standalone
2. **Explore input** — read docs/code, understand what needs testing
3. **Analyze existing tests** — read existing test files to establish coverage baseline
4. **Clarify scope** — confirm test type (E2E / API / Unit / all), present scope summary
5. **Write master strategy** — save concise strategy file (≤200 lines) with requirements coverage matrix
6. **User review** — present strategy, get approval
7. **Generate test code** — dispatch self-sufficient sub-agents
8. **Verify and handoff** — run tests, report coverage, prompt next skill

---

## Phase 1: EXPLORE

Understand what needs testing. Adapt approach based on mode and input type.

### Integrated Mode (from Superpowers Chain)

1. Scan `docs/plans/` for the most recent design document
2. Run `git diff main...HEAD --name-only` to identify changed/added files
3. Scan existing test directories for already-written test files
4. Extract: modules, features, business rules, acceptance criteria from the design doc
5. Present findings — skip to scope confirmation

### Standalone Mode

Adapt approach based on input type:

**Requirement document (Word/PDF/text):**
- Read the document (use pandoc for .docx, pdf skill for .pdf, Read for .md/.txt)
- Extract: modules, features, business rules, field descriptions, state transitions

**Verbal description:**
- Ask clarifying questions one at a time
- Focus on: what feature, what scenarios matter, what edge cases exist

**Code files / API endpoints:**
- Read the specified files
- For backend: analyze domain aggregates, command handlers, API routes, validation rules
- For frontend: analyze page components, form fields, user interactions
- Identify: happy paths, error paths, edge cases, state transitions

### Scope Confirmation (Hard Gate)

Before proceeding to Phase 2, present a scope summary and get confirmation:

```
测试范围确认 / Test Scope Confirmation:
- 目标模块: {module names}
- 测试类型: E2E / API / Unit / All
- 核心场景: {list 3-5 key scenarios}
- 已有测试: {N files, covering X modules}
- 预计 Agent 数量: {N} (1 agent per 1-2 suites)
- 排除范围: {what we're NOT testing}
```

Wait for user confirmation. Do NOT proceed without it.

---

## Phase 2: DESIGN — Master Strategy (≤200 lines)

<CRITICAL>
The master strategy MUST be ≤200 lines. Do NOT write detailed per-test-case plans here.
Detailed TC design is delegated to each sub-agent in Phase 3.
</CRITICAL>

### Requirements Coverage Matrix (Key Addition)

Before writing the strategy, perform gap analysis. Compare requirements from the design doc / PRD against existing test files:

```markdown
## Requirements Coverage Matrix

| Requirement/Feature | Existing Tests | Gap | Test Type Needed | Priority |
|-------------------|---------------|-----|-----------------|----------|
| User login        | ✅ unit (auth.spec) | E2E UI interaction | E2E | P0 |
| File upload       | ❌ none | Full coverage | E2E + API | P0 |
| Report export     | ✅ unit (export.spec) | Edge cases | API | P1 |
```

This matrix drives agent assignments — agents focus on gaps, not re-testing covered scenarios.

### Strategy Contents

Follow the template in `references/test-plan-template.md`. The strategy includes:

1. **Tech stack decisions** — test framework, runner, assertion library
2. **Directory structure** — where test files go
3. **Shared helpers** — reuse existing TDD helpers if they exist; create new ones only for gaps
4. **Mock strategy table** — what to mock and how
5. **Requirements coverage matrix** — gap analysis (see above)
6. **Module assignment table** — which agent handles which gaps + source paths
7. **Acceptance criteria per module** — one-line summary (NOT detailed TCs)

### What the Strategy Does NOT Contain

- Detailed test case descriptions (TC-1.1, TC-1.2, etc.)
- Step-by-step test procedures
- Full code examples for each test

These are designed by each sub-agent after reading the actual source code.

### Agent Granularity Rules

| Project Size | Agent Rule |
|-------------|-----------|
| Small (≤5 suites) | 1 agent per suite |
| Medium (6-15 suites) | 1 agent per 1-2 related suites |
| Large (16+ suites) | 1 agent per 2-3 related suites, max 3 |

**Hard limit:** Never assign more than 3 suites to a single agent.

**Always separate:** test infrastructure setup into its own agent (Agent-0).

### User Review (Hard Gate)

After writing the strategy file:
1. Tell the user the file path
2. Summarize: coverage gaps found, agent count, module assignments
3. Ask the user to review and confirm

Do NOT proceed to Phase 3 until the user approves.

---

## Phase 3: GENERATE — Self-Sufficient Sub-Agents

### Architecture

Each sub-agent is self-contained: reads the short strategy for global conventions, then explores its assigned module's source code, checks existing tests for that module, designs detailed test cases, and writes the test file.

### Step 0: Infrastructure Agent (Agent-0)

Dispatch first (others depend on its output):
- Check for existing test configuration and helpers from TDD phase
- Create only what's missing (do NOT duplicate existing setup)
- Agent type: `general-purpose`

### Step 1: Learn Project Patterns

Before dispatching module agents, analyze existing test files:

| Pattern | What to look for |
|---------|-----------------|
| Framework & runner | jest / vitest / playwright / pytest... |
| Auth pattern | Login helper, fixture, token setup |
| Data setup pattern | Factory / fixture / API call / DB seed |
| Assertion style | expect() / assert / should |

### Step 2: Dispatch Module Sub-Agents

Dispatch agents in parallel using the Task tool. Each agent prompt includes:

1. **The master strategy file path** (agent reads it for conventions/helpers/mocks)
2. **Assigned module names + source file paths**
3. **Instructions:**
   - Read the master strategy file for global conventions and coverage matrix
   - Check existing test files for the assigned module — do NOT duplicate covered scenarios
   - Explore the assigned module's source code (controllers, services, DTOs, entities)
   - Design detailed test cases for the **gaps** identified in the coverage matrix
   - Write complete, runnable test files following project conventions
   - Do NOT invent helpers that don't exist — use shared helpers from Agent-0
   - For E2E: test actions MUST use browser interactions, API calls only for setup
   - Match the declared test type — do not downgrade E2E to API

Sub-agent type: `general-purpose` (needs file read + write access)

### File Naming Convention

- Match existing project conventions
- E2E (Playwright): `{feature-name}.spec.ts`
- Backend (Jest/Vitest): `{feature-name}.spec.ts`
- Backend (pytest): `test_{feature_name}.py`

---

## Phase 4: VERIFY & HANDOFF

After all sub-agents complete:

1. **Run tests** — execute all generated test files, report pass/fail
2. **Quality audit** for E2E tests:
   - Count browser interactions vs API calls per test
   - Flag any E2E test with zero browser interactions
   - Report: "X of Y E2E tests have real UI interactions"
3. **Requirements coverage report** — trace back to the coverage matrix:
   - Mark each requirement as: ✅ now covered / ⚠️ partially covered / ❌ still missing
   - Present the updated matrix to the user
4. **Fix failures** — analyze and fix failing tests
5. **Handoff** — prompt the user:
   > Test generation complete. Next steps:
   > 1. Use `verification-before-completion` to verify all tests pass
   > 2. Use `finishing-a-development-branch` to complete the work

---

## Test Type Quality Rules

See `references/test-type-quality-rules.md` for detailed examples.

| Type | MUST contain | MUST NOT be |
|------|-------------|-------------|
| E2E | Browser navigation, UI interaction, visual assertion on page content | Pure API calls wrapped in Playwright |
| API / Integration | HTTP requests to real endpoints, response + DB state validation | Mocking everything or happy path only |
| Unit | Direct function/method calls, isolated from IO, edge cases | Integration test in disguise |

**Key rule:** E2E setup CAN use API calls, but test actions and assertions MUST go through the browser UI.

---

## Anti-Patterns

| Excuse | Reality |
|--------|---------|
| "Let me write the detailed plan in one giant file" | Master strategy ≤200 lines. Agents design their own TCs from source code. |
| "Let me just write the test code directly" | Without a strategy and coverage matrix, tests miss scenarios. Design first. |
| "Let me write all suites in one agent" | One agent per 1-3 suites max. Context degrades with more. |
| "I'll skip reading existing tests" | Ignoring existing coverage produces duplicate tests. Always check first. |
| "E2E tests are faster via API calls" | API tests belong in integration layer. E2E means browser. |
| "I'll paste the full plan into each agent" | Agents read the strategy file + their own source. Don't paste. |
| "TDD already covered this, no need for comprehensive tests" | TDD covers per-task correctness. This covers requirement completeness. Different goals. |
| "The coverage matrix is overhead" | Without gap analysis, agents re-test what's already covered and miss what's not. |

## Red Flags — STOP immediately and course-correct

- Master strategy exceeds 200 lines (cut per-module details)
- Writing test code before the strategy is approved
- Assigning more than 3 suites to one sub-agent
- Sub-agent not checking existing tests before writing new ones
- E2E test file has zero `page.click()` / `page.fill()` / `locator` interactions
- Skipping the requirements coverage matrix
- Generating tests without understanding the design doc / requirements first
- No gap analysis — generating tests that duplicate existing TDD coverage

---

## Additional Resources

### Reference Files

- **`references/test-plan-template.md`** — Master strategy template with concise format, agent assignment table, requirements coverage matrix, and sub-agent prompt templates (English + Chinese)
- **`references/test-type-quality-rules.md`** — Detailed quality rules per test type, "Setup via API / Test via UI" pattern, UI framework interaction tips (dropdowns, date pickers, file uploads, modals, tables)

### Example Files

- **`examples/example-strategy.md`** — A realistic completed master strategy (~80 lines) demonstrating proper format, coverage matrix, and agent assignments
