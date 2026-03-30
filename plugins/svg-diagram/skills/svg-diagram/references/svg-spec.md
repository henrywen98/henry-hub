# SVG Diagram Specification Reference

Complete reference for generating minimal-style SVG diagrams with CJK support.

## Table of Contents
1. [Canvas & Boilerplate](#canvas)
2. [Color Palette](#colors)
3. [Typography](#typography)
4. [Grid & Spacing System](#grid)
5. [Arrow & Marker Definitions](#markers)
6. [Shape Library](#shapes)
7. [Container / Group Patterns](#containers)
8. [Connector Patterns](#connectors)
9. [Flowchart Pattern](#flowchart)
10. [Architecture Diagram Pattern](#architecture)
11. [Sequence Diagram Pattern](#sequence)
12. [Layout Tips & Common Mistakes](#tips)

---

<a id="canvas"></a>
## 1. Canvas & Boilerplate

Every SVG must start with this structure:

```xml
<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <!-- markers, patterns, reusable elements -->
  </defs>

  <!-- diagram content -->
</svg>
```

Default sizes by diagram type:
- Flowchart (vertical): `viewBox="0 0 600 800"` or taller
- Flowchart (horizontal): `viewBox="0 0 1000 500"`
- Architecture diagram: `viewBox="0 0 900 650"`
- Sequence diagram: `viewBox="0 0 800 600"` or taller

Adjust width/height to fit content — never let elements overflow the viewBox. Add 40px padding on all sides.

---

<a id="colors"></a>
## 2. Color Palette

Minimal palette — use sparingly. Most of the diagram should be `#333` strokes on white.

### Primary (for nodes and shapes)
| Name         | Hex       | Usage                          |
|-------------|-----------|--------------------------------|
| Charcoal    | `#333333` | Default stroke, text           |
| Slate       | `#5C6670` | Secondary text, annotations    |
| Cloud       | `#F5F7FA` | Default shape fill             |
| White       | `#FFFFFF` | Background, alternate fill     |

### Accent (use ONE per diagram for emphasis, two max)
| Name         | Hex       | Usage                          |
|-------------|-----------|--------------------------------|
| Blue        | `#4A90D9` | Primary flow, key components   |
| Teal        | `#2BA5A5` | Secondary system, services     |
| Coral       | `#E8734A` | Warning, error, highlight      |
| Violet      | `#7B68EE` | AI/ML components, special      |
| Green       | `#5CB85C` | Success, data stores, stable   |

### Accent fills (light backgrounds for containers)
Derive from accent by using 10-15% opacity:
- Blue container: `#4A90D9` with `opacity="0.08"` → or use `#EBF2FB`
- Teal container: `#2BA5A5` with `opacity="0.08"` → or use `#E8F6F6`
- Coral container: `#E8734A` with `opacity="0.08"` → or use `#FDEFEA`
- Violet container: `#7B68EE` with `opacity="0.08"` → or use `#EEEAFD`
- Green container: `#5CB85C` with `opacity="0.08"` → or use `#EDF7ED`

### Rule of thumb
- Most shapes: `fill="#F5F7FA" stroke="#333333"`
- One accent color for the "main" flow or highlighted path
- A second accent only if showing contrast (e.g., old vs new, success vs error)

---

<a id="typography"></a>
## 3. Typography

### Font Stack (CJK-safe)
Always use this font-family for ALL text elements:
```
font-family="'PingFang SC', 'Microsoft YaHei', 'Noto Sans SC', 'Helvetica Neue', Arial, sans-serif"
```

### Sizes
| Role              | Size   | Weight | Color     |
|-------------------|--------|--------|-----------|
| Diagram title     | 18px   | 600    | `#333333` |
| Node label        | 14px   | 500    | `#333333` |
| Sublabel / desc   | 12px   | 400    | `#5C6670` |
| Connector label   | 11px   | 400    | `#5C6670` |
| Annotation        | 10px   | 400    | `#5C6670` |

### Text in shapes
- Always use `text-anchor="middle"` and `dominant-baseline="central"` for centered text
- For multi-line text in shapes, use multiple `<tspan>` elements with `dy` offsets:
```xml
<text x="100" y="40" text-anchor="middle" font-family="..." font-size="14" fill="#333">
  <tspan x="100" dy="0">第一行</tspan>
  <tspan x="100" dy="18">第二行</tspan>
</text>
```
- If label is long, break at natural points (Chinese: every 4-6 chars; English: word boundary)
- Center the text block vertically: offset the first tspan by `-((lineCount-1) * lineHeight / 2)`

### CJK character width
Chinese characters are roughly 1em wide each. A 14px font means each character ≈ 14px wide. For a shape that's 120px wide (with 16px horizontal padding on each side → 88px text area), that fits about 6 Chinese characters per line. Plan shape widths accordingly.

---

<a id="grid"></a>
## 4. Grid & Spacing System

Use a 20px base grid. All positions and sizes should be multiples of 20px (or 10px for fine adjustments).

### Spacing constants
| Constant              | Value  | Usage                                    |
|-----------------------|--------|------------------------------------------|
| `PADDING`             | 40px   | Canvas edge padding                      |
| `NODE_W`              | 160px  | Default node width                       |
| `NODE_H`              | 60px   | Default node height                      |
| `NODE_H_SMALL`        | 40px   | Compact node height                      |
| `NODE_GAP_V`          | 60px   | Vertical gap between nodes               |
| `NODE_GAP_H`          | 80px   | Horizontal gap between nodes             |
| `CONTAINER_PAD`       | 20px   | Padding inside container groups           |
| `CONTAINER_GAP`       | 40px   | Gap between containers                   |
| `ARROW_GAP`           | 8px    | Gap between shape edge and arrow start   |
| `CORNER_R`            | 8px    | Default corner radius for rectangles     |
| `DECISION_SIZE`       | 60px   | Diamond half-diagonal                    |

### Calculating positions
For a vertical flowchart with N nodes:
```
node[i].x = canvas_center_x - NODE_W/2
node[i].y = PADDING + i * (NODE_H + NODE_GAP_V)
canvas_height = PADDING*2 + N * NODE_H + (N-1) * NODE_GAP_V
```

For a horizontal layout with N nodes:
```
node[i].x = PADDING + i * (NODE_W + NODE_GAP_H)
node[i].y = canvas_center_y - NODE_H/2
canvas_width = PADDING*2 + N * NODE_W + (N-1) * NODE_GAP_H
```

---

<a id="markers"></a>
## 5. Arrow & Marker Definitions

Put these in `<defs>` at the top of every diagram:

```xml
<defs>
  <!-- Standard arrowhead (default charcoal) -->
  <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5"
          markerWidth="6" markerHeight="6" orient="auto-start-reverse">
    <path d="M 0 0 L 10 5 L 0 10 z" fill="#333333"/>
  </marker>

  <!-- Blue accent arrowhead -->
  <marker id="arrow-blue" viewBox="0 0 10 10" refX="9" refY="5"
          markerWidth="6" markerHeight="6" orient="auto-start-reverse">
    <path d="M 0 0 L 10 5 L 0 10 z" fill="#4A90D9"/>
  </marker>

  <!-- Open arrowhead (for optional/async flows) -->
  <marker id="arrow-open" viewBox="0 0 10 10" refX="9" refY="5"
          markerWidth="6" markerHeight="6" orient="auto-start-reverse">
    <path d="M 0 0 L 10 5 L 0 10" fill="none" stroke="#333333" stroke-width="1.5"/>
  </marker>

  <!-- Dot marker (for connection points) -->
  <marker id="dot" viewBox="0 0 10 10" refX="5" refY="5"
          markerWidth="5" markerHeight="5">
    <circle cx="5" cy="5" r="3" fill="#333333"/>
  </marker>
</defs>
```

Usage:
```xml
<line x1="100" y1="60" x2="100" y2="120"
      stroke="#333" stroke-width="1.5" marker-end="url(#arrow)"/>
```

For paths (curved arrows):
```xml
<path d="M 100,60 C 100,90 200,90 200,120"
      fill="none" stroke="#333" stroke-width="1.5" marker-end="url(#arrow)"/>
```

---

<a id="shapes"></a>
## 6. Shape Library

### Process / Step (rounded rectangle)
```xml
<g transform="translate({x},{y})">
  <rect width="160" height="60" rx="8" ry="8"
        fill="#F5F7FA" stroke="#333333" stroke-width="1.5"/>
  <text x="80" y="30" text-anchor="middle" dominant-baseline="central"
        font-family="'PingFang SC','Microsoft YaHei','Noto Sans SC',sans-serif"
        font-size="14" font-weight="500" fill="#333">
    处理步骤
  </text>
</g>
```

### Start / End (pill shape)
```xml
<g transform="translate({x},{y})">
  <rect width="120" height="40" rx="20" ry="20"
        fill="#F5F7FA" stroke="#333333" stroke-width="1.5"/>
  <text x="60" y="20" text-anchor="middle" dominant-baseline="central"
        font-family="..." font-size="14" font-weight="500" fill="#333">
    开始
  </text>
</g>
```

### Decision (diamond)
Use a rotated square or a `<polygon>`:
```xml
<g transform="translate({cx},{cy})">
  <polygon points="0,-40 50,0 0,40 -50,0"
           fill="#F5F7FA" stroke="#333333" stroke-width="1.5"/>
  <text x="0" y="0" text-anchor="middle" dominant-baseline="central"
        font-family="..." font-size="13" fill="#333">
    条件判断?
  </text>
</g>
```
Note: diamond center is at (cx, cy). Outgoing arrows start from the 4 points.

### Database (cylinder)
```xml
<g transform="translate({x},{y})">
  <path d="M 0,15 Q 0,0 60,0 Q 120,0 120,15 L 120,55 Q 120,70 60,70 Q 0,70 0,55 Z"
        fill="#F5F7FA" stroke="#333333" stroke-width="1.5"/>
  <path d="M 0,15 Q 0,30 60,30 Q 120,30 120,15"
        fill="none" stroke="#333333" stroke-width="1.5"/>
  <text x="60" y="48" text-anchor="middle" dominant-baseline="central"
        font-family="..." font-size="13" fill="#333">
    数据库
  </text>
</g>
```

### Cloud (for external services)
```xml
<g transform="translate({x},{y})">
  <path d="M 40,55 Q 10,55 10,40 Q 10,25 30,22 Q 30,5 55,5 Q 75,5 80,18 Q 100,15 105,30 Q 115,30 115,42 Q 115,55 95,55 Z"
        fill="#F5F7FA" stroke="#333333" stroke-width="1.5"/>
  <text x="62" y="38" text-anchor="middle" dominant-baseline="central"
        font-family="..." font-size="12" fill="#333">
    云服务
  </text>
</g>
```

### User / Actor (stick figure or icon)
```xml
<g transform="translate({x},{y})">
  <circle cx="20" cy="10" r="10" fill="none" stroke="#333" stroke-width="1.5"/>
  <line x1="20" y1="20" x2="20" y2="45" stroke="#333" stroke-width="1.5"/>
  <line x1="5" y1="30" x2="35" y2="30" stroke="#333" stroke-width="1.5"/>
  <line x1="20" y1="45" x2="5" y2="65" stroke="#333" stroke-width="1.5"/>
  <line x1="20" y1="45" x2="35" y2="65" stroke="#333" stroke-width="1.5"/>
  <text x="20" y="78" text-anchor="middle" font-family="..." font-size="12" fill="#333">
    用户
  </text>
</g>
```

### Document
```xml
<g transform="translate({x},{y})">
  <path d="M 0,0 L 120,0 L 120,60 Q 90,50 60,60 Q 30,70 0,60 Z"
        fill="#F5F7FA" stroke="#333333" stroke-width="1.5"/>
  <text x="60" y="28" text-anchor="middle" dominant-baseline="central"
        font-family="..." font-size="13" fill="#333">
    文档
  </text>
</g>
```

### Highlighted node (accent border)
Same as any shape, but change stroke color:
```xml
<rect ... stroke="#4A90D9" stroke-width="2"/>
```

---

<a id="containers"></a>
## 7. Container / Group Patterns

### Dashed container with label
Use for grouping related components (e.g., "服务层", "数据层"):
```xml
<g transform="translate({x},{y})">
  <!-- Background -->
  <rect width="380" height="200" rx="8" ry="8"
        fill="#EBF2FB" stroke="#4A90D9" stroke-width="1" stroke-dasharray="6,3"/>
  <!-- Label -->
  <text x="16" y="22" font-family="..." font-size="12" font-weight="600" fill="#4A90D9">
    服务层 Service Layer
  </text>
  <!-- Child elements go here, offset by CONTAINER_PAD -->
</g>
```

### Solid container (for major sections)
```xml
<rect width="380" height="200" rx="8" ry="8"
      fill="#F5F7FA" stroke="#DCDFE3" stroke-width="1"/>
```

### Swimlane (vertical columns)
```xml
<!-- Lane borders -->
<line x1="280" y1="40" x2="280" y2="560" stroke="#DCDFE3" stroke-width="1" stroke-dasharray="4,4"/>
<!-- Lane headers -->
<text x="140" y="25" text-anchor="middle" font-family="..." font-size="14" font-weight="600" fill="#333">
  客户端
</text>
```

---

<a id="connectors"></a>
## 8. Connector Patterns

### Straight line with arrow
```xml
<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"
      stroke="#333" stroke-width="1.5" marker-end="url(#arrow)"/>
```

### Right-angle connector (step line)
For connecting nodes that aren't directly above/below:
```xml
<!-- Go down, then right, then down -->
<path d="M {x1},{y1} L {x1},{mid_y} L {x2},{mid_y} L {x2},{y2}"
      fill="none" stroke="#333" stroke-width="1.5" marker-end="url(#arrow)"/>
```

### Curved connector
```xml
<path d="M {x1},{y1} C {x1},{ctrl_y} {x2},{ctrl_y} {x2},{y2}"
      fill="none" stroke="#333" stroke-width="1.5" marker-end="url(#arrow)"/>
```

### Dashed line (optional/async flow)
```xml
<line ... stroke-dasharray="6,3" marker-end="url(#arrow-open)"/>
```

### Bidirectional arrow
```xml
<line ... marker-start="url(#arrow)" marker-end="url(#arrow)"/>
```

### Label on connector
Place a small text element near the midpoint:
```xml
<!-- Background rect for readability -->
<rect x="{mid_x - 20}" y="{mid_y - 8}" width="40" height="16" rx="3" fill="white"/>
<text x="{mid_x}" y="{mid_y}" text-anchor="middle" dominant-baseline="central"
      font-family="..." font-size="11" fill="#5C6670">
  HTTP
</text>
```

---

<a id="flowchart"></a>
## 9. Flowchart Pattern

Complete example of a vertical flowchart:

```xml
<svg viewBox="0 0 600 520" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5"
            markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#333333"/>
    </marker>
  </defs>

  <!-- Start -->
  <g transform="translate(240, 40)">
    <rect width="120" height="40" rx="20" ry="20" fill="#F5F7FA" stroke="#333" stroke-width="1.5"/>
    <text x="60" y="20" text-anchor="middle" dominant-baseline="central"
          font-family="'PingFang SC','Microsoft YaHei','Noto Sans SC',sans-serif"
          font-size="14" fill="#333">开始</text>
  </g>

  <!-- Arrow: Start → Process -->
  <line x1="300" y1="80" x2="300" y2="130" stroke="#333" stroke-width="1.5" marker-end="url(#arrow)"/>

  <!-- Process -->
  <g transform="translate(220, 130)">
    <rect width="160" height="60" rx="8" ry="8" fill="#F5F7FA" stroke="#333" stroke-width="1.5"/>
    <text x="80" y="30" text-anchor="middle" dominant-baseline="central"
          font-family="'PingFang SC','Microsoft YaHei','Noto Sans SC',sans-serif"
          font-size="14" font-weight="500" fill="#333">数据预处理</text>
  </g>

  <!-- Arrow: Process → Decision -->
  <line x1="300" y1="190" x2="300" y2="260" stroke="#333" stroke-width="1.5" marker-end="url(#arrow)"/>

  <!-- Decision -->
  <g transform="translate(300, 300)">
    <polygon points="0,-40 60,0 0,40 -60,0" fill="#F5F7FA" stroke="#333" stroke-width="1.5"/>
    <text x="0" y="0" text-anchor="middle" dominant-baseline="central"
          font-family="'PingFang SC','Microsoft YaHei','Noto Sans SC',sans-serif"
          font-size="13" fill="#333">是否有效?</text>
  </g>

  <!-- Yes branch: right -->
  <line x1="360" y1="300" x2="480" y2="300" stroke="#333" stroke-width="1.5" marker-end="url(#arrow)"/>
  <text x="410" y="290" text-anchor="middle" font-family="'PingFang SC','Microsoft YaHei','Noto Sans SC',sans-serif"
        font-size="11" fill="#5C6670">是</text>

  <!-- No branch: down -->
  <line x1="300" y1="340" x2="300" y2="410" stroke="#333" stroke-width="1.5" marker-end="url(#arrow)"/>
  <text x="312" y="378" font-family="'PingFang SC','Microsoft YaHei','Noto Sans SC',sans-serif"
        font-size="11" fill="#5C6670">否</text>

  <!-- End -->
  <g transform="translate(240, 420)">
    <rect width="120" height="40" rx="20" ry="20" fill="#F5F7FA" stroke="#333" stroke-width="1.5"/>
    <text x="60" y="20" text-anchor="middle" dominant-baseline="central"
          font-family="'PingFang SC','Microsoft YaHei','Noto Sans SC',sans-serif"
          font-size="14" fill="#333">结束</text>
  </g>
</svg>
```

---

<a id="architecture"></a>
## 10. Architecture Diagram Pattern

Layout strategy for layered architecture:
```
Row 0 (y=40):   [  用户/客户端  ]
                       ↓
Row 1 (y=160):  ┌─ 服务层 ────────────────────┐
                │  [API网关]  [认证服务]  [业务服务] │
                └──────────────────────────────┘
                       ↓
Row 2 (y=340):  ┌─ 数据层 ────────────────────┐
                │  [PostgreSQL]  [Redis]  [S3]  │
                └──────────────────────────────┘
```

Steps:
1. Draw container rects first (dashed, light fill)
2. Place nodes inside containers, evenly spaced
3. Draw connectors between layers last
4. Add container labels in top-left corner

Tip: For N nodes in a container of width W, each node's x-center = `container_x + (W / (N+1)) * i` where i goes from 1 to N.

---

<a id="sequence"></a>
## 11. Sequence Diagram Pattern

Structure:
```xml
<!-- Actor headers at top -->
<g transform="translate(100, 30)">
  <rect width="100" height="36" rx="4" fill="#F5F7FA" stroke="#333" stroke-width="1.5"/>
  <text x="50" y="18" text-anchor="middle" dominant-baseline="central" ...>客户端</text>
</g>

<!-- Lifelines (dashed vertical) -->
<line x1="150" y1="66" x2="150" y2="500" stroke="#BFBFBF" stroke-width="1" stroke-dasharray="6,4"/>

<!-- Message arrows (solid = sync, dashed = async/response) -->
<line x1="150" y1="100" x2="400" y2="100" stroke="#333" stroke-width="1.5" marker-end="url(#arrow)"/>
<text x="275" y="92" text-anchor="middle" font-size="12" fill="#5C6670">发送请求</text>

<!-- Return (dashed) -->
<line x1="400" y1="140" x2="150" y2="140" stroke="#333" stroke-width="1"
      stroke-dasharray="6,3" marker-end="url(#arrow)"/>
<text x="275" y="132" text-anchor="middle" font-size="11" fill="#5C6670">返回结果</text>

<!-- Activation box -->
<rect x="145" y="95" width="10" height="50" fill="#4A90D9" opacity="0.3" stroke="#4A90D9" stroke-width="1"/>
```

---

<a id="tips"></a>
## 12. Layout Tips & Common Mistakes

### DO
- Calculate canvas size based on content before writing SVG
- Use `<g transform="translate(x,y)">` to position groups — makes coordinates inside relative
- Center text with `text-anchor="middle"` + `dominant-baseline="central"`
- Test Chinese character count against shape width (each char ≈ 1em wide)
- Keep stroke-width consistent: 1.5px for shapes, 1.5px for primary arrows, 1px for secondary
- Use `rx="8"` for subtle rounding, `rx="20"` only for pill shapes

### DON'T
- Don't use `<foreignObject>` — poor cross-platform support
- Don't use CSS `@import` or external stylesheets
- Don't use shadows (`filter: drop-shadow`) in minimal style
- Don't use gradients — flat fills only
- Don't make shapes too small for their text content
- Don't forget the `xmlns` attribute on the `<svg>` element
- Don't place connectors before shapes in the SVG source (they'll render behind)
- Don't use `font-family="Arial"` alone — CJK text will fall back to ugly system fonts

### Edge alignment for arrows
When drawing an arrow from shape A to shape B:
- **Top of B**: arrow ends at `B.y`
- **Bottom of A**: arrow starts at `A.y + A.height`
- **Left of B**: arrow ends at `B.x`
- **Right of A**: arrow starts at `A.x + A.width`
- Leave ARROW_GAP (8px) between shape edge and arrow tip for cleaner look if using markers

### Handling many nodes
If a diagram has >10 nodes, consider:
- Splitting into sub-diagrams
- Using smaller NODE_H_SMALL (40px)
- Reducing font to 12px
- Increasing canvas dimensions
- Using horizontal layout for wide, shallow hierarchies
