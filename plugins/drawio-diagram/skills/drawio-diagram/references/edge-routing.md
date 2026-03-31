# Edge Routing Rules

箭头穿过文字、重叠、穿越中间节点是 draw.io 图表最常见的质量问题。本文档提供完整的路由规则体系。

## Table of Contents
1. [7 条核心规则](#rules)
2. [障碍物避让详解](#obstacle)
3. [生成前心理验证](#checklist)
4. [架构图专项规则](#architecture)
5. [常见错误模式](#antipatterns)

---

<a id="rules"></a>
## 1. Seven Edge Routing Rules

### Rule 1: 禁止共享路径

两条及以上的 edge 不能走完全相同的路径。如果两条 edge 连接同一对节点（或路径重叠），必须使用不同的 exit/entry 点：

```
Bad:  exitY=0.5 + exitY=0.5  (重叠)
Good: exitY=0.3 + exitY=0.7  (分开)
```

### Rule 2: 双向连接走对侧

当 A↔B 有双向箭头时，使用相反的边：

```
A → B: exitX=1 (右), entryX=0 (左)
B → A: exitX=0 (左), entryX=1 (右)
```

这样两条线自然分开，不会重叠。

### Rule 3: 必须显式指定 exit/entry 点

每条 edge 的 style 中必须包含 `exitX`, `exitY`, `entryX`, `entryY` 四个属性。不指定时 draw.io 从中心自动路由，会穿过其他节点的文字。

```xml
style="edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;exitX=0.5;exitY=1;exitDx=0;exitDy=0;entryX=0.5;entryY=0;entryDx=0;entryDy=0;strokeColor=#333333;strokeWidth=2;"
```

### Rule 4: 障碍物避让（最重要）

画 edge 之前，先识别 source 和 target 之间的所有中间节点。如果直连路径会穿过任何中间节点的边界框，必须使用 waypoints 绕行。

详见 [障碍物避让详解](#obstacle)。

### Rule 5: 先规划布局再生成 XML

在写任何 XML 之前，先做布局规划：

1. 按流向（从上到下或从左到右）将节点分层/分区
2. 同层节点水平间距 ≥ 150px，层间垂直间距 ≥ 100px
3. 心算每条 edge 的路径："这条线中间会穿过哪些节点？"
4. 如果发现交叉不可避免，调整节点位置而非堆叠 waypoints

### Rule 6: 复杂路由用多个 waypoints

一个 waypoint 通常不够。L 型路径需要 1 个 waypoint，U 型需要 2 个，绕行需要 3 个或更多。

每个方向变化都需要一个 waypoint（拐角点）。waypoints 应该形成清晰的水平/垂直线段（正交路由）。

```xml
<mxCell id="e1" style="edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;" edge="1" parent="1" source="a" target="b">
  <mxGeometry relative="1" as="geometry">
    <Array as="points">
      <mxPoint x="500" y="200" />  <!-- 拐角 1 -->
      <mxPoint x="500" y="400" />  <!-- 拐角 2 -->
    </Array>
  </mxGeometry>
</mxCell>
```

### Rule 7: 使用自然连接点，禁止角落

连接点应该基于流向选择，永远不要用角落（如 entryX=1,entryY=1）。

| 流向 | exit 点 | entry 点 |
|------|---------|----------|
| 上→下 | exitX=0.5, exitY=1 (底部) | entryX=0.5, entryY=0 (顶部) |
| 左→右 | exitX=1, exitY=0.5 (右侧) | entryX=0, entryY=0.5 (左侧) |
| 对角线 | 用最近的边中点 | 用最近的边中点 |
| 反向 | 交换 exit/entry | 交换 exit/entry |

**Bad**: `exitX=1;exitY=1` — 从角落出发，看起来不自然
**Good**: `exitX=1;exitY=0.5` — 从右侧中点出发，干净整洁

---

<a id="obstacle"></a>
## 2. 障碍物避让详解

这是最常被忽略也最影响图表质量的规则。

### 检测流程

画每条 edge 之前：
1. 确定 source 和 target 的位置
2. 画一条假想的直线连接它们
3. 检查这条线是否穿过任何其他节点的边界框（x, y, width, height 矩形区域）
4. 如果穿过 → 必须添加 waypoints 绕行

### 间距要求

waypoints 距离障碍物边界至少 **20-30px**。计算方式：
```
障碍物右边界 = obstacle.x + obstacle.width
waypoint.x = 障碍物右边界 + 30
```

### 绕行策略

**场景：A 在左上，C 在右下，B 在中间**

```
[A]                        [A]
  \                          |
   \  ← 穿过 B！              | exitX=0.5, exitY=1
  [B]                      [B]  waypoint at (A.x, C.y)
     \                        \
      [C]                      [C]
```

**Bad**: 对角线直连穿过 B
**Good**: 先向下，再绕到 B 的外围

### 对角线连接的外围路由

当需要对角线连接远距离节点时，沿图表的外围（上方、下方或侧面）路由，不要穿过中间密集区域。

```xml
<!-- 场景：从右下的 Hotfix 连到左上的 Main，中间有 Develop -->
<!-- 错误：对角线穿过 Develop -->
<!-- 正确：从右侧绕行 -->
<mxCell id="e1" style="edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;
  exitX=1;exitY=0.5;entryX=1;entryY=0.5;" edge="1" parent="1"
  source="hotfix" target="main">
  <mxGeometry relative="1" as="geometry">
    <Array as="points">
      <mxPoint x="750" y="350" />  <!-- 绕到右侧 -->
      <mxPoint x="750" y="100" />  <!-- 沿右侧上行 -->
    </Array>
  </mxGeometry>
</mxCell>
```

---

<a id="checklist"></a>
## 3. 生成前心理验证

在输出 XML 之前，逐条检查：

1. **"有没有 edge 穿过非源/目标节点？"**
   → 如果有，添加 waypoints 绕行

2. **"有没有两条 edge 共享相同路径？"**
   → 如果有，调整 exit/entry 点使它们分开

3. **"有没有连接点在角落？"**
   → 如果有，改用边的中点

4. **"能不能通过重排节点来减少交叉？"**
   → 如果能，先修改布局再画线

### Fan-out 模式

当一个节点连接多个目标时，分散 exit/entry 点：

```
一个节点连 3 个目标：
  exitX=0.25  → 目标 1
  exitX=0.50  → 目标 2
  exitX=0.75  → 目标 3

多个节点连同一个目标：
  entryX=0.25  ← 来源 1
  entryX=0.50  ← 来源 2
  entryX=0.75  ← 来源 3
```

---

<a id="architecture"></a>
## 4. 架构图专项规则

架构图的层间连接（多对多）是最容易出问题的场景。

### 容器标签外置

架构图的分层容器（如"服务层"、"数据层"）必须使用外部标签：

```xml
<!-- 容器 value 为空 -->
<mxCell id="layer1" value="" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f5f5f5;strokeColor=#666666;dashed=1;dashPattern=5 5;" vertex="1" parent="1">
  <mxGeometry x="100" y="80" width="600" height="120" as="geometry" />
</mxCell>
<!-- 标签在容器左侧 -->
<mxCell id="layer1_label" value="服务层" style="text;html=1;align=right;verticalAlign=middle;fillColor=none;strokeColor=none;fontSize=13;fontStyle=1;fontColor=#666666;" vertex="1" parent="1">
  <mxGeometry x="20" y="110" width="70" height="30" as="geometry" />
</mxCell>
```

原因：`verticalAlign=top` 的内置标签恰好在箭头进入容器的路径上。

### 层间连接用 fan-out

3 个服务各连 2 个数据库（6 条线）：

```
Service A      Service B      Service C
exitX=0.35     exitX=0.35     exitX=0.35      ← DB 连接从偏左出
exitX=0.65     exitX=0.65     exitX=0.65      ← Cache 连接从偏右出

目标入口也要分散：
entryX=0.25    entryX=0.50    entryX=0.75
```

### 层间间距

层组之间最少 **80px** 垂直间距，给箭头留出路由空间。

---

<a id="antipatterns"></a>
## 5. 常见错误模式

### Anti-pattern 1: 省略 exit/entry 点
```xml
<!-- Bad: 自动路由，箭头穿过中间节点 -->
<mxCell style="edgeStyle=orthogonalEdgeStyle;" edge="1" source="a" target="c" />

<!-- Good: 显式指定 -->
<mxCell style="edgeStyle=orthogonalEdgeStyle;exitX=0.5;exitY=1;entryX=0.5;entryY=0;" edge="1" source="a" target="c" />
```

### Anti-pattern 2: 所有箭头从同一点出发
```
Bad:  3 条线都从 exitX=0.5 出发 → 重叠
Good: exitX=0.25, 0.5, 0.75 分别出发 → 分开
```

### Anti-pattern 3: 跨行直连不加 waypoints
```
Bad:  [A] ─────────────── [D]  ← 穿过 [B] 和 [C]
Good: [A] ─→ waypoint ─→ waypoint ─→ [D]  ← 绕行
```

### Anti-pattern 4: 角落连接
```
Bad:  exitX=1, exitY=1  (从右下角出发)
Good: exitX=1, exitY=0.5 (从右侧中点出发)
```
