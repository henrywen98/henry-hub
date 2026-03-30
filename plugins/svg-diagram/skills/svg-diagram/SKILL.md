---
name: svg-diagram
description: >
  Generate high-quality SVG diagrams including flowcharts, architecture diagrams, system diagrams,
  sequence flows, and technical illustrations. Use this skill whenever the user asks to create,
  draw, or visualize any kind of diagram, flowchart, architecture overview, system design,
  process flow, or technical illustration as SVG. Also trigger when the user says "画一个图",
  "流程图", "架构图", "示意图", "系统图", "拓扑图", or any request involving visual representation
  of processes, systems, or relationships. Even if the user just says "帮我画个图" or "visualize this",
  use this skill. Outputs clean, minimal-style SVG files with full CJK (Chinese/Japanese/Korean) text support.
---

# SVG Diagram Generator

Generate professional, minimal-style SVG diagrams with Chinese text support.

## Quick Start

1. Read the user's request and identify the diagram type
2. Consult `references/svg-spec.md` for element syntax, layout rules, and color palette
3. Build the SVG following the patterns below
4. Save the `.svg` file and present to the user

## Diagram Types

### Flowchart (流程图)
- Top-to-bottom or left-to-right flow
- Rounded rectangles for process steps, diamonds for decisions, rounded pills for start/end
- Connectors with arrowheads using `<marker>` definitions

### Architecture Diagram (架构图)
- Layered layout: top = user/client, middle = services, bottom = data/infra
- Group related components in dashed-border containers with labels
- Use icons or simple shapes to represent services, databases, queues, etc.

### System Topology (系统拓扑图)
- Nodes as rounded rectangles or circles
- Lines/arrows showing data flow or dependencies
- Labels on connections describing protocols or data types

### Sequence / Swimlane (时序图 / 泳道图)
- Vertical lifelines for each actor/system
- Horizontal arrows for messages, dashed arrows for responses
- Activation boxes on lifelines during processing

## Core Principles

1. **Minimal is beautiful** — Use thin strokes (1-2px), generous whitespace, muted colors. No gradients, no shadows, no 3D effects.
2. **Alignment is king** — Every element must sit on a logical grid. Use consistent spacing (multiples of 20px).
3. **Chinese text must work** — Always specify `font-family="'PingFang SC', 'Microsoft YaHei', 'Noto Sans SC', sans-serif"` for CJK text.
4. **Readable at any size** — Minimum font size 12px. Keep text concise inside shapes.
5. **Self-contained** — No external dependencies. All styles, markers, and defs inline.

## Before Writing Any SVG Code

**Always read `references/svg-spec.md` first.** It contains the complete element reference, color palette, layout grid system, arrow/marker definitions, and reusable patterns. This is essential for producing consistent, high-quality output.

## Output Rules

- Default canvas: `viewBox="0 0 800 600"` (adjust as needed for content)
- Add `xmlns="http://www.w3.org/2000/svg"` to root `<svg>` element
- Use `<defs>` block for reusable markers, filters, and gradients
- Group logical sections with `<g>` and use `transform="translate(x,y)"` for positioning
- File extension: `.svg`

## Workflow

```
1. Identify diagram type and content from user request
2. Read references/svg-spec.md for syntax and patterns
3. Plan layout on paper:
   - List all nodes/elements
   - Determine hierarchy and flow direction
   - Calculate grid positions (snap to 20px grid)
4. Write SVG:
   - <defs> block first (markers, patterns)
   - Background groups (containers, lanes)
   - Node shapes with text
   - Connectors/arrows last (so they render on top)
5. Review alignment and spacing
6. Save and present
```
