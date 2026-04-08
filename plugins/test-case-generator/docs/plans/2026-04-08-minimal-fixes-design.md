# test-case-generator 最小化修复设计

日期：2026-04-08
版本目标：v3.1.0（bugfix + prompt 调优 + 颗粒度原则调整，无架构变更）

## 背景

v3.0 在真实用户（测试人员夏夕）手中暴露出 5 个问题，记录在微信聊天日志里：

1. **42 页需求文档生成卡住 1+ 小时** —— `split_doc.py` 在 Windows + 中文文档上失败，触发多轮人工干预
2. **L3 数据输入层的字段用例按"字段类型"组织而非文档顺序** —— 测试人员核对时无法顺着需求文档走
3. **存在字段被跳过（未生成用例）的情况** —— "用例精简规则"被模型当成了"可以漏字段"
4. **测试用例颗粒度过粗：一条用例塞多个检查点** —— 例如 ZYCZXZ_006 "关键字搜索"用例含 7 个输入场景（完整名称/简称/空格/特殊字符/超长字符串/不输入/清空）。这样的用例**不能作为 Playwright 自动化的参考**，因为 1 条用例 = 多个 assertion，失败定位困难。用户明确要求"一条用例只测一个功能点"
5. **Playwright 执行用例**另有一套问题 —— **不在本轮范围内**

## 根因分析

### 卡 1 小时的直接原因

聊天日志显示，`scripts/split_doc.py` 在用户环境下连续失败：

```
Error: Cannot find heading pattern '^# 1\s+资产申请管理' in document
```

定位到 `split_doc.py:28`：

```python
pattern = re.escape(grp["heading_pattern"])
```

**契约不一致**：
- `analysis-schema.md` 没定义 `heading_pattern` 是"正则"还是"字面文本"
- Analysis agent 理解成"正则"，输出 `^# 1\s+资产申请管理`
- `split_doc.py` 做 `re.escape()`，把它当**字面量**转义成 `\^\#\ 1\\s\+资产申请管理`
- 结果：`\s+` 从"一个或多个空格"变成了字面字符串 `\s+`
- 文档里没有字面 `\s+`，永远匹配不上

**叠加问题**：
- 中文 Markdown 标题常出现非换行空格 `\xa0`（尤其是从 Word 转换来的）和全角空格 `\u3000`，普通 `\s` 在 `re.escape` 之后也丧失语义
- Windows + pandoc 产出的文件常带 UTF-8 BOM（`\ufeff`）和 CRLF 行尾（`\r\n`），在首行 heading 比较时会静默失败
- SKILL.md Step 2.5 的调用写死 `python3`，Windows 下返回 exit 49（`python3` 不存在，只有 `python`）
- `split_doc.py` 的 fallback 逻辑用 substring 匹配（`heading_text in line`），在文档里存在 `"## 1.2 本级管理"` 和 `"## 1.2.1 本级管理明细"` 这种嵌套编号时会误匹配到错的段，是**隐形 footgun**

### L3 字段顺序和覆盖问题的根因

- `sop-layers.md:75-146` L3 的内容是**按字段类型**组织的模板（文本输入框 / 下拉选择框 / 日期选择器 / …）
- Agent B 读这些模板时把它们当成了**组织结构**，而不是**生成规则参考**
- SKILL.md Step 3 Agent B prompt 没有明确指令说"按 `field_table` 数组顺序遍历"
- 也没有"每个字段至少一条用例"的约束
- "用例精简规则"（`sop-layers.md:254-257`）允许合并，但没说合并时 `test_point` 必须列出所涉及字段

### 用例颗粒度过粗的根因

- `sop-layers.md:248` Writing Guidelines 明确允许："一个测试用例可包含多个相关的检查步骤（如搜索功能的多种输入情况）"
- `sop-layers.md:254-257` "用例精简规则"鼓励三类合并：
  1. **同类型同规则字段合并**（多个"自动带入且只读"字段合为 1 条）
  2. **下拉选项精简**（>5 选项只测首末中）
  3. **相似场景合并**（多个表单的"取消不保存"用 1 条通用用例）
