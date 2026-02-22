# 文件分组策略参考

## Swift/iOS 项目模式

### 功能模块识别

同一功能的文件通常遵循以下命名约定：

```
Models/<Feature>.swift
Models/<Feature>Status.swift
Services/<Feature>Service.swift
ViewModels/<Feature>ViewModel.swift
Views/<Feature>View/<Feature>View.swift
Views/<Feature>View/<Feature>DetailView.swift
Tests/<Feature>Tests.swift
Tests/<Feature>ServiceTests.swift
```

**识别规则**：
- 提取文件名中的核心词（去除 Model/Service/ViewModel/View/Test 后缀）
- 具有相同核心词的文件归为同一功能模块
- 例：`Project.swift`, `ProjectService.swift`, `ProjectViewModel.swift` → 同一模块

### 目录层级分组

```
Views/Shared/           → feat(shared): 共享视图组件
Views/ProjectView/      → feat(project): 项目视图
Utilities/              → feat(utils): 工具类
Resources/              → chore(resources): 资源文件
```

### 特殊文件处理

| 文件模式 | 分组策略 | Commit 类型 |
|---------|---------|------------|
| `Schema*.swift` | 单独分组 | `chore(schema)` |
| `*Tests.swift` | 按功能模块分组 | `test(<feature>)` |
| `Localizable.xcstrings` | 与相关功能合并或单独 | `feat(i18n)` |
| `Constants.swift` | 与相关功能合并或单独 | `chore(config)` |
| `project.yml` | 单独分组 | `chore(build)` |
| `*.md` (非 README) | 按目录分组 | `docs(<scope>)` |

## Web/后端项目模式

### 功能模块识别

```
src/models/<feature>.ts
src/services/<feature>.service.ts
src/controllers/<feature>.controller.ts
src/routes/<feature>.routes.ts
tests/<feature>.test.ts
```

### 目录层级分组

```
src/components/         → feat(components)
src/utils/              → feat(utils)
src/config/             → chore(config)
public/                 → chore(assets)
```

## 通用分组规则

### 分组大小控制

- **理想大小**: 3-10 个文件
- **最大大小**: 20 个文件
- **超过时**: 拆分为更细粒度的子模块

### 分组优先级

1. **强关联**: Model + Service + ViewModel + View（同一功能）
2. **中关联**: 同一目录下的相关文件
3. **弱关联**: 同类型文件（所有测试、所有配置）

### 修改文件 vs 新文件

- **新文件**: 优先按功能模块分组
- **修改文件**:
  - 若修改支持新功能 → 合并到功能模块
  - 若独立修改 → 单独分组为 `refactor` 或 `fix`

### 敏感文件检测

以下文件需要警告用户：
- `.env*`
- `*credentials*`
- `*secret*`
- `*key.json`
- `*token*`
- `.npmrc` (可能含 token)

## 示例分组

给定以下变更：

```
?? Models/Project.swift
?? Models/ProjectStatus.swift
?? Services/ProjectService.swift
?? ViewModels/ProjectViewModel.swift
?? Views/ProjectView/ProjectListView.swift
?? Views/Shared/ItemDragPreview.swift
?? Views/Shared/ProjectPickerView.swift
?? Tests/ProjectTests.swift
?? Tests/ProjectServiceTests.swift
M  Models/CaptureItem.swift
M  ViewModels/BrowseViewModel.swift
?? specs/003-project/spec.md
```

**分组结果**：

| 组 | 类型 | 范围 | 文件 |
|----|------|------|------|
| 1 | feat | project | Project.swift, ProjectStatus.swift, ProjectService.swift, ProjectViewModel.swift, ProjectListView.swift, ProjectTests.swift, ProjectServiceTests.swift |
| 2 | feat | shared | ItemDragPreview.swift, ProjectPickerView.swift |
| 3 | refactor | capture | CaptureItem.swift (修改以支持 Project) |
| 4 | refactor | browse | BrowseViewModel.swift |
| 5 | docs | specs | specs/003-project/spec.md |
