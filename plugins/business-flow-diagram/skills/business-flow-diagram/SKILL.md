---
name: business-flow-diagram
description: >-
  This skill should be used when the user asks to generate a business flow
  diagram from code or requirement documents, such as "draw a business flow
  diagram", "visualize business process", "create an Excalidraw diagram",
  "find logic gaps", "画业务流程图", "梳理系统逻辑", "发现逻辑断点",
  "画流程全景图", "可视化业务流程", "从需求文档生成流程图",
  "从PRD画流程图", "根据代码画逻辑图", "生成Excalidraw图".
  Supports two input sources: codebase analysis and requirement documents.
  Also triggers for auditing cross-module automations, identifying missing
  logic, or creating business-friendly diagrams for non-technical stakeholders.
---

# Business Flow Diagram Generator

Analyzes a **codebase** or **requirement document** and generates a comprehensive Excalidraw flow diagram in business-friendly Chinese. The output helps business stakeholders understand the system's workflow, automations, and gaps — without any code terminology.

## Two Input Modes

| Mode | When to Use | How Phase 1 Works |
|------|------------|-------------------|
| **Code Mode** | User has a codebase and wants to extract actual business logic | Launch Explore agents to analyze source code |
| **Document Mode** | User has PRD, requirements, or business specs | Read the document(s) and extract business flows directly |

Determine the mode from context. If the user says "从代码中生成" or points to a repo, use Code Mode. If they provide a document path, URL, or paste requirements text, use Document Mode. If unclear, ask.

## Workflow Overview

```
Phase 1: Extract Business Logic (parallel agents or document reading)
    |
Phase 2: Synthesize & Gap Analysis
    |
Phase 3: Generate .excalidraw File (Write tool, no dependencies)
    |
Phase 4: Self-Verification (Read + check JSON content)
    |
Phase 5: Visual Verification (screenshot + inspect)
    |
Phase 6: Deliver
```

---

## Phase 1: Extract Business Logic

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

### Document Mode — Requirement Analysis

Read the provided documents and extract the same information:

1. **Read all documents** the user provides (PRD, business specs, user stories, etc.)
2. **Extract modules** — identify each business area described
3. **Extract flows** — map out the described workflows, approvals, state changes
4. **Extract rules** — business constraints, thresholds, conditions
5. **Infer automations** — from "when X happens, Y should happen" language
6. **Flag ambiguities** — where the document is unclear about flow connections

For documents, gap analysis focuses on **completeness** rather than **implementation**:
- Missing edge cases (what happens on delete? on error?)
- Undefined state transitions (document mentions states but not how to get between them)
- Missing cross-module connections (modules described in isolation)

---

## Phase 2: Synthesize & Gap Analysis

After extracting business logic (from either mode), build a structured model.

### Build the Business Model

Organize into:

1. **Modules** — each business area becomes a colored zone
2. **State Machines** — status flows within each module
3. **Automations** — "when X happens in module A, module B automatically does Y"
4. **Manual Steps** — operations requiring user action

### Identify Logic Gaps

Compare what SHOULD be automated vs what IS:

| Pattern | How to Detect | Business Risk |
|---------|--------------|---------------|
| Orphaned events | Published but no subscriber | No downstream effect |
| Missing reverse | Create auto-triggers but delete/update doesn't | Data inconsistency |
| Manual bottleneck | Could auto-advance but requires manual action | Workflow stalls |
| Broken chain | A→B→C but C doesn't feed back to A | Incomplete end-to-end flow |
| Undefined transition | Document mentions states but no path between them | Ambiguous workflow |

### Write the Blueprint

Before generating elements, produce a text blueprint:

```
Module 1 (Color) — "Business Name"
  States: A → B → C → D
  Rules: ...
  Automations in: ...
  Automations out: ...

Cross-module automations:
  1. [Source] action → [Target] auto-action

Gaps found:
  1. ...
```

---

## Phase 3: Generate .excalidraw File

