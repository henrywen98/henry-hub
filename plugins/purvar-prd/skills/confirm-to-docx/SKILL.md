---
name: confirm-to-docx
description: >-
  把"需求确认单"的 Markdown 转成符合璞华格式规范的 Word（.docx）：
  自动注入封面页（项目名/编号/项目信息表/修订历史表，全部留空待手填），
  正文使用 等线 12pt + 黑体偶数级标题，所有表格按列数命中预设列宽。
  当用户提到"需求确认单转Word/docx"、"确认单导出 Word"、"BP 确认单 docx"、
  "把确认单 md 变成 docx"、"/confirm-to-docx"、或者已经在用 /purvar.confirm
  生成确认单 md 之后想要 Word 交付件时触发本 skill。
  和 purvar-hld 的 md-to-docx 区分：那个是概要设计（仿宋/楷体、6 列变更记录、
  目录），本 skill 是需求确认单（等线/黑体、4 列项目信息表、4 列修订历史）。
  不适用：原始概要设计文档、其他通用 md→docx（用 purvar-hld 的 md-to-docx）。
---

# 需求确认单 Markdown → Word

把按 `/purvar.confirm` 规范写好的 Markdown 转成可交付给客户领导签字的 Word 文档。
样式取自客户已签字的真实确认单（杭州产投二期），针对中文做了字体显式声明、
表格列宽预设等优化，避免不同电脑上字体回退或列宽塌缩。

## 何时使用

- 拿到一份"需求确认单 md"想要 Word 交付件
- `/purvar.confirm` 生成完毕后用户问"怎么导出 Word"
- 用户提到"确认单转 docx"、"BP 确认单导出 Word"、"需求确认单转 Word"
- **不要用本 skill** 处理概要设计文档——那是 `purvar-hld` 的 `md-to-docx`

## 前置条件

- `pandoc` 已安装（`brew install pandoc`）
- `python-docx` 已安装（`pip3 install python-docx`）

## 输入约定

源 Markdown 应符合 `/purvar.confirm` 输出结构：

```
# 需求确认单 — <项目名>

## 1. <模块名>
### 1.1 功能概述
### 1.2 功能要点
### 1.3 信息项清单
| 信息项 | 备注 |
| ...
### 1.4 特殊业务规则（可选）

## 2. <下一个模块>
...
```

图片用相对路径 `![alt](docs/screenshots/xx.png)`。脚本会以 md 文件所在目录
为 `--resource-path`，相对路径能直接解析。

封面页元数据**不要写在 md 里**——脚本会自动插入空白封面表，由用户在 Word
里手填项目名、编号、版本、项目经理、编写日期、修订历史。

## 执行步骤

### 1. 校验输入

```bash
ls "<md文件路径>"
ls "${CLAUDE_PLUGIN_ROOT}/skills/confirm-to-docx/templates/reference-zhcn.docx"
```

如果 reference-zhcn.docx 不存在（首次使用或人为删除），先生成：

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/confirm-to-docx/scripts/build_reference.py"
```

读 md 内容，扫一遍：
- 检查所有 `![alt](path)` 图片路径是否存在（远程 URL 跳过）
- 缺图就**列出来询问用户是否继续**，不要直接中断
- **主动从上下文推断可填字段**：项目名称（md 文件名/标题）、需求版本（默认 V1.0 如首版）、最新编辑日期（今天）、需求类型（首版默认 initial）、编写人（git config user.name 或问用户），把这些值通过 build.sh 的 `--` 透传给 postprocess。**确实不知道的字段才留空**（如项目经理、业务部门、需求调研日期、客户确认签字、编号）。

### 2. 一键转换（推荐）

```bash
# 不预填封面：所有字段留空待手填
bash "${CLAUDE_PLUGIN_ROOT}/skills/confirm-to-docx/scripts/build.sh" \
  "<md文件路径>" "<输出docx路径>"

