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
| ai-pm-feedback-collector | PM碎片信息收集与洞察整理（JTBD + Opportunity Score + 情感分析） | `/plugins install ai-pm-feedback-collector@henry-hub` |
| purvar-prd | 璞华PRD工作流：/purvar.prd 生成PRD、/purvar.confirm 生成需求确认单、/purvar.clarify 澄清PRD | `/plugins install purvar-prd@henry-hub` |
| purvar-hld | 璞华概要设计说明书：组装7章概设 + Markdown→Word 转换 | `/plugins install purvar-hld@henry-hub` |

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

### 可视化

| 插件 | 说明 | 安装命令 |
|------|------|----------|
| drawio-diagram | Draw.io 图表生成器：流程图、架构图、系统拓扑图、业务流程全景图 | `/plugins install drawio-diagram@henry-hub` |

### 开发工具

| 插件 | 说明 | 安装命令 |
|------|------|----------|
| ssot-prompt-engineer | SSOT 规则提取器：从成品文档反向提取生成规则，输出 Skill Blueprint 供 skill-creator 消费 | `/plugins install ssot-prompt-engineer@henry-hub` |
| req-to-issues | 需求分析拆解工具：将需求素材分析拆解为 GitHub/GitLab Issue 并批量上传 | `/plugins install req-to-issues@henry-hub` |

## 说明

- 大部分插件为自建 skills
- 每个插件目录下都有中文 README.md，详细说明用途和使用方式
- 欢迎团队成员订阅使用
