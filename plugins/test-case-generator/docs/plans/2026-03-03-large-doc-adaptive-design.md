# 大文档自适应设计方案 v3.0

日期：2026-03-03

## 背景

test-case-generator v2.0 在处理大型需求文档（414KB / 67 section / 179 字段）时暴露三个核心问题：

1. **P0 文档丢失** — Analysis 阶段截断了 55% 的文档内容（子基金投资 + 股权投资项目完全未覆盖）
2. **P1 Agent 过载** — 单个 Agent A 需覆盖 67 section，输出仅为理论需求的 25%，大量 section 仅有骨架用例
3. **P1 L0 缺失** — 仅 9% 的 section 有 L0 基础验证用例

根因：每个 agent 输入 ~487KB（文档占 85%），上下文窗口饱和，输出空间不足。

## 设计原则

- **统一流程** — 不区分大小文档，所有文档走同一套分组流程
- **按模块拆分** — 每个大模块独立走 A/B/C/D agent 流程，独立生成 Excel
- **确定性切割** — 文档切割用 Python 脚本，不依赖 AI

## 整体流程

```
Step 1: 读取文档
Step 2: Global Analysis → analysis.json（含 module_groups）
Step 2.5: split_doc.py → 按 group 切割文档
Step 3: 对每个 group 按波并行派遣 A/B/C/D
Step 4: 对每个 group 独立 Merge
Step 5: 每个 group 生成独立 Excel
Step 6: 清理 + 汇总报告
```

## Part 1：Analysis 阶段

### analysis.json 输出格式

```json
{
  "source_doc": "invest_mgmt_doc.md",
  "common_rules": {
    "text_half_line_max": 50,
    "text_full_line_max": 100,
    "textarea_max": 2000,
    "amount_decimal": 6,
    "amount_total_digits": 20,
    "percentage_max": 999.99,
    "pagination_default": 5,
    "pagination_options": [5, 10, 20, 50]
  },
  "module_groups": [
    {
      "id": "grp_1",
      "name": "本级管理",
      "module_code": "BJGL",
      "heading_pattern": "## 1.2 本级管理",
      "doc_sections": [
        { "id": "sec_01", "title": "基金列表", "page_type": "list", "doc_order": 1 }
      ],
      "field_table": [ "...只含该模块的字段..." ],
      "dispatch": { "has_ui": true, "has_data_entry": true, "has_data_modify": true, "has_business_logic": true, "has_data_cleanup": true },
      "business_rules_summary": "..."
    }
  ]
}
```

关键设计：
- `common_rules` — 从文档公共说明中提取通用校验规则
- `module_groups` — 每个大模块独立包含 doc_sections、field_table、dispatch、business_rules_summary
- `heading_pattern` — 用于确定性文档切割的锚点
- 即使只有 1 个模块，`module_groups` 也有 1 个元素，流程不变

### analysis-schema.md 更新

需更新 analysis-schema.md，加入 `common_rules` 和 `module_groups` 的 schema 说明。

## Part 2：文档切割

### Step 2.5（新增）

Analysis 完成后，orchestrator 调用切割脚本：

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/split_doc.py analysis.json /tmp/doc.md cache_dir/
```

输出：
```
cache_dir/
├── doc_common.md          # 公共说明（需求概述、通用规则）
├── doc_grp_1.md           # 本级管理
├── doc_grp_2.md           # 载体管理
├── doc_grp_3.md           # 子基金投资
└── doc_grp_4.md           # 股权投资项目
```

切割逻辑：
- 读取 analysis.json 中每个 module_group 的 heading_pattern
- 用正则在 markdown 中定位每个大模块的起止位置
- 第一个大模块之前的内容 → doc_common.md
- 每个分片文件 = doc_common.md 内容 + 该模块的文档内容

## Part 3：Agent 派遣

### 每个 Group 的 Agent 派遣

```
Group N:
├── Agent A: L0+L1+L2 （always）
├── Agent B: L3 （if has_data_entry）
├── Agent C: L4 （if has_data_modify）
└── Agent D: L5+L6 （if has_business_logic or has_data_cleanup）
```

### Agent 输入

```
Agent 输入 = doc_grp_N.md（已包含 common 部分）
           + group 的 field_table / doc_sections
           + common_rules（置顶注入）
           + reference 文件（sop-layers.md, json-schema.md, example-output.json）
