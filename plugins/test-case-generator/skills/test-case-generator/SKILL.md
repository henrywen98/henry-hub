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

- **颗粒度原则（最高优先级）** — 每条测试用例**只测试一个独立功能点**。sop-layers.md 中每一层（L0-L6）列出的每个 sub-bullet 对应一条独立用例。**禁止**将多个检查点合并为一条多步骤用例；**禁止**将同类型同规则的多个字段合并为一条用例；**禁止**"下拉选项 >5 精简为首末中"。即使检查点相关或相似，也必须拆成独立用例。详见 sop-layers.md Writing Guidelines 的"颗粒度原则"。
- **自动化友好** — 生成的用例同时作为 Playwright 自动化测试的参考来源。1 条用例对应 1 个 test function / 1 个核心 assertion。`case_name` 必须足够具体以便脚本按名称定位（例如 `"企业全称-必填校验"` 而非 `"企业全称字段校验"`）。多步骤不等于多检查点：一条用例可以有多步 operation（点击 → 输入 → 提交），但只测试 1 个功能点。
- Read reference files from `${CLAUDE_PLUGIN_ROOT}/skills/test-case-generator/references/` as needed (sop-layers.md, json-schema.md, analysis-schema.md, example-analysis.json, example-output.json, excel-template-spec.md)
- Output ONLY a raw JSON array of test case objects (no wrapper, no markdown fences)
- Use "TEMP_NNN" as placeholder IDs (e.g., "TEMP_001", "TEMP_002")
- steps/expected: use `\n` between numbered items, each starting with `N.` (no space after number)
- precondition: include current page/dialog location, e.g., "用户已登录并打开新增弹窗"
- Follow the Writing Guidelines in sop-layers.md (note: "用例精简规则" has been removed; do NOT merge cases under any circumstance)
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
3. Identify `module_groups` — scan document for top-level functional modules, each getting its own group with `id`, `name`, `module_code`, `heading_text`
4. For each group: build `doc_sections`, `field_table` (with correct `type` and `interactions`), `dispatch` flags, and `business_rules_summary`
5. Write the result as JSON to `{cache_dir}/analysis.json`

**Critical instruction for the Analysis agent:** Scan the ENTIRE document from start to end. Every top-level functional module must be captured as a module_group. Do not stop after the first few modules. Count headings to verify all are covered.

**Critical instruction — heading_text 必须是字面文本**：`module_groups[].heading_text` 必须是文档中该模块标题行的**逐字复制**，包括所有空格、标点、编号格式。**不要**加任何正则字符（`^`、`\s`、`\d`、`+`、`*` 等）。如果文档里的标题是 `# 1 资产申请管理`，你就写 `# 1 资产申请管理`，一字不差。如果文档原文含有非换行空格 `\xa0` 或全角空格 `\u3000`，照抄即可（split 脚本会 normalize）。heading_text 必须在文档中**唯一匹配**，所以要包含足够的上下文（例如 `## 1.2 本级管理` 而不是 `## 1.2`，否则会和 `## 1.2.1` 碰撞）。详见 `analysis-schema.md` 中的 heading_text 示例。

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

Run the document splitting script. Use a cross-platform Python probe so Windows (where `python3` may not exist) also works:

```bash
PY=$(command -v python3 >/dev/null 2>&1 && echo python3 || echo python)
"$PY" "${CLAUDE_PLUGIN_ROOT}/scripts/split_doc.py" {cache_dir}/analysis.json {doc_md_path} {cache_dir}
```

This produces:
- `{cache_dir}/doc_common.md` — content before the first module
- `{cache_dir}/doc_{grp_id}.md` — common prefix + module content, one per group

If the script fails with `Cannot find heading_text: ...`, it will also output the 5 closest lines in the document as a diagnostic. This usually means the Analysis agent's `heading_text` is slightly off from the document original. Fix `{cache_dir}/analysis.json` manually and rerun this step.

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

Focus: per-field validation based on type (use the expanded field type taxonomy in sop-layers.md, including textarea, radio, checkbox, search_select, multi_dropdown, date_range). Cross-field interaction patterns (condition_show, condition_required, cascade_fill, inline_create). Uniqueness checks, submit-and-verify. Use `common_rules` values for field length/precision limits.

#### 字段遍历要求（严格执行）

**第一步 — Checklist 声明**：在开始生成用例前，先在思维中（不写入输出）列出 `field_table` 中所有字段名作为 checklist，例如：

```
[ ] 登记状态
[ ] 企业全称
[ ] 企业简称
[ ] 企业类型
...
```

