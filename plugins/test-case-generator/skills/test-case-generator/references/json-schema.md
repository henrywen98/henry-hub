# Test Case JSON Schema

All test case generation output MUST conform to this JSON schema. The `convert_to_xlsx.py` script reads this JSON to produce the final Excel file.

## Complete Schema

```json
{
  "version": "1.0",
  "meta": {
    "module_name": "(string) Module display name, e.g. '资源池'",
    "module_code": "(string) Module code for test case IDs, e.g. 'JJRCGL-GSBG'",
    "designer": "(string) Designer name, can be empty",
    "design_date": "(string) Date in YYYY/MM/DD format",
    "source_doc": "(string) Source document filename"
  },
  "style": {
    "title_bar": {
      "text": "功能测试用例",
      "font_name": "微软雅黑",
      "font_size": 12,
      "bold": true,
      "font_color": "#FFCC99",
      "fill_color": "#993300"
    },
    "summary_bar": {
      "labels": ["测试设计", "", "", "", "", "", "测试结果", "", "数量"],
      "result_labels": ["Pass", "Fail", "Blocked"],
      "font_name": "微软雅黑",
      "font_size": 11,
      "bold": true,
      "fill_color": "#305496"
    },
    "info_bar": {
      "merge_cols": "A:C",
      "font_name": "微软雅黑",
      "font_size": 11,
      "bold": true
    },
    "header_row": {
      "columns": [
        {"key": "id",           "label": "序号",     "width": 19},
        {"key": "module",       "label": "功能模块",  "width": 17},
        {"key": "sub_module",   "label": "子模块",    "width": 14},
        {"key": "test_point",   "label": "测试点",    "width": 24},
        {"key": "case_name",    "label": "用例名称",  "width": 27},
        {"key": "precondition", "label": "前提条件",  "width": 31},
        {"key": "steps",        "label": "操作步骤",  "width": 45},
        {"key": "expected",     "label": "预期结果",  "width": 56},
        {"key": "note",         "label": "用例备注",  "width": 9},
        {"key": "self_test",    "label": "自测结果",  "width": 9},
        {"key": "developer",    "label": "开发人员",  "width": 9},
        {"key": "self_date",    "label": "自测日期",  "width": 9},
        {"key": "priority",     "label": "优先级",    "width": 9},
        {"key": "exec_result",  "label": "执行结果",  "width": 9},
        {"key": "tester",       "label": "测试人员",  "width": 9},
        {"key": "test_date",    "label": "测试日期",  "width": 9},
        {"key": "remark",       "label": "备注",      "width": 9}
      ],
      "font_name": "微软雅黑",
      "font_size": 11,
      "bold": true,
      "fill_color": "#9BC2E6",
      "alignment": {"horizontal": "left", "vertical": "top", "wrap_text": true},
      "border": "thin"
    },
    "section_row": {
      "font_name": "微软雅黑",
      "font_size": 11,
      "bold": true,
      "fill_color": "#C0C0C0",
      "border": "thin"
    },
    "data_row": {
      "font_name": "微软雅黑",
      "font_size": 11,
      "bold": false,
      "alignment": {"horizontal": "left", "vertical": "top", "wrap_text": true},
      "border": "thin"
    }
  },
  "sections": [
    {
      "title": "模块显示名（MODULE-CODE）",
      "test_cases": [
        {
          "id": "MODULE-CODE_001",
          "module": "功能模块名",
          "sub_module": "子模块名",
          "test_point": "测试点描述",
          "case_name": "用例名称",
          "precondition": "前提条件（可为空字符串）",
          "steps": "1.操作步骤一\n2.操作步骤二",
          "expected": "1.预期结果一\n2.预期结果二",
          "note": "",
          "priority": ""
        }
      ]
    }
  ],
  "merge_rules": {
    "module": "same_value",
    "sub_module": "same_value",
    "test_point": "same_value"
  }
}
```

## Field Rules

### meta
- `module_name`: Human-readable module name from the requirement document
- `module_code`: Abbreviation used in test case IDs. Extract from requirement doc headings or use pinyin abbreviation
- `designer`: Leave empty if not specified
- `design_date`: Use today's date if not specified

### sections
- Each section represents a functional sub-module with its own gray separator row
- `title`: Format as "显示名（CODE）", e.g., "基金日常管理（JJRCGL-GSBG）"
- Test cases within a section share the same module_code prefix in their IDs

### test_cases
- `id`: Format `{MODULE-CODE}_{NNN}`, zero-padded 3 digits, sequential within section
- `steps` and `expected`: Use `\n` for line breaks between numbered items. Each item starts with `N.` (no space after number, period directly follows)
- `precondition`: Can be empty string if no precondition needed
- `note` and `priority`: Usually empty, filled by testers later

### style
- The `style` block is FIXED for all outputs — always use the exact values shown above
- Sub-agents do NOT need to generate the style block; the main agent adds it during merge

### merge_rules
- `same_value`: Merge adjacent rows with identical values in that column
- Only applies within a section (between section separator rows)

## Sub-Agent Partial Output Format

Sub-agents output ONLY the `test_cases` array (no meta, style, or sections wrapper):

```json
[
  {
    "id": "TEMP_001",
    "module": "资源池",
    "sub_module": "列表页",
    "test_point": "页面入口检查",
    "case_name": "...",
    "precondition": "...",
    "steps": "...",
    "expected": "...",
    "note": "",
    "priority": ""
  }
]
```

The main agent:
1. Collects arrays from all sub-agents
2. Concatenates in order (A → B → C → D)
3. Renumbers IDs sequentially with the correct MODULE-CODE prefix
4. Groups into sections by sub_module
5. Wraps in the full JSON structure with meta + style
