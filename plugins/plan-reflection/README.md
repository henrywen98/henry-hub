# plan-reflection — 多 Agent 计划反思循环

对 `~/.claude/plans/` 中的活跃计划执行多轮独立审核。一个 Reviewer Agent 找出 blocking issues，一个独立的 Corrector Agent 修正它们，循环最多 3 轮，带收敛保护。最终返回审核报告，由你决定下一步。

## 为什么需要这个

写 plan 的人（不管是人还是 AI）通常看不到自己的盲点：内部矛盾、遗漏的边界 case、不切实际的步骤、范围蔓延。让同一个 agent 自己审核自己的 plan 很少有效——审核者和作者共享同样的假设。

这个 skill 实现了 **多 agent 反思模式**：
- **独立审核** —— Reviewer 是只读的、独立的，没有作者的上下文偏见
- **职责分离** —— Reviewer 找问题，Corrector 修问题，互不干涉
- **硬约束循环** —— 最多 3 轮、blocking 数无进展即停止、persistent deferred 即停止
- **不自动实施** —— skill 永远把决策权交还给用户

## 使用方式

先用其他工具（比如 `superpowers:writing-plans`）写好一个 plan，确认它已经在 `~/.claude/plans/` 下，然后调用：

```
让我审一下计划
帮我 review 一下方案
adversarial review my plan
```

skill 会：
1. 找到当前活跃的 plan（多个则让你选）
2. 自动识别 plan 的领域（technical / product / devops / architecture / general）
3. 派发 Reviewer Agent 审核
4. 如果有 blocking issues，派发 Corrector Agent 修正
5. 循环最多 3 轮
6. 展示最终审核报告

## 终止条件

循环会在以下任意一个条件触发时停止：

| 条件 | 说明 |
|------|------|
| **PASS** | Reviewer 给出 PASS（零 blocking issues） |
| **Round cap** | 达到 3 轮上限 |
| **Stalled** | 第 2 轮起，blocking 数没有下降（持平或上升） |
| **Persistent deferred** | 同一个 issue 连续两轮被标记 DEFERRED |
| **Parse failure** | Reviewer 输出连续两次无法解析 |
| **Dispatch failure** | Agent 派发出错 |

无论哪种终止，都会展示完整的审核报告和轮次历史。

## 设计原则

- **Reviewer 只读** —— 不改任何文件，只输出方向性建议
- **Corrector 只改 plan 文件** —— 不动其他文件，只做最小范围修改
- **Orchestrator 不读 plan 内容** —— 主会话只解析结构化字段，避免上下文污染
- **不打分** —— 二元 blocking 判断比分数更难注水
- **不自审** —— Reviewer 和 Corrector 是不同的 agent，独立性是核心价值
- **不自动实施** —— 审核结束后用户自己决定下一步

## 不适用场景

- ❌ 生成新的 plan（请用 `superpowers:writing-plans`）
- ❌ 审核代码（请用 code-reviewer agents）
- ❌ 审核 `~/.claude/plans/` 之外的 markdown 文件
- ❌ 自动执行 plan

## 文件结构

```
plan-reflection/
├── .claude-plugin/plugin.json
├── README.md                                    # 本文件
└── skills/plan-reflection/
    ├── SKILL.md                                 # 主 skill（编排逻辑）
    └── references/
        ├── review-dimensions.md                 # 各领域审核维度
        └── report-templates.md                  # 审核/修正报告模板
```

## 安装

```
/plugins install plan-reflection@henry-hub
```
