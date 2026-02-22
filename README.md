# Henry Hub

Henry 的个人 Claude Code 插件市场，统一管理自建 skills 和常用插件，支持按需安装和团队共享。

## 快速开始

### 订阅 Marketplace

在 Claude Code 中执行：

```
/plugins → Discover → Add marketplace → github:henrywen98/henry-hub
```

### 按需安装插件

```
/plugins install <插件名>@henry-hub
```

## 插件列表

### 文档处理

| 插件 | 说明 | 安装命令 |
|------|------|----------|
| docx | Word 文档创建、编辑与分析 | `/plugins install docx@henry-hub` |
| pdf | PDF 提取、创建、合并与表单处理 | `/plugins install pdf@henry-hub` |
| pptx | PPT 演示文稿创建与编辑 | `/plugins install pptx@henry-hub` |
| xlsx | Excel 电子表格处理与数据分析 | `/plugins install xlsx@henry-hub` |

### 需求与文档工作流

| 插件 | 说明 | 安装命令 |
|------|------|----------|
| doc-coauthoring | 结构化文档协作工作流 | `/plugins install doc-coauthoring@henry-hub` |
| prd-workflow | PRD 需求规格文档创建与完善 | `/plugins install prd-workflow@henry-hub` |
| gen-requirement-doc | 需求确认单生成器 | `/plugins install gen-requirement-doc@henry-hub` |
| ai-pm-feedback-collector | 客户反馈整理为结构化需求文档 | `/plugins install ai-pm-feedback-collector@henry-hub` |
| github-issue-generator | 信息整理为标准 GitHub Issue 格式 | `/plugins install github-issue-generator@henry-hub` |
| bmad-prd-agent | 产品经理 Agent (John, 基于 BMAD) - PRD 全生命周期 | `/plugins install bmad-prd-agent@henry-hub` |

### 测试

| 插件 | 说明 | 安装命令 |
|------|------|----------|
| test-case-generator | 从需求文档生成结构化测试用例 + Excel | `/plugins install test-case-generator@henry-hub` |
| comprehensive-test-generation | 全面测试生成策略（E2E/API/Unit） | `/plugins install comprehensive-test-generation@henry-hub` |
| bmad-qa-agent | QA 自动化测试生成 Agent (Quinn, 基于 BMAD) | `/plugins install bmad-qa-agent@henry-hub` |

### 内容创作

| 插件 | 说明 | 安装命令 |
|------|------|----------|
| xhs-image-gen | 文案转小红书图文卡片，9 种风格 × 6 种布局 | `/plugins install xhs-image-gen@henry-hub` |

### 开发工具

| 插件 | 说明 | 安装命令 |
|------|------|----------|
| batch-commit | 批量智能提交，按功能模块分组 | `/plugins install batch-commit@henry-hub` |
| ssot-prompt-engineer | SSOT 驱动的提示词工程方法论 | `/plugins install ssot-prompt-engineer@henry-hub` |
| code-simplifier | 代码简化与优化（官方 fork） | `/plugins install code-simplifier@henry-hub` |
| superpowers | 核心技能库：TDD、调试、协作（官方 fork） | `/plugins install superpowers@henry-hub` |

## 说明

- 大部分插件为自建 skills，部分（code-simplifier、superpowers）为官方插件的 fork
- 部分插件（bmad-qa-agent、bmad-prd-agent）基于 BMAD-METHOD (MIT License) 提取
- 每个插件目录下都有中文 README.md，详细说明用途和使用方式
- 欢迎团队成员订阅使用
