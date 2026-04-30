---
name: doc-feature-extractor
description: Extract functional modules from heterogeneous business documents (.docx PRD/需求文档, .docx 解决方案/建设方案/升级方案, .xlsx 报价方案/功能清单/招标功能清单) into a styled Excel tracker. Decomposes core technology / business scope into the smallest reusable, separately-priceable, separately-evaluable units. **Trigger this skill whenever the user has business documents and wants a consolidated tracking spreadsheet of functional modules**, including: aggregating PRDs into a tracker, extracting modules from solution/proposal docs, consolidating quotation spreadsheets across multiple clients, assessing AI capability reusability, breaking technology into pricing units. Common triggers: "把 PRD 汇总成表格"、"PRD 功能点 Excel"、"需求文档跟踪表"、"梳理所有 PRD 的功能点"、"PRD 状态追踪"、"重跑/刷新汇总表"、"AI 能力评估"、"AI 能力复用判断"、"哪些能力能复用"、"模块化拆解"、"能力沉淀梳理"、"独立定价"、"分模块评估"、"最小业务单元"、"从建设方案抽功能模块"、"从解决方案/升级方案/方案文档抽功能"、"梳理方案的功能清单"、"把建设方案做成 Excel"、"报价方案合并"、"功能清单报价梳理"、"招标功能清单"、"客户报价对照"、"feature inventory from spec docs"、"aggregate PRDs into a spreadsheet"、"extract modules from solution docs"、"consolidate quotation spreadsheets"、"assess capability reusability"、"break down capabilities into pricing units"、"build a feature tracker from proposals". Especially valuable when documents come in mixed formats (PRD with FR-numbered tables, solution doc with deep heading nesting, quotation xlsx across multiple clients/sheets).
---

# Doc Feature Extractor

把 .docx PRD / 解决方案 / 建设方案 / 升级方案 + .xlsx 报价方案 / 功能清单这些**异构业务文档**抽成一份**带样式、可重跑、保留手填列**的 Excel 跟踪表。

## Operating mode (read this first)

如果你是被 **subagent / benchmark / 自动化测试** 调用,而不是在和真人交互的对话里,**不要进 plan mode、不要 ExitPlanMode、不要请求审批**。直接按工作流执行,完成后简短报告。理由:plan mode 等待用户审批,在自动化场景里会让任务卡住,需要外层手工 SendMessage 才能解锁,白白浪费一轮对话。

判断方式: prompt 里出现「benchmark」「测试」「subagent」「baseline」「输出到指定路径」等关键词,或者看到约束像「outputs MUST go to...」「不要修改项目根」「严格约束」,就是自动化场景,直接执行。

## When to use this

skill 提供 **3 种输入模式**,对应 3 个独立脚本。先按用户给的输入文档类型选模式,再走对应工作流。

### Mode A · PRD / 需求文档 (.docx)
**用 `scripts/aggregate.py`**

触发条件:
- 用户有多份 PRD / 需求确认单 / 规格说明书 散落在几个目录里
- 文档里通常有 FR-XXX 编号表 + 字段定义表
- 想要 6 sheet 跨项目跟踪表(能力清单 + 业务模块概览 + 需求明细 + AI 字段定义 + 文档生命周期总览 + README)
- 关心**长期手填列保留**(开发状态/责任人/复用度等)

典型 prompt: "把 PRD 汇总成跟踪表"、"梳理所有 PRD 的功能点"。

### Mode B · 解决方案 / 建设方案 / 升级方案 (.docx)
**用 `scripts/extract_solution.py`**

触发条件:
- 用户给的是商务方案或技术方案,以章节嵌套为主、**没有 FR 编号表**
- 文档可能内嵌"功能模块 + 费用 + 工作量"表(常见于升级方案)
- 想要快速看到该方案承诺了哪些功能模块、各自费用工时

典型 prompt: "把建设方案 docx 里的功能模块梳成 Excel"、"梳理这份升级方案的功能清单"、"从解决方案抽功能模块"。

输出 3 sheet: 模块概览(带费用/工时) / 章节明细 / README。

### Mode C · 报价方案 / 功能清单 (.xlsx)
**用 `scripts/extract_quotation.py`**

触发条件:
- 用户给的是 .xlsx 报价表(通常多 sheet,每行一个功能子模块)
- 跨多个客户(产投 / 科创 / 人才)需要合并对照
- 列结构典型: `[业务范围, 模块, 子模块, 功能描述, 分摊报价]` 或无价的招标功能清单

典型 prompt: "把这个功能清单报价 xlsx 抽成统一表"、"合并几份报价方案"、"客户报价对照"。

输出 2 sheet: 模块报价(报价列浅黄高亮) / README。

