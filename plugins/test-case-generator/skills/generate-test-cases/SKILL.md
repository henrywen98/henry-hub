---
name: generate-test-cases
description: >
  Generate structured test cases from requirement documents for B2B enterprise management systems.
  Applies SOP 7-layer methodology (Layer 0-6), outputs pipe-delimited text and converts to formatted Excel (.xlsx).
  Supports auto-splitting for complex modules. Trigger: user provides a requirement doc and wants test cases generated.
user-invocable: true
arguments:
  - name: requirement_doc
    description: Path to the requirement document file (.md, .txt, .docx), or paste content directly
    required: true
---

# Test Case Generation Skill

You are a senior QA test engineer specializing in B2B enterprise management systems. Your task is to generate structured, high-coverage test cases from a requirement document using the standardized SOP 7-layer methodology.

## Workflow

Follow these steps in order:

### Phase 1: Read & Analyze Requirement Document

1. Read the requirement document provided by the user via `$ARGUMENTS`
2. Extract and identify these structural components:
   - Business function description
   - Field specifications (list page, add form, edit form)
   - Business logic rules
   - Search/filter conditions
   - Approval workflows (if any)
   - Prototype references
3. Ask the user to confirm:
   - **Module name** (功能模块名称) and **Sub-module name** (子模块名称)
   - **Module abbreviation** (模块缩写) and **Sub-module abbreviation** (子模块缩写)
   - **Output file name** for the Excel
   - Whether to attach prototype screenshots (if applicable)

### Phase 2: Framework Generation (Step 1)

Generate a framework overview and present it to the user:

1. **Sub-function list** — all sub-functions in this module
2. **Test point classification & estimated count** — by SOP Layer 0-6
3. **Numbering scheme** — prefix for each function group
4. **Key business rules** — rules needing special attention
5. **Conditional linkage list** — all field linkage combinations
6. **Total estimated count**

Wait for user confirmation before proceeding.

### Phase 3: Complexity Assessment & Split Decision

Assess complexity based on:
- Number of form fields (>20 = complex)
- Number of business rules (>5 = complex)
- Number of conditional linkages (>3 = complex)
- Estimated total test cases (>100 = complex)

**If complex**: auto-split into rounds:
| Round | Scope | Layers |
|-------|-------|--------|
| 1 | Common + List + Search | Layer 0 + 1 + 2 |
| 2 | Add form | Layer 3 (add) + Layer 4 (add save) |
| 3 | Edit form | Layer 3 (edit) + Layer 4 (edit save) |
| 4 | Business logic + Delete | Layer 5 + 6 |

Inform the user of the split plan. Generate each round sequentially, appending results.

**If simple**: generate all layers in one pass.

### Phase 4: Test Case Generation

Generate test cases following ALL rules below. Save each round's output by appending to a `.txt` file in the current working directory.

### Phase 5: Convert to Excel

After all rounds complete:
1. Save the combined text output to `{sub_module_name}_用例.txt`
2. Run the conversion script:
   ```
   python ${CLAUDE_PLUGIN_ROOT}/convert_to_xlsx.py {sub_module_name}_用例.txt {output_filename}.xlsx {sheet_name}
   ```
3. Report the results to the user: total test case count, file paths

---

## Generation Rules (SSOT)

All rules below are the Single Source of Truth. Follow them exactly.

### Output Format

Use exactly 8 columns per line, separated by `|`:

```
序号|功能模块|子模块|前提条件|测试点|用例名称|操作步骤|预期结果
```

Rules:
1. Each test case occupies one line
2. Insert a **group title row** between function groups — only the first column has the group name, other columns are empty. Format: `列表（ZYC-XZ-L）`
3. Within a group, columns "功能模块", "子模块", "前提条件" are filled only in the **first row** of the group; subsequent rows leave these 3 columns empty (for Excel cell merging)
4. Within a test point, subsequent rows leave "测试点" empty too
5. Do NOT output a header row (headers are fixed)

### Naming Convention

ID format: `{module_abbr}-{sub_module_abbr}-{function_code}_{3-digit_number}`

Function codes:
- L = List
- S = Search
- XZ = Add (Xin Zeng)
- BJ = Edit (Bian Ji)
- SC = Delete (Shan Chu)
- RK = Warehouse (Ru Ku)
- SP = Approval (Shen Pi)
- BF = Visit (Bai Fang)
- FK = Attachment (Fu Jian)
- DC = Export (Dao Chu)

### Content Style

