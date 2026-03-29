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
Phase 3: Generate Excalidraw Elements
    |
Phase 4: Automated Verification Loop
    |
Phase 5: Deliver .excalidraw file
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

## Phase 3: Generate Excalidraw Elements

Use the bundled converter script at: `${CLAUDE_PLUGIN_ROOT}/skills/business-flow-diagram/scripts/gen_excalidraw.py`

### Usage Pattern

Create a wrapper script (e.g., `/tmp/diagram_data.py`) that defines elements and calls the converter:

```python
import sys
sys.path.insert(0, "${CLAUDE_PLUGIN_ROOT}/skills/business-flow-diagram/scripts")
from gen_excalidraw import convert_and_save

elements = [
    # Zone background (draw first)
    {"type":"rectangle","id":"zone1","x":20,"y":70,"width":440,"height":520,
     "backgroundColor":"#dbe4ff","fillStyle":"solid","roundness":{"type":3},
     "strokeColor":"#4a9eed","strokeWidth":1,"opacity":35},
    # Zone title
    {"type":"text","id":"z1t","x":32,"y":78,"text":"销售管理",
     "fontSize":20,"strokeColor":"#2563eb"},
    # State box with label
    {"type":"rectangle","id":"s1","x":45,"y":150,"width":105,"height":42,
     "backgroundColor":"#a5d8ff","fillStyle":"solid","roundness":{"type":3},
     "strokeColor":"#4a9eed","label":{"text":"草稿","fontSize":15}},
    # Arrow between states
    {"type":"arrow","id":"a1","x":150,"y":171,"width":25,"height":0,
     "points":[[0,0],[25,0]],"strokeColor":"#4a9eed","strokeWidth":2,
     "endArrowhead":"arrow"},
]

convert_and_save(elements, "业务流程全景图.excalidraw")
```

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

## Phase 4: Automated Verification

Run the bundled verification script: `${CLAUDE_PLUGIN_ROOT}/skills/business-flow-diagram/scripts/verify_excalidraw.py`

```bash
python verify_excalidraw.py <output.excalidraw>
```

It checks 5 things:
1. **Encoding** — no corrupted characters (U+FFFD)
2. **Font** — all text uses fontFamily 2 (CJK-compatible sans-serif)
3. **Tech terms** — no code terminology in displayed text
4. **Overlaps** — no elements overlapping >30% area
5. **Overflow** — no bound text wider than its container

**If verification fails**, fix the issue and regenerate:
- Corrupted chars → use `\uXXXX` unicode escapes
- Tech terms → replace with business equivalents
- Overlaps → adjust coordinates to add spacing
- Overflow → widen container or shorten label

**Repeat until all checks pass.**

---

## Phase 5: Deliver

1. Save `.excalidraw` to the project root (or user-specified path)
2. Report: file path, module count, automation count, gap count, verification result
3. Explain: open at excalidraw.com → Open → select file → Export as PNG/SVG