# 预填封面：`--` 之后的参数全部透传给 postprocess.py
bash "${CLAUDE_PLUGIN_ROOT}/skills/confirm-to-docx/scripts/build.sh" \
  "<md文件路径>" "<输出docx路径>" \
  -- \
  --project-name "<项目名称>" \
  --version V1.0 \
  --date 2026-04-27 \
  --req-type initial \
  --changelog 初稿 \
  --editor "<编写人>"
```

第二个参数省略时，输出与源 md 同目录、同文件名、扩展名 `.docx`。

### 封面预填字段（postprocess.py CLI 参数）

| 参数 | 对应封面位置 | 推断默认 |
|---|---|---|
| `--project-name` | 主标题 + 项目信息行 1 第二格 | md 标题或文件名 |
| `--issue-no` | 编号括号内 | 留空 |
| `--version` | 项目信息行 2 + 变更记录行 1 版本 | V1.0（首版） |
| `--manager` | 项目信息行 2 项目经理 | 留空（一般不知道） |
| `--editor` | 项目信息行 3 编写人 + 变更记录行 1 修改人 | git config user.name |
| `--date` | 项目信息行 3 编辑日期 + 变更记录行 1 日期 | 今天 |
| `--department` | 项目信息行 4 业务部门 | 留空（一般不知道） |
| `--research-dates` | 项目信息行 4 需求调研日期 | 留空；多日期用 `\n` 分隔 |
| `--req-type` | 行 5 复选框 ☑ 命中项 | 首版传 `initial` |
| `--changelog` | 变更记录行 1 变更内容 | 首版传 `初稿` |
| `--changelog-version` / `--changelog-date` | 变更记录单独覆盖 | 不填则沿用 `--version` / `--date` |
| `--no-cover` | 跳过封面（已有封面或要重跑表格规整时） | — |

`--req-type` 取值：`initial` / `new` / `change` / `env` / `""`。

### 3. 或者分步执行（需要排查问题时）

```bash
# 3.1 pandoc 转换正文
pandoc "<md路径>" \
  -o "<docx路径>" \
  --reference-doc="${CLAUDE_PLUGIN_ROOT}/skills/confirm-to-docx/templates/reference-zhcn.docx" \
  --resource-path="<md所在目录>" \
  --from gfm

# 3.2 后处理：插入封面 + 规整列宽 + 表头加底色（封面字段同样可传）
python3 "${CLAUDE_PLUGIN_ROOT}/skills/confirm-to-docx/scripts/postprocess.py" \
  "<docx路径>" \
  --project-name "<项目名称>" --version V1.0 --date 2026-04-27 \
  --req-type initial --changelog 初稿 --editor "<编写人>"
