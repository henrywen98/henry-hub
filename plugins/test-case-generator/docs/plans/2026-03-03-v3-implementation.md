# test-case-generator v3.0 Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Upgrade test-case-generator to handle large requirement documents by splitting into module groups, each independently processed with A/B/C/D agents and output as separate Excel files.

**Architecture:** Global Analysis identifies module groups and common rules. A Python script splits the document by group. Each group independently runs the full A/B/C/D agent pipeline and produces its own Excel. Unified flow for all document sizes.

**Tech Stack:** Python 3 (split_doc.py), Claude Code sub-agents, openpyxl

---

### Task 1: Update analysis-schema.md

**Files:**
- Modify: `plugins/test-case-generator/skills/test-case-generator/references/analysis-schema.md`

**Step 1: Rewrite analysis-schema.md with new schema**

Replace the entire schema with the v3.0 format. Key changes:
- Remove top-level `module_name`, `module_code`, `dispatch`, `field_table`, `business_rules_summary`, `filter_fields`, `list_fields`, `doc_sections`
- Add top-level `source_doc`, `common_rules`, `module_groups[]`
- Each `module_groups[]` entry contains: `id`, `name`, `module_code`, `heading_pattern`, `doc_sections[]`, `field_table[]`, `dispatch`, `business_rules_summary`

New file content:

```markdown
# Analysis JSON Schema

Phase 2 outputs `analysis.json` to the cache directory. All subsequent phases read this file as their contract.

## Schema

\```json
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
      "heading_pattern": "string — 文档中该模块的标题行正则锚点, e.g. '## 1.2 本级管理'",
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
\```

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

**heading_pattern：**
- 该模块在 markdown 文档中的标题行文本（含 ## 前缀）
- 用于 split_doc.py 定位切割点
- 必须能在文档中唯一匹配

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
```

**Step 2: Update example-analysis.json**

Rewrite to match the new schema, using the existing "资源池" example wrapped in module_groups:

```json
{
  "source_doc": "需求文档.docx",
  "common_rules": {
    "text_half_line_max": 50,
    "text_full_line_max": 100,
    "textarea_max": 2000,
    "amount_decimal": 2,
    "amount_total_digits": 15,
    "percentage_max": 100,
    "pagination_default": 10,
    "pagination_options": [10, 20, 50, 100]
  },
  "module_groups": [
    {
      "id": "grp_1",
      "name": "资源池",
      "module_code": "JJRCGL-GSBG",
      "heading_pattern": "## 1.1 资源池",
      "doc_sections": [
        { "id": "sec_01", "title": "资源池列表", "heading_level": 2, "page_type": "list", "doc_order": 1 },
        { "id": "sec_02", "title": "新增资源池", "heading_level": 2, "page_type": "form", "doc_order": 2 },
        { "id": "sec_03", "title": "编辑资源池", "heading_level": 2, "page_type": "form", "doc_order": 3 },
        { "id": "sec_04", "title": "入库审批", "heading_level": 2, "page_type": "approval", "doc_order": 4 }
      ],
      "field_table": [
        { "name": "登记状态", "type": "radio", "required": true, "max_length": null, "rules": "已注册/未注册，影响企业全称输入方式", "interactions": ["condition_show"] },
        { "name": "企业全称", "type": "search_select", "required": true, "max_length": 200, "rules": "已注册时从工商库搜索选择, 未注册时手动输入", "interactions": ["condition_show", "cascade_fill"] },
        { "name": "企业简称", "type": "text", "required": true, "max_length": 50, "rules": "已注册时自动填充, 可手动修改", "interactions": ["cascade_fill"] },
        { "name": "企业类型", "type": "dropdown", "required": true, "max_length": null, "rules": "选项: 参股基金/参股基金管理人/股权项目", "interactions": [] },
        { "name": "统一社会信用代码", "type": "text", "required": false, "max_length": 18, "rules": "已注册时自动填充且不可编辑", "interactions": ["cascade_fill"] },
        { "name": "登记机关", "type": "text", "required": false, "max_length": 100, "rules": "已注册时自动填充且不可编辑", "interactions": ["cascade_fill"] }
      ],
      "dispatch": {
        "has_ui": true,
        "has_data_entry": true,
        "has_data_modify": true,
        "has_business_logic": true,
        "has_data_cleanup": false
      },
      "business_rules_summary": "入库审批流程: 提交→审批→入库; 入库后部分字段不可编辑; 未入库状态可编辑/删除"
    }
  ]
}
```

**Step 3: Commit**