Directly write a `.excalidraw` JSON file using the `Write` tool. No scripts or dependencies needed.

### File Format

The `.excalidraw` format is a JSON file. Excalidraw will auto-calculate missing fields (seed, version, text dimensions) when opened, so only include what matters:

```json
{
  "type": "excalidraw",
  "version": 2,
  "source": "https://excalidraw.com",
  "elements": [ ...element objects... ],
  "appState": { "viewBackgroundColor": "#ffffff" },
  "files": {}
}
```

### Element Types

**Rectangle** (for zones, state boxes):
```json
{"type":"rectangle","id":"s1","x":45,"y":150,"width":105,"height":42,
 "backgroundColor":"#a5d8ff","fillStyle":"solid","roughness":0,
 "roundness":{"type":3},"strokeColor":"#4a9eed","strokeWidth":1}
```

**Text** (for labels, annotations):
```json
{"type":"text","id":"t1","x":32,"y":78,"text":"销售管理",
 "fontSize":20,"fontFamily":2,"strokeColor":"#2563eb"}
```

**Arrow** (for connections):
```json
{"type":"arrow","id":"a1","x":150,"y":171,"width":25,"height":0,
 "points":[[0,0],[25,0]],"strokeColor":"#4a9eed","strokeWidth":2,
 "endArrowhead":"arrow"}
```

**Diamond** (for decision points):
```json
{"type":"diamond","id":"d1","x":100,"y":100,"width":200,"height":80,
 "backgroundColor":"#fff3bf","fillStyle":"solid","strokeColor":"#f59e0b"}
```

### Key Rules

- **fontFamily must be 2** — sans-serif font that supports Chinese. fontFamily 1 (hand-drawn) and 3 (code) break CJK rendering
- **roughness should be 0** — clean lines, more readable for business diagrams
- **Text in shapes**: use separate text elements positioned inside the shape (Excalidraw auto-adjusts on open). For a 105x42 box at (45,150), center text at roughly (60, 162)
- **IDs must be unique** across all elements
- **Arrow step paths**: use multi-point arrays for routing, e.g., `"points":[[0,0],[0,30],[-200,30],[-200,60]]` creates a step-down-left pattern

### Layout Rules

**Spacing:**
- Module zones: 30px gap between adjacent zones
- State boxes: 105x42 minimum, 25px arrows between them
- Font sizes: 20 for zone titles, 13-15 for box labels, 14 for annotations
- 6-state machines: two rows of 3 with step-arrow connecting rows

**Color Scheme:**

| Module Type | Background | Box Fill | Stroke |
|-------------|-----------|----------|--------|
| Primary (Sales) | `#dbe4ff` | `#a5d8ff` | `#4a9eed` |
| Secondary (Purchase) | `#ffd8a8` op25 | `#ffd8a8` | `#f59e0b` |
| Storage (Inventory) | `#c3fae8` op25 | `#c3fae8` | `#06b6d4` |
| Process (Shipping) | `#e5dbff` op25 | `#d0bfff` | `#8b5cf6` |
| Document | `#d3f9d8` op25 | `#b2f2bb` | `#22c55e` |
| Finance (Payment) | `#eebefa` op25 | `#eebefa` | `#ec4899` |
| Warning/Gap | `#ffc9c9` op20 | `#ffc9c9` | `#ef4444` |
| Success/Fixed | `#b2f2bb` op50 | `#b2f2bb` | `#22c55e` |
| Condition/Note | `#fff3bf` op60 | `#fff3bf` | `#f59e0b` |

**Structure:**
- Upper row: core modules (left → right following business flow)
- Lower row: supporting modules (payments, master data)
- Bottom: "系统自动联动" list + "待完善功能" list (if any)

**Overlap Prevention:**
- Route arrows around boxes using multi-point step paths, never through them
- Approval V-shapes: offset reject box 50+ px below pass box
- Approval→state arrows: route around the right side to avoid crossing reject boxes
- Place annotation text to the right or below, never overlapping boxes