```

上下文对比：
| 输入项 | v2.0 | v3.0 |
|--------|------|------|
| 需求文档 | 414KB 完整文档 | ~100KB 分片 |
| field_table | 179 个字段 | ~40-50 个字段 |
| doc_sections | 67 个 | ~15-20 个 |

### 并行策略

按 group 分波，每波 4 个 agent 并行：

```
Wave 1: Group 1 的 A/B/C/D → 等待完成 → Merge 1
Wave 2: Group 2 的 A/B/C/D → 等待完成 → Merge 2
...
```

### Prompt 改进

1. 置顶注入 common_rules：
   ```
   ## 公共校验规则（优先级高于默认值）
   - 半行文本框最大 50 字，整行 100 字，文本域 2000 字
   - 金额精度 6 位小数，总位数 20 位
   - 百分比最大 999.99
   - 翻页默认 5 条，支持 5/10/20/50
   ```

2. 新增全局规则：
   - **禁止"同xxx"引用** — 每条用例必须独立可执行。相似模块可减少用例数量，但每条必须包含完整的 steps 和 expected
   - **预期结果不允许"A 或 B"式描述** — 需求未明确时使用 `[TODO:待确认]`

### 输出文件命名

```
cache_dir/
├── partial_grp1_a.json
├── partial_grp1_b.json
├── partial_grp1_c.json
├── partial_grp1_d.json
├── partial_grp2_a.json
├── ...
```

## Part 4：Merge 与输出

### 每个 Group 独立 Merge

每个 group 完成后独立 merge：

```
Group 1 完成 → Merge Agent 1 → BJGL_testcases.json → BJGL_testcases.xlsx
Group 2 完成 → Merge Agent 2 → ZTGL_testcases.json → ZTGL_testcases.xlsx
...
```

Merge 逻辑与 v2.0 一致（按 doc_section 分组 → 去重 → 编号 → 输出），范围缩小到单个 group。

### 输出文件

```
output_dir/
├── BJGL_testcases.json + .xlsx    # 本级管理
├── ZTGL_testcases.json + .xlsx    # 载体管理
├── ZJTZ_testcases.json + .xlsx    # 子基金投资
└── GQTZ_testcases.json + .xlsx    # 股权投资项目
```

### 汇总报告

```
测试用例生成完成！
源文档：国家制造业转型升级基金设计文档-投资管理.docx
共识别 N 个模块：

  模块           文件                    用例数   子模块
  本级管理       BJGL_testcases.xlsx     312      21
  载体管理       ZTGL_testcases.xlsx     480      46
  ...

总计：X 条测试用例
```

## 变更清单

| 文件 | 变更类型 | 说明 |
|------|----------|------|
| SKILL.md | 重写 | 统一分组流程，新增 Step 2.5，Step 3 按 group 循环 |
| analysis-schema.md | 更新 | 新增 common_rules、module_groups schema |
| scripts/split_doc.py | 新增 | 文档切割脚本 |
| scripts/convert_to_xlsx.py | 不变 | 无需修改 |
| sop-layers.md | 微调 | 新增禁止"同xxx"引用、禁止"A或B"预期结果规则 |
| json-schema.md | 不变 | 无需修改 |
| plugin.json | 更新 | version 升级到 3.0.0 |

## 预期效果

| 指标 | v2.0 | v3.0 |
|------|------|------|
| 文档覆盖率 | 45% | 100% |
| 每 section 平均用例 | 7.6 条 | 15-20 条 |
| Agent 上下文 | ~487KB | ~150KB |
| L0 覆盖率 | 9% | >90% |
| "同xxx"引用 | 21 条 | 0 条 |
| 模糊预期 | 75 条 | <10 条 |
