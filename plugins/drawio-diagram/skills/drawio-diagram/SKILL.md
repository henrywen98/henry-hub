---
name: drawio-diagram
description: >-
  Generate draw.io (.drawio) diagrams — flowcharts, architecture diagrams, system topology,
  business flow panoramas, sequence diagrams, and any visual representation of processes,
  systems, or relationships. Use this skill whenever the user asks to create, draw, or
  visualize any kind of diagram. Triggers on: "画一个图", "流程图", "架构图", "示意图",
  "系统图", "拓扑图", "帮我画个图", "draw a diagram", "visualize this", "create a flowchart",
  "画业务流程图", "梳理系统逻辑", "发现逻辑断点", "画流程全景图", "可视化业务流程",
  "从需求文档生成流程图", "从PRD画流程图", "根据代码画逻辑图", "draw.io", "drawio".
  Also triggers for auditing cross-module automations, identifying missing logic, or
  creating business-friendly diagrams for non-technical stakeholders. Even if the user
  just says "帮我画个图" without specifying format, use this skill.
---

# Draw.io Diagram Generator

Generates professional `.drawio` diagrams with Chinese text support, built-in visual verification, and automatic partitioning for complex flows.

## Two Input Modes

| Mode | When to Use | How Phase 1 Works |
|------|------------|-------------------|
| **Code Mode** | User has a codebase and wants to extract actual business logic | Launch Explore agents to analyze source code |
| **Document Mode** | User has PRD, requirements, specs, or describes the diagram directly | Read the document(s) / user description and extract structure |
| **Direct Mode** | User describes what to draw directly (e.g., "画一个XX架构图") | Skip Phase 1, go straight to Phase 2 |

Determine the mode from context. If the user says "从代码中生成" or points to a repo → Code Mode. If they provide a document path or paste requirements → Document Mode. If they describe the diagram content directly → Direct Mode. If unclear, ask.

## Workflow

```
Phase 0: Complexity Assessment — scan input, decide agent strategy
    ↓
Phase 1: Extract Content — parallel agents for complex inputs
    ↓
Phase 2: Structure & Partition Planning
    ↓
Phase 3: Generate .drawio File — read references/drawio-spec.md first!
    ↓                              (multi-page: parallel agents per page)
Phase 4: Visual Verification (export PNG → AI inspect)
    ↓
Phase 5: Fix & Re-verify (loop until clean)
    ↓
Phase 6: Deliver
```

---

## Phase 0: Complexity Assessment

Before diving into extraction, quickly scan the input to understand its scale and plan the agent strategy. This prevents wasting context window on a monolithic approach when parallel agents would be more effective.

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

Write this plan down before spawning any agents. The plan should specify:
1. Which agent handles which modules
2. What structured data each agent should return
3. How the outputs will be merged

---

## Phase 1: Extract Content

### Code Mode — Parallel Codebase Exploration

Launch **up to 3 Explore agents in parallel**, each with a focused scope. The goal is to extract every piece of business logic: state machines, status transitions, cross-module automations, approval flows.

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

**Example agent prompt:**
```
Very thorough exploration. Analyze the business logic in [path].
For each module, extract:
1. All status enums with transition rules (from → allowed_to states)
2. All methods that change state — what triggers them, business rules inside
3. All events published and their subscribers
4. Cross-module references
Return structured data, not summaries.
```

### Document Mode — Parallel Document Analysis

For **simple** documents (< 30 elements): read directly and extract inline.

For **complex** documents (6+ modules, 60+ elements): launch **up to 3 agents in parallel**, each responsible for a subset of modules. This prevents context overflow and allows deeper analysis per module.

**Agent split strategy** — group modules by business affinity:

| Agent | Focus | What to Extract |
|-------|-------|-----------------|
| Agent A | Core flow modules (sales, purchase, inventory) | State machines, transition rules, business constraints per module |
| Agent B | Logistics modules (shipment, document, payment) | State machines, approval flows, automation triggers per module |
| Agent C | Support + cross-cutting (master data, automations, appendix) | Entity relationships, cross-module event chains, planned features |