### Business Language Rules

All diagram text must use business language:

| Code Term | Business Term |
|-----------|--------------|
| Function names (`pick_up()`, etc.) | Remove; use arrows + action words |
| Event names (`PaymentCreated`) | "录入收款后", "审批通过后" |
| Technical concepts (`EventBus`, `ACL`) | "系统自动联动" |
| Field references (`sales_order_id`) | "关联销售订单" |
| Domain jargon (`aggregate`, `handler`) | Remove entirely |
| "限界上下文" | Module name: "销售管理", "采购管理" |

---

## Phase 4: Self-Verification

Read the generated `.excalidraw` file and check for these issues. No scripts needed — just read and inspect the JSON content.

### What to Check

1. **Encoding** — search for `\ufffd` or garbled characters in text fields
2. **Font** — every element with `fontFamily` should be `2` (not 1 or 3)
3. **Tech terms** — scan all `"text"` values for code terms (function names, event names, domain jargon). Every piece of text should be understandable by a non-technical business person
4. **Overlaps** — for elements that are close together, verify their bounding boxes don't significantly overlap (same x/y range with similar width/height)
5. **Completeness** — cross-check against the Phase 2 blueprint: is every module, state, automation, and gap represented?

### How to Check

Read the file with the `Read` tool (it's JSON, fully readable). Scan through the `elements` array and verify the above. Due to file size, read in sections (offset/limit) if needed.

### If Issues Found

Edit the `.excalidraw` file directly using the `Edit` tool to fix:
- Wrong `fontFamily` → change to `2`
- Tech terms in `"text"` → replace with business language
- Overlapping elements → adjust `x`/`y` coordinates
- Missing elements → add them

**Repeat read-check-fix until clean.**

---

## Phase 5: Visual Verification (important!)

Phase 4 catches structural issues by reading JSON, but misses visual problems — text that technically doesn't overlap but looks cramped, arrows that point to wrong places visually, unbalanced layout, etc. This phase uses **visual inspection** to catch those.

### How to Get a Screenshot

Pick whichever method is available in the current environment:

| Method | When to Use | How |
|--------|------------|-----|
| **Excalidraw MCP** | `mcp__claude_ai_Excalidraw__create_view` is available | Restore elements via `create_view`, the inline view IS the visual check |
| **Browser automation** | `mcp__claude-in-chrome__*` is available | Open excalidraw.com, load the file via JS, take screenshot |
| **IDE preview** | VS Code / Cursor with Excalidraw extension | `code <file>` then `screencapture` |
| **macOS Quick Look** | None of the above | `qlmanage -t -s 2000 -o /tmp/ <file>` (may not support .excalidraw) |
| **Ask the user** | All above fail | Ask user to open the file and paste a screenshot |

Use the `Read` tool on the screenshot to visually inspect. Check for:
- **Text readability** — can all labels be read? Any garbled characters?
- **Layout balance** — are modules evenly spaced? Any area too crowded?
- **Arrow routing** — do arrows go through boxes instead of around them?
- **Color coding** — are different modules visually distinguishable?
- **Completeness** — are all expected modules, states, and automations visible?

### Step 3: Fix and Re-verify

If visual issues are found:
1. Identify the problematic elements by ID (based on position/content)
2. Adjust coordinates in the element data
3. Regenerate the `.excalidraw` file
4. Re-run Phase 4 self-verification
5. Re-screenshot and inspect again

**Repeat until the diagram looks correct visually.**

> Note: if no screenshot method is available, skip this phase and rely on Phase 4. Always tell the user if visual verification was skipped.

---

## Phase 6: Deliver

1. Save `.excalidraw` to the project root (or user-specified path)
2. Report:
   - File path and size
   - Number of modules, automations, and gaps identified
   - Verification result (programmatic + visual)
3. Explain how to open: VS Code (click the file) or excalidraw.com → Open
