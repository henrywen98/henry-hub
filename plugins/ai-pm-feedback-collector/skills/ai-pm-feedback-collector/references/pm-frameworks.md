# PM 方法论参考

本文件提供 SKILL.md 中使用的 PM 方法论背景，帮助理解洞察提炼的理论基础。

---

## Jobs-to-be-Done (JTBD)

**来源**：Clayton Christensen / Tony Ulwick

**核心思想**：用户不是在"购买产品"，而是在"雇佣产品完成某个任务"。理解用户真正要完成的"任务"比理解用户"想要什么功能"更重要。

**格式**：
> When [具体情境]，I want to [动机/目标]，so I can [期望结果]

**在本 skill 中的应用**：
- Step 2 中，对每条反馈提取 JTBD，揭示用户的真实需求场景
- 帮助分离"用户说的方案"和"用户真正要完成的任务"

**示例**：
- 用户说："能不能加个批量导出按钮？"
- JTBD：When 我需要向领导汇报月度数据时，I want to 快速获取所有订单的汇总数据，so I can 在会议前准备好报告材料。
- 洞察：真正的 Job 是"准备汇报材料"，批量导出只是用户想到的一种解决方案。也许自动生成报告是更好的方案。

---

## Opportunity Score（机会评分）

**来源**：Dan Olsen，《The Lean Product Playbook》

**公式**：
```
Opportunity Score = Importance × (1 - Satisfaction)
```

- **Importance（重要性，0-1）**：这个需求对用户完成核心任务有多关键？
  - 1.0 = 没有这个功能无法完成核心任务
  - 0.7 = 重要但有替代方案
  - 0.3 = 锦上添花
  - 0.0 = 无关紧要

- **Satisfaction（满意度，0-1）**：用户对当前方案（包括手工方案、竞品方案）的满意程度？
  - 1.0 = 非常满意，不需要改进
  - 0.5 = 勉强能用，但有明显不便
  - 0.0 = 完全无法接受

**解读**：
- 高重要性 + 低满意度 = 高 Opportunity Score → 最值得投入的机会
- 高重要性 + 高满意度 = 低 Score → 用户已经满意，不需要改
- 低重要性 = 低 Score → 无论满意度如何都不值得优先投入

**定性替代**：无法精确量化时，用"高/中/低"估计：

| Opportunity Score | 重要性 | 满意度 |
|-------------------|--------|--------|
| 高 | 核心任务，无替代 | 用户明确表达不满 |
| 中 | 重要但有替代方案 | 勉强能用 |
| 低 | 锦上添花 | 用户基本满意 |

---

## The Mom Test

**来源**：Rob Fitzpatrick

**核心思想**：在收集用户反馈时，人们会出于礼貌说谎。好的反馈收集应该：

1. **问过去发生的事，不问假设性的未来**
   - ❌ "如果我们做了X功能，你会用吗？"（会得到虚假的肯定）
   - ✅ "上次你遇到这个问题时是怎么解决的？"

2. **问具体行为，不问观点**
   - ❌ "你觉得这个功能重要吗？"
   - ✅ "上周你用了几次这个功能？"

3. **关注用户的痛苦程度**
   - 用户只是"觉得不方便"还是"已经找到了替代方案"？
   - 如果用户已经在花钱/花时间解决这个问题，说明这是一个真实的痛点

**在本 skill 中的应用**：
- Step 3 情感标注时，关注用户的具体行为描述而非笼统评价
- 判断影响面时，优先看用户的实际行为（频次、替代方案）而非自述的重要性

---

## Opportunity vs Solution

**来源**：Teresa Torres，《Continuous Discovery Habits》

**核心思想**：将用户需求分为"机会（Opportunity）"和"解决方案（Solution）"两层：

- **Opportunity**：用户面临的问题、痛点或未被满足的需求（problem space）
- **Solution**：解决问题的具体方案（solution space）

**为什么要分离**：
- 一个 Opportunity 可能有多种 Solution
- 用户提出的 Solution 往往不是最优解
- PM 的职责是找到最好的 Solution，而不是照搬用户的建议

**Opportunity Solution Tree**：
```
Outcome（目标）
  └── Opportunity 1（用户遇到的问题）
  │     ├── Solution A
  │     ├── Solution B
  │     └── Solution C
  └── Opportunity 2
        ├── Solution D
        └── Solution E
```

**在本 skill 中的应用**：
- Step 2 分离问题与方案，确保洞察文档以 Opportunity 为主线
- Step 4 待验证假设清单，识别每个 Opportunity 的关键假设
