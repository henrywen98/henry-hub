# doc-feature-extractor — 通用业务文档功能模块抽取

把异构业务文档(.docx PRD / 解决方案 / 建设方案 / 升级方案、.xlsx 报价方案 / 功能清单 / 招标功能清单)抽成一份**带样式、可重跑、保留手填列**的 Excel 跟踪表。

## 核心理念

把**核心技术**拆成**最小可独立定价 / 评估 / 复用**的业务单元。无论输入是 PRD、解决方案还是报价表,核心目标都是让客户问"这个能力多少钱"、PM 问"模块到哪了"、测试问"实现准不准"时,各自能直接看自己那一层。

## 包含的 Skills

| Skill | 触发词 | 用途 |
|---|---|---|
| doc-feature-extractor | "把 PRD 汇总成表格"、"梳理建设方案功能模块"、"合并报价 xlsx"、"AI 能力复用判断"、"分模块评估"、"独立定价" 等 | 3 模式异构文档抽取 |

## 3 种输入模式

| Mode | 输入 | 脚本 | 输出 |
|---|---|---|---|
| **A** | PRD / 需求文档 (.docx) | `aggregate.py` | 6 sheet (能力 / 模块 / 明细 / 字段 / 生命周期 / README),含手填列保留 |
| **B** | 解决方案 / 建设方案 / 升级方案 (.docx) | `extract_solution.py` | 3 sheet (模块概览 / 章节明细 / README),自动识别内嵌"功能+费用+工时"表 |
| **C** | 报价方案 / 功能清单 (.xlsx) | `extract_quotation.py` | 2 sheet (模块报价 / README),跨 sheet 合并、报价列高亮 |

## 内置资源

- `references/header_keywords.md` — 中英 PRD 表头关键字储备
- `references/styling_recipe.md` — openpyxl 排版常量与封装范式
- `references/doc-types-anatomy.md` — 4 类样本文档结构指纹(调研产出)
- `evals/evals.json` — 6 个测试 prompt(覆盖 3 mode + 跨项目泛化检验)
- `skills/doc-feature-extractor/提示词.md` — **AI 一键启动: 把这个 skill 从 60% 完成度推到 95%+ 的做透路径**

## 当前完成度

**~60%** — 输入扩展、触发面扩展、跨项目可用都达成,但工程严谨性、错误处理、Mode 间一致性、aggregate.py 的杭州产投耦合解除都还欠债。

要把它做透,把 `skills/doc-feature-extractor/提示词.md` 喂给 AI,会自动按优先级一路 fix。

## 来源

源 skill 在杭州产投 AI 项目内部孵化(SVN r541-r557),针对 6 份 PRD + 1 份建设方案 + 1 份南通跨项目方案 + 1 份多客户报价 xlsx 验证后迁出,沉淀到本 hub 作为通用工具。
