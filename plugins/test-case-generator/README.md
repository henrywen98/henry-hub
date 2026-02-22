# 测试用例生成器 (test-case-generator)

从需求文档自动生成结构化测试用例，输出格式化 Excel 文件。

## 架构

采用 **编排器 + 并行子 Agent** 架构：

```
编排器（Orchestrator）
 ├─ 读取需求文档（pandoc/Read）
 ├─ Task: 结构分析 → analysis.json
 ├─ Task[并行]: Agent A/B/C/D → partial_*.json
 ├─ Task: 合并去重 → {module_code}_testcases.json
 ├─ python3 convert_to_xlsx.py → 格式化 Excel
 └─ 清理缓存
```

### 7 层 SOP 框架

| 层级 | 名称 | 触发条件 |
|------|------|----------|
| L0 | 基础验证 | 始终 |
| L1 | 展示层 | 始终 |
| L2 | 交互筛选 | 始终 |
| L3 | 数据输入 | 有新增/导入功能 |
| L4 | 数据修改 | 有编辑/修改功能 |
| L5 | 业务规则 | 有审批/状态/计算 |
| L6 | 数据清理 | 有删除/作废功能 |

### 子 Agent 分工

- **Agent A**: L0+L1+L2（页面展示、筛选交互）— 始终派遣
- **Agent B**: L3（数据输入验证）— 有新增功能时派遣
- **Agent C**: L4（数据修改验证）— 有编辑功能时派遣
- **Agent D**: L5+L6（业务规则、数据清理）— 有业务逻辑/删除时派遣

## 使用方法

```
/test-case-generator [doc_path]
```

- `doc_path`：需求文档路径（支持 .docx / .pdf / .md / .txt），可省略后直接粘贴内容

## 输出

- **JSON 中间文件**：`{module_code}_testcases.json`（结构化数据，可二次处理）
- **Excel 文件**：`{module_code}_testcases.xlsx`（17 列标准模板，含标题栏、汇总栏、COUNTIF 公式、单元格合并）

## 目录结构

```
test-case-generator/
├── .claude-plugin/plugin.json
├── README.md
├── skills/
│   └── test-case-generator/
│       ├── SKILL.md                          # 主技能文件
│       └── references/
│           ├── analysis-schema.md            # 分析阶段输出格式
│           ├── json-schema.md                # 测试用例 JSON 格式
│           ├── example-output.json           # 示例输出
│           ├── excel-template-spec.md        # Excel 模板规范
│           └── sop-layers.md                 # 7 层 SOP 详细规则
└── scripts/
    ├── convert_to_xlsx.py                    # JSON → Excel 转换脚本
    ├── test_convert.py                       # 转换脚本测试
    └── requirements.txt                      # Python 依赖
```

## 依赖

- Python 3.8+
- openpyxl >= 3.1.0（`pip3 install openpyxl`）
- pandoc（读取 .docx 文件时需要）
