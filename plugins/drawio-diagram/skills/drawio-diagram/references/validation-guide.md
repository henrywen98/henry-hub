# Diagram Validation Guide

完整的图表质量验证流程，包含结构化检查 schema、常见 XML 错误自动修复、以及重试循环策略。

## Table of Contents
1. [验证概览](#overview)
2. [结构化检查 Schema](#schema)
3. [验证检查清单](#checklist)
4. [XML 常见错误与自动修复](#autofix)
5. [重试循环策略](#retry)
6. [反馈格式化](#feedback)

---

<a id="overview"></a>
## 1. 验证概览

验证分两层：

| 层级 | 方式 | 检查内容 | 时机 |
|------|------|----------|------|
| **结构验证** | 脚本/XML 解析 | XML 语法、ID 唯一性、必需元素、引用完整性 | 生成后立即 |
| **视觉验证** | 导出 PNG + AI 审查 | 文字可读性、箭头路由、布局平衡、元素重叠 | 结构验证通过后 |

---

<a id="schema"></a>
## 2. 结构化检查 Schema

每个检查项归入以下分类：

### Issue Types

| Type | 含义 | 示例 |
|------|------|------|
| `overlap` | 元素互相覆盖，内容不可读 | "销售管理" 框覆盖了 "采购管理" 框 |
| `edge_routing` | 箭头穿过非源/目标节点 | 从 A 到 C 的箭头穿过了 B 的文字区域 |
| `text` | 文字截断、重叠或太小 | 标签被节点边界截断，只显示一半 |
| `layout` | 间距不均、对齐混乱、拥挤 | 左侧 3 个模块挤在一起，右侧大片空白 |
| `rendering` | 元素不完整、损坏或缺失 | 缺少 id="0" 根元素导致文件无法打开 |

### Severity Levels

| Severity | 含义 | 处理方式 |
|----------|------|----------|
| **critical** | 阻塞性问题，图表不可用 | 必须修复后才能交付 |
| **warning** | 外观问题，图表可用但不完美 | 记录但不阻塞交付 |

### 分类映射

| Issue Type | 默认 Severity | 升级为 Critical 的条件 |
|------------|--------------|----------------------|
| overlap | critical | — |
| edge_routing | critical | — |
| text | warning | 主要标签完全不可读时升级 |
| layout | warning | 超过 30% 的元素拥挤在一起时升级 |
| rendering | critical | — |

### 判定规则

- `valid = true` 当且仅当没有 critical 级别的 issue
- 只有 warning 级别的 issue → valid，记录 warnings
- 空图或只有 1-2 个元素的简单图 → 除非有明显错误，否则 pass
- 轻微的对齐偏差 → warning，不升级

---

<a id="checklist"></a>
## 3. 验证检查清单

### 结构验证（脚本可检查）

1. **valid-xml**: 文件是合法的 XML，能被解析
2. **has-mxfile-structure**: 根标签是 `<mxfile>`，包含 `<diagram>` → `<mxGraphModel>` → `<root>`
3. **has-root-cells**: 每个 page 包含 `id="0"` 和 `id="1" parent="0"` 的根 mxCell
4. **all-ids-unique**: 同一 page 内无重复 ID
5. **valid-references**: 所有 edge 的 source/target 引用的 ID 存在
6. **no-nested-mxcell**: mxCell 元素是平级兄弟，不嵌套
7. **no-xml-comments**: 不包含 `<!-- -->` 注释（draw.io 会删除注释，导致编辑工具出错）

### 视觉验证（AI 看 PNG 截图）

优先级从高到低：

1. **arrow-text-collision** [critical]: 箭头是否穿过节点标签或组标题？
2. **element-overlap** [critical]: 元素是否互相覆盖？
3. **text-readability** [warning]: 所有标签可见且未乱码？
4. **layout-balance** [warning]: 模块均匀分布？有拥挤或空白区域？
5. **arrow-routing** [critical]: 箭头绕过节点而非穿过？方向正确？
6. **color-coding** [warning]: 不同模块/组视觉上可区分？
7. **completeness** [warning]: 所有预期的模块、节点、连接都存在？

---

<a id="autofix"></a>
## 4. XML 常见错误与自动修复

AI 生成的 draw.io XML 常见的错误及修复方法：

### 结构性错误

| 错误 | 症状 | 修复 |
|------|------|------|
| 缺少根 mxCell | 文件无法打开 | 确保每个 `<root>` 内有 `<mxCell id="0"/>` 和 `<mxCell id="1" parent="0"/>` |
| mxCell 嵌套 | draw.io 解析异常 | 把嵌套的 mxCell 提升为兄弟元素 |
| ID 重复 | 元素相互覆盖 | 给重复 ID 加后缀 `_2`, `_3` |
| 包含 wrapper 标签 | 多层嵌套 | 去除多余的 `<mxfile>` 等 wrapper |

### 编码错误

| 错误 | 症状 | 修复 |
|------|------|------|
| 未转义的 `&` | XML 解析失败 | 替换为 `&amp;` |
| 未转义的 `<` `>` 在 value 中 | 解析失败 | 替换为 `&lt;` `&gt;` |
| JSON 转义遗留 `\"` | 属性值有反斜杠 | 去除反斜杠 |
| 双重转义 `&ampquot;` | 显示乱码 | 还原为 `&quot;` |

### 标签错误

| 错误 | 症状 | 修复 |
|------|------|------|
| `</tag/>` | 解析失败 | 改为 `</tag>` |
| 大小写不一致 `</MxCell>` | 标签不匹配 | 统一为 `</mxCell>` |
| `<Cell>` 代替 `<mxCell>` | 无法识别 | 替换为 `<mxCell>` |
| 缺少属性间空格 | 属性粘连 | 在属性间插入空格 |

### XML 注释

```xml
<!-- Bad: draw.io 会删除注释，导致 edit_diagram 的 search 匹配失败 -->
<!-- 这是一个注释 -->
<mxCell id="2" .../>

<!-- Good: 不使用注释 -->
<mxCell id="2" .../>
```

---

<a id="retry"></a>
## 5. 重试循环策略

### 自动修复流程

```
生成 XML
  → 结构验证
    → 失败？尝试自动修复（转义、去 wrapper、修标签）
      → 修复后重新验证
        → 仍然失败？报告具体错误，手动修复
    → 通过？继续视觉验证

导出 PNG
  → AI 视觉检查
    → 发现 critical issue？
      → 编辑 XML 修复（调整坐标、样式、waypoints）
      → 重新导出 PNG，重新检查
      → 最多重试 3 次
    → 只有 warnings？
      → 记录，交付
    → 全部通过？
      → 交付
```

### 最大重试次数

- 结构修复：自动修复 1 次，手动修复最多 2 次
- 视觉修复：最多 3 次（每次针对上一次的 critical issues）
- 超过重试上限：交付当前版本 + 告知用户剩余 warnings

### 反馈到 AI 的格式

每次重试时，将验证结果格式化为修复指令：

```
DIAGRAM VISUAL VALIDATION - Issues Found (Attempt 2/3)

Critical Issues (must fix):
  - [edge_routing] 从"销售管理"到"收款管理"的箭头穿过了"发货管理"的文字
  - [overlap] "采购管理"框和"库存管理"框重叠了 20px

Suggestions to fix:
  - 在"销售管理→收款管理"的 edge 上添加 waypoint 绕过"发货管理"
  - 将"库存管理"框向右移动 30px

Please fix these issues in the XML.
```

---

<a id="feedback"></a>
## 6. 反馈格式化

### 验证结果数据结构

```
{
  valid: boolean,
  issues: [
    {
      type: "overlap" | "edge_routing" | "text" | "layout" | "rendering",
      severity: "critical" | "warning",
      description: "具体描述哪个元素有什么问题"
    }
  ],
  suggestions: ["具体的修复建议，包含像素级指导"]
}
```

### 描述要求

- **具体指名**：不说"有些元素重叠"，说"'销售管理'框覆盖了'采购管理'框"
- **可操作**：不说"布局不好"，说"将'销售管理'框向右移动 50px"
- **包含坐标**：尽可能给出具体的 x, y 调整值
