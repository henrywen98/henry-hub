---
name: batch-commit
description: 批量智能提交 - 将工作区变更按功能模块分组，生成多个原子化 commit
---

# Batch Commit 命令

将工作区所有变更按逻辑分组，生成多个原子化的 Conventional Commits。

## 工作流程

### 1. 分析变更

执行以下命令获取工作区状态：

```bash
git status --porcelain
git diff --name-only          # 已修改未暂存
git diff --cached --name-only # 已暂存
git ls-files --others --exclude-standard # 未跟踪
```

### 2. 智能分组

按以下优先级对文件进行分组：

| 优先级 | 策略 | 示例 |
|-------|------|------|
| 1 | 功能模块 | Model + Service + ViewModel + View + Test 组合 |
| 2 | 目录层级 | 同一目录下的相关组件 |
| 3 | 文件类型 | 配置文件、文档、资源文件 |

**分组识别模式**（参考 `references/grouping-patterns.md`）：

- **功能模块**: 识别同名或相关名称的 Model/Service/ViewModel/View/Test
- **目录聚合**: 同一目录下的多个新文件
- **特殊文件**: Schema 迁移、配置文件、文档单独分组
- **修改文件**: 现有文件的修改按影响范围分组

### 3. 生成 Commit Message

使用 Conventional Commits 格式（中文描述）：

```
<type>(<scope>): <简短描述>

<详细说明>

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
```

**类型说明**:
- `feat`: 新功能
- `fix`: 修复 bug
- `refactor`: 重构（不改变功能）
- `docs`: 文档变更
- `test`: 测试相关
- `chore`: 配置、构建相关
- `style`: 代码格式（不影响逻辑）

**注意**: 不使用 emoji 前缀

### 4. 执行提交

对每个分组执行：

```bash
git add <file1> <file2> ...  # 使用具体文件名
git commit -m "$(cat <<'EOF'
<commit message>
EOF
)"
```

### 5. 循环处理

重复步骤 1-4 直到 `git status --porcelain` 输出为空。

## 输出格式

完成后输出中文汇总：

```
## 批量提交完成

共创建 N 个提交：

1. <type>(<scope>): <描述> (N files)
2. ...

提示：变更已全部提交到本地，请使用 `git push` 推送到远程。
```

## 关键约束

1. **不修改 git config**
2. **不执行 push 操作**
3. **不使用 `--no-verify` 跳过 hooks**
4. **使用具体文件名而非 `git add -A` 或 `git add .`**
5. **敏感文件警告**: 遇到 `.env`、`credentials`、`secret` 等文件时警告用户

## 错误处理

- **Pre-commit hook 失败**: 报告错误，修复后重新提交（创建新 commit，不用 --amend）
- **文件冲突**: 停止并提示用户解决
- **空提交**: 跳过该分组，继续下一个