```bash
git add plugins/test-case-generator/skills/test-case-generator/references/analysis-schema.md
git add plugins/test-case-generator/skills/test-case-generator/references/example-analysis.json
git commit -m "feat(test-case-generator): update analysis schema for v3.0 module groups"
```

---

### Task 2: Create split_doc.py

**Files:**
- Create: `plugins/test-case-generator/scripts/split_doc.py`

**Step 1: Write the test**

Create `plugins/test-case-generator/scripts/test_split_doc.py`:

```python
#!/usr/bin/env python3
"""Tests for split_doc.py"""
import json
import os
import tempfile
import pytest
from split_doc import split_document


@pytest.fixture
def sample_doc(tmp_path):
    """Create a sample markdown document with multiple modules."""
    content = """# 投资管理系统

## 公共说明

文本框最大50字。金额精度6位小数。

## 1.1 本级管理

### 基金列表

本级管理的基金列表页面...

### 新增基金

新增基金的表单...

## 1.2 载体管理

### 载体列表

载体管理的列表页面...

### 新增载体

新增载体的表单...

## 1.3 子基金投资

### 子基金列表

子基金投资的列表页面...
"""
    doc_path = tmp_path / "test_doc.md"
    doc_path.write_text(content, encoding="utf-8")
    return str(doc_path)


@pytest.fixture
def sample_analysis(tmp_path):
    """Create a sample analysis.json."""
    analysis = {
        "source_doc": "test_doc.md",
        "common_rules": {},
        "module_groups": [
            {"id": "grp_1", "name": "本级管理", "module_code": "BJGL", "heading_pattern": "## 1.1 本级管理"},
            {"id": "grp_2", "name": "载体管理", "module_code": "ZTGL", "heading_pattern": "## 1.2 载体管理"},
            {"id": "grp_3", "name": "子基金投资", "module_code": "ZJTZ", "heading_pattern": "## 1.3 子基金投资"},
        ],
    }
    analysis_path = tmp_path / "analysis.json"
    analysis_path.write_text(json.dumps(analysis, ensure_ascii=False), encoding="utf-8")
    return str(analysis_path)


def test_split_creates_common_and_group_files(sample_doc, sample_analysis, tmp_path):
    output_dir = str(tmp_path / "output")
    os.makedirs(output_dir)
    split_document(sample_analysis, sample_doc, output_dir)

    assert os.path.exists(os.path.join(output_dir, "doc_common.md"))
    assert os.path.exists(os.path.join(output_dir, "doc_grp_1.md"))
    assert os.path.exists(os.path.join(output_dir, "doc_grp_2.md"))
    assert os.path.exists(os.path.join(output_dir, "doc_grp_3.md"))


def test_common_contains_public_section(sample_doc, sample_analysis, tmp_path):
    output_dir = str(tmp_path / "output")
    os.makedirs(output_dir)
    split_document(sample_analysis, sample_doc, output_dir)

    common = open(os.path.join(output_dir, "doc_common.md"), encoding="utf-8").read()
    assert "公共说明" in common
    assert "文本框最大50字" in common
    assert "本级管理的基金列表" not in common


def test_group_file_contains_common_prefix(sample_doc, sample_analysis, tmp_path):
    output_dir = str(tmp_path / "output")
    os.makedirs(output_dir)
    split_document(sample_analysis, sample_doc, output_dir)

    grp1 = open(os.path.join(output_dir, "doc_grp_1.md"), encoding="utf-8").read()
    # Group file should contain common section + its own content
    assert "公共说明" in grp1
    assert "本级管理的基金列表" in grp1
    assert "载体管理的列表页面" not in grp1


def test_last_group_captures_remaining(sample_doc, sample_analysis, tmp_path):
    output_dir = str(tmp_path / "output")
    os.makedirs(output_dir)
    split_document(sample_analysis, sample_doc, output_dir)

    grp3 = open(os.path.join(output_dir, "doc_grp_3.md"), encoding="utf-8").read()
    assert "子基金投资的列表页面" in grp3


def test_single_group(tmp_path):
    """Single module_group should still produce common + group file."""
    doc = "# 系统\n\n## 公共\n\n说明\n\n## 1.1 资源池\n\n内容\n"
    doc_path = tmp_path / "doc.md"
    doc_path.write_text(doc, encoding="utf-8")

    analysis = {
        "source_doc": "doc.md",
        "common_rules": {},
        "module_groups": [
            {"id": "grp_1", "name": "资源池", "module_code": "ZYC", "heading_pattern": "## 1.1 资源池"}
        ],
    }
    analysis_path = tmp_path / "analysis.json"
    analysis_path.write_text(json.dumps(analysis, ensure_ascii=False), encoding="utf-8")

    output_dir = str(tmp_path / "output")
    os.makedirs(output_dir)
    split_document(str(analysis_path), str(doc_path), output_dir)

    assert os.path.exists(os.path.join(output_dir, "doc_common.md"))
    assert os.path.exists(os.path.join(output_dir, "doc_grp_1.md"))
    grp1 = open(os.path.join(output_dir, "doc_grp_1.md"), encoding="utf-8").read()
    assert "说明" in grp1
    assert "内容" in grp1
```

