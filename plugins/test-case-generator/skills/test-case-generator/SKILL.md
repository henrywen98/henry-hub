---
name: test-case-generator
description: >-
  Generate structured test cases from requirement documents, create functional test cases,
  convert requirements to test cases in Excel format.
  当用户说「生成测试用例」「需求文档转测试用例」「从需求生成用例」「写测试用例」时触发。
  Supports Word/PDF/text input, outputs formatted .xlsx with 17-column company template.
user-invocable: true
arguments:
  - name: doc_path
    description: "Path to requirement document (Word/PDF/text), or omit to paste content directly"
    required: false
---

# Test Case Generation Skill

Generate standardized functional test cases from requirement documents using a 7-layer SOP framework.

**Input:** Requirement document (Word/PDF/text) or pasted content
**Output:** Formatted Excel file (.xlsx) matching company template

## Orchestration Overview

This skill runs as a lightweight orchestrator. Each heavy phase is dispatched as a Task sub-agent with isolated context. The orchestrator's own context stays under ~5KB.

```
Orchestrator
 ├─ Read document (pandoc/Read — lightweight, no Task needed)
 ├─ Task: Analyze → writes cache/analysis.json
 ├─ Read analysis.json (~2KB) → decide dispatch, report to user
 ├─ Task[parallel]: Agent A/B/C/D → write cache/partial_*.json
 ├─ Task: Merge → writes {output}/{code}_testcases.json
 ├─ Bash: python3 convert_to_xlsx.py
 └─ Bash: rm -rf cache_dir
```

## Global Rules for All Sub-Agents

All Task sub-agents share these rules:

- Read reference files from `${CLAUDE_PLUGIN_ROOT}/skills/test-case-generator/references/` as needed (sop-layers.md, json-schema.md, analysis-schema.md, example-analysis.json, example-output.json, excel-template-spec.md)
- Output ONLY a raw JSON array of test case objects (no wrapper, no markdown fences)
- Use "TEMP_NNN" as placeholder IDs (e.g., "TEMP_001", "TEMP_002")
- steps/expected: use `\n` between numbered items, each starting with `N.` (no space after number)
- precondition: include current page/dialog location, e.g., "用户已登录并打开新增弹窗"
- Follow the Writing Guidelines and 用例精简规则 in sop-layers.md
- **去重原则:** UI 呈现（按钮显示/隐藏/置灰/文案）由 Agent A 覆盖。Agent C/D 在步骤中可引用按钮状态作为前提，但不生成重复的 UI 检查用例。

## Step 1: Read Requirement Document

Read the requirement document provided by the user. This runs in the orchestrator (no Task needed).

- **Word (.docx):** Use `pandoc -f docx -t markdown "$doc_path"` (fallback: python-docx)
- **PDF:** Use PyMuPDF (`python3 -c "import fitz; ..."`) or the `pdf` skill if installed
- **Text/Markdown:** Read directly with the Read tool
- **No path given:** Ask user to paste the requirement content

After reading, confirm: "已读取需求文档：{filename}，共 N 页/段落。开始分析..."

Set up the cache directory:
```
cache_dir = {output_dir}/.testcase-cache/
mkdir -p {cache_dir}
```

Where `output_dir` = same directory as input doc, or cwd if content was pasted.

## Step 2: Structural Analysis (Task sub-agent)

Dispatch a Task sub-agent with:
- **Prompt:** Include the full requirement document text, and instruct it to read `${CLAUDE_PLUGIN_ROOT}/skills/test-case-generator/references/analysis-schema.md` for the output format
- **Goal:** Analyze the requirement and write `{cache_dir}/analysis.json`
- **subagent_type:** `general-purpose`

The agent must:
1. Extract module_name, module_code, source_doc
2. Build the field_table with correct `type` and `interactions` values
3. Determine dispatch flags (has_ui, has_data_entry, has_data_modify, has_business_logic, has_data_cleanup)
4. Summarize business rules
5. List filter_fields and list_fields
6. Write the result as JSON to `{cache_dir}/analysis.json`

After the Task completes, the orchestrator:
1. Reads `{cache_dir}/analysis.json` (~2KB)
2. Reports to user:
   ```
   模块名称: {module_name}
   模块代码: {module_code}
   识别到 {N} 个字段, 其中 {M} 个有跨字段交互
   派遣方案:
   - Agent A: L0+L1+L2 (数据展示/筛选)
   - Agent B: L3 (数据新增) — Yes/No
   - Agent C: L4 (数据编辑) — Yes/No
   - Agent D: L5+L6 (业务规则/删除) — Yes/No
   正在并行派遣子代理...
   ```