- sop-layers.md 的 L1/L2/L3 templates 里，每个测试点下面列出的 sub-bullet 被模型理解成了"一条用例的多个步骤"而不是"多条独立用例"
- 这些规则在**手工 QA** 场景下是合理的（节省用例数量），但**自动化 QA** 场景下是有害的：
  - Playwright 引用时，1 条用例 = 1 个 test function / 1 个核心 assertion
  - 多步合并用例失败时无法精确报告哪一步挂了
  - 字段合并用例让每个字段的独立状态验证缺失
  - 选项精简让未测选项成为盲区

## 设计原则（本轮）

1. **不做过度设计** —— 不引入新 Task agent，不改架构，不加重试 scaffolding
2. **依赖模型能力的正确落点** —— 让模型做"理解文档结构 + 照抄字面 heading"，让脚本做"机械字符串比对"
3. **尊重现有长上下文处理策略** —— 当前 v3.0 的"读一次 → 机械切 → 每 agent 只看自己的 ~60KB 切片"是对的，只修补 bug 不改策略
4. **优雅失败优于静默错** —— 脚本匹配不到 heading 时宁可 raise 也不要 fuzzy fallback，配合诊断信息帮用户快速定位
5. **一用例一功能点（自动化优先）** —— 生成的用例既是手工测试依据，也是 Playwright 自动化测试的参考。自动化引用时，1 条用例对应 1 个 test function / 1 个核心 assertion。任何鼓励合并的规则在本轮一律删除

## 改动清单

### 改动 1：`analysis-schema.md` — 契约修正

将 `heading_pattern` 重命名为 `heading_text`，并在说明中**明确它是字面文本**。

- 将 schema 中 `"heading_pattern": "..."` 改为 `"heading_text": "..."`
- 字段说明改为：
  > 该模块在 markdown 文档中的标题行**字面文本**（含 `#` 前缀），必须与文档原文**逐字一致**，包括所有空格、标点、编号。**不得**包含 `\s+`、`^`、`\d`、`+`、`*` 等正则元字符。
  >
  > - ✅ 正确：`# 1 资产申请管理`
  > - ✅ 正确（含非换行空格）：`## 1.2\xa0本级管理`（如果文档原文就是这样，就照抄）
  > - ❌ 错误：`^# 1\s+资产申请管理`（含正则字符）
  > - ❌ 错误：`# 1 资产申请管理 `（多余尾空格 —— 不过 split 脚本会 normalize，所以也能跑通，但不推荐）

### 改动 2：`SKILL.md` Step 2 — Analysis agent prompt 调整

Analysis agent 的指令中加一条强约束：

> `module_groups[].heading_text` 必须是文档中该模块标题行的**逐字复制**（包括所有空格、标点、编号格式）。**不要**加任何正则字符（`^`、`\s`、`\d`、`+`、`*` 等）。如果文档里的标题是 `# 1 资产申请管理`，你就写 `# 1 资产申请管理`，一字不差。如果文档里含有非换行空格 `\xa0` 或全角空格 `\u3000`，照抄即可，切割脚本会负责 normalize。

同时将 SKILL.md Step 2 第 86 行中提到 `heading_pattern` 的地方更新为 `heading_text`。

### 改动 3：`scripts/split_doc.py` — 字面匹配 + normalize + 诊断失败

完整重写为字面匹配。

**normalize 函数**（应用于文档每一行和 heading_text 两端）：
- `\ufeff`（UTF-8 BOM）→ 去除
- `\r`（CRLF 的 CR 部分）→ 去除
- `\xa0`（non-breaking space）→ 普通空格
- `\u3000`（全角空格）→ 普通空格
- 多个连续空格 → 一个空格
- 两端 strip

**匹配逻辑**：`normalize(line) == normalize(heading_text)`，**完全相等**。避免 `"# 1 资产申请管理"` 误匹配到 `"# 11 资产盘点"`、`"## 1.2"` 误匹配到 `"## 1.2.1"`。

**匹配失败处理**：**不要** fallback 到 substring 搜索。改为：
- stderr 输出 `"Cannot find heading_text: {repr(heading_text)}"`
- 用 `difflib.get_close_matches(normalize(heading_text), [normalize(l) for l in lines], n=5, cutoff=0.6)` 输出最接近的 5 行作为 diagnostic
- 输出格式便于用户复制粘贴到 analysis.json 里修正
- `raise ValueError`

**JSON 字段兼容**：脚本主读 `grp["heading_text"]`；若字段不存在但有旧字段 `grp["heading_pattern"]`，发出 deprecation warning 到 stderr 并同样处理。**v3.2.0 删除兼容**。