**Each agent must return structured data:**
```
Module: 销售管理
  States: [草稿, 采购中, 已提货, 已入库, 发货中, 已完成]
  Transitions: 草稿→采购中(审批通过), 采购中→已提货(采购提货完成), ...
  Business Rules: [仅草稿可编辑删除, 收款上限=110%, ...]
  Automations In: [采购提货→已提货, 入库完成→已入库, ...]
  Automations Out: [审批通过→生成采购单, ...]
  Notes: [自动完成条件: 发货中+单证齐全+收款≥90%, ...]
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

Evaluate complexity to decide if the diagram needs multiple pages:

| Metric | Single Page | Multi-Page |
|--------|-------------|------------|
| Total nodes | ≤ 30 | > 30 |
| Distinct modules/groups | ≤ 5 | > 5 |
| Cross-module connections | ≤ 15 | > 15 |

**If multi-page**: split along business boundaries (each module or major subsystem gets its own page). Add a "全景总览" page as the first page. draw.io supports multiple `<diagram>` elements in one `.drawio` file — each becomes a separate tab/page.

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

Page 2 (or single page): Module A — "销售管理"
  Nodes: 状态1 → 状态2 → 状态3
  Decisions: 审批? → 通过/驳回
  Connections to other modules: → Module B (采购)

Gaps found (if applicable):
  1. ...
```

---

## Phase 3: Generate .drawio File

**Before writing any XML, read `references/drawio-spec.md`** — it contains the complete draw.io XML structure, element styles, color palette, layout grid, and working examples. This is essential for correct output.

### Parallel Generation for Multi-Page Diagrams

For complex diagrams with 6+ pages, generating all pages sequentially risks context overflow and slow execution. Instead, **split the generation across parallel agents**:

1. **Read drawio-spec.md yourself first** — understand the XML structure and style rules
2. **Assign pages to agents** — each agent generates 2-4 pages as complete `<diagram>` XML blocks
3. **Include the spec context in each agent prompt** — each agent needs: the drawio-spec rules, the blueprint for its assigned pages, the color scheme, and a list of all element IDs from other pages (to avoid ID conflicts)
4. **Merge** — collect all `<diagram>` blocks and wrap in a single `<mxfile>` element
5. **ID prefix convention** — to avoid cross-agent ID conflicts, each agent uses a prefix: Agent X uses `x_`, Agent Y uses `y_`, Agent Z uses `z_`

**Example agent prompt for page generation:**
```
Generate draw.io XML for these pages. Each page is a separate <diagram> element.
Follow the rules from drawio-spec.md (included below).
Use ID prefix "x_" for all elements to avoid conflicts.
Color scheme: Blue=#dae8fc/#6c8ebf, Green=#d5e8d4/#82b366, ...

Page 1: 全景总览
  - 8 module boxes in 2 rows, connected with arrows
  [blueprint details...]

Page 2: 销售管理
  - States: 草稿→采购中→已提货→已入库→发货中→已完成
  [blueprint details...]

Return ONLY the raw <diagram>...</diagram> XML blocks.
```

For simple diagrams (single page or 2-3 pages), generate sequentially — the overhead of spawning agents isn't worth it.

### Key Points (details in drawio-spec.md)

- draw.io files are XML with `<mxfile>` root containing `<diagram>` → `<mxGraphModel>` → `<root>` → `<mxCell>` elements
- Multi-page: multiple `<diagram>` elements inside `<mxfile>`, each with a `name` attribute (shows as tab)
- All text supports HTML via `value` attribute: `value="标题&lt;br&gt;副标题"`
- Use `style` attribute string for all visual properties (fill, stroke, shape, font, etc.)
- Chinese text works natively — no special font configuration needed
- Use `id` attributes that are unique across the entire file

### Arrow Routing (critical for readability)

Arrows crossing through text is the #1 visual quality issue. Two root causes and their fixes:

