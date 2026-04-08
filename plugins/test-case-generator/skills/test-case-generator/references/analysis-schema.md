# Analysis JSON Schema

Phase 2 outputs `analysis.json` to the cache directory. All subsequent phases read this file as their contract.

## Schema

```json
{
  "source_doc": "string — 源文档文件名",
  "common_rules": {
    "text_half_line_max": "number — 半行文本框最大字数, 如 50",
    "text_full_line_max": "number — 整行文本框最大字数, 如 100",
    "textarea_max": "number — 文本域最大字数, 如 2000",
    "amount_decimal": "number — 金额小数位数, 如 6",
    "amount_total_digits": "number — 金额总位数, 如 20",
    "percentage_max": "number — 百分比最大值, 如 999.99",
    "pagination_default": "number — 默认每页条数, 如 5",
    "pagination_options": "[number] — 可选每页条数, 如 [5, 10, 20, 50]"
  },
  "module_groups": [
    {
      "id": "grp_1",
      "name": "string — 模块显示名, e.g. '本级管理'",
      "module_code": "string — 用例ID前缀, e.g. 'BJGL'",
      "heading_text": "string — 该模块在 markdown 文档中的标题行字面文本, e.g. '## 1.2 本级管理'",
      "doc_sections": [
        {
          "id": "sec_01",
          "title": "基金列表",
          "heading_level": 2,
          "page_type": "list",
          "doc_order": 1
        }
      ],
      "field_table": [
        {
          "name": "企业全称",
          "type": "search_select",
          "required": true,
          "max_length": null,
          "rules": "已注册时从工商库搜索选择, 未注册时手动输入",
          "interactions": ["condition_show", "cascade_fill"]
        }
      ],
      "dispatch": {
        "has_ui": true,
        "has_data_entry": false,
        "has_data_modify": false,
        "has_business_logic": false,
        "has_data_cleanup": false
      },
      "business_rules_summary": "string — 该模块的业务规则摘要"
    }
  ]
}
```

## Field Reference

### common_rules

从需求文档的"公共说明"或"通用规则"章节提取。若文档无此类内容，使用以下默认值：

| 字段 | 默认值 | 说明 |
|------|--------|------|
| text_half_line_max | 50 | 半行文本框字数上限 |
| text_full_line_max | 100 | 整行文本框字数上限 |
| textarea_max | 2000 | 多行文本域字数上限 |
| amount_decimal | 2 | 金额小数位 |
| amount_total_digits | 15 | 金额总位数 |
| percentage_max | 100 | 百分比最大值 |
| pagination_default | 10 | 默认每页条数 |
| pagination_options | [10, 20, 50, 100] | 可选每页条数 |

### module_groups

按需求文档的一级/二级大章节拆分。每个 group 对应一个独立的功能模块，最终生成独立的 Excel 文件。

**拆分规则：**
- 取文档中"独立功能域"级别的大标题（如"本级管理"、"载体管理"、"子基金投资"）
- 每个 group 应包含完整的 CRUD + 审批 + 列表等功能
- 如文档只有一个模块，`module_groups` 只有 1 个元素

**heading_text：**
- 该模块在 markdown 文档中的标题行**字面文本**（含 `#` 前缀），必须与文档原文**逐字一致**，包括所有空格、标点、编号
- **不得**包含 `\s+`、`^`、`\d`、`+`、`*` 等正则元字符；split 脚本做字面字符串比较，不是正则
- 用于 split_doc.py 定位切割点，必须能在文档中唯一匹配
- 示例：
  - ✅ 正确：`# 1 资产申请管理`
  - ✅ 正确（含非换行空格 `\xa0`，若文档原文如此就照抄）：`## 1.2\xa0本级管理`
  - ❌ 错误：`^# 1\s+资产申请管理`（含正则字符）
  - ❌ 错误：`"# 1"`（过于简短，会与 `# 11`、`# 12` 碰撞）

### module_groups[].dispatch

- `has_ui`: Always `true`. Triggers Agent A (L0+L1+L2).
- `has_data_entry`: `true` if requirement describes create/add/import. Triggers Agent B (L3).
- `has_data_modify`: `true` if requirement describes edit/modify. Triggers Agent C (L4).
- `has_business_logic`: `true` if requirement describes approval/state/calculation. Triggers Agent D (L5+L6).
- `has_data_cleanup`: `true` if requirement describes delete/void/archive. Also triggers Agent D.

### module_groups[].field_table[].type

Valid values (aligned with sop-layers.md):
`text` | `textarea` | `dropdown` | `multi_dropdown` | `radio` | `checkbox` | `date` | `date_range` | `number` | `search_select` | `file`

### module_groups[].field_table[].interactions

Optional array. Valid values:
- `condition_show` — this field's visibility depends on another field's value
- `condition_required` — this field's required status depends on another field
- `cascade_fill` — this field is auto-filled when a parent entity is selected
- `inline_create` — this field has an "add new" button opening a sub-form

### module_groups[].doc_sections

该模块内的页面级章节列表。

- `id`: 唯一标识，格式 `sec_NN`（在整个 analysis.json 中全局唯一）
- `title`: 章节标题（取自需求文档原文）
- `heading_level`: 标题层级（1/2/3...）
- `page_type`: 页面类型。可选值：`list` | `form` | `detail` | `approval` | `other`
- `doc_order`: 在该 group 内的出现顺序（从 1 开始）

**粒度判断规则：**
- 取"页面级"标题作为 section（列表页、新增页、编辑页、审批页等）
- 文档只有两级标题时，取最细一级
- 三级以上标题时，取对应到独立页面/弹窗的层级
- 同一页面的不同 Tab 不拆分，归入同一 section
