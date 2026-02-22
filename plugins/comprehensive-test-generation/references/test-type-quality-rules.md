# Test Type Quality Rules

Reference guide for ensuring generated tests match their declared type. Use this to validate test quality during Phase 3 verification.

---

## Quality Matrix

### E2E Tests

**Definition:** Tests that exercise the application through the browser, simulating real user behavior.

**MUST contain:**
- Browser navigation (`page.goto`, route changes)
- UI element interaction (`click`, `fill`, `selectOption`, `check`, role-based locators)
- Visual assertions on page content (`expect(page).toHaveTitle`, `expect(locator).toBeVisible`, `toHaveText`, `toContainText`)

**MUST NOT be:**
- Pure API calls (`page.request.post/get`) wrapped in a Playwright test file — that's an API/integration test
- Tests where every assertion is on a JSON response body

**Setup exception:** Precondition data (creating users, orders, inventory) CAN use API calls for reliability. The distinction is:

| Phase | API allowed? | Browser required? |
|-------|-------------|-------------------|
| Setup / Precondition | Yes (preferred for speed & reliability) | No |
| Test Action | No | Yes |
| Assertion | Only for data verification alongside UI checks | Yes (primary) |

### API / Integration Tests

**Definition:** Tests that verify HTTP endpoints return correct responses and produce correct side effects.

**MUST contain:**
- HTTP requests to real running endpoints (not mocked)
- Response status code and body validation
- DB state verification where applicable (data was actually persisted)
- Both success and error scenarios

**MUST NOT be:**
- Tests that mock everything (repository, service, event bus) — that's a unit test
- Tests that only cover happy path

### Unit Tests

**Definition:** Tests that verify a single function, method, or class in isolation.

**MUST contain:**
- Direct function/method calls (no HTTP, no DB)
- Edge cases and boundary values
- Error/exception paths
- Isolated from IO (network, filesystem, database)

**MUST NOT be:**
- Integration tests in disguise (importing real DB sessions, making HTTP calls)
- Tests that only verify the happy path with one input

---

## The "Setup via API, Test via UI" Pattern

This is the recommended pattern for E2E tests. It separates reliable data setup from meaningful UI testing.

### Generic Playwright Example

```typescript
test.describe('Order Management', () => {
  let authToken: string;
  let orderId: string;

  test.beforeAll(async ({ request }) => {
    // [SETUP] Authenticate via API — fast and reliable
    const loginRes = await request.post('/api/login', {
      data: { username: 'admin', password: 'admin123' }
    });
    authToken = (await loginRes.json()).access_token;

    // [SETUP] Create prerequisite data via API
    const orderRes = await request.post('/api/orders', {
      headers: { Authorization: `Bearer ${authToken}` },
      data: { customer_id: 1, items: [{ product_id: 1, quantity: 10 }] }
    });
    orderId = (await orderRes.json()).id;
  });

  test('confirm order via UI', async ({ page }) => {
    // [ACTION] Navigate and interact through browser
    await page.goto(`/orders/${orderId}`);
    await expect(page.getByText('Created')).toBeVisible();

    await page.getByRole('button', { name: 'Confirm' }).click();

    // [ASSERT] Verify UI state changed
    await expect(page.getByText('Confirmed')).toBeVisible();
    await expect(page.getByRole('button', { name: 'Confirm' })).not.toBeVisible();
  });
});
```

### Generic pytest Example (Integration)

```python
class TestOrderCreation:
    """Integration tests for order creation endpoint."""

    @pytest.fixture
    def auth_headers(self, client):
        """[SETUP] Get auth token."""
        res = client.post("/api/login", json={"username": "admin", "password": "admin123"})
        token = res.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    def test_create_order_success(self, client, auth_headers):
        """[ACTION] Create order via API, [ASSERT] verify response and DB state."""
        response = client.post("/api/orders", json={
            "customer_id": 1,
            "items": [{"product_id": 1, "quantity": 10, "unit_price": 100}]
        }, headers=auth_headers)

        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "created"
        assert len(data["items"]) == 1
        assert float(data["total_amount"]) == 1000.0
```

