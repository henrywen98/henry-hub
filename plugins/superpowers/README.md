# superpowers

Claude Code 核心技能库：TDD、系统化调试、协作模式和经过验证的开发工作流。由 Jesse Vincent 开发，MIT 许可证，版本 4.3.1。

## 包含内容

### Skills（技能）

- **using-superpowers** - 技能系统入口，建立如何发现和使用技能的规则
- **brainstorming** - 头脑风暴：在实现前探索需求和设计，强制执行设计优先流程
- **writing-plans** - 编写计划：将需求转化为包含精细步骤的实施计划
- **executing-plans** - 执行计划：分批执行任务，带有审查检查点
- **subagent-driven-development** - 子代理驱动开发：每个任务分派独立子代理，含两阶段代码审查
- **test-driven-development** - 测试驱动开发（TDD）：先写测试，看它失败，再写最小实现
- **systematic-debugging** - 系统化调试：四阶段流程（根因调查 -> 模式分析 -> 假设验证 -> 实现修复）
- **dispatching-parallel-agents** - 并行代理分派：将独立任务分配给多个代理并行处理
- **requesting-code-review** - 请求代码审查：分派审查子代理检查代码质量
- **receiving-code-review** - 接收代码审查：以技术严谨态度评估反馈，而非盲从
- **using-git-worktrees** - 使用 Git Worktrees：创建隔离工作空间
- **finishing-a-development-branch** - 完成开发分支：验证测试、合并/PR/保留/丢弃的结构化选项
- **verification-before-completion** - 完成前验证：声明完成前必须有运行验证的证据
- **writing-skills** - 编写技能：将 TDD 应用于流程文档的创建

### Agents（代理）

- **code-reviewer** - 高级代码审查代理，对照计划和编码标准审查已完成的工作

### Commands（命令）

- **/brainstorm** - 在任何创造性工作前必须使用，探索需求和设计
- **/write-plan** - 创建包含精细任务的详细实施计划
- **/execute-plan** - 分批执行计划，带审查检查点

### Hooks（钩子）

- **SessionStart** - 会话启动时自动注入 using-superpowers 技能内容

### Lib（库）

- **skills-core.js** - 技能发现、解析和路径解析的核心模块

## 安装

```
/plugins install superpowers@henry-hub
```

## 使用示例

安装后，superpowers 会在每次会话启动时自动加载。核心工作流如下：

```
# 1. 头脑风暴 - 理解需求，设计方案
用户：我想给项目添加用户认证功能
Claude：（自动调用 brainstorming 技能，逐步提问，设计方案）

# 2. 编写计划 - 生成详细实施步骤
Claude：（调用 writing-plans 技能，生成 docs/plans/2026-02-22-auth-design.md）

# 3. 执行计划 - TDD + 代码审查
Claude：（调用 subagent-driven-development 或 executing-plans 技能）

# 4. 完成 - 验证、合并或创建 PR
Claude：（调用 finishing-a-development-branch 技能）
```

### 手动触发命令

```
/superpowers:brainstorm        # 启动头脑风暴
/superpowers:write-plan        # 编写实施计划
/superpowers:execute-plan      # 执行已有计划
```

### 调试工作流

```
# 遇到 bug 时，Claude 自动调用 systematic-debugging 技能
# 四阶段流程：根因调查 -> 模式分析 -> 假设验证 -> 实现修复
# 严禁在找到根因之前尝试修复
```
