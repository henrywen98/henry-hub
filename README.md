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

### 需求与文档工作流

| 插件 | 说明 | 安装命令 |
|------|------|----------|
| doc-coauthoring | 结构化文档协作工作流 | `/plugins install doc-coauthoring@henry-hub` |
| ai-pm-feedback-collector | 客户反馈整理为结构化需求文档 | `/plugins install ai-pm-feedback-collector@henry-hub` |
| github-issue-generator | 信息整理为标准 GitHub Issue 格式 | `/plugins install github-issue-generator@henry-hub` |
| purvar-prd | 璞华PRD工作流：/purvar.prd 生成PRD、/purvar.confirm 生成需求确认单、/purvar.clarify 澄清PRD | `/plugins install purvar-prd@henry-hub` |
| concept-design | 概要设计说明书生成工具：扫描PRD+技术架构，按7章模板生成面向甲方交付的概设 | `/plugins install concept-design@henry-hub` |

### 测试

| 插件 | 说明 | 安装命令 |
|------|------|----------|
| test-case-generator | 从需求文档生成结构化测试用例 + Excel | `/plugins install test-case-generator@henry-hub` |
| comprehensive-test-generation | 全面测试生成策略（E2E/API/Unit） | `/plugins install comprehensive-test-generation@henry-hub` |

### 标书与投标

| 插件 | 说明 | 安装命令 |
|------|------|----------|
| bid-generator | 投资管理领域标书生成（解析→骨架→填充→审查） | `/plugins install bid-generator@henry-hub` |

### 效率工具

| 插件 | 说明 | 安装命令 |
|------|------|----------|
| meeting-prep | 会议准备工具，6 问生成完整会前文档 | `/plugins install meeting-prep@henry-hub` |
| weekly-report | 周报生成工具，从聊天记录自动生成会议周报 | `/plugins install weekly-report@henry-hub` |

### 开发工具

| 插件 | 说明 | 安装命令 |
|------|------|----------|
| ssot-prompt-engineer | SSOT 驱动的提示词工程方法论 | `/plugins install ssot-prompt-engineer@henry-hub` |

## 说明

- 大部分插件为自建 skills
- 每个插件目录下都有中文 README.md，详细说明用途和使用方式
- 欢迎团队成员订阅使用
