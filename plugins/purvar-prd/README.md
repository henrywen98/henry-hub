# purvar-prd — 璞华需求文档工作流

璞华科技的需求文档生成工具集，从需求素材（会议纪要、需求清单、原型描述等）生成两种受众的文档（开发/测试 vs 客户领导），提供 PRD 澄清，并把客户用的需求确认单一键转 Word。

## 核心理念

需求文档分两类受众：
- **开发与测试**：要细——字段类型、必填、校验规则、异常分支。读 PRD。
- **客户领导**：要粗——做什么、范围在哪、关键规则对不对。签确认单。

这两种文档不能合一份，所以工作流分成 PRD 与确认单两条线，并提供澄清和 Word 导出辅助。

## 包含的 Skills

| Skill | 触发词 | 用途 |
|-------|--------|------|
| purvar-prd | `/purvar.prd` `/purvar.confirm` `/purvar.clarify` | 生成 PRD/需求确认单/澄清 PRD（命令封装） |
| confirm-to-docx | "确认单转Word"、"BP 确认单 docx"、"/confirm-to-docx" | 把 `/purvar.confirm` 输出的 md 转成符合璞华格式规范的 Word |

## 包含的 Commands

| Command | 受众 | 用途 |
|---|---|---|
| `/purvar.prd <素材>` | 开发 + 测试 | 功能迭代型 PRD（含六列信息项表格、异常边界、验收标准） |
| `/purvar.confirm <素材>` | 客户领导 | 需求确认单（功能概述 + 要点 + 信息项清单 + 业务规则，纯业务语言） |
| `/purvar.clarify [PRD路径]` | 自查 | 扫描 PRD 模糊点，逐题交互式澄清并写回 PRD |

## 内置资源

| 文件 | 说明 |
|---|---|
| `references/prd-rules.md` | PRD 编写规则（颗粒度、章节结构、六列表格定义） |
| `references/confirm-rules.md` | 需求确认单编写规则（颗粒度、章节结构、两列表格定义） |
| `references/clarify-categories.md` | PRD 澄清的 7 个扫描维度 |
| `skills/confirm-to-docx/scripts/build.sh` | 一键 md→docx |
| `skills/confirm-to-docx/scripts/build_reference.py` | 重建 reference-zhcn.docx 模板 |
| `skills/confirm-to-docx/scripts/postprocess.py` | 插封面 + 规整表格列宽 |
| `skills/confirm-to-docx/templates/reference-zhcn.docx` | pandoc reference-doc 模板（中文优化） |

## 典型工作流

```
拿到需求素材
  ├── 给开发/测试看 → /purvar.prd  → PRD.md
  │   └── 自查模糊点 → /purvar.clarify → PRD.md（更新）
  └── 给客户签字   → /purvar.confirm → 确认单.md
                       └── 导出 Word → confirm-to-docx skill → 确认单.docx
```

## 安装

```
/plugins install purvar-prd@henry-hub
```

## 版本历史

### v1.1.0

- 新增 `confirm-to-docx` skill：把 `/purvar.confirm` 输出的 md 转成符合璞华格式规范的 Word，含自动注入封面页（项目信息表 + 修订历史表，留空待手填）和表格列宽预设
- 与 `purvar-hld` 的 `md-to-docx`（概要设计：仿宋/楷体）区分：本 skill 走需求确认单（等线/黑体）路线

### v1.0.0

- 初版：`/purvar.prd` `/purvar.confirm` `/purvar.clarify` 三命令工作流
