# Assertions(评分点)

每个 eval 用同一套断言。可程序化检查的会写脚本验,主观项靠人评。

## 程序化(用 openpyxl 读取产出 xlsx 验)

| ID | 断言 | 检查方式 |
|---|---|---|
| `produces_xlsx` | outputs/ 下产出至少一个 .xlsx 文件 | glob `*.xlsx` 非空 |
| `multi_sheet` | xlsx 至少有 3 张 sheet | `len(wb.sheetnames) >= 3` |
| `has_feature_list` | 至少一张 sheet 看起来像功能清单(列名含"FR"或"功能"或"feature"或"requirement") | 模糊匹配表头 |
| `has_field_definitions` | 至少一张 sheet 含字段定义(列名含"字段"或"field"或"key"或"type") | 模糊匹配 |
| `has_lifecycle_or_status` | 至少一张 sheet 反映生命周期/状态(含"状态"/"生命周期"/"PRD"/"签字"等) | 模糊匹配 |
| `coverage_01_03` | 产出包含 01-03 前缀的 22 行左右 FR(±5) | grep prefix |
| `coverage_05` | 包含 05 前缀的 26 行左右 FR(±5) | grep prefix |
| `coverage_08` | 包含 08 前缀(只有需求确认单的功能也被收录) | 行存在 |
| `manual_columns_present` | 至少有一列看起来是手填的(开发状态/责任人/优先级/owner/status) | 表头匹配 |
| `has_styling` | 表头有非默认填充色(不是白底黑字) | openpyxl 检查 fill |
| `has_freeze_panes` | 至少一张 sheet 设了冻结窗格 | `ws.freeze_panes is not None` |
| `recalc_zero_errors` | 用 LibreOffice 重算后 0 个公式错误 | 调 recalc.py |

## 主观(看 outputs 与 REPORT.md 评)

| ID | 断言 | 评价方式 |
|---|---|---|
| `polished_visual` | 排版「打开即用」,不需要再调样式(冻结/筛选/斑马纹/wrap_text) | 视觉验收 |
| `manual_preservation_documented` | 手填列保留机制有提及/实现(REPORT 写或代码体现) | 看 REPORT 或代码 |
| `lifecycle_correct` | 生命周期表正确反映 08 缺 PRD、05 v1 已归档 | 视觉验收 |
| `efficiency` | 不绕路、不写无用代码、token 消耗合理 | 看 transcript |
