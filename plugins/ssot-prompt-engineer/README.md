# ssot-prompt-engineer

SSOT 规则提取器。从成品文档中反向提取生成规则（结构、写作模式、模板分类），输出标准化的 Skill Blueprint 文件，作为 skill-creator 的上游输入。

## 核心理念

```
样本文档 ──→ [SSOT Skill] ──→ skill-blueprint.md ──→ [skill-creator]
```

**不是写 Prompt，而是提取规则。** SSOT skill 是分析工具：从成品中提取隐性知识，结构化为 Skill Blueprint，交给 skill-creator 包装为可用的 skill。

## 使用场景

当用户提到以下内容时触发：

- "提取规则" / "extract rules"
- "逆向工程" / "reverse engineer"
- "生成蓝图" / "skill blueprint"
- "从样本提取" / "分析文档结构"
- "extract SOP" / "formalize the SOP"
- 给出一份成品文档，要求提取其写作规范/结构/SOP

## 工作流程

1. **自动分析**：读取样本文档，提取结构、规则、分类标注、输入参数
2. **轻量确认**：针对模糊的分类标注，问 1-2 个确认问题
3. **输出蓝图**：生成标准 schema 的 `skill-blueprint.md`

## 产出物

唯一产出：`skill-blueprint.md`（固定 8-section schema），包含：

| Section | 内容 | skill-creator 处理方式 |
|---------|------|----------------------|
| Meta | 文档类型、受众、来源 | skill 元信息 |
| 目标定义 | skill 的用途描述 | SKILL.md 开头 |
| 输入参数表 | 用户需提供的信息 | skill 输入引导 |
| 输出结构定义 | 章节骨架 + 分类标注 | skill 生成框架 |
| 固定模板内容 | 可直接复用的文本块 | `references/` 模板文件 |
| 半模板规则 | 结构固定、细节变化的部分 | `references/` + 生成规则 |
| 项目特定规则 | 完全依赖用户输入的部分 | SKILL.md 生成指令 |
| 写作风格约束 | 人称、语气、格式等 | 写作规范文件 |
| 质量检查项 | 验证清单 | 质量 checklist |

## 安装

```bash
/plugins install ssot-prompt-engineer@henry-hub
```

## 使用示例

```
用户：@概要设计说明书.docx 帮我从这份文档中提取规则，生成 skill blueprint
Claude：[自动分析文档结构、内容规则、模板分类...] → 输出初步蓝图 → 确认 1-2 个问题 → 输出最终 skill-blueprint.md

用户：分析这份测试报告的写作规范，我要做成一个 skill
Claude：[读取文档 → 提取规则 → 生成 skill-blueprint.md] → 交给 skill-creator 处理
```
