# comprehensive-test-generation

从需求文档和现有代码出发，通过结构化的四阶段流程（探索、策略设计、子Agent分布式生成、验证交付）生成全面的测试套件。与 TDD 互补——TDD 保证单任务正确性，本插件保证需求级别的测试覆盖完整性。

## 使用场景

当你需要以下操作时会触发此插件：

- "generate test cases" / "生成测试用例"
- "write e2e tests" / "写E2E测试"
- "generate comprehensive tests" / "全面测试"
- "补全测试覆盖" / "test coverage gap analysis"
- "generate playwright tests" / "写测试"
- "write tests for" / "add tests" / "add test coverage"
- "create test plan" / "测试计划"
- "test strategy" / "测试策略"
- "提高测试覆盖率" / "test my code"
- 从需求文档、功能规格、API 端点或现有代码创建自动化测试
- 在 subagent-driven-development 或 executing-plans 完成后，需要全面测试覆盖时

## 安装

```
/plugins install comprehensive-test-generation@henry-hub
```

## 使用示例

### 基本用法

```
给这个项目生成全面的测试用例
```

```
为 src/auth/ 模块写 E2E 测试
```

```
分析现有测试覆盖率，补全缺失的测试
```

### 四阶段流程

1. **探索阶段 (EXPLORE)** — 理解测试目标，分析需求文档和现有代码，确认测试范围
2. **策略设计 (DESIGN)** — 编写精简的主策略文件（不超过200行），包含需求覆盖矩阵和 Agent 分工表
3. **分布式生成 (GENERATE)** — 调度自治子 Agent 并行编写测试，每个 Agent 自行读取源码、设计用例、输出可运行的测试文件
4. **验证交付 (VERIFY)** — 运行测试、质量审计、输出覆盖报告，衔接后续验证流程

### 集成模式 vs 独立模式

- **集成模式**：检测到 `docs/plans/*.md` 设计文档且处于功能分支时自动启用，从设计文档提取需求，用 `git diff` 确定代码范围
- **独立模式**：无设计文档上下文时，接受任意输入（PRD、代码路径、口头描述）并执行完整探索流程