```

### 4. 告知用户结果

输出文件路径，列出哪些字段已预填、哪些留空，并提醒：
- 留空字段在 Word 里手填（一般是项目经理 / 业务部门 / 需求调研日期 / 编号 / 客户确认签字）
- 客户确认签字区留高，便于打印纸面手签
- 检查图片是否都嵌进去了（pandoc 偶尔会在远程图片或异常路径上静默跳过）
- 如果新加的表格列数不在预设里（2/3/4/6 列），后处理会兜底等宽分布；想要专属列宽请改 `scripts/postprocess.py` 的 `COL_WIDTHS` 字典

## 生成的文档结构

封面页（后处理插入，对齐杭州产投-AI应用 标准模板）：

```
（项目名称）           — 26pt 加粗居中
需求确认单             — 22pt 加粗居中
编号：(        )       — 12pt 右对齐
┌─项目信息表 (4 列, 6 行)─────────────────────────────┐
│ 项目名称   │ <跨 3 列 项目全称>                      │
│ 需求版本   │            │ 项目经理     │             │
│ 编写人     │            │ 最新编辑日期  │             │
│ 业务部门   │            │ 需求调研日期  │             │
│ 需求类型   │ ☐初始需求  ☐新增需求  ☐需求变更  ☐系统环境变更 │
│ 客户确认   │ <跨 3 列  确认签字：留高签字区>          │
└──────────────────────────────────────────────────┘
变更记录               — 12pt 加粗左对齐
┌─变更记录表 (4 列)───────────────────────────────────┐
│ 版本 │ 日期 │ 变更内容 │ 修改人                       │
│      │      │          │                             │
└──────────────────────────────────────────────────┘
─── 分页符 ───
正文（pandoc 转换）
├── # 需求确认单 — XXX  → Heading 1（22pt 加粗居中）
├── ## n. 模块          → Heading 2（16pt 黑体加粗）
├── ### n.x 子节        → Heading 3（16pt 加粗）
├── 表格                → 后处理按列数应用预设列宽，表头 F2F2F2 灰底
└── 图片                → 原样嵌入
```

## 样式规范

| 元素 | 字体 | 字号 | 其他 |
|---|---|---|---|
| 正文 | 等线 / Calibri | 12pt | 1.5 倍行距、两端对齐、首行缩进 2 字符 |
| H1 | 等线 | 22pt | 加粗、居中、kern 44 |
| H2 | 黑体 | 16pt | 加粗 |
| H3 | 等线 | 16pt | 加粗 |
| H4 | 黑体 | 14pt | 加粗 |
| H5 | 等线 | 14pt | 加粗 |
| H6 | 黑体 | 12pt | 加粗 |
| 表格 | 等线 | 12pt | 0.5pt 单线全边框、居中、fixed 布局 |
| 表头 | 等线 | 12pt | 加粗、F2F2F2 灰底、水平+垂直居中 |

页面：A4 纵向，上下页边距 2.54 cm，左右页边距 3.17 cm。

## 表格列宽预设

`scripts/postprocess.py::COL_WIDTHS` 按列数命中（单位 twip，总宽 8306 = 页内文宽）：

| 列数 | 列宽 | 说明 |
|---|---|---|
| 2 | 4153 / 4153 | 通用 2 列等宽 |
| 2（信息项-备注）| 2200 / 6106 | 第 2 列表头含"备注"时自动选用 |
| 3 | 1800 / 2200 / 4306 | label / 短值 / 长备注 |
| 4 | 2076 ×4 | 评分换算等等宽 4 列 |
| 4（项目名称起头）| 1660 / 2493 / 2076 / 2077 | 封面项目信息表 |
| 6 | 1500 / 1361 ×5 | 维度 + 多业务线 |
| 其他列数 | 自动等宽 | 兜底 |

## 调整样式

改正文/标题/表格的字体字号：编辑 `scripts/build_reference.py` 里的
`configure_normal` / `configure_heading` / `configure_table_grid`，重跑：

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/confirm-to-docx/scripts/build_reference.py"
```

模板会重新生成，下次转换自动生效。

改某种列数的列宽：编辑 `scripts/postprocess.py` 里的 `COL_WIDTHS` 字典即可，
不需要重建模板。

## 故障排查

**pandoc 报 "could not fetch image"**：检查 md 里的图片路径是相对路径还是
绝对路径。脚本把 `--resource-path` 设为 md 文件所在目录，所以路径要相对
md 文件，比如 md 在 `docs/req.md` 里，图片放在 `docs/screenshots/x.png`，
md 里写 `![](screenshots/x.png)` 而不是 `![](docs/screenshots/x.png)`。

**Word 打开后表格列宽不对**：检查 `scripts/postprocess.py` 里的
`COL_WIDTHS_LABEL_NOTE_2`/`COL_WIDTHS_PROJECT_INFO_4` 命中条件——分别用
"备注"在表头和第 0 列文本是"项目名称"识别。如果你的 md 表头不一样，
要么改命中条件，要么把对应列宽加到 `COL_WIDTHS` 里。

**字体在另一台电脑显示成宋体**：模板已显式设置 eastAsia=等线，但如果对方
机器没装等线（很罕见），Word 会回退。可以把 `build_reference.py` 里的
"等线" 改成 "微软雅黑"（更通用）重新生成模板。