**Step 2: Run tests to verify they fail**

Run: `cd plugins/test-case-generator/scripts && python3 -m pytest test_split_doc.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'split_doc'`

**Step 3: Implement split_doc.py**

```python
#!/usr/bin/env python3
"""Split a markdown document into per-module-group files based on analysis.json.

Usage: python split_doc.py <analysis.json> <document.md> <output_dir>

Outputs:
  output_dir/doc_common.md   — content before the first module group
  output_dir/doc_grp_N.md    — common prefix + module N content
"""
import json
import os
import re
import sys


def split_document(analysis_path, doc_path, output_dir):
    with open(analysis_path, "r", encoding="utf-8") as f:
        analysis = json.load(f)

    with open(doc_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    groups = analysis["module_groups"]

    # Find the line index where each group's heading starts
    boundaries = []
    for grp in groups:
        pattern = re.escape(grp["heading_pattern"])
        found = False
        for i, line in enumerate(lines):
            if re.match(pattern, line.strip()):
                boundaries.append(i)
                found = True
                break
        if not found:
            # Fallback: search for the heading text without exact prefix match
            heading_text = grp["heading_pattern"].lstrip("# ").strip()
            for i, line in enumerate(lines):
                if heading_text in line:
                    boundaries.append(i)
                    found = True
                    break
        if not found:
            raise ValueError(f"Cannot find heading pattern '{grp['heading_pattern']}' in document")

    # Common section: everything before the first group
    common_end = boundaries[0] if boundaries else len(lines)
    common_lines = lines[:common_end]
    common_text = "".join(common_lines).rstrip() + "\n"

    # Write doc_common.md
    with open(os.path.join(output_dir, "doc_common.md"), "w", encoding="utf-8") as f:
        f.write(common_text)

    # Write each group file: common + group content
    for idx, grp in enumerate(groups):
        start = boundaries[idx]
        end = boundaries[idx + 1] if idx + 1 < len(boundaries) else len(lines)
        group_lines = lines[start:end]
        group_text = common_text + "\n" + "".join(group_lines).rstrip() + "\n"

        with open(os.path.join(output_dir, f"doc_{grp['id']}.md"), "w", encoding="utf-8") as f:
            f.write(group_text)


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print(f"Usage: {sys.argv[0]} <analysis.json> <document.md> <output_dir>")
        sys.exit(1)
    split_document(sys.argv[1], sys.argv[2], sys.argv[3])
    print(f"Split complete. Files written to {sys.argv[3]}")
```

**Step 4: Run tests to verify they pass**

Run: `cd plugins/test-case-generator/scripts && python3 -m pytest test_split_doc.py -v`
Expected: All 5 tests PASS

**Step 5: Commit**

```bash
git add plugins/test-case-generator/scripts/split_doc.py
git add plugins/test-case-generator/scripts/test_split_doc.py
git commit -m "feat(test-case-generator): add split_doc.py for document splitting"
```

---

### Task 3: Update sop-layers.md with new global rules

**Files:**
- Modify: `plugins/test-case-generator/skills/test-case-generator/references/sop-layers.md` (lines 240-258, Writing Guidelines section)

**Step 1: Add two new rules to Writing Guidelines**

Append after the existing "用例精简规则" section (line 258):

```markdown
### 独立可执行原则
- **禁止"同xxx"引用** — 每条用例必须独立可执行。不得使用"同载体管理认缴信息"等引用描述代替实际的 steps 和 expected。相似模块可减少用例数量，但每条用例的 steps 和 expected 必须完整具体。
- **预期结果禁止"A或B"式描述** — 预期结果必须明确唯一。如需求未明确预期行为，使用 `[TODO:待确认具体行为]` 标注，不使用"显示A或B"等模糊表述。

### 公共规则引用
- 当 agent prompt 中包含 `common_rules` 时，字段验证用例必须引用其中的具体数值（如字数上限、金额精度），不使用默认假设值
```

**Step 2: Commit**

```bash
git add plugins/test-case-generator/skills/test-case-generator/references/sop-layers.md
git commit -m "feat(test-case-generator): add independent-execution and common-rules guidelines"
```

---

### Task 4: Rewrite SKILL.md

