---
name: vue-form-to-json
description: 将 Vue 2 + Element UI 的硬编码表单页面提取为 JSON 动态配置数组。当用户提到"表单转JSON"、"提取表单配置"、"form to JSON"、"生成表单JSON"、"分析表单字段"、"把表单变成配置"、要把 .vue 文件中的表单转为动态配置、或者要梳理一个表单组件中所有字段时使用。
---

# Vue 表单 → JSON 配置提取器

将 Vue 2 + Element UI 硬编码的表单页面转换为结构化的 JSON 配置数组，用于后端配置化驱动动态表单渲染。

**输入：** 一个 .vue 表单页面文件路径。
**输出：** JSON 配置数组，保存到 `jsonMock/<pageName>.json` 和 `jsonMock/<pageName>.md`。

## 参考文件

提取前先查阅以下项目文件，确保与最新实现一致：

| 文件 | 用途 |
|------|------|
| `rules/vuejson.md` | 权威 JSON Schema 定义和 fieldType 枚举 |
| `jsonMock/fundBasic.md` | 金标准示例（基金基本信息页的完整 JSON 输出） |
| `src/components/dynamicForm/DynamicField.vue` | 动态字段渲染器，含完整 componentMap（fieldType → Renderer 映射） |
| `src/mixins/formConfigMix.js` | 表单配置 mixin，定义了 JSON 如何被消费和处理 |

## 输出 Schema

每个字段生成一个 JSON 对象：

```json
{
  "fieldCode": "fundName",
  "fieldName": "基金名称",
  "fieldType": "TEXT",
  "fixedType": 1,
  "sortOrder": 3,
  "width": "50%",
  "required": 1,
  "readonly": 0,
  "locked": 0,
  "addVisible": 1,
  "editVisible": 1,
  "viewVisible": 1,
  "overrideType": "OVERRIDE",
  "propsJson": "",
  "linkageJson": ""
}
```

| 字段 | 说明 | 取值 |
|------|------|------|
| fieldCode | 字段编码，对应 `v-model="formData.xxx"` 的 key | 字符串 |
| fieldName | 显示名称（label 文本） | 字符串 |
| fieldType | 组件类型 | 见"组件类型映射表" |
| fixedType | 固定字段类型 | 0=非固定, 1=固定, 2=半固定 |
| sortOrder | 排序序号，从 1 开始，按字段在页面中的出现顺序递增 | 正整数 |
| width | 字段宽度 | 25% / 33% / 50% / 66% / 75% / 100% |
| required | 是否必填 | 0=否, 1=是 |
| readonly | 是否只读 | 0=否, 1=是 |
| locked | 是否锁定（锁定的字段不渲染） | 0=否, 1=是 |
| addVisible | 新增模式是否显示 | 0=否, 1=是 |
| editVisible | 编辑模式是否可见 | 0=否, 1=是 |
| viewVisible | 查看模式是否可见 | 0=否, 1=是 |
| overrideType | 覆盖类型 | 固定 "OVERRIDE" |
| propsJson | 组件特殊属性（JSON 字符串） | 见"特殊属性" |
| linkageJson | 字段联动条件（JSON 字符串） | 见"联动配置" |
| formId | 关联表单 ID（仅 LINK_TAG 类型使用） | 字符串，可选 |

### fixedType 语义

这个值决定了前端渲染逻辑如何处理该字段：

- **1（固定字段）**：在 Vue 模板中有专门的渲染逻辑（如特定的 v-if 条件、自定义交互），存入 `formConfig.fixedFields` map 中按 fieldCode 索引。`editVisible`/`viewVisible` 对固定字段不生效，固定字段的显隐由代码逻辑控制。
- **0（非固定字段）**：完全由 JSON 配置驱动，通过 `DynamicField` 组件渲染，`editVisible`/`viewVisible` 控制其在不同模式下的可见性。
- **2（半固定字段）**：有一定的自定义逻辑但部分属性可被配置覆盖。

已在 Vue 模板中有具体渲染逻辑的字段（即现存页面中的字段），一律标记为 `fixedType: 1`。

## 提取流程

### Step 1: 读取目标 Vue 文件

读取完整的 .vue 文件内容。大文件（3000+ 行）分段读取，先读 template 部分，再读 script 部分中的 data/rules。

### Step 2: 识别表单字段

在 `<template>` 中寻找表单字段。本项目有两种常见模式：

**模式 A — purvar_form_item（最常见）：**

