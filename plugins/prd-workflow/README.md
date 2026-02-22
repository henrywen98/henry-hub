# PRD 需求规格文档工作流

PRD（Product Requirements Document）需求规格文档的创建与完善工具。提供结构化的命令来生成和迭代需求文档。

## 使用场景

- 从零开始创建产品需求规格文档
- 将需求描述转化为标准 PRD 格式
- 对已有 PRD 进行澄清和细化

## 安装

```
/plugins install prd-workflow@henry-hub
```

## 包含命令

- `/prd.create <需求描述>` - 创建或更新需求规格文档
- `/prd.clarify` - 对已有 PRD 进行澄清和补充

## 使用示例

```
/prd.create 用户管理模块，支持注册、登录、权限管理
```

系统将自动生成简短名称、创建目录结构、输出标准格式的 PRD 文档。
