# 测试用例按需求文档结构排序 — 实施计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 让生成的测试用例 sections 按需求文档的章节顺序排列，方便测试人员对照需求文档核对。

**Architecture:** 分析阶段提取文档大纲 `doc_sections`，子 Agent 给每条用例打 `doc_section` 标签，合并阶段按 `doc_order` 重组 sections。4 个子 Agent 的 SOP 生成逻辑不变。

**Tech Stack:** Markdown skill 文件编辑，JSON 示例更新。无代码改动。

**Plugin Root:** `/Users/henry/.claude/plugins/marketplaces/henry-hub/plugins/test-case-generator`

---

### Task 1: 更新 analysis-schema.md — 新增 doc_sections 定义

**Files:**
- Modify: `skills/test-case-generator/references/analysis-schema.md`

**Step 1: 在 Schema JSON 中添加 doc_sections 字段**

在 `"list_fields"` 之后，添加 `doc_sections` 数组定义：

```json
"doc_sections": [
  {
    "id": "sec_01",
    "title": "资源池列表",
    "heading_level": 2,
    "page_type": "list",
    "doc_order": 1
  }
]
```

**Step 2: 在 Field Reference 部分添加 doc_sections 说明**

在文件末尾新增：

```markdown
### doc_sections

按需求文档标题顺序提取的章节列表，用于控制最终输出的 section 排列顺序。

- `id`: 唯一标识，格式 `sec_NN`
- `title`: 章节标题（取自需求文档原文）
- `heading_level`: 标题层级（1/2/3...）
- `page_type`: 页面类型。可选值：`list` | `form` | `detail` | `approval` | `other`
- `doc_order`: 在需求文档中的出现顺序（从 1 开始）

**粒度判断规则：**
- 取"页面级"标题作为 section（列表页、新增页、编辑页、审批页等）
- 文档只有两级标题时，取最细一级
- 三级以上标题时，取对应到独立页面/弹窗的层级
- 同一页面的不同 Tab 不拆分，归入同一 section
```

**Step 3: 验证**

Read `analysis-schema.md`，确认 JSON schema 和 Field Reference 部分都包含 doc_sections。

**Step 4: Commit**

```bash
git add skills/test-case-generator/references/analysis-schema.md
git commit -m "feat(test-case-generator): add doc_sections field to analysis schema"
```

---

### Task 2: 更新 example-analysis.json — 补充 doc_sections 示例

**Files:**
- Modify: `skills/test-case-generator/references/example-analysis.json`

**Step 1: 在 JSON 末尾（`list_fields` 之后）添加 doc_sections 示例**

```json
"doc_sections": [
  {
    "id": "sec_01",
    "title": "资源池列表",
    "heading_level": 2,
    "page_type": "list",
    "doc_order": 1
  },
  {
    "id": "sec_02",
    "title": "新增资源池",
    "heading_level": 2,
    "page_type": "form",
    "doc_order": 2
  },
  {
    "id": "sec_03",
    "title": "编辑资源池",
    "heading_level": 2,
    "page_type": "form",
    "doc_order": 3
  },
  {
    "id": "sec_04",
    "title": "入库审批",
    "heading_level": 2,
    "page_type": "approval",
    "doc_order": 4
  }
]
```

**Step 2: 验证**

用 `python3 -c "import json; json.load(open('...'))"` 验证 JSON 合法性。

**Step 3: Commit**

```bash
git add skills/test-case-generator/references/example-analysis.json
git commit -m "feat(test-case-generator): add doc_sections to example analysis"
```

---

### Task 3: 更新 json-schema.md — 子 Agent 输出格式增加 doc_section

**Files:**
- Modify: `skills/test-case-generator/references/json-schema.md`

**Step 1: 在 Sub-Agent Partial Output Format 的 JSON 示例中添加 doc_section 字段**

在 `"id": "TEMP_001"` 下一行添加 `"doc_section": "sec_01"`。

**Step 2: 在 The main agent 步骤说明中更新合并逻辑**

