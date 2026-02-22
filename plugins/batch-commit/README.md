# batch-commit

批量智能提交工具 -- 自动分析工作区所有变更，按功能模块智能分组，生成多个原子化的 Conventional Commits。告别手动逐个 `git add` + `git commit`，一条命令完成所有提交。

## 使用场景

- 当你完成了一个较大的功能开发，工作区有大量未提交的变更文件时
- 当你希望将变更按功能模块拆分为多个语义化的原子 commit，而不是一个巨大的 commit
- 输入 `/batch-commit` 即可触发

## 安装

```
/plugins install batch-commit@henry-hub
```

## 使用示例

```
> /batch-commit

分析工作区变更...
发现 12 个变更文件，分为 5 组：

1. feat(project): 添加项目管理功能模块 (7 files)
2. feat(shared): 添加共享视图组件 (2 files)
3. refactor(capture): 重构捕获模型以支持项目关联 (1 file)
4. refactor(browse): 更新浏览视图模型 (1 file)
5. docs(specs): 添加项目管理需求规格文档 (1 file)

## 批量提交完成

共创建 5 个提交。
提示：变更已全部提交到本地，请使用 `git push` 推送到远程。
```