### 不要用此 skill 的场景
- 用户已经有 Excel 跟踪表,只想**改其中几行** → 直接用 openpyxl 改
- 用户想**写新的 PRD/方案** → 用 `pm-execution:create-prd` 或类似
- 用户想从**代码反推 PRD** → 用 `code-to-prd:code-to-prd`
- 输入是 .pptx 或图片 → 当前不支持

## Why this skill exists

**业务动机(关键)**: 把核心技术 / 业务范围拆成**最小可独立定价、独立评估、独立复用**的业务单元。无论是 PRD、解决方案,还是报价表,核心目标都是让客户问"这个能力多少钱"、PM 问"模块到哪了"、测试问"实现准不准"时,都能直接看自己那一层。

不同输入类型在三层粒度上有不同的覆盖度:

| 输入类型 | 能力级 | 模块级 | 字段级 | 报价/工时 |
|---|---|---|---|---|
| PRD | ✓(catalog 配置) | ✓(从 PRD 章节抽) | ✓(字段表抽) | — |
| 解决方案 | ✓(可选,从内嵌 AI 智能体表) | ✓(从 Heading 章节抽) | — | ✓(从内嵌报价表抽,如有) |
| 报价 xlsx | — | ✓(每行一个) | — | ✓(主载体) |

**技术动机(实现层)**: 异构文档抽取的通用底盘。3 种 mode 共享: 通用表头识别(中英双语)、openpyxl 排版、xlsx skill 的公式重算协议。差异化的只是 reader 部分。

## Workflow

按输入类型走对应的 mini-workflow。所有 mode 的 Step 0 都一样:

### Step 0 · 选 mode 并 inspect 1-3 份代表性样本

**先用对应脚本的 `--inspect` flag 看文档结构**,不要直接跑抽取:

```bash
# Mode A (PRD)
python scripts/inspect_docx.py path/to/prd.docx     # 列 Heading 与表格

# Mode B (解决方案)
python scripts/extract_solution.py --input path/to/solution.docx --inspect
# 输出: Heading 层级分布 + 推荐模块 Heading 层级

# Mode C (报价 xlsx)
python scripts/extract_quotation.py --input path/to/quotation.xlsx --inspect
# 输出: 每个 sheet 的表头识别情况
```

亲眼看到结构再决定怎么配 — **跳过这步会得到一份漏功能的表**。

### Mode A Workflow (PRD)

完整 7 步,沿用现有杭州产投实战流程,详见下方 "Mode A 详细工作流"。要点:
1. 摸底用户项目目录结构和文件命名前缀方案
2. inspect_docx 采样
3. 复制模板 + 配置 PROJECT_CONFIG 区块(顶部 30 行)
4. `--dry-run` 验证抽取覆盖度
5. 正式生成 + LibreOffice 公式重算
6. 手填列保留回归测试
7. 视觉验收

### Mode B Workflow (解决方案)

```bash
# 1. inspect 看 Heading 分布
python scripts/extract_solution.py --input solution.docx --inspect

# 2. 试跑(默认自动选 Heading 层级)
python scripts/extract_solution.py --input solution.docx --output out.xlsx

# 3. 如果模块数明显偏少/偏多,手动指定层级
python scripts/extract_solution.py --input solution.docx --output out.xlsx --heading-level 4

# 4. 公式重算(虽然 Mode B 输出无公式,跑一遍稳妥)
python <xlsx_skill>/scripts/recalc.py out.xlsx 60

# 5. 直接打开看视觉
open out.xlsx
```

经验值:
- 浅嵌套方案(H1-H4): 模块通常在 H3
- 深嵌套方案(H2-H6): 模块通常在 H4
- 自动选 Heading 层级会优先 H3 → H2 → H4

如果文档内嵌 "功能模块 + 费用 + 工作量" 表,会自动识别并把 cost/effort 回填到模块概览,不需手动配置。

### Mode C Workflow (报价 xlsx)

```bash
# 1. inspect 看 sheet 与表头识别情况
python scripts/extract_quotation.py --input quotation.xlsx --inspect

# 2. 全 sheet 抽
python scripts/extract_quotation.py --input quotation.xlsx --output out.xlsx

# 3. 只抽某客户
python scripts/extract_quotation.py --input quotation.xlsx --output out-hzcj.xlsx --sheet "杭州产投"

# 4. 公式重算 + 视觉
python <xlsx_skill>/scripts/recalc.py out.xlsx 60
open out.xlsx
```

经验值:
- "汇总报价"/"小计"这类总览 sheet 通常没表头,会被自动跳过
- 表头识别允许中英文混合(`分摊报价 / 报价 / 金额 / 费用 / Total / Price` 等都命中)
- 父值继承: "业务范围"/"模块"列经常 merged cell 留空,脚本会从上面非空行继承

## Mode A 详细工作流(PRD)

> 以下是 Mode A 完整步骤,沿用之前 prd-aggregator 时代验证过的 7 步流程。

