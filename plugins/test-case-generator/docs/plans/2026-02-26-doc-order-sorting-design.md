# 设计：测试用例按需求文档结构排序

## 问题

测试人员反馈：生成的用例内容质量没问题，但排列顺序按 SOP 层级组织（L0→L6），与需求文档的章节结构不一致，核对时不方便。

测试人员的实际工作流：按需求文档的标题顺序逐章核对，同时参照原型图。

## 方案

**文档结构优先排序**：分析阶段提取需求文档大纲，子 Agent 给每条用例打 `doc_section` 标签，合并阶段按文档顺序重组 sections。

4 个子 Agent 的 SOP 生成逻辑完全不变，只改分析、标签、合并三处。

## 改动范围

| 文件 | 改动 |
|------|------|
| `references/analysis-schema.md` | 新增 `doc_sections` 字段定义 |
| `SKILL.md` Step 2 | 分析阶段提取文档大纲到 `doc_sections` |
| `SKILL.md` Step 3 | 子 Agent prompt 传入 `doc_sections`，要求打标签 |
| `SKILL.md` Step 4 | 合并阶段按 `doc_sections.doc_order` 排序 |
| `references/example-analysis.json` | 补充 `doc_sections` 示例 |
| `references/example-output.json` | 更新 sections 排列为文档顺序 |

**不改动**：`convert_to_xlsx.py`、`json-schema.md`、`sop-layers.md`、子 Agent 生成逻辑。

## analysis.json 新增字段

```json
{
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
    }
  ]
}
```

智能判断粒度规则：
- 取"页面级"标题作为 section（列表页、新增页、编辑页、审批页等）
- 两级标题时取最细一级
- 三级以上时取对应独立页面/弹窗的层级
- `page_type` 可选值：`list` | `form` | `detail` | `approval` | `other`

## 用例新增字段

每条用例新增 `doc_section` 字段（仅用于排序，不写入 Excel）：

```json
{
  "id": "TEMP_001",
  "doc_section": "sec_01",
  "module": "资源池",
  "sub_module": "列表页",
  ...
}
```

## 合并排序规则

```
第一优先级：doc_sections.doc_order（文档顺序）
第二优先级：Agent 顺序 A→B→C→D（即 SOP 层级 L0→L6）
第三优先级：同层内按 test_point 分组
```

合并操作：
1. 读取所有 partial JSON
2. 按 `doc_section` 分桶
3. 每桶内按 Agent 顺序排
4. 桶按 `doc_order` 排列
5. 每桶输出为一个 section，title 用文档标题

## 输出效果

改后的 Excel section 顺序：
```
资源池列表 → 新增资源池 → 编辑资源池 → 项目入库申请 → 参股基金入库 → 拜访记录
```

每个 section 内部仍按 L0→L6 排序，保证测试方法论的完整性。