**向后兼容只保留一个版本**的原因：下一轮如果还有 project 用旧字段，也已经有了足够的迁移窗口。

重写后约 50-60 行，无 regex。同步更新 `scripts/test_split_doc.py`（见改动 9）。

### 改动 4：Python 调用跨平台 fallback

SKILL.md 中所有 `python3 <script>.py ...` 的调用改为先探测：

```bash
PY=$(command -v python3 >/dev/null 2>&1 && echo python3 || echo python)
"$PY" "${CLAUDE_PLUGIN_ROOT}/scripts/split_doc.py" ...
```

涉及位置：
- Step 2.5：`split_doc.py` 调用
- Step 5：`convert_to_xlsx.py` 调用

**适用环境分析**：
- macOS / Linux / WSL：`command -v python3` 命中 → 用 `python3`
- Windows + Git Bash（Claude Code 在 Windows 的标准 shell 之一）：`command -v python3` 通常未命中 → fallback 到 `python`
- Windows + cmd.exe / PowerShell：POSIX 写法不工作，**但 Claude Code 的 Bash 工具在这些 shell 下本身就无法工作**，所以这个分支不存在于我们的运行环境

**失败语义**：如果两个 Python 都不存在，`"$PY" script.py` 会报 `python: command not found`，用户可以从错误信息直接定位。

### 改动 5：`SKILL.md` Step 3 Agent B prompt — 字段顺序 + 覆盖（加强版）

在 "Agent B — L3 (If has_data_entry)" 小节的 Focus 描述后追加整块 prompt（**不是软约束**）：

```
### 字段遍历要求（严格执行）

**第一步 — Checklist 声明**：在开始生成用例前，先在思维中（不写入输出）列出 field_table 中所有字段名作为 checklist，例如：

  [ ] 登记状态
  [ ] 企业全称
  [ ] 企业简称
  [ ] 企业类型
  ...

**第二步 — 按序遍历**：严格按 field_table 数组顺序（即文档中字段出现的原始顺序）生成用例。对每个字段：
1. 查找其 type 对应的规则（参见 sop-layers.md L3）
2. **对该字段的每一条验证规则生成一条独立的测试用例**（不合并！见下文"颗粒度原则"）
3. 在 checklist 上标记该字段已覆盖

sop-layers.md L3 的"按字段类型分组"是**生成规则参考**（告诉你每种类型该测什么），**不是**组织结构。**不要**按字段类型聚合重排，也不要把所有文本字段放一起再把所有下拉放一起。

**第三步 — 覆盖校验**：生成完毕前检查 checklist，确认 field_table 的**每一个字段都至少出现在 1 条测试用例的 test_point 或 case_name 中**。

### 颗粒度原则（严格执行）

每条测试用例**只测试一个独立功能点**。以下都是**禁止**的：

- ❌ 一个文本字段的"必填 / 长度 / 特殊字符 / 空格"合并为 1 条用例
- ❌ 多个文本字段合并为 1 条用例（即便类型和规则相同）
- ❌ 下拉选项 ">5 个只测首末中" 的精简

应该是：
- ✅ 每个字段的每一条规则 = 1 条独立用例
  - "企业全称-必填校验"
  - "企业全称-长度上限校验"
  - "企业全称-特殊字符校验"
  - "企业全称-空格校验"
- ✅ 每个下拉选项 = 1 条独立用例（即使 >5 个，也要逐个测；若选项极多如 100+ 的行政区划，在需求未明确时标注 `[TODO: 选项数量确认测试策略]`）

**跨字段交互**（`condition_show` / `condition_required` / `cascade_fill` / `inline_create`）在遍历完所有字段后单独追加，每个交互场景也是 1 条独立用例。

**成本提示**：本原则会让 Agent B 的输出用例数 2-4x 于 v3.0。这是**有意为之**，目的是为 Playwright 自动化引用提供足够的颗粒度。
```

### 改动 5b（新增）：Merge Agent prompt — 覆盖率校验

在 SKILL.md Step 4 Merge Agent 的任务清单中追加一步（原清单 1-10 之后）：

