---
name: drawio-diagram
description: >-
  Generate draw.io (.drawio) diagrams — flowcharts, architecture diagrams, system topology,
  business flow panoramas, sequence diagrams, and any visual representation of processes,
  systems, or relationships. Use this skill whenever the user asks to create, draw, or
  visualize any kind of diagram. Triggers on: "画一个图", "流程图", "架构图", "示意图",
  "系统图", "拓扑图", "帮我画个图", "draw a diagram", "visualize this", "create a flowchart",
  "画业务流程图", "梳理系统逻辑", "发现逻辑断点", "画流程全景图", "可视化业务流程",
  "从需求文档生成流程图", "从PRD画流程图", "根据代码画逻辑图", "draw.io", "drawio",
  "微服务架构图", "部署架构图".
  Also triggers for auditing cross-module automations, identifying missing logic, or
  creating business-friendly diagrams for non-technical stakeholders. Even if the user
  just says "帮我画个图" without specifying format, use this skill.
---

# Draw.io Diagram Generator

Generates professional `.drawio` diagrams with Chinese text support, built-in visual verification, and automatic partitioning for complex flows.

## Input Modes

| Mode | When to Use | How Phase 1 Works |
|------|------------|-------------------|
| **Code Mode** | User has a codebase and wants to extract actual business logic | Launch Explore agents to analyze source code |
| **Document Mode** | User has PRD, requirements, specs, or an existing diagram file | Read the document(s) and extract structure |
| **Direct Mode** | User describes what to draw directly (e.g., "画一个XX架构图") | Skip Phase 1, go straight to Phase 2 |

Determine the mode from context. If unclear, ask.

## Workflow

```
Phase 0: Complexity Assessment — scan input, decide agent strategy
    ↓
Phase 1: Extract Content — parallel agents for complex inputs
    ↓
Phase 2: Structure & Partition Planning
    ↓
Phase 3: Generate .drawio File
    ↓  Read references BEFORE generating: drawio-spec.md + edge-routing.md
    ↓  Multi-page complex: parallel agents per page group
    ↓
Phase 4: Visual Verification (export PNG → AI inspect)
    ↓  Read validation-guide.md for structured checking
    ↓
Phase 5: Fix & Re-verify (loop until clean, max 3 retries)
    ↓
Phase 6: Deliver
```

---

## Phase 0: Complexity Assessment

Quickly scan the input to understand scale and plan the approach.

### Quick Scan

Read the first ~100 lines of the input (or skim the codebase structure). Identify:
- **Number of distinct modules/areas** (e.g., 8 modules = complex)
- **Estimated total elements** (states + rules + connections)
- **Cross-module dependencies** (few vs many)

### Decide Execution Strategy

| Complexity | Modules | Elements | Strategy |
|-----------|---------|----------|----------|
| **Simple** | 1-3 | < 30 | Single-threaded: read all → generate single page |
| **Medium** | 4-5 | 30-60 | Single-threaded extraction, but plan multi-page output |
| **Complex** | 6+ | 60+ | **Parallel agents** for both extraction AND generation |

### Agent Plan for Complex Inputs

For complex inputs (6+ modules, 60+ elements), plan the full agent topology before executing:

```
Phase 1 agents (parallel extraction):
  Agent A: modules 1-3 (e.g., 销售+采购+库存)
  Agent B: modules 4-6 (e.g., 发货+单证+收款)
  Agent C: modules 7-8 + cross-module automations + appendix sections

Phase 3 agents (parallel generation):
  Agent X: overview page + modules 1-3 detail pages
  Agent Y: modules 4-6 detail pages
  Agent Z: modules 7-8 detail pages + automation summary page
  → Merge all pages into single .drawio file
```

Write this plan down before spawning any agents. Specify:
1. Which agent handles which modules
2. What structured data each agent should return
3. How the outputs will be merged

---

## Phase 1: Extract Content

### Code Mode — Parallel Codebase Exploration

Launch **up to 3 Explore agents in parallel**, each with a focused scope. Extract every piece of business logic: state machines, status transitions, cross-module automations, approval flows.

**Agent split strategy** — adapt to the codebase's architecture:

| Architecture | Agent 1 | Agent 2 | Agent 3 |
|-------------|---------|---------|---------|
| DDD/Layered | Core domains (orders, sales) | Supporting domains (inventory, shipping) | Cross-cutting (events, payments) |
| MVC | Controllers + routes | Models + validations | Background jobs + integrations |
| Microservices | Service A + B | Service C + D | Message queues + API contracts |
| Monolith | Feature group A | Feature group B | Shared logic + DB triggers |