将：
```
1. Collects arrays from all sub-agents
2. Concatenates in order (A → B → C → D)
3. Renumbers IDs sequentially with the correct MODULE-CODE prefix
4. Groups into sections by sub_module
5. Wraps in the full JSON structure with meta + style
```

改为：
```
1. Collects arrays from all sub-agents
2. Groups by `doc_section`, ordered by `doc_order` from analysis.json
3. Within each group, maintains agent order (A → B → C → D)
4. Each `doc_section` group becomes one section, title from doc_sections[].title
5. Renumbers IDs sequentially with the correct MODULE-CODE prefix
6. Strips `doc_section` field from final output (not needed in Excel)
7. Wraps in the full JSON structure with meta + style
```

**Step 3: 验证**

Read 文件确认两处改动完整。

**Step 4: Commit**

```bash
git add skills/test-case-generator/references/json-schema.md
git commit -m "feat(test-case-generator): add doc_section to sub-agent output format"
```

---

### Task 4: 更新 SKILL.md — Global Rules 新增打标签规则

**Files:**
- Modify: `skills/test-case-generator/SKILL.md`

**Step 1: 在 Global Rules 列表末尾添加 doc_section 标签规则**

在 `**去重原则:**` 那行之后添加：

```markdown
- **文档章节标签:** 每条用例必须包含 `doc_section` 字段，值为 analysis.json 中 `doc_sections[].id`。根据该用例测试的页面/功能，匹配最相关的 doc_section。如果一条用例跨多个页面，选择其主要操作所在的页面。
```

**Step 2: 验证**

Read SKILL.md 的 Global Rules 部分，确认新规则已添加。

**Step 3: Commit**

```bash
git add skills/test-case-generator/SKILL.md
git commit -m "feat(test-case-generator): add doc_section tagging rule to global rules"
```

---

### Task 5: 更新 SKILL.md Step 2 — 分析阶段提取文档大纲

**Files:**
- Modify: `skills/test-case-generator/SKILL.md`

**Step 1: 在 Step 2 的 agent must 列表中添加第 6 项**

当前列表是 1-6（到 "Write the result"），在第 5 项 "List filter_fields and list_fields" 之后、第 6 项 "Write the result" 之前插入：

```markdown
6. Extract `doc_sections` — scan document headings to build an ordered list of page-level sections. Apply granularity rules from analysis-schema.md. Each section gets a sequential `doc_order`.
```

原来的第 6 项改为第 7 项。

**Step 2: 验证**

Read SKILL.md Step 2 部分，确认列表现在有 7 项且顺序正确。

**Step 3: Commit**

```bash
git add skills/test-case-generator/SKILL.md
git commit -m "feat(test-case-generator): add doc outline extraction to analysis step"
```

---

### Task 6: 更新 SKILL.md Step 3 — 子 Agent prompt 传入 doc_sections

**Files:**
- Modify: `skills/test-case-generator/SKILL.md`

**Step 1: 在 Step 3 的 "Each agent's Task prompt includes" 列表中添加 doc_sections**

在 "The business_rules_summary from analysis.json (for Agent D)" 之后添加：

```markdown
- The doc_sections from analysis.json (for all agents — used for `doc_section` tagging)
```

**Step 2: 验证**

Read SKILL.md Step 3 的 prompt includes 列表，确认包含 doc_sections。

**Step 3: Commit**

```bash
git add skills/test-case-generator/SKILL.md
git commit -m "feat(test-case-generator): pass doc_sections to all sub-agents"
```

---

### Task 7: 更新 SKILL.md Step 4 — 合并阶段按文档顺序排序

**Files:**
- Modify: `skills/test-case-generator/SKILL.md`

**Step 1: 替换 Step 4 合并 Agent 的操作步骤**

将当前的 7 步：
```
1. Read all partial JSON files
2. Concatenate into a single test_cases array (order: A → B → C → D)
3. Deduplicate overlapping test cases (same test_point + case_name)
4. Group into sections by sub_module
5. Renumber all IDs sequentially
6. Build the complete JSON with meta + style
7. Write to output
```