```html
<el-col :span="12">
  <el-form-item label="" prop="registerStatus">
    <el-row class="purvar_form_item">
      <el-col :span="8" class="purvar_form_item_title">
        基金注册状态
        <span class="mustIn">*</span>
      </el-col>
      <el-col :span="16">
        <el-radio-group v-if="isEdit" v-model="formData.registerStatus">
          ...
        </el-radio-group>
        <div v-else class="purvar_form_item_content">{{ formData.registerStatusName }}</div>
      </el-col>
    </el-row>
  </el-form-item>
</el-col>
```

**模式 B — el-form-item label：**

```html
<el-col :span="12">
  <el-form-item label="字段名称" prop="fieldCode">
    <el-input v-model="formData.fieldCode" />
  </el-form-item>
</el-col>
```

### Step 3: 逐字段提取元数据

| 属性 | 提取规则 |
|------|----------|
| fieldCode | 优先从 `v-model="formData.xxx"` 提取 xxx；`prop` 仅用于表单校验，可能与 v-model key 不同（如 `prop="mcId"` 但 `v-model="formData.mcName"`），以 v-model 为准 |
| fieldName | `purvar_form_item_title` 内文本，或 `el-form-item label="..."` |
| fieldType | 根据编辑态组件映射（见下表）；同一字段通过 v-if 切换多种组件时，取最复杂/最主要的类型（如 QccSelect + el-input 切换 → LINK_TAG_SINGLE） |
| sortOrder | 按字段在模板中的出现顺序，从 1 开始递增 |
| width | 外层 `el-col :span` 值映射：6→25%, 8→33%, 12→50%, 16→66%, 18→75%, 24→100% |
| required | 有 `<span class="mustIn">*</span>` 或 script 中 rules 对象有 `required: true` 验证 → 1（以 rules 为准） |
| readonly | 无编辑态组件（只有文本展示）或 disabled → 1 |
| locked | 默认 0；除非明确需要隐藏的字段 |
| fixedType | 模板中有具体渲染逻辑 → 1 |
| addVisible | 默认 1；有条件隐藏在新增模式时 → 0 |
| editVisible | 默认 1；有条件隐藏在编辑模式时 → 0 |
| viewVisible | 默认 1；有条件隐藏在查看模式时 → 0 |

### Step 4: 组件类型映射表

完整映射（与 `DynamicField.vue` 的 componentMap 对齐）：

| Vue 组件 | fieldType | 说明 |
|----------|-----------|------|
| `el-input`（无 type 或 type="text"） | TEXT | 单行文本 |
| `el-input type="textarea"` | TEXTAREA | 多行文本 |
| `el-input-number` | NUMBER | 数字输入 |
| `el-select`（单选） | SELECT | 下拉单选 |
| `el-select`（multiple） | MULTI_SELECT | 下拉多选 |
| `el-radio-group` | RADIO | 单选框组 |
| `el-checkbox-group` | CHECKBOX | 多选框组 |
| `el-date-picker type="date"` | DATE | 日期选择 |
| `el-date-picker type="datetime"` | DATETIME | 日期时间 |
| `el-switch` | SWITCH | 开关 |
| `el-slider` | SLIDER | 滑块 |
| `el-rate` | RATE | 评分 |
| `QccSelect` / 企查查选择 | LINK_TAG_SINGLE | 关联标签单选 |
| 关联标签多选组件 | LINK_TAG | 关联标签（通用） |
| `el-cascader`（省市区） | ADDRESS | 地址/区域级联选择 |
| 计算/公式展示 | FORMULA | 公式字段（如 computed 合计值） |
| `SelectDept` / 部门选择 | ORG_SELECT | 机构选择 |
| 下拉机构选择 | ORG_SELECT_DROP | 下拉式机构选择 |
| 人员选择组件 | USER_SELECT | 人员选择 |
| 下拉选人 | USER_SELECT_DROP | 下拉式人员选择（el-select + remote） |
| 表格选人 | USER_SELECT_TABLE | 表格式人员选择 |
| `FileLibrary` | FILE_LIBRARY | 文件组件 |
| 附件上传（el-upload） | FILE | 附件上传 |
| 图片上传 | IMAGE | 图片上传 |
| 文件列表展示 | FILE_LIST | 文件列表 |
| 树形选择组件 | TREE_SELECT | 树选择 |

**类型歧义消解：** 当同一 Vue 组件可能映射多种 fieldType 时：
- `el-select` + `remote` + 人员数据 → `USER_SELECT_DROP`（而非 SELECT）
- `el-select` + `remote` + 机构数据 → `ORG_SELECT_DROP`（而非 SELECT）
- `el-select` + 普通码值数据 → `SELECT`
- `el-cascader` + 省市区 → `ADDRESS`
- 根据数据源和业务语义判断，不仅看组件标签

### Step 5: 联动配置（linkageJson）