### Step 1 · 摸底用户项目

- 目录结构: PRD 散落哪几个子目录? `PRD-开发/` `需求确认/`? `docs/specs/`? 平铺?
- 文件命名: 数字/字母前缀? (`01-03_xxx.docx` / `EPIC-04_xxx.docx` / `04_PRD.docx` + `04_signed.pdf`)
- PRD 大致格式: 有 FR 编号表? 有"AI 字段定义"或"数据字典"?
- 手填字段需求: 用户希望手填哪些列? (开发状态/责任人/优先级/复用度...)
- 是否有签字版 PDF / 归档: 影响 Sheet 5 生命周期总览

### Step 2 · 用 inspect_docx.py 采样 1-3 份代表性 PRD

```bash
python scripts/inspect_docx.py path/to/prd-1.docx path/to/prd-2.docx
```

**不要跳过这步** — 你要亲眼看到表头长什么样才能配 `FIELD_NAME_KEYS`、`FR_NUMBER_KEYS` 这些常量。

### Step 3 · 复制模板并配置 PROJECT CONFIG 区块

```bash
mkdir -p <project>/scripts
cp <skill_path>/scripts/aggregate.py <project>/scripts/
cp <skill_path>/scripts/inspect_docx.py <project>/scripts/
cp <skill_path>/scripts/requirements.txt <project>/scripts/
```

打开 `aggregate.py`,修改 **`┏━ EDIT FOR YOUR PROJECT`** 区块。带 `# ★` 的项必改:

| 配置项 | 例子 |
|---|---|
| `ROOT` / 输入目录 | 改成用户实际目录名 |
| `PREFIX_RE` | 例如 `r"^(EPIC-\d+)_"` 或 `r"^(\d+)_"` |
| `PREFIXES` | 显式列出所有前缀 |
| `PREFIX_DEFAULT_MODULE` | 前缀 → 人类可读的模块名 |
| `PREFIXES_FROM_CONFIRMATION` | 哪些前缀只有需求确认单 |
| `FIELD_NAME_KEYS` 等表头关键字 | 按 inspect_docx 看到的表头加 |
| `FALLBACK_HEADING_LEVEL` | 没 FR 表的前缀按哪个 H 层级切段 |
| `LENIENT_FIELD_PREFIXES` | 字段表只有「信息项+备注」简表的前缀 |
| `fr_module_splitter()` | 子模块 FR 编号能区分时写,否则 `return h_module` |
| `CAPABILITY_CATALOG` | 跨项目能力点列表(Sheet 1 主表),N:N 关联 |

⚠️ **CAPABILITY_CATALOG 的 modules 字符串必须跟 Sheet 2 实际抽出的子模块 1:1 一致**。先跑一遍生成 Sheet 2,把 16 行模块名拷过来对齐再写 catalog。

详细参考: `references/header_keywords.md`(表头关键字储备) + `references/styling_recipe.md`(排版常量)。

### Step 4 · `--dry-run` 验证抽取覆盖度

```bash
python scripts/aggregate.py --dry-run
# 也可以从 skill 目录直接跨项目调用,无需改 EDIT 区块:
# python <skill_path>/scripts/aggregate.py --input <project_root> --dry-run
```

每个前缀都应有非零 FR 行。某前缀 FR=0 字段=0 的处理: 检查表头关键字 → 检查 fallback heading → 检查 PREFIX_RE。**不达标不要进 Step 5**。

### Step 5 · 正式生成 + LibreOffice 重算公式

```bash
python scripts/aggregate.py
python <xlsx_skill_path>/scripts/recalc.py <output>.xlsx 60
```

期望: `{"status": "success", "total_errors": 0, "total_formulas": N}`。`#REF!` / `#DIV/0!` 错误通常在 Sheet 5 的状态备注公式。

### Step 6 · 手填列保留回归测试

```bash
# 模拟手填
python -c "
from openpyxl import load_workbook
wb = load_workbook('out.xlsx')
ws = wb['业务模块概览']
ws['G3'] = '开发中'
wb.save('out.xlsx')
"
# 重跑
python scripts/aggregate.py
# 验证: G3 应为 '开发中'
```

### Step 7 · 直接打开视觉验收

```bash
open <output>.xlsx   # macOS
```

**不要只看 dry-run 数字就宣布完成** — 视觉问题(列宽、wrap_text、条件格式)在数字里看不出来。

## Architecture summary (各 mode 输出)

### Mode A 输出 (PRD,6 sheet)

