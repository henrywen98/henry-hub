---
name: md-to-docx
description: 将 Markdown 文件转换为格式规范的 Word 文档（.docx），使用 pandoc + reference-doc 模板 + python-docx 后处理。当用户提到"转Word"、"生成docx"、"md转word"、"markdown转文档"、"/md-to-docx"时触发此技能。
---

# Markdown → Word 转换

将 Markdown 文件转换为与公司交付模板格式一致的 Word 文档。

## 前置条件

- `pandoc` 已安装（`brew install pandoc`）
- `python-docx` 已安装（`pip3 install python-docx`）

## Markdown 编写规范

### YAML Frontmatter（封面信息）

```yaml
---
title: 项目名称          # 封面主标题（黑体 26pt 居中）
subtitle: 概要设计说明书   # 封面副标题 + 页眉文字
company: 璞华科技有限公司  # 封面公司名（仿宋 16pt）
date: 2026年3月          # 封面日期（仿宋 16pt）
---
```

### 正文从章节标题开始

frontmatter 的 `title` 仅用于封面，正文**不要**重复写项目名作为一级标题：

```markdown
# 引言          ← 正确：正文从章节标题开始
## 编写目的
```

### 样式映射

| Markdown 语法 | Word 样式        | 字体            | 行距  |
|--------------|-----------------|----------------|-------|
| `#`          | Heading 1       | 黑体 16pt       | 1.5   |
| `##`         | Heading 2       | 楷体 16pt       | 1.5   |
| `###`        | Heading 3       | 仿宋加粗 16pt    | 1.73  |
| `####`       | Heading 4       | 黑体 14pt 加粗   | 1.5   |
| 正文          | Body Text       | 仿宋 14pt 缩进   | 1.5   |
| 首段          | First Paragraph | 仿宋 14pt 缩进   | 1.5   |
| 代码块        | Source Code     | Courier New 10pt | 1.0   |
| 列表          | Compact         | 仿宋 14pt        | 1.5   |

## 生成的文档结构

```
封面页（标题、副标题、公司、日期）    ← 后处理插入
─── 分节符 ───
变更记录表（6列空表）               ← 后处理插入
─── 分节符 ───
目录                              ← pandoc --toc 生成
正文（标题、段落、表格、图片……）     ← pandoc 转换
```

页眉：所有节显示 subtitle 字段内容，右对齐，仿宋 9pt

## 执行步骤

收到用户的 Markdown 文件路径后，按以下步骤执行：

### 1. 确认文件和模板

```bash
ls "<md文件路径>"
ls "templates/reference.docx"
```

### 2. 预检：验证引用资源和 frontmatter

读取 Markdown 文件内容，检查以下项目：

**Frontmatter 检查：**
- 确认存在 YAML frontmatter（`---` 包裹）
- 确认 `title` 字段存在且非空
- 如果缺少 `subtitle`/`company`/`date`，提醒用户补充（非阻塞，可继续）

**引用资源检查：**
- 用 Grep 提取所有图片引用：`!\[.*?\]\((.*?)\)`
- 对每个图片路径，以 Markdown 文件所在目录为基准，检查文件是否存在
- 远程 URL（http/https 开头）跳过检查
- 如有缺失文件，**列出所有缺失路径并询问用户是否继续**，不要直接中断

**标题重复检查：**
- 检查正文第一个 `#` 标题是否与 frontmatter 的 `title` 内容相似
- 如果重复，提醒用户删除正文中的重复标题

所有检查通过（或用户确认继续）后再执行转换。

### 3. 用 pandoc 生成初版 Word

```bash
pandoc "<md文件路径>" \
  --reference-doc="${CLAUDE_PLUGIN_ROOT}/templates/reference.docx" \
  --resource-path="<md文件所在目录>" \
  -o "<输出docx路径>" \
  --toc \
  --toc-depth=3 \
  -M toc-title="目录"
```

输出路径规则：与源 Markdown 文件同目录，扩展名改为 `.docx`。
例如 `docs/概要设计.md` → `docs/概要设计.docx`

`--resource-path` 必须设为 md 文件所在目录，这样 pandoc 才能正确解析相对路径引用的图片。

### 4. 执行后处理脚本

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/post_process.py \
  "<输出docx路径>" \
  "<md文件路径>"
```

后处理脚本完成以下工作：
- 清理 TOC 域代码（消除 Word 打开时的"是否更新域"弹窗）
- 移除 pandoc 自动生成的元数据段落（Title/Subtitle/Date）
- 修正所有 run 的中文字体（eastAsia 属性）
- 插入封面页（3空行→标题→副标题→12空行→公司→日期→分节符）
- 插入变更记录空表（仿宋 12pt 表头，6列 x 6行）
- 设置页眉（所有节，右对齐，仿宋 9pt）

### 模板样式调整（仅在需要时）

如需调整 Word 输出的样式（字体、字号、行距等），修改 `${CLAUDE_PLUGIN_ROOT}/scripts/build_template.py` 中的 `STYLE_DEFS` 字典，然后运行：

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/build_template.py
```

这会重新生成 `templates/reference.docx`。之后重新转换文档即可生效。

### 5. 告知用户结果

输出生成的文件路径，提醒用户：
- 检查封面信息是否正确
- 如需填写变更记录表，直接在 Word 中编辑
- 目录已生成为静态文本（无需更新域）
