# Excel Template Specification (Format B)

Extracted from: 用例模板.xlsx, 资源池测试用例.xlsx

## Document Structure

| Row | Purpose | Content |
|-----|---------|---------|
| 1 | Title Bar | "功能测试用例" + Test Result counters (Pass/Fail/Blocked) |
| 2 | Summary Bar | "测试设计" label (A2) + "测试结果" label (G2) + count formulas |
| 3 | Info Bar | Merged A3:C3 — "模块名称：xxx\n设计人员：\nxxx\n设计时间：YYYY/MM/DD" |
| 4 | Header Row | 17 column headers |
| 5 | Section Row | Gray separator: "模块名称（MODULE-CODE）" |
| 6+ | Data Rows | Test case data |

## Row 1 — Title Bar

- Cell A1: text = "功能测试用例"
- Spans A1 through H1 (8 cells, same fill)
- Font: 微软雅黑, 12pt, bold, color #FFCC99
- Fill: #993300
- Alignment: left, top, wrap_text=true
- Border: thin all sides
- Cell I1: text = "测试结果" (same style)
- Cell J1: text = "Pass" (same style)
- Cell K1: text = "Fail" (same style)
- Cell L1: text = "Blocked" (same style)
- Cells M1:Q1: empty, no fill, font 微软雅黑 11pt, border thin

## Row 2 — Summary Bar

- Cell A2: text = "测试设计"
  - Font: 微软雅黑, 11pt, bold, color #000000
  - Fill: #305496
  - Border: thin (left, bottom)
- Cells B2:F2: empty, fill #305496, border thin
- Cell G2: text = "测试结果"
  - Same font/fill as A2
  - Border: thin (right, bottom)
- Cell H2: empty
- Cell I2: text = "数量", normal weight
- Cell J2: formula =COUNTIF(N:N,"Pass")
- Cell K2: formula =COUNTIF(N:N,"Fail")
- Cell L2: formula =COUNTIF(N:N,"Blocked")

## Row 3 — Info Bar

- Merged A3:C3
- Content (multi-line):
  ```
  模块名称：{module_name}
  设计人员：
  {designer}
  设计时间：{design_date}
  ```
- Font: 微软雅黑, 11pt, bold
- No fill
- Alignment: left, top, wrap_text=true
- Border: thin all sides
- Row height: 60pt

## Row 4 — Header Row

17 columns in order:

| Col | Key | Label | Width |
|-----|-----|-------|-------|
| A | id | 序号 | 19 |
| B | module | 功能模块 | 17 |
| C | sub_module | 子模块 | 14 |
| D | test_point | 测试点 | 24 |
| E | case_name | 用例名称 | 27 |
| F | precondition | 前提条件 | 31 |
| G | steps | 操作步骤 | 45 |
| H | expected | 预期结果 | 56 |
| I | note | 用例备注 | 9 |
| J | self_test | 自测结果 | 9 |
| K | developer | 开发人员 | 9 |
| L | self_date | 自测日期 | 9 |
| M | priority | 优先级 | 9 |
| N | exec_result | 执行结果 | 9 |
| O | tester | 测试人员 | 9 |
| P | test_date | 测试日期 | 9 |
| Q | remark | 备注 | 9 |

- Font: 微软雅黑, 11pt, bold
- Fill: #9BC2E6
- Alignment: left, top, wrap_text=true (H column: center vertical)
- Border: thin all sides

## Section Separator Row

- Cell A only has text: "模块名称（MODULE-CODE）"
- Font: 微软雅黑, 11pt, bold
- Fill: #C0C0C0
- Alignment: left, top
- Border: thin all sides

## Data Rows

- Font: 微软雅黑, 11pt, normal
- No fill
- Alignment: left, top, wrap_text=true
- Border: thin all sides
- Row height: auto-calculated based on content (~13.5pt per wrapped line)

## Merge Rules

Within each section (between section separator rows):
- Column B (功能模块): merge adjacent cells with same value
- Column C (子模块): merge adjacent cells with same value
- Column D (测试点): merge adjacent cells with same value

Never merge across section boundaries.

## Test Case ID Pattern

Format: `{MODULE-CODE}_{NNN}`
- MODULE-CODE: extracted from section title parentheses, e.g., "基金日常管理（JJRCGL-GSBG）" → JJRCGL-GSBG
- NNN: 3-digit zero-padded sequential number, resets per section
- Example: JJRCGL-GSBG_001, JJRCGL-GSBG_002, ...
