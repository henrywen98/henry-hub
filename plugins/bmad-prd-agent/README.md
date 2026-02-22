# BMAD PRD Agent (John)

基于 [BMAD Method](https://github.com/bmad-code-org/BMAD-METHOD) 的产品经理 Agent，覆盖 PRD 全生命周期管理。

## 简介

John 是一位拥有 8+ 年 B2B 和消费者产品经验的产品管理专家。他以侦探般的风格工作——不断追问「为什么」，直指问题核心，用数据和事实说话。

John 可以帮你完成从需求发现到实现交付的完整产品管理流程。

## 功能概览

| Skill | 触发词 | 说明 |
|-------|--------|------|
| **create-prd** | 创建PRD / create PRD | 通过协作发现流程创建完整的产品需求文档 |
| **validate-prd** | 验证PRD / validate PRD | 系统化质量评估：结构、密度、可测量性、可追溯性 |
| **edit-prd** | 编辑PRD / edit PRD | 基于反馈或新需求改进现有 PRD |
| **create-epics** | 创建Epic / create epics | 将 PRD 拆分为以用户价值为中心的 Epic 和 Story |
| **check-readiness** | 实现准备 / readiness check | 验证 PRD、架构、Epic 的对齐和完整性 |
| **correct-course** | 纠偏 / correct course | 分析实现中的变更影响，生成变更提案 |

## 使用方式

### 直接对话

直接与 John 对话即可，他会根据你的需求引导你选择合适的 Skill：

```
你好 John，我想为一个新项目创建 PRD
```

### 使用触发词

每个 Skill 都有中英文触发词，可以直接使用：

- `创建PRD` 或 `create PRD` — 启动 PRD 创建流程
- `验证PRD` 或 `validate PRD` — 启动 PRD 验证
- `编辑PRD` 或 `edit PRD` — 编辑已有 PRD
- `创建Epic` 或 `create epics` — 将 PRD 拆分为 Epic/Story
- `实现准备` 或 `readiness check` — 检查实现就绪度
- `纠偏` 或 `correct course` — 处理实现中的变更

## 典型工作流

```
create-prd → validate-prd → create-epics → check-readiness
     ↑                                          |
     └──── correct-course (如遇变更) ←───────────┘
```

1. **创建 PRD** — 通过 12 个阶段的协作发现流程，产出完整的产品需求文档
2. **验证 PRD** — 13 步系统化检查，确保 PRD 质量达标
3. **创建 Epic** — 将 PRD 需求拆分为用户价值导向的 Epic 和 BDD Story
4. **检查就绪** — 对抗式审查，确保 PRD、架构、Epic 三者对齐
5. **纠偏**（按需） — 当实现中发现重大变更时，系统化分析影响并生成变更提案

## 致谢

本插件的方法论提取自 [BMAD-METHOD](https://github.com/bmad-code-org/BMAD-METHOD) v6.0.1（MIT License），由 [bmad-code-org](https://github.com/bmad-code-org) 维护。