**Problem 1: Arrows cross through container labels**
Container groups with `verticalAlign=top` put the label right where arrows enter from the layer above. Fix: use **external labels** — empty container `value=""` + separate text element to the left. See "Dashed container with external label" in drawio-spec.md.

**Problem 2: Multiple arrows overlap each other**
When many nodes connect to many targets, arrows share the same path. Fix: **fan out exit/entry points** — spread `exitX` and `entryX` across the node edges so arrows take different paths.

**General rules:**
1. Use `edgeStyle=orthogonalEdgeStyle;rounded=1` for all diagrams (clean, structured look)
2. Always specify `exitX/Y` and `entryX/Y` on edges
3. For architecture diagrams: use external container labels + fan-out pattern
4. Leave ≥ 80px gap between layer groups
5. Use waypoints for complex routing that still crosses elements

See "Connection Point Control", "Arrow-Text Collision Avoidance", and "Architecture Diagram Connection Pattern" in drawio-spec.md.

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

**Zero tolerance**: scan every `value` attribute before saving. If any text contains code terms like `EventBus`, `handler`, `aggregate`, `async`, `commit`, `session`, `query` — replace or remove them. This includes annotations and notes, not just node labels.

---

## Phase 4: Visual Verification

This is what makes complex diagrams reliable. After generating the `.drawio` file, export it to PNG and visually inspect.

### Export to PNG

Try methods in this priority order:

**Method 1: draw.io CLI (preferred)**
```bash
/Applications/draw.io.app/Contents/MacOS/draw.io -x -f png -s 2 -o /tmp/diagram-verify.png <file>.drawio
```
For multi-page files, export each page:
```bash
/Applications/draw.io.app/Contents/MacOS/draw.io -x -f png -s 2 -p 0 -o /tmp/page0.png <file>.drawio
/Applications/draw.io.app/Contents/MacOS/draw.io -x -f png -s 2 -p 1 -o /tmp/page1.png <file>.drawio
```
If the CLI is not installed, try `which draw.io` or check common paths. If not found, fall through.

**Method 2: Playwright (fallback)**
If draw.io CLI is not available, use Playwright to:
1. Open `https://app.diagrams.net` in a headless browser
2. Import the `.drawio` file
3. Take a screenshot

**Method 3: Browser MCP (fallback)**
If `mcp__claude-in-chrome__*` tools are available:
1. Open `https://app.diagrams.net` in Chrome
2. Use File → Open to load the diagram
3. Take a screenshot with the browser tools

### Inspect the Screenshot

Read the exported PNG with the `Read` tool (Claude can view images). Check for:

1. **Arrow-text collision** — do any arrows cross through node labels or group titles? This is the most common issue. If found, fix by adding/adjusting `exitX/Y`, `entryX/Y`, or waypoints.
2. **Text readability** — all labels visible and not garbled?
3. **Layout balance** — modules evenly spaced? Any area too crowded or too empty?
4. **Arrow routing** — arrows go around boxes, not through them? Arrow directions correct?
5. **Color coding** — different modules/groups visually distinguishable?
6. **Completeness** — all expected modules, nodes, and connections present?
7. **Overlap** — any elements covering each other?

---

## Phase 5: Fix & Re-verify

If the visual inspection reveals issues:

1. Identify what's wrong (overlapping text, missing arrow, bad layout, etc.)
2. Edit the `.drawio` XML with the `Edit` tool to fix coordinates, styles, or content
3. Re-export to PNG (Phase 4 Method 1/2/3)
4. Re-inspect the new screenshot

**Repeat until the diagram looks correct.** For complex diagrams, 2-3 iterations is normal.

If no export method is available (no CLI, no Playwright, no browser MCP), do a structural self-check instead:
- Read the XML and verify element positions don't overlap (check x/y/width/height ranges)
- Verify all connections reference valid source/target cell IDs
- Verify all text content is present
- Inform the user that visual verification was skipped

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
