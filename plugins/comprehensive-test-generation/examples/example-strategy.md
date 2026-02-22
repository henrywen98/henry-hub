# Test Strategy: AI Due Diligence Platform

> **Source**: docs/plans/2026-02-15-financial-analysis-design.md + existing codebase
> **Test type**: E2E + API
> **Date**: 2026-02-21
> **Status**: Approved

## 1. Tech Stack

| Type | Framework | Command |
|------|-----------|---------|
| E2E tests | Playwright | `pnpm --filter web test:e2e` |
| API tests | Vitest + supertest | `pnpm --filter api test` |
| Unit tests | Vitest | `pnpm --filter api test` |

## 2. Directory Structure

```
apps/web/tests/e2e/          ← Playwright E2E tests
apps/api/test/               ← API integration tests
apps/api/test/unit/          ← Unit tests
```

## 3. Shared Test Helpers

### e2e-helpers.ts — Auth + navigation
```typescript
export async function loginAs(page: Page, role: 'admin' | 'analyst') { ... }
export async function createCompany(request: APIRequestContext, name: string) { ... }
```

### api-helpers.ts — Request factory
```typescript
export function createTestApp(): INestApplication { ... }
export function getAuthToken(app: INestApplication, role: string): string { ... }
```

## 4. Mock Strategy

| Dependency | Mock Method | Notes |
|-----------|-------------|-------|
| AI/LLM analysis | vi.mock | Return fixed analysis JSON |
| File storage (S3) | vi.mock | Mock upload/download, return fake URLs |
| Email notifications | vi.mock | Verify send params only |
| Database | Real Docker PostgreSQL | Use TEST_DATABASE_URL |

## 5. Requirements Coverage Matrix

| Requirement/Feature | Existing Tests | Gap | Test Type Needed | Priority |
|-------------------|---------------|-----|-----------------|----------|
| User authentication | ✅ unit (auth.spec) | E2E login flow | E2E | P0 |
| Company CRUD | ✅ unit (company.spec) | E2E form interaction | E2E | P0 |
| Financial upload & parse | ❌ none | Full coverage | E2E + API | P0 |
| Analysis dashboard | ❌ none | Full coverage | E2E | P0 |
| Report export (PDF) | ❌ none | API generation + E2E download | E2E + API | P1 |
| Template management | ✅ E2E (template.spec) | — | — | — |
| Comparison view | ❌ none | Multi-company comparison | E2E | P1 |

## 6. Agent Assignments

| Agent | Modules | Source Paths | Key Test Points |
|-------|---------|-------------|-----------------|
| Agent-0 | Infra | — | Playwright config, shared helpers, test DB setup |
| Agent-1 | Auth | src/auth/, pages/login | E2E login/logout, session persistence, guard redirect |
| Agent-2 | Financial | src/financial/, pages/financial | Upload Excel→parse→display, reconciliation, data validation |
| Agent-3 | Analysis + Dashboard | src/analysis/, pages/dashboard | AI analysis trigger, results display, chart rendering |
| Agent-4 | Report + Comparison | src/report/, pages/comparison | PDF export download, multi-company comparison view |

## 7. Per-Module Acceptance Criteria

| Module | P0 Criteria | P1 Criteria |
|--------|------------|-------------|
| Auth | Login/logout works via UI, guard blocks unauthenticated access | Remember me, expired session redirect |
| Financial | Upload valid Excel → see parsed data, reject invalid file types | Large file handling, concurrent uploads |
| Analysis | Trigger analysis → see results, dashboard shows summary stats | Analysis retry on failure, progress indicator |
| Report | Export PDF → download succeeds | Custom template selection, bulk export |
| Comparison | Select 2+ companies → see comparison table | Sort/filter comparison data |