**第二步 — 按序遍历**：严格按 `field_table` 数组顺序（即文档中字段出现的原始顺序）生成用例。对每个字段：

1. 查找其 `type` 对应的规则（参见 `sop-layers.md` L3）
2. **对该字段的每一条验证规则生成一条独立的测试用例**（不合并！见下文"颗粒度原则"）
3. 在 checklist 上标记该字段已覆盖

`sop-layers.md` L3 的"按字段类型分组"是**生成规则参考**（告诉你每种类型该测什么），**不是**组织结构。**不要**按字段类型聚合重排，也不要把所有文本字段放一起再把所有下拉放一起。

**第三步 — 覆盖校验**：生成完毕前检查 checklist，确认 `field_table` 的**每一个字段都至少出现在 1 条测试用例的 `test_point` 或 `case_name` 中**。

#### 颗粒度原则（严格执行）

每条测试用例**只测试一个独立功能点**。以下都是**禁止**的：

- ❌ 一个文本字段的"必填 / 长度 / 特殊字符 / 空格"合并为 1 条用例
- ❌ 多个文本字段合并为 1 条用例（即便类型和规则相同）
- ❌ 下拉选项 ">5 个只测首末中" 的精简
- ❌ 把需求文档中相邻的多个检查点塞进一条用例的 steps

应该是：

- ✅ 每个字段的每一条规则 = 1 条独立用例，`case_name` 形如：
  - `"企业全称-必填校验"`
  - `"企业全称-长度上限校验"`
  - `"企业全称-特殊字符校验"`
  - `"企业全称-空格校验"`
- ✅ 每个下拉选项 = 1 条独立用例（即使 >5 个，也要逐个测；若选项极多如 100+ 的行政区划，在需求未明确时标注 `[TODO: 选项数量确认测试策略]`）
- ✅ 跨字段交互（`condition_show` / `condition_required` / `cascade_fill` / `inline_create`）在遍历完所有字段后单独追加，每个交互场景也是 1 条独立用例

**成本提示**：本原则会让 Agent B 的输出用例数 2-4x 于 v3.0。这是**有意为之**，目的是为 Playwright 自动化引用提供足够的颗粒度。

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
2. **Read** `{cache_dir}/analysis.json` to get the group's `doc_sections` array and `field_table`
3. **Group by doc_section** — for each `doc_sections` entry (ordered by `doc_order`), collect all test cases whose `doc_section` matches. Within each group, maintain agent order (A → B → C → D)
4. **Handle unmatched** — test cases without a valid `doc_section` go into a final "其他" section
5. **Deduplicate** overlapping test cases within each group (same test_point + case_name)
6. **Build sections** — each `doc_section` group becomes one section. Title format: "{doc_sections[].title}（{module_code}）"
7. **Renumber** all IDs sequentially across all sections: `{module_code}_001`, `{module_code}_002`, ...
8. **Strip** the `doc_section` field from every test case (not needed in final output)
9. **Build the complete JSON** with meta + style (copy style block exactly from json-schema.md) + sections + merge_rules
10. **Write** to `{output_dir}/{module_code}_testcases.json`
11. **字段覆盖率校验**（仅当该 group 的 `dispatch.has_data_entry == true`）：
    - 从 `analysis.json` 读取该 group 的 `field_table[].name` 列表
    - 扫描所有合并后的测试用例，收集每条用例 `test_point` 和 `case_name` 中提到的字段名
    - 对 `field_table` 中的每个字段名，确认它至少出现在 1 条用例里
    - 若有字段未覆盖，在输出 JSON 的 `meta` 对象下新增 `coverage_warnings` 数组，每项格式：`"[TODO: 漏测字段 {field_name}]"`
    - 健康指标：预期每个字段出现在 **3 条以上**用例里（因为颗粒度原则要求每条规则一条独立用例）；若某字段 < 2 条，在 stderr 输出提醒但不阻塞
    - 如有任何 warning，同时在 stderr 输出提醒告知用户

Merge can run immediately after each group's agents complete — no need to wait for other groups.

## Step 5: Generate Excel (Per Group)

Run the conversion script for each group (orchestrator runs this directly, no Task needed). Use the same cross-platform Python probe:

```bash
PY=$(command -v python3 >/dev/null 2>&1 && echo python3 || echo python)
"$PY" "${CLAUDE_PLUGIN_ROOT}/scripts/convert_to_xlsx.py" {json_path} {output_xlsx_path}
```

- `{json_path}` = JSON from Step 4 for this group
- `{output_xlsx_path}` = `{output_dir}/{module_code}_testcases.xlsx`
- If `openpyxl` is missing: install via `"$PY" -m pip install openpyxl`
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
