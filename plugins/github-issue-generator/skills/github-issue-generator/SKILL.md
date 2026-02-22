---
name: github-issue-generator
description: GitHub Issue 生成器。将信息整理成详细的 GitHub Issue 格式，包括标题、标签、详细描述、复现步骤等。触发短语：生成Issue、创建Issue、生成GitHub Issue、Issue格式整理、创建GitHub问题。
---

# GitHub Issue 生成器

此技能用于将原始信息整理成详细的 GitHub Issue 格式。

## 触发条件

当用户提出以下需求时触发此技能：
- 生成Issue
- 创建Issue
- 生成GitHub Issue
- Issue格式整理
- 创建GitHub问题
- 整理成Issue格式
- 转成GitHub Issue

## 执行步骤

### Step 1: 收集原始信息
接收需要整理成 Issue 的原始内容，可能来自：
- 文字描述
- 邮件内容
- 聊天记录
- 反馈文档
- 其他来源

### Step 2: 分析信息内容
分析原始信息，提取：
- 问题类型（Bug / Feature / Enhancement / Question）
- 影响范围
- 优先级/严重程度
- 相关模块/组件

### Step 3: 生成 Issue 结构
按照 GitHub Issue 格式生成内容：

**必须包含：**
- **标题 (Title)**: 简洁描述问题
- **描述 (Body)**:
  - 问题背景
  - 详细描述
  - 期望行为
  - 实际行为
- **标签 (Labels)**: bug, enhancement, feature, question, priority/high 等
- **指派 (Assignee)**: 如有需要

**可选包含：**
- **复现步骤**: 对于 Bug 类问题
- **环境信息**: 操作系统、版本等
- **附加文件**: 截图、日志等

### Step 4: 展示给用户确认
将生成的 Issue 内容展示给用户，等待确认。

### Step 5: 询问上传意愿
确认是否需要上传到 GitHub：
- 如果需要，询问目标仓库
- 如果不需要，保存到本地

## GitHub Issue 模板

```markdown
## 问题描述

### 背景
[描述问题背景]

### 详细描述
[详细说明问题]

### 期望行为
[期望的结果]

### 实际行为
[实际发生的情况]

## 环境信息

- 操作系统：
- 版本：
- 浏览器：

## 复现步骤

1. 第一步
2. 第二步
3. 第三步

## 附加信息

- 截图：
- 日志：
```

## 输出格式

- **本地保存**: `/home/henry/feedback/` 目录，文件名格式：`YYYY-MM-DD-issue-标题.md`
- **GitHub Issue**: 上传到用户指定的仓库

## 询问确认

生成 Issue 后，必须询问用户：

```
请选择后续操作：
1. 修改 - 编辑 Issue 内容
2. 上传到GitHub - 指定仓库后上传
3. 仅保存本地 - 不上传到 GitHub
```