**Files:**
- Modify: `plugins/test-case-generator/skills/test-case-generator/SKILL.md`

This is the core task. Rewrite the entire orchestration flow to use the unified module-group pipeline.

**Step 1: Rewrite SKILL.md**

Key changes from v2.0:
- Step 2: Analysis prompt instructs agent to output `module_groups` format (not flat)
- Step 2 orchestrator report: list all module groups with their dispatch flags
- Step 2.5 (new): Run `split_doc.py`
- Step 3: Loop over each `module_group`, dispatching A/B/C/D per group (one wave per group)
- Step 4: Loop over each group, dispatch independent merge agent
- Step 5: Loop over each group, generate Excel
- Step 6: Cleanup + summary report listing all generated files

Full SKILL.md content (see design doc for detailed architecture):

```markdown
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

\```
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
\```

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
\```
cache_dir = {output_dir}/.testcase-cache/
mkdir -p {cache_dir}
\```

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
   \```
   源文档: {source_doc}
   识别到 {N} 个模块:

     模块           代码      字段数  章节数  派遣
     {name}         {code}    {F}     {S}     A + B + C + D
     {name}         {code}    {F}     {S}     A + B + D
     ...

   开始切割文档并派遣子代理...
   \```

## Step 2.5: Split Document

Run the document splitting script:

\```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/split_doc.py {cache_dir}/analysis.json {doc_md_path} {cache_dir}
\```

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

\```
Wave 1: Group grp_1 → Agent A/B/C/D (parallel) → wait for completion
Wave 2: Group grp_2 → Agent A/B/C/D (parallel) → wait for completion
...
\```

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

\```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/convert_to_xlsx.py {json_path} {output_xlsx_path}
\```

- `{json_path}` = JSON from Step 4 for this group
- `{output_xlsx_path}` = `{output_dir}/{module_code}_testcases.xlsx`
- If `openpyxl` is missing: `pip3 install openpyxl`
- For Excel format details, see `${CLAUDE_PLUGIN_ROOT}/skills/test-case-generator/references/excel-template-spec.md`

## Step 6: Cleanup and Report

\```bash
rm -rf {cache_dir}
\```

Report:
\```
测试用例生成完成！
源文档: {source_doc}
共识别 {N} 个模块:

  模块           文件                      用例数   子模块
  {name}         {code}_testcases.xlsx     {C}      {S}
  {name}         {code}_testcases.xlsx     {C}      {S}
  ...

总计: {total} 条测试用例
\```

Open all generated Excel files: `open {output_dir}/*_testcases.xlsx`
```

**Step 2: Verify SKILL.md is well-formed**

Check: frontmatter has name + description, body references all needed paths with `${CLAUDE_PLUGIN_ROOT}`, all steps numbered sequentially, no broken markdown.

**Step 3: Commit**

```bash
git add plugins/test-case-generator/skills/test-case-generator/SKILL.md
git commit -m "feat(test-case-generator): rewrite SKILL.md for v3.0 unified group pipeline"
```

---

### Task 5: Update plugin.json version

**Files:**
- Modify: `plugins/test-case-generator/.claude-plugin/plugin.json`

**Step 1: Bump version to 3.0.0**

```json
{
  "name": "test-case-generator",
  "version": "3.0.0",
  "description": "Generate structured test cases from requirement documents using 7-layer SOP framework. Per-module-group parallel sub-agents + JSON intermediate + formatted Excel output."
}
```

**Step 2: Commit**

```bash
git add plugins/test-case-generator/.claude-plugin/plugin.json
git commit -m "chore(test-case-generator): bump version to 3.0.0"
```

---

### Task 6: Integration test with the investment management doc

**Files:** None (test only)

**Step 1: Reinstall the plugin**

```bash
# Clear the cache so skill reloads
rm -rf ~/.claude/plugins/cache/henry-hub/test-case-generator/
```

**Step 2: Run the skill on the test document**

In a new Claude Code session:
```
/test-case-generator @国家制造业转型升级基金设计文档-投资管理.docx
```

**Step 3: Verify results**

Check:
- [ ] Analysis identifies all module groups (本级管理, 载体管理, 子基金投资, 股权投资项目, and any others)
- [ ] split_doc.py successfully splits the document
- [ ] Each group generates its own Excel file
- [ ] No module is missing from output
- [ ] Total test case count significantly higher than v2.0's 506
- [ ] Each section has >5 test cases (no skeleton sections)
- [ ] No "同xxx" references in any test case
- [ ] L0 cases present in most sections

**Step 4: Commit test results (if any fixtures added)**

```bash
git add -A && git commit -m "test(test-case-generator): verify v3.0 with investment management doc"
```