**Each agent must extract:**
- All status/state values and their transition rules (from → to)
- Methods that change state (what triggers them, what happens)
- Events/messages — who publishes, who subscribes
- Business rules (validation thresholds, auto-triggers, approval conditions)
- Cross-module references (which module depends on which)

### Document Mode — Parallel Document Analysis

For **simple** documents (< 30 elements): read directly and extract inline.

For **complex** documents (6+ modules, 60+ elements): launch **up to 3 agents in parallel**, each responsible for a subset of modules.

**Each agent must return structured data:**
```
Module: 销售管理
  States: [草稿, 采购中, 已提货, 已入库, 发货中, 已完成]
  Transitions: 草稿→采购中(审批通过), 采购中→已提货(采购提货完成), ...
  Business Rules: [仅草稿可编辑删除, 收款上限=110%, ...]
  Automations In: [采购提货→已提货, 入库完成→已入库, ...]
  Automations Out: [审批通过→生成采购单, ...]
```

After all agents return, **merge** their outputs into a unified business model.

### Direct Mode

User describes the diagram directly. Skip to Phase 2 with the user's description as input.

---

## Phase 2: Structure & Partition Planning

### Build the Diagram Model

Organize into:

1. **Modules / Groups** — each business area or system component becomes a colored zone
2. **Nodes** — individual steps, states, services, or components
3. **Connections** — arrows showing flow, dependencies, or data movement
4. **Annotations** — notes, conditions, labels on connections

### Gap Analysis (Code/Document Mode only)

Compare what SHOULD be automated vs what IS:

| Pattern | How to Detect | Business Risk |
|---------|--------------|---------------|
| Orphaned events | Published but no subscriber | No downstream effect |
| Missing reverse | Create auto-triggers but delete/update doesn't | Data inconsistency |
| Manual bottleneck | Could auto-advance but requires manual action | Workflow stalls |
| Broken chain | A→B→C but C doesn't feed back to A | Incomplete end-to-end flow |
| Undefined transition | Document mentions states but no path between them | Ambiguous workflow |

### Partition Decision

| Metric | Single Page | Multi-Page |
|--------|-------------|------------|
| Total nodes | ≤ 30 | > 30 |
| Distinct modules/groups | ≤ 5 | > 5 |
| Cross-module connections | ≤ 15 | > 15 |

**If multi-page**: split along business boundaries. Add a "全景总览" page as the first page.

**Panorama page rules (critical):**
- Module boxes must be **rich** — include title, subtitle, key state flow, key business rules. NOT empty boxes with just a title.
- Minimum box size: 250x150 for modules with 4+ lines of content
- Minimum gap between boxes: **100px** so arrows are visible and not covered by text
- Arrow labels between modules should be **short** (1-3 chars like "入库", "出库")
- Include a **visual legend** using actual line/shape elements (not text descriptions). See "Visual Legend Pattern" in drawio-spec.md.
- The panorama should tell the full business story — someone reading only this page should understand the system.

### Write the Blueprint

Before generating XML, produce a text blueprint:

```
Page 1: 全景总览 (if multi-page)
  Modules: [A], [B], [C] — high-level connections

Page 2: Module A — "销售管理"
  Nodes: 状态1 → 状态2 → 状态3
  Decisions: 审批? → 通过/驳回

Gaps found (if applicable):
  1. ...
```

---

## Phase 3: Generate .drawio File

### Reference Loading (IMPORTANT)

Before writing any XML, read these references:

1. **Always read**: `references/drawio-spec.md` — XML structure, colors, shapes, layout grid
2. **Always read**: `references/edge-routing.md` — 7 routing rules, obstacle avoidance, mental checklist
3. **During verification**: `references/validation-guide.md` — structured checking schema

### Parallel Generation for Multi-Page Diagrams

For complex diagrams with 6+ pages, split across parallel agents:

1. Read drawio-spec.md and edge-routing.md yourself first
2. Assign pages to agents — each generates 2-4 pages as `<diagram>` XML blocks
3. Include spec context in each agent prompt — spec rules, blueprint, color scheme, existing IDs
4. **ID prefix convention** — Agent X uses `x_`, Agent Y uses `y_`, Agent Z uses `z_`
5. Merge all `<diagram>` blocks into a single `<mxfile>` element

For simple diagrams (1-3 pages), generate sequentially.

### Key XML Rules