| Sheet | 内容 | 行数级别 | 手填列 | 公式? |
|---|---|---|---|---|
| 能力清单 | 跨项目可复用能力点 | ~6-12 | ✓ 复用度 / 成熟度 / 已应用项目 / 复用注意事项 / 维护责任人 | 无 |
| 业务模块概览 | 项目内子模块 | ~10-20 | ✓ 关键能力 / 开发状态 / 责任人 / 优先级 / 计划交付 / 备注 | 无 |
| 需求明细 | FR / 章节切段 | ~50-200 | 无 | 无 |
| AI 字段定义 | 字段表 union | 字段并集 | ✓ 回填实现状态 / 测试通过率 / 备注 | 无 |
| 文档生命周期总览 | 每前缀一行 | ~每前缀 1 行 | 无 | ✓ 状态 + 汇总 |
| README | 用法说明 | 文本 | 无 | 无 |

设计意图(关键 — 两层视角):
- **能力清单 = 跨项目视角** ("我们沉淀了什么、下个客户能复用什么")
- **业务模块概览 = 项目内视角** ("这个项目里干了什么活")
- **N:N 关联**: 一个能力可横跨多模块;一个模块可挂多能力
- 手填列三层独立主键: 能力 ID / (前缀, 子模块) / (前缀, 模块, 字段名)

### Mode B 输出 (解决方案,3 sheet)

| Sheet | 内容 | 行数级别 | 手填评估列 |
|---|---|---|---|
| 模块概览 | 每个模块 Heading 一行 + 章节路径 + 描述 + 预估费用 + 预估工作量 | 通常 ~10-30 | ✓ 复用度 / 成熟度 / 已应用项目 / 维护责任人 / 备注(橙色) |
| 章节明细 | 文档所有 paragraph 与 heading | ~100-300 | 无 |
| README | 用法 + 抽取参数 | 文本 | 无 |

重跑契约: 按 `(模块名, 所属章节)` 主键合并保留手填值,不会被覆盖。

### Mode C 输出 (报价 xlsx,2 sheet)

| Sheet | 内容 | 行数级别 | 手填评估列 |
|---|---|---|---|
| 模块报价 | 每行一功能子模块, 报价列浅黄高亮 | ~100-1000(跨多 sheet 合并) | ✓ 复用度 / 成熟度 / 已应用项目 / 维护责任人 / 备注(橙色) |
| README | 用法 + 抽取参数 | 文本 | 无 |

重跑契约: 按 `(来源 sheet, 业务范围, 模块, 子模块)` 主键合并;手填值优先(用户改过的"备注"会盖掉源 xlsx 抽出的备注)。

### 排版固定(所有 mode)
- Arial 10,深蓝表头白字
- 斑马纹 + 灰细边框 + 首行筛选 + 首行冻结
- Mode A 还有: 橙黄手填列表头、前缀色带、条件格式(已完成行浅绿、缺 PRD 行浅红)
- Mode B/C: 评估手填列表头橙色 (`FFC000`)
- Mode C: 报价列浅黄高亮

## Bundled assets

- `scripts/aggregate.py` — Mode A 主脚本(顶部 EDIT 区块是配置面板,也支持 `--input <project_root>` 跨项目调用)
- `scripts/extract_solution.py` — Mode B,解决方案抽取
- `scripts/extract_quotation.py` — Mode C,报价 xlsx 抽取
- `scripts/_common.py` — 三脚本共享的结构工具 + 样式 + `load_manual_columns` 手填列保留
- `scripts/inspect_docx.py` — 调试工具(列 heading + 表头)
- `scripts/requirements.txt` — `python-docx`、`openpyxl`
- `references/header_keywords.md` — 中英 PRD 常见表头关键字
- `references/styling_recipe.md` — openpyxl 排版常量
- `references/doc-types-anatomy.md` — 4 类样本文档结构指纹
- `tests/` — pytest 回归测试 (合成 fixtures,无客户文档),改动后跑 `python3 -m pytest tests/ -v`
- `evals/evals.json` — 测试 prompt(供 skill-creator 用)
- `evals/samples/` — 跨项目泛化样本(svn:ignore)

## 反模式 / 常见坑

- ❌ 不用 inspect 直接配置表头关键字 → 总是漏抽
- ❌ 用 pandas `.to_excel` 写文件 → 公式和样式全丢,xlsx skill 强制要求 openpyxl
- ❌ 跳过 LibreOffice 重算 → Excel 公式单元格显示空白(直到用户手动 F9)
- ❌ Mode A 把手填列也按"自动列"重写 → 用户辛辛苦苦填的值全没了,违反 skill 核心契约
- ❌ Mode A 抽取覆盖度不达标就生成 → 用户拿到漏功能的表
- ❌ Mode B 自动 Heading 层级选错(模块数偏少/偏多)就交付 → 用 `--heading-level` 手动指定
- ❌ Mode C 把"汇总报价"/"小计"sheet 当数据 sheet → 表头识别会自动跳过,但要在 `--inspect` 时确认
- ❌ 把 .pptx 或图片当输入 → 当前 3 个 mode 都不支持