> **11. 覆盖率校验**（仅当该 group 有 `has_data_entry=true`）：
> - 从 `analysis.json` 读取该 group 的 `field_table[].name` 列表
> - 检查所有合并后的测试用例，收集每条用例 `test_point` 和 `case_name` 中提到的字段名
> - 对 `field_table` 中的每个字段名，确认它至少出现在 1 条用例里
> - 若有字段未覆盖，在 `meta` 字段下新增 `coverage_warnings` 数组，每项格式 `"[TODO: 漏测字段 {field_name}]"`
> - 如有 warning，同时在 stderr 输出提醒

**成本**：5 行 prompt + ~10 行合并逻辑，非 scaffolding，是 prompt 加法。它和改动 5 互为兜底：改动 5 让 Agent B 尽量不漏；如果它还是漏了，merge 阶段 catch 住并明确标记，用户可以立刻在 Excel 里看到 `[TODO: 漏测字段 xxx]`。

**与颗粒度原则配合**：由于改动 11 要求每个字段的每条规则都是独立用例，预期一个字段会出现在**多条**用例中（例如"企业全称"会有必填 / 长度 / 特殊字符 / 空格至少 4 条）。覆盖率校验的门槛仍然是"≥1 条"，但实际健康值应该是"每字段 ≥3 条"左右。merge agent 可以作为一个额外的健康指标输出（非 blocking）。

### 改动 6：`sop-layers.md` — 使用说明提醒 + 颗粒度原则（扩展版）

**6a. L3 章节头部说明**：在 L3 标题下面、"按字段类型生成"小节**之前**加一段说明：

> **使用顺序**：本节列出的字段类型模板是**生成规则参考**（告诉你每种类型应该生成哪些测试用例），不是组织顺序。Agent B 必须按 `field_table` 中字段出现的顺序遍历，对每个字段查找其类型对应的规则并应用。**不要**按字段类型分组聚合。详见 SKILL.md Step 3 "Agent B 字段遍历要求"。
>
> **颗粒度**：本节列出的每一个子项（sub-bullet，例如 `"输入正常值保存成功"`、`"不输入(必填字段) → 提示必填"`）对应**一条独立的测试用例**，**不要**合并为一条多步骤用例。详见 Writing Guidelines 的"颗粒度原则"。

**6b. 删除 `sop-layers.md:248`** Writing Guidelines 中的多检查点合并允许：

```diff
- 一个测试用例可包含多个相关的检查步骤 (如搜索功能的多种输入情况)
```

**6c. 删除 `sop-layers.md:254-257` "用例精简规则"整节**，连同标题 `### 用例精简规则` 一起删除。

**6d. 在 `### 质量要求` 之后新增 `### 颗粒度原则` 小节**：

```markdown
### 颗粒度原则（最高优先级）

每条测试用例**只测试一个独立功能点**。这是最高优先级原则，任何其他规则与此冲突时以本原则为准。

- 本 SOP 中每一层（L0-L6）列出的每个子项（sub-bullet）对应**一条独立用例**，不合并为多步骤用例
- 每个字段的每一条验证规则 = 1 条独立用例（不合并同类型同规则字段）
- 每个下拉选项 = 1 条独立用例（不做"首末中"精简）
- 每个交互场景 = 1 条独立用例

**原因**：生成的用例既是手工测试依据，也是 Playwright 自动化测试的参考。自动化引用时，1 条用例对应 1 个 test function / 1 个核心 assertion，便于失败定位和报告。

**唯一例外 — 多步骤不等于多检查点**：
- ✅ `"1.点击搜索框 2.输入'测试A' 3.点击查询按钮" → "1.搜索框获得焦点 2.输入内容显示 3.显示匹配结果"` 是 1 条用例，因为它只测试"用有效关键字搜索"这 1 个功能点，只是 operation 有多步
- ❌ `"1.输入完整企业全称 2.输入企业简称 3.输入空格 4.输入特殊字符 5.输入超长字符串" → "1.显示匹配记录 2.显示包含简称的记录 3.显示全部记录 4.显示无记录 5.显示过长提示"` 是 **错误的**，应拆分为 5 条独立用例，每条测一种输入场景
```

**6e. 同步检查 L1/L2/L4/L5/L6 的 sub-bullet 结构**：不改 template 内容，只在每一层章节末尾追加一句：

> **每个 sub-bullet 生成一条独立用例，不合并**（详见 Writing Guidelines 颗粒度原则）。

避免模型读每一层时又忘掉原则。

### 改动 7：`.claude-plugin/plugin.json` — 版本号

`version` 从 `3.0.0` 升到 `3.1.0`（bugfix + minor 改进）。