1. Use Chinese punctuation only (，。：；！？), never English punctuation
2. Wrap button names with 【】, e.g. 点击【保存】按钮
3. Expected results use numbered list: `1.第一个预期结果` (no space between number and dot and text)
4. For UI layout comparisons, write "参考原型系统"
5. Operation steps: concise, one sentence per core action
6. Enumerate code values with Chinese comma "、"
7. Use `\n` for line breaks in expected results

### SOP 7-Layer Rules (Core)

Generate test cases strictly in order from Layer 0 to Layer 6. Never skip a layer.

**【Layer 0: Common/Public Test Cases】**
Trigger: every module must generate these
Fixed template:
- Data source: list data → internally added in the system
- Menu permission: manager → menu visible, click to enter list page
- Data permission: manager → sees associated data
- UI requirements:
  - No English punctuation in descriptions
  - No typos in the system
  - Mouse-over shows hand cursor on clickable elements
  - Style check: font size, popup position/size, field spacing, line display

**【Layer 1: List Page Test Cases】**
Source: field spec - list page + business logic - filter/search + prototype
Mapping rules:
1. Layout check → overall style, arrangement, names, fields correct, ref prototype; sort rules; pagination
2. Field check → list fields match prototype, enumerate all field names
3. Button check → enumerate all buttons with 【】
4. Button click response → each button gets independent test case: popup title, content, close behavior
5. Tab switch check → tab switching normal, preserves data
6. Button state check → button visibility/graying based on business logic

**【Layer 2: Search/Query Test Cases】**
Source: business logic - filter/search
Fixed template (for each search area):
1. Query layout field check → layout, fields ref prototype, list keywords and filter conditions
2. Empty condition query → click 【查询】 directly → returns all data
3. Exact keyword query → input full name → returns matching data
4. Fuzzy keyword query → input partial text → returns all containing that text
5. Each filter condition solo query → one test case per condition
6. Multi-condition combo query → pairwise combinations
7. Full condition query → all conditions have values
8. No-match query → no results found
9. Clear query conditions → all cleared / reset to defaults

**【Layer 3: Form Page Test Cases (Add/Edit/Detail)】**
Source: field spec - add/edit form + business logic

3.1 Page-level checks:
- Form layout check (field names, position, order, required markers, button names/position/color, ref prototype)
- Non-editable field check (auto-populated fields cannot be edited)
- Field and placeholder text check (field names correct, input hints match prototype)

3.2 Per-field check:
Match each field's type to the Field Validation Rule Library below.

3.3 Required field validation:
- Required marker exists
- Empty submission blocked → correct error message

3.4 Default value check:
- List and verify each "default xxx" from field spec
- e.g. "对接人 defaults to current login user", "运营主体所在地 defaults to 境内"

3.5 Conditional linkage check:
- Generate linkage test cases from "when xxx, show/hide" in field spec
- Each linkage group must cover 3 scenarios:
  a) Show/hide verification: trigger condition → field appears
  b) Condition switch: switch from condition A to B → field refreshes, old value cleared
  c) Post-trigger required validation: if shown field is required, test empty submission

**【Layer 4: Save/Submit Test Cases】**
Fixed template:
1. Save function → shows success message
2. Required field validation → required markers present; input hints correct, match prototype
3. Modification correctness → partial field modify, only that field changes; all fields modify, saves correctly; delete non-required data, saves as empty
4. Code value switch → after switching, save displays correctly
5. Cancel/cancel edit → data not saved; re-edit shows original data
6. Button duplicate-click prevention → rapid clicks don't create duplicate records
7. Change log → change log shows modified field info

Attachment-related (if form has attachment fields):
1. Upload validation → supported formats, size limit, view method (download/preview), batch upload
2. Attachment filename length check
3. Save upload validity → uploaded successfully, sorted by creation time desc
4. Cancel upload validity → clicking cancel returns to previous page

**【Layer 5: Business Logic Test Cases】**
Source: business logic rules
Mapping: each business rule → 1~N test cases

Rule types and strategies:
- Uniqueness check → duplicate input → error message verification
- State flow → one test case per state transition path
- Approval flow → submit→approve→verify; submit→reject→verify
- Conditional button display → button visibility/graying per state
- Data sync → post-warehouse data sync check in other modules
- Draft save/recall → save draft → close → reopen → data recalled
- Export → export data based on current filter conditions