替换为：
```markdown
The merge agent must:
1. **Read** all partial JSON files: `partial_a.json`, `partial_b.json` (if exists), `partial_c.json` (if exists), `partial_d.json` (if exists)
2. **Read** `{cache_dir}/analysis.json` to get the `doc_sections` array
3. **Group by doc_section** — for each `doc_sections` entry (ordered by `doc_order`), collect all test cases whose `doc_section` matches. Within each group, maintain agent order (A → B → C → D)
4. **Handle unmatched** — test cases without a valid `doc_section` go into a final "其他" section
5. **Deduplicate** overlapping test cases within each group (same test_point + case_name)
6. **Build sections** — each `doc_section` group becomes one section. Title format: "{doc_sections[].title}（{module_code}）"
7. **Renumber** all IDs sequentially across all sections: `{module_code}_001`, `{module_code}_002`, ...
8. **Strip** the `doc_section` field from every test case (not needed in final output)
9. **Build the complete JSON** with meta + style (copy style block exactly from json-schema.md) + sections + merge_rules
10. **Write** to `{output_dir}/{module_code}_testcases.json`
```

**Step 2: 在 merge Task prompt 描述中补充 analysis.json 的读取**

将：
```
- **Prompt:** Read partial JSON files from cache_dir, read json-schema.md for the full output format
```

改为：
```
- **Prompt:** Read partial JSON files and analysis.json from cache_dir, read json-schema.md for the full output format. Use doc_sections from analysis.json to determine section ordering.
```

**Step 3: 验证**

Read SKILL.md Step 4 完整部分，确认新的 10 步合并逻辑和 prompt 描述正确。

**Step 4: Commit**

```bash
git add skills/test-case-generator/SKILL.md
git commit -m "feat(test-case-generator): reorder merge logic by doc_sections"
```

---

### Task 8: 更新 example-output.json — 展示文档顺序排列

**Files:**
- Modify: `skills/test-case-generator/references/example-output.json`

**Step 1: 将单一 section 拆分为多个 section，按文档顺序排列**

当前 example-output.json 只有一个 section "基金日常管理（JJRCGL-GSBG）" 包含所有 7 条用例。

拆分为：

```json
"sections": [
  {
    "title": "资源池列表（JJRCGL-GSBG）",
    "test_cases": [
      用例 001-005（列表页相关：入口、布局、搜索、筛选）
    ]
  },
  {
    "title": "新增资源池（JJRCGL-GSBG）",
    "test_cases": [
      用例 006（字段联动）
    ]
  },
  {
    "title": "入库审批（JJRCGL-GSBG）",
    "test_cases": [
      用例 007（审批流程）
    ]
  }
]
```

更新每条用例的 id 编号以保持连续。

**Step 2: 验证**

用 `python3 -c "import json; json.load(open('...'))"` 验证 JSON 合法性。

**Step 3: Commit**

```bash
git add skills/test-case-generator/references/example-output.json
git commit -m "feat(test-case-generator): update example output with doc-ordered sections"
```

---

### Task 9: 端到端验证

**Step 1: 通读所有改动文件，交叉检查一致性**

确认以下对齐关系：
- `analysis-schema.md` 的 `doc_sections` 定义 ↔ `example-analysis.json` 的示例数据
- `json-schema.md` 的 sub-agent 输出格式 ↔ `SKILL.md` Global Rules 的打标签规则
- `SKILL.md` Step 4 的合并逻辑 ↔ `json-schema.md` 的 main agent 步骤
- `example-output.json` 的 sections 结构 ↔ `example-analysis.json` 的 doc_sections 顺序

**Step 2: 确认无遗漏**

检查 `convert_to_xlsx.py` 不受影响（`doc_section` 字段在 Step 4 已被 strip）。

**Step 3: Final commit (if any fixes needed)**

```bash
git add -A
git commit -m "fix(test-case-generator): consistency fixes for doc-order sorting"
```
