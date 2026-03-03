---
name: purvar-prd
description: This skill should be used when the user asks to "生成PRD", "写PRD", "功能迭代PRD", "需求确认单", "生成需求确认单", "璞华PRD", "澄清PRD", "PRD模糊点", "检查PRD完整性", "PRD遗漏", "审查PRD", "写需求文档", "从会议纪要生成PRD", "从需求清单生成文档", or mentions creating requirement documents for development/test teams or client stakeholders. Provides /purvar.prd, /purvar.confirm, /purvar.clarify commands.
---

# 璞华需求文档工作流

璞华科技的需求文档生成工具集，从需求素材（会议纪要、需求清单、原型描述、需求确认单等）自动生成两种不同受众的文档，并提供PRD澄清能力。

## 可用命令

### /purvar.prd — 生成功能迭代型PRD

**受众**：开发工程师和测试工程师

从需求素材生成详细的功能迭代型PRD。面向已有业务系统的功能新增或变更，核心检验标准——"开发看了知道怎么做吗？测试看了知道怎么验吗？"

输出结构：原型 → 变更概要 → 影响范围 → 功能说明（含**六列信息项表格**：信息项/类型/必填/校验规则/默认值/备注）→ 异常与边界 → 验收标准 → 开放问题

**使用**：`/purvar.prd <需求素材>`

### /purvar.confirm — 生成需求确认单

**受众**：客户方分管领导和业务对接人

从需求素材生成面向客户的需求确认单。用大白话写，去掉所有技术细节，核心检验标准——"这是领导签字时需要确认的信息吗？"

输出结构：功能概述 → 功能要点 → 信息项清单（**两列表格**：信息项/备注）→ 审批流程（如有）→ 特殊业务规则（如有）

**使用**：`/purvar.confirm <需求素材>`

### /purvar.clarify — 澄清PRD

识别已有PRD中的模糊区域，通过逐题交互式提问澄清并直接更新PRD文件。

扫描7个维度：变更概要、影响范围、信息项完整性、业务规则、异常与边界、验收标准、开放问题。每次最多提5个问题，每题带推荐选项和理由。

**使用**：`/purvar.clarify` 或 `/purvar.clarify <PRD文件路径>`

## 何时用哪个命令

| 场景 | 命令 |
|------|------|
| 拿到需求素材，需要给开发和测试看 | `/purvar.prd` |
| 拿到需求素材，需要给客户确认签字 | `/purvar.confirm` |
| PRD写完了，想检查有没有遗漏 | `/purvar.clarify` |
| 同一批素材，两份文档都要 | 先 `/purvar.prd` 再 `/purvar.confirm` |

## 典型工作流

1. 收到需求素材（会议纪要/需求清单/原型描述）
2. `/purvar.confirm` → 生成需求确认单 → 发客户确认范围
3. 客户确认后 `/purvar.prd` → 生成PRD → 给开发测试
4. `/purvar.clarify` → 检查PRD完整性 → 补全模糊点

## 两种文档的关键区别

| 维度 | PRD（/purvar.prd） | 需求确认单（/purvar.confirm） |
|------|-------------------|---------------------------|
| 受众 | 开发+测试 | 客户领导 |
| 信息项表格 | 六列（含类型、必填、校验规则等） | 两列（信息项+备注） |
| 语言风格 | 技术精确 | 大白话，零技术术语 |
| 颗粒度 | 字段级（开发能拆任务） | 功能级（确认做不做、做什么） |
| 验收标准 | checkbox格式，逐条可验 | 无 |
| 异常与边界 | 详细场景表 | 无 |

## 参考资料

详细的编写规则和参考示例（位于插件根目录 `references/` 下）：

- **`${CLAUDE_PLUGIN_ROOT}/references/prd-rules.md`** — PRD完整编写规则、输出结构模板、两个参考示例（委派人员管理、市国资委备案）
- **`${CLAUDE_PLUGIN_ROOT}/references/confirm-rules.md`** — 需求确认单完整编写规则、输出结构模板、三个参考示例（委派人员管理、市国资委备案、重点项目推进表）
- **`${CLAUDE_PLUGIN_ROOT}/references/clarify-categories.md`** — PRD澄清的7个扫描维度及具体检查项