### 改动 8（新增）：`references/example-analysis.json` — 同步 rename

当前文件 line 18 有：
```json
"heading_pattern": "## 1.1 资源池",
```

改为：
```json
"heading_text": "## 1.1 资源池",
```

这是本次 rename 的唯一非 doc/非 script 受影响文件（已通过 `grep -r heading_pattern plugins/test-case-generator/` 审计确认）。历史 plan doc（`2026-03-03-*.md`）作为时间点快照**不动**。

### 改动 9（新增）：`scripts/test_split_doc.py` — 测试同步与新增 case

**必须修改的现有 case**：
- Fixture 字段 `heading_pattern` → `heading_text`（lines 56-58、119）

**必须新增的 case**（列出具体用例，不用"同步更新"这种模糊说法）：

1. `test_heading_with_nbsp`：构造 heading 含 `\xa0` 的 markdown（例如 `## 1.1\xa0本级管理`），analysis.json 的 `heading_text` 同样含 `\xa0`，确认切割成功
2. `test_heading_with_fullwidth_space`：构造 heading 含 `\u3000` 全角空格，确认切割成功
3. `test_bom_and_crlf`：构造一个 UTF-8 BOM + CRLF 行尾的 markdown，确认第一个 heading（通常是 BOM 污染的那一行）能被正确匹配
4. `test_numbered_collision`：构造两个 heading `## 1 本级` 和 `## 11 资产盘点`，确认它们不会互相误匹配（完全相等匹配的保护）
5. `test_regex_heading_fails_loudly`：构造 `heading_text: "^# 1\\s+本级"` 这种错的输入，确认脚本 raise ValueError 且 stderr 含最接近的 5 行候选
6. `test_deprecation_warning_on_old_field`：构造只有 `heading_pattern` 字段的旧 analysis.json，确认脚本能跑通同时 stderr 出现 deprecation warning

### 改动 10（新增）：根 CLAUDE.md Version 行

按项目约定（`/Users/henry/dev/2_areas/henry-hub/CLAUDE.md` 顶部 Version 行），push 后更新为：

```
> Version: v0.8.0 (2026-04-08)
```

或者按 semver 的 patch 语义：`v0.7.1 (2026-04-08)`。本轮虽然只改一个插件，但颗粒度原则是 behavioral change（输出形态变了），**倾向 `v0.8.0`**（minor）。最终决定在实施时确认。

### 改动 11（新增，核心 principle shift）：SKILL.md Global Rules 加入颗粒度原则

在 SKILL.md "Global Rules for All Sub-Agents" 小节追加 2 条规则（顶部位置，优先级高于其他规则）：

```markdown
- **颗粒度原则（最高优先级）** — 每条测试用例**只测试一个独立功能点**。sop-layers.md 中每一层列出的每个 sub-bullet 对应一条独立用例。**禁止**合并多个检查点为一个多步骤用例。**禁止**合并同类型同规则的多个字段。**禁止**"下拉选项 >5 精简"。详见 sop-layers.md Writing Guidelines 的"颗粒度原则"。
- **自动化友好** — 生成的用例是 Playwright 自动化测试的参考来源。1 条用例对应 1 个 test function / 1 个核心 assertion。每条用例的 `case_name` 必须足够具体，便于脚本按名称定位（例如 `"企业全称-必填校验"` 而非 `"企业全称字段校验"`）。
```

这两条是本轮的**核心原则**，所有改动（尤其改动 5、6）的措辞都以它们为准绳。放在 Global Rules 顶部的原因是 SKILL.md 会把这段注入到每个 sub-agent 的 prompt 里，确保 A/B/C/D 四个 agent 都遵守。

## 不在本轮范围内

| 项 | 为什么不做 |
|---|---|
| G3：子 agent 空返回自动重试 | 属于 scaffolding，先信模型；下轮若网络仍不稳再加 |
| G4：groups 并行 waves | 触及架构，需要考虑 Task 并行上限和 merge 时序 |
| 新的 Splitter Task agent | 过度设计，split 是机械操作不该耗 token |
| Playwright 执行用例 | 用户明确延后（下一轮） |
| Excel 用例数量硬上限 | 颗粒度原则会让用例数 2-4x，可能出现 1000+ 条的 Excel。暂不限制，先跑一遍看实际体量 |

## 验收方式

### 回归测试（手动）

