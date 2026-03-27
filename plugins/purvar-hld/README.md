# purvar-hld — 璞华概要设计说明书

从需求确认单和过往概设模板组装面向甲方交付的概要设计说明书，并转换为格式规范的 Word 文档。

## 核心理念

概设是合同要求的交付物，不是技术创作。功能范围在需求确认单中已经确认，技术/安全/部署章节在项目间变化不大。所以概设的工作本质是**格式转换 + 模板复用**。

## 包含的 Skills

| Skill | 触发词 | 用途 |
|-------|--------|------|
| concept-design | "生成概设"、"写概要设计"、"概设" | 从需求确认单 + 过往概设组装 Markdown 概设文档 |
| md-to-docx | "转Word"、"生成docx"、"/md-to-docx" | 将 Markdown 转换为格式规范的 Word 文档 |

## 内置资源

| 文件 | 说明 |
|------|------|
| `scripts/assemble_hld.py` | 概设分册拼接脚本（自动发现子系统、动态编号） |
| `scripts/post_process.py` | pandoc 输出后处理（封面、变更记录、字体修正、表格） |
| `scripts/build_template.py` | reference.docx 模板重建工具（18 个样式定义） |
| `templates/reference.docx` | pandoc reference-doc 模板 |

## 工作流程

```
concept-design (Phase 1-5)
  → 扫描素材 → 确认 → 并行提取 → 脚本拼接 → 核验
  → 输出：完整概设 .md

md-to-docx (手动触发)
  → pandoc + reference.docx → post_process.py → 最终 .docx
```

## 安装

```
/plugins install purvar-hld@henry-hub
```

## 版本历史

### v1.0.0

- 合并 concept-design (v2.0.0) 和 md-to-docx 为单一插件
- assemble_hld.py 动态化：自动发现分册、从 frontmatter 读取元信息
- 模板和脚本全部内置于插件