当字段显隐依赖其他字段值时，提取条件生成联动 JSON。

**简单条件** — `v-if="formData.registerStatus==='1'"`：

```json
{"conditions":[{"field":"registerStatus","operator":"eq","value":"1"}]}
```

**包含条件** — `v-if="formData.platforms && formData.platforms.includes('3')"`:

```json
{"conditions":[{"field":"platforms","operator":"contains","value":"3"}]}
```

**一控多场景** — 一个字段控制多个依赖字段（如 `needAgreement` 控制 `investmentManagement`、`withdrawFee`、`reason`）：
- `needAgreement === '1'` 时显示 investmentManagement 和 withdrawFee → 这两个字段的 linkageJson 都设为 `{"conditions":[{"field":"needAgreement","operator":"eq","value":"1"}]}`
- `needAgreement === '0'` 时显示 reason → reason 的 linkageJson 设为 `{"conditions":[{"field":"needAgreement","operator":"eq","value":"0"}]}`

operator 枚举：
- `eq` — 等于
- `neq` — 不等于
- `contains` — 包含（数组/多选字段）
- `notContains` — 不包含

多条件时 conditions 数组有多个元素，默认 AND 关系。序列化为字符串存入 linkageJson。无联动则为空字符串 `""`。

**复杂业务逻辑联动：** 有些显隐条件涉及复杂业务逻辑（如多层嵌套条件、计算判断），这些在 JSON 中难以完整表达。此时在 linkageJson 中记录能表达的部分，并在输出中添加注释说明需要代码侧 `getExtraVisible()` 方法兜底处理。

### Step 6: 特殊属性（propsJson）

不同 fieldType 的 propsJson 示例：

**LINK_TAG_SINGLE（关联标签）：**
```json
"{\"linkTag\":{\"selectType\":2,\"parentId\":\"19\"}}"
```

**SELECT（码值下拉，指定 parentId）：**
```json
"{\"codeParentId\":\"18\"}"
```

**DATE（指定格式）：**
```json
"{\"format\":\"yyyy-MM-dd\",\"valueFormat\":\"yyyy-MM-dd\"}"
```

**FILE_LIBRARY（文件组件）：**
```json
"{\"fileTypeId\":\"10011001\",\"stageType\":\"1001\",\"functionType\":\"FUND\"}"
```

**ADDRESS（级联层级）：**
```json
"{\"level\":3,\"parentId\":\"330100\"}"
```

**FORMULA（公式表达式）：**
```json
"{\"expression\":\"agreeInvePeriod + agreePaybackPeriod\",\"unit\":\"年\"}"
```

无特殊属性的字段 propsJson 为空字符串 `""`。

### Step 7: 输出 JSON

- 按 `sortOrder` 排列
- 保存到 `jsonMock/<pageName>.json`
- 同时在 `jsonMock/<pageName>.md` 中以 markdown 代码块展示

### Step 8: 验证

输出后进行交叉检查：

1. **数量一致性**：JSON 中的字段数量应与模板中独立的 `v-model="formData.xxx"` 绑定数量一致（排除 el-table 内的 `scope.row.xxx`）
2. **fieldCode 唯一性**：所有 fieldCode 不重复
3. **linkageJson 引用有效性**：所有 linkageJson 中引用的 field 值在输出的 fieldCode 列表中存在
4. **fieldType 合法性**：所有 fieldType 值在上述映射表的 fieldType 列中存在
5. **sortOrder 连续性**：sortOrder 从 1 开始连续递增，无跳跃

如有不一致，列出差异并说明原因（如表格字段排除、computed 值处理等）。

## 注意事项

- **el-table 内字段不计入**：`v-model="scope.row.xxx"` 是表格行内编辑，不是表单字段
- **同一字段多渲染方式**：一个 `el-col` 内通过 `v-if/v-else-if` 切换的多个组件，对应同一个字段的不同条件下的渲染，不是多个字段。fieldType 取最复杂/最主要的类型
- **section 标题不计入**：如 `<Title value-title="存续情况" />` 是分组标题，不产生 JSON 字段
- **多个 FileLibrary**：同一页面可能有多个 FileLibrary（不同 file-type-id），每个产生一个独立的 JSON 字段，在 propsJson 中记录各自的 fileTypeId/stageType
- **computed 展示字段**：如 `{{ agreeSum }}` 这样的计算值，如果在表单中作为独立展示项，可标记为 FORMULA 类型，readonly=1，expression 记录在 propsJson 中
- **rules 优先**：如果 `<script>` 中的 rules 对象有某字段的 required 验证规则，以 rules 为准（而非只看 mustIn 标记）
