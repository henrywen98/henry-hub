# bmad-qa-agent

基于 BMAD Method 的 QA 自动化测试生成 Agent (Quinn)。

## 简介

Quinn 是一个务实的 QA 自动化工程师 Agent，专注于快速为已有代码生成测试覆盖。采用"先覆盖、后优化"的策略，使用标准测试框架模式，生成简洁可维护的测试代码。

## 功能

- **测试框架自动检测** -- 扫描项目依赖和现有测试文件，自动识别使用的测试框架
- **API 测试生成** -- 覆盖状态码、响应结构、正常路径和关键错误场景
- **E2E 测试生成** -- 基于用户工作流，使用语义定位器，验证可见结果
- **自动运行验证** -- 生成后立即运行测试，失败则自动修复
- **覆盖率报告** -- 输出 Markdown 格式的测试摘要

## 使用方式

### 安装

```
/plugins install bmad-qa-agent@henry-hub
```

### 使用 Agent

直接对话即可：

```
帮我生成测试
```

```
为 src/api/ 下的接口生成 API 测试
```

```
为登录功能生成 E2E 测试
```

### 使用 Skill

也可以直接调用 skill：

```
/qa-automate
```

## 示例

### 生成 API 测试

```
用户：为 /api/users 接口生成测试
Quinn：检测到项目使用 Vitest，开始生成...
      - GET /api/users - 200 成功返回用户列表
      - GET /api/users/:id - 404 用户不存在
      - POST /api/users - 400 缺少必填字段
      所有测试已通过！
```

### 生成 E2E 测试

```
用户：为注册流程生成 E2E 测试
Quinn：检测到项目使用 Playwright，开始生成...
      - 用户填写注册表单并提交
      - 验证成功提示信息显示
      - 验证空表单提交的错误提示
      所有测试已通过！
```

## 组件

| 类型 | 名称 | 说明 |
|------|------|------|
| Agent | quinn | QA 自动化工程师，负责测试生成 |
| Skill | qa-automate | 自动检测框架、生成测试、运行验证 |

## 致谢

本插件基于 [BMAD-METHOD](https://github.com/bmad-code-org/BMAD-METHOD) v6.0.1 中的 QA Agent (Quinn) 提取并适配为 Claude Code 插件格式。

- 原始项目：[bmad-code-org/BMAD-METHOD](https://github.com/bmad-code-org/BMAD-METHOD)
- 许可证：MIT License
- 原作者：bmad-code-org
