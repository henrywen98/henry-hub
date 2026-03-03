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
**Output:** One or more formatted Excel files (.xlsx) matching company template, one per module group

## Orchestration Overview

This skill runs as a lightweight orchestrator. Each heavy phase is dispatched as a Task sub-agent with isolated context. The orchestrator's own context stays under ~5KB.

```
Orchestrator
 ├─ Read document (pandoc/Read — lightweight, no Task needed)
 ├─ Task: Global Analysis → writes cache/analysis.json
 ├─ Read analysis.json → report module groups to user
 ├─ Bash: python3 split_doc.py → split document per group
 ├─ For each module_group:
 │   ├─ Task[parallel]: Agent A/B/C/D → write cache/partial_grpN_*.json
 │   ├─ Task: Merge → writes {output}/{code}_testcases.json
 │   └─ Bash: python3 convert_to_xlsx.py
 ├─ Bash: rm -rf cache_dir
 └─ Summary report
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
- **文档章节标签:** 每条用例必须包含 `doc_section` 字段，值为该 group 的 `doc_sections[].id`。根据该用例测试的页面/功能，匹配最相关的 doc_section。
- **独立可执行:** 禁止"同xxx"引用。每条用例的 steps 和 expected 必须完整具体，不得引用其他用例。
- **预期结果明确:** 禁止"A 或 B"式模糊描述。需求未明确时使用 `[TODO:待确认]`。

## Step 1: Read Requirement Document

Read the requirement document provided by the user. This runs in the orchestrator (no Task needed).

- **Word (.docx):** Use `pandoc -f docx -t markdown "$doc_path"` (fallback: python-docx)
- **PDF:** Use PyMuPDF (`python3 -c "import fitz; ..."`) or the `pdf` skill if installed
- **Text/Markdown:** Read directly with the Read tool
- **No path given:** Ask user to paste the requirement content

Save the converted markdown to a temp file for sub-agents to read.

After reading, confirm: "已读取需求文档：{filename}，共 N 行。开始分析..."

Set up the cache directory:
```
cache_dir = {output_dir}/.testcase-cache/
mkdir -p {cache_dir}
```

Where `output_dir` = same directory as input doc, or cwd if content was pasted.

## Step 2: Global Analysis (Task sub-agent)

Dispatch a Task sub-agent with:
- **Prompt:** Include the full requirement document text, and instruct it to read `${CLAUDE_PLUGIN_ROOT}/skills/test-case-generator/references/analysis-schema.md` for the output format
- **Goal:** Analyze the requirement and write `{cache_dir}/analysis.json`
- **subagent_type:** `general-purpose`

The agent must:
1. Extract `source_doc`
2. Extract `common_rules` from the document's public/common section (use defaults from analysis-schema.md if not found)
3. Identify `module_groups` — scan document for top-level functional modules, each getting its own group with `id`, `name`, `module_code`, `heading_pattern`
4. For each group: build `doc_sections`, `field_table` (with correct `type` and `interactions`), `dispatch` flags, and `business_rules_summary`
5. Write the result as JSON to `{cache_dir}/analysis.json`

**Critical instruction for the Analysis agent:** Scan the ENTIRE document from start to end. Every top-level functional module must be captured as a module_group. Do not stop after the first few modules. Count headings to verify all are covered.

After the Task completes, the orchestrator:
1. Reads `{cache_dir}/analysis.json`
2. Reports to user:
   ```
   源文档: {source_doc}
   识别到 {N} 个模块:

     模块           代码      字段数  章节数  派遣
     {name}         {code}    {F}     {S}     A + B + C + D
     {name}         {code}    {F}     {S}     A + B + D
     ...

   开始切割文档并派遣子代理...
   ```

## Step 2.5: Split Document

Run the document splitting script:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/split_doc.py {cache_dir}/analysis.json {doc_md_path} {cache_dir}
```

This produces:
- `{cache_dir}/doc_common.md` — content before the first module
- `{cache_dir}/doc_{grp_id}.md` — common prefix + module content, one per group

## Step 3: Dispatch Sub-Agents (Per Group)

For each `module_group` in `analysis.json`, dispatch all applicable agents in a **SINGLE message with multiple parallel Task tool calls**.

Each agent's Task prompt includes:
- The split document path: `{cache_dir}/doc_{grp_id}.md` (agent reads it via Read tool)
- The group's `name` and `module_code`
- The group's `field_table` (for Agent B/C)
- The group's `business_rules_summary` (for Agent D)
- The group's `doc_sections` (for all agents — used for `doc_section` tagging)
- The `common_rules` from analysis.json (injected at top of prompt)
- Reference file paths: `${CLAUDE_PLUGIN_ROOT}/skills/test-case-generator/references/sop-layers.md`, `${CLAUDE_PLUGIN_ROOT}/skills/test-case-generator/references/json-schema.md`, `${CLAUDE_PLUGIN_ROOT}/skills/test-case-generator/references/example-output.json`
- Output path: `{cache_dir}/partial_{grp_id}_{agent_letter}.json`
- The Global Rules above

