---
name: req-to-issues
description: "需求分析拆解为 GitHub/GitLab Issue。将原始需求素材（会议纪要、聊天记录、口头描述、变更需求、模糊想法、PRD/产品文档等）分析、澄清、拆解为 Story 级别的 Issue 并批量上传。当用户提到"拆需求"、"需求拆解"、"生成issue"、"需求转issue"、"需求分析"、"拆成issue"、"把这个需求拆一下"、"分析一下这个需求"、"创建issue"、"PRD拆解"、"从PRD生成issue"、"req to issues"、"decompose requirements" 时触发。即使用户只是模糊地提到想把一个功能想法变成可执行的开发任务，也应考虑触发此 skill。"
---

# 需求分析拆解为 Issue

将各种来源的原始需求素材，经过分析、澄清、拆解，生成 Story 级别的 GitHub/GitLab Issue 并批量上传。

## 可用命令

### /req-to-issues — 完整流程（含上传）

从需求素材出发，经过分析→澄清→拆解→预览→批量上传的完整工作流。

**使用**: `/req-to-issues <需求素材>`

### /req-to-issues.dry — 仅分析拆解（不上传）

与 `/req-to-issues` 相同的分析拆解流程，但只生成本地 markdown 文件，不上传到远端仓库。适合还在梳理阶段、不确定是否要执行的需求。

**使用**: `/req-to-issues.dry <需求素材>`

## 核心流程

```
用户输入需求素材
       ↓
  ① 素材分析 — 提取业务目标、涉及角色、核心功能点
       ↓
  ② 模糊点识别 & 逐一澄清
  扫描维度：业务边界、用户角色、功能范围、数据流向、异常场景、约束条件
  每次最多 3 个问题，附带推荐选项
       ↓
  ③ 拆解总览 — 展示 N 个 Issue 的标题和一句话描述
  用户可调整粒度、合并或拆开
       ↓
  ④ 生成 Issue 详情 — 按模板生成每个 Issue 的完整内容
       ↓
  ⑤ 批量上传（/req-to-issues 专有）
  自动检测当前仓库或询问目标仓库
  通过 gh/glab CLI 批量创建，输出每个 Issue 的 URL
```

## Issue 结构

每个 Issue 包含以下字段（范围严格限定在"需求"层，不含模块/技术栈/API/表结构等实现细节）：

**需求描述** · **业务价值** · **验收标准** · **依赖关系** · **约束条件** · **优先级（P0-P3）** · **标签**

完整模板和每个字段的编写规则见 `${CLAUDE_PLUGIN_ROOT}/references/issue-template.md`——这是唯一事实源，编写时必须以它为准。

## 下游流程

Issue 创建完成后，开发对单个 Issue 使用 `brainstorming` skill 进行技术方案设计（模块拆分、API 形态、数据结构、FE/BE 边界等），从需求层进入设计层。

## 何时用哪个命令

| 场景 | 命令 |
|------|------|
| 需求已明确，想直接拆成 issue 开始干 | `/req-to-issues` |
| 还在梳理阶段，先看看怎么拆 | `/req-to-issues.dry` |
| 需求来自会议纪要、聊天记录等 | 都可以，取决于是否要立刻上传 |

## 参考资料

- **`${CLAUDE_PLUGIN_ROOT}/references/issue-template.md`** — Issue 完整模板和编写规则
- **`${CLAUDE_PLUGIN_ROOT}/references/clarify-dimensions.md`** — 模糊点扫描的 6 个维度及具体检查项
