# Master Test Strategy Template

Use this template when creating the master strategy in Phase 2. Target ≤200 lines total.

**Key principle:** This is a STRATEGY document, not a detailed test plan. Detailed test case design is delegated to each sub-agent, who will read actual source code.

---

## Template

```markdown
# Test Strategy: {Project/Feature Name}

> **Source**: {requirement doc path / verbal description / code paths}
> **Test type**: E2E / Backend / Both
> **Date**: YYYY-MM-DD
> **Status**: Draft

## 1. Tech Stack

| Type | Framework | Command |
|------|-----------|---------|
| Backend API tests | Jest + supertest + @nestjs/testing | `pnpm test` |
| Unit tests | Jest | `pnpm test` |
| E2E tests | Playwright | `pnpm test:e2e` |

## 2. Directory Structure

{Show where test files go — adapt to project}

## 3. Shared Test Helpers

### {helper-name}.ts — {purpose}
{Short code sketch, 10-20 lines max. Just the interface, not full implementation.}

## 4. Mock Strategy

| Dependency | Mock Method | Notes |
|-----------|-------------|-------|
| {e.g. AI/LLM} | jest.mock | Return fixed JSON |
| {e.g. File storage} | jest.mock | Mock upload/download |
| {e.g. Queue} | jest.mock | Verify enqueue params |
| {e.g. Database} | Real Docker DB | Use TEST_DATABASE_URL |

## 5. Requirements Coverage Matrix

Perform gap analysis before assigning agents. Compare requirements against existing test files:

| Requirement/Feature | Existing Tests | Gap | Test Type Needed | Priority |
|-------------------|---------------|-----|-----------------|----------|
| User login | ✅ unit (auth.spec) | E2E UI interaction | E2E | P0 |
| File upload | ❌ none | Full coverage | E2E + API | P0 |
| Report export | ✅ unit (export.spec) | Edge cases (large files, empty data) | API | P1 |
| Dashboard stats | ✅ E2E (dashboard.spec) | — | — | — |

Mark requirements with no gap as "—" to show they've been reviewed. This matrix drives agent assignments — agents focus on gaps only.

## 6. Agent Assignments

| Agent | Modules | Source Paths | Key Test Points |
|-------|---------|-------------|-----------------|
| Agent-0 | Infra | — | Jest/Playwright config + shared helpers |
| Agent-1 | Auth | src/auth/ | Register, login, JWT, refresh, guard |
| Agent-2 | Company, Dashboard | src/company/, src/dashboard/ | CRUD, cascade delete, stats |
| ... | ... | ... | ... |

## 7. Per-Module Acceptance Criteria

{One-liner per module — NOT detailed test cases}

| Module | P0 Criteria | P1 Criteria |
|--------|------------|-------------|
| Auth | Login/register works, JWT valid, guard blocks unauthorized | Token refresh, duplicate email |
| Company | CRUD + cascade delete + search | Pagination, sort |
| ... | ... | ... |
```

---

## What NOT to Include

The following belong in each sub-agent's own exploration, NOT in the master strategy:

❌ Detailed test case descriptions (TC-1.1, TC-1.2, etc.)
❌ Step-by-step test procedures
❌ Preconditions and expected results per test
❌ Full helper implementation code (just sketches)
❌ Per-endpoint request/response examples

---

## Example: Concise vs Bloated

### ✅ Good (concise — in master strategy)

```markdown
| Agent-3 | Financial | src/financial/ | Upload→parse→store, reconciliation engine (sum/diff/balance), export |
```

One line. Agent-3 will read `src/financial/` source code and design detailed TCs from the actual controller/service/DTO.

### ❌ Bad (bloated — do NOT put this in master strategy)

```markdown
## Suite 4: Financial Statement Upload (P0)

### TC-4.1 Upload valid Excel file
- **Precondition**: Logged in, company exists
- **Steps**:
  1. POST /api/financial/upload with multipart Excel
  2. Verify 201 response
  3. Check parsed data in DB
- **Expected**: Statement created with parsed rows

### TC-4.2 Upload invalid file format
...
```

This is 20+ lines for ONE suite. A project with 14 suites produces 300+ lines of just test cases. That's what explodes context.

---

## Size Guidelines

| Project Scale | Strategy Target | Agent Count |
|--------------|----------------|-------------|
| Small (1-3 modules) | 50-80 lines | 2-3 agents |
| Medium (4-10 modules) | 80-150 lines | 4-7 agents |
| Large (10+ modules) | 150-200 lines | 7-12 agents |

**Hard ceiling: 200 lines.** If the strategy exceeds this, cut per-module details — agents will discover them from source code.

---

## Sub-Agent Prompt Template

When dispatching a sub-agent in Phase 3, use this structure. **Adapt language to match project conventions.**

### English Version

```
Test engineer responsible for writing tests for {module names}.

Workflow:
1. Read {strategy-file-path} for global conventions (tech stack, mock strategy, directory structure, shared helpers, requirements coverage matrix)
2. Check existing test files — do NOT duplicate already-covered scenarios
3. Explore assigned source code:
   - {source paths to explore}
   - Focus on: controllers (routes + params), services (business logic), DTOs (validation rules), entities (data models)
4. Design test cases based on source code:
   - Happy path (normal flow)
   - Error path (validation, auth, 404, conflicts)
   - Edge cases (empty data, extreme values, concurrency)
   - Boundary values (pagination limits, string lengths)
5. Write complete, runnable test files to {output directory}
6. Follow shared helpers interfaces — do NOT invent helpers that don't exist

Acceptance criteria: {paste from strategy's per-module acceptance criteria}

Important:
- One scenario per test case
- Name by behavior: "creates valid order" not "test POST /orders"
- E2E tests: browser interactions for actions, API calls only for setup
- Do NOT fabricate non-existent helper functions
```

### Chinese Version (中文版)

```
你是测试工程师，负责为 {module names} 模块编写测试。

工作流程:
1. 读取 {strategy-file-path} 了解全局约定 (技术栈、Mock策略、目录结构、shared helpers、需求覆盖矩阵)
2. 检查已有测试文件 — 不要重复覆盖已有的场景
3. 探索你负责的源码:
   - {source paths to explore}
   - 重点读: controller (路由+参数), service (业务逻辑), dto (验证规则), entity (数据模型)
4. 基于源码设计测试用例:
   - Happy path (正常流程)
   - Error path (参数校验、权限、404、冲突)
   - Edge cases (空数据、极端值、并发)
   - Boundary values (分页边界、字符串长度)
5. 编写完整可运行的测试文件，放到 {output directory}
6. 遵循 shared helpers 的接口，不要发明不存在的 helper

验收标准: {paste from strategy's per-module acceptance criteria}

重要:
- 每个 test case 测试一个场景
- 按行为命名: "创建有效订单" 而非 "测试 POST /orders"
- E2E 测试: 浏览器交互做操作, API 仅用于 setup
- 不要编造不存在的 helper 函数
```
