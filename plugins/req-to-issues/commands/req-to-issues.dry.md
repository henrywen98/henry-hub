---
description: 将需求素材分析拆解为 Issue（仅预览，不上传）
---

## 用户输入

```text
$ARGUMENTS
```

如果为空或 `$ARGUMENTS` 显示为字面值，提示用户在 `/req-to-issues.dry` 后面粘贴需求素材。

## 任务

与 `/req-to-issues` 相同的分析拆解流程，但**不上传到远端仓库**。适合需求还在梳理阶段的场景。

## 执行步骤

### 1-5. 与 /req-to-issues 相同

执行 `/req-to-issues` 的步骤 1-5（加载参考资料 → 解析素材 → 澄清 → 拆解总览 → 生成详情）。

读取以下文件获取完整流程指引：
- `${CLAUDE_PLUGIN_ROOT}/references/issue-template.md`
- `${CLAUDE_PLUGIN_ROOT}/references/clarify-dimensions.md`

### 6. 保存到本地

将所有 Issue 内容保存为 markdown 文件到当前工作目录：

```
issues/
├── 01-P0-[标题].md
├── 02-P0-[标题].md
├── 03-P1-[标题].md
└── README.md          # 汇总：Issue 列表 + 依赖关系
```

### 7. 报告完成

输出：
- 保存的文件路径
- 按优先级分组的汇总
- 依赖关系图（如有）
- 提示：确认后可使用 `/req-to-issues` 直接上传