1. **跨平台冒烟**：
   - macOS：`pytest scripts/test_split_doc.py` 全绿
   - Windows（用户自测）：拿当前卡住的 42 页文档重跑一次，确认 split 阶段在 30 秒内成功
2. **字段顺序和覆盖**：
   - 用户拿一个 5-10 字段的需求文档跑一次，人工核对：
     - Excel 中 L3 相关用例的顺序与需求文档字段顺序一致
     - 每个字段在 `test_point` 或 `case_name` 中至少出现一次
     - 如果 Excel 的 meta 里出现 `coverage_warnings`，检查对应字段是否真的漏了
3. **颗粒度验证**（针对改动 11）：
   - 用户截图里的 ZYCZXZ_006 关键字搜索用例作为 baseline：v3.0 生成 1 条含 7 步的用例；v3.1 应当生成 **7 条独立用例**（每条测一个输入场景）
   - 验证方法：找一个含"关键字搜索"的需求文档（例如原截图的资源池新增）重跑，确认 `test_point = "关键字搜索"` 对应的用例数 ≥ 5 而不是 = 1
   - 验证 L3 字段用例：找一个含 3+ 文本字段的需求，确认每个文本字段都有"必填 / 长度 / 特殊字符" 至少 3 条独立用例
   - 验证下拉选项：找一个含 >5 选项的下拉字段，确认每个选项都有独立用例（而不是只测首末中）
4. **失败诊断**：
   - 手动改 analysis.json 把一个 heading_text 改成错的，跑一次，确认 stderr 输出含最接近的 5 行候选且用户能照着修
5. **用例数量 sanity check**：
   - 跑一遍后对比 v3.0 和 v3.1 的总用例数，预期 2-4x 增长
   - 若增长 <1.5x 说明改动 11 没生效；若增长 >6x 说明有 agent 误解了原则（例如为每个步骤都拆了一条）

### 契约回归

- 构造一个 `heading_text` 含特殊字符（`\xa0`、全角空格、数字编号）的 markdown 样例，跑 `split_doc.py`，确认切出来的文件数量和内容正确
- 构造一个 `heading_text` 误写成正则形式（`^# 1\s+资产`）的 analysis.json，跑 `split_doc.py`，确认它**优雅失败**并提示用户 heading_text 格式错误和 top-5 候选

## 变更文件总览

| 文件 | 改动类型 |
|------|----------|
| `plugins/test-case-generator/skills/test-case-generator/references/analysis-schema.md` | rename + spec |
| `plugins/test-case-generator/skills/test-case-generator/references/example-analysis.json` | rename 字段 |
| `plugins/test-case-generator/skills/test-case-generator/references/sop-layers.md` | 改动 6a-6e：L3 使用说明 + 删行 248 + 删用例精简规则节 + 新增颗粒度原则节 + L1/L2/L4/L5/L6 章节末提醒 |
| `plugins/test-case-generator/skills/test-case-generator/SKILL.md` | Step 2 / Step 3 Agent B / Step 4 Merge prompt + Global Rules 新增颗粒度原则 + 跨平台调用 |
| `plugins/test-case-generator/scripts/split_doc.py` | 重写 |
| `plugins/test-case-generator/scripts/test_split_doc.py` | 现有 case 改字段名 + 6 个新 case |
| `plugins/test-case-generator/.claude-plugin/plugin.json` | 3.0.0 → 3.1.0 |
| `CLAUDE.md`（根） | 顶部 Version 行 |

**零新增文件**，`split_doc.py` 重写但保留路径。

## 版本与发布

- test-case-generator 插件：`3.0.0` → `3.1.0`（minor，含颗粒度原则 behavioral change）
- henry-hub marketplace 根 CLAUDE.md Version 行：`v0.7.0 → v0.8.0 (2026-04-08)`（minor，因为插件行为改变；与改动 10 对齐）
- Commit 消息建议（推荐单 commit 方便回滚）：
  - `feat(test-case-generator): v3.1.0 enforce one-case-per-check + split_doc fixes`
  - 或者拆成若干个 commit：
    - `fix(test-case-generator): rewrite split_doc.py with literal match + diagnostics`
    - `feat(test-case-generator): enforce one-case-per-check granularity`
    - `fix(test-case-generator): field iteration order in Agent B prompt`
    - `feat(test-case-generator): add merge-time field coverage warnings`