## Step 3: Dispatch Sub-Agents (PARALLEL)

Dispatch all applicable agents in a **SINGLE message with multiple parallel Task tool calls**.

Each agent's Task prompt includes:
- The document path (agent reads it themselves via Read tool)
- module_name and module_code from analysis.json
- The field_table from analysis.json (for Agent B/C)
- The business_rules_summary from analysis.json (for Agent D)
- Reference file paths: `${CLAUDE_PLUGIN_ROOT}/skills/test-case-generator/references/sop-layers.md`, `${CLAUDE_PLUGIN_ROOT}/skills/test-case-generator/references/json-schema.md`, `${CLAUDE_PLUGIN_ROOT}/skills/test-case-generator/references/example-output.json`
- Output path: `{cache_dir}/partial_{agent_letter}.json`
- The Global Rules above

### Agent A — L0+L1+L2 (Always dispatched)

Layers: L0 (基础验证), L1 (展示), L2 (交互筛选).

Focus: menu/data permissions, UI standards, page layout, list fields/buttons, pagination, sorting, empty state, search/filter/date-range/combo-query/reset.

**Additional instruction:** 对弹窗/模态框/抽屉/Tab 内的列表，同样需按 L1(布局/字段/分页/排序/空数据) 和 L2(搜索/筛选/组合查询/重置) 生成用例。

Generate test cases following each applicable guideline in L0, L1, L2. Skip items that don't apply. Write output to `{cache_dir}/partial_a.json`.

### Agent B — L3 (If has_data_entry)

Layer: L3 (数据输入).

Focus: per-field validation based on type (use the expanded field type taxonomy in sop-layers.md, including textarea, radio, checkbox, search_select, multi_dropdown, date_range). Cross-field interaction patterns (condition_show, condition_required, cascade_fill, inline_create). Uniqueness checks, submit-and-verify. Follow 用例精简规则.

Write output to `{cache_dir}/partial_b.json`.

### Agent C — L4 (If has_data_modify)

Layer: L4 (数据修改).

Focus: edit recall display, editable vs read-only fields, status-based edit restrictions, post-modification verification. Do NOT duplicate UI button checks already covered by Agent A.

Write output to `{cache_dir}/partial_c.json`.

### Agent D — L5+L6 (If has_business_logic or has_data_cleanup)

Layers: L5 (业务规则) + L6 (数据清理).

Focus L5: approval flows (submit/approve/reject/withdraw), state transitions, data linkage, calculation rules, draft/temp state (if mentioned in requirement). Focus L6: delete permissions, confirmation dialogs, status restrictions, post-delete verification, cascade effects. Do NOT duplicate UI button checks already covered by Agent A. Skip layers that don't apply.

Write output to `{cache_dir}/partial_d.json`.

## Step 4: Merge Results (Task sub-agent)

After all sub-agents complete, dispatch a merge Task with:
- **Prompt:** Read partial JSON files from cache_dir, read json-schema.md for the full output format
- **subagent_type:** `general-purpose`

The merge agent must:
1. **Read** all partial JSON files: `partial_a.json`, `partial_b.json` (if exists), `partial_c.json` (if exists), `partial_d.json` (if exists)
2. **Concatenate** into a single test_cases array (order: A → B → C → D)
3. **Deduplicate** overlapping test cases (same test_point + case_name)
4. **Group into sections** by `sub_module` — each unique sub_module becomes a section
5. **Renumber** all IDs sequentially: `{module_code}_001`, `{module_code}_002`, ...
6. **Build the complete JSON** with meta + style (copy style block exactly from json-schema.md) + sections + merge_rules
7. **Write** to `{output_dir}/{module_code}_testcases.json`

## Step 5: Generate Excel

Run the conversion script (orchestrator runs this directly, no Task needed):

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/convert_to_xlsx.py {json_path} {output_xlsx_path}
```

- `{json_path}` = JSON from Step 4
- `{output_xlsx_path}` = `{output_dir}/{module_code}_testcases.xlsx`
- If `openpyxl` is missing: `pip3 install openpyxl`
- For Excel format details, see `${CLAUDE_PLUGIN_ROOT}/skills/test-case-generator/references/excel-template-spec.md`

## Step 6: Cleanup and Report

```bash
rm -rf {cache_dir}
```

Report:
```
测试用例生成完成!
- JSON: {json_path}
- Excel: {output_xlsx_path}
- 共生成 {N} 条测试用例，覆盖 {M} 个子模块
```

Open the file: `open {output_xlsx_path}`
