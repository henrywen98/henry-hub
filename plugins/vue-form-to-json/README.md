# vue-form-to-json

Vue 2 + Element UI 表单配置提取器。

## 功能

将 Vue 2 + Element UI 硬编码的表单页面转换为结构化的 JSON 配置数组，用于后端配置化驱动动态表单渲染。

## 使用场景

- 把 `.vue` 文件中的表单转为动态配置
- 梳理表单组件中所有字段
- 表单配置化改造

## 触发方式

提到以下关键词时自动触发：
- "表单转JSON"、"提取表单配置"、"form to JSON"
- "生成表单JSON"、"分析表单字段"、"把表单变成配置"

## 输入/输出

- **输入：** 一个 `.vue` 表单页面文件路径
- **输出：** JSON 配置数组，保存到 `jsonMock/<pageName>.json` 和 `jsonMock/<pageName>.md`

## 安装

```
/plugins install vue-form-to-json@henry-hub
```
