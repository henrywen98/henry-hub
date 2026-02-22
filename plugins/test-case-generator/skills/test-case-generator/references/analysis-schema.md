# Analysis JSON Schema

Phase 2 outputs `analysis.json` to the cache directory. All subsequent phases read this file as their contract.

## Schema

```json
{
  "module_name": "string — 模块显示名, e.g. '资源池'",
  "module_code": "string — 用例ID前缀, e.g. 'ZYC'",
  "source_doc": "string — 源文档文件名",
  "dispatch": {
    "has_ui": true,
    "has_data_entry": false,
    "has_data_modify": false,
    "has_business_logic": false,
    "has_data_cleanup": false
  },
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
  "business_rules_summary": "入库审批流程: 提交→审批→入库; 入库后部分字段不可编辑",
  "filter_fields": ["企业名称/项目简称", "企业类型", "是否已入库"],
  "list_fields": ["序号", "企业全称", "企业简称", "企业类型", "是否入库", "操作"]
}
```

## Field Reference

### dispatch
- `has_ui`: Always `true`. Triggers Agent A (L0+L1+L2).
- `has_data_entry`: `true` if requirement describes create/add/import. Triggers Agent B (L3).
- `has_data_modify`: `true` if requirement describes edit/modify. Triggers Agent C (L4).
- `has_business_logic`: `true` if requirement describes approval/state/calculation. Triggers Agent D (L5+L6).
- `has_data_cleanup`: `true` if requirement describes delete/void/archive. Also triggers Agent D.

### field_table[].type
Valid values (aligned with sop-layers.md):
`text` | `textarea` | `dropdown` | `multi_dropdown` | `radio` | `checkbox` | `date` | `date_range` | `number` | `search_select` | `file`

### field_table[].interactions
Optional array. Valid values:
- `condition_show` — this field's visibility depends on another field's value
- `condition_required` — this field's required status depends on another field
- `cascade_fill` — this field is auto-filled when a parent entity is selected
- `inline_create` — this field has an "add new" button opening a sub-form