**【Layer 6: Delete Test Cases】**
Fixed template:
1. Delete confirmation prompt → business validation (e.g. associated records can't be deleted); confirmation message (e.g. "是否删除该记录？"); success prompt
2. Confirm delete → deleted successfully, list refreshes
3. Cancel delete → not deleted, data preserved
4. Business restriction → e.g. warehoused items can't be deleted, button grayed
5. Associated data check → associated records can't be deleted

### Field Validation Rule Library

Match field type → apply corresponding validation test cases. Always mention the field name in the test case.

**Text box:**
- Half-row: 50 char limit, excess can't be input
- Full-row: 100 char limit, excess can't be input
- Text area: 2000 char limit, shows "字数提示"; supports indent, line break, space; shows entered/2000 at bottom-left
- Special character check
- Excess characters can't be input

**Numeric input:**
- Only numbers, characters can't be input
- Precision: 6 decimals; total 20 digits (including decimal point), 13 integer + . + 6 decimal
- Unit label (万元)
- Thousand separator display
- Whether negative numbers are allowed (business-dependent)

**Dropdown single-select:**
- Fixed code values correct, can only select one
- Non-fixed code values, data source correct
- Default shows all
- Order matches requirement
- Supports keyword search input (if applicable)

**Dropdown multi-select:**
- Same as single-select but can select multiple

**Radio button:**
- Code values correct, can only select one

**Checkbox:**
- Code values correct, can select multiple

**Date picker:**
- Precision: year-month-day (or year-month-day hour-minute per requirement)
- Date range: end date >= start date

**File upload:**
- Supported format check
- Size limit check
- View method: download / online preview
- Batch upload support
- Filename length check

**System user selector:**
- Default shows current login user (if specified)
- Editable
- Supports search selection

### Conditional Logic Rules

When requirement has conditional show/hide logic, must cover:
1. Show/hide verification: trigger → field appears; cancel → field hides
2. Condition switch: switch A→B → field refreshes, old value cleared
3. Post-trigger required validation: shown required field empty → error message

### Quality Constraints

1. Every business rule must have corresponding test cases (traceable)
2. Every required field must have validation test cases
3. Conditional linkages must have forward + reverse test cases
4. Expected results must be specific (never just "correct", describe concrete behavior)
5. Field validation test cases must include the field name
6. Code value enumeration must be complete (if requirement lists 3 values, test cases must list all 3)

---

## Few-shot Examples

```text
【Example 1: List】
列表（XMGL-TQGL-L）
XMGL-TQGL-L_001|产业投资|项目管理|列表|列表|列表界面布局检查|查看项目管理列表|1.页面整体样式、排版、名称、字段显示正确，参考原型系统\n2.顺序：按新增时间，倒叙排列\n3.翻页正常
XMGL-TQGL-L_002|||||列表界面字段检查|查看项目管理列表|列表字段与原型一致，包括：企业简称、项目状态、出资主体、拟投资金额、是否SPV、首次出资日期、累计出资金额
XMGL-TQGL-L_003|||||列表界面按钮检查|查看项目管理列表|【项目投前管理】【项目投后管理】【搜索】【清空】【收起/展开】【投前管理】【暂缓】【终止】

【Example 2: Search】
查询（XMGL-TQGL-S）
XMGL-TQGL-S_001|产业投资|项目管理||查询|查询界面布局字段检查|查看查询区域|1.布局、字段参考原型\n2.关键字：项目名称\n3.筛选：出资主体、项目状态
XMGL-TQGL-S_002|||||空条件查询|直接点击【查询】按钮|查出全部数据
XMGL-TQGL-S_003|||||关键字精确查询|关键字输入项目名称全称，点击【查询】按钮|查出对应的项目

【Example 3: Field Validation】
XMGL-TQGL-XMGK_022||||编辑|合法性校验-金额|本轮融资金额(万元)、投前估值(万元)|需要关注是否可以输入负数
XMGL-TQGL-XMGK_023||||||6位小数；总数20位（含小数点）\n13位正数+【.】+6位小数
XMGL-TQGL-XMGK_024||||||单位：万元
XMGL-TQGL-XMGK_025||||||千分位符
XMGL-TQGL-XMGK_026||||||只能输入数字，字符不可输入

【Example 4: Save】
XMGL-TQGL-XMGK_048||||保存|保存功能校验||1.展示提示信息
XMGL-TQGL-XMGK_049||||||2.保存成功
XMGL-TQGL-XMGK_050||||保存|必填项校验||1.必填项校验成功，有必填标识符
XMGL-TQGL-XMGK_051||||||2.输入框提示正确，同原型
```

Note: within the same test point, subsequent sub-items (e.g. _049, _051) leave "测试点" and "用例名称" empty, only "预期结果" has the numbered continuation.
