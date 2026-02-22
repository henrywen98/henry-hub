---
description: 启动 PRD 多专家红队评审工作流。接受任意格式输入（文件路径、文本、截图、URL），组建 14 人专家评审团进行独立评审、压力测试和 3 轮辩论。
argument-hint: <PRD文件路径或需求描述>
---

## 用户输入

```text
$ARGUMENTS
```

## 概述

启动 PRD Review Board 工作流，组建 14 位跨职能专家团队对 PRD 进行企业级红队评审。

## 执行流程

### 1. 确认输入与输出目录

- 解析 `$ARGUMENTS`：可能是文件路径、粘贴的文本、截图路径、URL 或需求描述
- 如果为空，使用 AskUserQuestion 询问用户提供 PRD 或需求描述
- 询问用户指定输出目录（默认：`./prd-review-output/`）
- 创建输出目录结构

### 2. 生成或确认 PRD

- 如果输入已经是结构化 PRD：直接使用，保存为 `{output}/01-prd-v1.md`
- 如果输入是原始需求：使用 Task 工具派遣 `prd-review-board:prd-writer` agent 生成 PRD
  ```
  Task(subagent_type="prd-review-board:prd-writer", prompt="根据以下输入生成结构化 PRD: ...")
  ```
- 展示 PRD 摘要给用户，确认后继续

### 3. 组建评审团 & 执行评审

加载 `prd-review-board` skill，按 skill 中定义的 Phase 2-8 依次执行：

1. **Phase 2**: TeamCreate → 并行 spawn 13 位专家 → 独立评审
2. **Phase 3**: 红队压力测试
3. **Phase 4**: 3 轮真实辩论（SendMessage）
4. **Phase 5**: 风险矩阵 & FinOps 评估
5. **Phase 6**: 必须修改项 & 修订 PRD
6. **Phase 7**: 最终裁决
7. **Phase 8**: 综合报告 & 团队清理

### 4. 输出报告

完成后向用户报告：
- 输出目录路径
- 最终裁决（GO / CONDITIONAL GO / NO-GO）
- 关键发现摘要（Top 3 风险）
- 各专家投票汇总

## 注意事项

- 此工作流使用 Team Swarm，将创建 13+ 个并行 agent，token 消耗较大
- 评审专家使用 sonnet 模型以控制成本，PRD 撰写使用 opus 模型
- 整个流程可能需要较长时间，请耐心等待
- 如需中断，可以随时告诉我停止