- draw.io files are XML: `<mxfile>` → `<diagram>` → `<mxGraphModel>` → `<root>` → `<mxCell>`
- Every page needs root cells: `<mxCell id="0"/>` and `<mxCell id="1" parent="0"/>`
- All `<mxCell>` elements must be **siblings** — never nest mxCell inside another mxCell
- **Never include XML comments** (`<!-- -->`). draw.io strips comments, which breaks structural references.
- Chinese text works natively — no special font configuration needed
- Use `html=1` and `&lt;br&gt;` for multi-line text in values
- **Animated connectors**: add `flowAnimation=1` to edge style for animated flow visualization

### Pre-Generation Mental Checklist

Before outputting XML, mentally verify (from edge-routing.md):

1. "Do any edges cross over shapes that aren't their source/target?" → add waypoints
2. "Do any two edges share the same path?" → adjust exit/entry points
3. "Are any connection points at corners (both X and Y are 0 or 1)?" → use edge centers
4. "Could I rearrange shapes to reduce crossings?" → revise layout

### Business Language Rules (Code Mode)

When generating diagrams from code analysis, all text must use business language:

| Code Term | Business Term |
|-----------|--------------|
| Function names (`pick_up()`, etc.) | Remove; use arrows + action words |
| Event names (`PaymentCreated`) | "录入收款后", "审批通过后" |
| Technical concepts (`EventBus`, `ACL`) | "系统自动联动" — never use "EventBus" even in annotations |
| Field references (`sales_order_id`) | "关联销售订单" |
| Domain jargon (`aggregate`, `handler`, `repository`) | Remove entirely |
| Implementation details (`异步执行`, `数据库提交后`) | Remove or rephrase as "自动触发" |

**Zero tolerance**: scan every `value` attribute before saving. If any text contains code terms like `EventBus`, `handler`, `aggregate`, `async`, `commit`, `session`, `query` — replace or remove them.

---

## Phase 4: Visual Verification

After generating the `.drawio` file, verify its visual quality.

### Export to PNG

Try methods in priority order:

**Method 1: draw.io CLI (preferred)**
```bash
/Applications/draw.io.app/Contents/MacOS/draw.io -x -f png -s 2 -o /tmp/diagram-verify.png <file>.drawio
```
For multi-page: add `-p <page_index>` (0-based).

**Method 2: Playwright (fallback)**
Open `https://app.diagrams.net` headless, import file, screenshot.

**Method 3: Browser MCP (fallback)**
Use `mcp__claude-in-chrome__*` tools if available.

### Structured Inspection

Read the PNG with the `Read` tool. Check using the **severity-based schema** from validation-guide.md:

**Critical (must fix before delivery):**
1. **arrow-text-collision** — arrows crossing through node labels or group titles
2. **element-overlap** — shapes covering each other, content unreadable
3. **edge-routing** — arrows going through non-source/target nodes
4. **rendering** — incomplete, corrupted, or missing elements

**Warning (record but don't block delivery):**
5. **text-readability** — labels visible and not garbled
6. **layout-balance** — modules evenly spaced, no extreme crowding
7. **color-coding** — different modules/groups visually distinguishable
8. **completeness** — all expected modules, nodes, connections present

`valid = true` only if zero critical issues.

---

## Phase 5: Fix & Re-verify

If critical issues found:

1. Identify specific elements with problems (by name, not "some elements")
2. Edit the `.drawio` XML with the `Edit` tool — adjust coordinates, add waypoints, fix styles
3. Re-export to PNG and re-inspect
4. **Max 3 retries.** After that, deliver with remaining warnings noted.

Common fixes:
- Arrow crossing text → add waypoints or adjust exit/entry points (see edge-routing.md)
- Elements overlapping → shift coordinates, increase spacing
- Text truncated → increase element width/height
- Missing connections → add edge elements with correct source/target IDs

If no export method is available, do structural self-check:
- Verify element positions don't overlap (check x/y/width/height ranges)
- Verify all connections reference valid source/target cell IDs
- Verify all text content is present
- Inform user that visual verification was skipped

---

## Phase 6: Deliver

1. Save `.drawio` to the project root (or user-specified path)
2. Report:
   - File path and size
   - Number of pages (if multi-page), modules, and connections
   - Gaps identified (if Code/Document mode)
   - Verification result (visual pass/fail, iterations needed)
3. Explain how to open:
   - **draw.io desktop**: double-click the file
   - **VS Code**: install "Draw.io Integration" extension, then click the file
   - **Web**: open https://app.diagrams.net → File → Open
