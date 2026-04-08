# test-case-generator 最小化修复设计

日期：2026-04-08
版本目标：v3.1.0（bugfix + prompt 调优，无架构变更）

## 背景

v3.0 在真实用户（测试人员夏夕）手中暴露出 4 个问题，记录在微信聊天日志里：

1. **42 页需求文档生成卡住 1+ 小时** —— `split_doc.py` 在 Windows + 中文文档上失败，触发多轮人工干预。
2. **L3 数据输入层的字段用例按"字段类型"组织而非文档顺序** —— 测试人员核对时无法顺着需求文档走。
3. **存在字段被跳过（未生成用例）的情况** —— "用例精简规则"被模型当成了"可以漏字段"。
4. **Playwright 执行用例**另有一套问题 —— **不在本轮范围内**。

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
- SKILL.md Step 2.5 的调用写死 `python3`，Windows 下返回 exit 49（`python3` 不存在，只有 `python`）

### L3 字段顺序和覆盖问题的根因

- `sop-layers.md:75-146` L3 的内容是**按字段类型**组织的模板（文本输入框 / 下拉选择框 / 日期选择器 / …）
- Agent B 读这些模板时把它们当成了**组织结构**，而不是**生成规则参考**
- SKILL.md Step 3 Agent B prompt 没有明确指令说"按 `field_table` 数组顺序遍历"
- 也没有"每个字段至少一条用例"的约束
- "用例精简规则"（`sop-layers.md:254-257`）允许合并，但没说合并时 `test_point` 必须列出所涉及字段

## 设计原则（本轮）

1. **不做过度设计** —— 不引入新 Task agent，不改架构，不加重试 scaffolding
2. **依赖模型能力的正确落点** —— 让模型做"理解文档结构 + 照抄字面 heading"，让脚本做"机械字符串比对"
3. **尊重现有长上下文处理策略** —— 当前 v3.0 的"读一次 → 机械切 → 每 agent 只看自己的 ~60KB 切片"是对的，只修补 bug 不改策略
4. **所有改动可回滚** —— 每一处都是局部修改

## 改动清单

### 改动 1：`analysis-schema.md` — 契约修正

将 `heading_pattern` 重命名为 `heading_text`，并在说明中**明确它是字面文本**。

- 将 schema 中 `"heading_pattern": "..."` 改为 `"heading_text": "..."`
- 将字段说明从"标题行正则锚点"改为"该模块在 markdown 文档中的标题行字面文本（含 `#` 前缀），必须与文档中原文完全一致（包括空格和标点），不得包含 `\s+`、`^`、`\d` 等正则字符"
- 加一个 example：✅ `# 1 资产申请管理`；❌ `^# 1\s+资产申请管理`

### 改动 2：`SKILL.md` Step 2 — Analysis agent prompt 调整

Analysis agent 的指令中加一条强约束：

> `module_groups[].heading_text` 必须是文档中该模块标题行的**逐字复制**（包括所有空格、标点、编号格式）。**不要**加任何正则字符（`^`、`\s`、`\d`、`+`、`*` 等）。如果文档里的标题是 `# 1 资产申请管理`，你就写 `# 1 资产申请管理`，一字不差。

### 改动 3：`scripts/split_doc.py` — 字面匹配 + 空白规范化

完整重写为字面匹配，只处理以下 normalize：
- `\xa0`（non-breaking space）→ 普通空格
- `\u3000`（ideographic space / 全角空格）→ 普通空格
- 多个连续空格 → 一个空格
- 两端 strip

匹配逻辑：`normalize(line) == normalize(heading_text)`（完全相等，不是 substring），避免 "# 1" 误匹配到 "# 10"。

Fallback：如果完全相等找不到，再尝试 `normalize(heading_text) in normalize(line)`（作为兜底），同时在 stderr 输出 warning 让用户知道命中的是模糊匹配。

JSON 字段：脚本读取 `grp["heading_text"]`；若存在旧字段 `grp["heading_pattern"]`（向后兼容一轮），发出 deprecation warning 并同样处理。**下个版本删除兼容。**

重写脚本约 40 行，删除当前的 `re.escape` + fallback substring 逻辑。同步更新 `scripts/test_split_doc.py`。

### 改动 4：Python 调用跨平台 fallback

SKILL.md 中所有 `python3 <script>.py ...` 的调用改为：

```bash
python3 <script>.py ... 2>/dev/null || python <script>.py ...
```

涉及位置：
- Step 2.5：`split_doc.py` 调用
- Step 5：`convert_to_xlsx.py` 调用