Process groups sequentially (one wave per group, 4 agents per wave):

```
Wave 1: Group grp_1 → Agent A/B/C/D (parallel) → wait for completion
Wave 2: Group grp_2 → Agent A/B/C/D (parallel) → wait for completion
...
```

### Agent A — L0+L1+L2 (Always dispatched)

Layers: L0 (基础验证), L1 (展示), L2 (交互筛选).

Focus: menu/data permissions, UI standards, page layout, list fields/buttons, pagination, sorting, empty state, search/filter/date-range/combo-query/reset.

**Additional instruction:** 对弹窗/模态框/抽屉/Tab 内的列表，同样需按 L1(布局/字段/分页/排序/空数据) 和 L2(搜索/筛选/组合查询/重置) 生成用例。

Generate test cases following each applicable guideline in L0, L1, L2. Skip items that don't apply. Write output to `{cache_dir}/partial_{grp_id}_a.json`.

### Agent B — L3 (If has_data_entry)

Layer: L3 (数据输入).

Focus: per-field validation based on type (use the expanded field type taxonomy in sop-layers.md, including textarea, radio, checkbox, search_select, multi_dropdown, date_range). Cross-field interaction patterns (condition_show, condition_required, cascade_fill, inline_create). Uniqueness checks, submit-and-verify. Follow 用例精简规则. Use `common_rules` values for field length/precision limits.

Write output to `{cache_dir}/partial_{grp_id}_b.json`.

### Agent C — L4 (If has_data_modify)

Layer: L4 (数据修改).

Focus: edit recall display, editable vs read-only fields, status-based edit restrictions, post-modification verification. Do NOT duplicate UI button checks already covered by Agent A.

Write output to `{cache_dir}/partial_{grp_id}_c.json`.

### Agent D — L5+L6 (If has_business_logic or has_data_cleanup)

Layers: L5 (业务规则) + L6 (数据清理).

Focus L5: approval flows (submit/approve/reject/withdraw), state transitions, data linkage, calculation rules, draft/temp state (if mentioned in requirement). Focus L6: delete permissions, confirmation dialogs, status restrictions, post-delete verification, cascade effects. Do NOT duplicate UI button checks already covered by Agent A. Skip layers that don't apply.

Write output to `{cache_dir}/partial_{grp_id}_d.json`.

## Step 4: Merge Results (Per Group)

After each group's sub-agents complete, dispatch a merge Task:
- **Prompt:** Read partial JSON files for that group and analysis.json from cache_dir, read json-schema.md for the full output format. Use the group's doc_sections to determine section ordering.
- **subagent_type:** `general-purpose`

The merge agent must:
1. **Read** all partial JSON files for this group: `partial_{grp_id}_a.json`, `partial_{grp_id}_b.json` (if exists), `partial_{grp_id}_c.json` (if exists), `partial_{grp_id}_d.json` (if exists)
2. **Read** `{cache_dir}/analysis.json` to get the group's `doc_sections` array
3. **Group by doc_section** — for each `doc_sections` entry (ordered by `doc_order`), collect all test cases whose `doc_section` matches. Within each group, maintain agent order (A → B → C → D)
4. **Handle unmatched** — test cases without a valid `doc_section` go into a final "其他" section
5. **Deduplicate** overlapping test cases within each group (same test_point + case_name)
6. **Build sections** — each `doc_section` group becomes one section. Title format: "{doc_sections[].title}（{module_code}）"
7. **Renumber** all IDs sequentially across all sections: `{module_code}_001`, `{module_code}_002`, ...
8. **Strip** the `doc_section` field from every test case (not needed in final output)
9. **Build the complete JSON** with meta + style (copy style block exactly from json-schema.md) + sections + merge_rules
10. **Write** to `{output_dir}/{module_code}_testcases.json`

Merge can run immediately after each group's agents complete — no need to wait for other groups.

## Step 5: Generate Excel (Per Group)

Run the conversion script for each group (orchestrator runs this directly, no Task needed):

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/convert_to_xlsx.py {json_path} {output_xlsx_path}
```

- `{json_path}` = JSON from Step 4 for this group
- `{output_xlsx_path}` = `{output_dir}/{module_code}_testcases.xlsx`
- If `openpyxl` is missing: `pip3 install openpyxl`
- For Excel format details, see `${CLAUDE_PLUGIN_ROOT}/skills/test-case-generator/references/excel-template-spec.md`

## Step 6: Cleanup and Report

```bash
rm -rf {cache_dir}
```

Report:
```
测试用例生成完成！
源文档: {source_doc}
共识别 {N} 个模块:

  模块           文件                      用例数   子模块
  {name}         {code}_testcases.xlsx     {C}      {S}
  {name}         {code}_testcases.xlsx     {C}      {S}
  ...

总计: {total} 条测试用例
```

Open all generated Excel files: `open {output_dir}/*_testcases.xlsx`