---

## UI Framework Interaction Tips

Common UI component libraries have quirks with Playwright. These are general patterns — always check the project's existing workarounds first.

### Dropdowns / Select Components

Many UI frameworks (Ant Design, MUI, Element Plus) render custom dropdowns that don't use native `<select>` elements.

**General approach:**
1. Click the select trigger to open the dropdown
2. Wait for the dropdown panel to appear
3. Click the option by text

```typescript
// Generic pattern for custom dropdown components
await page.locator('.select-trigger').click();
await page.locator('.dropdown-option').filter({ hasText: 'Option Text' }).click();
```

**If flaky:** Use `waitFor` before clicking options, or add small delays. Document the workaround as a helper function — don't fall back to API calls.

### Date Pickers

```typescript
// Most frameworks: click input, then select date from calendar
await page.locator('.date-input').click();
await page.locator('.calendar-cell').filter({ hasText: '15' }).click();

// Alternative: type directly if the input accepts text
await page.locator('.date-input input').fill('2026-01-15');
```

### Modal Dialogs

```typescript
// Wait for modal to be visible before interacting
const modal = page.locator('.modal-container');
await expect(modal).toBeVisible();
await modal.getByRole('button', { name: 'Confirm' }).click();
await expect(modal).not.toBeVisible();
```

### Tables

```typescript
// Target specific row by content, then interact with it
const row = page.locator('tr').filter({ hasText: 'Order #123' });
await row.getByRole('button', { name: 'Edit' }).click();
```

### File Upload Components

Playwright supports file uploads natively. Use these patterns instead of falling back to API calls:

**Direct file input:**
```typescript
// Most reliable — works with visible and hidden file inputs
const fileInput = page.locator('input[type="file"]');
await fileInput.setInputFiles('/path/to/test-file.xlsx');
```

**File chooser dialog:**
```typescript
// For buttons that trigger OS file picker
const fileChooserPromise = page.waitForEvent('filechooser');
await page.getByRole('button', { name: 'Upload' }).click();
const fileChooser = await fileChooserPromise;
await fileChooser.setFiles('/path/to/test-file.xlsx');
```

**Drag-and-drop upload zones:**
```typescript
// Drop zones that accept dragged files
await page.locator('.upload-dropzone').setInputFiles('/path/to/test-file.xlsx');
```

**Multiple files:**
```typescript
await fileInput.setInputFiles([
  '/path/to/file1.xlsx',
  '/path/to/file2.pdf',
]);
```

**E2E file upload tests MUST verify:**
- Upload success state (progress indicator, success message, file name displayed)
- Invalid file type rejection (error message visible in UI)
- File size limit enforcement (if applicable)
- Upload progress indication (if UI shows it)
- Post-upload page state (parsed data displayed, download link available, etc.)

---

## E2E Quality Self-Check

After generating E2E tests, verify each test file against this checklist:

- [ ] **Navigation exists**: At least one `page.goto()` or route-based navigation
- [ ] **UI interactions exist**: At least one `click()`, `fill()`, `selectOption()`, or `check()`
- [ ] **UI assertions exist**: At least one assertion on page content (`toBeVisible`, `toHaveText`, `toContainText`)
- [ ] **No test-action API calls**: `page.request.post/get` is only used in `beforeAll`/`beforeEach`, not in `test()` body actions
- [ ] **Selector matches project convention**: Uses the same selector strategy as existing tests (role-based, CSS, data-testid)
- [ ] **Setup is separated**: Precondition data creation is in setup hooks or clearly tagged, not mixed with test actions

### Quick Count Test

For a file with N tests declared as E2E:
- Count lines with `page.click|fill|selectOption|check|getByRole|getByText|locator` → should be > 0 per test
- Count lines with `page.request.post|page.request.get` inside `test()` blocks (not setup) → should be 0
- If the ratio is wrong, the test has been downgraded from E2E to API
