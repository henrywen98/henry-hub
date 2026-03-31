# Draw.io XML Specification Reference

Complete reference for generating `.drawio` diagram files with CJK support.

## Table of Contents
1. [File Structure](#structure)
2. [Color Palette](#colors)
3. [Grid & Spacing System](#grid)
4. [Shape Library](#shapes)
5. [Container / Group Patterns](#containers)
6. [Connector / Arrow Patterns](#connectors)
7. [Text & Labels](#text)
8. [Multi-Page Diagrams](#multipage)
9. [Flowchart Pattern](#flowchart)
10. [Architecture Diagram Pattern](#architecture)
11. [Layout Tips & Common Mistakes](#tips)

---

<a id="structure"></a>
## 1. File Structure

Every `.drawio` file is XML with this structure:

```xml
<mxfile host="app.diagrams.net">
  <diagram id="page1" name="页面名称">
    <mxGraphModel dx="1200" dy="800" grid="1" gridSize="10" guides="1"
                  tooltips="1" connect="1" arrows="1" fold="1" page="1"
                  pageScale="1" pageWidth="1200" pageHeight="900"
                  math="0" shadow="0">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />

        <!-- All diagram elements go here as mxCell elements -->

      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

**Key rules:**
- `mxCell id="0"` and `mxCell id="1" parent="0"` are mandatory root cells — always include them
- All visible elements have `parent="1"` (child of the default layer)
- `pageWidth` / `pageHeight` set the visible canvas size — adjust to fit content
- `dx` / `dy` control the scroll offset — use `dx` ≈ `pageWidth` and `dy` ≈ `pageHeight * 0.7` for centered view
- `gridSize="10"` means 10px snap grid; all coordinates should be multiples of 10 for clean alignment

### Element Types

Every visible element is an `<mxCell>` with a combination of attributes:

| Attribute | Purpose |
|-----------|---------|
| `id` | Unique identifier (string, must be unique across entire file) |
| `value` | Display text (supports HTML: `&lt;br&gt;` for line break, `&amp;` for &) |
| `style` | Semicolon-separated key=value pairs controlling appearance |
| `vertex="1"` | Marks this cell as a shape (node) |
| `edge="1"` | Marks this cell as a connector (arrow/line) |
| `parent` | ID of the parent cell (usually `"1"` for top-level, or a group cell ID) |
| `source` | (edges only) ID of the source vertex |
| `target` | (edges only) ID of the target vertex |

### Geometry

Every vertex has a child `<mxGeometry>` element:

```xml
<mxCell id="box1" value="标题" style="..." vertex="1" parent="1">
  <mxGeometry x="100" y="200" width="160" height="60" as="geometry" />
</mxCell>
```

Edges can also have geometry with `<Array>` points for routing:

```xml
<mxCell id="edge1" style="..." edge="1" parent="1" source="box1" target="box2">
  <mxGeometry relative="1" as="geometry">
    <Array as="points">
      <mxPoint x="300" y="400" />
    </Array>
  </mxGeometry>
</mxCell>
```

---

<a id="colors"></a>
## 2. Color Palette

draw.io uses a built-in color theme system. These are the standard themed fills that render cleanly:

### Built-in Theme Colors (recommended)

| Theme | Fill | Stroke | Usage |
|-------|------|--------|-------|
| Blue | `#dae8fc` | `#6c8ebf` | Primary flow, core modules, agents |
| Green | `#d5e8d4` | `#82b366` | Success, data stores, completed states |
| Yellow | `#fff2cc` | `#d6b656` | User actions, decisions, highlights |
| Orange | `#ffd8a8` | `#d79b00` | Warnings, secondary processes |
| Red | `#f8cecc` | `#b85450` | Errors, failures, critical paths |
| Purple | `#e1d5e7` | `#9673a6` | Data stores, databases, storage |
| Light Gray | `#f5f5f5` | `#666666` | Containers, groups, backgrounds |

### Neutral Colors

| Name | Hex | Usage |
|------|-----|-------|
| White | `#ffffff` | Default background |
| Light Gray BG | `#f5f5f5` | Group/container background |
| Dark Text | `#1a1a2e` | Title text |
| Medium Text | `#333333` | Body text |
| Muted Text | `#666666` | Annotations, secondary info |

### Usage Rules
- Use themed fill+stroke pairs together (they're designed to match)
- Max 4-5 colors per diagram to keep it readable
- Use Light Gray for container/group backgrounds
- Use Yellow for user actions / decision points
- Containers: use the fill color with low opacity or `#f5f5f5`

---

<a id="grid"></a>
## 3. Grid & Spacing System

All positions and sizes should be multiples of 10px (matching `gridSize="10"`).

### Spacing Constants

| Constant | Value | Usage |
|----------|-------|-------|
| `NODE_W` | 160px | Default node width |
| `NODE_H` | 50-60px | Default node height |
| `NODE_GAP_V` | 60px | Vertical gap between nodes |
| `NODE_GAP_H` | 80px | Horizontal gap between nodes |
| `GROUP_PAD` | 30px | Padding inside container groups |
| `GROUP_GAP` | 40px | Gap between groups |
| `ARROW_LABEL_OFFSET` | 10px | Offset for labels on arrows |

### Calculating Positions

For a vertical flowchart with N nodes:
```
node[i].x = center_x - NODE_W/2
node[i].y = start_y + i * (NODE_H + NODE_GAP_V)
pageHeight = start_y + N * NODE_H + (N-1) * NODE_GAP_V + 80
```

For horizontal layout with N nodes:
```
node[i].x = start_x + i * (NODE_W + NODE_GAP_H)
node[i].y = center_y - NODE_H/2
pageWidth = start_x + N * NODE_W + (N-1) * NODE_GAP_H + 80
```

---

<a id="shapes"></a>
## 4. Shape Library

### Process / Step (rounded rectangle) — most common
```xml
<mxCell id="step1" value="处理步骤" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=13;" vertex="1" parent="1">
  <mxGeometry x="100" y="200" width="160" height="50" as="geometry" />
</mxCell>
```

### Start / End (stadium / pill shape)
```xml
<mxCell id="start" value="开始" style="rounded=1;whiteSpace=wrap;html=1;arcSize=50;fillColor=#d5e8d4;strokeColor=#82b366;fontSize=13;fontStyle=1;" vertex="1" parent="1">
  <mxGeometry x="100" y="40" width="120" height="40" as="geometry" />
</mxCell>
```
`arcSize=50` creates full pill shape.

### Decision (diamond / rhombus)
```xml
<mxCell id="decision1" value="条件判断?" style="rhombus;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;fontSize=12;fontStyle=1;" vertex="1" parent="1">
  <mxGeometry x="100" y="200" width="130" height="80" as="geometry" />
</mxCell>
```

### Database (cylinder)
```xml
<mxCell id="db1" value="PostgreSQL" style="shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=10;fillColor=#e1d5e7;strokeColor=#9673a6;fontSize=12;" vertex="1" parent="1">
  <mxGeometry x="100" y="200" width="120" height="60" as="geometry" />
</mxCell>
```

### Document
```xml
<mxCell id="doc1" value="需求文档" style="shape=document;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=0.27;fillColor=#fff2cc;strokeColor=#d6b656;fontSize=12;" vertex="1" parent="1">
  <mxGeometry x="100" y="200" width="140" height="50" as="geometry" />
</mxCell>
```

### Parallelogram (input/output)
```xml
<mxCell id="io1" value="用户输入" style="shape=parallelogram;perimeter=parallelogramPerimeter;whiteSpace=wrap;html=1;fixedSize=1;fillColor=#fff2cc;strokeColor=#d6b656;fontSize=13;" vertex="1" parent="1">
  <mxGeometry x="100" y="200" width="180" height="50" as="geometry" />
</mxCell>
```

### Multi-document
```xml
<mxCell id="docs1" value="多个文档" style="shape=mxgraph.flowchart.multi-document;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontSize=12;" vertex="1" parent="1">
  <mxGeometry x="100" y="200" width="150" height="60" as="geometry" />
</mxCell>
```

### Plain Text (no border)
```xml
<mxCell id="note1" value="注释文本" style="text;html=1;align=left;verticalAlign=top;fillColor=none;strokeColor=none;fontSize=10;fontColor=#666666;" vertex="1" parent="1">
  <mxGeometry x="100" y="200" width="200" height="60" as="geometry" />
</mxCell>
```

### Swimlane Header
```xml
<mxCell id="lane1" value="客户端" style="shape=table;startSize=30;container=1;collapsible=0;childLayout=tableLayout;strokeColor=#6c8ebf;fillColor=#dae8fc;fontSize=14;fontStyle=1;" vertex="1" parent="1">
  <mxGeometry x="100" y="40" width="200" height="600" as="geometry" />
</mxCell>
```

---

<a id="containers"></a>
## 5. Container / Group Patterns

### Dashed container with external label (recommended for architecture diagrams)

When arrows cross between layers, a label inside the container's `value` attribute sits right where arrows pass through. To avoid this, use an **empty container + separate text element** for the label:

```xml
<!-- Container (no value — label is external) -->
<mxCell id="group1" value="" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f5f5f5;strokeColor=#666666;dashed=1;dashPattern=5 5;" vertex="1" parent="1">
  <mxGeometry x="100" y="80" width="600" height="120" as="geometry" />
</mxCell>
<!-- Label to the LEFT of container, outside arrow paths -->
<mxCell id="group1_label" value="服务层" style="text;html=1;align=right;verticalAlign=middle;fillColor=none;strokeColor=none;fontSize=13;fontStyle=1;fontColor=#666666;" vertex="1" parent="1">
  <mxGeometry x="20" y="110" width="70" height="30" as="geometry" />
</mxCell>
```

This keeps the label completely clear of any arrows entering or leaving the container.

### Dashed container with inline label (for flowcharts / non-layered diagrams)

When arrows don't typically cross through the container top (e.g., flowchart groups), an inline label is fine:

```xml
<mxCell id="group1" value="Phase 1: 需求分析" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f5f5f5;strokeColor=#666666;fontStyle=1;fontSize=14;verticalAlign=top;spacingTop=5;dashed=1;dashPattern=5 5;" vertex="1" parent="1">
  <mxGeometry x="60" y="80" width="300" height="200" as="geometry" />
</mxCell>
```
Key style properties:
- `verticalAlign=top` — label at top
- `spacingTop=5` — padding for label
- `dashed=1;dashPattern=5 5` — dashed border
- Child elements use `parent="group1"` OR just place them visually inside with `parent="1"`

### Solid container
Same as above but without `dashed=1;dashPattern=5 5`.

### Colored container (for emphasis)
```xml
<mxCell id="group2" value="核心模块" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontStyle=1;fontSize=14;verticalAlign=top;spacingTop=5;opacity=30;" vertex="1" parent="1">
  <mxGeometry x="60" y="80" width="300" height="200" as="geometry" />
</mxCell>
```
`opacity=30` makes it a subtle background.

---

<a id="connectors"></a>
## 6. Connector / Arrow Patterns

### Connection Point Control (IMPORTANT)

By default, draw.io auto-routes arrows from center-to-center, which causes arrows to cross over other elements' text. Always use `exitX`, `exitY`, `entryX`, `entryY` to control exactly which edge of a shape the arrow leaves from and arrives at:

```
exitX/entryX: 0 = left edge, 0.5 = center, 1 = right edge
exitY/entryY: 0 = top edge, 0.5 = center, 1 = bottom edge
```

Example — arrow leaves from bottom-center of source, enters top-center of target:
```xml
<mxCell id="e1" style="edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;exitX=0.5;exitY=1;exitDx=0;exitDy=0;entryX=0.5;entryY=0;entryDx=0;entryDy=0;strokeColor=#333333;strokeWidth=2;" edge="1" parent="1" source="box1" target="box2">
  <mxGeometry relative="1" as="geometry" />
</mxCell>
```

**When to use specific exit/entry points:**
- **Vertical flow** (top-to-bottom): `exitX=0.5;exitY=1` (bottom) → `entryX=0.5;entryY=0` (top)
- **Horizontal flow** (left-to-right): `exitX=1;exitY=0.5` (right) → `entryX=0;entryY=0.5` (left)
- **Diagonal / cross-layer**: use the edge closest to the target to minimize crossing other elements
- **Multiple arrows from same node**: spread exit points (e.g., `exitX=0.25`, `exitX=0.5`, `exitX=0.75`) to avoid overlap

### Arrow-Text Collision Avoidance

This is the most common visual quality issue. Arrows that cross through other nodes' text make diagrams hard to read.

**Prevention strategies:**
1. **Use `rounded=1`** in edge style — curved routing avoids sharp overlaps
2. **Specify exit/entry points** on the nearest edges — prevents long horizontal runs through text
3. **Use waypoints** to route around crowded areas (see "Arrow with waypoints" below)
4. **Increase layer spacing** — if arrows between layers cross other nodes, the layers are too close. Use ≥ 80px gap between layer groups
5. **Fan-out pattern**: when one node connects to multiple targets in a row, use spread exit points instead of all leaving from the same point

**Bad pattern** — three services all connecting to same database via auto-route:
```
[SvcA]   [SvcB]   [SvcC]      ← arrows from center of each
   \       |       /           ← cross through each other's text
    \      |      /
       [Database]
```

**Good pattern** — use exit/entry points to create clean vertical drops:
```
[SvcA]   [SvcB]   [SvcC]      ← each arrow exits bottom-center
   |       |       |           ← clean parallel lines, no crossing
   ↓       ↓       ↓
       [Database]              ← entry at top: entryX=0.25, 0.5, 0.75
```

### Basic arrow (connected to source and target)
```xml
<mxCell id="e1" style="edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;exitX=0.5;exitY=1;exitDx=0;exitDy=0;entryX=0.5;entryY=0;entryDx=0;entryDy=0;strokeColor=#333333;strokeWidth=2;" edge="1" parent="1" source="box1" target="box2">
  <mxGeometry relative="1" as="geometry" />
</mxCell>
```
`orthogonalEdgeStyle` creates right-angle routing. `rounded=1` softens corners. Always include `exitX/Y` and `entryX/Y` for predictable routing.

### Arrow with label
```xml
<mxCell id="e2" value="通过" style="edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;strokeColor=#82b366;strokeWidth=2;fontSize=10;fontColor=#82b366;" edge="1" parent="1" source="decision1" target="next1">
  <mxGeometry relative="1" as="geometry" />
</mxCell>
```

### Straight arrow (no routing)
```xml
<mxCell id="e3" style="html=1;strokeColor=#333333;strokeWidth=2;" edge="1" parent="1" source="a" target="b">
  <mxGeometry relative="1" as="geometry" />
</mxCell>
```

### Dashed arrow (optional / async flow)
```xml
<mxCell id="e4" style="edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;strokeColor=#666666;strokeWidth=1;dashed=1;" edge="1" parent="1" source="a" target="b">
  <mxGeometry relative="1" as="geometry" />
</mxCell>
```

### Thick arrow (main flow emphasis)
```xml
<mxCell id="e5" style="edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;strokeColor=#333333;strokeWidth=3;" edge="1" parent="1" source="a" target="b">
  <mxGeometry relative="1" as="geometry" />
</mxCell>
```

### Arrow with waypoints (custom routing)
When auto-routing would cross through other elements, manually specify intermediate points to route around them:
```xml
<mxCell id="e6" style="edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;strokeColor=#333333;strokeWidth=2;" edge="1" parent="1" source="a" target="b">
  <mxGeometry relative="1" as="geometry">
    <Array as="points">
      <mxPoint x="500" y="300" />
      <mxPoint x="500" y="500" />
    </Array>
  </mxGeometry>
</mxCell>
```

### Unconnected arrow (free-floating)
When source or target is not a shape, use `mxPoint` for endpoints:
```xml
<mxCell id="e7" style="html=1;strokeColor=#333333;strokeWidth=2;endArrow=block;endFill=1;" edge="1" parent="1">
  <mxGeometry relative="1" as="geometry">
    <mxPoint x="100" y="200" as="sourcePoint" />
    <mxPoint x="300" y="200" as="targetPoint" />
  </mxGeometry>
</mxCell>
```

---

<a id="text"></a>
## 7. Text & Labels

### Text formatting in `value` attribute
- Line break: `&#xa;` (in non-HTML mode) or `&lt;br&gt;` (in HTML mode with `html=1`)
- Bold: set `fontStyle=1` in style
- Italic: set `fontStyle=2`
- Bold+Italic: set `fontStyle=3`
- HTML entities: `&amp;` for &, `&lt;` for <, `&gt;` for >

### Font sizes by role

| Role | Size | Weight |
|------|------|--------|
| Diagram title | 18-22px | Bold (`fontStyle=1`) |
| Group/container label | 14px | Bold |
| Node label | 12-13px | Normal or Bold |
| Annotation / note | 10-11px | Normal |
| Arrow label | 10px | Normal |

### Chinese text
Chinese text works natively in draw.io — no special font-family needed. The renderer uses the system's default CJK font. Just put Chinese characters directly in the `value` attribute.

### Multi-line text
```xml
value="第一行&#xa;第二行&#xa;第三行"
```
Or with HTML:
```xml
value="第一行&lt;br&gt;第二行"
```

### Text alignment in style
- `align=center` (horizontal: left/center/right)
- `verticalAlign=middle` (vertical: top/middle/bottom)
- `whiteSpace=wrap` — enable word wrapping within shape bounds

---

<a id="multipage"></a>
## 8. Multi-Page Diagrams

draw.io supports multiple pages (tabs) in a single file. Each page is a separate `<diagram>` element:

```xml
<mxfile host="app.diagrams.net">
  <diagram id="overview" name="全景总览">
    <mxGraphModel ...>
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
        <!-- Overview elements -->
      </root>
    </mxGraphModel>
  </diagram>

  <diagram id="sales" name="销售模块">
    <mxGraphModel ...>
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
        <!-- Sales module detail elements -->
      </root>
    </mxGraphModel>
  </diagram>

  <diagram id="purchase" name="采购模块">
    <mxGraphModel ...>
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
        <!-- Purchase module detail elements -->
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

**Key rules for multi-page:**
- Each `<diagram>` gets its own `<mxGraphModel>` and `<root>` with fresh `id="0"` and `id="1"` cells
- Element IDs only need to be unique within a page, not across pages
- `name` attribute appears as the tab name in draw.io
- First `<diagram>` is the default page shown on open
- For panorama pattern: page 1 shows high-level modules as **rich boxes** (title + key descriptions inside), subsequent pages detail each module's state machines and flows

### Panorama Page Design Rules

The overview/panorama page is the most important page — it must convey the full business picture at a glance.

**Module boxes should be RICH, not empty:**
Each module box on the panorama should include:
- Module title (bold, colored)
- 1-line subtitle describing the module's role
- Key state flow summary (e.g., "审批 → 采购 → 提货 → 入库 → 发货 → 完成")
- Key business rules (e.g., "自动完成: 发货中+单证齐全+收款≥90%")
- Use `whiteSpace=wrap;html=1` and HTML line breaks (`<br>`) for multi-line content

**Box sizing:** Rich module boxes need to be large enough for their content. Minimum 250x150 for boxes with 4+ lines of text. Calculate: ~20px per line of text at fontSize=11.

**Arrow rules between modules:**
- **Minimum arrow length: 80px** — if boxes are too close, arrows become invisible under labels
- Arrow labels should be SHORT (1-3 characters like "入库", "出库", "审批通过") not full sentences
- For long labels, place them as separate text elements near the arrow, not as the arrow's `value`
- **Horizontal gap between module boxes: ≥ 100px** to leave room for visible arrows + labels

### Visual Legend Pattern

Legends should use **actual line/shape graphics**, not text descriptions. Build the legend from real draw.io elements:

```xml
<!-- Legend container -->
<mxCell id="legend_box" value="" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f5f5f5;strokeColor=#999999;dashed=1;dashPattern=5 5;" vertex="1" parent="1">
  <mxGeometry x="20" y="560" width="280" height="80" as="geometry" />
</mxCell>
<mxCell id="legend_title" value="图例" style="text;html=1;align=left;verticalAlign=middle;fillColor=none;strokeColor=none;fontSize=12;fontStyle=1;" vertex="1" parent="1">
  <mxGeometry x="30" y="565" width="40" height="20" as="geometry" />
</mxCell>

<!-- Legend item 1: solid arrow = main flow -->
<mxCell id="leg1_line" style="html=1;strokeColor=#333333;strokeWidth=2;endArrow=block;endFill=1;" edge="1" parent="1">
  <mxGeometry relative="1" as="geometry">
    <mxPoint x="30" y="600" as="sourcePoint" />
    <mxPoint x="80" y="600" as="targetPoint" />
  </mxGeometry>
</mxCell>
<mxCell id="leg1_text" value="主业务流程" style="text;html=1;align=left;verticalAlign=middle;fillColor=none;strokeColor=none;fontSize=10;fontColor=#666666;" vertex="1" parent="1">
  <mxGeometry x="85" y="590" width="70" height="20" as="geometry" />
</mxCell>

<!-- Legend item 2: dashed arrow = automation/feedback -->
<mxCell id="leg2_line" style="html=1;strokeColor=#b85450;strokeWidth=2;dashed=1;endArrow=block;endFill=1;" edge="1" parent="1">
  <mxGeometry relative="1" as="geometry">
    <mxPoint x="30" y="625" as="sourcePoint" />
    <mxPoint x="80" y="625" as="targetPoint" />
  </mxGeometry>
</mxCell>
<mxCell id="leg2_text" value="系统自动联动" style="text;html=1;align=left;verticalAlign=middle;fillColor=none;strokeColor=none;fontSize=10;fontColor=#666666;" vertex="1" parent="1">
  <mxGeometry x="85" y="615" width="80" height="20" as="geometry" />
</mxCell>
```

**Legend rules:**
- Always use actual draw.io edge/shape elements to illustrate each style, not text
- Place in bottom-left corner, outside the main diagram flow
- Include all line styles used in the diagram (solid, dashed, colors)
- Keep it compact: 2-4 items max

---

<a id="flowchart"></a>
## 9. Flowchart Pattern

Complete working example — a simple approval flow:

```xml
<mxfile host="app.diagrams.net">
  <diagram id="flow1" name="审批流程">
    <mxGraphModel dx="800" dy="600" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="800" pageHeight="600" math="0" shadow="0">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />

        <!-- 开始 -->
        <mxCell id="start" value="提交申请" style="rounded=1;whiteSpace=wrap;html=1;arcSize=50;fillColor=#d5e8d4;strokeColor=#82b366;fontSize=13;fontStyle=1;" vertex="1" parent="1">
          <mxGeometry x="300" y="40" width="120" height="40" as="geometry" />
        </mxCell>

        <!-- 审批节点 -->
        <mxCell id="review" value="主管审批" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=13;" vertex="1" parent="1">
          <mxGeometry x="280" y="130" width="160" height="50" as="geometry" />
        </mxCell>

        <!-- 判断 -->
        <mxCell id="decision" value="是否通过?" style="rhombus;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;fontSize=12;fontStyle=1;" vertex="1" parent="1">
          <mxGeometry x="295" y="230" width="130" height="80" as="geometry" />
        </mxCell>

        <!-- 通过 -->
        <mxCell id="approved" value="执行任务" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontSize=13;" vertex="1" parent="1">
          <mxGeometry x="480" y="245" width="140" height="50" as="geometry" />
        </mxCell>

        <!-- 驳回 -->
        <mxCell id="rejected" value="退回修改" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f8cecc;strokeColor=#b85450;fontSize=13;" vertex="1" parent="1">
          <mxGeometry x="100" y="245" width="140" height="50" as="geometry" />
        </mxCell>

        <!-- 结束 -->
        <mxCell id="end" value="完成" style="rounded=1;whiteSpace=wrap;html=1;arcSize=50;fillColor=#d5e8d4;strokeColor=#82b366;fontSize=13;fontStyle=1;" vertex="1" parent="1">
          <mxGeometry x="510" y="350" width="80" height="40" as="geometry" />
        </mxCell>

        <!-- 连接线 -->
        <mxCell id="e1" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor=#333333;strokeWidth=2;" edge="1" parent="1" source="start" target="review">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="e2" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor=#333333;strokeWidth=2;" edge="1" parent="1" source="review" target="decision">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="e3" value="通过" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor=#82b366;strokeWidth=2;fontSize=10;fontColor=#82b366;" edge="1" parent="1" source="decision" target="approved">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="e4" value="驳回" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor=#b85450;strokeWidth=2;fontSize=10;fontColor=#b85450;" edge="1" parent="1" source="decision" target="rejected">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="e5" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor=#333333;strokeWidth=2;" edge="1" parent="1" source="approved" target="end">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <!-- 退回 → 重新提交 -->
        <mxCell id="e6" value="修改后重新提交" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor=#666666;strokeWidth=1;dashed=1;fontSize=10;fontColor=#666666;" edge="1" parent="1" source="rejected" target="start">
          <mxGeometry relative="1" as="geometry">
            <Array as="points">
              <mxPoint x="170" y="40" />
            </Array>
          </mxGeometry>
        </mxCell>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

---

<a id="architecture"></a>
## 10. Architecture Diagram Pattern

Layout strategy for layered architecture:
```
Row 0 (y=40):   Title

Row 1 (y=80):   ┌─ 客户端层 ─────────────────────────────┐
                 │  [浏览器]      [移动端]      [API调用]   │
                 └──────────────────────────────────────────┘
                        ↓
Row 2 (y=260):  ┌─ 服务层 ────────────────────────────────┐
                │  [API网关]    [认证服务]    [业务服务]     │
                └──────────────────────────────────────────┘
                        ↓
Row 3 (y=440):  ┌─ 数据层 ────────────────────────────────┐
                │  [PostgreSQL]    [Redis]    [S3]          │
                └──────────────────────────────────────────┘
```

Steps:
1. Draw container groups first (dashed, light gray fill)
2. Place nodes inside containers, evenly spaced horizontally
3. Draw arrows between layers last
4. Container labels at top-left using `verticalAlign=top`

Tip: For N nodes in a container of width W, each node's x = `container_x + GROUP_PAD + i * ((W - 2*GROUP_PAD) / N)`

### Architecture Diagram Connection Pattern (IMPORTANT)

Architecture diagrams have **many-to-many connections** between layers. Use `edgeStyle=orthogonalEdgeStyle` (user-preferred aesthetic), but carefully manage exit/entry points to prevent overlap.

**Key rules for architecture arrows:**
1. **Container labels must be external** (see "Dashed container with external label" above) — if the label is inline at the top of a container, arrows entering from above will cross through it
2. **Fan out exit/entry points** so parallel arrows don't share the same path
3. **Use `rounded=1`** for softer corners at bends

**Fan-out pattern for many-to-many connections:**
When 3 services each connect to 2 databases (6 lines), stagger both exit and entry points:
```
Service A      Service B      Service C
exitX=0.35     exitX=0.35     exitX=0.35      ← DB connections exit left-of-center
exitX=0.65     exitX=0.65     exitX=0.65      ← Cache connections exit right-of-center
     |    \       |    |       /    |
     ↓     \      ↓    ↓      /     ↓
 entryX=    \  entryX= entryX=  /  entryX=
  0.25       \  0.5    0.5    /     0.75
    [PostgreSQL]            [Redis]
```

Spread `entryX` across the target (0.25, 0.5, 0.75) so arrows arrive at different points instead of all converging on center.

---

<a id="tips"></a>
## 11. Layout Tips & Common Mistakes

### DO
- Set `pageWidth`/`pageHeight` based on content before writing elements
- Use `edgeStyle=orthogonalEdgeStyle;rounded=1` for clean routing with soft corners
- **Always specify `exitX/Y` and `entryX/Y`** on edges to prevent arrows crossing through text
- Use `rounded=1` on edges — curved routing avoids sharp overlaps at intersections
- Use consistent colors within a module — same fill+stroke pair
- Keep `strokeWidth` consistent: 2px for main arrows, 1px for secondary
- Use `dashed=1` for optional/async flows
- Test that `value` text fits within `width` × `height` — Chinese characters are ~14px wide at fontSize=13
- For text with `&#xa;` line breaks, increase element `height` by ~20px per line
- **Leave ≥ 80px vertical gap** between layer groups so arrows have room to route
- **Fan out connection points** when multiple arrows leave/enter the same node (spread `exitX` values)

### DON'T
- **Don't omit `exitX/Y` and `entryX/Y`** — without them, arrows auto-route from center and cross through other nodes' text
- Don't use `fontFamily` in style unless you have a specific reason — draw.io default CJK font works well
- Don't make shapes too small for their text (min 120x40 for 4-char Chinese label)
- Don't use more than 5 colors per diagram
- Don't forget `id="0"` and `id="1" parent="0"` root cells (file won't open without them)
- Don't reuse IDs across elements within the same page
- Don't place all arrows before shapes — interleave them for readability in XML
- Don't use `shadow=1` in the mxGraphModel unless the user specifically wants it
- **Don't connect distant nodes across a row without waypoints** — the horizontal segment will cross through intermediate nodes

### Edge Alignment
When auto-routing doesn't place arrows well, use the `Array as="points"` pattern to manually route:
- For L-shaped routes: one waypoint
- For U-shaped routes: two waypoints
- For complex routing around obstacles: three or more waypoints

### Handling Large Diagrams (>30 nodes)
When a diagram gets complex:
1. Split into multi-page (see Section 8)
2. Page 1: overview with modules as single boxes
3. Subsequent pages: detail per module
4. Use consistent element IDs across pages for traceability (e.g., `sales_overview` on page 1, detail on page 2 named "销售模块")
5. Reduce node sizes for dense pages (140x40 instead of 160x50)
6. Use smaller font (11-12px) for detail pages