**注意**：`2>/dev/null` 只在 `python3` 本身不存在时才会触发 fallback。如果 `python3` 存在但脚本运行失败，错误会被吞掉 —— 这是一个有意识的 trade-off：
- 优点：Windows 环境无 `python3` 时自动走 `python`
- 缺点：失败信息需要从第二次运行（`python <script>`）的输出看，可能有少量误导

更稳妥的替代（如果有空）：先用 `command -v python3 >/dev/null && PY=python3 || PY=python`，再 `$PY script.py`。实现时选后者，避免吞错。

### 改动 5：`SKILL.md` Step 3 Agent B prompt — 字段顺序 + 覆盖

在 "Agent B — L3 (If has_data_entry)" 小节的 Focus 描述后追加：

> **字段遍历顺序**：严格按 `field_table` 数组顺序（即文档中字段出现的原始顺序）生成用例，**不要**按字段类型聚合重排。`sop-layers.md` 中 L3 按字段类型分组的模板是**生成规则参考**（告诉你每种类型该测什么），不是组织结构。
>
> **字段覆盖**：`field_table` 中的**每一个字段都必须至少出现在 1 条测试用例中**。按照"用例精简规则"合并时，合并后的用例 `test_point` 或 `case_name` 必须显式列出所覆盖的字段名（例如 `"企业全称/企业简称/法人代表 文本字段必填校验"`），不得用"全部文本字段"之类的模糊表述隐藏缺失。
>
> **生成策略**：对每个字段，先判断其 type，再去 `sop-layers.md` L3 找该 type 对应的生成规则，应用规则生成用例。跨字段交互（`condition_show` / `condition_required` / `cascade_fill` / `inline_create`）在遍历完所有字段后单独追加。

### 改动 6：`sop-layers.md` L3 章节 — 使用说明提醒

在 L3 标题下面、"按字段类型生成"小节**之前**加一段说明：

> **使用顺序**：本节列出的字段类型模板是**生成规则参考**（告诉你每种类型应该生成哪些测试用例），不是组织顺序。Agent B 必须按 `field_table` 中字段出现的顺序遍历，对每个字段查找其类型对应的规则并应用。**不要**按字段类型分组聚合。

### 改动 7：`.claude-plugin/plugin.json` — 版本号

`version` 从 `3.0.0` 升到 `3.1.0`（bugfix + minor 改进）。

## 不在本轮范围内

| 项 | 为什么不做 |
|---|---|
| G3：子 agent 空返回自动重试 | 属于 scaffolding，先信模型；下轮若网络仍不稳再加 |
| G4：groups 并行 waves | 触及架构，需要考虑 Task 并行上限和 merge 时序 |
| Merge 阶段字段覆盖率校验 | 先信 prompt；若下轮仍漏字段，再加"程序化兜底" |
| 新的 Splitter Task agent | 过度设计，split 是机械操作不该耗 token |
| Playwright 执行用例 | 用户明确延后 |

## 验收方式

### 回归测试（手动）

1. **跨平台冒烟**：
   - macOS：用现有 `scripts/test_split_doc.py` 跑过
   - Windows（用户自测）：用户拿掉当前卡住的 42 页文档重跑一次，确认 split 阶段在 30 秒内成功
2. **字段顺序和覆盖**：
   - 用户拿一个 5-10 字段的需求文档跑一次，人工核对：
     - Excel 中 L3 相关用例的顺序与需求文档字段顺序一致
     - 每个字段在 `test_point` 或 `case_name` 中至少出现一次

### 契约回归

- 手动构造一个 `heading_text` 含特殊字符（`\xa0`、全角空格、数字编号）的 markdown 样例，跑 `split_doc.py`，确认切出来的文件数量和内容正确
- 构造一个 `heading_text` 误写成正则形式（`^# 1\s+资产`）的 analysis.json，跑 `split_doc.py`，确认它**优雅失败**并提示用户 heading_text 格式错误

## 变更文件总览

| 文件 | 改动类型 |
|------|----------|
| `skills/test-case-generator/references/analysis-schema.md` | rename + spec |
| `skills/test-case-generator/references/sop-layers.md` | 加一段说明 |
| `skills/test-case-generator/SKILL.md` | Step 2 prompt + Step 3 Agent B prompt + Step 2.5/5 调用 |
| `scripts/split_doc.py` | 重写 |
| `scripts/test_split_doc.py` | 同步测试 |
| `.claude-plugin/plugin.json` | 3.0.0 → 3.1.0 |

**零新增文件，零删除文件**（除非测试脚本需要新增 case）。

## 版本与发布

- test-case-generator 插件：`3.0.0` → `3.1.0`
- henry-hub marketplace CLAUDE.md 顶部 Version 行：对应更新（patch level，小改版）
- commit 消息建议前缀：`fix(test-case-generator): ...`
